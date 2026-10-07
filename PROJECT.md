# Project: News Colossal Remediation

## Architecture
News Colossal is an autonomous news intelligence platform featuring RSS news ingestion, YouTube podcast scraping, narrative arc tracking, deduplication, cross-regional perspective clustering, automated daily digest newsletter archival/dispatch, and a high-fidelity VisionOS-inspired frontend interface.

```
[RSS Feeds] ──> fetch_news.py ──> intake.py (dedup) ──> memory.py (arcs) ──> curation.py ──> data/news.json
                                                                                                      │
[YouTube]   ──> fetch_podcasts.py ─────────────────────────> data/podcasts.json <─────────────────────┘ (mutual resonance)
                                                                    │
[Data Files] ──> generate_daily_newsletter.py ──> newsletters/YYYY-MM-DD.md
                                                                    │
[Data Files] ──> Frontend (index.html, app.js, style.css) ──> Executive Reader Deck & Thought Pulse
```

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | Newsletter Buttondown Optionality | Bypasses Buttondown dispatch when `BUTTONDOWN_API_KEY` is missing without failing | M1 | Survey 1, R1 |
| 2 | Daily Digest Archival | Formats and archives daily newsletter markdown in `newsletters/YYYY-MM-DD.md` | M1 | Survey 1, R1 |
| 3 | Newsletter Console Encoding Fix | Eliminates cp1252 character map crashes by avoiding non-ASCII console output or UTF-8 reconfiguration | M1 | Survey 1, R1 |
| 4 | GitHub Actions Digest Workflow | Ensures `.github/workflows/daily_digest.yml` executes reliably with proper error handling | M1 | Survey 1, R1 |
| 5 | Synchronization Pipeline Order | Inverts `.github/workflows/fetch-news.yml` to run `fetch_podcasts.py` before `fetch_news.py` | M2 | Survey 1/2, R2 |
| 6 | Podcast Resonance Preservation | `fetch_podcasts.py` preserves existing `resonant_news` and guards against empty scrapes | M2 | Survey 1/2, R2 |
| 7 | Mutual Resonance Link Generation | `fetch_news.py` produces non-empty resonance links in both `data/news.json` and `data/podcasts.json` | M2 | Survey 1/2, R2 |
| 8 | Entity Parsing in Narrative Memory | Flattens categorized entity dictionaries so entity matching scores function correctly | M3 | Survey 2, R3 |
| 9 | Autonomous Arc Threading | Links qualifying articles to active narrative arcs in `data/narrative_memory.json` with non-null `arc_id` | M3 | Survey 1/2, R3 |
| 10 | Duplicate Story Suppression | Drops `is_duplicate: true` articles from feed intake so 0 duplicates leak into `data/news.json` | M3 | Survey 1/2, R4 |
| 11 | Distinct Publisher Perspective Pairs | Requires `>= 2` distinct publishers and brand families for cross-regional perspective cards | M3 | Survey 1/2, R4 |
| 12 | Brand Family Diversity Cap (<=18%) | Adds `BBC Business` to `BRAND_FAMILIES` and dynamically enforces <= 18% cap per publisher family | M3 | Survey 1/2, R5 |
| 13 | Clean Sentence Boundary Truncation | Truncates article descriptions at sentence/word boundaries ending with `.` without trailing ellipses | M3 | Survey 1/2/3, R5 |
| 14 | Executive Reader Modal Intelligence | Renders podcast resonance box and narrative arc tracker inside Executive Reader Deck modal | M4 | Survey 1/3, R6 |
| 15 | Thought Pulse Resonant News Bridge | Renders clickable resonant news pill on Thought Pulse cards linking to reader modal | M4 | Survey 3, R6 |
| 16 | VisionOS Liquid Glass & 3D Physics | Adds liquid glass styling, maintains mobile responsiveness, and extends 3D tilt to cards and modal | M4 | Survey 3, R6 |
| 17 | Zero-Failure Hard Audit Validation | Upgrades and executes `production_hard_audit.py` to achieve 0 failures and 0 warnings across all requirements | M5 | Survey 1/2/3, R7 |
| 18 | E2E Regression Verification | Validates full pipeline execution sequence and data integrity end-to-end | M5 | Acceptance Criteria |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M1 | Daily Digest Archival & Dispatch Pipeline | `generate_daily_newsletter.py`, `.github/workflows/daily_digest.yml`, `newsletters/` | none | PLANNED |
| M2 | Pipeline Synchronization & Podcast Resonance | `.github/workflows/fetch-news.yml`, `scripts/fetch_podcasts.py`, `scripts/fetch_news.py` | none | PLANNED |
| M3 | Data Intelligence, Arcs, Dedup & Diversity | `scripts/intelligence/intake.py`, `memory.py`, `curation.py`, `engine.py`, `scripts/fetch_news.py` | M2 | PLANNED |
| M4 | Frontend Intelligence Integration & UI Fidelity | `app.js`, `style.css`, `index.html` | M2, M3 | PLANNED |
| M5 | End-to-End Verification & Master Audit | `production_hard_audit.py`, full workflow execution, E2E test suite | M1, M2, M3, M4 | PLANNED |

## Interface Contracts

### M1 Contract (`generate_daily_newsletter.py`)
- CLI entrypoint: `python generate_daily_newsletter.py`
- Environment: `BUTTONDOWN_API_KEY` optional. If missing/empty, logs info, archives markdown to `newsletters/YYYY-MM-DD.md`, skips HTTP POST, exits code 0.
- Console encoding: No non-ASCII characters that trigger `UnicodeEncodeError` in cp1252.

### M2 Contract (`fetch_podcasts.py` ↔ `fetch_news.py`)
- Execution sequence: `fetch_podcasts.py` runs before `fetch_news.py`.
- `data/podcasts.json` schema:
  - `episodes[]`: contains `id`, `title`, `podcast`, `channel`, `date`, `duration`, `thumbnail`, `youtube_url`, `topics`, `theme`, and optionally `resonant_news` (`[{id, title, url, source, resonance_score}]`).
  - `fetch_podcasts.py` preserves existing `resonant_news` for un-refreshed episodes and avoids wiping data on empty scrape.
- `data/news.json` schema:
  - `articles[]`: contains `resonant_podcast` (`{podcast_title, episode_title, youtube_url, resonance_score}`).

### M3 Contract (Data Intelligence Engine)
- `intake.py`: `enhanced_dedup` filters out `is_duplicate: True` items so they never enter downstream articles.
- `memory.py`: `match_article_to_arc` extracts all entities from `article['entities'].values()` and matches against `arc['entities']`.
- `curation.py`: `thread_narratives` populates `art['narrative_arc']` with `{arc_id, arc_title, day_number, total_chapters, importance_trend}` matching `data/narrative_memory.json`.
- `fetch_news.py`:
  - `BRAND_FAMILIES`: includes `"BBC Business": "BBC"`.
  - Brand cap: each brand family count $\le \lfloor 0.18 \times N \rfloor$.
  - `cluster_stories`: requires `len(set(p['source'] for p in perspectives)) >= 2` and distinct brand families.
  - `format_clean_description`: terminates on complete sentence/word boundary ending with `.`, no trailing `...` or `…`.

### M4 Contract (Frontend Interface)
- `app.js`:
  - `renderExecutiveModal(art)`: renders `.liquid-glass-resonance-box` (if `art.resonant_podcast`) and `.liquid-glass-narrative-box` (if `art.narrative_arc` with valid `arc_id`).
  - `renderThoughtPulse(ep)`: renders `.thought-card-resonant-news` button if `ep.resonant_news` exists, triggering `openModal(ep.resonant_news[0].id)`.
  - 3D tilt: attaches to `.news-card` and `.thought-card`.
- `style.css`:
  - Styles for `.liquid-glass-resonance-box`, `.liquid-glass-narrative-box`, and `.thought-card-resonant-news`.
  - VisionOS liquid glass aesthetic, ambient aurora, mobile responsive layout intact.

### M5 Contract (Verification & Audit)
- `production_hard_audit.py` passes 100% with 0 failures and 0 warnings.
- All acceptance criteria verified:
  - Pipeline runs exit 0.
  - Mutual resonance links > 0 in both JSON files.
  - Articles linked to active arcs in `narrative_memory.json`.
  - 0 duplicate articles.
  - Cross-regional pairs have distinct publishers.
  - Brand families $\le 18\%$.
  - Clean sentence endings (0 description warnings).

## Code Layout
- `generate_daily_newsletter.py`: newsletter generation & Buttondown dispatch.
- `newsletters/`: archived markdown digests.
- `scripts/fetch_podcasts.py`: YouTube podcast scraping & resonance preservation.
- `scripts/fetch_news.py`: RSS news ingestion, clustering, brand caps, formatting, mutual resonance.
- `scripts/intelligence/`:
  - `intake.py`: deduplication and intake filtering.
  - `memory.py`: narrative memory and arc matching.
  - `curation.py`: narrative arc threading and quality scoring.
  - `engine.py`: intelligence pipeline runner.
- `data/`:
  - `news.json`: primary news dataset.
  - `podcasts.json`: primary podcast dataset.
  - `narrative_memory.json`: active and archived narrative arcs.
- `.github/workflows/`:
  - `fetch-news.yml`: hourly news & podcast synchronization.
  - `daily_digest.yml`: daily newsletter generation workflow.
- Frontend:
  - `index.html`: main single-page application.
  - `app.js`: frontend logic, executive modal, thought pulse, 3D physics.
  - `style.css`: VisionOS liquid glass styles, layout, responsive queries.
- Audit & Verification:
  - `production_hard_audit.py`: master production hard audit.
