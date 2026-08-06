import urllib.request
import xml.etree.ElementTree as ET
import re

feeds = [
    ("TechCrunch", "https://techcrunch.com/feed/"),
    ("Ars Technica", "https://feeds.arstechnica.com/arstechnica/index"),
    ("CNET", "https://www.cnet.com/rss/news/"),
    ("The Verge", "https://www.theverge.com/rss/index.xml"),
    ("Wired", "https://www.wired.com/feed/rss"),
    ("NPR National", "https://feeds.npr.org/1001/rss.xml"),
    ("Hindustan Times", "https://www.hindustantimes.com/feeds/rss/india-news/rssfeed.xml"),
    ("Indian Express", "https://indianexpress.com/feed/"),
    ("BBC World", "https://feeds.bbci.co.uk/news/rss.xml")
]

headers = {'User-Agent': 'Mozilla/5.0'}

for name, url in feeds:
    print(f"=== {name} ===")
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=5) as resp:
            content = resp.read()
            root = ET.fromstring(content)
            items = root.findall('.//item') or root.findall('.//{http://www.w3.org/2005/Atom}entry')
            print(f"Items: {len(items)}")
            for item in items[:2]:
                title = item.findtext('title') or item.findtext('{http://www.w3.org/2005/Atom}title') or ''
                
                # Search all media attributes
                media_urls = []
                for elem in item.iter():
                    u = elem.attrib.get('url') or elem.attrib.get('href')
                    if u and any(ext in u.lower() for ext in ['.jpg', '.png', '.jpeg', '.webp', 'wp-content', 'images', 'ichef']):
                        media_urls.append(u)
                        
                # Search HTML content for <img> tags
                html_body = (item.findtext('description') or '') + ' ' + (item.findtext('{http://purl.org/rss/1.0/modules/content/}encoded') or '') + ' ' + (item.findtext('{http://www.w3.org/2005/Atom}content') or '')
                img_srcs = re.findall(r'src=["\']([^"\']+\.(?:jpg|png|jpeg|webp)[^"\']*)["\']', html_body, re.IGNORECASE)
                
                print(f"  Title: {title[:50]}")
                print(f"  Media XML: {media_urls[:2]}")
                print(f"  HTML Img Srcs: {img_srcs[:2]}")
    except Exception as e:
        print(f"  Error: {e}")
