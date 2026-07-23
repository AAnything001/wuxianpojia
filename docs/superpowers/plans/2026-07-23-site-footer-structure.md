# codexpojia.com Unified Site Footer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace all 55 static HTML footers with one responsive, crawlable footer modeled on the information hierarchy of `https://www.xlsxdiffmerge.com/license`, including a reciprocal link to `https://www.xlsxdiffmerge.com/`.

**Architecture:** Keep the footer markup in every HTML file so links remain available without JavaScript, and centralize only the presentation in `assets/site-footer.css`. Use one temporary, assertion-heavy Python rewrite script to update the known root and `knowledge/` HTML files without touching page bodies, then remove that script before the implementation commit.

**Tech Stack:** Static HTML5, CSS3, Python 3 standard library `unittest` and `html.parser`, Playwright Chromium CLI, Cloudflare Pages clean URLs.

## Global Constraints

- Modify all 55 existing HTML pages and no page-body content outside the old footer and the new stylesheet link.
- Do not modify download URLs, payment URLs, `downloads/wujin/stable/latest.json`, `downloads/wujin/stable/latest.json.sig`, CDK/activation behavior, or update signing logic.
- Preserve the exact partner target URL `https://www.xlsxdiffmerge.com/`.
- Render the footer as static HTML; do not inject it with JavaScript or load third-party runtime assets.
- Store the partner logo locally at `assets/partners/xlsxdiffmerge-logo.png`.
- Use root-relative internal links so the same markup works at the site root and under `/knowledge/`.
- Keep existing unrelated untracked files untouched and stage only files named in each task.
- Do not push or deploy without a separate explicit publish instruction.

## File Map

- Create `tests/test_site_footer.py`: structural contract for all HTML footers, shared CSS, partner asset, internal links, and external-link safety attributes.
- Create `assets/site-footer.css`: the sole source of footer layout, color, focus, and responsive behavior.
- Create `assets/partners/xlsxdiffmerge-logo.png`: local copy of the reference site's public product logo.
- Modify `index.html`, `codex-pojia.html`, `培训文案.html`, `user-notice.html`: add the shared stylesheet and unified footer markup.
- Modify `knowledge/index.html` and all 50 `knowledge/*.html` article pages: add the shared stylesheet and same unified footer markup.
- Temporarily create and then remove `tools/update_site_footer.py`: guarded mechanical rewrite; it must not exist in the final commit.

---

### Task 1: Add the footer contract test

**Files:**
- Create: `tests/test_site_footer.py`

**Interfaces:**
- Consumes: the 55 root and `knowledge/` HTML files.
- Produces: `SiteFooterTests`, which defines the exact markup and asset contract later tasks must satisfy.

- [ ] **Step 1: Write the failing structural test**

Create `tests/test_site_footer.py` with:

```python
from html.parser import HTMLParser
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
HTML_FILES = sorted(
    [*REPO_ROOT.glob("*.html"), *REPO_ROOT.joinpath("knowledge").glob("*.html")]
)
INTERNAL_LINKS = {
    "/",
    "/#download",
    "/#a-updates",
    "/codex-pojia",
    "/knowledge/",
    "/培训文案",
    "/user-notice",
}
PARTNER_URL = "https://www.xlsxdiffmerge.com/"
PAYMENT_LINKS = {
    "https://pay.ldxp.cn/item/bz252j",
    "https://pay.ldxp.cn/item/r778vo",
}


class FooterCollector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.footer_depth = 0
        self.footer_count = 0
        self.footer_classes = set()
        self.footer_links = []
        self.stylesheets = []
        self.images = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "link" and "stylesheet" in attributes.get("rel", "").split():
            self.stylesheets.append(attributes.get("href"))
        if tag == "footer":
            self.footer_count += 1
            self.footer_depth += 1
            self.footer_classes.update(attributes.get("class", "").split())
            return
        if not self.footer_depth:
            return
        if tag == "a":
            self.footer_links.append(attributes)
        elif tag == "img":
            self.images.append(attributes)

    def handle_endtag(self, tag):
        if tag == "footer" and self.footer_depth:
            self.footer_depth -= 1


class SiteFooterTests(unittest.TestCase):
    def parse(self, path):
        collector = FooterCollector()
        collector.feed(path.read_text(encoding="utf-8"))
        return collector

    def test_all_55_html_pages_use_the_shared_footer(self):
        self.assertEqual(55, len(HTML_FILES))
        for path in HTML_FILES:
            with self.subTest(path=path.relative_to(REPO_ROOT)):
                footer = self.parse(path)
                self.assertEqual(1, footer.footer_count)
                self.assertIn("site-footer", footer.footer_classes)
                self.assertEqual(1, footer.stylesheets.count("/assets/site-footer.css"))

    def test_every_footer_has_required_internal_and_partner_links(self):
        for path in HTML_FILES:
            with self.subTest(path=path.relative_to(REPO_ROOT)):
                footer = self.parse(path)
                hrefs = {link.get("href") for link in footer.footer_links}
                self.assertTrue(INTERNAL_LINKS.issubset(hrefs))
                self.assertTrue(PAYMENT_LINKS.issubset(hrefs))
                self.assertIn(PARTNER_URL, hrefs)
                partner = next(link for link in footer.footer_links if link.get("href") == PARTNER_URL)
                self.assertEqual("_blank", partner.get("target"))
                self.assertEqual({"noopener", "noreferrer"}, set(partner.get("rel", "").split()))

    def test_partner_logo_is_local_and_accessible(self):
        expected_src = "/assets/partners/xlsxdiffmerge-logo.png"
        for path in HTML_FILES:
            with self.subTest(path=path.relative_to(REPO_ROOT)):
                footer = self.parse(path)
                logo = next(image for image in footer.images if image.get("src") == expected_src)
                self.assertEqual("XlsxDiffMerge", logo.get("alt"))
                self.assertEqual("44", logo.get("width"))
                self.assertEqual("44", logo.get("height"))

        logo_path = REPO_ROOT / "assets" / "partners" / "xlsxdiffmerge-logo.png"
        self.assertTrue(logo_path.is_file())
        self.assertEqual(b"\x89PNG\r\n\x1a\n", logo_path.read_bytes()[:8])

    def test_shared_styles_cover_focus_and_breakpoints(self):
        css = (REPO_ROOT / "assets" / "site-footer.css").read_text(encoding="utf-8")
        self.assertIn(".site-footer", css)
        self.assertIn(":focus-visible", css)
        self.assertIn("@media (max-width: 899px)", css)
        self.assertIn("@media (max-width: 600px)", css)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the test and verify the expected failure**

Run:

```powershell
python -m unittest tests.test_site_footer -v
```

Expected: four tests fail because existing pages do not use `.site-footer`, `assets/site-footer.css` and the local partner logo do not exist, and the partner URL is absent.

- [ ] **Step 3: Commit the failing test**

```powershell
git add -- tests/test_site_footer.py
git commit -m "test: define unified site footer contract"
```

### Task 2: Add shared footer presentation and partner asset

**Files:**
- Create: `assets/site-footer.css`
- Create: `assets/partners/xlsxdiffmerge-logo.png`

**Interfaces:**
- Consumes: class names specified in Task 3's footer markup.
- Produces: a responsive presentation for `.site-footer` and a local 44x44 partner logo.

- [ ] **Step 1: Download the public partner logo to a local asset path**

```powershell
New-Item -ItemType Directory -Force -Path 'assets\partners' | Out-Null
Invoke-WebRequest -UseBasicParsing -Uri 'https://www.xlsxdiffmerge.com/logo.png' -OutFile 'assets\partners\xlsxdiffmerge-logo.png'
```

Expected: the file begins with the PNG signature and the current official asset is `14486` bytes.

- [ ] **Step 2: Add the complete shared stylesheet**

Create `assets/site-footer.css` with:

```css
footer.site-footer {
  --footer-bg: #0b1019;
  --footer-panel: #111925;
  --footer-line: #263143;
  --footer-text: #f4f6fa;
  --footer-muted: #a6afbd;
  --footer-accent: #ff5268;
  margin: 0;
  padding: 0;
  border: 0;
  background: var(--footer-bg);
  color: var(--footer-muted);
  font-family: Inter, "Segoe UI", "Microsoft YaHei", sans-serif;
  font-size: 13px;
  line-height: 1.65;
  text-align: left;
}

footer.site-footer,
footer.site-footer * {
  box-sizing: border-box;
}

footer.site-footer a {
  color: inherit;
  text-decoration: none;
}

footer.site-footer a:hover {
  color: var(--footer-text);
}

footer.site-footer a:focus-visible {
  outline: 2px solid var(--footer-accent);
  outline-offset: 4px;
  border-radius: 4px;
}

.site-footer__inner {
  width: min(1180px, calc(100% - 32px));
  margin: 0 auto;
}

.site-footer__main {
  display: grid;
  grid-template-columns: minmax(260px, 1.35fr) repeat(3, minmax(150px, 0.72fr));
  gap: 46px;
  padding: 58px 0 42px;
}

.site-footer__brand-link {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  min-height: 44px;
  color: var(--footer-text);
}

footer.site-footer img.site-footer__brand-logo,
footer.site-footer img.site-footer__partner-logo {
  display: block;
  flex: 0 0 auto;
  object-fit: contain;
}

footer.site-footer img.site-footer__brand-logo {
  width: 42px;
  height: 42px;
}

.site-footer__brand-name,
.site-footer__partner-name {
  display: block;
  color: var(--footer-text);
  font-weight: 900;
}

.site-footer__brand-tagline {
  max-width: 310px;
  margin: 18px 0 0;
  color: var(--footer-muted);
}

.site-footer__section-title {
  display: block;
  margin: 0 0 14px;
  color: var(--footer-text);
  font-size: 13px;
  font-weight: 900;
}

.site-footer__links {
  display: grid;
  gap: 4px;
}

.site-footer__links a,
.site-footer__links span {
  display: flex;
  align-items: center;
  min-height: 40px;
}

.site-footer__partners {
  display: grid;
  grid-template-columns: 120px minmax(0, 1fr);
  align-items: center;
  gap: 18px;
  padding: 22px 0;
  border-top: 1px solid var(--footer-line);
  border-bottom: 1px solid var(--footer-line);
}

.site-footer__partners-label {
  color: var(--footer-text);
  font-weight: 900;
}

.site-footer__partner-link {
  display: flex;
  align-items: center;
  gap: 13px;
  min-width: 0;
  min-height: 72px;
  padding: 12px 15px;
  border: 1px solid var(--footer-line);
  border-radius: 8px;
  background: var(--footer-panel);
  transition: border-color 160ms ease, background-color 160ms ease;
}

.site-footer__partner-link:hover {
  border-color: #46546b;
  background: #151f2d;
}

footer.site-footer img.site-footer__partner-logo {
  width: 44px;
  height: 44px;
  border-radius: 8px;
}

.site-footer__partner-copy {
  min-width: 0;
}

.site-footer__partner-domain {
  display: block;
  overflow-wrap: anywhere;
  color: var(--footer-muted);
  font-size: 11px;
}

.site-footer__partner-arrow {
  margin-left: auto;
  color: var(--footer-accent);
  font-size: 18px;
}

.site-footer__bottom {
  display: flex;
  justify-content: space-between;
  gap: 24px;
  padding: 24px 0 30px;
  color: #7f8998;
  font-size: 11px;
}

@media (max-width: 899px) {
  .site-footer__main {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 34px;
  }

  .site-footer__brand {
    grid-column: 1 / -1;
  }
}

@media (max-width: 600px) {
  .site-footer__inner {
    width: min(100% - 24px, 560px);
  }

  .site-footer__main {
    grid-template-columns: 1fr;
    gap: 28px;
    padding: 42px 0 30px;
  }

  .site-footer__brand {
    grid-column: auto;
  }

  .site-footer__partners {
    grid-template-columns: 1fr;
    gap: 10px;
  }

  .site-footer__partner-link {
    width: 100%;
  }

  .site-footer__bottom {
    align-items: flex-start;
    flex-direction: column;
    gap: 9px;
  }
}
```

- [ ] **Step 3: Run only the asset/style tests**

```powershell
python -m unittest tests.test_site_footer.SiteFooterTests.test_partner_logo_is_local_and_accessible tests.test_site_footer.SiteFooterTests.test_shared_styles_cover_focus_and_breakpoints -v
```

Expected: the CSS breakpoint test passes; the partner-logo test still fails for each HTML page because Task 3 has not added the image markup yet.

- [ ] **Step 4: Commit the shared resources**

```powershell
git add -- assets/site-footer.css assets/partners/xlsxdiffmerge-logo.png
git commit -m "feat: add shared site footer presentation"
```

### Task 3: Apply the unified static footer to all pages

**Files:**
- Modify: `index.html`
- Modify: `codex-pojia.html`
- Modify: `培训文案.html`
- Modify: `user-notice.html`
- Modify: `knowledge/index.html`
- Modify: `knowledge/*.html` (50 article files)
- Temporary create/delete: `tools/update_site_footer.py`

**Interfaces:**
- Consumes: `/assets/site-footer.css` and `/assets/partners/xlsxdiffmerge-logo.png` from Task 2.
- Produces: identical `.site-footer` static markup and one CSS link in each of the 55 HTML pages.

- [ ] **Step 1: Create a guarded one-use rewrite script**

Create `tools/update_site_footer.py` with constants for the stylesheet link and the following footer markup. The script must collect only `ROOT.glob("*.html")` and `ROOT / "knowledge"`, assert exactly 55 pages, assert one `<footer>...</footer>` match per page, preserve existing CRLF/LF style by decoding and encoding bytes, insert the stylesheet link immediately before `</head>`, and replace only the matched footer span.

```html
<footer class="site-footer">
  <div class="site-footer__inner">
    <div class="site-footer__main">
      <section class="site-footer__brand" aria-label="无限破甲">
        <a class="site-footer__brand-link" href="/" aria-label="无限破甲首页">
          <img class="site-footer__brand-logo" src="/assets/brand-gradient.svg" width="42" height="42" alt="">
          <span class="site-footer__brand-name">无限破甲</span>
        </a>
        <p class="site-footer__brand-tagline">让 AI 真正开始分析，把每一步变成可验证、可复用的逆向工作流。</p>
      </section>
      <section aria-label="产品">
        <strong class="site-footer__section-title">产品</strong>
        <div class="site-footer__links">
          <a href="/">官网首页</a>
          <a href="/#download">软件下载</a>
          <a href="/codex-pojia">Codex 破甲</a>
          <a href="/#a-updates">更新日志</a>
        </div>
      </section>
      <section aria-label="资源与条款">
        <strong class="site-footer__section-title">资源与条款</strong>
        <div class="site-footer__links">
          <a href="/knowledge/">Codex 破甲知识库</a>
          <a href="/培训文案">软件逆向培训</a>
          <a href="/user-notice">用户使用须知</a>
        </div>
      </section>
      <section aria-label="联系与购买">
        <strong class="site-footer__section-title">联系与购买</strong>
        <div class="site-footer__links">
          <span>客服 QQ：1606654577</span>
          <a href="https://pay.ldxp.cn/item/bz252j" target="_blank" rel="noopener noreferrer">体验 37 天 · ¥19.9</a>
          <a href="https://pay.ldxp.cn/item/r778vo" target="_blank" rel="noopener noreferrer">永久授权 · ¥68</a>
        </div>
      </section>
    </div>
    <div class="site-footer__partners">
      <span class="site-footer__partners-label">友情链接</span>
      <a class="site-footer__partner-link" href="https://www.xlsxdiffmerge.com/" target="_blank" rel="noopener noreferrer" aria-label="访问 XlsxDiffMerge 网站 xlsxdiffmerge.com">
        <img class="site-footer__partner-logo" src="/assets/partners/xlsxdiffmerge-logo.png" width="44" height="44" alt="XlsxDiffMerge">
        <span class="site-footer__partner-copy">
          <strong class="site-footer__partner-name">XlsxDiffMerge</strong>
          <small class="site-footer__partner-domain">xlsxdiffmerge.com</small>
        </span>
        <span class="site-footer__partner-arrow" aria-hidden="true">↗</span>
      </a>
    </div>
    <div class="site-footer__bottom">
      <span>© 2026 无限破甲。保留所有权利。</span>
      <span>仅供逆向学习研究，使用时应遵守当地法律法规。</span>
    </div>
  </div>
</footer>
```

The rewrite logic must be:

```python
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
STYLESHEET = '<link rel="stylesheet" href="/assets/site-footer.css">'
FOOTER_RE = re.compile(r"<footer\b[^>]*>.*?</footer>", re.IGNORECASE | re.DOTALL)
FOOTER = """<footer class="site-footer">
  <div class="site-footer__inner">
    <div class="site-footer__main">
      <section class="site-footer__brand" aria-label="无限破甲">
        <a class="site-footer__brand-link" href="/" aria-label="无限破甲首页">
          <img class="site-footer__brand-logo" src="/assets/brand-gradient.svg" width="42" height="42" alt="">
          <span class="site-footer__brand-name">无限破甲</span>
        </a>
        <p class="site-footer__brand-tagline">让 AI 真正开始分析，把每一步变成可验证、可复用的逆向工作流。</p>
      </section>
      <section aria-label="产品">
        <strong class="site-footer__section-title">产品</strong>
        <div class="site-footer__links">
          <a href="/">官网首页</a>
          <a href="/#download">软件下载</a>
          <a href="/codex-pojia">Codex 破甲</a>
          <a href="/#a-updates">更新日志</a>
        </div>
      </section>
      <section aria-label="资源与条款">
        <strong class="site-footer__section-title">资源与条款</strong>
        <div class="site-footer__links">
          <a href="/knowledge/">Codex 破甲知识库</a>
          <a href="/培训文案">软件逆向培训</a>
          <a href="/user-notice">用户使用须知</a>
        </div>
      </section>
      <section aria-label="联系与购买">
        <strong class="site-footer__section-title">联系与购买</strong>
        <div class="site-footer__links">
          <span>客服 QQ：1606654577</span>
          <a href="https://pay.ldxp.cn/item/bz252j" target="_blank" rel="noopener noreferrer">体验 37 天 · ¥19.9</a>
          <a href="https://pay.ldxp.cn/item/r778vo" target="_blank" rel="noopener noreferrer">永久授权 · ¥68</a>
        </div>
      </section>
    </div>
    <div class="site-footer__partners">
      <span class="site-footer__partners-label">友情链接</span>
      <a class="site-footer__partner-link" href="https://www.xlsxdiffmerge.com/" target="_blank" rel="noopener noreferrer" aria-label="访问 XlsxDiffMerge 网站 xlsxdiffmerge.com">
        <img class="site-footer__partner-logo" src="/assets/partners/xlsxdiffmerge-logo.png" width="44" height="44" alt="XlsxDiffMerge">
        <span class="site-footer__partner-copy">
          <strong class="site-footer__partner-name">XlsxDiffMerge</strong>
          <small class="site-footer__partner-domain">xlsxdiffmerge.com</small>
        </span>
        <span class="site-footer__partner-arrow" aria-hidden="true">↗</span>
      </a>
    </div>
    <div class="site-footer__bottom">
      <span>© 2026 无限破甲。保留所有权利。</span>
      <span>仅供逆向学习研究，使用时应遵守当地法律法规。</span>
    </div>
  </div>
</footer>"""

pages = sorted([*ROOT.glob("*.html"), *(ROOT / "knowledge").glob("*.html")])
if len(pages) != 55:
    raise SystemExit(f"expected 55 HTML pages, found {len(pages)}")

for path in pages:
    text = path.read_bytes().decode("utf-8")
    newline = "\r\n" if "\r\n" in text else "\n"
    matches = list(FOOTER_RE.finditer(text))
    if len(matches) != 1:
        raise SystemExit(f"{path}: expected one footer, found {len(matches)}")
    if STYLESHEET not in text:
        if text.lower().count("</head>") != 1:
            raise SystemExit(f"{path}: expected one closing head tag")
        text = re.sub(r"</head>", f"  {STYLESHEET}{newline}</head>", text, count=1, flags=re.IGNORECASE)
    text = FOOTER_RE.sub(FOOTER.replace("\n", newline), text, count=1)
    path.write_bytes(text.encode("utf-8"))

print(f"updated {len(pages)} HTML pages")
```

- [ ] **Step 2: Run the rewrite exactly once, then delete the temporary script**

```powershell
python tools/update_site_footer.py
```

Expected: prints `updated 55 HTML pages` and exits 0.

Delete `tools/update_site_footer.py` with `apply_patch`; do not stage it.

- [ ] **Step 3: Run the complete footer contract**

```powershell
python -m unittest tests.test_site_footer -v
```

Expected: 4 tests pass across all 55 pages.

- [ ] **Step 4: Run release regression tests and diff guards**

```powershell
python -m unittest tests.test_release_metadata -v
git diff --check
git diff --name-only -- downloads/wujin/stable tools/sign_update_manifest.py
```

Expected: release tests pass; `git diff --check` emits no errors; the final command emits no paths.

- [ ] **Step 5: Commit only the HTML footer changes**

```powershell
git add -- index.html codex-pojia.html '培训文案.html' user-notice.html knowledge/*.html
git commit -m "feat: unify footer across static pages"
```

### Task 4: Browser and final verification

**Files:**
- Create only diagnostic screenshots under: `output/playwright/`
- Do not stage diagnostic screenshots.

**Interfaces:**
- Consumes: completed static footer and shared CSS.
- Produces: desktop/mobile visual evidence and a locally runnable site.

- [ ] **Step 1: Start a local static server**

```powershell
python -m http.server 4173 --bind 127.0.0.1
```

Expected: the server listens at `http://127.0.0.1:4173/`. If port 4173 is occupied, use the next free port and record it.

- [ ] **Step 2: Capture representative desktop and mobile pages in Chromium**

Capture full-page screenshots at 1440x1000 and 390x844 for:

- `/`
- `/codex-pojia`
- `/knowledge/`
- `/knowledge/codex-pojia-what-is`
- `/user-notice`

Expected: footer columns form 4/2/1 responsive layouts as designed, no horizontal overflow appears, partner copy does not overlap its arrow, and all text fits its container.

- [ ] **Step 3: Verify the exact external destination and local routes**

```powershell
$partner = Invoke-WebRequest -UseBasicParsing -Uri 'https://www.xlsxdiffmerge.com/' -TimeoutSec 20
$routes = '/', '/codex-pojia', '/knowledge/', '/knowledge/codex-pojia-what-is', '/user-notice'
$routes | ForEach-Object { (Invoke-WebRequest -UseBasicParsing -Uri ("http://127.0.0.1:4173" + $_) -TimeoutSec 10).StatusCode }
$partner.StatusCode
```

Expected: all six status codes are `200`.

- [ ] **Step 4: Run the final verification suite**

```powershell
python -m unittest discover -s tests -v
git diff --check
git status --short --branch
```

Expected: all tests pass; only unrelated pre-existing untracked files and untracked `output/` artifacts remain; `main` is ahead of `origin/main` by the local design/plan/implementation commits.

No production push is part of this plan. Keep the local server running at the verified URL for review.
