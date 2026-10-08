#!/usr/bin/env python3
"""
Empirical Challenger Stress Test Suite - Milestone 3 Iteration 2
Author: challenger_m3_iter2_1 (Empirical Challenger)
Target: scripts/intelligence/memory.py, scripts/intelligence/intake.py

Adversarially challenges:
1. scripts/intelligence/memory.py:
   - Extreme null, falsy, malformed inputs to match_article_to_arc
   - Extreme null, missing fields, corrupted timestamps to update_memory
   - Extreme nulls, boundary sorting in prune_stale_arcs and get_active_arcs
   - File corruption resilience in load_memory and save_memory
2. scripts/intelligence/intake.py:
   - Entity token extraction without token inflation or taxonomy leakage
   - Strict category, entity overlap ratio (>=0.8) and count (>=2) bounds
   - Title Jaccard vs entity overlap edge conditions
   - Canonical selection hierarchy under degenerate / null attributes
   - Large-scale intake consistency: input == noise + dups + output invariant
"""

import os
import sys
import unittest
import tempfile
import json
from datetime import datetime, timezone, timedelta

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR = os.path.join(PROJECT_ROOT, 'scripts')

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

from intelligence.memory import (
    _flatten_entities,
    _parse_iso,
    match_article_to_arc,
    update_memory,
    prune_stale_arcs,
    get_active_arcs,
    load_memory,
    save_memory
)
from intelligence.intake import (
    run_intake,
    enhanced_dedup,
    get_all_entities_set,
    normalize_title,
    jaccard_similarity,
    filter_noise
)


class TestMemoryNullGuardsAndEdgeCases(unittest.TestCase):
    """Adversarial stress tests for null resilience and boundary logic in memory.py."""

    def test_match_article_to_arc_extreme_nulls_and_types(self):
        """Verify match_article_to_arc survives completely invalid inputs gracefully."""
        invalid_articles = [
            None, "", 123, [], False, True,
            {},
            {'title': None, 'category': None, 'entities': None},
            {'title': '   \n\t  ', 'category': '', 'entities': {}},
            {'title': None, 'category': 'Tech', 'entities': {'people': [None, 123, {'name': None}]}}
        ]
        invalid_arcs = [
            None, "", 123, {}, False, True,
            [],
            [None, 123, "not-a-dict", {}],
            [{'arc_id': 'empty-1'}],
            [{'arc_id': 'none-fields', 'keywords': None, 'entities': None, 'entity_signature': None, 'category': None}],
            [{'arc_id': 'bad-types', 'keywords': 123, 'entities': 456, 'entity_signature': 789, 'category': 999}],
            [{'arc_id': 'delim-only', 'keywords': [], 'entity_signature': '::::++++::::', 'entities': []}]
        ]

        for art in invalid_articles:
            for arcs in invalid_arcs:
                matched, score = match_article_to_arc(art, arcs)
                self.assertIsNone(matched, f"Expected None match for art={art!r}, arcs={arcs!r}")
                self.assertEqual(score, 0.0)

    def test_match_article_to_arc_threshold_boundaries(self):
        """Test threshold parameter boundaries (0.0, 1.0, negative, >1.0)."""
        arc = {
            'arc_id': 'arc-ai-agents',
            'title': 'Autonomous Software Agents Deployment',
            'keywords': ['agents', 'autonomous', 'software', 'deployment'],
            'entities': ['openai', 'anthropic', 'microsoft'],
            'category': 'Tech'
        }
        article = {
            'title': 'Anthropic Announces Autonomous Software Agents Deployment for Enterprise',
            'category': 'Tech',
            'entities': {'companies': [{'name': 'Anthropic'}]}
        }

        # With normal threshold
        matched, score = match_article_to_arc(article, [arc], threshold=0.4)
        self.assertIsNotNone(matched)
        self.assertGreaterEqual(score, 0.4)

        # With impossible threshold > 1.0
        matched_high, score_high = match_article_to_arc(article, [arc], threshold=1.5)
        self.assertIsNone(matched_high)
        self.assertEqual(score_high, 0.0)

        # With zero threshold
        matched_zero, score_zero = match_article_to_arc(article, [arc], threshold=0.0)
        self.assertIsNotNone(matched_zero)

    def test_update_memory_malformed_inputs_and_null_defense(self):
        """Verify update_memory functions safely when memory structure or articles are malformed."""
        # Null memory should be initialized to {"arcs": []}
        res1 = update_memory(None, [])
        self.assertIsInstance(res1, dict)
        self.assertIn("arcs", res1)

        res2 = update_memory({"arcs": None}, None)
        self.assertIsInstance(res2, dict)
        self.assertIsInstance(res2.get("arcs"), list)

        # Malformed existing arcs in memory
        memory_with_bad_arcs = {
            "arcs": [
                None,
                "not-a-dict",
                {},
                {
                    "arc_id": "arc-corrupt",
                    "chapter_count": None,
                    "chapter_titles": None,
                    "sources_involved": None,
                    "last_seen": None,
                    "keywords": None
                }
            ]
        }
        test_articles = [
            None,
            "not-an-article",
            {},
            {
                "title": None,
                "category": None,
                "entities": None,
                "source": None,
                "scores": None
            }
        ]
        updated = update_memory(memory_with_bad_arcs, test_articles)
        self.assertIsInstance(updated, dict)
        self.assertIsInstance(updated.get("arcs"), list)

    def test_update_memory_new_arc_creation_and_title_sanitization(self):
        """Verify new arc creation logic and title sanitization when article meets criteria."""
        now = datetime.now(timezone.utc).isoformat()
        memory = {"arcs": []}

        # Article with >= 3 entities and an action word in title
        long_title = "President signs comprehensive international maritime border security pact after tense multilateral summit negotiations"
        article = {
            'id': 'art-summit-01',
            'title': long_title,
            'category': 'World',
            'region': 'Asia-Pacific',
            'source': 'Reuters',
            'entities': {
                'entity_count': 4,
                'countries': [{'code': 'USA'}, {'code': 'JPN'}, {'code': 'PHL'}],
                'leaders': [{'name': 'Bongbong Marcos'}],
                'organizations': []
            },
            'scores': {'velocity': 3}
        }

        updated = update_memory(memory, [article])
        arcs = updated['arcs']
        self.assertEqual(len(arcs), 1)
        created_arc = arcs[0]

        # Check sanitization
        self.assertIsNotNone(created_arc.get('arc_id'))
        self.assertLessEqual(len(created_arc['title']), 50)
        self.assertFalse(created_arc['title'].endswith('...'))
        self.assertFalse(created_arc['title'].endswith('…'))
        self.assertEqual(created_arc['chapter_count'], 1)
        self.assertEqual(created_arc['importance_trend'], 'rising')
        self.assertEqual(article.get('_matched_arc_id'), created_arc['arc_id'])

    def test_prune_and_get_active_arcs_edge_cases(self):
        """Verify prune_stale_arcs and get_active_arcs withstand corrupt dates and cap at 100."""
        now = datetime.now(timezone.utc)

        # Create 150 arcs with various dates and None chapter counts
        arcs = []
        for i in range(150):
            days_ago = i % 30
            date_str = (now - timedelta(days=days_ago)).isoformat()
            # Interleave some corrupted dates
            if i % 15 == 0:
                date_str = None
            elif i % 15 == 1:
                date_str = "invalid-date-string"

            arcs.append({
                'arc_id': f"arc-{i}",
                'title': f"Arc Title {i}",
                'last_seen': date_str,
                'chapter_count': None if i % 5 == 0 else (i + 1)
            })

        mem = {'arcs': arcs}
        pruned = prune_stale_arcs(mem, max_age_days=14)
        self.assertLessEqual(len(pruned['arcs']), 100)

        # Active arcs (< 7 days)
        active = get_active_arcs(pruned)
        self.assertIsInstance(active, list)
        self.assertLessEqual(len(active), 100)
        # Verify sorting by chapter_count descending without crash
        for i in range(len(active) - 1):
            curr_cnt = active[i].get('chapter_count') or 0
            next_cnt = active[i + 1].get('chapter_count') or 0
            self.assertGreaterEqual(curr_cnt, next_cnt)

    def test_load_and_save_memory_corrupted_files(self):
        """Test load_memory resilience against corrupt files and save_memory round-trip."""
        with tempfile.TemporaryDirectory() as tmpdir:
            corrupt_file = os.path.join(tmpdir, "corrupt_memory.json")
            
            # Non-existent file
            res = load_memory(os.path.join(tmpdir, "non_existent.json"))
            self.assertEqual(res['arcs'], [])
            self.assertEqual(res['version'], 2)

            # Corrupt JSON file
            with open(corrupt_file, 'w', encoding='utf-8') as f:
                f.write("{ invalid json content ...")
            res_corrupt = load_memory(corrupt_file)
            self.assertEqual(res_corrupt['arcs'], [])

            # JSON array instead of dict
            with open(corrupt_file, 'w', encoding='utf-8') as f:
                f.write("[]")
            res_arr = load_memory(corrupt_file)
            self.assertEqual(res_arr['arcs'], [])

            # Valid save and load round-trip
            test_mem = {
                "arcs": [{"arc_id": "arc-1", "title": "Test Arc"}],
                "version": 2
            }
            valid_file = os.path.join(tmpdir, "valid_memory.json")
            save_memory(test_mem, valid_file)
            loaded = load_memory(valid_file)
            self.assertEqual(len(loaded['arcs']), 1)
            self.assertEqual(loaded['arcs'][0]['arc_id'], "arc-1")
            self.assertIn("last_updated", loaded)


class TestIntakeDuplicateSuppressionPrecision(unittest.TestCase):
    """Adversarial stress tests for deduplication precision and boundary logic in intake.py."""

    def test_get_all_entities_set_malformed_and_token_inflation(self):
        """Verify token extraction handles malformed fields and prevents token inflation."""
        # Ignored metadata and taxonomy keys
        ignored_data = {
            'actions': ['technology', 'finance'],
            'domains': ['macroeconomics'],
            'entity_count': 42,
            'entity_density': 0.99,
            'count': 10,
            'density': 0.1
        }
        tokens = get_all_entities_set(ignored_data)
        self.assertEqual(tokens, set(), f"Ignored keys leaked: {tokens}")

        # Multi-attribute entity dict should produce exactly ONE canonical token
        single_entity = {
            'companies': [
                {'name': 'Apple Inc', 'code': 'AAPL', 'matched': 'Apple', 'text': 'Apple'}
            ]
        }
        tokens_single = get_all_entities_set(single_entity)
        self.assertEqual(len(tokens_single), 1, f"Token inflation detected! Expected 1 token, got {tokens_single}")
        self.assertEqual(tokens_single, {'apple inc'})

        # Malformed values
        malformed = {
            'people': [None, 123, '', {}, {'name': None}],
            'places': None
        }
        res = get_all_entities_set(malformed)
        self.assertIn('123', res)

    def test_enhanced_dedup_category_isolation(self):
        """
        Articles with identical entities but DIFFERENT categories must NEVER be deduplicated
        via entity overlap (only via title Jaccard if titles match).
        """
        art_world = {
            'id': 'art-world-01',
            'title': 'Diplomatic Envoys Convene in Paris for Bilateral Accord',
            'description': 'French and European delegates met at the Élysée Palace.',
            'category': 'World',
            'entities': {'locations': [{'name': 'Paris'}, {'name': 'France'}]}
        }
        art_business = {
            'id': 'art-business-01',
            'title': 'French Tech Startups Secure Record Capital Inflows in Paris',
            'description': 'Venture capital funds poured investment into French AI firms.',
            'category': 'Business',
            'entities': {'locations': [{'name': 'Paris'}, {'name': 'France'}]}
        }

        # Distinct titles, same 2 entities, different category
        res = enhanced_dedup([art_world, art_business])
        self.assertEqual(len(res), 2)
        for art in res:
            self.assertFalse(art.get('is_duplicate', False), f"Article {art['id']} falsely marked as duplicate")

    def test_enhanced_dedup_single_shared_entity_boundary(self):
        """
        Articles in the same category sharing only ONE entity must NOT be marked duplicate.
        The algorithm requires len(intersection) >= 2.
        """
        art_a = {
            'id': 'art-germany-01',
            'title': 'Germany Expands High Speed Rail Transit Corridors',
            'description': 'Federal transport ministry announces green infrastructure investments.',
            'category': 'National',
            'entities': {'locations': [{'name': 'Germany'}]}
        }
        art_b = {
            'id': 'art-germany-02',
            'title': 'Berlin Hosts International Modern Art Exhibition',
            'description': 'Artists from fifty nations display contemporary works in capital.',
            'category': 'National',
            'entities': {'locations': [{'name': 'Germany'}]}
        }

        res = enhanced_dedup([art_a, art_b])
        self.assertEqual(len(res), 2)
        for art in res:
            self.assertFalse(art.get('is_duplicate', False))

    def test_enhanced_dedup_empty_category_boundary(self):
        """Articles with empty category ('') must NOT trigger entity dedup."""
        art_a = {
            'id': 'art-nocat-01',
            'title': 'Report on Global Renewable Wind Energy Developments',
            'description': 'Offshore wind farms expand in the North Sea basin.',
            'category': '',
            'entities': {'locations': [{'name': 'North Sea'}, {'name': 'Denmark'}]}
        }
        art_b = {
            'id': 'art-nocat-02',
            'title': 'Maritime Conservation Initiatives in North Sea Waters',
            'description': 'Biologists monitor marine sanctuaries off the Danish coast.',
            'category': '',
            'entities': {'locations': [{'name': 'North Sea'}, {'name': 'Denmark'}]}
        }

        res = enhanced_dedup([art_a, art_b])
        self.assertEqual(len(res), 2)
        for art in res:
            self.assertFalse(art.get('is_duplicate', False))

    def test_enhanced_dedup_true_duplicate_on_entities(self):
        """
        Articles with same category, >= 2 shared entities, and overlap ratio >= 0.8
        MUST trigger duplicate suppression.
        """
        art_reuters = {
            'id': 'art-reuters-merger',
            'title': 'Qualcomm Agrees to Acquire Autotalks in Automotive V2X Expansion',
            'description': 'Qualcomm Inc announced an agreement to purchase vehicle chipmaker Autotalks.',
            'category': 'Tech',
            'entities': {'companies': [{'name': 'Qualcomm'}, {'name': 'Autotalks'}]}
        }
        art_bloomberg = {
            'id': 'art-bloomberg-merger',
            'title': 'Chipmaker Qualcomm Finalizes Purchase of Connected Car Specialist Autotalks',
            'description': 'San Diego based Qualcomm has reached a deal to acquire Israeli chip firm Autotalks.',
            'category': 'Tech',
            'entities': {'companies': [{'name': 'Qualcomm'}, {'name': 'Autotalks'}]}
        }

        res = enhanced_dedup([art_reuters, art_bloomberg])
        self.assertEqual(len(res), 2)
        duplicates = [a for a in res if a.get('is_duplicate')]
        canonicals = [a for a in res if not a.get('is_duplicate')]
        self.assertEqual(len(duplicates), 1)
        self.assertEqual(len(canonicals), 1)

    def test_run_intake_full_pipeline_scale_and_invariants(self):
        """
        Large scale intake stress test:
        - 10 duplicate clusters of 5 articles each (= 50 duplicate items, 10 canonicals expected)
        - 20 distinct valid articles
        - 10 noise articles (listicles, clickbait)
        Total input: 80 articles.
        Verify:
        - Noise rejected == 10
        - Duplicates suppressed == 40
        - Output count == 30 (10 canonicals + 20 distinct)
        - Invariant: input_count == noise_rejected + duplicates_suppressed + output_count
        - Zero is_duplicate articles in output
        """
        articles = []

        # 1. 10 duplicate clusters
        for c in range(10):
            base_title = f"Syndicated Wire Story Regarding Major Global Event Number {c}"
            for rep in range(5):
                articles.append({
                    'id': f"cluster-{c}-rep-{rep}",
                    'title': f"{base_title} - Wire Source {rep}",
                    'description': f"Detailed reporting on global event {c} variant {rep}.",
                    'category': 'World',
                    'source': f"WireAgency_{rep}",
                    'imageUrl': f"https://cdn.example.com/photo_{c}.jpg",
                    'entities': {'events': [f"Event_{c}"]}
                })

        # 2. 20 distinct valid articles
        for d in range(20):
            articles.append({
                'id': f"distinct-story-{d}",
                'title': f"Unique Investigative Report On Subject {d} In Depth",
                'description': f"Comprehensive journalistic analysis covering subject {d}.",
                'category': 'Tech' if d % 2 == 0 else 'Business',
                'source': f"Investigative_{d}",
                'imageUrl': f"https://example.com/unique_{d}.jpg",
                'entities': {'topics': [f"Subject_{d}"]}
            })

        # 3. 10 noise articles
        noise_titles = [
            "10 things you need to know before buying groceries",
            "Best deals and discounts for holiday shopping guide",
            "Horoscope for today: what the stars say about your sign",
            "Crossword and sudoku puzzle solutions for Tuesday",
            "Best cooking tips and secret pasta recipes",
            "Reality TV drama unfolds in shocking new episode",
            "Watch live: photo gallery of red carpet celebrity arrivals",
            "Viral video of cute animal doing hilarious tricks",
            "Daily weather forecast and local pollen count",
            "Take our personality quiz to find your ideal career"
        ]
        for n, ntitle in enumerate(noise_titles):
            articles.append({
                'id': f"noise-article-{n}",
                'title': ntitle,
                'description': "Click here to read the full fun piece online.",
                'category': 'General',
                'source': "ClickbaitDaily"
            })

        self.assertEqual(len(articles), 80)

        final_articles, stats = run_intake(articles)

        # Invariant checks
        self.assertEqual(stats['input_count'], 80)
        self.assertEqual(stats['noise_rejected'], 10)
        self.assertEqual(stats['duplicates_suppressed'], 40)
        self.assertEqual(stats['output_count'], 30)
        self.assertEqual(
            stats['input_count'],
            stats['noise_rejected'] + stats['duplicates_suppressed'] + stats['output_count']
        )
        self.assertEqual(len(final_articles), 30)
        for art in final_articles:
            self.assertFalse(art.get('is_duplicate', False))


if __name__ == '__main__':
    unittest.main()
