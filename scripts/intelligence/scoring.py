# Copyright (c) 2026 Kashish Bhushan — News Colossal
"""
LAYER 2: SCORING of the News Colossal Editorial Intelligence Engine.
Implements an 8-editor scoring panel for comprehensive article evaluation.
"""

import re
import math
from datetime import datetime, timezone
from collections import Counter
from typing import List, Dict, Any, Optional

try:
    from intelligence.entities import DOMAIN_TAXONOMY, ACTION_CATEGORIES
except ImportError:
    # Fallback for standalone testing or initialization if entities is not yet complete
    DOMAIN_TAXONOMY = {}
    ACTION_CATEGORIES = {}

# --- Precompiled Regex Patterns ---
NUMBER_PATTERN = re.compile(r'\b\d+(?:\.\d+)?(?:%|\s*(?:million|billion|trillion|k|m|b))?\b', re.IGNORECASE)
QUOTE_PATTERN = re.compile(r'["\'](?:.*?)["\']')
ATTRIBUTION_PATTERN = re.compile(r'\b(?:said|announced|confirmed|reported|according to)\b', re.IGNORECASE)
ALL_CAPS_PATTERN = re.compile(r'^[^a-z]*$')
PUNCT_END_PATTERN = re.compile(r'(?:\?\?+|!!!+)\s*$')
WORDS_PATTERN = re.compile(r'\b[a-zA-Z0-9]{3,}\b')

# --- Stopwords ---
STOPWORDS = {
    'the', 'and', 'a', 'to', 'of', 'in', 'i', 'is', 'that', 'it', 'on', 'you',
    'this', 'for', 'but', 'with', 'are', 'have', 'be', 'at', 'or', 'as', 'was',
    'so', 'if', 'out', 'not', 'an', 'has', 'by', 'from', 'we', 'they', 'will',
    'can', 'about', 'which', 'up', 'been', 'some', 'more', 'what', 'who', 'when',
    'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'most', 'now',
    'other', 'such', 'no', 'nor', 'only', 'own', 'same', 'than', 'too', 'very',
    'just', 'don', 'should', 'their', 'there', 'then', 'these', 'those'
}

def tokenize(text: str) -> List[str]:
    """Tokenize text into lowercase alphanumeric tokens > 2 chars, removing stopwords."""
    if not text:
        return []
    tokens = WORDS_PATTERN.findall(text.lower())
    return [t for t in tokens if t not in STOPWORDS]

def parse_date_safe(date_str: str) -> Optional[datetime]:
    """Parse publication date using multiple formats."""
    if not date_str:
        return None
        
    date_str = date_str.strip()
    
    formats = [
        '%a, %d %b %Y %H:%M:%S %z',  # RFC 2822
        '%a, %d %b %Y %H:%M:%S %Z',
        '%Y-%m-%dT%H:%M:%S%z',       # ISO 8601 with tz
        '%Y-%m-%dT%H:%M:%SZ',        # ISO 8601 UTC
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%d',
    ]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except ValueError:
            continue
            
    # Fallback to handle fractional seconds e.g. 2026-09-29T19:42:15.123Z
    try:
        clean_date = re.sub(r'\.\d+', '', date_str)
        for fmt in formats:
            try:
                dt = datetime.strptime(clean_date, fmt)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt
            except ValueError:
                continue
    except Exception:
        pass
        
    return None

def velocity_score(article: Dict[str, Any], all_articles: List[Dict[str, Any]]) -> float:
    """Editor 1: Measures how fast a story is spreading across sources."""
    score = 0.15
    cluster = article.get('storyCluster')
    
    if cluster:
        size = cluster.get('size', 1)
        if size == 2:
            score = 0.3
        elif size == 3:
            score = 0.5
        elif size == 4:
            score = 0.7
        elif size >= 5:
            score = 0.9
            
        if cluster.get('crossRegional', False):
            score += 0.1
            score = min(1.0, score)
            
    pub_date = parse_date_safe(article.get('pubDate', ''))
    if pub_date:
        now = datetime.now(timezone.utc)
        age_hours = (now - pub_date).total_seconds() / 3600.0
        if 0 <= age_hours <= 3:
            score += 0.1
            
    return min(1.0, max(0.0, score))


# Cache variables for rarity scoring to avoid redundant IDF computation
_idf_cache = {}
_idf_cache_id = None
_min_idf = 0.0
_max_idf = 1.0

def rarity_score(article: Dict[str, Any], all_articles: List[Dict[str, Any]]) -> float:
    """Editor 2: Measures how unique/original this article's content is compared to the entire feed."""
    global _idf_cache, _idf_cache_id, _min_idf, _max_idf
    
    current_articles_id = id(all_articles)
    if current_articles_id != _idf_cache_id:
        _idf_cache.clear()
        doc_count = len(all_articles)
        term_counts = Counter()
        
        for a in all_articles:
            unique_tokens = set(tokenize(a.get('title', '')))
            term_counts.update(unique_tokens)
            
        for term, count in term_counts.items():
            # Standard IDF formula
            _idf_cache[term] = math.log((doc_count + 1) / (count + 1))
            
        article_idfs = []
        for a in all_articles:
            tokens = set(tokenize(a.get('title', '')))
            if tokens:
                avg = sum(_idf_cache.get(t, 0.0) for t in tokens) / len(tokens)
            else:
                avg = 0.0
            article_idfs.append(avg)
            
        if article_idfs:
            _min_idf = min(article_idfs)
            _max_idf = max(article_idfs)
        else:
            _min_idf = 0.0
            _max_idf = 1.0
            
        _idf_cache_id = current_articles_id
        
    tokens = set(tokenize(article.get('title', '')))
    if not tokens:
        return 0.0
        
    avg_idf = sum(_idf_cache.get(t, 0.0) for t in tokens) / len(tokens)
    
    if _max_idf > _min_idf:
        norm = (avg_idf - _min_idf) / (_max_idf - _min_idf)
    else:
        norm = 0.5
        
    return max(0.0, min(1.0, norm))

def narrative_score(article: Dict[str, Any], narrative_arcs: List[Dict[str, Any]]) -> float:
    """Editor 3: Evaluates article against ongoing narrative arcs."""
    if not narrative_arcs:
        return 0.2
        
    article_tokens = set(tokenize(article.get('title', '') + ' ' + article.get('description', '')))
    article_entities = article.get('entities', {})
    
    # Flatten article entity names for naive entity signature matching (for this example context)
    entity_strings = []
    for k, v in article_entities.items():
        if isinstance(v, list):
            entity_strings.extend([str(x).lower() for x in v])
        elif isinstance(v, (str, int, float)):
            entity_strings.append(str(v).lower())
            
    best_match = None
    
    for arc in narrative_arcs:
        arc_keywords = set(k.lower() for k in arc.get('keywords', []))
        overlap = len(article_tokens.intersection(arc_keywords))
        
        is_keyword_match = len(arc_keywords) > 0 and (overlap / len(arc_keywords)) >= 0.5
        
        signature = arc.get('entity_signature', '').lower()
        is_entity_match = signature and signature in entity_strings
        
        if is_keyword_match or is_entity_match:
            best_match = arc
            break
            
    if best_match:
        trend = best_match.get('importance_trend', 'stable')
        if trend == 'rising':
            return 0.9
        elif trend == 'stable':
            return 0.7
        else:
            return 0.4
            
    # Check if potential NEW arc
    entity_density = article_entities.get('entity_density', 0.0)
    action_count = len(article_entities.get('actions', []))
    if entity_density > 0.1 or action_count >= 2:
        return 0.6
        
    return 0.2

def quality_score(article: Dict[str, Any]) -> float:
    """Editor 4: Measures epistemic quality — informative and well-sourced."""
    score = 0.25
    title = article.get('title', '')
    desc = article.get('description', '')
    full_text = f"{title} {desc}"
    
    entities = article.get('entities', {})
    leaders = entities.get('leaders', [])
    if leaders:
        score += 0.15
        
    if NUMBER_PATTERN.search(full_text):
        score += 0.15
        
    if QUOTE_PATTERN.search(full_text):
        score += 0.10
        
    if ATTRIBUTION_PATTERN.search(full_text):
        score += 0.10
        
    if len(desc) > 150:
        score += 0.10
    elif len(desc) < 50:
        score -= 0.15
        
    img_url = article.get('imageUrl', '')
    if img_url and 'unsplash.com' not in img_url.lower():
        score += 0.05
        
    annot = article.get('annotation', {})
    if isinstance(annot, dict) and annot.get('what') and annot.get('why'):
        score += 0.10
        
    if ALL_CAPS_PATTERN.match(title) and any(c.isalpha() for c in title):
        score -= 0.20
        
    if PUNCT_END_PATTERN.search(title):
        score -= 0.10
        
    return max(0.0, min(1.0, score))

def density_score(article: Dict[str, Any]) -> float:
    """Editor 5: Measures information density per reading minute."""
    entities = article.get('entities', {})
    
    entity_count = entities.get('entity_count', 0)
    full_text = f"{article.get('title', '')} {article.get('description', '')}"
    data_points = len(NUMBER_PATTERN.findall(full_text))
    action_count = len(entities.get('actions', []))
    
    info_units = entity_count + data_points + action_count
    
    word_count = len(article.get('description', '').split())
    reading_minutes = max(word_count / 200.0, 0.5)
    
    density = info_units / reading_minutes
    
    if density >= 5.0:
        return 1.0
    elif density <= 1.0:
        return 0.2
    
    # Linear interpolation between 1.0 and 5.0 -> 0.2 and 1.0
    norm_score = 0.2 + 0.8 * ((density - 1.0) / 4.0)
    return max(0.2, min(1.0, norm_score))

def bridge_score(article: Dict[str, Any]) -> float:
    """Editor 6: Measures cross-domain relevance."""
    entities = article.get('entities', {})
    domains = set(entities.get('domains', []))
    domain_count = len(domains)
    
    if domain_count == 0:
        score = 0.1
    elif domain_count == 1:
        score = 0.2
    elif domain_count == 2:
        score = 0.5
    else:
        score = 0.85
        
    # countries may be a list of dicts with 'code' key, or a list of strings
    raw_countries = entities.get('countries', [])
    if raw_countries and isinstance(raw_countries[0], dict):
        countries = set(c.get('code', '') for c in raw_countries)
    else:
        countries = set(raw_countries)
    if len(countries) >= 2:
        score += 0.15
        
    return min(1.0, score)

def cognitive_type(article: Dict[str, Any]) -> str:
    """Editor 7: Classifies the required thinking type."""
    entities = article.get('entities', {})
    domains = [d.lower() for d in entities.get('domains', [])]
    actions = [a.lower() for a in entities.get('actions', [])]
    combined = set(domains + actions)
    
    types = {
        'strategic': {'geopolitics', 'diplomacy', 'conflict', 'military', 'war', 'treaty'},
        'analytical': {'economics', 'data', 'markets', 'trade', 'finance', 'inflation'},
        'technical': {'technology', 'science', 'research', 'innovation', 'ai', 'space'},
        'humanitarian': {'rights', 'health', 'crisis', 'refugee', 'climate', 'aid'},
        'governance': {'legislation', 'regulation', 'court', 'policy', 'law', 'election'},
        'investigative': {'justice', 'corruption', 'scandal', 'probe', 'crime', 'fraud'}
    }
    
    best_match = 'general'
    max_overlap = 0
    
    for ctype, keywords in types.items():
        overlap = len(combined.intersection(keywords))
        if overlap > max_overlap:
            max_overlap = overlap
            best_match = ctype
            
    return best_match

def temporal_score(article: Dict[str, Any]) -> float:
    """Editor 8: Smart decay based on event type."""
    pub_date = parse_date_safe(article.get('pubDate', ''))
    if not pub_date:
        return 0.5
        
    now = datetime.now(timezone.utc)
    age_hours = (now - pub_date).total_seconds() / 3600.0
    if age_hours < 0:
        age_hours = 0
        
    entities = article.get('entities', {})
    actions = [a.lower() for a in entities.get('actions', [])]
    
    ongoing_keywords = {'conflict', 'election', 'crisis', 'diplomacy'}
    oneoff_keywords = {'technology', 'launch', 'release', 'announcement'}
    
    is_ongoing = any(kw in a for a in actions for kw in ongoing_keywords)
    is_oneoff = any(kw in a for a in actions for kw in oneoff_keywords)
    
    if is_ongoing:
        if age_hours < 6: return 1.0
        if age_hours < 24: return 0.85
        if age_hours < 72: return 0.65
        return 0.45
    elif is_oneoff:
        if age_hours < 3: return 1.0
        if age_hours < 12: return 0.7
        if age_hours < 24: return 0.4
        return 0.2
    else:
        # Default
        if age_hours < 6: return 1.0
        if age_hours < 12: return 0.8
        if age_hours < 24: return 0.6
        if age_hours < 48: return 0.35
        return 0.2

def composite_score(scores: dict, noise_penalty: float = 0.0) -> float:
    """Weighted average of all editor scores."""
    weights = {
        'velocity': 0.18,
        'rarity': 0.12,
        'narrative': 0.15,
        'quality': 0.15,
        'density': 0.10,
        'bridge': 0.10,
        'temporal': 0.20,
    }
    
    weighted = sum(scores.get(k, 0.0) * weights[k] for k in weights)
    final = max(0.0, min(1.0, weighted + noise_penalty))
    return round(final, 4)

def run_scoring(articles: List[Dict[str, Any]], narrative_arcs: List[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    Run the complete 8-editor scoring panel on all articles.
    """
    if narrative_arcs is None:
        narrative_arcs = []
        
    all_scores = []
    cognitive_dist = Counter()
    
    for article in articles:
        # Ensure base structure
        if 'entities' not in article:
            article['entities'] = {}
            
        noise_penalty = article.get('noise_penalty', 0.0)
        
        scores = {
            'velocity': velocity_score(article, articles),
            'rarity': rarity_score(article, articles),
            'narrative': narrative_score(article, narrative_arcs),
            'quality': quality_score(article),
            'density': density_score(article),
            'bridge': bridge_score(article),
            'temporal': temporal_score(article),
        }
        
        comp = composite_score(scores, noise_penalty)
        cog_type = cognitive_type(article)
        
        # Enrich article
        article['scores'] = scores
        article['scores']['composite'] = comp
        article['cognitive_type'] = cog_type
        article['importance_score'] = round(comp * 10.0, 2)
        
        all_scores.append(comp)
        cognitive_dist[cog_type] += 1
        
    # Audit Printing
    if all_scores:
        avg_comp = sum(all_scores) / len(all_scores)
        sorted_scores = sorted(all_scores, reverse=True)
        top_5 = sorted_scores[:5]
        bottom_5 = sorted_scores[-5:][::-1]
        
        print("Scoring Panel Results:")
        print(f"  Average composite: {avg_comp:.2f}")
        print(f"  Top 5 scores: {top_5}")
        print(f"  Bottom 5 scores: {bottom_5}")
        
        cog_str = ", ".join(f"{k}={v}" for k, v in cognitive_dist.items())
        print(f"  Cognitive distribution: {cog_str}")
    else:
        print("Scoring Panel Results: No articles to score.")
        
    return articles
