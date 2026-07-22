# Task 5 Report: Cloudflare Static Release Metadata Scaffolding

## Scope and controller boundary

- Repository/worktree: `G:\AI\GW\.worktrees\wujin-website-v1.30.1`
- Branch: `codex/wujin-website-v1.30.1`
- Implemented source-side scaffolding only.
- Did not read, print, copy, or commit any production private key.
- Did not create `downloads/wujin/stable/latest.json` or `latest.json.sig`.
- Did not deploy Cloudflare Pages, push, merge, alter netdisk URLs, or claim that a
  Windows `1.30.1` package exists.

## Implemented

1. Added `tools/sign_update_manifest.py`.
   - Accepts only an explicit external private-key path.
   - Rejects a key path under any Git repository before attempting to parse it.
   - Accepts Ed25519 PKCS#8 PEM or a raw 32-byte seed.
   - Emits fixed-schema compact UTF-8 JSON with one trailing LF.
   - Emits the raw 64-byte detached Ed25519 signature expected by the Rust client.
   - Uses fixed product/channel/download/release-notes identity fields.
   - Validates SemVer and an RFC 3339 UTC `published_at` value.
   - Uses atomic replacement and performs no network requests.
   - Requires `--allow-production-output` when the destination is the live website
     route, leaving publication behind an explicit release gate.
2. Added `tools/requirements-signing.txt` and documented offline signing usage and
   the publication gate in `README.md`.
3. Added exact Cloudflare Pages `_headers` rules:
   - `latest.json`: `no-cache, must-revalidate`, JSON UTF-8 MIME.
   - `latest.json.sig`: `no-cache, must-revalidate`, octet-stream MIME.
   - Both routes retain `nosniff`.
4. Added a `Windows v1.30.1` update-log entry that is explicitly marked
   `开发中（尚未提供下载包）`.
5. Added behavior tests covering deterministic bytes, deterministic detached
   signatures, public-key verification, key-location isolation, exact Cloudflare
   headers, strict SemVer prerelease parsing, unchanged netdisk links, the non-release
   update-log wording, and absence of production manifest files.

## TDD evidence

RED command:

```powershell
python -m unittest tests/test_release_metadata.py -v
```

Observed before implementation: 3 failures and 1 error. The missing header rules,
missing `1.30.1` development record, and missing signer failed for the intended
reasons. The existing-link and no-production-manifest guards already passed.

GREEN command:

```powershell
python -m unittest tests/test_release_metadata.py -v
```

Observed after implementation: 7 tests passed, 0 failures. A follow-up RED case proved
that `1.30.1-01` was initially accepted; after tightening the SemVer expression, that
case and the full suite passed.

Additional verification:

```powershell
python -m py_compile tools/sign_update_manifest.py tests/test_release_metadata.py
git diff --check
```

Both exited successfully before commit.

## Release-gated work that remains locked

Only after the owner explicitly says `出包`, the Windows release gate passes, and all
existing netdisk links are tested:

1. Use the real update private key from outside both repositories.
2. Generate production `downloads/wujin/stable/latest.json` and
   `latest.json.sig` with `--allow-production-output`.
3. Review and commit those two production artifacts.
4. Merge/push the website independently to `main` so Cloudflare Pages deploys it.
5. Verify the production HTTPS routes return JSON and exactly 64 signature bytes,
   then verify the signature with the public key embedded in the released client.

No item in this locked list was executed during Task 5 development.
