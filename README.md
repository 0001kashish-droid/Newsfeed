# 🌐 News Colossal — High-Signal Global News Command Center & Executive Digest

> **News Colossal** is an ultra-premium, real-time news aggregation command center designed to eliminate digital noise, clickbait, and information overload. Built with **Apple VisionOS Liquid Specular Glass Aesthetics**, **3D Holographic Geospatial Hotspots**, **Smart Fuzzy Semantic Search**, **Native Mobile Touch Gestures**, and **Neural Human Speech Synthesis**.

---

### 🚀 Live Application & Repository Links
- 🌐 **Public Live App (GitHub Pages)**: [https://0001kashish-droid.github.io/Newsfeed/](https://0001kashish-droid.github.io/Newsfeed/)
- 💻 **GitHub Repository**: [https://github.com/0001kashish-droid/Newsfeed](https://github.com/0001kashish-droid/Newsfeed)
- ⚡ **Local Development Server**: `http://127.0.0.1:9000`

---

## 🌟 v2.1.0 — Senior-Grade 5-Pillar Overhaul

- 📊 **Source Diversity Enforcement**: BBC brand family capped at ≤18 articles (~10%), per-source cap at 7. No single publisher dominates the feed.
- 🎯 **Importance-Only Quality Gate**: Expanded 40-term noise blocklist + positive importance signal boost. Only impactful geopolitical, economic, scientific, and policy stories make the cut.
- 📜 **Always-Visible Deck Scrollbar**: Forced 7px accent scrollbar on all platforms (Android Chrome, Samsung Internet, iOS Safari) with `min-height: 40px` thumb. Bottom scroll fade gradient indicates more content.
- 📱 **Full-Screen Mobile Reader Deck**: `100vw × 100dvh` native-app-feel modal on phones (≤640px) with dedicated sticky header bar — zero button overlap on cover photos.
- 📐 **Enterprise Tablet Breakpoint**: Dedicated `768px–1024px` layer for iPad, Galaxy Tab, Surface — 2-column grid, 80vw modal, responsive content padding.
- 🔒 **Safe Area Insets**: `env(safe-area-inset-top/bottom)` for iPhone X+ notches and Android display cutouts.
- 👆 **WCAG Touch Targets**: All interactive buttons enforce `min-width: 44px; min-height: 44px` on touch devices.
- ✨ **Premium Entrance Animation**: Modal slides up with `scale(0.96) → scale(1)` spring easing. Cards stagger in with `--card-index` CSS delay.
- 🔤 **Refined Typography**: `font-feature-settings: 'kern' 1, 'liga' 1`, `text-rendering: optimizeLegibility`, antialiased font smoothing.
- 💎 **Glass Card Hover Depth**: Cards lift `translateY(-4px)` on hover with enhanced shadow glow.
- 🌊 **Scroll-Linked Progress Glow**: Reading progress bar pulses with accent glow while actively scrolling.

---

## 🎯 Why News Colossal Was Built & Curation Philosophy

In today's digital news landscape, readers are bombarded with tabloid gossip, clickbait headlines, viral social media drama, and promotional noise. **News Colossal was engineered with a single core mandate: Deliver high-impact macro intelligence across global continents while ruthlessly excluding low-value noise.**

### 🛑 Excluded Content Criteria (Noise / "Crap" Exclusion Filter)
Every incoming RSS headline is evaluated through an automated Noise-Reduction Signal Engine. Articles matching any of the following criteria are **strictly rejected**:
1. **Tabloid Gossip & Celebrity Drama**: Celebrity relationship updates, influencer social media feuds, viral TikTok trends, and reality TV summaries.
2. **Micro-Local Blotter & Isolated Incidents**: Routine municipal traffic updates, minor isolated crimes, or local incidents carrying zero macro significance.
3. **Promotional Content & Advertorials**: Corporate press releases disguised as news, sponsored product endorsements, and marketing announcements.
4. **Astrology & Clickbait Fragment Stubs**: Horoscopes, lottery draw numbers, listicles, and single-sentence snippet stubs lacking analytical context.

---

### ✦ Prioritized High-Signal Intelligence Criteria
Articles included across our **5 Global Continent Hotspots** must fulfill at least one core intelligence benchmark:
- 🌐 **Geopolitical & Diplomatic Affairs**: International treaties, summits, national security, major elections, and trade policy updates.
- 📈 **Macroeconomic & Financial Impact**: Central bank rate decisions, market trends, global inflation reports, supply chain shifts, and major corporate earnings.
- 🚀 **High-Tech & Scientific Breakthroughs**: Artificial intelligence models (AI/LLMs), space exploration (SpaceX/NASA), semiconductor developments, and clean energy breakthroughs.
- 🌍 **Regional Macro Events**: Infrastructure projects, climate initiatives, and key legislative decisions across **Asia-Pacific**, **Middle East**, **Europe**, **North America**, and **India**.

---

## 🏢 Publisher Source Diversity (19+ Global Outlets)

News Colossal aggregates live news across 19+ credible international publications with an automated two-pass fair balancer. **BBC brand family capped at ≤18 articles (~10%)**, every other brand family at ≤14. Per-source cap: **7 articles max**:

- **Global & International**: *The New York Times*, *The Guardian*, *BBC News*, *Associated Press*
- **Asia-Pacific**: *South China Morning Post*, *SCMP Tech*, *SCMP Business*, *BBC Asia*, *The Guardian Asia*
- **Middle East**: *Al Jazeera*, *BBC Middle East*
- **Europe**: *BBC Europe*, *The Guardian Europe*, *BBC Tech*, *BBC Business*
- **North America**: *Ars Technica*, *TechCrunch*, *CNBC*, *NPR*, *NYT Business*, *BBC US*
- **India**: *The Hindu*, *Hindustan Times*, *HT Tech*, *HT Business*

---

## 🛠 Local Setup & Automated Verification

```bash
# Clone repository
git clone https://github.com/0001kashish-droid/Newsfeed.git
cd Newsfeed

# Run full 6-layer automated production audit suite
python production_hard_audit.py

# Start local HTTP server
python -m http.server 9000 --bind 127.0.0.1
```
Open **[http://127.0.0.1:9000](http://127.0.0.1:9000)** in your web browser.

---

## 📄 License & Publisher Rights
All news content, headlines, and visuals belong to their respective original publishers (**The New York Times**, **BBC News**, **South China Morning Post**, **Ars Technica**, **TechCrunch**, **Al Jazeera**, **Hindustan Times**, **The Hindu**). News Colossal operates as a non-commercial news aggregator and reading interface.
