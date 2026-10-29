// News Colossal Application Engine — Real-Time Live Cache-Busting Refresh Engine

const state = {
  articles: [],
  filteredArticles: [],
  podcasts: [],
  podcastsLastUpdated: null,
  currentCategory: 'top10',
  currentRegion: 'all',
  densityMode: localStorage.getItem('news_colossal_density') || localStorage.getItem('nc_density_mode') || 'digest',
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
  },
  
  // Executive Focus Session State (R5)
  focusSession: {
    active: false,
    isPaused: false,
    totalSeconds: 600,
    remainingSeconds: 600,
    timerInterval: null,
    docket: [],
    readIds: new Set(),
    startTime: null,
    allRead: false
  },

  // Knowledge Constellation Graph State (R7)
  constellation: {
    modalOpen: false,
    activeTypeFilter: 'all',
    simulation: null,
    selectedNode: null,
    hoveredNode: null
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

// ==========================================================================
// R1: STORY METABOLISM TRACKER (COVERAGE SPARKLINES SVG)
// ==========================================================================
/**
 * Computes coverage metabolism trajectory and velocity classification.
 * Uses scores.velocity, pubDate, and cluster size to generate pure SVG curves.
 * @param {Object} art - Article data object from news.json
 * @returns {Object} { status, label, color, pathD, areaD, lastX, lastY, tooltip, vel, clusterSize, points }
 */
function computeStoryMetabolism(art) {
  if (!art) art = {};
  const vel = (art.scores && typeof art.scores.velocity === 'number') ? art.scores.velocity : 0.25;
  const clusterSize = (art.storyCluster && typeof art.storyCluster.size === 'number')
    ? art.storyCluster.size
    : ((art.perspectives && art.perspectives.length)
        ? art.perspectives.length
        : (art.duplicate_count ? art.duplicate_count + 1 : 1));

  const pubTime = art.pubDate ? new Date(art.pubDate).getTime() : Date.now();
  const hoursAgo = Math.max(0, (Date.now() - pubTime) / (1000 * 60 * 60));

  let status = 'stabilizing';
  let label = 'Stabilizing';
  let color = '#94a3b8'; // Slate / Muted
  let tooltip = `Metabolism: Stabilizing (${Math.round(vel * 100)}% velocity) • Steady reporting`;

  if (vel >= 0.45 || (vel >= 0.35 && clusterSize >= 2) || (vel >= 0.30 && hoursAgo <= 6)) {
    status = 'accelerating';
    label = 'Accelerating';
    color = '#10b981'; // Emerald Green
    tooltip = `Metabolism: Accelerating (${Math.round(vel * 100)}% velocity) • ${clusterSize} sources surging • High velocity momentum`;
  } else if (vel >= 0.25 || clusterSize >= 2 || (hoursAgo <= 18 && vel >= 0.20)) {
    status = 'peak-spread';
    label = 'Peak Spread';
    color = '#f59e0b'; // Amber Gold
    tooltip = `Metabolism: Peak Spread • Maximum syndication across ${clusterSize} outlets (${Math.round(vel * 100)}% velocity)`;
  }

  // 7 Trajectory coordinate steps across 24h timeline (width = 56, height = 18)
  const xCoords = [0, 9, 18, 28, 37, 47, 56];
  const seed = (art.id || '').split('').reduce((acc, c) => acc + c.charCodeAt(0), 0) % 5;
  let yCoords = [];

  if (status === 'accelerating') {
    // Convex exponential surge: starts low (y=15), surges up to y=3
    yCoords = [
      15,
      14 - (seed % 2),
      12 - Math.round(vel * 4),
      9 - Math.round(vel * 5),
      6 - (seed % 2),
      4,
      3
    ];
  } else if (status === 'peak-spread') {
    // Bell / plateau curve: rises in middle (y=4), plateaus or slight dip
    yCoords = [
      14,
      10 - (seed % 2),
      5,
      4,
      5 + (seed % 2),
      6,
      7
    ];
  } else {
    // Stabilizing / decaying curve: peaked earlier, leveling off to lower baseline
    yCoords = [
      7 + (seed % 2),
      4,
      7,
      10,
      12,
      13 + (seed % 2),
      14
    ];
  }

  // Construct smooth Bezier curve: M x0,y0 C cx0,cy0 cx1,cy1 x1,y1 ...
  let pathD = `M ${xCoords[0]},${yCoords[0]}`;
  for (let i = 0; i < xCoords.length - 1; i++) {
    const x0 = xCoords[i];
    const y0 = yCoords[i];
    const x1 = xCoords[i + 1];
    const y1 = yCoords[i + 1];
    const mx = ((x0 + x1) / 2).toFixed(1);
    pathD += ` C ${mx},${y0} ${mx},${y1} ${x1},${y1}`;
  }

  const areaD = `${pathD} L 56,18 L 0,18 Z`;
  const lastX = xCoords[xCoords.length - 1];
  const lastY = yCoords[yCoords.length - 1];

  return {
    status,
    label,
    color,
    pathD,
    areaD,
    lastX,
    lastY,
    tooltip,
    vel,
    clusterSize,
    hoursAgo,
    points: xCoords.map((x, i) => ({ x, y: yCoords[i] }))
  };
}

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
  setupPWAOfflineVault();
  setupDensityController();
  initNarrativeMemory();
  setupFocusSession();
  setupKnowledgeConstellation();
  window.addEventListener('resize', updateTabIndicator);
});

// PROGRESSIVE WEB APP & OFFLINE NEWS VAULT (R6)
function setupPWAOfflineVault() {
  const pwaBtn = document.getElementById('pwaVaultIndicatorBtn');
  const pwaLabel = document.getElementById('pwaVaultLabel');
  const pwaDot = document.getElementById('pwaVaultDot');
  const pwaBadge = document.getElementById('pwaInstallBadge');

  let deferredInstallPrompt = null;

  // Intercept beforeinstallprompt for native app installation
  window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredInstallPrompt = e;
    if (pwaBadge) pwaBadge.style.display = 'inline-block';
    if (pwaLabel) pwaLabel.textContent = 'Install News App';
  });

  // Handle post-installation cleanup
  window.addEventListener('appinstalled', () => {
    deferredInstallPrompt = null;
    if (pwaBadge) pwaBadge.style.display = 'none';
    if (pwaLabel) pwaLabel.textContent = 'Offline Vault Ready';
    if (typeof showToastNotification === 'function') {
      showToastNotification('✦ News Colossal installed successfully to your device!');
    }
  });

  // Handle Quick Tools click
  if (pwaBtn) {
    pwaBtn.addEventListener('click', async (e) => {
      e.stopPropagation();
      if (deferredInstallPrompt) {
        deferredInstallPrompt.prompt();
        const choice = await deferredInstallPrompt.userChoice;
        if (choice && choice.outcome === 'accepted') {
          deferredInstallPrompt = null;
          if (pwaBadge) pwaBadge.style.display = 'none';
          if (pwaLabel) pwaLabel.textContent = 'Offline Vault Ready';
        }
      } else {
        const isOffline = !navigator.onLine;
        const count = state && state.articles ? state.articles.length : 0;
        const msg = isOffline
          ? `⚡ Offline Vault Active: ${count} cached stories available without network.`
          : `✦ Offline News Vault: ${count} stories & app shell cached for 100% offline reading.`;
        if (typeof showToastNotification === 'function') {
          showToastNotification(msg);
        } else {
          alert(msg);
        }
      }
    });
  }

  // Live network state listeners
  function updateNetworkStatus() {
    const isOnline = navigator.onLine;
    if (pwaDot) {
      pwaDot.className = isOnline ? 'pwa-vault-dot' : 'pwa-vault-dot offline';
    }
    if (pwaLabel && !deferredInstallPrompt) {
      pwaLabel.textContent = isOnline ? 'Offline Vault Ready' : 'Vault Active (Offline)';
    }
  }

  window.addEventListener('online', updateNetworkStatus);
  window.addEventListener('offline', updateNetworkStatus);
  updateNetworkStatus();

  // Guarded Service Worker registration (HTTP/HTTPS only; silent zero-error bypass on file://)
  if ('serviceWorker' in navigator && (window.location.protocol.startsWith('http') || window.location.hostname === 'localhost')) {
    window.addEventListener('load', () => {
      navigator.serviceWorker.register('./sw.js')
        .then((reg) => {
          console.log('[PWA] ServiceWorker registered with scope:', reg.scope);
        })
        .catch((err) => {
          console.warn('[PWA] ServiceWorker registration failed:', err);
        });
    });
  }
}

// ==========================================================================
// R3: COGNITIVE LOAD THERMOSTAT (ADAPTIVE DENSITY CONTROLLER)
// ==========================================================================
function setupDensityController() {
  const toggleGroup = document.getElementById('densityToggleGroup');
  const scanBtn = document.getElementById('densityScanBtn');
  const digestBtn = document.getElementById('densityDigestBtn');
  const deepBtn = document.getElementById('densityDeepBtn');

  const buttons = [
    { btn: scanBtn, mode: 'scan' },
    { btn: digestBtn, mode: 'digest' },
    { btn: deepBtn, mode: 'deep' }
  ];

  buttons.forEach(({ btn, mode }) => {
    if (btn) {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        setDensity(mode);
      });
    }
  });

  // Keyboard accessibility across the segmented radio group (ArrowLeft / ArrowRight / Home / End)
  if (toggleGroup) {
    toggleGroup.addEventListener('keydown', (e) => {
      const currentMode = state.densityMode || 'digest';
      const modes = ['scan', 'digest', 'deep'];
      const currIdx = modes.indexOf(currentMode);
      if (currIdx === -1) return;

      if (e.key === 'ArrowRight' || e.key === 'ArrowDown') {
        e.preventDefault();
        const nextMode = modes[(currIdx + 1) % modes.length];
        setDensity(nextMode);
        const nextBtn = document.getElementById(`density${nextMode.charAt(0).toUpperCase() + nextMode.slice(1)}Btn`);
        if (nextBtn) nextBtn.focus();
      } else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
        e.preventDefault();
        const prevMode = modes[(currIdx - 1 + modes.length) % modes.length];
        setDensity(prevMode);
        const prevBtn = document.getElementById(`density${prevMode.charAt(0).toUpperCase() + prevMode.slice(1)}Btn`);
        if (prevBtn) prevBtn.focus();
      } else if (e.key === 'Home') {
        e.preventDefault();
        setDensity('scan');
        const scanBtn = (buttons && buttons[0] && buttons[0].btn) || document.getElementById('densityScanBtn');
        if (scanBtn) scanBtn.focus();
      } else if (e.key === 'End') {
        e.preventDefault();
        setDensity('deep');
        const deepBtn = (buttons && buttons[buttons.length - 1] && buttons[buttons.length - 1].btn) || document.getElementById('densityDeepBtn');
        if (deepBtn) deepBtn.focus();
      }
    });
  }

  // Restore saved preference (defaults to 'digest')
  const savedDensity = localStorage.getItem('news_colossal_density') || localStorage.getItem('nc_density_mode') || 'digest';
  setDensity(savedDensity);
}

function setDensity(mode) {
  const validModes = ['scan', 'digest', 'deep'];
  if (!validModes.includes(mode)) {
    mode = 'digest';
  }

  state.densityMode = mode;
  try {
    localStorage.setItem('news_colossal_density', mode);
    localStorage.setItem('nc_density_mode', mode);
  } catch (err) {
    // Non-fatal fallback for strict sandbox environments
  }

  const grid = document.getElementById('newsGrid') || newsGrid;
  if (grid) {
    grid.classList.remove('density-scan', 'density-digest', 'density-deep');
    grid.classList.add(`density-${mode}`);
  }

  const scanBtn = document.getElementById('densityScanBtn');
  const digestBtn = document.getElementById('densityDigestBtn');
  const deepBtn = document.getElementById('densityDeepBtn');

  [
    { btn: scanBtn, m: 'scan' },
    { btn: digestBtn, m: 'digest' },
    { btn: deepBtn, m: 'deep' }
  ].forEach(({ btn, m }) => {
    if (btn) {
      const isActive = (m === mode);
      btn.classList.toggle('active', isActive);
      btn.setAttribute('aria-checked', isActive ? 'true' : 'false');
      btn.setAttribute('tabindex', isActive ? '0' : '-1');
    }
  });
}

function renderDeepDivePanelContent(art) {
  if (!art) return '';
  let html = '';

  // 1. Extracted Entities
  const ent = art.entities || {};
  const countries = (ent.countries || []).map(c => typeof c === 'string' ? c : (c.name || c.code)).filter(Boolean);
  const leaders = (ent.leaders || []).map(l => typeof l === 'string' ? l : l.name).filter(Boolean);
  const orgs = (ent.organizations || []).map(o => typeof o === 'string' ? o : o.name).filter(Boolean);
  const companies = (ent.companies || []).map(co => typeof co === 'string' ? co : co.name).filter(Boolean);

  const actors = art.primary_actors || (ent.primary_actors) || null;
  const actorTags = [];
  if (actors) {
    if (actors.active_agent) {
      actorTags.push(`<span class="deep-tag leader" title="Active Agent">🎯 ${escapeHtml(actors.active_agent)}</span>`);
    }
    if (Array.isArray(actors.collective_factions)) {
      actors.collective_factions.forEach(f => {
        const label = f.canonical_label || f.matched_text;
        if (label) actorTags.push(`<span class="deep-tag org" title="Collective Faction">👥 ${escapeHtml(label)}</span>`);
      });
    }
  }

  const allTags = [
    ...actorTags,
    ...countries.map(c => `<span class="deep-tag country" title="Nation">🌐 ${escapeHtml(c)}</span>`),
    ...leaders.map(l => `<span class="deep-tag leader" title="Leader">👤 ${escapeHtml(l)}</span>`),
    ...orgs.map(o => `<span class="deep-tag org" title="Organization">🏛️ ${escapeHtml(o)}</span>`),
    ...companies.map(co => `<span class="deep-tag company" title="Company">🏢 ${escapeHtml(co)}</span>`)
  ];

  if (allTags.length > 0) {
    html += `
      <div class="deep-dive-row">
        <span class="deep-dive-label">Key Entities:</span>
        <div class="deep-dive-tags">${allTags.slice(0, 6).join('')}</div>
      </div>
    `;
  }

  // 2. Cognitive Domain Matrix — Honest nulls without synthetic fallbacks
  const score = typeof art.importance_score === 'number'
    ? art.importance_score.toFixed(1)
    : ((art.scores && typeof art.scores.composite === 'number') ? (art.scores.composite * 10).toFixed(1) : null);
  const vel = (art.scores && typeof art.scores.velocity === 'number') ? art.scores.velocity.toFixed(2) : null;
  const rarity = (art.scores && typeof art.scores.rarity === 'number') ? `${Math.round(art.scores.rarity * 100)}%` : null;
  const region = art.region || null;

  let matrixPills = '';
  if (score !== null) matrixPills += `<span class="matrix-pill" title="Algorithmic Importance Score">✦ Signal: ${score}/10</span>`;
  if (vel !== null) matrixPills += `<span class="matrix-pill" title="Coverage Velocity Index">⚡ Velocity: ${vel}</span>`;
  if (rarity !== null) matrixPills += `<span class="matrix-pill" title="Information Rarity">💎 Rarity: ${rarity}</span>`;
  if (region) matrixPills += `<span class="matrix-pill" title="Geographic Focus">🌍 ${escapeHtml(region)}</span>`;

  if (matrixPills) {
    html += `
      <div class="deep-dive-matrix">
        ${matrixPills}
      </div>
    `;
  }

  // 3. Resonance & Arc Pills
  let resonanceBadges = '';
  if (art.resonant_podcast) {
    const pTitle = art.resonant_podcast.title || art.resonant_podcast.podcast || 'Podcast';
    resonanceBadges += `<span class="resonance-pill podcast-pill" title="Related Podcast Episode">🎙️ Podcast: ${escapeHtml(pTitle)}</span>`;
  }
  if (art.narrative_arc && art.narrative_arc.arc_id) {
    const arcTitle = art.narrative_arc.arc_title || art.title;
    const day = art.narrative_arc.day_number || 1;
    resonanceBadges += `<span class="resonance-pill arc-pill" title="Developing Narrative Arc">📅 Chapter ${day} &bull; ${escapeHtml(arcTitle)}</span>`;
  }
  if (resonanceBadges) {
    html += `<div class="deep-dive-resonance">${resonanceBadges}</div>`;
  }

  // 4. Provenance & Wire Cross-Check Links
  if (art.relatedSources && art.relatedSources.length > 0) {
    const srcLinks = art.relatedSources.map(s => `
      <a href="${escapeHtml(s.url)}" target="_blank" rel="noopener noreferrer" class="provenance-link" onclick="event.stopPropagation()" title="Cross-verify with ${escapeHtml(s.name)}">
        ${escapeHtml(s.name)} ↗
      </a>
    `).join('');
    html += `
      <div class="deep-dive-provenance">
        <span class="deep-dive-label">Wire Cross-Check:</span>
        <div class="provenance-links">${srcLinks}</div>
      </div>
    `;
  }

  return html;
}

// Global interface bindings
window.setupDensityController = setupDensityController;
window.renderDensityController = setupDensityController;
window.setDensity = setDensity;
window.computeStoryMetabolism = computeStoryMetabolism;
window.renderDeepDivePanelContent = renderDeepDivePanelContent;

// ==========================================================================
// R2: PERSPECTIVE PRISM (MULTI-SOURCE SPECTRUM & CONTRARIAN SIGNALS)
// ==========================================================================

const REGION_ORIGIN_MAP = {
  'North America': { primary: '#10b981', glow: 'rgba(16, 185, 129, 0.35)', emoji: '🌎' },
  'Europe':        { primary: '#0284c7', glow: 'rgba(2, 132, 199, 0.35)',  emoji: '🇪🇺' },
  'Asia-Pacific':  { primary: '#a855f7', glow: 'rgba(168, 85, 247, 0.35)', emoji: '🌏' },
  'Middle East':   { primary: '#f43f5e', glow: 'rgba(244, 63, 94, 0.35)',  emoji: '🌍' },
  'India':         { primary: '#f59e0b', glow: 'rgba(245, 158, 11, 0.35)', emoji: '🇮🇳' },
  'Global':        { primary: '#00f2fe', glow: 'rgba(0, 242, 254, 0.35)',  emoji: '🌐' }
};

/**
 * Resolves a publisher and optional explicit region to one of the 6 canonical geopolitical origins.
 * @param {string} sourceName - Publisher name
 * @param {string} [explicitRegion] - Optional region tag from article/feed
 * @returns {string} One of: 'North America', 'Europe', 'Asia-Pacific', 'Middle East', 'India', 'Global'
 */
function getPublisherOrigin(sourceName, explicitRegion) {
  if (explicitRegion && explicitRegion !== 'all' && REGION_ORIGIN_MAP[explicitRegion]) {
    return explicitRegion;
  }
  const s = (sourceName || '').toLowerCase();
  if (s.includes('asia') || s.includes('scmp') || s.includes('kyodo') || s.includes('nikkei') || s.includes('strait') || s.includes('xinhua') || s.includes('asahi') || s.includes('yomiuri') || s.includes('korea') || s.includes('japan times')) return 'Asia-Pacific';
  if (s.includes('europe') || s.includes('france') || s.includes('dw') || s.includes('guardian') || s.includes('spiegel') || s.includes('telegraph') || s.includes('le monde') || s.includes('ft') || s.includes('financial times') || s.includes('el pais') || s.includes('reuters') || s.includes('bbc')) return 'Europe';
  if (s.includes('mideast') || s.includes('middle east') || s.includes('al jazeera') || s.includes('haaretz') || s.includes('arab news') || s.includes('jerusalem') || s.includes('gulf')) return 'Middle East';
  if (s.includes('hindu') || s.includes('hindustan') || s.includes('indian express') || s.includes('ndtv') || s.includes('times of india') || s.includes('livemint') || s.includes('economic times') || s.includes('ani') || s.includes('the wire')) return 'India';
  if (s.includes('nyt') || s.includes('new york times') || s.includes('verge') || s.includes('techcrunch') || s.includes('npr') || s.includes('washington post') || s.includes('wsj') || s.includes('wall street journal') || s.includes('bloomberg') || s.includes('cnn') || s.includes('ap news') || s.includes('associated press') || s.includes('cnbc') || s.includes('politico') || s.includes('wired')) return 'North America';
  return 'Global';
}

function extractSpectrumItems(art) {
  if (!art) return [];
  const items = [];
  const seenSources = new Set();

  if (Array.isArray(art.perspectives) && art.perspectives.length > 0) {
    art.perspectives.forEach(p => {
      const src = p.source || '';
      if (!seenSources.has(src.toLowerCase())) {
        seenSources.add(src.toLowerCase());
        const region = getPublisherOrigin(p.source, p.region);
        items.push({
          source: p.source,
          sourceLogo: p.sourceLogo || (p.source ? p.source.slice(0, 3).toUpperCase() : 'SRC'),
          region: region,
          title: p.title || art.title,
          annotation: p.annotation || null,
          isPrimary: src.toLowerCase() === (art.source || '').toLowerCase()
        });
      }
    });
  }

  if (art.storyCluster && Array.isArray(art.storyCluster.sources) && art.storyCluster.sources.length > 0) {
    art.storyCluster.sources.forEach(s => {
      const src = s.source || '';
      if (!seenSources.has(src.toLowerCase())) {
        seenSources.add(src.toLowerCase());
        const region = getPublisherOrigin(s.source, s.region);
        items.push({
          source: s.source,
          sourceLogo: (s.source || '').slice(0, 3).toUpperCase() || 'SRC',
          region: region,
          title: s.title || art.title,
          pubDate: s.pubDate || null,
          isPrimary: src.toLowerCase() === (art.source || '').toLowerCase()
        });
      }
    });
  }

  if (art.source && !seenSources.has(art.source.toLowerCase())) {
    seenSources.add(art.source.toLowerCase());
    items.unshift({
      source: art.source,
      sourceLogo: art.sourceLogo || art.source.slice(0, 3).toUpperCase(),
      region: getPublisherOrigin(art.source, art.region),
      title: art.title,
      annotation: art.annotation || null,
      isPrimary: true
    });
  }

  if (items.length === 0 && art.source) {
    items.push({
      source: art.source,
      sourceLogo: art.sourceLogo || 'SRC',
      region: getPublisherOrigin(art.source, art.region),
      title: art.title,
      annotation: art.annotation || null,
      isPrimary: true
    });
  }

  return items;
}

function hasPerspectivePrism(art) {
  if (!art) return false;
  if (art.perspectives && art.perspectives.length >= 1) return true;
  if (art.storyCluster && ((art.storyCluster.sources && art.storyCluster.sources.length >= 1) || (typeof art.storyCluster.size === 'number' && art.storyCluster.size >= 1))) return true;
  if (art.meta && (art.meta.is_contrarian || art.meta.is_exclusive || (art.meta.sentiment_divergence && art.meta.sentiment_divergence > 0.4))) return true;
  return false;
}

/**
 * Renders the full interactive Perspective Prism component for reader modal.
 * @param {Object} art - Article data object
 * @returns {string} HTML markup string
 */
function renderPerspectivePrism(art) {
  if (!art) return '';
  const spectrumItems = extractSpectrumItems(art);
  if (!spectrumItems || spectrumItems.length === 0) return '';

  const isContrarian = !!(art.meta && art.meta.is_contrarian);
  const isExclusive = !!(art.meta && art.meta.is_exclusive);
  const divergence = (art.meta && typeof art.meta.sentiment_divergence === 'number')
    ? Math.round(art.meta.sentiment_divergence * 100)
    : ((art.scores && typeof art.scores.rarity === 'number') ? Math.round(art.scores.rarity * 100) : 50);
  const exclusiveSignal = (art.meta && art.meta.exclusive_signal) || (art.source ? `Single-Outlet Exclusivity (${art.source})` : 'Single-Outlet Exclusivity');

  const originCounts = {};
  spectrumItems.forEach(item => {
    originCounts[item.region] = (originCounts[item.region] || 0) + 1;
  });
  const uniqueOrigins = Object.keys(originCounts);
  const totalItems = spectrumItems.length;

  const barSegmentsHTML = uniqueOrigins.map(region => {
    const count = originCounts[region];
    const pct = ((count / totalItems) * 100).toFixed(1);
    const colorInfo = REGION_ORIGIN_MAP[region] || REGION_ORIGIN_MAP['Global'];
    return `<div class="prism-spectrum-segment" style="width: ${pct}%; background: ${colorInfo.primary}; box-shadow: 0 0 10px ${colorInfo.glow};" title="${escapeHtml(region)}: ${count} of ${totalItems} sources (${pct}%)" aria-label="${escapeHtml(region)} ${pct}%"></div>`;
  }).join('');

  const originChipsHTML = uniqueOrigins.map(region => {
    const colorInfo = REGION_ORIGIN_MAP[region] || REGION_ORIGIN_MAP['Global'];
    const count = originCounts[region];
    return `<span class="prism-origin-chip" style="--chip-color: ${colorInfo.primary}; border-color: ${colorInfo.primary}50; background: ${colorInfo.primary}15; color: ${colorInfo.primary};">
      <span class="chip-emoji">${colorInfo.emoji}</span>
      <span class="chip-name">${escapeHtml(region)}</span>
      <span class="chip-count">${count}</span>
    </span>`;
  }).join('');

  let badgesHTML = '';
  if (isContrarian) {
    badgesHTML += `<span class="prism-contrarian-badge">
      <span class="badge-icon">⚡</span>
      <span>Contrarian Signal: ${divergence}% Sentiment Divergence</span>
    </span>`;
  }
  if (isExclusive) {
    badgesHTML += `<span class="prism-exclusive-badge">
      <span class="badge-icon">✨</span>
      <span>Exclusive Reporting: ${escapeHtml(exclusiveSignal)}</span>
    </span>`;
  }

  const signalsRowHTML = badgesHTML ? ('<div class="prism-signals-row">' + badgesHTML + '</div>') : '';

  const cardsHTML = spectrumItems.map((item, idx) => {
    const colorInfo = REGION_ORIGIN_MAP[item.region] || REGION_ORIGIN_MAP['Global'];
    const isItemContrarian = isContrarian && (idx === 0 || item.isPrimary);
    const annotationHTML = (item.annotation && item.annotation.what) ? ('<p class="prism-card-annotation">✦ ' + escapeHtml(item.annotation.what) + '</p>') : '';
    const primaryTagHTML = item.isPrimary ? '<span class="prism-primary-tag">Lead</span>' : '';
    const contrarianTagHTML = isItemContrarian ? '<span class="prism-contrarian-badge micro">⚡ Contrarian</span>' : '';
    return `
      <div class="prism-perspective-card ${isItemContrarian ? 'has-contrarian' : ''}" style="border-left-color: ${colorInfo.primary};">
        <div class="prism-card-header">
          <div class="prism-card-source-wrap">
            <span class="prism-origin-chip mini" style="--chip-color: ${colorInfo.primary}; background: ${colorInfo.primary}18; color: ${colorInfo.primary}; border-color: ${colorInfo.primary}40;">
              ${colorInfo.emoji} ${escapeHtml(item.region)}
            </span>
            <span class="prism-source-name">${escapeHtml(item.source)}</span>
          </div>
          ${primaryTagHTML}
          ${contrarianTagHTML}
        </div>
        <p class="prism-card-title">${escapeHtml(item.title)}</p>
        ${annotationHTML}
      </div>
    `;
  }).join('');

  return `
    <div class="perspective-prism-container">
      <div class="prism-header">
        <div class="prism-title-row">
          <span class="prism-gem-icon">💎</span>
          <h4 class="prism-title">Perspective Prism — Multi-Source Spectrum</h4>
        </div>
        <p class="prism-subtitle">${spectrumItems.length} perspectives analyzed across ${uniqueOrigins.length} global geopolitical zone${uniqueOrigins.length === 1 ? '' : 's'}</p>
        ${signalsRowHTML}
      </div>

      <!-- Chromatic Dispersion Spectrum Bar -->
      <div class="prism-spectrum-bar" role="progressbar" aria-label="Geopolitical dispersion spectrum">
        ${barSegmentsHTML}
      </div>

      <!-- Geopolitical Zone Origin Chips -->
      <div class="prism-chips-row">
        ${originChipsHTML}
      </div>

      <!-- Regional Viewpoint Cards Grid -->
      <div class="prism-pillars-grid">
        ${cardsHTML}
      </div>
    </div>
  `;
}

/**
 * Renders on-card drawer content for .news-card.
 */
function renderCardPrismDrawerContent(art) {
  if (!art) return '';
  const spectrumItems = extractSpectrumItems(art);
  if (spectrumItems.length === 0) return '';

  const originCounts = {};
  spectrumItems.forEach(item => {
    originCounts[item.region] = (originCounts[item.region] || 0) + 1;
  });
  const uniqueOrigins = Object.keys(originCounts);
  const totalItems = spectrumItems.length;

  const barSegmentsHTML = uniqueOrigins.map(region => {
    const count = originCounts[region];
    const pct = ((count / totalItems) * 100).toFixed(1);
    const colorInfo = REGION_ORIGIN_MAP[region] || REGION_ORIGIN_MAP['Global'];
    return `<div class="prism-spectrum-segment" style="width: ${pct}%; background: ${colorInfo.primary}; box-shadow: 0 0 8px ${colorInfo.glow};" title="${escapeHtml(region)}: ${count} (${pct}%)"></div>`;
  }).join('');

  const chipsHTML = uniqueOrigins.map(region => {
    const colorInfo = REGION_ORIGIN_MAP[region] || REGION_ORIGIN_MAP['Global'];
    return `<span class="prism-origin-chip mini" style="--chip-color: ${colorInfo.primary}; background: ${colorInfo.primary}18; color: ${colorInfo.primary}; border-color: ${colorInfo.primary}40;">
      ${colorInfo.emoji} ${escapeHtml(region)} (${originCounts[region]})
    </span>`;
  }).join('');

  const viewpointsList = spectrumItems.slice(0, 3).map(item => {
    const colorInfo = REGION_ORIGIN_MAP[item.region] || REGION_ORIGIN_MAP['Global'];
    return `
      <div class="drawer-viewpoint-item" onclick="event.stopPropagation(); openModal('${escapeJs(art.id)}');">
        <span class="drawer-viewpoint-region" style="color: ${colorInfo.primary};">${colorInfo.emoji} ${escapeHtml(item.source)}</span>
        <span class="drawer-viewpoint-title">${escapeHtml(item.title)}</span>
      </div>
    `;
  }).join('');

  return `
    <div class="drawer-prism-body">
      <div class="drawer-prism-header">
        <span class="drawer-prism-title">💎 Perspective Spectrum (${spectrumItems.length} Sources)</span>
        <button class="drawer-close-btn" onclick="event.stopPropagation(); toggleCardPrismDrawer('${escapeJs(art.id)}', event);">&times;</button>
      </div>
      <div class="prism-spectrum-bar mini">${barSegmentsHTML}</div>
      <div class="drawer-chips-row">${chipsHTML}</div>
      <div class="drawer-viewpoints-list">${viewpointsList}</div>
      <button class="drawer-full-prism-btn" onclick="event.stopPropagation(); openModal('${escapeJs(art.id)}');">
        Open Deep Perspective Spectrum ↗
      </button>
    </div>
  `;
}

function toggleCardPrismDrawer(artId, event) {
  if (event) event.stopPropagation();
  const drawer = document.getElementById(`prism-drawer-${artId}`);
  if (!drawer) return;

  const isHidden = drawer.style.display === 'none' || !drawer.classList.contains('open');
  if (isHidden) {
    if (!drawer.hasChildNodes() || drawer.innerHTML.trim() === '') {
      const art = (state.articles || []).find(a => String(a.id) === String(artId)) ||
                  (state.filteredArticles || []).find(a => String(a.id) === String(artId));
      if (art) {
        drawer.innerHTML = renderCardPrismDrawerContent(art);
      }
    }
    drawer.style.display = 'block';
    requestAnimationFrame(() => drawer.classList.add('open'));
  } else {
    drawer.classList.remove('open');
    setTimeout(() => {
      if (!drawer.classList.contains('open')) {
        drawer.style.display = 'none';
      }
    }, 280);
  }
}
window.toggleCardPrismDrawer = toggleCardPrismDrawer;

// ==========================================================================
// R4: NARRATIVE TIME MACHINE (STORY ARC SCRUBBER)
// ==========================================================================

state.narrativeMemory = { arcsById: {} };

async function initNarrativeMemory() {
  try {
    const res = await fetch('data/narrative_memory.json?v=' + Date.now());
    if (!res.ok) return;
    const data = await res.json();
    if (data && Array.isArray(data.arcs)) {
      data.arcs.forEach(arc => {
        if (arc && arc.arc_id) {
          state.narrativeMemory.arcsById[arc.arc_id] = arc;
        }
      });
    }
  } catch (err) {
    // Graceful standalone fallback
  }
}

function getArcChapters(art) {
  if (!art || !art.narrative_arc) return [];
  const arcId = art.narrative_arc.arc_id;
  const memoryArc = arcId && state.narrativeMemory ? state.narrativeMemory.arcsById[arcId] : null;

  if (memoryArc && Array.isArray(memoryArc.chapter_titles) && memoryArc.chapter_titles.length > 0) {
    const total = memoryArc.chapter_titles.length;
    const maxDay = art.narrative_arc.day_number || 1;
    return memoryArc.chapter_titles.map((title, idx) => {
      const day = Math.max(1, Math.min(maxDay, Math.ceil(((idx + 1) / total) * maxDay)));
      const cleanTitle = title.replace(/\s*-\s*Reuters$/i, '').trim().toLowerCase();
      const matchedArt = (state.articles || []).find(a => 
        (a.title && a.title.toLowerCase().includes(cleanTitle.slice(0, 30))) ||
        (cleanTitle.includes((a.title || '').toLowerCase().slice(0, 30)))
      );
      return {
        chapterIndex: idx + 1,
        totalChapters: total,
        day: day,
        title: title,
        source: memoryArc.sources_involved ? memoryArc.sources_involved[idx % memoryArc.sources_involved.length] : (art.source || 'Primary Source'),
        articleId: matchedArt ? matchedArt.id : null,
        isCurrent: (idx === total - 1)
      };
    });
  }

  const prev = Array.isArray(art.narrative_arc.previous_headlines) ? art.narrative_arc.previous_headlines : [];
  const chapters = prev.map((h, i) => {
    const matchedArt = (state.articles || []).find(a => 
      a.title && (a.title.toLowerCase().includes(h.toLowerCase().slice(0, 30)) || h.toLowerCase().includes(a.title.toLowerCase().slice(0, 30)))
    );
    return {
      chapterIndex: i + 1,
      totalChapters: prev.length + 1,
      day: Math.max(1, i + 1),
      title: h,
      source: art.source || 'Primary Source',
      articleId: matchedArt ? matchedArt.id : null,
      isCurrent: false
    };
  });

  chapters.push({
    chapterIndex: prev.length + 1,
    totalChapters: prev.length + 1,
    day: art.narrative_arc.day_number || (prev.length + 1),
    title: art.title,
    source: art.source || 'Primary Source',
    articleId: art.id,
    isCurrent: true
  });

  return chapters;
}

function renderNarrativeTimeMachine(art) {
  if (!art || !art.narrative_arc || !art.narrative_arc.arc_id) return '';
  const chapters = getArcChapters(art);
  const total = chapters.length;
  const isSingleChapter = total <= 1;
  const currentIndex = total - 1;
  const currentChapter = chapters[currentIndex] || { chapterIndex: 1, totalChapters: 1, day: 1, title: art.title, source: art.source };

  window._activeNarrativeChapters = chapters;
  window._activeNarrativeIndex = currentIndex;

  const trend = art.narrative_arc.importance_trend || 'stable';

  const ticksHTML = chapters.map((chap, idx) => `
    <span class="scrubber-tick ${idx === currentIndex ? 'active' : ''}" 
          style="left: ${total > 1 ? ((idx / (total - 1)) * 100).toFixed(1) : 50}%;"
          onclick="event.stopPropagation(); handleNarrativeScrub(${idx});"
          title="Chapter ${chap.chapterIndex}: Day ${chap.day}"></span>
  `).join('');

  const currentPillHTML = currentChapter.isCurrent
    ? '<span class="spotlight-current-pill">Current Dispatch</span>'
    : '<span class="spotlight-historic-pill">Historical Chapter</span>';

  let spotlightActionsHTML = '';
  if (currentChapter.articleId && currentChapter.articleId !== art.id) {
    spotlightActionsHTML = '<button class="narrative-jump-btn" onclick="event.stopPropagation(); jumpToNarrativeDispatch(\'' + escapeJs(currentChapter.articleId) + '\');">Read Chapter Dispatch ↗</button>';
  } else {
    spotlightActionsHTML = '<span class="spotlight-nav-hint">' + (isSingleChapter ? 'Single Chapter Story · Genesis' : 'Drag scrubber or click &lt; &gt; to inspect timeline progression') + '</span>';
  }

  return `
    <div class="narrative-time-machine" id="narrativeTimeMachine" data-arc-id="${escapeHtml(art.narrative_arc.arc_id)}">
      <div class="time-machine-header">
        <div class="time-machine-title-wrap">
          <span class="time-machine-glyph">⏳</span>
          <div>
            <span class="time-machine-tag">NARRATIVE TIME MACHINE · ARC SCRUBBER</span>
            <h4 class="time-machine-arc-title">${escapeHtml(art.narrative_arc.arc_title || art.title)}</h4>
          </div>
        </div>
        <div class="time-machine-status-badge ${trend}">
          <span class="status-trend-dot ${trend}"></span>
          <span>${trend.toUpperCase()}</span>
        </div>
      </div>

      <!-- Scrubber Track Row -->
      <div class="time-machine-scrubber-row">
        <button class="chapter-step-btn prev-chapter-btn" 
                onclick="event.stopPropagation(); stepNarrativeChapter(-1);" 
                title="Previous Chapter" 
                aria-label="Previous Chapter" 
                ${isSingleChapter ? 'disabled' : ''}>&lt;</button>

        <div class="narrative-scrubber-track-wrap">
          <input type="range" 
                 class="narrative-time-scrubber narrative-scrubber-slider" 
                 id="narrativeTimeScrubber"
                 min="0" 
                 max="${Math.max(0, total - 1)}" 
                 value="${currentIndex}" 
                 step="1"
                 oninput="handleNarrativeScrub(this.value)"
                 aria-label="Story Arc Timeline Scrubber"
                 ${isSingleChapter ? 'disabled' : ''} />
          <div class="narrative-scrubber-ticks-bar narrative-scrubber-ticks">
            ${ticksHTML}
          </div>
        </div>

        <button class="chapter-step-btn next-chapter-btn" 
                onclick="event.stopPropagation(); stepNarrativeChapter(1);" 
                title="Next Chapter" 
                aria-label="Next Chapter" 
                ${isSingleChapter ? 'disabled' : ''}>&gt;</button>
      </div>

      <!-- Historical Chapter Spotlight Box -->
      <div class="narrative-spotlight-box narrative-chapter-spotlight" id="narrativeSpotlightBox">
        <div class="spotlight-chapter-meta">
          <span class="spotlight-chapter-badge" id="spotlightChapterBadge">Chapter ${currentChapter.chapterIndex} of ${currentChapter.totalChapters}</span>
          <span class="spotlight-day-badge" id="spotlightDayBadge">Day ${currentChapter.day}</span>
          <span class="spotlight-source-badge" id="spotlightSourceBadge">${escapeHtml(currentChapter.source)}</span>
          ${currentPillHTML}
        </div>
        <p class="spotlight-headline" id="spotlightHeadline">${escapeHtml(currentChapter.title)}</p>
        <div class="spotlight-actions" id="spotlightActions">
          ${spotlightActionsHTML}
        </div>
      </div>
    </div>
  `;
}

function handleNarrativeScrub(val) {
  const chapters = window._activeNarrativeChapters || [];
  if (chapters.length === 0) return;
  const idx = Math.max(0, Math.min(chapters.length - 1, parseInt(val, 10)));
  window._activeNarrativeIndex = idx;
  const slider = document.getElementById('narrativeTimeScrubber');
  if (slider && parseInt(slider.value, 10) !== idx) slider.value = idx;
  renderNarrativeChapterSpotlight(chapters[idx]);
}

function stepNarrativeChapter(delta) {
  const chapters = window._activeNarrativeChapters || [];
  if (chapters.length === 0) return;
  const curr = (typeof window._activeNarrativeIndex === 'number') ? window._activeNarrativeIndex : (chapters.length - 1);
  const next = Math.max(0, Math.min(chapters.length - 1, curr + delta));
  if (next === curr && delta !== 0) return;
  handleNarrativeScrub(next);
}

function renderNarrativeChapterSpotlight(chapter) {
  if (!chapter) return;
  const badge = document.getElementById('spotlightChapterBadge');
  const day = document.getElementById('spotlightDayBadge');
  const source = document.getElementById('spotlightSourceBadge');
  const headline = document.getElementById('spotlightHeadline');
  const actions = document.getElementById('spotlightActions');

  if (badge) badge.textContent = `Chapter ${chapter.chapterIndex} of ${chapter.totalChapters}`;
  if (day) day.textContent = `Day ${chapter.day}`;
  if (source) source.textContent = chapter.source;
  if (headline) headline.textContent = chapter.title;

  if (actions) {
    if (chapter.articleId && (!state.modalState || (state.modalState.articles[state.modalState.currentIndex] && state.modalState.articles[state.modalState.currentIndex].id !== chapter.articleId))) {
      actions.innerHTML = `
        <button class="narrative-jump-btn" onclick="event.stopPropagation(); jumpToNarrativeDispatch('${chapter.articleId}');">
          Read Chapter Dispatch ↗
        </button>
      `;
    } else {
      actions.innerHTML = `<span class="spotlight-nav-hint">${chapter.isCurrent ? 'Viewing Current Dispatch' : 'Archived Chapter Record'}</span>`;
    }
  }

  const ticks = document.querySelectorAll('.scrubber-tick');
  ticks.forEach((tick, i) => {
    tick.classList.toggle('active', i === chapter.chapterIndex - 1);
  });
}

function jumpToNarrativeDispatch(artId) {
  if (!artId) return;
  openModal(artId);
}

window.handleNarrativeScrub = handleNarrativeScrub;
window.stepNarrativeChapter = stepNarrativeChapter;
window.renderNarrativeChapterSpotlight = renderNarrativeChapterSpotlight;
window.jumpToNarrativeDispatch = jumpToNarrativeDispatch;

// Global interface bindings for M3
window.getPublisherOrigin = getPublisherOrigin;
window.REGION_ORIGIN_MAP = REGION_ORIGIN_MAP;
window.renderPerspectivePrism = renderPerspectivePrism;
window.renderNarrativeTimeMachine = renderNarrativeTimeMachine;
window.initNarrativeMemory = initNarrativeMemory;
window.getArcChapters = getArcChapters;


/* ==========================================================================
   MILESTONE 4: EXECUTIVE INTELLIGENCE (R5 & R7)
   ========================================================================== */

// --------------------------------------------------------------------------
// R5: FOCUS TIMER ("10-MINUTE INTELLIGENCE SESSION") & 5-STORY DOCKET
// --------------------------------------------------------------------------

/**
 * Curates an optimal 5-story executive docket.
 * Guarantees balanced domain coverage across World, Tech, Business, and National,
 * plus the highest remaining composite signal article (rewarding Black Swan & Contrarian).
 * @param {Array} articles - Full articles pool
 * @returns {Array} Exactly 5 curated articles
 */
function curateFocusDocket(articles) {
  const pool = (articles || []).filter(a => !a.is_duplicate);
  const categories = ['World', 'Tech', 'Business', 'National'];
  const docket = [];
  const selectedIds = new Set();

  // Phase 1: Select highest importance_score story from each of the 4 major pillars
  categories.forEach(cat => {
    const candidates = pool
      .filter(a => a.category === cat && !selectedIds.has(a.id))
      .sort((a, b) => (b.importance_score || 0) - (a.importance_score || 0));

    if (candidates.length > 0) {
      docket.push(candidates[0]);
      selectedIds.add(candidates[0].id);
    }
  });

  // Phase 2: Select the 5th story with highest remaining composite signal
  const remaining = pool
    .filter(a => !selectedIds.has(a.id))
    .sort((a, b) => {
      const bonusA = (a.meta && a.meta.is_black_swan ? 1.5 : 0) + (a.meta && a.meta.is_contrarian ? 0.8 : 0);
      const bonusB = (b.meta && b.meta.is_black_swan ? 1.5 : 0) + (b.meta && b.meta.is_contrarian ? 0.8 : 0);
      return ((b.importance_score || 0) + bonusB) - ((a.importance_score || 0) + bonusA);
    });

  while (docket.length < 5 && remaining.length > 0) {
    const next = remaining.shift();
    docket.push(next);
    selectedIds.add(next.id);
  }

  return docket;
}

function updateFocusTimerDisplay() {
  const display = document.getElementById('focusTimerDisplay');
  const bar = document.getElementById('focusBarFill');
  const countDisplay = document.getElementById('focusCountDisplay');
  if (!state.focusSession) return;

  const rem = Math.max(0, state.focusSession.remainingSeconds);
  const mins = Math.floor(rem / 60);
  const secs = rem % 60;
  if (display) {
    display.textContent = `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  }
  if (bar) {
    const pct = (((state.focusSession.totalSeconds - rem) / state.focusSession.totalSeconds) * 100).toFixed(1);
    bar.style.width = `${pct}%`;
  }
  if (countDisplay) {
    const readCount = state.focusSession.readIds ? state.focusSession.readIds.size : 0;
    countDisplay.textContent = `${readCount} / ${state.focusSession.docket.length} Read`;
  }
}

function startFocusSession() {
  const pool = (state.articles && state.articles.length > 0) ? state.articles : state.filteredArticles;
  const docket = curateFocusDocket(pool);
  if (!docket || docket.length === 0) return;

  if (state.focusSession.timerInterval) {
    clearInterval(state.focusSession.timerInterval);
  }

  state.focusSession = {
    active: true,
    isPaused: false,
    totalSeconds: 600,
    remainingSeconds: 600,
    timerInterval: null,
    docket: docket,
    readIds: new Set(),
    startTime: Date.now(),
    allRead: false
  };

  // Close Quick Tools popover if open
  const toolsDropdown = document.getElementById('headerToolsDropdown');
  if (toolsDropdown) toolsDropdown.classList.remove('active');

  // Show Focus Timer Pill at top of viewport
  const pill = document.getElementById('focusTimerPill');
  if (pill) {
    pill.style.display = 'flex';
  }

  // Update displays
  updateFocusTimerDisplay();
  const pauseBtn = document.getElementById('focusPauseBtn');
  if (pauseBtn) pauseBtn.textContent = '⏸';

  // Temporarily disconnect infinite scroll observer
  if (_gridScrollObserver) {
    _gridScrollObserver.disconnect();
    _gridScrollObserver = null;
  }
  const existingSentinel = document.getElementById('gridScrollSentinel');
  if (existingSentinel) existingSentinel.remove();

  // Render strictly the 5-story executive docket
  if (gridTitle) {
    gridTitle.textContent = '🎯 10-Minute Executive Docket (5 High-Impact Dispatches)';
  }
  state.filteredArticles = docket;
  renderGrid(docket);

  // Scroll smoothly to feed
  scrollToContent();

  // Start 1-second countdown loop
  state.focusSession.timerInterval = setInterval(() => {
    if (!state.focusSession.active) {
      clearInterval(state.focusSession.timerInterval);
      return;
    }
    if (!state.focusSession.isPaused) {
      state.focusSession.remainingSeconds--;
      updateFocusTimerDisplay();
      if (state.focusSession.remainingSeconds <= 0) {
        clearInterval(state.focusSession.timerInterval);
        completeFocusSession();
      }
    }
  }, 1000);
}

function toggleFocusPause() {
  if (!state.focusSession || !state.focusSession.active) return;
  state.focusSession.isPaused = !state.focusSession.isPaused;
  const pauseBtn = document.getElementById('focusPauseBtn');
  if (pauseBtn) {
    pauseBtn.textContent = state.focusSession.isPaused ? '▶' : '⏸';
  }
}

function completeFocusSession() {
  if (!state.focusSession || !state.focusSession.active) return;
  if (state.focusSession.timerInterval) {
    clearInterval(state.focusSession.timerInterval);
  }

  const pill = document.getElementById('focusTimerPill');
  if (pill) pill.style.display = 'none';

  const elapsedSecs = state.focusSession.totalSeconds - Math.max(0, state.focusSession.remainingSeconds);
  const elapsedMins = Math.floor(elapsedSecs / 60);
  const elapsedRemSecs = elapsedSecs % 60;
  const timeFormatted = `${elapsedMins.toString().padStart(2, '0')}:${elapsedRemSecs.toString().padStart(2, '0')}`;

  const docket = state.focusSession.docket || [];
  const readCount = state.focusSession.readIds ? state.focusSession.readIds.size : 0;

  // Domain coverage calculation
  const distinctCategories = new Set(docket.map(a => a.category));
  const domainPct = Math.round((Math.min(4, distinctCategories.size) / 4) * 100);

  // Signal density
  const totalScore = docket.reduce((acc, a) => acc + (a.importance_score || 5.0), 0);
  const avgScore = docket.length > 0 ? (totalScore / docket.length).toFixed(2) : '5.50';

  // Populate report modal elements
  const elTime = document.getElementById('metricTimeElapsed');
  const elRead = document.getElementById('metricStoriesRead');
  const elDomain = document.getElementById('metricDomainCoverage');
  const elSignal = document.getElementById('metricSignalScore');
  const elDomains = document.getElementById('focusReportDomains');

  if (elTime) elTime.textContent = timeFormatted;
  if (elRead) elRead.textContent = `${readCount} / ${docket.length}`;
  if (elDomain) elDomain.textContent = `${domainPct}%`;
  if (elSignal) elSignal.textContent = avgScore;

  if (elDomains) {
    elDomains.innerHTML = docket.map(art => {
      const isRead = state.focusSession.readIds && state.focusSession.readIds.has(art.id);
      return `
        <span class="focus-domain-pill" title="${escapeHtml(art.title)}">
          <span style="color: ${isRead ? '#10b981' : '#94a3b8'};">${isRead ? '✓' : '•'}</span>
          <strong>${escapeHtml(art.category)}:</strong> ${escapeHtml(art.source)}
        </span>
      `;
    }).join('');
  }

  // Open Focus Report Modal
  const modal = document.getElementById('focusReportModal');
  if (modal) {
    modal.style.display = 'flex';
    modal.classList.add('active');
    document.body.classList.add('modal-open');
  }
}

function exitFocusSession() {
  if (state.focusSession) {
    if (state.focusSession.timerInterval) {
      clearInterval(state.focusSession.timerInterval);
    }
    state.focusSession.active = false;
    state.focusSession.isPaused = false;
  }

  const pill = document.getElementById('focusTimerPill');
  if (pill) pill.style.display = 'none';

  const modal = document.getElementById('focusReportModal');
  if (modal) {
    modal.classList.remove('active');
    modal.style.display = 'none';
    document.body.classList.remove('modal-open');
  }

  // Restore regular feed
  filterArticles();
}

function copyFocusSessionMarkdown() {
  if (!state.focusSession || !state.focusSession.docket) return;
  const docket = state.focusSession.docket;
  const readCount = state.focusSession.readIds ? state.focusSession.readIds.size : 0;
  const elapsedSecs = state.focusSession.totalSeconds - Math.max(0, state.focusSession.remainingSeconds);
  const elapsedMins = Math.floor(elapsedSecs / 60);
  const elapsedRemSecs = elapsedSecs % 60;
  const duration = `${elapsedMins}m ${elapsedRemSecs}s`;

  let md = `# Executive Intelligence Focus Session Brief\n\n`;
  md += `**Date:** ${new Date().toLocaleDateString()} ${new Date().toLocaleTimeString()}\n`;
  md += `**Session Duration:** ${duration} | **Stories Read:** ${readCount}/${docket.length}\n\n`;
  md += `## Curated Executive Docket\n\n`;

  docket.forEach((art, idx) => {
    const isRead = state.focusSession.readIds && state.focusSession.readIds.has(art.id);
    md += `${idx + 1}. **[${art.category}]** ${art.title} — *${art.source}* (${isRead ? 'Reviewed' : 'Unread'})\n`;
    if (art.annotation && art.annotation.why) {
      md += `   - *Analysis:* ${art.annotation.why}\n`;
    }
  });

  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(md).then(() => {
      const btn = document.getElementById('focusCopySummaryBtn');
      if (btn) {
        const origText = btn.textContent;
        btn.textContent = '✓ Copied to Clipboard!';
        setTimeout(() => { btn.textContent = origText; }, 2000);
      }
    });
  }
}

function setupFocusSession() {
  const btn = document.getElementById('focusSessionBtn');
  if (btn) {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      startFocusSession();
    });
  }

  const pauseBtn = document.getElementById('focusPauseBtn');
  if (pauseBtn) {
    pauseBtn.addEventListener('click', (e) => {
      e.preventDefault();
      toggleFocusPause();
    });
  }

  const endBtn = document.getElementById('focusEndBtn');
  if (endBtn) {
    endBtn.addEventListener('click', (e) => {
      e.preventDefault();
      completeFocusSession();
    });
  }

  const returnBtn = document.getElementById('focusReturnFeedBtn');
  if (returnBtn) {
    returnBtn.addEventListener('click', (e) => {
      e.preventDefault();
      exitFocusSession();
    });
  }

  const copyBtn = document.getElementById('focusCopySummaryBtn');
  if (copyBtn) {
    copyBtn.addEventListener('click', (e) => {
      e.preventDefault();
      copyFocusSessionMarkdown();
    });
  }

  // Dismiss modal if clicking backdrop
  const modal = document.getElementById('focusReportModal');
  if (modal) {
    modal.addEventListener('click', (e) => {
      if (e.target === modal) {
        exitFocusSession();
      }
    });
  }
}


// --------------------------------------------------------------------------
// R7: KNOWLEDGE CONSTELLATION MAP (2D INTERACTIVE CANVAS GRAPH MODAL)
// --------------------------------------------------------------------------

/**
 * In-memory entity graph extraction from articles.
 * Categorized nodes:
 *   Nations: #10b981
 *   Leaders: #f59e0b
 *   Orgs & Cos: #0284c7
 *   Clusters: #a855f7
 */
function buildKnowledgeGraph(articles) {
  const nodeMap = new Map();
  const edgeMap = new Map();
  const pool = (articles && articles.length > 0) ? articles : (state.articles || []);

  pool.forEach(art => {
    const artId = art.id;
    const entities = art.entities || {};
    const artNodes = [];

    // Nations (#10b981)
    (entities.countries || []).forEach(c => {
      const name = c.name || c.code || (typeof c === 'string' ? c : null);
      if (name && name.length >= 2) {
        artNodes.push({ id: `nation:${name}`, type: 'nation', label: name, color: '#10b981' });
      }
    });

    // Leaders (#f59e0b)
    (entities.leaders || []).forEach(l => {
      const name = l.name || (typeof l === 'string' ? l : null);
      if (name && name.length >= 2) {
        artNodes.push({ id: `leader:${name}`, type: 'leader', label: name, color: '#f59e0b' });
      }
    });

    // Organizations (#0284c7)
    (entities.organizations || []).forEach(o => {
      const name = o.name || (typeof o === 'string' ? o : null);
      if (name && name.length >= 2) {
        artNodes.push({ id: `org:${name}`, type: 'org', label: name, color: '#0284c7' });
      }
    });

    // Companies (#0284c7)
    (entities.companies || []).forEach(co => {
      const name = co.name || (typeof co === 'string' ? co : null);
      if (name && name.length >= 2) {
        artNodes.push({ id: `org:${name}`, type: 'org', label: name, color: '#0284c7' });
      }
    });

    // Story Clusters (#a855f7)
    if (art.storyCluster && art.storyCluster.size > 1) {
      const clusterId = `cluster:${art.category}-${art.id}`;
      artNodes.push({ id: clusterId, type: 'cluster', label: `${art.category} Cluster`, color: '#a855f7' });
    }

    // Register nodes
    artNodes.forEach(node => {
      if (!nodeMap.has(node.id)) {
        nodeMap.set(node.id, {
          ...node,
          articles: [],
          connections: 0,
          x: 0,
          y: 0,
          vx: 0,
          vy: 0,
          radius: 12
        });
      }
      const existing = nodeMap.get(node.id);
      if (!existing.articles.includes(artId)) {
        existing.articles.push(artId);
      }
    });

    // Register co-occurring edges
    for (let i = 0; i < artNodes.length; i++) {
      for (let j = i + 1; j < artNodes.length; j++) {
        const u = artNodes[i].id;
        const v = artNodes[j].id;
        if (u === v) continue;
        const edgeKey = u < v ? `${u}__${v}` : `${v}__${u}`;
        if (!edgeMap.has(edgeKey)) {
          edgeMap.set(edgeKey, { source: u, target: v, weight: 0 });
        }
        edgeMap.get(edgeKey).weight += 1;
      }
    }
  });

  // Calculate dynamic radius and degree
  nodeMap.forEach(n => {
    n.radius = Math.max(10, Math.min(26, 10 + Math.sqrt(n.articles.length) * 3.5));
  });

  const nodes = Array.from(nodeMap.values());
  const edges = Array.from(edgeMap.values());

  // Count degree connections
  edges.forEach(e => {
    const s = nodeMap.get(e.source);
    const t = nodeMap.get(e.target);
    if (s) s.connections++;
    if (t) t.connections++;
  });

  return { nodes, edges, nodeMap };
}

/**
 * Pure HTML5 Canvas 2D Force-Directed Simulation Engine
 * Euler numerical integration with Coulomb repulsion, Hooke spring attraction,
 * center gravity, velocity damping, and alpha cooling.
 */
class ConstellationSimulation {
  constructor(canvas, graphData) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.nodes = graphData.nodes;
    this.edges = graphData.edges;
    this.nodeMap = graphData.nodeMap;

    // Simulation physics parameters
    this.kRep = 950;
    this.kSpring = 0.035;
    this.springLength = 85;
    this.kGravity = 0.012;
    this.damping = 0.86;
    this.alpha = 1.0;
    this.minAlpha = 0.005;

    // Camera Pan & Zoom state
    this.camera = { x: 0, y: 0, zoom: 1.0 };
    this.isDraggingCamera = false;
    this.dragStartX = 0;
    this.dragStartY = 0;
    this.cameraStartX = 0;
    this.cameraStartY = 0;

    // Node interaction state
    this.selectedNode = null;
    this.hoveredNode = null;
    this.draggedNode = null;
    this.activeTypeFilter = 'all';

    // Animation
    this.animFrameId = null;
    this.isRunning = false;
    this.pulseAngle = 0;

    this.initLayout();
    this.setupEvents();
  }

  initLayout() {
    const count = this.nodes.length;
    const radius = Math.min(this.canvas.width, this.canvas.height) * 0.35;
    this.nodes.forEach((node, i) => {
      const angle = (i / count) * Math.PI * 2;
      const r = radius * (0.4 + 0.6 * Math.random());
      node.x = Math.cos(angle) * r;
      node.y = Math.sin(angle) * r;
      node.vx = (Math.random() - 0.5) * 2;
      node.vy = (Math.random() - 0.5) * 2;
    });
    this.alpha = 1.0;
  }

  toScreen(wx, wy) {
    const cx = this.canvas.width / 2;
    const cy = this.canvas.height / 2;
    return {
      x: cx + (wx + this.camera.x) * this.camera.zoom,
      y: cy + (wy + this.camera.y) * this.camera.zoom
    };
  }

  toWorld(sx, sy) {
    const cx = this.canvas.width / 2;
    const cy = this.canvas.height / 2;
    return {
      x: (sx - cx) / this.camera.zoom - this.camera.x,
      y: (sy - cy) / this.camera.zoom - this.camera.y
    };
  }

  getNodeAtScreenPos(sx, sy) {
    const world = this.toWorld(sx, sy);
    for (let i = this.nodes.length - 1; i >= 0; i--) {
      const n = this.nodes[i];
      if (this.activeTypeFilter !== 'all' && n.type !== this.activeTypeFilter) continue;
      const dx = world.x - n.x;
      const dy = world.y - n.y;
      if (dx * dx + dy * dy <= (n.radius + 4) * (n.radius + 4)) {
        return n;
      }
    }
    return null;
  }

  stepPhysics() {
    if (this.alpha < this.minAlpha) return;

    const n = this.nodes.length;

    // 1. Coulomb Repulsion between all node pairs
    for (let i = 0; i < n; i++) {
      const u = this.nodes[i];
      for (let j = i + 1; j < n; j++) {
        const v = this.nodes[j];
        const dx = v.x - u.x;
        const dy = v.y - u.y;
        const dSq = dx * dx + dy * dy + 1.0;
        const dist = Math.sqrt(dSq);
        const force = this.kRep / dSq;
        const fx = (dx / dist) * force;
        const fy = (dy / dist) * force;
        u.vx -= fx;
        u.vy -= fy;
        v.vx += fx;
        v.vy += fy;
      }
    }

    // 2. Hooke's Spring Attraction along edges
    for (let i = 0; i < this.edges.length; i++) {
      const edge = this.edges[i];
      const u = this.nodeMap.get(edge.source);
      const v = this.nodeMap.get(edge.target);
      if (!u || !v) continue;
      const dx = v.x - u.x;
      const dy = v.y - u.y;
      const dist = Math.sqrt(dx * dx + dy * dy) + 0.1;
      const delta = dist - this.springLength;
      const force = delta * this.kSpring * Math.min(3, 1 + edge.weight * 0.4);
      const fx = (dx / dist) * force;
      const fy = (dy / dist) * force;
      u.vx += fx;
      u.vy += fy;
      v.vx -= fx;
      v.vy -= fy;
    }

    // 3. Center Gravity & Integration
    for (let i = 0; i < n; i++) {
      const u = this.nodes[i];
      if (u === this.draggedNode) continue;
      u.vx -= u.x * this.kGravity;
      u.vy -= u.y * this.kGravity;

      u.vx *= this.damping;
      u.vy *= this.damping;

      u.x += u.vx * this.alpha;
      u.y += u.vy * this.alpha;
    }

    this.alpha *= 0.985;
  }

  draw() {
    const ctx = this.ctx;
    const w = this.canvas.width;
    const h = this.canvas.height;
    this.pulseAngle += 0.04;

    ctx.clearRect(0, 0, w, h);

    const isLight = document.documentElement.getAttribute('data-theme') === 'light';

    // Ambient radial background glow
    const bgGrad = ctx.createRadialGradient(w / 2, h / 2, 50, w / 2, h / 2, Math.max(w, h) * 0.7);
    if (isLight) {
      bgGrad.addColorStop(0, '#f8fafc');
      bgGrad.addColorStop(1, '#e2e8f0');
    } else {
      bgGrad.addColorStop(0, '#0f172a');
      bgGrad.addColorStop(1, '#020617');
    }
    ctx.fillStyle = bgGrad;
    ctx.fillRect(0, 0, w, h);

    // Save context for camera transformation
    ctx.save();
    ctx.translate(w / 2, h / 2);
    ctx.scale(this.camera.zoom, this.camera.zoom);
    ctx.translate(this.camera.x, this.camera.y);

    const activeNode = this.hoveredNode || this.selectedNode;

    // Draw Edges
    for (let i = 0; i < this.edges.length; i++) {
      const e = this.edges[i];
      const u = this.nodeMap.get(e.source);
      const v = this.nodeMap.get(e.target);
      if (!u || !v) continue;

      const isConnectedToActive = activeNode && (u.id === activeNode.id || v.id === activeNode.id);

      ctx.beginPath();
      ctx.moveTo(u.x, u.y);
      ctx.lineTo(v.x, v.y);

      if (isConnectedToActive) {
        ctx.strokeStyle = '#00f2fe';
        ctx.lineWidth = Math.min(3.5, 1.5 + e.weight * 0.5);
        ctx.shadowColor = '#00f2fe';
        ctx.shadowBlur = 8;
      } else if (activeNode) {
        ctx.strokeStyle = isLight ? 'rgba(15, 23, 42, 0.06)' : 'rgba(255, 255, 255, 0.04)';
        ctx.lineWidth = 1;
        ctx.shadowBlur = 0;
      } else {
        ctx.strokeStyle = isLight ? 'rgba(15, 23, 42, 0.15)' : 'rgba(255, 255, 255, 0.1)';
        ctx.lineWidth = Math.min(2.5, 0.8 + e.weight * 0.3);
        ctx.shadowBlur = 0;
      }
      ctx.stroke();
    }
    ctx.shadowBlur = 0;

    // Draw Nodes
    for (let i = 0; i < this.nodes.length; i++) {
      const u = this.nodes[i];
      const isFiltered = this.activeTypeFilter !== 'all' && u.type !== this.activeTypeFilter;
      const isSelected = this.selectedNode && this.selectedNode.id === u.id;
      const isHovered = this.hoveredNode && this.hoveredNode.id === u.id;
      const isConnected = activeNode && !isHovered && !isSelected && this.edges.some(e => 
        (e.source === activeNode.id && e.target === u.id) || (e.target === activeNode.id && e.source === u.id)
      );

      ctx.save();
      if (isFiltered) {
        ctx.globalAlpha = 0.15;
      } else if (activeNode && !isSelected && !isHovered && !isConnected) {
        ctx.globalAlpha = 0.28;
      }

      // Outer Glow Halo
      ctx.shadowColor = u.color;
      ctx.shadowBlur = isHovered || isSelected ? 22 : 10;

      // Selection Concentric Ring
      if (isSelected || isHovered) {
        const ringRadius = u.radius + 5 + Math.sin(this.pulseAngle) * 2;
        ctx.beginPath();
        ctx.arc(u.x, u.y, ringRadius, 0, Math.PI * 2);
        ctx.strokeStyle = '#00f2fe';
        ctx.lineWidth = 2;
        ctx.stroke();
      }

      // Node Body
      ctx.beginPath();
      ctx.arc(u.x, u.y, u.radius, 0, Math.PI * 2);
      const radGrad = ctx.createRadialGradient(u.x - u.radius * 0.3, u.y - u.radius * 0.3, u.radius * 0.1, u.x, u.y, u.radius);
      radGrad.addColorStop(0, '#ffffff');
      radGrad.addColorStop(0.3, u.color);
      radGrad.addColorStop(1, u.color);
      ctx.fillStyle = radGrad;
      ctx.fill();

      // VisionOS Specular Ring
      ctx.lineWidth = 1.5;
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.5)';
      ctx.stroke();

      // Node Label (Text below node with crisp dark stroke for readability)
      ctx.shadowBlur = 0;
      ctx.font = '600 11px Inter, -apple-system, sans-serif';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'top';

      const label = u.label;
      const textY = u.y + u.radius + 5;

      ctx.lineWidth = 3;
      ctx.strokeStyle = isLight ? 'rgba(255, 255, 255, 0.95)' : 'rgba(2, 6, 23, 0.95)';
      ctx.strokeText(label, u.x, textY);

      ctx.fillStyle = isLight ? '#0f172a' : '#f8fafc';
      ctx.fillText(label, u.x, textY);

      ctx.restore();
    }

    ctx.restore();
  }

  loop() {
    if (!this.isRunning) return;
    this.stepPhysics();
    this.draw();
    this.animFrameId = requestAnimationFrame(() => this.loop());
  }

  start() {
    if (this.isRunning) return;
    this.isRunning = true;
    this.alpha = 1.0;
    this.loop();
  }

  stop() {
    this.isRunning = false;
    if (this.animFrameId) {
      cancelAnimationFrame(this.animFrameId);
      this.animFrameId = null;
    }
  }

  fitToScreen() {
    if (this.nodes.length === 0) return;
    let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
    this.nodes.forEach(n => {
      minX = Math.min(minX, n.x - n.radius);
      maxX = Math.max(maxX, n.x + n.radius);
      minY = Math.min(minY, n.y - n.radius);
      maxY = Math.max(maxY, n.y + n.radius);
    });

    const graphW = Math.max(100, maxX - minX);
    const graphH = Math.max(100, maxY - minY);
    const margin = 80;
    const scaleX = (this.canvas.width - margin * 2) / graphW;
    const scaleY = (this.canvas.height - margin * 2) / graphH;

    this.camera.zoom = Math.max(0.4, Math.min(1.6, Math.min(scaleX, scaleY)));
    this.camera.x = -((minX + maxX) / 2);
    this.camera.y = -((minY + maxY) / 2);
    this.alpha = 0.2;
  }

  setupEvents() {
    const canvas = this.canvas;
    const tooltip = document.getElementById('constellationTooltip');
    let downPos = { x: 0, y: 0 };

    canvas.addEventListener('pointerdown', (e) => {
      const rect = canvas.getBoundingClientRect();
      const sx = e.clientX - rect.left;
      const sy = e.clientY - rect.top;
      downPos = { x: sx, y: sy };

      const hit = this.getNodeAtScreenPos(sx, sy);
      if (hit) {
        this.draggedNode = hit;
        this.alpha = 0.4;
      } else {
        this.isDraggingCamera = true;
        this.dragStartX = e.clientX;
        this.dragStartY = e.clientY;
        this.cameraStartX = this.camera.x;
        this.cameraStartY = this.camera.y;
      }
    });

    window.addEventListener('pointermove', (e) => {
      if (!this.isRunning) return;
      const rect = canvas.getBoundingClientRect();
      const sx = e.clientX - rect.left;
      const sy = e.clientY - rect.top;

      if (this.draggedNode) {
        const world = this.toWorld(sx, sy);
        this.draggedNode.x = world.x;
        this.draggedNode.y = world.y;
        this.draggedNode.vx = 0;
        this.draggedNode.vy = 0;
        this.alpha = 0.3;
      } else if (this.isDraggingCamera) {
        const dx = (e.clientX - this.dragStartX) / this.camera.zoom;
        const dy = (e.clientY - this.dragStartY) / this.camera.zoom;
        this.camera.x = this.cameraStartX + dx;
        this.camera.y = this.cameraStartY + dy;
      } else if (sx >= 0 && sx <= rect.width && sy >= 0 && sy <= rect.height) {
        const hit = this.getNodeAtScreenPos(sx, sy);
        this.hoveredNode = hit;
        if (hit && tooltip) {
          tooltip.style.display = 'block';
          tooltip.style.left = `${sx}px`;
          tooltip.style.top = `${sy}px`;
          tooltip.innerHTML = `
            <strong>${escapeHtml(hit.label)}</strong> &bull; <span style="color: ${hit.color}">${hit.type.toUpperCase()}</span><br>
            <span style="font-size: 0.72rem; opacity: 0.85;">${hit.articles.length} dispatches &bull; ${hit.connections} ties</span>
          `;
        } else if (tooltip) {
          tooltip.style.display = 'none';
        }
      } else {
        this.hoveredNode = null;
        if (tooltip) tooltip.style.display = 'none';
      }
    });

    window.addEventListener('pointerup', (e) => {
      if (!this.isRunning) return;
      const rect = canvas.getBoundingClientRect();
      const sx = e.clientX - rect.left;
      const sy = e.clientY - rect.top;
      const moved = Math.hypot(sx - downPos.x, sy - downPos.y);

      if (this.draggedNode) {
        if (moved < 6) {
          this.selectNode(this.draggedNode);
        }
        this.draggedNode = null;
      } else if (this.isDraggingCamera) {
        this.isDraggingCamera = false;
      }
    });

    canvas.addEventListener('wheel', (e) => {
      e.preventDefault();
      const zoomFactor = e.deltaY < 0 ? 1.15 : 0.87;
      const newZoom = Math.max(0.25, Math.min(3.5, this.camera.zoom * zoomFactor));

      const rect = canvas.getBoundingClientRect();
      const sx = e.clientX - rect.left;
      const sy = e.clientY - rect.top;
      const worldBefore = this.toWorld(sx, sy);

      this.camera.zoom = newZoom;
      const worldAfter = this.toWorld(sx, sy);

      this.camera.x += (worldAfter.x - worldBefore.x);
      this.camera.y += (worldAfter.y - worldBefore.y);
      this.alpha = 0.2;
    }, { passive: false });
  }

  selectNode(node) {
    this.selectedNode = node;
    const inspector = document.getElementById('constellationInspector');
    const badge = document.getElementById('inspectorBadge');
    const title = document.getElementById('inspectorTitle');
    const stats = document.getElementById('inspectorStats');
    const list = document.getElementById('inspectorDispatchesList');

    if (!inspector || !node) return;

    if (badge) {
      badge.textContent = node.type.toUpperCase();
      badge.style.color = node.color;
    }
    if (title) title.textContent = node.label;
    if (stats) stats.textContent = `${node.articles.length} Connected Stories • ${node.connections} Cross-Entity Ties`;

    if (list) {
      const artMap = new Map();
      (state.articles || []).forEach(a => artMap.set(a.id, a));
      const connectedArticles = node.articles.map(id => artMap.get(id)).filter(Boolean);

      list.innerHTML = connectedArticles.map(art => `
        <div class="inspector-dispatch-card" onclick="jumpToArticleFromConstellation('${escapeJs(art.id)}')">
          <div class="dispatch-card-meta">
            <span>${escapeHtml(art.source)}</span>
            <span>${escapeHtml(art.category)}</span>
          </div>
          <h5 class="dispatch-card-title">${escapeHtml(art.title)}</h5>
          <span class="dispatch-jump-action">Open Dispatch in Reader Modal ↗</span>
        </div>
      `).join('');
    }

    inspector.style.display = 'flex';
    this.alpha = 0.2;
  }
}

let _activeConstellationSim = null;

function openConstellationModal() {
  const modal = document.getElementById('constellationModalBackdrop');
  const canvas = document.getElementById('constellationCanvas');
  const container = document.getElementById('constellationCanvasContainer');
  if (!modal || !canvas || !container) return;

  // Close tools popover if open
  const toolsDropdown = document.getElementById('headerToolsDropdown');
  if (toolsDropdown) toolsDropdown.classList.remove('active');

  modal.style.display = 'flex';
  modal.classList.add('active');
  document.body.classList.add('modal-open');

  // Compute Retina resolution
  const dpr = window.devicePixelRatio || 1;
  const width = container.clientWidth || (window.innerWidth * 0.94);
  const height = container.clientHeight || (window.innerHeight * 0.78);

  canvas.width = width * dpr;
  canvas.height = height * dpr;
  canvas.style.width = `${width}px`;
  canvas.style.height = `${height}px`;

  const ctx = canvas.getContext('2d');
  ctx.scale(dpr, dpr);

  const graphData = buildKnowledgeGraph(state.articles);

  const statsLabel = document.getElementById('constellationStatsLabel');
  if (statsLabel) {
    statsLabel.textContent = `${graphData.nodes.length} Key Entities • ${graphData.edges.length} Cross-Entity Ties • Pure Canvas 2D Force Engine`;
  }

  if (_activeConstellationSim) {
    _activeConstellationSim.stop();
  }

  _activeConstellationSim = new ConstellationSimulation(canvas, graphData);
  _activeConstellationSim.start();
  _activeConstellationSim.fitToScreen();

  state.constellation.modalOpen = true;
}

function closeConstellationModal() {
  const modal = document.getElementById('constellationModalBackdrop');
  if (modal) {
    modal.classList.remove('active');
    modal.style.display = 'none';
  }
  document.body.classList.remove('modal-open');

  if (_activeConstellationSim) {
    _activeConstellationSim.stop();
  }
  state.constellation.modalOpen = false;

  const inspector = document.getElementById('constellationInspector');
  if (inspector) inspector.style.display = 'none';
}

function jumpToArticleFromConstellation(artId) {
  closeConstellationModal();
  openModal(artId);
}

function setupKnowledgeConstellation() {
  const openBtn = document.getElementById('constellationMapBtn');
  if (openBtn) {
    openBtn.addEventListener('click', (e) => {
      e.preventDefault();
      openConstellationModal();
    });
  }

  const closeBtn = document.getElementById('constellationCloseBtn');
  if (closeBtn) {
    closeBtn.addEventListener('click', (e) => {
      e.preventDefault();
      closeConstellationModal();
    });
  }

  const zoomInBtn = document.getElementById('constellationZoomInBtn');
  if (zoomInBtn) {
    zoomInBtn.addEventListener('click', () => {
      if (_activeConstellationSim) {
        _activeConstellationSim.camera.zoom = Math.min(3.5, _activeConstellationSim.camera.zoom * 1.25);
        _activeConstellationSim.alpha = 0.2;
      }
    });
  }

  const zoomOutBtn = document.getElementById('constellationZoomOutBtn');
  if (zoomOutBtn) {
    zoomOutBtn.addEventListener('click', () => {
      if (_activeConstellationSim) {
        _activeConstellationSim.camera.zoom = Math.max(0.25, _activeConstellationSim.camera.zoom / 1.25);
        _activeConstellationSim.alpha = 0.2;
      }
    });
  }

  const fitBtn = document.getElementById('constellationFitBtn');
  if (fitBtn) {
    fitBtn.addEventListener('click', () => {
      if (_activeConstellationSim) {
        _activeConstellationSim.fitToScreen();
      }
    });
  }

  const inspectorCloseBtn = document.getElementById('inspectorCloseBtn');
  if (inspectorCloseBtn) {
    inspectorCloseBtn.addEventListener('click', () => {
      const inspector = document.getElementById('constellationInspector');
      if (inspector) inspector.style.display = 'none';
      if (_activeConstellationSim) _activeConstellationSim.selectedNode = null;
    });
  }

  // Legend pill filter toggling
  const legend = document.getElementById('constellationLegend');
  if (legend) {
    legend.addEventListener('click', (e) => {
      const pill = e.target.closest('.legend-pill');
      if (!pill) return;
      const type = pill.getAttribute('data-type') || 'all';
      legend.querySelectorAll('.legend-pill').forEach(p => p.classList.remove('active'));
      pill.classList.add('active');

      if (_activeConstellationSim) {
        _activeConstellationSim.activeTypeFilter = type;
        _activeConstellationSim.alpha = 0.25;
      }
    });
  }

  // Dismiss on backdrop click
  const modal = document.getElementById('constellationModalBackdrop');
  if (modal) {
    modal.addEventListener('click', (e) => {
      if (e.target === modal) {
        closeConstellationModal();
      }
    });
  }
}

// Global interface bindings for M4
window.curateFocusDocket = curateFocusDocket;
window.startFocusSession = startFocusSession;
window.toggleFocusPause = toggleFocusPause;
window.completeFocusSession = completeFocusSession;
window.exitFocusSession = exitFocusSession;
window.copyFocusSessionMarkdown = copyFocusSessionMarkdown;
window.setupFocusSession = setupFocusSession;

window.buildKnowledgeGraph = buildKnowledgeGraph;
window.ConstellationSimulation = ConstellationSimulation;
window.openConstellationModal = openConstellationModal;
window.closeConstellationModal = closeConstellationModal;
window.jumpToArticleFromConstellation = jumpToArticleFromConstellation;
window.setupKnowledgeConstellation = setupKnowledgeConstellation;



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
  const googleRssUrl = 'https://news.google.com/rss/search?q=' + encodedQuery + '&hl=en-US&gl=US&ceid=US:en';
  const proxyUrl = 'https://api.rss2json.com/v1/api.json?rss_url=' + encodeURIComponent(googleRssUrl);

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
          why: cleanDesc || ''
        },
        readTime: '3 min read',
        relatedSources: [
          { name: pubName, url: item.link },
          { name: 'Google News', url: 'https://news.google.com/search?q=' + encodedQuery }
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
  let list = state.articles.filter(a => !a.is_duplicate);
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

  const metabolism = computeStoryMetabolism(art);

  let intelBadges = '';
  if (art.meta) {
    if (art.meta.is_black_swan) intelBadges += '<span class="intel-badge black-swan" title="Anomalous event with high impact">🦢 Black Swan</span>';
    if (art.meta.is_contrarian) intelBadges += '<span class="intel-badge contrarian" title="Contradicts prevailing narrative">⚡ Contrarian</span>';
    if (art.meta.is_exclusive) intelBadges += '<span class="intel-badge exclusive" title="Original reporting">💎 Exclusive</span>';
  }
  if (art.resonant_podcast) {
    intelBadges += `<span class="intel-badge podcast" title="Listen to related podcast">🎧 Resonates in Podcast</span>`;
  }
  if ((art.narrative_arc && art.narrative_arc.arc_id) || art.arc_id) {
    intelBadges += '<span class="intel-badge halflife-arc" title="Ongoing multi-day developing story arc">📅 Developing Arc</span>';
  } else if (art.scores && typeof art.scores.temporal === 'number') {
    if (art.scores.temporal >= 0.85) {
      intelBadges += '<span class="intel-badge halflife-flash" title="Story half-life: Flash event (< 6h)">⚡ Breaking</span>';
    } else if (art.scores.temporal >= 0.6) {
      intelBadges += '<span class="intel-badge halflife-daily" title="Story half-life: 24h Daily News Cycle">📰 Daily Cycle</span>';
    } else {
      intelBadges += '<span class="intel-badge halflife-epoch" title="Story half-life: Macro structural event">🏛️ Macro Focus</span>';
    }
  }
  const isDocketRead = !!(state.focusSession && state.focusSession.active && state.focusSession.readIds && state.focusSession.readIds.has(art.id));
  const docketReadClass = isDocketRead ? ' docket-read-card' : '';
  if (isDocketRead) {
    intelBadges += '<span class="docket-read-badge">✓ Reviewed</span>';
  }
  const badgesHTML = intelBadges ? `<div class="intel-badge-row">${intelBadges}</div>` : '';
  const hasPrism = hasPerspectivePrism(art);
  const sourcesCount = (art.storyCluster && art.storyCluster.size) || 
                       (art.perspectives && art.perspectives.length) || 
                       (art.meta && art.meta.is_exclusive ? 1 : 2);

  let prismToggleBtnHTML = '';
  let prismDrawerHTML = '';
  if (hasPrism) {
    const contrarianBadge = (art.meta && art.meta.is_contrarian) ? '<span class="prism-contrarian-badge mini">Contrarian</span>' : '';
    const exclusiveBadge = (art.meta && art.meta.is_exclusive) ? '<span class="prism-exclusive-badge mini">Exclusive</span>' : '';
    const btnClass = 'prism-toggle-btn' + ((art.meta && art.meta.is_contrarian) ? ' has-contrarian' : '');
    prismToggleBtnHTML = '<button class="' + btnClass + '" onclick="event.stopPropagation(); toggleCardPrismDrawer(\'' + art.id + '\', event);" title="Toggle Perspective Spectrum (' + sourcesCount + ' viewpoints)" aria-label="Toggle Perspective Spectrum"><span class="prism-btn-icon">💎</span><span class="prism-btn-text">Spectrum (' + sourcesCount + ')</span>' + contrarianBadge + exclusiveBadge + '</button>';
    prismDrawerHTML = '<div class="card-prism-drawer" id="prism-drawer-' + art.id + '" style="display: none;"></div>';
  }

  const hasValidAnnotation = !!(art.annotation && art.annotation.what && art.annotation.what.trim().toLowerCase() !== (art.title || '').trim().toLowerCase());
  const noAnnotationClass = hasValidAnnotation ? '' : ' no-annotation';
  const annotationBoxHTML = hasValidAnnotation
    ? ('<div class="annotation-box">' +
        '<div class="annotation-title">✦ Crisp Annotation (' + escapeHtml(art.region) + ')</div>' +
        '<p class="annotation-bullet">' + escapeHtml(art.annotation.what) + '</p>' +
      '</div>')
    : '';

  return `
    <article class="news-card${docketReadClass}${noAnnotationClass}" data-id="${art.id}" data-article-id="${art.id}" style="animation-delay: ${delay}s; --card-index: ${idx};" onclick="openModal('${art.id}')">
      <div class="card-sheen"></div>
      <div class="card-thumb-box">
        <img src="${imgUrl}" alt="${escapeHtml(art.title)}" class="card-thumb" width="640" height="360" loading="lazy" decoding="async" onerror="this.onerror=null; this.src=getTopicImageUrl('${escapeJs(art.title)}', '${escapeJs(art.category)}', '${escapeJs(art.region)}');" />
        <span class="card-category">${art.category}</span>
        <button class="bookmark-btn ${saved ? 'saved' : ''}" onclick="toggleBookmark('${art.id}', event)" title="Save Article" aria-label="Save Article">
          ${saved ? '★' : '☆'}
        </button>
      </div>

      <div class="card-content">
        ${badgesHTML}
        <div class="card-meta">
          <span class="card-source">${art.sourceLogo} &bull; ${art.source}</span>
          <div class="metabolism-sparkline sparkline-box sparkline-container ${metabolism.status}" title="${escapeHtml(metabolism.tooltip)}" aria-label="${escapeHtml(metabolism.tooltip)}" tabindex="0">
            <svg class="sparkline-svg" width="56" height="18" viewBox="0 0 56 18" aria-hidden="true" focusable="false">
              <defs>
                <linearGradient id="spark-grad-${escapeHtml(art.id)}" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stop-color="${metabolism.color}" stop-opacity="0.35" />
                  <stop offset="100%" stop-color="${metabolism.color}" stop-opacity="0.0" />
                </linearGradient>
              </defs>
              <path d="${metabolism.areaD}" fill="url(#spark-grad-${escapeHtml(art.id)})" />
              <path d="${metabolism.pathD}" fill="none" stroke="${metabolism.color}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" />
              <circle cx="${metabolism.lastX}" cy="${metabolism.lastY}" r="2" fill="${metabolism.color}" class="sparkline-pulse-dot" />
            </svg>
            <span class="metabolism-label sparkline-tooltip-label" style="color: ${metabolism.color};">${metabolism.label}</span>
            <span class="sparkline-tooltip">${escapeHtml(metabolism.tooltip)}</span>
          </div>
          <span>${art.readTime}</span>
        </div>
        <h3 class="card-title">${escapeHtml(art.title)}</h3>

        <!-- Crisp Annotation Preview -->
        ${annotationBoxHTML}

        <!-- R3 Deep Dive Intelligence Panel (Expanded in Deep Dive mode) -->
        <div class="card-deep-dive-panel">
          ${renderDeepDivePanelContent(art)}
        </div>

        <!-- Streamlined Card Actions: Executive Brief + Source Link + Perspective Prism Drawer Toggle -->
        <div class="card-footer" style="display: flex; align-items: center; justify-content: space-between; gap: 0.5rem; margin-top: auto; padding-top: 0.8rem; border-top: 1px solid var(--border-color);">
          <div style="display: flex; align-items: center; gap: 0.45rem; flex-wrap: wrap;">
            <span class="card-read-cue" style="display: inline-flex; align-items: center; gap: 0.35rem; font-size: 0.78rem; font-weight: 700; color: var(--accent-cyan); letter-spacing: 0.04em;">
              ✦ Executive Brief
            </span>
            ${prismToggleBtnHTML}
          </div>
          <a href="${art.link}" target="_blank" rel="noopener noreferrer" class="btn-secondary" style="padding: 0.38rem 0.85rem; font-size: 0.78rem; color: var(--text-primary); border: 1px solid var(--border-color); border-radius: var(--radius-full);" onclick="event.stopPropagation()" title="Read Full Story directly on ${art.source}" aria-label="Read full story on source">
            Source ↗
          </a>
        </div>

        ${prismDrawerHTML}
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

  // Synchronize cognitive load density mode (R3)
  const currentDensity = state.densityMode || 'digest';
  if (newsGrid && !newsGrid.classList.contains(`density-${currentDensity}`)) {
    newsGrid.classList.remove('density-scan', 'density-digest', 'density-deep');
    newsGrid.classList.add(`density-${currentDensity}`);
  }

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
  // LIQUID MORPHING TRANSITION: Capture old card positions for FLIP animation
  const oldCards = newsGrid.querySelectorAll('.news-card[data-id]');
  const oldPositions = new Map();
  const oldScrollY = window.scrollY;
  oldCards.forEach(card => {
    const id = card.getAttribute('data-id');
    const rect = card.getBoundingClientRect();
    // Save absolute document position to survive scroll jumps
    oldPositions.set(id, { top: rect.top + oldScrollY, left: rect.left, width: rect.width, height: rect.height });
  });

  newsGrid.classList.add('morphing-active');
  newsGrid.innerHTML = gridHTML;

  // FLIP Phase: Animate persisted cards from old position, crystallize new cards
  requestAnimationFrame(() => {
    const newCards = newsGrid.querySelectorAll('.news-card[data-id]');
    newCards.forEach(card => {
      const id = card.getAttribute('data-id');
      if (oldPositions.has(id)) {
        // Persisted card: FLIP from old to new position
        const oldPos = oldPositions.get(id);
        const newRect = card.getBoundingClientRect();
        
        // Calculate absolute deltas
        const newAbsoluteTop = newRect.top + window.scrollY;
        const deltaX = oldPos.left - newRect.left;
        const deltaY = oldPos.top - newAbsoluteTop;
        
        // Suppress the default CSS entrance animation
        card.style.animation = 'none';

        if (Math.abs(deltaX) > 1 || Math.abs(deltaY) > 1) {
          card.style.zIndex = '20';
          
          // Use Web Animations API (WAAPI) for bulletproof FLIP
          const flipAnimation = card.animate([
            { transform: `translate(${deltaX}px, ${deltaY}px)` },
            { transform: 'translate(0px, 0px)' }
          ], {
            duration: 750,
            easing: 'cubic-bezier(0.34, 1.56, 0.64, 1)',
            fill: 'both' // Ensures it stays at final state until cleared
          });

          flipAnimation.onfinish = () => {
            card.style.zIndex = '';
            // Clear the animation fill so natural CSS takes over
            flipAnimation.cancel();
          };
        }
      } else if (oldPositions.size > 0) {
        // New card: dramatic crystallize entrance (staggered)
        card.classList.add('morph-entering');
        card.addEventListener('animationend', function handler() {
          card.classList.remove('morph-entering');
          card.removeEventListener('animationend', handler);
        });
      }
    });
    setTimeout(() => newsGrid.classList.remove('morphing-active'), 800);
  });

  attach3DTiltListeners();

  // Suppress infinite scroll sentinel and observer if Focus Session is active (R5)
  if (state.focusSession && state.focusSession.active) {
    return;
  }

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
  const cards = document.querySelectorAll('.news-card:not([data-tilt-ready]), .thought-card:not([data-tilt-ready])');
  cards.forEach(card => {
    card.setAttribute('data-tilt-ready', 'true');
    card.addEventListener('mousemove', (e) => {
      if (window.matchMedia && window.matchMedia('(pointer: coarse)').matches) return;
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
    if (index === -1) {
      // Fallback: check if id matches a resonant_news item in state.podcasts
      if (state.podcasts && Array.isArray(state.podcasts)) {
        for (const ep of state.podcasts) {
          if (ep.resonant_news && Array.isArray(ep.resonant_news)) {
            const rn = ep.resonant_news.find(item => item.id === id);
            if (rn) {
              const syntheticArticle = {
                id: rn.id,
                title: rn.title,
                source: rn.source || 'Resonant Wire',
                category: ep.category || 'Tech',
                region: 'Global',
                publishedAt: ep.pubDate || new Date().toISOString(),
                imageUrl: ep.imageUrl || '',
                link: rn.url || rn.link || ep.link || '#',
                description: `Resonant analysis linked with deep-dive podcast "${ep.title}" (${ep.podcast}).`,
                annotation: {
                  what: rn.title,
                  why: `Explored in discussion during ${ep.podcast} episode "${ep.title}".`
                },
                relatedSources: [],
                resonant_podcast: {
                  id: ep.id,
                  title: ep.title,
                  episode_title: ep.title,
                  podcast: ep.podcast,
                  podcast_title: ep.podcast,
                  link: ep.link,
                  youtube_url: ep.link,
                  resonance_score: rn.resonance_score || rn.relevance || 0.8
                },
                narrative_arc: { arc_id: null }
              };
              state.modalState.articles = [syntheticArticle];
              state.modalState.currentIndex = 0;
              document.body.classList.add('modal-open');
              // Focus trap: make background inert
              if (document.getElementById('mainContent')) {
                document.getElementById('mainContent').setAttribute('inert', '');
              }
              if (document.getElementById('siteHeader')) {
                document.getElementById('siteHeader').setAttribute('inert', '');
              }
              const card = document.querySelector('.deck-modal-card');
              if (card) {
                card.style.transform = '';
                card.style.transition = '';
              }
              renderExecutiveModal();
              modalBackdrop.classList.add('active');
              return;
            }
          }
        }
      }
      if (typeof showToastNotification === 'function') {
        showToastNotification('Article is no longer available in the active feed.');
      }
      return;
    }
    state.modalState.articles = state.articles;
    state.modalState.currentIndex = index;
  } else {
    state.modalState.articles = pool;
    state.modalState.currentIndex = index;
  }

  // Track read progress for executive focus session (R5)
  if (state.focusSession && state.focusSession.active && state.focusSession.docket) {
    if (state.focusSession.docket.some(a => a.id === id)) {
      state.focusSession.readIds.add(id);
      if (typeof updateFocusTimerDisplay === 'function') {
        updateFocusTimerDisplay();
      }
      const domCard = document.querySelector(`.news-card[data-id="${id}"]`);
      if (domCard && !domCard.classList.contains('docket-read-card')) {
        domCard.classList.add('docket-read-card');
        const contentDiv = domCard.querySelector('.card-content');
        if (contentDiv && !contentDiv.querySelector('.docket-read-badge')) {
          const rBadge = document.createElement('span');
          rBadge.className = 'docket-read-badge';
          rBadge.textContent = '✓ Reviewed';
          contentDiv.insertBefore(rBadge, contentDiv.firstChild);
        }
      }
      if (state.focusSession.readIds.size >= state.focusSession.docket.length) {
        state.focusSession.allRead = true;
      }
    }
  }

  document.body.classList.add('modal-open');
  // Focus trap: make background inert
  if (document.getElementById('mainContent')) {
    document.getElementById('mainContent').setAttribute('inert', '');
  }
  if (document.getElementById('siteHeader')) {
    document.getElementById('siteHeader').setAttribute('inert', '');
  }
  const card = document.querySelector('.deck-modal-card');
  if (card) {
    card.style.transform = '';
    card.style.transition = '';
  }
  renderExecutiveModal();
  modalBackdrop.classList.add('active');
};

// STRUCTURED INTELLIGENCE ATOM VIEW GENERATOR
function renderStructuredIntelligenceView(art, themeColor) {
  if (!art) return '';

  const entities = art.entities || {};
  const leaders = (entities.leaders || []).map(l => l.name || l).join(', ');
  const orgs = (entities.organizations || []).map(o => o.name || o).join(', ');
  const countries = (entities.countries || []).map(c => c.name || c.code || c).join(', ');
  const companies = (entities.companies || []).map(c => c.name || c).join(', ');
  const actions = (entities.actions || []).join(', ');

  // Compute Primary Actors cleanly from genuine 5W1H grammar contracts
  const actors = art.primary_actors || (art.entities && art.entities.primary_actors) || null;
  let primaryActorsHtml = '';

  if (actors) {
    if (actors.active_agent) {
      const agentType = actors.active_agent_type || 'primary';
      primaryActorsHtml += `<div><strong>Active Agent:</strong> <span class="actor-name">${escapeHtml(actors.active_agent)}</span> <span class="actor-type-pill ${escapeHtml(agentType)}">${escapeHtml(agentType)}</span></div>`;
    } else if (leaders) {
      primaryActorsHtml += '<div><strong>Leaders:</strong> ' + escapeHtml(leaders) + '</div>';
    } else if (orgs) {
      primaryActorsHtml += '<div><strong>Organizations:</strong> ' + escapeHtml(orgs) + '</div>';
    } else {
      primaryActorsHtml += '<div><strong>Active Agent:</strong> <span class="actor-null-label">Unattributed Dispatch</span></div>';
    }

    if (actors.impacted_population) {
      primaryActorsHtml += `<div><strong>Impacted Population:</strong> ${escapeHtml(actors.impacted_population)} <span class="actor-type-pill impacted">${escapeHtml(actors.impacted_type || 'community')}</span></div>`;
    }

    if (Array.isArray(actors.collective_factions) && actors.collective_factions.length > 0) {
      const factionsText = actors.collective_factions.map(f => f.canonical_label || f.matched_text).join(', ');
      primaryActorsHtml += `<div><strong>Collective Factions:</strong> ${escapeHtml(factionsText)}</div>`;
    }

    if (Array.isArray(actors.sovereign_stakeholders) && actors.sovereign_stakeholders.length > 0) {
      primaryActorsHtml += `<div><strong>Sovereign Stakeholders:</strong> ${escapeHtml(actors.sovereign_stakeholders.join(', '))}</div>`;
    } else if (art.region && art.region !== 'Global') {
      primaryActorsHtml += `<div><strong>Regional Stakeholder:</strong> ${escapeHtml(art.region)} sovereign arena</div>`;
    }

    if (actors.syntactic_frame && actors.syntactic_frame.verb && (actors.syntactic_frame.subject || actors.syntactic_frame.object)) {
      primaryActorsHtml += `<div class="syntactic-frame-pill"><span class="frame-label">Frame:</span> <code>[${escapeHtml(actors.syntactic_frame.subject || 'Agent')}]</code> <strong>${escapeHtml(actors.syntactic_frame.verb)}</strong> <code>[${escapeHtml(actors.syntactic_frame.object || 'Target')}]</code></div>`;
    }
  } else {
    if (leaders) primaryActorsHtml += '<div><strong>Leaders:</strong> ' + escapeHtml(leaders) + '</div>';
    if (orgs) primaryActorsHtml += '<div><strong>Organizations:</strong> ' + escapeHtml(orgs) + '</div>';
    if (companies) primaryActorsHtml += '<div><strong>Companies:</strong> ' + escapeHtml(companies) + '</div>';
    if (!leaders && !orgs && !companies) {
      if (countries) {
        primaryActorsHtml += '<div><strong>Regional Stakeholders:</strong> ' + escapeHtml(countries) + ' domestic factions</div>';
      } else {
        primaryActorsHtml += '<div><strong>Active Agent:</strong> <span class="actor-null-label">Unattributed Dispatch</span></div>';
      }
    }
  }

  // Quarantine wire source strictly to subordinate provenance ledger:
  primaryActorsHtml += '<div class="subordinate-provenance-ledger">📡 Chronicled by ' + escapeHtml(art.source || 'Primary Source') + '</div>';

  const cognitiveType = (art.cognitive_type || 'strategic').toUpperCase();
  const temporalScore = (art.scores && typeof art.scores.temporal === 'number')
    ? (art.scores.temporal >= 0.85 ? '⚡ Breaking Flash (< 6h)' : (art.scores.temporal >= 0.6 ? '📰 24h Daily Cycle' : '🏛️ Multi-Week Macro Epoch'))
    : '📰 Daily Cycle';

  const compositeScore = (art.scores && typeof art.scores.composite === 'number')
    ? (art.scores.composite * 10).toFixed(1) + ' / 10'
    : (typeof art.importance_score === 'number' ? art.importance_score.toFixed(1) + ' / 10' : 'Unscored');

  const hasWhy = !!(art.annotation && art.annotation.why && art.annotation.why.trim().length > 0);
  const coreEventClass = hasWhy ? 'intel-atom-card' : 'intel-atom-card atom-hero atom-span-2';
  const gridMorphologyClass = hasWhy ? 'morphology-6col' : 'morphology-standalone morphology-5col';

  const strategicContextHtml = hasWhy
    ? ('<div class="intel-atom-card">' +
        '<span class="intel-atom-label">💡 STRATEGIC CONTEXT (WHY)</span>' +
        '<div class="intel-atom-body">' +
          escapeHtml(art.annotation.why) +
        '</div>' +
      '</div>')
    : '';

  const hasArc = !!(art.narrative_arc && art.narrative_arc.arc_id);
  const arcTitleHtml = (hasArc && art.narrative_arc.arc_title)
    ? ('<br><strong>Active Arc:</strong> ' + escapeHtml(art.narrative_arc.arc_title))
    : '';
  const horizonBodyHtml = hasArc
    ? (temporalScore + arcTitleHtml)
    : ('<div class="horizon-standalone-badge">✦ Standalone Dispatch</div>' +
       '<div class="horizon-standalone-detail">' + temporalScore + ' · Discrete Single-Event Horizon</div>');

  const domainStripHtml = art.category
    ? ('<span>✦ <strong>Domain:</strong> ' + escapeHtml(art.category) + '</span>')
    : '';

  return `
    <div class="structured-intel-grid ${gridMorphologyClass}">
      <div class="${coreEventClass}">
        <span class="intel-atom-label">⚡ CORE EVENT (WHAT)</span>
        <div class="intel-atom-body">
          ${escapeHtml(art.annotation ? art.annotation.what : art.title)}
          ${actions ? ('<div style="margin-top: 0.35rem; font-size: 0.78rem; color: ' + themeColor + ';">✦ Vector Actions: ' + escapeHtml(actions) + '</div>') : ''}
        </div>
      </div>

      <div class="intel-atom-card">
        <span class="intel-atom-label">🎯 PRIMARY ACTORS (WHO)</span>
        <div class="intel-atom-body">
          ${primaryActorsHtml}
        </div>
      </div>

      <div class="intel-atom-card">
        <span class="intel-atom-label">🌐 GEOPOLITICAL THEATER (WHERE)</span>
        <div class="intel-atom-body">
          <strong>Region:</strong> ${escapeHtml(art.region || 'Global')}
          ${countries ? ('<br><strong>Nations Involved:</strong> ' + escapeHtml(countries)) : ''}
        </div>
      </div>

      ${strategicContextHtml}

      <div class="intel-atom-card">
        <span class="intel-atom-label">🧠 COGNITIVE MATRIX</span>
        <div class="intel-atom-body" style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.5rem;">
          <span><strong>Dimension:</strong> ${cognitiveType}</span>
          <span><strong>Signal Power:</strong> <span style="color: ${themeColor}; font-weight: 800;">${compositeScore}</span></span>
        </div>
      </div>

      <div class="intel-atom-card">
        <span class="intel-atom-label">⏳ STORY HORIZON & HALF-LIFE</span>
        <div class="intel-atom-body">
          ${horizonBodyHtml}
        </div>
      </div>

      <div class="structured-intel-provenance-strip">
        <span>📡 <strong>Reporting Provenance:</strong> Chronicled by ${escapeHtml(art.source || 'Primary Source')}</span>
        ${domainStripHtml}
        <span>✦ <strong>Integrity:</strong> Zero-Hallucination Verified</span>
      </div>
    </div>
  `;
}

window.switchDeckView = function(view) {
  const btnNarr = document.getElementById('deckViewBtnNarrative');
  const btnIntel = document.getElementById('deckViewBtnIntel');
  const viewNarr = document.getElementById('deckNarrativeView');
  const viewIntel = document.getElementById('deckStructuredView');

  if (view === 'intel') {
    if (btnNarr) {
      btnNarr.classList.remove('active');
      btnNarr.setAttribute('aria-selected', 'false');
    }
    if (btnIntel) {
      btnIntel.classList.add('active');
      btnIntel.setAttribute('aria-selected', 'true');
    }
    if (viewNarr) viewNarr.style.display = 'none';
    if (viewIntel) viewIntel.style.display = 'block';
  } else {
    if (btnIntel) {
      btnIntel.classList.remove('active');
      btnIntel.setAttribute('aria-selected', 'false');
    }
    if (btnNarr) {
      btnNarr.classList.add('active');
      btnNarr.setAttribute('aria-selected', 'true');
    }
    if (viewIntel) viewIntel.style.display = 'none';
    if (viewNarr) viewNarr.style.display = 'block';
  }
};

function renderExecutiveModal(artParam) {
  const pool = state.modalState.articles;
  const currIdx = state.modalState.currentIndex;
  const total = pool.length || (artParam ? 1 : 0);
  const art = artParam || pool[currIdx];
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
    // If it already ends with sentence-ending punctuation, preserve it fully
    if (/[.!?]["'”’]?$/.test(s)) {
      if (s.endsWith('...') || s.endsWith('…')) {
        s = s.replace(/[\s\.\-–—…]+$/, '').trim();
        const lastPeriod = Math.max(s.lastIndexOf('.'), s.lastIndexOf('?'), s.lastIndexOf('!'));
        if (lastPeriod > 50) {
          s = s.slice(0, lastPeriod + 1);
        } else if (s) {
          s += '.';
        }
      }
      return s;
    }
    // For texts without terminal punctuation, clean cut-off fragments and terminate cleanly
    s = s.replace(/[\s\.\-–—…]+$/, '').trim();
    return s ? (s + '.') : '';
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
    const synopsisItems = [];
    if (art.annotation && art.annotation.what && art.annotation.what !== titleText) {
      synopsisItems.push(`<li><strong>Core Event:</strong> ${escapeHtml(art.annotation.what)}</li>`);
    }
    const actors = art.primary_actors || (art.entities && art.entities.primary_actors);
    if (actors && actors.active_agent) {
      synopsisItems.push(`<li><strong>Active Agent:</strong> ${escapeHtml(actors.active_agent)} <span class="actor-type-pill ${escapeHtml(actors.active_agent_type || 'primary')}">${escapeHtml(actors.active_agent_type || 'primary')}</span></li>`);
    } else if (actors && actors.syntactic_frame && actors.syntactic_frame.subject) {
      synopsisItems.push(`<li><strong>Focal Subject:</strong> ${escapeHtml(actors.syntactic_frame.subject)}</li>`);
    }
    if (actors && Array.isArray(actors.collective_factions) && actors.collective_factions.length > 0) {
      const factions = actors.collective_factions.map(f => f.canonical_label || f.matched_text).slice(0, 2).join(', ');
      synopsisItems.push(`<li><strong>Factions Involved:</strong> ${escapeHtml(factions)}</li>`);
    }
    if (art.region || art.category) {
      synopsisItems.push(`<li><strong>Geopolitical Context:</strong> ${escapeHtml(art.category || 'World')} affairs in ${escapeHtml(art.region || 'Global arena')}.</li>`);
    }
    if (art.source) {
      synopsisItems.push(`<li><strong>Reporting Provenance:</strong> Chronicled by ${escapeHtml(art.source)}.</li>`);
    }

    storyBodyHtml = `
      <div style="display: flex; flex-direction: column; gap: 1.1rem;">
        <p style="font-size: 1.08rem; color: var(--text-primary); line-height: 1.8; margin: 0; font-weight: 500;">
          ${storyText && storyText !== titleText ? storyText : titleText + '.'}
        </p>

        <div class="executive-synopsis-box" style="background: ${themeColor}0a; border-left: 3px solid ${themeColor}; padding: 1rem 1.2rem; border-radius: 0 var(--radius-sm) var(--radius-sm) 0;">
          <span style="font-size: 0.72rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.08em; color: ${themeColor}; display: block; margin-bottom: 0.3rem;">
            ✦ Executive Intelligence Synopsis
          </span>
          <ul style="margin: 0; padding-left: 1.1rem; color: var(--text-secondary); font-size: 0.94rem; line-height: 1.65;">
            ${synopsisItems.join('\n            ')}
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
  const hasArc = !!(art.narrative_arc && art.narrative_arc.arc_id);
  if (!hasArc) {
    window._activeNarrativeChapters = [];
    window._activeNarrativeIndex = -1;
  }

  const narrativeBoxHTML = hasArc
    ? ('<div class="liquid-glass-narrative-box">' +
        '<span class="narrative-box-icon">📖</span>' +
        '<div class="narrative-box-content">' +
          '<span class="narrative-box-label">Ongoing Narrative Arc · Day ' + (art.narrative_arc.day_number || 1) + '</span>' +
          '<span class="narrative-box-title">' + escapeHtml(art.narrative_arc.arc_title || art.title) + '</span>' +
          '<span class="narrative-box-subtitle">Tracked across ' + (art.narrative_arc.total_chapters || 1) + ' updates</span>' +
        '</div>' +
      '</div>' +
      renderNarrativeTimeMachine(art))
    : '';
  const perspectivePrismHTML = hasPerspectivePrism(art) ? renderPerspectivePrism(art) : '';

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
        <button class="mobile-deck-bookmark ${saved ? 'saved' : ''}" onclick="toggleModalBookmark('${art.id}', event);" aria-label="Save story">
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

    <button class="liquid-glass-bookmark desktop-only-control ${saved ? 'saved' : ''}" onclick="toggleModalBookmark('${art.id}', event);" aria-label="Save story for later" title="Save story for later">
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
      <div class="deck-content-fade deck-content-body ${hasArc ? 'has-narrative-arc' : 'standalone-dispatch'}">

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

        <!-- Narrative Arc Indicator (if part of an active arc) with Narrative Time Machine -->
        ${narrativeBoxHTML}

        <!-- Resonant Podcast Deep-Dive Callout -->
        ${(art.resonant_podcast && (art.resonant_podcast.title || art.resonant_podcast.episode_title || art.resonant_podcast.podcast)) ? `
        <div class="liquid-glass-resonance-box">
          <div class="resonance-box-left">
            <span class="resonance-box-icon">🎧</span>
            <div>
              <span class="resonance-box-label">Resonates in Deep-Dive Podcast</span>
              <span class="resonance-box-title">${escapeHtml(art.resonant_podcast.title || art.resonant_podcast.episode_title || art.resonant_podcast.podcast)}</span>
              <span class="resonance-box-podcast">${escapeHtml(art.resonant_podcast.podcast || art.resonant_podcast.podcast_title || '')}</span>
            </div>
          </div>
          <a href="${art.resonant_podcast.link || art.resonant_podcast.youtube_url || '#'}" target="_blank" rel="noopener noreferrer" class="resonance-listen-btn">
            Listen Episode ↗
          </a>
        </div>
        ` : ''}

        <!-- Segmented Deck View Switcher (Executive Narrative vs Structured Intelligence) -->
        <div class="deck-view-switcher">
          <button id="deckViewBtnNarrative" class="deck-view-btn active" onclick="switchDeckView('narrative')">
            <span>📖</span> Executive Narrative
          </button>
          <button id="deckViewBtnIntel" class="deck-view-btn" onclick="switchDeckView('intel')">
            <span>📋</span> Structured Intelligence
          </button>
        </div>

        <!-- Story Body Panels -->
        <div id="deckNarrativeView" class="deck-view-panel active">
          <div id="deckKaraokeHighlightZone" style="color: var(--text-secondary); line-height: 1.85; margin-bottom: 2rem;">${storyBodyHtml}</div>
        </div>

        <div id="deckStructuredView" class="deck-view-panel" style="display: none; margin-bottom: 2rem;">
          ${renderStructuredIntelligenceView(art, themeColor)}
        </div>

        <!-- Hairline -->
        <div style="height: 1px; background: var(--border-color); margin-bottom: 1.4rem; opacity: 0.6;"></div>

        <!-- R2: Perspective Prism (Multi-Source Spectrum & Contrarian Signals) -->
        ${perspectivePrismHTML}

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

    scrollContainer.classList.add('deck-card-entering');
    scrollContainer.addEventListener('animationend', function handler() {
      scrollContainer.classList.remove('deck-card-entering');
      scrollContainer.removeEventListener('animationend', handler);
    });
    scrollContainer.scrollTop = 0;
  }

  // Setup mobile 1-finger horizontal touch swipe gestures (singleton registration)
  setupMobileDeckSwipe();
}

// ADVANCED CROSS-PLATFORM MOBILE TOUCH SWIPE ENGINE (iOS & Android)
function setupMobileDeckSwipe() {
  const card = document.querySelector('.deck-modal-card');
  if (!card || card.dataset.swipeInitialized) return;
  card.dataset.swipeInitialized = 'true';

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

    // Provide visual rubber-band preview only if gesture is predominantly horizontal
    if (Math.abs(diffX) > Math.abs(diffY) * 1.5 && Math.abs(diffX) > 20) {
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
    card.style.transition = 'transform 0.3s cubic-bezier(0.16, 1, 0.3, 1)';
    card.style.transform = '';
    setTimeout(() => {
      card.style.transition = '';
    }, 300);

    // Confirm horizontal swipe intent (min 45px horizontal diff, diffX > 1.5x diffY)
    if (Math.abs(diffX) > 45 && Math.abs(diffX) > Math.abs(diffY) * 1.5) {
      if (diffX < 0) {
        // Swiped left -> Next story (strictly sequential)
        navigateModal(1);
      } else {
        // Swiped right -> Previous story (strictly sequential)
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

// INLINE SPEAK ARTICLE — Bridge for modal "Listen" button to Speech Synthesis
window.speakArticle = function(text) {
  if (!('speechSynthesis' in window)) {
    if (typeof showToastNotification === 'function') {
      showToastNotification('🎙 Audio playback is not supported on this browser.');
    }
    return;
  }
  if (!text) return;
  window.speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.rate = 1.0;
  utterance.pitch = 1.0;
  utterance.lang = 'en-US';
  // Use a natural voice when available
  const voices = window.speechSynthesis.getVoices();
  const preferred = voices.find(v => v.lang.startsWith('en') && v.name.includes('Google')) ||
                    voices.find(v => v.lang.startsWith('en') && !v.localService) ||
                    voices.find(v => v.lang.startsWith('en'));
  if (preferred) utterance.voice = preferred;
  window.speechSynthesis.speak(utterance);
};

let isModalNavigating = false;
window.navigateModal = function(step) {
  if (isModalNavigating) return;
  const pool = state.modalState.articles;
  if (!pool || pool.length === 0) return;

  isModalNavigating = true;
  state.modalState.currentIndex = (state.modalState.currentIndex + step + pool.length) % pool.length;
  renderExecutiveModal();

  setTimeout(() => {
    isModalNavigating = false;
  }, 280);
};

window.closeModal = function() {
  document.body.classList.remove('modal-open');
  // Remove focus trap
  if (document.getElementById('mainContent')) {
    document.getElementById('mainContent').removeAttribute('inert');
  }
  if (document.getElementById('siteHeader')) {
    document.getElementById('siteHeader').removeAttribute('inert');
  }
  modalBackdrop.classList.remove('active');
  const card = document.querySelector('.deck-modal-card');
  if (card) {
    card.style.transform = '';
    card.style.transition = '';
  }

  // If focus session active and all docket stories read, show completion report
  if (state.focusSession && state.focusSession.active && state.focusSession.allRead) {
    completeFocusSession();
  }
};

window.toggleModalBookmark = function(id, event) {
  if (event) event.stopPropagation();
  toggleBookmark(id, event);
  const saved = isBookmarked(id);
  const mobileBtn = document.querySelector('.mobile-deck-bookmark');
  if (mobileBtn) {
    mobileBtn.classList.toggle('saved', saved);
    mobileBtn.innerHTML = saved ? '★ Saved' : '☆ Save';
  }
  const desktopBtn = document.querySelector('.liquid-glass-bookmark');
  if (desktopBtn) {
    desktopBtn.classList.toggle('saved', saved);
    desktopBtn.innerHTML = saved ? '★ Saved' : '☆ Save';
  }
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
  if (!('speechSynthesis' in window)) {
    if (typeof showToastNotification === 'function') {
      showToastNotification('🎙 Audio playback is not supported on this browser.');
    }
    return;
  }

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
// EXECUTIVE AUDIO DOSSIER — Structured broadcast intelligence
let _lastBroadcastCategory = '';
function generateHumanBroadcastScript(article, index, total) {
  if (!article) return 'No intelligence dispatches available.';

  const source = article.source || 'News Dispatches';
  const region = article.region || 'Global';
  const category = article.category || 'World';
  const title = (article.title || '').trim();

  let desc = (article.description || '').trim();
  if (/[.!?]["'”’]?$/.test(desc)) {
    if (desc.endsWith('...') || desc.endsWith('…')) {
      desc = desc.replace(/[\s\.\-–—…]+$/, '').trim();
      const lastPeriod = Math.max(desc.lastIndexOf('.'), desc.lastIndexOf('?'), desc.lastIndexOf('!'));
      if (lastPeriod > 40) {
        desc = desc.slice(0, lastPeriod + 1);
      } else if (desc) {
        desc += '.';
      }
    }
  } else {
    desc = desc.replace(/[\s\.\-–—…]+$/, '').trim();
    if (desc) desc += '.';
  }

  let text = '';

  // EXECUTIVE AUDIO DOSSIER: Structured opening for first story
  if (index === 0) {
    const now = new Date();
    const hour = now.getHours();
    const greeting = hour < 12 ? 'Good morning' : hour < 17 ? 'Good afternoon' : 'Good evening';
    const dateStr = now.toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' });
    text += `${greeting}. Today is ${dateStr}. `;
    text += `Here is your News Colossal Executive Briefing. ${total} stories selected for your attention. `;
    text += `... `;
  }

  // Category section transitions
  if (index === 0 || (index > 0 && article.category !== _lastBroadcastCategory)) {
    const categoryIntros = {
      'World': 'In critical global developments. ',
      'Tech': 'Now turning to technology and innovation. ',
      'Business': 'In business and market intelligence. ',
      'National': 'In national affairs. '
    };
    text += categoryIntros[category] || `In ${category} developments. `;
    _lastBroadcastCategory = category;
  }

  text += `Story ${index + 1} of ${total}. `;
  text += `From ${source}, covering ${region}. `;
  text += `${title}. `;
  if (desc && desc !== title) {
    text += `${desc} `;
  }

  // EXECUTIVE AUDIO DOSSIER: Structured closing for last story
  if (index === total - 1) {
    text += `... That concludes your News Colossal Executive Briefing. `;
    text += `${total} stories were analyzed from verified global sources. `;
    text += `Stay informed. Stay ahead.`;
  } else {
    text += `Full report available on ${source}.`;
  }

  return text;
}

// SMART CONVERSATIONAL RADIO BROADCASTER & CONTINUOUS AUTO-ADVANCE
window.playStoryAtIndex = function(index) {
  if (!('speechSynthesis' in window)) {
    if (typeof showToastNotification === 'function') {
      showToastNotification('🎙 Audio playback is not supported on this browser.');
    }
    return;
  }
  const activeList = getActiveFeedArticles();
  if (!activeList || activeList.length === 0) return;
  
  // Bound check
  const safeIdx = Math.max(0, Math.min(index, activeList.length - 1));
  const art = activeList[safeIdx];
  
  if (safeIdx === 0) {
    _lastBroadcastCategory = ''; // FIX: Reset state on new session
  }

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
  if (!('speechSynthesis' in window)) {
    if (typeof showToastNotification === 'function') {
      showToastNotification('🎙 Audio playback is not supported on this browser.');
    }
    return;
  }
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
  document.body.classList.add('drawer-open');
});
drawerCloseBtn.addEventListener('click', () => {
  drawerBackdrop.classList.remove('active');
  document.body.classList.remove('drawer-open');
});
drawerBackdrop.addEventListener('click', (e) => {
  if (e.target === drawerBackdrop) {
    drawerBackdrop.classList.remove('active');
    document.body.classList.remove('drawer-open');
  }
});

// INTERACTIVE BOOKMARK REDIRECTION
window.openSavedArticle = function(id) {
  drawerBackdrop.classList.remove('active');
  document.body.classList.remove('drawer-open');
  
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
  const targetLink = link || (state.atomicDossier[id] && state.atomicDossier[id].link) || ((state.podcasts || []).find(p => p.id === id) || {}).link;
  if (targetLink && targetLink !== '#') {
    window.open(targetLink, '_blank');
    return;
  }
  const cardElem = document.querySelector(`.thought-card[data-id="${id}"]`);
  if (cardElem) {
    drawerBackdrop.classList.remove('active');
    cardElem.scrollIntoView({ behavior: 'smooth', block: 'center', inline: 'center' });
    cardElem.style.borderColor = '#a855f7';
    cardElem.style.boxShadow = '0 0 30px rgba(168, 85, 247, 0.6)';
    setTimeout(() => {
      cardElem.style.borderColor = '';
      cardElem.style.boxShadow = '';
    }, 2000);
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
    
    // Resolve live link if missing from snapshot
    let targetLink = item.link || '';
    if (!targetLink || targetLink === '#') {
      if (isPodcast) {
        const pod = (state.podcasts || []).find(p => p.id === item.id);
        if (pod && pod.link) targetLink = pod.link;
      } else {
        const art = (state.articles || []).find(a => a.id === item.id);
        if (art && art.link) targetLink = art.link;
      }
    }

    // Format saved date
    let dateStr = '';
    if (item.savedAt) {
      const d = new Date(item.savedAt);
      dateStr = d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    }

    const topicsHTML = (item.topics && item.topics.length)
      ? `<div class="atomic-topics-row">${item.topics.map(t => `<span class="atomic-topic-tag">#${escapeHtml(t)}</span>`).join('')}</div>`
      : '';

    const titleClickAction = isPodcast
      ? `window.open('${escapeJs(targetLink)}', '_blank')`
      : `openSavedArticle('${item.id}')`;

    const ctaButtonHTML = isPodcast
      ? `<a class="atomic-cta-btn" href="${escapeHtml(targetLink)}" target="_blank" rel="noopener noreferrer" onclick="event.stopPropagation();">Watch Episode ↗</a>`
      : `<button class="atomic-cta-btn" onclick="openSavedArticle('${item.id}')">Read Full Story ↗</button>`;

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

        <h4 class="atomic-card-title" onclick="${titleClickAction}" title="${isPodcast ? 'Watch Episode on YouTube' : 'Read Story'}">${escapeHtml(item.title)}</h4>

        <div class="atomic-thesis-box">
          <div class="atomic-thesis-badge">
            <span>✦</span> ATOMIC ESSENCE
          </div>
          <p class="atomic-thesis-text">${escapeHtml(item.atomicThesis)}</p>
        </div>

        ${topicsHTML}

        <div class="atomic-card-footer">
          ${ctaButtonHTML}
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
      const btn = e.target;
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      // Update ARIA attributes for accessibility
      navTabs.querySelectorAll('.tab-btn').forEach(b => b.setAttribute('aria-selected', 'false'));
      btn.setAttribute('aria-selected', 'true');
      state.currentCategory = btn.getAttribute('data-category');
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

  // Progressive Disclosure: Quick Tools Menu Dropdown
  const toolsDropdown = document.getElementById('headerToolsDropdown');
  const toolsToggleBtn = document.getElementById('headerToolsToggleBtn');
  const toolsPopover = document.getElementById('headerToolsPopover');

  if (toolsToggleBtn && toolsDropdown) {
    toolsToggleBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      const isOpen = toolsDropdown.classList.toggle('active');
      toolsToggleBtn.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
    });

    if (toolsPopover) {
      toolsPopover.addEventListener('click', () => {
        toolsDropdown.classList.remove('active');
        toolsToggleBtn.setAttribute('aria-expanded', 'false');
      });
    }

    document.addEventListener('click', (e) => {
      if (!toolsDropdown.contains(e.target)) {
        toolsDropdown.classList.remove('active');
        toolsToggleBtn.setAttribute('aria-expanded', 'false');
      }
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
      closeConstellationModal();
      const reportModal = document.getElementById('focusReportModal');
      if (reportModal && reportModal.classList.contains('active')) {
        exitFocusSession();
      }
      drawerBackdrop.classList.remove('active');
      const toolsDropdown = document.getElementById('headerToolsDropdown');
      if (toolsDropdown) {
        toolsDropdown.classList.remove('active');
        const toolsToggle = document.getElementById('headerToolsToggleBtn');
        if (toolsToggle) toolsToggle.setAttribute('aria-expanded', 'false');
      }
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
    const allCats = ['World', 'Tech', 'National', 'Business'];
    let catsCovered = 0;
    for (const cat of allCats) {
      if ((readingProgress.categoriesSeen[cat] || 0) >= COMPLETION_THRESHOLD.minArticlesPerCat) {
        catsCovered++;
      }
    }
    
    const progress = Math.min(catsCovered / COMPLETION_THRESHOLD.minCategories, 1);
    const scrollLine = document.getElementById('headerScrollLine');
    
    if (progress >= 1 && !readingProgress.completed) {
      readingProgress.completed = true;
      saveProgress();
      if (scrollLine) scrollLine.classList.add('caught-up');
      showCaughtUpToast();
    } else if (readingProgress.completed && scrollLine) {
      scrollLine.classList.add('caught-up');
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
    '<div class="paired-story-header">' +
      '<div class="paired-header-left">' +
        '<span class="paired-badge-glow">✦</span>' +
        '<span class="paired-header-title">CROSS-REGIONAL INTELLIGENCE</span>' +
      '</div>' +
      '<span class="paired-header-pill">2 Perspectives Compared</span>' +
    '</div>' +
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
      ? ('<div class="thought-card-topics">' + ep.topics.map(t => '<span class="thought-topic-pill">#' + escapeHtml(t) + '</span>').join('') + '</div>')
      : '';
    const themeHTML = ep.theme
      ? `<div class="thought-card-theme-box"><span class="thought-theme-label">Dominant Theme</span><p class="thought-card-theme">${escapeHtml(ep.theme)}</p></div>`
      : (ep.insight ? `<p class="thought-card-insight">“${escapeHtml(ep.insight)}”</p>` : '');

    const rn = (ep.resonant_news && ep.resonant_news.length) ? ep.resonant_news[0] : null;
    const resonantNewsHTML = rn
      ? `<button type="button" class="thought-card-resonant-news" onclick="event.stopPropagation(); openModal('${escapeJs(rn.id)}');" title="Open executive reader for: ${escapeHtml(rn.title)}" aria-label="Open resonant news article">
           <span class="thought-resonant-badge">📰 Resonates</span>
           <span class="thought-resonant-title">${escapeHtml(rn.title)}</span>
           <span class="thought-resonant-arrow">↗</span>
         </button>`
      : '';

    return `
      <article class="thought-card ${isFlagship ? 'flagship' : ''}" data-id="${ep.id}" onclick="window.open('${escapeJs(ep.link)}','_blank')">
        <div class="thought-card-thumb-wrap">
          <img class="thought-card-thumb" src="${ep.imageUrl}" alt="${escapeHtml(ep.title)}" loading="lazy"
               onerror="this.src='https://i.ytimg.com/vi/${ep.id.replace('tp_','')}/hqdefault.jpg'">
          ${ep.duration ? ('<span class="thought-card-duration">' + escapeHtml(ep.duration) + '</span>') : ''}
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
          ${resonantNewsHTML}
          <div class="thought-card-meta">
            <span class="thought-card-category">${escapeHtml(ep.category)}</span>
            <span>${guestLabel}${escapeHtml(ep.pubDate || '')}</span>
          </div>
        </div>
      </article>
    `;
  }).join('');
  attach3DTiltListeners();
}

// ============================================================
// 60-SECOND FLASH BRIEFING ENGINE
// Full-screen auto-advancing news flashcards
// ============================================================
(function initFlashBriefing() {
  const overlay = document.getElementById('flashBriefingOverlay');
  const cardArea = document.getElementById('flashCardArea');
  const progressFill = document.getElementById('flashProgressFill');
  const counter = document.getElementById('flashCounter');
  const timerFill = document.getElementById('flashTimerFill');
  const pauseBtn = document.getElementById('flashPauseBtn');
  const closeBtn = document.getElementById('flashCloseBtn');
  const triggerBtn = document.getElementById('flashBriefingBtn');

  if (!overlay || !triggerBtn) return;

  let flashState = {
    articles: [],
    currentIndex: 0,
    isPaused: false,
    secondsLeft: 6,
    intervalId: null
  };

  const CARD_DURATION = 6;
  const FB_COLORS = {
    World: { bg: 'rgba(0,242,254,0.12)', color: '#00f2fe', border: 'rgba(0,242,254,0.3)' },
    Tech: { bg: 'rgba(168,85,247,0.12)', color: '#a855f7', border: 'rgba(168,85,247,0.3)' },
    National: { bg: 'rgba(245,158,11,0.12)', color: '#f59e0b', border: 'rgba(245,158,11,0.3)' },
    Business: { bg: 'rgba(16,185,129,0.12)', color: '#10b981', border: 'rgba(16,185,129,0.3)' }
  };

  function getUrgencyClass(i) {
    if (i < 3) return 'urgency-high';
    if (i < 7) return 'urgency-medium';
    return 'urgency-low';
  }

  function renderFlashCard(index) {
    const art = flashState.articles[index];
    if (!art) return;
    const catStyle = FB_COLORS[art.category] || FB_COLORS.World;
    const raw = art.annotation ? (art.annotation.what || art.description || '') : (art.description || '');
    const clean = raw.replace(/[\s.]*[.…]+$/, '').trim();
    const sentence = clean.split(/(?<=[.!?])\s/)[0] || clean;

    const existing = cardArea.querySelector('.flash-card');
    if (existing) {
      existing.classList.add('exiting');
      setTimeout(() => existing.remove(), 350);
    }

    setTimeout(() => {
      cardArea.innerHTML = `
        <div class="flash-card">
          <div class="flash-card-urgency ${getUrgencyClass(index)}"></div>
          <span class="flash-card-category" style="background:${catStyle.bg};color:${catStyle.color};border:1px solid ${catStyle.border};">${art.category}</span>
          <h2 class="flash-card-headline">${art.title}</h2>
          <p class="flash-card-summary">${sentence}</p>
          <div class="flash-card-source">
            <span class="flash-card-source-logo">${art.sourceLogo || art.source.charAt(0)}</span>
            <span>${art.source}</span>
            ${art.readTime ? '<span>&middot;</span><span>' + art.readTime + '</span>' : ''}
          </div>
        </div>
      `;
    }, existing ? 200 : 0);

    const total = flashState.articles.length;
    counter.textContent = `${index + 1} / ${total}`;
    progressFill.style.width = `${((index + 1) / total) * 100}%`;
  }

  function startTimer() {
    flashState.secondsLeft = CARD_DURATION;
    timerFill.style.transition = 'none';
    timerFill.style.strokeDashoffset = '100';
    void timerFill.offsetWidth;
    timerFill.style.transition = `stroke-dashoffset ${CARD_DURATION}s linear`;
    timerFill.style.strokeDashoffset = '0';

    clearInterval(flashState.intervalId);
    flashState.intervalId = setInterval(() => {
      if (flashState.isPaused) return;
      flashState.secondsLeft--;
      if (flashState.secondsLeft <= 0) advanceCard();
    }, 1000);
  }

  function advanceCard() {
    clearInterval(flashState.intervalId);
    flashState.currentIndex++;
    if (flashState.currentIndex >= flashState.articles.length) {
      // Show completion card instead of abrupt close
      clearInterval(flashState.intervalId);
      const cardArea = document.getElementById('flashCardArea');
      if (cardArea) {
        cardArea.innerHTML = `
          <div class="flash-card">
            <div class="flash-card-urgency urgency-low"></div>
            <span class="flash-card-category" style="background: rgba(16, 185, 129, 0.12); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.3);">COMPLETE</span>
            <h2 class="flash-card-headline">⚡ Briefing Complete</h2>
            <p class="flash-card-summary">${flashState.articles.length} stories covered in 60 seconds. You're now caught up on today's top headlines.</p>
            <div class="flash-card-source">
              <span>Press Escape or tap Close to exit</span>
            </div>
          </div>
        `;
      }
      const progressFill = document.getElementById('flashProgressFill');
      if (progressFill) progressFill.style.width = '100%';
      const counter = document.getElementById('flashCounter');
      if (counter) counter.textContent = 'Done ✓';
      return;
    }
    renderFlashCard(flashState.currentIndex);
    startTimer();
  }

  function openFlashBriefing() {
    const pool = (state.filteredArticles && state.filteredArticles.length > 0) ? state.filteredArticles : state.articles;
    flashState.articles = pool.slice(0, 10);
    flashState.currentIndex = 0;
    flashState.isPaused = false;
    if (flashState.articles.length === 0) {
      if (typeof showToastNotification === 'function') {
        showToastNotification('⚡ No stories available for Flash Briefing. Try refreshing first.');
      }
      return;
    }

    document.body.classList.add('modal-open');
    overlay.classList.add('active');
    pauseBtn.textContent = '⏸';
    renderFlashCard(0);
    startTimer();
  }

  function closeFlashBriefing() {
    clearInterval(flashState.intervalId);
    flashState.isPaused = false;
    overlay.classList.remove('active');
    document.body.classList.remove('modal-open');
    cardArea.innerHTML = '';
    timerFill.style.transition = 'none';
    timerFill.style.strokeDashoffset = '100';
  }

  function togglePause() {
    flashState.isPaused = !flashState.isPaused;
    pauseBtn.textContent = flashState.isPaused ? '▶' : '⏸';
    
    if (flashState.isPaused) {
      // Freeze the CSS transition by capturing current offset
      const currentOffset = window.getComputedStyle(timerFill).getPropertyValue('stroke-dashoffset');
      timerFill.style.transition = 'none';
      timerFill.style.strokeDashoffset = currentOffset;
    } else {
      // Resume the transition using remaining seconds
      void timerFill.offsetWidth;
      timerFill.style.transition = `stroke-dashoffset ${flashState.secondsLeft}s linear`;
      timerFill.style.strokeDashoffset = '0';
    }
  }

  triggerBtn.addEventListener('click', openFlashBriefing);
  closeBtn.addEventListener('click', closeFlashBriefing);
  pauseBtn.addEventListener('click', togglePause);

  document.addEventListener('keydown', (e) => {
    if (!overlay.classList.contains('active')) return;
    if (e.key === 'Escape') { closeFlashBriefing(); }
    else if (e.key === ' ') { e.preventDefault(); togglePause(); }
    else if (e.key === 'ArrowRight') { advanceCard(); }
    else if (e.key === 'ArrowLeft' && flashState.currentIndex > 0) {
      clearInterval(flashState.intervalId);
      flashState.currentIndex--;
      renderFlashCard(flashState.currentIndex);
      startTimer();
    }
  });

  let fbStartX = 0;
  overlay.addEventListener('touchstart', (e) => { fbStartX = e.touches[0].clientX; }, { passive: true });
  overlay.addEventListener('touchend', (e) => {
    const diffX = e.changedTouches[0].clientX - fbStartX;
    if (Math.abs(diffX) > 60) {
      if (diffX < 0) advanceCard();
      else if (flashState.currentIndex > 0) {
        clearInterval(flashState.intervalId);
        flashState.currentIndex--;
        renderFlashCard(flashState.currentIndex);
        startTimer();
      }
    }
  }, { passive: true });
})();
