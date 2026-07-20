# Google Invisible SEO Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Improve Google crawlability, canonical understanding, page-entity metadata, and static asset delivery for the three existing pages without changing layout, styles, or visible body content.

**Architecture:** Keep the static Cloudflare Pages site and its canonical routing unchanged. Add only head metadata and JSON-LD to the three HTML files, add a Cloudflare Pages `_headers` configuration for non-HTML resources and baseline response headers, and refresh the three canonical sitemap timestamps. Verify exact `<body>` hashes before and after the change, then validate structured data, XML, Git scope, GitHub push, and the deployed production responses.

**Tech Stack:** Static HTML5, JSON-LD/Schema.org, XML Sitemap, Cloudflare Pages `_headers`, PowerShell, Git/GitHub

## Global Constraints

- Do not change DOM layout, CSS visual effects, or user-visible body copy.
- Preserve every existing `<title>` and `meta description` value.
- Do not add hidden keywords, doorway pages, duplicate URLs, or structured claims absent from visible content.
- Keep only the three canonical URLs in `sitemap.xml`; never add `.html` redirects, anchors, assets, or external URLs.
- Stage and commit only files owned by this task; preserve unrelated untracked workspace files.
- Ranking is not an acceptance criterion; crawlability, canonicalization, semantic validity, and deployment are.

---

### Task 1: Add non-visible page metadata and entity graphs

**Files:**
- Modify: `index.html`
- Modify: `codex-pojia.html`
- Modify: `培训文案.html`

**Interfaces:**
- Consumes: Existing title, description, canonical URL, visible FAQ copy, and homepage `Organization`/`WebSite`/`SoftwareApplication` entities.
- Produces: One canonical metadata set and one valid JSON-LD graph per page, using stable `#webpage`, `#breadcrumb`, `#faq`, `#website`, `#organization`, and `#software` identifiers.

- [ ] **Step 1: Record the body-content invariant**

Run:

```powershell
$files=@('index.html','codex-pojia.html','培训文案.html')
foreach($f in $files){
  $text=Get-Content -Raw -Encoding UTF8 $f
  $body=[regex]::Match($text,'(?s)<body>.*</body>').Value
  $sha=[Security.Cryptography.SHA256]::Create()
  try {
    $hash=$sha.ComputeHash([Text.Encoding]::UTF8.GetBytes($body))
    '{0} {1}' -f $f,(([BitConverter]::ToString($hash)).Replace('-','').ToLower())
  } finally { $sha.Dispose() }
}
```

Expected:

```text
index.html 8fb0a0efcb7fee36b7fbca6d6546d5e653291b74064a273ac8e8c89b15375d21
codex-pojia.html c09f2e47e885db795b366852afc6a43d0cad40ab1e1ce59694449981d1f5c1ae
培训文案.html 43818732b6fb5f54da4b74f2e28fc889010943b5788e4c455f049511e0473a2f
```

- [ ] **Step 2: Add the metadata contract to each page head**

Add exactly one `meta robots` with:

```html
<meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1">
```

Add Open Graph fields for type, locale, site name, existing title, existing description, canonical URL, and the existing 1099×701 product screenshot. Add Twitter `summary_large_image`, title, description, and image fields with the same values. Add a homepage preload for `assets/app-QQ20260716-215120.png` with `as="image"` and `fetchpriority="high"`.

- [ ] **Step 3: Connect the JSON-LD entities**

In `index.html`, retain the current three entities and append:

```json
{
  "@type": "WebPage",
  "@id": "https://codexpojia.com/#webpage",
  "url": "https://codexpojia.com/",
  "name": "Codex 破甲｜无限破甲 - AI 逆向分析与 CTF 学习路线",
  "description": "无限破甲支持 Codex、Claude、Kiro 等 AI 客户端，提供 Skill、MCP 配置及 CTF 软件逆向学习路线，帮助用户从问题识别走到证据整理。",
  "inLanguage": "zh-CN",
  "isPartOf": {"@id": "https://codexpojia.com/#website"},
  "about": {"@id": "https://codexpojia.com/#software"},
  "mainEntity": {"@id": "https://codexpojia.com/#software"}
}
```

In `codex-pojia.html`, convert the single FAQ object to an `@graph` containing `WebPage`, the unchanged `FAQPage`, and a two-item `BreadcrumbList`. In `培训文案.html`, add an `@graph` containing `WebPage` and a two-item `BreadcrumbList`. Use canonical URLs for all identifiers and do not add author, rating, date, search action, or review fields.

- [ ] **Step 4: Validate head uniqueness, JSON-LD, and exact body hashes**

Run a PowerShell validation that asserts one `<title>`, one description, one canonical, and one robots tag per file; extracts every `application/ld+json` block and parses it with `ConvertFrom-Json`; then rerun Step 1.

Expected: all assertions pass, JSON parsing emits no exception, and all three hashes exactly match Step 1.

- [ ] **Step 5: Review the isolated HTML diff**

Run:

```powershell
git diff --check -- index.html codex-pojia.html 培训文案.html
git diff -- index.html codex-pojia.html 培训文案.html
```

Expected: changes occur only before `</head>`; no body or CSS line changes appear.

---

### Task 2: Add Cloudflare response configuration and refresh sitemap dates

**Files:**
- Create: `_headers`
- Modify: `sitemap.xml`

**Interfaces:**
- Consumes: Cloudflare Pages static deployment with output directory `.` and the three canonical URLs.
- Produces: Browser-safe baseline headers, a seven-day revalidating asset cache, one-hour crawler-file cache, and accurate sitemap modification dates.

- [ ] **Step 1: Create `_headers`**

Create:

```text
/*
  Referrer-Policy: strict-origin-when-cross-origin
  X-Content-Type-Options: nosniff
  X-Frame-Options: SAMEORIGIN
  Permissions-Policy: camera=(), geolocation=(), microphone=()

/assets/*
  Cache-Control: public, max-age=604800, stale-while-revalidate=86400

/robots.txt
  Cache-Control: public, max-age=3600, must-revalidate

/sitemap.xml
  Cache-Control: public, max-age=3600, must-revalidate
```

Do not set `immutable` because asset filenames are not content-hashed. Do not override the current revalidating HTML cache.

- [ ] **Step 2: Refresh sitemap timestamps**

Change each of the three `<lastmod>` values from `2026-07-19` to `2026-07-20`. Do not change URL spelling, ordering, priority, or count.

- [ ] **Step 3: Validate XML and header rules**

Run:

```powershell
[xml](Get-Content -Raw -Encoding UTF8 sitemap.xml) | Out-Null
$xml=[xml](Get-Content -Raw -Encoding UTF8 sitemap.xml)
if($xml.urlset.url.Count -ne 3){throw 'sitemap URL count must be 3'}
if((Get-Content -Raw _headers) -match 'immutable'){throw 'unversioned assets must not be immutable'}
git diff --check -- _headers sitemap.xml
```

Expected: no output and exit code 0.

---

### Task 3: Commit, push, and verify Cloudflare production

**Files:**
- Commit: `index.html`
- Commit: `codex-pojia.html`
- Commit: `培训文案.html`
- Commit: `_headers`
- Commit: `sitemap.xml`
- Commit: `docs/superpowers/plans/2026-07-20-google-invisible-seo.md`

**Interfaces:**
- Consumes: Validated local static files, `origin` GitHub remote, `main` production branch, and Cloudflare Pages Git integration.
- Produces: A scoped Git commit on `main`, an updated `origin/main`, and verified production content at `https://codexpojia.com`.

- [ ] **Step 1: Run the full local verification**

Repeat the Task 1 and Task 2 validations. Check `git diff --check`. Confirm `git status --short` shows the five implementation files, this plan, and only pre-existing unrelated untracked files.

- [ ] **Step 2: Stage only task-owned files**

Run:

```powershell
git add -- index.html codex-pojia.html 培训文案.html _headers sitemap.xml docs/superpowers/plans/2026-07-20-google-invisible-seo.md
git diff --cached --check
git diff --cached --stat
```

Expected: no unrelated file is staged.

- [ ] **Step 3: Commit and push production branch**

Run:

```powershell
git commit -m "feat: strengthen invisible Google SEO signals"
git push origin main
```

Expected: commit succeeds and `origin/main` advances to the new commit.

- [ ] **Step 4: Wait for Cloudflare Pages deployment**

Poll the homepage response for the new `meta robots` marker and the asset response for `Cache-Control: public, max-age=604800, stale-while-revalidate=86400`, using bounded retries of no more than 60 seconds per attempt.

Expected: both markers appear on `codexpojia.com`, proving the Git-integrated production deployment completed.

- [ ] **Step 5: Verify all production routes**

Check HTTP 200 for the three canonical URLs, `/robots.txt`, and `/sitemap.xml`. Check permanent redirects from `/index.html`, `/codex-pojia.html`, and the encoded training `.html` URL to their canonical paths. Fetch all three HTML pages and confirm the new robots metadata and canonical URLs are present.

Expected: canonical resources return 200, legacy HTML routes return 308 with correct `Location`, and production HTML/headers match the committed implementation.
