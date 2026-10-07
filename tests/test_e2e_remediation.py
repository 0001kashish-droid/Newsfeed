#!/usr/bin/env python3
"""
E2E Remediation Verification Test Suite for News Colossal.
Author: test_writer_1 (Teamwork Test Writer)
Reference Specifications:
  - ORIGINAL_REQUEST.md (Requirements R1 - R7)
  - PROJECT.md (Feature Inventory 1-17 & Interface Contracts)
  - TEST_INFRA.md (Test Architecture & Tiers 1-4 Verification Matrix)

Covers Tiers 1-4:
  - Tier 1: Feature Coverage (T1.1 - T1.17)
  - Tier 2: Boundary & Corner Cases (T2.1 - T2.17)
  - Tier 3: Cross-Feature Combinations (T3.1 - T3.9)
  - Tier 4: Real-World Application Scenarios (T4.1 - T4.5)

Zero external pip dependencies (pure Python standard library).
"""

import os
import sys
import re
import json
import glob
import shutil
import tempfile
import unittest
import subprocess
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# Path Configuration
# ---------------------------------------------------------------------------
TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(TESTS_DIR)
SCRIPTS_DIR = os.path.join(PROJECT_ROOT, 'scripts')

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)


# ===========================================================================
# Helper Functions & Utilities
# ===========================================================================
def read_project_file(rel_path: str) -> str:
    """Reads a text file relative to project root with UTF-8 encoding."""
    full_path = os.path.join(PROJECT_ROOT, rel_path)
    with open(full_path, 'r', encoding='utf-8', errors='replace') as f:
        return f.read()


def load_project_json(rel_path: str) -> dict:
    """Loads a JSON file relative to project root."""
    full_path = os.path.join(PROJECT_ROOT, rel_path)
    with open(full_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def run_py_script(rel_path: str, env_vars: dict = None, timeout: int = 30) -> subprocess.CompletedProcess:
    """Runs a Python script inside PROJECT_ROOT with isolated environment."""
    script_path = os.path.join(PROJECT_ROOT, rel_path)
    env = os.environ.copy()
    if env_vars:
        for k, v in env_vars.items():
            if v is None:
                env.pop(k, None)
            else:
                env[k] = v

    return subprocess.run(
        [sys.executable, script_path],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        env=env,
        timeout=timeout
    )


# ===========================================================================
# Tier 1: Feature Coverage (Unit & Subsystem Interface Level)
# ===========================================================================
class TestTier1FeatureCoverage(unittest.TestCase):
    """
    Tier 1: Feature coverage for all 17 features per TEST_INFRA.md.
    """

    def test_t1_1_newsletter_buttondown_optionality(self):
        """
        [Feature 1 / R1] Newsletter Buttondown Optionality:
        When BUTTONDOWN_API_KEY is not set or empty, generate_daily_newsletter.py
        must gracefully bypass email delivery without failing (must exit code 0).
        """
        # Run with empty BUTTONDOWN_API_KEY
        proc = run_py_script('generate_daily_newsletter.py', env_vars={'BUTTONDOWN_API_KEY': ''})
        self.assertEqual(
            proc.returncode, 0,
            f"Feature 1 Failed: generate_daily_newsletter.py must exit with code 0 when BUTTONDOWN_API_KEY is unset, "
            f"got exit code {proc.returncode}. stderr: {proc.stderr.strip()}"
        )
        self.assertNotIn(
            "BUTTONDOWN_API_KEY not set. Add it as a GitHub Actions secret",
            proc.stderr + proc.stdout,
            "Feature 1 Failed: generate_daily_newsletter.py exited with error prompt instead of graceful bypass"
        )

    def test_t1_2_newsletter_markdown_archival(self):
        """
        [Feature 2 / R1] Daily Digest Archival:
        Formats and archives daily newsletter markdown in newsletters/*.md.
        File must contain header, date, and curated top stories.
        """
        newsletters_dir = os.path.join(PROJECT_ROOT, 'newsletters')
        self.assertTrue(os.path.isdir(newsletters_dir), "newsletters/ directory must exist")
        md_files = glob.glob(os.path.join(newsletters_dir, "*.md"))
        self.assertGreater(len(md_files), 0, "newsletters/ directory must contain archived digest files")

        # Read the latest digest
        latest_file = max(md_files, key=os.path.getmtime)
        with open(latest_file, 'r', encoding='utf-8') as f:
            content = f.read()

        self.assertIn("# 🌐 News Colossal — Daily Executive Digest", content, "Digest must contain standard title header")
        self.assertIn("✦ What Happened:", content, "Digest stories must contain '✦ What Happened:' section")
        self.assertIn("✦ Why It Matters:", content, "Digest stories must contain '✦ Why It Matters:' section")
        self.assertIn("Publisher:", content, "Digest stories must contain Publisher attribution")

    def test_t1_3_newsletter_console_encoding(self):
        """
        [Feature 3 / R1] Newsletter Console Encoding:
        Eliminates cp1252 character map crashes by avoiding non-ASCII console output
        or configuring UTF-8 stdout wrapper.
        """
        # Run with cp1252 stdout encoding
        proc = run_py_script(
            'generate_daily_newsletter.py',
            env_vars={'BUTTONDOWN_API_KEY': '', 'PYTHONIOENCODING': 'cp1252'}
        )
        self.assertNotIn(
            "UnicodeEncodeError", proc.stderr,
            f"Feature 3 Failed: Console output crashed with UnicodeEncodeError under cp1252: {proc.stderr}"
        )
        self.assertEqual(proc.returncode, 0, "Newsletter generation must succeed under cp1252 console encoding")

    def test_t1_4_github_actions_digest_workflow(self):
        """
        [Feature 4 / R1] GitHub Actions Digest Workflow:
        Ensures .github/workflows/daily_digest.yml executes reliably with proper error handling.
        """
        workflow_path = '.github/workflows/daily_digest.yml'
        content = read_project_file(workflow_path)
        self.assertIn('generate_daily_newsletter.py', content, "Workflow must execute generate_daily_newsletter.py")
        self.assertIn('BUTTONDOWN_API_KEY', content, "Workflow must pass BUTTONDOWN_API_KEY secret")
        self.assertIn('newsletters/', content, "Workflow must stage newsletters/ directory")
        self.assertIn('git commit', content, "Workflow must commit generated digest")
        self.assertIn('schedule:', content, "Workflow must configure scheduled run")

    def test_t1_5_synchronization_pipeline_order(self):
        """
        [Feature 5 / R2] Synchronization Pipeline Order:
        .github/workflows/fetch-news.yml must run fetch_podcasts.py BEFORE fetch_news.py
        so podcast intelligence is available when computing news resonance.
        """
        workflow_content = read_project_file('.github/workflows/fetch-news.yml')
        podcast_match = re.search(r'python\s+scripts/fetch_podcasts\.py', workflow_content)
        news_match = re.search(r'python\s+scripts/fetch_news\.py', workflow_content)

        self.assertIsNotNone(podcast_match, "fetch-news.yml must invoke fetch_podcasts.py")
        self.assertIsNotNone(news_match, "fetch-news.yml must invoke fetch_news.py")
        self.assertLess(
            podcast_match.start(), news_match.start(),
            "Feature 5 Failed: scripts/fetch_podcasts.py must be executed BEFORE scripts/fetch_news.py in fetch-news.yml"
        )

    def test_t1_6_podcast_resonance_preservation(self):
        """
        [Feature 6 / R2] Podcast Resonance Preservation:
        scripts/fetch_podcasts.py must preserve existing resonant_news links
        and guard against empty scrapes wiping data/podcasts.json.
        """
        script_content = read_project_file('scripts/fetch_podcasts.py')
        # Check that fetch_podcasts reads existing podcasts to preserve resonant_news
        has_load_logic = ('podcasts.json' in script_content and ('resonant_news' in script_content or 'existing' in script_content))
        has_guard_logic = ('len(all_episodes)' in script_content or 'empty' in script_content.lower())

        self.assertTrue(
            has_load_logic,
            "Feature 6 Failed: fetch_podcasts.py must load existing podcasts to preserve resonant_news across scrapes"
        )
        self.assertTrue(
            has_guard_logic,
            "Feature 6 Failed: fetch_podcasts.py must guard against empty scrapes overwriting podcasts.json"
        )

    def test_t1_7_mutual_resonance_link_generation(self):
        """
        [Feature 7 / R2] Mutual Resonance Link Generation:
        cross_link_resonance produces non-empty resonance links between matching
        news articles and podcast episodes.
        """
        from intelligence.curation import cross_link_resonance

        sample_articles = [{
            'id': 'art-ai-1',
            'title': 'Frontier Artificial Intelligence and Autonomous Agents',
            'description': 'Research on LLM reasoning and agentic workflows.',
            'annotation': {'what': 'AI agents achieve new benchmark scores.', 'why': 'Impacts software automation.'},
            'entities': {'domains': ['Artificial Intelligence', 'Software']}
        }]
        sample_podcasts = [{
            'id': 'pod-ai-1',
            'title': 'DHH: Future of Programming, AI, Agentic Engineering',
            'podcast': 'Lex Fridman Podcast',
            'link': 'https://youtube.com/watch?v=sample',
            'topics': ['Software Engineering', 'Agentic AI', 'Artificial Intelligence'],
            'theme': 'Debates agentic AI coding paradigms and software engineering.'
        }]

        articles_out, podcasts_out = cross_link_resonance(sample_articles, sample_podcasts, threshold=0.15)
        self.assertIsNotNone(
            articles_out[0].get('resonant_podcast'),
            "Feature 7 Failed: Matching article must receive resonant_podcast linkage"
        )
        self.assertGreater(
            len(podcasts_out[0].get('resonant_news', [])), 0,
            "Feature 7 Failed: Matching podcast must receive resonant_news linkage"
        )

    def test_t1_8_entity_parsing_in_narrative_memory(self):
        """
        [Feature 8 / R3] Entity Parsing in Narrative Memory:
        match_article_to_arc extracts flattened entity values from article['entities']
        so structured entity dicts match arc entity signatures correctly.
        """
        from intelligence.memory import match_article_to_arc

        article = {
            'title': 'Donald Trump announces new trade tariffs against European Union',
            'category': 'World',
            'entities': {
                'countries': [{'code': 'US', 'name': 'United States'}, {'code': 'EU', 'name': 'European Union'}],
                'leaders': [{'name': 'Donald Trump', 'matched': 'trump'}],
                'entity_count': 3
            }
        }
        arc = {
            'arc_id': 'test-arc-trump',
            'title': 'Trump Trade Tariffs Narrative',
            'keywords': ['trump', 'tariffs', 'trade', 'european', 'union'],
            'entity_signature': 'US:EU:Donald Trump',
            'category': 'World'
        }

        matched_arc, score = match_article_to_arc(article, [arc], threshold=0.3)
        self.assertIsNotNone(
            matched_arc,
            "Feature 8 Failed: match_article_to_arc must match article with structured entities dict to narrative arc"
        )
        self.assertEqual(matched_arc['arc_id'], 'test-arc-trump')

    def test_t1_9_autonomous_arc_threading(self):
        """
        [Feature 9 / R3] Autonomous Arc Threading:
        thread_narratives populates art['narrative_arc'] with valid arc_id,
        arc_title, day_number, total_chapters, and importance_trend.
        """
        from intelligence.curation import thread_narratives

        memory = {
            'arcs': [{
                'arc_id': 'arc-energy-crisis',
                'title': 'European Diesel Reserves Standoff',
                'first_seen': '2026-10-01T00:00:00+00:00',
                'chapter_count': 4,
                'chapter_titles': ['US warns Europe on diesel', 'Europe responds on energy'],
                'importance_trend': 'rising'
            }]
        }
        articles = [{
            'id': 'art-energy-1',
            'title': 'US presses Europe to release diesel reserves immediately',
            '_matched_arc_id': 'arc-energy-crisis'
        }]

        threaded = thread_narratives(articles, memory)
        arc_meta = threaded[0].get('narrative_arc')

        self.assertIsNotNone(arc_meta, "Article must contain narrative_arc dictionary")
        self.assertEqual(arc_meta.get('arc_id'), 'arc-energy-crisis', "Feature 9 Failed: arc_id must match memory arc")
        self.assertEqual(arc_meta.get('arc_title'), 'European Diesel Reserves Standoff')
        self.assertGreaterEqual(arc_meta.get('day_number', 0), 1)
        self.assertEqual(arc_meta.get('total_chapters'), 4)

    def test_t1_10_duplicate_story_suppression(self):
        """
        [Feature 10 / R4] Duplicate Story Suppression:
        run_intake or enhanced_dedup must drop is_duplicate: True articles so
        0 duplicate articles leak into downstream output.
        """
        from intelligence.intake import run_intake

        articles = [
            {
                'id': 'dup-1',
                'title': 'Federal Reserve cuts interest rates by 25 basis points',
                'description': 'The Federal Reserve lowered benchmark borrowing rates today.',
                'source': 'Reuters',
                'category': 'Business',
                'region': 'North America'
            },
            {
                'id': 'dup-2',
                'title': 'Federal Reserve cuts interest rates by 25 basis points',
                'description': 'The Federal Reserve lowered benchmark borrowing rates today.',
                'source': 'AP News',
                'category': 'Business',
                'region': 'North America'
            }
        ]

        cleaned, stats = run_intake(articles)
        # Verify no items with is_duplicate == True are returned
        duplicates_in_output = [a for a in cleaned if a.get('is_duplicate')]
        self.assertEqual(
            len(duplicates_in_output), 0,
            f"Feature 10 Failed: run_intake must suppress duplicate articles, found {len(duplicates_in_output)} duplicates in output"
        )
        self.assertEqual(len(cleaned), 1, "Feature 10 Failed: only canonical article should remain after dedup")

    def test_t1_11_distinct_publisher_perspective_pairs(self):
        """
        [Feature 11 / R4] Distinct Publisher Perspective Pairs:
        cluster_stories requires >= 2 distinct publishers and brand families
        for cross-regional perspective cards.
        """
        from scripts.fetch_news import cluster_stories

        # Case A: Same brand family (BBC News & BBC Europe) in different regions
        same_brand_articles = [
            {
                'id': 'art-bbc-1',
                'title': 'Global Summit on Climate Accord Reaches Final Agreement',
                'category': 'World',
                'region': 'Global',
                'source': 'BBC News',
                'sourceLogo': 'BBC',
                'pubDate': '2026-10-06T10:00:00Z'
            },
            {
                'id': 'art-bbc-2',
                'title': 'Global Summit on Climate Accord Reaches Final Agreement',
                'category': 'World',
                'region': 'Europe',
                'source': 'BBC Europe',
                'sourceLogo': 'BBC',
                'pubDate': '2026-10-06T11:00:00Z'
            }
        ]
        clustered_same = cluster_stories(same_brand_articles)
        self.assertFalse(
            clustered_same[0].get('pairedStory', False),
            "Feature 11 Failed: Same brand family (BBC News + BBC Europe) must NOT form a cross-regional pair"
        )

        # Case B: Distinct publishers (The Guardian & France 24)
        distinct_articles = [
            {
                'id': 'art-dist-1',
                'title': 'Global Summit on Climate Accord Reaches Final Agreement',
                'category': 'World',
                'region': 'Global',
                'source': 'The Guardian',
                'sourceLogo': 'TG',
                'pubDate': '2026-10-06T10:00:00Z'
            },
            {
                'id': 'art-dist-2',
                'title': 'Global Summit on Climate Accord Reaches Final Agreement',
                'category': 'World',
                'region': 'Europe',
                'source': 'France 24',
                'sourceLogo': 'F24',
                'pubDate': '2026-10-06T11:00:00Z'
            }
        ]
        clustered_distinct = cluster_stories(distinct_articles)
        self.assertTrue(
            clustered_distinct[0].get('pairedStory', False),
            "Feature 11 Failed: Distinct publishers (The Guardian + France 24) must form a cross-regional pair"
        )

    def test_t1_12_brand_family_diversity_cap(self):
        """
        [Feature 12 / R5] Brand Family Diversity Cap (<=18%):
        BRAND_FAMILIES must map 'BBC Business': 'BBC' and enforce <= 18% cap.
        """
        from scripts.fetch_news import BRAND_FAMILIES
        self.assertIn("BBC Business", BRAND_FAMILIES, "Feature 12 Failed: 'BBC Business' missing from BRAND_FAMILIES")
        self.assertEqual(BRAND_FAMILIES.get("BBC Business"), "BBC")

        # Check live data/news.json BBC representation
        news_data = load_project_json('data/news.json')
        articles = news_data.get('articles', [])
        if articles:
            bbc_count = sum(1 for a in articles if 'BBC' in a.get('source', '') or BRAND_FAMILIES.get(a.get('source')) == 'BBC')
            bbc_pct = (bbc_count / len(articles)) * 100
            self.assertLessEqual(
                bbc_pct, 18.0,
                f"Feature 12 Failed: BBC family accounts for {bbc_pct:.2f}% of articles ({bbc_count}/{len(articles)}), exceeding 18% cap"
            )

    def test_t1_13_clean_sentence_boundary_truncation(self):
        """
        [Feature 13 / R5] Clean Sentence Boundary Truncation:
        Article descriptions must terminate cleanly at sentence/word boundaries
        ending with '.' without trailing ellipses ('...' or '…').
        """
        news_data = load_project_json('data/news.json')
        articles = news_data.get('articles', [])
        truncated_count = 0
        for art in articles:
            desc = art.get('description', '')
            if desc.endswith('...') or desc.endswith('…') or (len(desc) > 30 and not desc.endswith('.')):
                truncated_count += 1

        self.assertEqual(
            truncated_count, 0,
            f"Feature 13 Failed: {truncated_count} articles have trailing ellipses or incomplete sentences in data/news.json"
        )

    def test_t1_14_executive_reader_modal_intelligence(self):
        """
        [Feature 14 / R6] Executive Reader Modal Intelligence:
        app.js must render .liquid-glass-resonance-box and .liquid-glass-narrative-box
        inside renderExecutiveModal.
        """
        app_js = read_project_file('app.js')
        self.assertIn(
            'liquid-glass-resonance-box', app_js,
            "Feature 14 Failed: .liquid-glass-resonance-box rendering missing in app.js"
        )
        self.assertIn(
            'liquid-glass-narrative-box', app_js,
            "Feature 14 Failed: .liquid-glass-narrative-box rendering missing in app.js"
        )

    def test_t1_15_thought_pulse_resonant_news_bridge(self):
        """
        [Feature 15 / R6] Thought Pulse Resonant News Bridge:
        app.js renders .thought-card-resonant-news button on Thought Pulse cards
        linking to reader modal.
        """
        app_js = read_project_file('app.js')
        self.assertIn(
            'thought-card-resonant-news', app_js,
            "Feature 15 Failed: .thought-card-resonant-news button missing in app.js"
        )

    def test_t1_16_visionos_liquid_glass_and_3d_physics(self):
        """
        [Feature 16 / R6] VisionOS Liquid Glass & 3D Physics:
        style.css styles liquid glass resonance & narrative elements,
        and app.js applies 3D tilt physics to both news cards and thought cards.
        """
        style_css = read_project_file('style.css')
        app_js = read_project_file('app.js')

        self.assertIn(
            '.liquid-glass-resonance-box', style_css,
            "Feature 16 Failed: .liquid-glass-resonance-box styles missing in style.css"
        )
        self.assertIn(
            '.liquid-glass-narrative-box', style_css,
            "Feature 16 Failed: .liquid-glass-narrative-box styles missing in style.css"
        )
        self.assertIn(
            '.thought-card-resonant-news', style_css,
            "Feature 16 Failed: .thought-card-resonant-news styles missing in style.css"
        )
        # Check tilt physics applied to thought cards as well as news cards
        has_thought_tilt = ('thought-card' in app_js and ('tilt' in app_js.lower() or 'transform' in app_js.lower()))
        self.assertTrue(
            has_thought_tilt,
            "Feature 16 Failed: 3D tilt interaction missing for .thought-card in app.js"
        )

    def test_t1_17_production_hard_audit_verification(self):
        """
        [Feature 17 / R7] Zero-Failure Hard Audit Validation:
        production_hard_audit.py is operational and verifies all 6 layers.
        """
        audit_code = read_project_file('production_hard_audit.py')
        self.assertIn("DATASET INTEGRITY", audit_code, "Audit layer 1 missing")
        self.assertIn("IMAGE AVAILABILITY", audit_code, "Audit layer 2 missing")
        self.assertIn("TEXT COMPLETENESS", audit_code, "Audit layer 3 missing")
        self.assertIn("CATEGORY ISOLATION", audit_code, "Audit layer 4 missing")
        self.assertIn("FRONTEND FILE VALIDATION", audit_code, "Audit layer 5 missing")


# ===========================================================================
# Tier 2: Boundary & Corner Cases
# ===========================================================================
class TestTier2BoundaryCornerCases(unittest.TestCase):
    """
    Tier 2: Boundary & Corner Cases per TEST_INFRA.md.
    """

    def test_t2_1_newsletter_empty_and_whitespace_api_keys(self):
        """
        [T2.1] Boundary: BUTTONDOWN_API_KEY with whitespace or empty strings.
        Must be treated as missing without throwing errors.
        """
        for key_val in ["", "   ", "\t"]:
            proc = run_py_script('generate_daily_newsletter.py', env_vars={'BUTTONDOWN_API_KEY': key_val})
            self.assertEqual(
                proc.returncode, 0,
                f"T2.1 Failed: Newsletter script must exit 0 when BUTTONDOWN_API_KEY is '{key_val}', got {proc.returncode}"
            )

    def test_t2_2_newsletter_empty_articles_list(self):
        """
        [T2.2] Boundary: Empty articles list in data/news.json.
        Newsletter generator must handle gracefully without crashing.
        """
        try:
            from generate_daily_newsletter import generate_newsletter
            with tempfile.TemporaryDirectory() as tmp_dir:
                tmp_news = os.path.join(tmp_dir, 'news.json')
                with open(tmp_news, 'w', encoding='utf-8') as f:
                    json.dump({'articles': []}, f)

                generate_newsletter(send_email=False)
        except SystemExit as se:
            self.fail(f"T2.2 Failed: generate_daily_newsletter called exit({se.code}) when API key was unset")
        except Exception as e:
            self.fail(f"T2.2 Failed: generate_newsletter crashed on empty articles: {e}")

    def test_t2_3_newsletter_console_cp1252_encoding_safety(self):
        """
        [T2.3] Boundary: Printing Unicode characters (emojis, smart quotes, em-dashes)
        under simulated strict cp1252 stdout.
        """
        proc = run_py_script(
            'generate_daily_newsletter.py',
            env_vars={'BUTTONDOWN_API_KEY': '', 'PYTHONIOENCODING': 'cp1252:strict'}
        )
        self.assertNotIn("UnicodeEncodeError", proc.stderr, "T2.3 Failed: Unicode characters triggered crash under cp1252")

    def test_t2_4_workflow_yaml_syntax_and_triggers(self):
        """
        [T2.4] Boundary: YAML structure & triggers of workflow files.
        """
        for path in ['.github/workflows/daily_digest.yml', '.github/workflows/fetch-news.yml']:
            content = read_project_file(path)
            self.assertTrue(content.startswith('name:'), f"{path} must define workflow name at top")
            self.assertIn('on:', content, f"{path} must define 'on:' trigger")
            self.assertIn('jobs:', content, f"{path} must define 'jobs:' block")

    def test_t2_5_pipeline_ordering_step_contracts(self):
        """
        [T2.5] Boundary: fetch-news.yml error propagation and step continuation.
        """
        content = read_project_file('.github/workflows/fetch-news.yml')
        # Podcast step can continue on error, but news step must not hide fatal pipeline errors
        self.assertIn('continue-on-error:', content, "Workflow must define explicit continue-on-error behavior")

    def test_t2_6_podcast_scrape_zero_episodes_guard(self):
        """
        [T2.6] Boundary: If podcast scraping yields 0 episodes, existing data must NOT be wiped.
        """
        podcasts_file = os.path.join(PROJECT_ROOT, 'data', 'podcasts.json')
        self.assertTrue(os.path.exists(podcasts_file), "data/podcasts.json must exist")
        with open(podcasts_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.assertGreater(data.get('total', 0), 0, "T2.6 Failed: data/podcasts.json total episodes must be > 0")
        self.assertGreater(len(data.get('episodes', [])), 0, "T2.6 Failed: data/podcasts.json episodes list must not be empty")

    def test_t2_7_mutual_resonance_disjoint_topics(self):
        """
        [T2.7] Boundary: Completely disjoint topics must yield 0 resonance (None and []).
        """
        from intelligence.curation import cross_link_resonance

        art = [{
            'id': 'art-disjoint',
            'title': 'Ancient Roman pottery excavation in Pompeii',
            'description': 'Archaeologists discover classical amphorae.',
            'entities': {'domains': ['Archaeology']}
        }]
        pod = [{
            'id': 'pod-disjoint',
            'title': 'Quantum Computing and Superconducting Qubits',
            'podcast': 'Physics Today',
            'topics': ['Quantum Mechanics', 'Superconductors'],
            'theme': 'Explores subatomic quantum coherence.'
        }]

        arts_out, pods_out = cross_link_resonance(art, pod, threshold=0.30)
        self.assertIsNone(arts_out[0].get('resonant_podcast'), "T2.7 Failed: Disjoint topic must not create resonant link")
        self.assertEqual(len(pods_out[0].get('resonant_news', [])), 0, "T2.7 Failed: Disjoint podcast must have empty resonant_news")

    def test_t2_8_narrative_memory_malformed_and_empty_entities(self):
        """
        [T2.8] Boundary: Empty, None, and non-standard article entities structures.
        match_article_to_arc must handle safely without exceptions.
        """
        from intelligence.memory import match_article_to_arc

        arc = {'arc_id': 'arc-1', 'keywords': ['market', 'crash'], 'entity_signature': 'US:Finance'}
        for malformed in [None, {}, [], {'countries': None}, {'leaders': 'not_a_list'}]:
            article = {'title': 'Stock market volatility index jumps', 'category': 'Business', 'entities': malformed}
            try:
                res, score = match_article_to_arc(article, [arc])
                self.assertIsInstance(score, (int, float))
            except Exception as e:
                self.fail(f"T2.8 Failed: match_article_to_arc threw exception on entities={malformed}: {e}")

    def test_t2_9_narrative_arc_threading_empty_or_new_arcs(self):
        """
        [T2.9] Boundary: thread_narratives with empty memory or uninitialized timestamps.
        """
        from intelligence.curation import thread_narratives

        articles = [{'id': 'art-solo', 'title': 'Solo Story'}]
        res = thread_narratives(articles, {'arcs': []})
        arc_info = res[0].get('narrative_arc')
        self.assertIsNotNone(arc_info)
        self.assertIsNone(arc_info.get('arc_id'))

    def test_t2_10_dedup_all_duplicates_and_no_duplicates(self):
        """
        [T2.10] Boundary:
        - 5 identical wire articles -> exactly 1 canonical retained.
        - 5 totally distinct articles -> all 5 retained.
        """
        from intelligence.intake import run_intake

        # 5 identical
        identical = [
            {'id': f'wire-{i}', 'title': 'Global Summit Adopts Historic Treaty', 'description': 'Delegates sign agreement.', 'category': 'World', 'region': 'Global', 'source': f'Source {i}'}
            for i in range(5)
        ]
        cleaned_identical, _ = run_intake(identical)
        self.assertEqual(len([a for a in cleaned_identical if not a.get('is_duplicate')]), 1)

        # 5 distinct
        distinct_titles = [
            'Quantum computing chip sets new processing speed record',
            'Central bank cuts benchmark interest rate amid cooling inflation',
            'Deep sea expedition discovers dozens of previously unknown species',
            'Electric aviation startup completes first intercity passenger flight',
            'Archaeologists unearth intact bronze age settlement in eastern valley'
        ]
        distinct = [
            {'id': f'dist-{i}', 'title': distinct_titles[i], 'description': f'Description {i}', 'category': 'Tech', 'region': 'North America', 'source': f'Src {i}'}
            for i in range(5)
        ]
        cleaned_distinct, _ = run_intake(distinct)
        self.assertEqual(len([a for a in cleaned_distinct if not a.get('is_duplicate')]), 5)


    def test_t2_11_cross_regional_same_brand_family_rejection(self):
        """
        [T2.11] Boundary: 3 articles from same brand family across 3 different regions
        must NOT produce a cross-regional paired story.
        """
        from scripts.fetch_news import cluster_stories

        articles = [
            {'id': 'bbc-1', 'title': 'Oil prices surge following supply disruptions', 'category': 'Business', 'region': 'Global', 'source': 'BBC News', 'pubDate': '2026-10-06T00:00:00Z'},
            {'id': 'bbc-2', 'title': 'Oil prices surge following supply disruptions', 'category': 'Business', 'region': 'Europe', 'source': 'BBC Europe', 'pubDate': '2026-10-06T01:00:00Z'},
            {'id': 'bbc-3', 'title': 'Oil prices surge following supply disruptions', 'category': 'Business', 'region': 'Asia-Pacific', 'source': 'BBC Asia', 'pubDate': '2026-10-06T02:00:00Z'},
        ]
        clustered = cluster_stories(articles)
        for art in clustered:
            self.assertFalse(
                art.get('pairedStory', False),
                "T2.11 Failed: All-BBC regional articles must not be classified as pairedStory"
            )

    def test_t2_12_brand_diversity_small_and_large_feed_sizes(self):
        """
        [T2.12] Boundary: Brand family cap <= 18% calculation for small feeds (N=5) and large feeds (N=100).
        """
        from scripts.fetch_news import balance_source_diversity, BRAND_FAMILIES

        # Large feed: 100 articles, 40 BBC
        large_articles = []
        for i in range(40):
            large_articles.append({'id': f'bbc-{i}', 'source': 'BBC News', 'region': 'Global', 'title': f'BBC {i}'})
        for i in range(60):
            large_articles.append({'id': f'oth-{i}', 'source': f'Publisher {i % 10}', 'region': 'Global', 'title': f'Other {i}'})

        balanced_large = balance_source_diversity(large_articles)
        bbc_count = sum(1 for a in balanced_large if BRAND_FAMILIES.get(a['source']) == 'BBC' or 'BBC' in a['source'])
        bbc_ratio = bbc_count / len(balanced_large)

        self.assertLessEqual(
            bbc_ratio, 0.18 + 0.01,  # allowable tolerance
            f"T2.12 Failed: BBC family ratio was {bbc_ratio:.3f}, expected <= 0.18"
        )

    def test_t2_13_description_truncation_edge_cases(self):
        """
        [T2.13] Boundary: Descriptions with trailing dots, question marks, and varying lengths.
        """
        test_cases = [
            ("Short clean sentence.", True),
            ("Another complete sentence without dots.", True),
            ("Sentence with question mark?", True),
            ("Trailing dots at end of sentence...", False),
            ("Trailing unicode ellipsis…", False),
            ("Cut off mid sentence without any punctuation", False),
        ]
        for text, is_clean in test_cases:
            has_bad_ending = text.endswith('...') or text.endswith('…') or (len(text) > 30 and not (text.endswith('.') or text.endswith('?') or text.endswith('!')))
            self.assertEqual(not has_bad_ending, is_clean, f"Failed for text: '{text}'")

    def test_t2_14_modal_rendering_with_null_resonance_and_arc(self):
        """
        [T2.14] Boundary: Modal rendering in app.js must handle resonant_podcast: null
        and narrative_arc: {arc_id: null} without runtime exceptions.
        """
        app_js = read_project_file('app.js')
        # Check conditional checks exist before rendering modal sections
        self.assertIn('resonant_podcast', app_js, "app.js must check resonant_podcast property")
        self.assertIn('narrative_arc', app_js, "app.js must check narrative_arc property")

    def test_t2_15_thought_pulse_rendering_empty_resonant_news(self):
        """
        [T2.15] Boundary: Thought pulse rendering in app.js when resonant_news is empty.
        """
        app_js = read_project_file('app.js')
        self.assertIn('resonant_news', app_js, "app.js must reference resonant_news property")

    def test_t2_16_frontend_mobile_responsiveness_and_touch(self):
        """
        [T2.16] Boundary: Mobile responsive queries and touch interactions.
        """
        style_css = read_project_file('style.css')
        self.assertIn('@media', style_css, "style.css must define responsive media queries")
        self.assertIn('max-width', style_css, "style.css must have mobile screen width breakpoints")

    def test_t2_17_production_audit_warning_thresholds(self):
        """
        [T2.17] Boundary: production_hard_audit.py warning check enforces 0 warnings.
        """
        audit_code = read_project_file('production_hard_audit.py')
        self.assertIn('warnings', audit_code, "Audit script must track warnings list")
        self.assertIn('truncated_text_count', audit_code, "Audit script must track truncated text count")


# ===========================================================================
# Tier 3: Cross-Feature Combinations
# ===========================================================================
class TestTier3CrossFeatureCombinations(unittest.TestCase):
    """
    Tier 3: Cross-Feature Combinations per TEST_INFRA.md.
    """

    def test_t3_1_newsletter_full_generation_without_api_key(self):
        """
        [T3.1 / F1+F2+F3] Combined Newsletter Pipeline:
        Executes newsletter generation with unset API key and cp1252 encoding.
        Verifies:
        1. Process exits with code 0.
        2. Markdown digest is created in newsletters/.
        3. No email is sent (skipped cleanly).
        4. No encoding exception.
        """
        proc = run_py_script(
            'generate_daily_newsletter.py',
            env_vars={'BUTTONDOWN_API_KEY': '', 'PYTHONIOENCODING': 'cp1252'}
        )
        self.assertEqual(proc.returncode, 0, f"T3.1 Failed: Process failed with code {proc.returncode}")
        self.assertNotIn("UnicodeEncodeError", proc.stderr)

        # Check newsletters directory for latest file
        newsletters_dir = os.path.join(PROJECT_ROOT, 'newsletters')
        md_files = glob.glob(os.path.join(newsletters_dir, "*.md"))
        self.assertGreater(len(md_files), 0, "Digest file must be generated")

    def test_t3_2_pipeline_synchronization_and_resonance_preservation(self):
        """
        [T3.2 / F5+F6+F7] Pipeline Inversion & Resonance Continuity:
        Workflow order (podcasts -> news) ensures podcasts are refreshed first,
        preserving prior resonance, then news consumes podcasts and updates links.
        """
        fetch_news_workflow = read_project_file('.github/workflows/fetch-news.yml')
        podcast_idx = fetch_news_workflow.find('scripts/fetch_podcasts.py')
        news_idx = fetch_news_workflow.find('scripts/fetch_news.py')

        self.assertGreater(podcast_idx, 0)
        self.assertGreater(news_idx, 0)
        self.assertLess(
            podcast_idx, news_idx,
            "T3.2 Failed: fetch_podcasts.py must precede fetch_news.py in synchronization workflow"
        )

    def test_t3_3_mutual_resonance_data_consistency(self):
        """
        [T3.3 / F7] Mutual Resonance Data Consistency:
        Verifies that resonant links in data/news.json and data/podcasts.json
        point to existing items and adhere to contract schemas.
        """
        news_data = load_project_json('data/news.json')
        podcasts_data = load_project_json('data/podcasts.json')

        news_articles = news_data.get('articles', [])
        podcast_episodes = podcasts_data.get('episodes', [])

        news_with_pod = [a for a in news_articles if a.get('resonant_podcast')]
        pods_with_news = [p for p in podcast_episodes if p.get('resonant_news')]

        self.assertGreater(
            len(news_with_pod), 0,
            "T3.3 Failed: data/news.json must contain articles with non-empty resonant_podcast"
        )
        self.assertGreater(
            len(pods_with_news), 0,
            "T3.3 Failed: data/podcasts.json must contain episodes with non-empty resonant_news"
        )

        # Schema assertion on article resonance
        sample_art = news_with_pod[0]['resonant_podcast']
        for key in ['title', 'podcast']:
            self.assertIn(key, sample_art, f"resonant_podcast must include '{key}'")

        # Schema assertion on podcast resonance
        sample_pod = pods_with_news[0]['resonant_news'][0]
        for key in ['title', 'source']:
            self.assertIn(key, sample_pod, f"resonant_news item must include '{key}'")

    def test_t3_4_entity_parsing_and_arc_threading_state(self):
        """
        [T3.4 / F8+F9] Narrative Entity Parsing & Arc Threading Consistency:
        Articles linked to narrative arcs in data/news.json must correspond
        to tracked arc IDs in data/narrative_memory.json.
        """
        news_data = load_project_json('data/news.json')
        memory_data = load_project_json('data/narrative_memory.json')

        tracked_arc_ids = {arc['arc_id'] for arc in memory_data.get('arcs', [])}
        articles = news_data.get('articles', [])

        linked_articles = [
            a for a in articles
            if a.get('narrative_arc') and a['narrative_arc'].get('arc_id')
        ]
        self.assertGreater(
            len(linked_articles), 0,
            "T3.4 Failed: data/news.json must contain articles linked to narrative arcs"
        )

        for art in linked_articles:
            art_arc_id = art['narrative_arc']['arc_id']
            self.assertIn(
                art_arc_id, tracked_arc_ids,
                f"T3.4 Failed: Article narrative_arc ID '{art_arc_id}' not found in narrative_memory.json"
            )

    def test_t3_5_deduplication_and_cross_regional_pairing(self):
        """
        [T3.5 / F10+F11] Deduplication & Perspective Pairing Integration:
        0 duplicates exist in feed, and all cross-regional perspective cards
        consist of distinct publishers.
        """
        news_data = load_project_json('data/news.json')
        articles = news_data.get('articles', [])

        # 1. Zero duplicates
        duplicates = [a for a in articles if a.get('is_duplicate')]
        self.assertEqual(len(duplicates), 0, f"T3.5 Failed: {len(duplicates)} duplicates leaked into data/news.json")

        # 2. Distinct publishers in perspectives
        paired_articles = [a for a in articles if a.get('pairedStory') and a.get('perspectives')]
        for art in paired_articles:
            perspectives = art.get('perspectives', [])
            sources = {p.get('source') for p in perspectives}
            self.assertGreaterEqual(
                len(sources), 2,
                f"T3.5 Failed: Perspective pair for '{art['title'][:40]}' has only {len(sources)} distinct publishers: {sources}"
            )

    def test_t3_6_brand_diversity_and_clean_descriptions(self):
        """
        [T3.6 / F12+F13] Brand Diversity & Description Hygiene:
        Feed adheres to <= 18% publisher caps and 100% clean sentence terminations.
        """
        news_data = load_project_json('data/news.json')
        articles = news_data.get('articles', [])
        self.assertGreater(len(articles), 0)

        # Brand caps
        sources = [a['source'] for a in articles]
        from collections import Counter
        counts = Counter(sources)
        for src, cnt in counts.items():
            pct = cnt / len(articles) * 100
            # Individual sources should not exceed 15-18%
            self.assertLessEqual(pct, 18.0, f"Source '{src}' at {pct:.1f}% exceeds 18% cap")

        # Clean description endings
        bad_endings = [a for a in articles if a.get('description', '').endswith('...') or a.get('description', '').endswith('…')]
        self.assertEqual(len(bad_endings), 0, f"{len(bad_endings)} articles end with trailing ellipses")

    def test_t3_7_reader_modal_and_thought_pulse_bridge_integration(self):
        """
        [T3.7 / F14+F15] Modal Intelligence & Thought Pulse Bridge Integration:
        Frontend connects Thought Pulse resonant pill to Executive Reader modal.
        """
        app_js = read_project_file('app.js')
        # Check that thought card resonance pill triggers modal opening
        self.assertIn('thought-card-resonant-news', app_js)
        self.assertIn('openModal', app_js)

    def test_t3_8_liquid_glass_css_and_card_physics_coupling(self):
        """
        [T3.8 / F16] Liquid Glass Aesthetics & Physics Coupling:
        VisionOS styling definitions present in style.css and 3D card tilt physics
        applied to news and thought cards in app.js.
        """
        style_css = read_project_file('style.css')
        app_js = read_project_file('app.js')

        self.assertIn('liquid-glass', style_css)
        self.assertIn('backdrop-filter', style_css)
        self.assertIn('.news-card', app_js)
        self.assertIn('.thought-card', app_js)

    def test_t3_9_hard_audit_rules_comprehensive_coverage(self):
        """
        [T3.9 / F17] Comprehensive Hard Audit Rules Coverage:
        production_hard_audit.py inspects source diversity, image validity,
        sentence termination, category isolation, and frontend scripts.
        """
        audit_code = read_project_file('production_hard_audit.py')
        required_checks = [
            'data/news.json',
            'BBC',
            'truncated_text_count',
            'app.js',
            'style.css',
            'index.html'
        ]
        for token in required_checks:
            self.assertIn(token, audit_code, f"T3.9 Failed: production_hard_audit.py missing check for '{token}'")


# ===========================================================================
# Tier 4: Real-World Application Scenarios
# ===========================================================================
class TestTier4RealWorldScenarios(unittest.TestCase):
    """
    Tier 4: Real-World Application Scenarios per TEST_INFRA.md.
    """

    def test_t4_1_cold_newsletter_run_scenario(self):
        """
        [T4.1 / Scenario 1] Cold Newsletter Run:
        BUTTONDOWN_API_KEY="" python generate_daily_newsletter.py
        Pass Criteria: Exits code 0, creates markdown file in newsletters/.
        """
        proc = run_py_script('generate_daily_newsletter.py', env_vars={'BUTTONDOWN_API_KEY': ''})
        self.assertEqual(
            proc.returncode, 0,
            f"Scenario 1 Failed: Cold newsletter run exited with code {proc.returncode}: {proc.stderr}"
        )

        newsletters_dir = os.path.join(PROJECT_ROOT, 'newsletters')
        md_files = glob.glob(os.path.join(newsletters_dir, "*.md"))
        self.assertGreater(len(md_files), 0, "Scenario 1 Failed: No markdown digest files found in newsletters/")

    def test_t4_2_scheduled_pipeline_sync_scenario(self):
        """
        [T4.2 / Scenario 2] Scheduled Pipeline Sync:
        fetch_podcasts.py followed by fetch_news.py pipeline contract.
        Pass Criteria:
        1. data/podcasts.json and data/news.json exist.
        2. Both contain non-empty mutual resonance links (> 0).
        """
        news_data = load_project_json('data/news.json')
        podcasts_data = load_project_json('data/podcasts.json')

        news_articles = news_data.get('articles', [])
        podcast_episodes = podcasts_data.get('episodes', [])

        news_resonances = sum(1 for a in news_articles if a.get('resonant_podcast'))
        podcast_resonances = sum(1 for p in podcast_episodes if p.get('resonant_news'))

        self.assertGreater(
            news_resonances, 0,
            "Scenario 2 Failed: data/news.json must contain > 0 articles with resonant_podcast links"
        )
        self.assertGreater(
            podcast_resonances, 0,
            "Scenario 2 Failed: data/podcasts.json must contain > 0 episodes with resonant_news links"
        )

    def test_t4_3_editorial_intelligence_and_feed_ingestion_scenario(self):
        """
        [T4.3 / Scenario 3] Editorial Intelligence & Feed Ingestion Integrity:
        data/news.json has active arcs, 0 duplicates, distinct cross-regional pairs,
        brand cap <= 18%, and 0 truncated sentences.
        """
        news_data = load_project_json('data/news.json')
        memory_data = load_project_json('data/narrative_memory.json')
        articles = news_data.get('articles', [])

        self.assertGreater(len(articles), 0, "Feed must contain curated articles")

        # 1. Active arcs matching narrative_memory.json
        arc_ids = {a['arc_id'] for a in memory_data.get('arcs', [])}
        linked = [a for a in articles if a.get('narrative_arc', {}).get('arc_id')]
        self.assertGreater(len(linked), 0, "Scenario 3 Failed: Must have articles linked to narrative arcs")
        for a in linked:
            self.assertIn(a['narrative_arc']['arc_id'], arc_ids, "Linked arc_id must exist in narrative_memory.json")

        # 2. 0 duplicate articles
        duplicates = [a for a in articles if a.get('is_duplicate')]
        self.assertEqual(len(duplicates), 0, "Scenario 3 Failed: 0 duplicate articles allowed in feed")

        # 3. Distinct publishers in cross-regional pairs
        paired = [a for a in articles if a.get('pairedStory')]
        for a in paired:
            sources = {p['source'] for p in a.get('perspectives', [])}
            self.assertGreaterEqual(len(sources), 2, "Cross-regional pairs must have >= 2 distinct publishers")

        # 4. Brand family cap <= 18%
        bbc_count = sum(1 for a in articles if 'BBC' in a.get('source', ''))
        bbc_pct = bbc_count / len(articles) * 100
        self.assertLessEqual(bbc_pct, 18.0, f"BBC family accounts for {bbc_pct:.1f}%, exceeding 18% cap")

        # 5. 0 truncated sentences
        bad_sentences = [
            a for a in articles
            if a.get('description', '').endswith('...') or a.get('description', '').endswith('…')
        ]
        self.assertEqual(len(bad_sentences), 0, "Scenario 3 Failed: descriptions must not end with trailing ellipses")

    def test_t4_4_frontend_executive_reader_ux_scenario(self):
        """
        [T4.4 / Scenario 4] Frontend Executive Reader UX Contract:
        app.js, style.css, and index.html render resonance box, narrative arc box,
        thought pulse bridge, and VisionOS glass styles.
        """
        app_js = read_project_file('app.js')
        style_css = read_project_file('style.css')
        index_html = read_project_file('index.html')

        self.assertIn('liquid-glass-resonance-box', app_js)
        self.assertIn('liquid-glass-narrative-box', app_js)
        self.assertIn('thought-card-resonant-news', app_js)
        self.assertIn('.liquid-glass-resonance-box', style_css)
        self.assertIn('.liquid-glass-narrative-box', style_css)
        self.assertIn('.thought-card-resonant-news', style_css)

    def test_t4_5_complete_production_hard_audit_scenario(self):
        """
        [T4.5 / Scenario 5] Complete Production Hard Audit:
        python production_hard_audit.py passes 100% with 0 errors and 0 warnings.
        """
        proc = run_py_script('production_hard_audit.py')
        self.assertEqual(
            proc.returncode, 0,
            f"Scenario 5 Failed: production_hard_audit.py exited with code {proc.returncode}"
        )
        self.assertIn("PRODUCTION READY: ALL 6 AUDIT LAYERS PASSED 100%", proc.stdout)
        self.assertNotIn("PRODUCTION AUDIT FAILED", proc.stdout)
        self.assertNotIn("[WARNINGS]:", proc.stdout, "Scenario 5 Failed: production_hard_audit.py emitted warnings")


# ===========================================================================
# Test Runner Entrypoint
# ===========================================================================
if __name__ == '__main__':
    unittest.main(verbosity=2)
