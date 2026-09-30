# Copyright (c) 2026 Kashish Bhushan — News Colossal
import json
import os
import uuid
from datetime import datetime, timezone, timedelta

DEFAULT_MEMORY_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    'data',
    'narrative_memory.json'
)

def _get_now_iso() -> str:
    """Helper to get current UTC time in ISO format."""
    return datetime.now(timezone.utc).isoformat()

def _parse_iso(dt_str: str) -> datetime:
    """Helper to parse ISO datetime string."""
    try:
        return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
    except ValueError:
        return datetime.now(timezone.utc)

def load_memory(memory_path: str = DEFAULT_MEMORY_PATH) -> dict:
    """Load narrative memory from disk. Returns empty structure if file doesn't exist."""
    if not os.path.exists(memory_path):
        return {
            "last_updated": _get_now_iso(),
            "arcs": [],
            "version": 2
        }
    try:
        with open(memory_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if "arcs" not in data:
                data["arcs"] = []
            return data
    except (json.JSONDecodeError, OSError):
        return {
            "last_updated": _get_now_iso(),
            "arcs": [],
            "version": 2
        }

def save_memory(memory: dict, memory_path: str = DEFAULT_MEMORY_PATH) -> None:
    """Save narrative memory to disk. Creates parent directories if needed."""
    os.makedirs(os.path.dirname(memory_path), exist_ok=True)
    memory["last_updated"] = _get_now_iso()
    with open(memory_path, 'w', encoding='utf-8') as f:
        json.dump(memory, f, indent=4, ensure_ascii=False)

def match_article_to_arc(article: dict, arcs: list, threshold: float = 0.4) -> tuple:
    """Check if an article matches any existing narrative arc.
    
    Matching criteria (OR logic — any one is sufficient):
    1. >=50% keyword overlap between article title tokens and arc keywords
    2. Entity signature overlap >=60%
    3. Same category + >=40% keyword overlap
    
    Returns: (matched_arc_or_None, match_confidence_float)
    """
    article_title_words = set(word.lower() for word in article.get('title', '').split() if len(word) > 2)
    article_entities = set(article.get('entities', []))
    article_category = article.get('category', '')
    
    best_match = None
    best_score = 0.0
    
    for arc in arcs:
        arc_keywords = set(k.lower() for k in arc.get('keywords', []))
        
        # 1. Keyword overlap
        keyword_overlap = len(article_title_words.intersection(arc_keywords))
        keyword_score = keyword_overlap / max(1, len(article_title_words))
        
        # 2. Entity overlap
        arc_entities = set(arc.get('entity_signature', '').split(':'))
        entity_overlap = len(article_entities.intersection(arc_entities))
        entity_score = entity_overlap / max(1, len(article_entities))
        
        # 3. Category + keyword overlap
        cat_match = (article_category and article_category == arc.get('category', ''))
        
        match_score = 0.0
        if keyword_score >= 0.5:
            match_score = max(match_score, keyword_score)
        if entity_score >= 0.6:
            match_score = max(match_score, entity_score)
        if cat_match and keyword_score >= 0.4:
            match_score = max(match_score, 0.4 + (keyword_score * 0.5))
            
        if match_score >= threshold and match_score > best_score:
            best_score = match_score
            best_match = arc
            
    return (best_match, best_score)

def update_memory(memory: dict, articles: list) -> dict:
    """Update narrative memory with today's articles."""
    arcs = memory.get('arcs', [])
    now_iso = _get_now_iso()
    today_dt = datetime.now(timezone.utc)
    yesterday_dt = today_dt - timedelta(days=1)
    
    updated_arcs_today = set()
    
    for article in articles:
        matched_arc, confidence = match_article_to_arc(article, arcs)
        
        if matched_arc:
            matched_arc['last_seen'] = now_iso
            matched_arc['chapter_count'] = matched_arc.get('chapter_count', 0) + 1
            if 'chapter_titles' not in matched_arc:
                matched_arc['chapter_titles'] = []
            matched_arc['chapter_titles'].append(article.get('title', ''))
            
            source = article.get('source', '')
            if source:
                sources = set(matched_arc.get('sources_involved', []))
                sources.add(source)
                matched_arc['sources_involved'] = list(sources)
                
            updated_arcs_today.add(matched_arc.get('arc_id'))
            
        else:
            entities = article.get('entities', {})
            title = article.get('title', '')
            # Simple heuristic for action words
            action_words = {'says', 'plans', 'proposes', 'kills', 'attacks', 'signs', 'rejects', 'warns', 'agrees', 'fails'}
            has_action = any(word.lower() in action_words for word in title.split())
            
            entity_count = entities.get('entity_count', 0) if isinstance(entities, dict) else 0
            
            if entity_count >= 3 and has_action:
                # Build entity signature from the entities dict
                sig_parts = []
                if isinstance(entities, dict):
                    for c in entities.get('countries', [])[:3]:
                        sig_parts.append(c.get('code', str(c)) if isinstance(c, dict) else str(c))
                    for l in entities.get('leaders', [])[:2]:
                        sig_parts.append(l.get('name', str(l)) if isinstance(l, dict) else str(l))
                    for o in entities.get('organizations', [])[:2]:
                        sig_parts.append(o.get('name', str(o)) if isinstance(o, dict) else str(o))
                
                new_arc = {
                    "arc_id": str(uuid.uuid4()),
                    "title": title[:50] + "..." if len(title) > 50 else title,
                    "keywords": [w.lower() for w in title.split() if len(w) > 3][:10],
                    "entity_signature": ":".join(sig_parts[:5]),
                    "category": article.get('category', 'General'),
                    "regions": [article.get('region', 'Global')],
                    "first_seen": now_iso,
                    "last_seen": now_iso,
                    "chapter_count": 1,
                    "chapter_titles": [title],
                    "importance_trend": "new",
                    "peak_velocity": article.get('scores', {}).get('velocity', 1) if isinstance(article.get('scores'), dict) else 1,
                    "sources_involved": [article.get('source', '')] if article.get('source') else []
                }
                arcs.append(new_arc)
                updated_arcs_today.add(new_arc['arc_id'])
                
    # Update importance trend
    for arc in arcs:
        last_seen = _parse_iso(arc.get('last_seen', now_iso))
        days_since_seen = (today_dt - last_seen).days
        
        updated_today = arc.get('arc_id') in updated_arcs_today
        # Approximate 'updated yesterday' by checking if it was seen within last 48 hours but not today
        updated_recently = days_since_seen <= 1
        
        if updated_today and updated_recently:
            arc['importance_trend'] = 'rising'
        elif updated_today:
            arc['importance_trend'] = 'stable'
        elif days_since_seen >= 2:
            arc['importance_trend'] = 'fading'
            
    memory['arcs'] = arcs
    return memory

def prune_stale_arcs(memory: dict, max_age_days: int = 14) -> dict:
    """Remove arcs that haven't been updated in max_age_days.
    Keep at most 100 arcs to prevent unbounded growth.
    """
    arcs = memory.get('arcs', [])
    now = datetime.now(timezone.utc)
    
    active_arcs = []
    for arc in arcs:
        last_seen = _parse_iso(arc.get('last_seen', _get_now_iso()))
        if (now - last_seen).days <= max_age_days:
            active_arcs.append(arc)
            
    # Sort by recentness and chapter count, keep top 100
    active_arcs.sort(key=lambda x: (_parse_iso(x.get('last_seen', _get_now_iso())), x.get('chapter_count', 0)), reverse=True)
    memory['arcs'] = active_arcs[:100]
    
    return memory

def get_active_arcs(memory: dict) -> list:
    """Return arcs updated in the last 7 days, sorted by chapter_count desc."""
    arcs = memory.get('arcs', [])
    now = datetime.now(timezone.utc)
    
    recent_arcs = []
    for arc in arcs:
        last_seen = _parse_iso(arc.get('last_seen', _get_now_iso()))
        if (now - last_seen).days <= 7:
            recent_arcs.append(arc)
            
    recent_arcs.sort(key=lambda x: x.get('chapter_count', 0), reverse=True)
    return recent_arcs
