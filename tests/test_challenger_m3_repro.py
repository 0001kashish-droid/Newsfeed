#!/usr/bin/env python3
"""
Empirical Bug Reproduction Harness for Milestone 3
Author: challenger_m3_1 (Empirical Challenger)

Reproduction script proving two critical bugs:
Bug 1: Memory crash on None title or None keywords in match_article_to_arc.
Bug 2: False-positive deduplication in intake.py when generic action/domain tokens match.
"""

import os
import sys
import unittest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR = os.path.join(PROJECT_ROOT, 'scripts')

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

from intelligence.memory import match_article_to_arc
from intelligence.intake import run_intake, enhanced_dedup, get_all_entities_set


class TestMilestone3EmpiricalBugs(unittest.TestCase):
    """
    Empirically reproduces and documents Milestone 3 bugs.
    """

    def test_reproduce_bug1_memory_crash_on_none_title(self):
        """
        Bug 1: AttributeError: 'NoneType' object has no attribute 'split'
        Location: scripts/intelligence/memory.py line 113.
        When an incoming article dictionary has {'title': None}, article.get('title', '')
        returns None instead of an empty string, causing .split() to fail.
        """
        article = {'title': None, 'category': 'General', 'entities': {}}
        arc = {'arc_id': 'arc-1', 'keywords': ['news'], 'entities': ['world']}

        with self.assertRaises(AttributeError) as ctx:
            match_article_to_arc(article, [arc])
        self.assertIn("'NoneType' object has no attribute 'split'", str(ctx.exception))
        print("\n[CONFIRMED BUG 1A] match_article_to_arc crashed on article['title']=None with AttributeError.")

    def test_reproduce_bug1_memory_crash_on_none_keywords(self):
        """
        Bug 1 (variant B): TypeError: 'NoneType' object is not iterable
        Location: scripts/intelligence/memory.py line 123.
        When arc has {'keywords': None}, arc.get('keywords', []) returns None,
        causing `k.lower() for k in None` to raise TypeError.
        """
        article = {'title': 'Valid Article Title', 'category': 'General', 'entities': {}}
        arc = {'arc_id': 'arc-1', 'keywords': None, 'entities': ['world']}

        with self.assertRaises(TypeError) as ctx:
            match_article_to_arc(article, [arc])
        self.assertIn("NoneType", str(ctx.exception))
        print("[CONFIRMED BUG 1B] match_article_to_arc crashed on arc['keywords']=None with TypeError.")

    def test_reproduce_bug2_false_positive_deduplication(self):
        """
        Bug 2: False-positive deduplication in enhanced_dedup / run_intake.
        Location: scripts/intelligence/intake.py lines 165-185, 219.
        Two completely unrelated stories:
        Story A: 'Breakthrough in Solid-State Battery Density Achieved'
        Story B: 'Quantum Computing Cluster Simulates Complex Molecular Folding'
        Both are in category 'Tech'.
        Neither has named entities (no country, company, leader, or org).
        Both have action keyword 'technology' detected.
        get_all_entities_set returns {'technology'} for both.
        entity_overlap_ratio is 1.0 (>= 0.8).
        Result: Story B is falsely marked as a duplicate of Story A and suppressed!
        """
        story_a = {
            'id': 'tech-battery',
            'title': 'Breakthrough in Solid-State Battery Density Achieved',
            'description': 'Researchers report energy density gains in solid electrolyte materials.',
            'category': 'Tech'
        }
        story_b = {
            'id': 'tech-quantum',
            'title': 'Quantum Computing Cluster Simulates Complex Molecular Folding',
            'description': 'Chemists use quantum algorithms to simulate protein conformations.',
            'category': 'Tech'
        }

        final_articles, stats = run_intake([story_a, story_b])
        # Two completely unrelated articles were supplied
        # If bug exists, duplicates_suppressed is 1 and only 1 article is returned
        print(f"[BUG 2 OBSERVATION] Input: 2 completely distinct tech articles. "
              f"Output count: {len(final_articles)}, Duplicates suppressed: {stats['duplicates_suppressed']}")
        
        # Verify that the bug indeed suppresses one of them
        self.assertEqual(stats['duplicates_suppressed'], 1, "Bug confirmed: False positive duplicate detected.")
        self.assertEqual(len(final_articles), 1, "Bug confirmed: Distinct tech story dropped.")


if __name__ == '__main__':
    unittest.main()
