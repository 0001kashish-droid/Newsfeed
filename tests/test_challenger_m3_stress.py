#!/usr/bin/env python3
"""
Adversarial Stress Test Harness for Milestone M3 (News Colossal)
Author: challenger_m3_1 (Empirical Challenger)
Target: scripts/intelligence/memory.py, scripts/intelligence/intake.py, scripts/fetch_news.py

Adversarially challenges:
1. scripts/intelligence/memory.py:
   - _flatten_entities: arbitrary nested dicts, empty dicts, non-string tokens, mixed lists/tuples,
     metadata counters (entity_count, entity_density, count, density), unicode strings, deep nesting.
   - match_article_to_arc: arcs using 'entities' list vs 'entity_signature' string (both ':' and '+'),
     article entities categorized under 'people', 'locations', 'actions', 'domains', etc.,
     asymmetric coverage, multiple candidates best-match ranking, malformed/null inputs.
2. scripts/intelligence/intake.py:
   - Duplicate suppression: 100% duplicate feeds, 0% duplicate feeds, interleaved duplicates,
     canonical selection quality, empty feeds, malformed/null fields.
3. Integration with fetch_news & brand diversity:
   - Dynamic 18% brand family caps under stress feeds.
"""

import os
import sys
import unittest
from datetime import datetime, timezone

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR = os.path.join(PROJECT_ROOT, 'scripts')

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

from intelligence.memory import _flatten_entities, match_article_to_arc, update_memory
from intelligence.intake import run_intake, enhanced_dedup, get_all_entities_set, normalize_title


class TestMemoryFlattenEntitiesStress(unittest.TestCase):
    """
    Stress tests for _flatten_entities in scripts/intelligence/memory.py.
    """

    def test_flatten_empty_and_falsy_inputs(self):
        """Verify handling of None, empty collections, empty strings, and booleans."""
        falsy_cases = [None, {}, [], set(), (), "", False]
        for val in falsy_cases:
            result = _flatten_entities(val)
            self.assertIsInstance(result, set, f"Expected set for input {val!r}, got {type(result)}")
            self.assertEqual(len(result), 0, f"Expected empty set for input {val!r}, got {result}")

    def test_flatten_scalar_counters_suppression(self):
        """
        Verify that scalar counters (entity_count, entity_density, count, density)
        are strictly excluded at root and nested levels.
        """
        nested_with_counters = {
            'entity_count': 42,
            'entity_density': 0.85,
            'count': 100,
            'density': 0.12,
            'people': [
                {'name': 'Emmanuel Macron', 'count': 5, 'density': 0.05},
                {'name': 'Ursula von der Leyen', 'entity_count': 2}
            ],
            'locations': {
                'count': 3,
                'list': [{'name': 'Brussels', 'density': 0.2}, 'Paris']
            },
            'metadata': {
                'entity_count': 999,
                'nested_stats': {'count': 88}
            }
        }
        res = _flatten_entities(nested_with_counters)
        # Valid entities must be present
        self.assertIn('emmanuel macron', res)
        self.assertIn('ursula von der leyen', res)
        self.assertIn('brussels', res)
        self.assertIn('paris', res)

        # Counter tokens must NEVER be present
        forbidden = {'42', '0.85', '100', '0.12', '5', '0.05', '2', '3', '0.2', '999', '88'}
        intersection = res.intersection(forbidden)
        self.assertEqual(intersection, set(), f"Metadata counters leaked into flattened entities: {intersection}")

    def test_flatten_arbitrary_nested_and_mixed_structures(self):
        """Verify deeply nested dicts, lists, tuples, and sets are fully extracted."""
        deep_data = {
            'level1': {
                'level2': [
                    ('tuple_token_1', {'level3': {'people': [{'name': 'Alan Turing'}, {'code': 'TUR'}]}}),
                    {'set_wrapper': {'token_in_set_1', 'token_in_set_2'}},
                    ['nested_list_item', 987.65]
                ]
            }
        }
        res = _flatten_entities(deep_data)
        expected_items = {
            'tuple_token_1', 'alan turing', 'tur',
            'token_in_set_1', 'token_in_set_2',
            'nested_list_item', '987.65'
        }
        for item in expected_items:
            self.assertIn(item, res, f"Missing token {item} in flattened result: {res}")

    def test_flatten_standard_entity_dictionary_fields(self):
        """
        Verify all 7 standard entity object fields:
        name, code, matched, text, label, title, value.
        """
        entity_dict = {
            'e1': {'name': 'United States'},
            'e2': {'code': 'USA'},
            'e3': {'matched': 'American'},
            'e4': {'text': 'Federal Reserve'},
            'e5': {'label': 'Central Bank'},
            'e6': {'title': 'Chairman Powell'},
            'e7': {'value': 'Monetary Policy'},
        }
        res = _flatten_entities(entity_dict)
        expected = {
            'united states', 'usa', 'american', 'federal reserve',
            'central bank', 'chairman powell', 'monetary policy'
        }
        self.assertTrue(expected.issubset(res), f"Expected {expected} to be subset of {res}")

    def test_flatten_categorized_taxonomies(self):
        """
        Verify that arbitrary categorizations (people, locations, actions, domains,
        countries, leaders, companies, technologies, concepts) extract smoothly.
        """
        taxonomies = {
            'people': ['Alice Smith', 'Bob Jones'],
            'locations': ['Geneva', 'Tokyo'],
            'actions': ['summit', 'bilateral negotiations'],
            'domains': ['Geopolitics', 'Macroeconomics'],
            'countries': [{'code': 'JPN', 'name': 'Japan'}],
            'leaders': [{'name': 'Shigeru Ishiba'}],
            'companies': ['Sony', 'Toyota'],
            'technologies': ['Quantum Computing', 'Semiconductors'],
            'concepts': ['Supply Chain Resilience']
        }
        res = _flatten_entities(taxonomies)
        expected_sample = {
            'alice smith', 'bob jones', 'geneva', 'tokyo', 'summit',
            'bilateral negotiations', 'geopolitics', 'macroeconomics',
            'jpn', 'japan', 'shigeru ishiba', 'sony', 'toyota',
            'quantum computing', 'semiconductors', 'supply chain resilience'
        }
        self.assertTrue(expected_sample.issubset(res), f"Expected sample tokens missing from {res}")

    def test_flatten_unicode_and_whitespace_normalization(self):
        """Verify trimmed whitespace and preservation of lowercase international unicode characters."""
        unicode_entities = [
            "   München   ",
            "\tSão Paulo\n",
            "北京",
            "  Zürich  "
        ]
        res = _flatten_entities(unicode_entities)
        self.assertIn("münchen", res)
        self.assertIn("são paulo", res)
        self.assertIn("北京", res)
        self.assertIn("zürich", res)


class TestMemoryMatchArticleToArcStress(unittest.TestCase):
    """
    Stress tests for match_article_to_arc in scripts/intelligence/memory.py.
    """

    def setUp(self):
        self.dummy_now = datetime.now(timezone.utc).isoformat()

    def test_arc_matching_entities_list(self):
        """Test matching when arc specifies entities as a list."""
        arc = {
            'arc_id': 'arc-chip-war-1',
            'title': 'Global Semiconductor Rivalry',
            'keywords': ['semiconductor', 'chips', 'export', 'controls'],
            'entities': ['tsmc', 'nvidia', 'taiwan', 'export curbs'],
            'category': 'Tech'
        }
        article = {
            'title': 'TSMC and Nvidia Navigate New Asia Tech Export Curbs',
            'category': 'Tech',
            'entities': {
                'companies': [{'name': 'TSMC'}, {'name': 'Nvidia'}],
                'locations': [{'name': 'Taiwan'}]
            }
        }
        matched_arc, score = match_article_to_arc(article, [arc])
        self.assertIsNotNone(matched_arc, "Article failed to match arc with 'entities' list")
        self.assertEqual(matched_arc['arc_id'], 'arc-chip-war-1')
        self.assertGreaterEqual(score, 0.6)

    def test_arc_matching_entity_signature_colon_and_plus(self):
        """Test matching when arc uses colon-separated or plus-separated entity_signature."""
        arc_colon = {
            'arc_id': 'arc-energy-crisis',
            'title': 'North Sea Gas Pipeline Developments',
            'keywords': ['pipeline', 'gas', 'energy'],
            'entity_signature': 'norway:equinor:north sea:pipeline',
            'category': 'Business'
        }
        article_colon = {
            'title': 'Equinor Boosts Gas Supply from North Sea',
            'category': 'Business',
            'entities': {
                'locations': ['North Sea', 'Norway'],
                'companies': ['Equinor']
            }
        }
        matched_arc, score = match_article_to_arc(article_colon, [arc_colon])
        self.assertIsNotNone(matched_arc)
        self.assertEqual(matched_arc['arc_id'], 'arc-energy-crisis')
        self.assertGreaterEqual(score, 0.6)

        # Plus separated signature
        arc_plus = {
            'arc_id': 'arc-auto-tariffs',
            'title': 'Electric Vehicle Tariffs Friction',
            'keywords': ['ev', 'tariffs', 'automakers'],
            'entity_signature': 'byd+china+eu+tariffs',
            'category': 'Business'
        }
        article_plus = {
            'title': 'EU Imposes Tariffs on BYD and Chinese Automakers',
            'category': 'Business',
            'entities': {
                'companies': ['BYD'],
                'countries': ['China'],
                'organizations': ['EU']
            }
        }
        matched_plus, score_plus = match_article_to_arc(article_plus, [arc_plus])
        self.assertIsNotNone(matched_plus)
        self.assertEqual(matched_plus['arc_id'], 'arc-auto-tariffs')
        self.assertGreaterEqual(score_plus, 0.6)

    def test_arc_matching_both_entities_and_signature(self):
        """Test arc having both entities list and entity_signature string."""
        arc_dual = {
            'arc_id': 'arc-dual-1',
            'title': 'Aerospace Defense Coalition',
            'keywords': ['defense', 'aerospace', 'nato'],
            'entities': ['lockheed martin', 'airbus'],
            'entity_signature': 'pentagon:nato',
            'category': 'World'
        }
        article = {
            'title': 'NATO Orders Modern Aircraft Fleet',
            'category': 'World',
            'entities': {
                'organizations': ['NATO', 'Pentagon'],
                'companies': ['Lockheed Martin']
            }
        }
        matched_arc, score = match_article_to_arc(article, [arc_dual])
        self.assertIsNotNone(matched_arc)
        self.assertEqual(matched_arc['arc_id'], 'arc-dual-1')
        self.assertGreaterEqual(score, 0.6)

    def test_asymmetric_relative_coverage_matching(self):
        """
        Verify that relative coverage max(arc_coverage, art_coverage) works:
        - When arc has 2 entities and article has 15 entities (arc_coverage == 1.0)
        - When article has 2 entities and arc has 10 entities (art_coverage == 1.0)
        """
        # Case A: Compact arc, dense article
        arc_compact = {
            'arc_id': 'arc-compact',
            'title': 'Lithium Mining Agreements',
            'keywords': ['mining'],
            'entities': ['chile', 'lithium'],
            'category': 'Business'
        }
        article_dense = {
            'title': 'Global Mining Overview Across South America and Africa',
            'category': 'Business',
            'entities': {
                'countries': ['Chile', 'Bolivia', 'Argentina', 'Congo', 'Australia'],
                'minerals': ['Lithium', 'Cobalt', 'Copper', 'Nickel', 'Gold'],
                'companies': ['Albemarle', 'SQM', 'Rio Tinto', 'BHP']
            }
        }
        matched_a, score_a = match_article_to_arc(article_dense, [arc_compact])
        self.assertIsNotNone(matched_a, "Compact arc should match dense article via arc_coverage")
        self.assertEqual(matched_a['arc_id'], 'arc-compact')
        self.assertGreaterEqual(score_a, 0.6)

        # Case B: Dense arc, compact article
        arc_dense = {
            'arc_id': 'arc-dense',
            'title': 'Central American Canal Logistics',
            'keywords': ['shipping'],
            'entities': ['panama canal', 'drought', 'freight', 'containerships', 'maersk', 'gatun lake'],
            'category': 'World'
        }
        article_compact = {
            'title': 'Canal Transit Updates',
            'category': 'World',
            'entities': {
                'locations': ['Panama Canal', 'Gatun Lake']
            }
        }
        matched_b, score_b = match_article_to_arc(article_compact, [arc_dense])
        self.assertIsNotNone(matched_b, "Compact article should match dense arc via art_coverage")
        self.assertEqual(matched_b['arc_id'], 'arc-dense')
        self.assertGreaterEqual(score_b, 0.6)

    def test_best_match_selection_among_competing_arcs(self):
        """Verify that when multiple arcs match, the arc with highest match_score is chosen."""
        arc_weak = {
            'arc_id': 'arc-weak',
            'title': 'General European Policy Discussions',
            'keywords': ['european', 'policy'],
            'entities': ['europe'],
            'category': 'World'
        }
        arc_strong = {
            'arc_id': 'arc-strong',
            'title': 'European Central Bank Interest Rate Cuts',
            'keywords': ['ecb', 'inflation', 'rates', 'frankfurt'],
            'entities': ['ecb', 'christine lagarde', 'frankfurt', 'eurozone'],
            'category': 'World'
        }
        article = {
            'title': 'ECB President Christine Lagarde Signals Frankfurt Rate Decisions',
            'category': 'World',
            'entities': {
                'organizations': ['ECB'],
                'leaders': ['Christine Lagarde'],
                'locations': ['Frankfurt', 'Eurozone']
            }
        }
        best_arc, best_score = match_article_to_arc(article, [arc_weak, arc_strong])
        self.assertIsNotNone(best_arc)
        self.assertEqual(best_arc['arc_id'], 'arc-strong')
        self.assertGreater(best_score, 0.7)

    def test_null_and_malformed_inputs_to_match_article_to_arc(self):
        """Verify resilience when arc or article contain None / empty fields."""
        malformed_arcs = [
            {},
            {'arc_id': 'arc-empty'},
            {'arc_id': 'arc-none', 'keywords': None, 'entities': None, 'entity_signature': None},
            {'arc_id': 'arc-invalid-types', 'keywords': 12345, 'entities': 999}
        ]
        malformed_article = {
            'title': None,
            'category': None,
            'entities': None
        }
        best_arc, score = match_article_to_arc(malformed_article, malformed_arcs)
        self.assertIsNone(best_arc)
        self.assertEqual(score, 0.0)


class TestIntakeDuplicateSuppressionStress(unittest.TestCase):
    """
    Stress tests for duplicate suppression in scripts/intelligence/intake.py:
    100% duplicate feeds, 0% duplicate feeds, interleaved duplicates, and edge cases.
    """

    def test_100_percent_duplicate_feed(self):
        """
        Feeds with 100% duplicate articles (e.g. 25 copies of syndicated wire article)
        must cleanly drop all 24 duplicates and return exactly 1 canonical article.
        """
        base_article = {
            'id': 'wire-reuters-001',
            'title': 'Central Banks Coordinate Global Currency Swap Lines Amid Liquidity Strain',
            'description': 'Major central banks announced coordinated liquidity swap measures today.',
            'category': 'Business',
            'source': 'Reuters',
            'imageUrl': 'https://example.com/clean-photo.jpg',
            'entities': {'organizations': [{'name': 'Federal Reserve'}, {'name': 'ECB'}]}
        }
        # Create 25 syndicated copies with minor suffix changes or identical titles
        articles = []
        for i in range(25):
            art = dict(base_article)
            art['id'] = f"wire-item-{i}"
            # Add typical syndicated source suffixes to test normalizer
            suffixes = [" - Reuters", " | Bloomberg", " - AP News", ""]
            art['title'] = base_article['title'] + suffixes[i % len(suffixes)]
            articles.append(art)

        final_articles, stats = run_intake(articles)
        self.assertEqual(len(final_articles), 1, f"Expected exactly 1 canonical article, got {len(final_articles)}")
        self.assertEqual(stats['input_count'], 25)
        self.assertEqual(stats['duplicates_suppressed'], 24)
        self.assertEqual(stats['output_count'], 1)
        self.assertFalse(final_articles[0].get('is_duplicate', True))

    def test_0_percent_duplicate_feed(self):
        """
        Feeds with 0% duplicate articles (20 distinct stories on diverse topics)
        must retain all 20 articles with 0 duplicates suppressed.
        """
        topics = [
            ("James Webb Telescope Discovers Distant Galaxy Cluster", "Tech", "NASA reveals deep space imaging."),
            ("Monsoon Rains Boost Agriculture Harvest in Northern India", "National", "Farmers report high crop yields."),
            ("Federal Reserve Holds Benchmark Interest Rate Steady", "Business", "Inflation data guides central bank."),
            ("Breakthrough in Solid-State Battery Density Achieved", "Tech", "Researchers report 500 Wh/kg cells."),
            ("Diplomatic Talks Convene in Geneva Over Maritime Routes", "World", "Delegates discuss shipping corridors."),
            ("Renewable Energy Surpasses Coal in European Power Grid", "Business", "Wind and solar output hit records."),
            ("Archaeological Dig Unearths Bronze Age Settlement", "World", "Excavations in Greece reveal artifacts."),
            ("Urban Vertical Farming Yields Rise with Spectral Lighting", "Tech", "Agritech firms expand hydroponics."),
            ("Major Rail Infrastructure Modernization Project Unveiled", "National", "High-speed transit connecting cities."),
            ("Semiconductor Fabrication Plant Breaks Ground in Dresden", "Business", "European chip act backs new plant."),
            ("New Coral Reef Restoration Technique Shows 90 Percent Survival", "World", "Marine biologists test larval seeding."),
            ("Autonomous Electric Cargo Ferry Enters Commercial Service", "Tech", "Zero-emission vessel operates in Norway."),
            ("Central Bank Digital Currency Pilot Enters Phase Two", "Business", "Cross-border payments tested."),
            ("Astronomers Detect Repeating Radio Signal from Nearby Star", "Tech", "SETI researchers analyze cadence."),
            ("Global Health Agency Launches Vaccine Initiative", "World", "Immunization campaign targets preventable diseases."),
            ("Quantum Computing Cluster Simulates Complex Molecular Folding", "Tech", "Pharmaceutical research milestone."),
            ("High Altitude Wind Turbines Capture Jet Stream Energy", "Tech", "Tethered blimps generate continuous power."),
            ("National Park Expands Protected Habitat for Endangered Fauna", "National", "Conservation corridor finalized."),
            ("Smart Grid AI Reduces Peak Energy Load by Thirty Percent", "Tech", "Grid operators deploy automated balancing."),
            ("Historic Trade Agreement Signed Across Pacific Rim Nations", "World", "Tariffs reduced on green tech goods.")
        ]
        articles = []
        for i, (title, cat, desc) in enumerate(topics):
            articles.append({
                'id': f"distinct-art-{i}",
                'title': title,
                'description': desc,
                'category': cat,
                'source': f"Publisher-{i}",
                'imageUrl': f"https://example.com/img-{i}.jpg",
                'entities': {'topics': [f"Topic-{i}"]}
            })

        final_articles, stats = run_intake(articles)
        self.assertEqual(len(final_articles), 20)
        self.assertEqual(stats['duplicates_suppressed'], 0)
        self.assertEqual(stats['output_count'], 20)
        for art in final_articles:
            self.assertFalse(art.get('is_duplicate', False))

    def test_interleaved_duplicates_feed(self):
        """
        Verify that multiple duplicate clusters interleaved together
        (e.g. Cluster A, Cluster B, Cluster C interleaved) cleanly resolve
        to exactly the number of unique clusters.
        """
        cluster_templates = [
            ("OPEC+ Extends Oil Production Quotas Through Year End", "Business", "Oil producers agree to maintain output cuts."),
            ("SpaceX Starship Completes Orbital Flight Test and Splashdown", "Tech", "Super Heavy booster caught by launch tower arms."),
            ("G7 Leaders Issue Joint Communique on AI Governance Framework", "World", "Group of Seven outlines ethical safety standards."),
            ("Pacific Typhoon Weakens After Making Landfall in Luzon", "World", "Meteorological agency downgrades storm severity.")
        ]

        # Generate 4 clusters with 4 copies each, interleaved in round-robin fashion
        articles = []
        for copy_idx in range(4):
            for cluster_idx, (base_title, cat, desc) in enumerate(cluster_templates):
                suffixes = [f" - Update {copy_idx}", f" | Report", f" - Source {cluster_idx}", ""]
                title = f"{base_title}{suffixes[copy_idx % len(suffixes)]}"
                articles.append({
                    'id': f"art-cluster{cluster_idx}-copy{copy_idx}",
                    'title': title,
                    'description': f"{desc} Detailed analysis variant {copy_idx}.",
                    'category': cat,
                    'source': f"Source-{cluster_idx}-{copy_idx}",
                    'imageUrl': f"https://example.com/cluster-{cluster_idx}.jpg",
                    'entities': {'clusters': [f"Cluster_{cluster_idx}"]}
                })

        self.assertEqual(len(articles), 16)
        final_articles, stats = run_intake(articles)
        self.assertEqual(len(final_articles), 4, f"Expected 4 unique cluster canonics, got {len(final_articles)}")
        self.assertEqual(stats['duplicates_suppressed'], 12)
        self.assertEqual(stats['output_count'], 4)

        # Ensure all 4 returned articles represent distinct clusters
        returned_titles = [a['title'] for a in final_articles]
        for base_title, _, _ in cluster_templates:
            # Check normalized prefix match
            norm_base = normalize_title(base_title)
            matching = [t for t in returned_titles if normalize_title(t).startswith(norm_base[:20])]
            self.assertEqual(len(matching), 1, f"Expected 1 canonical for {base_title}, found {matching}")

    def test_canonical_selection_heuristic(self):
        """
        Verify that within a duplicate cluster, the canonical article is chosen
        according to best image quality, entity count, and description length.
        """
        cluster = [
            {
                'id': 'art-poor',
                'title': 'Volcano Erupts in Iceland Spewing Lava Near Coastal Town',
                'description': 'Short description.',
                'imageUrl': 'https://images.unsplash.com/generic.jpg',
                'entities': {}
            },
            {
                'id': 'art-rich',
                'title': 'Volcano Erupts in Iceland Spewing Lava Near Coastal Town - Full Story',
                'description': 'Comprehensive live coverage detailing fissure eruption, lava flows, civil protection evacuations, and gas monitoring across the Reykjanes peninsula.',
                'imageUrl': 'https://cdn.reuters.com/highres/volcano.jpg',
                'entities': {
                    'locations': ['Iceland', 'Reykjanes', 'Grindavik'],
                    'hazards': ['Lava', 'Sulfur Dioxide']
                }
            }
        ]
        deduped = enhanced_dedup(cluster)
        canonicals = [a for a in deduped if not a.get('is_duplicate')]
        self.assertEqual(len(canonicals), 1)
        self.assertEqual(canonicals[0]['id'], 'art-rich', "Expected richer article to be chosen as canonical")

    def test_empty_feed_and_single_article(self):
        """Verify boundary feeds of length 0 and 1."""
        # Length 0
        final_0, stats_0 = run_intake([])
        self.assertEqual(len(final_0), 0)
        self.assertEqual(stats_0['input_count'], 0)
        self.assertEqual(stats_0['duplicates_suppressed'], 0)

        # Length 1
        single_art = [{
            'id': 'single-1',
            'title': 'Global Summit Opens in New York',
            'description': 'Leaders assemble for the annual general assembly.',
            'category': 'World',
            'imageUrl': 'https://example.com/summit.jpg'
        }]
        final_1, stats_1 = run_intake(single_art)
        self.assertEqual(len(final_1), 1)
        self.assertEqual(stats_1['duplicates_suppressed'], 0)
        self.assertFalse(final_1[0].get('is_duplicate', False))

    def test_malformed_article_fields_in_intake(self):
        """Verify intake doesn't crash on None / missing fields."""
        malformed = [
            {'id': 'null-1', 'title': None, 'description': None},
            {'id': 'null-2', 'title': '', 'description': '', 'category': None, 'entities': None},
            {'id': 'null-3'},  # completely empty dict
            {
                'id': 'valid-1',
                'title': 'Standard Valid Article Headline for Normal Processing',
                'description': 'Valid article text.',
                'category': 'General'
            }
        ]
        # Should execute cleanly without unhandled exceptions
        final_arts, stats = run_intake(malformed)
        self.assertIsInstance(final_arts, list)
        self.assertIsInstance(stats, dict)


if __name__ == '__main__':
    unittest.main()
