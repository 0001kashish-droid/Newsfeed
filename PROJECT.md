# Project: News Colossal — Hermetic News Intelligence Engine

## Architecture
News Colossal is a mathematically hermetic, zero-dependency news intelligence and logic engine. The backend pipeline is implemented strictly in the Python standard library (zero external APIs, zero pip packages), and the frontend is implemented in vanilla ES6+ / CSS3.

```
[RSS Feeds]
     │
     ▼
scripts/fetch_news.py ──> scripts/intelligence/sanitizer.py (7-Stage Automaton)
                                    │
                                    ├──> scripts/intelligence/intake.py (Quarantine Sieve)
                                    │         │
                                    │         ▼
                                    ├──> scripts/intelligence/entities.py (Syntactic 5W1H Grammar)
                                    │         │
                                    │         ▼
                                    ├──> scripts/intelligence/memory.py (Tri-Anchor Coherence Invariant)
                                    │         │
                                    │         ▼
                                    ├──> scripts/intelligence/curation.py (Honest Nulls & Curation)
                                    │         │
                                    ▼         ▼
                              data/news.json & data/narrative_memory.json
                                    │
                                    ▼
Frontend (index.html, app.js, style.css) ──> Adaptive UI Morphology & Executive Reader Deck
                                    │
                                    ▼
Tests & Audit: tests/test_hermetic_intelligence.py & production_hard_audit.py
```

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | 7-Stage Sanitization Automaton | Deterministic automaton in `sanitizer.py` stripping wire datelines, attribution suffixes, parentheticals, and editorial slugs | M1 | Survey 1, R1, R6 |
| 2 | Provenance Quarantine Sieve | Quarantines wire publishers to `provenance` ledger; mathematically bars them from `entities`, `primary_actors`, and `narrative_arcs` | M1 | Survey 1, R1, R6 |
| 3 | Ingestion & Intake Title Mutation | Mutates `article['title']` and `description` with clean text in `fetch_news.py` and `intake.py` | M1 | Survey 1, R1 |
| 4 | Entity Lexicon Decontamination | Removes `Reuters`, `AP`, `BBC` from `_ORG_MAPPINGS` and prevents bureau dateline city misattributions | M1 | Survey 1, R1 |
| 5 | Pronoun-Acronym Disambiguation | Resolves `who` vs `WHO` and `us` vs `US` collision bug in `entities.py` | M2 | Survey 2, R2 |
| 6 | Syntactic 5W1H Actor Grammar | Pure stdlib rule-based NP boundary analyzer and verb anchor extractor (`[Subject] [Verb] [Object]`) | M2 | Survey 2, R2, R6 |
| 7 | Collective Faction Recognition | Lexicon-based extraction of 8 non-state factions (insurgents, military commands, protesters, civilians, regulators, courts, envoys, researchers) | M2 | Survey 2, R2 |
| 8 | Sovereign Regional Stakeholders | Maps unled stories to regional/national sovereign stakeholders without synthetic `Editorial Bureau` fallbacks | M2 | Survey 2, R2 |
| 9 | Tri-Anchor Coherence Invariant | Strict logical AND across Anchor 1 (Geopolitical Theater), Anchor 2 (Entity Intersection $\ge 2$ or 1 leader+cat), Anchor 3 (Lexical Jaccard $\ge 0.30$) | M3 | Survey 2, R3, R6 |
| 10 | Standalone Dispatch Isolation | Isolates stories failing any anchor as standalone dispatches with `arc_id: null` | M3 | Survey 2, R3 |
| 11 | Narrative Memory Decontamination | Cleanses corrupt 85-chapter arc `5b745eea-...` in `narrative_memory.json` and rebuilds authentic chapters | M3 | Survey 2, R3 |
| 12 | Synthetic Fallback Elimination | Removes all canned strings (`"Verified news intelligence..."`, `"Regional & Non-State Factions"`, `"8.4 / 10"`, `"Editorial Bureau"`) | M4 | Survey 3, R4 |
| 13 | Adaptive UI Morphology | Dynamically reconfigures Executive Reader Deck and card layouts based on available dimensions (Hero Core Event, Bento, etc.) | M4 | Survey 3, R4 |
| 14 | Standalone Scrubber Suppression | Completely hides narrative timeline and scrubber inside Reader Deck when `arc_id: null` | M4 | Survey 3, R4 |
| 15 | Subordinate Provenance Ledger UI | Renders wire source exclusively as subordinate metadata (`📡 Chronicled by {source}`) | M4 | Survey 1/3, R1, R4 |
| 16 | Adversarial Wire Injection Fuzz Suite | Fuzzes dispatches with synthetic wire datelines, suffixes, and parentheticals; verifies 0 leakage | M5 | Survey 1/3, R5 |
| 17 | Cross-Topic Collision Resistance | High-entropy cross-topic mixes verify 0% false narrative binding across disparate topic domains | M5 | Survey 2/3, R5 |
| 18 | Hermetic Integrity & Production Audit | Validates 100% pass in `test_hermetic_intelligence.py`, `test_e2e_remediation.py`, and `production_hard_audit.py` (0 failures, 0 warnings) | M5 | Survey 1/2/3, R5, R6 |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M1 | Provenance Quarantine Sieve & Wire Sanitization | `scripts/intelligence/sanitizer.py`, `scripts/intelligence/entities.py`, `scripts/intelligence/intake.py`, `scripts/fetch_news.py`, `data/news.json` | none | DONE |
| M2 | Syntactic 5W1H Actor Grammar & Collective Factions | `scripts/intelligence/entities.py`, `data/news.json` | M1 | DONE |
| M3 | Tri-Anchor Semantic Narrative Arc Coherence | `scripts/intelligence/memory.py`, `scripts/intelligence/curation.py`, `data/narrative_memory.json`, `data/news.json` | M1, M2 | IN_PROGRESS |
| M4 | Adaptive UI Morphology & Honest Nulls | `app.js`, `style.css`, `index.html` | M2, M3 | PLANNED |
| M5 | Adversarial Regression Harness & Master Hard Audit | `tests/test_hermetic_intelligence.py`, `production_hard_audit.py`, full test suite discovery | M1, M2, M3, M4 | PLANNED |

## Interface Contracts

### M1 Contract: Provenance Quarantine Sieve (`sanitizer.py` ↔ `intake.py` ↔ `entities.py`)
- `scripts/intelligence/sanitizer.py`:
  - `normalize_text(text: str) -> str`
  - `sanitize_dispatch(title: str, description: str, source: str = '') -> Dict[str, Any]`:
    - Returns `{'clean_title': str, 'clean_description': str, 'stripped_dateline': Optional[str], 'stripped_attribution': Optional[str], 'meta_flags': dict}`.
  - `is_quarantined_publisher(name: str) -> bool`
  - `PUBLISHER_QUARANTINE_SET`: frozenset of all known wires, agencies, broadcasters, and newspaper brand tokens.
- `scripts/fetch_news.py`: Calls `sanitize_dispatch()` in `fetch_rss()`.
- `scripts/intelligence/intake.py`: Mutates `art['title']` and `art['description']` with clean text; stores quarantine status in `art['provenance']`.
- `scripts/intelligence/entities.py`: Excludes wire publishers from `_ORG_MAPPINGS` and filters results with `is_quarantined_publisher()`.
- Invariant: `entities.organizations` contains 0 wire publishers.

### M2 Contract: Syntactic 5W1H Actor Grammar (`entities.py` ↔ `data/news.json`)
- Class `SyntacticActorGrammar` in `scripts/intelligence/entities.py`:
  - Method `extract_actors(title: str, description: str, entities: dict, region: str) -> dict`.
  - Output schema in `article['primary_actors']`:
    ```json
    {
      "active_agent": "string or null",
      "active_agent_type": "leader | collective_faction | sovereign_stakeholder | syntactic_subject | null",
      "impacted_population": "string or null",
      "impacted_type": "impacted_community | state_body | null",
      "collective_factions": [
        {
          "category": "Insurgent / Rebel Factions | Military Command / Armed Forces | Civic Activists / Protesters | Civilians & Impacted Communities | Regulatory & State Authorities | Judicial & Investigative Bodies | Diplomatic Envoys | Scientific & Research Teams",
          "matched_text": "string",
          "canonical_label": "string"
        }
      ],
      "leaders": ["string"],
      "sovereign_stakeholders": ["string"],
      "syntactic_frame": {
        "subject": "string",
        "verb": "string",
        "object": "string"
      }
    }
    ```
- Invariant: Never outputs `Editorial Bureau`, `Syndicated Bureau`, or wire names.

### M3 Contract: Tri-Anchor Coherence Invariant (`memory.py` ↔ `curation.py`)
- `scripts/intelligence/memory.py`:
  - `substantive_stems(text: str) -> Set[str]`: Standard-library token stemmer and noise filter.
  - `match_article_to_arc(article: dict, arcs: list, threshold: float = 0.30) -> tuple`:
    - Evaluates:
      - Anchor 1: $C(A) \cap C(M) \neq \emptyset$ or region match without 'Global'.
      - Anchor 2: $|E(A) \cap E(M)| \ge 2$ or ($|L(A) \cap L(M)| \ge 1 \land \text{category}(A) == \text{category}(M)$).
      - Anchor 3: Lexical Jaccard overlap on substantive stems $\ge 0.30$.
    - Returns `(matched_arc, jaccard_score)` if all 3 anchors True; else `(None, 0.0)`.
- `scripts/intelligence/curation.py`:
  - Standalone dispatches receive `narrative_arc: {'arc_id': None, 'arc_title': None, 'day_number': 0, 'total_chapters': 0, 'importance_trend': None, 'previous_headlines': []}`.
- Invariant: 0% cross-topic collision between disparate domains.

### M4 Contract: Adaptive UI Morphology (`app.js` ↔ `style.css` ↔ `index.html`)
- `renderExecutiveModal(art)`:
  - If `art.primary_actors`: displays authentic active agents, collective factions, and sovereign stakeholders. Zero occurrences of `Editorial Bureau`.
  - Subordinate provenance: `📡 Chronicled by {art.source}`.
  - If `!art.narrative_arc || !art.narrative_arc.arc_id`: completely hides narrative scrubber and chapter steppers; dynamically expands core intelligence grid.
  - Zero placeholder strings (`"Verified news intelligence event..."`, `"8.4 / 10"`).

### M5 Contract: Adversarial Verification & Master Hard Audit
- `tests/test_hermetic_intelligence.py`:
  - Test suite with 5 classes: Wire Injection Fuzzing, Cross-Topic Collision Resistance, Syntactic Actor Grammar, Standalone Dispatches & Honest Nulls, and Pure Standard Library compliance.
  - Exit code 0, 0 failures, 0 errors.
- `production_hard_audit.py`: 100% pass across all 6 layers with 0 failures and 0 warnings.
- `python -m unittest discover -s tests -p "test_*.py"`: All tests pass.

## Code Layout
- `scripts/intelligence/sanitizer.py`: 7-stage sanitization automaton & publisher quarantine set (R1, R6).
- `scripts/intelligence/entities.py`: Entity extractor, pronoun disambiguation, `SyntacticActorGrammar` (R1, R2, R6).
- `scripts/intelligence/intake.py`: Title/description mutation, dedup, provenance quarantine (R1, R6).
- `scripts/intelligence/memory.py`: Tri-anchor narrative coherence invariant & memory storage (R3, R6).
- `scripts/intelligence/curation.py`: Narrative threading, honest null assignment (R3, R6).
- `scripts/fetch_news.py`: RSS news fetch with ingestion sanitization (R1, R6).
- `data/`:
  - `news.json`: primary news dataset.
  - `narrative_memory.json`: cleansed narrative arcs.
- `index.html`, `app.js`, `style.css`: Adaptive UI morphology, honest nulls, VisionOS liquid glass UI (R4).
- `tests/`:
  - `test_hermetic_intelligence.py`: Adversarial fuzz harness & regression suite (R5, R6).
  - `test_e2e_remediation.py`: Master E2E remediation suite.
- `production_hard_audit.py`: Master 6-layer production hard audit.
