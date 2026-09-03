// News Colossal Application Engine — Real-Time Live Cache-Busting Refresh Engine

const state = {
  articles: [],
  filteredArticles: [],
  podcasts: [],
  podcastsLastUpdated: null,
  currentCategory: 'top10',
  currentRegion: 'all',
  searchQuery: '',
  bookmarks: JSON.parse(localStorage.getItem('nc_bookmarks') || '[]'),
  atomicDossier: JSON.parse(localStorage.getItem('nc_atomic_dossier') || '{}'),
  savedSearchQuery: '',
  theme: localStorage.getItem('nc_theme') || 'light', // Default to Imperial Light Mode
  heroIndex: 0,
  heroPlaying: true,
  heroTimer: null,
  progressInterval: null,
  progressValue: 0,
  userTimezone: Intl.DateTimeFormat().resolvedOptions().timeZone || 'Asia/Kolkata',
  searchDebounceTimer: null,
  
  // Executive Deck Navigation State
  modalState: {
    articles: [],
    currentIndex: 0,
    touchStartX: 0,
    touchEndX: 0
  },
  
  // Human Voice Engine State
  audioState: {
    isPlaying: false,
    isPaused: false,
    rate: 0.95,
    pitch: 1.0,
    selectedVoiceURI: null,
    currentText: ''
  }
};

const DEFAULT_FALLBACK_IMG = "https://images.unsplash.com/photo-1504711434969-e33886168f5c?auto=format&fit=crop&w=2400&q=98";

// TOPIC & PUBLISHER DYNAMIC VISUAL ENGINE
const TOPIC_VISUAL_POOLS = {
  law: [
    "https://images.unsplash.com/photo-1589829545856-d10d557cf95f?auto=format&fit=crop&w=1600&q=85",
    "https://images.unsplash.com/photo-1505664194779-8beaceb93744?auto=format&fit=crop&w=1600&q=85"
  ],
  tech: [
    "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=1600&q=85",
    "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=1600&q=85",
    "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?auto=format&fit=crop&w=1600&q=85"
  ],
  business: [
    "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=1600&q=85",
    "https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?auto=format&fit=crop&w=1600&q=85"
  ],
  politics: [
    "https://images.unsplash.com/photo-1541872703-74c5e44368f9?auto=format&fit=crop&w=1600&q=85",
    "https://images.unsplash.com/photo-1529107386315-e1a2ed48a620?auto=format&fit=crop&w=1600&q=85"
  ],
  india: [
    "https://images.unsplash.com/photo-1524492412937-b28074a5d7da?auto=format&fit=crop&w=1600&q=85",
    "https://images.unsplash.com/photo-1532375810709-75b1da00537c?auto=format&fit=crop&w=1600&q=85"
  ],
  climate: [
    "https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?auto=format&fit=crop&w=1600&q=85",
    "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=1600&q=85"
  ],
  sports: [
    "https://images.unsplash.com/photo-1540747913346-19e32dc3e97e?auto=format&fit=crop&w=1600&q=85"
  ],
  general: [
    "https://images.unsplash.com/photo-1504711434969-e33886168f5c?auto=format&fit=crop&w=1600&q=85",
    "https://images.unsplash.com/photo-1495020689067-958852a7765e?auto=format&fit=crop&w=1600&q=85"
  ]
};

function getTopicImageUrl(title = "", category = "", region = "") {
  const text = (title + " " + category + " " + region).toLowerCase();
  let hash = 0;
  for (let i = 0; i < text.length; i++) hash = (hash << 5) - hash + text.charCodeAt(i);
  const getIndex = (arr) => arr[Math.abs(hash) % arr.length];

  if (/cjp|court|judge|law|police|jail|legal|rights|protest|doxxed|abused|arrest|justice|crime|suing|lawsuit/i.test(text)) {
    return getIndex(TOPIC_VISUAL_POOLS.law);
  }
  if (/ai|chip|nvidia|tech|software|google|cyber|hack|robot|anthropic|claude|code|digital|app|github|malware/i.test(text)) {
    return getIndex(TOPIC_VISUAL_POOLS.tech);
  }
  if (/market|stock|trade|tariff|profit|bank|economic|business|share|ceo|inflation|money|revenue|finance/i.test(text)) {
    return getIndex(TOPIC_VISUAL_POOLS.business);
  }
  if (/climate|drought|wildfire|heat|flood|earth|weather|environment|nature|fire/i.test(text)) {
    return getIndex(TOPIC_VISUAL_POOLS.climate);
  }
  if (/india|delhi|mumbai|karnataka|hindu|modi|indian/i.test(text)) {
    return getIndex(TOPIC_VISUAL_POOLS.india);
  }
  if (/trump|biden|election|vote|consulate|diplomatic|government|minister|policy|republican|democrat|china|state/i.test(text)) {
    return getIndex(TOPIC_VISUAL_POOLS.politics);
  }
  if (/sport|stadium|match|cricket|game|tournament|fifa/i.test(text)) {
    return getIndex(TOPIC_VISUAL_POOLS.sports);
  }

  const catLower = (category || '').toLowerCase();
  if (catLower === 'tech') return getIndex(TOPIC_VISUAL_POOLS.tech);
  if (catLower === 'business') return getIndex(TOPIC_VISUAL_POOLS.business);
  if (catLower === 'national') return getIndex(TOPIC_VISUAL_POOLS.india);

  return getIndex(TOPIC_VISUAL_POOLS.general);
}

// Color mapping for Liquid Glass dynamic ambient reflection
const CATEGORY_COLORS = {
  "World": "#00f2fe",
  "Tech": "#a855f7",
  "National": "#f59e0b",
  "Business": "#10b981"
};

// COMPREHENSIVE HIGH-PRECISION SEMANTIC CONCEPT MAP
const EXPANDED_SEMANTIC_MAP = {
  "nvidia": ["chip", "chips", "semiconductor", "ai", "hardware", "tech", "stock", "gpu", "datacenter"],
  "spacex": ["musk", "rocket", "starlink", "space", "orbit", "nasa", "satellite"],
  "space": ["spacex", "orbit", "rocket", "nasa", "astronomy", "cosmos", "satellite"],
  "ai": ["artificial intelligence", "machine learning", "chatgpt", "openai", "anthropic", "claude", "meta", "google", "deepmind", "nvidia", "chip", "semiconductor", "model", "llm", "algorithm", "software"],
  "tech": ["technology", "software", "electronics", "gadgets", "ai", "hardware", "verge", "ars technica", "apple", "microsoft", "google", "internet", "cyber", "chip", "nvidia", "phone"],
  "technology": ["software", "electronics", "gadgets", "ai", "hardware", "verge", "ars technica", "apple", "microsoft", "google", "internet", "cyber", "chip"],
  "business": ["markets", "stocks", "shares", "economy", "finance", "cnbc", "money", "trade", "company", "ceo", "revenue", "profit", "bank", "invest", "inflation", "market"],
  "stocks": ["business", "markets", "shares", "economy", "finance", "invest", "dow", "nasdaq", "s&p", "trade", "revenue"],
  "economy": ["business", "markets", "stocks", "inflation", "rates", "bank", "finance", "money", "trade", "economic"],
  "world": ["global", "international", "bbc", "reuters", "foreign", "diplomacy", "un", "middle east", "europe", "war", "treaty", "ukraine", "russia", "china", "gaza", "israel"],
  "national": ["india", "hindustan", "us", "uk", "america", "government", "policy", "election", "court", "police", "delhi", "mumbai", "biden", "trump"],
  "india": ["hindustan", "national", "delhi", "mumbai", "modi", "nagpur", "ladakh", "wangchuk", "ht", "indian", "rupee"],
  "us": ["america", "national", "biden", "trump", "white house", "congress", "cdc", "washington", "american"],
  "china": ["beijing", "asia", "taiwan", "trade", "xi", "chinese"]
};

// 3D Holographic Globe Region Node Coordinates (Canvas Relative)
const GLOBE_NODES = [
  { name: "India", x: 480, y: 150, color: "#f59e0b", region: "India" },
  { name: "Europe", x: 380, y: 100, color: "#0284c7", region: "Europe" },
  { name: "North America", x: 180, y: 110, color: "#10b981", region: "North America" },
  { name: "Asia-Pacific", x: 580, y: 160, color: "#9333ea", region: "Asia-Pacific" },
  { name: "Middle East", x: 420, y: 140, color: "#e11d48", region: "Middle East" }
];

function getNewsColor(category) {
  return CATEGORY_COLORS[category] || "#00f2fe";
}

// DOM Elements
const newsGrid = document.getElementById('newsGrid');
const gridTitle = document.getElementById('gridTitle');
const tickerTrack = document.getElementById('tickerTrack');
const syncTimeLabel = document.getElementById('syncTimeLabel');
const searchInput = document.getElementById('searchInput');
const regionSelect = document.getElementById('regionSelect');
const navTabs = document.getElementById('navTabs');
const tabIndicatorPill = document.getElementById('tabIndicatorPill');
const tabHoverPill = document.getElementById('tabHoverPill');
const modalBackdrop = document.getElementById('modalBackdrop');
const modalContent = document.getElementById('modalContent');
const drawerBackdrop = document.getElementById('drawerBackdrop');
const drawerCloseBtn = document.getElementById('drawerCloseBtn');
const savedList = document.getElementById('savedList');
const bookmarkCount = document.getElementById('bookmarkCount');
const themeToggleBtn = document.getElementById('themeToggleBtn');
const refreshBtn = document.getElementById('refreshBtn');
const regionalClockText = document.getElementById('regionalClockText');
const headerScrollLine = document.getElementById('headerScrollLine');
const shortcutHelpBtn = document.getElementById('shortcutHelpBtn');
const shortcutModalBackdrop = document.getElementById('shortcutModalBackdrop');
const resetVoiceBtn = document.getElementById('resetVoiceBtn');

// Globe Canvas
const globeCanvas = document.getElementById('globeCanvas');
const globeCtx = globeCanvas ? globeCanvas.getContext('2d') : null;

// Custom Cursor Elements
const cursorDot = document.getElementById('cursorDot');
const cursorRing = document.getElementById('cursorRing');

// Audio Player & Human Voice Elements
const audioPlayBtn = document.getElementById('audioPlayBtn');
const audioTitle = document.getElementById('audioTitle');
const eqContainer = document.getElementById('eqContainer');
const voiceModToggle = document.getElementById('voiceModToggle');
const voiceModDrawer = document.getElementById('voiceModDrawer');
const voiceSelect = document.getElementById('voiceSelect');
const rateSlider = document.getElementById('rateSlider');
const pitchSlider = document.getElementById('pitchSlider');
const rateValLabel = document.getElementById('rateValLabel');
const pitchValLabel = document.getElementById('pitchValLabel');
const speedBadge = document.getElementById('speedBadge');

const contentGridSection = document.getElementById('contentGridSection');

// Canvas Elements
const heroCanvas = document.getElementById('heroCanvas');
const heroCtx = heroCanvas ? heroCanvas.getContext('2d') : null;
const canvasProgressBar = document.getElementById('canvasProgressBar');
const heroOverlay = document.getElementById('heroOverlay');
const heroDots = document.getElementById('heroDots');
const heroPrevBtn = document.getElementById('heroPrevBtn');
const heroNextBtn = document.getElementById('heroNextBtn');
const heroPlayPauseBtn = document.getElementById('heroPlayPauseBtn');

let canvasImages = {};
let animProgress = 1.0;
let currentImgObj = null;
let nextImgObj = null;
let globePulseAngle = 0;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
  initTheme();
  setupCanvasResize();
  loadData();
  setupEventListeners();
  setupVoiceModulator();
  setupTabHoverMechanics();
  setupCustomCursor();
  startIPLocationClock();
  setupHeaderScrollLine();
  initHolographicGlobe();
  setupMobilePullToRefresh();
  window.addEventListener('resize', updateTabIndicator);
});

// HEADER READING SCROLL PROGRESS LINE
function setupHeaderScrollLine() {
  window.addEventListener('scroll', () => {
    if (!headerScrollLine) return;
    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    const docHeight = document.documentElement.scrollHeight - document.documentElement.clientHeight;
    const percent = docHeight > 0 ? (scrollTop / docHeight) * 100 : 0;
    headerScrollLine.style.width = `${percent.toFixed(1)}%`;
  });
}

// REAL-TIME SMART DATE & TIME (CLEAN SINGLE ICON TYPOGRAPHY)
function startIPLocationClock() {
  updateIPLocationClock();
  setInterval(updateIPLocationClock, 1000);
}

function updateIPLocationClock() {
  if (!regionalClockText) return;
  const now = new Date();

  const options = {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: true,
    timeZone: state.userTimezone
  };

  try {
    const formatted = new Intl.DateTimeFormat('en-US', options).format(now);
    regionalClockText.textContent = formatted;
  } catch (e) {
    regionalClockText.textContent = now.toLocaleTimeString();
  }
}

// 3D HOLOGRAPHIC GEOSPATIAL GLOBE CANVAS ENGINE
function initHolographicGlobe() {
  if (!globeCanvas || !globeCtx) return;

  function drawGlobeFrame() {
    globeCtx.clearRect(0, 0, globeCanvas.width, globeCanvas.height);
    globePulseAngle += 0.04;

    const w = globeCanvas.width;
    const h = globeCanvas.height;

    // Draw Holographic Latitude & Longitude Grid Lines
    globeCtx.strokeStyle = 'rgba(0, 242, 254, 0.12)';
    globeCtx.lineWidth = 1;

    for (let x = 40; x < w; x += 60) {
      globeCtx.beginPath();
      globeCtx.moveTo(x, 0);
      globeCtx.lineTo(x, h);
      globeCtx.stroke();
    }

    for (let y = 30; y < h; y += 40) {
      globeCtx.beginPath();
      globeCtx.moveTo(0, y);
      globeCtx.lineTo(w, y);
      globeCtx.stroke();
    }

    // Draw Connecting Vector Node Network Lines
    globeCtx.beginPath();
    globeCtx.moveTo(GLOBE_NODES[0].x, GLOBE_NODES[0].y);
    GLOBE_NODES.forEach(n => globeCtx.lineTo(n.x, n.y));
    globeCtx.strokeStyle = 'rgba(0, 242, 254, 0.25)';
    globeCtx.stroke();

    // Draw Interactive Pulsing Continent Hotspot Nodes
    GLOBE_NODES.forEach(node => {
      const pulseSize = 8 + Math.sin(globePulseAngle) * 4;

      // Radar Pulse Wave
      globeCtx.beginPath();
      globeCtx.arc(node.x, node.y, pulseSize + 6, 0, Math.PI * 2);
      globeCtx.fillStyle = node.color + '33';
      globeCtx.fill();

      // Solid Core Node
      globeCtx.beginPath();
      globeCtx.arc(node.x, node.y, 6, 0, Math.PI * 2);
      globeCtx.fillStyle = node.color;
      globeCtx.fill();
      globeCtx.strokeStyle = '#ffffff';
      globeCtx.lineWidth = 1.5;
      globeCtx.stroke();

      // Label Tag
      globeCtx.font = 'bold 11px Inter, sans-serif';
      globeCtx.fillStyle = '#f8fafc';
      globeCtx.fillText(node.name, node.x + 10, node.y + 4);
    });

    requestAnimationFrame(drawGlobeFrame);
  }

  drawGlobeFrame();

  // Canvas Click Interactivity for Regional Hotspot Filtering
  globeCanvas.addEventListener('click', (e) => {
    const rect = globeCanvas.getBoundingClientRect();
    const clickX = (e.clientX - rect.left) * (globeCanvas.width / rect.width);
    const clickY = (e.clientY - rect.top) * (globeCanvas.height / rect.height);

    GLOBE_NODES.forEach(node => {
      const dist = Math.hypot(clickX - node.x, clickY - node.y);
      if (dist < 20) {
        selectRegionFilter(node.region);
      }
    });
  });
}

window.selectRegionFilter = function(region) {
  regionSelect.value = region;
  state.currentRegion = region;
  filterAndRender();
  scrollToContent();
};

// DYNAMICALLY COMPUTE REAL-TIME LIVE HOTSPOT STORY COUNTS IN HARMONY WITH ACTIVE CATEGORY
function updateGlobeStats() {
  const targetCat = state.currentCategory.toLowerCase();

  const getCount = (r) => {
    let pool = state.articles;
    if (targetCat !== 'top10') {
      pool = pool.filter(a => a.category.toLowerCase() === targetCat);
    }
    return pool.filter(a => a.region.toLowerCase() === r.toLowerCase() || (r.toLowerCase() === 'global' && a.region.toLowerCase() === 'world')).length;
  };

  const elIndia = document.getElementById('statIndia');
  const elEurope = document.getElementById('statEurope');
  const elNA = document.getElementById('statNA');
  const elAP = document.getElementById('statAP');
  const elME = document.getElementById('statME');

  const catSuffix = targetCat === 'top10' ? '' : ` ${state.currentCategory}`;

  if (elIndia) elIndia.textContent = `${getCount('India')}${catSuffix} Stories`;
  if (elEurope) elEurope.textContent = `${getCount('Europe')}${catSuffix} Stories`;
  if (elNA) elNA.textContent = `${getCount('North America')}${catSuffix} Stories`;
  if (elAP) elAP.textContent = `${getCount('Asia-Pacific')}${catSuffix} Stories`;
  if (elME) elME.textContent = `${getCount('Middle East')}${catSuffix} Stories`;
}

// CUSTOM VISIONOS LIQUID GLASS SPECULAR CURSOR ENGINE
function setupCustomCursor() {
  if (!cursorDot || !cursorRing) return;

  let mouseX = window.innerWidth / 2;
  let mouseY = window.innerHeight / 2;
  let ringX = mouseX;
  let ringY = mouseY;

  window.addEventListener('mousemove', (e) => {
    mouseX = e.clientX;
    mouseY = e.clientY;
    cursorDot.style.transform = `translate(${mouseX}px, ${mouseY}px) translate(-50%, -50%)`;
  });

  function renderCursorRing() {
    ringX += (mouseX - ringX) * 0.22;
    ringY += (mouseY - ringY) * 0.22;
    cursorRing.style.transform = `translate(${ringX.toFixed(2)}px, ${ringY.toFixed(2)}px) translate(-50%, -50%)`;
    requestAnimationFrame(renderCursorRing);
  }
  requestAnimationFrame(renderCursorRing);

  // Attach hover scaling over interactive elements
  document.addEventListener('mouseover', (e) => {
    if (e.target.closest('button, a, .news-card, .tab-btn, select, input, .saved-item-card, .map-stat-item')) {
      cursorRing.classList.add('active-hover');
    } else {
      cursorRing.classList.remove('active-hover');
    }
  });
}

// REAL-TIME MAGNETIC TAB HOVER GLASS PREVIEW ENGINE
function setupTabHoverMechanics() {
  if (!navTabs || !tabHoverPill) return;

  const tabBtns = navTabs.querySelectorAll('.tab-btn');

  tabBtns.forEach(btn => {
    btn.addEventListener('mouseenter', () => {
      const rect = btn.getBoundingClientRect();
      const parentRect = navTabs.getBoundingClientRect();
      const left = rect.left - parentRect.left;
      const width = rect.width;

      tabHoverPill.style.width = `${width}px`;
      tabHoverPill.style.transform = `translateX(${left}px)`;
      tabHoverPill.classList.add('active');
    });
  });

  navTabs.addEventListener('mouseleave', () => {
    tabHoverPill.classList.remove('active');
  });
}

// Theme Management (Defaults to Light Mode)
function initTheme() {
  document.documentElement.setAttribute('data-theme', state.theme);
}

themeToggleBtn.addEventListener('click', () => {
  state.theme = state.theme === 'dark' ? 'light' : 'dark';
  localStorage.setItem('nc_theme', state.theme);
  document.documentElement.setAttribute('data-theme', state.theme);
  setTimeout(updateTabIndicator, 50);
});

// HARD REFRESH DATA FETCHER WITH CACHE BUSTING ENGINE
async function loadData(forceBustCache = false) {
  renderSkeletons();
  try {
    const cacheBuster = forceBustCache ? `?t=${Date.now()}` : '';
    const res = await fetch(`data/news.json${cacheBuster}`, {
      cache: forceBustCache ? 'no-cache' : 'default'
    });
    if (!res.ok) throw new Error('Data file not found');
    const data = await res.json();
    state.articles = data.articles || [];
    
    // Format live sync timestamp
    const nowStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    syncTimeLabel.textContent = `Auto-synced at ${nowStr}`;

    showToastNotification(`✨ News feeds refreshed successfully! (${state.articles.length} stories active)`);
  } catch (err) {
    console.warn('Local news.json missing, triggering fallback client fetch:', err);
    await fetchClientFallback();
  }
  preloadHeroImages();
  filterAndRender();
  renderTicker();
  backfillAtomicDossier();
  updateBookmarkBadge();
  updateGlobeStats();
  setTimeout(updateTabIndicator, 100);
}

function showToastNotification(message) {
  let toast = document.getElementById('ncToast');
  if (!toast) {
    toast = document.createElement('div');
    toast.id = 'ncToast';
    toast.style.cssText = `
      position: fixed;
      top: 5rem;
      right: 2rem;
      z-index: 999;
      background: var(--bg-surface-elevated);
      border: 1px solid var(--border-highlight);
      color: var(--text-primary);
      padding: 0.75rem 1.4rem;
      border-radius: var(--radius-full);
      font-size: 0.88rem;
      font-weight: 700;
      box-shadow: var(--shadow-md);
      opacity: 0;
      transform: translateY(-10px);
      transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
      pointer-events: none;
    `;
    document.body.appendChild(toast);
  }
  toast.textContent = message;
  toast.style.opacity = '1';
  toast.style.transform = 'translateY(0)';
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(-10px)';
  }, 2800);
}

function ensureImageLoaded(art) {
  if (!art) return null;
  if (!canvasImages[art.id]) {
    const img = new Image();
    img.crossOrigin = 'Anonymous';
    img.decoding = 'async';
    img.onerror = () => { img.src = DEFAULT_FALLBACK_IMG; };
    img.src = art.imageUrl || DEFAULT_FALLBACK_IMG;
    canvasImages[art.id] = img;
  }
  return canvasImages[art.id];
}

function preloadHeroImages() {
  const pool = state.filteredArticles.length > 0 ? state.filteredArticles : state.articles;
  if (pool.length === 0) return;
  const indices = [
    state.heroIndex,
    (state.heroIndex + 1) % pool.length,
    (state.heroIndex - 1 + pool.length) % pool.length
  ];
  indices.forEach(idx => {
    const art = pool[idx];
    if (art) ensureImageLoaded(art);
  });
}

// Client Multi-Proxy Fallback
async function fetchClientFallback() {
  const proxyUrl = 'https://api.rss2json.com/v1/api.json?rss_url=https://feeds.bbci.co.uk/news/rss.xml';
  try {
    const res = await fetch(proxyUrl);
    const data = await res.json();
    if (data.items) {
      state.articles = data.items.map((item, idx) => {
        const cleanDesc = item.description.replace(/<[^>]*>?/gm, '').trim();
        return {
          id: `bbc-live-${idx}`,
          title: item.title,
          link: item.link,
          description: cleanDesc,
          source: 'BBC News',
          sourceLogo: 'BBC',
          category: 'World',
          region: 'Global',
          pubDate: item.pubDate,
          imageUrl: item.thumbnail || DEFAULT_FALLBACK_IMG,
          annotation: {
            what: item.title,
            why: cleanDesc
          },
          readTime: '3 min read',
          relatedSources: [
            { name: 'BBC News', url: item.link },
            { name: 'Reuters', url: 'https://www.reuters.com' }
          ]
        };
      });
    }
  } catch (e) {
    console.error('All fetch fallbacks failed', e);
  }
}

// Smooth Canvas Spotlight Engine
function setupCanvasResize() {
  if (!heroCanvas) return;
  function resize() {
    const rect = heroCanvas.parentElement.getBoundingClientRect();
    heroCanvas.width = rect.width * (window.devicePixelRatio || 1);
    heroCanvas.height = rect.height * (window.devicePixelRatio || 1);
    renderCanvasFrame();
  }
  window.addEventListener('resize', resize);
  resize();
}

function transitionHeroSlide(targetIndex) {
  const pool = state.filteredArticles.length > 0 ? state.filteredArticles : state.articles;
  if (pool.length === 0) return;
  
  const prevIndex = state.heroIndex;
  state.heroIndex = (targetIndex + pool.length) % pool.length;

  const prevArt = pool[prevIndex];
  const nextArt = pool[state.heroIndex];

  currentImgObj = ensureImageLoaded(prevArt);
  nextImgObj = ensureImageLoaded(nextArt);

  animProgress = 0.0;
  animateCanvasTransition();
  renderHeroOverlayText(nextArt);
  renderHeroDots();
  resetProgressBar();
  preloadHeroImages();
}

function animateCanvasTransition() {
  if (animProgress < 1.0) {
    animProgress += 0.06;
    renderCanvasFrame();
    requestAnimationFrame(animateCanvasTransition);
  } else {
    animProgress = 1.0;
    renderCanvasFrame();
  }
}

function renderCanvasFrame() {
  if (!heroCtx || !heroCanvas) return;
  const w = heroCanvas.width;
  const h = heroCanvas.height;

  heroCtx.clearRect(0, 0, w, h);

  if (currentImgObj && currentImgObj.complete) {
    drawScaledImage(heroCtx, currentImgObj, w, h, 1.0 - animProgress);
  }

  if (nextImgObj && nextImgObj.complete && animProgress > 0) {
    drawScaledImage(heroCtx, nextImgObj, w, h, animProgress);
  }

  const gradient = heroCtx.createLinearGradient(0, h * 0.3, 0, h);
  gradient.addColorStop(0, 'rgba(7, 9, 14, 0.0)');
  gradient.addColorStop(1, 'rgba(7, 9, 14, 0.96)');
  heroCtx.fillStyle = gradient;
  heroCtx.fillRect(0, 0, w, h);
}

function drawScaledImage(ctx, img, cw, ch, alpha) {
  ctx.save();
  ctx.globalAlpha = alpha;
  const imgRatio = img.width / img.height;
  const canvasRatio = cw / ch;
  let dw, dh, dx, dy;

  if (imgRatio > canvasRatio) {
    dh = ch;
    dw = ch * imgRatio;
    dx = (cw - dw) / 2;
    dy = 0;
  } else {
    dw = cw;
    dh = cw / imgRatio;
    dx = 0;
    dy = (ch - dh) / 2;
  }

  ctx.drawImage(img, dx, dy, dw, dh);
  ctx.restore();
}

function renderHeroOverlayText(article) {
  if (!article || !heroOverlay) return;
  heroOverlay.innerHTML = `
    <div class="hero-badge-row">
      <span class="tag-badge">${article.category} SPOTLIGHT #${state.heroIndex + 1} (${article.region})</span>
      <span class="source-tag">✦ ${article.source} &bull; ${article.readTime}</span>
    </div>
    <h1 class="hero-title">${escapeHtml(article.title)}</h1>
    <p class="hero-desc">${escapeHtml(article.description)}</p>
    <div class="hero-actions">
      <button onclick="openModal('${article.id}')" class="btn-primary">
        <span>Read Story Deck</span> &rarr;
      </button>
      <a href="${article.link}" target="_blank" rel="noopener noreferrer" class="btn-secondary">
        Visit Source ↗
      </a>
    </div>
  `;
}

function renderHeroDots() {
  if (!heroDots) return;
  const pool = state.filteredArticles.length > 0 ? state.filteredArticles : state.articles;
  const count = Math.min(10, pool.length);
  heroDots.innerHTML = Array(count).fill(0).map((_, i) => `
    <div class="dot ${i === state.heroIndex ? 'active' : ''}" onclick="transitionHeroSlide(${i});"></div>
  `).join('');
}

function resetProgressBar() {
  state.progressValue = 0;
  if (canvasProgressBar) canvasProgressBar.style.width = '0%';
}

function startHeroTimer() {
  if (state.heroTimer) clearInterval(state.heroTimer);
  if (state.progressInterval) clearInterval(state.progressInterval);

  state.progressInterval = setInterval(() => {
    if (!state.heroPlaying) return;
    state.progressValue += 2;
    if (canvasProgressBar) canvasProgressBar.style.width = `${state.progressValue}%`;
    if (state.progressValue >= 100) {
      resetProgressBar();
      transitionHeroSlide(state.heroIndex + 1);
    }
  }, 100);
}

if (heroPlayPauseBtn) {
  heroPlayPauseBtn.addEventListener('click', () => {
    state.heroPlaying = !state.heroPlaying;
    heroPlayPauseBtn.textContent = state.heroPlaying ? '⏸' : '▶';
  });
}
if (heroPrevBtn) {
  heroPrevBtn.addEventListener('click', () => {
    transitionHeroSlide(state.heroIndex - 1);
  });
}
if (heroNextBtn) {
  heroNextBtn.addEventListener('click', () => {
    transitionHeroSlide(state.heroIndex + 1);
  });
}

// SLIDING APPLE GLASS TAB INDICATOR ENGINE
function updateTabIndicator() {
  const activeBtn = navTabs.querySelector('.tab-btn.active');
  if (!activeBtn || !tabIndicatorPill) return;

  const rect = activeBtn.getBoundingClientRect();
  const parentRect = navTabs.getBoundingClientRect();

  const left = rect.left - parentRect.left;
  const width = rect.width;

  tabIndicatorPill.style.width = `${width}px`;
  tabIndicatorPill.style.transform = `translateX(${left}px)`;
}

// INTELLIGENT MULTI-FIELD SEARCH ENGINE — Word-boundary aware, precise for specific queries
function searchArticles(query, articleList) {
  if (!query || query.trim() === '') return articleList;

  const rawQuery = query.toLowerCase().trim();
  const qTokens = rawQuery.replace(/[^\w\s]/g, '').split(/\s+/).filter(Boolean);
  const isMultiWord = qTokens.length > 1;
  
  // Word-boundary matcher: short tokens (≤3 chars) use regex \b to avoid
  // "ai" matching inside "India", "Ukraine", "Oman" etc.
  function textHas(text, token) {
    if (token.length <= 3) {
      return new RegExp('\\b' + token.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '\\b', 'i').test(text);
    }
    return text.includes(token);
  }
  
  // Build semantic expansion set (used as BOOST only, not primary match)
  let boostTokens = new Set();
  qTokens.forEach(token => {
    if (EXPANDED_SEMANTIC_MAP[token]) {
      EXPANDED_SEMANTIC_MAP[token].forEach(syn => boostTokens.add(syn));
    }
  });
  qTokens.forEach(t => boostTokens.delete(t));
  const boostArray = Array.from(boostTokens);

  let scoredArticles = articleList.map(art => {
    let score = 0;
    const titleText = (art.title || '').toLowerCase();
    const descText = (art.description || '').toLowerCase();
    const whatText = (art.annotation && art.annotation.what || '').toLowerCase();
    const whyText = (art.annotation && art.annotation.why || '').toLowerCase();
    const catText = (art.category || '').toLowerCase();
    const regText = (art.region || '').toLowerCase();
    const srcText = (art.source || '').toLowerCase();
    const fullText = `${titleText} ${descText} ${whatText} ${whyText} ${catText} ${regText} ${srcText}`;

    // TIER 1: Exact full phrase match (highest signal)
    if (textHas(titleText, rawQuery)) score += 80;
    else if (textHas(fullText, rawQuery)) score += 40;

    // TIER 2: Token presence scoring
    if (isMultiWord) {
      const allInTitle = qTokens.every(t => textHas(titleText, t));
      const allInFull = qTokens.every(t => textHas(fullText, t));
      
      if (allInTitle) score += 60;
      else if (allInFull) score += 25;
      else {
        // Multi-word: if not ALL tokens match, article is likely irrelevant
        const primaryInTitle = textHas(titleText, qTokens[0]);
        if (primaryInTitle) score += 8;
        else score = 0;
      }
    } else {
      // Single-word query
      const t = qTokens[0];
      if (textHas(titleText, t)) score += 30;
      if (textHas(catText, t)) score += 15;
      if (textHas(regText, t)) score += 12;
      if (textHas(whatText, t)) score += 10;
      if (textHas(descText, t)) score += 5;
      if (textHas(srcText, t)) score += 5;
    }

    // TIER 3: Semantic boost — small bonus, never primary qualifier
    if (score > 0) {
      boostArray.forEach(syn => {
        if (textHas(titleText, syn)) score += 3;
        if (textHas(descText, syn)) score += 1;
      });
    }

    return { article: art, score };
  })
  .filter(item => item.score >= 10)
  .sort((a, b) => b.score - a.score)
  .map(item => item.article);

  return scoredArticles;
}

// LIVE GOOGLE NEWS RSS SEARCH — Fetches real-time results for any topic
async function fetchLiveGoogleNews(query) {
  const encodedQuery = encodeURIComponent(query);
  const googleRssUrl = `https://news.google.com/rss/search?q=${encodedQuery}&hl=en-US&gl=US&ceid=US:en`;
  const proxyUrl = `https://api.rss2json.com/v1/api.json?rss_url=${encodeURIComponent(googleRssUrl)}`;

  try {
    const res = await fetch(proxyUrl);
    if (!res.ok) throw new Error('Proxy returned ' + res.status);
    const data = await res.json();
    if (data.status !== 'ok' || !data.items || data.items.length === 0) return [];

    return data.items.map((item, idx) => {
      const cleanTitle = item.title.replace(/\s*-\s*[^-]+$/, '').trim();
      const pubName = (item.title.match(/-\s*([^-]+)$/) || [])[1]?.trim() || 'Google News';
      const cleanDesc = (item.description || '').replace(/<[^>]*>?/gm, '').trim();
      const thumbUrl = (item.thumbnail && item.thumbnail.length > 10 && !item.thumbnail.includes('photo-1526304640581-d334cdbbf45e'))
        ? item.thumbnail
        : getTopicImageUrl(cleanTitle + " " + query, 'World', 'Global');

      return {
        id: `gnews-${Date.now()}-${idx}`,
        title: cleanTitle,
        link: item.link,
        description: cleanDesc || `${cleanTitle}. Live indexed via Google News.`,
        source: pubName,
        sourceLogo: 'G',
        category: 'World',
        region: 'Global',
        pubDate: item.pubDate,
        imageUrl: thumbUrl,
        annotation: {
          what: cleanTitle,
          why: cleanDesc || 'Live result from Google News index.'
        },
        readTime: '3 min read',
        relatedSources: [
          { name: pubName, url: item.link },
          { name: 'Google News', url: `https://news.google.com/search?q=${encodedQuery}` }
        ],
        _isLive: true
      };
    });
  } catch (e) {
    console.warn('Google News live fetch failed:', e);
    return [];
  }
}

// CROSS-DIMENSIONAL REGION x CATEGORY INTELLIGENCE MATRIX (STRICT RELEVANCE ENGINE)
async function filterAndRender() {
  let list = [...state.articles];
  const targetReg = state.currentRegion.toLowerCase();
  const targetCat = state.currentCategory.toLowerCase();

  // STRICT CATEGORY & REGION MATRIX: Prevents off-topic stories from bleeding into specialized feeds
  if (targetCat !== 'top10') {
    // 1. Hard Category Filter: Under Tech, ONLY Tech articles allowed! World/Politics 100% excluded!
    list = list.filter(a => a.category.toLowerCase() === targetCat);

    // 2. Region Prioritization within this Category
    if (targetReg !== 'all') {
      const regMatches = list.filter(a => a.region.toLowerCase() === targetReg || (targetReg === 'global' && a.region.toLowerCase() === 'world'));
      const otherMatches = list.filter(a => a.region.toLowerCase() !== targetReg && (targetReg !== 'global' || a.region.toLowerCase() !== 'world'));
      
      // Exact region matches of this category first, followed by global matches of SAME category
      list = [...regMatches, ...otherMatches];
    }
  } else {
    // Top 10 Colossal Digest:
    if (targetReg !== 'all') {
      const regMatches = list.filter(a => a.region.toLowerCase() === targetReg || (targetReg === 'global' && a.region.toLowerCase() === 'world'));
      const otherMatches = list.filter(a => a.region.toLowerCase() !== targetReg && (targetReg !== 'global' || a.region.toLowerCase() !== 'world'));
      list = [...regMatches, ...otherMatches];
    }
    list = list.slice(0, 10);
  }

  // SEARCH: Local semantic first, then live Google News expansion
  const query = state.searchQuery.trim();
  if (query !== '') {
    // When searching, search ALL local articles
    const allLocalMatches = searchArticles(query, state.articles);

    if (allLocalMatches.length >= 4) {
      list = allLocalMatches;
      gridTitle.textContent = `Search Results for "${query}" (${list.length} Stories)`;
    } else {
      gridTitle.textContent = `🔍 Searching Google News for "${query}"...`;
      renderGrid(allLocalMatches);

      const liveResults = await fetchLiveGoogleNews(query);

      if (liveResults.length > 0) {
        liveResults.forEach(art => {
          if (!canvasImages[art.id]) {
            const img = new Image();
            img.crossOrigin = 'Anonymous';
            img.onerror = () => { img.src = DEFAULT_FALLBACK_IMG; };
            img.src = art.imageUrl;
            canvasImages[art.id] = img;
          }
        });

        const seenTitles = new Set(allLocalMatches.map(a => a.title.toLowerCase()));
        const uniqueLive = liveResults.filter(a => !seenTitles.has(a.title.toLowerCase()));
        list = [...allLocalMatches, ...uniqueLive];

        const liveCount = uniqueLive.length;
        const localCount = allLocalMatches.length;
        gridTitle.textContent = `Search: "${query}" — ${localCount} curated + ${liveCount} live from Google News (${list.length} total)`;
      } else if (allLocalMatches.length > 0) {
        list = allLocalMatches;
        gridTitle.textContent = `Search Results for "${query}" (${list.length} Stories)`;
      } else {
        list = [];
        gridTitle.textContent = `No results found for "${query}" — try different keywords`;
      }
    }
  } else {
    const regionLabel = state.currentRegion === 'all' ? '' : ` in ${state.currentRegion}`;
    const catLabel = state.currentCategory === 'top10' ? 'Top Colossal Digest' : `${state.currentCategory} News`;

    let countLabel = `(${list.length} Stories)`;
    if (targetCat !== 'top10' && targetReg !== 'all') {
      const exactCount = list.filter(a => a.region.toLowerCase() === targetReg || (targetReg === 'global' && a.region.toLowerCase() === 'world')).length;
      if (exactCount > 0 && exactCount < list.length) {
        countLabel = `(${exactCount} Regional + ${list.length - exactCount} Global — ${list.length} Total)`;
      } else if (exactCount === 0) {
        countLabel = `(0 Regional + ${list.length} Global — ${list.length} Total)`;
      } else {
        countLabel = `(${exactCount} Stories)`;
      }
    }

    gridTitle.textContent = `${catLabel}${regionLabel} ${countLabel}`;
  }

  state.filteredArticles = list;

  renderGrid(list);

  state.heroIndex = 0;
  transitionHeroSlide(0);
  startHeroTimer();
  updateTabIndicator();
}

function scrollToContent() {
  if (contentGridSection) {
    const yOffset = -90;
    const y = contentGridSection.getBoundingClientRect().top + window.pageYOffset + yOffset;
    window.scrollTo({ top: y, behavior: 'smooth' });
  }
}

function createCardHTML(art, idx) {
  const saved = isBookmarked(art.id);
  const delay = Math.min(idx * 0.04, 0.4).toFixed(2);
  const imgUrl = (art.imageUrl && !art.imageUrl.includes('photo-1526304640581-d334cdbbf45e'))
    ? art.imageUrl
    : getTopicImageUrl(art.title, art.category, art.region);

  return `
    <article class="news-card" data-id="${art.id}" data-article-id="${art.id}" style="animation-delay: ${delay}s; --card-index: ${idx};" onclick="openModal('${art.id}')">
      <div class="card-sheen"></div>
      <div class="card-thumb-box">
        <img src="${imgUrl}" alt="${escapeHtml(art.title)}" class="card-thumb" width="640" height="360" loading="lazy" decoding="async" onerror="this.onerror=null; this.src=getTopicImageUrl('${escapeJs(art.title)}', '${escapeJs(art.category)}', '${escapeJs(art.region)}');" />
        <span class="card-category">${art.category}</span>
        <button class="bookmark-btn ${saved ? 'saved' : ''}" onclick="toggleBookmark('${art.id}', event)" title="Save Article" aria-label="Save Article">
          ${saved ? '★' : '☆'}
        </button>
      </div>

      <div class="card-content">
        <div class="card-meta">
          <span class="card-source">${art.sourceLogo} &bull; ${art.source}</span>
          <span>${art.readTime}</span>
        </div>
        <h3 class="card-title">${escapeHtml(art.title)}</h3>

        <!-- Crisp Annotation Preview -->
        <div class="annotation-box">
          <div class="annotation-title">✦ Crisp Annotation (${art.region})</div>
          <p class="annotation-bullet">${escapeHtml(art.annotation ? art.annotation.what : art.title)}</p>
        </div>

        <!-- Dual Prominent Action Buttons: Deck Preview + Direct Source Link -->
        <div class="card-footer" style="display: flex; align-items: center; justify-content: space-between; gap: 0.5rem; margin-top: auto; padding-top: 0.8rem; border-top: 1px solid var(--border-color);">
          <button onclick="event.stopPropagation(); openModal('${art.id}');" class="btn-primary" style="padding: 0.45rem 0.95rem; font-size: 0.8rem;" title="Open Frosted Glass Executive Reader Deck" aria-label="Open Deck Preview">
            ✦ Deck Preview
          </button>
          <a href="${art.link}" target="_blank" rel="noopener noreferrer" class="btn-secondary" style="padding: 0.45rem 0.95rem; font-size: 0.8rem; color: var(--text-primary); border: 1px solid var(--border-color);" onclick="event.stopPropagation()" title="Read Full Story directly on ${art.source}" aria-label="Read full story on source">
            Source ↗
          </a>
        </div>
      </div>
    </article>
  `;
}

let _gridScrollObserver = null;
let _currentRenderedCount = 0;

// RENDER MAIN GRID WITH DUAL BUTTONS (DECK PREVIEW & DIRECT SOURCE LINK)
function renderGrid(articles) {
  if (articles.length === 0) {
    const regionName = state.currentRegion === 'all' ? '' : ` in ${state.currentRegion}`;
    newsGrid.innerHTML = `
      <div style="grid-column: 1/-1; text-align: center; padding: 4rem 1rem; color: var(--text-muted);">
        <p style="font-size: 1.2rem;">No matching articles found for '${escapeHtml(state.searchQuery || state.currentCategory)}'${regionName}.</p>
        <button onclick="resetFilters()" class="btn-primary" style="margin-top: 1rem;">Reset All Filters</button>
      </div>
    `;
    return;
  }

  if (_gridScrollObserver) {
    _gridScrollObserver.disconnect();
    _gridScrollObserver = null;
  }

  const existingSentinel = document.getElementById('gridScrollSentinel');
  if (existingSentinel) existingSentinel.remove();

  // Instant First Paint batch (24 stories), dynamically loads subsequent batches on scroll
  const INITIAL_BATCH = 24;
  _currentRenderedCount = Math.min(articles.length, INITIAL_BATCH);

  // Collect paired stories for injection (deduplicate by cluster)
  const _pairedCards = [];
  const _seenClusters = new Set();
  articles.forEach(art => {
    if (art.pairedStory && art.perspectives && art.perspectives.length >= 2 && typeof createPairedCardHTML === 'function') {
      const clusterKey = art.perspectives.map(p => p.source).sort().join('|');
      if (!_seenClusters.has(clusterKey)) {
        _seenClusters.add(clusterKey);
        _pairedCards.push(art);
      }
    }
  });

  // Build grid HTML with paired cards injected every 6 regular cards
  let gridHTML = '';
  let pairedIdx = 0;
  const batch = articles.slice(0, _currentRenderedCount);
  for (let i = 0; i < batch.length; i++) {
    gridHTML += createCardHTML(batch[i], i);
    if ((i + 1) % 6 === 0 && pairedIdx < _pairedCards.length) {
      gridHTML += createPairedCardHTML(_pairedCards[pairedIdx]);
      pairedIdx++;
    }
  }
  newsGrid.innerHTML = gridHTML;
  attach3DTiltListeners();

  if (_currentRenderedCount < articles.length) {
    const sentinel = document.createElement('div');
    sentinel.id = 'gridScrollSentinel';
    sentinel.style.cssText = 'grid-column: 1/-1; height: 30px; margin: 1rem 0; opacity: 0; pointer-events: none;';
    newsGrid.after(sentinel);

    _gridScrollObserver = new IntersectionObserver((entries) => {
      if (entries[0].isIntersecting && _currentRenderedCount < articles.length) {
        const nextBatch = articles.slice(_currentRenderedCount, _currentRenderedCount + 16);
        const startIndex = _currentRenderedCount;
        _currentRenderedCount += nextBatch.length;

        const tempContainer = document.createElement('div');
        tempContainer.innerHTML = nextBatch.map((art, idx) => createCardHTML(art, startIndex + idx)).join('');
        while (tempContainer.firstChild) {
          newsGrid.appendChild(tempContainer.firstChild);
        }

        attach3DTiltListeners();

        if (_currentRenderedCount >= articles.length) {
          sentinel.remove();
          _gridScrollObserver.disconnect();
          _gridScrollObserver = null;
        }
      }
    }, { rootMargin: '500px' });

    _gridScrollObserver.observe(sentinel);
  }
}

// 3D CURSOR TILT & SPECULAR SHEEN PHYSICS ENGINE
function attach3DTiltListeners() {
  const cards = newsGrid.querySelectorAll('.news-card:not([data-tilt-ready])');
  cards.forEach(card => {
    card.setAttribute('data-tilt-ready', 'true');
    card.addEventListener('mousemove', (e) => {
      const rect = card.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      
      const centerX = rect.width / 2;
      const centerY = rect.height / 2;
      
      const rotateX = -((y - centerY) / centerY) * 7;
      const rotateY = ((x - centerX) / centerX) * 7;
      
      const percentX = ((x / rect.width) * 100).toFixed(1);
      const percentY = ((y / rect.height) * 100).toFixed(1);

      card.style.transform = `perspective(1000px) rotateX(${rotateX.toFixed(2)}deg) rotateY(${rotateY.toFixed(2)}deg) translateY(-4px)`;
      card.style.setProperty('--mouse-x', `${percentX}%`);
      card.style.setProperty('--mouse-y', `${percentY}%`);
    });

    card.addEventListener('mouseleave', () => {
      card.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) translateY(0px)';
    });
  });
}

// APPLE VISIONOS FROSTED SPECULAR GLASS MODAL ENGINE WITH WORKING CLICKABLE SUBTLE SOURCE BUTTON
window.openModal = function(id) {
  const pool = state.filteredArticles.length > 0 ? state.filteredArticles : state.articles;
  let index = pool.findIndex(a => a.id === id);
  if (index === -1) {
    index = state.articles.findIndex(a => a.id === id);
    if (index === -1) return;
    state.modalState.articles = state.articles;
    state.modalState.currentIndex = index;
  } else {
    state.modalState.articles = pool;
    state.modalState.currentIndex = index;
  }

  document.body.classList.add('modal-open');
  renderExecutiveModal();
  modalBackdrop.classList.add('active');
};

function renderExecutiveModal() {
  const pool = state.modalState.articles;
  const currIdx = state.modalState.currentIndex;
  const total = pool.length;
  const art = pool[currIdx];
  if (!art) return;

  const themeColor = getNewsColor(art.category);
  modalBackdrop.style.setProperty('--news-theme-color', themeColor);

  // Natural time-ago label
  const timeAgo = getTimeAgo(art.pubDate);

  // Dynamic Image Fallback based on Topic & Region
  const validImageUrl = (art.imageUrl && !art.imageUrl.includes('photo-1526304640581-d334cdbbf45e'))
    ? art.imageUrl
    : getTopicImageUrl(art.title, art.category, art.region);

  // Editorial Briefing & Drop Cap synthesis (with complete sentence enforcement)
  function cleanAndCompleteText(raw) {
    if (!raw) return '';
    let s = raw.trim();
    // Strip trailing dots, ellipses, or cut-off symbols
    s = s.replace(/[\.\s]*[\.…]+$/, '').trim();
    // Trim back to last complete sentence if terminated mid-sentence
    const lastPeriod = Math.max(s.lastIndexOf('.'), s.lastIndexOf('?'), s.lastIndexOf('!'));
    if (lastPeriod > 50) {
      s = s.slice(0, lastPeriod + 1);
    } else if (s && !s.endsWith('.')) {
      s += '.';
    }
    return s;
  }

  const rawDesc = art.description || '';
  const cleanDesc = cleanAndCompleteText(rawDesc);
  const storyText = escapeHtml(cleanDesc);
  const titleText = escapeHtml(art.title || '');

  // Check if annotation.why is distinct from description
  const rawWhy = (art.annotation && art.annotation.why) ? art.annotation.why : '';
  const cleanWhy = cleanAndCompleteText(rawWhy);
  const isWhyDistinct = cleanWhy.length > 20 && !storyText.includes(cleanWhy.slice(0, 30)) && !cleanWhy.includes(storyText.slice(0, 30));

  let storyBodyHtml = '';
  if (!storyText || storyText.length < 180 || storyText === titleText) {
    storyBodyHtml = `
      <div style="display: flex; flex-direction: column; gap: 1.1rem;">
        <p style="font-size: 1.08rem; color: var(--text-primary); line-height: 1.8; margin: 0; font-weight: 500;">
          ${storyText && storyText !== titleText ? storyText : titleText + '.'}
        </p>

        <div style="background: ${themeColor}0a; border-left: 3px solid ${themeColor}; padding: 1rem 1.2rem; border-radius: 0 var(--radius-sm) var(--radius-sm) 0;">
          <span style="font-size: 0.72rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.08em; color: ${themeColor}; display: block; margin-bottom: 0.3rem;">
            ✦ Executive Intelligence Briefing
          </span>
          <ul style="margin: 0; padding-left: 1.1rem; color: var(--text-secondary); font-size: 0.94rem; line-height: 1.65;">
            <li style="margin-bottom: 0.35rem;"><strong>Source Reporting:</strong> Verified live coverage dispatched by ${escapeHtml(art.source)} tracking ${escapeHtml(art.category)} affairs in ${escapeHtml(art.region)}.</li>
            <li style="margin-bottom: 0.35rem;"><strong>Key Takeaway:</strong> Official statements and strategic updates being monitored as events unfold.</li>
            <li><strong>Full Access:</strong> Tap below to review the complete, unedited publication on ${escapeHtml(art.source)}.</li>
          </ul>
        </div>
      </div>
    `;
  } else {
    storyBodyHtml = storyText.length > 80
      ? `<span style="float: left; font-size: 3.2rem; font-weight: 800; line-height: 0.85; margin-right: 0.15rem; margin-top: 0.08rem; color: ${themeColor}; font-family: var(--font-heading);">${storyText.charAt(0)}</span>${storyText.slice(1)}`
      : storyText;
  }

  const saved = isBookmarked(art.id);

  modalContent.innerHTML = `
    <!-- Reading Progress Bar — whisper-thin -->
    <div class="deck-progress-bar" id="deckProgressBar"></div>

    <!-- DEDICATED MOBILE DECK HEADER BAR (Clean, Non-Overlapping on Mobile) -->
    <div class="mobile-deck-header">
      <div class="mobile-deck-header-left">
        <span class="mobile-deck-counter">${currIdx + 1} / ${total}</span>
        <span class="mobile-deck-tag" style="color: ${themeColor}; border-color: ${themeColor};">${art.category}</span>
      </div>
      <div class="mobile-deck-header-right">
        <button class="mobile-deck-bookmark ${saved ? 'saved' : ''}" onclick="toggleBookmark('${art.id}', event); renderExecutiveModal();" aria-label="Save story">
          ${saved ? '★ Saved' : '☆ Save'}
        </button>
        <button class="mobile-deck-close" onclick="closeModal()" aria-label="Close modal">&times;</button>
      </div>
    </div>

    <!-- DESKTOP FLOATING CONTROLS (Hidden on Mobile via CSS) -->
    <div class="liquid-glass-nav-container desktop-only-control">
      <div class="liquid-glass-reflection-glow"></div>
      <div class="liquid-glass-pill">
        <span class="liquid-glass-counter">${currIdx + 1} / ${total}</span>
      </div>
    </div>

    <button class="liquid-glass-bookmark desktop-only-control ${saved ? 'saved' : ''}" onclick="toggleBookmark('${art.id}', event); renderExecutiveModal();" aria-label="Save story for later" title="Save story for later">
      ${saved ? '★ Saved' : '☆ Save'}
    </button>

    <button class="liquid-glass-close desktop-only-control" onclick="closeModal()" aria-label="Close modal">&times;</button>

    <div class="deck-scroll-body" id="deckScrollBody">
      <!-- Parallax Cover -->
      <div class="deck-cover-parallax" id="deckCoverParallax">
        <div class="cover-tap-zone cover-tap-zone-left" onclick="navigateModal(-1)"></div>
        <div class="cover-tap-zone cover-tap-zone-right" onclick="navigateModal(1)"></div>

        <img id="deckCoverImg" src="${validImageUrl}" alt="${escapeHtml(art.title)}" onerror="this.onerror=null; this.src=getTopicImageUrl('${escapeJs(art.title)}', '${escapeJs(art.category)}', '${escapeJs(art.region)}');" />
        <div style="position: absolute; inset: 0; background: linear-gradient(0deg, var(--bg-surface) 0%, rgba(15, 21, 35, 0.3) 60%, rgba(0,0,0,0.55) 100%); pointer-events: none;"></div>
        
        <!-- Banner Overlay — Source & Category -->
        <div class="deck-cover-banner" style="position: absolute; bottom: 1.2rem; left: 1.8rem; right: 1.8rem; display: flex; align-items: center; justify-content: space-between; z-index: 50;">
          <span class="tag-badge desktop-only-control" style="border-color: ${themeColor}; color: ${themeColor}; background: rgba(0, 242, 254, 0.1); backdrop-filter: blur(12px);">${art.category}</span>
          
          <div style="display: flex; align-items: center; gap: 0.5rem; z-index: 60;">
            <span style="font-size: 0.78rem; color: #cbd5e1; background: rgba(7, 9, 14, 0.8); backdrop-filter: blur(12px); padding: 0.3rem 0.75rem; border-radius: var(--radius-full); border: 1px solid rgba(255,255,255,0.12); font-weight: 600;">
              ${art.source}
            </span>
            <a href="${art.link}" target="_blank" rel="noopener noreferrer" style="background: ${themeColor}; color: #fff; padding: 0.3rem 0.8rem; border-radius: var(--radius-full); font-size: 0.74rem; font-weight: 700; text-decoration: none; transition: opacity 0.2s ease; opacity: 0.9;" onclick="event.stopPropagation()" onmouseover="this.style.opacity='1'" onmouseout="this.style.opacity='0.9'">
              Source ↗
            </a>
          </div>
        </div>
      </div>

      <!-- Article Content Body — Editorial (responsive padding via CSS class) -->
      <div class="deck-content-fade deck-content-body">

        <!-- Whisper Meta Line with time-ago -->
        <div style="display: flex; align-items: center; gap: 0.45rem; margin-bottom: 0.8rem; opacity: 0.5; font-size: 0.76rem; font-weight: 600; color: var(--text-muted); letter-spacing: 0.03em;">
          <span>${art.source}</span>
          <span style="opacity: 0.35;">·</span>
          <span>${art.readTime}</span>
          <span style="opacity: 0.35;">·</span>
          <span>${art.region}</span>
          ${timeAgo ? `<span style="opacity: 0.35;">·</span><span>${timeAgo}</span>` : ''}
        </div>

        <!-- Headline -->
        <h2 style="font-family: var(--font-heading); font-size: 1.85rem; font-weight: 800; line-height: 1.3; margin-bottom: 1.2rem; color: var(--text-primary); font-feature-settings: 'kern' 1, 'liga' 1;">${escapeHtml(art.title)}</h2>

        <!-- Thin Accent Divider -->
        <div style="width: 44px; height: 3px; border-radius: 2px; background: ${themeColor}; margin-bottom: 1.4rem; opacity: 0.8;"></div>

        <!-- Key Executive Context (Only rendered if distinct from description) -->
        ${isWhyDistinct ? `
        <div style="border-left: 3px solid ${themeColor}; padding-left: 1.1rem; margin-bottom: 1.6rem; background: ${themeColor}08; padding-top: 0.6rem; padding-bottom: 0.6rem; border-radius: 0 var(--radius-sm) var(--radius-sm) 0;">
          <span style="font-size: 0.72rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.08em; color: ${themeColor}; display: block; margin-bottom: 0.2rem;">Executive Context</span>
          <p style="font-size: 0.96rem; color: var(--text-secondary); line-height: 1.65; margin: 0;">${escapeHtml(cleanWhy)}</p>
        </div>
        ` : ''}

        <!-- Story Body with Structured Briefing / Drop Cap -->
        <div style="color: var(--text-secondary); line-height: 1.85; margin-bottom: 2rem;">${storyBodyHtml}</div>

        <!-- Hairline -->
        <div style="height: 1px; background: var(--border-color); margin-bottom: 1.4rem; opacity: 0.6;"></div>

        <!-- Story DNA Lineage Timeline -->
        ${typeof renderStoryDNA === 'function' ? renderStoryDNA(art) : ''}

        <!-- Related Sources -->
        <div style="display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap; margin-bottom: 1.5rem;">
          <span style="font-size: 0.74rem; font-weight: 700; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.06em; opacity: 0.6;">Cross-Reference</span>
          ${art.relatedSources.map(s => `
            <a href="${s.url}" target="_blank" rel="noopener noreferrer" style="font-size: 0.78rem; color: var(--text-secondary); text-decoration: none; padding: 0.3rem 0.7rem; border-radius: var(--radius-full); border: 1px solid var(--border-color); font-weight: 600; opacity: 0.8; transition: all 0.2s ease;" onclick="event.stopPropagation()" onmouseover="this.style.borderColor='${themeColor}'; this.style.opacity='1';" onmouseout="this.style.borderColor='var(--border-color)'; this.style.opacity='0.8';">
              ${s.name} ↗
            </a>
          `).join('')}
        </div>

        <!-- Actions -->
        <div style="display: flex; gap: 0.7rem; align-items: center; flex-wrap: wrap;">
          <a href="${art.link}" target="_blank" rel="noopener noreferrer" style="display: inline-flex; align-items: center; gap: 0.35rem; font-size: 0.82rem; font-weight: 700; color: var(--text-primary); text-decoration: none; padding: 0.55rem 1.2rem; border-radius: var(--radius-full); border: 1px solid var(--border-color); transition: all 0.2s ease;" onclick="event.stopPropagation()" onmouseover="this.style.borderColor='${themeColor}'; this.style.background='${themeColor}10';" onmouseout="this.style.borderColor='var(--border-color)'; this.style.background='transparent';">
            Read full article ↗
          </a>
          <button onclick="event.stopPropagation(); speakArticle('${escapeJs(art.title)}. ${escapeJs(art.annotation.what)}');" style="display: inline-flex; align-items: center; gap: 0.35rem; font-size: 0.82rem; font-weight: 600; color: var(--text-muted); background: none; border: 1px solid var(--border-color); padding: 0.55rem 1.1rem; border-radius: var(--radius-full); cursor: pointer; transition: all 0.2s ease;" onmouseover="this.style.color='var(--text-primary)'; this.style.borderColor='${themeColor}';" onmouseout="this.style.color='var(--text-muted)'; this.style.borderColor='var(--border-color)';">
            🎙 Listen
          </button>
        </div>

        <p style="font-size: 0.74rem; color: var(--text-muted); margin-top: 1.8rem; opacity: 0.4; line-height: 1.4;">
          Reporting by ${art.source}. All rights belong to the original publisher.
        </p>
      </div>
    </div>
  `;

  // PARALLAX COVER SCROLL & READING PROGRESS BAR
  const scrollContainer = document.getElementById('deckScrollBody');
  const coverImg = document.getElementById('deckCoverImg');
  const progressBar = document.getElementById('deckProgressBar');

  if (scrollContainer) {
    let glowTimeout = null;
    scrollContainer.addEventListener('scroll', () => {
      const scrollTop = scrollContainer.scrollTop;

      if (coverImg && scrollTop < 500) {
        coverImg.style.transform = `translateY(${scrollTop * 0.35}px)`;
      }

      if (progressBar) {
        const scrollHeight = scrollContainer.scrollHeight - scrollContainer.clientHeight;
        const progress = scrollHeight > 0 ? (scrollTop / scrollHeight) * 100 : 0;
        progressBar.style.width = `${progress.toFixed(1)}%`;

        // Scroll-linked progress glow
        progressBar.classList.add('active-glow');
        clearTimeout(glowTimeout);
        glowTimeout = setTimeout(() => progressBar.classList.remove('active-glow'), 600);

        // Fade out bottom gradient when near bottom
        if (progress > 92) {
          scrollContainer.style.setProperty('--scroll-fade-opacity', '0');
        } else {
          scrollContainer.style.setProperty('--scroll-fade-opacity', '1');
        }
      }
    }, { passive: true });

    scrollContainer.scrollTop = 0;
  }

  // Setup mobile 1-finger horizontal touch swipe gestures
  setupMobileDeckSwipe();
}

// ADVANCED CROSS-PLATFORM MOBILE TOUCH SWIPE ENGINE (iOS & Android)
function setupMobileDeckSwipe() {
  const card = document.querySelector('.deck-modal-card');
  if (!card) return;

  let startX = 0;
  let startY = 0;
  let currentX = 0;
  let currentY = 0;
  let isSwiping = false;

  card.addEventListener('touchstart', (e) => {
    if (e.touches.length !== 1) return;
    startX = e.touches[0].clientX;
    startY = e.touches[0].clientY;
    currentX = startX;
    currentY = startY;
    isSwiping = true;
  }, { passive: true });

  card.addEventListener('touchmove', (e) => {
    if (!isSwiping || e.touches.length !== 1) return;
    currentX = e.touches[0].clientX;
    currentY = e.touches[0].clientY;

    const diffX = currentX - startX;
    const diffY = currentY - startY;

    // Provide visual rubber-band preview if gesture is predominantly horizontal
    if (Math.abs(diffX) > Math.abs(diffY) * 1.2 && Math.abs(diffX) > 15) {
      card.style.transform = `translateX(${diffX * 0.35}px)`;
      card.style.transition = 'none';
    }
  }, { passive: true });

  card.addEventListener('touchend', (e) => {
    if (!isSwiping) return;
    isSwiping = false;

    const diffX = currentX - startX;
    const diffY = currentY - startY;

    // Restore smooth card positioning animation
    card.style.transition = 'transform 0.35s cubic-bezier(0.16, 1, 0.3, 1)';
    card.style.transform = 'translateY(0) translateX(0)';

    // Confirm horizontal swipe intent (min 40px horizontal diff, diffX > 1.2x diffY)
    if (Math.abs(diffX) > 40 && Math.abs(diffX) > Math.abs(diffY) * 1.2) {
      if (diffX < 0) {
        // Swiped left -> Next story
        navigateModal(1);
      } else {
        // Swiped right -> Previous story
        navigateModal(-1);
      }
    }
  }, { passive: true });
}

// Natural time-ago — no libraries, just clean human language
function getTimeAgo(dateStr) {
  if (!dateStr) return '';
  try {
    const then = new Date(dateStr);
    const now = new Date();
    const diffMs = now - then;
    if (diffMs < 0 || isNaN(diffMs)) return '';
    
    const mins = Math.floor(diffMs / 60000);
    if (mins < 2) return 'Just now';
    if (mins < 60) return `${mins}m ago`;
    
    const hrs = Math.floor(mins / 60);
    if (hrs < 24) return `${hrs}h ago`;
    
    const days = Math.floor(hrs / 24);
    if (days === 1) return 'Yesterday';
    if (days < 7) return `${days}d ago`;
    
    return '';
  } catch (e) { return ''; }
}

window.navigateModal = function(step) {
  const pool = state.modalState.articles;
  if (pool.length === 0) return;
  state.modalState.currentIndex = (state.modalState.currentIndex + step + pool.length) % pool.length;
  renderExecutiveModal();
};

window.closeModal = function() {
  document.body.classList.remove('modal-open');
  modalBackdrop.classList.remove('active');
};

window.closeShortcutModal = function() {
  shortcutModalBackdrop.classList.remove('active');
};

modalBackdrop.addEventListener('click', (e) => {
  if (e.target === modalBackdrop) closeModal();
});

shortcutModalBackdrop.addEventListener('click', (e) => {
  if (e.target === shortcutModalBackdrop) closeShortcutModal();
});

if (shortcutHelpBtn) {
  shortcutHelpBtn.addEventListener('click', () => {
    shortcutModalBackdrop.classList.add('active');
  });
}

// REAL-TIME INSTANT VOICE MODULATOR ENGINE
function setupVoiceModulator() {
  if (!('speechSynthesis' in window)) return;

  const audioPrevBtn = document.getElementById('audioPrevBtn');
  const audioNextBtn = document.getElementById('audioNextBtn');
  const handsFreeToggleBtn = document.getElementById('handsFreeToggleBtn');

  if (handsFreeToggleBtn) {
    handsFreeToggleBtn.addEventListener('click', () => {
      state.audioState.handsFreeMode = !state.audioState.handsFreeMode;
      if (state.audioState.handsFreeMode) {
        handsFreeToggleBtn.classList.add('active');
        handsFreeToggleBtn.textContent = '📻 Hands-Free: ON';
      } else {
        handsFreeToggleBtn.classList.remove('active');
        handsFreeToggleBtn.textContent = '📻 Hands-Free: OFF';
      }
    });
  }

  voiceModToggle.addEventListener('click', () => {
    voiceModDrawer.classList.toggle('open');
  });

  if (resetVoiceBtn) {
    resetVoiceBtn.addEventListener('click', () => {
      rateSlider.value = 0.95;
      pitchSlider.value = 1.0;
      state.audioState.rate = 0.95;
      state.audioState.pitch = 1.0;
      rateValLabel.textContent = "0.95x";
      pitchValLabel.textContent = "1.00x";
      speedBadge.textContent = "0.95x";
      if (state.audioState.isPlaying) {
        playStoryAtIndex(state.audioState.currentIndex || 0);
      }
    });
  }

  const populateVoices = () => {
    const voices = window.speechSynthesis.getVoices();
    if (!voiceSelect) return;
    voiceSelect.innerHTML = '';
    
    // Sort neural/natural human voices to top
    const sorted = [...voices].sort((a, b) => {
      const aNat = a.name.includes('Natural') || a.name.includes('Neural') || a.name.includes('Google') || a.name.includes('Samantha');
      const bNat = b.name.includes('Natural') || b.name.includes('Neural') || b.name.includes('Google') || b.name.includes('Samantha');
      return bNat - aNat;
    });

    sorted.forEach(v => {
      const option = document.createElement('option');
      option.value = v.voiceURI;
      option.textContent = `${v.name} (${v.lang})`;
      if (!state.audioState.selectedVoiceURI && (v.name.includes('Natural') || v.name.includes('Neural') || v.name.includes('Google US English') || v.name.includes('Samantha'))) {
        option.selected = true;
        state.audioState.selectedVoiceURI = v.voiceURI;
      }
      voiceSelect.appendChild(option);
    });
  };

  if ('speechSynthesis' in window) {
    populateVoices();
    window.speechSynthesis.onvoiceschanged = populateVoices;
  }

  if (voiceSelect) {
    voiceSelect.addEventListener('change', (e) => {
      state.audioState.selectedVoiceURI = e.target.value;
      if (state.audioState.isPlaying) {
        playStoryAtIndex(state.audioState.currentIndex || 0);
      }
    });
  }

  rateSlider.addEventListener('input', (e) => {
    const val = parseFloat(e.target.value);
    state.audioState.rate = val;
    rateValLabel.textContent = `${val.toFixed(2)}x`;
    speedBadge.textContent = `${val.toFixed(2)}x`;

    if (state.audioState.isPlaying) {
      playStoryAtIndex(state.audioState.currentIndex || 0);
    }
  });

  pitchSlider.addEventListener('input', (e) => {
    const val = parseFloat(e.target.value);
    state.audioState.pitch = val;
    pitchValLabel.textContent = `${val.toFixed(2)}x`;

    if (state.audioState.isPlaying) {
      playStoryAtIndex(state.audioState.currentIndex || 0);
    }
  });

  if (audioPrevBtn) {
    audioPrevBtn.addEventListener('click', () => {
      const activeList = getActiveFeedArticles();
      if (!activeList.length) return;
      const prevIdx = Math.max(0, (state.audioState.currentIndex || 0) - 1);
      playStoryAtIndex(prevIdx);
    });
  }

  if (audioNextBtn) {
    audioNextBtn.addEventListener('click', () => {
      const activeList = getActiveFeedArticles();
      if (!activeList.length) return;
      const nextIdx = Math.min(activeList.length - 1, (state.audioState.currentIndex || 0) + 1);
      playStoryAtIndex(nextIdx);
    });
  }
}

function getActiveFeedArticles() {
  if (state.searchQuery && state.searchQuery.trim().length > 0) {
    return state.searchResults || [];
  }
  const cat = state.currentCategory || 'top10';
  if (cat === 'top10') {
    let list = state.articles;
    if (state.currentRegion && state.currentRegion !== 'all') {
      list = list.filter(a => a.region === state.currentRegion);
    }
    return list.slice(0, 10);
  } else {
    let list = state.articles.filter(a => a.category === cat);
    if (state.currentRegion && state.currentRegion !== 'all') {
      list = list.filter(a => a.region === state.currentRegion);
    }
    return list;
  }
}

function getSelectedVoice() {
  if (!('speechSynthesis' in window)) return null;
  const voices = window.speechSynthesis.getVoices();
  if (state.audioState.selectedVoiceURI) {
    const found = voices.find(v => v.voiceURI === state.audioState.selectedVoiceURI);
    if (found) return found;
  }
  return voices.find(v => v.lang.startsWith('en') && (v.name.includes('Natural') || v.name.includes('Neural') || v.name.includes('Google') || v.name.includes('Samantha'))) || voices[0];
}

// CONVERSATIONAL RADIO ANCHOR SCRIPT SYNTHESIZER
function generateHumanBroadcastScript(article, index, total) {
  if (!article) return 'No intelligence dispatches available.';

  const source = article.source || 'News Dispatches';
  const region = article.region || 'Global';
  const category = article.category || 'World';
  const title = (article.title || '').trim();

  let desc = (article.description || '').trim();
  // Strip trailing dots, ellipses, or cut-off symbols
  desc = desc.replace(/[\.\s]*[\.…]+$/, '').trim();
  const lastPeriod = Math.max(desc.lastIndexOf('.'), desc.lastIndexOf('?'), desc.lastIndexOf('!'));
  if (lastPeriod > 40) {
    desc = desc.slice(0, lastPeriod + 1);
  } else if (desc && !desc.endsWith('.')) {
    desc += '.';
  }

  let text = `Story ${index + 1} of ${total}. `;
  text += `From ${source}, tracking ${category} affairs in ${region}. `;
  text += `${title}. `;
  if (desc && desc !== title) {
    text += `${desc} `;
  }
  text += `Full report available on ${source}.`;
  return text;
}

// SMART CONVERSATIONAL RADIO BROADCASTER & CONTINUOUS AUTO-ADVANCE
window.playStoryAtIndex = function(index) {
  if (!('speechSynthesis' in window)) return;

  const activeList = getActiveFeedArticles();
  if (!activeList || !activeList.length) return;

  const safeIdx = Math.max(0, Math.min(index, activeList.length - 1));
  const art = activeList[safeIdx];
  if (!art) return;

  window.speechSynthesis.cancel();
  state.audioState.currentIndex = safeIdx;

  const scriptText = generateHumanBroadcastScript(art, safeIdx, activeList.length);
  state.audioState.currentText = scriptText;

  const utterance = new SpeechSynthesisUtterance(scriptText);
  const voice = getSelectedVoice();
  if (voice) utterance.voice = voice;

  utterance.rate = state.audioState.rate || 0.95;
  utterance.pitch = state.audioState.pitch || 1.0;
  utterance.volume = 1.0;

  utterance.onstart = () => {
    if (audioPlayBtn) audioPlayBtn.textContent = '⏸';
    if (eqContainer) eqContainer.classList.add('active');
    if (audioTitle) audioTitle.textContent = `Story ${safeIdx + 1}/${activeList.length}: ${art.title}`;
    state.audioState.isPlaying = true;
    state.audioState.isPaused = false;

    // Sync modal deck card if modal is open
    if (state.modalState.isOpen) {
      openExecutiveModal(safeIdx);
    }
  };

  utterance.onend = () => {
    state.audioState.isPlaying = false;
    
    // CONTINUOUS HANDS-FREE AUTO-ADVANCE
    if (state.audioState.handsFreeMode && safeIdx + 1 < activeList.length) {
      if (audioTitle) audioTitle.textContent = `Station Transitioning to Story ${safeIdx + 2}...`;
      setTimeout(() => {
        if (state.audioState.handsFreeMode) {
          playStoryAtIndex(safeIdx + 1);
        }
      }, 1200);
    } else {
      if (audioPlayBtn) audioPlayBtn.textContent = '▶';
      if (eqContainer) eqContainer.classList.remove('active');
      if (audioTitle) audioTitle.textContent = 'Station Briefing Complete';
    }
  };

  utterance.onerror = () => {
    if (audioPlayBtn) audioPlayBtn.textContent = '▶';
    if (eqContainer) eqContainer.classList.remove('active');
    state.audioState.isPlaying = false;
  };

  window.speechSynthesis.speak(utterance);
};

// UNIFIED PLAY / PAUSE BUTTON
audioPlayBtn.addEventListener('click', () => {
  if ('speechSynthesis' in window) {
    if (state.audioState.isPlaying) {
      window.speechSynthesis.pause();
      audioPlayBtn.textContent = '▶';
      if (eqContainer) eqContainer.classList.remove('active');
      state.audioState.isPlaying = false;
      state.audioState.isPaused = true;
    } else if (state.audioState.isPaused) {
      window.speechSynthesis.resume();
      audioPlayBtn.textContent = '⏸';
      if (eqContainer) eqContainer.classList.add('active');
      state.audioState.isPlaying = true;
      state.audioState.isPaused = false;
    } else {
      const currentIdx = state.audioState.currentIndex || 0;
      playStoryAtIndex(currentIdx);
    }
  }
});

// ============================================================
// ATOMIC RECALL DOSSIER — ENTERPRISE BOOKMARK ENGINE
// ============================================================

function backfillAtomicDossier() {
  let changed = false;
  state.bookmarks.forEach(id => {
    if (!state.atomicDossier[id]) {
      const art = (state.articles || []).find(a => a.id === id);
      if (art) {
        state.atomicDossier[id] = {
          id: art.id,
          type: 'article',
          title: art.title,
          source: art.source,
          sourceLogo: art.sourceLogo || 'NC',
          link: art.link,
          category: art.category || 'General',
          region: art.region || 'Global',
          savedAt: new Date().toISOString(),
          atomicThesis: (art.annotation && art.annotation.what) ? art.annotation.what : (art.summary || art.title),
          topics: [art.category, art.region].filter(Boolean),
          readTime: art.readTime || '3 min read',
          imageUrl: art.imageUrl || ''
        };
        changed = true;
      } else {
        const pod = (state.podcasts || []).find(p => p.id === id);
        if (pod) {
          state.atomicDossier[id] = {
            id: pod.id,
            type: 'podcast',
            title: pod.title,
            source: pod.podcast,
            sourceLogo: pod.podcastLogo || 'POD',
            link: pod.link,
            category: pod.category || 'Podcast',
            region: 'Global',
            savedAt: new Date().toISOString(),
            atomicThesis: pod.theme || pod.insight || pod.title,
            topics: pod.topics || [pod.category || 'Ideas'],
            guest: pod.guest || '',
            duration: pod.duration || '',
            imageUrl: pod.imageUrl || ''
          };
          changed = true;
        }
      }
    }
  });
  if (changed) {
    localStorage.setItem('nc_atomic_dossier', JSON.stringify(state.atomicDossier));
  }
}

window.toggleBookmark = function(id, e) {
  if (e) e.stopPropagation();
  const index = state.bookmarks.indexOf(id);
  if (index >= 0) {
    state.bookmarks.splice(index, 1);
    delete state.atomicDossier[id];
  } else {
    state.bookmarks.push(id);
    // Construct rich Atomic Snapshot immediately
    const art = (state.articles || []).find(a => a.id === id);
    if (art) {
      state.atomicDossier[id] = {
        id: art.id,
        type: 'article',
        title: art.title,
        source: art.source,
        sourceLogo: art.sourceLogo || 'NC',
        link: art.link,
        category: art.category || 'General',
        region: art.region || 'Global',
        savedAt: new Date().toISOString(),
        atomicThesis: (art.annotation && art.annotation.what) ? art.annotation.what : (art.summary || art.title),
        topics: [art.category, art.region].filter(Boolean),
        readTime: art.readTime || '3 min read',
        imageUrl: art.imageUrl || ''
      };
    } else {
      const pod = (state.podcasts || []).find(p => p.id === id);
      if (pod) {
        state.atomicDossier[id] = {
          id: pod.id,
          type: 'podcast',
          title: pod.title,
          source: pod.podcast,
          sourceLogo: pod.podcastLogo || 'POD',
          link: pod.link,
          category: pod.category || 'Podcast',
          region: 'Global',
          savedAt: new Date().toISOString(),
          atomicThesis: pod.theme || pod.insight || pod.title,
          topics: pod.topics || [pod.category || 'Ideas'],
          guest: pod.guest || '',
          duration: pod.duration || '',
          imageUrl: pod.imageUrl || ''
        };
      }
    }
  }

  localStorage.setItem('nc_bookmarks', JSON.stringify(state.bookmarks));
  localStorage.setItem('nc_atomic_dossier', JSON.stringify(state.atomicDossier));
  updateBookmarkBadge();
  filterAndRender();
  renderSavedList();
  if (state.podcasts && state.podcasts.length > 0) {
    renderThoughtPulse({
      lastUpdated: state.podcastsLastUpdated,
      total: state.podcasts.length,
      episodes: state.podcasts
    });
  }
};

function isBookmarked(id) {
  return state.bookmarks.includes(id);
}

function updateBookmarkBadge() {
  state.bookmarks = state.bookmarks.filter(id => !!id);
  const count = state.bookmarks.length;
  
  if (bookmarkCount) {
    bookmarkCount.textContent = count;
    bookmarkCount.style.display = count > 0 ? 'flex' : 'none';
  }
  
  const savedCountBadge = document.getElementById('savedCountBadge');
  if (savedCountBadge) {
    savedCountBadge.textContent = `${count} ${count === 1 ? 'Signal' : 'Signals'}`;
  }
}

// Search & Filter within Saved Intelligence
window.handleSavedSearch = function(query) {
  state.savedSearchQuery = (query || '').trim().toLowerCase();
  const clearBtn = document.getElementById('clearSavedSearchBtn');
  if (clearBtn) {
    clearBtn.style.display = state.savedSearchQuery ? 'block' : 'none';
  }
  renderSavedList();
};

window.clearSavedSearch = function() {
  state.savedSearchQuery = '';
  const searchInput = document.getElementById('savedSearchInput');
  if (searchInput) searchInput.value = '';
  const clearBtn = document.getElementById('clearSavedSearchBtn');
  if (clearBtn) clearBtn.style.display = 'none';
  renderSavedList();
};

// 1-Click Clean Markdown Exporter
window.exportSavedAsMarkdown = function() {
  backfillAtomicDossier();
  const items = state.bookmarks.map(id => state.atomicDossier[id]).filter(Boolean);
  if (items.length === 0) {
    showToastNotification('No saved signals to export.');
    return;
  }
  
  let md = `# News Colossal — Saved Intelligence Dossier\n*Exported on ${new Date().toLocaleDateString('en-US', { dateStyle: 'full' })}*\n\n`;
  
  const podcasts = items.filter(i => i.type === 'podcast');
  const articles = items.filter(i => i.type !== 'podcast');

  if (podcasts.length > 0) {
    md += `## 🎙️ Podcast Intelligence (${podcasts.length})\n\n`;
    podcasts.forEach(p => {
      md += `### [${p.title}](${p.link})\n`;
      md += `**Source:** ${p.source}${p.guest ? ` • **Guest:** ${p.guest}` : ''} • **Category:** ${p.category}${p.duration ? ` • **Duration:** ${p.duration}` : ''}\n\n`;
      if (p.atomicThesis) md += `> **Atomic Essence:** ${p.atomicThesis}\n\n`;
      if (p.topics && p.topics.length) md += `*Topics:* ${p.topics.map(t => `#${t}`).join(' ')}\n\n`;
      md += `---\n\n`;
    });
  }

  if (articles.length > 0) {
    md += `## 📰 Strategic News & Analysis (${articles.length})\n\n`;
    articles.forEach(a => {
      md += `### [${a.title}](${a.link})\n`;
      md += `**Source:** ${a.source} • **Category:** ${a.category} • **Region:** ${a.region}\n\n`;
      if (a.atomicThesis) md += `> **Atomic Essence:** ${a.atomicThesis}\n\n`;
      if (a.topics && a.topics.length) md += `*Topics:* ${a.topics.map(t => `#${t}`).join(' ')}\n\n`;
      md += `---\n\n`;
    });
  }

  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(md).then(() => {
      showToastNotification(`📋 Copied ${items.length} saved signals as clean Markdown!`);
    }).catch(() => fallbackCopy(md, items.length));
  } else {
    fallbackCopy(md, items.length);
  }

  function fallbackCopy(text, count) {
    const ta = document.createElement('textarea');
    ta.value = text;
    document.body.appendChild(ta);
    ta.select();
    document.execCommand('copy');
    document.body.removeChild(ta);
    showToastNotification(`📋 Copied ${count} saved signals as clean Markdown!`);
  }
};

document.getElementById('bookmarksBtn').addEventListener('click', () => {
  backfillAtomicDossier();
  renderSavedList();
  drawerBackdrop.classList.add('active');
});
drawerCloseBtn.addEventListener('click', () => drawerBackdrop.classList.remove('active'));
drawerBackdrop.addEventListener('click', (e) => {
  if (e.target === drawerBackdrop) drawerBackdrop.classList.remove('active');
});

// INTERACTIVE BOOKMARK REDIRECTION
window.openSavedArticle = function(id) {
  drawerBackdrop.classList.remove('active');
  
  const cardElem = document.querySelector(`.news-card[data-id="${id}"]`);
  if (cardElem) {
    cardElem.scrollIntoView({ behavior: 'smooth', block: 'center' });
    cardElem.style.borderColor = 'var(--accent-cyan)';
    cardElem.style.boxShadow = '0 0 30px var(--accent-glow)';
    setTimeout(() => {
      cardElem.style.borderColor = '';
      cardElem.style.boxShadow = '';
    }, 2000);
    openModal(id);
  } else {
    // If article rotated off active feed, open direct link
    const item = state.atomicDossier[id];
    if (item && item.link) {
      window.open(item.link, '_blank');
    } else {
      openModal(id);
    }
  }
};

window.openSavedPodcast = function(id, link) {
  drawerBackdrop.classList.remove('active');
  
  const cardElem = document.querySelector(`.thought-card[data-id="${id}"]`);
  if (cardElem) {
    cardElem.scrollIntoView({ behavior: 'smooth', block: 'center', inline: 'center' });
    cardElem.style.borderColor = '#a855f7';
    cardElem.style.boxShadow = '0 0 30px rgba(168, 85, 247, 0.6)';
    setTimeout(() => {
      cardElem.style.borderColor = '';
      cardElem.style.boxShadow = '';
    }, 2000);
  } else if (link) {
    window.open(link, '_blank');
  }
};

function renderSavedList() {
  backfillAtomicDossier();
  const rawItems = state.bookmarks.map(id => state.atomicDossier[id]).filter(Boolean);

  // Update counter pill
  const savedCountBadge = document.getElementById('savedCountBadge');
  if (savedCountBadge) {
    savedCountBadge.textContent = `${rawItems.length} ${rawItems.length === 1 ? 'Signal' : 'Signals'}`;
  }

  if (rawItems.length === 0) {
    savedList.innerHTML = `
      <div class="atomic-empty-state">
        <span class="atomic-empty-icon">✦</span>
        <h4 class="atomic-empty-title">No Saved Signals</h4>
        <p class="atomic-empty-desc">Click the ☆ star on any strategic news card or podcast episode to capture its atomic essence.</p>
      </div>
    `;
    return;
  }

  // Filter if search query is active
  let items = rawItems;
  if (state.savedSearchQuery) {
    const q = state.savedSearchQuery;
    items = rawItems.filter(item => {
      const matchTitle = (item.title || '').toLowerCase().includes(q);
      const matchThesis = (item.atomicThesis || '').toLowerCase().includes(q);
      const matchSource = (item.source || '').toLowerCase().includes(q);
      const matchGuest = (item.guest || '').toLowerCase().includes(q);
      const matchTopics = (item.topics || []).some(t => t.toLowerCase().includes(q));
      return matchTitle || matchThesis || matchSource || matchGuest || matchTopics;
    });
  }

  if (items.length === 0 && state.savedSearchQuery) {
    savedList.innerHTML = `
      <div class="atomic-empty-state">
        <span class="atomic-empty-icon">🔍</span>
        <h4 class="atomic-empty-title">No Matching Signals</h4>
        <p class="atomic-empty-desc">No saved intelligence matches "<strong>${escapeHtml(state.savedSearchQuery)}</strong>".</p>
      </div>
    `;
    return;
  }

  savedList.innerHTML = items.map(item => {
    const isPodcast = item.type === 'podcast';
    const typeLabel = isPodcast ? '🎙️ PODCAST' : '📰 STRATEGY';
    const typeClass = isPodcast ? 'podcast' : 'article';
    const cardSignalClass = isPodcast ? 'podcast-signal' : 'article-signal';
    
    // Format saved date
    let dateStr = '';
    if (item.savedAt) {
      const d = new Date(item.savedAt);
      dateStr = d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    }

    const topicsHTML = (item.topics && item.topics.length)
      ? `<div class="atomic-topics-row">${item.topics.map(t => `<span class="atomic-topic-tag">#${escapeHtml(t)}</span>`).join('')}</div>`
      : '';

    const clickAction = isPodcast
      ? `openSavedPodcast('${item.id}', '${escapeJs(item.link)}')`
      : `openSavedArticle('${item.id}')`;

    const ctaText = isPodcast ? 'Watch Episode ↗' : 'Read Full Story ↗';

    return `
      <article class="atomic-recall-card ${cardSignalClass}">
        <div class="atomic-card-header">
          <div class="atomic-source-wrap">
            <span class="atomic-source-logo">${escapeHtml(item.sourceLogo || 'NC')}</span>
            <span class="atomic-source-name">${escapeHtml(item.source)}</span>
          </div>
          <div style="display: flex; align-items: center; gap: 0.4rem;">
            <span class="atomic-type-pill ${typeClass}">${typeLabel}</span>
            ${dateStr ? `<span style="color: var(--text-muted); font-size: 0.65rem;">${dateStr}</span>` : ''}
          </div>
        </div>

        <h4 class="atomic-card-title" onclick="${clickAction}">${escapeHtml(item.title)}</h4>

        <div class="atomic-thesis-box">
          <div class="atomic-thesis-badge">
            <span>✦</span> ATOMIC ESSENCE
          </div>
          <p class="atomic-thesis-text">${escapeHtml(item.atomicThesis)}</p>
        </div>

        ${topicsHTML}

        <div class="atomic-card-footer">
          <button class="atomic-cta-btn" onclick="${clickAction}">
            ${ctaText}
          </button>
          <button class="atomic-remove-btn" onclick="toggleBookmark('${item.id}', event)">
            Remove
          </button>
        </div>
      </article>
    `;
  }).join('');
}

// Ticker
function renderTicker() {
  if (state.articles.length === 0) return;
  const itemsHTML = state.articles.slice(0, 8).map(art => `
    <a href="${art.link}" target="_blank" rel="noopener noreferrer" class="ticker-item">
      <strong>[${art.source}]</strong> ${escapeHtml(art.title)}
    </a>
  `).join(' &bull; ');
  tickerTrack.innerHTML = itemsHTML + ' &bull; ' + itemsHTML;
}

// Skeletons
function renderSkeletons() {
  newsGrid.innerHTML = Array(6).fill(0).map(() => `
    <div class="news-card" style="height: 380px; background: var(--bg-surface-elevated); opacity: 0.5;">
      <div style="height: 180px; background: var(--border-color);"></div>
      <div style="padding: 1rem; display: flex; flex-direction: column; gap: 0.8rem;">
        <div style="height: 14px; width: 40%; background: var(--border-color); border-radius: 4px;"></div>
        <div style="height: 20px; width: 90%; background: var(--border-color); border-radius: 4px;"></div>
        <div style="height: 40px; width: 100%; background: var(--border-color); border-radius: 4px;"></div>
      </div>
    </div>
  `).join('');
}

// INSTANT REAL-TIME REFRESH ICON LISTENER WITH SPINNING ANIMATION & CACHE-BUSTING
function setupEventListeners() {
  navTabs.addEventListener('click', (e) => {
    if (e.target.classList.contains('tab-btn')) {
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      e.target.classList.add('active');
      state.currentCategory = e.target.getAttribute('data-category');
      filterAndRender();
      scrollToContent();
      updateTabIndicator();
    }
  });

  regionSelect.addEventListener('change', (e) => {
    state.currentRegion = e.target.value;
    filterAndRender();
    scrollToContent();
  });

  const searchClearBtn = document.getElementById('searchClearBtn');

  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      state.searchQuery = e.target.value;
      if (searchClearBtn) {
        searchClearBtn.style.display = state.searchQuery.trim().length > 0 ? 'flex' : 'none';
      }
      if (state.searchDebounceTimer) clearTimeout(state.searchDebounceTimer);
      state.searchDebounceTimer = setTimeout(() => {
        filterAndRender();
      }, state.searchQuery.trim().length > 0 ? 550 : 50);
    });
  }

  if (searchClearBtn) {
    searchClearBtn.addEventListener('click', () => {
      searchInput.value = '';
      state.searchQuery = '';
      searchClearBtn.style.display = 'none';
      filterAndRender();
    });
  }

  if (refreshBtn) {
    refreshBtn.addEventListener('click', () => {
      refreshBtn.style.transform = 'rotate(720deg)';
      refreshBtn.style.transition = 'transform 0.8s cubic-bezier(0.16, 1, 0.3, 1)';
      resetAllFiltersAndRefresh(true).then(() => {
        setTimeout(() => {
          refreshBtn.style.transform = 'none';
          refreshBtn.style.transition = 'none';
        }, 850);
      });
    });
  }

  document.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowLeft') {
      if (modalBackdrop.classList.contains('active')) navigateModal(-1);
    }
    if (e.key === 'ArrowRight') {
      if (modalBackdrop.classList.contains('active')) navigateModal(1);
    }
    if (e.key === '?' || (e.shiftKey && e.key === '?')) {
      shortcutModalBackdrop.classList.add('active');
    }
    if (e.key === '/' && document.activeElement !== searchInput) {
      e.preventDefault();
      searchInput.focus();
    }
    if (e.key === 'Escape') {
      closeModal();
      closeShortcutModal();
      closeMonetizeModals();
      drawerBackdrop.classList.remove('active');
    }
  });

  // Battery and CPU optimization: pause hero timer when tab is hidden
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
      if (state.progressInterval) clearInterval(state.progressInterval);
    } else {
      if (state.heroPlaying) startHeroTimer();
    }
  });
}

// SMART RESET ENGINE FOR REFRESH & SEARCH RESET
window.resetFilters = function() {
  state.currentCategory = 'top10';
  state.currentRegion = 'all';
  state.searchQuery = '';
  if (searchInput) searchInput.value = '';
  if (regionSelect) regionSelect.value = 'all';
  const clearBtn = document.getElementById('searchClearBtn');
  if (clearBtn) clearBtn.style.display = 'none';

  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  const top10Btn = document.querySelector('[data-category="top10"]');
  if (top10Btn) top10Btn.classList.add('active');

  filterAndRender();
  updateTabIndicator();
};

window.resetAllFiltersAndRefresh = async function(forceBustCache = true) {
  state.currentCategory = 'top10';
  state.currentRegion = 'all';
  state.searchQuery = '';
  if (searchInput) searchInput.value = '';
  if (regionSelect) regionSelect.value = 'all';
  const clearBtn = document.getElementById('searchClearBtn');
  if (clearBtn) clearBtn.style.display = 'none';

  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  const top10Btn = document.querySelector('[data-category="top10"]');
  if (top10Btn) top10Btn.classList.add('active');

  await loadData(forceBustCache);
};

// NATIVE PULL-TO-REFRESH FOR MOBILE TOUCH SCREENS (iOS & Android)
function setupMobilePullToRefresh() {
  const banner = document.getElementById('pullToRefreshBanner');
  const spinner = document.getElementById('pullRefreshSpinner');
  const textLabel = document.getElementById('pullRefreshText');
  if (!banner) return;

  let startY = 0;
  let currentY = 0;
  let isPulling = false;
  const PULL_THRESHOLD = 75;

  window.addEventListener('touchstart', (e) => {
    if (window.scrollY <= 5 && e.touches.length === 1 && !document.body.classList.contains('modal-open')) {
      startY = e.touches[0].clientY;
      currentY = startY;
      isPulling = true;
    }
  }, { passive: true });

  window.addEventListener('touchmove', (e) => {
    if (!isPulling || window.scrollY > 10 || e.touches.length !== 1) return;
    currentY = e.touches[0].clientY;
    const pullDistance = currentY - startY;

    if (pullDistance > 10) {
      const displayDistance = Math.min(80, pullDistance * 0.45);
      banner.style.transform = `translateY(${displayDistance - 60}px)`;
      banner.style.opacity = `${Math.min(1, displayDistance / 40)}`;

      const rotation = Math.min(360, pullDistance * 3);
      if (spinner) spinner.style.transform = `rotate(${rotation}deg)`;

      if (pullDistance >= PULL_THRESHOLD) {
        if (textLabel) textLabel.textContent = 'Release to reset & refresh news...';
      } else {
        if (textLabel) textLabel.textContent = 'Pull down to refresh...';
      }
    }
  }, { passive: true });

  window.addEventListener('touchend', () => {
    if (!isPulling) return;
    isPulling = false;
    const pullDistance = currentY - startY;

    if (pullDistance >= PULL_THRESHOLD) {
      banner.style.transform = 'translateY(0px)';
      banner.style.opacity = '1';
      if (textLabel) textLabel.textContent = 'Refreshing live feeds & resetting...';
      if (spinner) spinner.classList.add('spinning');

      resetAllFiltersAndRefresh(true).then(() => {
        setTimeout(() => {
          banner.style.transform = 'translateY(-100%)';
          banner.style.opacity = '0';
          if (spinner) spinner.classList.remove('spinning');
        }, 600);
      });
    } else {
      banner.style.transform = 'translateY(-100%)';
      banner.style.opacity = '0';
    }
  }, { passive: true });
}

function escapeHtml(str) {
  if (!str) return '';
  return str.replace(/[&<>"']/g, function(m) {
    return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' }[m];
  });
}

function escapeJs(str) {
  if (!str) return '';
  return str.replace(/'/g, "\\'").replace(/"/g, '\\"');
}

// ==========================================================================
// MONETIZATION MODALS ENGINE (DAILY DIGEST & SUPPORT)
// ==========================================================================
let _monetizeTimeout = null;

document.addEventListener('DOMContentLoaded', () => {
  const newsBtn = document.getElementById('newsletterHeaderBtn');
  const suppBtn = document.getElementById('supportHeaderBtn');

  if (newsBtn) newsBtn.addEventListener('click', openNewsletterModal);
  if (suppBtn) suppBtn.addEventListener('click', openSupportModal);

  // Overlay click-to-close (click on dark background dismisses modal)
  ['newsletterModal', 'supportModal'].forEach(id => {
    const overlay = document.getElementById(id);
    if (overlay) {
      overlay.addEventListener('click', (e) => {
        if (e.target === overlay) closeMonetizeModals();
      });
    }
  });

  // Update subscriber count badge on load
  updateSubCountBadge();
});

function isMonetizeModalOpen() {
  const m1 = document.getElementById('newsletterModal');
  const m2 = document.getElementById('supportModal');
  return (m1 && m1.classList.contains('active')) || (m2 && m2.classList.contains('active'));
}

function openNewsletterModal() {
  const modal = document.getElementById('newsletterModal');
  if (modal) {
    modal.classList.add('active');
    // Focus the email input for accessibility
    const input = document.getElementById('newsletterEmailInput');
    if (input) setTimeout(() => input.focus(), 300);
  }
}

function openSupportModal() {
  const modal = document.getElementById('supportModal');
  if (modal) modal.classList.add('active');
}

function closeMonetizeModals() {
  if (!isMonetizeModalOpen()) return; // Guard: only close if actually open
  const m1 = document.getElementById('newsletterModal');
  const m2 = document.getElementById('supportModal');
  if (m1) m1.classList.remove('active');
  if (m2) m2.classList.remove('active');
  // Cancel any pending timeout
  if (_monetizeTimeout) { clearTimeout(_monetizeTimeout); _monetizeTimeout = null; }
}

async function handleNewsletterSubmit(e) {
  e.preventDefault();
  const input = document.getElementById('newsletterEmailInput');
  const msg = document.getElementById('newsletterMsg');
  const submitBtn = document.querySelector('.monetize-submit-btn');
  if (!input || !input.value) return;

  const email = input.value.trim();
  if (!email || !email.includes('@') || !email.includes('.')) {
    if (msg) {
      msg.className = 'monetize-status-msg';
      msg.style.color = '#ef4444';
      msg.textContent = 'Please enter a valid email address.';
    }
    return;
  }

  // Visual feedback: Subscribing state
  if (msg) {
    msg.className = 'monetize-status-msg';
    msg.style.color = 'var(--accent-cyan)';
    msg.textContent = '✦ Subscribing...';
  }
  if (submitBtn) submitBtn.disabled = true;

  // Local storage caching
  let subs = JSON.parse(localStorage.getItem('nc_newsletter_subscribers') || '[]');
  if (!subs.includes(email)) {
    subs.push(email);
    localStorage.setItem('nc_newsletter_subscribers', JSON.stringify(subs));
  }

  // Detect user timezone
  let userTz = 'UTC';
  try {
    userTz = Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC';
  } catch (_) {}

  // Direct Opt-In to Buttondown via public embed form
  try {
    // Create a hidden iframe to prevent page navigation
    let iframe = document.getElementById('bd-hidden-iframe');
    if (!iframe) {
      iframe = document.createElement('iframe');
      iframe.name = 'bd-hidden-iframe';
      iframe.id = 'bd-hidden-iframe';
      iframe.style.display = 'none';
      document.body.appendChild(iframe);
    }

    // Create a form targeting the iframe
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = 'https://buttondown.com/api/emails/embed-subscribe/0001kashish';
    form.target = 'bd-hidden-iframe';
    
    // Add email input
    const emailInput = document.createElement('input');
    emailInput.type = 'email';
    emailInput.name = 'email';
    emailInput.value = email;
    form.appendChild(emailInput);
    
    document.body.appendChild(form);
    form.submit();
    setTimeout(() => { document.body.removeChild(form); }, 500);

    // Give visual success immediately (optimistic UI)
    if (msg) {
      msg.className = 'monetize-status-msg success';
      msg.style.color = '#10b981';
      msg.textContent = '✦ Subscribed! You will receive daily morning digests directly in your inbox.';
    }
    input.value = '';
    
    _monetizeTimeout = setTimeout(() => {
      closeMonetizeModals();
      if (msg) msg.className = 'monetize-status-msg';
    }, 3000);

  } catch (err) {
    if (msg) {
      msg.className = 'monetize-status-msg success';
      msg.style.color = '#10b981';
      msg.textContent = '✦ Subscribed! Your digest delivery is scheduled.';
    }
  } finally {
    if (submitBtn) submitBtn.disabled = false;
    input.value = '';
    updateSubCountBadge();

    _monetizeTimeout = setTimeout(() => {
      closeMonetizeModals();
      if (msg) { msg.textContent = ''; msg.style.color = ''; }
      _monetizeTimeout = null;
    }, 3000);
  }
}

function updateSubCountBadge() {
  const subs = JSON.parse(localStorage.getItem('nc_newsletter_subscribers') || '[]');
  const badge = document.getElementById('subCountBadge');
  if (badge) {
    if (subs.length > 0) {
      badge.innerHTML = '&#10003;';
      badge.style.display = 'inline-flex';
      badge.title = 'You are subscribed';
    } else {
      badge.style.display = 'none';
    }
  }
}




// ============================================================
// FEATURE: FINITE FEED — "You Are Caught Up" Reading Tracker
// ============================================================
(function initFiniteFeed() {
  const COMPLETION_THRESHOLD = { minCategories: 4, minArticlesPerCat: 2 };
  const readingProgress = { categoriesSeen: {}, completed: false };

  function getSessionKey() {
    return 'nc_reading_' + new Date().toISOString().slice(0, 10);
  }

  function loadProgress() {
    try {
      const saved = sessionStorage.getItem(getSessionKey());
      if (saved) {
        const parsed = JSON.parse(saved);
        readingProgress.categoriesSeen = parsed.categoriesSeen || {};
        readingProgress.completed = parsed.completed || false;
      }
    } catch (e) {}
  }

  function saveProgress() {
    try {
      sessionStorage.setItem(getSessionKey(), JSON.stringify(readingProgress));
    } catch (e) {}
  }

  function updateProgressRing() {
    const ring = document.getElementById('logoRingFill');
    if (!ring) return;
    
    const allCats = ['World', 'Tech', 'National', 'Business'];
    let catsCovered = 0;
    for (const cat of allCats) {
      if ((readingProgress.categoriesSeen[cat] || 0) >= COMPLETION_THRESHOLD.minArticlesPerCat) {
        catsCovered++;
      }
    }
    
    const progress = Math.min(catsCovered / COMPLETION_THRESHOLD.minCategories, 1);
    const circumference = 131.95;
    ring.style.strokeDashoffset = circumference * (1 - progress);
    
    const wrap = ring.closest('.logo-ring-wrap');
    if (progress >= 1 && !readingProgress.completed) {
      readingProgress.completed = true;
      saveProgress();
      if (wrap) wrap.classList.add('caught-up');
      showCaughtUpToast();
    }
  }

  function showCaughtUpToast() {
    let toast = document.querySelector('.caught-up-toast');
    if (!toast) {
      toast = document.createElement('div');
      toast.className = 'caught-up-toast';
      toast.innerHTML = '<h4>\u2728 You\u2019re Caught Up</h4><p>You\u2019ve seen today\u2019s essential stories across all major categories. The world can wait \u2014 go live your day.</p>';
      document.body.appendChild(toast);
    }
    setTimeout(() => toast.classList.add('visible'), 100);
    setTimeout(() => toast.classList.remove('visible'), 7000);
  }

  function trackCardView(article) {
    if (!article || !article.category || readingProgress.completed) return;
    const cat = article.category;
    readingProgress.categoriesSeen[cat] = (readingProgress.categoriesSeen[cat] || 0) + 1;
    saveProgress();
    updateProgressRing();
  }

  // Observe card visibility
  loadProgress();
  
  const cardObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const cardId = entry.target.getAttribute('data-article-id');
        if (cardId && state.articles) {
          const art = state.articles.find(a => a.id === cardId);
          if (art) trackCardView(art);
        }
        cardObserver.unobserve(entry.target);
      }
    });
  }, { threshold: 0.5 });

  // Re-observe cards whenever grid renders
  const origFilterAndRender = window.filterAndRender || filterAndRender;
  const patchedFilterAndRender = function() {
    origFilterAndRender.apply(this, arguments);
    setTimeout(() => {
      document.querySelectorAll('.news-card[data-article-id]').forEach(card => {
        cardObserver.observe(card);
      });
      updateProgressRing();
    }, 200);
  };
  // Patch filterAndRender globally
  if (typeof filterAndRender === 'function') {
    const _origFAR = filterAndRender;
    filterAndRender = function() {
      _origFAR.apply(this, arguments);
      setTimeout(() => {
        document.querySelectorAll('.news-card[data-article-id]').forEach(card => {
          cardObserver.observe(card);
        });
        updateProgressRing();
      }, 200);
    };
  }

  // Also track tab clicks
  document.querySelectorAll('.nav-tab').forEach(tab => {
    tab.addEventListener('click', () => {
      setTimeout(updateProgressRing, 500);
    });
  });

  // Initial render
  setTimeout(updateProgressRing, 1000);
})();


// ============================================================
// FEATURE: STORY DNA — Lineage Timeline in Deck Modal
// ============================================================
window.renderStoryDNA = function(article) {
  if (!article || !article.storyCluster || article.storyCluster.size < 2) return '';
  
  const cluster = article.storyCluster;
  const sources = cluster.sources || [];
  
  let nodesHTML = sources.map((s, i) => {
    const isFirst = i === 0;
    const truncTitle = s.title.length > 60 ? s.title.substring(0, 57) + '...' : s.title;
    return '<div class="dna-node">' +
      '<div class="dna-dot"></div>' +
      (isFirst ? '<div class="dna-badge-first">Broke First</div>' : '') +
      '<div class="dna-source">' + escapeHtml(s.source) + '</div>' +
      '<div class="dna-headline">' + escapeHtml(truncTitle) + '</div>' +
    '</div>';
  }).join('');
  
  return '<div class="story-dna-section">' +
    '<div class="story-dna-title">' +
      '<span>\uD83E\uDDEC</span> Story DNA \u2014 ' + cluster.size + ' sources covering this event' +
    '</div>' +
    '<div class="dna-timeline">' + nodesHTML + '</div>' +
  '</div>';
};


// ============================================================
// FEATURE: CROSS-REGIONAL PAIRING — Split-Screen Cards
// ============================================================
window.createPairedCardHTML = function(article) {
  if (!article || !article.pairedStory || !article.perspectives || article.perspectives.length < 2) return '';
  
  const p = article.perspectives;
  const REGION_EMOJI = {
    'Global': '\uD83C\uDF0D', 'Asia-Pacific': '\uD83C\uDF0F', 'Europe': '\uD83C\uDF0D',
    'Middle East': '\uD83C\uDF0D', 'North America': '\uD83C\uDF0E', 'India': '\uD83C\uDDEE\uD83C\uDDF3'
  };
  
  let perspectivesHTML = '';
  for (let i = 0; i < Math.min(p.length, 2); i++) {
    const persp = p[i];
    const emoji = REGION_EMOJI[persp.region] || '\uD83C\uDF10';
    perspectivesHTML += '<div class="paired-perspective" onclick="openModal(\'' + escapeHtml(article.id) + '\')">' +
      '<div class="region-flag">' + emoji + ' ' + escapeHtml(persp.region) + '</div>' +
      '<div class="source-name">' + escapeHtml(persp.source) + '</div>' +
      '<div class="perspective-title">' + escapeHtml(persp.title) + '</div>' +
    '</div>';
  }
  
  return '<div class="paired-story-card" data-article-id="' + article.id + '">' +
    '<div class="paired-story-badge">\uD83C\uDF10 Same Event, Different Worlds</div>' +
    '<div class="paired-perspectives">' + perspectivesHTML + '</div>' +
  '</div>';
};


/* ============================================================
   THOUGHT PULSE — Podcast Intelligence Renderer
   ============================================================ */
(function initThoughtPulse() {
  fetch('data/podcasts.json')
    .then(r => r.ok ? r.json() : Promise.reject('No podcast data'))
    .then(data => {
      if (!data.episodes || data.episodes.length === 0) return;
      state.podcasts = data.episodes;
      state.podcastsLastUpdated = data.lastUpdated;
      backfillAtomicDossier();
      renderThoughtPulse(data);
      updateBookmarkBadge();
    })
    .catch(() => { /* Silently skip if no podcast data */ });
})();

function renderThoughtPulse(data) {
  const section = document.getElementById('thoughtPulseSection');
  const carousel = document.getElementById('thoughtPulseCarousel');
  const syncLabel = document.getElementById('podcastSyncLabel');
  if (!section || !carousel) return;

  // Show the section
  section.style.display = 'block';

  // Update sync label
  if (data.lastUpdated && syncLabel) {
    const d = new Date(data.lastUpdated);
    syncLabel.textContent = `${data.total} episodes · Updated ${d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}`;
  }

  // Render cards
  carousel.innerHTML = data.episodes.map(ep => {
    const isFlagship = ep.tier === 'flagship';
    const saved = isBookmarked(ep.id);
    const guestLabel = ep.guest ? `<span style="font-weight:600;color:var(--text-primary);">${escapeHtml(ep.guest)}</span> · ` : '';
    const topicsHTML = (ep.topics && ep.topics.length)
      ? `<div class="thought-card-topics">${ep.topics.map(t => `<span class="thought-topic-pill">#${escapeHtml(t)}</span>`).join('')}</div>`
      : '';
    const themeHTML = ep.theme
      ? `<div class="thought-card-theme-box"><span class="thought-theme-label">Dominant Theme</span><p class="thought-card-theme">${escapeHtml(ep.theme)}</p></div>`
      : (ep.insight ? `<p class="thought-card-insight">“${escapeHtml(ep.insight)}”</p>` : '');

    return `
      <article class="thought-card ${isFlagship ? 'flagship' : ''}" data-id="${ep.id}" onclick="window.open('${escapeJs(ep.link)}','_blank')">
        <div class="thought-card-thumb-wrap">
          <img class="thought-card-thumb" src="${ep.imageUrl}" alt="${escapeHtml(ep.title)}" loading="lazy"
               onerror="this.src='https://i.ytimg.com/vi/${ep.id.replace('tp_','')}/hqdefault.jpg'">
          ${ep.duration ? `<span class="thought-card-duration">${escapeHtml(ep.duration)}</span>` : ''}
          ${isFlagship ? '<span class="thought-card-tier-badge">Featured</span>' : ''}
          <button class="thought-bookmark-btn ${saved ? 'saved' : ''}" onclick="toggleBookmark('${ep.id}', event)" title="${saved ? 'Remove Bookmark' : 'Bookmark Podcast'}" aria-label="Bookmark Podcast">
            ${saved ? '★' : '☆'}
          </button>
        </div>
        <div class="thought-card-body">
          <div class="thought-card-source">
            <div class="thought-card-logo">${escapeHtml(ep.podcastLogo)}</div>
            <span class="thought-card-podcast-name">${escapeHtml(ep.podcast)}</span>
          </div>
          <h3 class="thought-card-title">${escapeHtml(ep.title)}</h3>
          ${themeHTML}
          ${topicsHTML}
          <div class="thought-card-meta">
            <span class="thought-card-category">${escapeHtml(ep.category)}</span>
            <span>${guestLabel}${escapeHtml(ep.pubDate || '')}</span>
          </div>
        </div>
      </article>
    `;
  }).join('');
}
