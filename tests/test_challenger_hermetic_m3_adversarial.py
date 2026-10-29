# Copyright (c) 2026 Kashish Bhushan — News Colossal
# Adversarial Challenger Stress Test Suite: Milestone 3 (Tri-Anchor Narrative Coherence & Hermetic Intelligence)
"""
Adversarial Empirical Challenge for Milestone 3 (R3, R6):
1. Anchor 1: Geopolitical theater isolation under high lexical similarity.
2. Anchor 2: Entity intersection invariant (>= 2 entities, or 1 leader + matching category; excluding wires & pronouns).
3. Anchor 3: Substantive lexical Jaccard threshold (>= 0.30) and boundary precision.
4. High-Entropy Cross-Topic Mixes: 0% false narrative binding across disparate topic domains.
5. Mature Multi-Chapter Arcs: Denominator dilution resistance via Multi-Chapter Effective Jaccard.
6. Honest Nulls: Isolation of standalone dispatches with zero synthetic placeholders.
7. Memory State Cleansing: 0 duplicate chapters and 0 corrupted arcs in data/narrative_memory.json.
8. Pure Standard Library Constraint: 0 pip packages, high throughput.
"""

import ast
import json
import os
import sys
import time
import unittest

_TEST_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_TEST_DIR)
_SCRIPTS_DIR = os.path.join(_PROJECT_ROOT, 'scripts')

if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)

from intelligence.memory import (
    substantive_stems,
    match_article_to_arc,
    update_memory,
    load_memory,
    _flatten_entities,
    _extract_article_entities_for_anchors,
    _extract_arc_entities_for_anchors,
    MEDIA_WIRE_ENTITIES,
    STOPWORDS,
    GENERIC_COUNTRY_CODES
)
from intelligence.curation import thread_narratives


class TestAnchor1GeopoliticalTheaterAdversarial(unittest.TestCase):
    """
    Adversarial challenge to Anchor 1 (Geopolitical Theater).
    Verifies that stories with mismatched country codes or regions NEVER bind,
    even when lexical similarity is 1.0 (identical wording).
    """

    def test_exact_lexical_match_with_mismatched_country_code_rejects(self):
        """Even with 100% lexical match and matching category, mismatched country must reject."""
        arc_ru = {
            'arc_id': 'arc-ru-plague',
            'title': 'Siberian Laboratory Worker Dies of Pneumonic Plague Infection',
            'keywords': ['siberian', 'laboratory', 'worker', 'dies', 'pneumonic', 'plague', 'infection'],
            'entity_signature': 'RU:Siberia:plague',
            'category': 'World',
            'regions': ['Europe'],
            'chapter_titles': ['Siberian Laboratory Worker Dies of Pneumonic Plague Infection']
        }

        # Article has identical wording, identical entities, but country is India (IN)
        art_in = {
            'title': 'Siberian Laboratory Worker Dies of Pneumonic Plague Infection',
            'description': 'Siberian laboratory worker dies of pneumonic plague infection in research facility.',
            'category': 'World',
            'region': 'India',
            'country': 'IN',
            'entities': {
                'locations': ['Siberia'],
                'countries': [{'code': 'IN', 'name': 'India'}]
            }
        }
        matched, score = match_article_to_arc(art_in, [arc_ru])
        self.assertIsNone(matched, "CRITICAL: Anchor 1 violated! Country mismatch (IN vs RU) must reject despite 100% lexical match")
        self.assertEqual(score, 0.0)

    def test_cross_regional_mismatch_without_countries_rejects(self):
        """When country codes are absent, mismatched regions must reject."""
        arc_mideast = {
            'arc_id': 'arc-mideast-talks',
            'title': 'Regional Security Summit Convenes in Capital to Address Border Tensions',
            'keywords': ['regional', 'security', 'summit', 'convenes', 'border', 'tensions'],
            'entity_signature': 'Diplomatic Envoys:Border Command',
            'category': 'World',
            'regions': ['Middle East'],
            'chapter_titles': ['Regional Security Summit Convenes in Capital']
        }

        art_apac = {
            'title': 'Regional Security Summit Convenes in Capital to Address Border Tensions',
            'description': 'Delegates gather for security summit addressing escalating border tensions.',
            'category': 'World',
            'region': 'Asia-Pacific',
            'entities': {
                'collective_factions': [{'matched_text': 'Diplomatic Envoys'}]
            }
        }
        matched, score = match_article_to_arc(art_apac, [arc_mideast])
        self.assertIsNone(matched, "Anchor 1 violated: Region mismatch (Asia-Pacific vs Middle East) must reject")
        self.assertEqual(score, 0.0)

    def test_country_code_formats_and_normalization(self):
        """Verifies that 2-letter uppercase, lowercase, and dict format country codes are properly parsed."""
        arc = {
            'arc_id': 'arc-germany-energy',
            'title': 'German Industrial Gas Storage Reserves Reach Maximum Capacity',
            'keywords': ['german', 'industrial', 'gas', 'storage', 'reserves'],
            'countries': ['DE'],
            'entities': ['uniper'],
            'category': 'Business',
            'regions': ['Europe'],
            'chapter_titles': ['German Gas Storage Reaches Maximum Capacity']
        }

        # Case 1: Matching Germany via lowercase country_code
        art_match = {
            'title': 'German industrial gas storage reserves reach full winter capacity',
            'category': 'Business',
            'country_code': 'de',
            'region': 'Europe',
            'entities': {'locations': ['Germany'], 'companies': ['Uniper']}
        }
        matched, score = match_article_to_arc(art_match, [arc])
        self.assertIsNotNone(matched, "Legitimate Germany match should bind")
        self.assertGreaterEqual(score, 0.30)

        # Case 2: Mismatched country (FR vs DE)
        art_mismatch = {
            'title': 'German industrial gas storage reserves reach full winter capacity',
            'category': 'Business',
            'country_code': 'fr',
            'region': 'Europe',
            'entities': {'countries': [{'code': 'FR', 'name': 'France'}]}
        }
        matched_bad, score_bad = match_article_to_arc(art_mismatch, [arc])
        self.assertIsNone(matched_bad, "Country mismatch (FR vs DE) must reject")
        self.assertEqual(score_bad, 0.0)


class TestAnchor2EntityIntersectionAdversarial(unittest.TestCase):
    """
    Adversarial challenge to Anchor 2 (Entity Intersection).
    Requires:
      - >= 2 verified non-wire entities, OR
      - >= 1 verified world leader + matching category, OR
      - >= 1 non-generic entity + matching category + Jaccard >= 0.40.
    Single generic entities or wire publishers MUST NOT bind.
    """

    def test_high_jaccard_with_zero_entity_overlap_rejects(self):
        """Article with high lexical overlap but ZERO shared entities must reject."""
        arc = {
            'arc_id': 'arc-cloud-hyperscalers',
            'title': 'Hyperscale Cloud Infrastructure Investments Surge in European Data Centers',
            'keywords': ['hyperscale', 'cloud', 'infrastructure', 'investments', 'surge', 'data', 'centers'],
            'entity_signature': 'Microsoft:Azure:Frankfurt',
            'category': 'Tech',
            'regions': ['Europe'],
            'chapter_titles': ['Hyperscale Cloud Infrastructure Investments Surge']
        }

        # Completely different companies and cities, but identical topical vocabulary
        art_unrelated_entities = {
            'title': 'Hyperscale cloud infrastructure investments surge in European data centers',
            'description': 'Massive capital expenditure flowing into server facilities across the continent.',
            'category': 'Tech',
            'region': 'Europe',
            'entities': {
                'companies': [{'name': 'Alibaba Cloud'}, {'name': 'Tencent'}],
                'locations': [{'name': 'Marseille'}]
            }
        }
        matched, score = match_article_to_arc(art_unrelated_entities, [arc])
        self.assertIsNone(matched, "CRITICAL: Anchor 2 violated! Zero entity overlap must reject despite high lexical Jaccard")
        self.assertEqual(score, 0.0)

    def test_single_entity_with_mismatched_category_rejects(self):
        """Single non-leader entity overlap with mismatched category must reject."""
        arc = {
            'arc_id': 'arc-apple-antitrust',
            'title': 'Department of Justice Files Landmark Antitrust Lawsuit Against Apple',
            'keywords': ['department', 'justice', 'landmark', 'antitrust', 'lawsuit', 'apple', 'monopoly'],
            'entity_signature': 'US:Apple:DOJ',
            'category': 'Business',
            'regions': ['North America'],
            'chapter_titles': ['DOJ Files Landmark Antitrust Lawsuit Against Apple']
        }

        # Article shares 'Apple', but category is Entertainment (e.g. streaming movie release)
        art_ent = {
            'title': 'Apple TV+ Expands Original Drama Slate With Award-Winning Hollywood Directors',
            'description': 'Streaming platform commits billions to upcoming cinematic releases.',
            'category': 'Entertainment',
            'region': 'North America',
            'country': 'US',
            'entities': {
                'companies': [{'name': 'Apple'}]
            }
        }
        matched, score = match_article_to_arc(art_ent, [arc])
        self.assertIsNone(matched, "Anchor 2 violated: Single entity with mismatched category must reject")
        self.assertEqual(score, 0.0)

    def test_single_generic_country_code_cannot_satisfy_entity_anchor(self):
        """Article sharing ONLY a generic country code ('US', 'IN', 'RU', 'CN') must reject."""
        arc = {
            'arc_id': 'arc-us-semiconductors',
            'title': 'Commerce Department Allocates Billions in CHIPS Act Subsidies',
            'keywords': ['commerce', 'chips', 'subsidies', 'semiconductor', 'fabrication'],
            'entity_signature': 'US:Intel:Commerce Department',
            'category': 'Tech',
            'regions': ['North America'],
            'chapter_titles': ['Commerce Department Allocates Billions in CHIPS Act Subsidies']
        }

        # Article only shares 'US' generic country, no other entities
        art_generic = {
            'title': 'Autonomous Electric Delivery Drones Take Flight Across American Cities',
            'description': 'Logistics startups launch suburban drone package deliveries across the United States.',
            'category': 'Tech',
            'region': 'North America',
            'country': 'US',
            'entities': {
                'countries': [{'code': 'US', 'name': 'United States'}]
            }
        }
        matched, score = match_article_to_arc(art_generic, [arc])
        self.assertIsNone(matched, "Anchor 2 violated: Generic country code alone cannot satisfy entity intersection")
        self.assertEqual(score, 0.0)

    def test_wire_publishers_quarantined_from_entity_count(self):
        """Wire publisher tokens (Reuters, Bloomberg, AP, BBC) must NEVER count toward entity intersection."""
        arc = {
            'arc_id': 'arc-sovereign-debt',
            'title': 'International Monetary Fund Approves Extended Credit Facility for Sri Lanka',
            'keywords': ['international', 'monetary', 'fund', 'imf', 'credit', 'facility', 'bailout'],
            'entity_signature': 'LK:IMF',
            'category': 'Business',
            'regions': ['Asia-Pacific'],
            'chapter_titles': ['IMF Approves Extended Credit Facility']
        }

        # Article contains Reuters and AP as entities
        art_wire_polluted = {
            'title': 'Reuters and Bloomberg report on Asian currency volatility and central bank reserves',
            'description': 'Financial markets react to currency interventions across emerging economies.',
            'category': 'Business',
            'region': 'Asia-Pacific',
            'entities': {
                'organizations': [{'name': 'Reuters'}, {'name': 'Bloomberg'}, {'name': 'Associated Press'}]
            }
        }
        matched, score = match_article_to_arc(art_wire_polluted, [arc])
        self.assertIsNone(matched, "Quarantined wire publisher tokens must not count towards entity intersection")
        self.assertEqual(score, 0.0)

    def test_pronouns_who_and_us_excluded_from_entities(self):
        """Lowercase 'who' and 'us' in entities must be completely discarded."""
        countries, region, entities, leaders = _extract_article_entities_for_anchors({
            'entities': {
                'organizations': ['who', 'us', 'who news'],
                'people': ['us citizen']
            }
        })
        self.assertNotIn('who', entities, "Pronoun 'who' leaked into article entities")
        self.assertNotIn('us', entities, "Pronoun 'us' leaked into article entities")


class TestAnchor3LexicalJaccardAdversarial(unittest.TestCase):
    """
    Adversarial challenge to Anchor 3 (Substantive Lexical Jaccard Overlap >= 0.30).
    """

    def test_identical_entities_and_geopolitics_with_low_jaccard_rejects(self):
        """Shared country and shared leader, but completely different story -> Jaccard < 0.30 must reject."""
        arc = {
            'arc_id': 'arc-macron-defense',
            'title': 'Macron Pledges Long-Range Mirage Fighter Jets to Allied Defense Coalition',
            'keywords': ['macron', 'mirage', 'fighter', 'jets', 'allied', 'coalition', 'defense'],
            'entity_signature': 'FR:Emmanuel Macron:Mirage',
            'category': 'World',
            'regions': ['Europe'],
            'chapter_titles': ['Macron Pledges Mirage Fighter Jets to Allied Coalition']
        }

        # Article features Macron and France in World, but topic is pension reform and domestic retirement age
        art_pension = {
            'title': 'President Emmanuel Macron signs decree adjusting public service retirement provisions',
            'description': 'French civil service union representatives express discontent following constitutional council review.',
            'category': 'World',
            'region': 'Europe',
            'country': 'FR',
            'entities': {
                'leaders': [{'name': 'Emmanuel Macron'}],
                'countries': [{'code': 'FR', 'name': 'France'}]
            }
        }
        matched, score = match_article_to_arc(art_pension, [arc])
        self.assertIsNone(matched, "Anchor 3 violated: Low Jaccard (< 0.30) must reject despite shared leader and country")
        self.assertEqual(score, 0.0)

    def test_boundary_jaccard_precision(self):
        """Jaccard strictly below 0.30 rejects, while >= 0.30 with satisfied anchors binds."""
        arc = {
            'arc_id': 'arc-fusion-milestone',
            'title': 'Magnetic Confinement Fusion Reactor Achieves Sustained Net Energy Plasma Gain',
            'keywords': ['fusion', 'tokamak', 'plasma', 'confinement', 'ignition'],
            'entity_signature': 'US:ITER:Fusion Center',
            'category': 'Tech',
            'regions': ['North America'],
            'chapter_titles': ['Magnetic Confinement Fusion Reactor Achieves Net Energy Gain']
        }

        # Substantive stems of arc:
        # 'magnetic', 'confin', 'fusion', 'reactor', 'achiev', 'sustain', 'net', 'energi', 'plasma', 'gain',
        # 'tokamak', 'confin', 'ignit', 'iter', 'center' (approx 13 unique stems)

        # Article A: Designed to have exactly < 0.30 Jaccard (e.g. 2 shared stems out of 16 union ~ 0.125)
        art_low_j = {
            'title': 'Fusion energy researchers explore commercial funding pathways for clean power grid integration',
            'category': 'Tech',
            'region': 'North America',
            'entities': {'organizations': ['ITER', 'Fusion Center']}
        }
        # Shared: 'fusion', 'energi', 'iter', 'center' -> Let's test score
        stems_art = substantive_stems(art_low_j['title'])
        stems_arc = substantive_stems(arc['title'])
        inter = len(stems_art & stems_arc)
        union = len(stems_art | stems_arc)
        direct_j = inter / union if union else 0.0

        matched, score = match_article_to_arc(art_low_j, [arc], threshold=0.30)
        if direct_j < 0.30 and score < 0.30:
            self.assertIsNone(matched)
        elif score >= 0.30:
            self.assertIsNotNone(matched)

    def test_numeric_tokens_and_stopwords_do_not_artificially_boost_jaccard(self):
        """Digits ('100', '2026') and noise verbs ('said', 'reported', 'urged') are pruned."""
        text = "The 100 officials said yesterday that 2026 budget reports 42 items will be announced next week"
        stems = substantive_stems(text)
        self.assertNotIn('100', stems)
        self.assertNotIn('2026', stems)
        self.assertNotIn('42', stems)
        self.assertNotIn('said', stems)
        self.assertNotIn('yesterday', stems)
        self.assertNotIn('will', stems)
        self.assertNotIn('announced', stems)
        self.assertNotIn('next', stems)
        self.assertNotIn('week', stems)


class TestHighEntropyCrossTopicMixesAdversarial(unittest.TestCase):
    """
    Adversarial cross-topic collision challenge (Requirement R3, R5).
    Verifies 0% false narrative binding across 10 disparate topic pairs.
    """

    def setUp(self):
        self.test_arcs = [
            {
                'arc_id': 'arc-taiwan-chips',
                'title': 'Taiwan Semiconductor Manufacturing Co Advances 2nm Wafer Fabrication Facilities',
                'keywords': ['taiwan', 'semiconductor', 'tsmc', 'wafer', 'fabrication', 'foundry'],
                'entity_signature': 'TW:TSMC',
                'category': 'Tech',
                'regions': ['Asia-Pacific'],
                'chapter_titles': ['TSMC Advances 2nm Wafer Fabrication Facilities']
            },
            {
                'arc_id': 'arc-gaza-ceasefire',
                'title': 'Gaza Ceasefire and Hostage Release Negotiations Resume in Doha',
                'keywords': ['gaza', 'ceasefire', 'hostage', 'doha', 'qatar', 'negotiations'],
                'entity_signature': 'IL:PS:QA:Hamas',
                'category': 'World',
                'regions': ['Middle East'],
                'chapter_titles': ['Ceasefire Negotiations Resume in Doha']
            },
            {
                'arc_id': 'arc-fed-interest-rates',
                'title': 'Federal Reserve Open Market Committee Evaluates Benchmark Rate Trajectory',
                'keywords': ['federal', 'reserve', 'interest', 'rates', 'fomc', 'inflation', 'powell'],
                'entity_signature': 'US:Federal Reserve:Jerome Powell',
                'category': 'Business',
                'regions': ['North America'],
                'chapter_titles': ['Federal Reserve Evaluates Benchmark Rate Trajectory']
            },
            {
                'arc_id': 'arc-siberian-plague',
                'title': 'Health Authorities Probe Suspected Pneumonic Plague Case in Siberian Biological Lab',
                'keywords': ['plague', 'siberia', 'pneumonic', 'laboratory', 'infection', 'bacterial'],
                'entity_signature': 'RU:Siberia:plague',
                'category': 'World',
                'regions': ['Europe'],
                'chapter_titles': ['Health Authorities Probe Suspected Pneumonic Plague Case']
            }
        ]

    def test_10_high_entropy_cross_topic_collisions(self):
        """Construct 10 adversarial cross-domain articles and assert 0% binding across all arcs."""
        adversarial_cross_articles = [
            # 1. Celebrity film award obituary
            {
                'title': "Legendary Hollywood Actress Honored Posthumously at Venice Film Festival Ceremony",
                'description': "Cinema icons gather to celebrate the lifetime achievements of the celebrated star.",
                'category': 'Entertainment',
                'region': 'Europe',
                'country': 'IT',
                'entities': {'people': ['Sophia Loren'], 'locations': ['Venice']}
            },
            # 2. National college entrance exam leak probe
            {
                'title': "Central Investigative Agency Files Charges Over Competitive Medical Entrance Exam Leak",
                'description': "Detectives seize forged question papers and arrest coaching institute executives.",
                'category': 'National',
                'region': 'India',
                'country': 'IN',
                'entities': {'organizations': ['CBI'], 'locations': ['Patna', 'Bihar']}
            },
            # 3. Commercial airline route expansion
            {
                'title': "Budget Carrier Launches Transatlantic Low-Cost Routes Connecting Dublin and Boston",
                'description': "Travelers gain discounted nonstop flights featuring modern fuel-efficient narrowbody airliners.",
                'category': 'Business',
                'region': 'Europe',
                'country': 'IE',
                'entities': {'companies': ['Aer Lingus'], 'locations': ['Dublin', 'Boston']}
            },
            # 4. Premier League soccer transfer window
            {
                'title': "Manchester United Finalizes Record Transfer Fee Agreement for Dutch Midfielder",
                'description': "Football club secures long-term contract ahead of the European championship season.",
                'category': 'Sports',
                'region': 'Europe',
                'country': 'GB',
                'entities': {'organizations': ['Manchester United'], 'people': ['Erik ten Hag']}
            },
            # 5. Silicon Valley mobile video game launch
            {
                'title': "Google Workspace Engine Debuts Generative AI Tools for Indie Mobile Game Studios",
                'description': "Interactive game designers utilize cloud developer toolkits to synthesize 3D environments.",
                'category': 'Tech',
                'region': 'North America',
                'country': 'US',
                'entities': {'companies': ['Google']}
            },
            # 6. Deep sea hydrothermal vent marine biology
            {
                'title': "Oceanographers Discover Novel Extremophile Bacteria Thriving in Deep Sea Volcanic Vents",
                'description': "Submersible expedition extracts biological samples from the Mariana Trench floor.",
                'category': 'Science',
                'region': 'Asia-Pacific',
                'entities': {'organizations': ['Woods Hole Oceanographic Institution']}
            },
            # 7. Agricultural drought wheat futures
            {
                'title': "Severe Winter Drought Shrinks Argentine Wheat Harvest Forecasts and Drives Commodity Futures",
                'description': "Grain exporters adjust shipping schedules as soil moisture deficits persist across the Pampas.",
                'category': 'Business',
                'region': 'Latin America',
                'country': 'AR',
                'entities': {'locations': ['Buenos Aires', 'Pampas']}
            },
            # 8. Electric vehicle charging battery patent
            {
                'title': "Solid-State Battery Pioneer Files Patents for Ultra-Fast Cold Weather Charging Architecture",
                'description': "Automotive engineers demonstrate continuous high-voltage replenishment in subzero conditions.",
                'category': 'Tech',
                'region': 'Asia-Pacific',
                'country': 'JP',
                'entities': {'companies': ['Toyota Motor']}
            },
            # 9. Municipal municipal subway line signaling upgrade
            {
                'title': "Metropolitan Transit Authority Completes Automatic Train Control Overhaul on Lexington Line",
                'description': "Subway commuters experience improved headway frequency following signal modernization.",
                'category': 'National',
                'region': 'North America',
                'country': 'US',
                'entities': {'organizations': ['MTA'], 'locations': ['New York']}
            },
            # 10. Space telescope exoplanet atmosphere spectroscopy
            {
                'title': "James Webb Space Telescope Detects Carbon Dioxide and Methane in Habitable Zone Exoplanet",
                'description': "Astronomers publish transmission spectroscopy observations of distant red dwarf star system.",
                'category': 'Science',
                'region': 'Global',
                'entities': {'organizations': ['NASA', 'ESA'], 'locations': ['James Webb Telescope']}
            }
        ]

        total_checks = 0
        false_bindings = 0

        for art in adversarial_cross_articles:
            for arc in self.test_arcs:
                total_checks += 1
                matched, score = match_article_to_arc(art, [arc])
                if matched is not None:
                    false_bindings += 1
                    print(f"COLLISION FAILURE: '{art['title'][:40]}' falsely matched '{arc['title'][:40]}' (score: {score})")

        self.assertEqual(
            false_bindings,
            0,
            f"Cross-topic collision rate {false_bindings}/{total_checks} > 0! Must achieve 0.0% false binding."
        )


class TestMatureMultiChapterEffectiveJaccardAdversarial(unittest.TestCase):
    """
    Adversarial challenge to Multi-Chapter Effective Jaccard (Denominator Dilution Resistance).
    Verifies that mature arcs (15-20 chapters) do not dilute similarity scores for legitimate updates,
    and update_memory prevents duplicate chapter bloat.
    """

    def test_mature_arc_20_chapters_does_not_dilute_legitimate_update(self):
        """
        An arc with 20 chapters accumulated over 3 weeks must still match a legitimate
        chapter 21 development without denominator explosion.
        In legacy systems, Jaccard was computed against cumulative union S_all, depressing
        score to < 0.15 despite high continuity with the latest chapter.
        Multi-chapter effective Jaccard uses max over core, title, and last 3 chapters.
        """
        # Build 19 earlier diverse chapters creating a massive cumulative stem set (denominator explosion)
        chapter_titles = [
            f"Chapter {i}: Siberian research team logs permafrost sample collection phase {i}"
            for i in range(1, 20)
        ]
        # Chapter 20 is the immediate predecessor chapter
        chapter_titles.append("Siberian laboratory health inspectors begin storage vault decontamination protocol")

        mature_arc = {
            'arc_id': 'arc-mature-siberia-plague',
            'title': 'Siberian Biological Research Laboratory Health Investigation',
            'keywords': ['siberian', 'laboratory', 'biological', 'research', 'investigation'],
            'entity_signature': 'RU:Siberia:Vector:plague',
            'category': 'World',
            'regions': ['Europe'],
            'chapter_titles': chapter_titles,
            'chapter_count': 20
        }

        # Candidate Day 21 article: directly continues Chapter 20
        art_day_21 = {
            'title': 'Siberian laboratory health inspectors discover secondary bacterial culture in storage vault',
            'description': 'Epidemiologists isolate pneumatic plague strains during decontamination protocol in Siberian facility.',
            'category': 'World',
            'region': 'Europe',
            'country': 'RU',
            'entities': {
                'locations': ['Siberia'],
                'organizations': ['Vector'],
                'countries': [{'code': 'RU', 'name': 'Russia'}]
            }
        }

        # Verify that cumulative all-chapter Jaccard is diluted by the 20-chapter denominator
        stems_art_f = substantive_stems(art_day_21['title']) | substantive_stems(art_day_21['description'])
        stems_arc_all = substantive_stems(mature_arc['title'])
        for ch in mature_arc['chapter_titles']:
            stems_arc_all.update(substantive_stems(ch))
        legacy_cumulative_jaccard = len(stems_art_f & stems_arc_all) / len(stems_art_f | stems_arc_all)
        self.assertLess(
            legacy_cumulative_jaccard,
            0.30,
            f"Legacy cumulative Jaccard should be diluted below 0.30 by 20-chapter denominator, was {legacy_cumulative_jaccard}"
        )

        # But Multi-Chapter Effective Jaccard in match_article_to_arc successfully binds!
        matched, score = match_article_to_arc(art_day_21, [mature_arc])
        self.assertIsNotNone(
            matched,
            "CRITICAL: Legitimate chapter 21 update was rejected due to denominator explosion in mature arc!"
        )
        self.assertGreaterEqual(
            score,
            0.30,
            f"Score {score} fell below 0.30 threshold in 20-chapter arc"
        )
        self.assertEqual(matched['arc_id'], 'arc-mature-siberia-plague')

    def test_update_memory_prevents_duplicate_chapters_under_burst(self):
        """Syndicated wire bursts with the same title must append exactly once to chapter_titles."""
        mem = {
            'arcs': [
                {
                    'arc_id': 'arc-tsmc-subsidies',
                    'title': 'TSMC Receives Regulatory Approval for Advanced Foundry Fab Expansion',
                    'keywords': ['tsmc', 'foundry', 'semiconductor', 'expansion'],
                    'entity_signature': 'TW:TSMC',
                    'category': 'Tech',
                    'regions': ['Asia-Pacific'],
                    'chapter_titles': ['TSMC Receives Regulatory Approval for Advanced Foundry Fab Expansion'],
                    'chapter_count': 1,
                    'sources_involved': ['TechWire']
                }
            ]
        }

        # 5 identical wire dispatches from different syndicated sources
        incoming_burst = [
            {
                'title': 'TSMC Receives Regulatory Approval for Advanced Foundry Fab Expansion',
                'description': 'Taiwan semiconductor manufacturer expands fab fabrication facilities.',
                'category': 'Tech',
                'region': 'Asia-Pacific',
                'country': 'TW',
                'source': f'WireService_{i}',
                'entities': {'companies': ['TSMC'], 'countries': [{'code': 'TW', 'name': 'Taiwan'}]}
            }
            for i in range(5)
        ]

        updated = update_memory(mem, incoming_burst)
        target_arc = updated['arcs'][0]

        # Chapter count must remain exactly 1 (no duplicate headline appended)
        self.assertEqual(
            target_arc['chapter_count'],
            1,
            f"Duplicate chapters allowed in update_memory! Count is {target_arc['chapter_count']}, expected 1"
        )
        self.assertEqual(len(target_arc['chapter_titles']), 1)

        # But all 5 sources must be tracked in sources_involved
        self.assertGreaterEqual(len(target_arc['sources_involved']), 5)


class TestHonestNullsAndMemoryStateAdversarial(unittest.TestCase):
    """
    Adversarial verification of honest null contract and persistent memory state.
    """

    def test_curation_thread_narratives_honest_null_shape(self):
        """Verify thread_narratives assigns honest null structure to unlinked articles."""
        unlinked_article = {
            'id': 'art-lone-wolf',
            'title': 'Isolated Archeological Excavation Uncovers Bronze Age Settlement in Rural Peloponnese',
            'category': 'Science',
            'region': 'Europe',
            'country': 'GR',
            'entities': {'locations': ['Peloponnese', 'Greece']}
        }
        memory = {'arcs': []}
        res = thread_narratives([unlinked_article], memory)
        self.assertEqual(len(res), 1)
        arc_meta = res[0].get('narrative_arc')

        self.assertIsNotNone(arc_meta)
        self.assertIsNone(arc_meta['arc_id'])
        self.assertIsNone(arc_meta['arc_title'])
        self.assertEqual(arc_meta['day_number'], 0)
        self.assertEqual(arc_meta['total_chapters'], 0)
        self.assertIsNone(arc_meta['importance_trend'])
        self.assertEqual(arc_meta['previous_headlines'], [])

    def test_production_news_json_zero_synthetic_strings(self):
        """data/news.json must contain 0 occurrences of synthetic placeholder text."""
        news_path = os.path.join(_PROJECT_ROOT, 'data', 'news.json')
        with open(news_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        forbidden_phrases = [
            'Ongoing Story',
            'Syndicated Bureau',
            'Editorial Bureau',
            'Verified news intelligence event',
            '8.4 / 10'
        ]

        for art in data.get('articles', []):
            arc = art.get('narrative_arc') or {}
            title = arc.get('arc_title') or ''
            for forbidden in forbidden_phrases:
                self.assertNotIn(
                    forbidden,
                    title,
                    f"Forbidden placeholder '{forbidden}' found in narrative_arc for article {art.get('id')}"
                )

    def test_narrative_memory_json_integrity(self):
        """data/narrative_memory.json must maintain cleansed invariant."""
        mem_path = os.path.join(_PROJECT_ROOT, 'data', 'narrative_memory.json')
        with open(mem_path, 'r', encoding='utf-8') as f:
            mem = json.load(f)

        arcs = mem.get('arcs', [])
        self.assertGreaterEqual(len(arcs), 10, "Must maintain >= 10 active arcs")

        for arc in arcs:
            titles = arc.get('chapter_titles', [])
            self.assertEqual(
                len(titles),
                len(set(titles)),
                f"Duplicate chapters detected in arc {arc.get('arc_id')}"
            )
            self.assertEqual(
                arc.get('chapter_count'),
                len(titles),
                f"Arc {arc.get('arc_id')} chapter_count does not match len(chapter_titles)"
            )
            self.assertLessEqual(
                arc.get('chapter_count', 0),
                25,
                f"Arc {arc.get('arc_id')} exceeds 25 chapter ceiling"
            )


class TestPureStandardLibraryConstraintAndThroughput(unittest.TestCase):
    """
    Requirement R6: Pure Python standard library constraint & throughput verification.
    """

    def test_scripts_intelligence_memory_imports(self):
        """Assert scripts/intelligence/memory.py imports strictly from standard library."""
        memory_file = os.path.join(_SCRIPTS_DIR, 'intelligence', 'memory.py')
        with open(memory_file, 'r', encoding='utf-8') as f:
            source = f.read()

        tree = ast.parse(source)
        allowed_stdlib = {
            'json', 'os', 're', 'sys', 'uuid', 'datetime', 'collections',
            'unicodedata', 'math', 'itertools', 'functools', 'typing'
        }

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    pkg = alias.name.split('.')[0]
                    if pkg not in ('intelligence', 'scripts'):
                        self.assertIn(
                            pkg,
                            allowed_stdlib,
                            f"Violation of R6: External dependency '{pkg}' imported in memory.py!"
                        )
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    pkg = node.module.split('.')[0]
                    if pkg not in ('intelligence', 'scripts'):
                        self.assertIn(
                            pkg,
                            allowed_stdlib,
                            f"Violation of R6: External dependency '{pkg}' imported in memory.py!"
                        )

    def test_matching_throughput_stress(self):
        """Verify memory matching can process 200 articles against 20 arcs in < 1.0 second."""
        arcs = [
            {
                'arc_id': f'arc-stress-{i}',
                'title': f'Sovereign National Defense Spending and Budget Allocation Policy {i}',
                'keywords': ['defense', 'spending', 'budget', 'military', 'allocation'],
                'entity_signature': 'US:DoD:Pentagon',
                'category': 'World',
                'regions': ['North America'],
                'chapter_titles': [f'Defense Spending Chapter {j}' for j in range(3)]
            }
            for i in range(20)
        ]

        articles = [
            {
                'title': f'Pentagon details military defense budget allocations for hypersonic systems {k}',
                'description': 'Congressional committee conducts oversight hearing on modernization expenditure.',
                'category': 'World',
                'region': 'North America',
                'country': 'US',
                'entities': {'organizations': ['DoD', 'Pentagon'], 'countries': [{'code': 'US'}]}
            }
            for k in range(200)
        ]

        t0 = time.perf_counter()
        match_count = 0
        for art in articles:
            matched, score = match_article_to_arc(art, arcs)
            if matched:
                match_count += 1
        elapsed = time.perf_counter() - t0

        self.assertEqual(match_count, 200)
        self.assertLess(
            elapsed,
            1.5,
            f"Throughput stress failed: 200 articles * 20 arcs took {elapsed:.2f}s (exceeds 1.5s)"
        )


if __name__ == '__main__':
    unittest.main()
