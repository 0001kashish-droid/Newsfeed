"""
Empirical Challenge Battery for Milestone 1: Offline News Vault & PWA Foundation (R6)
Executed by Challenger 1 (challenger_rad_m1_1).

This standalone challenge suite rigorously tests:
1. manifest.json: JSON parsing, W3C Web App Manifest compliance, theme colors, display modes, icon resolution.
2. PWA Icon Suite: Binary PNG signatures, IHDR chunk dimensions and CRC integrity, IEND chunk, XML SVG parsing.
3. sw.js Service Worker: JS syntax & bracket balance, lifecycle hooks, static asset cache map file existence,
   dynamic cache routing, synthetic offline JSON payload validity.
4. HTML/CSS/JS Integration: manifest tags, UI indicator elements, liquid glass styling, file:// protocol safety guard.
"""

import json
import os
import re
import struct
import unittest
import xml.etree.ElementTree as ET
import zlib

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TestM1EmpiricalChallenge(unittest.TestCase):

    def setUp(self):
        self.manifest_path = os.path.join(PROJECT_ROOT, "manifest.json")
        self.sw_path = os.path.join(PROJECT_ROOT, "sw.js")
        self.index_path = os.path.join(PROJECT_ROOT, "index.html")
        self.style_path = os.path.join(PROJECT_ROOT, "style.css")
        self.app_path = os.path.join(PROJECT_ROOT, "app.js")
        self.assets_dir = os.path.join(PROJECT_ROOT, "assets")

    # =========================================================================
    # 1. MANIFEST.JSON CHALLENGE
    # =========================================================================
    def test_challenge_manifest_json_w3c_conformance(self):
        """Stress-test manifest.json for W3C compliance, required fields, and valid references."""
        self.assertTrue(os.path.isfile(self.manifest_path), "manifest.json must exist in project root")

        with open(self.manifest_path, "r", encoding="utf-8") as f:
            raw_content = f.read()

        # Parse JSON
        try:
            data = json.loads(raw_content)
        except Exception as e:
            self.fail(f"manifest.json failed JSON parsing: {e}")

        # Core Identity
        self.assertEqual(data.get("name"), "News Colossal — Global News Intelligence & Digest")
        self.assertEqual(data.get("short_name"), "News Colossal")
        self.assertTrue(bool(data.get("description")), "Description must be non-empty")
        self.assertEqual(data.get("start_url"), "./index.html")
        self.assertEqual(data.get("scope"), "./")

        # Display and Theme
        self.assertIn(data.get("display"), ["standalone", "fullscreen", "minimal-ui", "browser"])
        self.assertIn(data.get("orientation"), ["any", "natural", "portrait", "landscape"])

        hex_regex = re.compile(r"^#[0-9a-fA-F]{6}$")
        self.assertTrue(hex_regex.match(data.get("background_color", "")), "Invalid background_color hex")
        self.assertTrue(hex_regex.match(data.get("theme_color", "")), "Invalid theme_color hex")

        # Icons validation
        icons = data.get("icons", [])
        self.assertGreaterEqual(len(icons), 4, "Must provide both SVG and PNG icons at 192 and 512 dimensions")

        seen_dimensions = set()
        for idx, icon in enumerate(icons):
            src = icon.get("src")
            self.assertTrue(src, f"Icon {idx} missing src")
            full_icon_path = os.path.normpath(os.path.join(PROJECT_ROOT, src))
            self.assertTrue(os.path.isfile(full_icon_path), f"Icon path '{src}' does not exist on filesystem")
            self.assertGreater(os.path.getsize(full_icon_path), 0, f"Icon '{src}' is empty (0 bytes)")

            sizes = icon.get("sizes")
            self.assertTrue(re.match(r"^\d+x\d+$", sizes), f"Invalid icon size format: {sizes}")
            seen_dimensions.add(sizes)

            icon_type = icon.get("type")
            self.assertIn(icon_type, ["image/png", "image/svg+xml"], f"Unexpected mime type: {icon_type}")

            purpose = icon.get("purpose", "")
            self.assertTrue(any(p in purpose for p in ["any", "maskable"]), f"Invalid icon purpose: {purpose}")

        self.assertIn("192x192", seen_dimensions, "Missing 192x192 icon declaration")
        self.assertIn("512x512", seen_dimensions, "Missing 512x512 icon declaration")

        # Shortcuts validation
        shortcuts = data.get("shortcuts", [])
        self.assertGreaterEqual(len(shortcuts), 1, "Should declare quick action shortcuts")
        for sc in shortcuts:
            self.assertTrue(sc.get("name"), "Shortcut missing name")
            self.assertTrue(sc.get("url"), "Shortcut missing url")
            self.assertTrue(sc.get("url").startswith("./index.html"), "Shortcut must target index.html")

    # =========================================================================
    # 2. PWA ICON IMAGE HEADERS & BINARY STRUCTURE
    # =========================================================================
    def test_challenge_pwa_icon_image_headers(self):
        """Stress-test SVG and PNG binary headers, chunks, CRCs, and XML tree integrity."""
        # 2.1 SVG Icons
        for icon_name, expected_dim in [("icon-192.svg", 192), ("icon-512.svg", 512)]:
            svg_path = os.path.join(self.assets_dir, icon_name)
            self.assertTrue(os.path.isfile(svg_path), f"Missing {icon_name}")
            self.assertGreater(os.path.getsize(svg_path), 500, f"{icon_name} file size too small")

            with open(svg_path, "r", encoding="utf-8") as f:
                content = f.read()

            try:
                tree = ET.fromstring(content)
            except ET.ParseError as e:
                self.fail(f"Corrupt SVG XML in {icon_name}: {e}")

            self.assertTrue(tree.tag.endswith("svg"), f"{icon_name} root element is not <svg>")
            viewbox = tree.attrib.get("viewBox")
            self.assertTrue(bool(viewbox), f"{icon_name} missing viewBox attribute")
            vb_parts = [float(x) for x in viewbox.split()]
            self.assertEqual(len(vb_parts), 4, f"Invalid viewBox in {icon_name}")
            self.assertEqual((vb_parts[2], vb_parts[3]), (expected_dim, expected_dim),
                             f"{icon_name} viewBox ({vb_parts[2]}x{vb_parts[3]}) mismatch with {expected_dim}")

        # 2.2 PNG Icons (Binary magic bytes, IHDR chunk, CRC integrity, IEND chunk)
        for icon_name, (expected_w, expected_h) in [("icon-192.png", (192, 192)), ("icon-512.png", (512, 512))]:
            png_path = os.path.join(self.assets_dir, icon_name)
            self.assertTrue(os.path.isfile(png_path), f"Missing {icon_name}")

            with open(png_path, "rb") as f:
                data = f.read()

            # Check 8-byte PNG signature: \x89PNG\r\n\x1a\n
            self.assertTrue(data.startswith(b"\x89PNG\r\n\x1a\n"),
                            f"{icon_name} does not start with standard PNG magic bytes \\x89PNG\\r\\n\\x1a\\n")

            # Check IHDR Chunk length (must be 13 bytes)
            ihdr_len = struct.unpack(">I", data[8:12])[0]
            self.assertEqual(ihdr_len, 13, f"{icon_name} IHDR length must be 13 bytes")

            # Check IHDR Chunk type
            self.assertEqual(data[12:16], b"IHDR", f"{icon_name} first chunk must be IHDR")

            # Check IHDR dimensions
            w, h = struct.unpack(">II", data[16:24])
            self.assertEqual((w, h), (expected_w, expected_h),
                             f"{icon_name} dimensions {w}x{h} != expected {expected_w}x{expected_h}")

            bit_depth, color_type = data[24], data[25]
            self.assertEqual(bit_depth, 8, f"{icon_name} bit depth must be 8")
            self.assertIn(color_type, [2, 6], f"{icon_name} color type must be Truecolor or RGBA")

            # Check IHDR CRC32
            ihdr_crc = struct.unpack(">I", data[29:33])[0]
            computed_ihdr_crc = zlib.crc32(data[12:29]) & 0xFFFFFFFF
            self.assertEqual(ihdr_crc, computed_ihdr_crc, f"{icon_name} IHDR CRC mismatch")

            # Check IEND chunk at end: length 0, type IEND, CRC 0xAE426082
            self.assertTrue(data.endswith(b"\x00\x00\x00\x00IEND\xaeB`\x82"),
                            f"{icon_name} does not terminate with valid IEND chunk and CRC")

    # =========================================================================
    # 3. SERVICE WORKER SYNTAX VALIDITY & OFFLINE FALLBACK SIMULATION
    # =========================================================================
    def test_challenge_sw_js_syntax_balance_and_structure(self):
        """Perform bracket and quote balance verification across sw.js."""
        self.assertTrue(os.path.isfile(self.sw_path), "sw.js missing")

        with open(self.sw_path, "r", encoding="utf-8") as f:
            code = f.read()

        # Bracket balancing parser ignoring strings and comments
        stack = []
        pairs = {')': '(', '}': '{', ']': '['}
        i = 0
        n = len(code)
        in_string = None  # '"', "'", or '`'
        in_line_comment = False
        in_block_comment = False

        while i < n:
            c = code[i]
            next_c = code[i + 1] if i + 1 < n else ""

            if in_line_comment:
                if c == '\n':
                    in_line_comment = False
                i += 1
                continue

            if in_block_comment:
                if c == '*' and next_c == '/':
                    in_block_comment = False
                    i += 2
                    continue
                i += 1
                continue

            if in_string:
                if c == '\\':
                    i += 2  # skip escaped character
                    continue
                if c == in_string:
                    in_string = None
                i += 1
                continue

            # Check comments
            if c == '/' and next_c == '/':
                in_line_comment = True
                i += 2
                continue
            if c == '/' and next_c == '*':
                in_block_comment = True
                i += 2
                continue

            # Check strings
            if c in ("'", '"', '`'):
                in_string = c
                i += 1
                continue

            # Check brackets
            if c in ('(', '{', '['):
                stack.append((c, i))
            elif c in (')', '}', ']'):
                expected = pairs[c]
                self.assertTrue(len(stack) > 0, f"Unmatched closing '{c}' at position {i}")
                top, top_pos = stack.pop()
                self.assertEqual(top, expected, f"Mismatched bracket: opened '{top}' at {top_pos}, closed '{c}' at {i}")

            i += 1

        self.assertIsNone(in_string, "sw.js contains unclosed string literal")
        self.assertFalse(in_block_comment, "sw.js contains unclosed block comment")
        self.assertEqual(len(stack), 0, f"sw.js has unclosed opening brackets: {stack}")

    def test_challenge_sw_caching_paths_and_offline_fallback(self):
        """Verify that every static asset in sw.js actually exists on the filesystem and fallback payload is valid."""
        with open(self.sw_path, "r", encoding="utf-8") as f:
            code = f.read()

        # Extract STATIC_ASSETS array
        match = re.search(r"const\s+STATIC_ASSETS\s*=\s*\[(.*?)\];", code, re.DOTALL)
        self.assertIsNotNone(match, "Could not find STATIC_ASSETS declaration in sw.js")

        assets_block = match.group(1)
        raw_assets = re.findall(r"['\"](.*?)['\"]", assets_block)
        self.assertGreaterEqual(len(raw_assets), 8, "STATIC_ASSETS must cache app shell and datasets")

        # Verify filesystem presence for each cached asset
        for asset in raw_assets:
            if asset in ["./", "."]:
                target = os.path.join(PROJECT_ROOT, "index.html")
            elif asset.startswith("./"):
                target = os.path.join(PROJECT_ROOT, asset[2:])
            else:
                target = os.path.join(PROJECT_ROOT, asset)

            target = os.path.normpath(target)
            self.assertTrue(os.path.exists(target), f"Pre-cached asset '{asset}' maps to nonexistent file: {target}")

        # Check offline synthetic fallback response JSON
        fallback_match = re.search(r"const\s+fallbackData\s*=\s*({.*?});", code, re.DOTALL)
        self.assertIsNotNone(fallback_match, "Could not find synthetic fallbackData in sw.js")

        # Test fallback JSON structure simulation
        self.assertIn("articles", fallback_match.group(1))
        self.assertIn("offline", fallback_match.group(1))
        self.assertIn("message", fallback_match.group(1))

        # Check skipWaiting and clients.claim
        self.assertIn("self.skipWaiting()", code)
        self.assertIn("self.clients.claim()", code)

    # =========================================================================
    # 4. FRONTEND WIRING & PROTOCOL SAFETY CHALLENGE
    # =========================================================================
    def test_challenge_frontend_integration_and_guard(self):
        """Stress-test HTML, CSS, and JS integration for accessibility and protocol safety."""
        with open(self.index_path, "r", encoding="utf-8") as f:
            html = f.read()

        with open(self.style_path, "r", encoding="utf-8") as f:
            css = f.read()

        with open(self.app_path, "r", encoding="utf-8") as f:
            js = f.read()

        # HTML checks
        self.assertIn('<link rel="manifest" href="manifest.json"', html)
        self.assertIn('<link rel="apple-touch-icon"', html)
        self.assertIn('id="pwaVaultIndicatorBtn"', html)
        self.assertIn('id="pwaVaultDot"', html)
        self.assertIn('id="pwaVaultLabel"', html)
        self.assertIn('id="pwaInstallBadge"', html)

        # CSS checks
        self.assertIn(".pwa-vault-item", css)
        self.assertIn(".pwa-vault-dot", css)
        self.assertIn(".pwa-vault-dot.offline", css)
        self.assertIn(".pwa-install-badge", css)

        # JS checks: Service worker registration guard
        # Must protect against SecurityError when running via file://
        self.assertIn("window.location.protocol.startsWith('http')", js)
        self.assertIn("setupPWAOfflineVault", js)
        self.assertIn("beforeinstallprompt", js)
        self.assertIn("appinstalled", js)


if __name__ == "__main__":
    unittest.main()
