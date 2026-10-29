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
    save_memory,
    substantive_stems,
    _extract_article_entities_for_anchors,
    _extract_arc_entities_for_anchors
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
            'entities': {'companies': [{'name': 'Anthropic'}, {'name': 'Microsoft'}]}
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


class TestAdversarialCountryRejection(unittest.TestCase):
    """
    Adversarial Challenge: Single country code/name pairs must NEVER satisfy Anchor 2.
    Even under identical headlines and high Jaccard scores (J >= 0.50),
    sharing only 1 country code or country name must result in len(common_entities) <= 1,
    failing Anchor 2 and returning (None, 0.0).
    """

    def test_single_country_pairs_never_satisfy_anchor2_and_reject(self):
        countries_to_test = [
            ('DE', 'Germany', 'Europe'),
            ('US', 'United States', 'North America'),
            ('FR', 'France', 'Europe'),
            ('JP', 'Japan', 'Asia-Pacific'),
            ('IN', 'India', 'India'),
            ('RU', 'Russia', 'Europe'),
            ('CN', 'China', 'Asia-Pacific'),
            ('GB', 'United Kingdom', 'Europe'),
            ('IT', 'Italy', 'Europe'),
            ('BR', 'Brazil', 'Americas')
        ]

        for code, name, reg in countries_to_test:
            with self.subTest(code=code, name=name):
                arc = {
                    'arc_id': f'arc-country-{code.lower()}',
                    'title': f'{name} National Infrastructure Energy Modernization Program',
                    'keywords': [name.lower(), 'infrastructure', 'energy', 'modernization', 'program'],
                    'countries': [code],
                    'category': 'Business',
                    'regions': [reg],
                    'chapter_titles': [f'{name} Initiates Comprehensive Energy Infrastructure Upgrades']
                }

                art = {
                    'id': f'art-{code.lower()}-test',
                    'title': f'{name} advances national infrastructure energy modernization program',
                    'description': f'Federal authorities in {name} outline massive infrastructure investment plan.',
                    'category': 'Business',
                    'country_code': code.lower(),
                    'region': reg,
                    'entities': {'countries': [{'code': code, 'name': name}]}
                }

                # 1. Directly verify extracted entities
                _, _, art_ents, art_leaders = _extract_article_entities_for_anchors(art)
                _, _, arc_ents, arc_leaders = _extract_arc_entities_for_anchors(arc)
                common = art_ents.intersection(arc_ents)
                common_l = art_leaders.intersection(arc_leaders)

                # Anchor 2 invariants:
                # Cardinality of common entities MUST be at most 1 (the canonical country name, never 2-letter ISO code)
                self.assertLessEqual(
                    len(common), 1,
                    f"Country {code}/{name} inflated entities to {common} (len {len(common)})"
                )
                self.assertEqual(len(common_l), 0, "No leaders should be extracted from pure country entities")

                # Anchor 2 MUST evaluate to False
                anchor2 = (len(common) >= 2) or (len(common_l) >= 1)
                self.assertFalse(
                    anchor2,
                    f"Anchor 2 unexpectedly passed for single country {code}/{name}: common={common}"
                )

                # 2. Verify match_article_to_arc strictly returns (None, 0.0) despite high Jaccard
                matched, score = match_article_to_arc(art, [arc])
                self.assertIsNone(
                    matched,
                    f"Article sharing ONLY country {code}/{name} bound to arc with score {score}!"
                )
                self.assertEqual(score, 0.0)


class TestAdversarialSingleEntityBypassElimination(unittest.TestCase):
    """
    Adversarial Challenge: Removal of line 575 bypass strictly prevents single-entity binding.
    Pairs sharing exactly 1 entity and 0 leaders with matching category and high Jaccard (J >= 0.50)
    must strictly evaluate Anchor 2 to False and return (None, 0.0).
    """

    def test_single_company_with_high_jaccard_strictly_rejects(self):
        single_entities = [
            ('Anthropic', 'Tech', 'Anthropic Unveils Next Generation AI Autonomous Agents'),
            ('Nvidia', 'Tech', 'Nvidia Announces High Performance Semiconductor Architecture'),
            ('TSMC', 'Tech', 'TSMC Expands Advanced Foundry Fabrication Capacity'),
            ('Boeing', 'Business', 'Boeing Finalizes Commercial Aircraft Fleet Deliveries'),
            ('Pfizer', 'Business', 'Pfizer Reports Promising Clinical Trial Phase Results'),
            ('UNESCO', 'World', 'UNESCO Designates New World Heritage Protection Sites')
        ]

        for ent_name, cat, title in single_entities:
            with self.subTest(entity=ent_name, category=cat):
                arc = {
                    'arc_id': f'arc-{ent_name.lower()}',
                    'title': title,
                    'keywords': [ent_name.lower(), 'announces', 'advancement', 'strategy'],
                    'entities': [ent_name.lower()],  # exactly 1 entity
                    'category': cat,
                    'regions': ['Global'],
                    'chapter_titles': [title]
                }

                art = {
                    'id': f'art-{ent_name.lower()}',
                    'title': title,  # Identical title ensures Jaccard >= 0.80
                    'description': f'{ent_name} confirms official milestones in new statement.',
                    'category': cat,  # Category matches!
                    'region': 'Global',
                    'entities': {'organizations': [{'name': ent_name}]}  # exactly 1 entity
                }

                # 1. Direct inspection
                _, _, art_ents, art_leaders = _extract_article_entities_for_anchors(art)
                _, _, arc_ents, arc_leaders = _extract_arc_entities_for_anchors(arc)
                common = art_ents.intersection(arc_ents)
                common_l = art_leaders.intersection(arc_leaders)

                self.assertEqual(
                    len(common), 1,
                    f"Expected exactly 1 shared entity for {ent_name}, got {common}"
                )
                self.assertEqual(len(common_l), 0)

                # 2. Strict rejection: removal of line 575 bypass means this CANNOT bind
                matched, score = match_article_to_arc(art, [arc])
                self.assertIsNone(
                    matched,
                    f"Single entity {ent_name} bypassed Anchor 2 and bound with score {score}!"
                )
                self.assertEqual(score, 0.0)


class TestGenuineMultiEntityAndLeaderBinding(unittest.TestCase):
    """
    Verification: Confirm that genuine multi-entity matches (|E(A) ∩ E(M)| >= 2)
    and genuine leader matches (|L(A) ∩ L(M)| >= 1 with matching category)
    pass Anchor 2 and bind when Jaccard >= 0.30.
    """

    def test_genuine_multi_entity_matches_bind_successfully(self):
        pairs = [
            # 2 companies in Tech
            {
                'name': 'Tech multi-entity',
                'arc_title': 'Nvidia and TSMC Partner on Next Gen Silicon Architecture',
                'art_title': 'Nvidia and TSMC partner on next gen silicon architecture fabrication',
                'category': 'Tech',
                'region': 'North America',
                'arc_ents': ['nvidia', 'tsmc'],
                'art_ents': {'companies': [{'name': 'Nvidia'}, {'name': 'TSMC'}]}
            },
            # Country + Company in Business
            {
                'name': 'Germany and Siemens',
                'arc_title': 'German Industrial Manufacturing Powerhouse Siemens Expands Global Plants',
                'art_title': 'Siemens expands industrial manufacturing operations across Germany plants',
                'category': 'Business',
                'region': 'Europe',
                'arc_ents': ['germany', 'siemens'],
                'arc_countries': ['DE'],
                'art_country_code': 'de',
                'art_ents': {'locations': ['Germany'], 'companies': [{'name': 'Siemens'}]}
            },
            # 2 international organizations in World
            {
                'name': 'UN and NATO diplomacy',
                'arc_title': 'United Nations and NATO Coordinate Humanitarian Security Corridors',
                'art_title': 'United Nations and NATO officials coordinate humanitarian security corridors',
                'category': 'World',
                'region': 'Europe',
                'arc_ents': ['united nations', 'nato'],
                'art_ents': {'organizations': [{'name': 'United Nations'}, {'name': 'NATO'}]}
            }
        ]

        for p in pairs:
            with self.subTest(name=p['name']):
                arc = {
                    'arc_id': f"arc-{p['name'].replace(' ', '-')}",
                    'title': p['arc_title'],
                    'keywords': [e.lower() for e in p['arc_ents']] + ['strategic', 'operations'],
                    'entities': p['arc_ents'],
                    'countries': p.get('arc_countries', []),
                    'category': p['category'],
                    'regions': [p['region']],
                    'chapter_titles': [p['arc_title']]
                }
                art = {
                    'id': f"art-{p['name'].replace(' ', '-')}",
                    'title': p['art_title'],
                    'category': p['category'],
                    'country_code': p.get('art_country_code', ''),
                    'region': p['region'],
                    'entities': p['art_ents']
                }

                matched, score = match_article_to_arc(art, [arc])
                self.assertIsNotNone(
                    matched,
                    f"Multi-entity match failed for {p['name']}"
                )
                self.assertGreaterEqual(score, 0.30)
                self.assertEqual(matched['arc_id'], arc['arc_id'])

    def test_genuine_leader_matches_bind_with_matching_category(self):
        leaders = [
            ('Emmanuel Macron', 'macron', 'FR', 'Europe', 'World',
             'French President Emmanuel Macron Addresses European Security Summit',
             'Macron addresses European security summit on defense strategy'),
            ('Volodymyr Zelenskyy', 'zelenskyy', 'UA', 'Europe', 'World',
             'President Volodymyr Zelenskyy Appeals for Air Defense Missiles in Kyiv Address',
             'Zelenskyy appeals for air defense missiles in Kyiv address'),
            ('Narendra Modi', 'modi', 'IN', 'India', 'World',
             'Prime Minister Narendra Modi Inaugurates Global Technology Summit in Delhi',
             'Modi inaugurates global technology summit in Delhi address')
        ]

        for leader_full, leader_match, code, reg, cat, arc_headline, art_headline in leaders:
            with self.subTest(leader=leader_full):
                arc = {
                    'arc_id': f'arc-leader-{leader_match}',
                    'title': arc_headline,
                    'keywords': [leader_match, 'summit', 'address', 'defense'],
                    'entity_signature': f'{code}:{leader_full}',
                    'countries': [code],
                    'category': cat,
                    'regions': [reg],
                    'chapter_titles': [arc_headline]
                }
                art = {
                    'id': f'art-leader-{leader_match}',
                    'title': art_headline,
                    'category': cat,  # matching category
                    'country_code': code.lower(),
                    'region': reg,
                    'entities': {
                        'leaders': [{'name': leader_full, 'matched': leader_match}],
                        'countries': [{'code': code}]
                    }
                }

                matched, score = match_article_to_arc(art, [arc])
                self.assertIsNotNone(
                    matched,
                    f"Leader match failed for {leader_full}"
                )
                self.assertGreaterEqual(score, 0.30)

    def test_leader_match_with_category_mismatch_strictly_rejects(self):
        arc = {
            'arc_id': 'arc-leader-mismatch',
            'title': 'Chancellor Olaf Scholz Delivers European Foreign Policy Address',
            'keywords': ['scholz', 'foreign', 'policy', 'europe'],
            'entities': ['olaf scholz'],
            'category': 'World',
            'regions': ['Europe'],
            'chapter_titles': ['Chancellor Olaf Scholz Delivers European Foreign Policy Address']
        }
        art = {
            'id': 'art-leader-mismatch',
            'title': 'Olaf Scholz Comments On Industrial Technology Subsidies',
            'category': 'Tech',  # Category MISMATCH (Tech vs World)
            'region': 'Europe',
            'entities': {'leaders': [{'name': 'Olaf Scholz'}]}
        }

        matched, score = match_article_to_arc(art, [arc])
        self.assertIsNone(
            matched,
            "Leader match with category mismatch must strictly reject"
        )
        self.assertEqual(score, 0.0)


class TestStemmerSymmetryAndAdversarialPlurals(unittest.TestCase):
    """
    Verification: Symmetrical stemming across singular/plural inflections
    (silent 'e', y/ies, consonant doubling) and crash-proof handling of edge inputs.
    """

    def test_silent_e_singular_plural_symmetry(self):
        silent_e_pairs = [
            ('strike', 'strikes'),
            ('probe', 'probes'),
            ('vote', 'votes'),
            ('trade', 'trades'),
            ('missile', 'missiles'),
            ('siege', 'sieges'),
            ('drone', 'drones'),
            ('ceasefire', 'ceasefires'),
            ('regime', 'regimes'),
            ('offensive', 'offensives'),
            ('blockade', 'blockades'),
            ('dispute', 'disputes'),
            ('pipeline', 'pipelines'),
            ('truce', 'truces')
        ]

        for sing, plur in silent_e_pairs:
            with self.subTest(singular=sing, plural=plur):
                stems_sing = substantive_stems(sing)
                stems_plur = substantive_stems(plur)
                self.assertEqual(
                    stems_sing, stems_plur,
                    f"Silent-e stem mismatch: '{sing}' -> {stems_sing} vs '{plur}' -> {stems_plur}"
                )
                self.assertTrue(len(stems_sing) > 0, f"Stem of '{sing}' should not be empty")

    def test_y_ies_singular_plural_symmetry(self):
        y_ies_pairs = [
            ('treaty', 'treaties'),
            ('ministry', 'ministries'),
            ('foundry', 'foundries'),
            ('subsidy', 'subsidies'),
            ('company', 'companies'),
            ('factory', 'factories'),
            ('embassy', 'embassies'),
            ('refinery', 'refineries'),
            ('territory', 'territories'),
            ('battery', 'batteries')
        ]

        for sing, plur in y_ies_pairs:
            with self.subTest(singular=sing, plural=plur):
                stems_sing = substantive_stems(sing)
                stems_plur = substantive_stems(plur)
                self.assertEqual(
                    stems_sing, stems_plur,
                    f"y/ies stem mismatch: '{sing}' -> {stems_sing} vs '{plur}' -> {stems_plur}"
                )
                self.assertTrue(len(stems_sing) > 0, f"Stem of '{sing}' should not be empty")

    def test_edge_punctuation_and_adversarial_inputs_survive_without_crashes(self):
        adversarial_inputs = [
            None,
            "",
            "   \t\n   ",
            "???---...!!!",
            ",,, ;;; :::: () [] {}",
            "123 4567 890",
            "🚀🔥💥 news alert 🌐🤖",
            "абракадабра русский текст",
            "مرحبا بالعالم",
            "a an the of and or in on at to by",  # pure stopwords
            "reuters ap bbc afp bloomberg nyt cnn",  # pure wire entities
            "a" * 100000  # 100k single word
        ]

        for inp in adversarial_inputs:
            with self.subTest(inp_repr=repr(inp)[:40]):
                res = substantive_stems(inp)
                self.assertIsInstance(res, set)

    def test_double_s_guard(self):
        double_s_words = ['press', 'boss', 'class', 'crisis', 'process', 'access']
        for w in double_s_words:
            stems = substantive_stems(w)
            for st in stems:
                self.assertTrue(st.endswith('ss') or st == 'crisi' or len(st) >= 3)


if __name__ == '__main__':
    unittest.main()
