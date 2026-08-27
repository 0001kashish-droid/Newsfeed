# 🌐 News Colossal — High-Signal Global News Intelligence Platform

> **News Colossal** is an ultra-premium, real-time news aggregation command center engineered to eliminate digital noise, clickbait, and information overload. Built with **zero frameworks, zero dependencies** — pure vanilla JS, HTML5 Canvas, CSS3 glassmorphism, and a Python RSS pipeline automated via GitHub Actions.

### 🔗 Live App: [https://0001kashish-droid.github.io/Newsfeed/](https://0001kashish-droid.github.io/Newsfeed/)

---

## ✨ What Makes News Colossal Different

Features that **no other news aggregator** on the planet currently offers:

### 🎯 Finite Feed — "You Are Caught Up"
No news app tells you when to stop. A **progress ring** around the NC logo fills as you browse stories across categories. Once you've covered all major categories, it completes with a gentle message:
> *"✨ You're caught up. The world can wait — go live your day."*

Every other app is designed to keep you scrolling forever. News Colossal is designed to **respect your time**.

### 🧬 Story DNA — Lineage & Evolution Tracker
When you open a story covered by multiple outlets, a **visual timeline** appears showing:
- 🟢 Who broke the story first
- 🔵 Which outlets picked it up
- How headlines shifted across sources

No aggregator shows *how a story evolves*. News Colossal treats stories as **living organisms** that propagate across the media ecosystem.

### 🌐 Cross-Regional Story Pairing
When the same global event is covered by outlets in **different regions**, News Colossal creates a **split-screen card** showing both perspectives side by side. No editorializing, just juxtaposition.

### 📧 Daily Executive Digest
Automated daily email newsletter dispatched at **7:30 AM IST** via Buttondown. Top 5 stories curated and delivered to subscribers. Powered by GitHub Actions cron.

---

## 🏗️ Architecture

```
GitHub Actions Automation:
  fetch-news.yml   → Every 30 min: 27 RSS feeds → news.json → GitHub Pages
  daily_digest.yml → Daily 7:30 AM IST: Top 5 → Buttondown → Email

Frontend (100% Vanilla, Zero Dependencies):
  app.js    — 2400+ lines: state, canvas, search, modals, audio, gestures
  style.css — 2500+ lines: glassmorphism, 3D transforms, responsive
  index.html — Semantic markup, PWA meta, JSON-LD structured data

Pipeline (Python 3.11+, stdlib only):
  fetch_news.py — 27 RSS feeds, diversity balancer, story clustering engine
  generate_daily_newsletter.py — Top 5 curation + Buttondown API dispatch
```

**Zero dependencies.** No React. No Vue. No npm. No bundlers. No backend server.

---

## 🎨 Design & UX Features

| Feature | Description |
|---------|-------------|
| **VisionOS Liquid Glass** | Apple-inspired glassmorphism with backdrop-filter blur |
| **3D Holographic Globe** | Interactive HTML5 Canvas globe with click-to-filter by region |
| **Hero Spotlight Carousel** | 60fps Canvas crossfade slideshow with parallax cover images |
| **Semantic Fuzzy Search** | 3-tier scoring (exact, token, synonym) with live Google News fallback |
| **Neural Broadcaster** | Web Speech API with voice modulator (speed, pitch, neural voice) |
| **3D Card Tilt Physics** | Mouse-tracked rotateX/Y with dynamic specular sheen reflection |
| **Executive Deck Modal** | Full-screen reader with parallax cover, progress bar, swipe gestures |
| **Pull-to-Refresh** | Native mobile touch gesture with spinner animation |
| **Dark/Light Theme** | Full dual-theme with 20+ CSS custom properties |
| **Custom Cursor** | Smooth lerp physics cursor on desktop (dot + ring) |

---

## 📰 Source Diversity (27 Global Feeds)

Automated two-pass fair balancer: BBC family capped at 18, per-source cap at 6 articles.

| Region | Sources |
|--------|---------|
| **Global** | BBC News, Reuters, The Guardian, Ars Technica, CNET, BBC Business |
| **Asia-Pacific** | BBC Asia, SCMP, The Guardian, NYT Asia |
| **Europe** | BBC Europe, The Guardian, France 24 |
| **Middle East** | Al Jazeera, BBC Middle East, France 24 |
| **North America** | NYT, NPR, BBC US, TechCrunch, The Verge, NYT Business |
| **India** | Hindustan Times, Indian Express, The Hindu, HT Business |

### Story Clustering Engine
After fetching, articles are clustered by **Jaccard title similarity** (threshold 0.35) using Union-Find. Clusters identify who broke each story first, track headline variants across outlets, and flag cross-regional coverage for side-by-side perspective cards.

---

## 📧 Newsletter & Monetization

| Component | Details |
|-----------|---------|
| **Daily Digest** | Cron at `0 2 * * *` UTC → curates top 5 → dispatches via Buttondown API |
| **Subscription** | Hidden iframe form submission (no API key exposed client-side) |
| **Support** | Ko-fi integration (3-tier: Coffee / Executive / Supporter) |
| **Substack** | [kashishbhushan.substack.com](https://kashishbhushan.substack.com) |

---

## 🛡️ Content Curation Philosophy

Every RSS headline passes through an **automated Noise-Reduction Signal Engine**:

**❌ Rejected:** Celebrity gossip, tabloid drama, micro-local blotter, promotional advertorials, horoscopes, clickbait stubs.

**✅ Prioritized:**
- 🌐 Geopolitical & diplomatic affairs
- 📈 Macroeconomic & financial impact
- 🚀 High-tech & scientific breakthroughs
- 🌍 Regional macro events across 6 global zones

---

## 🛠 Local Setup

```bash
git clone https://github.com/0001kashish-droid/Newsfeed.git
cd Newsfeed

# Fetch fresh news data
python scripts/fetch_news.py

# Start local server
python -m http.server 9000 --bind 127.0.0.1
```
Open **[http://127.0.0.1:9000](http://127.0.0.1:9000)**

---

## 📄 License & Publisher Rights
All news content, headlines, and visuals belong to their respective original publishers. News Colossal operates as a non-commercial news aggregator and reading interface.
