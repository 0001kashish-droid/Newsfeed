#!/usr/bin/env python3
"""
Adversarial Stress Test Harness for Milestone M2 (News Colossal)
Author: challenger_m2_2 (Empirical Challenger)
Target: scripts/fetch_news.py, scripts/fetch_podcasts.py, scripts/intelligence/curation.py

Adversarially challenges:
1. Disjoint topics between news and podcasts (resonance score must be 0 and no false positive links).
2. Tokenization behavior for acronyms like 'AI' / 'EV'.
3. Handling of missing or corrupted data/podcasts.json during news fetching.
4. Execution when scripts are invoked from subdirectories vs project root.
"""

import os
import sys
import re
import json
import tempfile
import unittest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR = os.path.join(PROJECT_ROOT, 'scripts')

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

from scripts.fetch_news import (
    tokenize_resonance,
    correlate_podcasts_to_news,
    load_podcasts,
    save_podcasts,
    PODCASTS_PATH,
    NEWS_PATH
)
from scripts.fetch_podcasts import (
    load_existing_podcasts,
    PODCASTS_PATH as PODCASTS_PATH_FETCH
)
from intelligence.curation import cross_link_resonance, _tokenize


class TestMilestone2AdversarialDisjointTopics(unittest.TestCase):
    """
    Challenge 1: Verify behavior with disjoint topics between news and podcasts.
    Resonance score must be 0 and no false positive links.
    """

    def test_disjoint_topics_completely_unrelated(self):
        """Completely disjoint subjects (Pompeii archaeology vs Quantum physics)."""
        articles = [{
            'id': 'art-disjoint-1',
            'title': 'Excavations in Pompeii reveal preserved Roman fresco and amphorae',
            'description': 'Archaeologists uncover remarkable ancient artifacts in southern Italy.',
            'annotation': {'what': 'Archaeological findings in Pompeii.', 'why': 'Historic Roman cultural preservation.'},
            'category': 'Culture',
            'entities': {'domains': ['Archaeology', 'History']}
        }]
        podcasts = [{
            'id': 'pod-disjoint-1',
            'title': 'Quantum Decoherence and Superconducting Qubits',
            'podcast': 'Physics Frontiers',
            'link': 'https://youtube.com/watch?v=quantum1',
            'topics': ['Quantum Physics', 'Superconductors', 'Qubits'],
            'theme': 'Explores cryogenic quantum state maintenance.'
        }]

        arts_out, pods_out = correlate_podcasts_to_news(articles, podcasts, threshold=0.15)
        self.assertIsNone(
            arts_out[0].get('resonant_podcast'),
            "Disjoint article must have resonant_podcast = None"
        )
        self.assertEqual(
            pods_out[0].get('resonant_news', []),
            [],
            "Disjoint podcast must have resonant_news = []"
        )

    def test_disjoint_topics_coarse_category_overlap_boundary(self):
        """
        Adversarial Boundary: Articles and podcasts share only a broad taxonomy category ('Tech'),
        but have completely disjoint topics (undersea cable deployment vs SaaS sales strategies).
        Evaluates whether coarse category overlap triggers false positive links.
        """
        articles = [{
            'id': 'art-cable-1',
            'title': 'Subsea fiber optic cables laid across Pacific Ocean seabed',
            'description': 'Telecommunication consortium deploys high-capacity undersea fiber links.',
            'category': 'Tech',
            'entities': {'domains': []}
        }]
        podcasts = [{
            'id': 'pod-saas-1',
            'title': 'Scaling B2B Enterprise SaaS Sales Teams',
            'podcast': 'Startup Playbook',
            'link': 'https://youtube.com/watch?v=saas1',
            'topics': ['Tech'],
            'theme': 'Hiring account executives and outbound SDR playbooks.'
        }]

        arts_out, pods_out = correlate_podcasts_to_news(articles, podcasts, threshold=0.15)
        # Note: If topic overlap triggers topic_bonus=1.0 * 0.4 = 0.40 >= 0.15,
        # it falsely connects subsea cables to SaaS sales!
        has_link = arts_out[0].get('resonant_podcast') is not None
        if has_link:
            score = arts_out[0]['resonant_podcast'].get('resonance_score', 0.0)
            print(f"[OBSERVATION] False positive detected on coarse category 'Tech': score={score}")

    def test_empty_or_whitespace_article_and_podcast_fields(self):
        """Gracefully handle empty, None, or whitespace-only textual fields."""
        articles = [{
            'id': 'art-blank',
            'title': '',
            'description': None,
            'annotation': None,
            'category': 'World',
            'entities': None
        }]
        podcasts = [{
            'id': 'pod-blank',
            'title': '   ',
            'podcast': '',
            'link': '',
            'topics': [],
            'theme': None
        }]

        arts_out, pods_out = correlate_podcasts_to_news(articles, podcasts, threshold=0.15)
        self.assertIsNone(arts_out[0].get('resonant_podcast'))
        self.assertEqual(pods_out[0].get('resonant_news', []), [])


class TestMilestone2AdversarialAcronymTokenization(unittest.TestCase):
    """
    Challenge 2: Verify tokenization behavior for acronyms like 'AI' / 'EV'.
    """

    def test_uppercase_and_lowercase_bare_acronyms(self):
        """Bare 'AI' and 'EV' must be captured by tokenize_resonance."""
        toks_ai = tokenize_resonance("New AI model released")
        self.assertIn('ai', toks_ai, "tokenize_resonance must retain 'ai' token")

        toks_ev = tokenize_resonance("Electric vehicle EV market update")
        self.assertIn('ev', toks_ev, "tokenize_resonance must retain 'ev' token")

    def test_dotted_acronym_word_boundary_defect(self):
        """
        Adversarial Probe: 'A.I.' and 'E.V.' with periods.
        Regex r'\\ba\\.i\\.\\b' fails because \\b does not match between '.' (\\W) and ' ' (\\W).
        """
        text = "The revolution of A.I. in modern healthcare"
        toks = tokenize_resonance(text)
        # Empirical test: Does 'ai' exist in tokens?
        # If the regex \\ba\\.i\\.\\b failed, re.findall('a.i.') yields ['a', 'i'], both len 1,
        # which get filtered out, causing 'ai' to be completely missing!
        is_ai_present = 'ai' in toks
        print(f"[OBSERVATION] Dotted acronym 'A.I.' captured as 'ai': {is_ai_present} (Tokens: {toks})")
        self.assertTrue(
            is_ai_present,
            "DEFECT FOUND: tokenize_resonance failed to extract 'ai' from 'A.I.' due to trailing \\b regex failure!"
        )

    def test_dotted_ev_word_boundary_defect(self):
        """Adversarial Probe: 'E.V.' with periods."""
        text = "Subsidies for E.V. adoption announced"
        toks = tokenize_resonance(text)
        is_ev_present = 'ev' in toks
        print(f"[OBSERVATION] Dotted acronym 'E.V.' captured as 'ev': {is_ev_present} (Tokens: {toks})")
        self.assertTrue(
            is_ev_present,
            "DEFECT FOUND: tokenize_resonance failed to extract 'ev' from 'E.V.' due to trailing \\b regex failure!"
        )

    def test_curation_tokenizer_discards_acronyms(self):
        """
        Adversarial Probe: scripts/intelligence/curation.py _tokenize() enforces len(w) > 2.
        Therefore it drops 'ai' and 'ev' even when written without dots!
        """
        tokens = _tokenize("Frontier AI and EV vehicles")
        has_ai = 'ai' in tokens
        has_ev = 'ev' in tokens
        print(f"[OBSERVATION] curation._tokenize() captured 'ai': {has_ai}, 'ev': {has_ev} (Tokens: {tokens})")
        self.assertTrue(
            has_ai,
            "DEFECT FOUND: curation._tokenize() drops 'ai' because of len(w) > 2 restriction!"
        )


class TestMilestone2AdversarialPodcastsJsonResilience(unittest.TestCase):
    """
    Challenge 3: Verify handling of missing or corrupted data/podcasts.json during news fetching.
    """

    def test_missing_podcasts_file(self):
        """Non-existent podcasts.json path returns (None, []) without crash."""
        fake_path = os.path.join(PROJECT_ROOT, "data", "non_existent_podcasts_12345.json")
        data, episodes = load_podcasts(fake_path)
        self.assertIsNone(data)
        self.assertEqual(episodes, [])

    def test_corrupted_json_syntax(self):
        """Invalid JSON syntax in podcasts.json is safely caught."""
        with tempfile.NamedTemporaryFile('w', delete=False, suffix='.json') as f:
            f.write("{\"episodes\": [malformed json...")
            temp_path = f.name

        try:
            data, episodes = load_podcasts(temp_path)
            self.assertIsNone(data)
            self.assertEqual(episodes, [])
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_structural_corruption_null_episodes(self):
        """
        Adversarial Probe: JSON with {'episodes': null}.
        data.get('episodes', []) returns None because 'episodes' key exists with value None!
        """
        with tempfile.NamedTemporaryFile('w', delete=False, suffix='.json') as f:
            f.write(json.dumps({"lastUpdated": "2026-10-06", "total": 0, "episodes": None}))
            temp_path = f.name

        try:
            data, episodes = load_podcasts(temp_path)
            # In load_podcasts: episodes = data.get("episodes", []) if isinstance(data, dict) else []
            # When data['episodes'] is None, episodes is None!
            self.assertIsInstance(
                episodes, list,
                f"DEFECT FOUND: load_podcasts returned {type(episodes)} instead of list when episodes: null!"
            )
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_fetch_podcasts_load_existing_null_episodes_crash(self):
        """
        Adversarial Probe: fetch_podcasts.py load_existing_podcasts when episodes: null.
        In main(): existing_episodes = existing_data.get('episodes', [])
        When episodes: null, existing_episodes is None.
        Iterating 'for ep in existing_episodes:' crashes with TypeError: 'NoneType' object is not iterable!
        """
        with tempfile.NamedTemporaryFile('w', delete=False, suffix='.json') as f:
            f.write(json.dumps({"total": 0, "episodes": None}))
            temp_path = f.name

        try:
            existing = load_existing_podcasts(temp_path)
            eps = existing.get('episodes', [])
            self.assertIsInstance(
                eps, list,
                f"DEFECT: fetch_podcasts existing_episodes is {type(eps)} (None), which triggers TypeError on iteration!"
            )
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)


class TestMilestone2AdversarialSubdirectoryInvocation(unittest.TestCase):
    """
    Challenge 4: Verify execution when scripts are invoked from subdirectories vs project root.
    """

    def test_anchored_paths_in_fetch_news(self):
        """Verify PODCASTS_PATH and NEWS_PATH are absolute and project-relative."""
        self.assertTrue(os.path.isabs(PODCASTS_PATH), "PODCASTS_PATH must be absolute")
        self.assertTrue(os.path.isabs(NEWS_PATH), "NEWS_PATH must be absolute")
        self.assertTrue(PODCASTS_PATH.endswith(os.path.join("data", "podcasts.json")))
        self.assertTrue(NEWS_PATH.endswith(os.path.join("data", "news.json")))

    def test_anchored_paths_in_fetch_podcasts(self):
        """Verify PODCASTS_PATH in fetch_podcasts is absolute and project-relative."""
        self.assertTrue(os.path.isabs(PODCASTS_PATH_FETCH), "PODCASTS_PATH_FETCH must be absolute")
        self.assertTrue(PODCASTS_PATH_FETCH.endswith(os.path.join("data", "podcasts.json")))

    def test_load_and_save_podcasts_independent_of_cwd(self):
        """Verify load_podcasts and save_podcasts succeed regardless of current working directory."""
        original_cwd = os.getcwd()
        with tempfile.TemporaryDirectory() as foreign_dir:
            try:
                os.chdir(foreign_dir)
                # Should successfully load default project PODCASTS_PATH
                data, episodes = load_podcasts()
                self.assertIsNotNone(data)
                self.assertIsInstance(episodes, list)
            finally:
                os.chdir(original_cwd)


if __name__ == '__main__':
    unittest.main()
