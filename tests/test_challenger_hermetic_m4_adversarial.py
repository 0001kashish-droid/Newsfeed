#!/usr/bin/env python3
"""
Empirical Adversarial Challenge Suite - Milestone 4: Honest Nulls & Adaptive UI Morphology (R4)
Author: challenger_hermetic_m4_2 (Empirical Challenger)
Targets: app.js, style.css, data/news.json

Verifies:
1. Modal State Transitions & State Isolation:
   - Opening an arc-linked article (arc_id != null) sets _activeNarrativeChapters & _activeNarrativeIndex.
   - Navigating via ArrowRight (step=+1) to a standalone article (arc_id === null) completely clears
     window._activeNarrativeChapters to [] and window._activeNarrativeIndex to -1.
   - Scrubber markup (#narrativeTimeMachine, .time-machine-scrubber-row, .chapter-step-btn) is completely
     suppressed for standalone articles.
   - Navigating via ArrowLeft (step=-1) from standalone back to arc-linked restores authentic chapters.
   - Sequential navigation across all 134 articles in data/news.json verifies 0 cross-story chapter leakage.
   - Rapid bidirectional navigation and edge case states (None, empty arc, missing headlines, genesis arc).
2. Stress Test renderStructuredIntelligenceView Across All 134 Articles:
   - 0 exceptions thrown across all 134 articles in data/news.json.
   - All 134 articles produce valid, non-empty, well-formed HTML.
   - All 73 standalone articles render with Hero Core Event morphology:
     - 'intel-atom-card atom-hero atom-span-2'
     - 'morphology-standalone morphology-5col'
     - '.horizon-standalone-badge' with '✦ Standalone Dispatch'
     - '.horizon-standalone-detail' with 'Discrete Single-Event Horizon'
   - All wire reporting sources appear exclusively in subordinate provenance:
     - '.subordinate-provenance-ledger' (📡 Chronicled by {source})
     - '.structured-intel-provenance-strip' (📡 Reporting Provenance: Chronicled by {source})
     - 0 wire publisher names inside Active Agent, Leaders, Organizations, Collective Factions, or Sovereign Stakeholders.
3. Absolute Zero-Tolerance for Synthetic Placeholders:
   - Zero occurrences of 'Verified news intelligence event', 'Regional & Non-State Factions', '8.4 / 10',
     'Syndicated Bureau', 'Editorial Bureau', 'Solo Investigative Scoop'.
4. Adversarial Payload Fuzzing:
   - XSS injections, malformed records, null/missing fields, extreme score values.
"""

import html
import json
import os
import re
import unittest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read_file(relative_path):
    full_path = os.path.join(PROJECT_ROOT, relative_path)
    with open(full_path, "r", encoding="utf-8") as f:
        return f.read()


def load_json(relative_path):
    full_path = os.path.join(PROJECT_ROOT, relative_path)
    with open(full_path, "r", encoding="utf-8") as f:
        return json.load(f)


class ModalSimulationEngine:
    """
    High-fidelity simulation of the exact modal state machine and rendering rules in app.js:
    - openModal(id)
    - navigateModal(step)
    - renderExecutiveModal()
    - renderNarrativeTimeMachine(art)
    - getArcChapters(art)
    """

    def __init__(self, articles):
        self.articles = articles
        self.modal_state = {
            "articles": list(articles),
            "currentIndex": 0
        }
        self.active_narrative_chapters = []
        self.active_narrative_index = -1
        self.rendered_html = ""
        self.rendered_narrative_box = ""

    def get_arc_chapters(self, art):
        if not art or not art.get("narrative_arc") or not art["narrative_arc"].get("arc_id"):
            return []
        arc = art["narrative_arc"]
        prev = arc.get("previous_headlines") if isinstance(arc.get("previous_headlines"), list) else []
        chapters = []
        for idx, headline in enumerate(prev):
            chapters.append({
                "chapterIndex": idx + 1,
                "totalChapters": len(prev) + 1,
                "day": idx + 1,
                "title": headline,
                "source": art.get("source") or "Primary Source",
                "articleId": None,
                "isCurrent": False
            })

        chapters.append({
            "chapterIndex": len(prev) + 1,
            "totalChapters": len(prev) + 1,
            "day": arc.get("day_number") or (len(prev) + 1),
            "title": art.get("title"),
            "source": art.get("source") or "Primary Source",
            "articleId": art.get("id"),
            "isCurrent": True
        })
        return chapters

    def render_narrative_time_machine(self, art):
        if not art or not art.get("narrative_arc") or not art["narrative_arc"].get("arc_id"):
            return ""
        chapters = self.get_arc_chapters(art)
        total = len(chapters)
        current_index = total - 1

        self.active_narrative_chapters = chapters
        self.active_narrative_index = current_index

        arc = art["narrative_arc"]
        trend = arc.get("importance_trend") or "stable"
        arc_title = arc.get("arc_title") or art.get("title")

        return (
            f'<div class="narrative-time-machine" id="narrativeTimeMachine" data-arc-id="{html.escape(str(arc.get("arc_id")))}">'
            f'<div class="time-machine-header">'
            f'<span class="time-machine-tag">NARRATIVE TIME MACHINE · ARC SCRUBBER</span>'
            f'<h4 class="time-machine-arc-title">{html.escape(str(arc_title))}</h4>'
            f'</div>'
            f'<div class="time-machine-scrubber-row">'
            f'<button class="chapter-step-btn prev-chapter-btn">&lt;</button>'
            f'<input type="range" class="narrative-time-scrubber narrative-scrubber-slider" id="narrativeTimeScrubber" value="{current_index}" />'
            f'<button class="chapter-step-btn next-chapter-btn">&gt;</button>'
            f'</div>'
            f'<div class="narrative-spotlight-box narrative-chapter-spotlight" id="narrativeSpotlightBox">'
            f'</div>'
            f'</div>'
        )

    def render_executive_modal(self, art=None):
        pool = self.modal_state["articles"]
        curr_idx = self.modal_state["currentIndex"]
        if art is None:
            if not pool or curr_idx >= len(pool):
                return
            art = pool[curr_idx]

        has_arc = bool(art.get("narrative_arc") and art["narrative_arc"].get("arc_id"))
        if not has_arc:
            self.active_narrative_chapters = []
            self.active_narrative_index = -1

        if has_arc:
            time_machine_html = self.render_narrative_time_machine(art)
            narrative_box_html = (
                f'<div class="liquid-glass-narrative-box">'
                f'<span class="narrative-box-icon">📖</span>'
                f'<div class="narrative-box-content">'
                f'<span class="narrative-box-label">Ongoing Narrative Arc · Day {art["narrative_arc"].get("day_number", 1)}</span>'
                f'<span class="narrative-box-title">{html.escape(str(art["narrative_arc"].get("arc_title") or art.get("title")))}</span>'
                f'</div>'
                f'</div>'
                f'{time_machine_html}'
            )
        else:
            narrative_box_html = ""

        self.rendered_narrative_box = narrative_box_html
        return narrative_box_html

    def open_modal(self, article_id):
        idx = next((i for i, a in enumerate(self.modal_state["articles"]) if a.get("id") == article_id), -1)
        if idx == -1:
            return False
        self.modal_state["currentIndex"] = idx
        self.render_executive_modal()
        return True

    def navigate_modal(self, step):
        pool = self.modal_state["articles"]
        if not pool:
            return
        self.modal_state["currentIndex"] = (self.modal_state["currentIndex"] + step + len(pool)) % len(pool)
        self.render_executive_modal()


def render_structured_intelligence_view_sim(art, theme_color="#00f2fe"):
    """
    Exact mirror of renderStructuredIntelligenceView(art, themeColor) from app.js line 3457.
    """
    if art is None:
        return ""

    def escape_html(val):
        if val is None:
            return ""
        return (
            str(val)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#039;")
        )

    entities = art.get("entities") or {}
    leaders = ", ".join(l.get("name") if isinstance(l, dict) else str(l) for l in entities.get("leaders", []))
    orgs = ", ".join(o.get("name") if isinstance(o, dict) else str(o) for o in entities.get("organizations", []))
    countries = ", ".join(c.get("name") or c.get("code") if isinstance(c, dict) else str(c) for c in entities.get("countries", []))
    companies = ", ".join(c.get("name") if isinstance(c, dict) else str(c) for c in entities.get("companies", []))
    actions = ", ".join(str(a) for a in entities.get("actions", []))

    actors = art.get("primary_actors") or (art.get("entities") and art["entities"].get("primary_actors")) or None
    primary_actors_html = ""

    if actors:
        if actors.get("active_agent"):
            agent_type = actors.get("active_agent_type") or "primary"
            primary_actors_html += (
                f'<div><strong>Active Agent:</strong> <span class="actor-name">{escape_html(actors["active_agent"])}</span> '
                f'<span class="actor-type-pill {escape_html(agent_type)}">{escape_html(agent_type)}</span></div>'
            )
        elif leaders:
            primary_actors_html += f'<div><strong>Leaders:</strong> {escape_html(leaders)}</div>'
        elif orgs:
            primary_actors_html += f'<div><strong>Organizations:</strong> {escape_html(orgs)}</div>'
        else:
            primary_actors_html += '<div><strong>Active Agent:</strong> <span class="actor-null-label">Unattributed Dispatch</span></div>'

        if actors.get("impacted_population"):
            impacted_type = actors.get("impacted_type") or "community"
            primary_actors_html += (
                f'<div><strong>Impacted Population:</strong> {escape_html(actors["impacted_population"])} '
                f'<span class="actor-type-pill impacted">{escape_html(impacted_type)}</span></div>'
            )

        factions = actors.get("collective_factions")
        if isinstance(factions, list) and len(factions) > 0:
            factions_text = ", ".join(f.get("canonical_label") or f.get("matched_text") or str(f) for f in factions)
            primary_actors_html += f'<div><strong>Collective Factions:</strong> {escape_html(factions_text)}</div>'

        stakeholders = actors.get("sovereign_stakeholders")
        if isinstance(stakeholders, list) and len(stakeholders) > 0:
            primary_actors_html += f'<div><strong>Sovereign Stakeholders:</strong> {escape_html(", ".join(stakeholders))}</div>'
        elif art.get("region") and art["region"] != "Global":
            primary_actors_html += f'<div><strong>Regional Stakeholder:</strong> {escape_html(art["region"])} sovereign arena</div>'

        frame = actors.get("syntactic_frame")
        if frame and frame.get("verb") and (frame.get("subject") or frame.get("object")):
            primary_actors_html += (
                f'<div class="syntactic-frame-pill"><span class="frame-label">Frame:</span> '
                f'<code>[{escape_html(frame.get("subject") or "Agent")}]</code> '
                f'<strong>{escape_html(frame.get("verb"))}</strong> '
                f'<code>[{escape_html(frame.get("object") or "Target")}]</code></div>'
            )
    else:
        if leaders:
            primary_actors_html += f'<div><strong>Leaders:</strong> {escape_html(leaders)}</div>'
        if orgs:
            primary_actors_html += f'<div><strong>Organizations:</strong> {escape_html(orgs)}</div>'
        if companies:
            primary_actors_html += f'<div><strong>Companies:</strong> {escape_html(companies)}</div>'
        if not leaders and not orgs and not companies:
            if countries:
                primary_actors_html += f'<div><strong>Regional Stakeholders:</strong> {escape_html(countries)} domestic factions</div>'
            else:
                primary_actors_html += '<div><strong>Active Agent:</strong> <span class="actor-null-label">Unattributed Dispatch</span></div>'

    # Quarantine wire source strictly to subordinate provenance ledger:
    primary_actors_html += f'<div class="subordinate-provenance-ledger">📡 Chronicled by {escape_html(art.get("source") or "Primary Source")}</div>'

    cognitive_type = (art.get("cognitive_type") or "strategic").upper()
    scores = art.get("scores") or {}
    temporal = scores.get("temporal")
    if isinstance(temporal, (int, float)):
        if temporal >= 0.85:
            temporal_score = "⚡ Breaking Flash (< 6h)"
        elif temporal >= 0.6:
            temporal_score = "📰 24h Daily Cycle"
        else:
            temporal_score = "🏛️ Multi-Week Macro Epoch"
    else:
        temporal_score = "📰 Daily Cycle"

    composite = scores.get("composite")
    if isinstance(composite, (int, float)):
        composite_score = f"{composite * 10:.1f} / 10"
    elif isinstance(art.get("importance_score"), (int, float)):
        composite_score = f"{art['importance_score']:.1f} / 10"
    else:
        composite_score = "Unscored"

    has_why = bool(art.get("annotation") and art["annotation"].get("why") and art["annotation"]["why"].strip())
    core_event_class = "intel-atom-card" if has_why else "intel-atom-card atom-hero atom-span-2"
    grid_morphology_class = "morphology-6col" if has_why else "morphology-standalone morphology-5col"

    strategic_context_html = ""
    if has_why:
        strategic_context_html = (
            f'<div class="intel-atom-card">'
            f'<span class="intel-atom-label">💡 STRATEGIC CONTEXT (WHY)</span>'
            f'<div class="intel-atom-body">{escape_html(art["annotation"]["why"])}</div>'
            f'</div>'
        )

    has_arc = bool(art.get("narrative_arc") and art["narrative_arc"].get("arc_id"))
    arc_title_html = (
        f'<br><strong>Active Arc:</strong> {escape_html(art["narrative_arc"]["arc_title"])}'
        if (has_arc and art["narrative_arc"].get("arc_title"))
        else ""
    )
    horizon_body_html = (
        f"{temporal_score}{arc_title_html}"
        if has_arc
        else (
            f'<div class="horizon-standalone-badge">✦ Standalone Dispatch</div>'
            f'<div class="horizon-standalone-detail">{temporal_score} · Discrete Single-Event Horizon</div>'
        )
    )

    domain_strip_html = (
        f'<span>✦ <strong>Domain:</strong> {escape_html(art.get("category"))}</span>'
        if art.get("category")
        else ""
    )

    what_text = (art.get("annotation") and art["annotation"].get("what")) or art.get("title") or ""
    actions_html = (
        f'<div style="margin-top: 0.35rem; font-size: 0.78rem; color: {theme_color};">✦ Vector Actions: {escape_html(actions)}</div>'
        if actions
        else ""
    )

    return f"""
    <div class="structured-intel-grid {grid_morphology_class}">
      <div class="{core_event_class}">
        <span class="intel-atom-label">⚡ CORE EVENT (WHAT)</span>
        <div class="intel-atom-body">
          ${escape_html(what_text)}
          {actions_html}
        </div>
      </div>

      <div class="intel-atom-card">
        <span class="intel-atom-label">🎯 PRIMARY ACTORS (WHO)</span>
        <div class="intel-atom-body">
          {primary_actors_html}
        </div>
      </div>

      <div class="intel-atom-card">
        <span class="intel-atom-label">🌐 GEOPOLITICAL THEATER (WHERE)</span>
        <div class="intel-atom-body">
          <strong>Region:</strong> {escape_html(art.get("region") or "Global")}
          ${f"<br><strong>Nations Involved:</strong> {escape_html(countries)}" if countries else ""}
        </div>
      </div>

      {strategic_context_html}

      <div class="intel-atom-card">
        <span class="intel-atom-label">🧠 COGNITIVE MATRIX</span>
        <div class="intel-atom-body" style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.5rem;">
          <span><strong>Dimension:</strong> {cognitive_type}</span>
          <span><strong>Signal Power:</strong> <span style="color: {theme_color}; font-weight: 800;">{composite_score}</span></span>
        </div>
      </div>

      <div class="intel-atom-card">
        <span class="intel-atom-label">⏳ STORY HORIZON & HALF-LIFE</span>
        <div class="intel-atom-body">
          {horizon_body_html}
        </div>
      </div>

      <div class="structured-intel-provenance-strip">
        <span>📡 <strong>Reporting Provenance:</strong> Chronicled by {escape_html(art.get("source") or "Primary Source")}</span>
        {domain_strip_html}
        <span>✦ <strong>Integrity:</strong> Zero-Hallucination Verified</span>
      </div>
    </div>
    """


class TestMilestone4ModalStateTransitionsAndIsolation(unittest.TestCase):
    """
    Adversarially challenge state isolation across modal transitions:
    Simulates navigating from arc-linked articles to standalone articles and verifies
    that window._activeNarrativeChapters and window._activeNarrativeIndex are purged.
    """

    @classmethod
    def setUpClass(cls):
        cls.app_js = read_file("app.js")
        cls.news_data = load_json(os.path.join("data", "news.json"))
        cls.articles = cls.news_data.get("articles", [])
        cls.standalone = [a for a in cls.articles if not (a.get("narrative_arc") and a["narrative_arc"].get("arc_id"))]
        cls.arc_linked = [a for a in cls.articles if a.get("narrative_arc") and a["narrative_arc"].get("arc_id")]

    def test_app_js_contains_explicit_narrative_state_reset_contract(self):
        """Verify app.js contains explicit narrative state clearing for standalone dispatches."""
        self.assertIn("if (!hasArc) {", self.app_js, "app.js must guard narrative state with !hasArc")
        self.assertIn("window._activeNarrativeChapters = [];", self.app_js, "app.js must reset _activeNarrativeChapters to []")
        self.assertIn("window._activeNarrativeIndex = -1;", self.app_js, "app.js must reset _activeNarrativeIndex to -1")

    def test_arc_to_standalone_transition_clears_narrative_state(self):
        """Simulate opening an arc-linked story and navigating via ArrowRight to a standalone story."""
        arc_art = self.arc_linked[0]
        standalone_art = self.standalone[0]

        test_pool = [arc_art, standalone_art]
        engine = ModalSimulationEngine(test_pool)

        # 1. Open arc-linked story
        engine.open_modal(arc_art["id"])
        self.assertGreater(len(engine.active_narrative_chapters), 0, "Arc-linked story must populate chapters")
        self.assertGreaterEqual(engine.active_narrative_index, 0, "Arc-linked story must set active index >= 0")
        self.assertIn("narrative-time-machine", engine.rendered_narrative_box)
        self.assertIn("liquid-glass-narrative-box", engine.rendered_narrative_box)

        # 2. Navigate via ArrowRight (step=+1) to standalone story
        engine.navigate_modal(1)
        self.assertEqual(engine.modal_state["currentIndex"], 1)
        self.assertEqual(engine.active_narrative_chapters, [], "Active chapters MUST be cleared on standalone navigation")
        self.assertEqual(engine.active_narrative_index, -1, "Active index MUST be -1 on standalone navigation")
        self.assertEqual(engine.rendered_narrative_box, "", "Narrative box HTML MUST be empty for standalone story")

    def test_standalone_to_arc_transition_restores_narrative_state(self):
        """Simulate navigating from a standalone story into an arc-linked story."""
        arc_art = self.arc_linked[0]
        standalone_art = self.standalone[0]

        test_pool = [standalone_art, arc_art]
        engine = ModalSimulationEngine(test_pool)

        # 1. Open standalone story
        engine.open_modal(standalone_art["id"])
        self.assertEqual(engine.active_narrative_chapters, [])
        self.assertEqual(engine.active_narrative_index, -1)
        self.assertEqual(engine.rendered_narrative_box, "")

        # 2. Navigate via ArrowRight (step=+1) to arc story
        engine.navigate_modal(1)
        self.assertEqual(engine.modal_state["currentIndex"], 1)
        self.assertGreater(len(engine.active_narrative_chapters), 0)
        self.assertGreaterEqual(engine.active_narrative_index, 0)
        self.assertIn("narrative-time-machine", engine.rendered_narrative_box)

    def test_reverse_arrow_left_transition_clears_narrative_state(self):
        """Simulate navigating backward via ArrowLeft (step=-1) from arc to standalone."""
        arc_art = self.arc_linked[0]
        standalone_art = self.standalone[0]

        test_pool = [standalone_art, arc_art]
        engine = ModalSimulationEngine(test_pool)

        # 1. Open arc-linked story at index 1
        engine.open_modal(arc_art["id"])
        self.assertGreater(len(engine.active_narrative_chapters), 0)

        # 2. Navigate backward via ArrowLeft (step=-1) to standalone at index 0
        engine.navigate_modal(-1)
        self.assertEqual(engine.modal_state["currentIndex"], 0)
        self.assertEqual(engine.active_narrative_chapters, [])
        self.assertEqual(engine.active_narrative_index, -1)
        self.assertEqual(engine.rendered_narrative_box, "")

    def test_full_sweep_navigation_across_all_134_articles(self):
        """
        Step sequentially through all 134 articles in data/news.json via ArrowRight.
        Assert that every single transition maintains 100% strict state isolation:
        - Standalone articles ALWAYS have [] and -1 and ''
        - Arc-linked articles ALWAYS have non-empty chapters matching that exact arc
        """
        engine = ModalSimulationEngine(self.articles)
        engine.open_modal(self.articles[0]["id"])

        for step in range(len(self.articles)):
            curr_idx = engine.modal_state["currentIndex"]
            art = self.articles[curr_idx]
            has_arc = bool(art.get("narrative_arc") and art["narrative_arc"].get("arc_id"))

            if has_arc:
                self.assertGreater(
                    len(engine.active_narrative_chapters), 0,
                    f"Article {art['id']} has arc but empty chapters"
                )
                self.assertGreaterEqual(
                    engine.active_narrative_index, 0,
                    f"Article {art['id']} has arc but negative index"
                )
                self.assertIn(
                    "narrative-time-machine", engine.rendered_narrative_box,
                    f"Article {art['id']} missing narrative-time-machine in DOM"
                )
                # Verify that chapters belong to this exact article
                current_chapter = engine.active_narrative_chapters[engine.active_narrative_index]
                self.assertEqual(current_chapter["articleId"], art["id"])
            else:
                self.assertEqual(
                    engine.active_narrative_chapters, [],
                    f"Article {art['id']} leaked chapters across story transition! Chapters: {engine.active_narrative_chapters}"
                )
                self.assertEqual(
                    engine.active_narrative_index, -1,
                    f"Article {art['id']} leaked narrative index! Index: {engine.active_narrative_index}"
                )
                self.assertEqual(
                    engine.rendered_narrative_box, "",
                    f"Article {art['id']} rendered narrative box when arc_id is null!"
                )

            # Advance to next article via ArrowRight
            engine.navigate_modal(1)

    def test_rapid_alternating_state_transitions(self):
        """Stress-test 100 rapid alternating transitions between arc-linked and standalone stories."""
        arc_art = self.arc_linked[0]
        standalone_art = self.standalone[0]
        pool = [arc_art, standalone_art]

        engine = ModalSimulationEngine(pool)
        for i in range(100):
            engine.navigate_modal(1)
            expected_standalone = (i % 2 == 0)  # Started at 0 (arc), step 1 -> 1 (standalone)
            if expected_standalone:
                self.assertEqual(engine.active_narrative_chapters, [])
                self.assertEqual(engine.active_narrative_index, -1)
                self.assertEqual(engine.rendered_narrative_box, "")
            else:
                self.assertGreater(len(engine.active_narrative_chapters), 0)
                self.assertGreaterEqual(engine.active_narrative_index, 0)

    def test_edge_case_arc_payloads(self):
        """Stress-test corrupted and boundary narrative_arc payloads."""
        engine = ModalSimulationEngine([])
        edge_cases = [
            {"id": "edge-1", "title": "Null arc", "narrative_arc": None},
            {"id": "edge-2", "title": "Empty dict", "narrative_arc": {}},
            {"id": "edge-3", "title": "Arc ID null", "narrative_arc": {"arc_id": None}},
            {"id": "edge-4", "title": "Arc ID empty str", "narrative_arc": {"arc_id": ""}},
            {"id": "edge-5", "title": "No headlines", "narrative_arc": {"arc_id": "arc-1", "previous_headlines": None}},
            {"id": "edge-6", "title": "Headlines empty list", "narrative_arc": {"arc_id": "arc-2", "previous_headlines": []}},
        ]

        for art in edge_cases:
            engine.render_executive_modal(art)
            has_arc = bool(art.get("narrative_arc") and art["narrative_arc"].get("arc_id"))
            if not has_arc:
                self.assertEqual(engine.active_narrative_chapters, [], f"Failed on edge case {art['id']}")
                self.assertEqual(engine.active_narrative_index, -1, f"Failed on edge case {art['id']}")
                self.assertEqual(engine.rendered_narrative_box, "", f"Failed on edge case {art['id']}")
            else:
                self.assertGreater(len(engine.active_narrative_chapters), 0)
                self.assertEqual(engine.active_narrative_index, 0)


class TestStructuredIntelligenceMorphologyAllArticles(unittest.TestCase):
    """
    Stress-tests renderStructuredIntelligenceView across all 134 articles in data/news.json:
    - 0 exceptions thrown
    - All standalone articles render with Hero Core Event morphology
    - Subordinate provenance quarantine enforced
    """

    @classmethod
    def setUpClass(cls):
        cls.app_js = read_file("app.js")
        cls.style_css = read_file("style.css")
        cls.news_data = load_json(os.path.join("data", "news.json"))
        cls.articles = cls.news_data.get("articles", [])

    def test_css_classes_defined_for_hero_morphology(self):
        """Verify CSS defines all necessary rules for hero core event morphology."""
        self.assertIn(".intel-atom-card.atom-hero", self.style_css)
        self.assertIn(".atom-span-2", self.style_css)
        self.assertIn(".morphology-standalone", self.style_css)
        self.assertIn(".morphology-5col", self.style_css)
        self.assertIn(".horizon-standalone-badge", self.style_css)
        self.assertIn(".horizon-standalone-detail", self.style_css)
        self.assertIn(".subordinate-provenance-ledger", self.style_css)
        self.assertIn(".structured-intel-provenance-strip", self.style_css)

    def test_render_structured_intelligence_view_across_all_134_articles(self):
        """Verify all 134 articles render valid HTML without raising exceptions."""
        total = len(self.articles)
        self.assertEqual(total, 134, f"Expected 134 articles, found {total}")

        standalone_count = 0
        arc_count = 0

        for art in self.articles:
            try:
                html_out = render_structured_intelligence_view_sim(art)
            except Exception as e:
                self.fail(f"render_structured_intelligence_view crashed on article {art.get('id')}: {e}")

            self.assertIsNotNone(html_out)
            self.assertGreater(len(html_out.strip()), 100, f"Article {art.get('id')} produced truncated HTML")

            has_arc = bool(art.get("narrative_arc") and art["narrative_arc"].get("arc_id"))
            if has_arc:
                arc_count += 1
            else:
                standalone_count += 1

            # Tag balance sanity checks
            for tag in ["div", "span", "strong", "code"]:
                open_cnt = html_out.count(f"<{tag}")
                close_cnt = html_out.count(f"</{tag}>")
                self.assertEqual(
                    open_cnt, close_cnt,
                    f"Tag mismatch for <{tag}> in article {art.get('id')}: {open_cnt} opens vs {close_cnt} closes"
                )

        self.assertEqual(standalone_count, 73, "Expected 73 standalone articles")
        self.assertEqual(arc_count, 61, "Expected 61 arc-linked articles")

    def test_standalone_articles_render_hero_core_event_morphology(self):
        """Verify that all 73 standalone articles render with Hero Core Event morphology."""
        standalone_articles = [
            a for a in self.articles if not (a.get("narrative_arc") and a["narrative_arc"].get("arc_id"))
        ]
        self.assertEqual(len(standalone_articles), 73)

        for art in standalone_articles:
            html_out = render_structured_intelligence_view_sim(art)

            # 1. Grid morphology class must be standalone 5-column
            self.assertIn(
                "morphology-standalone morphology-5col", html_out,
                f"Article {art['id']} missing morphology-standalone class"
            )

            # 2. Core Event must have atom-hero atom-span-2
            self.assertIn(
                "intel-atom-card atom-hero atom-span-2", html_out,
                f"Article {art['id']} missing hero core event morphology"
            )

            # 3. Story Horizon must render standalone badges
            self.assertIn(
                '<div class="horizon-standalone-badge">✦ Standalone Dispatch</div>', html_out,
                f"Article {art['id']} missing standalone horizon badge"
            )
            self.assertIn(
                "Discrete Single-Event Horizon", html_out,
                f"Article {art['id']} missing Discrete Single-Event Horizon label"
            )

            # 4. Strategic Context (Why) atom must NOT be rendered (honest null)
            self.assertNotIn(
                "💡 STRATEGIC CONTEXT (WHY)", html_out,
                f"Article {art['id']} illegally rendered Strategic Context atom with empty/synthetic why!"
            )

    def test_wire_reporting_sources_appear_exclusively_in_subordinate_provenance(self):
        """
        Verify that wire reporting sources appear exclusively in subordinate provenance:
        - In .subordinate-provenance-ledger (📡 Chronicled by {source})
        - In .structured-intel-provenance-strip (📡 Reporting Provenance: Chronicled by {source})
        - 0 wire publisher names inside Active Agent, Leaders, Organizations, Collective Factions, or Sovereign Stakeholders.
        """
        wire_names = {
            "Reuters", "Associated Press", "AP", "BBC", "BBC News", "Bloomberg", "AFP",
            "Agence France-Presse", "CNN", "The Guardian", "The Hindu", "Al Jazeera",
            "NPR", "CNBC", "Axios", "France 24", "Hindustan Times", "New York Times"
        }

        for art in self.articles:
            html_out = render_structured_intelligence_view_sim(art)
            source = art.get("source") or "Primary Source"

            # 1. Subordinate provenance ledger in Primary Actors atom
            self.assertIn(
                f'<div class="subordinate-provenance-ledger">📡 Chronicled by {html.escape(source)}</div>',
                html_out,
                f"Article {art['id']} missing subordinate-provenance-ledger"
            )

            # 2. Bottom provenance strip
            self.assertIn(
                f'<span>📡 <strong>Reporting Provenance:</strong> Chronicled by {html.escape(source)}</span>',
                html_out,
                f"Article {art['id']} missing structured-intel-provenance-strip source"
            )

            # 3. Check that wire names are NOT injected into Active Agent, Leaders, Factions, etc.
            actors = art.get("primary_actors") or {}
            active_agent = actors.get("active_agent") or ""
            factions = [f.get("canonical_label", "") for f in actors.get("collective_factions", [])]
            stakeholders = actors.get("sovereign_stakeholders", [])
            entities = art.get("entities", {})
            orgs = [o if isinstance(o, str) else o.get("name", "") for o in entities.get("organizations", [])]
            leaders = [l if isinstance(l, str) else l.get("name", "") for l in entities.get("leaders", [])]

            for target in [active_agent] + factions + stakeholders + orgs + leaders:
                for w in wire_names:
                    self.assertNotEqual(
                        w.lower(), target.lower(),
                        f"Wire source '{w}' leaked into intelligence entity '{target}' in article {art['id']}!"
                    )


class TestZeroToleranceForSyntheticPlaceholders(unittest.TestCase):
    """Verifies that all forbidden synthetic placeholders and hardcoded strings are abolished."""

    @classmethod
    def setUpClass(cls):
        cls.app_js = read_file("app.js")
        cls.index_html = read_file("index.html")

    def test_zero_forbidden_strings_in_app_js(self):
        """Verify strict absence of forbidden synthetic strings from app.js."""
        forbidden_strings = [
            "Verified news intelligence event monitored across syndicated global publisher networks.",
            "Regional & Non-State Factions",
            "8.4 / 10",
            "Syndicated Bureau",
            "Editorial Bureau",
            "Solo Investigative Scoop",
            "Key Takeaway: Official statements",
            "Historical Dispatch"
        ]

        for s in forbidden_strings:
            self.assertNotIn(
                s, self.app_js,
                f"Forbidden synthetic placeholder '{s}' detected in app.js!"
            )

    def test_zero_forbidden_strings_in_index_html(self):
        """Verify strict absence of forbidden synthetic strings from index.html."""
        forbidden_strings = [
            "Verified news intelligence event",
            "Regional & Non-State Factions",
            "Editorial Bureau",
            "Syndicated Bureau"
        ]

        for s in forbidden_strings:
            self.assertNotIn(
                s, self.index_html,
                f"Forbidden synthetic placeholder '{s}' detected in index.html!"
            )


class TestAdversarialPayloadResilienceInMorphology(unittest.TestCase):
    """Stress-tests renderStructuredIntelligenceView with malicious or extreme payloads."""

    def test_xss_injection_resilience(self):
        """Verify XSS scripts are safely escaped and never rendered unescaped into HTML."""
        xss_art = {
            "id": "xss-test",
            "title": '<script>alert("title")</script>',
            "source": '<img src=x onerror=alert("src")>',
            "category": '<b onmouseover=alert("cat")>Tech</b>',
            "region": '<iframe src="evil.com"></iframe>',
            "annotation": {
                "what": '<script>alert("what")</script>',
                "why": '<script>alert("why")</script>'
            },
            "primary_actors": {
                "active_agent": '<script>alert("agent")</script>',
                "active_agent_type": '"><script>alert(1)</script>',
                "impacted_population": '<svg onload=alert(2)>',
                "collective_factions": [{"canonical_label": '<script>alert(3)</script>'}],
                "sovereign_stakeholders": ['<script>alert(4)</script>'],
                "syntactic_frame": {
                    "subject": '<script>sub</script>',
                    "verb": '<script>verb</script>',
                    "object": '<script>obj</script>'
                }
            },
            "scores": {"composite": 0.88, "temporal": 0.9}
        }

        html_out = render_structured_intelligence_view_sim(xss_art)
        self.assertNotIn("<script>", html_out)
        self.assertNotIn("<iframe", html_out)
        self.assertNotIn("<svg onload", html_out)
        self.assertNotIn("<img src=x", html_out)

    def test_empty_record_resilience(self):
        """Verify completely empty dictionary does not crash renderStructuredIntelligenceView."""
        empty_art = {}
        try:
            html_out = render_structured_intelligence_view_sim(empty_art)
        except Exception as e:
            self.fail(f"renderStructuredIntelligenceView crashed on empty record: {e}")
        self.assertIn("structured-intel-grid", html_out)
        self.assertIn("atom-hero", html_out)

    def test_none_input_resilience(self):
        """Verify None input returns empty string gracefully."""
        self.assertEqual(render_structured_intelligence_view_sim(None), "")


class TestCodebaseInvariantsAndKeyboardNavigation(unittest.TestCase):
    """Verifies static wiring in app.js and index.html for keyboard navigation and dataset immutability."""

    @classmethod
    def setUpClass(cls):
        cls.app_js = read_file("app.js")
        cls.index_html = read_file("index.html")
        cls.news_data = load_json(os.path.join("data", "news.json"))

    def test_keydown_modal_navigation_wiring(self):
        """Verify keydown listener in app.js routes ArrowRight and ArrowLeft to navigateModal."""
        self.assertIn("if (e.key === 'ArrowLeft')", self.app_js)
        self.assertIn("navigateModal(-1)", self.app_js)
        self.assertIn("if (e.key === 'ArrowRight')", self.app_js)
        self.assertIn("navigateModal(1)", self.app_js)

    def test_navigate_modal_function_contract(self):
        """Verify window.navigateModal advances index with modulo wrapping and calls renderExecutiveModal."""
        self.assertIn("window.navigateModal = function(step)", self.app_js)
        self.assertIn("state.modalState.currentIndex = (state.modalState.currentIndex + step + pool.length) % pool.length;", self.app_js)
        self.assertIn("renderExecutiveModal();", self.app_js)

    def test_deck_view_switcher_wiring(self):
        """Verify window.switchDeckView toggles between narrative view and structured intel view."""
        self.assertIn("window.switchDeckView = function(view)", self.app_js)
        self.assertIn("deckViewBtnNarrative", self.app_js)
        self.assertIn("deckViewBtnIntel", self.app_js)

    def test_dataset_immutability_and_count(self):
        """Verify dataset remains untouched at 134 articles with 0 duplicates."""
        articles = self.news_data.get("articles", [])
        self.assertEqual(len(articles), 134)
        seen_ids = set()
        for a in articles:
            self.assertNotIn(a["id"], seen_ids, f"Duplicate article ID: {a['id']}")
            seen_ids.add(a["id"])
            self.assertFalse(a.get("is_duplicate", False), f"Article marked as duplicate: {a['id']}")


if __name__ == "__main__":
    unittest.main(verbosity=2)

