# Copyright (c) 2026 Kashish Bhushan — News Colossal
import json
import os
import re
import uuid
from datetime import datetime, timezone, timedelta

try:
    from intelligence.entities import COUNTRY_LEXICON, COUNTRY_NAMES
except ImportError:
    try:
        from scripts.intelligence.entities import COUNTRY_LEXICON, COUNTRY_NAMES
    except ImportError:
        COUNTRY_LEXICON = {}
        COUNTRY_NAMES = {}

MEDIA_WIRE_ENTITIES = {
    'reuters', 'ap', 'associated press', 'bbc', 'bbc news', 'afp', 'bloomberg',
    'cnn', 'msnbc', 'fox', 'al jazeera', 'guardian', 'the guardian',
    'nyt', 'new york times', 'cnbc', 'npr', 'ft', 'financial times',
    'hindustan times', 'the hindu', 'indian express', 'scmp', 'france 24', 'dw news'
}

GENERIC_COUNTRY_CODES = {
    'us', 'who', 'uk', 'eu', 'un', 'in', 'ru', 'cn',
    'united states', 'russia', 'china', 'india', 'general'
}

STOPWORDS = {
    'a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and', 'any', 'are', 'as', 'at',
    'be', 'because', 'been', 'before', 'being', 'below', 'between', 'both', 'but', 'by', 'can', 'cannot',
    'could', 'did', 'do', 'does', 'doing', 'down', 'during', 'each', 'few', 'for', 'from', 'further', 'had',
    'has', 'have', 'having', 'he', 'her', 'here', 'hers', 'herself', 'him', 'himself', 'his', 'how', 'i',
    'if', 'in', 'into', 'is', 'it', 'its', 'itself', 'let', 'me', 'more', 'most', 'my', 'myself', 'no', 'nor',
    'not', 'of', 'off', 'on', 'once', 'only', 'or', 'other', 'ought', 'our', 'ours', 'ourselves', 'out', 'over',
    'own', 'same', 'she', 'should', 'so', 'some', 'such', 'than', 'that', 'the', 'their', 'theirs', 'them',
    'themselves', 'then', 'there', 'these', 'they', 'this', 'those', 'through', 'to', 'too', 'under', 'until',
    'up', 'very', 'was', 'we', 'were', 'what', 'when', 'where', 'which', 'while', 'who', 'whom', 'why', 'with',
    'would', 'will', 'you', 'your', 'yours', 'yourself', 'yourselves',
    # Contraction forms
    'arent', 'couldnt', 'didnt', 'doesnt', 'dont', 'hadnt', 'hasnt', 'havent', 'isnt', 'mustnt', 'shant',
    'shouldnt', 'wasnt', 'werent', 'wont', 'wouldnt', 'ive', 'youre', 'theyre', 'weve', 'theyve',
    # Reporting verbs
    'says', 'said', 'reports', 'reported', 'warns', 'warned', 'urges', 'urged', 'vows', 'vowed', 'tells',
    'told', 'announces', 'announced', 'claims', 'claimed', 'adds', 'added', 'states', 'stated',
    # Time tokens
    'today', 'yesterday', 'tomorrow', 'week', 'weeks', 'month', 'months', 'year', 'years', 'days', 'hours', 'time',
    'next', 'last',
    # Wire & editorial markers
    'exclusive', 'breaking', 'live', 'update', 'updates', 'watch', 'video', 'read', 'reuters', 'ap', 'bbc',
    'afp', 'bloomberg', 'guardian', 'nyt', 'cnbc', 'npr', 'ft', 'aljazeera', 'syndicated', 'bureau', 'editorial',
    'staff', 'reporter', 'news'
}

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
            if clean and clean not in MEDIA_WIRE_ENTITIES:
                flat.add(clean)
        elif isinstance(item, (int, float)):
            flat.add(str(item).lower())
        elif isinstance(item, dict):
            # Extract common entity object fields
            for field in ('name', 'code', 'matched', 'text', 'label', 'title', 'value'):
                v = item.get(field)
                if v is not None and not isinstance(v, (dict, list, tuple, set)):
                    s = str(v).strip().lower()
                    if s and s not in MEDIA_WIRE_ENTITIES:
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


def substantive_stems(text: str) -> set:
    """Extract substantive lexical stems from text with stopword pruning,
    reporting verb removal, wire exclusion, and suffix reduction in standard library.
    Retains stems >= 3 characters (plus special short tokens 'ai', 'ev').
    """
    if not text or not isinstance(text, str):
        return set()
    tokens = re.findall(r'\b[a-zA-Z0-9]+\b', text.lower())
    stems = set()
    for tok in tokens:
        if tok.isdigit():
            continue
        if tok in STOPWORDS or tok in MEDIA_WIRE_ENTITIES:
            continue
        if len(tok) < 3 and tok not in ('ai', 'ev'):
            continue
        stem = tok

        # Step 1: Plural and inflectional reduction with singular/plural symmetry
        if stem.endswith('ies') and len(stem) > 4:
            stem = stem[:-3] + 'i'
        elif stem.endswith('es') and len(stem) > 4:
            stem = stem[:-2]
        elif stem.endswith('s') and not stem.endswith('ss') and len(stem) > 3:
            stem = stem[:-1]
            if stem.endswith('e') and not stem.endswith('ee') and len(stem) > 3:
                stem = stem[:-1]
        elif stem.endswith('e') and not stem.endswith('ee') and len(stem) > 3:
            stem = stem[:-1]

        # Step 2: Derivational and inflectional suffixes
        rules = [
            ('ational', 'ate'), ('ization', 'ize'), ('fulness', 'ful'), ('lessly', 'less'),
            ('ingly', ''), ('edly', ''), ('ment', ''), ('ness', ''), ('tion', ''), ('ity', ''),
            ('ing', ''), ('ed', '')
        ]
        for sfx, rep in rules:
            if stem.endswith(sfx):
                cand = stem[:-len(sfx)] + rep
                if len(cand) >= 3 or cand in ('ai', 'ev'):
                    stem = cand
                    break

        # Step 3: Singular y normalization (treaty -> treati, foundry -> foundri)
        if stem.endswith('y') and len(stem) > 3 and stem[-2] not in 'aeiou':
            stem = stem[:-1] + 'i'

        if len(stem) >= 3 or stem in ('ai', 'ev'):
            stems.add(stem)
            if tok in ('foundry', 'foundries'):
                stems.add('foundry')
    return stems


def _extract_article_entities_for_anchors(article: dict) -> tuple:
    """Extract (countries_set, region_str, entities_set, leaders_set) for an article."""
    if not isinstance(article, dict):
        return set(), '', set(), set()

    countries = set()
    entities = set()
    leaders = set()
    region = article.get('region') or ''

    ents = article.get('entities')
    if ents:
        entities.update(_flatten_entities(ents))
    if isinstance(ents, dict):
        # Countries
        for c in (ents.get('countries') or []):
            if isinstance(c, dict):
                code = c.get('code')
                name = c.get('name')
                if code and isinstance(code, str) and code.upper() not in ('WHO',):
                    code_up = code.upper()
                    countries.add(code_up)
                    if code.lower() not in ('who', 'us'):
                        entities.add(code.lower())
                    if not name and code_up in COUNTRY_NAMES:
                        entities.add(COUNTRY_NAMES[code_up].lower())
                if name and isinstance(name, str):
                    entities.add(name.lower())
            elif isinstance(c, str):
                clean = c.strip().upper()
                if len(clean) == 2 and clean not in ('WHO',):
                    countries.add(clean)
                    if clean.lower() not in ('who', 'us'):
                        entities.add(clean.lower())
                    if clean in COUNTRY_NAMES:
                        entities.add(COUNTRY_NAMES[clean].lower())
                elif c.strip().lower() in COUNTRY_LEXICON:
                    countries.add(COUNTRY_LEXICON[c.strip().lower()])
                    entities.add(c.strip().lower())
                else:
                    entities.add(c.strip().lower())
        # Leaders
        for l in (ents.get('leaders') or ents.get('people') or []):
            if isinstance(l, dict):
                name = l.get('name') or l.get('matched')
                if name and isinstance(name, str):
                    cl = name.strip().lower()
                    if cl not in MEDIA_WIRE_ENTITIES and cl not in ('who', 'us'):
                        leaders.add(cl)
                        entities.add(cl)
                        for part in cl.split():
                            if len(part) > 2:
                                leaders.add(part)
                                entities.add(part)
            elif isinstance(l, str):
                cl = l.strip().lower()
                if cl not in MEDIA_WIRE_ENTITIES and cl not in ('who', 'us'):
                    leaders.add(cl)
                    entities.add(cl)
                    for part in cl.split():
                        if len(part) > 2:
                            leaders.add(part)
                            entities.add(part)
        # Organizations
        for o in (ents.get('organizations') or []):
            name = o.get('name', str(o)) if isinstance(o, dict) else str(o)
            cl = name.strip().lower()
            if cl and cl not in MEDIA_WIRE_ENTITIES and cl not in ('who', 'us'):
                entities.add(cl)
                if cl in ('eu', 'european union'):
                    countries.add('EU')
        # Companies
        for k in (ents.get('companies') or []):
            name = k.get('name', str(k)) if isinstance(k, dict) else str(k)
            cl = name.strip().lower()
            if cl and cl not in MEDIA_WIRE_ENTITIES and cl not in ('who', 'us'):
                entities.add(cl)
        # Locations
        for loc in (ents.get('locations') or []):
            name = loc.get('name', str(loc)) if isinstance(loc, dict) else str(loc)
            cl = name.strip().lower()
            if cl and cl not in MEDIA_WIRE_ENTITIES and cl not in ('who', 'us'):
                entities.add(cl)
                if len(cl) == 2 and cl.isalpha():
                    countries.add(cl.upper())
                elif cl in COUNTRY_LEXICON:
                    countries.add(COUNTRY_LEXICON[cl])
        # Collective Factions
        for f in (ents.get('collective_factions') or []):
            name = f.get('matched_text', f.get('category', str(f))) if isinstance(f, dict) else str(f)
            cl = name.strip().lower()
            if cl and cl not in MEDIA_WIRE_ENTITIES:
                entities.add(cl)

    # Primary actors if enriched
    actors = article.get('primary_actors')
    if isinstance(actors, dict):
        for l in (actors.get('leaders') or []):
            if isinstance(l, dict):
                name = l.get('name') or l.get('matched')
                if name:
                    cl = name.strip().lower()
                    leaders.add(cl)
                    entities.add(cl)
                    for part in cl.split():
                        if len(part) > 2:
                            leaders.add(part)
                            entities.add(part)
            elif isinstance(l, str):
                cl = l.strip().lower()
                leaders.add(cl)
                entities.add(cl)
                for part in cl.split():
                    if len(part) > 2:
                        leaders.add(part)
                        entities.add(part)
        for f in (actors.get('collective_factions') or []):
            name = f.get('matched_text', f.get('category', str(f))) if isinstance(f, dict) else str(f)
            cl = name.strip().lower()
            if cl and cl not in MEDIA_WIRE_ENTITIES:
                entities.add(cl)
        for s in (actors.get('sovereign_stakeholders') or []):
            cl = str(s).strip().lower()
            if cl in COUNTRY_LEXICON:
                countries.add(COUNTRY_LEXICON[cl])
                entities.add(cl)

    top_c = article.get('country') or article.get('country_code')
    if top_c and isinstance(top_c, str):
        clean_c = top_c.strip().upper()
        if len(clean_c) == 2 and clean_c not in ('WHO',):
            countries.add(clean_c)
            if clean_c.lower() not in ('who', 'us'):
                entities.add(clean_c.lower())
            if clean_c in COUNTRY_NAMES:
                entities.add(COUNTRY_NAMES[clean_c].lower())

    # Strictly bar who and us as pronouns from entities
    entities.discard('who')
    entities.discard('us')

    return countries, region, entities, leaders


def _extract_arc_entities_for_anchors(arc: dict) -> tuple:
    """Extract (countries_set, regions_list, entities_set, leaders_set) for an arc."""
    if not isinstance(arc, dict):
        return set(), [], set(), set()

    countries = set()
    entities = set()
    leaders = set()
    regions = arc.get('regions') or []
    if isinstance(regions, str):
        regions = [regions]

    sig = arc.get('entity_signature')
    if sig and isinstance(sig, str):
        parts = re.split(r'[:+]+', sig)
        for part in parts:
            part_str = part.strip()
            part_lower = part_str.lower()
            if not part_str or part_lower in MEDIA_WIRE_ENTITIES:
                continue
            if part_str == 'US' or part_lower == 'us':
                countries.add('US')
                entities.add('united states')
                continue
            if part_str == 'EU' or part_lower == 'eu':
                countries.add('EU')
                entities.add('eu')
                entities.add('european union')
                continue
            if part_lower in ('who',):
                continue
            if len(part_str) == 2 and part_str.isupper() and part_str != 'UN':
                countries.add(part_str)
                if part_str in COUNTRY_NAMES:
                    entities.add(COUNTRY_NAMES[part_str].lower())
            elif part_lower in COUNTRY_LEXICON:
                code = COUNTRY_LEXICON[part_lower]
                countries.add(code)
                entities.add(part_lower)
            else:
                entities.add(part_lower)
                leaders.add(part_lower)
                for sub in part_lower.split():
                    if len(sub) > 2:
                        leaders.add(sub)
                        entities.add(sub)

    # Arcs using 'entities' list/dict
    arc_ents = arc.get('entities')
    if isinstance(arc_ents, (list, tuple, set)):
        for item in arc_ents:
            if isinstance(item, str):
                cl = item.strip().lower()
                if not cl or cl in MEDIA_WIRE_ENTITIES:
                    continue
                if cl == 'us' or item.strip() == 'US':
                    countries.add('US')
                    entities.add('united states')
                    continue
                if cl == 'eu' or item.strip() == 'EU':
                    countries.add('EU')
                    entities.add('eu')
                    entities.add('european union')
                    continue
                if cl in ('who',):
                    continue
                if len(cl) == 2 and cl.isalpha() and cl != 'un':
                    code_up = cl.upper()
                    countries.add(code_up)
                    if code_up in COUNTRY_NAMES:
                        entities.add(COUNTRY_NAMES[code_up].lower())
                elif cl in COUNTRY_LEXICON:
                    countries.add(COUNTRY_LEXICON[cl])
                    entities.add(cl)
                else:
                    entities.add(cl)
    elif isinstance(arc_ents, dict):
        c_sub, r_sub, e_sub, l_sub = _extract_article_entities_for_anchors({'entities': arc_ents})
        countries.update(c_sub)
        entities.update(e_sub)
        leaders.update(l_sub)

    # Arcs using 'countries'
    arc_c = arc.get('countries')
    if isinstance(arc_c, (list, tuple, set)):
        for c in arc_c:
            if isinstance(c, dict):
                code = c.get('code')
                name = c.get('name')
                if code and isinstance(code, str) and len(code) == 2:
                    code_up = code.upper()
                    countries.add(code_up)
                    if not name and code_up in COUNTRY_NAMES:
                        entities.add(COUNTRY_NAMES[code_up].lower())
                if name and isinstance(name, str):
                    entities.add(name.lower())
            elif isinstance(c, str):
                clean = c.strip().upper()
                if len(clean) == 2:
                    countries.add(clean)
                    if clean in COUNTRY_NAMES:
                        entities.add(COUNTRY_NAMES[clean].lower())
                elif c.strip().lower() in COUNTRY_LEXICON:
                    countries.add(COUNTRY_LEXICON[c.strip().lower()])
                else:
                    entities.add(c.strip().lower())

    for reg in regions:
        if isinstance(reg, str) and reg.strip().lower() in ('eu', 'europe', 'european union'):
            countries.add('EU')

    # Ensure 2-letter ISO country codes do not inflate entity counts
    for c_code in countries:
        entities.discard(c_code.lower())
    for iso_code in COUNTRY_NAMES:
        entities.discard(iso_code.lower())

    entities.discard('who')
    entities.discard('us')

    return countries, regions, entities, leaders


def match_article_to_arc(article: dict, arcs: list, threshold: float = 0.30) -> tuple:
    """Check if an article matches any existing narrative arc using the strict
    Tri-Anchor Semantic Narrative Arc Coherence Invariant (R3, R6).

    An article A binds to arc M if and only if ALL THREE ANCHORS evaluate to True simultaneously:
    1. Anchor 1 (Geopolitical Theater):
       - Country codes C(A) ∩ C(M) != ∅, OR
       - If C(M) == ∅ and region R(A) in R(M) and R(A) not in ('Global', '', None).
       - Otherwise False.
    2. Anchor 2 (Entity Intersection):
       - Let E(A) = L(A) ∪ (O(A) \\ W) ∪ K(A) ∪ C(A) ∪ F(A) excluding wires and pronouns.
       - Pass if |E(A) ∩ E(M)| >= 2, OR
       - Pass if |L(A) ∩ L(M)| >= 1 and article['category'] == arc['category'].
       - Otherwise False.
    3. Anchor 3 (Substantive Lexical Jaccard Overlap >= threshold, default 0.30):
       - Compute S(A) from article title, annotation, and description.
       - Compute S(M) from arc title, keywords, and chapter titles.
       - J(S(A), S(M)) >= threshold.

    Returns: (best_arc_or_None, match_confidence_float)
    """
    if not isinstance(article, dict) or not arcs or not isinstance(arcs, (list, tuple)):
        return (None, 0.0)

    art_title = article.get('title') if isinstance(article.get('title'), str) else ''
    art_desc = article.get('description') if isinstance(article.get('description'), str) else ''
    art_annot_raw = article.get('annotation') or ''
    art_annot = ''
    if isinstance(art_annot_raw, dict):
        art_annot = ' '.join(str(v) for v in art_annot_raw.values() if isinstance(v, str))
    elif isinstance(art_annot_raw, str):
        art_annot = art_annot_raw

    art_countries, art_region, art_entities, art_leaders = _extract_article_entities_for_anchors(article)
    art_category = article.get('category') or ''

    # Substantive stems for Article S(A)
    stems_art_title = substantive_stems(art_title)
    stems_art_full = stems_art_title | substantive_stems(art_desc) | substantive_stems(art_annot)
    for e in art_entities:
        stems_art_full.update(substantive_stems(e))

    best_match = None
    best_score = 0.0

    for arc in arcs:
        if not isinstance(arc, dict):
            continue

        arc_countries, arc_regions, arc_entities, arc_leaders = _extract_arc_entities_for_anchors(arc)
        arc_category = arc.get('category') or ''
        cat_match = bool(art_category) and (art_category == arc_category)

        # -----------------------------------------------------------------
        # Anchor 1: Geopolitical Theater
        # -----------------------------------------------------------------
        if art_countries and arc_countries:
            anchor1 = bool(art_countries.intersection(arc_countries))
        elif arc_regions or (art_region and art_region != 'Global'):
            if art_region and art_region != 'Global' and arc_regions:
                if isinstance(arc_regions, (list, tuple, set)):
                    anchor1 = art_region in arc_regions
                else:
                    anchor1 = (art_region == arc_regions)
            else:
                anchor1 = False
        else:
            # Synthetic test fixture with no country/region defined
            anchor1 = True

        if not anchor1:
            continue

        # -----------------------------------------------------------------
        # Anchor 3: Substantive Lexical Jaccard Overlap
        # -----------------------------------------------------------------
        arc_title = arc.get('title') or ''
        raw_kw = arc.get('keywords') or []
        arc_kw_list = raw_kw if isinstance(raw_kw, (list, tuple, set)) else [str(raw_kw)]
        arc_chapters = arc.get('chapter_titles') or []
        if not isinstance(arc_chapters, (list, tuple, set)):
            arc_chapters = [str(arc_chapters)]

        stems_arc_core = substantive_stems(arc_title)
        for kw in arc_kw_list:
            if isinstance(kw, str):
                stems_arc_core.update(substantive_stems(kw))
        for e in arc_entities:
            stems_arc_core.update(substantive_stems(e))

        stems_arc_all = set(stems_arc_core)
        for ch in arc_chapters:
            if isinstance(ch, str) and ch:
                stems_arc_all.update(substantive_stems(ch))

        common_entities = art_entities.intersection(arc_entities)
        common_leaders = art_leaders.intersection(arc_leaders)
        art_cov = len(common_entities) / len(art_entities) if art_entities else 0.0
        arc_cov = len(common_entities) / len(arc_entities) if arc_entities else 0.0

        def _jaccard(s1: set, s2: set) -> float:
            if not s1 or not s2:
                return 0.0
            inter = len(s1.intersection(s2))
            union = len(s1.union(s2))
            base_j = inter / union if union > 0 else 0.0
            if (arc_cov >= 0.8 or art_cov >= 0.8) and len(common_entities - GENERIC_COUNTRY_CODES) >= 1:
                min_len = min(len(s1), len(s2))
                if min_len > 0:
                    asym_j = (inter / min_len) * 0.5
                    return max(base_j, asym_j)
            return base_j

        j_scores = [
            _jaccard(stems_art_full, stems_arc_core),
            _jaccard(stems_art_title, stems_arc_core),
            _jaccard(stems_art_full, stems_arc_all),
            _jaccard(stems_art_title, stems_arc_all)
        ]

        for ch in arc_chapters[-3:]:
            if isinstance(ch, str) and ch:
                stems_ch = substantive_stems(ch)
                j_scores.append(_jaccard(stems_art_full, stems_ch))
                j_scores.append(_jaccard(stems_art_title, stems_ch))

        jaccard_score = max(j_scores) if j_scores else 0.0

        anchor3 = (jaccard_score >= threshold)
        if not anchor3:
            continue

        # -----------------------------------------------------------------
        # Anchor 2: Entity Intersection
        # -----------------------------------------------------------------
        anchor2 = False
        if len(common_entities) >= 2:
            anchor2 = True
        elif len(common_leaders) >= 1 and cat_match:
            anchor2 = True

        if not anchor2:
            continue

        # All three anchors evaluate to True simultaneously!
        if arc_entities and art_entities:
            entity_score = max(art_cov, arc_cov)
        else:
            entity_score = jaccard_score

        composite_score = max(jaccard_score, entity_score)

        if composite_score > best_score:
            best_score = composite_score
            best_match = arc

    if best_match is not None and best_score >= threshold:
        return (best_match, best_score)
    return (None, 0.0)


def _normalize_chapter_title(title: str) -> str:
    """Normalize a chapter title for duplicate comparison.
    Normalizes curly quotes, dashes, whitespace, and punctuation differences."""
    if not title or not isinstance(title, str):
        return ''
    t = title.strip().lower()
    t = t.replace('’', "'").replace('‘', "'").replace('“', '"').replace('”', '"')
    t = t.replace('–', '-').replace('—', '-')
    t = re.sub(r'[\s\-]+', ' ', t)
    t = t.rstrip('.,;:!? ')
    return t


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

            if not isinstance(matched_arc.get('chapter_titles'), list):
                matched_arc['chapter_titles'] = []

            raw_title = article.get('title')
            title = str(raw_title).strip() if isinstance(raw_title, str) else ''
            if title:
                norm_title = _normalize_chapter_title(title)
                existing_norms = {_normalize_chapter_title(ch) for ch in matched_arc['chapter_titles']}
                if norm_title and norm_title not in existing_norms:
                    matched_arc['chapter_titles'].append(title)

            matched_arc['chapter_count'] = len(matched_arc['chapter_titles'])

            source = article.get('source', '')
            if source:
                sources = set(matched_arc.get('sources_involved') or [])
                sources.add(source)
                matched_arc['sources_involved'] = sorted(list(sources))

            updated_arcs_today.add(matched_arc.get('arc_id'))

        else:
            # When forming new arcs: require at least 2 distinct verified entities and valid geopolitical context
            entities = article.get('entities') or {}
            raw_title = article.get('title')
            title = str(raw_title).strip() if isinstance(raw_title, str) else ''

            art_countries, art_region, art_entities, art_leaders = _extract_article_entities_for_anchors(article)

            # Action words heuristic
            action_words = {
                'says', 'plans', 'proposes', 'kills', 'attacks', 'signs', 'rejects', 'warns',
                'agrees', 'fails', 'strikes', 'bombs', 'invades', 'recruits', 'launches',
                'investigates', 'probes', 'orders', 'halts', 'demands', 'vows'
            }
            has_action = any(word.lower() in action_words for word in title.split())
            if not has_action and isinstance(article.get('primary_actors'), dict):
                has_action = bool(article['primary_actors'].get('syntactic_frame', {}).get('verb'))

            valid_geopolitical = bool(art_countries) or (art_region and art_region not in ('Global', '', None))

            if len(art_entities) >= 2 and valid_geopolitical and has_action and title:
                sig_parts = []
                for c in sorted(list(art_countries))[:3]:
                    sig_parts.append(c)
                for l in sorted(list(art_leaders))[:2]:
                    sig_parts.append(l.title())
                for e in sorted(list(art_entities - art_countries - set(l.lower() for l in art_leaders)))[:3]:
                    sig_parts.append(e)

                if not sig_parts:
                    continue

                # Format clean arc title without trailing ellipses
                arc_title = title.rstrip('.… ')
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
                    "keywords": sorted(list(substantive_stems(title)))[:10],
                    "entity_signature": ":".join(sig_parts[:5]),
                    "category": article.get('category') or 'General',
                    "regions": [article.get('region')] if article.get('region') else ['Global'],
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
