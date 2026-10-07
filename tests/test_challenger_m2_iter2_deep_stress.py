#!/usr/bin/env python3
"""
Deep Empirical Adversarial Stress Test Suite for Milestone 2 Iteration 2
Agent: Challenger M2 Iter 2-1 (Empirical Challenger)
Target: scripts/fetch_news.py, scripts/fetch_podcasts.py, scripts/intelligence/curation.py, data/news.json, data/podcasts.json, .github/workflows/fetch-news.yml
"""

import os
import sys
import json
import tempfile
import unittest
import subprocess

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
    load_existing_news,
    normalize_episode_schema as normalize_news_ep,
    PODCASTS_PATH,
    NEWS_PATH,
)
from scripts.fetch_podcasts import (
    load_existing_podcasts,
    normalize_episode_schema as normalize_pod_ep,
)
from intelligence.curation import cross_link_resonance, _tokenize


class TestDiskDatasetsM2Contract(unittest.TestCase):
    """Deep verification of disk datasets data/news.json and data/podcasts.json against PROJECT.md M2 contracts."""

    def setUp(self):
        self.news_path = os.path.join(PROJECT_ROOT, 'data', 'news.json')
        self.podcasts_path = os.path.join(PROJECT_ROOT, 'data', 'podcasts.json')
        self.assertTrue(os.path.exists(self.news_path), f"Missing {self.news_path}")
        self.assertTrue(os.path.exists(self.podcasts_path), f"Missing {self.podcasts_path}")

        with open(self.news_path, 'r', encoding='utf-8') as f:
            self.news_data = json.load(f)
        with open(self.podcasts_path, 'r', encoding='utf-8') as f:
            self.podcasts_data = json.load(f)

    def test_news_dataset_resonance_contract(self):
        articles = self.news_data.get('articles', [])
        self.assertGreater(len(articles), 0, "news.json articles list must not be empty")

        resonant_articles = [a for a in articles if a.get('resonant_podcast') is not None]
        self.assertGreater(len(resonant_articles), 0, "Must have articles with resonant_podcast")

        # Every resonant article must satisfy PROJECT.md schema:
        # {podcast_title, episode_title, youtube_url, resonance_score}
        for art in resonant_articles:
            rp = art['resonant_podcast']
            self.assertIsInstance(rp, dict, f"resonant_podcast in {art.get('id')} must be a dict")
            for req_key in ['podcast_title', 'episode_title', 'youtube_url', 'resonance_score']:
                self.assertIn(req_key, rp, f"resonant_podcast in {art.get('id')} missing {req_key}")
            self.assertIsInstance(rp['resonance_score'], (int, float))
            self.assertGreaterEqual(rp['resonance_score'], 0.15, "Resonance score must meet threshold >= 0.15")
            self.assertLessEqual(rp['resonance_score'], 1.0, "Resonance score must be <= 1.0")
            self.assertTrue(rp['youtube_url'].startswith('http'), "youtube_url must be valid URL")

    def test_podcasts_dataset_schema_and_aliases(self):
        episodes = self.podcasts_data.get('episodes', [])
        self.assertGreater(len(episodes), 0, "podcasts.json episodes list must not be empty")

        resonant_episodes = [ep for ep in episodes if ep.get('resonant_news')]
        self.assertGreater(len(resonant_episodes), 0, "Must have episodes with resonant_news")

        # Check every episode for PROJECT.md contract line 57:
        # contains id, title, podcast, channel, date, duration, thumbnail, youtube_url, topics, theme
        for idx, ep in enumerate(episodes):
            for req_key in ['id', 'title', 'podcast', 'channel', 'date', 'duration', 'thumbnail', 'youtube_url', 'topics', 'theme']:
                self.assertIn(req_key, ep, f"Episode {idx} ({ep.get('id')}) missing {req_key}")

            # Dual alias consistency
            self.assertEqual(ep['podcast'], ep['channel'], f"Episode {idx} podcast != channel")
            self.assertEqual(ep['date'], ep.get('pubDate'), f"Episode {idx} date != pubDate")
            self.assertEqual(ep['thumbnail'], ep.get('imageUrl'), f"Episode {idx} thumbnail != imageUrl")
            self.assertEqual(ep['youtube_url'], ep.get('link'), f"Episode {idx} youtube_url != link")

            # Check resonant_news schema
            for n_idx, rn in enumerate(ep.get('resonant_news', [])):
                self.assertIsInstance(rn, dict, f"Episode {idx} resonant_news[{n_idx}] must be a dict")
                for rn_key in ['id', 'title', 'url', 'source', 'resonance_score']:
                    self.assertIn(rn_key, rn, f"Episode {idx} resonant_news[{n_idx}] missing {rn_key}")
                self.assertIsInstance(rn['resonance_score'], (int, float))
                self.assertGreaterEqual(rn['resonance_score'], 0.15)
                self.assertLessEqual(rn['resonance_score'], 1.0)
                self.assertTrue(rn['url'].startswith('http'), "url must be valid URL")


class TestAdversarialAcronymsAndBoundaryTokenization(unittest.TestCase):
    """Stress tests for tokenization of dotted acronyms, delimiters, and short words."""

    def test_dotted_acronyms_variations(self):
        cases = [
            ("The future of A.I. in medicine", "ai"),
            ("Breakthrough in a.i. research", "ai"),
            ("Adoption of E.V. fleets", "ev"),
            ("Transition to e.v. cars", "ev"),
            ("In (A.I.) we trust", "ai"),
            ("[A.I.] revolution", "ai"),
            ("Quote 'A.I.' here", "ai"),
            ('"A.I." is transforming tech', "ai"),
            ("A.I., robotics, and cloud", "ai"),
            ("A.I.: A comprehensive review", "ai"),
            ("A.I.-driven navigation", "ai"),
        ]
        for text, expected in cases:
            res_news = tokenize_resonance(text)
            self.assertIn(expected, res_news, f"tokenize_resonance failed to extract '{expected}' from: '{text}'")

            cur_tokens = _tokenize(text)
            self.assertIn(expected, cur_tokens, f"_tokenize failed to extract '{expected}' from: '{text}'")

    def test_short_stopwords_not_retained(self):
        """Verify that short words that are NOT ai/ev and are stopwords are properly rejected."""
        text = "to be or not to be in on at an us uk"
        tokens = tokenize_resonance(text)
        for stop in ['to', 'be', 'or', 'not', 'in', 'on', 'at', 'an', 'us', 'uk']:
            self.assertNotIn(stop, tokens, f"Stopword '{stop}' should not be in tokens")

        cur_tokens = _tokenize(text)
        for stop in ['to', 'be', 'or', 'not', 'in', 'on', 'at', 'an', 'us', 'uk']:
            self.assertNotIn(stop, cur_tokens, f"Stopword '{stop}' should not be in curation tokens")


class TestAdversarialDisjointScoring(unittest.TestCase):
    """Stress tests to verify zero false positives on disjoint articles and podcasts."""

    def test_shared_categories_zero_word_overlap_gives_zero(self):
        """Even with identical category and multiple entities, jaccard == 0 MUST force score == 0.0 in correlate_podcasts_to_news."""
        articles = [{
            'id': 'art-disjoint-deep-1',
            'title': 'Medieval cathedral stained glass restoration finished in Chartres',
            'description': 'French conservators restore 13th century Gothic stained glass windows.',
            'category': 'Culture',
            'entities': {'domains': ['Art', 'Conservation', 'History'], 'actions': ['Restoration']}
        }]
        podcasts = [{
            'id': 'pod-disjoint-deep-1',
            'title': 'Cryogenic cooling architectures for neutral atom quantum computers',
            'podcast': 'Deep Tech Frontier',
            'link': 'https://youtube.com/watch?v=cryo1',
            'topics': ['Art', 'Conservation', 'History'],
            'theme': 'Engineering dilution refrigerators for qubit stability.'
        }]

        arts_out, pods_out = correlate_podcasts_to_news(articles, podcasts, threshold=0.15)
        self.assertIsNone(arts_out[0].get('resonant_podcast'), "Disjoint article must not receive resonant_podcast")
        self.assertEqual(pods_out[0].get('resonant_news', []), [], "Disjoint podcast must not receive resonant_news")

    def test_curation_cross_link_zero_jaccard_strictness(self):
        """Verify that cross_link_resonance in curation.py strictly enforces jaccard > 0 when text words do not overlap."""
        articles = [{
            'id': 'art-c-1',
            'title': 'Ancient Babylonian cuneiform tablets translated by philologists',
            'description': 'Scholars decipher clay trade records found in southern dig sites.',
            'entities': {'domains': ['Linguistics', 'Mesopotamia']}
        }]
        podcasts = [{
            'id': 'pod-c-1',
            'title': 'Solid state battery electrolyte dendrite prevention',
            'podcast': 'Battery Tech',
            'link': 'https://youtube.com/watch?v=battery1',
            'topics': ['Linguistics', 'Mesopotamia'],  # Topic entities match, but ZERO words in title/desc overlap
            'theme': 'Ceramic separators preventing short circuits in electric vehicles.'
        }]
        arts_out, pods_out = cross_link_resonance(articles, podcasts, threshold=0.15)
        self.assertIsNone(arts_out[0].get('resonant_podcast'), "Disjoint article must have resonant_podcast = None")
        self.assertEqual(pods_out[0].get('resonant_news', []), [], "Disjoint podcast must have resonant_news = []")


class TestCorruptedInputsAndEmptyScrapeGuards(unittest.TestCase):
    """Stress tests for malformed JSON, None fields, and empty scrape resilience."""

    def test_load_podcasts_corrupted_json(self):
        with tempfile.NamedTemporaryFile('w', delete=False, suffix='.json') as f:
            f.write("{ invalid json [")
            bad_path = f.name
        try:
            data, eps = load_podcasts(bad_path)
            self.assertIsNone(data)
            self.assertEqual(eps, [])
        finally:
            if os.path.exists(bad_path):
                os.remove(bad_path)

    def test_load_podcasts_null_episodes_field(self):
        with tempfile.NamedTemporaryFile('w', delete=False, suffix='.json') as f:
            json.dump({"total": 0, "episodes": None}, f)
            null_path = f.name
        try:
            data, eps = load_podcasts(null_path)
            self.assertIsInstance(data, dict)
            self.assertEqual(eps, [])
        finally:
            if os.path.exists(null_path):
                os.remove(null_path)

    def test_load_existing_podcasts_null_episodes_field(self):
        with tempfile.NamedTemporaryFile('w', delete=False, suffix='.json') as f:
            json.dump({"total": 0, "episodes": None}, f)
            null_path = f.name
        try:
            data = load_existing_podcasts(null_path)
            self.assertIsInstance(data, dict)
            self.assertEqual(data.get('episodes'), [])
        finally:
            if os.path.exists(null_path):
                os.remove(null_path)

    def test_load_existing_news_corrupted_json(self):
        with tempfile.NamedTemporaryFile('w', delete=False, suffix='.json') as f:
            f.write("Not valid JSON at all")
            bad_path = f.name
        try:
            data, arts = load_existing_news(bad_path)
            self.assertIsNone(data)
            self.assertEqual(arts, [])
        finally:
            if os.path.exists(bad_path):
                os.remove(bad_path)

    def test_save_podcasts_handles_none_and_empty(self):
        with tempfile.NamedTemporaryFile('w', delete=False, suffix='.json') as f:
            save_path = f.name
        try:
            save_podcasts(None, None, save_path)
            with open(save_path, 'r', encoding='utf-8') as f:
                saved = json.load(f)
            self.assertEqual(saved.get('total'), 0)
            self.assertEqual(saved.get('episodes'), [])
        finally:
            if os.path.exists(save_path):
                os.remove(save_path)


class TestCLIExecutionAndIdempotence(unittest.TestCase):
    """Test CLI execution and determinism of --resonate-only mode."""

    def test_resonate_only_cli_execution(self):
        res = subprocess.run(
            [sys.executable, os.path.join(SCRIPTS_DIR, 'fetch_news.py'), '--resonate-only'],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True
        )
        self.assertEqual(res.returncode, 0, f"fetch_news.py --resonate-only failed with stderr:\n{res.stderr}")
        self.assertIn("Loaded", res.stdout)
        self.assertIn("Saved", res.stdout)

        # Verify disk files still valid and preserved
        with open(NEWS_PATH, 'r', encoding='utf-8') as f:
            news = json.load(f)
        with open(PODCASTS_PATH, 'r', encoding='utf-8') as f:
            podcasts = json.load(f)

        resonant_news = [a for a in news['articles'] if a.get('resonant_podcast')]
        resonant_pods = [p for p in podcasts['episodes'] if p.get('resonant_news')]

        self.assertGreater(len(resonant_news), 0, "Expected non-empty resonant articles")
        self.assertGreater(len(resonant_pods), 0, "Expected non-empty resonant podcasts")


class TestGitHubWorkflowOrderingContract(unittest.TestCase):
    """Test that .github/workflows/fetch-news.yml enforces podcast fetch before news fetch."""

    def test_workflow_step_order(self):
        wf_path = os.path.join(PROJECT_ROOT, '.github', 'workflows', 'fetch-news.yml')
        self.assertTrue(os.path.exists(wf_path), f"Workflow file missing: {wf_path}")
        with open(wf_path, 'r', encoding='utf-8') as f:
            content = f.read()

        podcast_idx = content.find('fetch_podcasts.py')
        news_idx = content.find('fetch_news.py')

        self.assertNotEqual(podcast_idx, -1, "fetch_podcasts.py not found in workflow")
        self.assertNotEqual(news_idx, -1, "fetch_news.py not found in workflow")
        self.assertLess(podcast_idx, news_idx, "fetch_podcasts.py MUST be executed before fetch_news.py")


if __name__ == '__main__':
    unittest.main()
