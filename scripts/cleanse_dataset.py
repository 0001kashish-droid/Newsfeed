# Copyright (c) 2026 Kashish Bhushan — News Colossal
# Dataset Cleansing Script for Milestone 1
import os
import sys
import json
import re

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

from intelligence.sanitizer import sanitize_dispatch, is_quarantined_publisher

_PROJECT_ROOT = os.path.dirname(_SCRIPT_DIR)
_NEWS_PATH = os.path.join(_PROJECT_ROOT, 'data', 'news.json')

def main():
    print(f"Loading {_NEWS_PATH}...")
    with open(_NEWS_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    articles = data.get('articles', [])
    print(f"Loaded {len(articles)} articles.")

    titles_sanitized = 0
    descs_sanitized = 0
    wire_orgs_removed = 0

    for art in articles:
        source = art.get('source', '')
        old_title = art.get('title', '')
        old_desc = art.get('description', '')

        res = sanitize_dispatch(old_title, old_desc, source)
        if res['clean_title'] != old_title:
            titles_sanitized += 1
            art['title'] = res['clean_title']
        if res['clean_description'] != old_desc:
            descs_sanitized += 1
            art['description'] = res['clean_description']

        if 'annotation' in art and isinstance(art['annotation'], dict):
            if 'what' in art['annotation']:
                art['annotation']['what'] = sanitize_dispatch(art['annotation']['what'], '')['clean_title']
            if 'why' in art['annotation']:
                art['annotation']['why'] = sanitize_dispatch(art['annotation']['why'], '')['clean_description']

        if 'entities' in art and isinstance(art['entities'], dict):
            orgs = art['entities'].get('organizations', [])
            before_len = len(orgs)
            art['entities']['organizations'] = [
                o for o in orgs if not is_quarantined_publisher(o.get('name', '') if isinstance(o, dict) else str(o))
            ]
            wire_orgs_removed += (before_len - len(art['entities']['organizations']))

            comps = art['entities'].get('companies', [])
            art['entities']['companies'] = [
                c for c in comps if not is_quarantined_publisher(c.get('name', '') if isinstance(c, dict) else str(c))
            ]

            leaders = art['entities'].get('leaders', [])
            art['entities']['leaders'] = [
                l for l in leaders if not is_quarantined_publisher(l.get('name', '') if isinstance(l, dict) else str(l))
            ]

            cnt = sum(len(art['entities'].get(s, [])) for s in ('countries', 'leaders', 'organizations', 'companies'))
            art['entities']['entity_count'] = cnt
            words = len(re.findall(r'\b\w+\b', f"{art['title']} {art['description']}"))
            art['entities']['entity_density'] = round(cnt / words, 4) if words > 0 else 0.0

        prov = art.setdefault('provenance', {})
        if not isinstance(prov, dict):
            prov = {}
            art['provenance'] = prov
        prov['wire_quarantined'] = True
        if res.get('stripped_dateline'):
            prov['stripped_dateline'] = res['stripped_dateline']
        if res.get('stripped_attribution'):
            prov['stripped_attribution'] = res['stripped_attribution']
        if res.get('meta_flags'):
            prov['editorial_flags'] = res['meta_flags']
            art.setdefault('meta', {}).update(res['meta_flags'])

    tmp_path = _NEWS_PATH + '.tmp'
    with open(tmp_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(tmp_path, _NEWS_PATH)

    print(f"Cleansing complete:")
    print(f"  Titles sanitized: {titles_sanitized}")
    print(f"  Descriptions sanitized: {descs_sanitized}")
    print(f"  Wire organizations removed: {wire_orgs_removed}")

if __name__ == '__main__':
    main()
