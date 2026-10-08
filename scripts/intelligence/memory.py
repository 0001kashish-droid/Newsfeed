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
    if not dt_str or not isinstance(dt_str, str):
        return datetime.now(timezone.utc)
    try:
        return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
    except (ValueError, TypeError, AttributeError):
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
            if not isinstance(data, dict):
                return {
                    "last_updated": _get_now_iso(),
                    "arcs": [],
                    "version": 2
                }
            if not isinstance(data.get("arcs"), list):
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

def _flatten_entities(entities) -> set:
    """Recursively flattens any entities data structure (categorized dictionary,
    list, set, tuple, or primitive) into a set of normalized lowercase entity tokens.
    
    Extracts all entity values regardless of category keys (e.g. 'people', 'organizations',
    'locations', 'countries', 'leaders', 'companies', 'domains', 'actions', etc.),
    skipping scalar metadata counters.
    """
    flat = set()
    if not entities:
        return flat

    def _add_item(item):
        if not item:
            return
        if isinstance(item, str):
            clean = item.strip().lower()
            if clean:
                flat.add(clean)
        elif isinstance(item, (int, float)):
            flat.add(str(item).lower())
        elif isinstance(item, dict):
            # Extract common entity object fields
            for field in ('name', 'code', 'matched', 'text', 'label', 'title', 'value'):
                v = item.get(field)
                if v is not None and not isinstance(v, (dict, list, tuple, set)):
                    s = str(v).strip().lower()
                    if s:
                        flat.add(s)
            # Recursively process other values in dict, ignoring scalar metadata counters
            for k, v in item.items():
                if k not in ('entity_count', 'entity_density', 'count', 'density'):
                    _add_item(v)
        elif isinstance(item, (list, tuple, set)):
            for sub in item:
                _add_item(sub)

    if isinstance(entities, dict):
        for k, v in entities.items():
            if k in ('entity_count', 'entity_density', 'count', 'density'):
                continue
            _add_item(v)
    elif isinstance(entities, (list, tuple, set)):
        for item in entities:
            _add_item(item)
    elif isinstance(entities, str):
        _add_item(entities)

    return flat


def match_article_to_arc(article: dict, arcs: list, threshold: float = 0.4) -> tuple:
    """Check if an article matches any existing narrative arc.
    
    Matching criteria (OR logic — any one is sufficient):
    1. >=50% keyword overlap between article title tokens and arc keywords
    2. Entity signature overlap >=60%
    3. Same category + >=40% keyword overlap
    
    Returns: (matched_arc_or_None, match_confidence_float)
    """
    if not isinstance(article, dict) or not arcs or not isinstance(arcs, (list, tuple)):
        return (None, 0.0)
    
    article_title_words = set(word.lower() for word in (article.get('title') or '').split() if len(word) > 2)
    
    # Flatten categorized entity dictionary into a set of normalized names & codes
    article_entities = _flatten_entities(article.get('entities'))
    article_category = article.get('category') or ''
    
    best_match = None
    best_score = 0.0
    
    for arc in arcs:
        if not isinstance(arc, dict):
            continue
        raw_kw = arc.get('keywords') or []
        if isinstance(raw_kw, (list, tuple, set)):
            arc_keywords = set(k.lower() for k in raw_kw if isinstance(k, str))
        else:
            arc_keywords = set()
        
        # 1. Keyword overlap
        keyword_overlap = len(article_title_words.intersection(arc_keywords))
        keyword_score = keyword_overlap / max(1, len(article_title_words))
        
        # 2. Entity overlap: support both arc['entities'] and arc['entity_signature']
        arc_entities = set()
        if arc.get('entities'):
            arc_entities.update(_flatten_entities(arc.get('entities')))
        if arc.get('entity_signature'):
            arc_sig = str(arc.get('entity_signature')).lower().replace('+', ':')
            arc_entities.update(k.strip() for k in arc_sig.split(':') if k.strip())
        
        if arc_entities and article_entities:
            entity_overlap = len(article_entities.intersection(arc_entities))
            arc_coverage = entity_overlap / len(arc_entities)
            art_coverage = entity_overlap / len(article_entities)
            entity_score = max(arc_coverage, art_coverage)
        else:
            entity_score = 0.0
        
        # 3. Category + keyword overlap
        arc_category = arc.get('category') or ''
        cat_match = bool(article_category) and (article_category == arc_category)
        
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
    if not isinstance(memory, dict):
        memory = {"arcs": []}
    if not isinstance(articles, (list, tuple)):
        articles = []
    arcs = memory.get('arcs') or []
    now_iso = _get_now_iso()
    today_dt = datetime.now(timezone.utc)
    yesterday_dt = today_dt - timedelta(days=1)
    
    updated_arcs_today = set()
    
    for article in articles:
        if not isinstance(article, dict):
            continue
        matched_arc, confidence = match_article_to_arc(article, arcs)
        
        if matched_arc:
            article['_matched_arc_id'] = matched_arc.get('arc_id')
            matched_arc['last_seen'] = now_iso
            matched_arc['chapter_count'] = (matched_arc.get('chapter_count') or 0) + 1
            if not isinstance(matched_arc.get('chapter_titles'), list):
                matched_arc['chapter_titles'] = []
            matched_arc['chapter_titles'].append(article.get('title') or '')
            
            source = article.get('source', '')
            if source:
                sources = set(matched_arc.get('sources_involved') or [])
                sources.add(source)
                matched_arc['sources_involved'] = list(sources)
                
            updated_arcs_today.add(matched_arc.get('arc_id'))
            
        else:
            entities = article.get('entities') or {}
            title = article.get('title') or ''
            # Simple heuristic for action words
            action_words = {'says', 'plans', 'proposes', 'kills', 'attacks', 'signs', 'rejects', 'warns', 'agrees', 'fails'}
            has_action = any(word.lower() in action_words for word in title.split())
            
            entity_count = (entities.get('entity_count') or 0) if isinstance(entities, dict) else 0
            
            if entity_count >= 3 and has_action:
                # Build entity signature from the entities dict
                sig_parts = []
                if isinstance(entities, dict):
                    for c in (entities.get('countries') or entities.get('locations') or [])[:3]:
                        sig_parts.append(c.get('code', c.get('name', str(c))) if isinstance(c, dict) else str(c))
                    for l in (entities.get('leaders') or entities.get('people') or [])[:2]:
                        sig_parts.append(l.get('name', l.get('matched', str(l))) if isinstance(l, dict) else str(l))
                    for o in (entities.get('organizations') or entities.get('companies') or [])[:2]:
                        sig_parts.append(o.get('name', o.get('matched', str(o))) if isinstance(o, dict) else str(o))
                if not sig_parts and isinstance(entities, (dict, list)):
                    sig_parts = list(_flatten_entities(entities))[:5]
                
                # Format clean arc title without trailing ellipses
                arc_title = title.strip().rstrip('.…')
                if len(arc_title) > 50:
                    cut = arc_title[:50]
                    last_space = cut.rfind(' ')
                    if last_space > 20:
                        arc_title = cut[:last_space].strip()
                    else:
                        arc_title = cut.strip()
                    arc_title = arc_title.rstrip('.,;:!?-\t ')
                
                new_arc_id = str(uuid.uuid4())
                new_arc = {
                    "arc_id": new_arc_id,
                    "title": arc_title,
                    "keywords": [w.lower() for w in title.split() if len(w) > 3][:10],
                    "entity_signature": ":".join(sig_parts[:5]),
                    "category": article.get('category') or 'General',
                    "regions": [article.get('region') or 'Global'],
                    "first_seen": now_iso,
                    "last_seen": now_iso,
                    "chapter_count": 1,
                    "chapter_titles": [title],
                    "importance_trend": "new",
                    "peak_velocity": (article.get('scores', {}).get('velocity') or 1) if isinstance(article.get('scores'), dict) else 1,
                    "sources_involved": [article.get('source', '')] if article.get('source') else []
                }
                arcs.append(new_arc)
                article['_matched_arc_id'] = new_arc_id
                updated_arcs_today.add(new_arc['arc_id'])
                
    # Update importance trend
    for arc in arcs:
        if not isinstance(arc, dict):
            continue
        last_seen = _parse_iso(arc.get('last_seen') or now_iso)
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
    if not isinstance(memory, dict):
        return {"arcs": []}
    arcs = memory.get('arcs') or []
    now = datetime.now(timezone.utc)
    
    active_arcs = []
    for arc in arcs:
        if not isinstance(arc, dict):
            continue
        last_seen = _parse_iso(arc.get('last_seen') or _get_now_iso())
        if (now - last_seen).days <= max_age_days:
            active_arcs.append(arc)
            
    # Sort by recentness and chapter count, keep top 100
    active_arcs.sort(
        key=lambda x: (_parse_iso(x.get('last_seen') or _get_now_iso()), x.get('chapter_count') or 0),
        reverse=True
    )
    memory['arcs'] = active_arcs[:100]
    
    return memory

def get_active_arcs(memory: dict) -> list:
    """Return arcs updated in the last 7 days, sorted by chapter_count desc."""
    if not isinstance(memory, dict):
        return []
    arcs = memory.get('arcs') or []
    now = datetime.now(timezone.utc)
    
    recent_arcs = []
    for arc in arcs:
        if not isinstance(arc, dict):
            continue
        last_seen = _parse_iso(arc.get('last_seen') or _get_now_iso())
        if (now - last_seen).days <= 7:
            recent_arcs.append(arc)
            
    recent_arcs.sort(key=lambda x: x.get('chapter_count') or 0, reverse=True)
    return recent_arcs
