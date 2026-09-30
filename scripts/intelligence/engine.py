# Copyright (c) 2026 Kashish Bhushan — News Colossal
# All Rights Reserved. Proprietary and confidential.
#
# EDITORIAL INTELLIGENCE ENGINE — Master Orchestrator
# Runs all 4 layers of the intelligence pipeline in sequence.

import os
import sys
import io
import json
import time
from datetime import datetime, timezone

# Force UTF-8 stdout to prevent Windows cp1252 encoding errors
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Ensure the scripts directory is importable
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_PARENT_DIR = os.path.dirname(_SCRIPT_DIR)
if _PARENT_DIR not in sys.path:
    sys.path.insert(0, _PARENT_DIR)

from intelligence.intake import run_intake
from intelligence.scoring import run_scoring
from intelligence.memory import load_memory, save_memory, update_memory, prune_stale_arcs, get_active_arcs
from intelligence.meta import run_meta_intelligence
from intelligence.curation import run_curation


# Default memory file location (relative to Newsfeed project root)
# _SCRIPT_DIR is scripts/intelligence/, so go up twice to reach project root
_PROJECT_ROOT = os.path.dirname(os.path.dirname(_SCRIPT_DIR))
_DEFAULT_MEMORY_PATH = os.path.join(_PROJECT_ROOT, 'data', 'narrative_memory.json')


def run_editorial_intelligence(articles, podcasts=None, memory_path=None):
    """Run the complete 4-layer Editorial Intelligence Engine.

    This is the master orchestrator that transforms raw fetched articles
    into an editorially intelligent, ranked, and curated news feed.

    Pipeline:
        Layer 1 (Intake)  -> Noise filter + Entity extraction + Dedup
        Layer 2 (Scoring) -> 8-editor scoring panel
        Layer 3 (Meta)    -> Contrarian/black swan/arbitrage/provenance
        Layer 4 (Curation)-> Ranking + cognitive diet + narrative threading + resonance

    Args:
        articles: List of article dicts from fetch_news.py
        podcasts: Optional list of podcast episode dicts from fetch_podcasts.py
        memory_path: Path to narrative_memory.json (defaults to data/narrative_memory.json)

    Returns:
        (processed_articles, processed_podcasts, intelligence_report)
    """
    if memory_path is None:
        memory_path = _DEFAULT_MEMORY_PATH

    start_time = time.time()
    input_count = len(articles)
    podcast_count = len(podcasts) if podcasts else 0

    print("")
    print("+" + "=" * 58 + "+")
    print("|  NEWS COLOSSAL -- EDITORIAL INTELLIGENCE ENGINE           |")
    print("|  4-Layer Deep Curation Pipeline                           |")
    print("+" + "=" * 58 + "+")
    print(f"\n  Input: {input_count} articles, {podcast_count} podcast episodes")
    print(f"  Memory: {memory_path}")

    # -- LAYER 1: INTAKE ------------------------------------------------
    print("\n" + "=" * 60)
    print("LAYER 1: INTAKE -- Noise Filter + Entity Extraction + Dedup")
    print("=" * 60)

    articles, intake_stats = run_intake(articles)

    # -- LAYER 2: SCORING -----------------------------------------------
    print("\n" + "=" * 60)
    print("LAYER 2: SCORING -- 8-Editor Intelligence Panel")
    print("=" * 60)

    # Load narrative memory for scoring context
    memory = load_memory(memory_path)
    active_arcs = get_active_arcs(memory)
    print(f"\n  Loaded {len(active_arcs)} active narrative arcs from memory")

    articles = run_scoring(articles, narrative_arcs=active_arcs)

    # -- LAYER 3: META-INTELLIGENCE -------------------------------------
    print("\n" + "=" * 60)
    print("LAYER 3: META-INTELLIGENCE -- Contrarian + Black Swan + Provenance")
    print("=" * 60)

    articles = run_meta_intelligence(articles)

    # -- LAYER 4: CURATION ----------------------------------------------
    articles, podcasts_out, curation_stats = run_curation(
        articles, podcasts=podcasts, memory=memory
    )

    # -- UPDATE NARRATIVE MEMORY ----------------------------------------
    print("\n" + "=" * 60)
    print("NARRATIVE MEMORY UPDATE")
    print("=" * 60)

    memory = update_memory(memory, articles)
    memory = prune_stale_arcs(memory, max_age_days=14)
    save_memory(memory, memory_path)

    arc_count = len(memory.get('arcs', []))
    print(f"\n  Memory updated: {arc_count} narrative arcs tracked")
    print(f"  Memory saved to: {memory_path}")

    # -- FINAL REPORT ---------------------------------------------------
    elapsed = time.time() - start_time

    intelligence_report = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'elapsed_seconds': round(elapsed, 2),
        'input_articles': input_count,
        'input_podcasts': podcast_count,
        'intake': intake_stats,
        'curation': curation_stats,
        'narrative_arcs_tracked': arc_count,
        'output_articles': len(articles),
        'output_podcasts': len(podcasts_out) if podcasts_out else 0,
    }

    print("")
    print("+" + "=" * 58 + "+")
    print("|  INTELLIGENCE PIPELINE COMPLETE                           |")
    print("+" + "=" * 58 + "+")
    print(f"\n  Input:  {input_count} articles -> Output: {len(articles)} articles")
    print(f"  Noise rejected:        {intake_stats.get('noise_rejected', 0)}")
    print(f"  Duplicates suppressed: {intake_stats.get('duplicates_suppressed', 0)}")
    print(f"  Narrative arcs:        {arc_count}")
    print(f"  Podcast resonances:    {curation_stats.get('podcast_resonances', 0)}")
    print(f"  Elapsed time:          {elapsed:.2f}s")

    # Top 10 stories
    print(f"\n  -- TOP 10 STORIES BY INTELLIGENCE SCORE --")
    for i, art in enumerate(articles[:10]):
        score = art.get('importance_score', 0)
        ctype = art.get('cognitive_type', '?')
        src = art.get('source', '?')
        title = art.get('title', '?')[:65]
        flags = []
        meta = art.get('meta', {})
        if meta.get('is_contrarian'):
            flags.append('[CONTRARIAN]')
        if meta.get('is_black_swan'):
            flags.append('[BLACK SWAN]')
        if meta.get('is_exclusive'):
            flags.append('[EXCLUSIVE]')
        if art.get('narrative_arc', {}).get('arc_id'):
            flags.append('[ARC]')
        if art.get('resonant_podcast'):
            flags.append('[PODCAST]')
        flag_str = ' '.join(flags)
        print(f"    #{i+1:2d} [{score:5.2f}] [{ctype:13s}] [{src:18s}] {title}")
        if flag_str:
            print(f"         {flag_str}")

    return articles, podcasts_out, intelligence_report
