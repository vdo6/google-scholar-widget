#!/usr/bin/env python3
"""Update Google Scholar statistics with a strict timeout."""

import json
import os
import multiprocessing as mp
from queue import Empty
from pathlib import Path
from datetime import datetime, timezone

SCHOLAR_ID = "Xa97hl4AAAAJ"
DEST = Path(__file__).parent / "scholar_data.json"
TIMEOUT = 90


def retrieve(queue):
    try:
        print("Connecting to Google Scholar...", flush=True)

        from scholarly import scholarly

        print("Searching author profile...", flush=True)
        author = scholarly.search_author_id(SCHOLAR_ID)

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
        print(f"Retrieval error: {exc}", flush=True)
        queue.put(("error", str(exc)))


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
            "TIMEOUT: Google Scholar did not respond "
            f"within {TIMEOUT} seconds.",
            flush=True
        )
        print("Previous data preserved.", flush=True)

        process.terminate()
        process.join(timeout=5)

        if process.is_alive():
            process.kill()
            process.join()

        raise SystemExit(1)

    finally:
        if process.is_alive():
            process.terminate()
        process.join(timeout=5)
        queue.close()

    if status != "success":
        print("Update failed. Previous data preserved.")
        raise SystemExit(1)

    # Atomic replacement: preserve old data on failure
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
