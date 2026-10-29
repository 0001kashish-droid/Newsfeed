"""
Milestone 1 Test Suite: Offline News Vault & PWA Foundation (R6)
Verifies manifest.json schema, standalone icons, sw.js dual caching strategies,
HTML/CSS VisionOS integration, and guarded Service Worker registration in app.js.
"""

import json
import os
import struct
import unittest
import xml.etree.ElementTree as ET

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TestM1PWAOfflineVault(unittest.TestCase):

    def setUp(self):
        self.manifest_path = os.path.join(PROJECT_ROOT, "manifest.json")
        self.sw_path = os.path.join(PROJECT_ROOT, "sw.js")
        self.index_path = os.path.join(PROJECT_ROOT, "index.html")
        self.style_path = os.path.join(PROJECT_ROOT, "style.css")
        self.app_path = os.path.join(PROJECT_ROOT, "app.js")
        self.assets_dir = os.path.join(PROJECT_ROOT, "assets")

    def test_manifest_json_validity_and_schema(self):
        """Verify manifest.json conforms to W3C Web App Manifest specification."""
        self.assertTrue(os.path.exists(self.manifest_path), "manifest.json must exist in project root")

        with open(self.manifest_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertIn("name", data)
        self.assertEqual(data["name"], "News Colossal — Global News Intelligence & Digest")
        self.assertIn("short_name", data)
        self.assertEqual(data["short_name"], "News Colossal")
        self.assertIn("description", data)
        self.assertEqual(data["start_url"], "./index.html")
        self.assertEqual(data["display"], "standalone")
        self.assertEqual(data["background_color"], "#0b1120")
        self.assertEqual(data["theme_color"], "#0b1120")

        self.assertIn("icons", data)
        self.assertGreaterEqual(len(data["icons"]), 2, "Manifest must declare multiple icon sizes")

        # Verify all icons referenced in manifest actually exist on disk
        for icon in data["icons"]:
            self.assertIn("src", icon)
            self.assertIn("sizes", icon)
            self.assertIn("type", icon)
            icon_file = os.path.join(PROJECT_ROOT, icon["src"])
            self.assertTrue(os.path.exists(icon_file), f"Manifest icon '{icon['src']}' not found on disk")

    def test_icon_assets_exist_and_are_valid(self):
        """Verify 192x192 and 512x512 SVG and PNG icons exist and have valid structure."""
        svg_192 = os.path.join(self.assets_dir, "icon-192.svg")
        svg_512 = os.path.join(self.assets_dir, "icon-512.svg")
        png_192 = os.path.join(self.assets_dir, "icon-192.png")
        png_512 = os.path.join(self.assets_dir, "icon-512.png")

        self.assertTrue(os.path.exists(svg_192), "assets/icon-192.svg must exist")
        self.assertTrue(os.path.exists(svg_512), "assets/icon-512.svg must exist")
        self.assertTrue(os.path.exists(png_192), "assets/icon-192.png must exist")
        self.assertTrue(os.path.exists(png_512), "assets/icon-512.png must exist")

        # Verify SVGs are parseable XML
        tree_192 = ET.parse(svg_192)
        root_192 = tree_192.getroot()
        self.assertTrue(root_192.tag.endswith("svg"), "Root element must be <svg>")

        tree_512 = ET.parse(svg_512)
        root_512 = tree_512.getroot()
        self.assertTrue(root_512.tag.endswith("svg"), "Root element must be <svg>")

        # Verify PNG binary headers (Magic bytes and IHDR dimensions)
        with open(png_192, "rb") as f:
            header = f.read(24)
            self.assertEqual(header[:8], b"\x89PNG\r\n\x1a\n", "icon-192.png must have valid PNG magic bytes")
            width, height = struct.unpack(">II", header[16:24])
            self.assertEqual((width, height), (192, 192), "icon-192.png dimensions must be 192x192")

        with open(png_512, "rb") as f:
            header = f.read(24)
            self.assertEqual(header[:8], b"\x89PNG\r\n\x1a\n", "icon-512.png must have valid PNG magic bytes")
            width, height = struct.unpack(">II", header[16:24])
            self.assertEqual((width, height), (512, 512), "icon-512.png dimensions must be 512x512")

    def test_service_worker_architecture_and_strategies(self):
        """Verify sw.js implements dual caching strategies, resilient installation, and cache lifecycle."""
        self.assertTrue(os.path.exists(self.sw_path), "sw.js must exist in project root")

        with open(self.sw_path, "r", encoding="utf-8") as f:
            sw_code = f.read()

        # Check Cache Key
        self.assertIn("news-colossal-vault-v1", sw_code, "sw.js must declare cache version bucket")

        # Check Pre-cache list
        self.assertIn("index.html", sw_code)
        self.assertIn("style.css", sw_code)
        self.assertIn("app.js", sw_code)
        self.assertIn("manifest.json", sw_code)
        self.assertIn("data/news.json", sw_code)
        self.assertIn("data/podcasts.json", sw_code)

        # Check Resilient install with individual catch
        self.assertIn(".catch(", sw_code, "sw.js must use catch isolation during precache")
        self.assertIn("skipWaiting", sw_code, "sw.js must skip waiting on install")

        # Check Activation cache deletion and client claim
        self.assertIn("caches.delete", sw_code, "sw.js must clean old cache versions")
        self.assertIn("clients.claim", sw_code, "sw.js must claim clients on activate")

        # Check Dual Caching Strategies
        self.assertIn("data/news.json", sw_code)
        self.assertIn("data/podcasts.json", sw_code)
        self.assertIn("offline", sw_code)

    def test_index_html_pwa_integration(self):
        """Verify index.html contains manifest links and Quick Tools Offline Vault UI."""
        with open(self.index_path, "r", encoding="utf-8") as f:
            html = f.read()

        self.assertIn('<link rel="manifest" href="manifest.json"', html)
        self.assertIn('<link rel="apple-touch-icon" href="assets/icon-192.svg"', html)
        self.assertIn('id="pwaVaultIndicatorBtn"', html)
        self.assertIn('id="pwaVaultDot"', html)
        self.assertIn('id="pwaVaultLabel"', html)
        self.assertIn('id="pwaInstallBadge"', html)
        self.assertIn('class="header-tools-popover"', html)

    def test_style_css_pwa_vault_styling(self):
        """Verify style.css contains VisionOS liquid glass styling for PWA vault elements."""
        with open(self.style_path, "r", encoding="utf-8") as f:
            css = f.read()

        self.assertIn(".pwa-vault-item", css)
        self.assertIn(".pwa-vault-dot", css)
        self.assertIn(".pwa-vault-dot.offline", css)
        self.assertIn(".pwa-install-badge", css)

    def test_app_js_pwa_wiring_and_protocol_safety(self):
        """Verify app.js wires setupPWAOfflineVault with protocol safety guards."""
        with open(self.app_path, "r", encoding="utf-8") as f:
            js = f.read()

        self.assertIn("setupPWAOfflineVault", js)
        self.assertIn("pwaVaultIndicatorBtn", js)
        self.assertIn("pwaVaultLabel", js)
        self.assertIn("pwaVaultDot", js)
        self.assertIn("pwaInstallBadge", js)
        self.assertIn("beforeinstallprompt", js)
        self.assertIn("appinstalled", js)

        # Confirm guarded registration for zero console errors on file:// protocol
        self.assertIn("window.location.protocol.startsWith('http')", js)
        self.assertIn("window.location.hostname === 'localhost'", js)

        # Confirm setupPWAOfflineVault is invoked in initialization
        self.assertIn("setupPWAOfflineVault();", js)


if __name__ == "__main__":
    unittest.main()
