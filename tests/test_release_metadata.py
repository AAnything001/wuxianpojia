import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


REPO_ROOT = Path(__file__).resolve().parents[1]
SIGNER = REPO_ROOT / "tools" / "sign_update_manifest.py"
HEADERS = REPO_ROOT / "_headers"
INDEX = REPO_ROOT / "index.html"


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

    def test_update_log_marks_1_30_1_as_development_not_an_available_package(self):
        page = INDEX.read_text(encoding="utf-8")

        self.assertIn("Windows v1.30.1", page)
        self.assertIn("开发中（尚未提供下载包）", page)

    def test_existing_netdisk_urls_are_unchanged(self):
        page = INDEX.read_text(encoding="utf-8")
        expected_urls = {
            "https://pan.baidu.com/s/1wvuMX5b-ATgDE-hhCmbakg?pwd=uigu",
            "https://pan.quark.cn/s/fe6c168221f6",
            "https://wwbbc.lanzouv.com/i95673xe26ti",
            "https://wwbbc.lanzouv.com/i9zwz3xnj43g",
        }

        for url in expected_urls:
            self.assertIn(url, page)

    def test_production_manifest_is_not_present_before_packaging_approval(self):
        stable = REPO_ROOT / "downloads" / "wujin" / "stable"

        self.assertFalse((stable / "latest.json").exists())
        self.assertFalse((stable / "latest.json.sig").exists())

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


if __name__ == "__main__":
    unittest.main()
