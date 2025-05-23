#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.13"
# dependencies = ["httpx"]
# [tool.uv]
# exclude-newer = "2025-03-13T00:00:00Z"
# ///

import json
from pathlib import Path

import httpx  # type: ignore

INE_BASE_URL = "https://servicios.ine.es/wstempus/js/ES"

client = httpx.Client(
    base_url=INE_BASE_URL,
    limits=httpx.Limits(max_keepalive_connections=16),
    transport=httpx.HTTPTransport(retries=5),
)


def ine_request(client: httpx.Client, endpoint):
    """Fetch data from INE API endpoint with automatic pagination."""
    page = 1
    data = []

    while True:
        response = client.get(
            f"/{endpoint}",
            params={"det": 10, "page": page},
            follow_redirects=True,
            timeout=120,
        ).json()

        if not response:
            break

        data.extend(response)

        if len(response) < 500:
            break

        page += 1

    return data


def save_jsonl(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")


data_dir = Path("ine")
data_dir.mkdir(exist_ok=True)

# OPERACIONES_DISPONIBLES
print("Fetching OPERACIONES_DISPONIBLES...")
operations = ine_request(client, "OPERACIONES_DISPONIBLES")
save_jsonl(operations, data_dir / "operaciones.jsonl")
print(f"\t✓ Found {len(operations)} operations")
print(f"\t✓ Operations data saved to {data_dir}/operaciones.jsonl")

# VARIABLES
print("Fetching VARIABLES...")
variables = ine_request(client, "VARIABLES")
save_jsonl(variables, data_dir / "variables.jsonl")
print(f"\t✓ Found {len(variables)} variables")
print(f"\t✓ Variables data saved to {data_dir}/variables.jsonl")

# PUBLICACIONES
print("Fetching PUBLICACIONES...")
publications = ine_request(client, "PUBLICACIONES")
save_jsonl(publications, data_dir / "publicaciones.jsonl")
print(f"\t✓ Found {len(publications)} publications")
print(f"\t✓ Publications data saved to {data_dir}/publicaciones.jsonl")

# TABLAS_OPERACION
print("Fetching TABLAS_OPERACION...")
tables = [
    table
    for operation in operations
    for table in ine_request(client, f"TABLAS_OPERACION/{operation['Id']}")
]
save_jsonl(tables, data_dir / "tablas.jsonl")
print(f"\t✓ Found {len(tables)} tables")
print(f"\t✓ Tables data saved to {data_dir}/tablas.jsonl")
