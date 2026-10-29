# Copyright (c) 2026 Kashish Bhushan — News Colossal
# Dataset Re-enrichment Script for Milestone 2 Iteration 2
import json
import os
import sys

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_SCRIPT_DIR)
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

from intelligence.entities import extract_entities
from intelligence.sanitizer import is_quarantined_publisher

_NEWS_PATH = os.path.join(_PROJECT_ROOT, 'data', 'news.json')

def main():
    print(f"Loading {_NEWS_PATH}...")
    with open(_NEWS_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    articles = data.get('articles', [])
    print(f"Loaded {len(articles)} articles.")

    updated_count = 0
    clean_actors = 0
    null_actors = 0
    factions_total = 0

    for i, art in enumerate(articles):
        title = art.get('title', '')
        description = art.get('description', '')
        region = art.get('region', '')

        extracted = extract_entities(title, description, region=region)
        actors = extracted['primary_actors']

        # Enforce quarantine guard
        if actors.get('active_agent') and is_quarantined_publisher(actors['active_agent']):
            actors['active_agent'] = None
            actors['active_agent_type'] = None

        art['entities'] = extracted
        art['primary_actors'] = actors

        updated_count += 1
        if actors.get('active_agent'):
            clean_actors += 1
        else:
            null_actors += 1

        factions_total += len(actors.get('collective_factions', []))

    tmp_path = _NEWS_PATH + '.tmp'
    with open(tmp_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(tmp_path, _NEWS_PATH)

    print(f"Re-enrichment complete across {updated_count} articles:")
    print(f"  Active agents present: {clean_actors}")
    print(f"  Honest nulls: {null_actors}")
    print(f"  Collective faction mentions: {factions_total}")

if __name__ == '__main__':
    main()
