# Google 不可见 SEO 优化设计

## 目标

在不改变 `codexpojia.com` 三个公开页面的布局、视觉样式和正文文案的前提下，增强 Google 对页面主题、站点实体、规范 URL 和资源性能的理解。优化完成后提交到当前 GitHub 仓库的 `main` 分支，并确认 Cloudflare Pages 生产部署成功。

目标页面：

- `https://codexpojia.com/`
- `https://codexpojia.com/codex-pojia`
- `https://codexpojia.com/%E5%9F%B9%E8%AE%AD%E6%96%87%E6%A1%88`

## 约束

- 不调整 DOM 布局、CSS 视觉效果或用户可见正文。
- 保留现有 `<title>` 与 `meta description`，避免未经确认修改浏览器标签和搜索摘要候选文本。
- 不添加隐藏关键词、门页、重复页面或与正文不一致的结构化数据。
- 不提交工作区内与本任务无关的未跟踪文件。
- 不承诺具体排名；以可抓取性、规范化、页面理解和性能信号为验收目标。

## 方案选择

### 方案 A：仅补充页面元数据

为三个页面增加 robots、Open Graph 和 Twitter 元数据。风险最低，但不能改善页面实体关系、资源加载或 Cloudflare 响应策略。

### 方案 B：完整的不可见技术 SEO（采用）

在方案 A 基础上补全 JSON-LD 页面实体、图片加载提示、站点地图更新时间以及 Cloudflare 静态响应配置。覆盖抓取、理解、规范化和性能，且不改变用户看到的页面。

### 方案 C：增加可见内容与外部链接

潜在排名收益更高，但会改变站点内容或依赖站外发布，不符合本次范围。

## 页面 Head 元数据

三个页面均增加：

- `meta robots`：允许索引与跟踪，并开放大图预览和完整摘要候选。
- `og:type`、`og:locale`、`og:site_name`、`og:title`、`og:description`、`og:url`。
- `twitter:card`、`twitter:title`、`twitter:description`。

Open Graph 和 Twitter 字段复用页面现有标题、描述与 canonical，不创造新的页面主张。首页使用 `website` 类型，两个内容页使用 `article` 类型。

## 结构化数据

- 保留首页现有 `Organization`、`WebSite` 和 `SoftwareApplication`。
- 为首页补充 `WebPage`，通过 `isPartOf`、`about` 和 `mainEntity` 连接现有实体。
- 将 Codex 破甲页从单一 `FAQPage` 扩展为 `@graph`，保留与可见 FAQ 完全一致的问题答案，并加入 `WebPage` 与 `BreadcrumbList`。
- 为培训页增加 `WebPage` 与 `BreadcrumbList`，只描述页面已有内容，不伪造作者、评分、发布日期或搜索功能。

所有实体使用稳定的 canonical URL 与 `@id`，语言统一为 `zh-CN`。

## 性能与抓取

- 对首屏关键图片增加明确的获取优先级；对非首屏图片使用延迟加载。
- 在不改变 CSS 呈现的前提下，为可确定尺寸的位图补充固有宽高，减少布局偏移。
- 新增 Cloudflare Pages `_headers`：HTML 保持可重新验证，静态资源使用适度长期缓存，并设置不影响渲染的基础响应头。
- 不对未版本化资源使用 `immutable`，避免资源更新后客户端长期拿到旧文件。
- 保留 Cloudflare 当前对 `.html` 到无后缀 canonical URL 的 `308` 重定向。

## robots 与 Sitemap

- 保留当前 `robots.txt` 的允许、禁止目录和 sitemap 声明。
- `sitemap.xml` 继续只包含三个 canonical URL。
- 页面发生本次 SEO 修改后，将三个 `lastmod` 更新为实际部署日期 `2026-07-20`。
- 不向 sitemap 添加 `.html` 重定向地址、静态资源、页内锚点或外站链接。

## 验证

本地验证：

- 三个 HTML 文档均可解析，且标题、正文和样式内容未被改变。
- 每页只有一个 canonical、一个 title 和一个 description。
- JSON-LD 均为合法 JSON，FAQ 内容与可见文本一致。
- sitemap 是合法 XML，包含且仅包含三个 canonical URL。
- `_headers` 规则不缓存 HTML 为 immutable。

发布验证：

- 只暂存并提交本任务相关文件。
- 推送 `main` 到 `origin`。
- 等待 Cloudflare Pages 自动部署；如自动部署不可用，则使用现有项目配置执行等价生产部署。
- 三个 canonical URL 和 sitemap 均返回 HTTP 200。
- 三个 `.html` 旧地址仍返回指向 canonical URL 的永久重定向。
- 线上 HTML 包含新增元数据，HTTP 响应包含预期缓存/抓取头。

## 不在本次范围

- 修改页面可见文案、导航、布局或设计。
- 新建关键词内容页。
- 购买或自动发布外链。
- 伪造用户评价、评分或 FAQ。
- Google Search Console 的 DNS 验证；该步骤需要 Google 提供的专属验证值。
