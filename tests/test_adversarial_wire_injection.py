# Copyright (c) 2026 Kashish Bhushan — News Colossal
# Test Suite: Adversarial Wire Injection & Sanitization Stress Harness (Milestone 1)

import os
import sys
import re
import json
import random
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
    extract_entities,
    ORGANIZATION_LEXICON,
    COMPANY_LEXICON,
    LEADER_LEXICON
)
from intelligence.intake import run_intake


class TestAdversarialNestedBrackets(unittest.TestCase):
    """Stress tests nested parentheticals and bracketed tags around wire names."""

    def test_nested_parentheses_trailing(self):
        cases = [
            ("Peace talks resume ((Reuters))", "Peace talks resume"),
            ("Summit concludes in Geneva (((AP)))", "Summit concludes in Geneva"),
            ("Ceasefire agreement announced ((BBC News))", "Ceasefire agreement announced"),
            ("Global markets rally ((Bloomberg))", "Global markets rally"),
        ]
        for raw, expected in cases:
            res = sanitize_dispatch(raw)
            self.assertEqual(res['clean_title'], expected,
                             f"Failed on nested parentheses: raw='{raw}', got='{res['clean_title']}'")

    def test_nested_brackets_and_mixed(self):
        cases = [
            ("Peace talks resume [[AP]]", "Peace talks resume"),
            ("Peace talks resume ([Reuters])", "Peace talks resume"),
            ("Peace talks resume [(AP)]", "Peace talks resume"),
            ("Peace talks resume [[[AFP]]]", "Peace talks resume"),
        ]
        for raw, expected in cases:
            res = sanitize_dispatch(raw)
            self.assertEqual(res['clean_title'], expected,
                             f"Failed on mixed nested brackets: raw='{raw}', got='{res['clean_title']}'")


class TestAdversarialMultipleWires(unittest.TestCase):
    """Stress tests multiple chained wires, joint reporting, and syndication attributions."""

    def test_multiple_wires_attribution_suffix(self):
        cases = [
            ("Diplomatic talks resume in Vienna - Reuters via BBC News", "Diplomatic talks resume in Vienna"),
            ("Emergency summit called in Brussels - AP, Reuters", "Emergency summit called in Brussels"),
            ("Energy prices fall sharply - Reuters / AP", "Energy prices fall sharply"),
            ("Global inflation cools - Bloomberg News / Dow Jones", "Global inflation cools"),
            ("Treaty signed in secret - AFP / Reuters / AP", "Treaty signed in secret"),
            ("Trade deal announced - Reuters and AP", "Trade deal announced"),
        ]
        for raw, expected in cases:
            res = sanitize_dispatch(raw)
            self.assertEqual(res['clean_title'], expected,
                             f"Failed on multi-wire suffix: raw='{raw}', got='{res['clean_title']}'")

    def test_multiple_wires_in_parentheses_or_brackets(self):
        cases = [
            ("Diplomatic talks resume in Vienna (Reuters/AP)", "Diplomatic talks resume in Vienna"),
            ("Emergency summit called in Brussels (AFP / Reuters)", "Emergency summit called in Brussels"),
            ("Energy prices fall sharply [Reuters/AP]", "Energy prices fall sharply"),
            ("Global inflation cools (Reuters, AP)", "Global inflation cools"),
            ("Treaty signed in secret (Reuters and AP)", "Treaty signed in secret"),
        ]
        for raw, expected in cases:
            res = sanitize_dispatch(raw)
            self.assertEqual(res['clean_title'], expected,
                             f"Failed on multi-wire parenthetical: raw='{raw}', got='{res['clean_title']}'")


class TestAdversarialWeirdDatelines(unittest.TestCase):
    """Stress tests complex, compound, and multi-city dateline formats."""

    def test_compound_city_datelines(self):
        cases = [
            ("WASHINGTON / BRUSSELS (AFP) — Envoys reached a compromise.",
             "Envoys reached a compromise."),
            ("TEL AVIV/BEIRUT (Reuters) - Ceasefire monitors deployed.",
             "Ceasefire monitors deployed."),
            ("KYIV, Ukraine (AP) --- Defense ministry confirms strikes.",
             "Defense ministry confirms strikes."),
            ("GENEVA / VIENNA (Reuters) : Talks resumed behind closed doors.",
             "Talks resumed behind closed doors."),
        ]
        for raw, expected in cases:
            res = sanitize_dispatch("Headline", raw)
            self.assertEqual(res['clean_description'], expected,
                             f"Failed compound city dateline: raw='{raw}', got='{res['clean_description']}'")

    def test_multi_wire_datelines(self):
        cases = [
            ("WASHINGTON / BRUSSELS (AFP/Reuters) — Envoys reached a compromise.",
             "Envoys reached a compromise."),
            ("GENEVA (Reuters/AFP/AP) — The delegation arrived on Sunday.",
             "The delegation arrived on Sunday."),
            ("BEIJING (AP-Reuters) — Trade ministers opened talks.",
             "Trade ministers opened talks."),
            ("BRUSSELS (Reuters / AFP) - New carbon guidelines unveiled.",
             "New carbon guidelines unveiled."),
        ]
        for raw, expected in cases:
            res = sanitize_dispatch("Headline", raw)
            self.assertEqual(res['clean_description'], expected,
                             f"Failed multi-wire dateline: raw='{raw}', got='{res['clean_description']}'")

    def test_nested_dateline_brackets(self):
        cases = [
            ("((AP)) Washington — Major policy shift announced.",
             "Major policy shift announced."),
            ("([Reuters]) London — Finance minister addressed parliament.",
             "Finance minister addressed parliament."),
            ("[AP/Reuters] Tokyo — Currency intervention confirmed.",
             "Currency intervention confirmed."),
        ]
        for raw, expected in cases:
            res = sanitize_dispatch("Headline", raw)
            self.assertEqual(res['clean_description'], expected,
                             f"Failed nested dateline brackets: raw='{raw}', got='{res['clean_description']}'")


class TestAdversarialDatelineIntegrity(unittest.TestCase):
    """Ensures dateline processing does NOT chop legitimate story text into attribution."""

    def test_dateline_does_not_swallow_story_text(self):
        # When dateline has a slash or wire, verify the story body is preserved
        raw_desc = "WASHINGTON / BRUSSELS (AFP/Reuters) — Envoys reached a major peace compromise today."
        res = sanitize_dispatch("Envoys Reach Compromise", raw_desc)
        self.assertIn("Envoys reached a major peace compromise today", res['clean_description'],
                      f"Story body was swallowed! Got clean_desc='{res['clean_description']}'")


class TestAdversarialEntityZeroLeakage(unittest.TestCase):
    """Ensures NO wire publishers leak into entities under any adversarial injection."""

    def test_adversarial_entity_extraction_zero_leakage(self):
        adversarial_texts = [
            "WASHINGTON / BRUSSELS (AFP/Reuters) — The WHO and UN coordinated aid with Apple and Microsoft.",
            "Peace talks resume ((Reuters)) with NATO and White House involvement.",
            "Emergency summit called in Brussels - AP, Reuters reporting on European Commission.",
            "Border talks conclude ((BBC News)) as Supreme Court issues landmark ruling.",
            "Global inflation cools - Bloomberg News / Dow Jones / AFP on Federal Reserve policy.",
            "Treaty signed in secret (Reuters and AP) between France and Germany.",
            "Hospital supplies reaching Gaza safely, according to Reuters and BBC News.",
            "Lawmaker speaks to AFP/Reuters after Congress hearing on artificial intelligence.",
        ]

        for text in adversarial_texts:
            res = sanitize_dispatch(text, text)
            ents = extract_entities(res['clean_title'], res['clean_description'])
            
            # Check organizations
            for org in ents.get('organizations', []):
                name = org.get('name', '')
                self.assertFalse(is_quarantined_publisher(name),
                                 f"Quarantined publisher leaked into organizations: '{name}' from text: '{text}'")

            # Check companies
            for comp in ents.get('companies', []):
                name = comp.get('name', '')
                self.assertFalse(is_quarantined_publisher(name),
                                 f"Quarantined publisher leaked into companies: '{name}' from text: '{text}'")

            # Check leaders
            for leader in ents.get('leaders', []):
                name = leader.get('name', '')
                self.assertFalse(is_quarantined_publisher(name),
                                 f"Quarantined publisher leaked into leaders: '{name}' from text: '{text}'")


class TestAdversarialLegitimateTitlePreservation(unittest.TestCase):
    """Verifies that legitimate headlines and non-wire content are NOT stripped or truncated."""

    def test_legitimate_news_titles_preserved(self):
        cases = [
            "AP tests show high lead levels in drinking water across three states",
            "Reuters Institute publishes global digital news report on AI adoption",
            "BBC Proms announces summer concert lineup featuring classical masters",
            "Apple acquires new AI startup for $200M in cash",
            "WHO warns of surging cholera cases across 12 countries",
            "US and China agree on new climate targets ahead of COP summit",
            "Defense secretary visits troops in South Korea amid regional tensions",
            "Tech giants face new EU antitrust investigation into cloud dominance",
            "G7 leaders pledge $50B in Ukraine aid from frozen Russian assets",
            "Supreme Court will hear arguments on interstate commerce regulation",
            "NASA rover discovers organic molecules in ancient Martian riverbed",
            "Federal Reserve holds benchmark interest rate steady at 5.25%",
        ]
        for title in cases:
            res = sanitize_dispatch(title, "Description text.")
            self.assertEqual(res['clean_title'], title,
                             f"Legitimate title modified! Raw='{title}', got='{res['clean_title']}'")


class TestAdversarialFuzzGenerator(unittest.TestCase):
    """Fuzzes sanitizer with 200 randomized combinations of wires, datelines, slugs, and headlines."""

    def test_randomized_fuzz_invariants(self):
        random.seed(42)

        base_headlines = [
            "Envoys reach tentative peace compromise",
            "Central bank lowers key benchmark rate",
            "Earthquake shakes coastal region causing widespread outages",
            "Scientists discover novel compound effective against resistant bacteria",
            "Tech conference showcases next-generation quantum computing chip",
            "Parliament votes to approve comprehensive healthcare reform",
            "Space probe transmits high-resolution images of outer moon",
            "Maritime dispute settled following bilateral negotiations",
        ]

        slugs = ["", "EXCLUSIVE: ", "BREAKING: ", "ANALYSIS: ", "SPECIAL REPORT: ", "OPINION: "]
        cities = ["WASHINGTON", "GENEVA", "BEIJING", "LONDON", "NEW DELHI", "KYIV, Ukraine", "WASHINGTON / BRUSSELS"]
        wire_combos = [
            "Reuters", "AP", "AFP", "BBC News", "Bloomberg",
            "(Reuters)", "((Reuters))", "[AP]", "[[AP]]", "([Reuters])",
            "AFP/Reuters", "Reuters / AP", "Reuters via BBC News", "Bloomberg News / Dow Jones",
            "AFP, Reuters, AP"
        ]
        separators = [" — ", " - ", " : ", " --- "]

        leakage_count = 0
        empty_clean_count = 0
        total_runs = 200

        for i in range(total_runs):
            headline = random.choice(base_headlines)
            slug = random.choice(slugs)
            wire = random.choice(wire_combos)
            city = random.choice(cities)
            sep = random.choice(separators)

            # Injected title: slug + headline + optional suffix
            suffix_style = random.choice(['dash', 'paren', 'bracket', 'none'])
            if suffix_style == 'dash':
                raw_title = f"{slug}{headline} - {wire}"
            elif suffix_style == 'paren':
                raw_title = f"{slug}{headline} ({wire})"
            elif suffix_style == 'bracket':
                raw_title = f"{slug}{headline} [{wire}]"
            else:
                raw_title = f"{slug}{headline}"

            # Injected desc: city + wire + sep + headline
            raw_desc = f"{city} ({wire}){sep}{headline}. The situation remains under close observation."

            res = sanitize_dispatch(raw_title, raw_desc)
            clean_t = res['clean_title']
            clean_d = res['clean_description']

            if not clean_t:
                empty_clean_count += 1

            ents = extract_entities(clean_t, clean_d)
            for org in ents.get('organizations', []):
                if is_quarantined_publisher(org.get('name', '')):
                    leakage_count += 1

            for comp in ents.get('companies', []):
                if is_quarantined_publisher(comp.get('name', '')):
                    leakage_count += 1

        self.assertEqual(leakage_count, 0, f"Fuzz test had {leakage_count} wire leakage instances!")
        self.assertEqual(empty_clean_count, 0, f"Fuzz test had {empty_clean_count} empty clean titles!")


if __name__ == '__main__':
    unittest.main()
