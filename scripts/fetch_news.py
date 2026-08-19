import os
import json
import re
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
import random

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
                    "description": clean_html(desc)[:220] + "..." if len(clean_html(desc)) > 220 else clean_html(desc),
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


def main():
    all_news = []
    for src in SOURCES:
        print(f"Fetching {src['name']} ({src['category']} - {src['region']})...")
        news_items = fetch_rss(src)
        all_news.extend(news_items)
        print(f"  -> Got {len(news_items)} articles")
    
    print(f"\nRaw total: {len(all_news)}")
    
    # Apply diversity balancing
    balanced = balance_source_diversity(all_news)
    print(f"After diversity balancing: {len(balanced)}")
    
    # Print diversity audit
    from collections import Counter
    for region in sorted(set(a['region'] for a in balanced)):
        region_arts = [a for a in balanced if a['region'] == region]
        counts = Counter(a['source'] for a in region_arts)
        sources_str = ", ".join(f"{s}:{c}" for s, c in counts.most_common())
        print(f"  {region}: {len(region_arts)} articles [{sources_str}]")
    
    output = {
        "lastUpdated": datetime.now(timezone.utc).isoformat(),
        "total": len(balanced),
        "articles": balanced
    }
    
    os.makedirs("data", exist_ok=True)
    with open("data/news.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"\nSaved {len(balanced)} articles to data/news.json successfully!")

if __name__ == "__main__":
    main()


