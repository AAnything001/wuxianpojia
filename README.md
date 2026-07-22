# wujin-website-prototype

Static landing page for WUJIN / 无限破甲.

## Cloudflare Pages

- Framework preset: `None`
- Production branch: `main`
- Build command: `exit 0`
- Build output directory: `.`
- Custom domain: `codexpojia.com`

## Signed update metadata

`tools/sign_update_manifest.py` creates deterministic `latest.json` bytes and a raw
64-byte detached Ed25519 signature. The signer performs no network requests. Install
its Python dependency before entering the offline signing environment:

```powershell
python -m pip install -r tools/requirements-signing.txt
```

The private key path must be outside every Git repository. The live output route is
also locked unless release packaging has been explicitly approved:

```powershell
python tools/sign_update_manifest.py `
  --private-key D:\external-secrets\wujin-update-private.pem `
  --version 1.30.1 `
  --published-at 2026-07-22T00:00:00Z `
  --output-dir downloads\wujin\stable `
  --allow-production-output
```

The signer rejects ambiguous Win32 components (including trailing dots/spaces,
reserved device names, and alternate data streams), resolves existing 8.3 aliases
before applying the production gate, and refuses any key/output overlap. It stages
both files in a unique sibling directory and swaps the complete directory as one
transaction; if promotion fails, the previous pair is restored. An existing output
directory must therefore be empty or contain exactly `latest.json` and
`latest.json.sig`.

Do not run the production command, add `latest.json`/`latest.json.sig`, or deploy the
Pages site until the Windows package and every existing netdisk link have passed the
release gate.
