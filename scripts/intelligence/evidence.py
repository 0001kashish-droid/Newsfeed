"""Evidence-led claim extraction and conservative cross-source checks.

This module is deliberately source-bounded.  It does not claim to establish
truth from headlines: it records what a publisher reported, whether independent
publishers describe the same event, and which unresolved signals need review.
"""

import re
from collections import defaultdict
from typing import Any, Dict, Iterable, List


WORD_RE = re.compile(r"[A-Za-z][A-Za-z0-9'-]{2,}")
NUMBER_RE = re.compile(r"\b\d+(?:\.\d+)?(?:%|\s*(?:million|billion|trillion|k|m|b))?\b", re.I)
NEGATION_RE = re.compile(r"\b(?:no|not|never|denies|denied|false|rejects|rejected)\b", re.I)
STOPWORDS = {
    'the', 'and', 'for', 'with', 'from', 'that', 'this', 'into', 'over',
    'amid', 'after', 'before', 'under', 'says', 'say', 'sources', 'source',
    'report', 'reports', 'news', 'their', 'they', 'have', 'has', 'will',
    'are', 'was', 'were', 'its', 'his', 'her', 'who', 'about', 'than',
}


def _tokens(text: str) -> set:
    return {word.lower() for word in WORD_RE.findall(text or '') if word.lower() not in STOPWORDS}


def _overlap(left: str, right: str) -> float:
    a, b = _tokens(left), _tokens(right)
    if not a or not b:
        return 0.0
    return len(a & b) / min(len(a), len(b))


def _brand(source: str) -> str:
    """Normalise publisher names sufficiently to avoid counting a duplicate feed twice."""
    return re.sub(r'\s+', ' ', (source or '').strip().lower())


def _conflict_signals(claim: str, candidate: str) -> List[str]:
    signals: List[str] = []
    claim_numbers = set(NUMBER_RE.findall(claim or ''))
    candidate_numbers = set(NUMBER_RE.findall(candidate or ''))
    if claim_numbers and candidate_numbers and claim_numbers != candidate_numbers:
        signals.append('different numeric detail')
    if bool(NEGATION_RE.search(claim or '')) != bool(NEGATION_RE.search(candidate or '')):
        signals.append('opposite negation signal')
    return signals


def _confidence(independent_support: int, disputed: bool) -> Dict[str, Any]:
    # This is a confidence in the *evidence coverage*, not a probability that a claim is true.
    score = 0.35 + 0.25 + min(independent_support, 3) * 0.15
    if disputed:
        score -= 0.20
    score = round(max(0.15, min(score, 0.90)), 2)
    label = 'limited' if score < 0.55 else ('moderate' if score < 0.75 else 'well-supported')
    return {
        'score': score,
        'label': label,
        'meaning': 'Evidence coverage, not a truth probability.',
    }


def build_evidence_ledger(article: Dict[str, Any]) -> Dict[str, Any]:
    """Build auditable claim-level provenance from article and cluster metadata."""
    title = (article.get('title') or '').strip()
    source = (article.get('source') or 'Unknown publisher').strip()
    link = article.get('link') or ''
    cluster = article.get('storyCluster') or {}
    members = cluster.get('sources') if isinstance(cluster.get('sources'), list) else []
    independent: Dict[str, Dict[str, Any]] = {}
    conflicts: List[Dict[str, str]] = []

    for member in members:
        if not isinstance(member, dict):
            continue
        member_source = (member.get('source') or '').strip()
        member_title = (member.get('title') or '').strip()
        if not member_source or _brand(member_source) == _brand(source) or not member_title:
            continue
        overlap = _overlap(title, member_title)
        if overlap >= 0.35:
            independent.setdefault(_brand(member_source), {
                'source': member_source,
                'headline': member_title,
                'url': member.get('link') or member.get('url') or '',
                'overlap': round(overlap, 2),
            })
            for signal in _conflict_signals(title, member_title):
                conflicts.append({'source': member_source, 'signal': signal})

    meta = article.get('meta') or {}
    disputed = bool(conflicts or meta.get('cluster_contested'))
    supporting = list(independent.values())
    claim = {
        'id': 'core-event',
        'statement': title or 'No publisher headline is available.',
        'classification': 'directly_reported',
        'evidence': [{
            'source': source,
            'url': link,
            'quote': title,
            'kind': 'publisher_headline',
        }] if title else [],
        'corroboration': {
            'independent_sources': supporting,
            'method': 'Headline token-overlap across distinct publisher brands; this detects the same event, not agreement on every detail.',
        },
        'inference': None,
        'disputed': {
            'present': disputed,
            'signals': conflicts,
            'note': 'Requires source review before treating disputed details as settled.' if disputed else 'No contradiction signal was detected in the available cluster metadata.',
        },
        'unknown': [
            'Claim-by-claim agreement, underlying documents, and omitted context are not established from headlines alone.'
        ],
        'confidence': _confidence(len(supporting), disputed),
    }
    return {
        'version': 1,
        'method': 'deterministic-source-bounded',
        'claims': [claim],
        'review_required': disputed or not supporting,
        'limitations': [
            'The system does not infer factual truth from publisher count.',
            'Only supplied article metadata and clustered headlines are assessed.',
        ],
    }


def enrich_evidence_ledgers(articles: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Attach an evidence ledger to every article without changing editorial text."""
    enriched = []
    for article in articles:
        article['evidence_ledger'] = build_evidence_ledger(article)
        enriched.append(article)
    return enriched
