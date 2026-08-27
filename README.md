# 🌐 News Colossal — High-Signal Global News Intelligence Platform

> **News Colossal** is an ultra-premium, real-time news aggregation command center engineered to eliminate digital noise, clickbait, and information overload. Built with pure vanilla JS, HTML5 Canvas, and CSS3 glassmorphism.

### 🔗 Live App: [https://0001kashish-droid.github.io/Newsfeed/](https://0001kashish-droid.github.io/Newsfeed/)

---

## ✨ What Makes News Colossal Different

Features that **no other news aggregator** currently offers:

### 🎯 Finite Feed — "You Are Caught Up"
A **progress ring** around the NC logo fills as you browse stories across categories. Once you've covered all major categories, it completes with a gentle message, respecting your time rather than optimizing for infinite scrolling.

### 🧬 Story DNA — Lineage & Evolution Tracker
When you open a story covered by multiple outlets, a **visual timeline** appears showing who broke the story first, which outlets picked it up, and how headlines shifted.

### 🌐 Cross-Regional Story Pairing
When the same global event is covered by outlets in **different regions**, News Colossal creates a **split-screen card** showing both perspectives side by side.

### 📧 Daily Executive Digest
Automated daily email newsletter dispatched at **7:30 AM IST**. Top 5 stories curated and delivered directly to your inbox.

---

## 🎨 Design & UX Features

| Feature | Description |
|---------|-------------|
| **VisionOS Liquid Glass** | Apple-inspired glassmorphism with backdrop-filter blur |
| **3D Holographic Globe** | Interactive HTML5 Canvas globe with click-to-filter by region |
| **Hero Spotlight Carousel** | 60fps Canvas crossfade slideshow with parallax cover images |
| **Semantic Fuzzy Search** | 3-tier scoring (exact, token, synonym) |
| **Neural Broadcaster** | Web Speech API with voice modulator |
| **3D Card Tilt Physics** | Mouse-tracked rotateX/Y with dynamic specular sheen reflection |
| **Executive Deck Modal** | Full-screen reader with parallax cover, progress bar, swipe gestures |
| **Pull-to-Refresh** | Native mobile touch gesture with spinner animation |
| **Dark/Light Theme** | Full dual-theme with 20+ CSS custom properties |
| **Custom Cursor** | Smooth lerp physics cursor on desktop |

---

## 📰 Source Diversity

Aggregating live news across 27+ credible international publications:

- **Global:** BBC News, Reuters, The Guardian, Ars Technica, CNET, BBC Business
- **Asia-Pacific:** BBC Asia, SCMP, The Guardian, NYT Asia
- **Europe:** BBC Europe, The Guardian, France 24
- **Middle East:** Al Jazeera, BBC Middle East, France 24
- **North America:** NYT, NPR, BBC US, TechCrunch, The Verge, NYT Business
- **India:** Hindustan Times, Indian Express, The Hindu, HT Business

---

## 🛡️ Content Curation Philosophy

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

# Fetch fresh news data (Requires Python 3.11+)
python scripts/fetch_news.py

# Start local server
python -m http.server 9000 --bind 127.0.0.1
```
Open **[http://127.0.0.1:9000](http://127.0.0.1:9000)**

---

## 📄 License & Publisher Rights
All news content, headlines, and visuals belong to their respective original publishers. News Colossal operates as a non-commercial news aggregator and reading interface.
