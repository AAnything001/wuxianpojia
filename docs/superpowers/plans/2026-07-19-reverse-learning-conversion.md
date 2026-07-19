# 逆向入门课程与转化文案改版 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把培训页面改成零基础用户能看懂、能开始学习软件逆向，并能自然了解无限破甲价值的课程页。

**Architecture:** 继续使用单文件 `培训文案.html` 的原生 HTML/CSS/JavaScript。保留现有课程目录、hash 切换和进度交互，重写章节数据与正文结构；移除资料地图表格及外部资料链接，新增练习模板和购买 CTA。

**Tech Stack:** 原生 HTML、CSS、JavaScript；现有静态 Python HTTP server；无需新增依赖。

## Global Constraints

- 不制作无限破甲软件的安装、激活或客户端操作教程。
- 不保留“学习资料地图”、工具分类表、安装命令或 GitHub 来源链接。
- 课程必须面向零基础读者，短句、白话、先结论后术语。
- 不使用虚假稀缺、夸大成功率、恐吓或“保证破解”等购买话术。
- CTA 展示 7 天体验 ¥19.9 和永久版 ¥68。

---

### Task 1: 重写课程内容与页面段落

**Files:**
- Modify: `G:\AI\GW\wujin-website-prototype\培训文案.html`

**Interfaces:**
- Preserve: `courseDocs`, `courseList`, `courseIndexFromHash`, `renderCourse`, `course-prev`, `course-next` existing DOM/JS behavior.
- Produce: seven course entries with ids `start`, `objects`, `questions`, `static`, `dynamic`, `evidence`, `practice`.

- [ ] **Step 1: Replace the hero copy**

Replace the current hero heading and lead with:

```html
<h1>逆向知道的一切<br><span class="gradient">从看懂一个文件开始</span></h1>
<p class="lead">软件逆向，就是把程序拆开观察，弄清它做了什么。这里从最简单的一步开始，不要求你先会工具。</p>
```

- [ ] **Step 2: Replace the seven course data entries**

Set `courseDocs` to seven plain-language entries with the following titles and focus:

```text
start: 软件逆向到底是什么 / 把程序拆开观察
objects: 先认识你手里的文件 / APK、EXE、网页请求是什么
questions: 学会问一个好问题 / 现象、目标、想确认的事
static: 不运行程序也能看什么 / 文件信息、字符串、资源
dynamic: 运行后如何验证猜测 / 输入、输出、文件变化、请求
evidence: 把证据整理成结论 / 记录时间、步骤、输出和未知项
practice: 用真实场景练习一次 / APK、EXE、网页、未知文件提问模板
```

Each entry must contain a short `lead`, exactly three `points`, and one `note`; every point must describe one observable action or beginner-friendly question. Do not include GitHub URLs, shell install commands, or product activation steps.

- [ ] **Step 3: Remove the old learning map section**

Delete the complete `<section id="skills">...</section>` block, including the table, `.source` links, copy buttons, installation commands, and the `工具资料` navigation link.

- [ ] **Step 4: Rewrite the practice section**

Keep four cards for APK, EXE, Web/API, and unknown files. Each card must use the pattern “我看到了什么 / 我想确认什么 / 请先告诉我下一步”，and the section must not mention external repositories.

### Task 2: Add a clear purchase guide without turning the page into a product manual

**Files:**
- Modify: `G:\AI\GW\wujin-website-prototype\培训文案.html`

**Interfaces:**
- Consume: existing payment URLs in `index.html` (`https://pay.ldxp.cn/item/bz252j` and `https://pay.ldxp.cn/item/r778vo`).
- Produce: one visible CTA section after practice content and before the footer.

- [ ] **Step 1: Add the CTA section**

Add a section with these user-facing ideas:

```html
<p class="eyebrow">学到这里，下一步有人带路</p>
<h2>你负责提出问题，路线和证据有人帮你理清。</h2>
<p>无限破甲不是替你跳过学习，而是把“描述问题、安排分析顺序、整理证据”这条路线接到 AI 上。适合想学逆向、但总卡在下一步的人。</p>
<a href="https://pay.ldxp.cn/item/bz252j">先试 7 天 · ¥19.9</a>
<a href="https://pay.ldxp.cn/item/r778vo">长期使用 · ¥68</a>
```

- [ ] **Step 2: Add transparent boundary copy**

Include one short note: “它不能保证所有目标都有结果，也不能替代你对样本和证据的判断。” Do not add countdowns, fake user numbers, or guaranteed outcomes.

### Task 3: Remove obsolete styling and external-link behavior

**Files:**
- Modify: `G:\AI\GW\wujin-website-prototype\培训文案.html`

- [ ] **Step 1: Remove obsolete map styles**

Delete `.table-wrap`, `table`, `th`, `td`, `.cmd`, `.source`, `.copy` rules if no remaining element uses them.

- [ ] **Step 2: Keep mobile course usability**

Preserve the mobile horizontal course tabs and ensure the new CTA stacks to one column below 620px.

### Task 4: Verify the page before handoff

**Files:**
- Test: `G:\AI\GW\wujin-website-prototype\培训文案.html`

- [ ] **Step 1: Static content checks**

Run:

```powershell
rg -n "学习资料地图|工具资料|github.com|git clone|npx skills add|courseDocs|19.9|68" 培训文案.html
```

Expected: no learning-map/tool-install/GitHub matches; `courseDocs`, `19.9`, and `68` are present.

- [ ] **Step 2: HTTP and browser checks**

Run the existing local server and verify `培训文案.html` returns `200`. In a browser, verify seven course tabs, hash navigation, previous/next buttons, CTA links, and no console errors.

- [ ] **Step 3: Mobile layout check**

At a 390px viewport, verify `document.documentElement.scrollWidth === 390` and that the course tabs and CTA remain usable without horizontal page overflow.

