from html.parser import HTMLParser
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
ROOT_HTML = sorted(REPO_ROOT.glob("*.html"))
KNOWLEDGE_HTML = sorted(REPO_ROOT.joinpath("knowledge").glob("*.html"))
TYPOGRAPHY_HREF = "/assets/typography.css"
FOOTER_HREF = "/assets/site-footer.css"


class StylesheetCollector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stylesheets = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "link" and "stylesheet" in attributes.get("rel", "").split():
            self.stylesheets.append(attributes.get("href"))


def stylesheets(path):
    collector = StylesheetCollector()
    collector.feed(path.read_text(encoding="utf-8"))
    return collector.stylesheets


class TypographySystemTests(unittest.TestCase):
    def test_production_page_inventory_is_stable(self):
        self.assertEqual(4, len(ROOT_HTML))
        self.assertEqual(51, len(KNOWLEDGE_HTML))

    def test_shared_stylesheet_contract(self):
        css_path = REPO_ROOT / "assets" / "typography.css"
        self.assertTrue(css_path.is_file())
        css = css_path.read_text(encoding="utf-8")
        for token in (
            "--font-sans:",
            "--font-mono:",
            "--type-display: clamp(38px, 5vw, 64px)",
            "--type-h1: clamp(36px, 4.5vw, 52px)",
            "--type-h2: clamp(28px, 3.5vw, 40px)",
            "--type-body: 1rem",
            "text-size-adjust: 100%",
        ):
            self.assertIn(token, css)
        self.assertNotIn("@font-face", css)
        self.assertNotIn("url(", css)

    def test_homepage_loads_typography_last(self):
        links = stylesheets(REPO_ROOT / "index.html")
        self.assertEqual(1, links.count(TYPOGRAPHY_HREF))
        self.assertEqual(TYPOGRAPHY_HREF, links[-1])

    def test_secondary_root_pages_load_typography_last(self):
        for path in ROOT_HTML:
            with self.subTest(path=path.name):
                links = stylesheets(path)
                self.assertEqual(1, links.count(TYPOGRAPHY_HREF))
                self.assertEqual(TYPOGRAPHY_HREF, links[-1])

    def test_knowledge_pages_load_typography_last(self):
        for path in KNOWLEDGE_HTML:
            with self.subTest(path=path.name):
                links = stylesheets(path)
                self.assertEqual(1, links.count(TYPOGRAPHY_HREF))
                self.assertEqual(TYPOGRAPHY_HREF, links[-1])
                self.assertLess(links.index(FOOTER_HREF), links.index(TYPOGRAPHY_HREF))


if __name__ == "__main__":
    unittest.main()
