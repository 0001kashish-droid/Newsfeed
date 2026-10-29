# Copyright (c) 2026 Kashish Bhushan — News Colossal
# Test Suite: Milestone 3 — Tri-Anchor Semantic Narrative Arc Coherence (R3, R6)
"""
Verifies Requirement R3 (Tri-Anchor Semantic Narrative Arc Coherence) and R6 (Pure Standard Library Constraint):
1. Substantive Lexical Stemmer:
   - Standard-library token extraction, stopword filtering, reporting verb pruning, wire token exclusion.
   - Standard-library suffix reduction (-ational, -ization, -fulness, -lessly, -ingly, -edly, -ing, -ed, -es, -s, -ment, -ness, -tion, -ity).
   - Retention of stems >= 3 chars plus 'ai', 'ev'.
2. Strict Tri-Anchor Narrative Arc Coherence Invariant:
   - Anchor 1: Geopolitical theater test (country code match or subregion match without 'Global').
   - Anchor 2: Entity intersection test (|E_art ∩ E_arc| >= 2, or 1 leader + matching category; excluding wires and pronouns).
   - Anchor 3: Substantive lexical Jaccard overlap >= 0.30.
   - All 3 anchors must hold simultaneously; otherwise return (None, 0.0).
3. 0% False Binding Across Disparate Topic Domains.
4. Geopolitical Theater Isolation (Siberia plague vs Indian state vs US tech).
5. Entity Intersection Guards (single generic entity without shared leader rejects).
6. Honest Null Assignment for unthreaded dispatches:
   {'arc_id': None, 'arc_title': None, 'day_number': 0, 'total_chapters': 0, 'importance_trend': None, 'previous_headlines': []}.
   Never fallback to 'Ongoing Story' or 'Syndicated Bureau'.
7. Memory State Cleansing:
   - data/narrative_memory.json has 0 duplicate chapters and 0 corrupted giant arcs.
   - Multi-chapter arcs maintain authentic coherence with founding dispatch.
"""

import json
import os
import sys
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
    MEDIA_WIRE_ENTITIES,
    STOPWORDS
)
from intelligence.curation import thread_narratives


class TestSubstantiveStems(unittest.TestCase):
    """
    Verifies pure standard library substantive stem extraction, stopword filtering,
    reporting verb pruning, wire exclusion, and suffix reduction.
    """

    def test_substantive_stems_stopword_pruning(self):
        """Standard stopwords, reporting verbs, and time tokens must be pruned."""
        text = "The president said today that reports and warnings will be announced next week"
        stems = substantive_stems(text)
        self.assertNotIn("the", stems)
        self.assertNotIn("said", stems)
        self.assertNotIn("today", stems)
        self.assertNotIn("that", stems)
        self.assertNotIn("reports", stems)
        self.assertNotIn("warnings", stems)
        self.assertNotIn("will", stems)
        self.assertNotIn("be", stems)
        self.assertNotIn("announced", stems)
        self.assertNotIn("week", stems)
        self.assertIn("president", stems)

    def test_substantive_stems_wire_and_short_token_exclusion(self):
        """Wire publisher tokens and short noise (< 3 chars) must be pruned except 'ai'/'ev'."""
        text = "Reuters reports that BBC and AP confirmed AI and EV surge in US - Bloomberg"
        stems = substantive_stems(text)
        self.assertNotIn("reuters", stems)
        self.assertNotIn("bbc", stems)
        self.assertNotIn("ap", stems)
        self.assertNotIn("bloomberg", stems)
        self.assertNotIn("in", stems)
        self.assertNotIn("us", stems)
        # Authentic 2-letter technology tokens must be preserved
        self.assertIn("ai", stems)
        self.assertIn("ev", stems)
        self.assertIn("surg", stems)

    def test_substantive_stems_suffix_reduction(self):
        """Porter-style standard library suffix reduction rules."""
        test_cases = [
            ("relational", "relate"),
            ("organization", "organize"),
            ("carefulness", "careful"),
            ("flawlessly", "flawless"),
            ("exceedingly", "exceed"),
            ("repeatedly", "repeat"),
            ("development", "develop"),
            ("darkness", "dark"),
            ("activity", "activ"),
            ("fighting", "fight"),
            ("attacked", "attack"),
            ("strike", "strik"),
            ("strikes", "strik"),
            ("probe", "prob"),
            ("probes", "prob"),
            ("missile", "missil"),
            ("missiles", "missil"),
            ("treaty", "treati"),
            ("treaties", "treati"),
            ("foundry", "foundri"),
            ("foundries", "foundri"),
            ("ministry", "ministri"),
            ("ministries", "ministri"),
            ("kills", "kill"),
            ("protests", "protest")
        ]
        for word, expected_stem in test_cases:
            with self.subTest(word=word):
                stems = substantive_stems(word)
                self.assertIn(expected_stem, stems, f"Word '{word}' should reduce to stem '{expected_stem}'")

    def test_substantive_stems_singular_plural_symmetry(self):
        """Singular and plural forms of silent-e and y/ies words must produce identical stems."""
        pairs = [
            ("strike", "strikes"),
            ("probe", "probes"),
            ("missile", "missiles"),
            ("treaty", "treaties"),
            ("foundry", "foundries"),
            ("ministry", "ministries"),
        ]
        for sing, plur in pairs:
            with self.subTest(pair=f"{sing} vs {plur}"):
                self.assertEqual(
                    substantive_stems(sing),
                    substantive_stems(plur),
                    f"Stem mismatch between singular '{sing}' and plural '{plur}'"
                )

    def test_substantive_stems_double_s_guard(self):
        """Words ending in 'ss' (e.g. press, boss, class) must not have 's' stripped."""
        self.assertIn("press", substantive_stems("press"))
        self.assertIn("boss", substantive_stems("boss"))
        self.assertIn("class", substantive_stems("class"))

    def test_substantive_stems_null_and_malformed_inputs(self):
        """None, empty strings, and non-string types must return empty set safely."""
        self.assertEqual(substantive_stems(""), set())
        self.assertEqual(substantive_stems(None), set())
        self.assertEqual(substantive_stems(12345), set())
        self.assertEqual(substantive_stems([]), set())


class TestTriAnchorCrossTopicRejection(unittest.TestCase):
    """
    Verifies 0% false binding across disparate topics (R3).
    Stories from different topical domains must never bind to an arc.
    """

    def setUp(self):
        self.semiconductor_arc = {
            'arc_id': 'arc-semiconductors',
            'title': 'Asia Semiconductor Export Controls and Foundry Subsidies',
            'keywords': ['semiconductor', 'chips', 'foundry', 'export', 'subsidies'],
            'entity_signature': 'TW:US:TSMC',
            'category': 'Tech',
            'regions': ['Asia-Pacific', 'North America'],
            'chapter_titles': ['TSMC Expands Advanced Packaging in Taiwan']
        }
        self.gaza_arc = {
            'arc_id': 'arc-gaza-hostages',
            'title': 'Gaza Hostage Negotiations and Ceasefire Framework Talks',
            'keywords': ['hostage', 'ceasefire', 'negotiations', 'cairo', 'hamas'],
            'entity_signature': 'IL:PS:EG:Hamas',
            'category': 'World',
            'regions': ['Middle East'],
            'chapter_titles': ['Negotiators Meet in Cairo for Hostage Talks']
        }
        self.ukraine_arc = {
            'arc_id': 'arc-ukraine-strikes',
            'title': 'Russian Barrage Hits Kyiv Energy Grid as Air Defenses Intercept',
            'keywords': ['barrage', 'missile', 'kyiv', 'strikes', 'intercept'],
            'entity_signature': 'RU:UA:Volodymyr Zelenskyy',
            'category': 'World',
            'regions': ['Europe'],
            'chapter_titles': ['Massive Missile Strike Targets Kyiv Substation']
        }
        self.plague_arc = {
            'arc_id': 'arc-siberia-plague',
            'title': 'US closely monitoring case of lab worker who died of plague in Siberia',
            'keywords': ['plague', 'siberia', 'laboratory', 'technician', 'infection'],
            'entity_signature': 'US:RU:plague',
            'category': 'World',
            'regions': ['Europe'],
            'chapter_titles': ['US closely monitoring case of lab worker who died of plague in Siberia']
        }

    def test_0_percent_false_binding_across_disparate_topics(self):
        """Cross-topic rejection: assert 0% false binding across disparate domains."""
        disparate_articles = [
            # 1. Celebrity obituary
            {
                'title': "Actress Eva Marie Saint, who won an Oscar for 'On the Waterfront,' dies at 102",
                'category': 'World',
                'region': 'North America',
                'entities': {'people': ['Eva Marie Saint'], 'countries': ['US']}
            },
            # 2. SiriusXM comedy dispute
            {
                'title': "Sebastian Maniscalco's SiriusXM channel is hurting up-and-coming talent, comics say",
                'category': 'Entertainment',
                'region': 'North America',
                'entities': {'companies': ['SiriusXM'], 'people': ['Sebastian Maniscalco']}
            },
            # 3. Bihar NEET student death investigation
            {
                'title': 'CBI files closure report in Pocso court over death of 17-yr-old NEET aspirant in Bihar',
                'category': 'National',
                'region': 'India',
                'entities': {'organizations': ['CBI'], 'locations': ['Bihar']}
            },
            # 4. Google AI games
            {
                'title': 'Google now lets you make games with AI in Workspace preview',
                'category': 'Tech',
                'region': 'North America',
                'entities': {'companies': ['Google']}
            },
            # 5. Italian centenarian study
            {
                'title': "Sardinian village where more women reach 100 may be new centenarian 'blue zone'",
                'category': 'World',
                'region': 'Europe',
                'entities': {'locations': ['Sardinia', 'Italy'], 'countries': ['IT']}
            }
        ]

        arcs = [self.semiconductor_arc, self.gaza_arc, self.ukraine_arc, self.plague_arc]

        for art in disparate_articles:
            for arc in arcs:
                with self.subTest(article=art['title'][:30], arc=arc['title'][:30]):
                    matched_arc, score = match_article_to_arc(art, [arc])
                    self.assertIsNone(
                        matched_arc,
                        f"CRITICAL COHERENCE LEAK: Disparate article '{art['title']}' falsely matched arc '{arc['title']}' (score: {score})"
                    )
                    self.assertEqual(score, 0.0)


class TestGeopoliticalTheaterIsolation(unittest.TestCase):
    """
    Verifies Anchor 1: Geopolitical theater isolation.
    Stories from mismatched countries or regions cannot bind.
    """

    def test_geopolitical_theater_isolation(self):
        """Siberian plague lab arc (RU, Europe) cannot bind to Indian or US-only stories."""
        siberia_arc = {
            'arc_id': 'arc-siberia-plague',
            'title': 'Siberian Plague Outbreak Investigation',
            'keywords': ['plague', 'siberia', 'lab', 'infection'],
            'entity_signature': 'RU:plague',
            'category': 'World',
            'regions': ['Europe'],
            'chapter_titles': ['Siberian Plague Outbreak Investigation']
        }

        # Indian state story
        india_article = {
            'title': 'Plague preventive measures ordered in Indian state after suspected infection',
            'category': 'World',
            'region': 'India',
            'entities': {'countries': [{'code': 'IN', 'name': 'India'}]}
        }
        matched_india, score_india = match_article_to_arc(india_article, [siberia_arc])
        self.assertIsNone(matched_india, "Mismatched geopolitical theater (IN vs RU) must not bind")
        self.assertEqual(score_india, 0.0)

        # US domestic story
        us_article = {
            'title': 'Plague history museum exhibition opens in Silicon Valley technology center',
            'category': 'World',
            'region': 'North America',
            'entities': {'countries': [{'code': 'US', 'name': 'United States'}]}
        }
        matched_us, score_us = match_article_to_arc(us_article, [siberia_arc])
        self.assertIsNone(matched_us, "Mismatched geopolitical theater (US vs RU) must not bind")
        self.assertEqual(score_us, 0.0)


class TestEntityIntersectionRequirement(unittest.TestCase):
    """
    Verifies Anchor 2: Entity intersection requirement.
    Single generic entity without shared leader rejects.
    """

    def test_single_generic_entity_without_shared_leader_rejects(self):
        """An article with only 1 generic country (e.g. US) and no shared leader cannot bind."""
        arc = {
            'arc_id': 'arc-us-economy',
            'title': 'Federal Reserve Interest Rate Cuts Cycle',
            'keywords': ['federal', 'reserve', 'interest', 'rates', 'powell', 'inflation'],
            'entity_signature': 'US:Federal Reserve:Jerome Powell',
            'category': 'Business',
            'regions': ['North America'],
            'chapter_titles': ['Fed Cuts Rates by 25 Basis Points']
        }

        # Unrelated article that only mentions the US
        generic_us_article = {
            'title': 'US National Park Attendance Hits All-Time Record High During Summer',
            'description': 'Tourism officials report millions visited Yosemite and Yellowstone this season.',
            'category': 'Business',
            'region': 'North America',
            'entities': {
                'countries': [{'code': 'US', 'name': 'United States'}]
            }
        }
        matched, score = match_article_to_arc(generic_us_article, [arc])
        self.assertIsNone(
            matched,
            "Single generic entity ('US') without shared leader or high topical Jaccard must reject"
        )
        self.assertEqual(score, 0.0)

    def test_shared_leader_with_matching_category_passes(self):
        """Shared leader + matching category satisfies Anchor 2."""
        arc = {
            'arc_id': 'arc-zelensky-kyiv',
            'title': 'Zelenskyy Appeals for Air Defense Missiles in Kyiv Address',
            'keywords': ['zelensky', 'zelenskyy', 'missiles', 'defense', 'kyiv'],
            'entity_signature': 'RU:UA:Volodymyr Zelenskyy',
            'category': 'World',
            'regions': ['Europe'],
            'chapter_titles': ['Zelenskyy Appeals for Air Defense Missiles in Kyiv Address']
        }
        article = {
            'title': 'Zelenskyy appeals for urgent air defense missiles following strikes in Kyiv',
            'description': 'President Volodymyr Zelenskyy addressed the nation following strikes in Kyiv appealing for air defense missiles.',
            'category': 'World',
            'region': 'Europe',
            'entities': {
                'leaders': [{'name': 'Volodymyr Zelenskyy', 'matched': 'zelenskyy'}],
                'countries': [{'code': 'UA', 'name': 'Ukraine'}]
            }
        }
        matched, score = match_article_to_arc(article, [arc])
        self.assertIsNotNone(matched)
        self.assertEqual(matched['arc_id'], 'arc-zelensky-kyiv')
        self.assertGreaterEqual(score, 0.30)

    def test_single_country_code_and_name_cannot_satisfy_anchor2(self):
        """A single country with both code and name must never satisfy Anchor 2 alone."""
        from intelligence.memory import _extract_article_entities_for_anchors, _extract_arc_entities_for_anchors

        # Test Germany
        art_de = {
            'title': 'Munich Beer Festival Celebrates Record Turnout in Bavaria',
            'entities': {'countries': [{'code': 'DE', 'name': 'Germany'}]}
        }
        arc_de = {
            'arc_id': 'arc-germany-defense',
            'title': 'German Bundeswehr Modernization and Procurement Plan',
            'keywords': ['bundeswehr', 'modernization', 'procurement', 'defense'],
            'entity_signature': 'DE:Bundeswehr',
            'category': 'Military',
            'regions': ['Europe'],
            'chapter_titles': ['German Bundeswehr Modernization Plan']
        }
        _, _, art_ents, _ = _extract_article_entities_for_anchors(art_de)
        _, _, arc_ents, _ = _extract_arc_entities_for_anchors(arc_de)
        common = art_ents.intersection(arc_ents)
        self.assertLess(len(common), 2, f"Country inflation: common entities {common} must have length < 2")
        self.assertEqual(common, {'germany'})

        matched, score = match_article_to_arc(art_de, [arc_de])
        self.assertIsNone(matched, "Single country alone without shared leader or topical entities must reject")
        self.assertEqual(score, 0.0)

        # Test France
        art_fr = {
            'title': 'Bordeaux Wine Harvest Season Yields High Quality Vintage',
            'entities': {'countries': [{'code': 'FR', 'name': 'France'}]}
        }
        arc_fr = {
            'arc_id': 'arc-france-pension',
            'title': 'French Pension Reform Protests and Demonstrations',
            'keywords': ['pension', 'reform', 'protests', 'strike'],
            'entity_signature': 'FR:Emmanuel Macron',
            'category': 'World',
            'regions': ['Europe'],
            'chapter_titles': ['French Pension Reform Protests']
        }
        matched_fr, score_fr = match_article_to_arc(art_fr, [arc_fr])
        self.assertIsNone(matched_fr, "Single country alone without shared leader must reject")
        self.assertEqual(score_fr, 0.0)

    def test_unauthorized_1_entity_bypass_is_eliminated(self):
        """Sharing only 1 topical entity without a shared leader must strictly reject Anchor 2."""
        arc = {
            'arc_id': 'arc-ai-supercomputing',
            'title': 'Nvidia AI Chip Architecture and High-Performance Compute Cluster',
            'keywords': ['nvidia', 'gpu', 'datacenter', 'blackwell'],
            'entity_signature': 'US:Nvidia:Datacenter:Compute',
            'category': 'Tech',
            'regions': ['North America'],
            'chapter_titles': ['Nvidia Announces Next-Gen Compute Architecture']
        }
        article_single_entity = {
            'title': 'Nvidia Announces Developer Tools and Neural Network Libraries',
            'description': 'Nvidia keynote covers machine learning frameworks and developer tools.',
            'category': 'Tech',
            'region': 'North America',
            'entities': {
                'companies': ['Nvidia']
            }
        }
        matched, score = match_article_to_arc(article_single_entity, [arc])
        self.assertIsNone(matched, "Strict Anchor 2 contract requires >= 2 topical entities; 1 entity must reject")
        self.assertEqual(score, 0.0)


class TestJaccardThresholdConstraint(unittest.TestCase):
    """
    Verifies Anchor 3: Substantive lexical Jaccard overlap >= 0.30.
    """

    def test_jaccard_below_30_rejects(self):
        """Even with shared countries, Jaccard < 0.30 rejects binding."""
        arc = {
            'arc_id': 'arc-china-hypersonic',
            'title': 'China Tests Long-Range Hypersonic Glider Over Pacific Waters',
            'keywords': ['hypersonic', 'glider', 'trajectory', 'missile', 'pacific'],
            'entity_signature': 'CN:US',
            'category': 'World',
            'regions': ['Asia-Pacific'],
            'chapter_titles': ['China Tests Long-Range Hypersonic Glider']
        }
        # Article shares countries CN and US, but topic is giant pandas
        panda_article = {
            'title': 'China Sends Giant Panda Pair to National Zoo in Washington',
            'description': 'Conservationists celebrate the arrival of two giant pandas from Chengdu.',
            'category': 'World',
            'region': 'Asia-Pacific',
            'entities': {
                'countries': [{'code': 'CN', 'name': 'China'}, {'code': 'US', 'name': 'United States'}]
            }
        }
        matched, score = match_article_to_arc(panda_article, [arc])
        self.assertIsNone(matched, "Jaccard < 0.30 must reject even if country codes match")
        self.assertEqual(score, 0.0)


class TestHonestNullAssignment(unittest.TestCase):
    """
    Verifies honest null contract in curation.py thread_narratives.
    """

    def test_isolated_dispatches_receive_honest_null(self):
        """Articles that do not match an arc must receive clean honest nulls."""
        articles = [
            {
                'id': 'art-isolated-1',
                'title': "María del Carmen Abascal, symbol of Spain's housing protests, dies at 73",
                'category': 'World',
                'region': 'Europe',
                'entities': {'locations': ['Spain']}
            }
        ]
        memory = {'arcs': []}
        threaded = thread_narratives(articles, memory)
        self.assertEqual(len(threaded), 1)
        narrative_arc = threaded[0].get('narrative_arc')
        self.assertIsNotNone(narrative_arc)
        self.assertIsNone(narrative_arc['arc_id'])
        self.assertIsNone(narrative_arc['arc_title'])
        self.assertEqual(narrative_arc['day_number'], 0)
        self.assertEqual(narrative_arc['total_chapters'], 0)
        self.assertIsNone(narrative_arc['importance_trend'])
        self.assertEqual(narrative_arc['previous_headlines'], [])

    def test_zero_occurrences_of_ongoing_story_or_syndicated_bureau(self):
        """data/news.json must contain 0 occurrences of 'Ongoing Story' or 'Syndicated Bureau'."""
        news_path = os.path.join(_PROJECT_ROOT, 'data', 'news.json')
        with open(news_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        for art in data.get('articles', []):
            arc_info = art.get('narrative_arc') or {}
            arc_title = arc_info.get('arc_title')
            self.assertNotEqual(arc_title, 'Ongoing Story', f"Found forbidden 'Ongoing Story' in {art.get('id')}")
            self.assertNotEqual(arc_title, 'Syndicated Bureau', f"Found forbidden 'Syndicated Bureau' in {art.get('id')}")


class TestNarrativeMemoryCleansing(unittest.TestCase):
    """
    Verifies that data/narrative_memory.json is cleansed of duplicate chapters and giant corrupted arcs.
    """

    def setUp(self):
        self.memory_path = os.path.join(_PROJECT_ROOT, 'data', 'narrative_memory.json')
        with open(self.memory_path, 'r', encoding='utf-8') as f:
            self.memory = json.load(f)

    def test_zero_duplicate_chapters_in_narrative_memory(self):
        """Every arc must contain 0 duplicate chapter titles and chapter_count == len(titles)."""
        arcs = self.memory.get('arcs', [])
        self.assertGreaterEqual(len(arcs), 10, "Must maintain at least 10 active arcs")

        for arc in arcs:
            titles = arc.get('chapter_titles', [])
            self.assertIsInstance(titles, list)
            unique_titles = list(dict.fromkeys(titles))
            self.assertEqual(
                len(titles),
                len(unique_titles),
                f"Arc '{arc.get('arc_id')}' contains duplicate chapter titles: {titles}"
            )
            self.assertEqual(
                arc.get('chapter_count'),
                len(titles),
                f"Arc '{arc.get('arc_id')}' chapter_count {arc.get('chapter_count')} != len(titles) {len(titles)}"
            )

    def test_zero_corrupted_giant_arcs(self):
        """No arc exceeds 25 chapters and known corrupted arcs are sanitized."""
        arcs = self.memory.get('arcs', [])
        for arc in arcs:
            self.assertLessEqual(
                arc.get('chapter_count', 0),
                25,
                f"Giant arc detected: '{arc.get('arc_id')}' has {arc.get('chapter_count')} chapters"
            )

        # Specifically check plague arc 5b745eea
        plague_arcs = [a for a in arcs if a.get('arc_id') == '5b745eea-fec4-44a4-b06a-b28637c6004d']
        if plague_arcs:
            plague_arc = plague_arcs[0]
            for title in plague_arc.get('chapter_titles', []):
                lower = title.lower()
                self.assertNotIn('eva marie saint', lower, "Obituary leaked into plague arc")
                self.assertNotIn('siriusxm', lower, "SiriusXM comedy leaked into plague arc")
                self.assertNotIn('neet', lower, "Bihar NEET death leaked into plague arc")
                self.assertNotIn('game', lower, "Google AI games leaked into plague arc")

    def test_update_memory_prevents_duplicate_chapters(self):
        """update_memory must not append duplicate chapter titles if title was already tracked."""
        mem = {
            'arcs': [
                {
                    'arc_id': 'arc-test-1',
                    'title': 'European Gas Prices Surge',
                    'keywords': ['gas', 'prices', 'surge', 'europe'],
                    'entity_signature': 'DE:Gazprom',
                    'category': 'Business',
                    'regions': ['Europe'],
                    'chapter_count': 1,
                    'chapter_titles': ['European Gas Prices Surge Today'],
                    'sources_involved': ['Reuters']
                }
            ]
        }
        repeat_article = {
            'title': 'European Gas Prices Surge Today',
            'category': 'Business',
            'region': 'Europe',
            'source': 'The Guardian',
            'entities': {
                'locations': ['Germany'],
                'companies': ['Gazprom']
            }
        }
        updated = update_memory(mem, [repeat_article])
        target_arc = updated['arcs'][0]
        self.assertEqual(len(target_arc['chapter_titles']), 1, "Duplicate chapter title must not be added")
        self.assertEqual(target_arc['chapter_count'], 1, "chapter_count must not inflate on duplicate")
        self.assertIn('The Guardian', target_arc['sources_involved'])

    def test_zero_wire_suffixes_in_all_narrative_arcs(self):
        """No chapter title in data/narrative_memory.json may contain trailing wire suffixes."""
        forbidden_wires = ['- reuters', '- ap', '- bbc', '- afp', '- bloomberg']
        for arc in self.memory.get('arcs', []):
            for ch in arc.get('chapter_titles', []):
                for wire in forbidden_wires:
                    self.assertFalse(
                        ch.lower().endswith(wire),
                        f"Wire suffix '{wire}' found in arc '{arc.get('arc_id')}': '{ch}'"
                    )

    def test_zero_typographical_duplicate_chapters_in_narrative_memory(self):
        """No arc in data/narrative_memory.json may have typographical duplicates (curly vs straight quotes, dashes, compound hyphens/spaces)."""
        import re
        for arc in self.memory.get('arcs', []):
            seen = set()
            for ch in arc.get('chapter_titles', []):
                norm = re.sub(r'[\'\"’“”\s\-–—]', '', ch.lower())
                self.assertNotIn(
                    norm, seen,
                    f"Typographical duplicate chapter found in arc '{arc.get('arc_id')}': '{ch}'"
                )
                seen.add(norm)

    def test_update_memory_normalized_duplicate_rejection(self):
        """update_memory must normalize curly quotes, straight quotes, and dashes to reject typographical dups."""
        mem = {
            'arcs': [
                {
                    'arc_id': 'arc-test-norm',
                    'title': "French Student Protests – Europe Live",
                    'keywords': ['french', 'student', 'protests', 'europe'],
                    'entity_signature': 'FR:Sorbonne',
                    'category': 'World',
                    'regions': ['Europe'],
                    'chapter_count': 1,
                    'chapter_titles': ["French high school protests continue despite PM’s promise of action – Europe live"],
                    'sources_involved': ['The Guardian']
                }
            ]
        }
        # Repeat article using straight quote and regular hyphen
        repeat_article = {
            'title': "French high school protests continue despite PM's promise of action - Europe live",
            'category': 'World',
            'region': 'Europe',
            'source': 'France 24',
            'entities': {
                'locations': ['France', 'Paris'],
                'organizations': ['Sorbonne']
            }
        }
        updated = update_memory(mem, [repeat_article])
        target_arc = updated['arcs'][0]
        self.assertEqual(
            len(target_arc['chapter_titles']), 1,
            f"Typographical duplicate was appended: {target_arc['chapter_titles']}"
        )
        self.assertEqual(target_arc['chapter_count'], 1)
        self.assertIn('France 24', target_arc['sources_involved'])

    def test_update_memory_compound_hyphen_and_defensive_types(self):
        """update_memory must collapse compound hyphens (high-school vs high school) and handle non-string titles without crashing."""
        mem = {
            'arcs': [
                {
                    'arc_id': 'arc-compound-test',
                    'title': "French Student Protests In Paris",
                    'keywords': ['french', 'student', 'protests', 'paris'],
                    'entity_signature': 'FR:Sorbonne',
                    'category': 'World',
                    'regions': ['Europe'],
                    'chapter_count': 1,
                    'chapter_titles': ["French police suspend use of stun grenades after high school protester loses hand"],
                    'sources_involved': ['The Guardian']
                }
            ]
        }
        # Compound hyphen variant
        hyphen_article = {
            'title': "French police suspend use of stun grenades after high-school protester loses hand",
            'category': 'World',
            'region': 'Europe',
            'source': 'France 24',
            'entities': {
                'locations': ['France', 'Paris'],
                'organizations': ['Sorbonne']
            }
        }
        # Non-string titles (fuzzing/adversarial int, bool, None)
        corrupt_int = {'title': 12345, 'category': 'World', 'region': 'Europe', 'entities': {'locations': ['France', 'Paris'], 'organizations': ['Sorbonne']}}
        corrupt_none = {'title': None, 'category': 'World', 'region': 'Europe', 'entities': {'locations': ['France', 'Paris'], 'organizations': ['Sorbonne']}}
        corrupt_bool = {'title': True, 'category': 'World', 'region': 'Europe', 'entities': {'locations': ['France', 'Paris'], 'organizations': ['Sorbonne']}}

        updated = update_memory(mem, [hyphen_article, corrupt_int, corrupt_none, corrupt_bool])
        target_arc = updated['arcs'][0]
        self.assertEqual(
            len(target_arc['chapter_titles']), 1,
            f"Compound hyphen duplicate was appended: {target_arc['chapter_titles']}"
        )
        self.assertEqual(target_arc['chapter_count'], 1)
        self.assertIn('France 24', target_arc['sources_involved'])


if __name__ == '__main__':
    unittest.main()

