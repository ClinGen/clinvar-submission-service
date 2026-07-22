#!/usr/bin/env python
"""POST a sample curation to the local CVSS API for manual testing.

Usage:
    uv run scripts/add_curation.py
    uv run scripts/add_curation.py --host http://localhost:8000

The script reads API_KEY from the environment (or .env). Create an API key
via the Django admin panel and set it in .env before running.
"""

import argparse
import json
import os
import sys
import uuid

import requests
from dotenv import load_dotenv

load_dotenv()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--host",
        default="http://localhost:8000",
        help="Base URL of the running CVSS instance (default: http://localhost:8000)",
    )
    args = parser.parse_args()

    api_key = os.getenv("API_KEY")
    if not api_key:
        print("Error: API_KEY is not set. Add it to .env or export it.")
        sys.exit(1)

    payload = {
        "variant": {
            "car_id": "CA123",
            "gene_symbol": "FOO",
            "reference_sequence": "NM_000000.1",
            "hgvs": "NM_000000.1:c.123A>G",
            "alternate_designations": "foobar_alt_1",
        },
        "disease": {
            "id_type": "MONDO",
            "id_value": "MONDO:0000001",
        },
        "publications": [
            {
                "pubmed_id": "11111111",
                "doi": None,
                "title": "Foobar variant study",
                "authors": ["Foo A", "Bar B"],
                "publication_year": 2020,
            }
        ],
        "affiliation": "10000",
        "source_app": "foobar-app",
        "schema_version": "1.0",
        "raw_payload": {"foo": "bar"},
        "local_id": str(uuid.uuid4()),
        "linking_id": str(uuid.uuid4()),
        "germline_classification": "Pathogenic",
        "mode_of_inheritance": "Autosomal dominant",
        "date_last_evaluated": "2025-01-01",
        "comment_on_classification": "Foobar comment on classification.",
        "collection_method": "literature only",
        "allele_origin": "germline",
        "affected_status": "yes",
    }

    url = f"{args.host}/api/v1/curation/create/"
    print(f"POST {url}")
    print(f"local_id: {payload['local_id']}")

    response = requests.post(
        url,
        json=payload,
        headers={"Authorization": f"Api-Key {api_key}"},
    )

    print(f"Status: {response.status_code}")
    try:
        print(json.dumps(response.json(), indent=2))
    except requests.exceptions.JSONDecodeError:
        print(response.text)

    if not response.ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
