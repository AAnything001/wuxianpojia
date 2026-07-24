# Site Typography System Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Apply one responsive, system-font typography standard to all 55 production HTML pages without loading external font files or changing page content and layout.

**Architecture:** Add `assets/typography.css` as the final stylesheet on every production page. The shared file owns font stacks, type tokens and semantic overrides; existing page CSS continues to own color, spacing, layout and motion. Static Python contract tests verify the stylesheet, load order and full-page coverage before browser checks validate computed sizes and wrapping.

**Tech Stack:** Static HTML/CSS, Python `unittest`, PowerShell and local `python -m http.server`.

## Global Constraints

- Use only local system fonts; add no `@font-face`, remote font URL or third-party request.
- Body text is 16px with 1.75 line height on desktop and mobile.
- Homepage H1 uses `clamp(34px, 4vw, 52px)` after user visual review; inner-page H1 uses `clamp(36px, 4.5vw, 52px)`.
- H2 uses `clamp(28px, 3.5vw, 40px)`; H3 is 20px desktop and 18px mobile.
- Navigation and buttons remain 14–15px; captions and disclaimers never fall below 12px.
- Chinese heading tracking is no tighter than `-0.025em`; body tracking is zero.
- Do not change page copy, colors, layout structure, purchase links or behavior.
- Load `/assets/typography.css` after inline styles and `/assets/site-footer.css`.

---

### Task 1: Define the typography contract

**Files:**
- Create: `tests/test_typography_system.py`
- Reference: `docs/superpowers/specs/2026-07-24-site-typography-system-design.md`

**Interfaces:**
- Consumes: the 55-file production set defined by root `*.html` plus `knowledge/*.html`.
- Produces: test contracts for `assets/typography.css` and the exact stylesheet link `<link rel="stylesheet" href="/assets/typography.css">`.

- [ ] **Step 1: Write the failing contract tests**

```python
from html.parser import HTMLParser
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
ROOT_HTML = sorted(REPO_ROOT.glob("*.html"))
KNOWLEDGE_HTML = sorted(REPO_ROOT.joinpath("knowledge").glob("*.html"))
TYPOGRAPHY_HREF = "/assets/typography.css"
FOOTER_HREF = "/assets/site-footer.css"


class StylesheetCollector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stylesheets = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "link" and "stylesheet" in attributes.get("rel", "").split():
            self.stylesheets.append(attributes.get("href"))


def stylesheets(path):
    collector = StylesheetCollector()
    collector.feed(path.read_text(encoding="utf-8"))
    return collector.stylesheets


class TypographySystemTests(unittest.TestCase):
    def test_production_page_inventory_is_stable(self):
        self.assertEqual(4, len(ROOT_HTML))
        self.assertEqual(51, len(KNOWLEDGE_HTML))

    def test_shared_stylesheet_contract(self):
        css_path = REPO_ROOT / "assets" / "typography.css"
        self.assertTrue(css_path.is_file())
        css = css_path.read_text(encoding="utf-8")
        for token in (
            "--font-sans:",
            "--font-mono:",
            "--type-display: clamp(34px, 4vw, 52px)",
            "--type-h1: clamp(36px, 4.5vw, 52px)",
            "--type-h2: clamp(28px, 3.5vw, 40px)",
            "--type-body: 1rem",
            "text-size-adjust: 100%",
        ):
            self.assertIn(token, css)
        self.assertNotIn("@font-face", css)
        self.assertNotIn("url(", css)

    def test_homepage_loads_typography_last(self):
        links = stylesheets(REPO_ROOT / "index.html")
        self.assertEqual(1, links.count(TYPOGRAPHY_HREF))
        self.assertEqual(TYPOGRAPHY_HREF, links[-1])

    def test_secondary_root_pages_load_typography_last(self):
        for path in ROOT_HTML:
            with self.subTest(path=path.name):
                links = stylesheets(path)
                self.assertEqual(1, links.count(TYPOGRAPHY_HREF))
                self.assertEqual(TYPOGRAPHY_HREF, links[-1])

    def test_knowledge_pages_load_typography_last(self):
        for path in KNOWLEDGE_HTML:
            with self.subTest(path=path.name):
                links = stylesheets(path)
                self.assertEqual(1, links.count(TYPOGRAPHY_HREF))
                self.assertEqual(TYPOGRAPHY_HREF, links[-1])
                self.assertLess(links.index(FOOTER_HREF), links.index(TYPOGRAPHY_HREF))


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the tests and verify the red state**

Run: `python -m unittest tests.test_typography_system -v`

Expected: inventory passes; stylesheet and page-link tests fail because `assets/typography.css` and its links do not yet exist.

- [ ] **Step 3: Commit the contract**

```powershell
git add tests/test_typography_system.py
git commit -m "test: define site typography contract"
```

### Task 2: Implement the shared system and homepage slice

**Files:**
- Create: `assets/typography.css`
- Modify: `index.html`
- Test: `tests/test_typography_system.py`

**Interfaces:**
- Consumes: the token names asserted by Task 1.
- Produces: global custom properties and semantic type rules used by every later page.

- [ ] **Step 1: Create the shared stylesheet**

```css
:root {
  --font-sans: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI",
    "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei",
    "Noto Sans CJK SC", "Noto Sans SC", Arial, sans-serif;
  --font-mono: "Cascadia Code", "SFMono-Regular", Consolas,
    "Liberation Mono", monospace;
  --type-display: clamp(34px, 4vw, 52px);
  --type-h1: clamp(36px, 4.5vw, 52px);
  --type-h2: clamp(28px, 3.5vw, 40px);
  --type-h3: 1.25rem;
  --type-lead: 1.125rem;
  --type-body: 1rem;
  --type-ui: 0.9375rem;
  --type-small: 0.875rem;
  --type-caption: 0.75rem;
  --weight-body: 400;
  --weight-medium: 550;
  --weight-ui: 680;
  --weight-heading: 730;
  --leading-display: 1.12;
  --leading-h1: 1.16;
  --leading-h2: 1.22;
  --leading-h3: 1.4;
  --leading-body: 1.75;
  --leading-small: 1.65;
}

html {
  font-size: 100%;
  -webkit-text-size-adjust: 100%;
  text-size-adjust: 100%;
}

body {
  font-family: var(--font-sans);
  font-size: var(--type-body);
  font-weight: var(--weight-body);
  line-height: var(--leading-body);
  letter-spacing: 0;
}

button,
input,
select,
textarea {
  font: inherit;
}

h1,
h2,
h3,
h4,
h5,
h6 {
  font-family: var(--font-sans);
  text-wrap: balance;
}

h1,
.hero h1 {
  font-size: var(--type-h1);
  font-weight: var(--weight-heading);
  line-height: var(--leading-h1);
  letter-spacing: -0.025em;
}

h2,
.section h2,
.cta h2 {
  font-size: var(--type-h2);
  font-weight: var(--weight-heading);
  line-height: var(--leading-h2);
  letter-spacing: -0.02em;
}

h3,
.card h3,
.step h3 {
  font-size: var(--type-h3);
  font-weight: 700;
  line-height: var(--leading-h3);
  letter-spacing: -0.01em;
}

.lead,
.section-lead,
.article .lead {
  font-size: var(--type-lead);
  line-height: var(--leading-body);
}

.article p,
.article li,
.card p,
.step p,
.faq p,
.pricecard li,
.download-box p {
  font-size: var(--type-body);
  line-height: var(--leading-body);
}

.navlinks,
.navcta,
.primary,
.secondary,
.download-btn,
.actions a {
  font-size: var(--type-ui);
  font-weight: var(--weight-ui);
  line-height: 1.4;
}

.eyebrow {
  font-size: var(--type-caption);
  font-weight: 700;
  line-height: 1.5;
  letter-spacing: 0.08em;
}

.micro,
.topline,
.bar,
.badge,
.trial-badge,
.site-footer__bottom {
  font-size: var(--type-caption);
  line-height: 1.6;
}

.a .hero h1 {
  font-size: var(--type-display);
  font-weight: 750;
  line-height: var(--leading-display);
  letter-spacing: -0.025em;
}

.a .lead,
.a .section-lead {
  font-size: var(--type-lead);
}

.a .card p,
.a .pricecard li,
.a .download-box p {
  font-size: var(--type-body);
}

.a .free-modules-tier-copy {
  font-size: var(--type-body);
  line-height: var(--leading-body);
}

.a .free-modules-number strong {
  font-size: 30px;
  line-height: 1.15;
}

.a .free-modules-number span,
.a .free-modules-categories span {
  font-size: 13px;
}

.article-link span,
.related a {
  font-size: var(--type-small);
  line-height: var(--leading-small);
}

.site-footer,
.site-footer__brand-tagline,
.site-footer__section-title,
.site-footer__links {
  font-size: var(--type-small);
  line-height: var(--leading-small);
}

code,
pre,
kbd,
samp {
  font-family: var(--font-mono);
}

@media (max-width: 720px) {
  :root {
    --type-h3: 1.125rem;
    --type-lead: 1.0625rem;
  }

  .a .hero h1 {
    font-size: 34px;
  }

  .a .free-modules-number strong {
    font-size: 28px;
  }

  h1,
  .hero h1 {
    font-size: 36px;
  }

  h2,
  .section h2,
  .cta h2 {
    font-size: 28px;
  }

  .a h1 .title-line,
  .a h1 .title-accent {
    white-space: normal;
  }
}
```

- [ ] **Step 2: Remove the two legacy homepage H1 `!important` overrides**

Delete these declarations from `index.html` while leaving the adjacent desktop spacing media rule intact:

```css
.a .hero h1{font-size:clamp(36px,3.6vw,52px)!important}
@media(max-width:600px){.a .hero h1{font-size:28px!important}}
```

- [ ] **Step 3: Load the stylesheet last on the homepage**

Add immediately before `</head>` and after every existing stylesheet/style block:

```html
<link rel="stylesheet" href="/assets/typography.css">
```

- [ ] **Step 4: Verify the homepage slice**

Run:

```powershell
python -m unittest `
  tests.test_typography_system.TypographySystemTests.test_shared_stylesheet_contract `
  tests.test_typography_system.TypographySystemTests.test_homepage_loads_typography_last -v
```

Expected: 2 tests pass.

- [ ] **Step 5: Commit the homepage slice**

```powershell
git add assets/typography.css index.html
git commit -m "feat: add shared typography system"
```

### Task 3: Connect secondary root pages and footer

**Files:**
- Modify: `codex-pojia.html`
- Modify: `培训文案.html`
- Modify: `user-notice.html`
- Modify: `assets/site-footer.css`
- Test: `tests/test_typography_system.py`

**Interfaces:**
- Consumes: all custom properties from `assets/typography.css`.
- Produces: typography coverage for the four root HTML pages and a footer that reads the shared tokens.

- [ ] **Step 1: Add the final stylesheet link to each secondary page**

Add this after `/assets/site-footer.css` and all inline style blocks:

```html
<link rel="stylesheet" href="/assets/typography.css">
```

- [ ] **Step 2: Make the shared footer consume the typography tokens**

Replace the three declarations at the start of `.site-footer`:

```css
font-family: Inter, "Segoe UI", "Microsoft YaHei", sans-serif;
font-size: 13px;
line-height: 1.65;
```

with:

```css
font-family: var(--font-sans);
font-size: var(--type-small);
line-height: var(--leading-small);
```

- [ ] **Step 3: Verify all root pages**

Run: `python -m unittest tests.test_typography_system.TypographySystemTests.test_secondary_root_pages_load_typography_last tests.test_site_footer -v`

Expected: typography root-page test and all existing footer tests pass.

- [ ] **Step 4: Commit the secondary-page slice**

```powershell
git add codex-pojia.html 培训文案.html user-notice.html assets/site-footer.css
git commit -m "feat: apply typography to core pages"
```

### Task 4: Connect all knowledge pages

**Files:**
- Modify: `knowledge/index.html`
- Modify: `knowledge/*.html` (all 51 files)
- Test: `tests/test_typography_system.py`

**Interfaces:**
- Consumes: `/assets/typography.css` and the existing `/assets/site-footer.css` marker.
- Produces: exactly one final typography link on every knowledge page.

- [ ] **Step 1: Insert the link mechanically while preserving encoding and newline style**

Run from the repository root:

```powershell
$typographyMarker = '  <link rel="stylesheet" href="/assets/site-footer.css">'
$typographyLink = '  <link rel="stylesheet" href="/assets/typography.css">'
Get-ChildItem -LiteralPath '.\knowledge' -Filter '*.html' -File | ForEach-Object {
    $content = [IO.File]::ReadAllText($_.FullName)
    if ($content.Contains($typographyLink)) {
        throw "Typography link already exists: $($_.FullName)"
    }
    if (-not $content.Contains($typographyMarker)) {
        throw "Footer stylesheet marker missing: $($_.FullName)"
    }
    $newline = if ($content.Contains("`r`n")) { "`r`n" } else { "`n" }
    $updated = $content.Replace(
        $typographyMarker,
        $typographyMarker + $newline + $typographyLink
    )
    [IO.File]::WriteAllText(
        $_.FullName,
        $updated,
        [Text.UTF8Encoding]::new($false)
    )
}
```

- [ ] **Step 2: Verify knowledge coverage**

Run: `python -m unittest tests.test_typography_system.TypographySystemTests.test_knowledge_pages_load_typography_last -v`

Expected: 1 test passes with all 51 subtests passing.

- [ ] **Step 3: Inspect the mechanical diff**

Run: `git diff --stat -- knowledge; git diff --check -- knowledge`

Expected: 51 HTML files changed, one link added to each, and no whitespace errors.

- [ ] **Step 4: Commit the knowledge slice**

```powershell
git add knowledge
git commit -m "feat: apply typography to knowledge pages"
```

### Task 5: Full automated verification and local preview

**Files:**
- Verify: all production HTML/CSS and tests
- No screenshots or visual-automation artifacts are created; the user performs final visual review.

**Interfaces:**
- Consumes: completed typography system and all page links.
- Produces: passing automated tests and a live isolated-worktree preview at port 4174.

- [ ] **Step 1: Run all automated tests**

Run: `python -m unittest discover -s tests -v`

Expected: all tests pass with zero failures and zero errors.

- [ ] **Step 2: Start the isolated local server**

Run from the typography worktree:

```powershell
Start-Process -FilePath python `
  -ArgumentList '-m','http.server','4174','--directory',(Get-Location).Path `
  -WindowStyle Hidden
```

Expected: the server listens on port 4174 without changing the existing port 4173 preview.

- [ ] **Step 3: Verify the preview endpoints and hand visual review to the user**

Check these routes with `Invoke-WebRequest`:

```text
/
/codex-pojia.html
/%E5%9F%B9%E8%AE%AD%E6%96%87%E6%A1%88.html
/user-notice.html
/knowledge/
/knowledge/codex-pojia-what-is.html
```

```powershell
$previewRoutes = @(
  '/',
  '/codex-pojia.html',
  '/%E5%9F%B9%E8%AE%AD%E6%96%87%E6%A1%88.html',
  '/user-notice.html',
  '/knowledge/',
  '/knowledge/codex-pojia-what-is.html'
)
foreach ($route in $previewRoutes) {
  $response = Invoke-WebRequest -Uri ("http://127.0.0.1:4174" + $route) -UseBasicParsing
  if ($response.StatusCode -ne 200) { throw "Preview failed: $route" }
}
```

Expected: all six routes return HTTP 200. Give the user `http://127.0.0.1:4174/?variant=A` for their own desktop/mobile visual inspection; do not take screenshots.

- [ ] **Step 4: Inspect the final repository delta**

Run:

```powershell
git status --short
git diff HEAD~3 --stat
git log -4 --oneline
```

Expected: typography work is contained to the test, shared stylesheet, footer stylesheet and 55 production HTML files; pre-existing unrelated untracked files remain untouched.
