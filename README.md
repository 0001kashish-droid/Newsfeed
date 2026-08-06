# News Colossal — Live Real-Time News Command Center & Digest

[![Live Site](https://img.shields.org/badge/Live_Site-GitHub_Pages-00f2fe?style=for-the-badge&logo=github)](https://0001kashish-droid.github.io/Newsfeed/)
[![RSS Automation](https://img.shields.org/badge/RSS_Sync-GitHub_Actions-3b82f6?style=for-the-badge&logo=githubactions)](.github/workflows/fetch-news.yml)
[![Design System](https://img.shields.org/badge/UI/UX-Apple_Liquid_Glass-a855f7?style=for-the-badge)](style.css)

> **"Cutting through the noise of modern news platforms to bring you clarity, executive focus, and high-fidelity intelligence."**

---

## 🎯 Why News Colossal Was Built

In today's digital landscape, modern news platforms are overwhelmed with **information overload, sensational clickbait, invasive pop-up ads, paywalls, and distracting visual clutter**. Readers spend more time dodging ads and filtering noise than gaining meaningful insight into major global developments.

**News Colossal** was engineered to solve this exact problem:

1. **Focus Over Noise**: Distills massive RSS news streams into a curated **Top 10 Colossal Digest** spanning World, Technology, National, and Business headlines.
2. **Crisp Executive Annotations**: Every story includes a 2-bullet executive breakdown (**✦ What Happened** & **✦ Impact & Context**) so you grasp the core takeaways in seconds.
3. **Multi-Source Credibility**: Provides one-click cross-verification across trusted publishers (*BBC, Reuters, NYT, Ars Technica, The Verge, Al Jazeera, Hindustan Times, The Hindu, NPR, WSJ*).
4. **Natural Human Voice Synthesizer**: Converts written digests into conversational audio briefings using neural human-like speech synthesis.
5. **Apple Liquid Glass Interface**: An ultra-premium, distraction-free glassmorphic interface with dynamic category color reflections, zero ads, and fluid side navigation paddles.

---

## ✨ Key Features

- **🌐 Live 30-Minute RSS Automation**: Powered by GitHub Actions serverless cron workflows (`fetch_news.py`) running every 30 minutes to fetch live headlines without CORS restrictions.
- **💎 Apple Liquid Glass Navigation**: Floating side paddles (**64×140px target zones**) and a top Liquid Glass pill with dynamic news category color reflections (*Cyan for World, Purple for Tech, Amber for National, Emerald for Business*).
- **📱 Touch & Keyboard Fluidity**: Full touch swipe gesture support (`touchstart` / `touchend`) on mobile, left/right cover banner tap zones, and keyboard arrow hotkeys (`←` / `→`).
- **🖼 100% Real High-Definition Media**: Automatically upscales thumbnail streams (BBC 1024px, NYT SuperJumbo, Ars Technica 1152px, HT 1600px) with CSS contrast sharpening.
- **🗣 Natural Human Audio Synthesizer**: Integrated Web Speech API audio engine filtering for neural, conversational human voice models (*Google US English, Microsoft Ava, Natural, Samantha, Karen*).
- **☀️ Light Mode Default**: Clean high-contrast light mode by default with instant toggle to Dark Cyberpunk mode.

---

## 🛠 Tech Stack

- **Frontend**: HTML5, Vanilla JavaScript (ES6+), CSS Glassmorphism Engine
- **Automation Pipeline**: Python 3, GitHub Actions Cron (`fetch-news.yml`), ElementTree XML Parser
- **Deployment**: GitHub Pages (`main` branch origin)
- **APIs & Data**: Native Web Speech API, LocalStorage Bookmarks API, HTML5 Canvas 2D Crossfade Engine

---

## 🚀 Live Production URL

👉 **[https://0001kashish-droid.github.io/Newsfeed/](https://0001kashish-droid.github.io/Newsfeed/)**

---

## 💻 Local Development Setup

To run News Colossal locally on your machine:

```bash
# 1. Clone repository
git clone https://github.com/0001kashish-droid/Newsfeed.git
cd Newsfeed

# 2. Fetch fresh live RSS headlines
python scripts/fetch_news.py

# 3. Start local development HTTP server
python -m http.server 8080
```

Open `http://localhost:8080` in your web browser.

---

## 📄 License & Attribution

News Colossal aggregates public open RSS XML feeds. All article rights, trademarks, and content belong to their respective original publishers (BBC, Reuters, NYT, Ars Technica, The Verge, Al Jazeera, Hindustan Times, The Hindu, NPR, WSJ, CNBC).
