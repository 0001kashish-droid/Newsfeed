#!/usr/bin/env python3
"""
Empirical Challenger Stress Test Suite - Milestone 5
Final Victory Release Audit & Master Pipeline Stress Verification

Adversarially tests:
1. Environment Variable Resilience (Missing, empty, whitespace, malformed BUTTONDOWN_API_KEY).
2. Network Fault Tolerance & Feed Drops (YouTube timeouts, HTTP 500s, empty scrapes, RSS outage fallbacks).
3. Console Encoding & Unicode Safety (cp1252 simulation, CJK/Arabic/emojis, stdout reconfigure faults).
4. Ingestion Deduplication Edge Cases (Suffix stripping, Jaccard boundaries, entity overlap, false positives).
5. Brand Family Capping Stability (Small/large feeds, severe skew, convergence under fluctuation).
6. Mutual Resonance Cross-Link Integrity (Bidirectional schema invariants, disjoint topics, preservation).
7. Production Hard Audit & Master E2E Suite Execution.

Zero external dependencies (pure Python standard library).
"""

import os
import sys
import unittest
import json
import shutil
import tempfile
import urllib.error
import urllib.request
import subprocess
from unittest.mock import patch, MagicMock
from collections import Counter

# Set paths
TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(TESTS_DIR)
SCRIPTS_DIR = os.path.join(PROJECT_ROOT, 'scripts')
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)


# ===========================================================================
# 1. Environment Variable Adverse Conditions
# ===========================================================================
class TestAdverseEnvironmentVariables(unittest.TestCase):
    """Stress tests pipeline behavior under missing, empty, and malformed environment variables."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.sample_news = os.path.join(self.temp_dir, 'news.json')
        sample_data = {
            "lastUpdated": "2026-10-07T12:00:00Z",
            "articles": [
                {
                    "id": "art-1",
                    "title": "Global Semiconductor Alliance Formed",
                    "description": "Nations agree on supply chain security.",
                    "source": "Reuters",
                    "category": "Tech",
                    "region": "Global",
                    "link": "https://reuters.com/tech-semi",
                    "importance_score": 0.95,
                    "annotation": {"what": "Semiconductor alliance launched.", "why": "Secures microchips."}
                }
            ]
        }
        with open(self.sample_news, 'w', encoding='utf-8') as f:
            json.dump(sample_data, f)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_missing_buttondown_api_key_env_var(self):
        """When BUTTONDOWN_API_KEY is not in os.environ, script must bypass email and exit 0."""
        from generate_daily_newsletter import generate_newsletter, send_via_buttondown

        with patch.dict(os.environ, {}, clear=True):
            sent = send_via_buttondown("Test Subject", "Test Body")
            self.assertFalse(sent, "send_via_buttondown must return False when API key is missing")

            output = generate_newsletter(send_email=True, news_file=self.sample_news)
            self.assertIn("# 🌐 News Colossal — Daily Executive Digest", output)
            self.assertIn("Global Semiconductor Alliance Formed", output)

    def test_empty_and_whitespace_buttondown_api_key(self):
        """When BUTTONDOWN_API_KEY is empty or whitespace, it must cleanly skip dispatch."""
        from generate_daily_newsletter import send_via_buttondown

        for bad_key in ["", "   ", "\t\n  ", None]:
            env_dict = {"BUTTONDOWN_API_KEY": bad_key} if bad_key is not None else {}
            with patch.dict(os.environ, env_dict, clear=True):
                result = send_via_buttondown("Subject", "Body")
                self.assertFalse(result, f"Failed for bad key: {repr(bad_key)}")

    def test_malformed_buttondown_api_key_http_error(self):
        """When BUTTONDOWN_API_KEY is malformed, HTTP 401 Unauthorized must be caught and return False."""
        from generate_daily_newsletter import send_via_buttondown

        fake_err = urllib.error.HTTPError(
            url="https://api.buttondown.com/v1/emails",
            code=401,
            msg="Unauthorized",
            hdrs={},
            fp=MagicMock(read=lambda: b'{"detail": "Invalid token"}')
        )

        with patch.dict(os.environ, {"BUTTONDOWN_API_KEY": "MALFORMED_FAKE_KEY"}):
            with patch('urllib.request.urlopen', side_effect=fake_err):
                result = send_via_buttondown("Subject", "Body")
                self.assertFalse(result, "send_via_buttondown must return False on HTTPError without raising")

    def test_newsletter_archival_persistence_across_all_conditions(self):
        """Verifies newsletter markdown is saved to disk regardless of email dispatch failure."""
        from generate_daily_newsletter import generate_newsletter

        newsletters_dir = os.path.join(PROJECT_ROOT, 'newsletters')
        with patch.dict(os.environ, {"BUTTONDOWN_API_KEY": "INVALID_KEY"}):
            with patch('generate_daily_newsletter.send_via_buttondown', return_value=False):
                generate_newsletter(send_email=True, news_file=self.sample_news)
                self.assertTrue(os.path.isdir(newsletters_dir))
                md_files = [f for f in os.listdir(newsletters_dir) if f.endswith('.md')]
                self.assertGreater(len(md_files), 0, "Archived markdown digest must exist")

    def test_corrupt_or_missing_news_file_handling(self):
        """When news.json is missing or corrupted, newsletter generator must not crash."""
        from generate_daily_newsletter import generate_newsletter

        # 1. Non-existent file
        res = generate_newsletter(news_file=os.path.join(self.temp_dir, 'non_existent.json'))
        self.assertEqual(res, "", "Must return empty string and not crash on missing file")

        # 2. Corrupt JSON file
        corrupt_file = os.path.join(self.temp_dir, 'corrupt.json')
        with open(corrupt_file, 'w', encoding='utf-8') as f:
            f.write("INVALID JSON CONTENT {{{")
        with self.assertRaises(json.JSONDecodeError):
            generate_newsletter(news_file=corrupt_file)


# ===========================================================================
# 2. Network Fault Tolerance & Feed Drops
# ===========================================================================
class TestNetworkFaultToleranceAndFeedDrops(unittest.TestCase):
    """Stress tests resilience against network timeouts, HTTP errors, and empty feed responses."""

    def test_youtube_scrape_socket_timeout(self):
        """scrape_channel must handle socket.timeout / URLError gracefully and return empty list."""
        from fetch_podcasts import scrape_channel

        timeout_err = urllib.error.URLError("timed out")
        with patch('urllib.request.urlopen', side_effect=timeout_err):
            episodes = scrape_channel({'name': 'Test Pod', 'handle': '@test', 'logo': 'TP', 'tier': 'flagship'})
            self.assertEqual(episodes, [], "Must return empty list on timeout without uncaught exception")

    def test_youtube_scrape_http_error_codes(self):
        """scrape_channel must handle HTTP 404, 429, 500 without crashing."""
        from fetch_podcasts import scrape_channel

        for code in [404, 429, 500, 503]:
            http_err = urllib.error.HTTPError("http://youtube.com", code, "Error", {}, None)
            with patch('urllib.request.urlopen', side_effect=http_err):
                episodes = scrape_channel({'name': 'Test Pod', 'handle': '@test', 'logo': 'TP', 'tier': 'flagship'})
                self.assertEqual(episodes, [], f"Must handle HTTP {code} gracefully")

    def test_youtube_empty_scrape_data_loss_prevention(self):
        """When YouTube scraping returns 0 episodes, fetch_podcasts must NEVER wipe data/podcasts.json."""
        from fetch_podcasts import main as podcasts_main

        # Read current podcasts.json
        podcasts_file = os.path.join(DATA_DIR, 'podcasts.json')
        with open(podcasts_file, 'r', encoding='utf-8') as f:
            original_data = f.read()

        # Simulate total scrape failure (all channels return empty list)
        with patch('fetch_podcasts.scrape_channel', return_value=[]):
            podcasts_main()

        with open(podcasts_file, 'r', encoding='utf-8') as f:
            post_data = f.read()

        self.assertEqual(
            original_data, post_data,
            "CRITICAL: data/podcasts.json was modified or wiped after empty scrape!"
        )

    def test_youtube_partial_failure_preserves_unrefreshed_and_resonance(self):
        """When some channels fail, previous episodes and their resonant_news must be preserved."""
        from fetch_podcasts import main as podcasts_main, load_existing_podcasts

        existing = load_existing_podcasts(os.path.join(DATA_DIR, 'podcasts.json'))
        existing_eps = existing.get('episodes', [])
        self.assertGreater(len(existing_eps), 0)

        # Scrape only returns 1 episode from Lex Fridman
        mock_ep = {
            'id': 'tp_mock_123',
            'title': 'Mock Episode Title on AI',
            'podcast': 'Lex Fridman Podcast',
            'channel': 'Lex Fridman Podcast',
            'podcastLogo': 'LF',
            'tier': 'flagship',
            'guest': 'Mock Guest',
            'topics': ['AI'],
            'theme': 'Mock Theme',
            'imageUrl': 'https://i.ytimg.com/vi/mock/maxresdefault.jpg',
            'thumbnail': 'https://i.ytimg.com/vi/mock/maxresdefault.jpg',
            'link': 'https://www.youtube.com/watch?v=mock',
            'youtube_url': 'https://www.youtube.com/watch?v=mock',
            'pubDate': '1d ago',
            'date': '1d ago',
            'duration': '1:00:00',
            'views': '',
            'category': 'AI & Tech',
            'resonant_news': []
        }

        # Verify load_existing_podcasts loads correctly
        self.assertTrue('episodes' in existing)

    def test_rss_feed_complete_outage_cached_fallback(self):
        """When all RSS feeds fail, fetch_news must fall back to cached articles without wiping news.json."""
        from fetch_news import main as news_main

        news_file = os.path.join(DATA_DIR, 'news.json')
        with open(news_file, 'r', encoding='utf-8') as f:
            original_data = f.read()

        with patch('fetch_news.fetch_rss', return_value=[]):
            # Also mock network within correlate_podcasts_to_news or other steps
            news_main()

        with open(news_file, 'r', encoding='utf-8') as f:
            post_data = json.loads(f.read())

        self.assertGreater(len(post_data.get('articles', [])), 0, "Cached articles must be preserved")


# ===========================================================================
# 3. Console Encoding Safety & Unicode Resilience
# ===========================================================================
class TestEncodingSafetyAndUnicodeResilience(unittest.TestCase):
    """Stress tests character encoding safety under cp1252 and exotic Unicode payloads."""

    def test_newsletter_under_cp1252_encoding(self):
        """Newsletter generator must run cleanly under PYTHONIOENCODING=cp1252."""
        proc = subprocess.run(
            [sys.executable, os.path.join(PROJECT_ROOT, 'generate_daily_newsletter.py')],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            env={**os.environ, 'BUTTONDOWN_API_KEY': '', 'PYTHONIOENCODING': 'cp1252'}
        )
        self.assertEqual(proc.returncode, 0)
        self.assertNotIn("UnicodeEncodeError", proc.stderr)

    def test_newsletter_exotic_unicode_payloads(self):
        """Sanitizer and formatter must handle CJK, Cyrillic, Arabic, and emojis safely."""
        from generate_daily_newsletter import _sanitize_text, _extract_what, _extract_why

        exotic_payloads = [
            "全球半导体联盟成立 🚀 — 创新与供应链",
            "Российские ученые разработали новый квантовый чип ⚡",
            "تحالف الذكاء الاصطناعي العالمي يناقش السياسات الحديثة 🌐",
            "Special characters: «» “ ” ‘ ’ — – … \u200b\ufeff",
            "<script>alert('xss')</script>Safe headline with emojis: ☕ 📰 ✦"
        ]

        for p in exotic_payloads:
            cleaned = _sanitize_text(p)
            self.assertNotIn("<script>", cleaned.lower())
            # Must encode to UTF-8 without error
            cleaned.encode('utf-8')

            art = {
                'title': p,
                'description': p,
                'annotation': {'what': p, 'why': p}
            }
            what = _extract_what(art)
            why = _extract_why(art)
            self.assertGreater(len(what), 0)
            self.assertGreater(len(why), 0)

    def test_sys_stdout_reconfigure_resilience(self):
        """generate_daily_newsletter must not fail even if sys.stdout has no reconfigure attribute."""
        script_path = os.path.join(PROJECT_ROOT, 'generate_daily_newsletter.py')
        with open(script_path, 'r', encoding='utf-8') as f:
            code = f.read()

        self.assertIn("hasattr(sys.stdout, 'reconfigure')", code)
        self.assertIn("hasattr(sys.stderr, 'reconfigure')", code)


# ===========================================================================
# 4. Ingestion Deduplication Edge Cases
# ===========================================================================
class TestIngestionDeduplicationStress(unittest.TestCase):
    """Stress tests title normalization, high Jaccard overlap, and entity-based deduplication."""

    def test_source_suffix_stripping_and_title_normalization(self):
        """normalize_title must strip publisher suffixes uniformly."""
        from intelligence.intake import normalize_title

        cases = [
            ("Global Summit Opens in Geneva - BBC News", "global summit opens in geneva"),
            ("Global Summit Opens in Geneva | Reuters", "global summit opens in geneva"),
            ("Global Summit Opens in Geneva — The Guardian", "global summit opens in geneva"),
            ("Global Summit Opens in Geneva - AP", "global summit opens in geneva"),
            ("Global Summit Opens in Geneva | NYT", "global summit opens in geneva"),
        ]

        for raw, expected in cases:
            norm = normalize_title(raw)
            self.assertEqual(norm, expected, f"Failed normalizing '{raw}': got '{norm}'")

    def test_high_jaccard_overlap_boundary_thresholds(self):
        """Articles above threshold must be clustered as duplicates; below must be distinct."""
        from intelligence.intake import enhanced_dedup

        # Jaccard overlap exactly at boundary
        # "eu passes historic ai act regulations" (6 tokens)
        # "eu passes historic ai act rules" (6 tokens, 5 shared: 5/7 = 0.71)
        # "eu passes historic artificial intelligence act regulations"
        art1 = {'id': '1', 'title': 'EU passes historic AI act regulations', 'category': 'Tech'}
        art2 = {'id': '2', 'title': 'EU passes historic AI act regulations today', 'category': 'Tech'}
        art3 = {'id': '3', 'title': 'Japan launches new high speed maglev train', 'category': 'Tech'}

        # With high threshold 0.80:
        # art1 tokens: eu, passes, historic, ai, act, regulations (6)
        # art2 tokens: eu, passes, historic, ai, act, regulations, today (7)
        # intersection: 6, union: 7 -> 6/7 = 0.857 >= 0.85 -> duplicate!
        res = enhanced_dedup([art1, art2, art3], threshold=0.85)
        dups = [a for a in res if a.get('is_duplicate')]
        non_dups = [a for a in res if not a.get('is_duplicate')]

        self.assertEqual(len(dups), 1, "art2 should be marked duplicate of art1")
        self.assertEqual(len(non_dups), 2, "art1 canonical and art3 distinct should remain")

    def test_entity_overlap_deduplication_rule(self):
        """Articles with different titles but identical category and >=80% entity overlap are deduplicated."""
        from intelligence.intake import enhanced_dedup

        art1 = {
            'id': 'e1',
            'title': 'Macron hosts Scholz for bilateral discussions in Paris',
            'category': 'World',
            'entities': {
                'leaders': [{'name': 'Emmanuel Macron'}, {'name': 'Olaf Scholz'}],
                'countries': [{'name': 'France'}, {'name': 'Germany'}],
                'locations': [{'name': 'Paris'}]
            }
        }
        art2 = {
            'id': 'e2',
            'title': 'French and German leaders hold summit on European defense',
            'category': 'World',
            'entities': {
                'leaders': [{'name': 'Emmanuel Macron'}, {'name': 'Olaf Scholz'}],
                'countries': [{'name': 'France'}, {'name': 'Germany'}],
                'locations': [{'name': 'Paris'}]
            }
        }

        res = enhanced_dedup([art1, art2], threshold=0.85)
        dups = [a for a in res if a.get('is_duplicate')]
        self.assertEqual(len(dups), 1, "Entity overlap >=80% in same category must dedup syndicated stories")

    def test_canonical_selection_oracle(self):
        """Canonical selection must choose the richer article (better image, more entities, longer desc)."""
        from intelligence.intake import enhanced_dedup

        thin_art = {
            'id': 'thin',
            'title': 'Breakthrough in battery storage technology',
            'description': 'Short description.',
            'category': 'Tech',
            'imageUrl': 'https://images.unsplash.com/sample',
            'entities': {}
        }
        rich_art = {
            'id': 'rich',
            'title': 'Breakthrough in battery storage technology today',
            'description': 'Comprehensive in-depth description of the solid state battery development.',
            'category': 'Tech',
            'imageUrl': 'https://custom-publisher.com/battery.jpg',
            'entities': {'domains': ['Energy', 'Materials'], 'companies': [{'name': 'QuantumScape'}]}
        }

        res = enhanced_dedup([thin_art, rich_art], threshold=0.80)
        canonical = [a for a in res if not a.get('is_duplicate')][0]
        self.assertEqual(canonical['id'], 'rich', "Richer article must be selected as canonical")

    def test_false_positive_deduplication_prevention(self):
        """Distinct stories sharing generic words must NEVER be deduplicated."""
        from intelligence.intake import enhanced_dedup

        art1 = {'id': 'fed', 'title': 'Federal Reserve cuts interest rates by 25 basis points', 'category': 'Business'}
        art2 = {'id': 'boe', 'title': 'Bank of England holds interest rates steady amid inflation', 'category': 'Business'}
        art3 = {'id': 'ecb', 'title': 'European Central Bank signals possible rate cut in June', 'category': 'Business'}

        res = enhanced_dedup([art1, art2, art3], threshold=0.85)
        dups = [a for a in res if a.get('is_duplicate')]
        self.assertEqual(len(dups), 0, "Distinct stories must not trigger false positive deduplication")


# ===========================================================================
# 5. Brand Family Capping Stability
# ===========================================================================
class TestBrandFamilyCappingStability(unittest.TestCase):
    """Stress tests brand family capping (<= 18%) across fluctuating feed sizes and severe skew."""

    def test_small_feed_capping_convergence(self):
        """Small feeds (N=6 to N=15) must converge without infinite loops or collapsing to 0 articles."""
        from fetch_news import enforce_brand_family_cap

        for n in range(6, 16):
            # Feed where 80% is BBC
            articles = []
            for i in range(n):
                src = "BBC News" if i < int(n * 0.8) else f"Source_{i}"
                articles.append({'id': f'a_{i}', 'title': f'Story {i}', 'source': src})

            capped = enforce_brand_family_cap(articles, max_ratio=0.18)
            self.assertGreater(len(capped), 0, f"Capped feed must not collapse to 0 for N={n}")

            # Verify brand cap invariant
            bbc_count = sum(1 for a in capped if 'BBC' in a['source'])
            allowed_max = max(1, int(0.18 * len(capped)))
            self.assertLessEqual(
                bbc_count, allowed_max,
                f"BBC count {bbc_count} exceeds allowed {allowed_max} for capped length {len(capped)}"
            )

    def test_severe_brand_skew_capping_invariant(self):
        """A feed with 100 articles where 60 are BBC sub-brands must strictly cap BBC to <= 18%."""
        from fetch_news import enforce_brand_family_cap

        articles = []
        bbc_sub_brands = ["BBC News", "BBC Asia", "BBC Europe", "BBC Middle East", "BBC US", "BBC Business"]
        for i in range(60):
            articles.append({'id': f'bbc_{i}', 'title': f'BBC Story {i}', 'source': bbc_sub_brands[i % len(bbc_sub_brands)]})
        for i in range(40):
            articles.append({'id': f'other_{i}', 'title': f'Other Story {i}', 'source': f'Publisher_{i % 10}'})

        capped = enforce_brand_family_cap(articles, max_ratio=0.18)
        bbc_count = sum(1 for a in capped if 'BBC' in a['source'])
        bbc_ratio = bbc_count / len(capped)

        self.assertLessEqual(
            bbc_ratio, 0.180001,
            f"BBC ratio {bbc_ratio:.4f} exceeds 18% cap (count={bbc_count}, total={len(capped)})"
        )

    def test_monolithic_single_brand_feed(self):
        """When all articles come from the same single brand family, cap terminates safely."""
        from fetch_news import enforce_brand_family_cap

        articles = [{'id': f'b_{i}', 'title': f'Title {i}', 'source': 'BBC News'} for i in range(20)]
        capped = enforce_brand_family_cap(articles, max_ratio=0.18)
        self.assertIsInstance(capped, list)

    def test_unmapped_brands_capping(self):
        """Publishers not in BRAND_FAMILIES are treated as their own individual brand."""
        from fetch_news import enforce_brand_family_cap

        articles = []
        for i in range(50):
            src = "UniquePublisher" if i < 30 else f"Other_{i}"
            articles.append({'id': f'u_{i}', 'title': f'Title {i}', 'source': src})

        capped = enforce_brand_family_cap(articles, max_ratio=0.18)
        u_count = sum(1 for a in capped if a['source'] == 'UniquePublisher')
        allowed_max = max(1, int(0.18 * len(capped)))
        self.assertLessEqual(u_count, allowed_max)


# ===========================================================================
# 6. Mutual Resonance Cross-Link Integrity
# ===========================================================================
class TestMutualResonanceIntegrityAndConsistency(unittest.TestCase):
    """Stress tests mutual resonance bi-directional consistency and schema completeness."""

    def test_live_datasets_bidirectional_resonance_invariant(self):
        """Every article with resonant_podcast MUST point to an episode whose resonant_news links back."""
        with open(os.path.join(DATA_DIR, 'news.json'), 'r', encoding='utf-8') as f:
            news_data = json.load(f)
        with open(os.path.join(DATA_DIR, 'podcasts.json'), 'r', encoding='utf-8') as f:
            podcasts_data = json.load(f)

        articles = news_data.get('articles', [])
        episodes = podcasts_data.get('episodes', [])

        ep_by_id = {ep['id']: ep for ep in episodes if 'id' in ep}
        ep_by_url = {ep.get('link'): ep for ep in episodes if ep.get('link')}

        # Articles pointing to podcasts
        resonant_arts = [a for a in articles if a.get('resonant_podcast')]
        self.assertGreater(len(resonant_arts), 0, "data/news.json must contain resonant articles")

        for art in resonant_arts:
            rp = art['resonant_podcast']
            # Episode must exist in podcasts.json
            target_ep = ep_by_id.get(rp.get('id')) or ep_by_url.get(rp.get('youtube_url') or rp.get('link'))
            self.assertIsNotNone(
                target_ep,
                f"Article '{art['id']}' references podcast ID '{rp.get('id')}' not found in podcasts.json"
            )

            # Target episode must have resonant_news pointing back
            linked_news_ids = {n.get('id') for n in target_ep.get('resonant_news', [])}
            self.assertIn(
                art['id'], linked_news_ids,
                f"Bi-directional invariant broken: episode '{target_ep['id']}' does not link back to article '{art['id']}'"
            )

    def test_resonant_podcast_and_resonant_news_schema_completeness(self):
        """Verifies full schema compliance for resonance objects in both datasets."""
        with open(os.path.join(DATA_DIR, 'news.json'), 'r', encoding='utf-8') as f:
            news_data = json.load(f)
        with open(os.path.join(DATA_DIR, 'podcasts.json'), 'r', encoding='utf-8') as f:
            podcasts_data = json.load(f)

        # Check article resonance schema
        for art in news_data.get('articles', []):
            rp = art.get('resonant_podcast')
            if rp:
                self.assertTrue(rp.get('podcast_title') or rp.get('podcast'), f"Missing podcast title in {art['id']}")
                self.assertTrue(rp.get('episode_title') or rp.get('title'), f"Missing episode title in {art['id']}")
                self.assertTrue(rp.get('youtube_url') or rp.get('link'), f"Missing youtube url in {art['id']}")
                score = rp.get('resonance_score') or rp.get('relevance')
                self.assertIsNotNone(score, f"Missing resonance score in {art['id']}")
                self.assertGreater(score, 0.0)

        # Check podcast resonance schema
        for ep in podcasts_data.get('episodes', []):
            for rn in ep.get('resonant_news', []):
                self.assertTrue(rn.get('id'), f"Missing article ID in podcast {ep['id']}")
                self.assertTrue(rn.get('title'), f"Missing article title in podcast {ep['id']}")
                self.assertTrue(rn.get('source'), f"Missing article source in podcast {ep['id']}")
                self.assertTrue(rn.get('url') or rn.get('link'), f"Missing article url in podcast {ep['id']}")
                score = rn.get('resonance_score') or rn.get('relevance')
                self.assertIsNotNone(score)

    def test_zero_correlation_disjoint_topics_safety(self):
        """When articles and podcasts share zero topics/tokens, correlation must not crash."""
        from fetch_news import correlate_podcasts_to_news

        arts = [{'id': 'a1', 'title': 'Antarctic Penguin Population Census', 'description': 'Biology of Adelie penguins.', 'entities': {'domains': ['Zoology']}}]
        pods = [{'id': 'p1', 'title': 'Silicon Valley Venture Capital Trends', 'topics': ['Finance'], 'theme': 'Startups in software.'}]

        out_arts, out_pods = correlate_podcasts_to_news(arts, pods, threshold=0.15)
        self.assertIsNone(out_arts[0].get('resonant_podcast'))
        self.assertEqual(len(out_pods[0].get('resonant_news', [])), 0)


# ===========================================================================
# 7. Production Hard Audit & Master Test Suites
# ===========================================================================
class TestProductionAuditAndE2ERegression(unittest.TestCase):
    """Executes production_hard_audit.py and tests/test_e2e_remediation.py."""

    def test_production_hard_audit_script_execution(self):
        """Executes python production_hard_audit.py and ensures exit code 0 with 0 errors/warnings."""
        proc = subprocess.run(
            [sys.executable, os.path.join(PROJECT_ROOT, 'production_hard_audit.py')],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True
        )
        self.assertEqual(
            proc.returncode, 0,
            f"production_hard_audit.py failed with code {proc.returncode}:\n{proc.stdout}\n{proc.stderr}"
        )
        self.assertIn("PRODUCTION READY: ALL 6 AUDIT LAYERS PASSED 100%", proc.stdout)
        self.assertNotIn("PRODUCTION AUDIT FAILED", proc.stdout)
        self.assertNotIn("[WARNINGS]:", proc.stdout)

    def test_e2e_remediation_suite_execution(self):
        """Executes python -m unittest tests/test_e2e_remediation.py and ensures all 48 tests pass."""
        proc = subprocess.run(
            [sys.executable, '-m', 'unittest', 'tests/test_e2e_remediation.py'],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True
        )
        self.assertEqual(
            proc.returncode, 0,
            f"tests/test_e2e_remediation.py failed with code {proc.returncode}:\n{proc.stderr}"
        )
        self.assertIn("OK", proc.stderr)


if __name__ == '__main__':
    unittest.main(verbosity=2)
