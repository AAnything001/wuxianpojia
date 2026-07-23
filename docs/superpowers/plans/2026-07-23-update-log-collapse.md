# Homepage Update Log Collapse Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 默认只显示首页最新 4 条更新日志，支持无障碍展开与收起，并同步更新最终 CTA 标题文案。

**Architecture:** 继续使用 `index.html` 内现有的更新日志模板。模板生成后，由一段局部脚本隐藏第 5 条及之后的日志并创建原生按钮；按钮同步控制 `hidden`、`aria-expanded` 与文案，不引入依赖或改动日志数据。

**Tech Stack:** 静态 HTML、CSS、原生 JavaScript、Python unittest、Playwright Chromium

---

### Task 1: 更新日志折叠交互

**Files:**
- Modify: `index.html:164-165`
- Modify: `index.html:251`
- Browser test artifact: `output/playwright/update-log-collapse-desktop.png`
- Browser test artifact: `output/playwright/update-log-collapse-mobile.png`

- [ ] **Step 1: 运行失败的浏览器行为检查**

打开 `http://127.0.0.1:4175/index.html?variant=A#a-updates`，执行以下断言：

```js
const items = page.locator('#a-update-log-list .update-log-item');
assert.equal(await items.count(), 5);
assert.equal(await page.locator('#a-update-log-list .update-log-item:visible').count(), 4);
const toggle = page.locator('.update-log-toggle');
assert.equal(await toggle.textContent(), '展开全部更新');
assert.equal(await toggle.getAttribute('aria-expanded'), 'false');
assert.equal(await toggle.getAttribute('aria-controls'), 'a-update-log-list');
```

Expected: FAIL because `#a-update-log-list` and `.update-log-toggle` do not exist.

- [ ] **Step 2: 添加最小折叠实现**

将日志列表改为：

```html
<div class="update-log-list" id="a-update-log-list">
```

在模板生成后加入：

```js
const collapsedUpdateItems=[...updateLog.querySelectorAll('.update-log-item')].slice(4);
if(collapsedUpdateItems.length){
  collapsedUpdateItems.forEach(item=>{item.hidden=true});
  const updateToggle=document.createElement('button');
  updateToggle.type='button';
  updateToggle.className='update-log-toggle';
  updateToggle.setAttribute('aria-expanded','false');
  updateToggle.setAttribute('aria-controls','a-update-log-list');
  updateToggle.textContent='展开全部更新';
  updateToggle.addEventListener('click',()=>{
    const expanded=updateToggle.getAttribute('aria-expanded')!=='true';
    collapsedUpdateItems.forEach(item=>{item.hidden=!expanded});
    updateToggle.setAttribute('aria-expanded',String(expanded));
    updateToggle.textContent=expanded?'收起更新':'展开全部更新';
    if(!expanded){updateLog.querySelector('.update-log-head')?.scrollIntoView({block:'start'})}
  });
  updateLog.append(updateToggle);
}
```

添加 `.update-log-toggle` 的次级按钮样式，并在 600px 以下保持按钮占满可用宽度。

- [ ] **Step 3: 运行浏览器检查确认通过**

验证桌面 1050×691 与手机 390×844：

```js
assert.equal(await page.locator('.update-log-item:visible').count(), 4);
await page.locator('.update-log-toggle').press('Enter');
assert.equal(await page.locator('.update-log-item:visible').count(), 5);
assert.equal(await page.locator('.update-log-toggle').getAttribute('aria-expanded'), 'true');
assert.equal(await page.locator('.update-log-toggle').textContent(), '收起更新');
await page.locator('.update-log-toggle').press('Space');
assert.equal(await page.locator('.update-log-item:visible').count(), 4);
assert.equal(await page.locator('.update-log-toggle').getAttribute('aria-expanded'), 'false');
```

Expected: PASS with no browser console errors or horizontal overflow.

- [ ] **Step 4: 提交折叠功能**

```powershell
git add -- index.html
git diff --cached --check
git commit -m "feat: collapse homepage update log"
```

### Task 2: 修改最终 CTA 标题

**Files:**
- Modify: `index.html:210`

- [ ] **Step 1: 运行失败的文案检查**

```powershell
$html = Get-Content -Raw -Encoding utf8 'index.html'
if (-not $html.Contains('<h2>自由，才是 AI 的默认配置</h2>')) { throw 'Missing new final CTA heading' }
```

Expected: FAIL with `Missing new final CTA heading`.

- [ ] **Step 2: 替换标题**

```html
<h2>自由，才是 AI 的默认配置</h2>
```

- [ ] **Step 3: 运行文案检查和仓库测试**

```powershell
$html = Get-Content -Raw -Encoding utf8 'index.html'
if (-not $html.Contains('<h2>自由，才是 AI 的默认配置</h2>')) { throw 'Missing new final CTA heading' }
if ($html.Contains('陌生程序不必永远是黑箱。')) { throw 'Old final CTA heading remains' }
$pythonPath = 'C:\Users\Anything001\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $pythonPath -m unittest discover -s tests -p 'test_*.py' -v
git diff --check -- index.html
```

Expected: new copy present once, old copy absent, all repository tests pass, and `git diff --check` prints no error.

- [ ] **Step 4: 提交文案修改**

```powershell
git add -- index.html
git diff --cached --check
git commit -m "copy: update homepage final CTA heading"
```

### Task 3: 最终浏览器与预览验证

**Files:**
- Verify: `index.html`
- Verify: `output/playwright/update-log-collapse-desktop.png`
- Verify: `output/playwright/update-log-collapse-mobile.png`

- [ ] **Step 1: 重跑桌面和手机完整交互检查**

确认默认 4 条、展开 5 条、收起 4 条、Enter/Space 操作、ARIA 状态、按钮文案、最终 CTA 新标题和零控制台错误。

- [ ] **Step 2: 运行最终仓库检查**

```powershell
$pythonPath = 'C:\Users\Anything001\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $pythonPath -m unittest discover -s tests -p 'test_*.py' -v
git diff --check HEAD~2..HEAD
git status --short -- index.html docs/superpowers/specs/2026-07-23-update-log-collapse-design.md docs/superpowers/plans/2026-07-23-update-log-collapse.md
```

Expected: all repository tests pass, scoped files are clean, and local preview returns HTTP 200.
