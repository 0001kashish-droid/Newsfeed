#!/usr/bin/env python3
"""
Milestone 3 Empirical Stress Testing Suite.
Empirically tests source diversity balancing, story clustering, and text formatting logic.
"""

import math
import os
import sys
import unittest
from collections import Counter

# Set up paths
_TEST_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_TEST_DIR)
_SCRIPTS_DIR = os.path.join(_PROJECT_ROOT, "scripts")

if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)

from fetch_news import (
    balance_source_diversity,
    cluster_stories,
    format_clean_description,
    BRAND_FAMILIES,
    SOURCES
)


class TestBalanceSourceDiversityStress(unittest.TestCase):
    """
    Stress tests for balance_source_diversity:
    - Feeds of size 3, 5, 10, 50, 100, 300 with heavily skewed brand distributions.
    - Verify brand_count <= max(1, floor(0.18 * total)) without dropping all articles.
    """

    def setUp(self):
        self.bbc_sources = [
            ("BBC News", "Global"),
            ("BBC Asia", "Asia-Pacific"),
            ("BBC Europe", "Europe"),
            ("BBC Middle East", "Middle East"),
            ("BBC US", "North America"),
            ("BBC Business", "Global"),
        ]
        self.other_sources = [
            ("The Guardian", "Global"),
            ("Reuters", "Global"),
            ("France 24", "Europe"),
            ("New York Times", "North America"),
            ("SCMP", "Asia-Pacific"),
            ("Hindustan Times", "India"),
        ]

    def _generate_skewed_feed(self, total_size, bbc_ratio=0.9):
        """Generates a synthetic feed with skewed brand distribution."""
        n_bbc = max(1, int(round(total_size * bbc_ratio)))
        if n_bbc >= total_size and total_size > 1:
            n_bbc = total_size - 1
        n_other = total_size - n_bbc

        articles = []
        # Distribute BBC across sources and regions to test global brand capping
        for i in range(n_bbc):
            src, reg = self.bbc_sources[i % len(self.bbc_sources)]
            articles.append({
                "id": f"art-bbc-{i}",
                "title": f"BBC Major Headline Event {i}",
                "source": src,
                "region": f"{reg}-{i // len(self.bbc_sources)}",  # allow multiple per region
                "category": "World",
                "pubDate": "2026-10-07T00:00:00Z"
            })

        for i in range(n_other):
            src, reg = self.other_sources[i % len(self.other_sources)]
            articles.append({
                "id": f"art-other-{i}",
                "title": f"Non-BBC Perspective Headline Event {i}",
                "source": src,
                "region": f"{reg}-{i // len(self.other_sources)}",
                "category": "World",
                "pubDate": "2026-10-07T00:00:00Z"
            })

        return articles

    def test_skewed_feed_size_3(self):
        feed = self._generate_skewed_feed(3, bbc_ratio=0.9)
        result = balance_source_diversity(feed)
        self.assertGreater(len(result), 0, "Feed should not drop all articles")
        total = len(result)
        b_counts = Counter(BRAND_FAMILIES.get(a["source"], a["source"]) for a in result)
        for brand, count in b_counts.items():
            allowed = max(1, math.floor(0.18 * total))
            self.assertLessEqual(
                count, allowed,
                f"Brand {brand} count ({count}) exceeds allowed ({allowed}) in feed of {total}"
            )

    def test_skewed_feed_size_5(self):
        feed = self._generate_skewed_feed(5, bbc_ratio=0.9)
        result = balance_source_diversity(feed)
        self.assertGreater(len(result), 0, "Feed should not drop all articles")
        total = len(result)
        b_counts = Counter(BRAND_FAMILIES.get(a["source"], a["source"]) for a in result)
        for brand, count in b_counts.items():
            allowed = max(1, math.floor(0.18 * total))
            self.assertLessEqual(
                count, allowed,
                f"Brand {brand} count ({count}) exceeds allowed ({allowed}) in feed of {total}"
            )

    def test_skewed_feed_size_10(self):
        feed = self._generate_skewed_feed(10, bbc_ratio=0.9)
        result = balance_source_diversity(feed)
        self.assertGreater(len(result), 0, "Feed should not drop all articles")
        total = len(result)
        b_counts = Counter(BRAND_FAMILIES.get(a["source"], a["source"]) for a in result)
        for brand, count in b_counts.items():
            allowed = max(1, math.floor(0.18 * total))
            self.assertLessEqual(
                count, allowed,
                f"Brand {brand} count ({count}) exceeds allowed ({allowed}) in feed of {total}"
            )

    def test_skewed_feed_size_50(self):
        feed = self._generate_skewed_feed(50, bbc_ratio=0.9)
        result = balance_source_diversity(feed)
        self.assertGreater(len(result), 0, "Feed should not drop all articles")
        total = len(result)
        b_counts = Counter(BRAND_FAMILIES.get(a["source"], a["source"]) for a in result)
        for brand, count in b_counts.items():
            allowed = max(1, math.floor(0.18 * total))
            self.assertLessEqual(
                count, allowed,
                f"Brand {brand} count ({count}) exceeds allowed ({allowed}) in feed of {total}"
            )

    def test_skewed_feed_size_100(self):
        feed = self._generate_skewed_feed(100, bbc_ratio=0.9)
        result = balance_source_diversity(feed)
        self.assertGreater(len(result), 0, "Feed should not drop all articles")
        total = len(result)
        b_counts = Counter(BRAND_FAMILIES.get(a["source"], a["source"]) for a in result)
        for brand, count in b_counts.items():
            allowed = max(1, math.floor(0.18 * total))
            self.assertLessEqual(
                count, allowed,
                f"Brand {brand} count ({count}) exceeds allowed ({allowed}) in feed of {total}"
            )

    def test_skewed_feed_size_300(self):
        feed = self._generate_skewed_feed(300, bbc_ratio=0.9)
        result = balance_source_diversity(feed)
        self.assertGreater(len(result), 0, "Feed should not drop all articles")
        total = len(result)
        b_counts = Counter(BRAND_FAMILIES.get(a["source"], a["source"]) for a in result)
        for brand, count in b_counts.items():
            allowed = max(1, math.floor(0.18 * total))
            self.assertLessEqual(
                count, allowed,
                f"Brand {brand} count ({count}) exceeds allowed ({allowed}) in feed of {total}"
            )

    def test_single_brand_feed(self):
        """Pure single-brand feed (100% BBC) must cap according to allowed limit."""
        feed = [
            {
                "id": f"art-bbc-{i}",
                "title": f"BBC Major Headline Event {i}",
                "source": self.bbc_sources[i % len(self.bbc_sources)][0],
                "region": f"region-{i}",
                "category": "World",
                "pubDate": "2026-10-07T00:00:00Z"
            }
            for i in range(50)
        ]
        result = balance_source_diversity(feed)
        self.assertGreater(len(result), 0)
        b_counts = Counter(BRAND_FAMILIES.get(a["source"], a["source"]) for a in result)
        self.assertEqual(len(b_counts), 1)
        # With only 1 brand, count is 1 (allowed cap drops to max(1, ...))
        self.assertEqual(b_counts["BBC"], 1)


    def test_mixed_skewed_brands(self):
        """Feed with multiple skewed brands: 60% BBC, 30% Guardian, 10% Reuters."""
        articles = []
        for i in range(60):
            src, reg = self.bbc_sources[i % len(self.bbc_sources)]
            articles.append({"id": f"b-{i}", "title": f"B {i}", "source": src, "region": f"r-b-{i}", "category": "World"})
        for i in range(30):
            articles.append({"id": f"g-{i}", "title": f"G {i}", "source": "The Guardian", "region": f"r-g-{i}", "category": "World"})
        for i in range(10):
            articles.append({"id": f"r-{i}", "title": f"R {i}", "source": "Reuters", "region": f"r-r-{i}", "category": "World"})

        result = balance_source_diversity(articles)
        total = len(result)
        b_counts = Counter(BRAND_FAMILIES.get(a["source"], a["source"]) for a in result)
        for brand, count in b_counts.items():
            allowed = max(1, math.floor(0.18 * total))
            self.assertLessEqual(count, allowed, f"Brand {brand} count ({count}) exceeds allowed ({allowed})")

    def test_empty_feed_handling(self):
        result = balance_source_diversity([])
        self.assertEqual(result, [])


class TestClusterStoriesStress(unittest.TestCase):
    """
    Stress tests for cluster_stories:
    - Pairs from same brand family (BBC News + BBC Europe)
    - Pairs from same publisher
    - Pairs from distinct publishers / distinct brand families across regions
    """

    def test_same_brand_family_rejected(self):
        """Articles sharing brand family (BBC News + BBC Europe) must NOT form a pairedStory."""
        articles = [
            {
                "id": "bbc-1",
                "title": "Global Climate Summit Reaches Historic Treaty Agreement",
                "source": "BBC News",
                "region": "Global",
                "category": "World",
                "pubDate": "2026-10-07T10:00:00Z"
            },
            {
                "id": "bbc-2",
                "title": "Global Climate Summit Reaches Historic Treaty Agreement In Europe",
                "source": "BBC Europe",
                "region": "Europe",
                "category": "World",
                "pubDate": "2026-10-07T10:15:00Z"
            }
        ]
        cluster_stories(articles)
        self.assertFalse(articles[0].get("pairedStory", False), "Same brand family must NOT have pairedStory=True")
        self.assertFalse(articles[1].get("pairedStory", False), "Same brand family must NOT have pairedStory=True")
        self.assertEqual(articles[0].get("perspectives", []), [])
        self.assertEqual(articles[1].get("perspectives", []), [])

    def test_same_publisher_rejected(self):
        """Articles from identical publisher must NOT form a pairedStory."""
        articles = [
            {
                "id": "rtr-1",
                "title": "Oil Prices Surge Following Crucial OPEC Production Cuts",
                "source": "Reuters",
                "region": "Global",
                "category": "World",
                "pubDate": "2026-10-07T08:00:00Z"
            },
            {
                "id": "rtr-2",
                "title": "Oil Prices Surge After Unexpected OPEC Production Cuts",
                "source": "Reuters",
                "region": "Middle East",
                "category": "World",
                "pubDate": "2026-10-07T08:30:00Z"
            }
        ]
        cluster_stories(articles)
        self.assertFalse(articles[0].get("pairedStory", False), "Identical publisher must NOT have pairedStory=True")
        self.assertFalse(articles[1].get("pairedStory", False), "Identical publisher must NOT have pairedStory=True")

    def test_distinct_publishers_accepted(self):
        """Articles from distinct publishers, brands, and regions MUST form a pairedStory."""
        articles = [
            {
                "id": "art-1",
                "title": "Major Breakthrough In Renewable Fusion Reactor Testing",
                "source": "BBC News",
                "region": "Global",
                "category": "World",
                "pubDate": "2026-10-07T06:00:00Z"
            },
            {
                "id": "art-2",
                "title": "Major Breakthrough In Renewable Fusion Reactor Facility",
                "source": "France 24",
                "region": "Europe",
                "category": "World",
                "pubDate": "2026-10-07T06:30:00Z"
            }
        ]
        cluster_stories(articles)
        self.assertTrue(articles[0].get("pairedStory", False), "Distinct publishers should form pairedStory")
        self.assertTrue(articles[1].get("pairedStory", False), "Distinct publishers should form pairedStory")
        perspectives = articles[0].get("perspectives", [])
        self.assertEqual(len(perspectives), 2)
        distinct_sources = set(p["source"] for p in perspectives)
        distinct_brands = set(BRAND_FAMILIES.get(p["source"], p["source"]) for p in perspectives)
        distinct_regions = set(p["region"] for p in perspectives)
        self.assertGreaterEqual(len(distinct_sources), 2)
        self.assertGreaterEqual(len(distinct_brands), 2)
        self.assertGreaterEqual(len(distinct_regions), 2)

    def test_three_way_cluster_with_brand_overlap(self):
        """A cluster with BBC News, BBC Europe, and France 24 must only include 1 BBC in perspectives."""
        articles = [
            {
                "id": "art-1",
                "title": "Global Cyber Security Coalition Targets Ransomware Gangs",
                "source": "BBC News",
                "region": "Global",
                "category": "World",
                "pubDate": "2026-10-07T05:00:00Z"
            },
            {
                "id": "art-2",
                "title": "Global Cyber Security Coalition Targets International Ransomware Gangs",
                "source": "BBC Europe",
                "region": "Europe",
                "category": "World",
                "pubDate": "2026-10-07T05:10:00Z"
            },
            {
                "id": "art-3",
                "title": "Global Cyber Security Coalition Targets Ransomware Syndicates Across Continents",
                "source": "France 24",
                "region": "Europe",
                "category": "World",
                "pubDate": "2026-10-07T05:20:00Z"
            }
        ]
        cluster_stories(articles)
        # Should be cross-regional because BBC News (Global) and France 24 (Europe) differ in region and brand
        self.assertTrue(articles[0].get("pairedStory", False))
        perspectives = articles[0].get("perspectives", [])
        brands = [BRAND_FAMILIES.get(p["source"], p["source"]) for p in perspectives]
        self.assertEqual(len(brands), len(set(brands)), "No duplicate brand family in perspectives")
        self.assertEqual(set(brands), {"BBC", "France 24"})

    def test_different_categories_do_not_cluster(self):
        """Articles in different categories must not cluster even with identical titles."""
        articles = [
            {
                "id": "art-w",
                "title": "Autonomous Drone Fleet Completes Autonomous Delivery Mission",
                "source": "Reuters",
                "region": "Global",
                "category": "World",
                "pubDate": "2026-10-07T04:00:00Z"
            },
            {
                "id": "art-t",
                "title": "Autonomous Drone Fleet Completes Autonomous Delivery Mission",
                "source": "Ars Technica",
                "region": "North America",
                "category": "Tech",
                "pubDate": "2026-10-07T04:10:00Z"
            }
        ]
        cluster_stories(articles)
        self.assertFalse(articles[0].get("pairedStory", False))
        self.assertFalse(articles[1].get("pairedStory", False))


class TestFormatCleanDescriptionStress(unittest.TestCase):
    """
    Stress tests for format_clean_description with boundary cases:
    - Descriptions ending in '...'
    - Descriptions ending in '…'
    - Trailing whitespace
    - Single long words
    - Cut off mid-word
    - Abbreviations like 'U.S.' or 'A.I.'
    - Verify 0 trailing ellipses and clean period termination.
    """

    def test_trailing_ascii_ellipsis(self):
        raw = "The delegates reached a tentative agreement on maritime shipping tariffs..."
        res = format_clean_description(raw)
        self.assertFalse(res.endswith("..."), "Must not end in trailing ASCII ellipsis")
        self.assertTrue(res.endswith("."), "Must end cleanly with a period")
        self.assertNotIn("..", res)

    def test_trailing_unicode_ellipsis(self):
        raw = "Scientists have completed the genome mapping for the deep sea specimen…"
        res = format_clean_description(raw)
        self.assertFalse(res.endswith("…"), "Must not end in trailing unicode ellipsis")
        self.assertTrue(res.endswith("."), "Must end cleanly with a period")
        self.assertNotIn("…", res)

    def test_trailing_whitespace_and_tabs(self):
        raw = "Financial regulators issued an updated advisory regarding stablecoin liquidity.   \t  \n"
        res = format_clean_description(raw)
        self.assertFalse(res.endswith(" "), "Must not have trailing spaces")
        self.assertTrue(res.endswith("."), "Must end cleanly with a period")

    def test_single_long_word(self):
        raw = "Pneumonoultramicroscopicsilicovolcanoconiosis" * 8  # 360 chars
        res = format_clean_description(raw, max_len=260)
        self.assertFalse(res.endswith("..."), "Must not end with ellipsis")
        self.assertFalse(res.endswith("…"), "Must not end with unicode ellipsis")
        self.assertTrue(res.endswith("."), "Must end cleanly with a period")
        self.assertLessEqual(len(res), 265)

    def test_cut_off_mid_word(self):
        sentence = ("The central bank announced that interest rates would remain unchanged for the remainder of the "
                    "fiscal calendar year amidst growing uncertainty surrounding international consumer spending and "
                    "fluctuating trade dynamics throughout modern global economic centers and financial jurisdictions.")
        res = format_clean_description(sentence, max_len=260)
        self.assertFalse(res.endswith("..."), "Must not end with ellipsis")
        self.assertFalse(res.endswith("…"), "Must not end with unicode ellipsis")
        self.assertTrue(res.endswith("."), "Must end cleanly with a period")
        self.assertTrue(res[:-1].isalnum() or res[-2].isalnum())

    def test_abbreviation_us_at_end(self):
        raw = "The trade representative formally returned to the U.S."
        res = format_clean_description(raw)
        self.assertFalse(res.endswith("..."))
        self.assertTrue(res.endswith("."), "Must end with period")
        self.assertTrue(res.endswith("U.S."), f"Should preserve abbreviation U.S., got '{res}'")

    def test_abbreviation_ai_at_end(self):
        raw = "New ethical standards were proposed for applied A.I."
        res = format_clean_description(raw)
        self.assertFalse(res.endswith("..."))
        self.assertTrue(res.endswith("."), "Must end with period")
        self.assertTrue(res.endswith("A.I."), f"Should preserve abbreviation A.I., got '{res}'")

    def test_abbreviation_with_ellipsis_stripped(self):
        raw = "The tech delegation concluded discussions across the U.S...."
        res = format_clean_description(raw)
        self.assertFalse(res.endswith("..."))
        self.assertFalse(res.endswith("…"))
        self.assertTrue(res.endswith("."), "Must end with period")

    def test_html_encoded_entities_and_tags(self):
        raw = "<p>Global trade volume grew by <b>3.5%</b> in Q3 &amp; exceeded projections...</p>"
        res = format_clean_description(raw)
        self.assertNotIn("<p>", res)
        self.assertNotIn("<b>", res)
        self.assertNotIn("&amp;", res)
        self.assertIn("&", res)
        self.assertFalse(res.endswith("..."))
        self.assertTrue(res.endswith("."))

    def test_multiple_dots_and_mixed_ellipses(self):
        raw = "A massive earthquake struck off the coastline causing widespread alerts..... … . "
        res = format_clean_description(raw)
        self.assertFalse(res.endswith("..."))
        self.assertFalse(res.endswith("…"))
        self.assertTrue(res.endswith("."))
        self.assertNotIn("..", res)

    def test_question_and_exclamation_marks(self):
        raw_q = "Will the upcoming space mission discover subsurface oceans?"
        res_q = format_clean_description(raw_q)
        self.assertTrue(res_q.endswith("."))

        raw_e = "The historic championship ended in a thrilling last-second victory!"
        res_e = format_clean_description(raw_e)
        self.assertTrue(res_e.endswith("."))

    def test_empty_and_whitespace_input(self):
        self.assertEqual(format_clean_description(""), "")
        self.assertEqual(format_clean_description("   \n\t  "), "")
        self.assertEqual(format_clean_description("..."), "")
        self.assertEqual(format_clean_description("……"), "")


if __name__ == "__main__":
    unittest.main()

