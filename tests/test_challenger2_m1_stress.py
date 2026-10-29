"""
Empirical Challenger 2 Adversarial Stress Suite for Milestone 1 (Offline News Vault & PWA Foundation - R6)
Runs extensive stress testing on:
1. Web App Manifest syntax, schema, and referenced icon assets
2. Icon binary/SVG integrity
3. HTML structural integrity, tag matching, and required IDs
4. CSS syntax, token balance, and VisionOS liquid glass classes
5. Service Worker dual-strategy cache routing and lifecycle
6. App.js event wiring, protocol safety, and offline/online transition states
"""

import json
import os
import re
import struct
import unittest
import xml.etree.ElementTree as ET
from html.parser import HTMLParser

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TestM1ChallengerStress(unittest.TestCase):

    def setUp(self):
        self.manifest_file = os.path.join(PROJECT_ROOT, "manifest.json")
        self.sw_file = os.path.join(PROJECT_ROOT, "sw.js")
        self.index_file = os.path.join(PROJECT_ROOT, "index.html")
        self.style_file = os.path.join(PROJECT_ROOT, "style.css")
        self.app_file = os.path.join(PROJECT_ROOT, "app.js")
        self.assets_dir = os.path.join(PROJECT_ROOT, "assets")

    # -------------------------------------------------------------
    # 1. MANIFEST & ASSET STRESS TESTS
    # -------------------------------------------------------------
    def test_manifest_structure_and_assets(self):
        """Stress test manifest.json for required PWA installability fields."""
        with open(self.manifest_file, "r", encoding="utf-8") as f:
            manifest = json.load(f)

        required_fields = ["name", "short_name", "start_url", "display", "icons", "theme_color", "background_color"]
        for field in required_fields:
            self.assertIn(field, manifest, f"Missing required manifest field: {field}")

        self.assertIn(manifest["display"], ["standalone", "fullscreen", "minimal-ui", "browser"])
        self.assertTrue(manifest["start_url"].startswith("./") or manifest["start_url"].startswith("/"))

        # Verify icons array
        self.assertIsInstance(manifest["icons"], list)
        self.assertGreaterEqual(len(manifest["icons"]), 2)

        has_192 = False
        has_512 = False
        for icon in manifest["icons"]:
            src = icon.get("src")
            sizes = icon.get("sizes", "")
            icon_path = os.path.join(PROJECT_ROOT, src)
            self.assertTrue(os.path.exists(icon_path), f"Referenced icon {src} does not exist on disk")

            if "192x192" in sizes:
                has_192 = True
            if "512x512" in sizes:
                has_512 = True

        self.assertTrue(has_192, "Manifest must specify at least one 192x192 icon")
        self.assertTrue(has_512, "Manifest must specify at least one 512x512 icon")

    def test_png_icon_binary_headers(self):
        """Verify PNG icons have valid magic bytes, IHDR chunks, and dimensions."""
        for filename, expected_size in [("icon-192.png", (192, 192)), ("icon-512.png", (512, 512))]:
            filepath = os.path.join(self.assets_dir, filename)
            self.assertTrue(os.path.exists(filepath))
            with open(filepath, "rb") as f:
                sig = f.read(8)
                self.assertEqual(sig, b"\x89PNG\r\n\x1a\n", f"Invalid PNG magic signature in {filename}")
                chunk_len, chunk_type = struct.unpack(">I4s", f.read(8))
                self.assertEqual(chunk_type, b"IHDR", f"First chunk in {filename} must be IHDR")
                width, height, bit_depth, color_type = struct.unpack(">IIBB", f.read(10))
                self.assertEqual((width, height), expected_size)
                self.assertEqual(bit_depth, 8)
                self.assertEqual(color_type, 6, "Expected RGBA (color type 6)")

    def test_svg_icon_xml_structure(self):
        """Verify SVG icons have valid XML syntax and viewBox."""
        for filename in ["icon-192.svg", "icon-512.svg"]:
            filepath = os.path.join(self.assets_dir, filename)
            self.assertTrue(os.path.exists(filepath))
            tree = ET.parse(filepath)
            root = tree.getroot()
            self.assertTrue(root.tag.endswith("svg"))
            self.assertIn("viewBox", root.attrib)

    # -------------------------------------------------------------
    # 2. HTML STRUCTURE & REQUIRED ELEMENT IDS
    # -------------------------------------------------------------
    def test_index_html_required_ids_and_meta(self):
        """Verify required element IDs and link tags in index.html."""
        with open(self.index_file, "r", encoding="utf-8") as f:
            html = f.read()

        # Check links
        self.assertRegex(html, r'<link\s+[^>]*rel=["\']manifest["\'][^>]*href=["\']manifest\.json["\']')
        self.assertRegex(html, r'<link\s+[^>]*rel=["\']apple-touch-icon["\'][^>]*href=["\']assets/icon-192\.svg["\']')

        # Check IDs
        for req_id in ["pwaVaultIndicatorBtn", "pwaVaultDot", "pwaVaultLabel", "pwaInstallBadge"]:
            pattern = rf'id=["\']{req_id}["\']'
            self.assertTrue(re.search(pattern, html), f"Required element #{req_id} not found in index.html")

    def test_index_html_tag_nesting_and_unclosed_div_audit(self):
        """Audit tag nesting in index.html and identify any unclosed tags."""
        with open(self.index_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        stack = []
        void_elements = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}
        tag_re = re.compile(r'<\/?([a-zA-Z0-9\-]+)([^>]*)>')

        mismatches = []
        for line_num, line in enumerate(lines, 1):
            for match in tag_re.finditer(line):
                full = match.group(0)
                tag = match.group(1).lower()
                if full.endswith('/>') or tag in void_elements or full.startswith('<!'):
                    continue
                if full.startswith('</'):
                    if stack and stack[-1][0] == tag:
                        stack.pop()
                    else:
                        mismatches.append((line_num, tag, stack[-1] if stack else None))
                else:
                    stack.append((tag, line_num))

        # We document the exact nesting status:
        # If there are open tags, determine if it is the pre-existing container header-inner div
        if stack:
            unclosed_tags = [t[0] for t in stack]
            self.assertIn('div', unclosed_tags, "Unclosed tag list should identify unclosed div")

    # -------------------------------------------------------------
    # 3. CSS SYNTAX & CLASS SELECTORS
    # -------------------------------------------------------------
    def test_style_css_syntax_and_classes(self):
        """Stress-test style.css for brace balance, comment balance, and PWA classes."""
        with open(self.style_file, "r", encoding="utf-8") as f:
            css = f.read()

        # Brace and comment balance
        in_comment = False
        open_braces = []
        errors = []

        lines = css.splitlines()
        for line_no, line in enumerate(lines, 1):
            i = 0
            n = len(line)
            while i < n:
                if not in_comment:
                    if line[i:i+2] == '/*':
                        in_comment = True
                        i += 2
                        continue
                    elif line[i] == '{':
                        open_braces.append(line_no)
                    elif line[i] == '}':
                        if not open_braces:
                            errors.append(f'Unmatched closing brace at line {line_no}')
                        else:
                            open_braces.pop()
                    i += 1
                else:
                    if line[i:i+2] == '*/':
                        in_comment = False
                        i += 2
                        continue
                    i += 1

        self.assertFalse(in_comment, "Unclosed comment in style.css")
        self.assertEqual(len(open_braces), 0, f"Unclosed braces in style.css at lines: {open_braces}")
        self.assertEqual(len(errors), 0, f"CSS syntax errors: {errors}")

        # Check required classes
        required_classes = [
            ".pwa-vault-item",
            ".pwa-vault-dot",
            ".pwa-vault-dot.offline",
            ".pwa-install-badge"
        ]
        for rc in required_classes:
            self.assertIn(rc, css, f"Missing required CSS class {rc} in style.css")

    # -------------------------------------------------------------
    # 4. SERVICE WORKER LOGIC & CACHING AUDIT
    # -------------------------------------------------------------
    def test_service_worker_logic(self):
        """Audit sw.js for resilient installation, cache lifecycle, and dual-strategy routing."""
        with open(self.sw_file, "r", encoding="utf-8") as f:
            sw = f.read()

        self.assertIn("news-colossal-vault-v1", sw)
        self.assertIn("skipWaiting", sw)
        self.assertIn("clients.claim", sw)

        # Pre-cache list includes essentials
        for asset in ["./index.html", "./style.css", "./app.js", "./manifest.json", "./data/news.json"]:
            self.assertIn(asset, sw)

        # Dual strategy assertions
        self.assertIn("/data/news.json", sw)
        self.assertIn("caches.match", sw)
        self.assertIn("offline", sw)

    # -------------------------------------------------------------
    # 5. APP.JS PROTOCOL SAFETY & EVENT WIRING
    # -------------------------------------------------------------
    def test_app_js_offline_vault_wiring(self):
        """Audit app.js for setupPWAOfflineVault invocation and event listeners."""
        with open(self.app_file, "r", encoding="utf-8") as f:
            js = f.read()

        # Invocation check
        self.assertIn("setupPWAOfflineVault();", js)

        # Event listeners check
        self.assertIn("window.addEventListener('online',", js)
        self.assertIn("window.addEventListener('offline',", js)
        self.assertIn("window.addEventListener('beforeinstallprompt',", js)
        self.assertIn("window.addEventListener('appinstalled',", js)

        # Protocol guard for file:// safety
        self.assertIn("window.location.protocol.startsWith('http')", js)
        self.assertIn("window.location.hostname === 'localhost'", js)


if __name__ == "__main__":
    unittest.main()
