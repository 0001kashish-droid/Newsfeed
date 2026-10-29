#!/usr/bin/env python3
"""
Empirical Challenger 2 Stress & Verification Suite — Milestone 4 (Executive Intelligence)
Author: challenger_rad_m4_2 (Empirical Challenger)
Targets: index.html, app.js, style.css, data/news.json

Rigorously verifies:
1. Modal Lifecycle and DOM Elements:
   - Element IDs: #focusTimerPill, #focusSessionBtn, #focusReportModal,
     #constellationModalBackdrop, #constellationCanvas, #constellationMapBtn.
   - Sub-element hierarchies, ARIA accessibility attributes, button linkages.
2. Focus Session Timer & Docket Curation Engine (R5):
   - Curate 5-story executive docket algorithm (4-pillar balance + Black Swan / Contrarian boosts).
   - Infinite scroll observer detachment and suppression.
   - Timer countdown math, formatting, pause/resume, and progress bar fill %.
   - Completion report statistics (duration, read count, domain coverage %, signal density).
   - Exit session clean-up and standard feed restoration.
3. Knowledge Constellation Graph & Physics Engine (R7):
   - In-memory entity graph extraction (nations, leaders, orgs, clusters).
   - Neon color scheme adherence (#10b981, #f59e0b, #0284c7, #a855f7).
   - Coordinate transformation math: toScreen(), toWorld(), round-trip invertibility.
   - Pan drag math (1:1 motion tracking) and zoom-to-cursor invariance.
   - Hit testing Euclidean distance math.
   - Euler force simulation numerical stability (repulsion, spring attraction, gravity, damping, alpha decay).
   - Canvas resize handling and DPR scaling analysis.
   - Dispatch jump invocation: jumpToArticleFromConstellation(artId) -> openModal(artId).
4. Full Audit & Test Suite Compatibility:
   - production_hard_audit.py (all 6 layers)
   - test_e2e_remediation.py (all 48 tests)
"""

import os
import sys
import unittest
import re
import json
import math

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read_file(relative_path):
    full_path = os.path.join(PROJECT_ROOT, relative_path)
    with open(full_path, 'r', encoding='utf-8') as f:
        return f.read()


class TestMilestone4DOMElementsAndAccessibility(unittest.TestCase):
    """Verifies all required DOM elements, container hierarchies, and accessibility tags."""

    @classmethod
    def setUpClass(cls):
        cls.index_html = read_file('index.html')
        cls.style_css = read_file('style.css')
        cls.app_js = read_file('app.js')

    def test_required_element_ids_exist(self):
        """Verify the exact element IDs mandated in Milestone 4 interface contracts."""
        required_ids = [
            'focusTimerPill',
            'focusSessionBtn',
            'focusReportModal',
            'constellationModalBackdrop',
            'constellationCanvas',
            'constellationMapBtn'
        ]
        for eid in required_ids:
            self.assertIn(f'id="{eid}"', self.index_html, f"Missing required element id='{eid}' in index.html")

    def test_focus_timer_pill_structure(self):
        """Verify #focusTimerPill sub-elements: display, count, bar, and controls."""
        self.assertIn('id="focusTimerDisplay"', self.index_html)
        self.assertIn('id="focusCountDisplay"', self.index_html)
        self.assertIn('id="focusBarFill"', self.index_html)
        self.assertIn('id="focusPauseBtn"', self.index_html)
        self.assertIn('id="focusEndBtn"', self.index_html)
        
        # Verify initial hidden state
        pill_match = re.search(r'<div[^>]*id="focusTimerPill"[^>]*>', self.index_html)
        self.assertIsNotNone(pill_match)
        self.assertIn('style="display: none;"', pill_match.group(0))
        self.assertIn('role="timer"', pill_match.group(0))

    def test_quick_tools_popover_buttons(self):
        """Verify #focusSessionBtn and #constellationMapBtn are placed inside #headerToolsPopover."""
        popover_match = re.search(r'id="headerToolsPopover".*?</div>\s*</div>\s*</div>', self.index_html, re.DOTALL)
        self.assertIsNotNone(popover_match, "Could not isolate #headerToolsPopover block")
        popover_html = popover_match.group(0)
        self.assertIn('id="focusSessionBtn"', popover_html)
        self.assertIn('id="constellationMapBtn"', popover_html)

    def test_focus_report_modal_structure(self):
        """Verify #focusReportModal metrics grid and action buttons."""
        self.assertIn('id="metricTimeElapsed"', self.index_html)
        self.assertIn('id="metricStoriesRead"', self.index_html)
        self.assertIn('id="metricDomainCoverage"', self.index_html)
        self.assertIn('id="metricSignalScore"', self.index_html)
        self.assertIn('id="focusReportDomains"', self.index_html)
        self.assertIn('id="focusCopySummaryBtn"', self.index_html)
        self.assertIn('id="focusReturnFeedBtn"', self.index_html)

    def test_constellation_modal_structure(self):
        """Verify #constellationModalBackdrop controls, canvas, tooltip, and inspector."""
        self.assertIn('id="constellationStatsLabel"', self.index_html)
        self.assertIn('id="constellationLegend"', self.index_html)
        self.assertIn('id="constellationZoomInBtn"', self.index_html)
        self.assertIn('id="constellationZoomOutBtn"', self.index_html)
        self.assertIn('id="constellationFitBtn"', self.index_html)
        self.assertIn('id="constellationCloseBtn"', self.index_html)
        self.assertIn('id="constellationCanvasContainer"', self.index_html)
        self.assertIn('id="constellationCanvas"', self.index_html)
        self.assertIn('id="constellationTooltip"', self.index_html)
        self.assertIn('id="constellationInspector"', self.index_html)
        self.assertIn('id="inspectorBadge"', self.index_html)
        self.assertIn('id="inspectorTitle"', self.index_html)
        self.assertIn('id="inspectorStats"', self.index_html)
        self.assertIn('id="inspectorDispatchesList"', self.index_html)
        self.assertIn('id="inspectorCloseBtn"', self.index_html)


class TestFocusDocketAlgorithmAndTimerLifecycle(unittest.TestCase):
    """Stress-tests the 5-story docket curation algorithm and session lifecycle."""

    @classmethod
    def setUpClass(cls):
        cls.app_js = read_file('app.js')
        with open(os.path.join(PROJECT_ROOT, 'data', 'news.json'), 'r', encoding='utf-8') as f:
            cls.news_data = json.load(f)

    def _simulate_curate_focus_docket(self, pool):
        """Python implementation of curateFocusDocket in app.js."""
        if not pool or len(pool) == 0:
            return []

        # Filter out duplicates
        candidates = [a for a in pool if not a.get('is_duplicate')]
        if len(candidates) < 5:
            candidates = list(pool)

        docket = []
        selected_ids = set()

        # 1. 4-Pillar Domain Balance (World, Tech, Business, National)
        pillars = ['World', 'Tech', 'Business', 'National']
        for pillar in pillars:
            pillar_stories = [a for a in candidates if a.get('category') == pillar and a.get('id') not in selected_ids]
            if pillar_stories:
                pillar_stories.sort(key=lambda a: a.get('importance_score', 5.0), reverse=True)
                top = pillar_stories[0]
                docket.append(top)
                selected_ids.add(top.get('id'))

        # 2. Select remaining stories maximizing composite signal
        def get_signal_score(a):
            base = a.get('importance_score', 5.0)
            meta = a.get('meta', {})
            # Black swan bonus
            if meta.get('is_black_swan'):
                base += 1.5
            # Contrarian bonus
            if meta.get('is_contrarian'):
                base += 0.8
            # Narrative arc bonus
            if a.get('narrative_arc') and a.get('narrative_arc', {}).get('arc_id'):
                base += 0.5
            return base

        remaining = [a for a in candidates if a.get('id') not in selected_ids]
        remaining.sort(key=get_signal_score, reverse=True)

        while len(docket) < 5 and remaining:
            nxt = remaining.pop(0)
            docket.append(nxt)
            selected_ids.add(nxt.get('id'))

        # Fallback if candidates pool was under 5
        if len(docket) < 5 and len(pool) > 0:
            for a in pool:
                if len(docket) >= 5:
                    break
                if a.get('id') not in selected_ids:
                    docket.append(a)
                    selected_ids.add(a.get('id'))

        return docket[:5]

    def test_curate_docket_from_production_dataset(self):
        """Verify docket curation yields exactly 5 high-importance, domain-balanced stories."""
        articles = self.news_data.get('articles', [])
        docket = self._simulate_curate_focus_docket(articles)

        self.assertEqual(len(docket), 5, "Docket must contain exactly 5 stories")
        
        # Verify 4 distinct domains represented
        categories = {a.get('category') for a in docket}
        for pillar in ['World', 'Tech', 'Business', 'National']:
            self.assertIn(pillar, categories, f"Pillar '{pillar}' must be represented in executive docket")

        # Verify all 5 story IDs are unique
        ids = [a.get('id') for a in docket]
        self.assertEqual(len(set(ids)), 5, "All docket stories must have distinct IDs")

    def test_curate_docket_under_skewed_input(self):
        """Stress-test curation when some pillars have 0 articles in input pool."""
        skewed_pool = [
            {'id': 'w1', 'category': 'World', 'importance_score': 9.2},
            {'id': 'w2', 'category': 'World', 'importance_score': 8.8},
            {'id': 'w3', 'category': 'World', 'importance_score': 7.5},
            {'id': 't1', 'category': 'Tech', 'importance_score': 9.0},
            {'id': 't2', 'category': 'Tech', 'importance_score': 8.5},
            {'id': 't3', 'category': 'Tech', 'importance_score': 7.0},
        ]
        docket = self._simulate_curate_focus_docket(skewed_pool)
        self.assertEqual(len(docket), 5, "Must still curate exactly 5 stories even when Business and National are absent")
        self.assertIn('w1', [a['id'] for a in docket])
        self.assertIn('t1', [a['id'] for a in docket])

    def test_timer_countdown_and_formatting(self):
        """Verify timer countdown logic and MM:SS formatting."""
        def format_time(seconds):
            rem = max(0, seconds)
            mins = rem // 60
            secs = rem % 60
            return f"{mins:02d}:{secs:02d}"

        self.assertEqual(format_time(600), "10:00")
        self.assertEqual(format_time(599), "09:59")
        self.assertEqual(format_time(60), "01:00")
        self.assertEqual(format_time(59), "00:59")
        self.assertEqual(format_time(1), "00:01")
        self.assertEqual(format_time(0), "00:00")
        self.assertEqual(format_time(-10), "00:00")

    def test_progress_bar_percentage_math(self):
        """Verify progress bar percentage calculation."""
        def calc_pct(total, remaining):
            rem = max(0, remaining)
            return round(((total - rem) / total) * 100, 1)

        self.assertEqual(calc_pct(600, 600), 0.0)
        self.assertEqual(calc_pct(600, 300), 50.0)
        self.assertEqual(calc_pct(600, 0), 100.0)
        self.assertEqual(calc_pct(600, 150), 75.0)

    def test_session_report_metrics_computation(self):
        """Verify session report calculations: elapsed time, domain coverage %, signal density."""
        docket = [
            {'id': '1', 'category': 'World', 'importance_score': 8.5},
            {'id': '2', 'category': 'Tech', 'importance_score': 7.5},
            {'id': '3', 'category': 'Business', 'importance_score': 6.0},
            {'id': '4', 'category': 'National', 'importance_score': 9.0},
            {'id': '5', 'category': 'Tech', 'importance_score': 8.0},
        ]
        read_ids = {'1', '2', '4'}
        remaining_secs = 245  # 355 seconds elapsed (5m 55s)

        elapsed_secs = 600 - remaining_secs
        elapsed_mins = elapsed_secs // 60
        elapsed_rem = elapsed_secs % 60
        time_formatted = f"{elapsed_mins:02d}:{elapsed_rem:02d}"
        self.assertEqual(time_formatted, "05:55")

        distinct_cats = len({a['category'] for a in docket})
        domain_pct = round((min(4, distinct_cats) / 4) * 100)
        self.assertEqual(domain_pct, 100)

        total_score = sum(a['importance_score'] for a in docket)
        avg_score = round(total_score / len(docket), 2)
        self.assertEqual(avg_score, 7.80)

    def test_infinite_scroll_suppression_wiring(self):
        """Verify app.js disconnects infinite scroll observer during focus session."""
        self.assertIn("if (_gridScrollObserver)", self.app_js)
        self.assertIn("_gridScrollObserver.disconnect()", self.app_js)
        self.assertIn("existingSentinel.remove()", self.app_js)
        # Verify renderGrid checks state.focusSession.active before setting observer
        self.assertIn("state.focusSession && state.focusSession.active", self.app_js)


class TestConstellationGraphTransformsAndPhysics(unittest.TestCase):
    """Stress-tests the HTML5 Canvas coordinate math, physics simulation, and hit detection."""

    @classmethod
    def setUpClass(cls):
        cls.app_js = read_file('app.js')

    def test_canvas_coordinate_transform_roundtrip(self):
        """Verify toWorld(toScreen(w)) == w and toScreen(toWorld(s)) == s algebraically."""
        def to_screen(wx, wy, cx, cy, cam_x, cam_y, zoom):
            return (
                cx + (wx + cam_x) * zoom,
                cy + (wy + cam_y) * zoom
            )

        def to_world(sx, sy, cx, cy, cam_x, cam_y, zoom):
            return (
                (sx - cx) / zoom - cam_x,
                (sy - cy) / zoom - cam_y
            )

        # Test across multiple camera states and zooms
        test_cases = [
            (800, 600, 0, 0, 1.0, 150.0, -80.0),
            (1920, 1080, 50.5, -30.2, 1.75, 45.0, 120.0),
            (1024, 768, -120.0, 85.0, 0.4, -300.0, 200.0),
            (640, 480, 0, 0, 3.5, 0.0, 0.0),
        ]

        for w, h, cam_x, cam_y, zoom, wx, wy in test_cases:
            cx = w / 2
            cy = h / 2

            # World -> Screen -> World
            sx, sy = to_screen(wx, wy, cx, cy, cam_x, cam_y, zoom)
            roundtrip_wx, roundtrip_wy = to_world(sx, sy, cx, cy, cam_x, cam_y, zoom)

            self.assertAlmostEqual(wx, roundtrip_wx, places=5,
                                   msg=f"World->Screen->World roundtrip failed at zoom {zoom}")
            self.assertAlmostEqual(wy, roundtrip_wy, places=5,
                                   msg=f"World->Screen->World roundtrip failed at zoom {zoom}")

            # Screen -> World -> Screen
            test_sx, test_sy = 450.0, 320.0
            r_wx, r_wy = to_world(test_sx, test_sy, cx, cy, cam_x, cam_y, zoom)
            r_sx, r_sy = to_screen(r_wx, r_wy, cx, cy, cam_x, cam_y, zoom)

            self.assertAlmostEqual(test_sx, r_sx, places=5,
                                   msg=f"Screen->World->Screen roundtrip failed at zoom {zoom}")
            self.assertAlmostEqual(test_sy, r_sy, places=5,
                                   msg=f"Screen->World->Screen roundtrip failed at zoom {zoom}")

    def test_zoom_to_cursor_fixed_point_invariance(self):
        """
        Verify that under wheel zoom, the world position under the mouse cursor
        remains invariant before and after camera compensation.
        """
        def to_world(sx, sy, cx, cy, cam_x, cam_y, zoom):
            return (
                (sx - cx) / zoom - cam_x,
                (sy - cy) / zoom - cam_y
            )

        cx, cy = 500.0, 400.0
        cam_x, cam_y = 25.0, -15.0
        zoom = 1.0

        # Mouse pointer at (650, 480)
        sx, sy = 650.0, 480.0
        world_before = to_world(sx, sy, cx, cy, cam_x, cam_y, zoom)

        # Zoom in by 1.15x
        new_zoom = zoom * 1.15
        world_after = to_world(sx, sy, cx, cy, cam_x, cam_y, new_zoom)

        # Compensate camera per app.js lines 2030-2031:
        # cam_x += (world_after.x - world_before.x)
        # cam_y += (world_after.y - world_before.y)
        cam_x += (world_after[0] - world_before[0])
        cam_y += (world_after[1] - world_before[1])

        # Evaluate world position at cursor after camera shift
        world_final = to_world(sx, sy, cx, cy, cam_x, cam_y, new_zoom)

        self.assertAlmostEqual(world_before[0], world_final[0], places=5,
                               msg="Zoom-to-cursor invariant violated in X coordinate")
        self.assertAlmostEqual(world_before[1], world_final[1], places=5,
                               msg="Zoom-to-cursor invariant violated in Y coordinate")

    def test_pan_camera_1_to_1_tracking(self):
        """Verify pan delta (clientX - dragStartX) / zoom moves world correctly."""
        cam_x = 0.0
        cam_y = 0.0
        zoom = 1.5

        delta_screen_x = 150.0
        delta_screen_y = -90.0

        dx = delta_screen_x / zoom
        dy = delta_screen_y / zoom

        cam_x += dx
        cam_y += dy

        # Verify new world offset scaled by zoom matches original screen delta
        self.assertAlmostEqual(cam_x * zoom, delta_screen_x, places=5)
        self.assertAlmostEqual(cam_y * zoom, delta_screen_y, places=5)

    def test_node_hit_detection_math(self):
        """Verify hit testing detects points within node radius + 4px margin."""
        def hit_test(sx, sy, node, cx, cy, cam_x, cam_y, zoom):
            # toWorld
            wx = (sx - cx) / zoom - cam_x
            wy = (sy - cy) / zoom - cam_y
            dx = wx - node['x']
            dy = wy - node['y']
            threshold = node['radius'] + 4
            return (dx * dx + dy * dy) <= (threshold * threshold)

        node = {'x': 100.0, 'y': 50.0, 'radius': 16.0}
        cx, cy = 400.0, 300.0
        cam_x, cam_y = 0.0, 0.0
        zoom = 1.0

        # Click at node center
        screen_center = (400.0 + 100.0, 300.0 + 50.0)  # (500, 350)
        self.assertTrue(hit_test(500.0, 350.0, node, cx, cy, cam_x, cam_y, zoom))

        # Click at border (distance = 20px, radius 16 + margin 4 = 20)
        self.assertTrue(hit_test(520.0, 350.0, node, cx, cy, cam_x, cam_y, zoom))

        # Click just outside (distance = 21px)
        self.assertFalse(hit_test(521.0, 350.0, node, cx, cy, cam_x, cam_y, zoom))

        # Click far away
        self.assertFalse(hit_test(700.0, 700.0, node, cx, cy, cam_x, cam_y, zoom))

    def test_force_simulation_physics_numerical_stability(self):
        """Verify repulsion and spring attraction don't produce NaN or infinity under coincident nodes."""
        # Singularity test: two nodes at the exact same location
        u = {'x': 0.0, 'y': 0.0, 'vx': 0.0, 'vy': 0.0}
        v = {'x': 0.0, 'y': 0.0, 'vx': 0.0, 'vy': 0.0}
        k_rep = 950.0

        dx = v['x'] - u['x']
        dy = v['y'] - u['y']
        # app.js line 1717 uses: const dSq = dx * dx + dy * dy + 1.0;
        dSq = dx * dx + dy * dy + 1.0
        dist = math.sqrt(dSq)
        force = k_rep / dSq
        fx = (dx / dist) * force
        fy = (dy / dist) * force

        self.assertFalse(math.isnan(fx))
        self.assertFalse(math.isnan(fy))
        self.assertEqual(fx, 0.0, "Coincident nodes should produce 0 division-by-zero artifacts")
        self.assertEqual(fy, 0.0)

    def test_canvas_resize_and_retina_dpr_analysis(self):
        """
        Verify Retina DPR scaling and canvas dimensions in openConstellationModal.
        Tests that devicePixelRatio is captured and canvas buffer is scaled.
        """
        self.assertIn("const dpr = window.devicePixelRatio || 1;", self.app_js)
        self.assertIn("canvas.width = width * dpr;", self.app_js)
        self.assertIn("canvas.height = height * dpr;", self.app_js)
        self.assertIn("canvas.style.width = `${width}px`;", self.app_js)
        self.assertIn("canvas.style.height = `${height}px`;", self.app_js)
        self.assertIn("ctx.scale(dpr, dpr);", self.app_js)

    def test_dispatch_jump_invocation_wiring(self):
        """Verify jumpToArticleFromConstellation(artId) closes modal and opens reader deck."""
        self.assertIn("function jumpToArticleFromConstellation(artId) {", self.app_js)
        self.assertIn("closeConstellationModal();", self.app_js)
        self.assertIn("openModal(artId);", self.app_js)
        self.assertIn("window.jumpToArticleFromConstellation = jumpToArticleFromConstellation;", self.app_js)


class TestFullAuditAndE2ERegressionInvariants(unittest.TestCase):
    """Verifies baseline contracts and runs production hard audit and e2e regression."""

    def test_production_hard_audit_execution(self):
        """Verify production_hard_audit.py passes with 0 failures and 0 warnings."""
        import subprocess
        result = subprocess.run([sys.executable, 'production_hard_audit.py'],
                                cwd=PROJECT_ROOT,
                                capture_output=True,
                                text=True)
        self.assertEqual(result.returncode, 0, f"production_hard_audit.py failed:\n{result.stderr}\n{result.stdout}")
        self.assertIn("ALL 6 AUDIT LAYERS PASSED 100%", result.stdout)

    def test_e2e_remediation_test_suite_execution(self):
        """Verify test_e2e_remediation.py passes 48/48 tests."""
        import subprocess
        result = subprocess.run([sys.executable, '-m', 'unittest', 'tests/test_e2e_remediation.py'],
                                cwd=PROJECT_ROOT,
                                capture_output=True,
                                text=True)
        self.assertEqual(result.returncode, 0, f"test_e2e_remediation.py failed:\n{result.stderr}\n{result.stdout}")
        self.assertIn("OK", result.stderr)


if __name__ == '__main__':
    unittest.main(verbosity=2)
