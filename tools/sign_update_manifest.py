#!/usr/bin/env python3
"""Create the exact Wujin update manifest bytes and detached Ed25519 signature."""

import argparse
import json
import os
import re
import shutil
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
OUTPUT_NAMES = {"latest.json", "latest.json.sig"}
PRERELEASE_IDENTIFIER = r"(?:0|[1-9][0-9]*|[0-9]*[A-Za-z-][0-9A-Za-z-]*)"
SEMVER = re.compile(
    r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)"
    rf"(?:-{PRERELEASE_IDENTIFIER}(?:\.{PRERELEASE_IDENTIFIER})*)?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$"
)
WIN32_RESERVED_NAMES = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    *(f"COM{number}" for number in range(1, 10)),
    *(f"LPT{number}" for number in range(1, 10)),
}


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
    current = path
    if current.is_file():
        current = current.parent
    for directory in (current, *current.parents):
        if (directory / ".git").exists():
            return True
    return False


def reject_ambiguous_win32_spelling(path: Path) -> None:
    spelling = str(path)
    if spelling.startswith(("\\\\?\\", "\\\\.\\")):
        raise ValueError("ambiguous Win32 path: extended device spelling is not allowed")
    if path.drive and not path.root:
        raise ValueError("ambiguous Win32 path: drive-relative spelling is not allowed")

    anchor = path.anchor
    for component in path.parts:
        if component == anchor or component in {".", ".."}:
            continue
        if component.endswith((".", " ")):
            raise ValueError("ambiguous Win32 path: component ends with a dot or space")
        if ":" in component:
            raise ValueError("ambiguous Win32 path: alternate data stream is not allowed")
        base_name = component.split(".", 1)[0].upper()
        if base_name in WIN32_RESERVED_NAMES:
            raise ValueError("ambiguous Win32 path: reserved device name is not allowed")


def expand_win32_long_path(path: Path) -> Path:
    if os.name != "nt":
        return path

    import ctypes

    suffix = []
    existing = path
    while not existing.exists() and existing.parent != existing:
        suffix.append(existing.name)
        existing = existing.parent

    buffer = ctypes.create_unicode_buffer(32768)
    length = ctypes.windll.kernel32.GetLongPathNameW(
        str(existing), buffer, len(buffer)
    )
    if 0 < length < len(buffer):
        existing = Path(buffer.value)
    for component in reversed(suffix):
        existing /= component
    return existing


def normalize_target_path(path: Path) -> Path:
    expanded = path.expanduser()
    reject_ambiguous_win32_spelling(expanded)
    absolute = Path(os.path.abspath(str(expanded)))
    resolved = Path(os.path.realpath(str(absolute)))
    return expand_win32_long_path(resolved)


def same_target(first: Path, second: Path) -> bool:
    return os.path.normcase(os.path.normpath(str(first))) == os.path.normcase(
        os.path.normpath(str(second))
    )


def path_is_within(path: Path, directory: Path) -> bool:
    try:
        path.relative_to(directory)
        return True
    except ValueError:
        return False


def reject_key_output_overlap(key_path: Path, output_dir: Path) -> None:
    if same_target(key_path, output_dir) or path_is_within(key_path, output_dir):
        raise ValueError("private key must not overlap signing transaction paths")

    for name in OUTPUT_NAMES:
        final_path = output_dir / name
        if final_path.exists() and os.path.samefile(key_path, final_path):
            raise ValueError("private key must not overlap signing transaction paths")


def reject_key_transaction_paths(key_path: Path, *directories: Path) -> None:
    for directory in directories:
        if same_target(key_path, directory) or path_is_within(key_path, directory):
            raise ValueError("private key must not overlap signing transaction paths")
        candidates = (directory, *(directory / name for name in OUTPUT_NAMES))
        for candidate in candidates:
            if same_target(key_path, candidate):
                raise ValueError("private key must not overlap signing transaction paths")
            if candidate.exists() and candidate.is_file() and os.path.samefile(
                key_path, candidate
            ):
                raise ValueError("private key must not overlap signing transaction paths")


def validate_inputs(args: argparse.Namespace) -> Tuple[Path, Path]:
    key_path = normalize_target_path(args.private_key)
    output_dir = normalize_target_path(args.output_dir)

    if is_inside_git_repository(key_path):
        raise ValueError("update private key must stay outside every Git repository")
    if not key_path.is_file():
        raise ValueError("update private key path must name an existing file")
    reject_key_output_overlap(key_path, output_dir)
    if not SEMVER.fullmatch(args.version):
        raise ValueError("version must be valid SemVer")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", args.published_at):
        raise ValueError("published-at must be an RFC 3339 UTC timestamp ending in Z")
    published_at = datetime.fromisoformat(args.published_at.replace("Z", "+00:00"))
    if published_at.tzinfo != timezone.utc:
        raise ValueError("published-at must use UTC")
    production_output = normalize_target_path(PRODUCTION_OUTPUT)
    if same_target(output_dir, production_output) and not args.allow_production_output:
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


def write_durable(path: Path, content: bytes) -> None:
    with path.open("xb") as output:
        output.write(content)
        output.flush()
        os.fsync(output.fileno())


def validate_existing_output(output_dir: Path) -> None:
    if not output_dir.exists():
        return
    if not output_dir.is_dir():
        raise ValueError("output-dir must be a directory")
    existing = {entry.name for entry in output_dir.iterdir()}
    if existing not in (set(), OUTPUT_NAMES):
        raise ValueError("output-dir must be empty or contain exactly the existing pair")


def reserve_backup_path(output_dir: Path) -> Path:
    backup = Path(
        tempfile.mkdtemp(
            prefix=f".{output_dir.name}.wujin-backup-", dir=output_dir.parent
        )
    )
    os.rmdir(backup)
    return backup


def publish_pair(
    output_dir: Path, manifest: bytes, signature: bytes, key_path: Path
) -> None:
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    validate_existing_output(output_dir)
    stage = Path(
        tempfile.mkdtemp(
            prefix=f".{output_dir.name}.wujin-stage-", dir=output_dir.parent
        )
    )
    backup = None
    try:
        reject_key_transaction_paths(key_path, stage)
        write_durable(stage / "latest.json", manifest)
        write_durable(stage / "latest.json.sig", signature)

        if output_dir.exists():
            backup = reserve_backup_path(output_dir)
            reject_key_transaction_paths(key_path, backup)
            os.replace(output_dir, backup)
        try:
            os.replace(stage, output_dir)
        except BaseException as promotion_error:
            if backup is not None:
                try:
                    os.replace(backup, output_dir)
                    backup = None
                except BaseException as recovery_error:
                    raise OSError(
                        f"pair promotion failed and recovery is required at {backup}"
                    ) from recovery_error
            raise promotion_error

        if backup is not None:
            shutil.rmtree(backup)
            backup = None
    finally:
        if stage.is_dir() and not path_is_within(key_path, stage):
            shutil.rmtree(stage)


def main() -> int:
    args = parse_args()
    try:
        key_path, output_dir = validate_inputs(args)
        manifest = manifest_bytes(args.version, args.published_at)
        signature = load_private_key(key_path).sign(manifest)
        if len(signature) != 64:
            raise ValueError("Ed25519 detached signature must be exactly 64 bytes")
        publish_pair(output_dir, manifest, signature, key_path)
    except (OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    print(f"Wrote deterministic manifest and detached signature to {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
