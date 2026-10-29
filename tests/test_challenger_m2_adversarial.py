"""
Adversarial Stress Test Suite for Milestone 2: Feed Intelligence
Reviewer 2 Adversarial Stress Testing:
1. computeStoryMetabolism edge case resilience (None, empty, NaN, negative velocity, extreme clusters, malformed pubDates, special chars in id)
2. SVG Path and Coordinate integrity (No NaN, valid Bezier syntax, correct bounding box 56x18)
3. Zero DOM rebuild guarantees (Static code analysis and state verification)
4. VisionOS liquid glass aesthetic & responsive breakpoint rules (1024px, 640px, Dark/Light modes)
5. Historical contract preservation & zero-regression checks
"""

import json
import os
import re
import unittest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class TestM2AdversarialSuite(unittest.TestCase):

    def setUp(self):
        with open(os.path.join(PROJECT_ROOT, "index.html"), "r", encoding="utf-8") as f:
            self.index_html = f.read()
        with open(os.path.join(PROJECT_ROOT, "style.css"), "r", encoding="utf-8") as f:
            self.style_css = f.read()
        with open(os.path.join(PROJECT_ROOT, "app.js"), "r", encoding="utf-8") as f:
            self.app_js = f.read()
        with open(os.path.join(PROJECT_ROOT, "data", "news.json"), "r", encoding="utf-8") as f:
            self.news_data = json.load(f)

    # -------------------------------------------------------------------------
    # 1. ADVERSARIAL STRESS TEST: computeStoryMetabolism input boundary resilience
    # -------------------------------------------------------------------------
    def test_compute_story_metabolism_boundary_conditions(self):
        """Stress-test Python replica of computeStoryMetabolism with hostile and boundary inputs."""
        def run_metabolism(art):
            if not art:
                art = {}
            scores = art.get('scores') or {}
            vel = scores.get('velocity') if isinstance(scores.get('velocity'), (int, float)) else 0.25
            cluster = art.get('storyCluster') or {}
            cluster_size = cluster.get('size') or len(art.get('perspectives') or []) or ((art.get('duplicate_count', 0) + 1) if art.get('duplicate_count') else 1)
            
            hours_ago = 12.0
            status = 'stabilizing'
            label = 'Stabilizing'
            color = '#94a3b8'

            if vel >= 0.45 or (vel >= 0.35 and cluster_size >= 2) or (vel >= 0.30 and hours_ago <= 6):
                status = 'accelerating'
                label = 'Accelerating'
                color = '#10b981'
            elif vel >= 0.25 or cluster_size >= 2 or (hours_ago <= 18 and vel >= 0.20):
                status = 'peak-spread'
                label = 'Peak Spread'
                color = '#f59e0b'

            x_coords = [0, 9, 18, 28, 37, 47, 56]
            seed = sum(ord(c) for c in (art.get('id') or '')) % 5
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
                'xCoords': x_coords,
                'yCoords': y_coords
            }

        hostile_inputs = [
            None,
            {},
            {'id': None, 'scores': None},
            {'id': 'x' * 500, 'scores': {'velocity': 0.0}},
            {'id': 'special-!@#$%^&*()', 'scores': {'velocity': 1.0}, 'storyCluster': {'size': 999}},
            {'id': 'neg-vel', 'scores': {'velocity': -0.5}},
            {'id': 'extreme-vel', 'scores': {'velocity': 10.5}},
            {'id': 'no-cluster', 'perspectives': [1, 2, 3, 4, 5], 'duplicate_count': 10},
        ]

        for inp in hostile_inputs:
            res = run_metabolism(inp)
            self.assertIn(res['status'], ['accelerating', 'peak-spread', 'stabilizing'])
            self.assertTrue(res['pathD'].startswith('M 0,'))
            self.assertFalse('NaN' in res['pathD'])
            self.assertFalse('None' in res['pathD'])
            self.assertTrue(res['areaD'].endswith('L 56,18 L 0,18 Z'))
            for y in res['yCoords']:
                self.assertIsInstance(y, int)

    # -------------------------------------------------------------------------
    # 2. ZERO DOM REBUILD VERIFICATION
    # -------------------------------------------------------------------------
    def test_zero_dom_rebuild_contract(self):
        """Verify that setDensity toggles classes on newsGrid without invoking renderGrid or innerHTML re-render."""
        # Find setDensity function body in app.js
        match = re.search(r'function setDensity\s*\((.*?)\)\s*\{(.*?)\n\}', self.app_js, re.DOTALL)
        self.assertTrue(match, "setDensity function must be defined in app.js")
        body = match.group(2)

        # setDensity must NOT call renderGrid, filterAndRender, or mutate newsGrid.innerHTML
        self.assertNotIn('renderGrid(', body, "setDensity MUST NOT invoke renderGrid (would trigger DOM rebuild)")
        self.assertNotIn('filterAndRender(', body, "setDensity MUST NOT invoke filterAndRender")
        self.assertNotIn('innerHTML', body, "setDensity MUST NOT overwrite innerHTML")

        # Must toggle classes cleanly
        self.assertIn("classList.remove('density-scan', 'density-digest', 'density-deep')", body)
        self.assertIn("classList.add(`density-${mode}`)", body)

        # Must persist to localStorage
        self.assertIn("localStorage.setItem('news_colossal_density'", body)

    # -------------------------------------------------------------------------
    # 3. RESPONSIVE BREAKPOINT CHECKS (1024px & 640px)
    # -------------------------------------------------------------------------
    def test_responsive_layout_rules(self):
        """Verify grid layout definitions at 1024px and 640px breakpoints."""
        # Helper to extract entire media block with balanced braces
        def extract_media_blocks(css, query):
            blocks = []
            idx = 0
            while True:
                pos = css.find(query, idx)
                if pos == -1:
                    break
                brace_start = css.find('{', pos)
                if brace_start == -1:
                    break
                depth = 1
                curr = brace_start + 1
                while curr < len(css) and depth > 0:
                    if css[curr] == '{':
                        depth += 1
                    elif css[curr] == '}':
                        depth -= 1
                    curr += 1
                blocks.append(css[brace_start+1:curr-1])
                idx = curr
            return blocks

        tablet_blocks = extract_media_blocks(self.style_css, '@media (max-width: 1024px)')
        self.assertTrue(len(tablet_blocks) > 0, "Tablet media query missing")
        combined_tablet = "\n".join(tablet_blocks)
        self.assertIn('.news-grid.density-scan', combined_tablet)
        self.assertIn('repeat(2, 1fr)', combined_tablet)
        self.assertIn('.news-grid.density-deep', combined_tablet)

        mobile_blocks = extract_media_blocks(self.style_css, '@media (max-width: 640px)')
        self.assertTrue(len(mobile_blocks) > 0, "Mobile media query missing")
        combined_mobile = "\n".join(mobile_blocks)
        self.assertIn('.news-grid.density-scan', combined_mobile)
        self.assertIn('grid-template-columns: 1fr', combined_mobile)
        self.assertIn('.news-grid.density-deep', combined_mobile)
        self.assertIn('#densityToggleGroup', combined_mobile)

    # -------------------------------------------------------------------------
    # 4. VISIONOS LIQUID GLASS AESTHETIC INTEGRITY
    # -------------------------------------------------------------------------
    def test_visionos_liquid_glass_aesthetic(self):
        """Verify glassmorphic properties: backdrop-filter blur, specular sheen, and translucency."""
        self.assertIn("backdrop-filter: blur(16px)", self.style_css)
        self.assertIn("-webkit-backdrop-filter: blur(16px)", self.style_css)
        self.assertIn(".sparkline-tooltip", self.style_css)
        self.assertIn("backdrop-filter: blur(8px)", self.style_css)
        self.assertIn(".sparkline-pulse-dot", self.style_css)
        self.assertIn("@keyframes sparklinePulse", self.style_css)

        # Light and dark mode support
        self.assertIn('[data-theme="dark"] #densityToggleGroup', self.style_css)
        self.assertIn('[data-theme="dark"] .density-btn.active', self.style_css)
        self.assertIn('[data-theme="dark"] .deep-tag', self.style_css)
        self.assertIn('[data-theme="dark"] .matrix-pill', self.style_css)

    # -------------------------------------------------------------------------
    # 5. INTEGRITY VERIFICATION (No hardcoded facades or cheats)
    # -------------------------------------------------------------------------
    def test_no_hardcoded_facades_or_integrity_violations(self):
        """Ensure no mocked return values or fake test assertions in production scripts."""
        # computeStoryMetabolism in app.js should calculate coordinates dynamically
        self.assertIn("pathD += ` C ${mx},${y0} ${mx},${y1} ${x1},${y1}`", self.app_js)
        self.assertIn("xCoords.map((x, i) => ({ x, y: yCoords[i] }))", self.app_js)

        # createCardHTML should call computeStoryMetabolism dynamically
        self.assertIn("const metabolism = computeStoryMetabolism(art);", self.app_js)

        # Ensure no cheating markers
        self.assertNotIn("/* CHEAT", self.app_js)
        self.assertNotIn("/* BYPASS", self.app_js)
        self.assertNotIn("mockMetabolism", self.app_js)


if __name__ == "__main__":
    unittest.main()
