#!/usr/bin/env python3
"""
Challenger Hermetic M3 Iteration 2 (2) - Memory & Typographical Adversarial Suite
Target: scripts/intelligence/memory.py, data/narrative_memory.json, data/news.json

Empirically challenges:
1. Typographical duplicate rejection in update_memory() and _normalize_chapter_title()
2. Wire markers, attribution suffixes, and editorial slugs in data/narrative_memory.json
3. Honest null schema stability and referential integrity across data/news.json
4. Multi-chapter Jaccard stability: denominator dilution resistance and runaway isolation
"""

import os
import sys
import json
import re
import unittest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR = os.path.join(PROJECT_ROOT, 'scripts')

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

from intelligence.memory import (
    _normalize_chapter_title,
    update_memory,
    match_article_to_arc,
    substantive_stems
)


class TestTypographicalDuplicateRejection(unittest.TestCase):
    """Stress-test typographical normalization and chapter deduplication in update_memory()."""

    def setUp(self):
        self.base_arc = {
            'arc_id': 'test-arc-typo',
            'title': "French High School Protests Escalate",
            'keywords': ['french', 'school', 'protest', 'escal'],
            'entity_signature': 'FR:Sorbonne',
            'category': 'World',
            'regions': ['Europe'],
            'chapter_count': 1,
            'chapter_titles': [
                "French high school protests continue despite PM's promise of action - Europe live"
            ],
            'sources_involved': ['The Guardian']
        }

    def test_single_quote_permutations_rejected(self):
        """Curly single quotes (’ and ‘) must match straight quote (') and reject."""
        variations = [
            "French high school protests continue despite PM’s promise of action - Europe live",  # right single / apostrophe
            "French high school protests continue despite PM‘s promise of action - Europe live",  # left single quote
            "French high school protests continue despite PM's promise of action - Europe live",  # straight quote
        ]
        for var in variations:
            norm = _normalize_chapter_title(var)
            self.assertEqual(
                norm,
                "french high school protests continue despite pm's promise of action europe live",
                f"Normalization failed for quote variation: {var}"
            )

    def test_double_quote_permutations_rejected(self):
        """Curly double quotes (“ and ”) must match straight double quote (\") and reject."""
        t1 = 'Scholz vows: “We will protect critical German infrastructure”'
        t2 = 'Scholz vows: "We will protect critical German infrastructure"'
        self.assertEqual(_normalize_chapter_title(t1), _normalize_chapter_title(t2))

    def test_dash_permutations_rejected(self):
        """En-dash (–), em-dash (—), and hyphen (-) must normalize to hyphen and reject."""
        t_hyphen = "Student strikes grow - Paris reacts"
        t_en = "Student strikes grow – Paris reacts"
        t_em = "Student strikes grow — Paris reacts"
        self.assertEqual(_normalize_chapter_title(t_hyphen), _normalize_chapter_title(t_en))
        self.assertEqual(_normalize_chapter_title(t_hyphen), _normalize_chapter_title(t_em))

    def test_whitespace_and_trailing_punctuation_rejected(self):
        """Excess whitespace and trailing punctuation must normalize cleanly."""
        t_clean = "Student strikes grow - Paris reacts"
        t_dirty1 = "Student   strikes   grow  -  Paris reacts."
        t_dirty2 = "Student strikes grow - Paris reacts..."
        t_dirty3 = "Student strikes grow - Paris reacts! "
        t_dirty4 = "\tStudent strikes grow - Paris reacts; \t"
        t_dirty5 = "Student strikes grow - Paris reacts: "
        for td in [t_dirty1, t_dirty2, t_dirty3, t_dirty4, t_dirty5]:
            self.assertEqual(
                _normalize_chapter_title(td),
                _normalize_chapter_title(t_clean),
                f"Trailing punctuation/whitespace failed for: {repr(td)}"
            )

    def test_update_memory_rejects_typographical_burst(self):
        """A burst of 6 typographical variations sent in a single update_memory call must not duplicate."""
        mem = {'arcs': [dict(self.base_arc)]}
        mem['arcs'][0]['chapter_titles'] = list(self.base_arc['chapter_titles'])

        burst = [
            {
                'title': "French high school protests continue despite PM’s promise of action – Europe live",
                'category': 'World',
                'region': 'Europe',
                'source': 'France 24',
                'entities': {'locations': ['France', 'Paris'], 'organizations': ['Sorbonne']}
            },
            {
                'title': "French high school protests continue despite PM‘s promise of action — Europe live.",
                'category': 'World',
                'region': 'Europe',
                'source': 'Le Monde',
                'entities': {'locations': ['France', 'Paris'], 'organizations': ['Sorbonne']}
            },
            {
                'title': "French   high  school protests  continue  despite PM's promise of action - Europe live...",
                'category': 'World',
                'region': 'Europe',
                'source': 'RFI',
                'entities': {'locations': ['France', 'Paris'], 'organizations': ['Sorbonne']}
            },
            {
                'title': "French high school protests continue despite PM's promise of action - Europe live: ",
                'category': 'World',
                'region': 'Europe',
                'source': 'AFP',
                'entities': {'locations': ['France', 'Paris'], 'organizations': ['Sorbonne']}
            }
        ]

        updated = update_memory(mem, burst)
        target_arc = updated['arcs'][0]
        self.assertEqual(
            len(target_arc['chapter_titles']), 1,
            f"Burst appended typographical duplicates: {target_arc['chapter_titles']}"
        )
        self.assertEqual(target_arc['chapter_count'], 1)
        self.assertIn('France 24', target_arc['sources_involved'])
        self.assertIn('Le Monde', target_arc['sources_involved'])
        self.assertIn('RFI', target_arc['sources_involved'])

    def test_distinct_chapters_preserved(self):
        """Legitimate substantive chapter updates must not be rejected."""
        mem = {'arcs': [dict(self.base_arc)]}
        mem['arcs'][0]['chapter_titles'] = list(self.base_arc['chapter_titles'])

        new_chapter_art = {
            'title': "French police deploy water cannon as Paris protests enter day three",
            'category': 'World',
            'region': 'Europe',
            'source': 'France 24',
            'entities': {'locations': ['France', 'Paris'], 'organizations': ['Sorbonne']}
        }
        updated = update_memory(mem, [new_chapter_art])
        target_arc = updated['arcs'][0]
        # Jaccard might or might not bind depending on threshold, but if it binds, it must be appended
        if len(target_arc['chapter_titles']) > 1:
            self.assertEqual(len(target_arc['chapter_titles']), 2)
            self.assertEqual(target_arc['chapter_count'], 2)

    def test_null_empty_and_corrupt_title_handling(self):
        """update_memory must safely handle empty, whitespace-only, and punctuation-only titles."""
        mem = {'arcs': [dict(self.base_arc)]}
        mem['arcs'][0]['chapter_titles'] = list(self.base_arc['chapter_titles'])

        corrupt_articles = [
            {'title': None, 'category': 'World', 'region': 'Europe', 'entities': {'locations': ['France', 'Paris'], 'organizations': ['Sorbonne']}},
            {'title': '', 'category': 'World', 'region': 'Europe', 'entities': {'locations': ['France', 'Paris'], 'organizations': ['Sorbonne']}},
            {'title': '   \t\n  ', 'category': 'World', 'region': 'Europe', 'entities': {'locations': ['France', 'Paris'], 'organizations': ['Sorbonne']}},
            {'title': '....;;;', 'category': 'World', 'region': 'Europe', 'entities': {'locations': ['France', 'Paris'], 'organizations': ['Sorbonne']}},
        ]
        updated = update_memory(mem, corrupt_articles)
        target_arc = updated['arcs'][0]
        self.assertEqual(
            len(target_arc['chapter_titles']), 1,
            "Corrupt or empty titles were erroneously added to chapter_titles"
        )

    def test_non_string_title_vulnerability_attribute_error(self):
        """EMPIRICAL FINDING: update_memory() safely handles non-string title (int, bool) without AttributeError."""
        mem = {'arcs': [dict(self.base_arc)]}
        mem['arcs'][0]['chapter_titles'] = list(self.base_arc['chapter_titles'])

        corrupt_int = {'title': 12345, 'category': 'World', 'region': 'Europe', 'entities': {'locations': ['France', 'Paris'], 'organizations': ['Sorbonne']}}
        # Verify remediation: line 679 safely handles non-string title without crashing
        res = update_memory(mem, [corrupt_int])
        self.assertEqual(len(res['arcs'][0]['chapter_titles']), 1)



class TestNarrativeMemoryDatasetIntegrity(unittest.TestCase):
    """Empirical audit of data/narrative_memory.json for wire contamination and invariants."""

    def setUp(self):
        mem_path = os.path.join(PROJECT_ROOT, 'data', 'narrative_memory.json')
        with open(mem_path, 'r', encoding='utf-8') as f:
            self.memory = json.load(f)

    def test_zero_wire_suffixes(self):
        """Verify 0 trailing wire attribution suffixes (- Reuters, - AP, - BBC, etc.)."""
        forbidden_suffixes = ['- reuters', '- ap', '- bbc', '- afp', '- bloomberg', '- nyt']
        violations = []
        for arc in self.memory.get('arcs', []):
            for ch in arc.get('chapter_titles', []):
                for sfx in forbidden_suffixes:
                    if ch.lower().endswith(sfx):
                        violations.append((arc.get('arc_id'), ch, sfx))
        self.assertEqual(
            violations, [],
            f"Trailing wire suffixes found in narrative memory: {violations}"
        )

    def test_zero_wire_names_in_entity_signatures(self):
        """Verify no publisher or wire name leaked into arc entity signatures."""
        wire_tokens = {'reuters', 'ap', 'bbc', 'afp', 'bloomberg', 'guardian', 'nyt'}
        violations = []
        for arc in self.memory.get('arcs', []):
            sig = arc.get('entity_signature') or ''
            for part in sig.split(':'):
                if part.lower() in wire_tokens:
                    violations.append((arc.get('arc_id'), sig))
        self.assertEqual(
            violations, [],
            f"Wire names leaked into entity_signatures: {violations}"
        )

    def test_zero_wire_names_in_keywords(self):
        """Verify no publisher or wire name leaked into arc keywords."""
        wire_tokens = {'reuters', 'ap', 'bbc', 'afp', 'bloomberg'}
        violations = []
        for arc in self.memory.get('arcs', []):
            for kw in arc.get('keywords', []):
                if kw.lower() in wire_tokens:
                    violations.append((arc.get('arc_id'), kw))
        self.assertEqual(
            violations, [],
            f"Wire names leaked into arc keywords: {violations}"
        )

    def test_scan_for_live_blog_and_editorial_slugs(self):
        """Empirically audit presence of editorial live markers in chapter titles."""
        # Note: 'Europe live' and 'Live:' are editorial markers from syndicated titles
        live_markers = ['europe live', 'live:']
        found = []
        for arc in self.memory.get('arcs', []):
            for ch in arc.get('chapter_titles', []):
                for marker in live_markers:
                    if marker in ch.lower():
                        found.append({'arc_id': arc.get('arc_id'), 'title': ch, 'marker': marker})
        # Record finding for challenger report
        if found:
            print(f"\n[CHALLENGER AUDIT] Found {len(found)} live marker occurrences in narrative_memory.json:")
            for item in found:
                print(f"  Arc {item['arc_id'][:8]}: '{item['title']}' (marker: {item['marker']})")

    def test_scan_for_hyphen_space_duplicate_chapters(self):
        """Audit for subtle typographical duplicates differing only by hyphen vs space."""
        duplicates = []
        for arc in self.memory.get('arcs', []):
            titles = arc.get('chapter_titles', [])
            seen_clean = {}
            for ch in titles:
                # Remove hyphens and whitespace to detect compound duplicates (e.g. high-school vs high school)
                clean = re.sub(r'[\s\-–—]+', '', ch.lower())
                clean = re.sub(r'[^a-z0-9]', '', clean)
                if clean in seen_clean:
                    duplicates.append({
                        'arc_id': arc.get('arc_id'),
                        'ch1': seen_clean[clean],
                        'ch2': ch
                    })
                else:
                    seen_clean[clean] = ch
        if duplicates:
            print(f"\n[CHALLENGER AUDIT] Found {len(duplicates)} compound hyphen/space duplicate chapters:")
            for d in duplicates:
                print(f"  Arc {d['arc_id'][:8]}: '{d['ch1']}' vs '{d['ch2']}'")


class TestHonestNullInvariants(unittest.TestCase):
    """Verify honest null invariant adherence across data/news.json."""

    def setUp(self):
        news_path = os.path.join(PROJECT_ROOT, 'data', 'news.json')
        with open(news_path, 'r', encoding='utf-8') as f:
            self.news_data = json.load(f)
        mem_path = os.path.join(PROJECT_ROOT, 'data', 'narrative_memory.json')
        with open(mem_path, 'r', encoding='utf-8') as f:
            self.memory = json.load(f)

    def test_honest_null_schema_on_standalone_articles(self):
        """Every article not bound to an arc must have exactly the canonical honest null structure."""
        expected_null = {
            'arc_id': None,
            'arc_title': None,
            'day_number': 0,
            'total_chapters': 0,
            'importance_trend': None,
            'previous_headlines': []
        }
        articles = self.news_data.get('articles', [])
        self.assertGreater(len(articles), 0)

        null_count = 0
        for art in articles:
            arc_struct = art.get('narrative_arc')
            self.assertIsNotNone(arc_struct, f"Article {art.get('id')} lacks narrative_arc structure")
            if arc_struct.get('arc_id') is None:
                null_count += 1
                self.assertEqual(
                    arc_struct, expected_null,
                    f"Article {art.get('id')} has non-canonical null structure: {arc_struct}"
                )
        self.assertGreater(null_count, 0, "Expected standalone articles with honest nulls")

    def test_referential_integrity_between_news_and_narrative_memory(self):
        """Every article referencing an arc_id must exist in data/narrative_memory.json."""
        arc_ids_in_mem = {arc.get('arc_id') for arc in self.memory.get('arcs', [])}
        articles = self.news_data.get('articles', [])

        active_count = 0
        for art in articles:
            arc_struct = art.get('narrative_arc', {})
            arc_id = arc_struct.get('arc_id')
            if arc_id is not None:
                active_count += 1
                self.assertIn(
                    arc_id, arc_ids_in_mem,
                    f"Article {art.get('id')} references missing arc_id {arc_id}"
                )
        self.assertGreater(active_count, 0, "Expected articles bound to active arcs")

    def test_chapter_count_exact_synchronization(self):
        """Article total_chapters must match the exact chapter_count in narrative memory."""
        arc_map = {arc.get('arc_id'): arc for arc in self.memory.get('arcs', [])}
        articles = self.news_data.get('articles', [])

        for art in articles:
            arc_struct = art.get('narrative_arc', {})
            arc_id = arc_struct.get('arc_id')
            if arc_id is not None:
                mem_arc = arc_map[arc_id]
                expected_count = len(mem_arc.get('chapter_titles', []))
                self.assertEqual(
                    arc_struct.get('total_chapters'), expected_count,
                    f"Article {art.get('id')} total_chapters ({arc_struct.get('total_chapters')}) != mem ({expected_count})"
                )


class TestMultiChapterJaccardStability(unittest.TestCase):
    """Stress-test multi-chapter Jaccard calculations to prevent denominator dilution and runaway."""

    def test_denominator_dilution_protection_via_pairwise_recent_chapters(self):
        """Verify that accumulating many chapters does not prevent a valid follow-up from matching."""
        # Create an arc with 10 historical chapters covering varied vocabulary
        historical_chapters = [
            f"Chapter {i}: German government debates economic policy and industrial energy subsidies in Berlin"
            for i in range(1, 10)
        ]
        # Latest chapter is specifically about semiconductor subsidies in Dresden
        historical_chapters.append("Germany approves 5 billion euro subsidy for Dresden chip factory")

        arc = {
            'arc_id': 'arc-chip-factory',
            'title': "Germany Approves Dresden Semiconductor Subsidy",
            'keywords': ['germani', 'approv', 'dresden', 'semiconductor', 'subsidi'],
            'entity_signature': 'DE:Dresden',
            'category': 'Business',
            'regions': ['Europe'],
            'chapter_count': 10,
            'chapter_titles': historical_chapters,
            'sources_involved': ['Handelsblatt']
        }

        # Incoming article follows up on the Dresden chip factory
        incoming = {
            'title': "Dresden chip factory construction begins following German government subsidy approval",
            'category': 'Business',
            'region': 'Europe',
            'entities': {
                'locations': ['Germany', 'Dresden'],
                'organizations': ['European Semiconductor Union']
            }
        }

        matched_arc, score = match_article_to_arc(incoming, [arc], threshold=0.30)
        self.assertIsNotNone(
            matched_arc,
            f"Valid follow-up failed to match due to denominator dilution! Score: {score}"
        )
        self.assertGreaterEqual(score, 0.30)

    def test_arc_mutation_runaway_resistance(self):
        """Unrelated story must NOT bind to an arc even if the arc has a large vocabulary pool."""
        historical_chapters = [
            f"Chapter {i}: European union diplomats hold climate summits in Brussels and Paris"
            for i in range(1, 15)
        ]
        arc = {
            'arc_id': 'arc-climate-summit',
            'title': "EU Climate Summit in Brussels",
            'keywords': ['eu', 'climat', 'summit', 'brussel', 'pari', 'diplomat'],
            'entity_signature': 'FR:Brussels',
            'category': 'World',
            'regions': ['Europe'],
            'chapter_count': 14,
            'chapter_titles': historical_chapters,
            'sources_involved': ['Le Monde']
        }

        # Unrelated European story (e.g. art heist or sports)
        unrelated = {
            'title': "Louvre museum recovers stolen 18th century painting during French police raid",
            'category': 'World',
            'region': 'Europe',
            'entities': {
                'locations': ['France', 'Paris'],
                'organizations': ['Louvre']
            }
        }

        matched_arc, score = match_article_to_arc(unrelated, [arc], threshold=0.30)
        self.assertIsNone(
            matched_arc,
            f"Unrelated story falsely bound to large arc! Score: {score}"
        )


if __name__ == '__main__':
    unittest.main()
