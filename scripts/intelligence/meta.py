# Copyright (c) 2026 Kashish Bhushan — News Colossal
import re
from datetime import datetime

POSITIVE_SIGNALS = ['success', 'win', 'victory', 'breakthrough', 'record', 'boost',
                    'growth', 'progress', 'achievement', 'landmark', 'historic',
                    'celebrates', 'praised', 'welcome', 'relief', 'optimism']
NEGATIVE_SIGNALS = ['fail', 'crisis', 'threat', 'danger', 'warn', 'slam',
                    'condemn', 'reject', 'oppose', 'fear', 'concern', 'alarm',
                    'criticism', 'backlash', 'controversy', 'risk', 'collapse']
NEUTRAL_SIGNALS = ['announce', 'report', 'state', 'confirm', 'plan', 'propose']

SOURCE_DOMAIN_AUTHORITY = {
    'BBC News': {'geopolitics': 0.9, 'technology': 0.6, 'health': 0.8, 'economics': 0.7, 'default': 0.75},
    'Reuters': {'geopolitics': 0.95, 'economics': 0.9, 'technology': 0.7, 'default': 0.85},
    'The Guardian': {'rights': 0.9, 'climate': 0.85, 'geopolitics': 0.8, 'default': 0.75},
    'Al Jazeera': {'geopolitics': 0.85, 'rights': 0.8, 'default': 0.7},
    'TechCrunch': {'technology': 0.9, 'economics': 0.5, 'default': 0.45},
    'Ars Technica': {'technology': 0.92, 'science': 0.85, 'default': 0.5},
    'NYT': {'geopolitics': 0.9, 'governance': 0.85, 'economics': 0.8, 'default': 0.8},
    'New York Times': {'geopolitics': 0.9, 'governance': 0.85, 'economics': 0.8, 'default': 0.8},
    'NPR': {'governance': 0.85, 'rights': 0.8, 'default': 0.7},
    'CNBC': {'economics': 0.9, 'technology': 0.65, 'default': 0.6},
    'Hindustan Times': {'geopolitics': 0.7, 'governance': 0.75, 'default': 0.6},
    'The Hindu': {'governance': 0.8, 'rights': 0.75, 'default': 0.65},
    'Indian Express': {'governance': 0.75, 'default': 0.6},
    'SCMP': {'geopolitics': 0.8, 'economics': 0.75, 'default': 0.65},
    'France 24': {'geopolitics': 0.75, 'default': 0.6},
    'DW News': {'geopolitics': 0.7, 'climate': 0.75, 'default': 0.6},
}

def _init_meta(article: dict) -> None:
    if 'meta' not in article:
        article['meta'] = {}

def _calc_sentiment_polarity(text: str) -> float:
    text_lower = text.lower()
    pos_count = sum(1 for word in POSITIVE_SIGNALS if word in text_lower)
    neg_count = sum(1 for word in NEGATIVE_SIGNALS if word in text_lower)
    total = pos_count + neg_count
    if total == 0:
        return 0.0
    return (pos_count - neg_count) / total

def detect_contrarian_signals(articles: list) -> list:
    """Find articles within clusters that have divergent sentiment."""
    clusters = {}
    for i, article in enumerate(articles):
        _init_meta(article)
        cluster = article.get('storyCluster')
        if cluster is not None and isinstance(cluster, dict):
            cid = id(cluster)
            if cid not in clusters:
                clusters[cid] = []
            clusters[cid].append((i, article))
            
    for cluster_id, cluster_articles in clusters.items():
        if len(cluster_articles) < 2:
            continue
            
        polarities = []
        for i, article in cluster_articles:
            text = f"{article.get('title', '')} {article.get('description', '')}"
            polarity = _calc_sentiment_polarity(text)
            polarities.append((polarity, i))
            
        if not polarities:
            continue
            
        polarities.sort(key=lambda x: x[0])
        min_pol, min_idx = polarities[0]
        max_pol, max_idx = polarities[-1]
        
        divergence = max_pol - min_pol
        if divergence > 0.5:
            # Mark cluster as contested
            for _, idx in polarities:
                articles[idx]['meta']['cluster_contested'] = True
                
            # Assume majority is closer to median
            median_pol = polarities[len(polarities)//2][0]
            for pol, idx in polarities:
                if abs(pol - median_pol) > 0.4:
                    articles[idx]['meta']['is_contrarian'] = True
                    articles[idx]['meta']['sentiment_divergence'] = divergence
                    
    return articles

def detect_black_swans(articles: list) -> list:
    """Flag articles that don't match any existing pattern."""
    crisis_words = {'crisis', 'collapse', 'war', 'attack', 'crash', 'pandemic', 'emergency', 'unprecedented'}
    
    for article in articles:
        _init_meta(article)
        criteria_met = 0
        
        # 1. High rarity score (0-1 scale, > 0.7 is rare)
        rarity = article.get('scores', {}).get('rarity', 0.5)
        if rarity > 0.7:
            criteria_met += 1
            
        # 2. Unusual entity combinations (high entity count with high rarity)
        entities = article.get('entities', {})
        entity_count = entities.get('entity_count', 0) if isinstance(entities, dict) else 0
        if entity_count >= 3 and rarity > 0.6:
            criteria_met += 1
            
        # 3. High entity density
        if entity_count >= 5:
            criteria_met += 1
            
        # 4. Singleton (not clustered)
        if article.get('storyCluster') is None:
            criteria_met += 1
            
        # 5. Contains crisis words
        title_desc = f"{article.get('title', '')} {article.get('description', '')}".lower()
        if any(word in title_desc for word in crisis_words):
            criteria_met += 1
            
        if criteria_met >= 3:
            article['meta']['is_black_swan'] = True
            article['meta']['black_swan_reason'] = 'Unusual entity combination + high rarity + crisis signal'
            
    return articles

def _flatten_entity_names(entities_dict):
    """Extract a flat list of entity name strings from the entities dict."""
    names = []
    if not isinstance(entities_dict, dict):
        return names
    for c in entities_dict.get('countries', []):
        if isinstance(c, dict):
            names.append(c.get('code', ''))
        else:
            names.append(str(c))
    for l in entities_dict.get('leaders', []):
        if isinstance(l, dict):
            names.append(l.get('name', ''))
        else:
            names.append(str(l))
    for o in entities_dict.get('organizations', []):
        if isinstance(o, dict):
            names.append(o.get('name', ''))
        else:
            names.append(str(o))
    for co in entities_dict.get('companies', []):
        if isinstance(co, dict):
            names.append(co.get('name', ''))
        else:
            names.append(str(co))
    return [n for n in names if n]


def detect_information_arbitrage(articles: list) -> list:
    """Find stories reported by only one region that no other region has picked up."""
    # Build entity index to check uniqueness
    all_entities = {}
    for i, article in enumerate(articles):
        entity_names = _flatten_entity_names(article.get('entities', {}))
        for entity in entity_names:
            if entity not in all_entities:
                all_entities[entity] = []
            all_entities[entity].append(i)
            
    for i, article in enumerate(articles):
        _init_meta(article)
        cluster = article.get('storyCluster')
        if cluster is not None:
            continue
            
        entity_names = _flatten_entity_names(article.get('entities', {}))
        
        if not entity_names:
            continue
            
        # Check if ZERO other articles share similar entities
        shared_count = 0
        for entity in entity_names:
            shared_count += len(all_entities.get(entity, [])) - 1
            
        if shared_count == 0:
            article['meta']['is_exclusive'] = True
            article['meta']['exclusive_signal'] = 'Only source covering this event'
            
    return articles

def compute_source_authority(article: dict) -> float:
    """Rate the source's credibility for the article's specific topic domain."""
    source = article.get('source', '')
    domain = article.get('category', '').lower()
    
    if not source or source not in SOURCE_DOMAIN_AUTHORITY:
        return 0.5
        
    source_domains = SOURCE_DOMAIN_AUTHORITY[source]
    return source_domains.get(domain, source_domains.get('default', 0.5))

def build_provenance_chain(articles: list) -> list:
    """Within each cluster, determine the provenance order."""
    clusters = {}
    for i, article in enumerate(articles):
        _init_meta(article)
        cluster = article.get('storyCluster')
        if cluster is not None and isinstance(cluster, dict):
            # Use id() of the shared cluster dict to group articles
            cid = id(cluster)
            if cid not in clusters:
                clusters[cid] = []
            clusters[cid].append((i, article))
            
    for cid, cluster_articles in clusters.items():
        if not cluster_articles:
            continue
            
        # Sort by pubDate
        def get_time(item):
            art = item[1]
            pub_date = art.get('pubDate', '')
            for fmt in ['%a, %d %b %Y %H:%M:%S %Z', '%a, %d %b %Y %H:%M:%S %z',
                         '%Y-%m-%dT%H:%M:%S.%fZ', '%Y-%m-%dT%H:%M:%S%z',
                         '%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%d %H:%M:%S']:
                try:
                    dt = datetime.strptime(pub_date, fmt)
                    # Strip timezone to avoid naive vs aware comparison
                    return dt.replace(tzinfo=None)
                except (ValueError, TypeError):
                    continue
            return datetime(2000, 1, 1)  # Far past fallback
                
        cluster_articles.sort(key=get_time)
        
        longest_desc = -1
        richest_idx = -1
        
        for rank, (idx, article) in enumerate(cluster_articles, start=1):
            article['meta']['provenance_rank'] = rank
            article['meta']['is_original_reporter'] = (rank == 1)
            
            desc_len = len(article.get('description', ''))
            if desc_len > longest_desc:
                longest_desc = desc_len
                richest_idx = idx
                
        if richest_idx != -1:
            articles[richest_idx]['meta']['has_richest_reporting'] = True
            
    return articles

def run_meta_intelligence(articles: list) -> list:
    """Orchestrate all Layer 3 analysis."""
    articles = detect_contrarian_signals(articles)
    articles = detect_black_swans(articles)
    articles = detect_information_arbitrage(articles)
    articles = build_provenance_chain(articles)
    
    for article in articles:
        _init_meta(article)
        auth = compute_source_authority(article)
        article['meta']['source_authority'] = auth
        
        base_score = article.get('importance_score', 1.0)
        
        if article['meta'].get('is_contrarian'):
            base_score += 1.0
        if article['meta'].get('is_black_swan'):
            base_score += 0.8
        if article['meta'].get('is_exclusive'):
            base_score += 0.5
        if article['meta'].get('is_original_reporter'):
            base_score += 0.3
        if article['meta'].get('has_richest_reporting'):
            base_score += 0.2
            
        base_score *= (0.7 + 0.3 * auth)
        article['importance_score'] = round(base_score, 2)
        
    # Audit counts
    contrarian_count = sum(1 for a in articles if a.get('meta', {}).get('is_contrarian'))
    black_swan_count = sum(1 for a in articles if a.get('meta', {}).get('is_black_swan'))
    exclusive_count = sum(1 for a in articles if a.get('meta', {}).get('is_exclusive'))
    original_count = sum(1 for a in articles if a.get('meta', {}).get('is_original_reporter'))
    
    print(f"\n  Meta-Intelligence Audit:")
    print(f"    Contrarian signals:    {contrarian_count}")
    print(f"    Black swan candidates: {black_swan_count}")
    print(f"    Information exclusives: {exclusive_count}")
    print(f"    Original reporters:    {original_count}")
    print(f"    Total articles scored: {len(articles)}")
    
    return articles
