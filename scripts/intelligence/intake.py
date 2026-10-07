# Copyright (c) 2026 Kashish Bhushan — News Colossal

import re
from typing import List, Tuple, Dict, Any

from intelligence.entities import extract_entities, compute_entity_signature

# 1. NOISE FILTER

# Hard Reject Patterns (article is completely removed)
HARD_REJECT_PATTERNS = [
    # Listicles & clickbait
    r'\b\d+\s+(things|ways|reasons|tips|hacks|tricks|facts)\b',
    r'\bbest\s+(deals|buys|products|gifts)\b',
    r'\bgift\s+guide\b',
    r'\bthings\s+you\s+need\s+to\s+know\b',
    
    # Entertainment noise
    r'\bhoroscope\b', r'\bcrossword\b', r'\bsudoku\b', r'\bpuzzle\b',
    r'\brecipe[s]?\b', r'\bcooking\s+tips\b',
    r'\breality\s+tv\b', r'\bkardashian\b',
    r'\btiktok\s+trend\b',
    
    # Promotional / affiliate
    r'\bsponsored\s+(content|post)\b', r'\baffiliate\b',
    r'\bpaid\s+partnership\b',
    r'\bcoupon\b', r'\bdiscount\s+code\b', r'\bsale\s+alert\b',
    r'\bshopping\s+guide\b',
    
    # Gallery/media format noise
    r'\bin\s+pictures\b', r'\bphoto\s+gallery\b',
    r'\bwatch\s+live\b',
    r'\bas\s+it\s+happened\b',
    r'\blive\s+updates\b', r'\blive\s+blog\b',
    
    # Meta/admin/newsletter
    r'\bnewsletter\s+signup\b',
    r'\bwhat\s+to\s+watch\b', r'\bstreaming\s+guide\b',
    r'\bbox\s+office\b',
    
    # Fluff
    r'\bviral\s+video\b', r'\bcute\s+animal\b',
    r'\bmeme[s]?\b',
    
    # Weather/traffic
    r'\bweather\s+forecast\b', r'\bpollen\s+count\b',
    r'\btraffic\s+update\b',
    
    # Quiz/interactive
    r'\bquiz\b', r'\btake\s+our\s+survey\b',
]

COMPILED_HARD_REJECT = [(p, re.compile(p, re.IGNORECASE)) for p in HARD_REJECT_PATTERNS]

# Soft Penalty Patterns (reduce score but don't reject)
SOFT_PENALTY_PATTERNS = [
    (r'\bopinion[:\s]\b', -0.15),
    (r'\bcommentary\b', -0.10),
    (r'\beditorial\b', -0.10),
    (r'\bletter[s]?\s+to\s+(the\s+)?editor\b', -0.20),
    (r'\bround-?up\b', -0.10),
    (r'\bcompilation\b', -0.15),
    (r'\bobituary\b', -0.05),
    (r'\bin\s+memoriam\b', -0.05),
    (r'\bmorning\s+briefing\b', -0.10),
    (r'\bevening\s+briefing\b', -0.10),
    (r'\bdaily\s+digest\b', -0.10),
    (r'\bpodcast\s*:', -0.05),
    (r'\bbook\s+review\b', -0.08),
]

COMPILED_SOFT_PENALTY = [(p, score, re.compile(p, re.IGNORECASE)) for p, score in SOFT_PENALTY_PATTERNS]

# 2. SOURCE SUFFIX STRIPPING
SOURCE_SUFFIXES = [
    r'\s*[|\-–—]\s*(BBC|BBC News|Reuters|AP|Al Jazeera|The Guardian|NPR|CNBC|NYT).*$',
    r'\s*[|\-–—]\s*\w[\w\s]{2,30}$',  # Generic " - Publisher Name" suffix
]

COMPILED_SOURCE_SUFFIXES = [re.compile(p, re.IGNORECASE) for p in SOURCE_SUFFIXES]


def filter_noise(articles: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Filters articles based on hard reject patterns and applies soft penalties.
    Returns (accepted_articles, rejected_articles).
    """
    accepted = []
    rejected = []
    
    for article in articles:
        title = article.get('title', '') or ''
        description = article.get('description', '') or ''
        text_to_check = f"{title} {description}"
        
        # Check hard rejects
        is_rejected = False
        for pattern_str, regex in COMPILED_HARD_REJECT:
            if regex.search(text_to_check):
                article['rejection_reason'] = pattern_str
                rejected.append(article)
                is_rejected = True
                break
                
        if is_rejected:
            continue
            
        # Check soft penalties
        noise_penalty = 0.0
        noise_flags = []
        for pattern_str, score, regex in COMPILED_SOFT_PENALTY:
            if regex.search(text_to_check):
                noise_penalty += score
                noise_flags.append(pattern_str)
                
        # Clamp noise penalty between -1.0 and 0.0
        noise_penalty = max(-1.0, min(0.0, noise_penalty))
        
        article['noise_penalty'] = noise_penalty
        article['noise_flags'] = noise_flags
        accepted.append(article)
        
    return accepted, rejected


def enrich_entities(articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Enriches articles by extracting entities from their title and description.
    """
    for article in articles:
        title = article.get('title', '') or ''
        description = article.get('description', '') or ''
        article['entities'] = extract_entities(title, description)
    return articles


def normalize_title(title: str) -> str:
    """
    Strips source suffixes, normalizes whitespace, and lowercases the title.
    """
    if not title:
        return ""
    
    norm_title = title
    for regex in COMPILED_SOURCE_SUFFIXES:
        norm_title = regex.sub('', norm_title)
        
    norm_title = re.sub(r'\s+', ' ', norm_title).strip().lower()
    return norm_title


def jaccard_similarity(str1: str, str2: str) -> float:
    """
    Calculates Jaccard similarity between two strings based on their tokens.
    """
    set1 = set(str1.split())
    set2 = set(str2.split())
    if not set1 or not set2:
        return 0.0
    intersection = set1.intersection(set2)
    union = set1.union(set2)
    return len(intersection) / len(union)


def get_all_entities_set(entities: Dict[str, Any]) -> set:
    """
    Flattens entity dict into a set of lowercased strings for overlap comparison.
    """
    all_ents = set()
    if not entities:
        return all_ents
    for k, v in entities.items():
        if isinstance(v, list):
            all_ents.update([str(e).lower() for e in v])
    return all_ents


def enhanced_dedup(articles: List[Dict[str, Any]], threshold: float = 0.35) -> List[Dict[str, Any]]:
    """
    Deduplicates articles using Jaccard similarity on titles and entity signature overlap.
    """
    clusters = []
    
    for article in articles:
        title = article.get('title', '') or ''
        norm_title = normalize_title(title)
        category = article.get('category', '')
        entities = article.get('entities', {})
        
        art_entities = get_all_entities_set(entities)
        
        found_cluster = False
        for cluster in clusters:
            rep = cluster[0]
            rep_title = rep.get('title', '') or ''
            rep_norm = normalize_title(rep_title)
            
            # 1. Check Jaccard similarity
            jaccard = jaccard_similarity(norm_title, rep_norm)
            
            # 2. Check entity overlap
            rep_entities = get_all_entities_set(rep.get('entities', {}))
            entity_overlap_ratio = 0.0
            if art_entities and rep_entities:
                intersection = art_entities.intersection(rep_entities)
                union = art_entities.union(rep_entities)
                entity_overlap_ratio = len(intersection) / len(union)
                
            is_dup_jaccard = (jaccard >= threshold)
            is_dup_entity = (entity_overlap_ratio >= 0.8 and category == rep.get('category', '') and category != '')
            
            if is_dup_jaccard or is_dup_entity:
                cluster.append(article)
                found_cluster = True
                break
                
        if not found_cluster:
            clusters.append([article])
            
    # Process clusters and pick canonicals
    processed = []
    for cluster in clusters:
        if len(cluster) == 1:
            article = cluster[0]
            article['is_duplicate'] = False
            article['duplicate_count'] = 0
            processed.append(article)
        else:
            def score_article(art: Dict[str, Any]) -> Tuple[int, int, int]:
                desc = art.get('description', '') or ''
                desc_len = len(desc)
                ent_count = sum(len(v) for v in art.get('entities', {}).values() if isinstance(v, list))
                img = art.get('imageUrl', '') or ''
                has_good_img = 1 if img and 'unsplash' not in img.lower() else 0
                return (has_good_img, ent_count, desc_len)
                
            best_idx = 0
            best_score = (-1, -1, -1)
            for i, art in enumerate(cluster):
                score = score_article(art)
                if score > best_score:
                    best_score = score
                    best_idx = i
                    
            canonical = cluster[best_idx]
            canonical_id = canonical.get('id')
            
            canonical['is_duplicate'] = False
            canonical['duplicate_count'] = len(cluster) - 1
            processed.append(canonical)
            
            for i, art in enumerate(cluster):
                if i != best_idx:
                    art['is_duplicate'] = True
                    art['canonical_id'] = canonical_id
                    processed.append(art)
                    
    return processed


def run_intake(articles: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Orchestrates the Layer 1 INTAKE pipeline.
    """
    input_count = len(articles)
    
    # 1. Noise filter
    accepted, rejected = filter_noise(articles)
    noise_rejected = len(rejected)
    
    # 2. Enrich with entities
    accepted = enrich_entities(accepted)
    
    # 3. Enhanced dedup
    deduped = enhanced_dedup(accepted)
    
    # Calculate stats
    rejection_reasons = {}
    for art in rejected:
        reason = art.get('rejection_reason', 'unknown')
        rejection_reasons[reason] = rejection_reasons.get(reason, 0) + 1
        
    output_count = sum(1 for art in deduped if not art.get('is_duplicate'))
    duplicates_suppressed = len(deduped) - output_count
    
    articles_with_entities = sum(
        1 for art in deduped 
        if sum(len(v) for v in art.get('entities', {}).values() if isinstance(v, list)) > 0
    )
    entity_coverage = (articles_with_entities / len(deduped)) if deduped else 0.0
    
    stats = {
        'input_count': input_count,
        'noise_rejected': noise_rejected,
        'duplicates_suppressed': duplicates_suppressed,
        'output_count': output_count,
        'entity_coverage': round(entity_coverage, 2),
        'rejection_reasons': rejection_reasons
    }
    
    print("--- INTAKE LAYER AUDIT STATS ---")
    for k, v in stats.items():
        print(f"{k}: {v}")
    print("--------------------------------")
    
    final_articles = [art for art in deduped if not art.get('is_duplicate')]
    return final_articles, stats
