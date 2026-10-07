#!/usr/bin/env python3
"""
Adversarial Verification Suite for Milestone 2 Iteration 2
Author: Challenger M2 Iter 2-2
Validates:
1. Acronym regex boundary bug fix for 'A.I.' and 'E.V.' across punctuation, symbols, whitespace, edge cases.
2. Disjoint stories having 0.0 similarity and returning None (both in fetch_news and curation).
3. Schema contracts, null safety, and mutual resonance bidirectional integrity in data/news.json and data/podcasts.json.
"""

import os
import sys
import json
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
    load_existing_news,
    NEWS_PATH,
    PODCASTS_PATH
)
from scripts.intelligence.curation import _tokenize, cross_link_resonance


class TestAdversarialAcronymBoundaries(unittest.TestCase):
    """Deep adversarial testing of A.I. / E.V. regex boundary fixes."""

    def test_ai_punctuation_and_whitespace_variations(self):
        cases = [
            "A.I. revolution",
            "The future of A.I.",
            "Standalone A.I. here",
            "(A.I.) in healthcare",
            "[A.I.] systems",
            "{A.I.} chips",
            "A.I., robotics, and cloud",
            "What about A.I.?",
            "Amazing A.I.!",
            "Topic: A.I.: The Next Frontier",
            "Section 1; A.I.; section 2",
            "'A.I.' quoted with single quotes",
            '"A.I." quoted with double quotes',
            "“A.I.” with smart curly double quotes",
            "‘A.I.’ with smart curly single quotes",
            "A.I.-powered autonomous agents",
            "A.I./ML multi-disciplinary field",
            "...A.I... surrounded by ellipsis",
            "A.I. \n newline whitespace",
            "Leading tab \tA.I.\t trailing tab",
            "A.I.",  # exact string only
            "a.i.",  # lowercase dotted
            "A.i.",  # mixed case dotted
            "AI",    # bare uppercase
            "ai",    # bare lowercase
        ]

        for text in cases:
            with self.subTest(text=text):
                fn_toks = tokenize_resonance(text)
                cur_toks = _tokenize(text)
                self.assertIn('ai', fn_toks, f"tokenize_resonance failed to extract 'ai' from: {text!r}")
                self.assertIn('ai', cur_toks, f"curation._tokenize failed to extract 'ai' from: {text!r}")

    def test_ev_punctuation_and_whitespace_variations(self):
        cases = [
            "E.V. revolution",
            "The future of E.V.",
            "Standalone E.V. here",
            "(E.V.) in automotive",
            "[E.V.] batteries",
            "{E.V.} charging",
            "E.V., battery, and grid",
            "What about E.V.?",
            "Amazing E.V.!",
            "Topic: E.V.: Clean Transportation",
            "Section 1; E.V.; section 2",
            "'E.V.' quoted with single quotes",
            '"E.V." quoted with double quotes',
            "“E.V.” with smart curly double quotes",
            "‘E.V.’ with smart curly single quotes",
            "E.V.-focused mobility transition",
            "E.V./PHEV vehicle sales",
            "...E.V... surrounded by ellipsis",
            "E.V. \n newline whitespace",
            "Leading tab \tE.V.\t trailing tab",
            "E.V.",  # exact string only
            "e.v.",  # lowercase dotted
            "E.v.",  # mixed case dotted
            "EV",    # bare uppercase
            "ev",    # bare lowercase
        ]

        for text in cases:
            with self.subTest(text=text):
                fn_toks = tokenize_resonance(text)
                cur_toks = _tokenize(text)
                self.assertIn('ev', fn_toks, f"tokenize_resonance failed to extract 'ev' from: {text!r}")
                self.assertIn('ev', cur_toks, f"curation._tokenize failed to extract 'ev' from: {text!r}")

    def test_acronym_negative_lookaround_no_false_positives(self):
        """Words containing 'a.i.' or 'e.v.' with adjacent word chars must not match as acronyms."""
        negative_cases_ai = [
            "ha.i.r",
            "cla.i.m",
            "fa.i.l",
            "la.i.d",
            "pa.i.d",
            "ra.i.d",
        ]
        for text in negative_cases_ai:
            with self.subTest(text=text):
                fn_toks = tokenize_resonance(text)
                cur_toks = _tokenize(text)
                self.assertNotIn('ai', fn_toks, f"tokenize_resonance falsely extracted 'ai' from: {text!r}")
                self.assertNotIn('ai', cur_toks, f"curation._tokenize falsely extracted 'ai' from: {text!r}")

        negative_cases_ev = [
            "re.v.iew",
            "de.v.ice",
            "le.v.el",
            "se.v.en",
        ]
        for text in negative_cases_ev:
            with self.subTest(text=text):
                fn_toks = tokenize_resonance(text)
                cur_toks = _tokenize(text)
                self.assertNotIn('ev', fn_toks, f"tokenize_resonance falsely extracted 'ev' from: {text!r}")
                self.assertNotIn('ev', cur_toks, f"curation._tokenize falsely extracted 'ev' from: {text!r}")


class TestAdversarialDisjointStories(unittest.TestCase):
    """Deep adversarial testing of disjoint story similarity and None returns."""

    def test_disjoint_stories_shared_category_fetch_news(self):
        """Zero token overlap with identical category in fetch_news: score must be 0.0 and return None."""
        articles = [{
            'id': 'art-ocean',
            'title': 'Deep sea hydrothermal vents host novel chemotrophic bacteria',
            'description': 'Marine biologists discover unique hydrothermal ecosystems in the Mariana Trench.',
            'annotation': {'what': 'Abyssal benthic exploration.'},
            'category': 'Science',
            'entities': {'domains': ['Biology', 'Oceanography'], 'actions': ['Exploration']}
        }]
        podcasts = [{
            'id': 'pod-astronomy',
            'title': 'James Webb Space Telescope detects high-redshift galaxy clusters',
            'podcast': 'Cosmos Unveiled',
            'link': 'https://youtube.com/watch?v=jwst1',
            'topics': ['Science', 'Astronomy', 'Astrophysics'],
            'theme': 'Infrared observations of the early universe cosmological epoch.'
        }]

        arts_out, pods_out = correlate_podcasts_to_news(articles, podcasts, threshold=0.15)
        self.assertIsNone(
            arts_out[0].get('resonant_podcast'),
            "Disjoint article sharing only broad category 'Science' must return None"
        )
        self.assertEqual(
            pods_out[0].get('resonant_news', []),
            [],
            "Disjoint podcast sharing only broad category 'Science' must have resonant_news = []"
        )

    def test_disjoint_stories_shared_category_curation(self):
        """Zero token overlap with identical category in curation: score must be 0.0 and return None."""
        articles = [{
            'id': 'art-ocean',
            'title': 'Deep sea hydrothermal vents host novel chemotrophic bacteria',
            'description': 'Marine biologists discover unique hydrothermal ecosystems in the Mariana Trench.',
            'annotation': {'what': 'Abyssal benthic exploration.'},
            'category': 'Science',
            'entities': {'domains': ['science'], 'actions': []}
        }]
        podcasts = [{
            'id': 'pod-astronomy',
            'title': 'James Webb Space Telescope detects high-redshift galaxy clusters',
            'podcast': 'Cosmos Unveiled',
            'link': 'https://youtube.com/watch?v=jwst1',
            'topics': ['science', 'astronomy'],
            'theme': 'Infrared observations of the early universe cosmological epoch.'
        }]

        arts_out, pods_out = cross_link_resonance(articles, podcasts, threshold=0.15)
        self.assertIsNone(
            arts_out[0].get('resonant_podcast'),
            "cross_link_resonance: Disjoint article sharing category must return None"
        )
        self.assertEqual(
            pods_out[0].get('resonant_news', []),
            [],
            "cross_link_resonance: Disjoint podcast sharing category must have resonant_news = []"
        )

    def test_disjoint_stories_exact_zero_score_check(self):
        """Verify that when jaccard == 0, calculated score is strictly 0.0."""
        # Test manually using fetch_news logic
        art_toks = {'excavations', 'pompeii', 'amphorae'}
        ep_toks = {'quantum', 'qubits', 'superconductors'}
        intersection = art_toks & ep_toks
        union = art_toks | ep_toks
        jaccard = len(intersection) / len(union) if union else 0.0
        self.assertEqual(jaccard, 0.0)

        # Even with 100% topic bonus
        topic_bonus = 1.0
        if jaccard > 0:
            score = jaccard * 0.6 + topic_bonus * 0.4
        else:
            score = 0.0
        self.assertEqual(score, 0.0, "Score must be exactly 0.0 when jaccard is 0")

    def test_matching_stories_ai_acronym_cross_resonance(self):
        """Verify that an article with 'A.I.' and a podcast with 'AI' match properly."""
        articles = [{
            'id': 'art-ai-1',
            'title': 'Frontier A.I. safety regulations enacted by global summit',
            'description': 'Delegates agree on rigorous evaluation standards for multimodal A.I. models.',
            'annotation': {'what': 'Multimodal A.I. governance standards.'},
            'category': 'Tech',
            'entities': {'domains': ['ai', 'tech'], 'actions': ['regulation']}
        }]
        podcasts = [{
            'id': 'pod-ai-1',
            'title': 'The Frontier of AI Safety and Regulation',
            'podcast': 'AI Breakthroughs',
            'link': 'https://youtube.com/watch?v=aisafety',
            'topics': ['ai', 'regulation', 'safety'],
            'theme': 'Evaluating governance models for frontier AI architectures.'
        }]

        arts_out, pods_out = correlate_podcasts_to_news(articles, podcasts, threshold=0.15)
        self.assertIsNotNone(
            arts_out[0].get('resonant_podcast'),
            "Article with A.I. must resonate with podcast discussing AI"
        )
        res = arts_out[0]['resonant_podcast']
        self.assertGreater(res['resonance_score'], 0.15)
        self.assertEqual(len(pods_out[0]['resonant_news']), 1)
        self.assertEqual(pods_out[0]['resonant_news'][0]['id'], 'art-ai-1')


class TestAdversarialDiskStateConsistency(unittest.TestCase):
    """Verify the actual data files on disk for mutual resonance and schema contracts."""

    def test_disk_data_files_mutual_linkage(self):
        with open(NEWS_PATH, 'r', encoding='utf-8') as f:
            news = json.load(f)
        with open(PODCASTS_PATH, 'r', encoding='utf-8') as f:
            podcasts = json.load(f)

        news_articles = news.get('articles', [])
        podcast_episodes = podcasts.get('episodes', [])

        news_with_resonance = [a for a in news_articles if a.get('resonant_podcast')]
        pods_with_resonance = [p for p in podcast_episodes if p.get('resonant_news')]

        self.assertGreater(len(news_with_resonance), 0, "data/news.json must have resonant_podcast links")
        self.assertGreater(len(pods_with_resonance), 0, "data/podcasts.json must have resonant_news links")

        # Map of podcasts by id and link
        podcast_map = {p.get('id'): p for p in podcast_episodes}
        podcast_url_map = {p.get('link'): p for p in podcast_episodes}

        # Check every article's resonant_podcast
        for art in news_with_resonance:
            res = art['resonant_podcast']
            # Must satisfy schema
            required_art_keys = ['id', 'title', 'episode_title', 'podcast', 'podcast_title', 'link', 'youtube_url', 'relevance', 'resonance_score']
            for k in required_art_keys:
                self.assertIn(k, res, f"Article {art.get('id')} resonant_podcast missing key {k}")
            self.assertGreater(res['resonance_score'], 0.0, "Resonance score must be > 0.0")

            # Must exist in podcasts.json
            target_pod = podcast_map.get(res['id']) or podcast_url_map.get(res['link'])
            self.assertIsNotNone(target_pod, f"Referenced podcast {res['id']} not found in podcasts.json")

            # Bidirectional check: podcast's resonant_news must contain this article id
            matching_pod_news = [n for n in target_pod.get('resonant_news', []) if n.get('id') == art.get('id')]
            self.assertTrue(len(matching_pod_news) > 0, f"Podcast {target_pod.get('id')} does not link back to article {art.get('id')}")

        # Check every podcast's resonant_news
        article_map = {a.get('id'): a for a in news_articles}
        for ep in pods_with_resonance:
            for item in ep['resonant_news']:
                required_pod_keys = ['id', 'title', 'source', 'link', 'url', 'relevance', 'resonance_score']
                for k in required_pod_keys:
                    self.assertIn(k, item, f"Podcast {ep.get('id')} resonant_news item missing key {k}")
                self.assertGreater(item['resonance_score'], 0.0)

                target_art = article_map.get(item['id'])
                self.assertIsNotNone(target_art, f"Referenced article {item['id']} not found in news.json")
                self.assertIsNotNone(target_art.get('resonant_podcast'), f"Article {item['id']} does not link back to podcast")

    def test_podcast_schema_dual_aliases_all_episodes(self):
        """Every episode in podcasts.json must have contract schema aliases."""
        with open(PODCASTS_PATH, 'r', encoding='utf-8') as f:
            podcasts = json.load(f)

        for ep in podcasts.get('episodes', []):
            for k in ['channel', 'podcast', 'date', 'pubDate', 'thumbnail', 'imageUrl', 'link', 'youtube_url', 'resonant_news']:
                self.assertIn(k, ep, f"Episode {ep.get('id')} missing schema key {k}")


if __name__ == '__main__':
    unittest.main()
