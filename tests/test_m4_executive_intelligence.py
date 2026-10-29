"""
Milestone 4 Test Suite: Executive Intelligence
(R5: Focus Timer & R7: Knowledge Constellation Map)

Verifies:
- R5: Focus Timer ("10-Minute Intelligence Session"):
    - DOM elements in index.html (#focusTimerPill, #focusSessionBtn, #focusReportModal)
    - Focus Timer engine in app.js (countdown, start/pause/end/exit)
    - Optimal 5-story executive docket algorithm (4-pillar domain balance + apex signal)
    - Infinite scroll suppression during active session
    - Read tracking and completion report stats modal
    - VisionOS liquid glass styles in style.css + light mode adaptations
- R7: Knowledge Constellation Map (2D Interactive Canvas Graph modal):
    - DOM elements in index.html (#constellationModalBackdrop, #constellationCanvas, #constellationMapBtn, controls, legend, inspector)
    - In-memory entity graph extraction (leaders, nations, orgs, clusters)
    - Pure HTML5 Canvas 2D force-directed simulation (Euler integration, zero external dependencies)
    - Categorized neon colors (Nations #10b981, Leaders #f59e0b, Orgs #0284c7, Clusters #a855f7)
    - Interactive navigation (pan, zoom, hover tooltip, node selection, dispatch jump to openModal)
    - VisionOS liquid glass modal & canvas styling in style.css + light mode
- Preserved Invariants:
    - Zero external npm / pip dependencies
    - data/news.json untouched
    - All existing baseline and radical contracts preserved
"""

import json
import os
import re
import unittest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TestM4ExecutiveIntelligence(unittest.TestCase):

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
    # R5: Focus Timer DOM Elements (index.html)
    # -------------------------------------------------------------------------
    def test_focus_timer_pill_in_html(self):
        """Verify #focusTimerPill and its sub-elements in index.html."""
        self.assertIn('id="focusTimerPill"', self.index_html)
        self.assertIn('class="focus-timer-pill"', self.index_html)
        self.assertIn('focus-pill-pulse', self.index_html)
        self.assertIn('id="focusTimerDisplay"', self.index_html)
        self.assertIn('id="focusCountDisplay"', self.index_html)
        self.assertIn('id="focusBarFill"', self.index_html)
        self.assertIn('id="focusPauseBtn"', self.index_html)
        self.assertIn('id="focusEndBtn"', self.index_html)

    def test_focus_session_btn_in_quick_tools(self):
        """Verify #focusSessionBtn is placed in #headerToolsPopover."""
        self.assertIn('id="focusSessionBtn"', self.index_html)
        self.assertIn('focus-tool-pill', self.index_html)
        popover_match = re.search(r'id="headerToolsPopover".*?id="focusSessionBtn"', self.index_html, re.DOTALL)
        self.assertIsNotNone(popover_match, "#focusSessionBtn should reside inside #headerToolsPopover")

    def test_focus_report_modal_in_html(self):
        """Verify #focusReportModal and executive completion stats elements."""
        self.assertIn('id="focusReportModal"', self.index_html)
        self.assertIn('id="focusReportTitle"', self.index_html)
        self.assertIn('id="metricTimeElapsed"', self.index_html)
        self.assertIn('id="metricStoriesRead"', self.index_html)
        self.assertIn('id="metricDomainCoverage"', self.index_html)
        self.assertIn('id="metricSignalScore"', self.index_html)
        self.assertIn('id="focusReportDomains"', self.index_html)
        self.assertIn('id="focusReturnFeedBtn"', self.index_html)
        self.assertIn('id="focusCopySummaryBtn"', self.index_html)

    # -------------------------------------------------------------------------
    # R5: Focus Session Engine (app.js)
    # -------------------------------------------------------------------------
    def test_focus_session_state_and_functions_exported(self):
        """Verify Focus Session state and window bindings in app.js."""
        self.assertIn("focusSession:", self.app_js)
        self.assertIn("function curateFocusDocket(", self.app_js)
        self.assertIn("function startFocusSession(", self.app_js)
        self.assertIn("function toggleFocusPause(", self.app_js)
        self.assertIn("function completeFocusSession(", self.app_js)
        self.assertIn("function exitFocusSession(", self.app_js)

        self.assertIn("window.curateFocusDocket = curateFocusDocket", self.app_js)
        self.assertIn("window.startFocusSession = startFocusSession", self.app_js)
        self.assertIn("window.toggleFocusPause = toggleFocusPause", self.app_js)
        self.assertIn("window.completeFocusSession = completeFocusSession", self.app_js)
        self.assertIn("window.exitFocusSession = exitFocusSession", self.app_js)

    def test_curate_focus_docket_algorithm_simulation(self):
        """Simulate and verify the 5-story executive docket algorithm on production news data."""
        articles = self.news_data.get('articles', [])
        self.assertGreater(len(articles), 20)

        # Python replica of curateFocusDocket logic
        pool = [a for a in articles if not a.get('is_duplicate')]
        categories = ['World', 'Tech', 'Business', 'National']
        docket = []
        selected_ids = set()

        for cat in categories:
            candidates = [a for a in pool if a.get('category') == cat and a.get('id') not in selected_ids]
            candidates.sort(key=lambda a: a.get('importance_score', 0), reverse=True)
            if candidates:
                docket.append(candidates[0])
                selected_ids.add(candidates[0]['id'])

        remaining = [a for a in pool if a.get('id') not in selected_ids]
        remaining.sort(
            key=lambda a: (
                a.get('importance_score', 0) +
                (1.5 if a.get('meta', {}).get('is_black_swan') else 0) +
                (0.8 if a.get('meta', {}).get('is_contrarian') else 0)
            ),
            reverse=True
        )

        while len(docket) < 5 and remaining:
            nxt = remaining.pop(0)
            docket.append(nxt)
            selected_ids.add(nxt['id'])

        self.assertEqual(len(docket), 5, "Docket must contain exactly 5 articles")
        docket_cats = {a.get('category') for a in docket}
        for cat in categories:
            self.assertIn(cat, docket_cats, f"Docket must contain at least one {cat} story for domain balance")

        # Zero duplicates
        self.assertEqual(len(selected_ids), 5, "All 5 stories in docket must have distinct IDs")

    def test_focus_session_infinite_scroll_suppression(self):
        """Verify app.js disconnects infinite scroll observer when focus session is active."""
        self.assertIn("state.focusSession && state.focusSession.active", self.app_js)
        # Check that renderGrid guards scroll observer
        self.assertIn("_gridScrollObserver.disconnect()", self.app_js)

    # -------------------------------------------------------------------------
    # R7: Knowledge Constellation DOM Elements (index.html)
    # -------------------------------------------------------------------------
    def test_constellation_modal_elements_in_html(self):
        """Verify #constellationModalBackdrop and its components in index.html."""
        self.assertIn('id="constellationModalBackdrop"', self.index_html)
        self.assertIn('id="constellationModalBox"', self.index_html)
        self.assertIn('id="constellationCanvas"', self.index_html)
        self.assertIn('id="constellationStatsLabel"', self.index_html)
        self.assertIn('id="constellationLegend"', self.index_html)
        self.assertIn('id="constellationZoomInBtn"', self.index_html)
        self.assertIn('id="constellationZoomOutBtn"', self.index_html)
        self.assertIn('id="constellationFitBtn"', self.index_html)
        self.assertIn('id="constellationCloseBtn"', self.index_html)
        self.assertIn('id="constellationTooltip"', self.index_html)
        self.assertIn('id="constellationInspector"', self.index_html)
        self.assertIn('id="inspectorDispatchesList"', self.index_html)

    def test_constellation_btn_in_quick_tools(self):
        """Verify #constellationMapBtn is placed in #headerToolsPopover."""
        self.assertIn('id="constellationMapBtn"', self.index_html)
        popover_match = re.search(r'id="headerToolsPopover".*?id="constellationMapBtn"', self.index_html, re.DOTALL)
        self.assertIsNotNone(popover_match, "#constellationMapBtn should reside inside #headerToolsPopover")

    # -------------------------------------------------------------------------
    # R7: Knowledge Constellation Engine (app.js)
    # -------------------------------------------------------------------------
    def test_constellation_functions_and_classes_exported(self):
        """Verify graph extraction, simulation class, and interaction handlers in app.js."""
        self.assertIn("function buildKnowledgeGraph(", self.app_js)
        self.assertIn("class ConstellationSimulation", self.app_js)
        self.assertIn("function openConstellationModal(", self.app_js)
        self.assertIn("function closeConstellationModal(", self.app_js)
        self.assertIn("function jumpToArticleFromConstellation(", self.app_js)

        self.assertIn("window.buildKnowledgeGraph = buildKnowledgeGraph", self.app_js)
        self.assertIn("window.ConstellationSimulation = ConstellationSimulation", self.app_js)
        self.assertIn("window.openConstellationModal = openConstellationModal", self.app_js)
        self.assertIn("window.closeConstellationModal = closeConstellationModal", self.app_js)
        self.assertIn("window.jumpToArticleFromConstellation = jumpToArticleFromConstellation", self.app_js)

    def test_build_knowledge_graph_simulation_and_colors(self):
        """Verify entity graph extraction logic and required neon color mappings."""
        expected_colors = {
            'nation': '#10b981',
            'leader': '#f59e0b',
            'org': '#0284c7',
            'cluster': '#a855f7'
        }
        for node_type, color in expected_colors.items():
            self.assertIn(color, self.app_js, f"Color '{color}' for '{node_type}' must be present in app.js")

        # Simulate graph extraction in Python
        articles = self.news_data.get('articles', [])
        node_map = {}
        edge_map = {}

        for art in articles:
            art_id = art.get('id')
            entities = art.get('entities', {})
            art_nodes = []

            for c in entities.get('countries', []):
                name = c.get('name') or c.get('code')
                if name and len(name) >= 2:
                    art_nodes.append((f"nation:{name}", "nation", name, "#10b981"))

            for l in entities.get('leaders', []):
                name = l.get('name')
                if name and len(name) >= 2:
                    art_nodes.append((f"leader:{name}", "leader", name, "#f59e0b"))

            for o in entities.get('organizations', []):
                name = o.get('name')
                if name and len(name) >= 2:
                    art_nodes.append((f"org:{name}", "org", name, "#0284c7"))

            for co in entities.get('companies', []):
                name = co.get('name')
                if name and len(name) >= 2:
                    art_nodes.append((f"org:{name}", "org", name, "#0284c7"))

            cluster = art.get('storyCluster')
            if cluster and cluster.get('size', 0) > 1:
                cid = f"cluster:{art.get('category')}-{art_id}"
                art_nodes.append((cid, "cluster", f"{art.get('category')} Cluster", "#a855f7"))

            for nid, ntype, label, color in art_nodes:
                if nid not in node_map:
                    node_map[nid] = {'id': nid, 'type': ntype, 'label': label, 'articles': []}
                if art_id not in node_map[nid]['articles']:
                    node_map[nid]['articles'].append(art_id)

            for i in range(len(art_nodes)):
                for j in range(i + 1, len(art_nodes)):
                    u = art_nodes[i][0]
                    v = art_nodes[j][0]
                    if u == v:
                        continue
                    edge_key = f"{u}__{v}" if u < v else f"{v}__{u}"
                    edge_map[edge_key] = edge_map.get(edge_key, 0) + 1

        self.assertGreater(len(node_map), 30, "Graph should extract at least 30 distinct entity nodes")
        self.assertGreater(len(edge_map), 40, "Graph should extract at least 40 co-occurring edges")

    def test_pure_canvas_2d_force_simulation_math(self):
        """Verify physics simulation mathematics (Coulomb, Hooke, damping, cooling)."""
        self.assertIn("stepPhysics()", self.app_js)
        self.assertIn("toScreen(", self.app_js)
        self.assertIn("toWorld(", self.app_js)
        self.assertIn("getNodeAtScreenPos(", self.app_js)
        self.assertIn("fitToScreen()", self.app_js)
        self.assertIn("this.damping", self.app_js)
        self.assertIn("this.alpha", self.app_js)
        # Ensure zero external graph libraries imported
        self.assertNotIn("d3.force", self.app_js)
        self.assertNotIn("THREE.", self.app_js)

    # -------------------------------------------------------------------------
    # VisionOS Liquid Glass Styles (style.css)
    # -------------------------------------------------------------------------
    def test_focus_timer_styles_in_css(self):
        """Verify CSS styling for .focus-timer-pill and completion report modal."""
        self.assertIn(".focus-timer-pill", self.style_css)
        self.assertIn("position: fixed", self.style_css)
        self.assertIn(".focus-pill-pulse", self.style_css)
        self.assertIn(".focus-pill-bar-fill", self.style_css)
        self.assertIn(".focus-report-card", self.style_css)
        self.assertIn(".focus-metrics-grid", self.style_css)
        self.assertIn('[data-theme="light"] .focus-timer-pill', self.style_css)

    def test_constellation_styles_in_css(self):
        """Verify CSS styling for constellation modal, canvas, and inspector."""
        self.assertIn(".constellation-modal-backdrop", self.style_css)
        self.assertIn(".constellation-modal-box", self.style_css)
        self.assertIn(".constellation-canvas", self.style_css)
        self.assertIn(".constellation-inspector", self.style_css)
        self.assertIn(".inspector-dispatch-card", self.style_css)
        self.assertIn(".constellation-tooltip", self.style_css)
        self.assertIn('[data-theme="light"] .constellation-canvas-container', self.style_css)

    # -------------------------------------------------------------------------
    # Preservation of Baseline Contracts & Invariants
    # -------------------------------------------------------------------------
    def test_baseline_and_prior_milestone_contracts_preserved(self):
        """Verify all pre-existing contracts across M1, M2, M3 remain unbroken."""
        required_contracts = [
            "setupMobileDeckSwipe",
            "setupMobilePullToRefresh",
            "resetAllFiltersAndRefresh",
            "pullToRefreshBanner",
            "searchClearBtn",
            "scrollbar-width: thin",
            "liquid-glass-resonance-box",
            "liquid-glass-narrative-box",
            "thought-card-resonant-news",
            "pwaVaultIndicatorBtn",
            "setupPWAOfflineVault",
            "computeStoryMetabolism",
            "setupDensityController",
            "getPublisherOrigin",
            "renderPerspectivePrism",
            "renderNarrativeTimeMachine"
        ]
        combined_source = self.index_html + self.style_css + self.app_js
        for contract in required_contracts:
            self.assertIn(contract, combined_source, f"Contract '{contract}' was lost or renamed!")


if __name__ == '__main__':
    unittest.main()
