# Hero Download Update Badge Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在首页 Hero 的首个下载按钮内部提供红底白字、间歇斜向扫光的“新版本”标签，并保持原下载弹窗交互不变。

**Architecture:** 继续使用 `index.html` 的现有静态 HTML/CSS 与下载弹窗监听器。页面加载时只向 Hero 首个下载按钮追加一个非交互 `span`，通过局部绝对定位样式固定在右侧；扫光由标签的 `::after` 伪元素完成，不改变标签或按钮布局。Python `unittest` 负责约束选择器作用域、文案、颜色、动效与减少动态效果回退。

**Tech Stack:** 静态 HTML、CSS、Python unittest、Chromium

## Global Constraints

- 只修改首页 Hero 中带有 `data-download-placeholder` 的首个下载按钮。
- 标签文案必须是 `新版本`，无障碍名称必须是 `Windows v1.30.1 已发布`。
- 标签必须使用品牌红色背景和白色文字；2.8 秒动画的前 60% 静止，后 40% 完成一次斜向扫光。
- `prefers-reduced-motion: reduce` 下必须停用扫光动画。
- 不修改下载弹窗、下载地址、购买地址、更新日志、CDK/激活逻辑和发布元数据。
- 本轮只提供本地预览，不推送、不部署，用户预览前不提交功能改动。
- 页脚联系方式统一显示为 `联系邮箱：admin@hwtoken.top`，并使用 `mailto:admin@hwtoken.top`。

---

### Task 1: Hero 下载按钮新版本标签

**Files:**
- Create: `tests/test_hero_download_badge.py`
- Modify: `index.html`

**Interfaces:**
- Consumes: Hero 首个 `<a class="download-btn" href="#download" data-download-placeholder>` 与既有 `openDownloadModal` 事件绑定。
- Produces: `.hero-download-update-badge` 非交互标签及桌面、移动端样式。

- [ ] **Step 1: 写入失败的静态结构测试**

```python
from pathlib import Path
import re
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
INDEX_HTML = REPO_ROOT / "index.html"


class HeroDownloadBadgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = INDEX_HTML.read_text(encoding="utf-8")
        match = re.search(
            r'<section class="hero">.*?<div class="cta-row">(.*?)</div><p class="micro">',
            cls.html,
            re.DOTALL,
        )
        if match is None:
            raise AssertionError("Hero CTA row not found")
        cls.hero_cta = match.group(1)

    def test_badge_exists_only_in_the_hero_download_button(self):
        self.assertIn(
            '<a class="download-btn" href="#download" data-download-placeholder>',
            self.hero_cta,
        )
        self.assertEqual(
            1,
            self.html.count(
                "document.querySelector('.variant.a .hero "
                ".download-btn[data-download-placeholder]')"
            ),
        )
        self.assertEqual(
            1,
            self.html.count("heroUpdateBadge.className='hero-download-update-badge'"),
        )
        self.assertEqual(
            1,
            self.html.count(
                "heroUpdateBadge.setAttribute('aria-label',"
                "'Windows v1.30.1 已发布')"
            ),
        )
        self.assertEqual(1, self.html.count("heroUpdateBadge.textContent='新版本'"))
        self.assertEqual(1, self.html.count("heroDownloadButton.append(heroUpdateBadge)"))

    def test_badge_has_scoped_desktop_and_mobile_styles(self):
        self.assertIn(".a .hero-download-update-badge", self.html)
        self.assertRegex(
            self.html,
            r"\.a \.hero-download-update-badge\{[^}]*right:14px",
        )
        self.assertRegex(
            self.html,
            r"@media\(max-width:600px\)\{\.a \.hero \.download-btn\{[^}]*\}"
            r"\.a \.hero-download-update-badge\{[^}]*right:12px",
        )

    def test_download_modal_binding_is_unchanged(self):
        binding = (
            "document.querySelectorAll('[data-download-placeholder],a[href=\"#download\"]')"
            ".forEach(link=>link.addEventListener('click',openDownloadModal));"
        )
        self.assertEqual(1, self.html.count(binding))


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: 运行测试并确认因标签缺失而失败**

Run: `python -m unittest tests.test_hero_download_badge -v`

Expected: FAIL in the badge structure and style assertions because `.hero-download-update-badge` does not exist.

- [ ] **Step 3: 添加最小 HTML 与响应式 CSS**

在现有页面脚本开头创建标签并追加到 Hero 首个下载按钮：

```js
const heroDownloadButton=document.querySelector('.variant.a .hero .download-btn[data-download-placeholder]');
if(heroDownloadButton&&!heroDownloadButton.querySelector('.hero-download-update-badge')){
  const heroUpdateBadge=document.createElement('span');
  heroUpdateBadge.className='hero-download-update-badge';
  heroUpdateBadge.setAttribute('aria-label','Windows v1.30.1 已发布');
  heroUpdateBadge.textContent='新版本';
  heroDownloadButton.append(heroUpdateBadge);
}
```

添加局部样式：

```css
.a .hero .download-btn{position:relative;padding-inline:88px}
.a .hero-download-update-badge{position:absolute;top:50%;right:14px;display:inline-flex;align-items:center;justify-content:center;padding:6px 8px;border-radius:999px;background:#fff;color:var(--red);font-size:10px;font-weight:900;line-height:1;white-space:nowrap;box-shadow:0 4px 12px rgba(0,0,0,.2);transform:translateY(-50%);pointer-events:none}
@media(max-width:600px){.a .hero .download-btn{padding-inline:74px}.a .hero-download-update-badge{right:12px;padding:5px 7px;font-size:9px}}
```

- [ ] **Step 4: 运行静态测试和仓库回归测试**

Run: `python -m unittest tests.test_hero_download_badge -v`

Expected: 3 tests PASS.

Run: `python -m unittest discover -s tests -p "test_*.py" -v`

Expected: all repository tests PASS.

- [ ] **Step 5: 完成本地浏览器验证**

在 `1294x829` 和 `390x844` 视口确认标签不覆盖按钮文字、平台图标或按钮边界；点击标签坐标后，验证 `[data-download-modal]` 获得 `is-open`，且页面无横向溢出和控制台错误。

- [ ] **Step 6: 检查改动范围**

Run: `git diff --check -- index.html tests/test_hero_download_badge.py`

Expected: exit 0；diff 仅包含 Hero 标签、局部样式和对应测试，不包含发布元数据、下载地址或购买地址变更。

### Task 2: 全站页脚联系邮箱

**Files:**
- Modify: `*.html` 与 `knowledge/*.html` 中的共享页脚
- Modify: `tests/test_site_footer.py`

**Interfaces:**
- Consumes: 55 个页面现有的 `<span>客服 QQ：1606654577</span>` 页脚节点。
- Produces: 55 个 `<a href="mailto:admin@hwtoken.top">联系邮箱：admin@hwtoken.top</a>` 联系入口。

- [ ] **Step 1: 运行页脚邮箱红灯测试**

Run: `python -m unittest tests.test_site_footer.SiteFooterTests.test_every_footer_uses_the_contact_email -v`

Expected: FAIL for all 55 pages because the old QQ span is still present。

- [ ] **Step 2: 受控替换 55 个页脚节点**

仅替换精确字符串 `<span>客服 QQ：1606654577</span>`，不改动首页最终 CTA、付款链接、网盘链接或其它页面文案。

- [ ] **Step 3: 运行页脚回归测试**

Run: `python -m unittest tests.test_site_footer.SiteFooterTests.test_every_footer_uses_the_contact_email -v`

Expected: 55 个子测试 PASS；每页均有正确 `mailto:` href，页脚不再包含旧 QQ 号码。

### Task 3: 红底白字与间歇扫光

**Files:**
- Modify: `tests/test_hero_download_badge.py`
- Modify: `index.html:192-196`

**Interfaces:**
- Consumes: 现有 `.hero-download-update-badge` 标签和桌面、移动端定位规则。
- Produces: `hero-update-badge-sheen` 关键帧、标签 `::after` 高光层与减少动态效果回退。

- [ ] **Step 1: 写入失败的视觉契约测试**

```python
def test_badge_uses_red_sheen_animation_with_reduced_motion_fallback(self):
    self.assertRegex(
        self.html,
        r"\.a \.hero-download-update-badge\{[^}]*overflow:hidden[^}]*\}",
    )
    self.assertRegex(
        self.html,
        r"\.a \.hero-download-update-badge\{[^}]*"
        r"background:var\(--red\);color:#fff;[^}]*\}",
    )
    self.assertIn(
        ".a .hero-download-update-badge::after{content:\"\";position:absolute;"
        "inset:-50%;background:linear-gradient(115deg,transparent 42%,"
        "rgba(255,255,255,.78) 49%,rgba(255,255,255,.28) 53%,transparent 60%);"
        "transform:translateX(-100%);animation:hero-update-badge-sheen 2.8s "
        "ease-in-out infinite;pointer-events:none}",
        self.html,
    )
    self.assertIn(
        "@keyframes hero-update-badge-sheen{0%,60%{transform:translateX(-100%)}"
        "100%{transform:translateX(100%)}}",
        self.html,
    )
    self.assertIn(
        "@media(prefers-reduced-motion:reduce){"
        ".a .hero-download-update-badge::after{animation:none}}",
        self.html,
    )
```

- [ ] **Step 2: 运行聚焦测试并确认红灯**

Run: `python -m unittest tests.test_hero_download_badge.HeroDownloadBadgeTests.test_badge_uses_red_sheen_animation_with_reduced_motion_fallback -v`

Expected: FAIL because the badge still uses a white background and has no sheen pseudo-element or keyframes.

- [ ] **Step 3: 添加最小红色扫光样式**

```css
.a .hero-download-update-badge{position:absolute;top:50%;right:14px;display:inline-flex;align-items:center;justify-content:center;padding:6px 8px;overflow:hidden;isolation:isolate;border-radius:999px;background:var(--red);color:#fff;font-size:10px;font-weight:900;line-height:1;white-space:nowrap;box-shadow:0 4px 14px rgba(255,55,55,.34);transform:translateY(-50%);pointer-events:none}
.a .hero-download-update-badge::after{content:"";position:absolute;inset:-50%;background:linear-gradient(115deg,transparent 42%,rgba(255,255,255,.78) 49%,rgba(255,255,255,.28) 53%,transparent 60%);transform:translateX(-100%);animation:hero-update-badge-sheen 2.8s ease-in-out infinite;pointer-events:none}
@keyframes hero-update-badge-sheen{0%,60%{transform:translateX(-100%)}100%{transform:translateX(100%)}}
@media(prefers-reduced-motion:reduce){.a .hero-download-update-badge::after{animation:none}}
```

- [ ] **Step 4: 运行聚焦与共享页脚测试**

Run: `python -m unittest tests.test_hero_download_badge tests.test_site_footer -v`

Expected: 9 tests PASS.

- [ ] **Step 5: 验证真实浏览器行为**

在 `1294x829` 和 `390x844` 视口确认红底白字、扫光限制在胶囊圆角内、按钮和标签尺寸不随动画变化；点击标签中心后下载弹窗仍打开。使用减少动态效果上下文确认 `::after` 的 `animation-name` 为 `none`。
