# Copyright (c) 2026 Kashish Bhushan — News Colossal
# Adversarial Challenger Test Suite: Milestone 2 (Syntactic 5W1H Actor Grammar & Collective Factions)
"""
Adversarial Empirical Challenge for Milestone 2 (R2, R6):
1. Stress-test Non-State Collective Factions & 5W1H frames (Insurgents, Militias, Protesters, Civilians).
2. Stress-test Legal, Court, and Regulatory Actors (Supreme Court, EPA, Regulators, Courts, Prosecutors).
3. Pronoun-Acronym Collision Stress: 'who' vs 'WHO', 'us' vs 'US', 'un' vs 'UN', 'eu' vs 'EU'.
4. Sovereign Regional Fallbacks vs Honest Nulls for abstract event nouns.
5. Strict Negative Invariants: Zero 'Editorial Bureau' or 'Syndicated Bureau' fallbacks anywhere.
6. Wire Injection and Dateline Contamination Stress on Actor Extraction.
7. Verification of data/news.json persistent invariants.
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
    _ORG_MAPPINGS
)
from intelligence.sanitizer import (
    is_quarantined_publisher,
    PUBLISHER_QUARANTINE_SET,
    sanitize_dispatch
)


class TestAdversarialNonStateCollectiveFactions(unittest.TestCase):
    """
    Empirical testing of complex syntactic headline frames and collective non-state actors.
    """

    def test_tigray_rebel_groups_adversarial_variations(self):
        """
        Headline: 'Tigray rebel groups ‘forcibly recruiting boys as young as 15’ as fighting spreads'
        Must assert:
          - Active Agent: 'Tigray rebel groups'
          - Active Agent Type: 'collective_faction'
          - Faction Category: 'Insurgent / Rebel Factions'
          - Impacted Population: 'boys as young as 15'
          - Impacted Type: 'impacted_community'
          - Syntactic Frame: subject='Tigray rebel groups', verb='recruiting', object='boys as young as 15'
        """
        variants = [
            # Standard curly quotes
            "Tigray rebel groups ‘forcibly recruiting boys as young as 15’ as fighting spreads",
            # Straight single quotes
            "Tigray rebel groups 'forcibly recruiting boys as young as 15' as fighting spreads",
            # Double quotes
            'Tigray rebel groups "forcibly recruiting boys as young as 15" as fighting spreads',
            # No quotes
            "Tigray rebel groups forcibly recruiting boys as young as 15 as fighting spreads"
        ]
        for title in variants:
            with self.subTest(title=title):
                res = extract_entities(title, region="Global")
                actors = res['primary_actors']

                self.assertEqual(actors['active_agent'], "Tigray rebel groups")
                self.assertEqual(actors['active_agent_type'], "collective_faction")
                self.assertTrue(
                    any(f['category'] == "Insurgent / Rebel Factions" for f in actors['collective_factions']),
                    f"Failed to find Insurgent category in {actors['collective_factions']}"
                )
                self.assertIn("boys as young as 15", actors['impacted_population'])
                self.assertEqual(actors['impacted_type'], "impacted_community")
                self.assertEqual(actors['syntactic_frame']['subject'], "Tigray rebel groups")
                self.assertEqual(actors['syntactic_frame']['verb'], "recruiting")
                self.assertEqual(actors['syntactic_frame']['object'], "boys as young as 15")

    def test_insurgent_and_paramilitary_factions(self):
        """Test diverse non-state armed actors across international theaters."""
        cases = [
            (
                "Rapid Support Forces clash with Sudanese army near Khartoum",
                "Rapid Support Forces",
                "Insurgent / Rebel Factions",
                "Military Command / Armed Forces"
            ),
            (
                "Houthi fighters launch drone attack against commercial vessel in Red Sea",
                "Houthi fighters",
                "Insurgent / Rebel Factions",
                None
            ),
            (
                "M23 rebels seize strategic mining outpost in eastern Congo",
                "M23 rebels",
                "Insurgent / Rebel Factions",
                None
            ),
            (
                "Taliban officials enforce strict cross-border travel regulations",
                "Taliban",
                "Insurgent / Rebel Factions",
                None
            )
        ]
        for title, exp_token, exp_cat, exp_second_cat in cases:
            with self.subTest(title=title):
                res = extract_entities(title)
                actors = res['primary_actors']
                self.assertIn(
                    exp_token.lower(), actors['active_agent'].lower(),
                    f"Expected faction token '{exp_token}' in active_agent '{actors['active_agent']}'"
                )
                self.assertEqual(actors['active_agent_type'], "collective_faction")
                cats = [f['category'] for f in actors['collective_factions']]
                self.assertIn(exp_cat, cats)
                if exp_second_cat:
                    self.assertIn(exp_second_cat, cats)

    def test_civic_protesters_and_impacted_communities(self):
        """Test grassroots movements, tenant unions, and civilian populations."""
        cases = [
            (
                "Tenant unions mobilize nationwide rent strike over soaring urban housing costs",
                "Tenant unions",
                "Civic Activists / Protesters"
            ),
            (
                "Displaced persons arrive at southern border crossing seeking humanitarian aid",
                None,
                "Civilians & Impacted Communities"
            ),
            (
                "Demonstrators surround city hall after council approves austerity budget",
                "Demonstrators",
                "Civic Activists / Protesters"
            )
        ]
        for title, exp_agent, exp_cat in cases:
            with self.subTest(title=title):
                res = extract_entities(title)
                actors = res['primary_actors']
                cats = [f['category'] for f in actors['collective_factions']]
                self.assertIn(exp_cat, cats)
                if exp_agent:
                    self.assertIn(exp_agent, actors['active_agent'])


class TestAdversarialLegalAndRegulatoryActors(unittest.TestCase):
    """
    Stress-testing legal, judicial, and regulatory institutional actors.
    """

    def test_supreme_court_strikes_down_epa_regulation(self):
        """
        Headline: 'Supreme Court strikes down controversial EPA regulation'
        Must assert:
          - Active Agent: 'Supreme Court'
          - Active Agent Type: 'collective_faction'
          - Faction: 'Judicial & Investigative Bodies'
          - Factions contain both 'Judicial & Investigative Bodies' and 'Regulatory & State Authorities'
        """
        title = "Supreme Court strikes down controversial EPA regulation"
        res = extract_entities(title)
        actors = res['primary_actors']

        self.assertEqual(actors['active_agent'], "Supreme Court")
        self.assertEqual(actors['active_agent_type'], "collective_faction")
        cats = [f['category'] for f in actors['collective_factions']]
        self.assertIn("Judicial & Investigative Bodies", cats)
        self.assertIn("Regulatory & State Authorities", cats)
        self.assertEqual(actors['syntactic_frame']['subject'], "Supreme Court")
        self.assertEqual(actors['syntactic_frame']['verb'], "strikes")

    def test_regulatory_watchdogs_and_courts(self):
        cases = [
            (
                "Federal Trade Commission probes tech giants over AI market dominance",
                ("Federal Trade Commission",),
                "collective_faction",
                "probes",
                "Regulatory & State Authorities"
            ),
            (
                "Grand jury indicts former cabinet official on corruption charges",
                ("Grand jury",),
                "collective_faction",
                "indicts",
                "Judicial & Investigative Bodies"
            ),
            (
                "European Commission fines chipmaker over anticompetitive rebate practices",
                ("European Commission",),
                "collective_faction",
                "fines",
                "Regulatory & State Authorities"
            ),
            (
                "Special counsel interviews key intelligence witnesses in security inquiry",
                ("Special counsel",),
                "collective_faction",
                "",
                "Judicial & Investigative Bodies"
            )
        ]
        for title, valid_agents, exp_type, exp_verb, exp_cat in cases:
            with self.subTest(title=title):
                res = extract_entities(title)
                actors = res['primary_actors']
                self.assertIn(actors['active_agent'], valid_agents)
                self.assertEqual(actors['active_agent_type'], exp_type)
                cats = [f['category'] for f in actors['collective_factions']]
                self.assertIn(exp_cat, cats)
                if exp_verb:
                    self.assertEqual(actors['syntactic_frame']['verb'], exp_verb)


class TestPronounAcronymCollisionAdversarialHarness(unittest.TestCase):
    """
    Adversarial stress-testing of pronoun collisions against acronyms.
    """

    def test_eva_marie_saint_and_who_collision_stress(self):
        """
        Adversarial cases using relative and interrogative 'who'.
        Must produce 0 WHO organization extractions.
        """
        adversarial_headlines = [
            "Actress Eva Marie Saint, who won an Oscar, dies at 102",
            "Actress Eva Marie Saint, who won an Academy Award for 'On the Waterfront', dies at 102",
            "The diplomat who negotiated the peace agreement reflects on two years of talks",
            "Who will control the critical minerals supply chain in the coming decade?",
            "Pensioner who organized neighborhood resistance avoids eviction",
            "Scientists who discovered the fossil explain its evolutionary significance",
            "Whomever ordered the strike must face an international inquiry, advocates urge"
        ]
        for title in adversarial_headlines:
            with self.subTest(title=title):
                res = extract_entities(title)
                org_names = [o['name'] for o in res.get('organizations', [])]
                self.assertNotIn("WHO", org_names, f"False WHO extracted from '{title}'")

    def test_us_pronoun_collision_stress(self):
        """
        Adversarial cases using objective pronoun 'us'.
        Must produce 0 US country extractions.
        """
        adversarial_headlines = [
            "The novel reminds us of the fragility of modern democracy",
            "What the new archaeological dig tells us about ancient trade routes",
            "Let us not forget the hard lessons of the financial crisis",
            "Giving us a glimpse into the future of quantum computing",
            "The warning comes to us after weeks of silent diplomatic deadlock"
        ]
        for title in adversarial_headlines:
            with self.subTest(title=title):
                res = extract_entities(title)
                country_codes = [c['code'] for c in res.get('countries', [])]
                self.assertNotIn("US", country_codes, f"False US extracted from '{title}'")

    def test_genuine_acronyms_robustly_extracted(self):
        """
        Ensure strictness did NOT break legitimate detection of WHO, US, UN, EU.
        """
        cases = [
            ("WHO declares end of emergency status for global outbreak", "WHO", "org"),
            ("U.S. and China resume bilateral military communications", "US", "country"),
            ("US Federal Reserve signals pause on interest rate adjustments", "US", "country"),
            ("UN General Assembly votes on humanitarian aid resolution", "UN", "org"),
            ("EU antitrust regulators open formal investigation into tech bundle", "EU", "country")
        ]
        for title, expected_entity, kind in cases:
            with self.subTest(title=title):
                res = extract_entities(title)
                if kind == 'org':
                    org_names = [o['name'] for o in res.get('organizations', [])]
                    self.assertIn(expected_entity, org_names, f"Missed genuine {expected_entity} in '{title}'")
                elif kind == 'country':
                    country_codes = [c['code'] for c in res.get('countries', [])]
                    self.assertIn(expected_entity, country_codes, f"Missed genuine {expected_entity} in '{title}'")


class TestSovereignFallbackAndHonestNulls(unittest.TestCase):
    """
    Stress-testing sovereign stakeholder fallbacks and honest nulls on abstract event nouns.
    """

    def test_abstract_event_nouns_resolve_to_sovereign_authorities(self):
        """
        Stories starting with abstract nouns ('Crisis', 'Talks', 'Summit', 'War')
        must NOT extract the abstract noun as an active agent, but resolve to Sovereign Authorities.
        """
        cases = [
            (
                "Crisis deepens in Lebanon as currency plunges to record lows",
                "Lebanon Sovereign Authorities",
                "sovereign_stakeholder"
            ),
            (
                "Crisis deepens in Syria as economic conditions deteriorate",
                "Syria Sovereign Authorities",
                "sovereign_stakeholder"
            ),
            (
                "Talks resume between delegations in Geneva over border dispute",
                "Switzerland Sovereign Authorities",  # Geneva triggers CH
                "sovereign_stakeholder"
            ),
            (
                "Inflation accelerates across Argentina despite austerity measures",
                "Argentina Sovereign Authorities",
                "sovereign_stakeholder"
            )
        ]
        for title, exp_agent, exp_type in cases:
            with self.subTest(title=title):
                res = extract_entities(title)
                actors = res['primary_actors']
                self.assertEqual(actors['active_agent'], exp_agent)
                self.assertEqual(actors['active_agent_type'], exp_type)

    def test_regional_stakeholder_resolution_when_unled(self):
        cases = [
            ("Regional trade summit convenes to evaluate tariff reductions", "Asia-Pacific"),
            ("Trade ministers meet for closed-door economic talks", "Asia-Pacific")
        ]
        for title, region in cases:
            with self.subTest(title=title):
                res = extract_entities(title, region=region)
                actors = res['primary_actors']
                self.assertEqual(actors['active_agent'], f"{region} Regional Stakeholders")
                self.assertEqual(actors['active_agent_type'], "sovereign_stakeholder")

    def test_honest_null_when_global_and_no_actors(self):
        """
        When a story has no leaders, no factions, no countries, and region is Global,
        active_agent must be None (Honest Null), NEVER 'Editorial Bureau'.
        """
        titles = [
            "Talks collapse following unexpected diplomatic deadlock",
            "Global markets fluctuate following unexpected economic indicator release"
        ]
        for title in titles:
            with self.subTest(title=title):
                res = extract_entities(title, region="Global")
                actors = res['primary_actors']
                self.assertIsNone(actors['active_agent'])
                self.assertIsNone(actors['active_agent_type'])


class TestNegativeAssertZeroEditorialBureau(unittest.TestCase):
    """
    Empirical assertion: 0 occurrences of 'Editorial Bureau' or 'Syndicated Bureau' anywhere.
    """

    def test_adversarial_empty_and_garbage_payloads(self):
        garbage_inputs = [
            "",
            "   ",
            "---",
            "BREAKING NEWS",
            "Opinion: Why this matters",
            "Editorial: Our view on the election",
            "Reuters",
            "Associated Press - London",
            "Staff Reports | The Washington Post",
            "12345 67890 !@#$%^&*()"
        ]
        for text in garbage_inputs:
            with self.subTest(text=text):
                res = extract_entities(text)
                serialized = json.dumps(res)
                self.assertNotIn("Editorial Bureau", serialized)
                self.assertNotIn("Syndicated Bureau", serialized)
                for wire in ("Reuters", "AP", "Associated Press", "BBC", "Agence France-Presse"):
                    self.assertNotEqual(res['primary_actors']['active_agent'], wire)

    def test_adversarial_wire_suffix_injection(self):
        """Wire attribution suffixes must never become active agents."""
        wires = ["Reuters", "AP", "AFP", "Bloomberg", "BBC News", "Dow Jones"]
        base_title = "Treasury yields drop amid bond market rally"
        for wire in wires:
            with self.subTest(wire=wire):
                title = f"{base_title} - {wire}"
                sanitized = sanitize_dispatch(title, "")
                res = extract_entities(sanitized['clean_title'])
                serialized = json.dumps(res)
                self.assertNotIn("Editorial Bureau", serialized)
                self.assertNotEqual(res['primary_actors']['active_agent'], wire)


class TestFullNewsfeedDatasetEmpiricalAudit(unittest.TestCase):
    """
    Exhaustive empirical validation of all 134 articles in data/news.json.
    """

    def setUp(self):
        path = os.path.join(_PROJECT_ROOT, 'data', 'news.json')
        with open(path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        self.articles = self.data.get('articles', [])

    def test_dataset_size_and_primary_actors_presence(self):
        self.assertEqual(len(self.articles), 134)
        for art in self.articles:
            self.assertIn('primary_actors', art)
            actors = art['primary_actors']
            for key in ('active_agent', 'active_agent_type', 'impacted_population',
                        'impacted_type', 'collective_factions', 'leaders',
                        'sovereign_stakeholders', 'syntactic_frame'):
                self.assertIn(key, actors, f"Missing key '{key}' in article {art['id']}")

    def test_zero_editorial_bureau_across_entire_news_json(self):
        raw_json = json.dumps(self.data)
        self.assertNotIn("Editorial Bureau", raw_json)
        self.assertNotIn("Syndicated Bureau", raw_json)

    def test_no_wire_publishers_in_active_agent(self):
        for art in self.articles:
            agent = art['primary_actors'].get('active_agent')
            if agent:
                self.assertFalse(
                    is_quarantined_publisher(agent),
                    f"Quarantined publisher leaked as active_agent in {art['id']}: '{agent}'"
                )

    def test_collective_factions_coverage(self):
        factions_found = []
        for art in self.articles:
            for f in art['primary_actors'].get('collective_factions', []):
                factions_found.append(f)
        self.assertGreater(len(factions_found), 10, f"Too few collective factions found: {len(factions_found)}")
        categories = set(f['category'] for f in factions_found)
        # Should span multiple distinct categories across 134 real articles
        self.assertGreaterEqual(len(categories), 5)

    def test_exact_two_legitimate_who_articles(self):
        """Verifies exactly 2 legitimate WHO articles exist in data/news.json, both referring to World Health Organization."""
        who_articles = [
            a for a in self.articles
            if any(o.get('name') == 'WHO' for o in a.get('entities', {}).get('organizations', []))
        ]
        self.assertEqual(len(who_articles), 2, f"Expected exactly 2 WHO articles, found {len(who_articles)}")
        for art in who_articles:
            text = f"{art.get('title', '')} {art.get('description', '')}"
            self.assertTrue(
                'world health organization' in text.lower() or
                'w.h.o.' in text.lower() or
                'WHO' in text.split(),
                f"Article {art['id']} has false WHO match: {text}"
            )


class TestChallengerHeadToHeadVerifications(unittest.TestCase):
    """
    Direct head-to-head empirical tests resolving defects identified in Challenger M2 Iteration 2.
    """

    def test_base_plural_verbs_match_re_verbs(self):
        """Base plural verbs must match _RE_VERBS without suffix corruption."""
        verbs = ['launch', 'pass', 'veto', 'march', 'identify', 'target', 'interview', 'renew', 'face']
        for verb in verbs:
            with self.subTest(verb=verb):
                self.assertIsNotNone(
                    SyntacticActorGrammar._RE_VERBS.search(verb),
                    f"SyntacticActorGrammar._RE_VERBS failed to match base verb: '{verb}'"
                )

    def test_head_to_head_adversarial_headlines(self):
        """Verify clean active agent extraction for Challenger challenge headlines."""
        cases = [
            ("Houthi fighters target cargo ship", "Houthi fighters", "collective_faction"),
            ("Demonstrators march through capital", "Demonstrators", "collective_faction"),
            ("Special counsel interviews key witnesses", "Special counsel", "collective_faction"),
            ("Lawmakers pass emergency funding bill", "Lawmakers", "syntactic_subject"),
            ("Pediatricians renew call to ban raw milk as anti-science rhetoric reigns", "Pediatricians", "syntactic_subject"),
            ("Burnham to meet German chancellor in Berlin to discuss security and EU ties", "Burnham", "syntactic_subject"),
        ]
        for title, exp_agent, exp_type in cases:
            with self.subTest(title=title):
                res = extract_entities(title)
                actors = res['primary_actors']
                self.assertEqual(actors['active_agent'], exp_agent, f"Failed for '{title}': got '{actors['active_agent']}'")
                if exp_type:
                    self.assertEqual(actors['active_agent_type'], exp_type)

    def test_predicate_swallowing_prevention_without_verb_anchor(self):
        """When no verb anchor is detected, do not swallow predicate into agent_faction."""
        # Unrecognized hypothetical verb 'quxies'
        res = extract_entities("Houthi fighters quxies cargo vessel across southern waters")
        actors = res['primary_actors']
        self.assertNotIn("quxies", actors['active_agent'])
        self.assertNotIn("cargo vessel", actors['active_agent'])
        self.assertEqual(actors['active_agent'], "Houthi fighters")

    def test_dataset_zero_trailing_prepositions_and_auxiliaries(self):
        """Assert 0 articles in data/news.json have active_agent ending in trailing invalid words."""
        path = os.path.join(_PROJECT_ROOT, 'data', 'news.json')
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        articles = data.get('articles', [])
        trailing_invalid = {'to', 'is', 'are', 'was', 'were', 'the', 'a', 'an', 'in', 'on', 'at', 'for', 'from', 'with', 'by', 'and', 'or', 'as'}
        bad_endings = []
        for a in articles:
            agent = a.get('entities', {}).get('primary_actors', {}).get('active_agent')
            if agent:
                words = str(agent).split()
                if words[-1].lower() in trailing_invalid:
                    bad_endings.append((a['id'], agent))
        self.assertEqual(bad_endings, [], f"Found active agents with invalid trailing words: {bad_endings}")

    def test_dataset_zero_agents_exceeding_five_words(self):
        """Assert 0 articles in data/news.json have active_agent exceeding 5 words."""
        path = os.path.join(_PROJECT_ROOT, 'data', 'news.json')
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        articles = data.get('articles', [])
        gt5 = []
        for a in articles:
            agent = a.get('entities', {}).get('primary_actors', {}).get('active_agent')
            if agent and len(str(agent).split()) > 5:
                gt5.append((a['id'], agent))
        self.assertEqual(gt5, [], f"Found active agents exceeding 5 words: {gt5}")

    def test_dataset_zero_bare_investigation_faction(self):
        """Assert 0 articles have bare 'investigation' as active agent."""
        path = os.path.join(_PROJECT_ROOT, 'data', 'news.json')
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        articles = data.get('articles', [])
        investigations = [a['id'] for a in articles if str(a.get('entities', {}).get('primary_actors', {}).get('active_agent', '')).lower() == 'investigation']
        self.assertEqual(investigations, [], f"Found bare investigation active agents: {investigations}")


if __name__ == '__main__':
    unittest.main()
