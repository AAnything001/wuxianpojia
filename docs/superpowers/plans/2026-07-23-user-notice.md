# 用户使用须知协议 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为无限破甲新增独立的用户使用须知协议页面，并在首页和 Codex 破甲专题页页脚提供入口。

**Architecture:** 使用现有静态 HTML/CSS 风格新增 `user-notice.html`，不引入 JavaScript、构建工具或外部依赖。协议页保持单栏阅读布局，只包含授权范围、合法使用、免责声明三项；首页、专题页和 sitemap 仅做最小链接更新。

**Tech Stack:** 静态 HTML、内联 CSS、JSON-LD、XML sitemap、PowerShell 验证命令。

## Global Constraints

- 协议只说明授权范围、合法使用和免责声明，不增加退款、隐私、争议解决或其他一级条款。
- 不得影响首页购买入口、下载流程、CDK、激活校验或现有转化内容。
- 页面 canonical 使用 `https://codexpojia.com/user-notice` 无后缀形式。
- 中文内容使用现有 UTF-8 HTML 文件编码。
- 不纳入工作区现有未跟踪文件；每次提交只包含本任务文件。

---

### Task 1: Create the standalone protocol page

**Files:**
- Create: `user-notice.html`
- Test: PowerShell HTML metadata and section-count checks

**Interfaces:**
- Produces: `https://codexpojia.com/user-notice` static document with title, canonical, Open Graph metadata, `WebPage` JSON-LD, three numbered sections, and links to `index.html`, `codex-pojia.html`, and `knowledge/`.

- [ ] **Step 1: Add the document shell and metadata**

Create `user-notice.html` with UTF-8 HTML, `lang="zh-CN"`, viewport metadata, the following exact title/canonical/description, and JSON-LD:

```html
<title>用户使用须知协议｜无限破甲</title>
<meta name="description" content="无限破甲用户使用须知协议，说明 Codex 破甲相关软件与服务的授权范围、合法使用边界和免责声明。">
<link rel="canonical" href="https://codexpojia.com/user-notice">
<meta property="og:type" content="article">
<meta property="og:locale" content="zh_CN">
<meta property="og:site_name" content="无限破甲">
<meta property="og:title" content="用户使用须知协议｜无限破甲">
<meta property="og:description" content="说明无限破甲相关软件与服务的授权范围、合法使用边界和免责声明。">
<meta property="og:url" content="https://codexpojia.com/user-notice">
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "WebPage",
  "@id": "https://codexpojia.com/user-notice#webpage",
  "url": "https://codexpojia.com/user-notice",
  "name": "用户使用须知协议",
  "description": "无限破甲相关软件与服务的授权范围、合法使用边界和免责声明。",
  "inLanguage": "zh-CN",
  "dateModified": "2026-07-23"
}
</script>
```

- [ ] **Step 2: Add the branded single-column layout**

Reuse the existing `codex-pojia.html` variables (`--ink`, `--muted`, `--line`, `--red`, `--violet`) and create `.wrap`, `.nav`, `.brand`, `.article`, `.section`, `.notice`, and `.footer` rules. Keep the article width at `min(820px, calc(100% - 32px))`, use a responsive `@media(max-width:600px)` rule, and avoid buttons, modals, animation, and purchase calls to action.

- [ ] **Step 3: Add exactly the three protocol sections**

Add a header with eyebrow `使用边界` and `h1` `用户使用须知协议`, followed by the agreement preface. Add exactly three `section` elements with `h2` headings `1. 授权范围`, `2. 合法使用`, and `3. 免责声明`. Use the approved copy from `docs/superpowers/specs/2026-07-23-user-notice-design.md`; do not add another numbered heading.

- [ ] **Step 4: Add navigation and footer links**

Use relative links to `index.html`, `codex-pojia.html`, and `knowledge/` in the nav/footer. Make the footer text match the existing low-profile link style and include `© 2026 无限破甲`.

- [ ] **Step 5: Validate the new page before commit**

Run:

```powershell
$html = Get-Content -Raw -Encoding utf8 'user-notice.html'
([regex]::Matches($html, '<h2')).Count
Select-String -Path 'user-notice.html' -Pattern '1\. 授权范围|2\. 合法使用|3\. 免责声明|https://codexpojia.com/user-notice'
git diff --check -- 'user-notice.html'
```

Expected: heading count `3`, all three headings and canonical are found, and `git diff --check` has no output.

- [ ] **Step 6: Commit the standalone page**

```powershell
git add -- user-notice.html
git commit -m "feat: add user notice page"
```

### Task 2: Add footer entries and sitemap URL

**Files:**
- Modify: `index.html:206` (existing footer link paragraph)
- Modify: `codex-pojia.html:146` (existing footer link span)
- Modify: `sitemap.xml` (existing `<urlset>` entries)
- Test: exact link and XML parse checks

**Interfaces:**
- Consumes: `user-notice.html` from Task 1.
- Produces: footer navigation to `user-notice.html` and sitemap URL `https://codexpojia.com/user-notice`.

- [ ] **Step 1: Add the homepage footer link**

In the existing homepage footer link paragraph, append ` · <a class="footer-seo-link" href="user-notice.html">用户使用须知协议</a>` after the knowledge-base link. Do not alter the adjacent purchase, download, or update-log markup.

- [ ] **Step 2: Add the Codex 破甲 footer link**

In the existing `codex-pojia.html` footer span, append ` · <a href="user-notice.html">用户使用须知协议</a>` after the training link. Preserve all other links and text.

- [ ] **Step 3: Add the canonical sitemap entry**

Add this `<url>` immediately after the existing Codex 破甲 URL entry:

```xml
<url>
  <loc>https://codexpojia.com/user-notice</loc>
  <lastmod>2026-07-23</lastmod>
</url>
```

- [ ] **Step 4: Validate links and XML**

Run:

```powershell
Select-String -Path 'index.html','codex-pojia.html' -Pattern 'user-notice\.html|用户使用须知协议'
[xml]$sitemap = Get-Content -Raw -Encoding utf8 'sitemap.xml'
($sitemap.urlset.url.loc | Where-Object { $_ -eq 'https://codexpojia.com/user-notice' }).Count
git diff --check -- 'index.html' 'codex-pojia.html' 'sitemap.xml'
```

Expected: both HTML files contain the new link, the sitemap count is `1`, and diff check has no output.

- [ ] **Step 5: Commit navigation metadata changes**

```powershell
git add -- index.html codex-pojia.html sitemap.xml
git commit -m "feat: link user notice from site footers"
```

### Task 3: Run the complete static verification

**Files:**
- Test: `index.html`, `codex-pojia.html`, `user-notice.html`, `sitemap.xml`

**Interfaces:**
- Consumes: all changes from Tasks 1-2.
- Produces: verified local static pages and a clean scoped diff; no production publish is performed unless separately requested.

- [ ] **Step 1: Check local file targets and required links**

Run:

```powershell
$targets = @('index.html','codex-pojia.html','user-notice.html','knowledge/index.html')
foreach ($target in $targets) { if (-not (Test-Path -LiteralPath $target)) { throw "Missing $target" } }
$notice = Get-Content -Raw -Encoding utf8 'user-notice.html'
foreach ($link in @('index.html','codex-pojia.html','knowledge/')) { if ($notice -notmatch [regex]::Escape($link)) { throw "Missing link $link" } }
```

Expected: no exception and no missing target output.

- [ ] **Step 2: Validate metadata and exact section scope**

Run:

```powershell
$notice = Get-Content -Raw -Encoding utf8 'user-notice.html'
if (([regex]::Matches($notice, '<h2')).Count -ne 3) { throw 'Unexpected section count' }
if ($notice -notmatch 'rel="canonical" href="https://codexpojia.com/user-notice"') { throw 'Canonical missing' }
if ($notice -notmatch 'application/ld\+json') { throw 'JSON-LD missing' }
```

Expected: no exception.

- [ ] **Step 3: Verify desktop and mobile rendering with Playwright**

Start the existing local static server, then run Playwright from the bundled Codex runtime:

```powershell
& '.\run-prototype.ps1'
$env:NODE_PATH = 'C:\Users\Anything001\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\node_modules'
$nodePath = 'C:\Users\Anything001\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe'
$script = "const { chromium }=require('playwright'); const assert=require('node:assert/strict'); (async()=>{const browser=await chromium.launch({headless:true,executablePath:'C:\\\\Program Files (x86)\\\\Microsoft\\\\Edge\\\\Application\\\\msedge.exe'}); for(const item of [{name:'desktop',width:1280,height:900},{name:'mobile',width:390,height:844}]){const page=await browser.newPage({viewport:{width:item.width,height:item.height}}); await page.goto('http://127.0.0.1:4173/user-notice.html',{waitUntil:'networkidle'}); assert.equal(await page.locator('main h2').count(),3); const overflow=await page.evaluate(()=>({clientWidth:document.documentElement.clientWidth,scrollWidth:document.documentElement.scrollWidth})); assert.ok(overflow.scrollWidth<=overflow.clientWidth,JSON.stringify(overflow)); await page.screenshot({path:'output/playwright/user-notice-'+item.name+'.png',fullPage:true}); await page.close();} await browser.close(); console.log('user notice browser check: PASS')})().catch(error=>{console.error(error);process.exit(1)})"
& $nodePath -e $script
```

Expected: `user notice browser check: PASS`, two screenshots at `output/playwright/user-notice-desktop.png` and `output/playwright/user-notice-mobile.png`, and no assertion error.

- [ ] **Step 4: Check all scoped changes and working tree**

Run:

```powershell
git diff --check HEAD~2..HEAD
git status --short
```

Expected: diff check has no output; status shows only pre-existing unrelated untracked files, with no unstaged changes to the four scoped site files.

- [ ] **Step 5: Record completion evidence**

Report the two implementation commit IDs, local verification results, and explicitly state that no Cloudflare deployment was triggered because the user requested page production, not publication.
