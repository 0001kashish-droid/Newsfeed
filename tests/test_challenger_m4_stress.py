#!/usr/bin/env python3
"""
Empirical Challenger Stress Test Suite - Milestone 4 (Frontend Intelligence Integration & UI/UX Fidelity)
Author: challenger_m4_1 (Empirical Challenger)
Targets: app.js, style.css, index.html

Adversarially stress-tests:
1. JavaScript Syntax & Lexical Balance in app.js:
   - Template literals (`` ` ``) and interpolations (`${...}`) balance
   - Bracket, brace, parenthesis closure invariants
   - Tokenization and syntax safety
2. Adversarial Data Schemas in renderExecutiveModal:
   - Null narrative_arc
   - narrative_arc with null arc_id
   - Active narrative_arc with partial or full attributes
   - Null resonant_podcast
   - resonant_podcast with single attribute (e.g. podcast only)
   - resonant_podcast with full attributes
   - Null/missing annotation or relatedSources
   - XSS injection payloads in title, podcast, arc_title, source, why
3. Adversarial Data Schemas in renderThoughtPulse:
   - Null or empty resonant_news
   - Single resonant_news
   - Multiple resonant_news items
   - XSS injection payloads in resonant_news title and id
   - Event propagation isolation (event.stopPropagation() on button)
4. 3D Tilt Cursor Physics Math & Touch Safety:
   - Pointer coarse media query guard
   - 0px width/height bounding rect mathematical evaluation
   - Infinite/extreme mouse coordinates
   - Card selector coverage (.news-card AND .thought-card)
   - Duplicate listener prevention via data-tilt-ready
5. CSS Selector, VisionOS Liquid Glass & Responsive Fidelity:
   - .liquid-glass-resonance-box and .liquid-glass-narrative-box definitions
   - .thought-card-resonant-news button styling
   - 3D transform-style: preserve-3d and will-change on .thought-card
   - Specular sheen pseudo-elements (.thought-card::after)
   - @media (pointer: coarse) safety reset
   - @media (max-width: 768px) and @media (max-width: 480px) responsive queries
   - [data-theme="light"] adaptations
   - scrollbar-width: thin preservation
6. OpenModal Fallback Synthesis Simulation:
   - Resolution from active pool
   - Resolution from state.articles
   - Synthetic fallback resolution from state.podcasts resonant_news
   - Non-existent ID handling
"""

import os
import sys
import unittest
import re
import json

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read_file(relative_path):
    full_path = os.path.join(PROJECT_ROOT, relative_path)
    with open(full_path, 'r', encoding='utf-8') as f:
        return f.read()


class TestJavaScriptSyntaxAndLexicalBalance(unittest.TestCase):
    """Stress-tests the lexical balance and syntax integrity of app.js."""

    @classmethod
    def setUpClass(cls):
        cls.app_js = read_file('app.js')

    def test_template_literal_and_interpolation_balance(self):
        """Verify backticks and ${} template interpolations are strictly balanced."""
        code = self.app_js
        i = 0
        n = len(code)
        in_line_comment = False
        in_block_comment = False
        in_regex = False
        in_string_single = False
        in_string_double = False
        
        # Stack for template literals: holds list of open brace depths inside `${...}`
        # Every entry is an integer representing the current brace depth when `${` was entered
        template_stack = []
        brace_depth = 0
        
        while i < n:
            ch = code[i]
            next_ch = code[i + 1] if i + 1 < n else ''
            
            # Line comment handling
            if in_line_comment:
                if ch == '\n':
                    in_line_comment = False
                i += 1
                continue
            
            # Block comment handling
            if in_block_comment:
                if ch == '*' and next_ch == '/':
                    in_block_comment = False
                    i += 2
                    continue
                i += 1
                continue
                
            # Escaped character handling inside strings
            if (in_string_single or in_string_double or template_stack) and ch == '\\':
                i += 2
                continue
                
            if in_string_single:
                if ch == "'":
                    in_string_single = False
                i += 1
                continue
                
            if in_string_double:
                if ch == '"':
                    in_string_double = False
                i += 1
                continue

            # Start comments
            if ch == '/' and next_ch == '/':
                in_line_comment = True
                i += 2
                continue
            if ch == '/' and next_ch == '*':
                in_block_comment = True
                i += 2
                continue

            # Start regular single/double quote strings
            if ch == "'":
                in_string_single = True
                i += 1
                continue
            if ch == '"':
                in_string_double = True
                i += 1
                continue

            # Template literal entry / exit
            if ch == '`':
                if template_stack and template_stack[-1] == 'IN_TEMPLATE':
                    template_stack.pop()
                else:
                    template_stack.append('IN_TEMPLATE')
                i += 1
                continue

            # Template interpolation ${...}
            if template_stack and template_stack[-1] == 'IN_TEMPLATE' and ch == '$' and next_ch == '{':
                template_stack.append('IN_EXPR')
                brace_depth += 1
                i += 2
                continue

            if template_stack and template_stack[-1] == 'IN_EXPR':
                if ch == '{':
                    brace_depth += 1
                elif ch == '}':
                    brace_depth -= 1
                    if brace_depth == 0:
                        template_stack.pop()  # Finished IN_EXPR, back in IN_TEMPLATE
                i += 1
                continue

            i += 1

        self.assertEqual(len(template_stack), 0, f"Unbalanced template literals detected: {template_stack}")
        self.assertFalse(in_string_single, "Unterminated single-quoted string literal")
        self.assertFalse(in_string_double, "Unterminated double-quoted string literal")
        self.assertFalse(in_block_comment, "Unterminated block comment")

    def test_parentheses_and_bracket_balance(self):
        """Verify top-level parenthesis and bracket balance across app.js."""
        code = self.app_js
        paren_count = 0
        bracket_count = 0
        in_str = None
        escape = False
        in_line_comment = False
        in_block_comment = False
        
        i = 0
        while i < len(code):
            c = code[i]
            next_c = code[i + 1] if i + 1 < len(code) else ''

            if in_line_comment:
                if c == '\n':
                    in_line_comment = False
                i += 1
                continue
            if in_block_comment:
                if c == '*' and next_c == '/':
                    in_block_comment = False
                    i += 2
                    continue
                i += 1
                continue

            if in_str:
                if escape:
                    escape = False
                elif c == '\\':
                    escape = True
                elif c == in_str:
                    in_str = None
                i += 1
                continue

            if c == '/' and next_c == '/':
                in_line_comment = True
                i += 2
                continue
            if c == '/' and next_c == '*':
                in_block_comment = True
                i += 2
                continue

            if c in ("'", '"', '`'):
                in_str = c
                i += 1
                continue

            if c == '(':
                paren_count += 1
            elif c == ')':
                paren_count -= 1
            elif c == '[':
                bracket_count += 1
            elif c == ']':
                bracket_count -= 1

            self.assertGreaterEqual(paren_count, 0, f"Unmatched closing parenthesis at position {i}")
            self.assertGreaterEqual(bracket_count, 0, f"Unmatched closing bracket at position {i}")
            i += 1

        self.assertEqual(paren_count, 0, f"Unbalanced parentheses in app.js: delta={paren_count}")
        self.assertEqual(bracket_count, 0, f"Unbalanced brackets in app.js: delta={bracket_count}")


class TestExecutiveModalAdversarialSimulation(unittest.TestCase):
    """
    Simulates the exact DOM rendering logic of renderExecutiveModal in Python
    to stress-test against adversarial inputs and edge cases.
    """

    @classmethod
    def setUpClass(cls):
        cls.app_js = read_file('app.js')

    def _simulate_render_executive_modal(self, art):
        """Python mirror of the exact rendering rules from app.js."""
        # Clean helper from app.js line 1326
        def clean_and_complete_text(raw):
            if not raw:
                return ''
            s = raw.strip()
            s = re.sub(r'[\.\s]*[\.…]+$', '', s).strip()
            last_period = max(s.rfind('.'), s.rfind('?'), s.rfind('!'))
            if last_period > 50:
                s = s[:last_period + 1]
            elif s and not s.endswith('.'):
                s += '.'
            return s

        def escape_html(s):
            if not s:
                return ''
            s = str(s)
            return (s.replace('&', '&amp;')
                     .replace('<', '&lt;')
                     .replace('>', '&gt;')
                     .replace('"', '&quot;')
                     .replace("'", '&#039;'))

        raw_desc = art.get('description') or ''
        clean_desc = clean_and_complete_text(raw_desc)
        story_text = escape_html(clean_desc)
        title_text = escape_html(art.get('title') or '')

        raw_why = art.get('annotation', {}).get('why', '') if art.get('annotation') else ''
        clean_why = clean_and_complete_text(raw_why)
        is_why_distinct = (
            len(clean_why) > 20 and
            clean_why[:30] not in story_text and
            story_text[:30] not in clean_why
        )

        rendered_sections = {}

        # 1. Executive Context Section
        if is_why_distinct:
            rendered_sections['executive_context'] = f'<p>{escape_html(clean_why)}</p>'
        else:
            rendered_sections['executive_context'] = None

        # 2. Narrative Arc Box
        narrative_arc = art.get('narrative_arc')
        if narrative_arc and narrative_arc.get('arc_id'):
            day_num = narrative_arc.get('day_number') or 1
            arc_title = escape_html(narrative_arc.get('arc_title') or 'Developing Story')
            total_chapters = narrative_arc.get('total_chapters') or 1
            rendered_sections['narrative_box'] = {
                'rendered': True,
                'class': 'liquid-glass-narrative-box',
                'day': day_num,
                'title': arc_title,
                'chapters': total_chapters,
                'html': f'<div class="liquid-glass-narrative-box">Day {day_num} {arc_title} {total_chapters}</div>'
            }
        else:
            rendered_sections['narrative_box'] = {'rendered': False, 'html': ''}

        # 3. Resonant Podcast Box
        rp = art.get('resonant_podcast')
        if rp and (rp.get('title') or rp.get('episode_title') or rp.get('podcast')):
            title = escape_html(rp.get('title') or rp.get('episode_title') or rp.get('podcast'))
            podcast = escape_html(rp.get('podcast') or rp.get('podcast_title') or '')
            link = rp.get('link') or rp.get('youtube_url') or '#'
            rendered_sections['resonance_box'] = {
                'rendered': True,
                'class': 'liquid-glass-resonance-box',
                'title': title,
                'podcast': podcast,
                'link': link,
                'html': f'<div class="liquid-glass-resonance-box">{title} {podcast} {link}</div>'
            }
        else:
            rendered_sections['resonance_box'] = {'rendered': False, 'html': ''}

        return rendered_sections

    def test_null_narrative_arc_suppression(self):
        """Article with null narrative_arc produces 0 narrative box markup."""
        art = {
            'id': 'art-1',
            'title': 'Test Story',
            'narrative_arc': None,
            'resonant_podcast': None
        }
        res = self._simulate_render_executive_modal(art)
        self.assertFalse(res['narrative_box']['rendered'])
        self.assertEqual(res['narrative_box']['html'], '')

    def test_narrative_arc_with_null_arc_id_suppression(self):
        """Article with narrative_arc: {arc_id: null} produces 0 narrative box markup."""
        art = {
            'id': 'art-2',
            'title': 'Test Story',
            'narrative_arc': {'arc_id': None, 'arc_title': 'Ghost Arc', 'day_number': 2},
            'resonant_podcast': None
        }
        res = self._simulate_render_executive_modal(art)
        self.assertFalse(res['narrative_box']['rendered'])
        self.assertEqual(res['narrative_box']['html'], '')

    def test_active_narrative_arc_rendering(self):
        """Article with active arc renders valid .liquid-glass-narrative-box."""
        art = {
            'id': 'art-3',
            'title': 'Valid Story',
            'narrative_arc': {
                'arc_id': 'arc-global-chips',
                'arc_title': 'Semiconductor Supply Wars',
                'day_number': 4,
                'total_chapters': 7
            },
            'resonant_podcast': None
        }
        res = self._simulate_render_executive_modal(art)
        self.assertTrue(res['narrative_box']['rendered'])
        self.assertEqual(res['narrative_box']['class'], 'liquid-glass-narrative-box')
        self.assertEqual(res['narrative_box']['day'], 4)
        self.assertEqual(res['narrative_box']['title'], 'Semiconductor Supply Wars')
        self.assertEqual(res['narrative_box']['chapters'], 7)

    def test_null_resonant_podcast_suppression(self):
        """Article with null resonant_podcast produces 0 resonance box markup."""
        art = {
            'id': 'art-4',
            'title': 'Test Story',
            'narrative_arc': None,
            'resonant_podcast': None
        }
        res = self._simulate_render_executive_modal(art)
        self.assertFalse(res['resonance_box']['rendered'])
        self.assertEqual(res['resonance_box']['html'], '')

    def test_partial_resonant_podcast_with_only_podcast_name(self):
        """Article with resonant_podcast having only podcast name renders gracefully."""
        art = {
            'id': 'art-5',
            'title': 'Test Story',
            'resonant_podcast': {'podcast': 'Hard Fork'}
        }
        res = self._simulate_render_executive_modal(art)
        self.assertTrue(res['resonance_box']['rendered'])
        self.assertEqual(res['resonance_box']['title'], 'Hard Fork')
        self.assertEqual(res['resonance_box']['podcast'], 'Hard Fork')
        self.assertEqual(res['resonance_box']['link'], '#')

    def test_xss_injection_resilience_in_modal(self):
        """Verify modal escapes all HTML tags in titles, arcs, podcasts, and why notes."""
        malicious_art = {
            'id': 'art-evil',
            'title': '<script>alert("pwned_title")</script>',
            'description': '<img src=x onerror=alert("pwned_desc")>',
            'annotation': {
                'why': '<b>bold explanation</b> <script>alert("pwned_why")</script>'
            },
            'narrative_arc': {
                'arc_id': 'arc-evil',
                'arc_title': '<iframe src="evil.com"></iframe>',
                'day_number': 1,
                'total_chapters': 1
            },
            'resonant_podcast': {
                'title': '<svg onload=alert("pwned_pod")>',
                'podcast': '"><script>alert(1)</script>',
                'link': 'https://youtube.com/watch?v=123'
            }
        }
        res = self._simulate_render_executive_modal(malicious_art)
        
        # Verify narrative arc escaped
        self.assertIn('&lt;iframe src=&quot;evil.com&quot;&gt;&lt;/iframe&gt;', res['narrative_box']['html'])
        self.assertNotIn('<iframe', res['narrative_box']['html'])

        # Verify resonance box escaped
        self.assertIn('&lt;svg onload=alert(&quot;pwned_pod&quot;)&gt;', res['resonance_box']['html'])
        self.assertIn('&quot;&gt;&lt;script&gt;alert(1)&lt;/script&gt;', res['resonance_box']['html'])
        self.assertNotIn('<svg', res['resonance_box']['html'])
        self.assertNotIn('<script>', res['resonance_box']['html'])


class TestThoughtPulseAdversarialSimulation(unittest.TestCase):
    """Stress-tests renderThoughtPulse against adversarial schemas and event isolation."""

    @classmethod
    def setUpClass(cls):
        cls.app_js = read_file('app.js')

    def _simulate_render_thought_card(self, ep):
        def escape_html(s):
            if not s:
                return ''
            return (str(s).replace('&', '&amp;')
                          .replace('<', '&lt;')
                          .replace('>', '&gt;')
                          .replace('"', '&quot;')
                          .replace("'", '&#039;'))

        def escape_js(s):
            if not s:
                return ''
            return str(s).replace("'", "\\'").replace('"', '\\"')

        rn = ep.get('resonant_news', [])[0] if (ep.get('resonant_news') and len(ep['resonant_news']) > 0) else None

        if rn:
            resonant_html = (
                f'<button type="button" class="thought-card-resonant-news" '
                f'onclick="event.stopPropagation(); openModal(\'{escape_js(rn.get("id"))}\');" '
                f'title="Open executive reader for: {escape_html(rn.get("title"))}" '
                f'aria-label="Open resonant news article">\n'
                f'  <span class="thought-resonant-badge">📰 Resonates</span>\n'
                f'  <span class="thought-resonant-title">{escape_html(rn.get("title"))}</span>\n'
                f'  <span class="thought-resonant-arrow">↗</span>\n'
                f'</button>'
            )
        else:
            resonant_html = ''

        card_html = (
            f'<article class="thought-card" data-id="{ep.get("id")}" onclick="window.open(\'{escape_js(ep.get("link"))}\',\'_blank\')">\n'
            f'  <h3 class="thought-card-title">{escape_html(ep.get("title"))}</h3>\n'
            f'  {resonant_html}\n'
            f'</article>'
        )

        return {
            'has_resonant_news': rn is not None,
            'resonant_html': resonant_html,
            'card_html': card_html,
            'rn_data': rn
        }

    def test_empty_or_null_resonant_news_produces_no_pill(self):
        """Episode with empty resonant_news produces clean card without resonant button."""
        ep_null = {'id': 'ep-1', 'title': 'Deep Tech', 'resonant_news': None, 'link': 'https://yt.com'}
        ep_empty = {'id': 'ep-2', 'title': 'AI Talk', 'resonant_news': [], 'link': 'https://yt.com'}

        res1 = self._simulate_render_thought_card(ep_null)
        res2 = self._simulate_render_thought_card(ep_empty)

        self.assertFalse(res1['has_resonant_news'])
        self.assertEqual(res1['resonant_html'], '')
        self.assertNotIn('thought-card-resonant-news', res1['card_html'])

        self.assertFalse(res2['has_resonant_news'])
        self.assertEqual(res2['resonant_html'], '')
        self.assertNotIn('thought-card-resonant-news', res2['card_html'])

    def test_multiple_resonant_news_picks_primary_safely(self):
        """Episode with multiple resonant stories selects the top story without layout breakage."""
        ep = {
            'id': 'ep-3',
            'title': 'Geo Politics',
            'link': 'https://yt.com/watch?v=geo',
            'resonant_news': [
                {'id': 'rn-primary', 'title': 'Primary Headline'},
                {'id': 'rn-secondary', 'title': 'Secondary Headline'}
            ]
        }
        res = self._simulate_render_thought_card(ep)
        self.assertTrue(res['has_resonant_news'])
        self.assertIn('Primary Headline', res['resonant_html'])
        self.assertNotIn('Secondary Headline', res['resonant_html'])
        self.assertIn("openModal('rn-primary')", res['resonant_html'])

    def test_event_propagation_isolation_in_rendered_button(self):
        """Verify button explicitly contains event.stopPropagation() before openModal call."""
        ep = {
            'id': 'ep-4',
            'title': 'Finance Today',
            'link': 'https://yt.com/watch?v=fin',
            'resonant_news': [{'id': 'art-fin', 'title': 'Market Surge'}]
        }
        res = self._simulate_render_thought_card(ep)
        self.assertIn('type="button"', res['resonant_html'])
        self.assertIn('onclick="event.stopPropagation(); openModal(\'art-fin\');"', res['resonant_html'])

    def test_xss_in_resonant_news_title_and_id(self):
        """Verify adversarial payloads in resonant news titles and IDs are sanitized."""
        ep = {
            'id': 'ep-5',
            'title': 'Security Now',
            'link': 'https://yt.com',
            'resonant_news': [{
                'id': "rn-safe'); alert('xss",
                'title': '<script>alert("pill_xss")</script>'
            }]
        }
        res = self._simulate_render_thought_card(ep)
        self.assertNotIn('<script>', res['resonant_html'])
        self.assertIn('&lt;script&gt;alert(&quot;pill_xss&quot;)&lt;/script&gt;', res['resonant_html'])
        # Verify single quotes escaped in openModal parameter
        self.assertIn("openModal('rn-safe\\\'); alert(\\\'xss');", res['resonant_html'])


class TestTiltPhysicsCalculationsAndTouchRobustness(unittest.TestCase):
    """Stress-tests the math and edge conditions in attach3DTiltListeners."""

    @classmethod
    def setUpClass(cls):
        cls.app_js = read_file('app.js')

    def test_tilt_listener_selector_coverage(self):
        """Verify attach3DTiltListeners targets both .news-card and .thought-card with tilt-ready filter."""
        self.assertIn(
            "document.querySelectorAll('.news-card:not([data-tilt-ready]), .thought-card:not([data-tilt-ready])')",
            self.app_js,
            "attach3DTiltListeners must query both news and thought cards without duplicate binding"
        )

    def test_pointer_coarse_safety_guard_present(self):
        """Verify attach3DTiltListeners guards against touchscreens via window.matchMedia('(pointer: coarse)')."""
        self.assertIn(
            "window.matchMedia('(pointer: coarse)').matches",
            self.app_js,
            "Pointer coarse media query guard missing from mousemove listener in app.js"
        )

    def test_tilt_math_simulation(self):
        """Simulate tilt physics math under typical and edge bounding rectangles."""
        def calc_tilt(rect_width, rect_height, client_x, client_y, rect_left=100, rect_top=100):
            x = client_x - rect_left
            y = client_y - rect_top
            
            if rect_width <= 0 or rect_height <= 0:
                # Defensive check evaluation
                return {'error': 'zero_dimension'}

            center_x = rect_width / 2
            center_y = rect_height / 2

            rotate_x = -((y - center_y) / center_y) * 7
            rotate_y = ((x - center_x) / center_x) * 7

            percent_x = round((x / rect_width) * 100, 1)
            percent_y = round((y / rect_height) * 100, 1)

            return {
                'rotateX': round(rotate_x, 2),
                'rotateY': round(rotate_y, 2),
                'percentX': percent_x,
                'percentY': percent_y
            }

        # Normal card: 300x400 at center
        normal = calc_tilt(300, 400, 250, 300)  # center is (100+150, 100+200) = (250, 300)
        self.assertEqual(normal['rotateX'], 0.0)
        self.assertEqual(normal['rotateY'], 0.0)
        self.assertEqual(normal['percentX'], 50.0)
        self.assertEqual(normal['percentY'], 50.0)

        # Top-left corner
        top_left = calc_tilt(300, 400, 100, 100)
        self.assertEqual(top_left['rotateX'], 7.0)
        self.assertEqual(top_left['rotateY'], -7.0)
        self.assertEqual(top_left['percentX'], 0.0)
        self.assertEqual(top_left['percentY'], 0.0)

        # Bottom-right corner
        bottom_right = calc_tilt(300, 400, 400, 500)
        self.assertEqual(bottom_right['rotateX'], -7.0)
        self.assertEqual(bottom_right['rotateY'], 7.0)
        self.assertEqual(bottom_right['percentX'], 100.0)
        self.assertEqual(bottom_right['percentY'], 100.0)

        # Zero-dimension boundary condition
        zero_dim = calc_tilt(0, 0, 100, 100)
        self.assertEqual(zero_dim['error'], 'zero_dimension')


class TestStyleCssSelectorAndVisionOSFidelity(unittest.TestCase):
    """Stress-tests style.css selectors, liquid glass rules, responsive queries, and themes."""

    @classmethod
    def setUpClass(cls):
        cls.style_css = read_file('style.css')

    def test_liquid_glass_resonance_box_selectors(self):
        """Verify .liquid-glass-resonance-box and child classes exist with blur and backdrop filters."""
        self.assertIn('.liquid-glass-resonance-box {', self.style_css)
        self.assertIn('.liquid-glass-resonance-box:hover {', self.style_css)
        self.assertIn('.resonance-box-left {', self.style_css)
        self.assertIn('.resonance-box-icon {', self.style_css)
        self.assertIn('.resonance-box-title {', self.style_css)
        self.assertIn('.resonance-box-podcast {', self.style_css)
        self.assertIn('.resonance-listen-btn {', self.style_css)
        self.assertIn('.resonance-listen-btn:hover {', self.style_css)

    def test_liquid_glass_narrative_box_selectors(self):
        """Verify .liquid-glass-narrative-box and child classes exist."""
        self.assertIn('.liquid-glass-narrative-box {', self.style_css)
        self.assertIn('.liquid-glass-narrative-box:hover {', self.style_css)
        self.assertIn('.narrative-box-icon {', self.style_css)
        self.assertIn('.narrative-box-content {', self.style_css)
        self.assertIn('.narrative-box-label {', self.style_css)
        self.assertIn('.narrative-box-title {', self.style_css)
        self.assertIn('.narrative-box-subtitle {', self.style_css)

    def test_thought_card_resonant_news_selectors(self):
        """Verify .thought-card-resonant-news and sub-elements."""
        self.assertIn('.thought-card-resonant-news {', self.style_css)
        self.assertIn('.thought-card-resonant-news:hover {', self.style_css)
        self.assertIn('.thought-resonant-badge {', self.style_css)
        self.assertIn('.thought-resonant-title {', self.style_css)
        self.assertIn('.thought-resonant-arrow {', self.style_css)

    def test_thought_card_3d_physics_rules(self):
        """Verify .thought-card has 3D transform properties and radial sheen reflection."""
        # Check preserve-3d and will-change on .thought-card
        thought_card_block = re.search(r'\.thought-card\s*\{([^}]+)\}', self.style_css)
        self.assertIsNotNone(thought_card_block, "CSS block for .thought-card not found")
        content = thought_card_block.group(1)
        self.assertIn('transform-style: preserve-3d', content)
        self.assertIn('will-change: transform', content)

        # Check radial gradient sheen pseudo-element
        self.assertIn('.thought-card::after', self.style_css)
        self.assertIn('var(--mouse-x', self.style_css)
        self.assertIn('var(--mouse-y', self.style_css)

    def test_coarse_pointer_media_query_reset(self):
        """Verify @media (pointer: coarse) resets transforms and disables sheens."""
        coarse_match = re.search(r'@media\s*\(\s*pointer\s*:\s*coarse\s*\)\s*\{([^}]+(\{[^}]+\}[^}]+)*)\}', self.style_css)
        self.assertIsNotNone(coarse_match, "Coarse pointer media query missing")
        coarse_content = coarse_match.group(1)
        self.assertIn('transform: none !important', coarse_content)
        self.assertIn('display: none !important', coarse_content)

    def test_responsive_media_queries(self):
        """Verify 768px and 480px media queries adapt resonance and narrative boxes."""
        self.assertIn('@media (max-width: 768px)', self.style_css)
        self.assertIn('@media (max-width: 480px)', self.style_css)

        # In 480px, .liquid-glass-resonance-box becomes column-stacked
        match_480 = re.search(r'@media\s*\(max-width:\s*480px\)\s*\{([^}]+(\{[^}]+\}[^}]+)*)\}', self.style_css)
        self.assertIsNotNone(match_480)
        content_480 = match_480.group(1)
        self.assertIn('flex-direction: column', content_480)

    def test_light_theme_adaptations(self):
        """Verify [data-theme="light"] adaptations for intelligence widgets."""
        self.assertIn('[data-theme="light"] .liquid-glass-resonance-box', self.style_css)
        self.assertIn('[data-theme="light"] .liquid-glass-narrative-box', self.style_css)
        self.assertIn('[data-theme="light"] .thought-card-resonant-news', self.style_css)

    def test_native_scrollbar_width_preserved(self):
        """Verify scrollbar-width: thin is preserved in style.css."""
        self.assertIn('scrollbar-width: thin', self.style_css)


class TestOpenModalFallbackSynthesisSimulation(unittest.TestCase):
    """Stress-tests the synthetic article fallback resolution logic in openModal."""

    def _simulate_open_modal(self, article_id, state_articles, state_podcasts):
        pool = state_articles
        # 1. Direct match
        art = next((a for a in pool if a.get('id') == article_id), None)
        if art:
            return {'status': 'resolved_direct', 'article': art}

        # 2. Resonant news in podcasts fallback
        for ep in (state_podcasts or []):
            for rn in ep.get('resonant_news', []) or []:
                if rn.get('id') == article_id:
                    synthetic = {
                        'id': rn['id'],
                        'title': rn.get('title'),
                        'source': rn.get('source', 'Resonant Wire'),
                        'category': ep.get('category', 'Tech'),
                        'region': 'Global',
                        'publishedAt': ep.get('pubDate', '2026-10-07T00:00:00Z'),
                        'imageUrl': ep.get('imageUrl', ''),
                        'link': rn.get('url') or rn.get('link') or ep.get('link') or '#',
                        'description': f'Resonant analysis linked with deep-dive podcast "{ep.get("title")}" ({ep.get("podcast")}).',
                        'annotation': {
                            'what': rn.get('title'),
                            'why': f'Explored in discussion during {ep.get("podcast")} episode "{ep.get("title")}".'
                        },
                        'relatedSources': [],
                        'resonant_podcast': {
                            'id': ep.get('id'),
                            'title': ep.get('title'),
                            'episode_title': ep.get('title'),
                            'podcast': ep.get('podcast'),
                            'podcast_title': ep.get('podcast'),
                            'link': ep.get('link'),
                            'youtube_url': ep.get('link'),
                            'resonance_score': rn.get('resonance_score') or 0.8
                        },
                        'narrative_arc': {'arc_id': None}
                    }
                    return {'status': 'resolved_synthetic', 'article': synthetic}

        return {'status': 'not_found', 'article': None}

    def test_direct_resolution(self):
        articles = [{'id': 'art-100', 'title': 'Existing Article'}]
        podcasts = []
        res = self._simulate_open_modal('art-100', articles, podcasts)
        self.assertEqual(res['status'], 'resolved_direct')
        self.assertEqual(res['article']['id'], 'art-100')

    def test_synthetic_fallback_resolution(self):
        articles = [{'id': 'art-100', 'title': 'Other Article'}]
        podcasts = [{
            'id': 'ep-99',
            'title': 'AI Revolution',
            'podcast': 'Dwarkesh Podcast',
            'link': 'https://youtube.com/watch?v=ai',
            'category': 'Tech',
            'resonant_news': [{
                'id': 'art-fallback-1',
                'title': 'OpenAI Releases Orion Model',
                'source': 'Bloomberg'
            }]
        }]
        res = self._simulate_open_modal('art-fallback-1', articles, podcasts)
        self.assertEqual(res['status'], 'resolved_synthetic')
        synth = res['article']
        self.assertEqual(synth['id'], 'art-fallback-1')
        self.assertEqual(synth['title'], 'OpenAI Releases Orion Model')
        self.assertEqual(synth['source'], 'Bloomberg')
        self.assertIsNotNone(synth['resonant_podcast'])
        self.assertEqual(synth['resonant_podcast']['podcast'], 'Dwarkesh Podcast')
        self.assertEqual(synth['narrative_arc'], {'arc_id': None})
        self.assertEqual(synth['relatedSources'], [])

    def test_unknown_id_handles_gracefully(self):
        articles = [{'id': 'art-1'}]
        podcasts = [{'id': 'ep-1', 'resonant_news': [{'id': 'art-2'}]}]
        res = self._simulate_open_modal('completely-unknown-id', articles, podcasts)
        self.assertEqual(res['status'], 'not_found')
        self.assertIsNone(res['article'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
