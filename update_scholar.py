#!/usr/bin/env python3
"""Refresh a snapshot of a single public Google Scholar author profile.
Existing data is left untouched on network, parsing, or validation failure.
"""
from __future__ import annotations
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from scholarly import scholarly

ID = 'Xa97hl4AAAAJ'
DEST = Path(__file__).parent / 'scholar_data.json'

def main():
    author = scholarly.search_author_id(ID)
    author = scholarly.fill(author, sections=['indices', 'counts'])
    if author.get('scholar_id') != ID:
        raise RuntimeError('Google Scholar returned a different author')
    values = {'citations': author.get('citedby'), 'hindex': author.get('hindex'), 'i10index': author.get('i10index')}
    for key, value in values.items():
        if type(value) is not int or value < 0:
            raise RuntimeError(f'Missing or invalid {key}: {value!r}')
    yearly = author.get('cites_per_year')
    if not isinstance(yearly, dict) or not yearly:
        raise RuntimeError('Missing annual citation counts')
    counts = {}
    for y, n in yearly.items():
        y, n = int(y), int(n)
        if not 1900 <= y <= datetime.now(timezone.utc).year or n < 0:
            raise RuntimeError('Invalid yearly data')
        counts[str(y)] = n
    data = {'scholar_id': ID, **values, 'cites_per_year': counts,
            'updated': datetime.now(timezone.utc).date().isoformat()}
    # Write only after every field passes validation.
    tmp = DEST.with_suffix('.json.tmp')
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    os.replace(tmp, DEST)
    print(f"Updated {DEST}: {values['citations']} citations")

if __name__ == '__main__':
    main()
