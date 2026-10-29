# Copyright (c) 2026 Kashish Bhushan — News Colossal
# Empirical Challenger M1 Iteration 2: Deep Stress & Adversarial Test Harness

import os
import sys
import unittest
import json

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


class TestEmpiricalChallengerM1Iter2(unittest.TestCase):
    """
    Adversarial Stress Test Suite probing compound wire parsing,
    boundary preservation, punctuation handling, and entity quarantine.
    """

    # -------------------------------------------------------------------------
    # 1. Multi-City & Multi-Wire Dateline Variations
    # -------------------------------------------------------------------------
    def test_dateline_with_slashed_dates_and_numbers(self):
        """Verifies that slashed years, dates, and figures in story text are NOT swallowed."""
        raw_desc = (
            "WASHINGTON / BRUSSELS (AFP/Reuters) — The EU's 2024/2025 fiscal budget "
            "allocated 45/100 points for carbon reductions across member states."
        )
        res = sanitize_dispatch("Headline", raw_desc)
        self.assertIn("2024/2025 fiscal budget", res['clean_description'])
        self.assertIn("45/100 points", res['clean_description'])
        self.assertTrue(res['clean_description'].endswith('.'))

    def test_compound_wires_with_varied_joiners(self):
        """Tests compound wires connected with &, |, and, via, -, /."""
        cases = [
            ("Peace summit begins (Reuters & AP)", "Peace summit begins"),
            ("Markets stabilize (Bloomberg | Reuters)", "Markets stabilize"),
            ("Markets stabilize (Bloomberg | FT)", "Markets stabilize"),
            ("Oil production shifts (AFP and Reuters)", "Oil production shifts"),
            ("Border pact signed (AP via BBC News)", "Border pact signed"),
            ("Envoys meet in Doha (Reuters - AP)", "Envoys meet in Doha"),
            ("New sanctions planned (AFP/Reuters/AP)", "New sanctions planned"),
        ]
        for raw, expected in cases:
            with self.subTest(raw=raw):
                res = sanitize_dispatch(raw, "Description.")
                self.assertEqual(res['clean_title'], expected)

    def test_multi_wire_datelines_without_trailing_dashes(self):
        """Tests datelines without dash separators (e.g. (Reuters/AP) Text begins)."""
        raw_desc = "(Reuters/AP) Defense ministers concluded three days of talks on security."
        res = sanitize_dispatch("Defense Talks", raw_desc)
        self.assertEqual(
            res['clean_description'],
            "Defense ministers concluded three days of talks on security."
        )

    def test_compound_datelines_with_three_cities(self):
        """Tests datelines spanning three cities and multiple wires."""
        raw_desc = (
            "WASHINGTON / LONDON / BERLIN (AFP/Reuters/AP) — Joint statement issued "
            "on transatlantic trade agreements."
        )
        res = sanitize_dispatch("Joint Statement", raw_desc)
        self.assertEqual(
            res['clean_description'],
            "Joint statement issued on transatlantic trade agreements."
        )

    # -------------------------------------------------------------------------
    # 2. Nested Bracket Permutations
    # -------------------------------------------------------------------------
    def test_nested_brackets_depth_1_to_3(self):
        """Tests bracket nesting depths 1, 2, and 3 across parentheses and square brackets."""
        cases = [
            ("Ceasefire declared (Reuters)", "Ceasefire declared"),
            ("Ceasefire declared ((Reuters))", "Ceasefire declared"),
            ("Ceasefire declared (((Reuters)))", "Ceasefire declared"),
            ("Ceasefire declared [AP]", "Ceasefire declared"),
            ("Ceasefire declared [[AP]]", "Ceasefire declared"),
            ("Ceasefire declared [[[AP]]]", "Ceasefire declared"),
            ("Ceasefire declared ([AFP])", "Ceasefire declared"),
            ("Ceasefire declared [(AFP)]", "Ceasefire declared"),
            ("Ceasefire declared (([Reuters]))", "Ceasefire declared"),
            ("Ceasefire declared ((Reuters / AP))", "Ceasefire declared"),
            ("Ceasefire declared [[AFP/Reuters]]", "Ceasefire declared"),
        ]
        for raw, expected in cases:
            with self.subTest(raw=raw):
                res = sanitize_dispatch(raw, "Description.")
                self.assertEqual(res['clean_title'], expected)

    def test_nested_dateline_brackets(self):
        """Tests nested brackets in prefix datelines."""
        cases = [
            ("((AP)) Washington — Major policy shift announced.", "Major policy shift announced."),
            ("([Reuters]) London — Finance minister addressed parliament.", "Finance minister addressed parliament."),
            ("[[AFP/Reuters]] Paris — Summit convened.", "Summit convened."),
            ("((Reuters/AP)) Brussels - Trade pact sealed.", "Trade pact sealed."),
        ]
        for raw, expected in cases:
            with self.subTest(raw=raw):
                res = sanitize_dispatch("Headline", raw)
                self.assertEqual(res['clean_description'], expected)

    # -------------------------------------------------------------------------
    # 3. Mid-Sentence Wire Mentions Must NOT Be Stripped
    # -------------------------------------------------------------------------
    def test_mid_sentence_wire_mentions_not_stripped(self):
        """Verifies that wire service names occurring legitimately mid-sentence are preserved."""
        raw_desc = (
            "The foreign minister gave an exclusive interview to Reuters and AP journalists "
            "before boarding the flight to Geneva."
        )
        res = sanitize_dispatch("Diplomatic Flight", raw_desc)
        self.assertIn("interview to Reuters and AP journalists", res['clean_description'])

    # -------------------------------------------------------------------------
    # 4. Zero Wire Leakage into Extracted Entities
    # -------------------------------------------------------------------------
    def test_adversarial_compound_wire_zero_entity_leakage(self):
        """Verifies that compound wires never leak into entities."""
        adversarial_inputs = [
            "WASHINGTON / BRUSSELS (AFP/Reuters) — NATO ministers met today.",
            "GENEVA (Reuters & AP) — The WHO announced a new epidemic protocol.",
            "BERLIN (Bloomberg News / Reuters) — Siemens announced a major expansion.",
            "TOKYO (AFP via BBC News) — Sony unveiled its latest quantum sensor.",
            "LONDON (Reuters, AP) — AstraZeneca releases clinical trial results.",
        ]
        for text in adversarial_inputs:
            with self.subTest(text=text):
                res = sanitize_dispatch(text, text)
                ents = extract_entities(res['clean_title'], res['clean_description'])
                all_entity_names = (
                    [o['name'] for o in ents.get('organizations', [])] +
                    [c['name'] for c in ents.get('companies', [])] +
                    [l['name'] for l in ents.get('leaders', [])]
                )
                for name in all_entity_names:
                    self.assertFalse(
                        is_quarantined_publisher(name),
                        f"Quarantined publisher '{name}' leaked into entities from '{text}'"
                    )

    # -------------------------------------------------------------------------
    # 5. Legitimate Media-Related Headlines Preserved
    # -------------------------------------------------------------------------
    def test_legitimate_news_mentioning_wires_preserved(self):
        """Verifies legitimate news about wire agencies or media companies are not damaged."""
        titles = [
            "AP tests show high lead levels in municipal water supplies",
            "Reuters Institute publishes annual report on journalism trust",
            "BBC Proms announces 2026 international festival lineup",
            "Apple and Google face regulatory scrutiny in Europe",
            "Bloomberg Philanthropies awards climate resilience grants",
            "Associated Press Stylebook releases updated guidance on artificial intelligence",
        ]
        for title in titles:
            with self.subTest(title=title):
                res = sanitize_dispatch(title, "Description text.")
                self.assertEqual(res['clean_title'], title)

    # -------------------------------------------------------------------------
    # 6. Sentence Termination and Formatting
    # -------------------------------------------------------------------------
    def test_clean_description_sentence_termination(self):
        """Verifies that all descriptions cleanly end on punctuation."""
        descriptions = [
            "WASHINGTON (Reuters) — Envoys reached an agreement yesterday",
            "PARIS (AFP) — Strike action disrupts high-speed rail lines...",
            "GENEVA (AP) — WHO issues updated global health guidelines - Reuters",
            "BERLIN (Reuters) — Factory output rose 1.2% in third quarter",
        ]
        for desc in descriptions:
            with self.subTest(desc=desc):
                res = sanitize_dispatch("Title", desc)
                clean_d = res['clean_description']
                self.assertTrue(clean_d.endswith(('.', '!', '?')),
                                f"Description '{clean_d}' does not end with terminal punctuation")
                self.assertFalse(clean_d.endswith('..'),
                                f"Description '{clean_d}' ends with double period")


if __name__ == '__main__':
    unittest.main()
