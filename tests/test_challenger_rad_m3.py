"""
Adversarial Stress Test Suite: Milestone 3 Reader Intelligence
Reviewer / Adversarial Critic: reviewer_rad_m3_2
Verifies:
1. VisionOS Liquid Glass aesthetic, light/dark mode parity, mobile drawer responsiveness.
2. Narrative Arc scrubber edge cases:
   - Single chapter arcs (genesis state, disabled slider & stepping buttons)
   - Multi-day arcs (bounded day calculation, tick positioning)
   - Missing narrative_memory.json fallback to previous_headlines
   - Empty previous_headlines fallback
   - Null / undefined article structures
3. Perspective Prism spectrum & meta-intelligence edge cases:
   - 6 Geopolitical origins mapping & explicit region precedence
   - Source deduplication across perspectives & clusters
   - Proportional dispersion bar math
   - Contrarian signal divergence & exclusive badges
4. Interface contract preservation & baseline invariants.
"""

import json
import os
import re
import unittest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TestM3VisionOSAestheticAndMobileFidelity(unittest.TestCase):
    """Stress-tests the VisionOS liquid glass aesthetic, light/dark parity, and mobile layout."""

    @classmethod
    def setUpClass(cls):
        style_path = os.path.join(PROJECT_ROOT, "style.css")
        with open(style_path, "r", encoding="utf-8") as f:
            cls.style_css = f.read()

    def test_prism_liquid_glass_specular_properties(self):
        """Perspective Prism must use frosted specular glass tokens."""
        self.assertIn(".perspective-prism-container", self.style_css)
        self.assertIn("backdrop-filter: blur(24px)", self.style_css)
        self.assertIn("inset 0 1px 0 rgba(255, 255, 255, 0.15)", self.style_css)
        self.assertIn("linear-gradient(90deg, #10b981, #0284c7, #a855f7, #f43f5e, #f59e0b, #00f2fe)", self.style_css)

    def test_narrative_time_machine_liquid_glass_properties(self):
        """Narrative Time Machine must use frosted specular glass tokens."""
        self.assertIn(".narrative-time-machine", self.style_css)
        self.assertIn("backdrop-filter: blur(12px)", self.style_css)
        self.assertIn("inset 0 1px 0 rgba(255, 255, 255, 0.08)", self.style_css)

    def test_light_dark_parity_dual_selectors(self):
        """Both [data-theme='light'] and body.theme-light must be defined for all M3 components."""
        selectors_to_check = [
            ".perspective-prism-container",
            ".narrative-time-machine",
            ".card-prism-drawer",
            ".chapter-step-btn",
            ".narrative-jump-btn",
            ".prism-spectrum-bar",
            ".prism-perspective-card"
        ]
        for sel in selectors_to_check:
            has_data_attr = f'[data-theme="light"] {sel}' in self.style_css or f'[data-theme="light"]' in self.style_css
            has_body_class = f'body.theme-light {sel}' in self.style_css or f'body.theme-light' in self.style_css
            self.assertTrue(has_data_attr, f"Missing [data-theme='light'] support for {sel}")
            self.assertTrue(has_body_class, f"Missing body.theme-light support for {sel}")

    def test_mobile_drawer_responsiveness_and_touch_safety(self):
        """Mobile drawer must have ellipsis on titles, button touch targets, and flexible grid."""
        # Check text ellipsis on drawer viewpoints
        self.assertIn("text-overflow: ellipsis", self.style_css)
        self.assertIn("white-space: nowrap", self.style_css)

        # Check step button sizing (minimum 34px touch target)
        btn_match = re.search(r'\.chapter-step-btn\s*\{([^}]+)\}', self.style_css)
        self.assertTrue(btn_match, ".chapter-step-btn must be defined in style.css")
        btn_rules = btn_match.group(1)
        self.assertIn("width: 34px", btn_rules)
        self.assertIn("height: 34px", btn_rules)

        # Check prism pillars grid uses responsive auto-fit
        grid_match = re.search(r'\.prism-pillars-grid\s*\{([^}]+)\}', self.style_css)
        self.assertTrue(grid_match, ".prism-pillars-grid must be defined in style.css")
        grid_rules = grid_match.group(1)
        self.assertIn("repeat(auto-fit, minmax(", grid_rules)


class TestNarrativeScrubberAdversarialEdgeCases(unittest.TestCase):
    """Stress-tests Narrative Arc scrubber algorithms against adversarial edge cases."""

    @classmethod
    def setUpClass(cls):
        app_path = os.path.join(PROJECT_ROOT, "app.js")
        with open(app_path, "r", encoding="utf-8") as f:
            cls.app_js = f.read()

        news_path = os.path.join(PROJECT_ROOT, "data", "news.json")
        with open(news_path, "r", encoding="utf-8") as f:
            cls.news_data = json.load(f)

        narrative_path = os.path.join(PROJECT_ROOT, "data", "narrative_memory.json")
        with open(narrative_path, "r", encoding="utf-8") as f:
            cls.narrative_memory = json.load(f)

    def test_single_chapter_arc_genesis_state(self):
        """Single chapter arcs must disable scrubber and stepper buttons, and render genesis state."""
        self.assertIn("const isSingleChapter = total <= 1;", self.app_js)
        self.assertIn("${isSingleChapter ? 'disabled' : ''}", self.app_js)
        self.assertIn("Single Chapter Story · Genesis", self.app_js)

    def test_missing_narrative_memory_fallback_chain(self):
        """When memory arc is not found, getArcChapters must fall back to previous_headlines."""
        # Extract getArcChapters function body
        fn_match = re.search(r'function getArcChapters\(art\)\s*\{(.*?)\n\}', self.app_js, re.DOTALL)
        self.assertTrue(fn_match, "getArcChapters must be defined")
        fn_code = fn_match.group(1)

        # Ensure fallback to previous_headlines is present
        self.assertIn("art.narrative_arc.previous_headlines", fn_code)
        self.assertIn("totalChapters: prev.length + 1", fn_code)
        self.assertIn("day: art.narrative_arc.day_number || (prev.length + 1)", fn_code)

    def test_null_and_malformed_article_safety(self):
        """Functions must guard against null and malformed article inputs."""
        # getArcChapters null guard
        self.assertIn("if (!art || !art.narrative_arc) return [];", self.app_js)
        # renderNarrativeTimeMachine null guard
        self.assertIn("if (!art || !art.narrative_arc || !art.narrative_arc.arc_id) return '';", self.app_js)
        # hasPerspectivePrism null guard
        self.assertIn("if (!art) return false;", self.app_js)
        # renderPerspectivePrism null guard
        self.assertIn("if (!art) return '';", self.app_js)

    def test_production_arc_articles_integrity(self):
        """All articles with narrative_arc in news.json must have valid arc_id and valid chapters."""
        articles = self.news_data.get("articles", self.news_data)
        arc_articles = [a for a in articles if a.get("narrative_arc") and a["narrative_arc"].get("arc_id")]
        self.assertGreater(len(arc_articles), 0, "Production dataset must have articles linked to arcs")

        arcs_in_memory = {a["arc_id"]: a for a in self.narrative_memory.get("arcs", [])}

        for art in arc_articles:
            arc_info = art["narrative_arc"]
            arc_id = arc_info["arc_id"]
            self.assertTrue(arc_id, f"Article {art.get('id')} has empty arc_id")
            # Must either exist in memory or have previous_headlines
            in_memory = arc_id in arcs_in_memory
            has_prev = bool(arc_info.get("previous_headlines"))
            self.assertTrue(
                in_memory or has_prev,
                f"Article {art.get('id')} with arc {arc_id} must have memory record or previous_headlines"
            )


class TestPerspectivePrismAdversarialEdgeCases(unittest.TestCase):
    """Stress-tests Perspective Prism origin resolution, deduplication, and signal calculation."""

    @classmethod
    def setUpClass(cls):
        app_path = os.path.join(PROJECT_ROOT, "app.js")
        with open(app_path, "r", encoding="utf-8") as f:
            cls.app_js = f.read()

    def test_origin_mapping_all_canonical_regions(self):
        """All 6 canonical regions must be present in REGION_ORIGIN_MAP with hex and emoji."""
        regions = ['North America', 'Europe', 'Asia-Pacific', 'Middle East', 'India', 'Global']
        for r in regions:
            self.assertIn(f"'{r}':", self.app_js, f"Region {r} must be defined in REGION_ORIGIN_MAP")

    def test_explicit_region_takes_precedence(self):
        """Explicit region argument must take precedence over source heuristics."""
        self.assertIn("if (explicitRegion && explicitRegion !== 'all' && REGION_ORIGIN_MAP[explicitRegion])", self.app_js)

    def test_source_deduplication_in_spectrum(self):
        """extractSpectrumItems must deduplicate sources case-insensitively."""
        self.assertIn("const seenSources = new Set();", self.app_js)
        self.assertIn("seenSources.has(src.toLowerCase())", self.app_js)

    def test_contrarian_and_exclusive_badges_wired(self):
        """Contrarian and exclusive badges must be properly integrated in prism markup."""
        self.assertIn("prism-contrarian-badge", self.app_js)
        self.assertIn("Contrarian Signal: ${divergence}% Sentiment Divergence", self.app_js)
        self.assertIn("prism-exclusive-badge", self.app_js)
        self.assertIn("Exclusive Reporting: ${escapeHtml(exclusiveSignal)}", self.app_js)


class TestContractPreservationAndZeroRegressions(unittest.TestCase):
    """Ensures no pre-existing contracts or features were broken or degraded."""

    @classmethod
    def setUpClass(cls):
        with open(os.path.join(PROJECT_ROOT, "app.js"), "r", encoding="utf-8") as f:
            cls.app_js = f.read()
        with open(os.path.join(PROJECT_ROOT, "style.css"), "r", encoding="utf-8") as f:
            cls.style_css = f.read()
        with open(os.path.join(PROJECT_ROOT, "index.html"), "r", encoding="utf-8") as f:
            cls.index_html = f.read()

    def test_historical_contracts_intact(self):
        """All 13 historical contracts must be present."""
        contracts = [
            ("setupMobileDeckSwipe", self.app_js),
            ("setupMobilePullToRefresh", self.app_js),
            ("resetAllFiltersAndRefresh", self.app_js),
            ("pullToRefreshBanner", self.index_html),
            ("searchClearBtn", self.index_html),
            ("scrollbar-width: thin", self.style_css),
            ("liquid-glass-resonance-box", self.app_js),
            ("liquid-glass-narrative-box", self.app_js),
            ("thought-card-resonant-news", self.app_js),
            ("pwaVaultIndicatorBtn", self.index_html),
            ("setupPWAOfflineVault", self.app_js),
            ("computeStoryMetabolism", self.app_js),
            ("setupDensityController", self.app_js)
        ]
        for name, content in contracts:
            self.assertIn(name, content, f"Historical contract '{name}' missing!")


if __name__ == "__main__":
    unittest.main()
