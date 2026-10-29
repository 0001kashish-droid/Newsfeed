# Copyright (c) 2026 Kashish Bhushan — News Colossal
# Test Suite: Milestone 2 — Syntactic 5W1H Actor Grammar & Collective Factions (R2, R6)
"""
Verifies Requirement R2 (Syntactic 5W1H Actor Grammar) and R6 (Pure Standard Library Constraint):
1. Pronoun-Acronym Collision Resistance (WHO vs 'who', US vs 'us', UN vs 'un', EU vs 'eu').
2. Syntactic 5W1H Actor Extraction:
   - Active Agent & Active Agent Type ('leader', 'collective_faction', 'sovereign_stakeholder', 'syntactic_subject').
   - Impacted Population & Impacted Type ('impacted_community', 'state_body').
   - Syntactic Frame (subject, verb, object).
3. 8 Canonical Collective Factions (Insurgents, Armed Forces, Protesters, Civilians, Regulators, Courts, Envoys, Researchers).
4. Sovereign Regional Stakeholder Resolution when leaders and factions are absent.
5. Strict Negative Invariants: Zero occurrences of 'Editorial Bureau', 'Syndicated Bureau', or quarantined wire names.
6. Persistent Dataset Integrity across all 134 articles in data/news.json.
"""

import os
import sys
import json
import unittest

_TEST_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_TEST_DIR)
_SCRIPTS_DIR = os.path.join(_PROJECT_ROOT, 'scripts')

if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)

from intelligence.entities import (
    extract_entities,
    SyntacticActorGrammar,
    _COUNTRY_MAPPINGS,
    _ORG_MAPPINGS,
    ORGANIZATION_LEXICON,
    COUNTRY_LEXICON
)
from intelligence.sanitizer import (
    PUBLISHER_QUARANTINE_SET,
    is_quarantined_publisher
)


class TestPronounAcronymCollisionResistance(unittest.TestCase):
    """
    Verifies that lowercase everyday English pronouns ('who', 'us', 'un', 'eu')
    are never misclassified as sovereign states or global organizations.
    """

    def test_default_dictionaries_exclude_lowercase_pronouns(self):
        """Lowercase 'us' and 'who' must be absent from pattern lexicons."""
        self.assertNotIn('us', _COUNTRY_MAPPINGS['US'])
        self.assertIn('US', _COUNTRY_MAPPINGS['US'])
        self.assertNotIn('who', _ORG_MAPPINGS['WHO'])
        self.assertIn('WHO', _ORG_MAPPINGS['WHO'])
        self.assertNotIn('un', _ORG_MAPPINGS['UN'])
        self.assertIn('UN', _ORG_MAPPINGS['UN'])
        self.assertNotIn('eu', _COUNTRY_MAPPINGS['EU'])
        self.assertIn('EU', _COUNTRY_MAPPINGS['EU'])

    def test_pronoun_who_in_relative_clauses(self):
        """Relative pronoun 'who' must produce 0 WHO organization entities."""
        cases = [
            "Eva Marie Saint, who won an Oscar for 'On the Waterfront', dies at 102",
            "Flydubai attack investigation widens as alleged hijacker's training in New Zealand scrutinised",
            "Evicted pensioner who sparked Spain housing protests dies: tenant union",
            "Abby Choi's ex-father-in-law a 'cunning old fox' who clung to her wealth, court told",
            "The doctor who treated the first patient described the symptoms",
            "Who is responsible for the recent maritime security breach?"
        ]
        for title in cases:
            with self.subTest(title=title):
                ents = extract_entities(title)
                org_names = [o['name'] for o in ents.get('organizations', [])]
                self.assertNotIn('WHO', org_names, f"False WHO extracted from: '{title}'")

    def test_pronoun_us_in_clauses(self):
        """Object pronoun 'us' must produce 0 US country entities."""
        cases = [
            "The Social Reckoning is a tepid thriller that reminds us of how we got here",
            "Let us examine the economic factors driving the transition",
            "What the latest findings tell us about deep space exploration",
            "The author asks us to reconsider historical perspectives"
        ]
        for title in cases:
            with self.subTest(title=title):
                ents = extract_entities(title)
                country_codes = [c['code'] for c in ents.get('countries', [])]
                self.assertNotIn('US', country_codes, f"False US extracted from: '{title}'")

    def test_genuine_uppercase_acronyms_preserved(self):
        """Authentic uppercase WHO, US, UN, EU must be correctly detected."""
        # WHO
        res_who = extract_entities("WHO warns of new infectious disease spread across regions")
        self.assertIn('WHO', [o['name'] for o in res_who.get('organizations', [])])

        res_who_full = extract_entities("World Health Organization declares conclusion of emergency")
        self.assertIn('WHO', [o['name'] for o in res_who_full.get('organizations', [])])

        # US
        res_us = extract_entities("US, Russia explore gas sale to Europe amid Ukraine war")
        country_codes = [c['code'] for c in res_us.get('countries', [])]
        self.assertIn('US', country_codes)
        self.assertIn('RU', country_codes)

        res_us_dots = extract_entities("U.S. sanctions imposed on technology exporters")
        self.assertIn('US', [c['code'] for c in res_us_dots.get('countries', [])])

        res_us_full = extract_entities("United States announces bilateral trade agreement")
        self.assertIn('US', [c['code'] for c in res_us_full.get('countries', [])])

        # UN
        res_un = extract_entities("UN peacekeepers deployed along disputed border zone")
        self.assertIn('UN', [o['name'] for o in res_un.get('organizations', [])])

        # EU
        res_eu = extract_entities("EU introduces comprehensive artificial intelligence regulation")
        self.assertIn('EU', [c['code'] for c in res_eu.get('countries', [])])


class TestCollectiveFactionsGrammar(unittest.TestCase):
    """
    Verifies that SyntacticActorGrammar correctly extracts the 8 canonical
    collective non-state factions and maps them to appropriate labels.
    """

    def test_category_1_insurgent_rebel_factions(self):
        title = "Tigray rebel groups ‘forcibly recruiting boys as young as 15’ as fighting spreads"
        desc = "Civilians try to flee as men and boys rounded up on streets by new alliance in Ethiopia"
        res = extract_entities(title, desc, region="Global")
        actors = res['primary_actors']

        self.assertEqual(actors['active_agent'], "Tigray rebel groups")
        self.assertEqual(actors['active_agent_type'], "collective_faction")
        self.assertTrue(any(f['category'] == "Insurgent / Rebel Factions" for f in actors['collective_factions']))
        self.assertIn("boys as young as 15", actors['impacted_population'])
        self.assertEqual(actors['impacted_type'], "impacted_community")
        self.assertEqual(actors['syntactic_frame']['subject'], "Tigray rebel groups")
        self.assertEqual(actors['syntactic_frame']['verb'], "recruiting")
        self.assertEqual(actors['syntactic_frame']['object'], "boys as young as 15")

    def test_category_2_military_command_armed_forces(self):
        title = "Military command launches airstrikes against insurgent positions"
        res = extract_entities(title)
        actors = res['primary_actors']

        self.assertEqual(actors['active_agent'], "Military command")
        self.assertEqual(actors['active_agent_type'], "collective_faction")
        self.assertTrue(any(f['category'] == "Military Command / Armed Forces" for f in actors['collective_factions']))
        self.assertEqual(actors['syntactic_frame']['verb'], "launches")

    def test_category_3_civic_activists_protesters(self):
        title = "Civic activists march through central district demanding electoral reforms"
        res = extract_entities(title)
        actors = res['primary_actors']

        self.assertEqual(actors['active_agent'], "Civic activists")
        self.assertEqual(actors['active_agent_type'], "collective_faction")
        self.assertTrue(any(f['category'] == "Civic Activists / Protesters" for f in actors['collective_factions']))

    def test_category_4_civilians_impacted_communities(self):
        title = "Displaced families seek emergency shelter as severe floods submerge villages"
        res = extract_entities(title)
        actors = res['primary_actors']

        self.assertTrue(any(f['category'] == "Civilians & Impacted Communities" for f in actors['collective_factions']))
        self.assertEqual(actors['impacted_type'], "impacted_community")
        self.assertIn("Displaced families", actors['impacted_population'])

    def test_category_5_regulatory_state_authorities(self):
        title = "Regulators fine tech conglomerate over competition and antitrust violations"
        res = extract_entities(title)
        actors = res['primary_actors']

        self.assertEqual(actors['active_agent'], "Regulators")
        self.assertEqual(actors['active_agent_type'], "collective_faction")
        self.assertTrue(any(f['category'] == "Regulatory & State Authorities" for f in actors['collective_factions']))
        self.assertEqual(actors['syntactic_frame']['verb'], "fine")

    def test_category_6_judicial_investigative_bodies(self):
        title = "CBI files closure report in Bihar court"
        res = extract_entities(title)
        actors = res['primary_actors']

        self.assertEqual(actors['active_agent'], "CBI")
        self.assertEqual(actors['active_agent_type'], "collective_faction")
        self.assertTrue(any(f['category'] == "Judicial & Investigative Bodies" for f in actors['collective_factions']))
        self.assertEqual(actors['syntactic_frame']['verb'], "files")
        self.assertEqual(actors['syntactic_frame']['object'], "closure report")

    def test_category_7_diplomatic_envoys(self):
        title = "Diplomats sign historic maritime border demarcation treaty"
        res = extract_entities(title)
        actors = res['primary_actors']

        self.assertEqual(actors['active_agent'], "Diplomats")
        self.assertEqual(actors['active_agent_type'], "collective_faction")
        self.assertTrue(any(f['category'] == "Diplomatic Envoys" for f in actors['collective_factions']))
        self.assertEqual(actors['syntactic_frame']['verb'], "sign")

    def test_category_8_scientific_research_teams(self):
        title = "Researchers discover novel mechanism regulating cellular metabolism"
        res = extract_entities(title)
        actors = res['primary_actors']

        self.assertEqual(actors['active_agent'], "Researchers")
        self.assertEqual(actors['active_agent_type'], "collective_faction")
        self.assertTrue(any(f['category'] == "Scientific & Research Teams" for f in actors['collective_factions']))
        self.assertEqual(actors['syntactic_frame']['verb'], "discover")


class TestSovereignStakeholdersAndLeaderPriority(unittest.TestCase):
    """
    Verifies world leader prioritization and sovereign regional stakeholder resolution.
    """

    def test_world_leader_priority(self):
        """World leaders take precedence as active agents."""
        title = "Volodymyr Zelenskyy warns of renewed missile counteroffensive"
        res = extract_entities(title)
        actors = res['primary_actors']

        self.assertEqual(actors['active_agent'], "Volodymyr Zelenskyy")
        self.assertEqual(actors['active_agent_type'], "leader")
        self.assertIn("Volodymyr Zelenskyy", actors['leaders'])

    def test_sovereign_country_stakeholder_fallback(self):
        """Abstract stories with sovereign country mention resolve to sovereign authorities."""
        title = "Diplomatic talks resume on uranium enrichment protocols"
        desc = "Delegations from Iran met to review inspection requirements"
        res = extract_entities(title, desc)
        actors = res['primary_actors']

        self.assertEqual(actors['active_agent'], "Iran Sovereign Authorities")
        self.assertEqual(actors['active_agent_type'], "sovereign_stakeholder")
        self.assertIn("Iran", actors['sovereign_stakeholders'])

    def test_regional_stakeholder_fallback(self):
        """Stories without specific leader or country resolve to regional stakeholders."""
        title = "Regional trade summit convenes to evaluate tariff reductions"
        res = extract_entities(title, region="Asia-Pacific")
        actors = res['primary_actors']

        self.assertEqual(actors['active_agent'], "Asia-Pacific Regional Stakeholders")
        self.assertEqual(actors['active_agent_type'], "sovereign_stakeholder")
        self.assertIn("Asia-Pacific Regional Stakeholders", actors['sovereign_stakeholders'])

    def test_syntactic_subject_agent(self):
        """Authentic non-leader, non-faction actors are captured as syntactic_subject."""
        title = "Apple introduces breakthrough silicon architecture for mobile processors"
        res = extract_entities(title)
        actors = res['primary_actors']

        self.assertEqual(actors['active_agent'], "Apple")
        self.assertEqual(actors['active_agent_type'], "syntactic_subject")
        self.assertEqual(actors['syntactic_frame']['verb'], "introduces")


class TestNegativeInvariantsAndQuarantine(unittest.TestCase):
    """
    Verifies strict negative invariants:
    - 0 occurrences of 'Editorial Bureau' or 'Syndicated Bureau'.
    - Quarantined wire publishers are mathematically barred from actor positions.
    """

    def test_zero_editorial_bureau_in_all_extractions(self):
        test_inputs = [
            ("Peace talks resume in Vienna - Reuters", "Reporting from Vienna"),
            ("Tech giant reports quarterly earnings (AP)", ""),
            ("Emergency summit concludes | BBC News", "London, UK"),
            ("Eva Marie Saint, who won an Oscar, dies at 102", ""),
            ("Single breaking news event", ""),
            ("", "")
        ]
        for title, desc in test_inputs:
            with self.subTest(title=title):
                res = extract_entities(title, desc)
                serialized = json.dumps(res)
                self.assertNotIn("Editorial Bureau", serialized)
                self.assertNotIn("Syndicated Bureau", serialized)

    def test_quarantined_wire_barred_from_active_agent(self):
        cases = [
            "Reuters reports global market surge",
            "Associated Press investigates regional water supply",
            "BBC News covers parliamentary debate"
        ]
        for title in cases:
            with self.subTest(title=title):
                res = extract_entities(title)
                actors = res['primary_actors']
                for wire in ('Reuters', 'AP', 'Associated Press', 'BBC', 'BBC News'):
                    self.assertNotEqual(actors['active_agent'], wire)

    def test_dow_jones_in_quarantine_set(self):
        """Advisory from Challenger M1 Iter 2: 'dow jones' in PUBLISHER_QUARANTINE_SET."""
        self.assertIn('dow jones', PUBLISHER_QUARANTINE_SET)
        self.assertTrue(is_quarantined_publisher('Dow Jones'))
        self.assertTrue(is_quarantined_publisher('Dow Jones News'))


class TestNewsDatasetIntegrity(unittest.TestCase):
    """
    Verifies the persistent data/news.json file satisfies all Milestone 2 invariants.
    """

    def setUp(self):
        news_path = os.path.join(_PROJECT_ROOT, 'data', 'news.json')
        with open(news_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        self.articles = self.data.get('articles', [])

    def test_all_134_articles_have_primary_actors(self):
        self.assertEqual(len(self.articles), 134)
        for art in self.articles:
            self.assertIn('primary_actors', art, f"Missing primary_actors in {art['id']}")
            actors = art['primary_actors']
            self.assertIsInstance(actors, dict)
            self.assertIn('active_agent', actors)
            self.assertIn('active_agent_type', actors)
            self.assertIn('impacted_population', actors)
            self.assertIn('impacted_type', actors)
            self.assertIn('collective_factions', actors)
            self.assertIn('leaders', actors)
            self.assertIn('sovereign_stakeholders', actors)
            self.assertIn('syntactic_frame', actors)
            self.assertIsInstance(actors['syntactic_frame'], dict)
            self.assertIn('subject', actors['syntactic_frame'])
            self.assertIn('verb', actors['syntactic_frame'])
            self.assertIn('object', actors['syntactic_frame'])

    def test_zero_editorial_bureau_across_dataset(self):
        serialized = json.dumps(self.data)
        self.assertNotIn("Editorial Bureau", serialized)
        self.assertNotIn("Syndicated Bureau", serialized)

    def test_zero_pronoun_collisions_across_dataset(self):
        """Verifies that no article extracts WHO solely from pronoun 'who'."""
        for art in self.articles:
            orgs = [o['name'] for o in art.get('entities', {}).get('organizations', [])]
            if 'WHO' in orgs:
                text = f"{art.get('title', '')} {art.get('description', '')}"
                is_real_who = (
                    'world health organization' in text.lower() or
                    'w.h.o.' in text.lower() or
                    any(tok == 'WHO' for tok in text.split())
                )
                self.assertTrue(
                    is_real_who,
                    f"False WHO pronoun collision in article {art['id']}: '{art.get('title')}'"
                )

    def test_collective_factions_diversity_across_dataset(self):
        """Verifies that authentic collective factions are extracted across the real feed."""
        categories_found = set()
        for art in self.articles:
            for f in art.get('primary_actors', {}).get('collective_factions', []):
                categories_found.add(f['category'])
        self.assertGreaterEqual(len(categories_found), 5, f"Expected rich collective factions, found: {categories_found}")


if __name__ == '__main__':
    unittest.main()
