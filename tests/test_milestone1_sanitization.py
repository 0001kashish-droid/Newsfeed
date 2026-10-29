# Copyright (c) 2026 Kashish Bhushan — News Colossal
# Test Suite: Milestone 1 — Provenance Quarantine Sieve & Wire Sanitization (R1, R6)

import os
import sys
import json
import unittest

_TEST_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_TEST_DIR)
_SCRIPTS_DIR = os.path.join(_PROJECT_ROOT, 'scripts')

if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)

from intelligence.sanitizer import (
    PUBLISHER_QUARANTINE_SET,
    is_quarantined_publisher,
    normalize_text,
    sanitize_dispatch
)
from intelligence.entities import (
    _ORG_MAPPINGS,
    ORGANIZATION_LEXICON,
    extract_entities
)
from intelligence.intake import (
    normalize_title,
    run_intake,
    enrich_entities
)


class TestPublisherQuarantineSet(unittest.TestCase):
    """Verifies that the publisher quarantine set is comprehensive and rejects false matches."""

    def test_core_wire_services_present(self):
        core_wires = ['reuters', 'ap', 'associated press', 'bbc', 'bbc news', 'afp', 'bloomberg', 'upi', 'xinhua']
        for wire in core_wires:
            self.assertIn(wire, PUBLISHER_QUARANTINE_SET, f"Expected '{wire}' in PUBLISHER_QUARANTINE_SET")

    def test_is_quarantined_publisher_positives(self):
        positive_cases = [
            'Reuters', 'reuters', 'REUTERS',
            'BBC', 'BBC News', 'bbc news',
            'AP', 'Associated Press', 'The Associated Press',
            'The Guardian', 'Guardian', 'New York Times', 'NYT',
            'Agence France-Presse', 'AFP', 'Bloomberg News',
            'The Wall Street Journal', 'WSJ', 'Financial Times'
        ]
        for name in positive_cases:
            self.assertTrue(is_quarantined_publisher(name), f"Expected '{name}' to be recognized as quarantined publisher")

    def test_is_quarantined_publisher_negatives(self):
        negative_cases = [
            'WHO', 'World Health Organization',
            'White House', 'Pentagon', 'Congress', 'Supreme Court',
            'United Nations', 'UN', 'NATO', 'European Commission',
            'Apple', 'Google', 'Microsoft', 'Nvidia', 'Tesla',
            'Donald Trump', 'Emmanuel Macron', 'Friedrich Merz',
            '', None, 123
        ]
        for name in negative_cases:
            self.assertFalse(is_quarantined_publisher(name), f"Expected '{name}' to NOT be quarantined publisher")


class TestSanitizationAutomaton(unittest.TestCase):
    """Verifies each stage of the 7-stage deterministic sanitization automaton."""

    def test_stage1_nfkc_and_unescape(self):
        raw = "EU&amp;apos;s &#039;historic&#039; bill &amp; reform \u00a0in &quot;Brussels&quot;"
        res = sanitize_dispatch(raw, "")
        self.assertNotIn('&amp;', res['clean_title'])
        self.assertNotIn('&quot;', res['clean_title'])
        self.assertNotIn('&#039;', res['clean_title'])
        self.assertNotIn('\u00a0', res['clean_title'])
        self.assertIn("EU's", res['clean_title'])

    def test_stage2_wire_datelines(self):
        dateline_cases = [
            ("WASHINGTON (AP) — The President signed the executive order.",
             "The President signed the executive order."),
            ("BEIJING, Oct 23 (Reuters) - China’s central bank lowered reserve ratios.",
             "China's central bank lowered reserve ratios."),
            ("(Reuters) - Global markets rallied on positive jobs data.",
             "Global markets rallied on positive jobs data."),
            ("[AP] Washington — Congress passed the emergency funding bill.",
             "Congress passed the emergency funding bill."),
            ("MUMBAI (Reuters) — The Reserve Bank kept rates on hold.",
             "The Reserve Bank kept rates on hold.")
        ]
        for raw, expected in dateline_cases:
            res = sanitize_dispatch("Headline", raw)
            self.assertEqual(res['clean_description'], expected)
            self.assertIsNotNone(res['stripped_dateline'])

    def test_stage3_editorial_slugs(self):
        slug_cases = [
            ("EXCLUSIVE: Direct talks underway in Geneva", "Direct talks underway in Geneva", 'is_exclusive'),
            ("BREAKING: Earthquake strikes central Japan", "Earthquake strikes central Japan", 'is_breaking'),
            ("ANALYSIS: Why the semiconductor market is shifting", "Why the semiconductor market is shifting", 'is_analysis'),
            ("EXPLAINER: What the new emissions treaty requires", "What the new emissions treaty requires", 'is_explainer'),
            ("OPINION: Reforming the global energy transition", "Reforming the global energy transition", 'is_opinion'),
        ]
        for raw_title, expected_clean, expected_flag in slug_cases:
            res = sanitize_dispatch(raw_title, "Description text.")
            self.assertEqual(res['clean_title'], expected_clean)
            self.assertTrue(res['meta_flags'].get(expected_flag), f"Expected {expected_flag} in meta_flags for '{raw_title}'")

    def test_stage4_trailing_attribution_suffixes(self):
        suffix_cases = [
            ("Bollywood actor Nana Patekar dies at 75 - Reuters", "Bollywood actor Nana Patekar dies at 75"),
            ("Tech giant reports blowout quarterly earnings - BBC News", "Tech giant reports blowout quarterly earnings"),
            ("Border dispute resolved in bilateral summit | Associated Press", "Border dispute resolved in bilateral summit"),
            ("New space mission scheduled for November (Reuters)", "New space mission scheduled for November"),
            ("Clean energy investment hits milestone — The Guardian", "Clean energy investment hits milestone")
        ]
        for raw, expected in suffix_cases:
            res = sanitize_dispatch(raw, "Description.")
            self.assertEqual(res['clean_title'], expected)

    def test_stage5_embedded_attribution_clauses(self):
        clause_cases = [
            ("Christa Pike now walking after US execution went wrong, lawyer tells BBC",
             "Christa Pike now walking after US execution went wrong"),
            ("US and Lebanon protecting wanted Syrian general, BBC finds",
             "US and Lebanon protecting wanted Syrian general"),
            ("Hospital supplies reaching Gaza safely, reports Reuters",
             "Hospital supplies reaching Gaza safely"),
            ("New trade route established across Central Asia, according to the Associated Press",
             "New trade route established across Central Asia")
        ]
        for raw, expected in clause_cases:
            res = sanitize_dispatch(raw, "Description.")
            self.assertEqual(res['clean_title'], expected)

    def test_stage6_wire_footers_and_bylines(self):
        desc = "The treaty was signed at midnight. (Reporting by John Doe; Editing by Jane Smith)"
        res = sanitize_dispatch("Headline", desc)
        self.assertEqual(res['clean_description'], "The treaty was signed at midnight.")
        self.assertNotIn("Reporting by", res['clean_description'])

    def test_stage7_sentence_termination(self):
        # Description without terminal period
        res = sanitize_dispatch("Headline", "The delegate arrived in Berlin without comment")
        self.assertTrue(res['clean_description'].endswith('.'), f"Got: {res['clean_description']}")
        
        # Description with trailing ellipsis must terminate cleanly with a single period
        res2 = sanitize_dispatch("Headline", "A lawyer says the defendant is moving around her room...")
        self.assertTrue(res2['clean_description'].endswith('.'), f"Got: {res2['clean_description']}")
        self.assertFalse(res2['clean_description'].endswith('...'), f"Got: {res2['clean_description']}")


class TestEntityQuarantineIntegration(unittest.TestCase):
    """Verifies that wire publishers are completely purged from entity lexicons and extraction."""

    def test_org_mappings_lexicon_clean(self):
        self.assertNotIn('Reuters', _ORG_MAPPINGS)
        self.assertNotIn('AP', _ORG_MAPPINGS)
        self.assertNotIn('BBC', _ORG_MAPPINGS)
        self.assertNotIn('reuters', ORGANIZATION_LEXICON)
        self.assertNotIn('associated press', ORGANIZATION_LEXICON)
        self.assertNotIn('bbc', ORGANIZATION_LEXICON)

    def test_extract_entities_excludes_wire_publishers(self):
        text = "Reuters reported that the BBC and Associated Press attended the WHO briefing in Geneva."
        ents = extract_entities(text)
        org_names = [o['name'] for o in ents.get('organizations', [])]
        comp_names = [c['name'] for c in ents.get('companies', [])]
        
        self.assertIn('WHO', org_names)
        self.assertNotIn('Reuters', org_names)
        self.assertNotIn('BBC', org_names)
        self.assertNotIn('AP', org_names)
        self.assertNotIn('Reuters', comp_names)
        self.assertNotIn('BBC', comp_names)


class TestIntakePipelineIntegration(unittest.TestCase):
    """Verifies that run_intake mutates titles and descriptions and sets quarantine provenance."""

    def test_run_intake_mutates_and_quarantines(self):
        test_articles = [
            {
                'id': 'test-1',
                'title': 'EXCLUSIVE: Peace talks resume in Vienna - Reuters',
                'description': 'VIENNA (Reuters) — Diplomats met on Tuesday morning Reuters.',
                'source': 'Reuters',
                'category': 'World',
                'entities': {'organizations': [{'name': 'Reuters', 'matched': 'reuters'}]}
            }
        ]
        cleaned, stats = run_intake(test_articles)
        self.assertEqual(len(cleaned), 1)
        art = cleaned[0]
        
        self.assertEqual(art['title'], "Peace talks resume in Vienna")
        self.assertEqual(art['description'], "Diplomats met on Tuesday morning.")
        self.assertTrue(art.get('provenance', {}).get('wire_quarantined'))
        self.assertTrue(art.get('meta', {}).get('is_exclusive'))
        
        # Verify entities cleansed
        org_names = [o['name'] for o in art.get('entities', {}).get('organizations', [])]
        self.assertNotIn('Reuters', org_names)

    def test_normalize_title_standard_library(self):
        cases = [
            ("Global Summit Opens in Geneva - BBC News", "global summit opens in geneva"),
            ("Global Summit Opens in Geneva | Reuters", "global summit opens in geneva"),
            ("Global Summit Opens in Geneva — The Guardian", "global summit opens in geneva"),
            ("Global Summit Opens in Geneva - AP", "global summit opens in geneva"),
            ("Global Summit Opens in Geneva | NYT", "global summit opens in geneva"),
        ]
        for raw, expected in cases:
            self.assertEqual(normalize_title(raw), expected)


class TestDataNewsIntegrity(unittest.TestCase):
    """Verifies the persistent data/news.json file satisfies all Milestone 1 invariants."""

    def setUp(self):
        news_path = os.path.join(_PROJECT_ROOT, 'data', 'news.json')
        with open(news_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        self.articles = self.data.get('articles', [])

    def test_zero_wire_publishers_in_organizations(self):
        leaked = []
        for art in self.articles:
            for o in art.get('entities', {}).get('organizations', []):
                name = o.get('name', '')
                if is_quarantined_publisher(name):
                    leaked.append((art['id'], name))
        self.assertEqual(len(leaked), 0, f"Found wire publishers in entities.organizations: {leaked}")

    def test_zero_wire_suffixes_in_titles(self):
        contaminated = []
        for art in self.articles:
            title = art.get('title', '')
            if any(s in title for s in [' - Reuters', ' - BBC', ' - AP', ' | Reuters', ' | BBC', ' — Reuters']):
                contaminated.append((art['id'], title))
        self.assertEqual(len(contaminated), 0, f"Found wire suffixes in titles: {contaminated}")

    def test_zero_wire_names_at_end_of_descriptions(self):
        contaminated = []
        for art in self.articles:
            desc = art.get('description', '')
            if desc.endswith('Reuters.') or desc.endswith('BBC.') or desc.endswith('AP.'):
                contaminated.append((art['id'], desc))
        self.assertEqual(len(contaminated), 0, f"Found wire names at end of descriptions: {contaminated}")

    def test_all_descriptions_cleanly_terminated(self):
        malformed = []
        for art in self.articles:
            desc = art.get('description', '')
            if desc.endswith('...') or desc.endswith('…') or (len(desc) > 30 and not desc.endswith('.')):
                malformed.append((art['id'], desc))
        self.assertEqual(len(malformed), 0, f"Found malformed description endings: {malformed}")


if __name__ == '__main__':
    unittest.main()
