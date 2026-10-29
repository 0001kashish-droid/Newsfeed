# Cleanse narrative_memory.json and re-thread news.json
import json
import os

MEDIA_WIRE = {'reuters', 'ap', 'bbc', 'bloomberg', 'afp', 'cnn', 'msnbc', 'fox'}

mem_path = 'data/narrative_memory.json'
with open(mem_path, 'r', encoding='utf-8') as f:
    mem = json.load(f)

cleaned_arcs = []
for arc in mem.get('arcs', []):
    sig = arc.get('entity_signature', '')
    parts = [p.strip() for p in sig.replace('+', ':').split(':') if p.strip()]
    clean_parts = [p for p in parts if p.lower() not in MEDIA_WIRE]
    
    # If the arc has no topical entities left, drop it
    if not clean_parts:
        print(f"Dropping corrupted arc: {arc.get('arc_id')} - {arc.get('title')}")
        continue
    
    arc['entity_signature'] = ':'.join(clean_parts)
    
    # If this was the Apple arc or has corrupted chapters, clean chapter titles
    if '00d4e7ae' in arc.get('arc_id', ''):
        chaps = arc.get('chapter_titles', [])
        valid_chaps = [c for c in chaps if any(w in c.lower() for w in ['apple', 'mac', 'ai requests'])]
        arc['chapter_titles'] = valid_chaps
        arc['chapter_count'] = len(valid_chaps)
    
    cleaned_arcs.append(arc)

mem['arcs'] = cleaned_arcs
with open(mem_path, 'w', encoding='utf-8') as f:
    json.dump(mem, f, indent=4, ensure_ascii=False)

print(f"Cleaned narrative_memory.json: {len(cleaned_arcs)} valid arcs remaining.")

# Now re-thread data/news.json using the updated memory and matching rules
import sys
sys.path.insert(0, os.path.abspath('scripts'))
from intelligence.curation import thread_narratives

news_path = 'data/news.json'
with open(news_path, 'r', encoding='utf-8') as f:
    news_data = json.load(f)

articles = news_data.get('articles', [])
# Clear any old _matched_arc_id to force re-evaluation
for a in articles:
    a.pop('_matched_arc_id', None)

articles = thread_narratives(articles, mem)
news_data['articles'] = articles

with open(news_path, 'w', encoding='utf-8') as f:
    json.dump(news_data, f, indent=2, ensure_ascii=False)

print("Successfully re-threaded data/news.json")
