"""Download the corpus PDFs listed in manifest.yaml and verify their SHA-256 checksums.

Files already present with the right checksum are skipped, so re-running is safe.

Usage: python -m eval.corpus.fetch
"""

import hashlib
import sys

import httpx

from eval.corpus.manifest import load_manifest
from eval.settings import PAPERS_DIR


def sha256_of(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    manifest = load_manifest()
    PAPERS_DIR.mkdir(parents=True, exist_ok=True)
    failures = 0

    with httpx.Client(follow_redirects=True, timeout=60, headers={"User-Agent": "Mozilla/5.0"}) as client:
        for paper in manifest.papers:
            target = PAPERS_DIR / paper.filename
            if target.exists() and sha256_of(target.read_bytes()) == paper.sha256:
                print(f"ok        {paper.id} (already downloaded)")
                continue

            response = client.get(paper.url)
            response.raise_for_status()
            digest = sha256_of(response.content)
            if digest != paper.sha256:
                # The publisher changed the file. A silent swap would change every eval number.
                print(f"MISMATCH  {paper.id}: expected {paper.sha256}, got {digest}")
                print("          Check the new file before updating its sha256 in manifest.yaml.")
                failures += 1
                continue

            target.write_bytes(response.content)
            print(f"fetched   {paper.id} ({len(response.content):,} bytes)")

    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
