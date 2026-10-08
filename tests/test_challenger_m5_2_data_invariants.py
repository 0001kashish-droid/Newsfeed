#!/usr/bin/env python3
"""
Empirical Challenger Data Invariant Stress Test Suite - Milestone 5
Author: challenger_m5_2 (Milestone 5 Data Integrity & Invariant Stress Tester)
Target Datasets: data/news.json, data/podcasts.json, data/narrative_memory.json

Adversarially and empirically stress-tests:
1. Invariant I1 - Duplicate Suppression:
   - data/news.json contains 0 duplicate items (is_duplicate: True count == 0).
   - Zero duplicate URLs or identical sanitized titles.
2. Invariant I2 - Brand Family Diversity Caps:
   - No brand family (BBC, etc.) exceeds strictly 18% of the total article count.
   - Dynamic cap logic handles fractional edges and boundary conditions.
3. Invariant I3 - Sentence Boundary Terminations:
   - 100% of article descriptions terminate cleanly on complete sentence punctuation.
   - Zero trailing ellipses ('...', '…') or mid-word truncations.
4. Invariant I4 - Distinct Perspective Publishers:
   - Every paired story and story cluster requires >= 2 distinct sources and distinct brand families.
5. Invariant I5 - Autonomous Narrative Arc Threading:
   - Active narrative arcs schema validity in data/narrative_memory.json.
   - All articles in news.json with non-null arc_id map to a valid arc in narrative_memory.json.
6. Invariant I6 - Bidirectional Mutual Resonance:
   - Mutual resonance links exist in data/news.json (> 0 articles linked).
   - Mutual resonance links exist in data/podcasts.json (> 0 episodes linked).
   - Every resonant_news ID in podcasts.json resolves to a real article in news.json.
   - Every resonant_podcast in news.json resolves to a real episode in podcasts.json.
7. Invariant I7 - Podcast Metadata Completeness:
   - Every episode has non-empty topics and non-empty theme.
   - Resonant news objects have valid IDs, titles, and positive resonance scores.
"""

import os
import sys
import json
import math
import re
import unittest
from collections import Counter

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR = os.path.join(PROJECT_ROOT, 'scripts')

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

from fetch_news import (
    BRAND_FAMILIES,
    balance_source_diversity,
    format_clean_description,
    cluster_stories,
)
from intelligence.intake import enhanced_dedup, normalize_title


class TestMilestone5DataInvariants(unittest.TestCase):
    """
    Comprehensive empirical validation of all data invariants across
    News Colossal persistent datasets.
    """

    @classmethod
    def setUpClass(cls):
        cls.news_path = os.path.join(PROJECT_ROOT, 'data', 'news.json')
        cls.podcasts_path = os.path.join(PROJECT_ROOT, 'data', 'podcasts.json')
        cls.memory_path = os.path.join(PROJECT_ROOT, 'data', 'narrative_memory.json')

        with open(cls.news_path, 'r', encoding='utf-8') as f:
            cls.news_data = json.load(f)
        cls.articles = cls.news_data.get('articles', [])

        with open(cls.podcasts_path, 'r', encoding='utf-8') as f:
            cls.podcasts_data = json.load(f)
        cls.episodes = cls.podcasts_data.get('episodes', [])

        with open(cls.memory_path, 'r', encoding='utf-8') as f:
            cls.memory_data = json.load(f)
        cls.arcs = cls.memory_data.get('arcs', [])

    # -------------------------------------------------------------------------
    # Invariant I1: Duplicate Suppression
    # -------------------------------------------------------------------------
    def test_i1_zero_duplicate_flag_leakage(self):
        """Verify that zero articles in data/news.json have is_duplicate: True."""
        self.assertGreater(len(self.articles), 0, "news.json must contain curated articles")
        leaked_duplicates = [a for a in self.articles if a.get('is_duplicate') is True]
        self.assertEqual(
            len(leaked_duplicates),
            0,
            f"Found {len(leaked_duplicates)} articles with is_duplicate: True in news.json"
        )

    def test_i1_zero_duplicate_urls_or_canonical_titles(self):
        """Verify that all article links and normalized titles are strictly unique."""
        links = [a.get('link') for a in self.articles if a.get('link')]
        url_counts = Counter(links)
        duplicate_urls = {u: c for u, c in url_counts.items() if c > 1}
        self.assertEqual(
            len(duplicate_urls),
            0,
            f"Found duplicate URLs in news.json: {duplicate_urls}"
        )

        norm_titles = [normalize_title(a.get('title', '')) for a in self.articles if a.get('title')]
        title_counts = Counter(norm_titles)
        duplicate_titles = {t: c for t, c in title_counts.items() if c > 1}
        self.assertEqual(
            len(duplicate_titles),
            0,
            f"Found duplicate normalized titles in news.json: {duplicate_titles}"
        )

    # -------------------------------------------------------------------------
    # Invariant I2: Brand Family Diversity Caps
    # -------------------------------------------------------------------------
    def test_i2_brand_family_caps_in_dataset(self):
        """
        Verify that no publisher brand family exceeds strictly 18% of the feed.
        """
        total = len(self.articles)
        self.assertGreater(total, 0)
        
        # Build map of source -> brand family
        brand_counts = Counter()
        for art in self.articles:
            src = art.get('source', '')
            brand = BRAND_FAMILIES.get(src, src)
            brand_counts[brand] += 1

        cap_ratio = 0.18
        max_allowed = max(1, math.floor(cap_ratio * total))

        violations = []
        for brand, count in brand_counts.items():
            pct = count / total
            if pct > cap_ratio:
                violations.append((brand, count, pct, max_allowed))

        self.assertEqual(
            len(violations),
            0,
            f"Brand family diversity cap exceeded: {violations} (threshold: {cap_ratio*100}%, max allowed: {max_allowed})"
        )

    def test_i2_bbc_family_specifically(self):
        """Verify BBC family specifically does not exceed 18%."""
        total = len(self.articles)
        bbc_count = sum(1 for a in self.articles if BRAND_FAMILIES.get(a.get('source', '')) == 'BBC')
        bbc_pct = bbc_count / total * 100
        self.assertLessEqual(
            bbc_pct,
            18.0,
            f"BBC family exceeds 18% cap: {bbc_count}/{total} ({bbc_pct:.2f}%)"
        )

    # -------------------------------------------------------------------------
    # Invariant I3: Sentence Boundary Terminations
    # -------------------------------------------------------------------------
    def test_i3_description_sentence_boundaries(self):
        """
        Verify that 100% of article descriptions end on complete sentence punctuation
        (., !, ?, or punctuation followed by quote) and do not end in ellipses.
        """
        valid_endings = ('.', '!', '?', '."', ".'", '!”', '?”', '…”')
        bad_endings = ('...', '…', '..')

        malformed = []
        for art in self.articles:
            desc = art.get('description', '').strip()
            if not desc:
                continue
            
            # Check for trailing ellipses
            has_ellipsis = any(desc.endswith(b) for b in bad_endings)
            
            # Check for punctuation
            ends_with_punc = desc.endswith(('.', '!', '?')) or (
                len(desc) >= 2 and desc[-1] in ('"', "'", '”', '’') and desc[-2] in ('.', '!', '?')
            )

            if has_ellipsis or not ends_with_punc:
                malformed.append((art.get('id'), desc[-30:] if len(desc) >= 30 else desc))

        self.assertEqual(
            len(malformed),
            0,
            f"Found {len(malformed)} descriptions failing sentence termination invariant: {malformed[:5]}"
        )

    # -------------------------------------------------------------------------
    # Invariant I4: Distinct Perspective Publishers
    # -------------------------------------------------------------------------
    def test_i4_distinct_publishers_in_cross_regional_pairs(self):
        """
        Verify that every paired story and perspective cluster has >= 2 distinct
        publishers and distinct brand families.
        """
        cluster_violations = []
        for art in self.articles:
            perspectives = art.get('perspectives', [])
            if not perspectives or len(perspectives) < 2:
                continue

            sources = set(p.get('source', '') for p in perspectives)
            brands = set(BRAND_FAMILIES.get(p.get('source', ''), p.get('source', '')) for p in perspectives)

            if len(sources) < 2 or len(brands) < 2:
                cluster_violations.append((art.get('id'), sources, brands))

        self.assertEqual(
            len(cluster_violations),
            0,
            f"Found perspective clusters without distinct publishers: {cluster_violations}"
        )

    # -------------------------------------------------------------------------
    # Invariant I5: Autonomous Narrative Arc Threading
    # -------------------------------------------------------------------------
    def test_i5_narrative_memory_schema_validity(self):
        """Verify schema of active narrative arcs in data/narrative_memory.json."""
        self.assertGreater(len(self.arcs), 0, "narrative_memory.json must contain arcs")
        for arc in self.arcs:
            self.assertIn('arc_id', arc)
            self.assertTrue(arc['arc_id'])
            self.assertIn('title', arc)
            self.assertIn('chapter_count', arc)
            self.assertGreaterEqual(arc['chapter_count'], 1)
            self.assertIn('chapter_titles', arc)
            self.assertIsInstance(arc['chapter_titles'], list)

    def test_i5_news_narrative_arc_reference_integrity(self):
        """
        Verify that all articles with non-null arc_id point to an existing arc
        in data/narrative_memory.json.
        """
        arc_id_set = {arc['arc_id'] for arc in self.arcs}
        linked_articles = [a for a in self.articles if a.get('narrative_arc', {}).get('arc_id')]
        self.assertGreater(
            len(linked_articles),
            0,
            "data/news.json should contain articles linked to active narrative arcs"
        )

        invalid_refs = []
        for art in linked_articles:
            ref_id = art['narrative_arc']['arc_id']
            if ref_id not in arc_id_set:
                invalid_refs.append((art['id'], ref_id))

        self.assertEqual(
            len(invalid_refs),
            0,
            f"Found articles referencing non-existent narrative arcs: {invalid_refs}"
        )

    # -------------------------------------------------------------------------
    # Invariant I6: Bidirectional Mutual Resonance Contract
    # -------------------------------------------------------------------------
    def test_i6_mutual_resonance_non_empty(self):
        """Verify that mutual resonance links exist in both datasets."""
        news_with_podcasts = [a for a in self.articles if a.get('resonant_podcast')]
        podcasts_with_news = [ep for ep in self.episodes if ep.get('resonant_news')]

        self.assertGreater(
            len(news_with_podcasts),
            0,
            "data/news.json must contain articles with resonant_podcast links"
        )
        self.assertGreater(
            len(podcasts_with_news),
            0,
            "data/podcasts.json must contain episodes with resonant_news links"
        )

    def test_i6_podcasts_resonant_news_resolve_to_valid_articles(self):
        """
        Verify every resonant_news entry in podcasts.json points to a valid article ID
        in data/news.json and has a valid non-empty title and positive score.
        """
        article_id_map = {a['id']: a for a in self.articles}
        broken_links = []
        invalid_metadata = []

        for ep in self.episodes:
            for item in ep.get('resonant_news', []):
                art_id = item.get('id')
                art_title = item.get('title')
                score = item.get('resonance_score', item.get('relevance', 0))

                if not art_id or art_id not in article_id_map:
                    broken_links.append((ep['id'], art_id))
                if not art_title or score <= 0:
                    invalid_metadata.append((ep['id'], art_id, art_title, score))

        self.assertEqual(
            len(broken_links),
            0,
            f"Found resonant_news in podcasts.json referencing non-existent news IDs: {broken_links}"
        )
        self.assertEqual(
            len(invalid_metadata),
            0,
            f"Found resonant_news with invalid title or non-positive score: {invalid_metadata}"
        )

    def test_i6_news_resonant_podcasts_resolve_to_valid_episodes(self):
        """
        Verify every resonant_podcast in news.json has valid metadata and maps to
        an episode in data/podcasts.json.
        """
        episode_titles = {ep.get('title', '').strip().lower() for ep in self.episodes}
        episode_urls = {ep.get('youtube_url') for ep in self.episodes if ep.get('youtube_url')}
        episode_urls.update({ep.get('link') for ep in self.episodes if ep.get('link')})

        broken_podcast_links = []
        for art in self.articles:
            res_pod = art.get('resonant_podcast')
            if not res_pod:
                continue

            ep_title = res_pod.get('episode_title', '').strip().lower()
            yt_url = res_pod.get('youtube_url')
            score = res_pod.get('resonance_score', 0)

            title_matches = any(ep_title in t or t in ep_title for t in episode_titles)
            url_matches = yt_url in episode_urls if yt_url else False

            if not (title_matches or url_matches):
                broken_podcast_links.append((art['id'], ep_title, yt_url))
            self.assertGreater(score, 0, f"Article {art['id']} resonant_podcast has invalid score {score}")

        self.assertEqual(
            len(broken_podcast_links),
            0,
            f"Found news articles referencing non-existent podcast episodes: {broken_podcast_links}"
        )

    # -------------------------------------------------------------------------
    # Invariant I7: Podcast Metadata Completeness
    # -------------------------------------------------------------------------
    def test_i7_podcast_episodes_metadata_completeness(self):
        """
        Verify that all episodes in podcasts.json have non-empty topics and theme.
        """
        incomplete = []
        for ep in self.episodes:
            topics = ep.get('topics')
            theme = ep.get('theme')

            if not isinstance(topics, list) or len(topics) == 0:
                incomplete.append((ep.get('id'), 'missing/empty topics', topics))
            if not isinstance(theme, str) or not theme.strip():
                incomplete.append((ep.get('id'), 'missing/empty theme', theme))

        self.assertEqual(
            len(incomplete),
            0,
            f"Found podcast episodes with incomplete metadata: {incomplete}"
        )


class TestAlgorithmicStressGenerators(unittest.TestCase):
    """
    Adversarial algorithmic generators to stress-test core invariants against
    edge case inputs.
    """

    def test_brand_diversity_under_skewed_inputs(self):
        """Stress-test balance_source_diversity under extreme single-source dominance."""
        feed = []
        for i in range(100):
            feed.append({
                'id': f'bbc-{i}',
                'title': f'BBC News Story {i}',
                'source': 'BBC News',
                'category': 'World',
                'importance_score': 100 - i
            })
        for i in range(20):
            feed.append({
                'id': f'guardian-{i}',
                'title': f'Guardian Story {i}',
                'source': 'The Guardian',
                'category': 'World',
                'importance_score': 80 - i
            })

        balanced = balance_source_diversity(feed)
        total = len(balanced)
        self.assertGreater(total, 0)

        bbc_count = sum(1 for a in balanced if a['source'] == 'BBC News')
        bbc_pct = bbc_count / total
        self.assertLessEqual(
            bbc_pct,
            0.181,  # allow small float precision delta
            f"BBC ratio {bbc_pct:.3f} exceeded 18% under extreme dominance"
        )

    def test_sentence_formatter_under_adversarial_truncation(self):
        """Stress-test format_clean_description with various cutoffs and punctuation."""
        cases = [
            ("This is a clean sentence. And another.", "This is a clean sentence. And another."),
            ("Trailing dots here...", "Trailing dots here."),
            ("Trailing unicode ellipsis…", "Trailing unicode ellipsis."),
            ("Mid-word cut off like this and then trunc", "Mid-word cut off like this and then trunc."),
            ("Multiple punctuation marks?!", "Multiple punctuation marks?!"),
            ("Quote ending with dot.\" And more.", "Quote ending with dot.\" And more."),
        ]
        for raw, expected in cases:
            cleaned = format_clean_description(raw)
            self.assertTrue(
                cleaned.endswith(('.', '!', '?')) or cleaned[-1] in ('"', "'") and cleaned[-2] in ('.', '!', '?'),
                f"Failed to produce valid sentence boundary for input '{raw}': got '{cleaned}'"
            )
            self.assertFalse(cleaned.endswith('...'), f"Still ended with '...' for '{raw}'")
            self.assertFalse(cleaned.endswith('…'), f"Still ended with '…' for '{raw}'")

    def test_dedup_under_massive_duplicate_influx(self):
        """Stress-test enhanced_dedup with 100 near-identical wire syndicated copies."""
        base_title = "Breaking: International Space Summit Reaches Historic Treaty in Geneva"
        duplicates = []
        for i in range(50):
            duplicates.append({
                'id': f'wire-{i}',
                'title': f"{base_title} - Update {i % 3}",
                'link': f'https://example.com/story-{i}',
                'source': f'Source_{i % 5}',
                'description': "World leaders in Geneva concluded negotiations on peaceful space orbital management today.",
                'entities': {'countries': ['Switzerland'], 'actions': ['treaty']},
                'importance_score': 5.0 + (i * 0.1)
            })

        deduped = enhanced_dedup(duplicates)
        # Should collapse almost all duplicates into a single canonical story or very few
        self.assertLess(len(deduped), 10, f"Dedup failed to collapse duplicate flood, got {len(deduped)} stories")


if __name__ == '__main__':
    unittest.main()
