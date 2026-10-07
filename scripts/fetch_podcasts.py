#!/usr/bin/env python3
"""
Thought Pulse - Podcast Intelligence Pipeline
Scrapes YouTube channel pages for latest episodes.
Extracts dominant topics, synthesizes thematic annotations,
filters noise, classifies categories, and writes data/podcasts.json.
"""
import urllib.request
import json
import os
import re
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# Path Configuration & Standard Library Setup
# ---------------------------------------------------------------------------
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_SCRIPT_DIR)
_DATA_DIR = os.path.join(_PROJECT_ROOT, "data")
PODCASTS_PATH = os.path.join(_DATA_DIR, "podcasts.json")

PODCAST_SOURCES = [
    # Thinkers & Deep Dives
    {'name': 'Lex Fridman Podcast', 'handle': '@lexfridman', 'logo': 'LF', 'tier': 'flagship'},
    {'name': 'TED', 'handle': '@TED', 'logo': 'TED', 'tier': 'flagship'},
    {'name': 'Huberman Lab', 'handle': '@hubermanlab', 'logo': 'HL', 'tier': 'flagship'},
    {'name': 'Tim Ferriss', 'handle': '@timferriss', 'logo': 'TF', 'tier': 'standard'},
    {'name': 'Freakonomics', 'handle': '@freakonomicsradio', 'logo': 'FRK', 'tier': 'flagship'},
    
    # Global Geopolitics & News
    {'name': 'The Economist', 'handle': '@TheEconomist', 'logo': 'TE', 'tier': 'flagship'},
    {'name': 'Council on Foreign Relations', 'handle': '@CFR_org', 'logo': 'CFR', 'tier': 'flagship'},
    {'name': 'CSIS', 'handle': '@CSIS', 'logo': 'CSIS', 'tier': 'standard'},
    {'name': 'BBC Podcasts', 'handle': '@BBCPodcasts', 'logo': 'BBC', 'tier': 'flagship'},
    {'name': 'NPR', 'handle': '@NPR', 'logo': 'NPR', 'tier': 'standard'},
    {'name': 'PBS NewsHour', 'handle': '@PBSNewsHour', 'logo': 'PBS', 'tier': 'standard'},
    
    # Business, Finance & Tech
    {'name': 'WSJ Podcasts', 'handle': '@WSJPodcasts', 'logo': 'WSJ', 'tier': 'flagship'},
    {'name': 'Bloomberg Originals', 'handle': '@BloombergOriginals', 'logo': 'BB', 'tier': 'flagship'},
    {'name': 'Financial Times', 'handle': '@FinancialTimes', 'logo': 'FT', 'tier': 'standard'},
    {'name': 'Harvard Business Review', 'handle': '@HarvardBusinessReview', 'logo': 'HBR', 'tier': 'standard'},
    {'name': 'McKinsey', 'handle': '@McKinsey', 'logo': 'McK', 'tier': 'standard'},
    {'name': 'a16z', 'handle': '@a16z', 'logo': 'a16z', 'tier': 'standard'},
    {'name': 'All-In Podcast', 'handle': '@AllInPodOfficial', 'logo': 'AIP', 'tier': 'standard'},
    {'name': 'Acquired', 'handle': '@AcquiredFM', 'logo': 'ACQ', 'tier': 'standard'},
    
    # Science & Academia
    {'name': 'Nature', 'handle': '@naturevideo', 'logo': 'NAT', 'tier': 'standard'},
    {'name': 'World Economic Forum', 'handle': '@wef', 'logo': 'WEF', 'tier': 'standard'},
    {'name': 'Stanford', 'handle': '@stanford', 'logo': 'SU', 'tier': 'standard'},
    {'name': 'Diary of a CEO', 'handle': '@TheDiaryOfACEO', 'logo': 'DC', 'tier': 'standard'}
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

FIGURE_THEMES = {
    'yuval noah harari': {
        'guest': 'Yuval Noah Harari',
        'topics': ['AI Governance', 'Information Networks', 'Democracy', 'Human Civilization'],
        'theme': 'Examines how artificial intelligence, information networks, and automated bureaucracy challenge democratic truth and human agency.'
    },
    'andrew huberman': {
        'guest': 'Andrew Huberman',
        'topics': ['Neuroscience', 'Circadian Biology', 'Sleep Science', 'Human Performance'],
        'theme': 'Dives into the neurobiology of deep sleep, cortisol regulation, and actionable protocols to eliminate chronic exhaustion.'
    },
    'dhh': {
        'guest': 'David Heinemeier Hansson (DHH)',
        'topics': ['Software Engineering', 'Agentic AI', 'Vibe Coding', 'Open Source'],
        'theme': 'Debates the evolution of software development, agentic AI coding paradigms, and the enduring power of open-source software.'
    },
    'ed zitron': {
        'guest': 'Ed Zitron',
        'topics': ['AI Economics', 'Tech Bubble', 'Silicon Valley', 'Industry Critique'],
        'theme': 'A critical dissection of the generative AI hype cycle, enterprise adoption economics, and looming structural reckoning.'
    },
    'antónio guterres': {
        'guest': 'António Guterres',
        'topics': ['Geopolitics', 'Global Governance', 'United Nations', 'Multilateralism'],
        'theme': 'Assesses the diminishing power of global superpowers, multilateral diplomacy, and structural reforms needed for world peace.'
    },
    'antonio guterres': {
        'guest': 'António Guterres',
        'topics': ['Geopolitics', 'Global Governance', 'United Nations', 'Multilateralism'],
        'theme': 'Assesses the diminishing power of global superpowers, multilateral diplomacy, and structural reforms needed for world peace.'
    },
    'david friedberg': {
        'guest': 'David Friedberg',
        'topics': ['Macroeconomics', 'American Empire', 'Global Trade', 'Venture Capital'],
        'theme': 'Explores macro shifts in American economic supremacy, debt accumulation, and geopolitical realignment.'
    },
    'ed conway': {
        'guest': 'Ed Conway',
        'topics': ['Global Supply Chains', 'Material Economics', 'Energy Transition', 'Geopolitics'],
        'theme': 'Analyzes the foundational materials—sand, salt, iron, copper, oil, and lithium—that power modern global civilization.'
    },
    'joe liemandt': {
        'guest': 'Joe Liemandt',
        'topics': ['AI Tutoring', 'Education Reform', 'Accelerated Learning', 'EdTech'],
        'theme': 'Investigates how 1-on-1 AI-driven adaptive learning systems can 10x educational velocity and student mastery.'
    },
    'saloni dattani': {
        'guest': 'Saloni Dattani',
        'topics': ['Biomedical Research', 'Drug Discovery', 'Public Health', 'Medical History'],
        'theme': 'Explores the historical bottleneck between basic scientific discovery and clinical real-world medical treatments.'
    },
    'dr. chris palmer': {
        'guest': 'Dr. Chris Palmer',
        'topics': ['Metabolic Psychiatry', 'Brain Energy', 'Nutritional Neuroscience', 'Mental Health'],
        'theme': 'Connects mitochondrial dysfunction and cellular metabolism to treatment-resistant psychiatric conditions.'
    }
}

TOPIC_PATTERNS = [
    (r'\b(cancer|mrna|vaccine)\b', 'Biotechnology', 'Breakthroughs in personalized mRNA therapies and targeted oncology treatments.'),
    (r'\b(cursor)\b', 'AI Tools & Dev', 'The architecture and rapid user adoption behind AI-first code editors and developer workflows.'),
    (r'\b(workforce|ai agents?|agentic)\b', 'Future of Work', 'How organizations orchestrate hybrid teams composed of human knowledge workers and autonomous AI agents.'),
    (r'\b(immigration|crackdown)\b', 'Economic Policy & Labor', 'Examines the labor market shocks, wage pressures, and macroeconomic fallout of hardline border enforcement.'),
    (r'\b(nato|trump|sweden)\b', 'Geopolitics & Defense', 'European defense preparedness, the future of the NATO alliance, and transatlantic geopolitical alignment.'),
    (r'\b(manufacturing)\b', 'Industrial Strategy', 'Reshoring, advanced automation, and the competitive renewal of domestic manufacturing capabilities.'),
    (r'\b(math|reasoning|best models)\b', 'Frontier AI Reasoning', 'Evaluating frontier LLM reasoning limits, mathematical verification, and neuro-symbolic breakthroughs.'),
    (r'\b(materials)\b', 'Resource Economics', 'Material abundance, mineral extraction limits, and the physical foundations of technology.'),
    (r'\b(space architect|philosopher|barrier to thriving)\b', 'Human Flourishing', 'Interdisciplinary perspectives on designing sustainable habitats and long-term societal resilience.'),
    (r'\b(cycling|ai control room)\b', 'Performance Analytics', 'Deploying real-time AI telematics and predictive strategy models to elite sports competitions.'),
    (r'\b(positive-sum|gavin baker)\b', 'Venture Capital & AI', 'Macro investment theses on technological supercycles and broad-based economic value creation.'),
    (r'\b(infrastructure)\b', 'AI Infrastructure', 'The capital expenditure race in datacenters, specialized silicon, and power generation for foundation models.'),
    (r'\b(sneaker|creative genius)\b', 'Industrial Design', 'The fusion of biomimicry, cultural narrative, and boundary-pushing consumer product design.'),
    (r'\b(boerse stuttgart|exchange)\b', 'Financial Markets', 'Capital market digitalization, digital assets, and European financial infrastructure modernization.'),
    (r'\b(messy middle|big change)\b', 'Organizational Transformation', 'Navigating cognitive resistance and operational inertia during major organizational restructuring.'),
    (r'\b(grocery)\b', 'Retail Economics', 'Consumer spending shifts, omnichannel supply chain automation, and grocery retail margin dynamics.'),
    (r'\b(trust ai advice)\b', 'Consumer Psychology', 'The behavioral paradox of consumers distrusting AI yet increasingly relying on algorithmic guidance.'),
    (r'\b(models,? moats)\b', 'AI Strategy', 'Evaluating competitive defensibility, commoditization of base models, and application-layer margins.'),
    (r'\b(citizens|politicians)\b', 'Civic Innovation', 'Grassroots participatory democracy, civic empowerment models, and modern community self-governance.'),
    (r'\b(economics of innovation)\b', 'Innovation Economics', 'How generative intelligence drastically compresses research and development cycles across industries.')
]


def classify_category(title, desc=''):
    text = (title + ' ' + desc[:300]).lower()
    scores = {}
    for cat, kws in CATEGORY_KEYWORDS.items():
        scores[cat] = sum(1 for kw in kws if kw in text)
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else 'Ideas & Culture'


def extract_guest(title, podcast_name):
    clean = re.sub(r'\s*[|\-\u2014]\s*' + re.escape(podcast_name) + r'.*$', '', title, flags=re.IGNORECASE)
    clean = re.sub(r'\s*[|\-\u2014]\s*(Podcast|Episode|Ep\.?)\s*#?\d*\s*$', '', clean, flags=re.IGNORECASE)
    clean = re.sub(r'^(The full-length interview with|Interview with)\s+', '', clean, flags=re.IGNORECASE)
    
    # Check known figures first
    for fig_key, info in FIGURE_THEMES.items():
        if fig_key in title.lower():
            return info['guest']

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


def extract_podcast_intelligence(title, podcast, raw_guest=''):
    title_lower = title.lower()

    # 1. Check known prominent thought leaders
    for fig_key, info in FIGURE_THEMES.items():
        if fig_key in title_lower:
            return {
                'guest': info['guest'],
                'topics': info['topics'],
                'theme': info['theme']
            }

    # 2. Check pattern matches
    matched_topics = []
    matched_themes = []
    for pat, topic, theme_desc in TOPIC_PATTERNS:
        if re.search(pat, title_lower):
            matched_topics.append(topic)
            matched_themes.append(theme_desc)

    guest = raw_guest or extract_guest(title, podcast)

    # 3. Add domain keywords if present
    if 'ai' in title_lower or 'artificial intelligence' in title_lower:
        if 'Artificial Intelligence' not in matched_topics and 'AI Tools & Dev' not in matched_topics and 'Frontier AI Reasoning' not in matched_topics:
            matched_topics.append('Artificial Intelligence')
    if any(w in title_lower for w in ['economy', 'market', 'trade', 'gdp', 'inflation']):
        if 'Global Economy' not in matched_topics and 'Economic Policy & Labor' not in matched_topics:
            matched_topics.append('Global Economy')
    if any(w in title_lower for w in ['health', 'medicine', 'brain', 'sleep', 'diet']):
        if 'Health & Medicine' not in matched_topics and 'Biotechnology' not in matched_topics:
            matched_topics.append('Health & Medicine')
    if any(w in title_lower for w in ['geopolitic', 'war', 'nato', 'un ', 'diplomacy']):
        if 'Geopolitics' not in matched_topics and 'Geopolitics & Defense' not in matched_topics:
            matched_topics.append('Geopolitics')

    if not matched_topics:
        matched_topics = ['Ideas & Culture']

    if matched_themes:
        theme = matched_themes[0]
    else:
        clean_title = re.sub(r'\s*[|\-\u2014]\s*.*$', '', title).strip()
        theme = f'Explores strategic perspectives and key developments concerning {clean_title.lower()}.'

    return {
        'guest': guest,
        'topics': matched_topics[:4],
        'theme': theme
    }


def parse_duration_seconds(dur_str):
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

            meta = lvm.get('metadata', {}).get('lockupMetadataViewModel', {})
            title = meta.get('title', {}).get('content', '')

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

            duration = ''
            overlays = lvm.get('contentImage', {}).get('thumbnailViewModel', {}).get('overlays', [])
            for ov in overlays:
                badges = ov.get('thumbnailBottomOverlayViewModel', {}).get('badges', [])
                for b in badges:
                    dur_text = b.get('thumbnailBadgeViewModel', {}).get('text', '')
                    if dur_text and ':' in dur_text:
                        duration = dur_text

            dur_secs = parse_duration_seconds(duration)
            if 0 < dur_secs < 120:
                continue
            lower_title = title.lower()
            if any(kw in lower_title for kw in ['#shorts', '#short', 'clip', 'highlight', 'trailer', 'teaser']):
                continue

            thumb_url = f'https://i.ytimg.com/vi/{vid_id}/maxresdefault.jpg'
            link = f'https://www.youtube.com/watch?v={vid_id}'

            intel = extract_podcast_intelligence(title, source['name'])
            category = classify_category(title)

            episodes.append({
                'id': f'tp_{vid_id}',
                'title': title,
                'podcast': source['name'],
                'channel': source['name'],
                'podcastLogo': source['logo'],
                'tier': source['tier'],
                'guest': intel['guest'],
                'topics': intel['topics'],
                'theme': intel['theme'],
                'imageUrl': thumb_url,
                'thumbnail': thumb_url,
                'link': link,
                'youtube_url': link,
                'pubDate': published,
                'date': published,
                'duration': duration,
                'views': views,
                'category': category,
                'resonant_news': [],
            })
        break

    return episodes


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


def load_existing_podcasts(podcasts_path=None):
    """Load existing podcasts.json to preserve existing resonant_news mappings and episode history."""
    path = podcasts_path or PODCASTS_PATH
    if not os.path.exists(path):
        return {}
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, dict):
                raw_eps = data.get('episodes')
                data['episodes'] = raw_eps if isinstance(raw_eps, list) else []
                return data
    except Exception as e:
        print(f"[WARN] Could not load existing podcasts from {path}: {e}")
    return {}


def main():
    podcasts_path = PODCASTS_PATH

    # 1. Load existing podcasts.json to preserve prior resonant_news linkages
    existing_data = load_existing_podcasts(podcasts_path)
    existing_episodes = (existing_data.get('episodes') or []) if isinstance(existing_data, dict) else []

    existing_resonant = {}
    for ep in existing_episodes:
        if isinstance(ep, dict):
            res_news = ep.get('resonant_news', [])
            if res_news:
                if ep.get('id'):
                    existing_resonant[ep['id']] = res_news
                if ep.get('link'):
                    existing_resonant[ep['link']] = res_news

    # 2. Scrape live channels
    all_episodes = []
    for src in PODCAST_SOURCES:
        print(f"Fetching {src['name']}...")
        try:
            eps = scrape_channel(src)
            all_episodes.extend(eps)
            print(f"  -> Got {len(eps)} episodes")
        except Exception as e:
            print(f"  [ERROR] {src['name']}: {e}")

    # 3. Guard against empty scrapes: do NOT overwrite existing data with empty list
    if not all_episodes or len(all_episodes) == 0:
        print("\n[WARN] Podcast scraping returned 0 episodes (empty scrape).")
        print("Preserving existing data/podcasts.json to prevent data loss.")
        return

    # 4. Preserve existing resonant_news mappings for refreshed episodes
    for ep in all_episodes:
        ep_id = ep.get('id', '')
        ep_link = ep.get('link', '')
        if ep_id in existing_resonant:
            ep['resonant_news'] = existing_resonant[ep_id]
        elif ep_link in existing_resonant:
            ep['resonant_news'] = existing_resonant[ep_link]
        else:
            ep.setdefault('resonant_news', [])

    # 5. Preserve un-refreshed episodes from existing data if not re-scraped
    scraped_ids = {ep.get('id') for ep in all_episodes if ep.get('id')}
    for ex_ep in existing_episodes:
        if isinstance(ex_ep, dict):
            ex_id = ex_ep.get('id')
            if ex_id and ex_id not in scraped_ids:
                ex_ep.setdefault('resonant_news', [])
                all_episodes.append(ex_ep)
                scraped_ids.add(ex_id)

    # 6. Sort newest first
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

    # 7. Cap episodes per source to prevent domination
    capped_episodes = []
    source_counts = {}
    for ep in all_episodes:
        src_name = ep.get('podcast', '')
        count = source_counts.get(src_name, 0)
        if count < 3: # Max 3 episodes per source
            capped_episodes.append(ep)
            source_counts[src_name] = count + 1
        
        if len(capped_episodes) >= 30:
            break
            
    all_episodes = [normalize_episode_schema(ep) for ep in capped_episodes]

    print(f"\nTotal: {len(all_episodes)} episodes")

    # Final guard before writing: never wipe podcasts.json with empty list
    if not all_episodes or len(all_episodes) == 0:
        print("[WARN] Post-processing resulted in empty episode list. Preserving existing data/podcasts.json.")
        return

    output = {
        'lastUpdated': datetime.now(timezone.utc).isoformat(),
        'total': len(all_episodes),
        'episodes': all_episodes,
    }
    os.makedirs(os.path.dirname(podcasts_path), exist_ok=True)
    temp_path = f"{podcasts_path}.tmp"
    with open(temp_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    os.replace(temp_path, podcasts_path)
    print(f"\nSaved {len(all_episodes)} episodes with topics and themes to data/podcasts.json")


if __name__ == '__main__':
    main()
