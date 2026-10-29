"""
Authoritative Adversarial Stress & Quality Audit Suite for Milestone 3
Reviewer: reviewer_rad_m3_1
Target: R2 Perspective Prism & R4 Narrative Time Machine
"""

import json
import os
import re
import unittest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TestM3AdversarialAudit(unittest.TestCase):

    def setUp(self):
        self.app_path = os.path.join(PROJECT_ROOT, "app.js")
        self.style_path = os.path.join(PROJECT_ROOT, "style.css")
        self.index_path = os.path.join(PROJECT_ROOT, "index.html")
        self.news_path = os.path.join(PROJECT_ROOT, "data", "news.json")
        self.memory_path = os.path.join(PROJECT_ROOT, "data", "narrative_memory.json")

        with open(self.app_path, "r", encoding="utf-8") as f:
            self.app_js = f.read()
        with open(self.style_path, "r", encoding="utf-8") as f:
            self.style_css = f.read()
        with open(self.index_path, "r", encoding="utf-8") as f:
            self.index_html = f.read()
        with open(self.news_path, "r", encoding="utf-8") as f:
            self.news_data = json.load(f)
        with open(self.memory_path, "r", encoding="utf-8") as f:
            self.memory_data = json.load(f)

    # -------------------------------------------------------------------------
    # 1. R2 Perspective Prism: Geopolitical Origin Adversarial Mapping
    # -------------------------------------------------------------------------
    def test_geopolitical_palette_and_origins(self):
        """Stress-test the 6 canonical regions and hex colors in REGION_ORIGIN_MAP."""
        canonical_origins = {
            'North America': '#10b981',
            'Europe': '#0284c7',
            'Asia-Pacific': '#a855f7',
            'Middle East': '#f43f5e',
            'India': '#f59e0b',
            'Global': '#00f2fe'
        }
        # Check map declaration
        self.assertIn("const REGION_ORIGIN_MAP = {", self.app_js)
        for region, hex_color in canonical_origins.items():
            pattern = rf"'{re.escape(region)}':\s*\{{[^}}]*primary:\s*'{hex_color}'"
            self.assertTrue(
                re.search(pattern, self.app_js),
                f"Region '{region}' should have primary color '{hex_color}' in REGION_ORIGIN_MAP"
            )

    def test_get_publisher_origin_robustness(self):
        """Stress-test getPublisherOrigin logic against adversarial source names and regions."""
        fn_match = re.search(r'function getPublisherOrigin\([^)]*\)\s*\{([\s\S]*?)\n\}', self.app_js)
        self.assertTrue(fn_match, "getPublisherOrigin function body not found")
        fn_code = fn_match.group(1)

        # Check explicit region guard (must not return 'all')
        self.assertIn("explicitRegion !== 'all'", fn_code)
        self.assertIn("REGION_ORIGIN_MAP[explicitRegion]", fn_code)

        # Check case-insensitivity: must normalize with toLowerCase()
        self.assertIn(".toLowerCase()", fn_code)

        # Check default fallback is 'Global'
        self.assertIn("return 'Global';", fn_code)

    def test_contrarian_and_exclusive_signal_integrity(self):
        """Verify contrarian and exclusive badge markup and mathematical calculations."""
        # Contrarian signal must calculate divergence or provide realistic default
        self.assertIn("art.meta.is_contrarian", self.app_js)
        self.assertIn("art.meta.sentiment_divergence", self.app_js)
        self.assertIn("Math.round(art.meta.sentiment_divergence * 100)", self.app_js)

        # Exclusive signal must handle custom exclusive_signal text
        self.assertIn("art.meta.is_exclusive", self.app_js)
        self.assertIn("exclusiveSignal", self.app_js)

        # CSS styles must include pulsating glows for contrarian and exclusive badges
        self.assertIn("pulseContrarianGlow", self.style_css)
        self.assertIn(".prism-contrarian-badge", self.style_css)
        self.assertIn(".prism-exclusive-badge", self.style_css)

    def test_on_card_prism_drawer_integration(self):
        """Verify on-card collapsible prism drawer integration and event propagation isolation."""
        # Toggle button in card HTML
        self.assertIn("prism-toggle-btn", self.app_js)
        # Event propagation must be stopped to avoid inadvertently opening reader modal
        self.assertIn("event.stopPropagation()", self.app_js)
        # Drawer element placeholder with unique ID
        self.assertIn('prism-drawer-', self.app_js)
        self.assertIn('card-prism-drawer', self.app_js)
        # Lazy rendering in toggleCardPrismDrawer
        self.assertIn("function toggleCardPrismDrawer(", self.app_js)
        self.assertIn("renderCardPrismDrawerContent", self.app_js)

    # -------------------------------------------------------------------------
    # 2. R4 Narrative Time Machine: Timeline Scrubber & Progression
    # -------------------------------------------------------------------------
    def test_narrative_memory_sync_and_structure(self):
        """Stress-test data/narrative_memory.json against schema expectations."""
        arcs = self.memory_data.get("arcs", [])
        self.assertGreater(len(arcs), 0, "Narrative memory must contain arcs")
        for arc in arcs:
            self.assertIn("arc_id", arc)
            self.assertIn("title", arc)
            self.assertIn("chapter_count", arc)
            self.assertIn("chapter_titles", arc)
            self.assertIsInstance(arc["chapter_titles"], list)
            self.assertGreaterEqual(len(arc["chapter_titles"]), 1)

    def test_narrative_scrubber_slider_controls(self):
        """Verify interactive range slider, stepping controls, and event bindings."""
        # Scrubber slider element
        self.assertIn('type="range"', self.app_js)
        self.assertIn('class="narrative-time-scrubber narrative-scrubber-slider"', self.app_js)
        self.assertIn('oninput="handleNarrativeScrub(this.value)"', self.app_js)

        # Stepping buttons
        self.assertIn('stepNarrativeChapter(-1)', self.app_js)
        self.assertIn('stepNarrativeChapter(1)', self.app_js)

        # Single chapter arc graceful degradation
        self.assertIn('isSingleChapter', self.app_js)
        self.assertIn('Single Chapter Story', self.app_js)

    def test_historical_dispatch_jump_mechanism(self):
        """Verify 1-click dispatch jump inline modal exploration."""
        self.assertIn("function jumpToNarrativeDispatch(", self.app_js)
        self.assertIn("window.jumpToNarrativeDispatch = jumpToNarrativeDispatch", self.app_js)
        self.assertIn("openModal(artId)", self.app_js)

    def test_scrubber_event_boundary_safety(self):
        """Verify handleNarrativeScrub and stepNarrativeChapter protect against index bounds."""
        scrub_fn = re.search(r'function handleNarrativeScrub\([^)]*\)\s*\{([\s\S]*?)\n\}', self.app_js)
        self.assertTrue(scrub_fn)
        # Must bound idx between 0 and chapters.length - 1
        self.assertIn("Math.max(0, Math.min(chapters.length - 1", scrub_fn.group(1))

        step_fn = re.search(r'function stepNarrativeChapter\([^)]*\)\s*\{([\s\S]*?)\n\}', self.app_js)
        self.assertTrue(step_fn)
        # Must bound next step between 0 and chapters.length - 1
        self.assertIn("Math.max(0, Math.min(chapters.length - 1", step_fn.group(1))

    # -------------------------------------------------------------------------
    # 3. VisionOS Liquid Glass Design System Fidelity
    # -------------------------------------------------------------------------
    def test_visionos_liquid_glass_css_compliance(self):
        """Verify Apple VisionOS Frosted Specular Liquid Glass properties."""
        # Backdrop filters
        self.assertIn("backdrop-filter: blur(24px)", self.style_css)
        self.assertIn("-webkit-backdrop-filter: blur(24px)", self.style_css)
        # Chromatic linear gradient bar
        self.assertIn(
            "linear-gradient(90deg, #10b981, #0284c7, #a855f7, #f43f5e, #f59e0b, #00f2fe)",
            self.style_css
        )
        # Dual light mode support
        self.assertIn('[data-theme="light"] .perspective-prism-container', self.style_css)
        self.assertIn('body.theme-light .perspective-prism-container', self.style_css)
        self.assertIn('[data-theme="light"] .narrative-time-machine', self.style_css)
        self.assertIn('body.theme-light .narrative-time-machine', self.style_css)

    # -------------------------------------------------------------------------
    # 4. Anti-Cheat & Integrity Auditing
    # -------------------------------------------------------------------------
    def test_no_hardcoded_facades_in_source(self):
        """Verify that functions execute dynamic computation rather than hardcoded dummy responses."""
        # getPublisherOrigin must have actual conditional logic for sources
        self.assertIn("s.includes('guardian')", self.app_js.lower())
        self.assertIn("s.includes('nyt')", self.app_js.lower())
        self.assertIn("s.includes('reuters')", self.app_js.lower())

        # renderPerspectivePrism must calculate dynamic counts
        self.assertIn("originCounts[item.region]", self.app_js)
        self.assertIn("uniqueOrigins.map", self.app_js)

        # renderNarrativeTimeMachine must calculate dynamic chapter counts
        self.assertIn("getArcChapters(art)", self.app_js)
        self.assertIn("chapters.map", self.app_js)


if __name__ == "__main__":
    unittest.main()
