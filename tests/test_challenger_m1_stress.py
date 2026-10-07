#!/usr/bin/env python3
"""
Adversarial Stress Test Harness for Milestone M1 (News Colossal)
Author: challenger_m1_1 (Empirical Challenger)
Target: generate_daily_newsletter.py & .github/workflows/daily_digest.yml
"""

import os
import sys
import json
import tempfile
import subprocess
import unittest
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


class TestM1AdversarialStress(unittest.TestCase):
    """
    Adversarial empirical challenge suite for M1.
    """

    def _run_cli(self, env_overrides=None, args=None, cwd=PROJECT_ROOT):
        """Run generate_daily_newsletter.py via CLI subprocess."""
        cmd = [sys.executable, os.path.join(PROJECT_ROOT, "generate_daily_newsletter.py")]
        if args:
            cmd.extend(args)
        
        env = os.environ.copy()
        if env_overrides:
            for k, v in env_overrides.items():
                if v is None:
                    env.pop(k, None)
                else:
                    env[k] = v

        return subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            env=env,
            timeout=30
        )

    # -----------------------------------------------------------------------
    # Attack Vector 1: API Key Permutations & Exit Code Contract
    # -----------------------------------------------------------------------
    def test_stress_api_key_completely_unset(self):
        """Verify exit code 0 when BUTTONDOWN_API_KEY is completely unset from env."""
        proc = self._run_cli(env_overrides={"BUTTONDOWN_API_KEY": None})
        self.assertEqual(proc.returncode, 0, f"Unset API key failed with exit {proc.returncode}: {proc.stderr}")
        self.assertIn("[BUTTONDOWN] No API key configured. Skipping email delivery.", proc.stdout)

    def test_stress_api_key_empty_and_whitespace_variants(self):
        """Verify exit code 0 across multiple whitespace/blank API key values."""
        adversarial_keys = [
            "",
            " ",
            "    ",
            "\t",
            "\n",
            "\r\n",
            "   \t  \n  ",
        ]
        for key in adversarial_keys:
            with self.subTest(key=repr(key)):
                proc = self._run_cli(env_overrides={"BUTTONDOWN_API_KEY": key})
                self.assertEqual(
                    proc.returncode, 0,
                    f"API key {repr(key)} produced exit code {proc.returncode}: {proc.stderr}"
                )
                self.assertIn("[BUTTONDOWN] No API key configured. Skipping email delivery.", proc.stdout)

    def test_stress_api_key_dummy_network_failure(self):
        """Verify that an invalid API key causing HTTP 401/403 does not raise unhandled exception."""
        proc = self._run_cli(env_overrides={"BUTTONDOWN_API_KEY": "invalid_test_token_12345"})
        # Should catch HTTP error and not crash with exit 1
        self.assertEqual(
            proc.returncode, 0,
            f"Invalid API key crashed with exit {proc.returncode}: {proc.stderr}"
        )
        self.assertTrue(
            ("[BUTTONDOWN ERROR]" in proc.stdout) or ("[BUTTONDOWN SUCCESS]" in proc.stdout),
            f"Expected BUTTONDOWN ERROR or SUCCESS log, got: {proc.stdout}"
        )

    # -----------------------------------------------------------------------
    # Attack Vector 2: Console Encodings & Hostile Environment
    # -----------------------------------------------------------------------
    def test_stress_encoding_cp1252_strict(self):
        """Simulate strict Windows cp1252 console output."""
        proc = self._run_cli(env_overrides={
            "BUTTONDOWN_API_KEY": "",
            "PYTHONIOENCODING": "cp1252:strict"
        })
        self.assertEqual(proc.returncode, 0, f"cp1252:strict failed: {proc.stderr}")
        self.assertNotIn("UnicodeEncodeError", proc.stderr)

    def test_stress_encoding_ascii_strict(self):
        """Simulate strict ASCII console output."""
        proc = self._run_cli(env_overrides={
            "BUTTONDOWN_API_KEY": "",
            "PYTHONIOENCODING": "ascii:strict"
        })
        self.assertEqual(proc.returncode, 0, f"ascii:strict failed: {proc.stderr}")
        self.assertNotIn("UnicodeEncodeError", proc.stderr)

    def test_stress_encoding_latin1(self):
        """Simulate latin-1 console output."""
        proc = self._run_cli(env_overrides={
            "BUTTONDOWN_API_KEY": "",
            "PYTHONIOENCODING": "latin-1:strict"
        })
        self.assertEqual(proc.returncode, 0, f"latin-1 failed: {proc.stderr}")
        self.assertNotIn("UnicodeEncodeError", proc.stderr)

    def test_stress_hostile_unicode_env_vars(self):
        """Pass non-ASCII Unicode and emojis in environment variables."""
        hostile_env = {
            "BUTTONDOWN_API_KEY": "",
            "UNICODE_VAR_1": "日本語テスト_Привет_мир_€$¥",
            "UNICODE_VAR_2": "⚡🌐✦🚀✨🔥",
            "UNICODE_VAR_3": "Right-to-Left: \u200fالعربية\u200e \u200fעברית\u200e",
            "PYTHONIOENCODING": "cp1252:replace"
        }
        proc = self._run_cli(env_overrides=hostile_env)
        self.assertEqual(proc.returncode, 0, f"Hostile env vars caused crash: {proc.stderr}")
        self.assertNotIn("UnicodeEncodeError", proc.stderr)

    # -----------------------------------------------------------------------
    # Attack Vector 3: Markdown Archival Integrity & Structure Verification
    # -----------------------------------------------------------------------
    def test_stress_markdown_archival_both_formats(self):
        """Verify both ISO (YYYY-MM-DD.md) and legacy (daily_digest_YYYY_MM_DD.md) are generated and valid."""
        newsletters_dir = os.path.join(PROJECT_ROOT, "newsletters")
        now = datetime.now()
        iso_file = os.path.join(newsletters_dir, f"{now.strftime('%Y-%m-%d')}.md")
        legacy_file = os.path.join(newsletters_dir, f"daily_digest_{now.strftime('%Y_%m_%d')}.md")

        self.assertTrue(os.path.exists(iso_file), f"ISO format digest missing: {iso_file}")
        self.assertTrue(os.path.exists(legacy_file), f"Legacy format digest missing: {legacy_file}")

        with open(iso_file, "r", encoding="utf-8") as f:
            iso_content = f.read()

        with open(legacy_file, "r", encoding="utf-8") as f:
            legacy_content = f.read()

        self.assertEqual(iso_content, legacy_content, "ISO and legacy files must have identical content")
        self.assertGreater(len(iso_content), 500, "Digest file must not be suspiciously small")

    def test_stress_markdown_syntax_and_links(self):
        """Verify markdown headers, sections, links syntax, and absence of duplicate articles in digest."""
        proc = self._run_cli(env_overrides={"BUTTONDOWN_API_KEY": ""})
        self.assertEqual(proc.returncode, 0, f"CLI run failed: {proc.stderr}")
        now = datetime.now()
        iso_file = os.path.join(PROJECT_ROOT, "newsletters", f"{now.strftime('%Y-%m-%d')}.md")
        with open(iso_file, "r", encoding="utf-8") as f:
            content = f.read()

        # 1. Main Header
        self.assertIn("# 🌐 News Colossal — Daily Executive Digest", content)

        # 2. Date Subheader
        today_formatted = now.strftime("%B %d, %Y")
        self.assertIn(today_formatted, content)
        self.assertIn("*Top 5 Noise-Free Macro Intelligence Stories*", content)

        # 3. Check for 5 distinct numbered story headers
        story_titles = []
        for i in range(1, 6):
            header_prefix = f"### {i}. "
            self.assertIn(header_prefix, content, f"Story #{i} header missing")
            # Extract title
            start_pos = content.find(header_prefix) + len(header_prefix)
            end_pos = content.find("\n", start_pos)
            title = content[start_pos:end_pos].strip()
            self.assertTrue(len(title) > 0, f"Story #{i} title is empty")
            story_titles.append(title)

        # 4. Verify ZERO duplicate story titles in digest
        self.assertEqual(
            len(story_titles), len(set(story_titles)),
            f"Digest contains duplicate article titles: {story_titles}"
        )

        # 5. Check section headers
        self.assertEqual(content.count("**✦ What Happened:**"), 5, "Expected exactly 5 '✦ What Happened:' blocks")
        self.assertEqual(content.count("**✦ Why It Matters:**"), 5, "Expected exactly 5 '✦ Why It Matters:' blocks")
        self.assertEqual(content.count("**Publisher:**"), 5, "Expected exactly 5 'Publisher:' lines")

        # 6. Verify valid links
        import re
        links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
        self.assertGreater(len(links), 10, "Expected at least 10 markdown links")
        for text, url in links:
            self.assertTrue(url.startswith("http://") or url.startswith("https://") or url.startswith("#"),
                            f"Invalid link destination: {url} with text {text}")

    # -----------------------------------------------------------------------
    # Attack Vector 4: Data Boundary Corner Cases
    # -----------------------------------------------------------------------
    def test_stress_isolated_empty_articles_json(self):
        """Run generate_newsletter with an empty articles list."""
        from generate_daily_newsletter import generate_newsletter
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".json", delete=False) as tf:
            json.dump({"articles": []}, tf)
            tmp_path = tf.name

        try:
            res = generate_newsletter(send_email=False, news_file=tmp_path)
            self.assertEqual(res, "", "Empty articles list should return empty string gracefully")
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def test_stress_isolated_missing_json_file(self):
        """Run generate_newsletter with a non-existent file path."""
        from generate_daily_newsletter import generate_newsletter
        res = generate_newsletter(send_email=False, news_file="non_existent_file_9999.json")
        self.assertEqual(res, "", "Missing news file should return empty string gracefully")

    def test_stress_isolated_duplicates_filtering(self):
        """Verify that is_duplicate: True items are strictly excluded from newsletter."""
        from generate_daily_newsletter import generate_newsletter
        mock_articles = [
            {
                "id": "art-dup-1",
                "title": "Duplicate High Importance Story",
                "importance_score": 99.0,
                "is_duplicate": True,
                "source": "Wire A"
            },
            {
                "id": "art-real-1",
                "title": "Legitimate Story Number One",
                "importance_score": 10.0,
                "is_duplicate": False,
                "source": "Source 1"
            },
            {
                "id": "art-real-2",
                "title": "Legitimate Story Number Two",
                "importance_score": 9.0,
                "is_duplicate": False,
                "source": "Source 2"
            }
        ]

        with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".json", delete=False) as tf:
            json.dump({"articles": mock_articles}, tf)
            tmp_path = tf.name

        try:
            res = generate_newsletter(send_email=False, news_file=tmp_path)
            self.assertNotIn("Duplicate High Importance Story", res,
                             "is_duplicate: True item must NOT appear in generated newsletter!")
            self.assertIn("Legitimate Story Number One", res)
            self.assertIn("Legitimate Story Number Two", res)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def test_stress_isolated_hostile_unicode_in_articles(self):
        """Verify newsletter generation handles extreme unicode, emojis, and unescaped markdown in article fields."""
        from generate_daily_newsletter import generate_newsletter
        toxic_articles = [
            {
                "id": "tox-1",
                "title": "Emoji Party 🎉✨🚀 & Unicode Math ∑∫∂x and symbols ⚡✦",
                "importance_score": 8.5,
                "is_duplicate": False,
                "source": "Tokyo News / 東京新聞",
                "category": "Tech / テック",
                "region": "Asia-Pacific",
                "link": "https://example.com/art?q=1&lang=ja#anchor",
                "annotation": {
                    "what": "Special characters <script>alert(1)</script> and markdown **bold** [link](here).",
                    "why": "RTL text: \u200fهذا نص باللغة العربية للاختبار\u200e and quotes “smart” ‘single’."
                }
            }
        ]

        with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".json", delete=False) as tf:
            json.dump({"articles": toxic_articles}, tf)
            tmp_path = tf.name

        try:
            res = generate_newsletter(send_email=False, news_file=tmp_path)
            self.assertIn("Emoji Party 🎉✨🚀", res)
            self.assertIn("東京新聞", res)
            self.assertIn("هذا نص باللغة العربية للاختبار", res)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def test_stress_stdout_without_reconfigure_attribute(self):
        """Verify generate_daily_newsletter.py does not crash if stdout lacks reconfigure attribute."""
        snippet = """
import sys
# Create dummy object without reconfigure
class DummyStream:
    def write(self, s): pass
    def flush(self): pass

old_stdout = sys.stdout
sys.stdout = DummyStream()
try:
    import generate_daily_newsletter
    print("IMPORT_OK")
finally:
    sys.stdout = old_stdout
"""
        proc = subprocess.run(
            [sys.executable, "-c", snippet],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True
        )
        self.assertEqual(proc.returncode, 0, f"Module failed when stdout lacks reconfigure: {proc.stderr}")


if __name__ == "__main__":
    unittest.main()
