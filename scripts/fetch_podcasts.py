#!/usr/bin/env python3
"""
Thought Pulse - Podcast Intelligence Pipeline
Scrapes YouTube channel pages for latest episodes (RSS fallback when available).
Filters noise, extracts insights, classifies categories, writes data/podcasts.json.
"""
import urllib.request
import json
import os
import re
from datetime import datetime, timezone

PODCAST_SOURCES = [
    {'name': 'Lex Fridman Podcast', 'handle': '@lexfridman', 'logo': 'LF', 'tier': 'flagship'},
    {'name': 'TED', 'handle': '@TED', 'logo': 'TED', 'tier': 'flagship'},
    {'name': 'Huberman Lab', 'handle': '@hubermanlab', 'logo': 'HL', 'tier': 'flagship'},
    {'name': 'The Economist', 'handle': '@TheEconomist', 'logo': 'TE', 'tier': 'flagship'},
    {'name': 'Bloomberg Television', 'handle': '@BloombergTelevision', 'logo': 'BB', 'tier': 'flagship'},
    {'name': 'Financial Times', 'handle': '@FinancialTimes', 'logo': 'FT', 'tier': 'standard'},
    {'name': 'Harvard Business Review', 'handle': '@HarvardBusinessReview', 'logo': 'HBR', 'tier': 'standard'},
    {'name': 'McKinsey', 'handle': '@McKinsey', 'logo': 'McK', 'tier': 'standard'},
    {'name': 'a16z', 'handle': '@a16z', 'logo': 'a16z', 'tier': 'standard'},
    {'name': 'Diary of a CEO', 'handle': '@TheDiaryOfACEO', 'logo': 'DC', 'tier': 'flagship'},
    {'name': 'All-In Podcast', 'handle': '@alaboratory', 'logo': 'AIP', 'tier': 'standard'},
    {'name': 'Tim Ferriss', 'handle': '@timferriss', 'logo': 'TF', 'tier': 'standard'},
    {'name': 'Acquired', 'handle': '@AcquiredFM', 'logo': 'ACQ', 'tier': 'standard'},
    {'name': 'World Economic Forum', 'handle': '@wikieconomics_official', 'logo': 'WEF', 'tier': 'standard'},
    {'name': 'Stanford', 'handle': '@stanford', 'logo': 'SU', 'tier': 'standard'},
]

SPONSOR_STARTS = [
    'thanks to our partners', 'thanks to our sponsors',
    'this episode is brought to you', 'sponsored by',
    'use code', 'sign up at', 'get started at',
]

CATEGORY_KEYWORDS = {
    'AI & Tech': ['ai', 'artificial intelligence', 'machine learning', 'llm',
                  'programming', 'software', 'coding', 'tech', 'robot', 'semiconductor',
                  'chip', 'neural', 'algorithm', 'cyber', 'quantum', 'agentic', 'compute'],
    'Business & Economy': ['business', 'economy', 'market', 'invest', 'startup', 'entrepreneur',
                           'founder', 'ceo', 'venture', 'capital', 'finance', 'stock',
                           'growth', 'scale', 'billion', 'company', 'trade', 'gdp'],
    'Science & Health': ['science', 'health', 'brain', 'neuro', 'biology', 'medicine', 'diet',
                         'fitness', 'sleep', 'mental', 'psychology', 'research',
                         'gene', 'dna', 'disease', 'nutrition', 'longevity'],
    'Geopolitics & Policy': ['geopolit', 'war', 'diplomac', 'sanction', 'military', 'government',
                             'policy', 'regulation', 'election', 'democracy', 'nato',
                             'climate', 'energy', 'nuclear', 'security'],
    'Philosophy & Ideas': ['philosophy', 'meaning', 'consciousness', 'moral', 'ethic', 'human',
                           'civiliz', 'history', 'culture', 'freedom', 'truth', 'wisdom',
                           'purpose', 'spiritual'],
}


def classify_category(title, desc=''):
    text = (title + ' ' + desc[:300]).lower()
    scores = {}
    for cat, kws in CATEGORY_KEYWORDS.items():
        scores[cat] = sum(1 for kw in kws if kw in text)
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else 'Ideas & Culture'


def extract_insight(description):
    if not description:
        return ''
    lines = [l.strip() for l in description.split('\n') if l.strip()]
    for line in lines:
        lower = line.lower()
        if any(lower.startswith(s) for s in SPONSOR_STARTS):
            continue
        if line.startswith('http') or line.startswith('www.'):
            continue
        if re.match(r'^\d{1,2}:\d{2}', line):
            continue
        if len(line) < 30:
            continue
        if len(line) > 200:
            dot = line.find('. ', 80)
            if 0 < dot < 200:
                return line[:dot + 1]
            return line[:197] + '...'
        return line
    return ''


def extract_guest(title, podcast_name):
    clean = re.sub(r'\s*[|\-\u2014]\s*' + re.escape(podcast_name) + r'.*$', '', title, flags=re.IGNORECASE)
    clean = re.sub(r'\s*[|\-\u2014]\s*(Podcast|Episode|Ep\.?)\s*#?\d*\s*$', '', clean, flags=re.IGNORECASE)
    m = re.match(r'^([A-Z][a-zA-Z.\s]+?):\s', clean)
    if m and len(m.group(1).split()) <= 4:
        return m.group(1).strip()
    m = re.search(r'\bwith\s+([A-Z][a-zA-Z.\s]+?)$', clean)
    if m and len(m.group(1).split()) <= 4:
        return m.group(1).strip()
    m = re.match(r"^([A-Z][a-zA-Z.'\s]+?)\s*[-\u2014]\s", clean)
    if m and len(m.group(1).split()) <= 4:
        return m.group(1).strip()
    return ''


def parse_duration_seconds(dur_str):
    """Parse '5:15:51' or '12:34' to total seconds."""
    if not dur_str:
        return 0
    parts = dur_str.split(':')
    try:
        if len(parts) == 3:
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
        elif len(parts) == 2:
            return int(parts[0]) * 60 + int(parts[1])
    except ValueError:
        pass
    return 0


def scrape_channel(source):
    """Scrape a YouTube channel page for video metadata using ytInitialData."""
    url = f"https://www.youtube.com/{source['handle']}/videos"
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
    })
    resp = urllib.request.urlopen(req, timeout=20)
    html = resp.read().decode('utf-8', errors='replace')

    match = re.search(r'var ytInitialData = (\{.*?\});\s*</script>', html, re.DOTALL)
    if not match:
        match = re.search(r'ytInitialData\s*=\s*(\{.*?\});\s*', html, re.DOTALL)
    if not match:
        print(f"  [WARN] No ytInitialData found for {source['name']}")
        return []

    data = json.loads(match.group(1))
    tabs = data.get('contents', {}).get('twoColumnBrowseResultsRenderer', {}).get('tabs', [])

    episodes = []
    for tab in tabs:
        tr = tab.get('tabRenderer', {})
        if not tr.get('selected'):
            continue
        grid = tr.get('content', {}).get('richGridRenderer', {})
        if not grid:
            continue
        items = grid.get('contents', [])
        for item in items:
            rir = item.get('richItemRenderer', {})
            if not rir:
                continue
            lvm = rir.get('content', {}).get('lockupViewModel', {})
            if not lvm:
                continue

            vid_id = lvm.get('contentId', '')
            if not vid_id:
                continue

            # Title
            meta = lvm.get('metadata', {}).get('lockupMetadataViewModel', {})
            title = meta.get('title', {}).get('content', '')

            # Sub-metadata (published time, views)
            published = ''
            views = ''
            sub_meta = meta.get('metadata', {}).get('contentMetadataViewModel', {}).get('metadataRows', [])
            for row in sub_meta:
                for part in row.get('metadataParts', []):
                    txt = part.get('text', {}).get('content', '')
                    if 'ago' in txt:
                        published = txt
                    elif 'view' in txt.lower():
                        views = txt

            # Duration (from badge overlay)
            duration = ''
            overlays = lvm.get('contentImage', {}).get('thumbnailViewModel', {}).get('overlays', [])
            for ov in overlays:
                badges = ov.get('thumbnailBottomOverlayViewModel', {}).get('badges', [])
                for b in badges:
                    dur_text = b.get('thumbnailBadgeViewModel', {}).get('text', '')
                    if dur_text and ':' in dur_text:
                        duration = dur_text

            # Accessibility label (has description-like text)
            acc_label = lvm.get('rendererContext', {}).get('accessibilityContext', {}).get('label', '')

            # --- FILTERS ---
            # Skip shorts (< 2 min)
            dur_secs = parse_duration_seconds(duration)
            if 0 < dur_secs < 120:
                continue
            # Skip noise titles
            lower_title = title.lower()
            if any(kw in lower_title for kw in ['#shorts', '#short', 'clip', 'highlight', 'trailer', 'teaser']):
                continue

            # Thumbnail
            thumb_url = f'https://i.ytimg.com/vi/{vid_id}/maxresdefault.jpg'
            link = f'https://www.youtube.com/watch?v={vid_id}'

            insight = extract_insight(acc_label)
            guest = extract_guest(title, source['name'])
            category = classify_category(title, acc_label)

            episodes.append({
                'id': f'tp_{vid_id}',
                'title': title,
                'podcast': source['name'],
                'podcastLogo': source['logo'],
                'tier': source['tier'],
                'guest': guest,
                'insight': insight,
                'imageUrl': thumb_url,
                'link': link,
                'pubDate': published,
                'duration': duration,
                'views': views,
                'category': category,
            })
        break

    return episodes


def main():
    all_episodes = []
    for src in PODCAST_SOURCES:
        print(f"Fetching {src['name']}...")
        try:
            eps = scrape_channel(src)
            all_episodes.extend(eps)
            print(f"  -> Got {len(eps)} episodes")
        except Exception as e:
            print(f"  [ERROR] {src['name']}: {e}")

    # Sort newest first (by published text — rough but functional)
    priority = {'hour': 0, 'day': 1, 'week': 2, 'month': 3, 'year': 4}
    def sort_key(ep):
        pub = ep.get('pubDate', '').lower()
        for unit, pri in priority.items():
            if unit in pub:
                num = re.search(r'(\d+)', pub)
                n = int(num.group(1)) if num else 1
                return pri * 1000 + n
        return 9999
    all_episodes.sort(key=sort_key)

    # Keep top 30
    all_episodes = all_episodes[:30]

    print(f"\nTotal: {len(all_episodes)} episodes")
    from collections import Counter
    for src, cnt in Counter(e['podcast'] for e in all_episodes).most_common():
        print(f"  {src}: {cnt}")
    cats = Counter(e['category'] for e in all_episodes)
    print(f"Categories: {dict(cats)}")

    output = {
        'lastUpdated': datetime.now(timezone.utc).isoformat(),
        'total': len(all_episodes),
        'episodes': all_episodes,
    }
    os.makedirs('data', exist_ok=True)
    with open('data/podcasts.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"\nSaved to data/podcasts.json")


if __name__ == '__main__':
    main()
