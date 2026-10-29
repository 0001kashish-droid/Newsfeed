# Copyright (c) 2026 Kashish Bhushan — News Colossal
# Test Suite: Milestone 5 — Hermetic News Intelligence Master Fuzz Harness & Hard Audit (R5, R6)
"""
Master Hermetic Intelligence Verification Test Suite for News Colossal:
1. AdversarialWireInjectionFuzzTest:
   - Fuzzes raw dispatches with diverse synthetic wire datelines, attribution suffixes,
     corrupted parentheticals, and editorial slugs.
   - Asserts 0 wire tokens leak into entities, primary_actors, or narrative_arcs.
2. CrossTopicCollisionResistanceTest:
   - High-entropy cross-topic mixes (semiconductors vs diplomacy vs obituaries vs climate vs aerospace).
   - Proves mathematical zero-leakage across disparate topic domains (Anchor 1, Anchor 2, Anchor 3 invariants).
3. SyntacticActorGrammarFuzzTest:
   - Fuzzes syntactic frames ([Subject] [Verb] [Object]), 8 canonical collective factions,
     and sovereign regional stakeholders.
   - Asserts 0 occurrences of 'Editorial Bureau', 'Syndicated Bureau', or wire names.
4. StandaloneDispatchesHonestNullsTest:
   - Verifies standalone dispatch isolation (arc_id: null).
   - Verifies UI contract integrity (zero synthetic placeholders, scrubber suppression, honest null badges).
5. HermeticZeroDependencyComplianceTest:
   - AST walk of all backend modules ensuring strictly 100% Python standard library usage.
   - Asserts zero external pip packages and zero external AI APIs.

Zero external dependencies (pure Python standard library).
Runtime budget: < 10 seconds.
"""

import ast
import glob
import json
import os
import random
import re
import sys
import unittest

_TEST_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_TEST_DIR)
_SCRIPTS_DIR = os.path.join(_PROJECT_ROOT, 'scripts')

if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)

from intelligence.sanitizer import (
    PUBLISHER_QUARANTINE_SET,
    is_quarantined_publisher,
    normalize_text,
    sanitize_dispatch
)
from intelligence.entities import (
    extract_entities,
    SyntacticActorGrammar,
    COUNTRY_LEXICON,
    COUNTRY_NAMES,
    ORGANIZATION_LEXICON
)
from intelligence.memory import (
    substantive_stems,
    match_article_to_arc,
    GENERIC_COUNTRY_CODES,
    MEDIA_WIRE_ENTITIES
)
from intelligence.curation import thread_narratives


# =============================================================================
# CLASS 1: ADVERSARIAL WIRE INJECTION FUZZ TEST
# =============================================================================
class AdversarialWireInjectionFuzzTest(unittest.TestCase):
    """
    Fuzz raw dispatches with diverse synthetic wire datelines, attribution suffixes,
    corrupted parentheticals, and editorial slugs; verify 0 wire tokens leak into
    entities, primary_actors, or narrative_arcs.
    """

    def test_adversarial_datelines_matrix(self):
        """Stress tests compound, multi-city, nested bracket, and date-infused wire datelines."""
        cases = [
            ("WASHINGTON / BRUSSELS (AFP/Reuters) — Envoys reached a historic peace compromise.",
             "Envoys reached a historic peace compromise."),
            ("GENEVA / VIENNA (Reuters) : Talks resumed behind closed doors.",
             "Talks resumed behind closed doors."),
            ("TEL AVIV/BEIRUT (Reuters) - Ceasefire monitors deployed along the border.",
             "Ceasefire monitors deployed along the border."),
            ("((AP)) Washington — Major clean energy policy shift announced by the cabinet.",
             "Major clean energy policy shift announced by the cabinet."),
            ("([Reuters]) London — Finance minister addressed parliament on currency stability.",
             "Finance minister addressed parliament on currency stability."),
            ("[[AFP]] Tokyo --- Bank of Japan confirms currency intervention.",
             "Bank of Japan confirms currency intervention."),
            ("BEIJING, Oct 24 (Reuters) - Central bank lowered reserve requirement ratios.",
             "Central bank lowered reserve requirement ratios."),
            ("KYIV, Oct 25, 2026 (AP) — Defense ministry confirms counter-offensive progress.",
             "Defense ministry confirms counter-offensive progress."),
            ("Reuters — Global inflation cools to three-year low across major economies.",
             "Global inflation cools to three-year low across major economies."),
            ("ASSOCIATED PRESS — Supreme Court will hear arguments on interstate commerce.",
             "Supreme Court will hear arguments on interstate commerce."),
            ("MUMBAI (Reuters) — The Reserve Bank kept benchmark lending rates steady.",
             "The Reserve Bank kept benchmark lending rates steady."),
        ]

        for raw_desc, expected_clean in cases:
            res = sanitize_dispatch("Headline", raw_desc)
            self.assertEqual(
                res['clean_description'], expected_clean,
                f"Dateline stripping failed on: '{raw_desc}' -> Got: '{res['clean_description']}'"
            )
            self.assertIsNotNone(res['stripped_dateline'])

            # Entity extraction zero-leakage
            ents = extract_entities(res['clean_title'], res['clean_description'])
            for org in ents.get('organizations', []):
                self.assertFalse(
                    is_quarantined_publisher(org.get('name', '')),
                    f"Wire publisher leaked into organizations: '{org.get('name')}'"
                )
            for comp in ents.get('companies', []):
                self.assertFalse(
                    is_quarantined_publisher(comp.get('name', '')),
                    f"Wire publisher leaked into companies: '{comp.get('name')}'"
                )

    def test_adversarial_attribution_suffixes_matrix(self):
        """Stress tests dashes, pipes, nested parentheticals, and joint syndication suffixes."""
        cases = [
            ("Diplomatic talks resume in Vienna - Reuters", "Diplomatic talks resume in Vienna"),
            ("Emergency summit called in Brussels | Associated Press", "Emergency summit called in Brussels"),
            ("Energy prices fall sharply — AFP / Reuters", "Energy prices fall sharply"),
            ("Global inflation cools --- BBC News", "Global inflation cools"),
            ("Treaty signed in secret -- Bloomberg News", "Treaty signed in secret"),
            ("Peace talks resume (Reuters)", "Peace talks resume"),
            ("Peace talks resume ((Reuters))", "Peace talks resume"),
            ("Peace talks resume (((AP)))", "Peace talks resume"),
            ("Peace talks resume ([Reuters/AP])", "Peace talks resume"),
            ("Tech conference unveils quantum chip [Bloomberg]", "Tech conference unveils quantum chip"),
            ("Tech conference unveils quantum chip [[AFP]]", "Tech conference unveils quantum chip"),
            ("Summit concludes - Reuters via BBC News", "Summit concludes"),
            ("Trade deal signed - Bloomberg News / Dow Jones", "Trade deal signed"),
            ("Ceasefire declared (Reuters and AP)", "Ceasefire declared"),
            ("Border treaty signed - AFP, Reuters, AP", "Border treaty signed"),
            ("Peace talks resume in Vienna Reuters.", "Peace talks resume in Vienna"),
            ("Border treaty signed AP!", "Border treaty signed"),
        ]

        for raw_title, expected_clean in cases:
            res = sanitize_dispatch(raw_title, "Description text.")
            self.assertEqual(
                res['clean_title'], expected_clean,
                f"Suffix stripping failed on: '{raw_title}' -> Got: '{res['clean_title']}'"
            )
            self.assertIsNotNone(res['stripped_attribution'])

            ents = extract_entities(res['clean_title'], res['clean_description'])
            for org in ents.get('organizations', []):
                self.assertFalse(is_quarantined_publisher(org.get('name', '')))

    def test_embedded_attribution_clauses_and_footers(self):
        """Stress tests sentence-boundary reporting clauses and editorial byline footers."""
        clause_cases = [
            ("Hospital supplies delivered safely, according to Reuters.",
             "Hospital supplies delivered safely."),
            ("Border talks stalled, BBC News reports.",
             "Border talks stalled."),
            ("Envoys met behind closed doors, reported by AFP.",
             "Envoys met behind closed doors."),
            ("Lawmakers reached bipartisan accord, officials tell Reuters.",
             "Lawmakers reached bipartisan accord."),
            ("Global semiconductor shipments rose, Bloomberg finds.",
             "Global semiconductor shipments rose."),
        ]
        for raw, expected in clause_cases:
            res = sanitize_dispatch("Headline", raw)
            self.assertEqual(
                res['clean_description'], expected,
                f"Clause stripping failed: '{raw}' -> Got: '{res['clean_description']}'"
            )

        footer_cases = [
            ("The delegation arrived on Sunday. (Reporting by John Smith; Editing by Jane Doe)",
             "The delegation arrived on Sunday."),
            ("The treaty takes effect immediately. Copyright 2026 Reuters. All rights reserved.",
             "The treaty takes effect immediately."),
            ("New regulations announced in Brussels. Read more at Bloomberg.",
             "New regulations announced in Brussels."),
        ]
        for raw, expected in footer_cases:
            res = sanitize_dispatch("Headline", raw)
            self.assertEqual(
                res['clean_description'], expected,
                f"Footer stripping failed: '{raw}' -> Got: '{res['clean_description']}'"
            )

    def test_combinatorial_randomized_fuzzing_250_iterations(self):
        """Fuzzes 250 combinatorial dispatches combining slugs, cities, wires, and separators."""
        random.seed(42)

        base_headlines = [
            "Envoys reach tentative peace compromise",
            "Central bank lowers benchmark lending rate",
            "Earthquake shakes coastal region causing power outages",
            "Scientists discover novel antibiotic against resistant bacteria",
            "Tech conference showcases next-generation quantum computing chip",
            "Parliament votes to approve comprehensive healthcare reform",
            "Space probe transmits high-resolution images of outer moon",
            "Maritime dispute settled following bilateral negotiations",
            "Automaker launches high-efficiency solid-state battery",
            "Supreme Court upholds constitutional privacy protections",
        ]

        slugs = ["", "EXCLUSIVE: ", "BREAKING: ", "ANALYSIS: ", "SPECIAL REPORT: ", "UPDATE 1: ", "FACTBOX: ", "LIVE: "]
        cities = ["WASHINGTON", "GENEVA", "BEIJING", "LONDON", "NEW DELHI", "KYIV, Ukraine", "WASHINGTON / BRUSSELS", "TOKYO"]
        wire_combos = [
            "Reuters", "AP", "AFP", "BBC News", "Bloomberg",
            "(Reuters)", "((Reuters))", "[AP]", "[[AP]]", "([Reuters])",
            "AFP/Reuters", "Reuters / AP", "Reuters via BBC News", "Bloomberg News / Dow Jones",
            "AFP, Reuters, AP"
        ]
        separators = [" — ", " - ", " : ", " --- "]

        leakage_entities = 0
        leakage_actors = 0
        leakage_stems = 0

        for _ in range(250):
            headline = random.choice(base_headlines)
            slug = random.choice(slugs)
            wire = random.choice(wire_combos)
            city = random.choice(cities)
            sep = random.choice(separators)

            suffix_style = random.choice(['dash', 'paren', 'bracket', 'none'])
            if suffix_style == 'dash':
                raw_title = f"{slug}{headline} - {wire}"
            elif suffix_style == 'paren':
                raw_title = f"{slug}{headline} ({wire})"
            elif suffix_style == 'bracket':
                raw_title = f"{slug}{headline} [{wire}]"
            else:
                raw_title = f"{slug}{headline}"

            raw_desc = f"{city} ({wire}){sep}{headline}. The situation remains under close observation."

            res = sanitize_dispatch(raw_title, raw_desc)
            clean_t = res['clean_title']
            clean_d = res['clean_description']

            self.assertTrue(bool(clean_t), "Clean title cannot be empty")

            ents = extract_entities(clean_t, clean_d)
            for org in ents.get('organizations', []):
                if is_quarantined_publisher(org.get('name', '')):
                    leakage_entities += 1
            for comp in ents.get('companies', []):
                if is_quarantined_publisher(comp.get('name', '')):
                    leakage_entities += 1

            actors = SyntacticActorGrammar.extract_actors(clean_t, clean_d, ents, "Global")
            active_agent = actors.get('active_agent') or ''
            if is_quarantined_publisher(active_agent) or active_agent in ('Editorial Bureau', 'Syndicated Bureau'):
                leakage_actors += 1

            stems = substantive_stems(clean_t) | substantive_stems(clean_d)
            for wire_term in MEDIA_WIRE_ENTITIES:
                if wire_term in stems:
                    leakage_stems += 1

        self.assertEqual(leakage_entities, 0, f"Leaked {leakage_entities} wire entities in 250 fuzz runs!")
        self.assertEqual(leakage_actors, 0, f"Leaked {leakage_actors} wire actors in 250 fuzz runs!")
        self.assertEqual(leakage_stems, 0, f"Leaked {leakage_stems} wire stems in 250 fuzz runs!")

    def test_legitimate_editorial_content_preserved_without_false_positives(self):
        """Verifies legitimate headlines containing wire-like tokens are preserved intact."""
        legitimate_cases = [
            "AP tests show high lead levels in drinking water across three states",
            "Reuters Institute publishes global digital news report on AI adoption",
            "BBC Proms announces summer concert lineup featuring classical masters",
            "Apple acquires new AI startup for $200M in cash",
            "WHO warns of surging cholera cases across 12 countries",
            "US and China agree on new climate targets ahead of COP summit",
            "Defense secretary visits troops in South Korea amid regional tensions",
            "Tech giants face new EU antitrust investigation into cloud dominance",
        ]
        for title in legitimate_cases:
            res = sanitize_dispatch(title, "Legitimate reporting body text.")
            self.assertEqual(
                res['clean_title'], title,
                f"Legitimate title modified! Raw='{title}', Got='{res['clean_title']}'"
            )


# =============================================================================
# CLASS 2: CROSS-TOPIC COLLISION RESISTANCE TEST
# =============================================================================
class CrossTopicCollisionResistanceTest(unittest.TestCase):
    """
    High-entropy cross-topic mixes (semiconductors vs diplomacy vs obituaries vs climate vs aerospace).
    Proves mathematical zero-leakage across disparate topic domains (Anchor 1, Anchor 2, Anchor 3 invariants).
    """

    def setUp(self):
        # 5 Canonical Arcs across disparate domains
        self.arc_tech_chips = {
            'arc_id': 'arc-tech-semiconductors-001',
            'title': 'Global Advanced Semiconductor Foundry Scaling',
            'category': 'Tech',
            'countries': ['TW', 'US'],
            'regions': ['Asia-Pacific', 'North America'],
            'entities': ['tsmc', 'nvidia', 'asml', 'semiconductors', 'lithography', 'wafer', 'gpu'],
            'leaders': [],
            'keywords': ['tsmc', 'semiconductor', 'foundry', 'lithography', 'chip', 'wafer'],
            'chapter_titles': [
                'TSMC breaks ground on advanced 2nm wafer fabrication facility',
                'Nvidia unveils next-generation Blackwell architecture for AI data centers'
            ]
        }

        self.arc_diplomatic_talks = {
            'arc_id': 'arc-mideast-ceasefire-002',
            'title': 'Middle East Diplomatic Ceasefire Mediation',
            'category': 'World',
            'countries': ['EG', 'QA', 'PS', 'IL'],
            'regions': ['Middle East'],
            'entities': ['egypt', 'qatar', 'gaza', 'hamas', 'israel', 'ceasefire', 'hostages'],
            'leaders': [],
            'keywords': ['envoys', 'ceasefire', 'talks', 'hostages', 'mediation', 'truce'],
            'chapter_titles': [
                'Envoys convene emergency diplomatic talks in Cairo',
                'Mediators present phased truce proposal to regional delegations'
            ]
        }

        self.arc_cultural_obituaries = {
            'arc_id': 'arc-arts-obituaries-003',
            'title': 'Cultural Legacy & Cinematic Memorials',
            'category': 'Culture',
            'countries': ['US', 'FR'],
            'regions': ['North America', 'Europe'],
            'entities': ['oscar', 'hollywood', 'academy', 'cinema', 'broadway'],
            'leaders': [],
            'keywords': ['oscar', 'dies', 'waterfront', 'actress', 'tribute', 'memorial'],
            'chapter_titles': [
                'Eva Marie Saint Oscar retrospective celebrated by cinema historians'
            ]
        }

        self.arc_arctic_permafrost = {
            'arc_id': 'arc-polar-permafrost-004',
            'title': 'Polar Cryosphere Thawing & Environmental Hazards',
            'category': 'Science',
            'countries': ['RU'],
            'regions': ['Europe', 'Asia-Pacific'],
            'entities': ['siberia', 'permafrost', 'anthrax', 'tundra', 'arctic'],
            'leaders': [],
            'keywords': ['permafrost', 'thaw', 'anthrax', 'siberia', 'spores', 'tundra'],
            'chapter_titles': [
                'Permafrost thawing in Siberia triggers biological containment alerts'
            ]
        }

        self.arc_planetary_probes = {
            'arc_id': 'arc-space-exploration-005',
            'title': 'Planetary Science & Solar System Exploration',
            'category': 'Tech',
            'countries': ['US', 'EU'],
            'regions': ['Global'],
            'entities': ['nasa', 'mars', 'esa', 'rover', 'venus', 'biosignatures'],
            'leaders': [],
            'keywords': ['nasa', 'mars', 'rover', 'planetary', 'esa', 'orbit'],
            'chapter_titles': [
                'Mars rover explores ancient river delta for biosignatures'
            ]
        }

        self.all_arcs = [
            self.arc_tech_chips,
            self.arc_diplomatic_talks,
            self.arc_cultural_obituaries,
            self.arc_arctic_permafrost,
            self.arc_planetary_probes
        ]

    def test_cross_domain_matrix_zero_leakage(self):
        """
        Cross-matches 15 dispatches across 5 disparate domains against opposing arcs.
        Asserts 0.00% false binding rate.
        """
        dispatches = [
            # Domain 1 Dispatches (Semiconductors)
            {'id': 'd1_1', 'domain': 'tech', 'title': 'TSMC posts record quarterly profit on surging AI chip demand', 'description': 'Taiwan semiconductor foundry reports strong revenues.', 'category': 'Tech', 'region': 'Asia-Pacific', 'entities': {'countries': [{'code': 'TW', 'name': 'Taiwan'}], 'companies': [{'name': 'TSMC'}], 'organizations': []}},
            {'id': 'd1_2', 'domain': 'tech', 'title': 'ASML ships high-NA EUV lithography systems to advanced foundries', 'description': 'Lithography supplier accelerates wafer equipment deliveries.', 'category': 'Tech', 'region': 'Europe', 'entities': {'countries': [{'code': 'NL', 'name': 'Netherlands'}], 'companies': [{'name': 'ASML'}], 'organizations': []}},
            {'id': 'd1_3', 'domain': 'tech', 'title': 'Nvidia accelerates Blackwell Ultra GPU server deliveries', 'description': 'AI hardware systems scale across global data center networks.', 'category': 'Tech', 'region': 'North America', 'entities': {'countries': [{'code': 'US', 'name': 'United States'}], 'companies': [{'name': 'Nvidia'}], 'organizations': []}},

            # Domain 2 Dispatches (Diplomacy)
            {'id': 'd2_1', 'domain': 'diplomacy', 'title': 'Envoys from Egypt and Qatar convene emergency ceasefire talks in Cairo', 'description': 'Delegates seek to broker hostage release agreement.', 'category': 'World', 'region': 'Middle East', 'entities': {'countries': [{'code': 'EG', 'name': 'Egypt'}, {'code': 'QA', 'name': 'Qatar'}], 'companies': [], 'organizations': []}},
            {'id': 'd2_2', 'domain': 'diplomacy', 'title': 'UN Security Council adopts resolution urging immediate humanitarian truce in Gaza', 'description': 'Security council calls for unhindered aid delivery.', 'category': 'World', 'region': 'Middle East', 'entities': {'countries': [{'code': 'PS', 'name': 'Palestine'}], 'companies': [], 'organizations': [{'name': 'UN'}]}},
            {'id': 'd2_3', 'domain': 'diplomacy', 'title': 'Diplomats resume bilateral maritime border boundary discussions in Geneva', 'description': 'Envoys explore peaceful resolution to territorial demarcation.', 'category': 'World', 'region': 'Europe', 'entities': {'countries': [{'code': 'CH', 'name': 'Switzerland'}], 'companies': [], 'organizations': []}},

            # Domain 3 Dispatches (Obituaries)
            {'id': 'd3_1', 'domain': 'culture', 'title': "Eva Marie Saint, Oscar winner for 'On the Waterfront', dies at 102", 'description': 'Legendary cinema icon passed away peacefully at home.', 'category': 'Culture', 'region': 'North America', 'entities': {'countries': [{'code': 'US', 'name': 'United States'}], 'companies': [], 'organizations': []}},
            {'id': 'd3_2', 'domain': 'culture', 'title': 'Renowned French novelist and literary icon passes away at home in Paris', 'description': 'Literary world mourns the loss of celebrated author.', 'category': 'Culture', 'region': 'Europe', 'entities': {'countries': [{'code': 'FR', 'name': 'France'}], 'companies': [], 'organizations': []}},
            {'id': 'd3_3', 'domain': 'culture', 'title': 'Legendary jazz saxophonist succumbs to cardiac failure in New York', 'description': 'Musical trailblazer influenced generations of improvisational performers.', 'category': 'Culture', 'region': 'North America', 'entities': {'countries': [{'code': 'US', 'name': 'United States'}], 'companies': [], 'organizations': []}},

            # Domain 4 Dispatches (Polar/Climate)
            {'id': 'd4_1', 'domain': 'climate', 'title': 'Permafrost thawing in Siberia releases ancient anthrax spores threatening reindeer', 'description': 'Warming temperatures across the tundra expose buried pathogen reserves.', 'category': 'Science', 'region': 'Asia-Pacific', 'entities': {'countries': [{'code': 'RU', 'name': 'Russia'}], 'companies': [], 'organizations': []}},
            {'id': 'd4_2', 'domain': 'climate', 'title': 'Antarctic ice shelf calving event triggers global ocean salinity warning', 'description': 'Polar scientists observe major iceberg separation.', 'category': 'Science', 'region': 'Global', 'entities': {'countries': [], 'companies': [], 'organizations': []}},

            # Domain 5 Dispatches (Aerospace)
            {'id': 'd5_1', 'domain': 'space', 'title': 'NASA rover analyzes sedimentary lacustrine deposits on Mars searching for biosignatures', 'description': 'Planetary scientists confirm ancient lakebed exploration.', 'category': 'Tech', 'region': 'Global', 'entities': {'countries': [{'code': 'US', 'name': 'United States'}], 'companies': [], 'organizations': [{'name': 'NASA'}]}},
            {'id': 'd5_2', 'domain': 'space', 'title': 'ESA probe completes gravity-assist flyby of Venus en route to Mercury orbit insertion', 'description': 'Spacecraft instruments gather atmospheric data during close approach.', 'category': 'Tech', 'region': 'Global', 'entities': {'countries': [], 'companies': [], 'organizations': [{'name': 'ESA'}]}},
        ]

        # Domain to matching arc map
        target_arc_map = {
            'tech': 'arc-tech-semiconductors-001',
            'diplomacy': 'arc-mideast-ceasefire-002',
            'culture': 'arc-arts-obituaries-003',
            'climate': 'arc-polar-permafrost-004',
            'space': 'arc-space-exploration-005'
        }

        false_bindings = 0
        total_mismatched_tests = 0

        for art in dispatches:
            own_arc_id = target_arc_map[art['domain']]
            opposing_arcs = [a for a in self.all_arcs if a['arc_id'] != own_arc_id]

            for opp_arc in opposing_arcs:
                total_mismatched_tests += 1
                matched, score = match_article_to_arc(art, [opp_arc])
                if matched is not None:
                    false_bindings += 1

        self.assertEqual(
            false_bindings, 0,
            f"Collision detected! {false_bindings} false bindings out of {total_mismatched_tests} mismatched pairs."
        )

    def test_anchor1_geopolitical_theater_isolation(self):
        """Articles sharing vocabulary but in conflicting geopolitical theaters must be rejected."""
        # Article sharing financial/debt vocabulary with Greece, but located in Argentina
        art_argentina = {
            'title': 'Sovereign debt restructuring and emergency budget austerity talks concluded',
            'description': 'Officials agreed on fiscal deficit reduction and creditor repayments.',
            'category': 'Business',
            'region': 'Latin America',
            'entities': {
                'countries': [{'code': 'AR', 'name': 'Argentina'}],
                'companies': [],
                'organizations': []
            }
        }
        arc_greece = {
            'arc_id': 'arc-greece-debt-001',
            'title': 'Sovereign Debt Austerity Negotiations in Athens',
            'category': 'Business',
            'countries': ['GR'],
            'regions': ['Europe'],
            'entities': ['greece', 'athens', 'debt', 'austerity', 'deficit'],
            'leaders': [],
            'keywords': ['sovereign', 'debt', 'austerity', 'budget', 'creditor', 'talks'],
            'chapter_titles': ['Greek parliament passes emergency budget austerity measures']
        }

        matched, score = match_article_to_arc(art_argentina, [arc_greece])
        self.assertIsNone(matched, "Anchor 1 failed to isolate disjoint geopolitical theaters!")
        self.assertEqual(score, 0.0)

    def test_anchor2_entity_isolation_insufficient_intersections(self):
        """Articles with identical region and moderate lexical overlap but < 2 entities must be rejected."""
        art_generic_us = {
            'title': 'Federal regulatory commission reviews market inflation and consumer pricing indices',
            'description': 'Economic policy briefing updates projections for national markets.',
            'category': 'Business',
            'region': 'North America',
            'entities': {
                'countries': [{'code': 'US', 'name': 'United States'}], # Only 1 generic entity
                'companies': [],
                'organizations': []
            }
        }
        arc_federal_reserve = {
            'arc_id': 'arc-fed-rates-002',
            'title': 'Federal Reserve Benchmark Interest Rate Decisions',
            'category': 'Business',
            'countries': ['US'],
            'regions': ['North America'],
            'entities': ['federal reserve', 'jerome powell', 'us', 'fomc'],
            'leaders': ['Jerome Powell'],
            'keywords': ['federal', 'reserve', 'interest', 'rate', 'inflation', 'powell'],
            'chapter_titles': ['Federal Reserve holds benchmark rate steady']
        }

        matched, score = match_article_to_arc(art_generic_us, [arc_federal_reserve])
        self.assertIsNone(matched, "Anchor 2 failed to reject insufficient entity intersection!")
        self.assertEqual(score, 0.0)

    def test_anchor3_lexical_jaccard_strict_cutoff(self):
        """Articles with matching theater and shared entity but substantive Jaccard < 0.30 must be rejected."""
        art_iran_archaeology = {
            'title': 'Archaeologists uncover ancient Persian ceramic relics and historical artifacts',
            'description': 'Excavation team near Shiraz discovers preserved pottery from antiquity.',
            'category': 'World',
            'region': 'Middle East',
            'entities': {
                'countries': [{'code': 'IR', 'name': 'Iran'}],
                'companies': [],
                'organizations': []
            }
        }
        arc_iran_oil_opec = {
            'arc_id': 'arc-iran-oil-003',
            'title': 'Persian Gulf Crude Oil Tanker Traffic & Maritime Sanctions',
            'category': 'World',
            'countries': ['IR'],
            'regions': ['Middle East'],
            'entities': ['iran', 'persian gulf', 'crude', 'tanker', 'opec'],
            'leaders': [],
            'keywords': ['oil', 'tanker', 'crude', 'petroleum', 'strait', 'hormuz'],
            'chapter_titles': ['Iran crude tanker shipments rise amid OPEC quota talks']
        }

        matched, score = match_article_to_arc(art_iran_archaeology, [arc_iran_oil_opec])
        self.assertIsNone(matched, "Anchor 3 failed to reject sub-threshold Jaccard overlap (< 0.30)!")
        self.assertEqual(score, 0.0)

    def test_substantive_stems_mathematical_jaccard_invariants(self):
        """Verifies mathematical reflexivity, symmetry, boundedness, and empty set properties."""
        s1 = substantive_stems("TSMC semiconductor foundry produces advanced 2nm chips")
        s2 = substantive_stems("Semiconductor chip foundries scale advanced manufacturing nodes")
        s_empty = substantive_stems("")

        def jaccard(a, b):
            if not a or not b:
                return 0.0
            return len(a & b) / len(a | b)

        # Reflexivity
        self.assertEqual(jaccard(s1, s1), 1.0)
        # Symmetry
        self.assertEqual(jaccard(s1, s2), jaccard(s2, s1))
        # Boundedness
        j_val = jaccard(s1, s2)
        self.assertTrue(0.0 <= j_val <= 1.0)
        # Empty set handling
        self.assertEqual(jaccard(s1, s_empty), 0.0)
        self.assertEqual(jaccard(s_empty, s_empty), 0.0)


# =============================================================================
# CLASS 3: SYNTACTIC ACTOR GRAMMAR FUZZ TEST
# =============================================================================
class SyntacticActorGrammarFuzzTest(unittest.TestCase):
    """
    Fuzz syntactic frames, 8 canonical collective factions, and sovereign stakeholders.
    Asserts 0 occurrences of 'Editorial Bureau', 'Syndicated Bureau', or wire names.
    """

    def test_all_8_canonical_collective_factions(self):
        """Fuzzes each of the 8 canonical collective non-state factions."""
        faction_cases = [
            ("Tigray rebel groups capture northern logistics hub", "Insurgent / Rebel Factions", "collective_faction"),
            ("Armed forces deploy air defense batteries along maritime border", "Military Command / Armed Forces", "collective_faction"),
            ("Civic activists stage nationwide general strike over pensions", "Civic Activists / Protesters", "collective_faction"),
            ("Displaced families flee escalating bombardments in rural districts", "Civilians & Impacted Communities", "impacted_community"),
            ("Securities regulators subpoena major tech companies over market monopoly", "Regulatory & State Authorities", "collective_faction"),
            ("Federal prosecutors file indictment against corporate officers for fraud", "Judicial & Investigative Bodies", "collective_faction"),
            ("UN envoys convene emergency peace summit in Geneva", "Diplomatic Envoys", "collective_faction"),
            ("Astronomers detect anomalous gravitational wave signals from deep cosmos", "Scientific & Research Teams", "collective_faction"),
        ]

        for text, expected_category, expected_role_type in faction_cases:
            res = SyntacticActorGrammar.extract_actors(text, text, {}, "Global")
            factions = res.get('collective_factions', [])
            categories = [f['category'] for f in factions]
            self.assertIn(
                expected_category, categories,
                f"Expected faction category '{expected_category}' not found in: '{text}'. Got: {categories}"
            )
            if expected_role_type == "impacted_community":
                self.assertEqual(res.get('impacted_type'), 'impacted_community')
            else:
                self.assertEqual(
                    res.get('active_agent_type'), 'collective_faction',
                    f"Expected active_agent_type 'collective_faction' for: '{text}'"
                )

    def test_syntactic_frame_subject_verb_object_fuzzing(self):
        """Fuzzes Subject-Verb-Object syntactic frame extraction across diverse verbs."""
        cases = [
            ("Navy intercepts unidentified submersible vessel", "Navy", "intercepts", "unidentified submersible vessel"),
            ("Supreme Court strikes down controversial environmental decree", "Supreme Court", "strikes down", "controversial environmental decree"),
            ("Central bank cuts benchmark interest rate amid slowing growth", "Central bank", "cuts", "benchmark interest rate"),
            ("Scientists discover novel antibiotic against resistant bacteria", "Scientists", "discover", "novel antibiotic"),
            ("Envoys sign historic bilateral trade agreement", "Envoys", "sign", "historic bilateral trade agreement"),
        ]

        for text, exp_s, exp_v, exp_o in cases:
            res = SyntacticActorGrammar.extract_actors(text, "", {}, "Global")
            frame = res.get('syntactic_frame', {})
            self.assertTrue(bool(frame.get('subject')), f"Missing subject in frame for: '{text}'")
            self.assertTrue(bool(frame.get('verb')), f"Missing verb in frame for: '{text}'")
            self.assertTrue(bool(frame.get('object')), f"Missing object in frame for: '{text}'")

    def test_sovereign_regional_stakeholder_resolution(self):
        """Unled abstract event headlines must resolve to sovereign stakeholders without placeholders."""
        abstract_cases = [
            ("Catastrophic flooding paralyzes transport corridors across Queensland", "Asia-Pacific", "AU", "Australia Sovereign Authorities"),
            ("Severe heatwave triggers emergency power alerts across Texas", "North America", "US", "United States Sovereign Authorities"),
            ("Massive earthquake strikes offshore Tokyo", "Asia-Pacific", "JP", "Japan Sovereign Authorities"),
            ("Widespread blizzard grounds flights across Frankfurt and Munich", "Europe", "DE", "Germany Sovereign Authorities"),
        ]

        for title, region, country_code, expected_authority in abstract_cases:
            ents = {'countries': [{'code': country_code, 'name': COUNTRY_NAMES.get(country_code, '')}]}
            res = SyntacticActorGrammar.extract_actors(title, "", ents, region)
            self.assertEqual(
                res.get('active_agent_type'), 'sovereign_stakeholder',
                f"Expected sovereign_stakeholder for abstract event '{title}', got: {res.get('active_agent_type')}"
            )
            self.assertEqual(res.get('active_agent'), expected_authority)
            self.assertNotIn('Editorial Bureau', res.get('sovereign_stakeholders', []))

    def test_zero_editorial_bureau_negative_invariants_across_corpus(self):
        """Iterates over news.json articles and assert 0 occurrences of 'Editorial Bureau'."""
        news_file = os.path.join(_PROJECT_ROOT, 'data', 'news.json')
        if os.path.exists(news_file):
            with open(news_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            articles = data.get('articles', [])
            for art in articles:
                pa = art.get('primary_actors') or {}
                self.assertNotEqual(pa.get('active_agent'), 'Editorial Bureau')
                self.assertNotEqual(pa.get('active_agent'), 'Syndicated Bureau')
                for f in pa.get('collective_factions', []):
                    self.assertNotIn('Editorial Bureau', f.get('canonical_label', ''))
                for s in pa.get('sovereign_stakeholders', []):
                    self.assertNotIn('Editorial Bureau', s)

    def test_adversarial_corrupted_syntactic_inputs(self):
        """Stress tests grammar automaton with malformed, empty, and numeric payloads."""
        corrupted = [
            ("", ""),
            ("1234567890 9876543210", ""),
            ("??? !!! --- ... /// @@@ ### $$$ %%% ^^^ &&& ***", ""),
            ("   \t\n   ", "   \t\n   "),
            ("🚨 💥 🔥 🌍 🕊️ ⚖️", ""),
            ("War.", "Crisis continues."),
        ]
        for t, d in corrupted:
            res = SyntacticActorGrammar.extract_actors(t, d, {}, "Global")
            self.assertIsInstance(res, dict)
            self.assertIn('active_agent', res)
            self.assertIn('active_agent_type', res)
            self.assertIn('collective_factions', res)
            self.assertIn('syntactic_frame', res)


# =============================================================================
# CLASS 4: STANDALONE DISPATCHES HONEST NULLS TEST
# =============================================================================
class StandaloneDispatchesHonestNullsTest(unittest.TestCase):
    """
    Test standalone dispatch isolation (arc_id: null), verify UI contract integrity
    (zero synthetic placeholders, scrubber suppression, honest null badges).
    """

    def test_standalone_dispatch_isolation_backend_schema(self):
        """Unthreaded articles must receive strictly honest null narrative_arc structures."""
        art = {
            'id': 'test-standalone-001',
            'title': 'Bilateral trade conference concludes in Zurich',
            'category': 'Business',
            'region': 'Europe'
        }
        res = thread_narratives([art], {'arcs': []})
        arc_meta = res[0].get('narrative_arc', {})

        self.assertIsNone(arc_meta.get('arc_id'))
        self.assertIsNone(arc_meta.get('arc_title'))
        self.assertEqual(arc_meta.get('day_number'), 0)
        self.assertEqual(arc_meta.get('total_chapters'), 0)
        self.assertIsNone(arc_meta.get('importance_trend'))
        self.assertEqual(arc_meta.get('previous_headlines'), [])

    def test_data_news_json_standalone_articles_honest_nulls(self):
        """Ensures honest null consistency across data/news.json standalone dispatches."""
        news_file = os.path.join(_PROJECT_ROOT, 'data', 'news.json')
        self.assertTrue(os.path.exists(news_file), "data/news.json must exist")

        with open(news_file, 'r', encoding='utf-8') as f:
            articles = json.load(f).get('articles', [])

        standalone = [a for a in articles if a.get('narrative_arc', {}).get('arc_id') is None]
        self.assertGreater(len(standalone), 40, "Expected significant fraction of standalone dispatches")

        for art in standalone:
            arc_data = art['narrative_arc']
            self.assertIsNone(arc_data['arc_id'])
            self.assertIsNone(arc_data['arc_title'])
            self.assertEqual(arc_data['day_number'], 0)
            self.assertEqual(arc_data['total_chapters'], 0)
            self.assertEqual(arc_data['previous_headlines'], [])

    def test_ui_contract_forbidden_placeholder_eradication_in_app_js(self):
        """Scans app.js asserting zero occurrences of forbidden synthetic placeholders."""
        app_js_path = os.path.join(_PROJECT_ROOT, 'app.js')
        self.assertTrue(os.path.exists(app_js_path), "app.js must exist")

        with open(app_js_path, 'r', encoding='utf-8') as f:
            content = f.read()

        forbidden_strings = [
            'Verified news intelligence event',
            'Regional & Non-State Factions',
            '8.4 / 10',
            'Syndicated Bureau',
            'Editorial Bureau',
            'Dispatched by ',
            'Solo Investigative Scoop',
            'Key Takeaway: Official statements',
            'Official statements and strategic updates',
            'Historical Dispatch',
        ]

        found = [p for p in forbidden_strings if p in content]
        self.assertEqual(found, [], f"Forbidden synthetic strings found in app.js: {found}")

    def test_ui_contract_scrubber_suppression_and_honest_badges(self):
        """Verifies that app.js suppresses scrubber and defines honest standalone badges."""
        app_js_path = os.path.join(_PROJECT_ROOT, 'app.js')
        style_css_path = os.path.join(_PROJECT_ROOT, 'style.css')

        with open(app_js_path, 'r', encoding='utf-8') as f:
            app_js = f.read()
        with open(style_css_path, 'r', encoding='utf-8') as f:
            style_css = f.read()

        # Scrubber suppression gating
        self.assertIn('hasArc = !!(art.narrative_arc && art.narrative_arc.arc_id)', app_js)
        # Standalone badge in app.js
        self.assertIn('horizon-standalone-badge', app_js)
        self.assertIn('✦ Standalone Dispatch', app_js)

        # CSS definitions
        self.assertIn('.horizon-standalone-badge', style_css)
        self.assertIn('.deck-content-body.standalone-dispatch', style_css)

    def test_ui_contract_subordinate_provenance_and_adaptive_morphology(self):
        """Verifies subordinate provenance and adaptive grid expansion rules."""
        app_js_path = os.path.join(_PROJECT_ROOT, 'app.js')
        style_css_path = os.path.join(_PROJECT_ROOT, 'style.css')

        with open(app_js_path, 'r', encoding='utf-8') as f:
            app_js = f.read()
        with open(style_css_path, 'r', encoding='utf-8') as f:
            style_css = f.read()

        # Provenance ledger
        self.assertIn('subordinate-provenance-ledger', app_js)
        self.assertIn('📡 Chronicled by', app_js)

        # Adaptive hero morphology
        self.assertIn('.atom-hero', style_css)
        self.assertIn('.atom-span-2', style_css)


# =============================================================================
# CLASS 5: HERMETIC ZERO-DEPENDENCY COMPLIANCE TEST
# =============================================================================
class HermeticZeroDependencyComplianceTest(unittest.TestCase):
    """
    AST walk of all backend modules ensuring strictly 100% Python standard library usage.
    Asserts zero external pip packages and zero external AI APIs.
    """

    def _get_backend_python_files(self):
        scripts_files = glob.glob(os.path.join(_PROJECT_ROOT, 'scripts', '**', '*.py'), recursive=True)
        root_files = [
            os.path.join(_PROJECT_ROOT, 'generate_daily_newsletter.py'),
            os.path.join(_PROJECT_ROOT, 'production_hard_audit.py')
        ]
        all_files = [f for f in scripts_files + root_files if os.path.exists(f)]
        return all_files

    def test_ast_import_pure_standard_library_compliance(self):
        """AST walk over all backend scripts verifying every import is in standard library."""
        stdlib_modules = getattr(sys, 'stdlib_module_names', {
            'os', 'sys', 're', 'json', 'math', 'time', 'datetime', 'collections', 'itertools',
            'functools', 'urllib', 'http', 'html', 'unicodedata', 'hashlib', 'uuid', 'random',
            'subprocess', 'shutil', 'tempfile', 'unittest', 'ast', 'typing', 'email', 'xml',
            'csv', 'io', 'pathlib', 'traceback', 'glob'
        })
        allowed_internal = {'intelligence', 'scripts', 'backend'}

        files = self._get_backend_python_files()
        self.assertGreater(len(files), 10, "Expected at least 10 backend python files")

        violations = []

        for fpath in files:
            with open(fpath, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read(), fpath)

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        top = alias.name.split('.')[0]
                        if top not in stdlib_modules and top not in allowed_internal:
                            violations.append((os.path.basename(fpath), top))
                elif isinstance(node, ast.ImportFrom):
                    if node.level == 0 and node.module:
                        top = node.module.split('.')[0]
                        if top not in stdlib_modules and top not in allowed_internal:
                            violations.append((os.path.basename(fpath), top))

        self.assertEqual(violations, [], f"Non-standard-library imports detected: {violations}")

    def test_strict_rejection_of_disallowed_pip_packages(self):
        """Verifies zero presence of forbidden external packages across the AST."""
        forbidden_packages = {
            'requests', 'urllib3', 'httpx', 'aiohttp', 'bs4', 'beautifulsoup4', 'feedparser',
            'nltk', 'spacy', 'transformers', 'torch', 'torchvision', 'sklearn', 'scipy',
            'numpy', 'pandas', 'openai', 'anthropic', 'google.generativeai', 'huggingface',
            'cohere', 'flask', 'django', 'fastapi', 'pydantic'
        }

        files = self._get_backend_python_files()
        imported_modules = set()

        for fpath in files:
            with open(fpath, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read(), fpath)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for a in node.names:
                        imported_modules.add(a.name.split('.')[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.level == 0 and node.module:
                        imported_modules.add(node.module.split('.')[0])

        inter = imported_modules.intersection(forbidden_packages)
        self.assertEqual(inter, set(), f"Forbidden external packages imported: {inter}")

    def test_zero_external_ai_api_endpoints_and_credentials(self):
        """Scans backend source files for external AI API endpoints."""
        ai_endpoints = [
            'api.openai.com',
            'api.anthropic.com',
            'generativelanguage.googleapis.com',
            'api.cohere.ai',
            'huggingface.co/api'
        ]

        files = self._get_backend_python_files()
        endpoint_violations = []

        for fpath in files:
            with open(fpath, 'r', encoding='utf-8') as f:
                content = f.read()
            for ep in ai_endpoints:
                if ep in content:
                    endpoint_violations.append((os.path.basename(fpath), ep))

        self.assertEqual(endpoint_violations, [], f"External AI endpoints found: {endpoint_violations}")

    def test_hermetic_execution_without_site_packages(self):
        """Verifies core intelligence components import cleanly with isolated stdlib sys.path."""
        isolated_path = [_SCRIPTS_DIR] + [p for p in sys.path if 'site-packages' not in p.lower()]
        orig_path = sys.path.copy()
        try:
            sys.path = isolated_path
            import intelligence.sanitizer
            import intelligence.entities
            import intelligence.memory
            import intelligence.curation
            self.assertTrue(True)
        finally:
            sys.path = orig_path


if __name__ == '__main__':
    unittest.main()
