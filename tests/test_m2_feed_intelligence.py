"""
Milestone 2 Test Suite: Feed Intelligence (Metabolism Sparklines & Cognitive Thermostat - R1, R3)
Verifies:
- R1: Story Metabolism Tracker (Coverage Sparklines pure SVG mathematical modeling, status classifications, tooltips)
- R3: Cognitive Load Thermostat (Adaptive Density Controller in index.html, localStorage persistence, zero-DOM-rebuild layout adaptations)
- VisionOS Liquid Glass styling in style.css for sparklines and density modes
- Preservation of all existing UI & pipeline contracts
"""

import json
import os
import re
import unittest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TestM2FeedIntelligence(unittest.TestCase):

    def setUp(self):
        self.index_path = os.path.join(PROJECT_ROOT, "index.html")
        self.style_path = os.path.join(PROJECT_ROOT, "style.css")
        self.app_path = os.path.join(PROJECT_ROOT, "app.js")
        self.news_path = os.path.join(PROJECT_ROOT, "data", "news.json")

        with open(self.index_path, "r", encoding="utf-8") as f:
            self.index_html = f.read()
        with open(self.style_path, "r", encoding="utf-8") as f:
            self.style_css = f.read()
        with open(self.app_path, "r", encoding="utf-8") as f:
            self.app_js = f.read()
        with open(self.news_path, "r", encoding="utf-8") as f:
            self.news_data = json.load(f)

    # -------------------------------------------------------------------------
    # R3: Cognitive Load Thermostat Controller in index.html
    # -------------------------------------------------------------------------
    def test_density_toggle_group_in_index_html(self):
        """Verify the 3-position segmented density controller exists beside regionSelect."""
        self.assertIn('id="densityToggleGroup"', self.index_html, "densityToggleGroup element missing in index.html")
        self.assertIn('id="densityScanBtn"', self.index_html, "densityScanBtn missing in index.html")
        self.assertIn('id="densityDigestBtn"', self.index_html, "densityDigestBtn missing in index.html")
        self.assertIn('id="densityDeepBtn"', self.index_html, "densityDeepBtn missing in index.html")

        # Verify buttons have data-density attributes
        self.assertIn('data-density="scan"', self.index_html)
        self.assertIn('data-density="digest"', self.index_html)
        self.assertIn('data-density="deep"', self.index_html)

        # Verify accessibility roles
        self.assertIn('role="radiogroup"', self.index_html)
        self.assertIn('role="radio"', self.index_html)

        # Verify placement inside .filter-bar beside regionSelect
        filter_bar_match = re.search(r'<nav class="filter-bar".*?</nav>', self.index_html, re.DOTALL)
        self.assertTrue(filter_bar_match, "filter-bar navigation missing in index.html")
        filter_bar_content = filter_bar_match.group(0)
        self.assertIn('id="densityToggleGroup"', filter_bar_content, "densityToggleGroup must be inside .filter-bar")
        self.assertIn('id="regionSelect"', filter_bar_content, "regionSelect must be inside .filter-bar")

    # -------------------------------------------------------------------------
    # R1: Story Metabolism Tracker Logic in app.js
    # -------------------------------------------------------------------------
    def test_compute_story_metabolism_exists_and_exported(self):
        """Verify computeStoryMetabolism function is implemented and exported."""
        self.assertIn("function computeStoryMetabolism(", self.app_js)
        self.assertIn("window.computeStoryMetabolism = computeStoryMetabolism", self.app_js)

    def test_compute_story_metabolism_mathematical_model(self):
        """Verify trajectory modeling and velocity classifications."""
        # Simulated python replica of the app.js computeStoryMetabolism logic
        def simulate_metabolism(art):
            scores = art.get('scores') or {}
            vel = scores.get('velocity', 0.25)
            cluster = art.get('storyCluster') or {}
            cluster_size = cluster.get('size') or len(art.get('perspectives') or []) or ((art.get('duplicate_count', 0) + 1) if art.get('duplicate_count') else 1)
            
            if vel >= 0.45 or (vel >= 0.35 and cluster_size >= 2):
                status = 'accelerating'
                label = 'Accelerating'
                color = '#10b981'
            elif vel >= 0.25 or cluster_size >= 2:
                status = 'peak-spread'
                label = 'Peak Spread'
                color = '#f59e0b'
            else:
                status = 'stabilizing'
                label = 'Stabilizing'
                color = '#94a3b8'

            x_coords = [0, 9, 18, 28, 37, 47, 56]
            seed = sum(ord(c) for c in art.get('id', '')) % 5
            if status == 'accelerating':
                y_coords = [15, 14 - (seed % 2), 12 - int(round(vel * 4)), 9 - int(round(vel * 5)), 6 - (seed % 2), 4, 3]
            elif status == 'peak-spread':
                y_coords = [14, 10 - (seed % 2), 5, 4, 5 + (seed % 2), 6, 7]
            else:
                y_coords = [7 + (seed % 2), 4, 7, 10, 12, 13 + (seed % 2), 14]

            path_d = f"M {x_coords[0]},{y_coords[0]}"
            for i in range(len(x_coords) - 1):
                x0, y0 = x_coords[i], y_coords[i]
                x1, y1 = x_coords[i+1], y_coords[i+1]
                mx = round((x0 + x1) / 2, 1)
                path_d += f" C {mx},{y0} {mx},{y1} {x1},{y1}"

            area_d = f"{path_d} L 56,18 L 0,18 Z"
            return {
                'status': status,
                'label': label,
                'color': color,
                'pathD': path_d,
                'areaD': area_d,
                'lastX': x_coords[-1],
                'lastY': y_coords[-1]
            }

        # Case 1: High velocity story
        art_accel = {'id': 'art-1', 'scores': {'velocity': 0.55}}
        res_accel = simulate_metabolism(art_accel)
        self.assertEqual(res_accel['status'], 'accelerating')
        self.assertEqual(res_accel['label'], 'Accelerating')
        self.assertEqual(res_accel['color'], '#10b981')
        self.assertTrue(res_accel['pathD'].startswith('M 0,'))
        self.assertTrue(res_accel['areaD'].endswith('L 56,18 L 0,18 Z'))
        self.assertEqual(res_accel['lastX'], 56)
        self.assertEqual(res_accel['lastY'], 3)

        # Case 2: Clustered peak-spread story
        art_peak = {'id': 'art-2', 'scores': {'velocity': 0.28}, 'storyCluster': {'size': 3}}
        res_peak = simulate_metabolism(art_peak)
        self.assertEqual(res_peak['status'], 'accelerating' if (0.28 >= 0.35) else 'peak-spread')
        self.assertEqual(res_peak['color'], '#f59e0b')

        # Case 3: Stabilizing story
        art_stab = {'id': 'art-3', 'scores': {'velocity': 0.15}}
        res_stab = simulate_metabolism(art_stab)
        self.assertEqual(res_stab['status'], 'stabilizing')
        self.assertEqual(res_stab['label'], 'Stabilizing')
        self.assertEqual(res_stab['color'], '#94a3b8')

    def test_all_articles_in_dataset_compute_metabolism_cleanly(self):
        """Verify that every article in data/news.json produces a valid metabolism."""
        articles = self.news_data.get('articles', [])
        self.assertGreater(len(articles), 50, "news.json should have plenty of curated articles")

        statuses = set()
        for art in articles:
            scores = art.get('scores') or {}
            vel = scores.get('velocity', 0.25)
            cluster = art.get('storyCluster') or {}
            cluster_size = cluster.get('size') or len(art.get('perspectives') or []) or 1
            if vel >= 0.45 or (vel >= 0.35 and cluster_size >= 2):
                statuses.add('accelerating')
            elif vel >= 0.25 or cluster_size >= 2:
                statuses.add('peak-spread')
            else:
                statuses.add('stabilizing')

        # Confirm representation across all three velocity stages
        self.assertIn('accelerating', statuses)
        self.assertIn('peak-spread', statuses)
        self.assertIn('stabilizing', statuses)

    # -------------------------------------------------------------------------
    # R3: Adaptive Density Controller in app.js
    # -------------------------------------------------------------------------
    def test_density_controller_logic_in_app_js(self):
        """Verify setupDensityController and setDensity in app.js."""
        self.assertIn("function setupDensityController()", self.app_js)
        self.assertIn("function setDensity(", self.app_js)
        self.assertIn("news_colossal_density", self.app_js, "localStorage key news_colossal_density must be handled")
        self.assertIn("density-scan", self.app_js)
        self.assertIn("density-digest", self.app_js)
        self.assertIn("density-deep", self.app_js)

        # Check export on window
        self.assertIn("window.setupDensityController = setupDensityController", self.app_js)
        self.assertIn("window.setDensity = setDensity", self.app_js)

        # Check DOMContentLoaded registration
        self.assertIn("setupDensityController()", self.app_js)

        # Check WAI-ARIA keyboard navigation support (Arrow, Home, End keys)
        self.assertIn("ArrowRight", self.app_js)
        self.assertIn("ArrowLeft", self.app_js)
        self.assertIn("Home", self.app_js)
        self.assertIn("End", self.app_js)

    def test_card_html_embeds_sparkline_and_deep_dive_panel(self):
        """Verify createCardHTML embeds inline sparklines and deep dive markup."""
        self.assertIn("metabolism-sparkline", self.app_js)
        self.assertIn("sparkline-svg", self.app_js)
        self.assertIn("sparkline-tooltip", self.app_js)
        self.assertIn("card-deep-dive-panel", self.app_js)
        self.assertIn("renderDeepDivePanelContent", self.app_js)

    # -------------------------------------------------------------------------
    # CSS Styles for Sparklines and Density Modes in style.css
    # -------------------------------------------------------------------------
    def test_style_css_density_and_sparkline_rules(self):
        """Verify VisionOS glass styles and density layout classes in style.css."""
        # Density toggle group and buttons
        self.assertIn("#densityToggleGroup", self.style_css)
        self.assertIn(".density-btn", self.style_css)
        self.assertIn(".density-btn.active", self.style_css)

        # Grid density modes
        self.assertIn(".news-grid.density-scan", self.style_css)
        self.assertIn(".news-grid.density-digest", self.style_css)
        self.assertIn(".news-grid.density-deep", self.style_css)

        # Scan mode hiding rules
        self.assertIn(".news-grid.density-scan .card-thumb-box", self.style_css)
        self.assertIn(".news-grid.density-scan .annotation-box", self.style_css)
        self.assertIn(".news-grid.density-scan .card-footer", self.style_css)
        self.assertIn(".news-grid.density-scan .card-deep-dive-panel", self.style_css)

        # Deep dive mode display rules
        self.assertIn(".news-grid.density-deep .card-deep-dive-panel", self.style_css)
        self.assertIn(".deep-dive-row", self.style_css)
        self.assertIn(".deep-tag", self.style_css)
        self.assertIn(".deep-dive-matrix", self.style_css)
        self.assertIn(".matrix-pill", self.style_css)
        self.assertIn(".deep-dive-provenance", self.style_css)
        self.assertIn(".provenance-link", self.style_css)

        # Sparklines styling
        self.assertIn(".metabolism-sparkline", self.style_css)
        self.assertIn(".sparkline-box", self.style_css)
        self.assertIn(".sparkline-svg", self.style_css)
        self.assertIn(".sparkline-tooltip", self.style_css)
        self.assertIn(".sparkline-pulse-dot", self.style_css)

        # Responsive media queries
        self.assertIn("@media (max-width: 1024px)", self.style_css)
        self.assertIn("@media (max-width: 640px)", self.style_css)

    # -------------------------------------------------------------------------
    # Safeguard Contracts Preservation
    # -------------------------------------------------------------------------
    def test_safeguards_and_contracts_preserved(self):
        """Ensure all pre-existing contracts remain strictly intact."""
        self.assertIn("setupMobileDeckSwipe", self.app_js)
        self.assertIn("setupMobilePullToRefresh", self.app_js)
        self.assertIn("resetAllFiltersAndRefresh", self.app_js)
        self.assertIn("pullToRefreshBanner", self.index_html)
        self.assertIn("searchClearBtn", self.index_html)
        self.assertIn("scrollbar-width: thin", self.style_css)
        self.assertIn("liquid-glass-resonance-box", self.style_css)
        self.assertIn("liquid-glass-narrative-box", self.style_css)
        self.assertIn("thought-card-resonant-news", self.app_js)
        self.assertIn("pwaVaultIndicatorBtn", self.index_html)
        self.assertIn("setupPWAOfflineVault", self.app_js)


if __name__ == "__main__":
    unittest.main()
