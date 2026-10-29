# Copyright (c) 2026 Kashish Bhushan — News Colossal
# All Rights Reserved. Pure Standard Library Implementation.
"""
Linguistic and Token-Based Sanitization Automaton & Provenance Quarantine Sieve.
Eliminates publisher/wire cross-contamination across raw titles, descriptions,
entities, primary actors, and narrative arcs.

Exclusively uses the Python standard library (unicodedata, re, html, json).
Zero external dependencies.
"""

import html
import re
import unicodedata
from typing import Dict, Any, Optional

__all__ = [
    'PUBLISHER_QUARANTINE_SET',
    'is_quarantined_publisher',
    'normalize_text',
    'sanitize_dispatch',
]

# =============================================================================
# EXHAUSTIVE PUBLISHER & WIRE QUARANTINE SET
# =============================================================================

PUBLISHER_QUARANTINE_SET = frozenset({
    # Primary news wires and agencies
    'reuters', 'reuters news', 'ap', 'ap news', 'associated press', 'the associated press',
    'afp', 'afp news', 'agence france-presse', 'bloomberg', 'bloomberg news',
    'upi', 'united press international', 'press association', 'pti', 'press trust of india',
    'ani', 'kyodo', 'yonhap', 'xinhua', 'tass', 'interfax', 'efe', 'dpa', 'ansamed',
    
    # Major global broadcasters and networks
    'bbc', 'bbc news', 'bbc world', 'bbc asia', 'bbc europe', 'bbc us', 'bbc middle east', 'bbc business',
    'cnn', 'cnn news', 'msnbc', 'fox news', 'fox', 'cnbc', 'npr',
    'france 24', 'dw', 'dw news', 'deutsche welle', 'al jazeera',
    'sky news', 'cbc', 'abc news', 'cbs news', 'nbc news', 'pbs', 'pbs newshour',
    
    # Prominent daily newspapers and journals
    'guardian', 'the guardian', 'nyt', 'new york times', 'the new york times',
    'wall street journal', 'the wall street journal', 'wsj',
    'washington post', 'the washington post',
    'ft', 'financial times', 'the financial times',
    'economist', 'the economist',
    'scmp', 'south china morning post',
    'hindustan times', 'the hindustan times', 'ht', 'ht business',
    'the hindu', 'indian express', 'the indian express',
    'los angeles times', 'latimes', 'usa today',
    'telegraph', 'the telegraph', 'the daily telegraph',
    'independent', 'the independent',
    'dow jones', 'dow jones news',
    
    # Digital publications and tech journals
    'the verge', 'techcrunch', 'ars technica', 'cnet',
    'politico', 'axios', 'time', 'newsweek', 'forbes', 'fortune'
})

def is_quarantined_publisher(name: str) -> bool:
    """Check if an entity name or string matches any known publisher or news wire in the quarantine set."""
    if not name or not isinstance(name, str):
        return False
    norm = unicodedata.normalize('NFKC', name).strip().lower()
    if norm in PUBLISHER_QUARANTINE_SET:
        return True
    if norm.startswith('the ') and norm[4:].strip() in PUBLISHER_QUARANTINE_SET:
        return True
    if norm.endswith(' news') and norm[:-5].strip() in PUBLISHER_QUARANTINE_SET:
        return True
    return False


# =============================================================================
# COMPILED REGEX AUTOMATON PATTERNS
# =============================================================================

# Sort by length descending to match longest multi-word wire names first
_WIRE_OR_PATTERN = '|'.join(re.escape(p) for p in sorted(PUBLISHER_QUARANTINE_SET, key=len, reverse=True))

# Compound wire expression allowing joined wires (e.g. "AFP/Reuters", "Reuters via BBC News", "Reuters, AP")
_COMPOUND_WIRE_PATTERN = (
    r'(?:' + _WIRE_OR_PATTERN + r')'
    r'(?:(?:\s*[/,\-–—&|]\s*|\s+(?:and|via)\s+)(?:' + _WIRE_OR_PATTERN + r'))*'
)

# Stage 2: Wire Datelines at start of text
# Examples:
#   "WASHINGTON (AP) —"
#   "BEIJING, Oct 23 (Reuters) -"
#   "WASHINGTON / BRUSSELS (AFP/Reuters) —"
#   "((AP)) Washington —"
#   "([Reuters]) London —"
#   "Reuters —"
RE_WIRE_DATELINE = re.compile(
    r'^(?:'
    # Pattern A: [WIRE] City — or [[WIRE]] — or ((WIRE)) City —
    r'[\(\[]{1,3}\s*' + _COMPOUND_WIRE_PATTERN + r'\s*[\)\]]{1,3}\s*(?:[A-Za-z0-9\s/.,\'-]{0,40}?\s*[-–—:]+\s*)?'
    r'|'
    # Pattern B: City, [Date]? (WIRE) [—–-:] or City / City (WIRE/WIRE) [—–-:]
    r'(?:[A-Z][A-Za-z0-9\s/.,\'-]{0,60}?\s*)?[\(\[]{1,3}\s*' + _COMPOUND_WIRE_PATTERN + r'\s*[\)\]]{1,3}\s*[-–—:]+\s*'
    r'|'
    # Pattern C: WIRE [—–-:] at the start of dispatch
    r'(?:' + _COMPOUND_WIRE_PATTERN + r')\s*[-–—:]+\s*'
    r')',
    re.IGNORECASE
)

# Stage 3: Editorial Slugs and Framing Prefixes
RE_EDITORIAL_SLUG = re.compile(
    r'^(?:'
    r'(EXCLUSIVE|BREAKING(?:\s+NEWS)?|UPDATE(?:\s+\d+)?|ANALYSIS|EXPLAINER|FACTBOX|'
    r'LIVE(?:\s+UPDATES)?|WATCH|SPECIAL\s+REPORT|NEWS\s+ALERT|Q&A|OPINION|EDITORIAL)'
    r'\s*[:|—–-]+\s*'
    r')',
    re.IGNORECASE
)

# Stage 4: Trailing Attribution Suffixes
RE_ATTR_SUFFIX = re.compile(
    r'(?:'
    # Pattern A: Separator (|, -, –, —) + compound wire + optional trailing chars
    r'\s*[|\-–—]+(?:\s*[|\-–—]+)*\s*(?:' + _COMPOUND_WIRE_PATTERN + r')\b.*$'
    r'|'
    # Pattern B: Parenthetical or bracketed compound wire (1-3 bracket levels)
    r'\s*[\(\[]{1,3}\s*(?:' + _COMPOUND_WIRE_PATTERN + r')\s*[\)\]]{1,3}\s*$'
    r'|'
    # Pattern C: Space + wire at end of string (with optional terminal punctuation)
    r'\s+(?:' + _COMPOUND_WIRE_PATTERN + r')\s*[\.!?]?\s*$'
    r')',
    re.IGNORECASE
)

# Stage 5: Embedded Attribution Clauses at sentence or headline boundary
RE_ATTR_CLAUSE = re.compile(
    r',?\s*(?:'
    r'(?:(?:reports?|reported)\s+(?:by\s+)?(?:the\s+)?(?:' + _WIRE_OR_PATTERN + r'))'
    r'|'
    r'(?:(?:' + _WIRE_OR_PATTERN + r')\s+(?:reports?|reported))'
    r'|'
    r'(?:according\s+to\s+(?:the\s+)?(?:' + _WIRE_OR_PATTERN + r'))'
    r'|'
    r'(?:(?:(?:lawyers?|officials?|sources?|spokes(?:person|man|woman)|authorities)\s+)?tells?\s+(?:the\s+)?(?:' + _WIRE_OR_PATTERN + r'))'
    r'|'
    r'(?:(?:' + _WIRE_OR_PATTERN + r')\s+finds?)'
    r')\b\s*[\.!?]?\s*$',
    re.IGNORECASE
)

# Stage 6: Wire Footers & Bylines
RE_WIRE_FOOTER = re.compile(
    r'(?:'
    r'\s*\((?:reporting\s+by|editing\s+by|writing\s+by|additional\s+reporting).*?\)\s*$'
    r'|'
    r'\s*(?:reporting\s+by|editing\s+by|writing\s+by|additional\s+reporting).*?$'
    r'|'
    r'\s*(?:copyright\s+\d{4}|all\s+rights\s+reserved).*?$'
    r'|'
    r'\s*(?:read\s+(?:more|full\s+story)\s+(?:at|on)\s+(?:' + _WIRE_OR_PATTERN + r')).*?$'
    r')',
    re.IGNORECASE
)


# =============================================================================
# DETERMINISTIC SANITIZATION AUTOMATON
# =============================================================================

def stage1_nfkc_and_unescape(text: str) -> str:
    """Stage 1: NFKC Unicode normalization, HTML unescaping, whitespace canonicalization."""
    if not text:
        return ""
    # HTML entities (handles double-encoded entities like &amp;apos;)
    for _ in range(2):
        new_text = html.unescape(text)
        if new_text == text:
            break
        text = new_text
    # Unicode NFKC normalization
    text = unicodedata.normalize('NFKC', text)
    # Canonicalize typography & non-breaking/zero-width spaces
    text = text.replace('\u00a0', ' ').replace('\u200b', '').replace('\ufeff', '')
    text = text.replace('“', '"').replace('”', '"').replace('‘', "'").replace('’', "'")
    text = text.replace('`', "'")
    # Normalize multiple whitespace
    text = re.sub(r'[ \t\r\n]+', ' ', text).strip()
    return text


def sanitize_dispatch(title: str, description: str = '', source: str = '') -> Dict[str, Any]:
    """
    Deterministically sanitizes dispatch title and description across the 7-stage automaton.
    
    Returns:
        {
            'clean_title': str,
            'clean_description': str,
            'stripped_dateline': Optional[str],
            'stripped_attribution': Optional[str],
            'meta_flags': dict
        }
    """
    stripped_dateline = None
    stripped_attr = None
    meta_flags: Dict[str, Any] = {}

    # -------------------------------------------------------------------------
    # TITLE SANITIZATION PIPELINE
    # -------------------------------------------------------------------------
    t = stage1_nfkc_and_unescape(title)

    # Stage 2: Prefix datelines on title (rare, but present on some wire feeds)
    m_dl_t = RE_WIRE_DATELINE.match(t)
    if m_dl_t:
        stripped_dateline = m_dl_t.group(0).strip()
        t = t[m_dl_t.end():].strip()

    # Stage 3: Editorial slugs & framing extraction
    m_slug_t = RE_EDITORIAL_SLUG.match(t)
    if m_slug_t:
        slug = m_slug_t.group(1).upper()
        if 'EXCLUSIVE' in slug:
            meta_flags['is_exclusive'] = True
        elif 'BREAKING' in slug:
            meta_flags['is_breaking'] = True
        elif 'ANALYSIS' in slug:
            meta_flags['is_analysis'] = True
        elif 'EXPLAINER' in slug:
            meta_flags['is_explainer'] = True
        elif 'OPINION' in slug or 'EDITORIAL' in slug:
            meta_flags['is_opinion'] = True
        elif 'FACTBOX' in slug:
            meta_flags['is_factbox'] = True
        t = t[m_slug_t.end():].strip()

    # Stage 6 first: Wire footer / byline strip (to expose any preceding wire suffix)
    m_foot_t = RE_WIRE_FOOTER.search(t)
    if m_foot_t:
        t = t[:m_foot_t.start()].strip()

    # Stage 5 & 4: Attribution clauses and trailing attribution suffixes (iterative)
    for _ in range(2):
        # Match complete attribution clauses first (e.g. ", lawyer tells BBC")
        m_clause_t = RE_ATTR_CLAUSE.search(t)
        if m_clause_t:
            stripped_attr = (stripped_attr or '') + ' ' + m_clause_t.group(0).strip()
            t = t[:m_clause_t.start()].strip()

        # Explicit source suffix check if source provided
        if source:
            s_pat = re.compile(r'\s*[|\-–—/]+\s*' + re.escape(source) + r'\b.*$', re.IGNORECASE)
            m_src = s_pat.search(t)
            if m_src:
                stripped_attr = (stripped_attr or '') + ' ' + m_src.group(0).strip()
                t = t[:m_src.start()].strip()

        m_attr_t = RE_ATTR_SUFFIX.search(t)
        if m_attr_t:
            stripped_attr = (stripped_attr or '') + ' ' + m_attr_t.group(0).strip()
            t = t[:m_attr_t.start()].strip()

    # Stage 7: Title punctuation cleanup
    clean_title = re.sub(r'[\s,;:–—\-/]+$', '', t).strip()
    clean_title = re.sub(r'\s+', ' ', clean_title).strip()

    # -------------------------------------------------------------------------
    # DESCRIPTION SANITIZATION PIPELINE
    # -------------------------------------------------------------------------
    d = stage1_nfkc_and_unescape(description)

    # Stage 2: Prefix datelines on description
    m_dl_d = RE_WIRE_DATELINE.match(d)
    if m_dl_d:
        if not stripped_dateline:
            stripped_dateline = m_dl_d.group(0).strip()
        d = d[m_dl_d.end():].strip()

    # Stage 3: Editorial slugs on description
    m_slug_d = RE_EDITORIAL_SLUG.match(d)
    if m_slug_d:
        d = d[m_slug_d.end():].strip()

    # Stage 6 first: Wire footers / bylines
    m_foot_d = RE_WIRE_FOOTER.search(d)
    if m_foot_d:
        d = d[:m_foot_d.start()].strip()

    # Stage 5 & 4: Attribution clauses and trailing attribution suffixes (iterative)
    for _ in range(2):
        m_clause_d = RE_ATTR_CLAUSE.search(d)
        if m_clause_d:
            if not stripped_attr:
                stripped_attr = m_clause_d.group(0).strip()
            d = d[:m_clause_d.start()].strip()

        if source:
            s_pat = re.compile(r'\s*[|\-–—/]+\s*' + re.escape(source) + r'\b.*$', re.IGNORECASE)
            d = s_pat.sub('', d).strip()

        m_attr_d = RE_ATTR_SUFFIX.search(d)
        if m_attr_d:
            if not stripped_attr:
                stripped_attr = m_attr_d.group(0).strip()
            d = d[:m_attr_d.start()].strip()

    # Stage 7: Description sentence termination & punctuation cleanup
    d = re.sub(r'[\s.…,;:–—\-/]+$', '', d).strip()
    d = re.sub(r'\s+', ' ', d).strip()
    if d and not d.endswith(('!', '?')):
        d += '.'
    clean_description = d

    return {
        'clean_title': clean_title,
        'clean_description': clean_description,
        'stripped_dateline': stripped_dateline,
        'stripped_attribution': stripped_attr.strip() if stripped_attr else None,
        'meta_flags': meta_flags
    }


def normalize_text(text: str) -> str:
    """Normalize text through the 7-stage sanitization automaton for deduplication & comparisons."""
    if not text:
        return ""
    res = sanitize_dispatch(text)
    return res['clean_title']
