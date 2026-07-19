# 百度 SEO 基础与 Codex 破甲专题页设计

## 目标

提升 `codexpojia.com` 对“Codex 破甲”搜索意图的相关性，同时不改变现有首页主体布局和培训页体验。

## 首页 Head

首页静态 HTML 加入并长期保留：

```html
<title>Codex 破甲｜无限破甲 - AI 逆向分析与 CTF 学习路线</title>
<meta name="description" content="无限破甲支持 Codex、Claude、Kiro 等 AI 客户端，提供 Skill、MCP 配置及 CTF 软件逆向学习路线，帮助用户从问题识别走到证据整理。">
<link rel="canonical" href="https://codexpojia.com/">
```

现有百度验证标签必须保留。

## Codex 破甲专题页

创建静态页面 `codex-pojia.html`，采用“搜索解释 + 产品转化”的混合结构：

1. Hero：明确回答“Codex 破甲是什么”。
2. 为什么 Codex 会停止、拒绝或只解释概念。
3. 无限破甲提供的分析路线和适用边界。
4. APK、EXE、Web、CTF 四类研究场景。
5. Codex、Claude、Kiro 等客户端支持说明。
6. 常见问题 FAQ。
7. 7 天体验 ¥19.9、永久版 ¥68、下载入口。
8. CTF 环境研究及遵守当地法律法规说明。

页面必须使用静态 HTML 输出核心关键词和正文，不依赖 JavaScript 才能显示。页面使用独立 Title、Description 和 Canonical：

```html
<title>Codex 破甲是什么？｜无限破甲使用场景、版本与常见问题</title>
<meta name="description" content="了解 Codex 破甲的含义、适用场景、支持客户端和常见问题。无限破甲提供面向 CTF 与授权软件逆向研究的 AI 分析路线。">
<link rel="canonical" href="https://codexpojia.com/codex-pojia.html">
```

“Codex 破甲”自然出现在标题、H1、首段、小标题和 FAQ 中，不使用隐藏文本和批量堆砌。

## 低调内部链接

首页顶部导航、Hero、价格区保持不变。在首页页脚增加低调的文字链接：

```html
<a href="codex-pojia.html">Codex 破甲介绍</a>
```

链接使用当前页脚的小字号和弱化颜色，不做按钮、不加动画，不影响原有页面视觉重点。

## robots.txt

创建：

```text
User-agent: *
Allow: /
Disallow: /docs/
Disallow: /output/
Sitemap: https://codexpojia.com/sitemap.xml
```

## sitemap.xml

创建标准 XML Sitemap，包含：

- `https://codexpojia.com/`
- `https://codexpojia.com/codex-pojia.html`
- `https://codexpojia.com/%E5%9F%B9%E8%AE%AD%E6%96%87%E6%A1%88.html`

`lastmod` 使用 `2026-07-19`。首页优先级 `1.0`，专题页 `0.9`，培训页 `0.8`。

## 验证标准

- 首页百度验证标签仍存在。
- 首页 Title、Description、Canonical 与规格完全一致。
- 专题页核心内容无需 JavaScript 即可读取。
- 首页只在页脚新增一个低调专题页内链。
- `robots.txt` 和 `sitemap.xml` 可被静态服务器访问。
- Sitemap XML 可解析并包含 3 个唯一 URL。
- 四个公开入口：首页、专题页、培训页、Sitemap 均返回 HTTP 200。
- 桌面和 390px 手机视口无新增横向溢出。
