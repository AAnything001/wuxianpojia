import argparse
import contextlib
import ctypes
import importlib.util
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path
from unittest import mock
from urllib.parse import urlparse

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
SIGNER = REPO_ROOT / "tools" / "sign_update_manifest.py"
HEADERS = REPO_ROOT / "_headers"
INDEX = REPO_ROOT / "index.html"
SIGNER_SPEC = importlib.util.spec_from_file_location("wujin_update_signer", SIGNER)
SIGNER_MODULE = importlib.util.module_from_spec(SIGNER_SPEC)
SIGNER_SPEC.loader.exec_module(SIGNER_MODULE)


class HrefCollector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.download_hrefs = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            attributes = dict(attrs)
            classes = attributes.get("class", "").split()
            href = attributes.get("href")
            if "download-option" in classes and href is not None:
                self.download_hrefs.append(href)


def write_private_key(path: Path) -> bytes:
    encoded = Ed25519PrivateKey.generate().private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(encoded)
    return encoded


def signer_args(key_path: Path, output_dir: Path, version="1.30.1"):
    return [
        str(SIGNER),
        "--private-key",
        str(key_path),
        "--version",
        version,
        "--published-at",
        "2026-07-22T00:00:00Z",
        "--output-dir",
        str(output_dir),
    ]


class ReleaseMetadataTests(unittest.TestCase):
    def test_cloudflare_headers_keep_manifest_fresh_with_explicit_mime_types(self):
        headers = HEADERS.read_text(encoding="utf-8")

        self.assertIn(
            "/downloads/wujin/stable/latest.json\n"
            "  Cache-Control: no-cache, must-revalidate\n"
            "  Content-Type: application/json; charset=utf-8",
            headers,
        )
        self.assertIn(
            "/downloads/wujin/stable/latest.json.sig\n"
            "  Cache-Control: no-cache, must-revalidate\n"
            "  Content-Type: application/octet-stream",
            headers,
        )

    def test_signed_release_files_are_checked_out_byte_for_byte(self):
        attributes = (REPO_ROOT / ".gitattributes").read_text(encoding="utf-8")

        self.assertIn("/downloads/wujin/stable/latest.json -text", attributes)
        self.assertIn("/downloads/wujin/stable/latest.json.sig -text", attributes)

    def test_update_log_highlights_the_1_30_3_release_and_preserves_history(self):
        page = INDEX.read_text(encoding="utf-8")

        self.assertIn('datetime="2026-07-24">2026.07.24</time>', page)
        self.assertIn("Windows v1.30.3 · 新用户配置与协议流程优化", page)
        self.assertIn(
            "提高新用户首次配置成功率；新增配置冲突检查与修复，并优化用户协议确认流程。",
            page,
        )
        self.assertIn("'Windows v1.30.3 已发布'", page)
        self.assertIn('"dateModified": "2026-07-24"', page)
        self.assertIn('datetime="2026-07-23">2026.07.23</time>', page)
        self.assertIn("Windows v1.30.1 · 大版本更新，务必下载", page)
        self.assertIn("更新 5.5 破甲方案，新增支持 5.6 最新方案；新增免费模块，进一步增强你的 AI。", page)
        self.assertNotIn("开发中（尚未提供下载包）", page)

    def test_download_urls_match_current_release_channels(self):
        page = INDEX.read_text(encoding="utf-8")
        expected_urls = {
            "https://pan.baidu.com/s/1wvuMX5b-ATgDE-hhCmbakg?pwd=uigu",
            "https://pan.quark.cn/s/fe6c168221f6",
            "https://wwbbc.lanzouv.com/iOjYk3yftdni",
            "https://wwbbc.lanzouv.com/iBE7j3yh7dwh",
        }
        collector = HrefCollector()
        collector.feed(page)
        actual_urls = set(collector.download_hrefs)

        self.assertEqual(expected_urls, actual_urls)
        self.assertEqual(len(expected_urls), len(collector.download_hrefs))
        self.assertTrue(all(urlparse(href).scheme == "https" for href in actual_urls))

    def test_production_manifest_is_valid_and_signed(self):
        stable = REPO_ROOT / "downloads" / "wujin" / "stable"
        manifest = (stable / "latest.json").read_bytes()
        signature = (stable / "latest.json.sig").read_bytes()
        data = json.loads(manifest)

        self.assertEqual(
            {
                "schema_version": 1,
                "product": "wujin-reverse-skill",
                "channel": "stable",
                "version": "1.30.3",
                "published_at": "2026-07-24T16:26:54Z",
                "download_page": "https://codexpojia.com/#download",
                "release_notes_url": "https://codexpojia.com/#a-updates",
            },
            data,
        )
        self.assertEqual(64, len(signature))
        public_key = bytes.fromhex(
            "9eb3b20cc6fba13a26a6a6d3485e65b681db654c25ce352bce7b314e08574695"
        )
        Ed25519PublicKey.from_public_bytes(public_key).verify(signature, manifest)

    def test_signer_writes_deterministic_exact_json_and_detached_signature(self):
        with tempfile.TemporaryDirectory() as private_dir, tempfile.TemporaryDirectory() as first_dir, tempfile.TemporaryDirectory() as second_dir:
            key_path = Path(private_dir) / "update-private.pem"
            private_key = Ed25519PrivateKey.generate()
            key_path.write_bytes(
                private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption(),
                )
            )

            common = [
                sys.executable,
                str(SIGNER),
                "--private-key",
                str(key_path),
                "--version",
                "1.30.1",
                "--published-at",
                "2026-07-22T00:00:00Z",
            ]
            for output_dir in (first_dir, second_dir):
                result = subprocess.run(
                    common + ["--output-dir", output_dir],
                    check=False,
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(0, result.returncode, result.stderr)

            first_manifest = (Path(first_dir) / "latest.json").read_bytes()
            second_manifest = (Path(second_dir) / "latest.json").read_bytes()
            first_signature = (Path(first_dir) / "latest.json.sig").read_bytes()
            second_signature = (Path(second_dir) / "latest.json.sig").read_bytes()

            expected = {
                "schema_version": 1,
                "product": "wujin-reverse-skill",
                "channel": "stable",
                "version": "1.30.1",
                "published_at": "2026-07-22T00:00:00Z",
                "download_page": "https://codexpojia.com/#download",
                "release_notes_url": "https://codexpojia.com/#a-updates",
            }
            expected_bytes = (json.dumps(expected, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")

            self.assertEqual(expected_bytes, first_manifest)
            self.assertEqual(first_manifest, second_manifest)
            self.assertEqual(first_signature, second_signature)
            self.assertEqual(64, len(first_signature))
            private_key.public_key().verify(first_signature, first_manifest)

    def test_signer_rejects_a_private_key_path_inside_the_repository(self):
        result = subprocess.run(
            [
                sys.executable,
                str(SIGNER),
                "--private-key",
                str(REPO_ROOT / "README.md"),
                "--version",
                "1.30.1",
                "--published-at",
                "2026-07-22T00:00:00Z",
                "--output-dir",
                tempfile.gettempdir(),
            ],
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertNotEqual(0, result.returncode)
        self.assertIn("outside every Git repository", result.stderr)

    def test_signer_rejects_semver_prerelease_numeric_identifiers_with_leading_zeroes(self):
        with tempfile.TemporaryDirectory() as private_dir, tempfile.TemporaryDirectory() as output_dir:
            key_path = Path(private_dir) / "update-private.pem"
            key_path.write_bytes(
                Ed25519PrivateKey.generate().private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption(),
                )
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(SIGNER),
                    "--private-key",
                    str(key_path),
                    "--version",
                    "1.30.1-01",
                    "--published-at",
                    "2026-07-22T00:00:00Z",
                    "--output-dir",
                    output_dir,
                ],
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertNotEqual(0, result.returncode)
            self.assertIn("valid SemVer", result.stderr)

    def test_signer_rejects_unicode_digits_in_semver(self):
        with tempfile.TemporaryDirectory() as private_dir, tempfile.TemporaryDirectory() as output_dir:
            key_path = Path(private_dir) / "update-private.pem"
            write_private_key(key_path)
            result = subprocess.run(
                [sys.executable]
                + signer_args(key_path, Path(output_dir), version="1.3٠.1"),
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertNotEqual(0, result.returncode)
            self.assertIn("valid SemVer", result.stderr)

    def test_signer_rejects_win32_trailing_dot_or_space_components(self):
        with tempfile.TemporaryDirectory() as private_dir, tempfile.TemporaryDirectory() as parent_dir:
            key_path = Path(private_dir) / "update-private.pem"
            write_private_key(key_path)
            stable = Path(parent_dir) / "stable"
            stable.mkdir()

            for ambiguous in (
                Path(str(stable) + "."),
                Path(str(stable) + " "),
                Path(parent_dir) / "component." / "stable",
                Path(parent_dir) / "NUL" / "stable",
                Path(str(stable) + ":alternate"),
                REPO_ROOT / "downloads" / "wujin" / "stable.",
                Path(f"{REPO_ROOT.drive}downloads\\wujin\\stable"),
            ):
                with self.subTest(path=ambiguous):
                    args = argparse.Namespace(
                        private_key=key_path,
                        output_dir=ambiguous,
                        version="1.30.1",
                        published_at="2026-07-22T00:00:00Z",
                        allow_production_output=True,
                    )
                    with self.assertRaisesRegex(ValueError, "ambiguous Win32 path"):
                        SIGNER_MODULE.validate_inputs(args)

            if os.name == "nt":
                self.assertTrue(Path(str(stable) + ".").exists())
                self.assertTrue(os.path.samefile(stable, Path(str(stable) + ".")))

    def test_production_gate_normalizes_dot_segments_and_win32_short_aliases(self):
        with tempfile.TemporaryDirectory() as private_dir:
            key_path = Path(private_dir) / "update-private.pem"
            write_private_key(key_path)
            spellings = [
                REPO_ROOT / "downloads" / "wujin" / "nested" / ".." / "stable"
            ]
            if os.name == "nt":
                buffer = ctypes.create_unicode_buffer(32768)
                length = ctypes.windll.kernel32.GetShortPathNameW(
                    str(REPO_ROOT), buffer, len(buffer)
                )
                if 0 < length < len(buffer):
                    spellings.append(
                        Path(buffer.value) / "downloads" / "wujin" / "stable"
                    )

            for spelling in spellings:
                with self.subTest(path=spelling):
                    args = argparse.Namespace(
                        private_key=key_path,
                        output_dir=spelling,
                        version="1.30.1",
                        published_at="2026-07-22T00:00:00Z",
                        allow_production_output=False,
                    )
                    with self.assertRaisesRegex(ValueError, "production output is locked"):
                        SIGNER_MODULE.validate_inputs(args)

    def test_signer_rejects_key_inside_output_tree_without_changing_key_bytes(self):
        for relative_key in ("latest.json", "latest.json.sig", "private.pem"):
            with self.subTest(relative_key=relative_key), tempfile.TemporaryDirectory() as root_dir:
                output_dir = Path(root_dir) / "stable"
                key_path = output_dir / relative_key
                original_key = write_private_key(key_path)
                result = subprocess.run(
                    [sys.executable] + signer_args(key_path, output_dir),
                    check=False,
                    capture_output=True,
                    text=True,
                )

                self.assertNotEqual(0, result.returncode)
                self.assertIn("overlap signing transaction paths", result.stderr)
                self.assertEqual(original_key, key_path.read_bytes())

    def test_signer_rejects_a_hardlink_alias_between_key_and_final_output(self):
        with tempfile.TemporaryDirectory() as root_dir, tempfile.TemporaryDirectory() as private_dir:
            output_dir = Path(root_dir) / "stable"
            output_dir.mkdir()
            key_path = Path(private_dir) / "update-private.pem"
            original_key = write_private_key(key_path)
            os.link(key_path, output_dir / "latest.json")

            result = subprocess.run(
                [sys.executable] + signer_args(key_path, output_dir),
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertNotEqual(0, result.returncode)
            self.assertIn("overlap signing transaction paths", result.stderr)
            self.assertEqual(original_key, key_path.read_bytes())

    def test_signer_rejects_a_backup_path_collision_without_changing_any_input(self):
        with tempfile.TemporaryDirectory() as root_dir, tempfile.TemporaryDirectory() as private_dir:
            output_dir = Path(root_dir) / "stable"
            output_dir.mkdir()
            old_manifest = b'{"version":"old"}\n'
            old_signature = b"s" * 64
            (output_dir / "latest.json").write_bytes(old_manifest)
            (output_dir / "latest.json.sig").write_bytes(old_signature)
            key_path = Path(private_dir) / "update-private.pem"
            original_key = write_private_key(key_path)

            stderr = io.StringIO()
            with mock.patch.object(sys, "argv", signer_args(key_path, output_dir)), mock.patch.object(
                SIGNER_MODULE, "reserve_backup_path", return_value=key_path
            ), contextlib.redirect_stderr(stderr):
                result = SIGNER_MODULE.main()

            self.assertEqual(2, result)
            self.assertIn("overlap signing transaction paths", stderr.getvalue())
            self.assertEqual(original_key, key_path.read_bytes())
            self.assertEqual(old_manifest, (output_dir / "latest.json").read_bytes())
            self.assertEqual(old_signature, (output_dir / "latest.json.sig").read_bytes())

    def test_signer_rejects_a_stage_path_collision_without_changing_the_key(self):
        with tempfile.TemporaryDirectory() as root_dir, tempfile.TemporaryDirectory() as private_dir:
            output_dir = Path(root_dir) / "stable"
            output_dir.mkdir()
            key_path = Path(private_dir) / "update-private.pem"
            original_key = write_private_key(key_path)

            stderr = io.StringIO()
            with mock.patch.object(sys, "argv", signer_args(key_path, output_dir)), mock.patch.object(
                SIGNER_MODULE.tempfile, "mkdtemp", return_value=str(key_path)
            ), contextlib.redirect_stderr(stderr):
                result = SIGNER_MODULE.main()

            self.assertEqual(2, result)
            self.assertIn("overlap signing transaction paths", stderr.getvalue())
            self.assertEqual(original_key, key_path.read_bytes())
            self.assertEqual(set(), {entry.name for entry in output_dir.iterdir()})

    def test_pair_commit_failure_restores_the_complete_previous_pair(self):
        with tempfile.TemporaryDirectory() as root_dir, tempfile.TemporaryDirectory() as private_dir:
            output_dir = Path(root_dir) / "stable"
            output_dir.mkdir()
            old_manifest = b'{"version":"old"}\n'
            old_signature = b"s" * 64
            (output_dir / "latest.json").write_bytes(old_manifest)
            (output_dir / "latest.json.sig").write_bytes(old_signature)
            key_path = Path(private_dir) / "update-private.pem"
            write_private_key(key_path)
            real_replace = os.replace
            replace_count = 0

            def fail_second_replace(source, destination):
                nonlocal replace_count
                replace_count += 1
                if replace_count == 2:
                    raise OSError("injected second replace failure")
                return real_replace(source, destination)

            stderr = io.StringIO()
            with mock.patch.object(sys, "argv", signer_args(key_path, output_dir)), mock.patch.object(
                SIGNER_MODULE.os, "replace", side_effect=fail_second_replace
            ), contextlib.redirect_stderr(stderr):
                result = SIGNER_MODULE.main()

            self.assertEqual(2, result)
            self.assertIn("injected second replace failure", stderr.getvalue())
            self.assertEqual(old_manifest, (output_dir / "latest.json").read_bytes())
            self.assertEqual(old_signature, (output_dir / "latest.json.sig").read_bytes())
            self.assertEqual([], list(Path(root_dir).glob(".stable.wujin-*")))

    def test_second_stage_write_failure_leaves_the_previous_pair_unchanged(self):
        with tempfile.TemporaryDirectory() as root_dir, tempfile.TemporaryDirectory() as private_dir:
            output_dir = Path(root_dir) / "stable"
            output_dir.mkdir()
            old_manifest = b'{"version":"old"}\n'
            old_signature = b"s" * 64
            (output_dir / "latest.json").write_bytes(old_manifest)
            (output_dir / "latest.json.sig").write_bytes(old_signature)
            key_path = Path(private_dir) / "update-private.pem"
            write_private_key(key_path)
            real_write = SIGNER_MODULE.write_durable
            write_count = 0

            def fail_second_write(path, content):
                nonlocal write_count
                write_count += 1
                if write_count == 2:
                    raise OSError("injected second stage write failure")
                return real_write(path, content)

            stderr = io.StringIO()
            with mock.patch.object(sys, "argv", signer_args(key_path, output_dir)), mock.patch.object(
                SIGNER_MODULE, "write_durable", side_effect=fail_second_write
            ), contextlib.redirect_stderr(stderr):
                result = SIGNER_MODULE.main()

            self.assertEqual(2, result)
            self.assertIn("injected second stage write failure", stderr.getvalue())
            self.assertEqual(old_manifest, (output_dir / "latest.json").read_bytes())
            self.assertEqual(old_signature, (output_dir / "latest.json.sig").read_bytes())
            self.assertEqual([], list(Path(root_dir).glob(".stable.wujin-*")))


if __name__ == "__main__":
    unittest.main()
