# macOS 客户端发布与双平台下载设计

## 目标

将官网从仅提供 Windows 下载更新为同时提供 Windows 与 macOS 下载。macOS 客户端通过蓝奏云发布，同时支持 Apple Silicon 与 Intel。所有通用下载入口应让访客先选择操作系统，系统专属下载卡片则直接进入对应下载渠道。

## 发布信息

- macOS 下载地址：`https://wwbbc.lanzouv.com/i9zwz3xnj43g`
- 支持架构：Apple Silicon、Intel
- Windows 下载地址保持不变：百度网盘、夸克网盘、蓝奏云
- macOS 下载渠道当前仅提供蓝奏云

## 页面改动

改动集中在 `index.html`。

### 首屏与平台说明

- 将仅描述 Windows 的首屏辅助文案改为同时说明 Windows 和 macOS 可用。
- 平台文案使用：`Windows 10/11 x64 · macOS（Apple Silicon / Intel）`。
- 顶部导航、首屏和最终转化区的通用“立即下载”按钮继续打开下载弹窗，不直接跳转到单一平台。

### 系统专属下载卡片

- 保留现有 Windows 下载卡片及其弹窗入口。
- 将“Mac 版本还在路上”改为“macOS 版本下载”。
- 将准备中说明改为：`支持 Apple Silicon 与 Intel · 下载后按使用说明完成配置。`
- 将不可点击的“马上就来”状态改为可点击的“下载 macOS 版”按钮。
- macOS 卡片按钮直接在新窗口打开已确认的蓝奏云地址，并使用 `noopener noreferrer`。

### 双平台下载弹窗

- 标题改为“选择系统和下载入口”。
- 说明文案明确 Windows 提供三个网盘渠道，macOS 当前提供蓝奏云。
- Windows 区保留百度网盘、夸克网盘和原蓝奏云入口。
- 新增 macOS 区，显示 Apple 图标、`macOS`、`支持 Apple Silicon 与 Intel`，并链接到新的蓝奏云地址。
- 弹窗继续支持遮罩点击关闭、关闭按钮、Escape 关闭和焦点返回。
- 移动端保持单列布局，不产生横向溢出。

### SEO 与更新日志

- 将 `SoftwareApplication` 结构化数据的 `operatingSystem` 扩展为 Windows 10、Windows 11 和 macOS。
- 在更新日志顶部新增 `2026.07.20` 记录，标题为“macOS 客户端正式发布”，正文说明同时支持 Apple Silicon 与 Intel。
- `codex-pojia.html`、`培训文案.html`、`sitemap.xml` 和 `robots.txt` 不含 macOS 尚未发布的表述，不做修改。

## 交互与错误处理

- 通用下载按钮始终打开双平台弹窗，避免默认把 macOS 用户送到 Windows 下载。
- 系统专属卡片直接打开对应下载入口，减少一次选择。
- 下载站点在新窗口打开；若浏览器阻止新窗口，沿用弹窗中的现有提示。
- 不在前端探测用户操作系统，也不自动跳转，避免识别错误和隐藏另一个平台。

## 验收标准

- 首屏清楚说明同时支持 Windows 与 macOS。
- macOS 卡片不再显示“还在路上”或“马上就来”。
- macOS 专属按钮和弹窗内的 macOS 入口均指向 `https://wwbbc.lanzouv.com/i9zwz3xnj43g`。
- 下载弹窗同时展示 Windows 与 macOS，Windows 原有三个下载链接保持不变。
- 结构化数据包含 macOS，更新日志包含 2026.07.20 发布记录。
- 弹窗打开、关闭、Escape、焦点返回均正常，浏览器控制台无 JavaScript 错误。
- 桌面端和 390px 移动端无横向溢出，下载选项文字不重叠。
- 页面中不存在 macOS 仍在准备或尚未发布的公开文案。
