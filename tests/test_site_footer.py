from html.parser import HTMLParser
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
HTML_FILES = sorted(
    [*REPO_ROOT.glob("*.html"), *REPO_ROOT.joinpath("knowledge").glob("*.html")]
)
INTERNAL_LINKS = {
    "/",
    "/#download",
    "/#a-updates",
    "/codex-pojia",
    "/knowledge/",
    "/培训文案",
    "/user-notice",
}
PARTNER_URL = "https://www.xlsxdiffmerge.com/"
CONTACT_EMAIL = "admin@hwtoken.top"
CONTACT_EMAIL_HREF = f"mailto:{CONTACT_EMAIL}"
PAYMENT_LINKS = {
    "https://pay.ldxp.cn/item/bz252j",
    "https://pay.ldxp.cn/item/r778vo",
}


class FooterCollector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.footer_depth = 0
        self.footer_count = 0
        self.footer_classes = set()
        self.footer_links = []
        self.footer_text = []
        self.stylesheets = []
        self.images = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "link" and "stylesheet" in attributes.get("rel", "").split():
            self.stylesheets.append(attributes.get("href"))
        if tag == "footer":
            self.footer_count += 1
            self.footer_depth += 1
            self.footer_classes.update(attributes.get("class", "").split())
            return
        if not self.footer_depth:
            return
        if tag == "a":
            self.footer_links.append(attributes)
        elif tag == "img":
            self.images.append(attributes)

    def handle_endtag(self, tag):
        if tag == "footer" and self.footer_depth:
            self.footer_depth -= 1

    def handle_data(self, data):
        if self.footer_depth:
            self.footer_text.append(data)


class SiteFooterTests(unittest.TestCase):
    def parse(self, path):
        collector = FooterCollector()
        collector.feed(path.read_text(encoding="utf-8"))
        return collector

    def test_all_55_html_pages_use_the_shared_footer(self):
        self.assertEqual(55, len(HTML_FILES))
        for path in HTML_FILES:
            with self.subTest(path=path.relative_to(REPO_ROOT)):
                footer = self.parse(path)
                self.assertEqual(1, footer.footer_count)
                self.assertIn("site-footer", footer.footer_classes)
                self.assertEqual(1, footer.stylesheets.count("/assets/site-footer.css"))

    def test_every_footer_has_required_internal_and_partner_links(self):
        for path in HTML_FILES:
            with self.subTest(path=path.relative_to(REPO_ROOT)):
                footer = self.parse(path)
                hrefs = {link.get("href") for link in footer.footer_links}
                self.assertTrue(INTERNAL_LINKS.issubset(hrefs))
                self.assertTrue(PAYMENT_LINKS.issubset(hrefs))
                self.assertIn(PARTNER_URL, hrefs)
                partner = next(link for link in footer.footer_links if link.get("href") == PARTNER_URL)
                self.assertEqual("_blank", partner.get("target"))
                self.assertEqual({"noopener", "noreferrer"}, set(partner.get("rel", "").split()))

    def test_partner_logo_is_local_and_accessible(self):
        expected_src = "/assets/partners/xlsxdiffmerge-logo.png"
        for path in HTML_FILES:
            with self.subTest(path=path.relative_to(REPO_ROOT)):
                footer = self.parse(path)
                logo = next(
                    (image for image in footer.images if image.get("src") == expected_src),
                    None,
                )
                self.assertIsNotNone(logo)
                self.assertEqual("XlsxDiffMerge", logo.get("alt"))
                self.assertEqual("44", logo.get("width"))
                self.assertEqual("44", logo.get("height"))

        logo_path = REPO_ROOT / "assets" / "partners" / "xlsxdiffmerge-logo.png"
        self.assertTrue(logo_path.is_file())
        self.assertEqual(b"\x89PNG\r\n\x1a\n", logo_path.read_bytes()[:8])

    def test_every_footer_uses_the_contact_email(self):
        for path in HTML_FILES:
            with self.subTest(path=path.relative_to(REPO_ROOT)):
                footer = self.parse(path)
                hrefs = {link.get("href") for link in footer.footer_links}
                text = " ".join(footer.footer_text)
                self.assertIn(CONTACT_EMAIL_HREF, hrefs)
                self.assertIn(f"联系邮箱：{CONTACT_EMAIL}", text)
                self.assertNotIn("1606654577", text)

    def test_shared_styles_cover_focus_and_breakpoints(self):
        css_path = REPO_ROOT / "assets" / "site-footer.css"
        self.assertTrue(css_path.is_file())
        css = css_path.read_text(encoding="utf-8")
        self.assertIn(".site-footer", css)
        self.assertIn("--footer-bg: #f4f6fa", css)
        self.assertIn(":focus-visible", css)
        self.assertIn("@media (max-width: 899px)", css)
        self.assertIn("@media (max-width: 600px)", css)


if __name__ == "__main__":
    unittest.main()
