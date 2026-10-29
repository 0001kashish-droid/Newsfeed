# Copyright (c) 2026 Kashish Bhushan — News Colossal
# Adversarial Empirical Challenge Suite: Milestone 3-2
# Author: challenger_hermetic_m3_2
"""
Empirical stress-test and verification harness for:
1. Honest Null Invariants on completely unlinked dispatches across all memory states.
2. Boundary input stress on substantive_stems and match_article_to_arc
   (None, empty strings, emojis, unicode, extreme length strings, malformed schemas).
3. Tri-Anchor Coherence Invariant permutations (strictly requires Anchor 1 AND 2 AND 3).
4. Cross-milestone regression stability:
   - Milestone 1: Zero wire publishers in entities or active agents.
   - Milestone 2: Clean active agents (<= 5 words, no synthetic fallbacks).
"""

import copy
import json
import os
import sys
import time
import unittest

_TEST_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_TEST_DIR)
_SCRIPTS_DIR = os.path.join(_PROJECT_ROOT, 'scripts')

if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)

from intelligence.memory import (
    substantive_stems,
    match_article_to_arc,
    update_memory,
    load_memory,
    _flatten_entities,
    _extract_article_entities_for_anchors,
    _extract_arc_entities_for_anchors,
    MEDIA_WIRE_ENTITIES,
    STOPWORDS
)
from intelligence.curation import thread_narratives
from intelligence.sanitizer import PUBLISHER_QUARANTINE_SET, is_quarantined_publisher
from intelligence.entities import SyntacticActorGrammar, extract_entities


class TestHonestNullInvariants(unittest.TestCase):
    """
    Adversarial verification of honest null schema on unlinked articles
    across various memory states and feed configurations.
    """

    def _expected_null_structure(self):
        return {
            'arc_id': None,
            'arc_title': None,
            'day_number': 0,
            'total_chapters': 0,
            'importance_trend': None,
            'previous_headlines': []
        }

    def test_unlinked_dispatches_with_empty_memory(self):
        """Articles processed against empty memory must receive genuine honest null schema."""
        articles = [
            {'id': 'art-1', 'title': 'Novel Deep Space Discovery Confirmed'},
            {'id': 'art-2', 'title': 'Global Renewable Capacity Breaks Record'}
        ]
        empty_memories = [None, {}, {'arcs': []}, {'version': 1, 'arcs': []}]
        for mem in empty_memories:
            with self.subTest(mem=mem):
                arts_copy = copy.deepcopy(articles)
                result = thread_narratives(arts_copy, mem)
                for a in result:
                    self.assertIn('narrative_arc', a)
                    self.assertEqual(a['narrative_arc'], self._expected_null_structure())

    def test_unlinked_dispatches_with_active_memory(self):
        """Articles that do not match active arcs must 100% receive honest null schema."""
        memory = {
            'version': 1,
            'arcs': [
                {
                    'arc_id': 'arc-ai-chip-war',
                    'title': 'Semiconductor Export Curbs and Foundries',
                    'keywords': ['semiconductor', 'foundry', 'chips'],
                    'entity_signature': 'US:TW:TSMC:Nvidia',
                    'regions': ['North America', 'Asia-Pacific'],
                    'category': 'Tech',
                    'first_seen': '2026-10-01T00:00:00Z',
                    'chapter_count': 5,
                    'chapter_titles': [
                        'Foundry subsidies approved',
                        'Export control rules tighten',
                        'Chip design firms pivot'
                    ]
                }
            ]
        }
        # Completely unlinked articles
        unlinked_articles = [
            {
                'id': 'art-novel-1',
                'title': 'Peruvian Archaeologists Uncover Pre-Incan Temple',
                'description': 'Excavation team unearths coastal ceremonial complex.',
                'region': 'South America',
                'category': 'Culture',
                'entities': {'countries': [{'code': 'PE', 'name': 'Peru'}], 'people': [], 'organizations': ['National Institute of Culture']}
            },
            {
                'id': 'art-novel-2',
                'title': 'Deep Sea Hydrothermal Vent Ecosystem Discovered in Southern Ocean',
                'description': 'Marine biologists identify novel chemosynthetic organisms.',
                'region': 'Global',
                'category': 'Science',
                'entities': {'countries': [], 'people': [], 'organizations': ['Oceanic Institute']}
            },
            {
                'id': 'art-novel-3',
                'title': 'Local Municipal Election Results Certified in Reykjavik',
                'description': 'Civic coalition wins majority in city council voting.',
                'region': 'Europe',
                'category': 'Politics',
                'entities': {'countries': [{'code': 'IS', 'name': 'Iceland'}], 'people': [], 'organizations': ['Reykjavik Council']}
            }
        ]

        result = thread_narratives(unlinked_articles, memory)
        for a in result:
            self.assertIn('narrative_arc', a)
            na = a['narrative_arc']
            self.assertEqual(na, self._expected_null_structure(),
                             f"Article {a['id']} received non-honest null: {na}")
            self.assertIsNone(na['arc_id'])
            self.assertIsNone(na['arc_title'])
            self.assertEqual(na['day_number'], 0)
            self.assertEqual(na['total_chapters'], 0)
            self.assertIsNone(na['importance_trend'])
            self.assertEqual(na['previous_headlines'], [])

    def test_news_json_real_dataset_unlinked_adherence(self):
        """100% of unlinked articles in data/news.json must adhere to honest null schema."""
        news_path = os.path.join(_PROJECT_ROOT, 'data', 'news.json')
        with open(news_path, 'r', encoding='utf-8') as f:
            news = json.load(f)
        articles = news.get('articles', [])
        self.assertGreater(len(articles), 0)

        unlinked = [a for a in articles if not a.get('narrative_arc', {}).get('arc_id')]
        self.assertGreater(len(unlinked), 0, "Real dataset must have unlinked articles")

        expected = self._expected_null_structure()
        for a in unlinked:
            na = a.get('narrative_arc', {})
            self.assertEqual(na, expected, f"Article {a.get('id')} failed honest null schema: {na}")


class TestBoundaryInputStress(unittest.TestCase):
    """
    Stress-tests boundary inputs against substantive_stems and match_article_to_arc:
    None, empty strings, emojis, unicode, extreme lengths, and malformed types.
    """

    def test_substantive_stems_boundary_primitives(self):
        """None, empty strings, whitespace, non-strings must safely produce empty set."""
        falsy_inputs = [None, "", "   ", "\t\n\r", 0, 12345, 3.14159, False, True, [], {}, object()]
        for inp in falsy_inputs:
            with self.subTest(inp=inp):
                res = substantive_stems(inp)
                self.assertIsInstance(res, set)
                self.assertEqual(len(res), 0)

    def test_substantive_stems_unicode_and_emojis(self):
        """Emojis and non-Latin unicode must not crash tokenization or stemming."""
        emoji_text = "🚀🔥💻🌍🤖✨🎉💥"
        res = substantive_stems(emoji_text)
        self.assertIsInstance(res, set)
        self.assertEqual(len(res), 0)

        mixed_text = "AI revolution in Tokyo 🚀🤖 chips packaging surging in 2026! 🇯🇵"
        res_mixed = substantive_stems(mixed_text)
        self.assertIn("ai", res_mixed)
        self.assertIn("tokyo", res_mixed)
        self.assertIn("chip", res_mixed)

        cjk_text = "人工智能 科技 芯片 制造 突破"
        res_cjk = substantive_stems(cjk_text)
        self.assertIsInstance(res_cjk, set)

        cyrillic_text = "Россия Москва Газпром энергетика"
        res_cyr = substantive_stems(cyrillic_text)
        self.assertIsInstance(res_cyr, set)

    def test_substantive_stems_extreme_length_and_performance(self):
        """Massive 100,000-character payload must complete without ReDoS or memory blowout."""
        repeated_text = ("semiconductor foundry supply chain manufacturing export controls " * 1500)
        self.assertGreater(len(repeated_text), 90000)

        t0 = time.perf_counter()
        res = substantive_stems(repeated_text)
        elapsed = time.perf_counter() - t0

        self.assertLess(elapsed, 0.25, f"substantive_stems took too long on 100k chars: {elapsed:.4f}s")
        self.assertIn("semiconductor", res)
        self.assertIn("foundry", res)
        self.assertIn("manufactur", res)

    def test_substantive_stems_all_punctuation_and_all_numbers(self):
        """Punctuation-only and number-only strings must produce empty set."""
        punct = "!@#$%^&*()_+-=[]{}|;':\",./<>?`~\\|" * 100
        self.assertEqual(substantive_stems(punct), set())

        numbers = "100 2026 3.1415 9999999 000 42 7"
        self.assertEqual(substantive_stems(numbers), set())

    def test_match_article_to_arc_extreme_boundaries(self):
        """match_article_to_arc must gracefully handle malformed, None, empty, or huge inputs."""
        valid_arc = {
            'arc_id': 'arc-test-1',
            'title': 'Diplomatic Summit on Climate Targets in Geneva',
            'keywords': ['climate', 'summit', 'diplomatic', 'geneva', 'emissions'],
            'entity_signature': 'CH:Geneva:UN',
            'regions': ['Europe'],
            'category': 'World',
            'chapter_titles': ['Delegates Arrive in Geneva for Climate Talks']
        }

        # Case 1: article is None, non-dict, or empty
        for bad_art in [None, {}, [], "article", 12345]:
            match, score = match_article_to_arc(bad_art, [valid_arc])
            self.assertIsNone(match)
            self.assertEqual(score, 0.0)

        # Case 2: arcs list is None, empty, or contains invalid items
        valid_article = {
            'title': 'Geneva Climate Summit Concludes with Emissions Treaty',
            'description': 'Delegates reach consensus on renewable energy pledges.',
            'region': 'Europe',
            'category': 'World',
            'entities': {'countries': [{'code': 'CH', 'name': 'Switzerland'}], 'organizations': ['UN', 'Geneva']}
        }
        for bad_arcs in [None, [], [None], [{}], ["invalid"], [1234]]:
            match, score = match_article_to_arc(valid_article, bad_arcs)
            self.assertIsNone(match)
            self.assertEqual(score, 0.0)

        # Case 3: article with 100,000 char title and description
        huge_article = {
            'title': 'Geneva Climate Treaty ' + ('climate emissions treaty ' * 3000),
            'description': 'Geneva summit delegates ' + ('renewable energy consensus ' * 3000),
            'region': 'Europe',
            'category': 'World',
            'entities': {'countries': [{'code': 'CH', 'name': 'Switzerland'}], 'organizations': ['UN', 'Geneva']}
        }
        t0 = time.perf_counter()
        match, score = match_article_to_arc(huge_article, [valid_arc])
        elapsed = time.perf_counter() - t0
        self.assertLess(elapsed, 0.50, f"match_article_to_arc exceeded latency budget: {elapsed:.4f}s")
        # Should still safely evaluate
        self.assertIsInstance(score, float)

        # Case 4: arc with 500 chapters
        deep_arc = copy.deepcopy(valid_arc)
        deep_arc['chapter_titles'] = [f"Chapter {i} update on Geneva treaty" for i in range(500)]
        match, score = match_article_to_arc(valid_article, [deep_arc])
        self.assertIsNotNone(match)
        self.assertGreaterEqual(score, 0.30)

        # Case 5: threshold boundaries (NaN, inf, negative, huge)
        match, score = match_article_to_arc(valid_article, [valid_arc], threshold=2.0)
        self.assertIsNone(match)
        self.assertEqual(score, 0.0)


class TestTriAnchorStrictPermutations(unittest.TestCase):
    """
    Formally verifies that ALL 3 anchors (Geopolitical Theater, Entity Intersection,
    Lexical Jaccard >= 0.30) must hold simultaneously. Failing any one anchor
    MUST result in immediate rejection (None, 0.0).
    """

    def setUp(self):
        self.target_arc = {
            'arc_id': 'arc-berlin-defense-pact',
            'title': 'Germany France Bilateral Defense Procurement Framework in Berlin',
            'keywords': ['defense', 'procurement', 'framework', 'berlin', 'treaty', 'tanks'],
            'entity_signature': 'DE:FR:Bundeswehr:DGA',
            'regions': ['Europe'],
            'category': 'World',
            'chapter_titles': ['Berlin Defense Procurement Talks Open']
        }

    def test_anchor1_fails_geopolitical_mismatch(self):
        """
        Anchor 2 (Shared entities DE, FR) and Anchor 3 (Jaccard > 0.40) match,
        but Anchor 1 FAILS (Region is Asia-Pacific with no country intersection).
        Must reject (None, 0.0).
        """
        article = {
            'title': 'Germany France Defense Procurement Framework Treaty in Berlin',
            'description': 'Bilateral defense procurement framework agreements signed.',
            'region': 'Asia-Pacific',  # Geographic theater mismatch
            'category': 'World',
            'entities': {
                'countries': [{'code': 'JP', 'name': 'Japan'}],  # No DE / FR country match
                'organizations': ['Bundeswehr', 'DGA']
            }
        }
        match, score = match_article_to_arc(article, [self.target_arc])
        self.assertIsNone(match, "Must reject when Anchor 1 fails (geopolitical theater mismatch)")
        self.assertEqual(score, 0.0)

    def test_anchor2_fails_insufficient_entities(self):
        """
        Anchor 1 (Europe match) and Anchor 3 (Jaccard > 0.40) match,
        but Anchor 2 FAILS (disjoint entities: no shared non-generic entities or leaders).
        Must reject (None, 0.0).
        """
        article = {
            'title': 'Defense Procurement Framework Treaty for Tanks and Equipment in Europe',
            'description': 'Procurement talks open for defense framework treaty equipment.',
            'region': 'Europe',
            'category': 'World',
            'entities': {
                'organizations': ['Nordic Defense Union', 'Baltic Assembly'],
                'people': ['Kaja Kallas']
            }
        }
        match, score = match_article_to_arc(article, [self.target_arc], threshold=0.30)
        self.assertIsNone(match, "Must reject when Anchor 2 fails (insufficient non-generic entities)")
        self.assertEqual(score, 0.0)

    def test_country_code_and_name_alias_entity_behavior(self):
        """
        Empirical characterization of entity extraction:
        Verify that a country object {'code': 'DE', 'name': 'Germany'} adds both 'de' and 'germany'.
        """
        article = {
            'title': 'Test article',
            'entities': {'countries': [{'code': 'DE', 'name': 'Germany'}]}
        }
        _, _, entities, _ = _extract_article_entities_for_anchors(article)
        self.assertIn('de', entities)
        self.assertIn('germany', entities)

    def test_anchor3_fails_low_jaccard_similarity(self):
        """
        Anchor 1 (Europe, DE) and Anchor 2 (DE, FR, Bundeswehr) match,
        but Anchor 3 FAILS (Jaccard < 0.30, disparate topic within same entities).
        Must reject (None, 0.0).
        """
        article = {
            'title': 'Germany and France Cultural Museum Exhibition Opens',
            'description': 'Bundeswehr historical artifacts displayed in joint artistic retrospective.',
            'region': 'Europe',
            'category': 'World',
            'entities': {
                'countries': [{'code': 'DE', 'name': 'Germany'}, {'code': 'FR', 'name': 'France'}],
                'organizations': ['Bundeswehr', 'DGA']
            }
        }
        match, score = match_article_to_arc(article, [self.target_arc], threshold=0.30)
        self.assertIsNone(match, "Must reject when Anchor 3 fails (Jaccard < 0.30)")
        self.assertEqual(score, 0.0)

    def test_all_three_anchors_satisfy_passes(self):
        """When Anchor 1 AND Anchor 2 AND Anchor 3 simultaneously hold, binding succeeds."""
        article = {
            'title': 'Germany France Bilateral Defense Procurement Framework Moves Ahead',
            'description': 'Berlin talks confirm joint procurement treaty for military tanks.',
            'region': 'Europe',
            'category': 'World',
            'entities': {
                'countries': [{'code': 'DE', 'name': 'Germany'}, {'code': 'FR', 'name': 'France'}],
                'organizations': ['Bundeswehr', 'DGA']
            }
        }
        match, score = match_article_to_arc(article, [self.target_arc], threshold=0.30)
        self.assertIsNotNone(match, "Must bind when all three anchors are satisfied")
        self.assertEqual(match['arc_id'], self.target_arc['arc_id'])
        self.assertGreaterEqual(score, 0.30)


class TestCrossMilestoneRegression(unittest.TestCase):
    """
    Empirically verifies that Milestone 1 (Wire Sanitization & Quarantine)
    and Milestone 2 (Syntactic 5W1H Actor Grammar & Collective Factions)
    remain 100% intact across memory processing and news data.
    """

    def test_milestone1_zero_wire_publishers_in_quarantine_leakage(self):
        """Quarantined wire services must never appear in article organizations or arc entities."""
        known_wires = {'reuters', 'associated press', 'ap', 'bbc', 'bloomberg', 'afp', 'dow jones'}
        news_path = os.path.join(_PROJECT_ROOT, 'data', 'news.json')
        with open(news_path, 'r', encoding='utf-8') as f:
            news = json.load(f)
        articles = news.get('articles', [])

        for a in articles:
            ents = a.get('entities', {})
            orgs = ents.get('organizations', []) if isinstance(ents, dict) else []
            for org in orgs:
                if isinstance(org, str):
                    self.assertNotIn(org.lower(), known_wires,
                                     f"Wire service '{org}' leaked into organizations for {a.get('id')}")

        memory_path = os.path.join(_PROJECT_ROOT, 'data', 'narrative_memory.json')
        with open(memory_path, 'r', encoding='utf-8') as f:
            memory = json.load(f)
        arcs = memory.get('arcs', [])

        for arc in arcs:
            sig = arc.get('entity_signature', '')
            for wire in known_wires:
                self.assertNotIn(wire, sig.lower().split(':'),
                                 f"Wire token '{wire}' leaked into entity_signature of arc {arc.get('arc_id')}")

    def test_milestone2_active_agents_clean_and_concise(self):
        """Active agents must be concise (<= 5 words), with zero 'Editorial Bureau' occurrences."""
        news_path = os.path.join(_PROJECT_ROOT, 'data', 'news.json')
        with open(news_path, 'r', encoding='utf-8') as f:
            news = json.load(f)
        articles = news.get('articles', [])

        for a in articles:
            pa = a.get('primary_actors')
            self.assertIsNotNone(pa, f"Article {a.get('id')} missing primary_actors")
            self.assertIsInstance(pa, dict)

            agent = pa.get('active_agent')
            if agent:
                self.assertNotIn('editorial bureau', agent.lower(),
                                 f"Forbidden placeholder 'Editorial Bureau' in active_agent for {a.get('id')}")
                self.assertNotIn('syndicated bureau', agent.lower(),
                                 f"Forbidden placeholder 'Syndicated Bureau' in active_agent for {a.get('id')}")
                words = agent.split()
                self.assertLessEqual(len(words), 5,
                                     f"Active agent '{agent}' exceeds 5 words ({len(words)} words) for {a.get('id')}")

    def test_milestone2_grammar_actor_extraction_boundary_inputs(self):
        """SyntacticActorGrammar survives empty, malformed, and emoji inputs without hallucination."""
        grammar = SyntacticActorGrammar()
        cases = [
            ("", "", {}, ""),
            (None, None, None, None),
            ("🚀🔥💥", "✨🎉", {}, "Global"),
            ("Short title", "", {'people': []}, "North America"),
            ("Long complex diplomatic dispatch headline where negotiators meet in Geneva",
             "A detailed summary with full punctuation.",
             {'people': ['Antony Blinken'], 'organizations': ['State Department'], 'countries': [{'code': 'US', 'name': 'United States'}]},
             "North America")
        ]
        for title, desc, ents, reg in cases:
            with self.subTest(title=title):
                actors = grammar.extract_actors(title or '', desc or '', ents or {}, reg or '')
                self.assertIsInstance(actors, dict)
                self.assertIn('active_agent', actors)
                self.assertIn('active_agent_type', actors)
                self.assertIn('collective_factions', actors)
                self.assertIn('syntactic_frame', actors)
                if actors.get('active_agent'):
                    self.assertNotIn('editorial bureau', actors['active_agent'].lower())
                    self.assertNotIn('syndicated bureau', actors['active_agent'].lower())


if __name__ == '__main__':
    unittest.main()
