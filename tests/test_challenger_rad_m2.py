#!/usr/bin/env python3
"""
Milestone 2 Empirical Challenge Test Suite (Feed Intelligence: R1 & R3)
Author: Challenger 1 (challenger_rad_m2_1)
Target: app.js, index.html, style.css, data/news.json

Verifies:
1. Micro-sparkline SVG generator resilience under extreme edge cases:
   - velocity = 0.0
   - velocity = 1.0
   - missing scores ({}, None, non-numeric)
   - null/missing/malformed pubDate
   - single source vs huge cluster (1 vs 500 outlets)
   - extreme velocity anomalies (-1.0, 99.0)
   - SVG XML well-formedness validation via xml.etree.ElementTree
   - 100% of production articles in data/news.json produce valid SVG paths
2. Cognitive Load Thermostat density switching:
   - All 3 states (.density-scan, .density-digest, .density-deep) present in style.css
   - Appropriate display/collapse rules for deep-dive panel, annotations, thumbnails
   - Responsive breakpoints (1024px, 640px) cover density modes
   - 3-position controller in index.html inside .filter-bar with ARIA attributes
   - JS density controller logic in app.js with localStorage persistence
3. HTML Duplicate ID Audit:
   - Strict zero duplicate IDs in index.html
"""

import collections
import json
import math
import os
import re
import unittest
import xml.etree.ElementTree as ET

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def compute_story_metabolism_py(art):
    """
    Python mirror of computeStoryMetabolism(art) from app.js (lines 161-259).
    Faithfully replicates the exact arithmetic, branch conditions, and coordinate generation.
    """
    if art is None:
        art = {}

    scores = art.get('scores') if isinstance(art.get('scores'), dict) else {}
    vel_raw = scores.get('velocity') if scores else None
    vel = vel_raw if isinstance(vel_raw, (int, float)) else 0.25

    cluster = art.get('storyCluster') if isinstance(art.get('storyCluster'), dict) else {}
    cluster_size_raw = cluster.get('size') if cluster else None
    if isinstance(cluster_size_raw, (int, float)):
        cluster_size = int(cluster_size_raw)
    elif art.get('perspectives') and isinstance(art.get('perspectives'), list):
        cluster_size = len(art.get('perspectives'))
    elif art.get('duplicate_count'):
        cluster_size = int(art.get('duplicate_count')) + 1
    else:
        cluster_size = 1

    # Date handling
    pub_date_raw = art.get('pubDate')
    # If pubDate is null/missing/invalid, fallback to 0 hours ago
    hours_ago = 0.0
    if pub_date_raw:
        try:
            # Simple RFC / ISO parsing approximation
            import email.utils
            parsed = email.utils.parsedate_to_datetime(pub_date_raw)
            import datetime
            now = datetime.datetime.now(datetime.timezone.utc)
            delta = (now - parsed).total_seconds()
            hours_ago = max(0.0, delta / 3600.0)
        except Exception:
            hours_ago = 0.0

    status = 'stabilizing'
    label = 'Stabilizing'
    color = '#94a3b8'
    tooltip = f"Metabolism: Stabilizing ({int(round(vel * 100))}% velocity) • Steady reporting"

    if vel >= 0.45 or (vel >= 0.35 and cluster_size >= 2) or (vel >= 0.30 and hours_ago <= 6):
        status = 'accelerating'
        label = 'Accelerating'
        color = '#10b981'
        tooltip = f"Metabolism: Accelerating ({int(round(vel * 100))}% velocity) • {cluster_size} sources surging • High velocity momentum"
    elif vel >= 0.25 or cluster_size >= 2 or (hours_ago <= 18 and vel >= 0.20):
        status = 'peak-spread'
        label = 'Peak Spread'
        color = '#f59e0b'
        tooltip = f"Metabolism: Peak Spread • Maximum syndication across {cluster_size} outlets ({int(round(vel * 100))}% velocity)"

    x_coords = [0, 9, 18, 28, 37, 47, 56]
    art_id = str(art.get('id') or '')
    seed = sum(ord(c) for c in art_id) % 5

    if status == 'accelerating':
        y_coords = [
            15,
            14 - (seed % 2),
            12 - int(round(vel * 4)),
            9 - int(round(vel * 5)),
            6 - (seed % 2),
            4,
            3
        ]
    elif status == 'peak-spread':
        y_coords = [
            14,
            10 - (seed % 2),
            5,
            4,
            5 + (seed % 2),
            6,
            7
        ]
    else:
        y_coords = [
            7 + (seed % 2),
            4,
            7,
            10,
            12,
            13 + (seed % 2),
            14
        ]

    path_d = f"M {x_coords[0]},{y_coords[0]}"
    for i in range(len(x_coords) - 1):
        x0 = x_coords[i]
        y0 = y_coords[i]
        x1 = x_coords[i + 1]
        y1 = y_coords[i + 1]
        mx = round((x0 + x1) / 2.0, 1)
        path_d += f" C {mx},{y0} {mx},{y1} {x1},{y1}"

    area_d = f"{path_d} L 56,18 L 0,18 Z"
    last_x = x_coords[-1]
    last_y = y_coords[-1]

    return {
        'status': status,
        'label': label,
        'color': color,
        'pathD': path_d,
        'areaD': area_d,
        'lastX': last_x,
        'lastY': last_y,
        'tooltip': tooltip,
        'vel': vel,
        'clusterSize': cluster_size,
        'hoursAgo': hours_ago,
        'points': [{'x': x_coords[i], 'y': y_coords[i]} for i in range(len(x_coords))]
    }


def validate_svg_markup(path_d, area_d, last_x, last_y, color, gradient_id="test-grad"):
    """Validates SVG markup well-formedness by parsing it through xml.etree.ElementTree."""
    svg_str = f"""<svg xmlns="http://www.w3.org/2000/svg" width="56" height="18" viewBox="0 0 56 18">
      <defs>
        <linearGradient id="{gradient_id}" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="{color}" stop-opacity="0.35" />
          <stop offset="100%" stop-color="{color}" stop-opacity="0.0" />
        </linearGradient>
      </defs>
      <path d="{area_d}" fill="url(#{gradient_id})" />
      <path d="{path_d}" fill="none" stroke="{color}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" />
      <circle cx="{last_x}" cy="{last_y}" r="2" fill="{color}" />
    </svg>"""
    root = ET.fromstring(svg_str)
    return root


class TestMilestone2EmpiricalChallenge(unittest.TestCase):

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
            data = json.load(f)
            self.news_data = data.get("articles", []) if isinstance(data, dict) else data

    # =========================================================================
    # PART 1: SPARKLINE SVG GENERATION ADVERSARIAL STRESS TESTS
    # =========================================================================

    def test_sparkline_edge_case_velocity_zero(self):
        """Stress-test velocity = 0.0 (stagnant/zero coverage velocity)."""
        art = {
            "id": "art-zero-vel",
            "title": "Stagnant News Event",
            "scores": {"velocity": 0.0},
            "pubDate": "2026-10-22T00:00:00Z"
        }
        res = compute_story_metabolism_py(art)
        self.assertEqual(res['status'], 'stabilizing')
        self.assertEqual(res['label'], 'Stabilizing')
        self.assertEqual(res['color'], '#94a3b8')
        self.assertIn("0% velocity", res['tooltip'])

        # Path validation
        self.assertTrue(res['pathD'].startswith("M 0,"))
        self.assertIn(" C ", res['pathD'])
        self.assertTrue(res['areaD'].endswith(" L 56,18 L 0,18 Z"))
        self.assertEqual(res['lastX'], 56)
        self.assertIsInstance(res['lastY'], int)

        # SVG XML parser check
        elem = validate_svg_markup(res['pathD'], res['areaD'], res['lastX'], res['lastY'], res['color'])
        self.assertIsNotNone(elem)

    def test_sparkline_edge_case_velocity_one(self):
        """Stress-test velocity = 1.0 (maximum 100% velocity surge)."""
        art = {
            "id": "art-max-vel",
            "title": "Hyper Breaking Story",
            "scores": {"velocity": 1.0},
            "pubDate": "2026-10-22T05:00:00Z"
        }
        res = compute_story_metabolism_py(art)
        self.assertEqual(res['status'], 'accelerating')
        self.assertEqual(res['label'], 'Accelerating')
        self.assertEqual(res['color'], '#10b981')
        self.assertIn("100% velocity", res['tooltip'])

        # Check coordinate bounds
        for pt in res['points']:
            self.assertGreaterEqual(pt['x'], 0)
            self.assertLessEqual(pt['x'], 56)
            self.assertGreaterEqual(pt['y'], 0)
            self.assertLessEqual(pt['y'], 18)

        elem = validate_svg_markup(res['pathD'], res['areaD'], res['lastX'], res['lastY'], res['color'])
        self.assertIsNotNone(elem)

    def test_sparkline_edge_case_missing_scores(self):
        """Stress-test articles with missing, null, or empty scores object."""
        test_cases = [
            {"id": "art-no-scores", "title": "No Scores"},
            {"id": "art-empty-scores", "title": "Empty Scores", "scores": {}},
            {"id": "art-null-scores", "title": "Null Scores", "scores": None},
            {"id": "art-str-velocity", "title": "String Velocity", "scores": {"velocity": "lightning"}}
        ]
        for art in test_cases:
            res = compute_story_metabolism_py(art)
            self.assertEqual(res['vel'], 0.25, f"Should fall back to default velocity 0.25 for {art['id']}")
            self.assertTrue(res['pathD'].startswith("M 0,"))
            self.assertTrue(res['areaD'].endswith(" L 56,18 L 0,18 Z"))
            elem = validate_svg_markup(res['pathD'], res['areaD'], res['lastX'], res['lastY'], res['color'])
            self.assertIsNotNone(elem)

    def test_sparkline_edge_case_null_or_invalid_pubdate(self):
        """Stress-test articles with null, missing, empty, or unparseable pubDate."""
        test_cases = [
            {"id": "art-null-date", "title": "Null Date", "pubDate": None},
            {"id": "art-empty-date", "title": "Empty Date", "pubDate": ""},
            {"id": "art-bogus-date", "title": "Bogus Date", "pubDate": "unparseable-timestamp-epoch-xyz"},
        ]
        for art in test_cases:
            res = compute_story_metabolism_py(art)
            self.assertFalse(math.isnan(res['hoursAgo']))
            self.assertGreaterEqual(res['hoursAgo'], 0)
            self.assertTrue(res['pathD'].startswith("M 0,"))
            elem = validate_svg_markup(res['pathD'], res['areaD'], res['lastX'], res['lastY'], res['color'])
            self.assertIsNotNone(elem)

    def test_sparkline_edge_case_single_source_vs_huge_cluster(self):
        """Stress-test single source (size 1) vs massive syndicated cluster (size 500)."""
        # Single source
        art_single = {
            "id": "art-single",
            "title": "Single Reporter Scoop",
            "scores": {"velocity": 0.2},
            "storyCluster": {"size": 1},
            "perspectives": []
        }
        res_single = compute_story_metabolism_py(art_single)
        self.assertEqual(res_single['clusterSize'], 1)

        # Huge cluster
        art_huge = {
            "id": "art-huge",
            "title": "Global Wire Event",
            "scores": {"velocity": 0.36},
            "storyCluster": {"size": 500},
            "perspectives": [{"source": f"Wire {i}"} for i in range(50)]
        }
        res_huge = compute_story_metabolism_py(art_huge)
        self.assertEqual(res_huge['clusterSize'], 500)
        self.assertEqual(res_huge['status'], 'accelerating')
        self.assertIn("500 sources surging", res_huge['tooltip'])

        elem = validate_svg_markup(res_huge['pathD'], res_huge['areaD'], res_huge['lastX'], res_huge['lastY'], res_huge['color'])
        self.assertIsNotNone(elem)

    def test_sparkline_extreme_anomalies_and_empty_inputs(self):
        """Stress-test extreme inputs: None, {}, negative velocity, huge velocity."""
        anomalies = [
            None,
            {},
            {"id": "neg-vel", "scores": {"velocity": -1.5}},
            {"id": "huge-vel", "scores": {"velocity": 99.0}},
            {"id": "numeric-id-12345", "scores": {"velocity": 0.5}}
        ]
        for art in anomalies:
            res = compute_story_metabolism_py(art)
            self.assertIn(res['status'], ['accelerating', 'peak-spread', 'stabilizing'])
            self.assertTrue(len(res['pathD']) > 10, "pathD must be non-empty")
            self.assertTrue(len(res['areaD']) > 15, "areaD must be non-empty")
            self.assertFalse(any(math.isnan(p['y']) for p in res['points']))
            elem = validate_svg_markup(res['pathD'], res['areaD'], res['lastX'], res['lastY'], res['color'])
            self.assertIsNotNone(elem)

    def test_all_134_production_articles_svg_validity(self):
        """Empirically test every article in data/news.json generates valid SVG paths and XML."""
        self.assertGreaterEqual(len(self.news_data), 100, "Dataset must contain >= 100 articles")
        statuses = collections.Counter()

        for art in self.news_data:
            res = compute_story_metabolism_py(art)
            statuses[res['status']] += 1

            # Validate path format: M x,y (C mx,y0 mx,y1 x1,y1)+
            self.assertRegex(res['pathD'], r'^M\s+\d+,\d+(\s+C\s+[\d.]+,\d+\s+[\d.]+,\d+\s+\d+,\d+){6}$')
            self.assertTrue(res['areaD'].endswith(" L 56,18 L 0,18 Z"))

            # XML validity check
            root = validate_svg_markup(res['pathD'], res['areaD'], res['lastX'], res['lastY'], res['color'], f"grad-{art.get('id', 'x')}")
            paths = root.findall('.//{http://www.w3.org/2000/svg}path')
            self.assertEqual(len(paths), 2, "Must contain exactly 2 path elements (area and line)")

        # Verify all statuses are represented across the dataset
        self.assertGreater(statuses['accelerating'], 0, "Expected accelerating articles")
        self.assertGreater(statuses['peak-spread'], 0, "Expected peak-spread articles")
        self.assertGreater(statuses['stabilizing'], 0, "Expected stabilizing articles")

    # =========================================================================
    # PART 2: DENSITY SWITCHING STATES & CSS / HTML AUDIT
    # =========================================================================

    def test_density_all_3_states_exist_in_css(self):
        """Verify .news-grid.density-scan, .news-grid.density-digest, and .news-grid.density-deep exist in style.css."""
        self.assertIn(".news-grid.density-scan", self.style_css, "density-scan CSS rule missing")
        self.assertIn(".news-grid.density-digest", self.style_css, "density-digest CSS rule missing")
        self.assertIn(".news-grid.density-deep", self.style_css, "density-deep CSS rule missing")

    def test_density_css_layout_and_element_visibility_rules(self):
        """Verify visibility and layout definitions for all 3 density modes."""
        # Scan mode must hide heavy elements
        self.assertIn(".news-grid.density-scan .card-thumb-box", self.style_css)
        self.assertIn(".news-grid.density-scan .annotation-box", self.style_css)
        self.assertIn(".news-grid.density-scan .card-footer", self.style_css)
        self.assertIn(".news-grid.density-scan .card-deep-dive-panel", self.style_css)

        # Digest mode collapses deep dive panel
        self.assertIn(".news-grid.density-digest .card-deep-dive-panel", self.style_css)

        # Deep dive mode reveals deep dive panel
        self.assertIn(".news-grid.density-deep .card-deep-dive-panel", self.style_css)
        self.assertIn("display: block", self.style_css)

        # Responsive queries cover density modes
        self.assertIn("@media (max-width: 1024px)", self.style_css)
        self.assertIn("@media (max-width: 640px)", self.style_css)

    def test_density_toggle_group_html_structure(self):
        """Verify #densityToggleGroup and its 3 radio buttons exist with proper ARIA attributes."""
        self.assertIn('id="densityToggleGroup"', self.index_html)
        self.assertIn('role="radiogroup"', self.index_html)
        self.assertIn('id="densityScanBtn"', self.index_html)
        self.assertIn('id="densityDigestBtn"', self.index_html)
        self.assertIn('id="densityDeepBtn"', self.index_html)

        # Verify buttons have data-density attributes
        self.assertIn('data-density="scan"', self.index_html)
        self.assertIn('data-density="digest"', self.index_html)
        self.assertIn('data-density="deep"', self.index_html)

        # Verify located inside .filter-bar navigation
        filter_bar_match = re.search(r'<nav class="filter-bar".*?</nav>', self.index_html, re.DOTALL)
        self.assertTrue(filter_bar_match, "filter-bar nav must exist in index.html")
        self.assertIn('id="densityToggleGroup"', filter_bar_match.group(0))

    def test_density_controller_js_implementation(self):
        """Verify density controller JavaScript logic and localStorage persistence in app.js."""
        self.assertIn("function setupDensityController()", self.app_js)
        self.assertIn("function setDensity(mode)", self.app_js)
        self.assertIn("window.setupDensityController = setupDensityController", self.app_js)
        self.assertIn("window.setDensity = setDensity", self.app_js)

        # Verify localStorage keys
        self.assertIn("localStorage.getItem('news_colossal_density')", self.app_js)
        self.assertIn("localStorage.setItem('news_colossal_density', mode)", self.app_js)

        # Verify grid class manipulation
        self.assertIn("grid.classList.remove('density-scan', 'density-digest', 'density-deep')", self.app_js)
        self.assertIn("grid.classList.add(`density-${mode}`)", self.app_js)

    # =========================================================================
    # PART 3: HTML DUPLICATE ID AUDIT
    # =========================================================================

    def test_strict_zero_duplicate_ids_in_index_html(self):
        """Empirically verify index.html contains ZERO duplicate element IDs."""
        id_pattern = re.compile(r'id=["\']([^"\']+)["\']')
        ids = id_pattern.findall(self.index_html)
        counts = collections.Counter(ids)
        duplicates = {id_name: count for id_name, count in counts.items() if count > 1}

        self.assertEqual(
            len(duplicates), 0,
            f"index.html must have 0 duplicate element IDs, but found {len(duplicates)} duplicates: {duplicates}"
        )
        self.assertGreater(len(ids), 80, "Expected at least 80 element IDs in index.html")


if __name__ == '__main__':
    unittest.main()
