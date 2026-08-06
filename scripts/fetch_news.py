import os
import json
import re
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

SOURCES = [
    # World Feeds
    {
        "id": "bbc-world",
        "name": "BBC News",
        "category": "World",
        "region": "Global",
        "url": "https://feeds.bbci.co.uk/news/rss.xml",
        "logo": "BBC"
    },
    {
        "id": "reuters-world",
        "name": "Reuters",
        "category": "World",
        "region": "Global",
        "url": "https://news.google.com/rss/search?q=site:reuters.com+when:24h&hl=en-US&gl=US&ceid=US:en",
        "logo": "RTR"
    },
    {
        "id": "nyt-world",
        "name": "New York Times",
        "category": "World",
        "region": "North America",
        "url": "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
        "logo": "NYT"
    },
    {
        "id": "aljazeera",
        "name": "Al Jazeera",
        "category": "World",
        "region": "Middle East",
        "url": "https://www.aljazeera.com/xml/rss/all.xml",
        "logo": "AJ"
    },
    # Tech Feeds
    {
        "id": "techcrunch",
        "name": "TechCrunch",
        "category": "Tech",
        "region": "Global",
        "url": "https://techcrunch.com/feed/",
        "logo": "TC"
    },
    {
        "id": "theverge",
        "name": "The Verge",
        "category": "Tech",
        "region": "Global",
        "url": "https://www.theverge.com/rss/index.xml",
        "logo": "VRG"
    },
    {
        "id": "cnet",
        "name": "CNET",
        "category": "Tech",
        "region": "Global",
        "url": "https://www.cnet.com/rss/news/",
        "logo": "CNET"
    },
    {
        "id": "rtings",
        "name": "RTINGS",
        "category": "Tech",
        "region": "Global",
        "url": "https://news.google.com/rss/search?q=site:rtings.com+when:7d&hl=en-US&gl=US&ceid=US:en",
        "logo": "RTG"
    },
    # National Feeds
    {
        "id": "ndtv",
        "name": "NDTV",
        "category": "National",
        "region": "India",
        "url": "https://feeds.feedburner.com/ndtvnews-top-stories",
        "logo": "NDTV"
    },
    {
        "id": "npr-national",
        "name": "NPR News",
        "category": "National",
        "region": "North America",
        "url": "https://feeds.npr.org/1001/rss.xml",
        "logo": "NPR"
    },
    # Business Feeds
    {
        "id": "cnbc-business",
        "name": "CNBC",
        "category": "Business",
        "region": "Global",
        "url": "https://search.cnbc.com/rs/search/combinedqueries/view.xml?partnerId=2000&keywords=finance",
        "logo": "CNBC"
    },
    {
        "id": "wsj-markets",
        "name": "WSJ Markets",
        "category": "Business",
        "region": "Global",
        "url": "https://news.google.com/rss/search?q=site:wsj.com+markets+when:24h&hl=en-US&gl=US&ceid=US:en",
        "logo": "WSJ"
    }
]

# Ultra-HD curated photography (4K/1080p uncompressed)
CRISP_IMAGES = {
    "World": [
        "https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?auto=format&fit=crop&w=1600&q=95",
        "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?auto=format&fit=crop&w=1600&q=95",
        "https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=1600&q=95",
        "https://images.unsplash.com/photo-1446776811953-b23d57bd21aa?auto=format&fit=crop&w=1600&q=95"
    ],
    "Tech": [
        "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=1600&q=95",
        "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?auto=format&fit=crop&w=1600&q=95",
        "https://images.unsplash.com/photo-1519389950473-47ba0277781c?auto=format&fit=crop&w=1600&q=95",
        "https://images.unsplash.com/photo-1485827404703-89b55fcc595e?auto=format&fit=crop&w=1600&q=95"
    ],
    "National": [
        "https://images.unsplash.com/photo-1532375810709-75b1da00537c?auto=format&fit=crop&w=1600&q=95",
        "https://images.unsplash.com/photo-1541872703-74c5e44368f9?auto=format&fit=crop&w=1600&q=95",
        "https://images.unsplash.com/photo-1570125909232-eb263c188f7e?auto=format&fit=crop&w=1600&q=95"
    ],
    "Business": [
        "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?auto=format&fit=crop&w=1600&q=95",
        "https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?auto=format&fit=crop&w=1600&q=95",
        "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=1600&q=95"
    ]
}

def clean_html(raw_html):
    if not raw_html:
        return ""
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext.strip()

def upscale_image_url(url):
    if not url:
        return url
    
    # BBC iChef high-res replacement (/240/, /320/, /480/ -> /1024/)
    url = re.sub(r'ichef\.bbci\.co\.uk/news/\d+/', 'ichef.bbci.co.uk/news/1024/', url)
    
    # Reuters & general width params
    url = re.sub(r'w=\d+', 'w=1200', url)
    url = re.sub(r'width=\d+', 'width=1200', url)
    url = re.sub(r'h=\d+', 'h=800', url)
    url = re.sub(r'height=\d+', 'height=800', url)
    url = re.sub(r'quality=\d+', 'quality=95', url)
    url = re.sub(r'q=\d+', 'q=95', url)
    
    # NYT replacement
    url = url.replace('thumbStandard', 'superJumbo')
    url = url.replace('mediumThreeByTwo210', 'superJumbo')
    url = url.replace('articleLarge', 'superJumbo')
    
    # NDTV & generic thumbnail replacements
    url = re.sub(r'\d+x\d+', '1200x800', url)
    return url

def extract_image(item, default_category, title):
    # Search all nodes for media thumbnail or enclosure
    for elem in item.iter():
        tag = elem.tag.lower()
        if 'content' in tag or 'thumbnail' in tag or 'enclosure' in tag or 'group' in tag:
            url = elem.attrib.get('url') or elem.attrib.get('href')
            if url and ('jpg' in url or 'png' in url or 'webp' in url or 'jpeg' in url or 'media' in url or 'ichef' in url):
                return upscale_image_url(url)
    
    # Check img tags in description HTML
    desc = item.findtext('description') or item.findtext('{http://www.w3.org/2005/Atom}summary') or ""
    img_match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', desc)
    if img_match:
        return upscale_image_url(img_match.group(1))

    # Fallback ultra-crisp image
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

def fetch_rss(source):
    items = []
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) NewsColossalBot/1.0'}
    req = urllib.request.Request(source['url'], headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            content = resp.read()
            root = ET.fromstring(content)
            
            channel_items = root.findall('.//item') or root.findall('.//{http://www.w3.org/2005/Atom}entry')
            
            for index, item in enumerate(channel_items[:12]):
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
                    "relatedSources": [
                        {"name": "BBC News", "url": "https://www.bbc.com/news"},
                        {"name": "Reuters", "url": "https://www.reuters.com"},
                        {"name": "Al Jazeera", "url": "https://www.aljazeera.com"}
                    ]
                })
    except Exception as e:
        print(f"Error fetching {source['name']}: {e}")
    return items

def main():
    all_news = []
    for src in SOURCES:
        print(f"Fetching {src['name']} ({src['category']})...")
        news_items = fetch_rss(src)
        all_news.extend(news_items)
        
    print(f"Total articles fetched: {len(all_news)}")
    
    output = {
        "lastUpdated": datetime.now(timezone.utc).isoformat(),
        "total": len(all_news),
        "articles": all_news
    }
    
    os.makedirs("data", exist_ok=True)
    with open("data/news.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print("Saved HD dataset to data/news.json successfully!")

if __name__ == "__main__":
    main()
