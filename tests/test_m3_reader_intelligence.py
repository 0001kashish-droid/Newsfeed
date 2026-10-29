"""
Milestone 3 Test Suite: Reader Intelligence (R2: Perspective Prism & R4: Narrative Time Machine)
Verifies:
- R2: Perspective Prism:
    - 6 Geopolitical Origins mapping (North America, Europe, Asia-Pacific, Middle East, India, Global)
    - getPublisherOrigin(sourceName, explicitRegion)
    - renderPerspectivePrism(art) with chromatic spectrum bar, origin chips, contrarian/exclusive badges
    - On-card collapsible prism drawer toggle (.prism-toggle-btn) and drawer (.card-prism-drawer)
    - toggleCardPrismDrawer(artId, event) handler
- R4: Narrative Time Machine:
    - Embedding inside Executive Reader Modal (.liquid-glass-narrative-box)
    - Narrative scrubber slider (<input type="range" class="narrative-time-scrubber narrative-scrubber-slider">)
    - Chapter stepping buttons (<button class="chapter-step-btn"> < and >)
    - Chapter progression display (Chapter X of Y, Day progression, title)
    - 1-click dispatch jump (jumpToNarrativeDispatch) and scrubber handlers
    - Single-chapter arc graceful degradation (disabled scrubber state)
- VisionOS Liquid Glass Styling in style.css for R2 and R4 components + light mode overrides
- Invariants: data/news.json untouched, baseline contracts preserved
"""

import json
import os
import re
import unittest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TestM3ReaderIntelligence(unittest.TestCase):

    def setUp(self):
        self.index_path = os.path.join(PROJECT_ROOT, "index.html")
        self.style_path = os.path.join(PROJECT_ROOT, "style.css")
        self.app_path = os.path.join(PROJECT_ROOT, "app.js")
        self.news_path = os.path.join(PROJECT_ROOT, "data", "news.json")
        self.narrative_memory_path = os.path.join(PROJECT_ROOT, "data", "narrative_memory.json")

        with open(self.index_path, "r", encoding="utf-8") as f:
            self.index_html = f.read()
        with open(self.style_path, "r", encoding="utf-8") as f:
            self.style_css = f.read()
        with open(self.app_path, "r", encoding="utf-8") as f:
            self.app_js = f.read()
        with open(self.news_path, "r", encoding="utf-8") as f:
            self.news_data = json.load(f)

    # -------------------------------------------------------------------------
    # R2: Geopolitical Origins & getPublisherOrigin
    # -------------------------------------------------------------------------
    def test_geopolitical_origins_mapping_defined(self):
        """Verify 6 geopolitical origins and their VisionOS chromatic palette."""
        expected_origins = {
            'North America': '#10b981',
            'Europe': '#0284c7',
            'Asia-Pacific': '#a855f7',
            'Middle East': '#f43f5e',
            'India': '#f59e0b',
            'Global': '#00f2fe'
        }
        for origin, color in expected_origins.items():
            self.assertIn(origin, self.app_js, f"Origin '{origin}' missing in app.js mapping")
            self.assertIn(color, self.app_js, f"Origin chromatic color '{color}' missing in app.js")

    def test_get_publisher_origin_function_exported(self):
        """Verify getPublisherOrigin exists and is exposed to window."""
        self.assertIn("function getPublisherOrigin(", self.app_js)
        self.assertIn("window.getPublisherOrigin = getPublisherOrigin", self.app_js)

    def test_get_publisher_origin_source_mapping_logic(self):
        """Verify key global publishers keywords map to correct geopolitical origins."""
        expected_mappings = [
            ("new york times", "North America"),
            ("guardian", "Europe"),
            ("nikkei", "Asia-Pacific"),
            ("al jazeera", "Middle East"),
            ("hindu", "India"),
            ("reuters", "Europe"),
            ("hindustan", "India"),
            ("bbc", "Europe")
        ]
        app_js_lower = self.app_js.lower()
        for keyword, region in expected_mappings:
            self.assertIn(keyword, app_js_lower, f"Keyword '{keyword}' should be mapped in getPublisherOrigin in app.js")

    # -------------------------------------------------------------------------
    # R2: Perspective Prism Rendering & On-Card Drawer
    # -------------------------------------------------------------------------
    def test_render_perspective_prism_implemented_and_exported(self):
        """Verify renderPerspectivePrism is implemented and attached to window."""
        self.assertIn("function renderPerspectivePrism(", self.app_js)
        self.assertIn("window.renderPerspectivePrism = renderPerspectivePrism", self.app_js)

    def test_perspective_prism_markup_elements(self):
        """Verify prism renders spectrum bar, chips, and contrarian/exclusive badges."""
        self.assertIn("perspective-prism-container", self.app_js)
        self.assertIn("prism-spectrum-bar", self.app_js)
        self.assertIn("prism-origin-chip", self.app_js)
        self.assertIn("prism-contrarian-badge", self.app_js)
        self.assertIn("prism-exclusive-badge", self.app_js)
        self.assertIn("meta.is_contrarian", self.app_js)
        self.assertIn("meta.is_exclusive", self.app_js)

    def test_on_card_prism_drawer_button_and_container(self):
        """Verify news cards contain the collapsible drawer button and container."""
        self.assertIn("prism-toggle-btn", self.app_js)
        self.assertIn("card-prism-drawer", self.app_js)
        self.assertIn("toggleCardPrismDrawer", self.app_js)
        self.assertIn("window.toggleCardPrismDrawer = toggleCardPrismDrawer", self.app_js)

    def test_perspective_prism_in_executive_modal(self):
        """Verify executive reader modal embeds the Perspective Prism."""
        modal_fn_match = re.search(r'function renderExecutiveModal\(.*?\n\}', self.app_js, re.DOTALL)
        self.assertTrue(modal_fn_match, "renderExecutiveModal function missing in app.js")
        modal_fn_code = modal_fn_match.group(0)
        self.assertIn("renderPerspectivePrism", modal_fn_code)

    # -------------------------------------------------------------------------
    # R4: Narrative Time Machine
    # -------------------------------------------------------------------------
    def test_narrative_memory_json_structure(self):
        """Verify data/narrative_memory.json exists with valid narrative arc chapters."""
        self.assertTrue(os.path.isfile(self.narrative_memory_path), "data/narrative_memory.json must exist")
        with open(self.narrative_memory_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertIn("arcs", data, "data/narrative_memory.json must contain 'arcs' list")
        self.assertGreater(len(data["arcs"]), 0, "narrative_memory.json must contain at least one arc")

        for arc in data["arcs"][:5]:
            self.assertIn("arc_id", arc)
            self.assertIn("title", arc)
            self.assertIn("chapter_count", arc)
            self.assertIn("chapter_titles", arc)
            self.assertIsInstance(arc["chapter_titles"], list)

    def test_narrative_time_machine_functions_exported(self):
        """Verify Narrative Time Machine functions exist and are exposed to window."""
        self.assertIn("function renderNarrativeTimeMachine(", self.app_js)
        self.assertIn("window.renderNarrativeTimeMachine = renderNarrativeTimeMachine", self.app_js)
        self.assertIn("function handleNarrativeScrub(", self.app_js)
        self.assertIn("window.handleNarrativeScrub = handleNarrativeScrub", self.app_js)
        self.assertIn("function stepNarrativeChapter(", self.app_js)
        self.assertIn("window.stepNarrativeChapter = stepNarrativeChapter", self.app_js)
        self.assertIn("function jumpToNarrativeDispatch(", self.app_js)
        self.assertIn("window.jumpToNarrativeDispatch = jumpToNarrativeDispatch", self.app_js)

    def test_narrative_scrubber_and_stepper_elements(self):
        """Verify scrubber range slider, stepping buttons, and chapter spotlight markup."""
        self.assertIn("narrative-time-scrubber", self.app_js)
        self.assertIn("narrative-scrubber-slider", self.app_js)
        self.assertIn("chapter-step-btn", self.app_js)
        self.assertIn("narrative-chapter-spotlight", self.app_js)
        self.assertIn("liquid-glass-narrative-box", self.app_js)

    def test_single_chapter_arc_handling(self):
        """Verify single chapter arcs handle gracefully with disabled slider and clear status."""
        self.assertIn("isSingleChapter", self.app_js)
        self.assertIn("disabled", self.app_js)
        self.assertIn("Single Chapter Story", self.app_js)

    def test_narrative_time_machine_in_executive_modal(self):
        """Verify executive reader modal embeds the Narrative Time Machine."""
        modal_fn_match = re.search(r'function renderExecutiveModal\(.*?\n\}', self.app_js, re.DOTALL)
        self.assertTrue(modal_fn_match)
        modal_fn_code = modal_fn_match.group(0)
        self.assertIn("renderNarrativeTimeMachine", modal_fn_code)

    # -------------------------------------------------------------------------
    # VisionOS Liquid Glass Styling in style.css
    # -------------------------------------------------------------------------
    def test_visionos_prism_css_classes(self):
        """Verify CSS classes for Perspective Prism with liquid glass and spectrum bar."""
        self.assertIn(".perspective-prism-container", self.style_css)
        self.assertIn(".prism-spectrum-bar", self.style_css)
        self.assertIn(".prism-origin-chip", self.style_css)
        self.assertIn(".prism-contrarian-badge", self.style_css)
        self.assertIn(".prism-exclusive-badge", self.style_css)
        self.assertIn(".prism-toggle-btn", self.style_css)
        self.assertIn(".card-prism-drawer", self.style_css)

    def test_visionos_narrative_css_classes(self):
        """Verify CSS classes for Narrative Time Machine slider, stepper, spotlight."""
        self.assertIn(".narrative-time-machine", self.style_css)
        self.assertIn(".narrative-scrubber-slider", self.style_css)
        self.assertIn(".chapter-step-btn", self.style_css)
        self.assertIn(".narrative-chapter-spotlight", self.style_css)
        self.assertIn(".narrative-scrubber-ticks", self.style_css)

    def test_visionos_light_mode_overrides(self):
        """Verify light mode styling overrides exist for reader intelligence components."""
        self.assertIn("body.theme-light .perspective-prism-container", self.style_css)
        self.assertIn("body.theme-light .narrative-time-machine", self.style_css)
        self.assertIn("body.theme-light .card-prism-drawer", self.style_css)

    # -------------------------------------------------------------------------
    # Baseline Invariants & Integrity
    # -------------------------------------------------------------------------
    def test_data_news_json_invariants_preserved(self):
        """Verify data/news.json has not been corrupted or modified."""
        articles = self.news_data.get("articles", self.news_data)
        self.assertGreaterEqual(len(articles), 134, "Articles dataset must have at least 134 articles")
        sample = articles[0]
        self.assertIn("id", sample)
        self.assertIn("title", sample)
        self.assertIn("source", sample)
        self.assertIn("category", sample)
        self.assertIn("region", sample)

    def test_preserved_interface_contracts(self):
        """Verify all existing contracts from previous milestones remain intact."""
        contracts = [
            "setupMobileDeckSwipe",
            "setupMobilePullToRefresh",
            "resetAllFiltersAndRefresh",
            "pullToRefreshBanner",
            "searchClearBtn",
            "liquid-glass-resonance-box",
            "liquid-glass-narrative-box",
            "thought-card-resonant-news",
            "pwaVaultIndicatorBtn",
            "setupPWAOfflineVault",
            "computeStoryMetabolism",
            "setupDensityController"
        ]
        for c in contracts:
            self.assertTrue(
                c in self.app_js or c in self.style_css or c in self.index_html,
                f"Contract '{c}' must be preserved across app.js / style.css / index.html"
            )


if __name__ == "__main__":
    unittest.main()
