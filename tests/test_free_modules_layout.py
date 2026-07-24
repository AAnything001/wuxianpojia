from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
INDEX_HTML = REPO_ROOT / "index.html"
LAYOUT_CSS = REPO_ROOT / "assets" / "home-free-modules.css"
LAYOUT_HREF = "/assets/home-free-modules.css"
TYPOGRAPHY_HREF = "/assets/typography.css"


class FreeModulesLayoutTests(unittest.TestCase):
    def test_homepage_loads_the_component_styles_before_typography(self):
        html = INDEX_HTML.read_text(encoding="utf-8")
        layout_link = f'<link rel="stylesheet" href="{LAYOUT_HREF}">'
        typography_link = f'<link rel="stylesheet" href="{TYPOGRAPHY_HREF}">'
        self.assertEqual(1, html.count(layout_link))
        self.assertLess(html.index(layout_link), html.index(typography_link))

    def test_free_modules_card_uses_a_structured_content_grid(self):
        self.assertTrue(LAYOUT_CSS.is_file())
        css = LAYOUT_CSS.read_text(encoding="utf-8")
        required = (
            ".a .free-modules-tier.is-free",
            "padding: 32px",
            ".a .free-modules-tier-head",
            "border-bottom: 1px solid #e8eaf1",
            ".a .free-modules-numbers",
            "grid-template-columns: repeat(3, minmax(0, 1fr))",
            ".a .free-modules-number",
            "border-radius: 14px",
            ".a .free-modules-categories span",
            ".a .free-modules-clients::before",
            "@media (max-width: 600px)",
        )
        for declaration in required:
            with self.subTest(declaration=declaration):
                self.assertIn(declaration, css)

    def test_component_styles_do_not_change_copy_or_load_assets(self):
        self.assertTrue(LAYOUT_CSS.is_file())
        css = LAYOUT_CSS.read_text(encoding="utf-8")
        self.assertNotIn("url(", css)
        self.assertNotIn("@font-face", css)


if __name__ == "__main__":
    unittest.main()
