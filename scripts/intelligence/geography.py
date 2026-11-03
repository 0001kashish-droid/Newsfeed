# Copyright (c) 2026 Kashish Bhushan — News Colossal
"""Story geography with separate event, actor, impact, and theatre dimensions.

Feed sections describe where a publisher categorises a dispatch; they do not
reliably describe where an event happens.  This module keeps that provenance in
``source_region`` and derives a reader-facing geography record from extracted
entities.  It deliberately returns honest empty lists when a story has no
geographic evidence instead of inventing a location.
"""

from typing import Any, Dict, Iterable, List


COUNTRY_REGION = {
    'US': 'North America', 'CA': 'North America', 'MX': 'North America',
    'UK': 'Europe', 'DE': 'Europe', 'FR': 'Europe', 'IT': 'Europe',
    'ES': 'Europe', 'PL': 'Europe', 'NL': 'Europe', 'SE': 'Europe',
    'CH': 'Europe', 'AT': 'Europe', 'GR': 'Europe', 'PT': 'Europe',
    'IE': 'Europe', 'BE': 'Europe', 'DK': 'Europe', 'FI': 'Europe',
    'NO': 'Europe', 'CZ': 'Europe', 'HU': 'Europe', 'RO': 'Europe',
    'BG': 'Europe', 'RS': 'Europe', 'HR': 'Europe', 'UA': 'Europe',
    'EU': 'Europe',
    'CN': 'Asia-Pacific', 'JP': 'Asia-Pacific', 'KR': 'Asia-Pacific',
    'KP': 'Asia-Pacific', 'TW': 'Asia-Pacific', 'AU': 'Asia-Pacific',
    'NZ': 'Asia-Pacific', 'ID': 'Asia-Pacific', 'MM': 'Asia-Pacific',
    'VN': 'Asia-Pacific', 'TH': 'Asia-Pacific', 'PH': 'Asia-Pacific',
    'MY': 'Asia-Pacific', 'SG': 'Asia-Pacific', 'ASEAN': 'Asia-Pacific',
    'IN': 'India',
    'IR': 'Middle East', 'IL': 'Middle East', 'PS': 'Middle East',
    'SA': 'Middle East', 'TR': 'Middle East', 'EG': 'Middle East',
    'SY': 'Middle East', 'LB': 'Middle East', 'AF': 'Middle East',
    'PK': 'Middle East',
    'RU': 'Europe', 'BR': 'Global', 'AR': 'Global', 'CL': 'Global',
    'PE': 'Global', 'CO': 'Global', 'CU': 'Global', 'ZA': 'Global',
    'NG': 'Global', 'KE': 'Global', 'ET': 'Global', 'BD': 'Global',
}


def _country_codes(article: Dict[str, Any]) -> List[str]:
    countries = article.get('entities', {}).get('countries', [])
    codes: List[str] = []
    for country in countries:
        code = country.get('code') if isinstance(country, dict) else country
        if isinstance(code, str) and code and code not in codes:
            codes.append(code)
    return codes


def _regions(codes: Iterable[str]) -> List[str]:
    regions: List[str] = []
    for code in codes:
        region = COUNTRY_REGION.get(code)
        if region and region not in regions:
            regions.append(region)
    return regions


def _strategic_theatre(codes: List[str], event_regions: List[str]) -> str:
    code_set = set(codes)
    if code_set.intersection({'RU', 'UA', 'PL', 'FI', 'SE', 'RS', 'HU'}) and 'Europe' in event_regions:
        return 'European Security'
    if code_set.intersection({'CN', 'TW', 'JP', 'KR', 'KP', 'PH', 'AU'}) and code_set.intersection({'US', 'CN', 'TW', 'JP', 'KR', 'KP', 'PH', 'AU'}):
        return 'Indo-Pacific'
    if code_set.intersection({'IR', 'IL', 'PS', 'SA', 'SY', 'LB', 'AF'}):
        return 'Middle East'
    if 'IN' in code_set and code_set.intersection({'PK', 'BD', 'CN', 'AF'}):
        return 'South Asia'
    if event_regions:
        return event_regions[0]
    return 'Global'


def _actor_labels(article: Dict[str, Any]) -> List[str]:
    actors = article.get('primary_actors') or article.get('entities', {}).get('primary_actors') or {}
    labels: List[str] = []
    for value in [actors.get('active_agent'), *actors.get('leaders', []), *actors.get('sovereign_stakeholders', [])]:
        if isinstance(value, str) and value and value not in labels:
            labels.append(value)
    return labels[:4]


def enrich_story_geography(article: Dict[str, Any]) -> Dict[str, Any]:
    """Attach a multi-dimensional, evidence-led geography model to one story."""
    source_region = article.get('source_region') or article.get('region') or 'Global'
    article['source_region'] = source_region

    codes = _country_codes(article)
    event_regions = _regions(codes)
    primary_region = event_regions[0] if event_regions else source_region
    geography = {
        'event_regions': event_regions,
        'actors': _actor_labels(article),
        'affected_regions': event_regions,
        'strategic_theatre': _strategic_theatre(codes, event_regions),
        'source_region': source_region,
        'confidence': 'entity-derived' if event_regions else 'source-context',
    }
    article['geography'] = geography
    article['region'] = primary_region
    return article


def enrich_story_geographies(articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Apply multi-dimensional geography in place, preserving feed provenance."""
    return [enrich_story_geography(article) for article in articles]
