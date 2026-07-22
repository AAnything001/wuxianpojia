# Codex Knowledge Base Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a low-profile visible Codex 破甲 knowledge base with 50 static article pages, footer entry points, sitemap coverage, GitHub push, and Cloudflare verification.

**Architecture:** The site is static HTML served by Cloudflare Pages from the repository root. Add `knowledge/index.html` plus 50 `knowledge/*.html` article files, link them from existing page footers, and add every canonical URL to `sitemap.xml`.

**Tech Stack:** Static HTML, inline CSS matching existing landing pages, JSON-LD, XML sitemap, GitHub `main`, Cloudflare Pages.

## Global Constraints

- Do not hide articles or keyword text from users.
- Keep homepage and `codex-pojia` conversion sections unchanged.
- Use visible low-profile footer links only.
- Target keywords: `codexpojia`, `codex破甲`, `codex逆向`, `ai逆向`, `codex逆向`.
- Use deployment date `2026-07-22` for new `lastmod` and article modified dates.
- Do not stage unrelated untracked files.

---

### Task 1: Generate Knowledge Base Pages

**Files:**
- Create: `knowledge/index.html`
- Create: `knowledge/*.html` for 50 article pages

**Interfaces:**
- Consumes: existing static asset `assets/brand-gradient.svg`
- Produces: canonical URL set under `https://codexpojia.com/knowledge/`

- [ ] **Step 1: Create the knowledge directory**

Run: `New-Item -ItemType Directory -Force -Path knowledge`

- [ ] **Step 2: Generate 50 visible article pages**

Each article must include one H1, visible body text, a canonical URL, robots meta, keywords meta, Open Graph fields, and Article JSON-LD.

- [ ] **Step 3: Generate `knowledge/index.html`**

The index must list 5 categories with 10 article links each.

- [ ] **Step 4: Verify file count**

Run: `(Get-ChildItem knowledge -Filter *.html).Count`
Expected: `51`

### Task 2: Add Low-Profile Footer Entry Points

**Files:**
- Modify: `index.html`
- Modify: `codex-pojia.html`

**Interfaces:**
- Consumes: `knowledge/index.html`
- Produces: visible footer link text `Codex 破甲知识库`

- [ ] **Step 1: Add footer entry to homepage**

Add a weak footer link to `knowledge/` next to the existing SEO link.

- [ ] **Step 2: Add footer entry to Codex topic page**

Add a weak footer link to `knowledge/` next to existing footer links.

- [ ] **Step 3: Verify link exists**

Run: `rg -n "Codex 破甲知识库|knowledge/" index.html codex-pojia.html`
Expected: both files contain the link.

### Task 3: Update Sitemap

**Files:**
- Modify: `sitemap.xml`

**Interfaces:**
- Consumes: all canonical URLs produced by Task 1
- Produces: XML sitemap with 54 URLs

- [ ] **Step 1: Add knowledge base index URL**

Add `https://codexpojia.com/knowledge/`.

- [ ] **Step 2: Add 50 article canonical URLs**

Each article URL uses the no-extension canonical form.

- [ ] **Step 3: Verify XML**

Run: `[xml]$sitemap = Get-Content sitemap.xml -Raw; $sitemap.urlset.url.Count`
Expected: `54`

### Task 4: Verify, Commit, Push, and Check Cloudflare

**Files:**
- All files from Tasks 1-3
- Spec and plan docs

**Interfaces:**
- Consumes: local static files and Git remote `origin/main`
- Produces: pushed commit and live Cloudflare pages

- [ ] **Step 1: Parse JSON-LD**

Run a PowerShell parser across `knowledge/*.html`, `index.html`, and `codex-pojia.html`.
Expected: no JSON parse errors.

- [ ] **Step 2: Check diff cleanliness**

Run: `git diff --check`
Expected: no whitespace errors.

- [ ] **Step 3: Stage only relevant files**

Stage `knowledge/`, `index.html`, `codex-pojia.html`, `sitemap.xml`, and the two Codex knowledge base docs.

- [ ] **Step 4: Commit**

Run: `git commit -m "feat: add codex knowledge base"`

- [ ] **Step 5: Push**

Run: `git push origin main`

- [ ] **Step 6: Verify Cloudflare live content**

Fetch `https://codexpojia.com/knowledge/`, one sample article, and `https://codexpojia.com/sitemap.xml`.
Expected: index and sample article return keyword content, sitemap contains `knowledge/`.

