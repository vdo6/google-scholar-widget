
#!/usr/bin/env python3
"""Update Google Scholar statistics safely."""

import json
import os
import multiprocessing as mp
from queue import Empty
from pathlib import Path
from datetime import datetime, timezone

SCHOLAR_ID = "Xa97hl4AAAAJ"
DEST = Path(__file__).parent / "scholar_data.json"

TIMEOUT = 240
REQUEST_TIMEOUT = 30
MAX_RETRIES = 2


def retrieve(queue):
    try:
        print("Connecting to Google Scholar...", flush=True)

        from scholarly import scholarly

        scholarly.set_timeout(REQUEST_TIMEOUT)
        scholarly.set_retries(MAX_RETRIES)

        print("Searching author profile...", flush=True)

        author = scholarly.search_author_id(SCHOLAR_ID)

        print("Author profile found.", flush=True)
        print("Retrieving citation statistics...", flush=True)

        author = scholarly.fill(
            author,
            sections=["indices", "counts"]
        )

        if author.get("scholar_id") != SCHOLAR_ID:
            raise ValueError("Incorrect Scholar profile")

        values = {
            "citations": author.get("citedby"),
            "hindex": author.get("hindex"),
            "i10index": author.get("i10index")
        }

        for key, value in values.items():
            if type(value) is not int or value < 0:
                raise ValueError(f"Invalid {key}: {value}")

        yearly = author.get("cites_per_year")

        if not isinstance(yearly, dict) or not yearly:
            raise ValueError("Missing yearly citations")

        current_year = datetime.now(timezone.utc).year
        counts = {}

        for year, count in yearly.items():
            year = int(year)
            count = int(count)

            if not 1900 <= year <= current_year:
                raise ValueError("Invalid year")

            if count < 0:
                raise ValueError("Invalid citation count")

            counts[str(year)] = count

        data = {
            "scholar_id": SCHOLAR_ID,
            **values,
            "cites_per_year": counts,
            "updated": datetime.now(
                timezone.utc
            ).date().isoformat()
        }

        queue.put(("success", data))

    except Exception as exc:
        error = f"{type(exc).__name__}: {exc}"
        print(f"Retrieval error: {error}", flush=True)
        queue.put(("error", error))


def main():
    print("Starting Google Scholar update", flush=True)
    print(f"Scholar ID: {SCHOLAR_ID}", flush=True)

    queue = mp.Queue()

    process = mp.Process(
        target=retrieve,
        args=(queue,)
    )

    process.start()

    try:
        status, result = queue.get(timeout=TIMEOUT)

    except Empty:
        print(
            f"TIMEOUT: No result within {TIMEOUT} seconds.",
            flush=True
        )
        print("Previous data preserved.", flush=True)

        raise SystemExit(1)

    finally:
        if process.is_alive():
            process.terminate()

        process.join(timeout=5)

        if process.is_alive():
            process.kill()
            process.join()

        queue.close()

    if status != "success":
        print(f"Update failed: {result}", flush=True)
        print("Previous data preserved.", flush=True)
        raise SystemExit(1)

    temp = DEST.with_suffix(".json.tmp")

    try:
        temp.write_text(
            json.dumps(result, indent=2) + "\n",
            encoding="utf-8"
        )
        os.replace(temp, DEST)

    finally:
        if temp.exists():
            temp.unlink()

    print("Google Scholar updated successfully!")
    print(f"Citations: {result['citations']}")
    print(f"h-index: {result['hindex']}")
    print(f"i10-index: {result['i10index']}")
    print(f"Updated: {result['updated']}")


if __name__ == "__main__":
    mp.freeze_support()
    main()
