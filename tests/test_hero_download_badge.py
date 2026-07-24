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
                "'Windows v1.30.3 已发布')"
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

    def test_download_modal_binding_is_unchanged(self):
        binding = (
            "document.querySelectorAll('[data-download-placeholder],a[href=\"#download\"]')"
            ".forEach(link=>link.addEventListener('click',openDownloadModal));"
        )
        self.assertEqual(1, self.html.count(binding))


if __name__ == "__main__":
    unittest.main()
