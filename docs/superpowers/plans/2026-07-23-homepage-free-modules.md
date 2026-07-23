# 官网首页免费模块栏目 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在首页痛点栏目下方新增以 EXE 下载为主目标的“免费与专业分层”栏目，并保留本地测试服务供用户验收。

**Architecture:** 只修改根目录 `index.html`，在默认 A 版页面中插入语义化静态栏目，并复用现有 `data-download-placeholder` 下载弹窗事件。所有新样式使用 `free-modules-` 前缀，避免污染现有卡片、价格、下载和其他 A/B/C 变体。

**Tech Stack:** 静态 HTML、内联 CSS、现有原生 JavaScript 下载弹窗、PowerShell 静态断言、Playwright 浏览器验证。

## Global Constraints

- 新栏目位于现有痛点卡片与“了解破甲”横条之后、`#a-cap` 之前。
- 页面只出现一个 `#a-free-modules`，本次不增加顶部导航项。
- 免费卡片约占桌面端 70% 视觉权重，专业卡片约占 30%；小于 `850px` 时按免费、专业顺序单列。
- 免费能力文案固定为 11 个模块、5 类能力、6 个客户端、无需 CDK，并明确不等于 Reverse Skill、MCP 或完整逆向工具链。
- 下载主按钮复用 `data-download-placeholder`；专业链接指向 `codex-pojia.html`。
- 不修改购买链接、现有下载 URL、用户须知入口、更新日志或 EXE/CDK/激活逻辑。
- 本轮不推送 `origin/main`；完成后保持本地测试服务运行并提供完整 URL。

---

### Task 1: Add the free-versus-professional section

**Files:**
- Modify: `index.html:155-162` (A 版扩展样式)
- Modify: `index.html:199-200` (痛点栏目与 `#a-cap` 之间)
- Test: PowerShell exact selector, position, copy, and link assertions

**Interfaces:**
- Consumes: Existing `data-download-placeholder` click handler and `.download-modal` component in `index.html`.
- Produces: `section#a-free-modules`, `.free-modules-download`, and `.free-modules-learn` elements.

- [ ] **Step 1: Run the failing static section check**

Run:

```powershell
$homepageHtml = Get-Content -Raw -Encoding utf8 'index.html'
if ($homepageHtml -notmatch 'id="a-free-modules"') { throw 'Missing #a-free-modules' }
```

Expected: FAIL with `Missing #a-free-modules`.

- [ ] **Step 2: Add scoped responsive CSS**

Add one CSS rule block to the A 版 extension style before its closing `</style>`. Define these exact class responsibilities:

```css
.a .free-modules-section{padding-top:72px}
.a .free-modules-tier-grid{display:grid;grid-template-columns:minmax(0,1.4fr) minmax(280px,.72fr);gap:16px;margin-top:28px}
.a .free-modules-tier{position:relative;overflow:hidden;padding:28px;border:1px solid #dfe3eb;border-radius:18px;background:rgba(255,255,255,.94)}
.a .free-modules-tier.is-free{border-color:#ffbdc5;box-shadow:0 18px 44px rgba(239,61,99,.1)}
.a .free-modules-tier.is-free:after{content:"";position:absolute;z-index:0;top:-70px;right:-50px;width:180px;height:180px;border-radius:50%;background:radial-gradient(circle,rgba(128,88,232,.18),transparent 68%);pointer-events:none}
.a .free-modules-tier.is-free>*{position:relative;z-index:1}
.a .free-modules-tier-head{display:flex;align-items:center;justify-content:space-between;gap:12px}
.a .free-modules-tier-label{font-size:13px;font-weight:900}
.a .free-modules-badge{padding:6px 9px;border-radius:999px;background:#fff0f2;color:#d82645;font-size:10px;font-weight:900}
.a .free-modules-badge.is-professional{background:#f1f2f6;color:#596171}
.a .free-modules-tier h3{margin:20px 0 8px;font-size:clamp(23px,2.4vw,31px);line-height:1.18}
.a .free-modules-tier-copy{margin:0;color:#727a8b;font-size:13px;line-height:1.7}
.a .free-modules-numbers{display:flex;gap:8px;margin:18px 0}
.a .free-modules-number{flex:1;padding:12px 8px;border-top:1px solid #e4e7ee;text-align:center}
.a .free-modules-number strong{display:block;font-size:24px}
.a .free-modules-number span{color:#8a919f;font-size:10px}
.a .free-modules-categories{display:flex;flex-wrap:wrap;gap:7px;margin:14px 0 18px}
.a .free-modules-categories span{padding:7px 9px;border:1px solid #e0e4eb;border-radius:8px;background:#fafbfe;color:#535b6b;font-size:11px;font-weight:800}
.a .free-modules-clients{padding:10px 12px;border-left:3px solid #8058e8;background:#f7f5ff;color:#5e6677;font-size:11px;line-height:1.65}
.a .free-modules-download{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-top:18px;padding:14px 17px;border-radius:11px;background:linear-gradient(100deg,#ff3045,#ef4778 48%,#8058e8);color:#fff;font-size:13px;font-weight:900;box-shadow:0 14px 30px rgba(239,61,99,.18)}
.a .free-modules-download small{font-size:10px;font-weight:700;opacity:.82}
.a .free-modules-professional-list{display:grid;gap:0;margin:18px 0}
.a .free-modules-professional-item{padding:10px 0;border-bottom:1px solid #e8eaf0;color:#4f5767;font-size:12px;font-weight:800}
.a .free-modules-learn{display:inline-flex;margin-top:8px;color:#7658d7;font-size:12px;font-weight:900}
.a .free-modules-boundary{display:flex;align-items:center;justify-content:space-between;gap:18px;margin-top:14px;padding:13px 17px;border:1px solid #e2e5ed;border-radius:12px;background:rgba(255,255,255,.86);color:#757d8d;font-size:11px}
@media(max-width:850px){.a .free-modules-tier-grid{grid-template-columns:1fr}.a .free-modules-boundary{align-items:flex-start;flex-direction:column}.a .free-modules-download{align-items:flex-start;flex-direction:column}}
@media(max-width:600px){.a .free-modules-section{padding-top:54px}.a .free-modules-tier{padding:21px}.a .free-modules-numbers{gap:4px}.a .free-modules-number{padding-inline:4px}.a .free-modules-number strong{font-size:21px}}
```

The rule block must not add keyframes or persistent animation.

- [ ] **Step 3: Add the semantic section markup**

Insert the following structure after the pain section that contains `.pain-cta` and before `<section class="section accent" id="a-cap">`:

```html
<section class="section free-modules-section" id="a-free-modules" aria-labelledby="a-free-modules-title">
  <p class="eyebrow">FREE MODULES · 新版内置</p>
  <h2 id="a-free-modules-title">先免费强化你的 AI，<br>需要逆向时再破甲。</h2>
  <p class="section-lead">无需激活，无需自己找仓库。下载无限破甲 EXE，选择需要的模块，一次安装到已经检测到的 AI 客户端。</p>
  <div class="free-modules-tier-grid">
    <article class="free-modules-tier is-free">
      <div class="free-modules-tier-head"><span class="free-modules-tier-label">免费环境强化</span><span class="free-modules-badge">无需 CDK</span></div>
      <h3>11 个常用 Skill，下载即可选装。</h3>
      <p class="free-modules-tier-copy">覆盖设计、创意、内容、研究和能力构建，模块已经随 EXE 内置。</p>
      <div class="free-modules-numbers" aria-label="免费模块数据"><div class="free-modules-number"><strong>11</strong><span>免费模块</span></div><div class="free-modules-number"><strong>5</strong><span>能力分类</span></div><div class="free-modules-number"><strong>6</strong><span>AI 客户端</span></div></div>
      <div class="free-modules-categories" aria-label="免费模块分类"><span>设计</span><span>创意</span><span>内容与演示</span><span>研究</span><span>能力构建</span></div>
      <p class="free-modules-clients">自动检测并适配 Claude、Codex、Kiro、Cursor、Cline、Windsurf</p>
      <a class="free-modules-download" href="#download" data-download-placeholder><span>免费下载 Windows EXE</span><small>模块已内置 · 无需运行时下载 →</small></a>
    </article>
    <article class="free-modules-tier">
      <div class="free-modules-tier-head"><span class="free-modules-tier-label">专业破甲能力</span><span class="free-modules-badge is-professional">激活后使用</span></div>
      <h3>需要深入分析时，再解锁完整工作流。</h3>
      <p class="free-modules-tier-copy">免费模块不会激活或替代专业逆向能力。</p>
      <div class="free-modules-professional-list"><div class="free-modules-professional-item">完整 Reverse Skill</div><div class="free-modules-professional-item">MCP 与工具链配置</div><div class="free-modules-professional-item">授权软件与 CTF 逆向流程</div><div class="free-modules-professional-item">配置备份、校验与恢复</div></div>
      <a class="free-modules-learn" href="codex-pojia.html">了解专业破甲 →</a>
    </article>
  </div>
  <div class="free-modules-boundary"><span>免费模块：日常 AI 能力增强</span><span>专业破甲：Reverse Skill、MCP 与逆向工具链</span></div>
</section>
```

- [ ] **Step 4: Run static assertions**

Run:

```powershell
$homepageHtml = Get-Content -Raw -Encoding utf8 'index.html'
if (([regex]::Matches($homepageHtml, 'id="a-free-modules"')).Count -ne 1) { throw 'Free module section count mismatch' }
$freeIndex = $homepageHtml.IndexOf('id="a-free-modules"')
$painIndex = $homepageHtml.IndexOf('class="pain-cta"')
$capIndex = $homepageHtml.IndexOf('id="a-cap"')
if (-not ($painIndex -lt $freeIndex -and $freeIndex -lt $capIndex)) { throw 'Free module section position mismatch' }
foreach ($text in @('11 个常用 Skill','5</strong><span>能力分类','6</strong><span>AI 客户端','Claude、Codex、Kiro、Cursor、Cline、Windsurf','data-download-placeholder','href="codex-pojia.html">了解专业破甲')) { if ($homepageHtml -notmatch [regex]::Escape($text)) { throw "Missing $text" } }
git diff --check -- index.html
```

Expected: no exception and no diff-check output.

- [ ] **Step 5: Verify the scoped diff and commit**

Run:

```powershell
git diff --stat -- index.html
git diff --unified=2 -- index.html
git add -- index.html
git diff --cached --check
git commit -m "feat: add homepage free modules section"
```

Expected: one production file committed; existing payment/download/footer lines show no unrelated changes.

### Task 2: Verify interaction and keep a local preview running

**Files:**
- Test: `index.html`
- Artifact: `output/playwright/homepage-free-modules-desktop.png`
- Artifact: `output/playwright/homepage-free-modules-mobile.png`

**Interfaces:**
- Consumes: `section#a-free-modules`, `.free-modules-download`, `.free-modules-learn`, existing `.download-modal`, and `[data-download-close]`.
- Produces: browser evidence at desktop/mobile sizes and a running local preview URL.

- [ ] **Step 1: Run existing repository tests**

Run:

```powershell
$pythonPath = 'C:\Users\Anything001\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $pythonPath -m unittest discover -s tests -p 'test_*.py' -v
```

Expected: all existing tests pass with `OK`.

- [ ] **Step 2: Start a persistent local preview server**

Confirm port `4175` is free, start the bundled Python server hidden, and retain its PID:

```powershell
$previewPort = 4175
if (Get-NetTCPConnection -LocalPort $previewPort -State Listen -ErrorAction SilentlyContinue) { throw 'Preview port 4175 is already in use; choose another unused port and use that same value in Step 3' }
$pythonPath = 'C:\Users\Anything001\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
$previewProcess = Start-Process -FilePath $pythonPath -ArgumentList '-m','http.server',$previewPort,'--directory','G:\AI\GW\wujin-website-prototype' -WindowStyle Hidden -PassThru
Start-Sleep -Milliseconds 800
if (-not (Get-NetTCPConnection -LocalPort $previewPort -State Listen -ErrorAction SilentlyContinue)) { throw 'Preview server failed to start' }
"PID=$($previewProcess.Id) URL=http://127.0.0.1:$previewPort/index.html?variant=A#a-free-modules"
```

Expected: a listening port, PID, and complete preview URL.

- [ ] **Step 3: Run Playwright desktop/mobile interaction checks**

Use bundled Node and the complete pnpm Playwright path:

```powershell
$nodePath = 'C:\Users\Anything001\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe'
$env:PW_MODULE = 'C:\Users\Anything001\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\node_modules\.pnpm\playwright@1.61.1\node_modules\playwright'
$env:PW_BROWSER = 'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
$env:PREVIEW_URL = 'http://127.0.0.1:4175/index.html?variant=A#a-free-modules'
$script = @'
const { chromium } = require(process.env.PW_MODULE);
const assert = require('node:assert/strict');

(async () => {
  const browser = await chromium.launch({ headless: true, executablePath: process.env.PW_BROWSER });
  const results = [];
  for (const item of [
    { name: 'desktop', width: 1280, height: 900 },
    { name: 'mobile', width: 390, height: 844 },
  ]) {
    const page = await browser.newPage({ viewport: { width: item.width, height: item.height }, reducedMotion: 'reduce' });
    const errors = [];
    page.on('pageerror', error => errors.push(String(error)));
    page.on('console', message => { if (message.type() === 'error') errors.push(message.text()); });
    await page.goto(process.env.PREVIEW_URL, { waitUntil: 'networkidle' });
    assert.equal(await page.locator('#a-free-modules').count(), 1);
    const metrics = (await page.locator('.free-modules-number').allTextContents()).map(text => text.replace(/\s+/g, ''));
    assert.deepEqual(metrics, ['11免费模块', '5能力分类', '6AI客户端']);
    assert.equal(await page.locator('.free-modules-learn').getAttribute('href'), 'codex-pojia.html');
    const overflow = await page.evaluate(() => ({ clientWidth: document.documentElement.clientWidth, scrollWidth: document.documentElement.scrollWidth }));
    assert.ok(overflow.scrollWidth <= overflow.clientWidth, `${item.name}: ${JSON.stringify(overflow)}`);
    const download = page.locator('.free-modules-download');
    await download.click();
    assert.ok(await page.locator('.download-modal').evaluate(element => element.classList.contains('is-open')));
    assert.ok(await page.locator('[data-download-close]').evaluate(element => element === document.activeElement));
    await page.locator('[data-download-close]').click();
    assert.ok(await page.locator('.download-modal').evaluate(element => !element.classList.contains('is-open')));
    assert.ok(await download.evaluate(element => element === document.activeElement));
    await page.screenshot({ path: `output/playwright/homepage-free-modules-${item.name}.png`, fullPage: true });
    assert.deepEqual(errors, []);
    results.push({ name: item.name, ...overflow });
    await page.close();
  }
  await browser.close();
  console.log(JSON.stringify({ status: 'PASS', viewports: results, modalChecks: 2 }));
})().catch(error => { console.error(error); process.exit(1); });
'@
& $nodePath -e $script
```

Expected: JSON output with `status: PASS`, two viewports, modal check count `2`, and no horizontal overflow.

- [ ] **Step 4: Inspect both screenshots**

Open both PNG files and verify:

- Free card is visually dominant on desktop.
- Professional card remains secondary.
- Mobile order is free first, professional second.
- Heading, metric row, client names, CTA, and boundary note remain readable.
- No text overlaps, clipped controls, or unintended persistent animation.

- [ ] **Step 5: Run final scoped verification and report the preview**

Run:

```powershell
git diff --check HEAD~1..HEAD
git status --short -- index.html docs/superpowers/specs/2026-07-23-homepage-free-modules-design.md docs/superpowers/plans/2026-07-23-homepage-free-modules.md
git log -3 --oneline
```

Expected: no scoped dirty files, design/plan/implementation commits present, unrelated untracked files untouched, and preview server still listening. Report the full preview URL and do not push `origin/main` until the user approves the preview.
