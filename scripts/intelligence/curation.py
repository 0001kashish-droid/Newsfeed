# Copyright (c) 2026 Kashish Bhushan — News Colossal
# All Rights Reserved. Proprietary and confidential.
#
# LAYER 4: CURATION — Final ranking, cognitive diet balancing,
# narrative arc threading, and podcast<->news resonance bridging.

import re
from datetime import datetime, timezone
from collections import Counter, defaultdict


# ---------------------------------------------------------------------------
# Tokenizer (shared utility — same logic as existing pipeline)
# ---------------------------------------------------------------------------
_STOPWORDS = frozenset({
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
    'of', 'is', 'are', 'was', 'were', 'has', 'have', 'had', 'be', 'been',
    'being', 'will', 'would', 'could', 'should', 'may', 'might', 'do',
    'does', 'did', 'not', 'no', 'so', 'if', 'up', 'out', 'by', 'with',
    'from', 'as', 'into', 'its', 'it', 'this', 'that', 'than', 'then',
    'what', 'when', 'where', 'who', 'how', 'all', 'each', 'new', 'says',
    'said', 'over', 'after', 'about', 'also', 'more', 'most', 'just',
    'now', 'can', 'very', 'like', 'get', 'us', 'uk', 'via', 'amid',
})
_TOKEN_RE = re.compile(r'[a-z0-9]+')


def _tokenize(text):
    """Extract meaningful lowercase tokens, removing stopwords."""
    raw = (text or '').lower()
    raw = re.sub(r'(?<!\w)a\.i\.(?!\w)', 'ai', raw)
    raw = re.sub(r'(?<!\w)e\.v\.(?!\w)', 'ev', raw)
    return [w for w in _TOKEN_RE.findall(raw)
            if (len(w) > 2 or w in {'ai', 'ev'}) and w not in _STOPWORDS]


# ---------------------------------------------------------------------------
# 4A. COMPOSITE RANKING
# ---------------------------------------------------------------------------
def rank_articles(articles):
    """Sort articles by importance_score descending.

    Also assigns a human-readable rank field to each article.
    """
    # Use importance_score (set by Layer 2 + Layer 3 boosts)
    articles.sort(
        key=lambda a: a.get('importance_score', 0),
        reverse=True
    )
    for i, art in enumerate(articles):
        art['rank'] = i + 1
    return articles


# ---------------------------------------------------------------------------
# 4B. COGNITIVE DIET BALANCER
# ---------------------------------------------------------------------------
# Maximum fraction any single cognitive type can occupy in top N
_MAX_COGNITIVE_FRACTION = 0.35
# Minimum types that should appear in top 20
_MIN_COGNITIVE_DIVERSITY = 3


def cognitive_diet_balance(articles, top_n=20):
    """Ensure the top N articles have cognitive diversity.

    If one cognitive type dominates (>35% of top N), demote the weakest
    articles of that type to make room for underrepresented types.
    This preserves the overall ranking but nudges diversity at the top.
    """
    if len(articles) <= top_n:
        return articles

    top = articles[:top_n]
    rest = articles[top_n:]

    type_counts = Counter(a.get('cognitive_type', 'general') for a in top)
    max_allowed = int(top_n * _MAX_COGNITIVE_FRACTION)

    # Find overrepresented types
    demoted = []
    for ctype, count in type_counts.items():
        if count > max_allowed:
            # Sort articles of this type by importance (ascending) to find weakest
            typed_in_top = [a for a in top if a.get('cognitive_type') == ctype]
            typed_in_top.sort(key=lambda a: a.get('importance_score', 0))
            excess = count - max_allowed
            # Demote the weakest excess articles
            for a in typed_in_top[:excess]:
                demoted.append(a)

    if not demoted:
        return articles

    # Remove demoted from top, add to rest
    demoted_ids = {id(a) for a in demoted}
    top = [a for a in top if id(a) not in demoted_ids]

    # Find promotion candidates from rest that are of underrepresented types
    represented_types = set(a.get('cognitive_type', 'general') for a in top)
    underrepresented = [a for a in rest
                        if a.get('cognitive_type', 'general') not in represented_types
                        or type_counts.get(a.get('cognitive_type', 'general'), 0) < 2]

    # Promote the best underrepresented articles
    underrepresented.sort(key=lambda a: a.get('importance_score', 0), reverse=True)
    promotions = underrepresented[:len(demoted)]

    promoted_ids = {id(a) for a in promotions}
    rest = [a for a in rest if id(a) not in promoted_ids]
    rest.extend(demoted)

    top.extend(promotions)
    top.sort(key=lambda a: a.get('importance_score', 0), reverse=True)
    rest.sort(key=lambda a: a.get('importance_score', 0), reverse=True)

    result = top + rest
    # Re-assign ranks
    for i, art in enumerate(result):
        art['rank'] = i + 1

    # Audit
    new_types = Counter(a.get('cognitive_type', 'general') for a in result[:top_n])
    print(f"\n  Cognitive Diet Balance:")
    print(f"    Demoted {len(demoted)} articles, promoted {len(promotions)}")
    print(f"    Top-{top_n} cognitive spread: {dict(new_types)}")

    return result


# ---------------------------------------------------------------------------
# 4C. NARRATIVE ARC THREADING
# ---------------------------------------------------------------------------
def thread_narratives(articles, memory):
    """Enrich articles with narrative arc metadata from memory.

    For each article that matched a narrative arc during memory update,
    add human-readable arc context.
    """
    empty_arc_struct = {
        'arc_id': None,
        'arc_title': None,
        'day_number': 0,
        'total_chapters': 0,
        'importance_trend': None
    }

    if not memory or not memory.get('arcs'):
        for art in articles:
            art['narrative_arc'] = dict(empty_arc_struct)
        return articles

    arcs_by_id = {arc['arc_id']: arc for arc in memory.get('arcs', [])}

    for art in articles:
        matched_arc_id = art.get('_matched_arc_id')
        if not matched_arc_id and memory.get('arcs'):
            try:
                from intelligence.memory import match_article_to_arc
                fallback_arc, _ = match_article_to_arc(art, memory.get('arcs', []))
                if fallback_arc:
                    matched_arc_id = fallback_arc.get('arc_id')
            except Exception:
                pass

        if matched_arc_id and matched_arc_id in arcs_by_id:
            arc = arcs_by_id[matched_arc_id]
            # Calculate day number
            try:
                first_seen = arc.get('first_seen')
                if first_seen and isinstance(first_seen, str):
                    first = datetime.fromisoformat(first_seen.replace('Z', '+00:00'))
                    now = datetime.now(timezone.utc)
                    day_num = max(1, (now - first).days + 1)
                else:
                    day_num = arc.get('chapter_count', 1)
            except Exception:
                day_num = arc.get('chapter_count', 1)

            art['narrative_arc'] = {
                'arc_id': arc['arc_id'],
                'arc_title': arc.get('title', 'Ongoing Story'),
                'day_number': day_num,
                'total_chapters': arc.get('chapter_count', 1),
                'importance_trend': arc.get('importance_trend', 'stable'),
                'previous_headlines': arc.get('chapter_titles', [])[-3:]
            }
        else:
            art['narrative_arc'] = dict(empty_arc_struct)

    # Audit
    threaded = [a for a in articles if a.get('narrative_arc', {}).get('arc_id') is not None]
    print(f"\n  Narrative Threading:")
    print(f"    {len(threaded)} articles connected to ongoing arcs")
    if threaded:
        arc_names = Counter(a['narrative_arc']['arc_title'] for a in threaded)
        for name, count in arc_names.most_common(5):
            print(f"      '{name}': {count} articles")

    return articles


# ---------------------------------------------------------------------------
# 4D. PODCAST <-> NEWS RESONANCE
# ---------------------------------------------------------------------------
def cross_link_resonance(articles, podcasts, threshold=0.30):
    """Find topical bridges between podcast episodes and news articles.

    When a podcast episode discusses the same topic as a news article,
    create bidirectional links. Uses Jaccard similarity on title tokens
    plus entity overlap.

    Enriches:
    - article['resonant_podcast'] = {title, podcast, link, relevance} or None
    - episode['resonant_news'] = [{title, source, link, relevance}, ...] or []
    """
    if not podcasts:
        for art in articles:
            art.setdefault('resonant_podcast', None)
        return articles, podcasts

    # Tokenize all podcast titles
    podcast_tokens = {}
    podcast_entities = {}
    for ep in podcasts:
        ep_title = ep.get('title', '')
        ep_topics = ep.get('topics', [])
        ep_theme = ep.get('theme', '')
        # Combine title + topics + theme for richer matching
        combined = f"{ep_title} {' '.join(ep_topics)} {ep_theme}"
        podcast_tokens[ep.get('id', '')] = set(_tokenize(combined))
        # Extract simple entity-like tokens from topics
        podcast_entities[ep.get('id', '')] = set(
            t.lower() for t in (ep_topics or []) if (len(t) > 2 or t.lower() in {'ai', 'ev'})
        )

    # Tokenize all article titles + annotation
    article_tokens = {}
    for art in articles:
        title = art.get('title') or ''
        annotation = art.get('annotation') or {}
        what = annotation.get('what', '') if isinstance(annotation, dict) else ''
        desc = art.get('description') or ''
        combined = f"{title} {what} {desc}"
        article_tokens[art.get('id', '')] = set(_tokenize(combined))

    # Find resonances
    resonance_count = 0
    for art in articles:
        art_id = art.get('id', '')
        art_toks = article_tokens.get(art_id, set())
        if not art_toks:
            art['resonant_podcast'] = None
            continue

        best_match = None
        best_score = 0.0

        for ep in podcasts:
            ep_id = ep.get('id', '')
            ep_toks = podcast_tokens.get(ep_id, set())
            if not ep_toks:
                continue

            # Jaccard similarity
            intersection = art_toks & ep_toks
            union = art_toks | ep_toks
            jaccard = len(intersection) / len(union) if union else 0.0

            # Entity/topic bonus
            ep_ents = podcast_entities.get(ep_id, set())
            art_domains = set()
            entities = art.get('entities')
            if isinstance(entities, dict):
                for ent_list in [entities.get('domains', []),
                                 entities.get('actions', [])]:
                    if isinstance(ent_list, list):
                        art_domains.update(str(d).lower() for d in ent_list if d)

            entity_overlap = len(ep_ents & art_domains) / max(len(ep_ents | art_domains), 1) if (ep_ents or art_domains) else 0.0

            # Combined score (weighted): require jaccard > 0 to prevent false positives on disjoint stories
            if jaccard > 0:
                combined_score = jaccard * 0.6 + entity_overlap * 0.4
            else:
                combined_score = 0.0

            if combined_score > best_score and combined_score >= threshold:
                best_score = combined_score
                best_match = ep

        if best_match:
            art['resonant_podcast'] = {
                'id': best_match.get('id', ''),
                'title': best_match.get('title', ''),
                'episode_title': best_match.get('title', ''),
                'podcast': best_match.get('podcast', ''),
                'podcast_title': best_match.get('podcast', ''),
                'link': best_match.get('link', ''),
                'youtube_url': best_match.get('link', ''),
                'relevance': round(best_score, 3),
                'resonance_score': round(best_score, 3)
            }
            resonance_count += 1

            # Bidirectional: add to podcast's resonant_news
            if 'resonant_news' not in best_match or not isinstance(best_match['resonant_news'], list):
                best_match['resonant_news'] = []
            existing_news_ids = {n.get('id') for n in best_match['resonant_news'] if isinstance(n, dict)}
            if art.get('id') not in existing_news_ids:
                best_match['resonant_news'].append({
                    'id': art.get('id', ''),
                    'title': art.get('title', ''),
                    'source': art.get('source', ''),
                    'link': art.get('link', ''),
                    'url': art.get('link', ''),
                    'relevance': round(best_score, 3),
                    'resonance_score': round(best_score, 3)
                })
        else:
            art['resonant_podcast'] = None

    # Ensure all podcasts have the field
    for ep in podcasts:
        if not isinstance(ep.get('resonant_news'), list):
            ep['resonant_news'] = []

    # Audit
    print(f"\n  Podcast <-> News Resonance:")
    print(f"    {resonance_count} news articles linked to podcast episodes")
    podcasts_with_links = sum(1 for ep in podcasts if ep.get('resonant_news'))
    print(f"    {podcasts_with_links} podcast episodes linked to news stories")

    return articles, podcasts


# ---------------------------------------------------------------------------
# 4E. TOP-N SELECTION
# ---------------------------------------------------------------------------
def select_final(articles, max_articles=150):
    """Final selection gate. Keeps top N articles by rank.

    Also ensures minimum representation:
    - At least 2 articles per category (if available)
    - At least 1 article per region (if available)
    """
    if len(articles) <= max_articles:
        return articles

    # Guarantee minimums first
    guaranteed = []
    guaranteed_ids = set()

    # Ensure category representation
    by_category = defaultdict(list)
    for art in articles:
        by_category[art.get('category', 'World')].append(art)

    for cat, cat_arts in by_category.items():
        cat_arts.sort(key=lambda a: a.get('importance_score', 0), reverse=True)
        for art in cat_arts[:2]:
            if art.get('id') not in guaranteed_ids:
                guaranteed.append(art)
                guaranteed_ids.add(art.get('id'))

    # Ensure region representation
    by_region = defaultdict(list)
    for art in articles:
        by_region[art.get('region', 'Global')].append(art)

    for reg, reg_arts in by_region.items():
        reg_arts.sort(key=lambda a: a.get('importance_score', 0), reverse=True)
        if reg_arts[0].get('id') not in guaranteed_ids:
            guaranteed.append(reg_arts[0])
            guaranteed_ids.add(reg_arts[0].get('id'))

    # Fill remaining slots from ranked list
    remaining_slots = max_articles - len(guaranteed)
    for art in articles:
        if remaining_slots <= 0:
            break
        if art.get('id') not in guaranteed_ids:
            guaranteed.append(art)
            guaranteed_ids.add(art.get('id'))
            remaining_slots -= 1

    # Re-sort by importance
    guaranteed.sort(key=lambda a: a.get('importance_score', 0), reverse=True)
    for i, art in enumerate(guaranteed):
        art['rank'] = i + 1

    return guaranteed


# ---------------------------------------------------------------------------
# 4F. MASTER ORCHESTRATOR — LAYER 4
# ---------------------------------------------------------------------------
def run_curation(articles, podcasts=None, memory=None):
    """Orchestrate the complete Layer 4 curation pipeline.

    Steps:
    1. Rank articles by composite importance score
    2. Balance cognitive diet in top-20
    3. Thread narrative arcs from memory
    4. Cross-link podcast <-> news resonance
    5. Final selection (top N with guaranteed representation)

    Returns: (curated_articles, enriched_podcasts, curation_stats)
    """
    print("\n" + "=" * 60)
    print("LAYER 4: CURATION & FINAL RANKING")
    print("=" * 60)

    # Step 1: Rank
    articles = rank_articles(articles)
    top5 = [a.get('importance_score', 0) for a in articles[:5]]
    print(f"\n  Initial ranking complete. Top 5 scores: {top5}")

    # Step 2: Cognitive diet
    articles = cognitive_diet_balance(articles, top_n=20)

    # Step 3: Narrative threading
    articles = thread_narratives(articles, memory)

    # Step 4: Podcast resonance
    if podcasts:
        articles, podcasts = cross_link_resonance(articles, podcasts)
    else:
        for art in articles:
            art.setdefault('resonant_podcast', None)
        podcasts = podcasts or []

    # Step 5: Final selection
    articles = select_final(articles, max_articles=150)

    # Build stats
    curation_stats = {
        'final_count': len(articles),
        'cognitive_distribution': dict(Counter(
            a.get('cognitive_type', 'general') for a in articles[:20]
        )),
        'narrative_threaded': sum(
            1 for a in articles
            if a.get('narrative_arc', {}).get('arc_id') is not None
        ),
        'podcast_resonances': sum(
            1 for a in articles if a.get('resonant_podcast') is not None
        ),
        'top_5_scores': [round(a.get('importance_score', 0), 2)
                         for a in articles[:5]],
        'categories': dict(Counter(a.get('category', 'World') for a in articles)),
        'regions': dict(Counter(a.get('region', 'Global') for a in articles)),
    }

    print(f"\n  Final output: {curation_stats['final_count']} articles")
    print(f"  Categories: {curation_stats['categories']}")
    print(f"  Regions: {curation_stats['regions']}")

    return articles, podcasts, curation_stats
