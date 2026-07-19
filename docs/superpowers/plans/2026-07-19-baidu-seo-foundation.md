# 百度 SEO 基础与 Codex 破甲专题页 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为 `codexpojia.com` 增加百度可抓取的首页 SEO 标签、Codex 破甲专题页、robots.txt 和 sitemap.xml。

**Architecture:** 保持现有无构建静态站点结构。首页只修改 `<head>` 和页脚；专题页使用独立静态 HTML；robots 与 sitemap 放在站点根目录，由 Cloudflare Pages 原样发布。

**Tech Stack:** HTML5、CSS、XML Sitemap、robots.txt、现有 Python 静态服务器。

## Global Constraints

- 保留 `<meta name="baidu-site-verification" content="codeva-5fHpMyNMLb">`。
- 首页顶部导航、Hero、价格区和现有交互保持不变。
- 首页只在页脚增加低调的 `Codex 破甲介绍`文字链接。
- 专题页核心内容必须是静态 HTML，不依赖 JavaScript 才能显示。
- 不使用隐藏文字、关键词堆砌、虚假结果保证或虚假稀缺。
- 专题页说明内容用于 CTF 与授权软件逆向研究，并提醒遵守当地法律法规。

---

### Task 1: 首页 SEO Head 与低调内链

**Files:**
- Modify: `G:\AI\GW\wujin-website-prototype\index.html`

- [ ] **Step 1: Replace the homepage title and add static metadata**

Immediately after the Baidu verification tag, ensure the following elements exist exactly once:

```html
<title>Codex 破甲｜无限破甲 - AI 逆向分析与 CTF 学习路线</title>
<meta name="description" content="无限破甲支持 Codex、Claude、Kiro 等 AI 客户端，提供 Skill、MCP 配置及 CTF 软件逆向学习路线，帮助用户从问题识别走到证据整理。">
<link rel="canonical" href="https://codexpojia.com/">
```

- [ ] **Step 2: Add the footer internal link**

Add this link inside the Variant A footer without changing the header navigation:

```html
<a class="footer-seo-link" href="codex-pojia.html">Codex 破甲介绍</a>
```

Style it with the current footer font size and muted color. No button background, animation, or prominent placement.

- [ ] **Step 3: Verify homepage source**

Run:

```powershell
rg -n "baidu-site-verification|Codex 破甲｜无限破甲|name=\"description\"|rel=\"canonical\"|footer-seo-link" index.html
```

Expected: one match for each required head element and one footer link.

### Task 2: Codex 破甲专题页

**Files:**
- Create: `G:\AI\GW\wujin-website-prototype\codex-pojia.html`

- [ ] **Step 1: Create the static page head**

Use `lang="zh-CN"`, UTF-8, responsive viewport, favicon `assets/brand-gradient.svg`, and:

```html
<title>Codex 破甲是什么？｜无限破甲使用场景、版本与常见问题</title>
<meta name="description" content="了解 Codex 破甲的含义、适用场景、支持客户端和常见问题。无限破甲提供面向 CTF 与授权软件逆向研究的 AI 分析路线。">
<link rel="canonical" href="https://codexpojia.com/codex-pojia.html">
```

- [ ] **Step 2: Build the static body**

Create visible sections in this order:

```text
H1: Codex 破甲是什么？
Definition: explain the search term in plain language
Why Codex stops: task boundary, missing context, missing route
How Wujin helps: identify, inspect, verify, preserve evidence
Scenarios: APK, EXE, Web/API, CTF
Supported clients: Codex, Claude, Kiro and other Skill/MCP-capable clients
FAQ: meaning, beginner suitability, result boundary, local tool behavior
CTA: trial ¥19.9, permanent ¥68, homepage/download link
Compliance: CTF/authorized research and local-law notice
```

Use the existing payment URLs:

```text
https://pay.ldxp.cn/item/bz252j
https://pay.ldxp.cn/item/r778vo
```

Link back to `index.html` and `培训文案.html`. Keep all keyword-bearing content visible and static.

- [ ] **Step 3: Verify static content**

Run:

```powershell
rg -n "Codex 破甲|CTF|授权软件逆向|19.9|¥68|canonical|description" codex-pojia.html
```

Expected: all required topics and metadata are present; the page has one H1.

### Task 3: Robots and Sitemap

**Files:**
- Create: `G:\AI\GW\wujin-website-prototype\robots.txt`
- Create: `G:\AI\GW\wujin-website-prototype\sitemap.xml`

- [ ] **Step 1: Create robots.txt**

```text
User-agent: *
Allow: /
Disallow: /docs/
Disallow: /output/
Sitemap: https://codexpojia.com/sitemap.xml
```

- [ ] **Step 2: Create sitemap.xml**

Use XML Sitemap namespace `http://www.sitemaps.org/schemas/sitemap/0.9`. Include exactly three unique `<url>` entries with `lastmod` `2026-07-19`:

```text
https://codexpojia.com/                                  priority 1.0
https://codexpojia.com/codex-pojia.html                  priority 0.9
https://codexpojia.com/%E5%9F%B9%E8%AE%AD%E6%96%87%E6%A1%88.html priority 0.8
```

- [ ] **Step 3: Parse and count the sitemap**

Run PowerShell XML parsing and assert exactly three `<url>` nodes and three unique `<loc>` values.

### Task 4: Browser and HTTP Verification

**Files:**
- Test: `index.html`
- Test: `codex-pojia.html`
- Test: `培训文案.html`
- Test: `robots.txt`
- Test: `sitemap.xml`

- [ ] **Step 1: Verify local HTTP status**

Use the existing server on port `4173`; expect HTTP `200` for `/`, `/codex-pojia.html`, encoded training-page URL, `/robots.txt`, and `/sitemap.xml`.

- [ ] **Step 2: Verify rendered pages**

With Playwright, verify the homepage footer link resolves to `codex-pojia.html`, the专题页 has exactly one H1, CTA URLs are correct, and no page-level JavaScript errors occur.

- [ ] **Step 3: Verify mobile layout**

At 390px width, confirm the专题页 body does not exceed the viewport and CTA buttons remain visible.

