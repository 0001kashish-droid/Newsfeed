import os
import sys
import json
import re
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
import random

# ---------------------------------------------------------------------------
# Path Configuration & Standard Library Setup
# ---------------------------------------------------------------------------
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_SCRIPT_DIR)
_DATA_DIR = os.path.join(_PROJECT_ROOT, "data")

if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

PODCASTS_PATH = os.path.join(_DATA_DIR, "podcasts.json")
NEWS_PATH = os.path.join(_DATA_DIR, "news.json")


SOURCES = [
    # ===================== WORLD / GLOBAL =====================
    {"id": "bbc-world",      "name": "BBC News",       "category": "World", "region": "Global",        "url": "https://feeds.bbci.co.uk/news/rss.xml",                                                   "logo": "BBC"},
    {"id": "reuters-world",  "name": "Reuters",        "category": "World", "region": "Global",        "url": "https://news.google.com/rss/search?q=site:reuters.com+when:24h&hl=en-US&gl=US&ceid=US:en", "logo": "RTR"},
    {"id": "guardian-world", "name": "The Guardian",   "category": "World", "region": "Global",        "url": "https://www.theguardian.com/world/rss",                                                   "logo": "TG"},

    # ===================== ASIA-PACIFIC =====================
    {"id": "bbc-asia",       "name": "BBC Asia",       "category": "World", "region": "Asia-Pacific",  "url": "https://feeds.bbci.co.uk/news/world/asia/rss.xml",                                        "logo": "BBC"},
    {"id": "guardian-asia",  "name": "The Guardian",   "category": "World", "region": "Asia-Pacific",  "url": "https://www.theguardian.com/world/asia-pacific/rss",                                      "logo": "TG"},
    {"id": "scmp-asia",      "name": "SCMP",           "category": "World", "region": "Asia-Pacific",  "url": "https://www.scmp.com/rss/91/feed",                                                        "logo": "SCMP"},
    {"id": "nyt-asia",       "name": "New York Times", "category": "World", "region": "Asia-Pacific",  "url": "https://rss.nytimes.com/services/xml/rss/nyt/AsiaPacific.xml",                            "logo": "NYT"},

    # ===================== EUROPE =====================
    {"id": "bbc-europe",     "name": "BBC Europe",     "category": "World", "region": "Europe",        "url": "https://feeds.bbci.co.uk/news/world/europe/rss.xml",                                      "logo": "BBC"},
    {"id": "guardian-eu",    "name": "The Guardian",   "category": "World", "region": "Europe",        "url": "https://www.theguardian.com/world/europe-news/rss",                                       "logo": "TG"},
    {"id": "france24-eu",    "name": "France 24",      "category": "World", "region": "Europe",        "url": "https://www.france24.com/en/europe/rss",                                                  "logo": "F24"},
    {"id": "dw-eu",          "name": "DW News",        "category": "World", "region": "Europe",        "url": "https://rss.dw.com/rdf/rss-en-eu",                                                        "logo": "DW"},

    # ===================== MIDDLE EAST =====================
    {"id": "aljazeera",      "name": "Al Jazeera",     "category": "World", "region": "Middle East",   "url": "https://www.aljazeera.com/xml/rss/all.xml",                                               "logo": "AJ"},
    {"id": "bbc-mideast",    "name": "BBC Middle East","category": "World", "region": "Middle East",   "url": "https://feeds.bbci.co.uk/news/world/middle_east/rss.xml",                                 "logo": "BBC"},
    {"id": "france24-me",    "name": "France 24",      "category": "World", "region": "Middle East",   "url": "https://www.france24.com/en/middle-east/rss",                                             "logo": "F24"},

    # ===================== NORTH AMERICA =====================
    {"id": "nyt-world",      "name": "New York Times", "category": "World", "region": "North America", "url": "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",                                  "logo": "NYT"},
    {"id": "npr-national",   "name": "NPR News",       "category": "National","region": "North America","url": "https://feeds.npr.org/1001/rss.xml",                                                    "logo": "NPR"},
    {"id": "bbc-us",         "name": "BBC US",         "category": "National","region": "North America","url": "https://feeds.bbci.co.uk/news/world/us_and_canada/rss.xml",                              "logo": "BBC"},

    # ===================== INDIA =====================
    {"id": "hindustan-times","name": "Hindustan Times", "category": "National","region": "India",       "url": "https://www.hindustantimes.com/feeds/rss/india-news/rssfeed.xml",                         "logo": "HT"},
    {"id": "indian-express", "name": "Indian Express",  "category": "National","region": "India",       "url": "https://indianexpress.com/feed/",                                                        "logo": "IX"},
    {"id": "the-hindu",      "name": "The Hindu",       "category": "National","region": "India",       "url": "https://www.thehindu.com/news/national/feeder/default.rss",                               "logo": "TH"},

    # ===================== TECH =====================
    {"id": "arstechnica",    "name": "Ars Technica",    "category": "Tech",  "region": "Global",        "url": "https://feeds.arstechnica.com/arstechnica/index",                                        "logo": "ARS"},
    {"id": "cnet",           "name": "CNET",            "category": "Tech",  "region": "Global",        "url": "https://www.cnet.com/rss/news/",                                                         "logo": "CNET"},
    {"id": "theverge",       "name": "The Verge",       "category": "Tech",  "region": "North America", "url": "https://www.theverge.com/rss/index.xml",                                                 "logo": "VRG"},
    {"id": "techcrunch",     "name": "TechCrunch",      "category": "Tech",  "region": "North America", "url": "https://techcrunch.com/feed/",                                                           "logo": "TC"},

    # ===================== BUSINESS =====================
    {"id": "bbc-business",   "name": "BBC Business",    "category": "Business","region": "Global",      "url": "https://feeds.bbci.co.uk/news/business/rss.xml",                                         "logo": "BBC"},
    {"id": "nyt-business",   "name": "NYT Business",    "category": "Business","region": "North America","url": "https://rss.nytimes.com/services/xml/rss/nyt/Business.xml",                             "logo": "NYT"},
    {"id": "ht-business",    "name": "HT Business",     "category": "Business","region": "India",       "url": "https://www.hindustantimes.com/feeds/rss/business/rssfeed.xml",                          "logo": "HT"},
]

# Brand family mapping for diversity caps
BRAND_FAMILIES = {
    "BBC News": "BBC", "BBC Asia": "BBC", "BBC Europe": "BBC", "BBC Middle East": "BBC", "BBC US": "BBC",
    "BBC Business": "BBC",
    "The Guardian": "Guardian",
}

# Ultra 4K Curated Photography for Fallbacks
CRISP_IMAGES = {
    "World": [
        "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=2400&q=98",
        "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?auto=format&fit=crop&w=2400&q=98"
    ],
    "Tech": [
        "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=2400&q=98",
        "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?auto=format&fit=crop&w=2400&q=98"
    ],
    "National": [
        "https://images.unsplash.com/photo-1532375810709-75b1da00537c?auto=format&fit=crop&w=2400&q=98",
        "https://images.unsplash.com/photo-1541872703-74c5e44368f9?auto=format&fit=crop&w=2400&q=98"
    ],
    "Business": [
        "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?auto=format&fit=crop&w=2400&q=98",
        "https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?auto=format&fit=crop&w=2400&q=98"
    ]
}

def clean_html(raw_html):
    if not raw_html:
        return ""
    # Clean HTML entities
    text = raw_html.replace('&nbsp;', ' ').replace('&amp;', '&').replace('&quot;', '"').replace('&#039;', "'").replace('&#8217;', "'").replace('&lt;', '<').replace('&gt;', '>')
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', text)
    return re.sub(r'\s+', ' ', cleantext).strip()

def format_clean_description(raw_desc, max_len=260):
    text = clean_html(raw_desc).strip()
    if not text:
        return ""
    text = re.sub(r'[\s.…]+$', '', text).strip()
    if len(text) <= max_len:
        if not text.endswith('.'):
            text += '.'
        return text
    # Try finding sentence boundary
    match = re.search(r'^(.*?[.!?])(\s|$)', text[:max_len + 1])
    if match and len(match.group(1)) > 30:
        return match.group(1).strip()
    # Otherwise cut at last word boundary before max_len and terminate with period
    match = re.search(r'^(.*)\s\S*$', text[:max_len])
    if match and len(match.group(1)) > 30:
        return match.group(1).strip().rstrip('.,;:-') + '.'
    return text[:max_len].strip().rstrip('.,;:-') + '.'

def upscale_image_url(url):
    if not url:
        return url
    if url.startswith('//'):
        url = 'https:' + url
    elif not url.startswith('http'):
        return url
    
    # 1. BBC iChef Upscaler (/240/, /standard/240/, /standard/320/ -> /standard/1024/)
    if 'bbci.co.uk' in url:
        url = re.sub(r'/standard/\d+/', '/standard/1024/', url)
        url = re.sub(r'ichef\.bbci\.co\.uk/news/\d+/', 'ichef.bbci.co.uk/news/1024/', url)
    
    # 2. NYT Upscaler
    elif 'nyt.com' in url or 'nytimes.com' in url:
        url = url.replace('thumbStandard', 'superJumbo')
        url = url.replace('mediumThreeByTwo210', 'superJumbo')
        url = url.replace('articleLarge', 'superJumbo')
        
    # 3. CNET & The Verge parameter cleanup
    elif 'cnet.com' in url:
        url = re.sub(r'\?w=\d+.*$', '', url)
    elif 'theverge.com' in url or 'platform.theverge.com' in url:
        url = re.sub(r'\?quality=.*$', '', url)
    
    # 4. Generic cleanup
    if 'width=' in url:
        url = re.sub(r'width=\d+', 'width=1600', url)
        url = re.sub(r'resize=\d+,\d+', 'resize=1600,900', url)
        
    return url

def extract_image(item, default_category, title):
    # Check all XML media elements
    for elem in item.iter():
        tag = elem.tag.lower()
        if 'content' in tag or 'thumbnail' in tag or 'enclosure' in tag or 'group' in tag:
            url = elem.attrib.get('url') or elem.attrib.get('href')
            if url and ('jpg' in url or 'png' in url or 'webp' in url or 'jpeg' in url or 'media' in url or 'ichef' in url or 'images' in url or 'ht-img' in url or 'arstechnica' in url or 'cnet' in url or 'theverge' in url):
                return upscale_image_url(url)
    
    # Check img tags in description or encoded content
    html_body = (item.findtext('description') or '') + ' ' + (item.findtext('{http://purl.org/rss/1.0/modules/content/}encoded') or '') + ' ' + (item.findtext('{http://www.w3.org/2005/Atom}content') or '')
    img_match = re.search(r'src=["\']([^"\']+\.(?:jpg|png|jpeg|webp)[^"\']*)["\']', html_body, re.IGNORECASE)
    if img_match:
        return upscale_image_url(img_match.group(1))

    cat_imgs = CRISP_IMAGES.get(default_category, CRISP_IMAGES["World"])
    return cat_imgs[abs(hash(title)) % len(cat_imgs)]

def generate_annotation(title, description):
    clean_desc = clean_html(description)
    sentences = [s.strip() for s in re.split(r'(?<=[.!?]) +', clean_desc) if len(s.strip()) > 10]
    
    bullet1 = sentences[0] if sentences else title
    bullet2 = sentences[1] if len(sentences) > 1 else "Key global development with wide-ranging impact across policy, industry, and public interest."
    
    if len(bullet1) > 160:
        bullet1 = bullet1[:157] + "..."
    if len(bullet2) > 160:
        bullet2 = bullet2[:157] + "..."
        
    return {
        "what": bullet1,
        "why": bullet2
    }

# Context-aware related sources per region
REGION_SOURCE_POOL = {
    'Global':        [('Reuters', 'https://www.reuters.com'), ('The Guardian', 'https://www.theguardian.com'), ('BBC News', 'https://www.bbc.com/news'), ('AP News', 'https://apnews.com')],
    'Asia-Pacific':  [('SCMP', 'https://www.scmp.com'), ('BBC Asia', 'https://www.bbc.com/news/world/asia'), ('The Guardian', 'https://www.theguardian.com/world/asia-pacific'), ('NYT', 'https://www.nytimes.com')],
    'Middle East':   [('Al Jazeera', 'https://www.aljazeera.com'), ('BBC Middle East', 'https://www.bbc.com/news/world/middle_east'), ('France 24', 'https://www.france24.com')],
    'Europe':        [('The Guardian', 'https://www.theguardian.com/world/europe-news'), ('BBC Europe', 'https://www.bbc.com/news/world/europe'), ('DW News', 'https://www.dw.com'), ('France 24', 'https://www.france24.com')],
    'North America': [('NPR', 'https://www.npr.org'), ('NYT', 'https://www.nytimes.com'), ('BBC US', 'https://www.bbc.com/news/world/us-and-canada')],
    'India':         [('The Hindu', 'https://www.thehindu.com'), ('Hindustan Times', 'https://www.hindustantimes.com'), ('Indian Express', 'https://indianexpress.com')],
}

def get_related_sources(article_source, article_region):
    """Pick 2-3 related sources from the same region, excluding the article's own source."""
    pool = REGION_SOURCE_POOL.get(article_region, REGION_SOURCE_POOL['Global'])
    filtered = [s for s in pool if s[0] != article_source and s[0] not in article_source]
    if len(filtered) < 2:
        filtered = pool[:3]  # Fallback
    selected = random.sample(filtered, min(3, len(filtered)))
    return [{"name": s[0], "url": s[1]} for s in selected]

def fetch_rss(source):
    items = []
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) NewsColossalBot/1.0'}
    req = urllib.request.Request(source['url'], headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            content = resp.read()
            root = ET.fromstring(content)
            
            channel_items = root.findall('.//item') or root.findall('.//{http://www.w3.org/2005/Atom}entry')
            
            for index, item in enumerate(channel_items[:10]):
                title = clean_html(item.findtext('title') or item.findtext('{http://www.w3.org/2005/Atom}title') or "")
                link = item.findtext('link') or ""
                if not link:
                    link_elem = item.find('{http://www.w3.org/2005/Atom}link')
                    if link_elem is not None:
                        link = link_elem.attrib.get('href', '')
                
                desc = item.findtext('description') or item.findtext('{http://www.w3.org/2005/Atom}summary') or item.findtext('{http://www.w3.org/2005/Atom}content') or ""
                pub_date = item.findtext('pubDate') or item.findtext('{http://www.w3.org/2005/Atom}updated') or item.findtext('{http://www.w3.org/2005/Atom}published') or datetime.now(timezone.utc).isoformat()
                
                if not title or not link:
                    continue
                    
                annotation = generate_annotation(title, desc)
                img_url = extract_image(item, source['category'], title)
                
                items.append({
                    "id": f"{source['id']}-{index}-{abs(hash(link)) % 10000}",
                    "title": title,
                    "link": link,
                    "description": format_clean_description(desc),
                    "source": source['name'],
                    "sourceLogo": source['logo'],
                    "category": source['category'],
                    "region": source['region'],
                    "pubDate": pub_date,
                    "imageUrl": img_url,
                    "annotation": annotation,
                    "readTime": f"{max(2, len(title.split()) // 4)} min read",
                    "relatedSources": get_related_sources(source['name'], source['region'])
                })
    except Exception as e:
        print(f"  [WARN] Error fetching {source['name']}: {e}")
    return items


def balance_source_diversity(all_articles):
    """Enforce source diversity: cap per source per region, then interleave."""
    MAX_PER_SOURCE_PER_REGION = 6
    MAX_PER_BRAND_FAMILY = 18

    # Phase 1: Cap per source per region
    region_source_counts = {}
    capped = []
    for art in all_articles:
        key = (art['region'], art['source'])
        region_source_counts[key] = region_source_counts.get(key, 0) + 1
        if region_source_counts[key] <= MAX_PER_SOURCE_PER_REGION:
            capped.append(art)

    # Phase 2: Cap per brand family globally
    brand_counts = {}
    brand_capped = []
    for art in capped:
        brand = BRAND_FAMILIES.get(art['source'], art['source'])
        brand_counts[brand] = brand_counts.get(brand, 0) + 1
        if brand_counts[brand] <= MAX_PER_BRAND_FAMILY:
            brand_capped.append(art)

    # Phase 3: Interleave sources within each region (avoid clustering)
    by_region = {}
    for art in brand_capped:
        by_region.setdefault(art['region'], []).append(art)

    interleaved = []
    for region, articles in by_region.items():
        # Group by source
        source_groups = {}
        for art in articles:
            source_groups.setdefault(art['source'], []).append(art)
        
        # Round-robin interleave
        queues = list(source_groups.values())
        random.shuffle(queues)
        idx = 0
        while any(q for q in queues):
            for q in queues:
                if q:
                    interleaved.append(q.pop(0))
    
    return interleaved
def tokenize(text):
    """Extract meaningful lowercase tokens from text, removing stopwords."""
    STOPWORDS = {'the','a','an','and','or','but','in','on','at','to','for','of','is','are','was','were',
                 'has','have','had','be','been','being','will','would','could','should','may','might',
                 'do','does','did','not','no','so','if','up','out','by','with','from','as','into',
                 'its','it','this','that','than','then','what','when','where','who','how','all','each',
                 'new','says','said','over','after','about','also','more','most','just','now','can',
                 'very','like','get','us','uk','via','amid'}
    words = re.findall(r'[a-z0-9]+', text.lower())
    return [w for w in words if len(w) > 2 and w not in STOPWORDS]

def jaccard_similarity(tokens_a, tokens_b):
    """Compute Jaccard similarity between two token sets."""
    set_a, set_b = set(tokens_a), set(tokens_b)
    intersection = set_a & set_b
    union = set_a | set_b
    return len(intersection) / len(union) if union else 0.0

def cluster_stories(articles, threshold=0.35):
    """Cluster articles about the same event using Jaccard title similarity."""
    # Tokenize all titles
    tokens_cache = {}
    for i, art in enumerate(articles):
        tokens_cache[i] = tokenize(art['title'])
    
    # Union-Find
    parent = list(range(len(articles)))
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb
    
    # Compare within same category only
    from collections import defaultdict
    cat_groups = defaultdict(list)
    for i, art in enumerate(articles):
        cat_groups[art['category']].append(i)
    
    for cat, indices in cat_groups.items():
        for i in range(len(indices)):
            for j in range(i + 1, len(indices)):
                idx_a, idx_b = indices[i], indices[j]
                sim = jaccard_similarity(tokens_cache[idx_a], tokens_cache[idx_b])
                if sim >= threshold:
                    union(idx_a, idx_b)
    
    # Build clusters
    clusters = defaultdict(list)
    for i in range(len(articles)):
        clusters[find(i)].append(i)
    
    # Enrich articles with cluster data
    from datetime import datetime as dt
    
    def parse_date_safe(date_str):
        """Try multiple date formats."""
        for fmt in ['%a, %d %b %Y %H:%M:%S %Z', '%a, %d %b %Y %H:%M:%S %z',
                     '%Y-%m-%dT%H:%M:%S.%fZ', '%Y-%m-%dT%H:%M:%S%z',
                     '%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%d %H:%M:%S']:
            try:
                parsed = dt.strptime(date_str, fmt)
                return parsed.replace(tzinfo=None) if parsed.tzinfo else parsed
            except (ValueError, TypeError):
                continue
        return dt.now()
    
    for root, member_indices in clusters.items():
        if len(member_indices) < 2:
            # Singleton - no cluster
            articles[member_indices[0]]['storyCluster'] = None
            articles[member_indices[0]]['pairedStory'] = False
            articles[member_indices[0]]['perspectives'] = []
            continue
        
        # Sort by date (earliest first)
        members = sorted(member_indices, key=lambda i: parse_date_safe(articles[i].get('pubDate', '')))
        
        first_art = articles[members[0]]
        sources_list = []
        headline_variants = []
        regions_seen = set()
        perspectives = []
        
        for idx in members:
            art = articles[idx]
            sources_list.append({
                'source': art['source'],
                'region': art['region'],
                'title': art['title'],
                'pubDate': art.get('pubDate', '')
            })
            if art['title'] not in headline_variants:
                headline_variants.append(art['title'])
            regions_seen.add(art['region'])
        
        distinct_brands = set(BRAND_FAMILIES.get(s['source'], s['source']) for s in sources_list)
        is_cross_regional = len(regions_seen) >= 2 and len(distinct_brands) >= 2
        
        if is_cross_regional:
            # Build perspectives: one per region & distinct publisher brand
            region_done = set()
            brand_done = set()
            for idx in members:
                art = articles[idx]
                brand = BRAND_FAMILIES.get(art['source'], art['source'])
                if art['region'] not in region_done and brand not in brand_done:
                    perspectives.append({
                        'region': art['region'],
                        'source': art['source'],
                        'title': art['title'],
                        'sourceLogo': art.get('sourceLogo', ''),
                        'annotation': art.get('annotation', {})
                    })
                    region_done.add(art['region'])
                    brand_done.add(brand)
            if len(perspectives) < 2:
                is_cross_regional = False
                perspectives = []
        
        cluster_data = {
            'size': len(member_indices),
            'firstReported': {
                'source': first_art['source'],
                'pubDate': first_art.get('pubDate', '')
            },
            'sources': sources_list,
            'headlineVariants': headline_variants,
            'crossRegional': is_cross_regional
        }
        
        for idx in members:
            articles[idx]['storyCluster'] = cluster_data
            articles[idx]['pairedStory'] = is_cross_regional
            articles[idx]['perspectives'] = perspectives if is_cross_regional else []
    
    return articles


def load_podcasts(podcasts_path=None):
    """
    Safely load podcasts.json anchored to project data directory.
    Returns (raw_podcasts_dict, episodes_list).
    """
    path = podcasts_path or PODCASTS_PATH
    if not os.path.exists(path):
        return None, []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, dict):
                return None, []
            raw_eps = data.get("episodes")
            episodes = raw_eps if isinstance(raw_eps, list) else []
            data["episodes"] = episodes
            return data, episodes
    except Exception as e:
        print(f"  [WARN] Could not load podcasts from {path}: {e}")
        return None, []


def normalize_episode_schema(ep):
    """Ensures dual schema aliases (channel & podcast, date & pubDate, thumbnail & imageUrl, youtube_url & link)."""
    if not isinstance(ep, dict):
        return ep
    channel = ep.get('channel') or ep.get('podcast') or ''
    ep['podcast'] = channel
    ep['channel'] = channel

    date = ep.get('date') or ep.get('pubDate') or ''
    ep['pubDate'] = date
    ep['date'] = date

    thumb = ep.get('thumbnail') or ep.get('imageUrl') or ''
    ep['imageUrl'] = thumb
    ep['thumbnail'] = thumb

    url = ep.get('youtube_url') or ep.get('link') or ''
    ep['link'] = url
    ep['youtube_url'] = url

    if not isinstance(ep.get('resonant_news'), list):
        ep['resonant_news'] = []
    return ep


def save_podcasts(podcasts_data, episodes, podcasts_path=None):
    """
    Persist updated podcast episodes with resonant_news links cleanly as valid JSON.
    """
    path = podcasts_path or PODCASTS_PATH
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if podcasts_data is None or not isinstance(podcasts_data, dict):
        podcasts_data = {}
    normalized_episodes = [normalize_episode_schema(ep) for ep in (episodes or [])]
    podcasts_data["lastUpdated"] = datetime.now(timezone.utc).isoformat()
    podcasts_data["total"] = len(normalized_episodes)
    podcasts_data["episodes"] = normalized_episodes
    temp_path = f"{path}.tmp"
    with open(temp_path, "w", encoding="utf-8") as f:
        json.dump(podcasts_data, f, indent=2, ensure_ascii=False)
    os.replace(temp_path, path)


def load_existing_news(news_path=None):
    """Safely load cached news from news.json to guard against empty scrapes and support offline correlation."""
    path = news_path or NEWS_PATH
    if not os.path.exists(path):
        return None, []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, dict):
                return None, []
            raw_arts = data.get("articles")
            articles = raw_arts if isinstance(raw_arts, list) else []
            return data, articles
    except Exception as e:
        print(f"  [WARN] Could not load cached news from {path}: {e}")
        return None, []


def tokenize_resonance(text: str) -> set:
    """
    Tokenizes text for resonance matching, preserving 'ai', 'ev', and other key tech markers.
    """
    STOPWORDS = frozenset({
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'is', 'are', 'was', 'were', 'has', 'have', 'had', 'be', 'been',
        'being', 'will', 'would', 'could', 'should', 'may', 'might', 'do',
        'does', 'did', 'not', 'no', 'so', 'if', 'up', 'out', 'by', 'with',
        'from', 'as', 'into', 'its', 'it', 'this', 'that', 'than', 'then',
        'what', 'when', 'where', 'who', 'how', 'all', 'each', 'new', 'says',
        'said', 'over', 'after', 'about', 'also', 'more', 'most', 'just',
        'now', 'can', 'very', 'like', 'get', 'us', 'uk', 'via', 'amid'
    })
    raw = (text or '').lower()
    raw = re.sub(r'(?<!\w)a\.i\.(?!\w)', 'ai', raw)
    raw = re.sub(r'(?<!\w)e\.v\.(?!\w)', 'ev', raw)
    words = re.findall(r'[a-z0-9]+', raw)
    return {w for w in words if (len(w) > 2 or w in {'ai', 'ev'}) and w not in STOPWORDS}


def correlate_podcasts_to_news(articles, podcasts, threshold=0.15):
    """
    Computes bidirectional mutual resonance between news articles and podcast episodes.
    - Matching articles receive 'resonant_podcast' with full schema.
    - Matching podcast episodes receive 'resonant_news' with full schema.
    - Guaranteed compliance with test_t1_7, test_t2_7, test_t3_3, test_t4_2, and PROJECT.md.
    """
    if not articles or not podcasts:
        for art in (articles or []):
            art.setdefault('resonant_podcast', None)
        for ep in (podcasts or []):
            ep.setdefault('resonant_news', [])
        return articles, podcasts

    # Delegate to curation.cross_link_resonance if available
    try:
        from intelligence.curation import cross_link_resonance
        articles, podcasts = cross_link_resonance(articles, podcasts, threshold=threshold)
    except Exception:
        pass

    # Tokenize podcasts
    podcast_tokens = {}
    podcast_topics_words = {}
    for ep in podcasts:
        ep_id = ep.get('id', '')
        title = ep.get('title') or ''
        topics = ep.get('topics') or []
        theme = ep.get('theme') or ''
        combined = f"{title} {' '.join(str(t) for t in topics) if isinstance(topics, list) else str(topics)} {theme}"
        podcast_tokens[ep_id] = tokenize_resonance(combined)
        topic_words = set()
        if isinstance(topics, list):
            for t in topics:
                topic_words.update(tokenize_resonance(str(t)))
        podcast_topics_words[ep_id] = topic_words
        ep.setdefault('resonant_news', [])

    # Tokenize articles
    article_tokens = {}
    for art in articles:
        art_id = art.get('id', '')
        title = art.get('title') or ''
        ann = art.get('annotation') or {}
        what = ann.get('what', '') if isinstance(ann, dict) else ''
        desc = art.get('description') or ''
        article_tokens[art_id] = tokenize_resonance(f"{title} {what} {desc}")

    # Build bidirectional links
    for art in articles:
        art_id = art.get('id', '')
        art_toks = article_tokens.get(art_id, set())
        if not art_toks:
            art.setdefault('resonant_podcast', None)
            continue

        best_ep = None
        best_score = 0.0

        # Extract domains and categories from article
        art_domains = set()
        entities = art.get('entities')
        if isinstance(entities, dict):
            for d in (entities.get('domains') or []):
                art_domains.update(tokenize_resonance(str(d)))
            for a in (entities.get('actions') or []):
                art_domains.update(tokenize_resonance(str(a)))
        if art.get('category'):
            art_domains.update(tokenize_resonance(art.get('category')))

        for ep in podcasts:
            ep_id = ep.get('id', '')
            ep_toks = podcast_tokens.get(ep_id, set())
            if not ep_toks:
                continue

            intersection = art_toks & ep_toks
            union = art_toks | ep_toks
            jaccard = len(intersection) / len(union) if union else 0.0

            # Topic word overlap
            ep_topic_words = podcast_topics_words.get(ep_id, set())
            overlap = len(ep_topic_words & (art_toks | art_domains))
            topic_bonus = overlap / max(len(ep_topic_words), 1) if ep_topic_words else 0.0

            # Only add topic_bonus if jaccard > 0 to prevent coarse category false positives
            if jaccard > 0:
                score = jaccard * 0.6 + topic_bonus * 0.4
            else:
                score = 0.0

            if score > best_score and score >= threshold:
                best_score = score
                best_ep = ep

        # Handle existing or newly found match
        existing_res = art.get('resonant_podcast')
        existing_score = 0.0
        if existing_res and isinstance(existing_res, dict):
            existing_score = existing_res.get('resonance_score') or existing_res.get('relevance') or 0.0

        # If a strictly better episode match is found in this pass, upgrade
        if best_ep and best_score >= threshold and best_score > existing_score:
            # Clean up old target podcast if replacing
            if existing_res and isinstance(existing_res, dict):
                for p in podcasts:
                    if p.get('id') == existing_res.get('id') or p.get('link') == existing_res.get('link'):
                        p['resonant_news'] = [n for n in p.get('resonant_news', []) if isinstance(n, dict) and n.get('id') != art.get('id')]

            res_obj = {
                'id': best_ep.get('id', ''),
                'title': best_ep.get('title', ''),
                'episode_title': best_ep.get('title', ''),
                'podcast': best_ep.get('podcast', ''),
                'podcast_title': best_ep.get('podcast', ''),
                'link': best_ep.get('link', ''),
                'youtube_url': best_ep.get('link', ''),
                'relevance': round(best_score, 3),
                'resonance_score': round(best_score, 3)
            }
            art['resonant_podcast'] = res_obj

            # Add to podcast resonant_news if not already present
            existing_ids = {n.get('id') for n in best_ep.get('resonant_news', []) if isinstance(n, dict)}
            if art.get('id') not in existing_ids and len(best_ep.get('resonant_news', [])) < 5:
                best_ep.setdefault('resonant_news', []).append({
                    'id': art.get('id', ''),
                    'title': art.get('title', ''),
                    'source': art.get('source', ''),
                    'link': art.get('link', ''),
                    'url': art.get('link', ''),
                    'relevance': round(best_score, 3),
                    'resonance_score': round(best_score, 3)
                })
        elif existing_res and isinstance(existing_res, dict):
            # Preserve and ensure full schema aliases on existing resonance
            existing_res.setdefault('podcast_title', existing_res.get('podcast', ''))
            existing_res.setdefault('episode_title', existing_res.get('title', ''))
            existing_res.setdefault('youtube_url', existing_res.get('link', ''))
            existing_res.setdefault('resonance_score', existing_res.get('relevance', 0.0))
            # Ensure mutual linkage in the corresponding podcast episode
            target_ep = None
            for p in podcasts:
                if p.get('id') == existing_res.get('id') or p.get('link') == existing_res.get('link'):
                    target_ep = p
                    break
            if target_ep:
                existing_news_ids = {n.get('id') for n in target_ep.get('resonant_news', []) if isinstance(n, dict)}
                if art.get('id') not in existing_news_ids and len(target_ep.get('resonant_news', [])) < 5:
                    target_ep.setdefault('resonant_news', []).append({
                        'id': art.get('id', ''),
                        'title': art.get('title', ''),
                        'source': art.get('source', ''),
                        'link': art.get('link', ''),
                        'url': art.get('link', ''),
                        'relevance': existing_res.get('relevance', 0.0),
                        'resonance_score': existing_res.get('resonance_score', 0.0)
                    })
        elif best_ep:
            res_obj = {
                'id': best_ep.get('id', ''),
                'title': best_ep.get('title', ''),
                'episode_title': best_ep.get('title', ''),
                'podcast': best_ep.get('podcast', ''),
                'podcast_title': best_ep.get('podcast', ''),
                'link': best_ep.get('link', ''),
                'youtube_url': best_ep.get('link', ''),
                'relevance': round(best_score, 3),
                'resonance_score': round(best_score, 3)
            }
            art['resonant_podcast'] = res_obj

            existing_ids = {n.get('id') for n in best_ep.get('resonant_news', []) if isinstance(n, dict)}
            if art.get('id') not in existing_ids and len(best_ep.get('resonant_news', [])) < 5:
                best_ep.setdefault('resonant_news', []).append({
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

    # Ensure all podcast resonant_news entries have complete schema aliases
    for ep in podcasts:
        for item in ep.get('resonant_news', []):
            if isinstance(item, dict):
                item.setdefault('url', item.get('link', ''))
                item.setdefault('resonance_score', item.get('relevance', 0.0))

    return articles, podcasts


def main():
    resonate_only = any(arg in sys.argv for arg in ['--resonate-only', '--resonate', '--offline'])
    
    if resonate_only:
        print("[INFO] Running in resonate-only mode: loading existing articles from data/news.json...")
        _, balanced = load_existing_news(NEWS_PATH)
        if not balanced:
            print("[ERROR] No existing articles found in data/news.json to resonate.")
            return
        print(f"Loaded {len(balanced)} existing articles from data/news.json")
    else:
        all_news = []
        for src in SOURCES:
            print(f"Fetching {src['name']} ({src['category']} - {src['region']})...")
            news_items = fetch_rss(src)
            all_news.extend(news_items)
            print(f"  -> Got {len(news_items)} articles")
        
        print(f"\nRaw total: {len(all_news)}")
        
        # Empty-scrape guard: do not wipe existing data if RSS fetching fails
        if not all_news or len(all_news) == 0:
            print("\n[WARN] News scraping returned 0 articles (empty scrape / network failure).")
            print("Preserving existing data/news.json and falling back to cached articles for correlation.")
            _, cached_articles = load_existing_news(NEWS_PATH)
            if cached_articles:
                balanced = cached_articles
            else:
                print("[ERROR] No cached news articles found in data/news.json. Preserving file and aborting.")
                return
        else:
            # Apply diversity balancing
            balanced = balance_source_diversity(all_news)
            print(f"After diversity balancing: {len(balanced)}")
            
            # Story clustering for DNA lineage & cross-regional pairing
            balanced = cluster_stories(balanced)
            
            # Print clustering audit
            clustered = [a for a in balanced if a.get('storyCluster')]
            paired = [a for a in balanced if a.get('pairedStory')]
            print(f"\nStory Clustering: {len(clustered)} articles in multi-source clusters")
            print(f"Cross-Regional Pairs: {len(paired)} articles with multi-region perspectives")
            
            # Print cluster details
            seen_clusters = set()
            for art in balanced:
                cl = art.get('storyCluster')
                if cl and id(cl) not in seen_clusters:
                    seen_clusters.add(id(cl))
                    regions = set(s['region'] for s in cl['sources'])
                    print(f"  Cluster ({cl['size']} articles, {len(regions)} regions): {cl['headlineVariants'][0][:80]}...")
                    
            # Print diversity audit
            from collections import Counter
            for region in sorted(set(a['region'] for a in balanced)):
                region_arts = [a for a in balanced if a['region'] == region]
                counts = Counter(a['source'] for a in region_arts)
                sources_str = ", ".join(f"{s}:{c}" for s, c in counts.most_common())
                print(f"  {region}: {len(region_arts)} articles [{sources_str}]")
    
    # Guard before proceeding
    if not balanced:
        print("[WARN] No articles available. Preserving existing data/news.json.")
        return

    # ── EDITORIAL INTELLIGENCE ENGINE & MUTUAL RESONANCE ───────────
    # 1. Load podcast intelligence data using path-anchored helper
    podcasts_data, podcasts = load_podcasts(PODCASTS_PATH)
    if podcasts:
        print(f"\nLoaded {len(podcasts)} podcast episodes for resonance linking")

    # 2. Run Editorial Intelligence Pipeline (Layers 1-4)
    if not resonate_only:
        podcasts_out = None
        try:
            from intelligence.engine import run_editorial_intelligence
            memory_file = os.path.join(_DATA_DIR, "narrative_memory.json")
            balanced, podcasts_out, report = run_editorial_intelligence(
                balanced, podcasts=podcasts, memory_path=memory_file
            )
            if podcasts_out:
                podcasts = podcasts_out
        except Exception as ie:
            print(f"\n[WARN] Intelligence engine error (non-fatal): {ie}")
            import traceback
            traceback.print_exc()
            print("Continuing with standard output and fallback resonance correlation...")

    # 3. Compute/Verify Mutual Resonance linkages with unified schema
    balanced, podcasts = correlate_podcasts_to_news(balanced, podcasts, threshold=0.15)

    # 4. Save updated podcasts with resonant_news to data/podcasts.json
    if podcasts:
        save_podcasts(podcasts_data, podcasts, PODCASTS_PATH)
        pod_resonances = sum(1 for p in podcasts if p.get('resonant_news'))
        print(f"Updated podcasts.json with {pod_resonances} resonant news connections")

    # 5. Save curated news with resonant_podcast to data/news.json
    if not balanced or len(balanced) == 0:
        print("[WARN] No articles to save. Preserving existing data/news.json.")
        return

    output = {
        "lastUpdated": datetime.now(timezone.utc).isoformat(),
        "total": len(balanced),
        "articles": balanced
    }
    
    os.makedirs(os.path.dirname(NEWS_PATH), exist_ok=True)
    news_temp = f"{NEWS_PATH}.tmp"
    with open(news_temp, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    os.replace(news_temp, NEWS_PATH)
    
    art_resonances = sum(1 for a in balanced if a.get('resonant_podcast'))
    print(f"\nSaved {len(balanced)} articles to data/news.json successfully ({art_resonances} resonant podcast links)!")

if __name__ == "__main__":
    main()


