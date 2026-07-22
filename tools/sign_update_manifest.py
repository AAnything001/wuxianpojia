#!/usr/bin/env python3
"""Create the exact Wujin update manifest bytes and detached Ed25519 signature."""

import argparse
import json
import os
import re
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Tuple

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
)
from cryptography.hazmat.backends import default_backend


REPO_ROOT = Path(__file__).resolve().parents[1]
PRODUCTION_OUTPUT = REPO_ROOT / "downloads" / "wujin" / "stable"
PRERELEASE_IDENTIFIER = r"(?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*)"
SEMVER = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    rf"(?:-{PRERELEASE_IDENTIFIER}(?:\.{PRERELEASE_IDENTIFIER})*)?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Offline deterministic signer for Wujin static update metadata."
    )
    parser.add_argument("--private-key", type=Path, required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--published-at", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument(
        "--allow-production-output",
        action="store_true",
        help="Required only when writing the website's live downloads route after release approval.",
    )
    return parser.parse_args()


def is_inside_git_repository(path: Path) -> bool:
    current = path.resolve()
    if current.is_file():
        current = current.parent
    for directory in (current, *current.parents):
        if (directory / ".git").exists():
            return True
    return False


def validate_inputs(args: argparse.Namespace) -> Tuple[Path, Path]:
    key_path = args.private_key.expanduser().resolve()
    output_dir = args.output_dir.expanduser().resolve()

    if is_inside_git_repository(key_path):
        raise ValueError("update private key must stay outside every Git repository")
    if not key_path.is_file():
        raise ValueError("update private key path must name an existing file")
    if not SEMVER.fullmatch(args.version):
        raise ValueError("version must be valid SemVer")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", args.published_at):
        raise ValueError("published-at must be an RFC 3339 UTC timestamp ending in Z")
    published_at = datetime.fromisoformat(args.published_at.replace("Z", "+00:00"))
    if published_at.tzinfo != timezone.utc:
        raise ValueError("published-at must use UTC")
    if output_dir == PRODUCTION_OUTPUT.resolve() and not args.allow_production_output:
        raise ValueError(
            "production output is locked; use --allow-production-output only after release approval"
        )
    return key_path, output_dir


def load_private_key(key_path: Path) -> Ed25519PrivateKey:
    encoded = key_path.read_bytes()
    try:
        key = serialization.load_pem_private_key(
            encoded, password=None, backend=default_backend()
        )
    except ValueError:
        if len(encoded) != 32:
            raise ValueError("private key must be Ed25519 PKCS#8 PEM or a raw 32-byte seed")
        key = Ed25519PrivateKey.from_private_bytes(encoded)
    if not isinstance(key, Ed25519PrivateKey):
        raise ValueError("private key must be Ed25519")
    return key


def manifest_bytes(version: str, published_at: str) -> bytes:
    manifest = {
        "schema_version": 1,
        "product": "wujin-reverse-skill",
        "channel": "stable",
        "version": version,
        "published_at": published_at,
        "download_page": "https://codexpojia.com/#download",
        "release_notes_url": "https://codexpojia.com/#a-updates",
    }
    return (
        json.dumps(manifest, ensure_ascii=False, separators=(",", ":")) + "\n"
    ).encode("utf-8")


def write_atomic(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(handle, "wb") as temporary:
            temporary.write(content)
            temporary.flush()
            os.fsync(temporary.fileno())
        os.replace(temporary_name, path)
    except BaseException:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise


def main() -> int:
    args = parse_args()
    try:
        key_path, output_dir = validate_inputs(args)
        manifest = manifest_bytes(args.version, args.published_at)
        signature = load_private_key(key_path).sign(manifest)
        if len(signature) != 64:
            raise ValueError("Ed25519 detached signature must be exactly 64 bytes")
        write_atomic(output_dir / "latest.json.sig", signature)
        write_atomic(output_dir / "latest.json", manifest)
    except (OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    print(f"Wrote deterministic manifest and detached signature to {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
