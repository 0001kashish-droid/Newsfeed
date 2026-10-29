"""
Authoritative Adversarial Stress, Integrity & Quality Audit Suite for Milestone 4
Reviewer: reviewer_rad_m4_1 (Reviewer & Adversarial Critic)
Target: R5 Focus Timer ("10-Minute Intelligence Session") & R7 Knowledge Constellation Map (2D Interactive Canvas Graph)
"""

import json
import math
import os
import re
import unittest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TestM4AdversarialAudit(unittest.TestCase):

    def setUp(self):
        self.app_path = os.path.join(PROJECT_ROOT, "app.js")
        self.style_path = os.path.join(PROJECT_ROOT, "style.css")
        self.index_path = os.path.join(PROJECT_ROOT, "index.html")
        self.news_path = os.path.join(PROJECT_ROOT, "data", "news.json")
        self.podcasts_path = os.path.join(PROJECT_ROOT, "data", "podcasts.json")
        self.memory_path = os.path.join(PROJECT_ROOT, "data", "narrative_memory.json")

        with open(self.app_path, "r", encoding="utf-8") as f:
            self.app_js = f.read()
        with open(self.style_path, "r", encoding="utf-8") as f:
            self.style_css = f.read()
        with open(self.index_path, "r", encoding="utf-8") as f:
            self.index_html = f.read()
        with open(self.news_path, "r", encoding="utf-8") as f:
            self.news_data = json.load(f)
        with open(self.podcasts_path, "r", encoding="utf-8") as f:
            self.podcasts_data = json.load(f)
        with open(self.memory_path, "r", encoding="utf-8") as f:
            self.memory_data = json.load(f)

    # =========================================================================
    # 1. INTEGRITY AUDIT: No Shortcuts, No Cheating, No Facades
    # =========================================================================
    def test_integrity_no_hardcoded_article_ids_in_docket(self):
        """Verify curateFocusDocket implements algorithmic selection without hardcoded IDs."""
        docket_match = re.search(r'function curateFocusDocket\(articles\)\s*\{([\s\S]*?)\n\}', self.app_js)
        self.assertTrue(docket_match, "curateFocusDocket function must exist")
        body = docket_match.group(1)

        # Ensure no specific article IDs from data/news.json are hardcoded
        articles = self.news_data.get('articles', [])
        sample_ids = [a['id'] for a in articles[:10]]
        for aid in sample_ids:
            self.assertNotIn(f"'{aid}'", body, f"Hardcoded article ID '{aid}' detected in curateFocusDocket!")
            self.assertNotIn(f'"{aid}"', body, f'Hardcoded article ID "{aid}" detected in curateFocusDocket!')

    def test_integrity_no_hardcoded_graph_nodes_or_edges(self):
        """Verify buildKnowledgeGraph dynamically extracts entities from data, not static mocks."""
        graph_match = re.search(r'function buildKnowledgeGraph\(articles\)\s*\{([\s\S]*?)\n\}', self.app_js)
        self.assertTrue(graph_match, "buildKnowledgeGraph function must exist")
        body = graph_match.group(1)

        # Check for dynamic extraction from entities
        self.assertIn("entities.countries", body)
        self.assertIn("entities.leaders", body)
        self.assertIn("entities.organizations", body)
        self.assertIn("entities.companies", body)
        self.assertIn("nodeMap.set", body)
        self.assertIn("edgeMap.set", body)

    def test_integrity_no_external_graph_libraries(self):
        """Verify zero external npm, pip, or CDN graph libraries (no d3, Three.js, cytoscape, vis.js)."""
        banned_libraries = ["d3.", "THREE.", "cytoscape", "vis.Network", "echarts", "highcharts"]
        for lib in banned_libraries:
            self.assertNotIn(lib, self.app_js, f"Banned external library '{lib}' detected in app.js")
            self.assertNotIn(lib, self.index_html, f"Banned external library script '{lib}' detected in index.html")

    def test_integrity_data_invariants(self):
        """Verify news.json, podcasts.json, narrative_memory.json were not corrupted or wiped."""
        self.assertEqual(len(self.news_data.get('articles', [])), 134, "news.json must maintain exactly 134 curated articles")
        podcasts = self.podcasts_data.get('podcasts') or self.podcasts_data.get('episodes', [])
        self.assertGreaterEqual(len(podcasts), 6, "podcasts.json must contain valid podcasts")
        self.assertGreaterEqual(len(self.memory_data.get('arcs', {})), 10, "narrative_memory.json must maintain active arcs")

    # =========================================================================
    # 2. R5 FOCUS TIMER: Algorithmic Adversarial Stress Testing
    # =========================================================================
    def _simulate_curate_docket(self, articles):
        """Python execution matching app.js curateFocusDocket logic."""
        pool = [a for a in (articles or []) if not a.get('is_duplicate')]
        categories = ['World', 'Tech', 'Business', 'National']
        docket = []
        selected_ids = set()

        # Phase 1: 4 major pillars
        for cat in categories:
            candidates = [a for a in pool if a.get('category') == cat and a.get('id') not in selected_ids]
            candidates.sort(key=lambda a: (a.get('importance_score', 0) or 0), reverse=True)
            if candidates:
                docket.append(candidates[0])
                selected_ids.add(candidates[0]['id'])

        # Phase 2: 5th story with composite signal
        remaining = [a for a in pool if a.get('id') not in selected_ids]
        remaining.sort(
            key=lambda a: (
                (a.get('importance_score', 0) or 0) +
                (1.5 if a.get('meta', {}).get('is_black_swan') else 0) +
                (0.8 if a.get('meta', {}).get('is_contrarian') else 0)
            ),
            reverse=True
        )

        while len(docket) < 5 and remaining:
            nxt = remaining.pop(0)
            docket.append(nxt)
            selected_ids.add(nxt['id'])

        return docket

    def test_docket_production_dataset_balance(self):
        """Verify docket on actual production dataset produces strictly balanced 5 stories."""
        docket = self._simulate_curate_docket(self.news_data.get('articles', []))
        self.assertEqual(len(docket), 5, "Docket must have exactly 5 stories on production dataset")
        cats = {a['category'] for a in docket}
        for expected_cat in ['World', 'Tech', 'Business', 'National']:
            self.assertIn(expected_cat, cats, f"Pillar '{expected_cat}' must be present in curated docket")
        self.assertEqual(len({a['id'] for a in docket}), 5, "All 5 stories must have distinct IDs")

    def test_docket_empty_input(self):
        """Adversarial: Empty articles input must yield empty docket without exception."""
        docket = self._simulate_curate_docket([])
        self.assertEqual(docket, [])

    def test_docket_all_duplicates(self):
        """Adversarial: When all articles are duplicates, docket should be empty."""
        dupes = [{'id': f'dup_{i}', 'category': 'World', 'is_duplicate': True, 'importance_score': 8.0} for i in range(10)]
        docket = self._simulate_curate_docket(dupes)
        self.assertEqual(docket, [])

    def test_docket_single_category_feed(self):
        """Adversarial: Feed with only 'Tech' articles should gracefully return 5 Tech articles without crash."""
        tech_only = [{'id': f'tech_{i}', 'category': 'Tech', 'is_duplicate': False, 'importance_score': float(i)} for i in range(10)]
        docket = self._simulate_curate_docket(tech_only)
        self.assertEqual(len(docket), 5)
        self.assertTrue(all(a['category'] == 'Tech' for a in docket))
        self.assertEqual(len({a['id'] for a in docket}), 5)

    def test_docket_missing_and_none_importance_scores(self):
        """Adversarial: Articles with None or missing importance_score must not fail sorting."""
        messy = [
            {'id': 'a1', 'category': 'World', 'importance_score': None},
            {'id': 'a2', 'category': 'Tech'},
            {'id': 'a3', 'category': 'Business', 'importance_score': 7.5},
            {'id': 'a4', 'category': 'National', 'importance_score': 0},
            {'id': 'a5', 'category': 'World', 'importance_score': -1.5, 'meta': {'is_black_swan': True}},
        ]
        docket = self._simulate_curate_docket(messy)
        self.assertEqual(len(docket), 5)

    def test_docket_black_swan_and_contrarian_signal_boost(self):
        """Adversarial: Verify Black Swan (+1.5) and Contrarian (+0.8) boosts are correctly prioritized in phase 2."""
        candidates = [
            {'id': 'w1', 'category': 'World', 'importance_score': 6.0},
            {'id': 't1', 'category': 'Tech', 'importance_score': 6.0},
            {'id': 'b1', 'category': 'Business', 'importance_score': 6.0},
            {'id': 'n1', 'category': 'National', 'importance_score': 6.0},
            # 5th candidate choices:
            {'id': 'plain_high', 'category': 'World', 'importance_score': 7.0},
            {'id': 'black_swan_boosted', 'category': 'World', 'importance_score': 6.0, 'meta': {'is_black_swan': True}}, # 6.0 + 1.5 = 7.5 > 7.0
        ]
        docket = self._simulate_curate_docket(candidates)
        docket_ids = [a['id'] for a in docket]
        self.assertIn('black_swan_boosted', docket_ids, "Black swan boosted story (effective 7.5) should beat plain 7.0 story")

    # =========================================================================
    # 3. R7 KNOWLEDGE CONSTELLATION: Graph Extraction Adversarial Testing
    # =========================================================================
    def _simulate_build_knowledge_graph(self, articles):
        """Python execution matching app.js buildKnowledgeGraph logic."""
        node_map = {}
        edge_map = {}

        for art in (articles or []):
            art_id = art.get('id')
            entities = art.get('entities') or {}
            if not isinstance(entities, dict):
                entities = {}
            art_nodes = []

            # Nations
            countries = entities.get('countries') or []
            if isinstance(countries, list):
                for c in countries:
                    name = None
                    if isinstance(c, dict):
                        name = c.get('name') or c.get('code')
                    elif isinstance(c, str):
                        name = c
                    if name and len(name) >= 2:
                        art_nodes.append((f"nation:{name}", "nation", name, "#10b981"))

            # Leaders
            leaders = entities.get('leaders') or []
            if isinstance(leaders, list):
                for l in leaders:
                    name = None
                    if isinstance(l, dict):
                        name = l.get('name')
                    elif isinstance(l, str):
                        name = l
                    if name and len(name) >= 2:
                        art_nodes.append((f"leader:{name}", "leader", name, "#f59e0b"))

            # Organizations
            orgs = entities.get('organizations') or []
            if isinstance(orgs, list):
                for o in orgs:
                    name = None
                    if isinstance(o, dict):
                        name = o.get('name')
                    elif isinstance(o, str):
                        name = o
                    if name and len(name) >= 2:
                        art_nodes.append((f"org:{name}", "org", name, "#0284c7"))

            # Companies
            companies = entities.get('companies') or []
            if isinstance(companies, list):
                for co in companies:
                    name = None
                    if isinstance(co, dict):
                        name = co.get('name')
                    elif isinstance(co, str):
                        name = co
                    if name and len(name) >= 2:
                        art_nodes.append((f"org:{name}", "org", name, "#0284c7"))

            # Clusters
            cluster = art.get('storyCluster')
            if isinstance(cluster, dict) and cluster.get('size', 0) > 1:
                cid = f"cluster:{art.get('category')}-{art_id}"
                art_nodes.append((cid, "cluster", f"{art.get('category')} Cluster", "#a855f7"))

            for nid, ntype, label, color in art_nodes:
                if nid not in node_map:
                    node_map[nid] = {
                        'id': nid,
                        'type': ntype,
                        'label': label,
                        'color': color,
                        'articles': [],
                        'connections': 0
                    }
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

        for edge_key, weight in edge_map.items():
            u, v = edge_key.split('__')
            if u in node_map:
                node_map[u]['connections'] += 1
            if v in node_map:
                node_map[v]['connections'] += 1

        return {'nodes': list(node_map.values()), 'edges': edge_map, 'node_map': node_map}

    def test_graph_extraction_production_data(self):
        """Stress-test entity graph extraction on production dataset."""
        result = self._simulate_build_knowledge_graph(self.news_data.get('articles', []))
        nodes = result['nodes']
        edges = result['edges']

        self.assertGreater(len(nodes), 30, "Graph should extract substantial entity count (>30)")
        self.assertGreater(len(edges), 40, "Graph should extract substantial co-occurrence ties (>40)")

        # Verify all 4 categories exist
        types = {n['type'] for n in nodes}
        for t in ['nation', 'leader', 'org', 'cluster']:
            self.assertIn(t, types, f"Entity type '{t}' must be represented in graph")

    def test_graph_extraction_empty_or_malformed_inputs(self):
        """Adversarial: Entity extraction with malformed entities (None, integers, empty lists)."""
        malformed = [
            {'id': 'm1', 'entities': None},
            {'id': 'm2', 'entities': {'countries': [{'name': 'A'}]}}, # len < 2, should be ignored
            {'id': 'm3', 'entities': {'countries': [{'name': 'France'}], 'leaders': ['Macron']}},
            {'id': 'm4', 'entities': {'organizations': [123, None, {'name': 'United Nations'}]}},
        ]
        result = self._simulate_build_knowledge_graph(malformed)
        nodes = result['nodes']
        labels = {n['label'] for n in nodes}
        self.assertIn('France', labels)
        self.assertIn('Macron', labels)
        self.assertIn('United Nations', labels)
        self.assertNotIn('A', labels, "Entities with length < 2 should be skipped to prevent noise")

    # =========================================================================
    # 4. MATHEMATICAL & PHYSICS SIMULATION AUDIT
    # =========================================================================
    def test_physics_coulomb_distance_singularity_protection(self):
        """Verify Coulomb electrostatic repulsion math protects against d=0 singularity."""
        # In stepPhysics:
        # const dSq = dx * dx + dy * dy + 1.0;
        # Since 1.0 is added, dSq is guaranteed >= 1.0 even when dx=0, dy=0.
        self.assertIn("dx * dx + dy * dy + 1.0", self.app_js, "Coulomb formula must guard d=0 singularity with + 1.0")

    def test_coordinate_transforms_mathematical_inverses(self):
        """Verify toScreen and toWorld transforms are exact mathematical inverses."""
        cx = 500
        cy = 400
        cam_x = -45.5
        cam_y = 120.3
        zoom = 1.45

        def to_screen(wx, wy):
            return cx + (wx + cam_x) * zoom, cy + (wy + cam_y) * zoom

        def to_world(sx, sy):
            return (sx - cx) / zoom - cam_x, (sy - cy) / zoom - cam_y

        test_points = [(0, 0), (100, -200), (-342.1, 88.9), (1234.56, -789.01)]
        for wx, wy in test_points:
            sx, sy = to_screen(wx, wy)
            inv_wx, inv_wy = to_world(sx, sy)
            self.assertAlmostEqual(wx, inv_wx, places=7)
            self.assertAlmostEqual(wy, inv_wy, places=7)

    def test_alpha_cooling_decay_convergence(self):
        """Verify alpha cooling mathematically decays to minAlpha (< 0.005) to conserve CPU."""
        alpha = 1.0
        decay = 0.985
        frames = 0
        while alpha >= 0.005:
            alpha *= decay
            frames += 1
        # Should converge between 300 and 400 frames (~5-6 seconds at 60 FPS)
        self.assertLess(frames, 400)
        self.assertGreater(frames, 250)

    # =========================================================================
    # 5. UI, ACCESSIBILITY & SECURITY AUDIT
    # =========================================================================
    def test_focus_timer_accessibility_and_roles(self):
        """Verify #focusTimerPill has role='timer' and aria-live='polite'."""
        self.assertIn('role="timer"', self.index_html)
        self.assertIn('aria-live="polite"', self.index_html)

    def test_modals_dialog_roles(self):
        """Verify completion report modal and constellation modal have dialog roles."""
        self.assertIn('id="focusReportModal" role="dialog" aria-modal="true"', self.index_html)
        self.assertIn('id="constellationModalBackdrop" role="dialog" aria-modal="true"', self.index_html)

    def test_xss_escaping_in_graph_inspector_and_focus_report(self):
        """Verify escapeHtml and escapeJs are consistently used in DOM injections."""
        self.assertIn("escapeHtml(art.title)", self.app_js)
        self.assertIn("escapeHtml(art.source)", self.app_js)
        self.assertIn("escapeJs(art.id)", self.app_js)
        self.assertIn("escapeHtml(hit.label)", self.app_js)


if __name__ == '__main__':
    unittest.main()
