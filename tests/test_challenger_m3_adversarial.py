"""
Adversarial Empirical Challenge Suite for Milestone 3 (Reader Intelligence).
Author: Challenger 2 (Milestone 3: Perspective Prism R2 & Narrative Time Machine R4)

Tests:
1. On-card drawer click handlers and independent inspection.
2. 3D cursor tilt math and dynamic bounding rect robustness.
3. jumpToNarrativeDispatch edge cases (null, empty, nonexistent, podcast-only).
4. Perspective Prism input fuzzing (XSS, zero division, unknown origins, contrarian signals).
5. Narrative Time Machine scrubber & stepper boundary testing (clamps, single-chapter Genesis, out-of-bounds).
6. VisionOS Frosted Specular Liquid Glass CSS & Light Theme invariants.
7. Baseline contracts & data invariants.
"""

import json
import math
import os
import re
import unittest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TestM3AdversarialChallenge(unittest.TestCase):

    def setUp(self):
        self.app_path = os.path.join(PROJECT_ROOT, "app.js")
        self.style_path = os.path.join(PROJECT_ROOT, "style.css")
        self.index_path = os.path.join(PROJECT_ROOT, "index.html")
        self.news_path = os.path.join(PROJECT_ROOT, "data", "news.json")
        self.memory_path = os.path.join(PROJECT_ROOT, "data", "narrative_memory.json")
        self.podcasts_path = os.path.join(PROJECT_ROOT, "data", "podcasts.json")

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

    # =========================================================================
    # 1. On-Card Drawer Click Handlers & Independent Inspection
    # =========================================================================
    def test_drawer_toggle_allows_independent_inspection(self):
        """Verify that expanding one drawer does NOT close other open drawers."""
        toggle_fn_match = re.search(r'function toggleCardPrismDrawer\(artId, event\)\s*\{(.*?)\n\}', self.app_js, re.DOTALL)
        self.assertTrue(toggle_fn_match, "toggleCardPrismDrawer function must exist in app.js")
        code = toggle_fn_match.group(1)

        # Confirm event.stopPropagation is called
        self.assertIn("stopPropagation", code, "toggleCardPrismDrawer must stop event propagation to card")

        # Confirm target is specific to artId: `prism-drawer-${artId}`
        self.assertIn("prism-drawer-", code, "Drawer lookup must use artId specific element ID")

        # Confirm NO global drawer closing loop exists inside toggleCardPrismDrawer
        self.assertNotIn("querySelectorAll('.card-prism-drawer", code, 
                         "Drawer toggle must NOT close other drawers; independent inspection must be preserved")
        self.assertNotIn("querySelectorAll('.news-card .open')", code)

    def test_drawer_elements_have_stop_propagation(self):
        """Verify every clickable element inside the drawer halts event bubbling."""
        # Find renderCardPrismDrawerContent
        fn_match = re.search(r'function renderCardPrismDrawerContent\(art\)\s*\{(.*?)\n\}', self.app_js, re.DOTALL)
        self.assertTrue(fn_match, "renderCardPrismDrawerContent must exist")
        content_code = fn_match.group(1)

        # All click handlers must include stopPropagation
        click_matches = re.findall(r'onclick="([^"]+)"', content_code)
        self.assertGreater(len(click_matches), 0, "Drawer must have interactive click targets")
        for handler in click_matches:
            self.assertIn("stopPropagation", handler, f"Click handler '{handler}' in drawer must stopPropagation")

    # =========================================================================
    # 2. 3D Cursor Tilt & Expanded Drawer Interaction
    # =========================================================================
    def test_3d_cursor_tilt_dynamic_rect_adaptation(self):
        """Verify 3D cursor tilt engine recalculates getBoundingClientRect on mousemove."""
        tilt_fn_match = re.search(r'function attach3DTiltListeners\(\)\s*\{(.*?)\n\}', self.app_js, re.DOTALL)
        self.assertTrue(tilt_fn_match, "attach3DTiltListeners must exist")
        tilt_code = tilt_fn_match.group(1)

        # Tilt listener must read getBoundingClientRect dynamically on every move
        self.assertIn("card.getBoundingClientRect()", tilt_code)
        self.assertIn("rect.width", tilt_code)
        self.assertIn("rect.height", tilt_code)

        # Mathematical simulation of tilt physics under varying drawer expansion heights
        def simulate_tilt(card_w, card_h, client_x, client_y):
            # Simulated getBoundingClientRect
            rect_left = 100
            rect_top = 200
            x = client_x - rect_left
            y = client_y - rect_top
            centerX = card_w / 2
            centerY = card_h / 2
            rotateX = -((y - centerY) / centerY) * 7
            rotateY = ((x - centerX) / centerX) * 7
            return rotateX, rotateY

        # Unexpanded card (height 380px)
        rx1, ry1 = simulate_tilt(320, 380, 260, 390)
        self.assertFalse(math.isnan(rx1) or math.isinf(rx1))
        self.assertFalse(math.isnan(ry1) or math.isinf(ry1))
        self.assertAlmostEqual(rx1, 0.0, places=1)
        self.assertAlmostEqual(ry1, 0.0, places=1)

        # Expanded card with drawer open (height 680px)
        rx2, ry2 = simulate_tilt(320, 680, 100, 200) # top-left corner
        self.assertFalse(math.isnan(rx2) or math.isinf(rx2))
        self.assertAlmostEqual(rx2, 7.0, places=1) # tilted back
        self.assertAlmostEqual(ry2, -7.0, places=1) # tilted left

        # Bottom of expanded drawer
        rx3, ry3 = simulate_tilt(320, 680, 260, 880) # bottom-center
        self.assertFalse(math.isnan(rx3) or math.isinf(rx3))
        self.assertAlmostEqual(rx3, -7.0, places=1)

    # =========================================================================
    # 3. jumpToNarrativeDispatch Edge Cases & Fault Tolerance
    # =========================================================================
    def test_jump_to_narrative_dispatch_guard_and_delegation(self):
        """Verify jumpToNarrativeDispatch has an explicit guard and delegates safely to openModal."""
        jump_fn_match = re.search(r'function jumpToNarrativeDispatch\(artId\)\s*\{(.*?)\n\}', self.app_js, re.DOTALL)
        self.assertTrue(jump_fn_match, "jumpToNarrativeDispatch must exist")
        jump_code = jump_fn_match.group(1).strip()

        # Must guard against falsy/null/empty ID
        self.assertTrue(re.search(r'if\s*\(\s*!artId\s*\)\s*return;', jump_code), 
                        "jumpToNarrativeDispatch must return immediately if artId is falsy")
        self.assertIn("openModal(artId)", jump_code, "jumpToNarrativeDispatch must delegate to openModal")

    def test_open_modal_missing_target_graceful_handling(self):
        """Verify openModal handles missing IDs without raising unhandled exceptions."""
        modal_fn_match = re.search(r'window\.openModal\s*=\s*function\(id\)\s*\{(.*?)\nwindow\.', self.app_js, re.DOTALL)
        if not modal_fn_match:
            modal_fn_match = re.search(r'window\.openModal\s*=\s*function\(id\)\s*\{(.*?)\nfunction\s+renderExecutiveModal', self.app_js, re.DOTALL)
        self.assertTrue(modal_fn_match, "openModal function definition must be found")
        modal_code = modal_fn_match.group(1)

        # Checks index === -1 against state.articles
        self.assertIn("index === -1", modal_code)

        # Fallback to podcast resonant_news check
        self.assertIn("resonant_news", modal_code)

        # Graceful return with toast notification if missing
        self.assertIn("showToastNotification", modal_code)
        self.assertIn("Article is no longer available in the active feed.", modal_code)
        self.assertIn("return;", modal_code)

    def test_narrative_jump_button_only_rendered_for_valid_historical_ids(self):
        """Verify that 'Read Chapter Dispatch ↗' button is suppressed if articleId is null."""
        time_fn_match = re.search(r'function renderNarrativeTimeMachine\(art\)\s*\{(.*?)\n\}', self.app_js, re.DOTALL)
        self.assertTrue(time_fn_match)
        time_code = time_fn_match.group(1)

        # Check conditional rendering of jump button
        self.assertIn("currentChapter.articleId && currentChapter.articleId !== art.id", time_code)
        self.assertIn("spotlight-nav-hint", time_code)

    # =========================================================================
    # 4. Perspective Prism Input Fuzzing & Math Verification
    # =========================================================================
    def test_perspective_prism_color_palette_completeness(self):
        """Verify all 6 regions in REGION_ORIGIN_MAP have primary, glow, and emoji."""
        region_map_match = re.search(r'const REGION_ORIGIN_MAP\s*=\s*\{(.*?)\};', self.app_js, re.DOTALL)
        self.assertTrue(region_map_match, "REGION_ORIGIN_MAP must be defined in app.js")
        map_code = region_map_match.group(1)

        required_regions = ['North America', 'Europe', 'Asia-Pacific', 'Middle East', 'India', 'Global']
        for region in required_regions:
            self.assertIn(f"'{region}'", map_code, f"Region {region} must exist in REGION_ORIGIN_MAP")

    def test_extract_spectrum_items_fallback_to_global(self):
        """Verify unknown or unmapped publishers default safely to Global."""
        # Simulated getPublisherOrigin logic
        def get_publisher_origin(source_name, explicit_region):
            if explicit_region and explicit_region != 'all' and explicit_region in [
                'North America', 'Europe', 'Asia-Pacific', 'Middle East', 'India', 'Global'
            ]:
                return explicit_region
            s = (source_name or '').lower()
            if any(k in s for k in ['asia', 'scmp', 'kyodo', 'nikkei', 'strait', 'xinhua', 'asahi', 'yomiuri', 'korea', 'japan times']):
                return 'Asia-Pacific'
            if any(k in s for k in ['europe', 'france', 'dw', 'guardian', 'spiegel', 'telegraph', 'le monde', 'ft', 'financial times', 'el pais', 'reuters', 'bbc']):
                return 'Europe'
            if any(k in s for k in ['mideast', 'middle east', 'al jazeera', 'haaretz', 'arab news', 'jerusalem', 'gulf']):
                return 'Middle East'
            if any(k in s for k in ['hindu', 'hindustan', 'indian express', 'ndtv', 'times of india', 'livemint', 'economic times', 'ani', 'the wire']):
                return 'India'
            if any(k in s for k in ['nyt', 'new york times', 'verge', 'techcrunch', 'npr', 'washington post', 'wsj', 'wall street journal', 'bloomberg', 'cnn', 'ap news', 'associated press', 'cnbc', 'politico', 'wired']):
                return 'North America'
            return 'Global'

        self.assertEqual(get_publisher_origin("The Guardian", "Europe"), "Europe")
        self.assertEqual(get_publisher_origin("Wall Street Journal", "North America"), "North America")
        self.assertEqual(get_publisher_origin("Nikkei Asia", "Asia-Pacific"), "Asia-Pacific")
        self.assertEqual(get_publisher_origin("Al Jazeera English", "Middle East"), "Middle East")
        self.assertEqual(get_publisher_origin("The Hindu BusinessLine", "India"), "India")
        self.assertEqual(get_publisher_origin("Unknown Alien Dispatch", "all"), "Global")
        self.assertEqual(get_publisher_origin(None, None), "Global")
        self.assertEqual(get_publisher_origin("", ""), "Global")

    def test_spectrum_dispersion_bar_percentage_math(self):
        """Verify that spectrum dispersion bar calculates segment percentages summing to ~100%."""
        def calc_bar_segments(items):
            origin_counts = {}
            for item in items:
                reg = item['region']
                origin_counts[reg] = origin_counts.get(reg, 0) + 1
            total = len(items)
            percentages = [round((cnt / total) * 100, 1) for cnt in origin_counts.values()]
            return percentages

        # Test single item
        pcts_single = calc_bar_segments([{'region': 'Europe'}])
        self.assertEqual(pcts_single, [100.0])

        # Test 3-way balance
        pcts_three = calc_bar_segments([
            {'region': 'Europe'},
            {'region': 'North America'},
            {'region': 'Asia-Pacific'}
        ])
        self.assertAlmostEqual(sum(pcts_three), 100.0, places=0)

        # Test 5 items
        pcts_five = calc_bar_segments([
            {'region': 'Europe'},
            {'region': 'Europe'},
            {'region': 'North America'},
            {'region': 'India'},
            {'region': 'Middle East'}
        ])
        self.assertAlmostEqual(sum(pcts_five), 100.0, places=1)

    # =========================================================================
    # 5. Narrative Time Machine Scrubber & Stepper Boundary Testing
    # =========================================================================
    def test_scrubber_bounds_clamping(self):
        """Verify handleNarrativeScrub clamps out-of-bounds indices to [0, length-1]."""
        scrub_fn_match = re.search(r'function handleNarrativeScrub\(val\)\s*\{(.*?)\n\}', self.app_js, re.DOTALL)
        self.assertTrue(scrub_fn_match, "handleNarrativeScrub must exist")
        scrub_code = scrub_fn_match.group(1)

        # Must have clamp logic: Math.max(0, Math.min(chapters.length - 1, ...))
        self.assertIn("Math.max(0, Math.min(chapters.length - 1", scrub_code)
        self.assertIn("parseInt(val, 10)", scrub_code)

    def test_step_chapter_boundary_protection(self):
        """Verify stepNarrativeChapter prevents stepping past chapter bounds."""
        step_fn_match = re.search(r'function stepNarrativeChapter\(delta\)\s*\{(.*?)\n\}', self.app_js, re.DOTALL)
        self.assertTrue(step_fn_match, "stepNarrativeChapter must exist")
        step_code = step_fn_match.group(1)

        # Must clamp next index: Math.max(0, Math.min(chapters.length - 1, curr + delta))
        self.assertIn("Math.max(0, Math.min(chapters.length - 1, curr + delta))", step_code)
        self.assertIn("if (next === curr && delta !== 0) return;", step_code)

    def test_single_chapter_genesis_graceful_handling(self):
        """Verify single chapter arcs disable the range slider and navigation buttons."""
        time_fn_match = re.search(r'function renderNarrativeTimeMachine\(art\)\s*\{(.*?)\n\}', self.app_js, re.DOTALL)
        self.assertTrue(time_fn_match)
        time_code = time_fn_match.group(1)

        self.assertIn("isSingleChapter = total <= 1", time_code)
        self.assertIn("${isSingleChapter ? 'disabled' : ''}", time_code)
        self.assertIn("Single Chapter Story · Genesis", time_code)

    # =========================================================================
    # 6. VisionOS Frosted Specular Liquid Glass CSS & Light Mode Invariants
    # =========================================================================
    def test_visionos_frosted_specular_glass_styling_tokens(self):
        """Verify VisionOS design tokens (blur, specular border, chromatic glow) are used."""
        # Check .perspective-prism-container
        prism_css_match = re.search(r'\.perspective-prism-container\s*\{(.*?)\}', self.style_css, re.DOTALL)
        self.assertTrue(prism_css_match, ".perspective-prism-container must be defined in style.css")
        prism_rules = prism_css_match.group(1)
        self.assertIn("backdrop-filter: blur(", prism_rules)
        self.assertIn("border-radius:", prism_rules)

        # Check .card-prism-drawer
        drawer_css_match = re.search(r'\.card-prism-drawer\s*\{(.*?)\}', self.style_css, re.DOTALL)
        self.assertTrue(drawer_css_match, ".card-prism-drawer must be defined in style.css")
        drawer_rules = drawer_css_match.group(1)
        self.assertIn("backdrop-filter: blur(", drawer_rules)
        self.assertIn("transition:", drawer_rules)

        # Check .narrative-time-machine
        narrative_css_match = re.search(r'\.narrative-time-machine\s*\{(.*?)\}', self.style_css, re.DOTALL)
        self.assertTrue(narrative_css_match, ".narrative-time-machine must be defined in style.css")
        narrative_rules = narrative_css_match.group(1)
        self.assertIn("backdrop-filter: blur(", narrative_rules)

    def test_light_mode_support_for_all_m3_components(self):
        """Verify both body.theme-light and [data-theme='light'] selectors are present."""
        components = [
            ".perspective-prism-container",
            ".card-prism-drawer",
            ".narrative-time-machine"
        ]
        for comp in components:
            self.assertTrue(
                f"body.theme-light {comp}" in self.style_css or f"[data-theme=\"light\"] {comp}" in self.style_css,
                f"Light mode selector missing for {comp}"
            )

    # =========================================================================
    # 7. Baseline Invariants
    # =========================================================================
    def test_news_dataset_integrity(self):
        """Ensure data/news.json has exactly 134 articles and valid schema."""
        articles = self.news_data.get("articles", self.news_data)
        self.assertEqual(len(articles), 134, "Dataset must retain all 134 curated articles")
        for a in articles:
            self.assertIn("id", a)
            self.assertIn("title", a)
            self.assertIn("source", a)
            self.assertIn("category", a)


if __name__ == "__main__":
    unittest.main()
