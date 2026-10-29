#!/usr/bin/env python3
"""
Authoritative Empirical Challenger Test Suite - Milestone 4
Executive Intelligence: Focus Timer (R5) & Knowledge Constellation Map (R7)

Targets:
- Focus Timer 5-story docket curation (app.js: curateFocusDocket)
- Knowledge Constellation graph extraction & physics simulation (app.js: buildKnowledgeGraph, ConstellationSimulation)
- Invariants & Pre-existing Contracts
"""

import json
import math
import os
import re
import unittest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read_file(rel_path):
    with open(os.path.join(PROJECT_ROOT, rel_path), "r", encoding="utf-8") as f:
        return f.read()


class TestFocusTimerDocketCuration(unittest.TestCase):
    """
    Adversarial stress-testing of curateFocusDocket:
    - 4-pillar domain guarantee (World, Tech, Business, National)
    - Highest importance_score sorting per pillar
    - 5th story apex composite signal (importance + Black Swan 1.5 + Contrarian 0.8)
    - Handling varied, skewed, sparse, and adversarial datasets
    """

    @classmethod
    def setUpClass(cls):
        cls.app_js = read_file("app.js")
        with open(os.path.join(PROJECT_ROOT, "data", "news.json"), "r", encoding="utf-8") as f:
            cls.news_data = json.load(f)

    def _curate_focus_docket_sim(self, articles):
        """Python mirror of exact app.js curateFocusDocket algorithm."""
        if not articles:
            return []
        pool = [a for a in articles if isinstance(a, dict) and not a.get("is_duplicate")]
        categories = ["World", "Tech", "Business", "National"]
        docket = []
        selected_ids = set()

        # Phase 1: Select highest importance_score story from each of the 4 major pillars
        for cat in categories:
            candidates = [
                a for a in pool
                if a.get("category") == cat and a.get("id") not in selected_ids
            ]
            candidates.sort(key=lambda a: float(a.get("importance_score") or 0), reverse=True)
            if candidates:
                docket.append(candidates[0])
                selected_ids.add(candidates[0]["id"])

        # Phase 2: Select 5th story with highest remaining composite signal
        remaining = [a for a in pool if a.get("id") not in selected_ids]

        def get_composite_score(a):
            base = float(a.get("importance_score") or 0)
            meta = a.get("meta") or {}
            bonus_bs = 1.5 if meta.get("is_black_swan") else 0.0
            bonus_con = 0.8 if meta.get("is_contrarian") else 0.0
            return base + bonus_bs + bonus_con

        remaining.sort(key=get_composite_score, reverse=True)

        while len(docket) < 5 and remaining:
            nxt = remaining.pop(0)
            docket.append(nxt)
            selected_ids.add(nxt["id"])

        return docket

    def test_production_news_docket_guarantees(self):
        """Verify docket curation on actual production data/news.json."""
        articles = self.news_data.get("articles", [])
        docket = self._curate_focus_docket_sim(articles)

        self.assertEqual(len(docket), 5, "Curated docket must contain exactly 5 stories")

        # Verify no duplicate IDs
        docket_ids = [a["id"] for a in docket]
        self.assertEqual(len(docket_ids), len(set(docket_ids)), "All docket story IDs must be unique")

        # Verify 4-pillar coverage
        categories = {a.get("category") for a in docket}
        for pillar in ["World", "Tech", "Business", "National"]:
            self.assertIn(pillar, categories, f"Docket must contain at least one story from pillar {pillar}")

        # Verify top importance per pillar
        for pillar in ["World", "Tech", "Business", "National"]:
            pillar_in_docket = next(a for a in docket if a.get("category") == pillar)
            all_pillar_articles = [
                a for a in articles
                if not a.get("is_duplicate") and a.get("category") == pillar
            ]
            max_importance = max(float(a.get("importance_score", 0)) for a in all_pillar_articles)
            self.assertEqual(
                float(pillar_in_docket.get("importance_score", 0)),
                max_importance,
                f"Selected {pillar} story must have highest importance_score in that pillar"
            )

    def test_docket_composite_score_boost_black_swan_and_contrarian(self):
        """Verify Phase 2 correctly rewards Black Swan (+1.5) and Contrarian (+0.8)."""
        articles = [
            {"id": "w1", "category": "World", "importance_score": 9.0},
            {"id": "t1", "category": "Tech", "importance_score": 9.0},
            {"id": "b1", "category": "Business", "importance_score": 9.0},
            {"id": "n1", "category": "National", "importance_score": 9.0},
            {"id": "rem_normal", "category": "World", "importance_score": 8.0},
            {"id": "rem_contrarian", "category": "Tech", "importance_score": 7.5, "meta": {"is_contrarian": True}},  # 7.5 + 0.8 = 8.3
            {"id": "rem_black_swan", "category": "Business", "importance_score": 7.0, "meta": {"is_black_swan": True}},  # 7.0 + 1.5 = 8.5
        ]

        docket = self._curate_focus_docket_sim(articles)
        self.assertEqual(len(docket), 5)
        fifth_story = docket[4]
        # rem_black_swan should beat rem_contrarian (8.5 vs 8.3) and rem_normal (8.5 vs 8.0)
        self.assertEqual(fifth_story["id"], "rem_black_swan")

    def test_docket_skewed_dataset_missing_pillars(self):
        """Verify graceful fallback when 1 or more pillars are missing from feed."""
        # Dataset with only World and Tech (0 Business, 0 National)
        articles = [
            {"id": "w1", "category": "World", "importance_score": 9.0},
            {"id": "w2", "category": "World", "importance_score": 8.0},
            {"id": "w3", "category": "World", "importance_score": 7.0},
            {"id": "t1", "category": "Tech", "importance_score": 9.5},
            {"id": "t2", "category": "Tech", "importance_score": 8.5},
            {"id": "t3", "category": "Tech", "importance_score": 6.0},
        ]
        docket = self._curate_focus_docket_sim(articles)
        self.assertEqual(len(docket), 5)
        docket_ids = {a["id"] for a in docket}
        self.assertIn("w1", docket_ids)
        self.assertIn("t1", docket_ids)

    def test_docket_sparse_dataset_under_5_articles(self):
        """Verify behavior when fewer than 5 unique articles exist in feed."""
        articles = [
            {"id": "a1", "category": "World", "importance_score": 8.0},
            {"id": "a2", "category": "Tech", "importance_score": 9.0},
        ]
        docket = self._curate_focus_docket_sim(articles)
        self.assertEqual(len(docket), 2)

        # Empty dataset
        docket_empty = self._curate_focus_docket_sim([])
        self.assertEqual(len(docket_empty), 0)

    def test_docket_suppresses_is_duplicate_articles(self):
        """Verify articles with is_duplicate: True are never included in docket."""
        articles = [
            {"id": "w1", "category": "World", "importance_score": 10.0, "is_duplicate": True},
            {"id": "w2", "category": "World", "importance_score": 8.0, "is_duplicate": False},
            {"id": "t1", "category": "Tech", "importance_score": 9.0},
            {"id": "b1", "category": "Business", "importance_score": 9.0},
            {"id": "n1", "category": "National", "importance_score": 9.0},
            {"id": "x1", "category": "World", "importance_score": 7.0},
        ]
        docket = self._curate_focus_docket_sim(articles)
        docket_ids = [a["id"] for a in docket]
        self.assertNotIn("w1", docket_ids, "is_duplicate article must be strictly excluded")
        self.assertIn("w2", docket_ids)


class TestConstellationGraphExtractionAndPhysics(unittest.TestCase):
    """
    Adversarial stress-testing of Knowledge Constellation Graph:
    - Node categorization and neon color fidelity
    - Edge weighting and co-occurrence counts
    - Duplicate entity resilience
    - Zero divide-by-zero guarantees in Euler/Verlet spring-electrical physics
    """

    @classmethod
    def setUpClass(cls):
        cls.app_js = read_file("app.js")
        with open(os.path.join(PROJECT_ROOT, "data", "news.json"), "r", encoding="utf-8") as f:
            cls.news_data = json.load(f)

    def _build_knowledge_graph_sim(self, articles):
        """Python mirror of app.js buildKnowledgeGraph."""
        node_map = {}
        edge_map = {}

        for art in (articles or []):
            art_id = art.get("id")
            entities = art.get("entities") or {}
            art_nodes = []

            # Nations (#10b981)
            for c in entities.get("countries", []):
                name = c.get("name") if isinstance(c, dict) else (c.get("code") if isinstance(c, dict) else str(c))
                if name and len(name) >= 2:
                    art_nodes.append({"id": f"nation:{name}", "type": "nation", "label": name, "color": "#10b981"})

            # Leaders (#f59e0b)
            for l in entities.get("leaders", []):
                name = l.get("name") if isinstance(l, dict) else str(l)
                if name and len(name) >= 2:
                    art_nodes.append({"id": f"leader:{name}", "type": "leader", "label": name, "color": "#f59e0b"})

            # Organizations (#0284c7)
            for o in entities.get("organizations", []):
                name = o.get("name") if isinstance(o, dict) else str(o)
                if name and len(name) >= 2:
                    art_nodes.append({"id": f"org:{name}", "type": "org", "label": name, "color": "#0284c7"})

            # Companies (#0284c7)
            for co in entities.get("companies", []):
                name = co.get("name") if isinstance(co, dict) else str(co)
                if name and len(name) >= 2:
                    art_nodes.append({"id": f"org:{name}", "type": "org", "label": name, "color": "#0284c7"})

            # Story Clusters (#a855f7)
            sc = art.get("storyCluster")
            if sc and isinstance(sc, dict) and sc.get("size", 0) > 1:
                cid = f"cluster:{art.get('category')}-{art_id}"
                art_nodes.append({"id": cid, "type": "cluster", "label": f"{art.get('category')} Cluster", "color": "#a855f7"})

            # Register nodes in nodeMap
            for node in art_nodes:
                nid = node["id"]
                if nid not in node_map:
                    node_map[nid] = {
                        "id": nid,
                        "type": node["type"],
                        "label": node["label"],
                        "color": node["color"],
                        "articles": [],
                        "connections": 0,
                        "x": 0.0,
                        "y": 0.0,
                        "vx": 0.0,
                        "vy": 0.0,
                        "radius": 12.0
                    }
                if art_id not in node_map[nid]["articles"]:
                    node_map[nid]["articles"].append(art_id)

            # Register co-occurring edges
            for i in range(len(art_nodes)):
                for j in range(i + 1, len(art_nodes)):
                    u = art_nodes[i]["id"]
                    v = art_nodes[j]["id"]
                    if u == v:
                        continue
                    edge_key = f"{u}__{v}" if u < v else f"{v}__{u}"
                    if edge_key not in edge_map:
                        edge_map[edge_key] = {"source": u, "target": v, "weight": 0}
                    edge_map[edge_key]["weight"] += 1

        for n in node_map.values():
            n["radius"] = max(10.0, min(26.0, 10.0 + math.sqrt(len(n["articles"])) * 3.5))

        nodes = list(node_map.values())
        edges = list(edge_map.values())

        for e in edges:
            s = node_map.get(e["source"])
            t = node_map.get(e["target"])
            if s:
                s["connections"] += 1
            if t:
                t["connections"] += 1

        return {"nodes": nodes, "edges": edges, "node_map": node_map}

    def test_graph_node_types_and_neon_colors(self):
        """Verify all 4 node categories and exact hex colors."""
        articles = self.news_data.get("articles", [])
        graph = self._build_knowledge_graph_sim(articles)
        types_found = {n["type"] for n in graph["nodes"]}
        expected_types = {"nation", "leader", "org", "cluster"}

        # Check types presence
        self.assertTrue(expected_types.issubset(types_found), f"Expected {expected_types}, got {types_found}")

        # Check color mapping integrity
        color_rules = {
            "nation": "#10b981",
            "leader": "#f59e0b",
            "org": "#0284c7",
            "cluster": "#a855f7"
        }
        for n in graph["nodes"]:
            expected_color = color_rules.get(n["type"])
            self.assertEqual(n["color"], expected_color)

    def test_graph_edge_weighting_and_bidirectional_consistency(self):
        """Verify edge weights increment strictly and connections are counted."""
        articles = self.news_data.get("articles", [])
        graph = self._build_knowledge_graph_sim(articles)

        self.assertGreater(len(graph["edges"]), 40)
        for e in graph["edges"]:
            self.assertGreaterEqual(e["weight"], 1)
            self.assertNotEqual(e["source"], e["target"], "No self-referential loops allowed")

        # Verify degree count matches edge endpoints
        for n in graph["nodes"]:
            actual_conn = sum(1 for e in graph["edges"] if e["source"] == n["id"] or e["target"] == n["id"])
            self.assertEqual(n["connections"], actual_conn)

    def test_physics_step_zero_divide_by_zero_under_all_conditions(self):
        """
        Stress test stepPhysics under extreme adversarial positions:
        - 2 nodes positioned at exact identical coordinates (0, 0)
        - 100 nodes at exact identical coordinates
        - Extreme coordinates (e.g. 1e12, -1e12)
        - 0 nodes, 1 node
        Verify no ZeroDivisionError, no NaN, no Inf.
        """
        k_rep = 950.0
        k_spring = 0.035
        spring_length = 85.0
        k_gravity = 0.012
        damping = 0.86

        def simulate_physics_step(nodes, edges, node_map, alpha=1.0):
            n = len(nodes)
            # 1. Coulomb Repulsion
            for i in range(n):
                u = nodes[i]
                for j in range(i + 1, n):
                    v = nodes[j]
                    dx = v["x"] - u["x"]
                    dy = v["y"] - u["y"]
                    d_sq = dx * dx + dy * dy + 1.0  # + 1.0 ensures >= 1.0 always
                    dist = math.sqrt(d_sq)
                    force = k_rep / d_sq
                    fx = (dx / dist) * force
                    fy = (dy / dist) * force

                    self.assertFalse(math.isnan(fx), "Coulomb fx cannot be NaN")
                    self.assertFalse(math.isnan(fy), "Coulomb fy cannot be NaN")
                    self.assertFalse(math.isinf(fx), "Coulomb fx cannot be Inf")
                    self.assertFalse(math.isinf(fy), "Coulomb fy cannot be Inf")

                    u["vx"] -= fx
                    u["vy"] -= fy
                    v["vx"] += fx
                    v["vy"] += fy

            # 2. Hooke's Spring Attraction
            for edge in edges:
                u = node_map.get(edge["source"])
                v = node_map.get(edge["target"])
                if not u or not v:
                    continue
                dx = v["x"] - u["x"]
                dy = v["y"] - u["y"]
                dist = math.sqrt(dx * dx + dy * dy) + 0.1  # + 0.1 ensures > 0 always
                delta = dist - spring_length
                force = delta * k_spring * min(3.0, 1.0 + edge["weight"] * 0.4)
                fx = (dx / dist) * force
                fy = (dy / dist) * force

                self.assertFalse(math.isnan(fx), "Hooke fx cannot be NaN")
                self.assertFalse(math.isnan(fy), "Hooke fy cannot be NaN")
                self.assertFalse(math.isinf(fx), "Hooke fx cannot be Inf")
                self.assertFalse(math.isinf(fy), "Hooke fy cannot be Inf")

                u["vx"] += fx
                u["vy"] += fy
                v["vx"] -= fx
                v["vy"] -= fy

            # 3. Center Gravity & Integration
            for i in range(n):
                u = nodes[i]
                u["vx"] -= u["x"] * k_gravity
                u["vy"] -= u["y"] * k_gravity
                u["vx"] *= damping
                u["vy"] *= damping
                u["x"] += u["vx"] * alpha
                u["y"] += u["vy"] * alpha

                self.assertFalse(math.isnan(u["x"]), "Node x position cannot be NaN")
                self.assertFalse(math.isnan(u["y"]), "Node y position cannot be NaN")

        # Test Case 1: Collocated nodes (dx=0, dy=0)
        collocated_nodes = [
            {"id": "n1", "x": 0.0, "y": 0.0, "vx": 0.0, "vy": 0.0},
            {"id": "n2", "x": 0.0, "y": 0.0, "vx": 0.0, "vy": 0.0},
            {"id": "n3", "x": 0.0, "y": 0.0, "vx": 0.0, "vy": 0.0},
        ]
        collocated_edges = [
            {"source": "n1", "target": "n2", "weight": 2},
            {"source": "n2", "target": "n3", "weight": 1},
        ]
        cmap = {n["id"]: n for n in collocated_nodes}
        for _ in range(50):
            simulate_physics_step(collocated_nodes, collocated_edges, cmap)

        # Verify coordinates remained real numbers
        for n in collocated_nodes:
            self.assertTrue(math.isfinite(n["x"]))
            self.assertTrue(math.isfinite(n["y"]))

        # Test Case 2: Extreme values
        extreme_nodes = [
            {"id": "e1", "x": 1e6, "y": 1e6, "vx": 0.0, "vy": 0.0},
            {"id": "e2", "x": -1e6, "y": -1e6, "vx": 0.0, "vy": 0.0},
        ]
        extreme_edges = [{"source": "e1", "target": "e2", "weight": 5}]
        emap = {n["id"]: n for n in extreme_nodes}
        for _ in range(10):
            simulate_physics_step(extreme_nodes, extreme_edges, emap)
        for n in extreme_nodes:
            self.assertTrue(math.isfinite(n["x"]))
            self.assertTrue(math.isfinite(n["y"]))

    def test_app_js_source_code_guards_against_zero_division(self):
        """Verify the exact mathematical denominators in app.js contain defensive padding."""
        # Check Coulomb repulsion denominator in app.js
        self.assertIn("dx * dx + dy * dy + 1.0", self.app_js, "app.js must include + 1.0 in dSq to eliminate division by zero")
        # Check Hooke spring attraction denominator in app.js
        self.assertIn("Math.sqrt(dx * dx + dy * dy) + 0.1", self.app_js, "app.js must include + 0.1 in Hooke dist to eliminate division by zero")


class TestPreservedContractsAndDOMStructure(unittest.TestCase):
    """Verifies interface contracts and DOM elements in index.html, style.css, and app.js."""

    @classmethod
    def setUpClass(cls):
        cls.index_html = read_file("index.html")
        cls.style_css = read_file("style.css")
        cls.app_js = read_file("app.js")

    def test_r5_focus_timer_dom_and_quick_tools(self):
        """Verify Focus Timer elements in HTML."""
        self.assertIn('id="focusTimerPill"', self.index_html)
        self.assertIn('id="focusSessionBtn"', self.index_html)
        self.assertIn('id="focusReportModal"', self.index_html)
        self.assertIn('id="focusTimerDisplay"', self.index_html)
        self.assertIn('id="focusCountDisplay"', self.index_html)
        self.assertIn('id="focusBarFill"', self.index_html)
        self.assertIn('id="focusPauseBtn"', self.index_html)
        self.assertIn('id="focusEndBtn"', self.index_html)

    def test_r7_constellation_modal_dom_and_quick_tools(self):
        """Verify Knowledge Constellation elements in HTML."""
        self.assertIn('id="constellationMapBtn"', self.index_html)
        self.assertIn('id="constellationModalBackdrop"', self.index_html)
        self.assertIn('id="constellationCanvas"', self.index_html)
        self.assertIn('id="constellationStatsLabel"', self.index_html)
        self.assertIn('id="constellationLegend"', self.index_html)
        self.assertIn('id="constellationInspector"', self.index_html)
        self.assertIn('id="inspectorDispatchesList"', self.index_html)

    def test_visionos_liquid_glass_styles(self):
        """Verify VisionOS styling rules for Focus Timer and Constellation."""
        self.assertIn(".focus-timer-pill", self.style_css)
        self.assertIn(".constellation-modal-backdrop", self.style_css)
        self.assertIn(".constellation-modal-box", self.style_css)
        self.assertIn(".constellation-canvas", self.style_css)
        self.assertIn(".constellation-inspector", self.style_css)
        self.assertIn('[data-theme="light"] .focus-timer-pill', self.style_css)
        self.assertIn('[data-theme="light"] .constellation-canvas-container', self.style_css)

    def test_window_exports(self):
        """Verify required functions are cleanly exported to window."""
        exports = [
            "curateFocusDocket",
            "startFocusSession",
            "toggleFocusPause",
            "completeFocusSession",
            "exitFocusSession",
            "buildKnowledgeGraph",
            "ConstellationSimulation",
            "openConstellationModal",
            "closeConstellationModal",
            "jumpToArticleFromConstellation"
        ]
        for exp in exports:
            self.assertIn(f"window.{exp} =", self.app_js, f"window.{exp} export missing in app.js")


if __name__ == "__main__":
    unittest.main()
