// News Colossal Application Engine — 3D Canvas Card Stack Edition

const state = {
  articles: [],
  filteredArticles: [],
  currentCategory: 'top10',
  currentRegion: 'all',
  searchQuery: '',
  bookmarks: JSON.parse(localStorage.getItem('nc_bookmarks') || '[]'),
  theme: localStorage.getItem('nc_theme') || 'dark',
  heroIndex: 0,
  heroPlaying: true,
  heroTimer: null,
  progressInterval: null,
  progressValue: 0,
  
  // 3D Card Stack Modal State
  stackState: {
    articles: [],
    currentIndex: 0,
    isPlaying: false
  },
  
  audioState: { isPlaying: false, utterance: null }
};

const DEFAULT_FALLBACK_IMG = "https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?auto=format&fit=crop&w=1600&q=95";

// DOM Elements
const newsGrid = document.getElementById('newsGrid');
const gridTitle = document.getElementById('gridTitle');
const tickerTrack = document.getElementById('tickerTrack');
const syncTimeLabel = document.getElementById('syncTimeLabel');
const searchInput = document.getElementById('searchInput');
const regionSelect = document.getElementById('regionSelect');
const navTabs = document.getElementById('navTabs');
const modalBackdrop = document.getElementById('modalBackdrop');
const modalContent = document.getElementById('modalContent');
const modalCloseBtn = document.getElementById('modalCloseBtn');
const drawerBackdrop = document.getElementById('drawerBackdrop');
const drawerCloseBtn = document.getElementById('drawerCloseBtn');
const savedList = document.getElementById('savedList');
const bookmarkCount = document.getElementById('bookmarkCount');
const themeToggleBtn = document.getElementById('themeToggleBtn');
const refreshBtn = document.getElementById('refreshBtn');
const audioPlayBtn = document.getElementById('audioPlayBtn');
const audioTitle = document.getElementById('audioTitle');
const svgMapContainer = document.getElementById('svgMapContainer');
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

// Initialize
document.addEventListener('DOMContentLoaded', () => {
  initTheme();
  setupCanvasResize();
  loadData();
  setupEventListeners();
  loadSvgMap();
});

// Theme Management
function initTheme() {
  document.documentElement.setAttribute('data-theme', state.theme);
}

themeToggleBtn.addEventListener('click', () => {
  state.theme = state.theme === 'dark' ? 'light' : 'dark';
  localStorage.setItem('nc_theme', state.theme);
  document.documentElement.setAttribute('data-theme', state.theme);
});

// Load SVG Map
async function loadSvgMap() {
  try {
    const res = await fetch('assets/map.svg');
    if (res.ok) {
      const svgText = await res.text();
      svgMapContainer.innerHTML = svgText;
      setupMapInteractivity();
    }
  } catch (e) {
    console.log('Map SVG fallback');
  }
}

function setupMapInteractivity() {
  const nodes = document.querySelectorAll('.region-node');
  nodes.forEach(node => {
    node.addEventListener('click', () => {
      const region = node.getAttribute('data-region');
      regionSelect.value = region;
      state.currentRegion = region;
      filterAndRender();
      scrollToContent();
    });
  });
}

// Data Fetcher
async function loadData() {
  renderSkeletons();
  try {
    const res = await fetch('data/news.json');
    if (!res.ok) throw new Error('Data file not found');
    const data = await res.json();
    state.articles = data.articles || [];
    if (data.lastUpdated) {
      const formatted = new Date(data.lastUpdated).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      syncTimeLabel.textContent = `Auto-synced at ${formatted}`;
    }
  } catch (err) {
    console.warn('Local news.json missing, triggering fallback client fetch:', err);
    await fetchClientFallback();
  }
  preloadAllImages();
  filterAndRender();
  renderTicker();
  updateBookmarkBadge();
}

function preloadAllImages() {
  state.articles.forEach(art => {
    if (!canvasImages[art.id]) {
      const img = new Image();
      img.crossOrigin = 'Anonymous';
      img.onerror = () => { img.src = DEFAULT_FALLBACK_IMG; };
      img.src = art.imageUrl;
      canvasImages[art.id] = img;
    }
  });
}

// Client Multi-Proxy Fallback
async function fetchClientFallback() {
  const proxyUrl = 'https://api.rss2json.com/v1/api.json?rss_url=https://feeds.bbci.co.uk/news/rss.xml';
  try {
    const res = await fetch(proxyUrl);
    const data = await res.json();
    if (data.items) {
      state.articles = data.items.map((item, idx) => ({
        id: `bbc-live-${idx}`,
        title: item.title,
        link: item.link,
        description: item.description.replace(/<[^>]*>?/gm, '').slice(0, 180) + '...',
        source: 'BBC News',
        sourceLogo: 'BBC',
        category: 'World',
        region: 'Global',
        pubDate: item.pubDate,
        imageUrl: item.thumbnail || DEFAULT_FALLBACK_IMG,
        annotation: {
          what: item.title,
          why: 'Key breaking geopolitical news story.'
        },
        readTime: '3 min read',
        relatedSources: [
          { name: 'BBC News', url: item.link },
          { name: 'Reuters', url: 'https://www.reuters.com' }
        ]
      }));
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

  currentImgObj = prevArt ? canvasImages[prevArt.id] : null;
  nextImgObj = nextArt ? canvasImages[nextArt.id] : null;

  animProgress = 0.0;
  animateCanvasTransition();
  renderHeroOverlayText(nextArt);
  renderHeroDots();
  resetProgressBar();
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
  gradient.addColorStop(0, 'rgba(11, 15, 25, 0.0)');
  gradient.addColorStop(1, 'rgba(11, 15, 25, 0.96)');
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
        <span>3D Card Stack Preview</span> &rarr;
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

// Category & Region Filtering Engine
function filterAndRender() {
  let list = [...state.articles];

  // 1. Region Filtering FIRST
  if (state.currentRegion !== 'all') {
    const targetReg = state.currentRegion.toLowerCase();
    if (targetReg === 'global') {
      list = list.filter(a => a.region.toLowerCase() === 'global' || a.region.toLowerCase() === 'world');
    } else {
      list = list.filter(a => a.region.toLowerCase() === targetReg);
    }
  }

  // 2. Category Filtering SECOND
  const regionLabel = state.currentRegion === 'all' ? '' : ` (${state.currentRegion})`;
  
  if (state.currentCategory === 'top10') {
    list = list.slice(0, 10);
    gridTitle.textContent = `Top 10 News Digest${regionLabel}`;
  } else if (state.currentCategory.toLowerCase() === 'world') {
    list = list.filter(a => a.category.toLowerCase() === 'world');
    gridTitle.textContent = `World News Coverage${regionLabel}`;
  } else if (state.currentCategory.toLowerCase() === 'tech') {
    list = list.filter(a => a.category.toLowerCase() === 'tech');
    gridTitle.textContent = `Technology & Electronics${regionLabel}`;
  } else if (state.currentCategory.toLowerCase() === 'national') {
    list = list.filter(a => a.category.toLowerCase() === 'national');
    gridTitle.textContent = `National News Focus${regionLabel}`;
  } else if (state.currentCategory.toLowerCase() === 'business') {
    list = list.filter(a => a.category.toLowerCase() === 'business');
    gridTitle.textContent = `Business & Markets${regionLabel}`;
  } else {
    list = list.filter(a => a.category.toLowerCase() === state.currentCategory.toLowerCase());
    gridTitle.textContent = `${state.currentCategory} News${regionLabel}`;
  }

  // 3. Search Filter THIRD
  if (state.searchQuery.trim() !== '') {
    const q = state.searchQuery.toLowerCase();
    list = list.filter(a => 
      a.title.toLowerCase().includes(q) || 
      a.description.toLowerCase().includes(q) || 
      a.source.toLowerCase().includes(q)
    );
  }

  state.filteredArticles = list;

  renderGrid(list);

  // Update top canvas spotlight
  state.heroIndex = 0;
  transitionHeroSlide(0);
  startHeroTimer();
}

function scrollToContent() {
  if (contentGridSection) {
    const yOffset = -90;
    const y = contentGridSection.getBoundingClientRect().top + window.pageYOffset + yOffset;
    window.scrollTo({ top: y, behavior: 'smooth' });
  }
}

// Render Main Grid with OnError Fallback
function renderGrid(articles) {
  if (articles.length === 0) {
    const regionName = state.currentRegion === 'all' ? '' : ` in ${state.currentRegion}`;
    newsGrid.innerHTML = `
      <div style="grid-column: 1/-1; text-align: center; padding: 4rem 1rem; color: var(--text-muted);">
        <p style="font-size: 1.2rem;">No matching articles found for '${escapeHtml(state.currentCategory)}'${regionName}.</p>
        <button onclick="resetFilters()" class="btn-primary" style="margin-top: 1rem;">Reset All Filters</button>
      </div>
    `;
    return;
  }

  newsGrid.innerHTML = articles.map(art => {
    const saved = isBookmarked(art.id);
    return `
      <article class="news-card">
        <div class="card-thumb-box">
          <img src="${art.imageUrl}" alt="${escapeHtml(art.title)}" class="card-thumb" loading="lazy" onerror="this.onerror=null; this.src='${DEFAULT_FALLBACK_IMG}';" />
          <span class="card-category">${art.category}</span>
          <button class="bookmark-btn ${saved ? 'saved' : ''}" onclick="toggleBookmark('${art.id}', event)" title="Save Article">
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
            <p class="annotation-bullet">${escapeHtml(art.annotation.what)}</p>
          </div>

          <div class="card-footer">
            <button onclick="openModal('${art.id}')" class="btn-text">
              Crisp Briefing &rarr;
            </button>
            <a href="${art.link}" target="_blank" rel="noopener noreferrer" class="link-external" title="Full Story at ${art.source}">
              Source ↗
            </a>
          </div>
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

// 3D CARD STACK CANVAS PREVIEW ENGINE
window.openModal = function(id) {
  const pool = state.filteredArticles.length > 0 ? state.filteredArticles : state.articles;
  const index = pool.findIndex(a => a.id === id);
  if (index === -1) return;

  state.stackState.articles = pool;
  state.stackState.currentIndex = index;

  render3DCardStack();
  modalBackdrop.classList.add('active');
};

function render3DCardStack() {
  const pool = state.stackState.articles;
  const currIdx = state.stackState.currentIndex;
  const total = pool.length;

  const prevIdx = (currIdx - 1 + total) % total;
  const nextIdx = (currIdx + 1) % total;

  const currArt = pool[currIdx];
  const prevArt = pool[prevIdx];
  const nextArt = pool[nextIdx];

  modalContent.innerHTML = `
    <div class="card-stack-viewport">
      <!-- Previous Card Stack -->
      <div class="stacked-card prev" onclick="navigateStack(-1)">
        <div style="font-size: 0.75rem; color: var(--accent-cyan); text-transform: uppercase; margin-bottom: 0.3rem;">&lsaquo; PREVIOUS STORY</div>
        <h4 style="font-family: var(--font-heading); font-size: 1.1rem; font-weight: 700; max-height: 2.8em; overflow: hidden;">${escapeHtml(prevArt.title)}</h4>
      </div>

      <!-- Active Center Card -->
      <div class="stacked-card active">
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.8rem;">
          <span class="tag-badge">${currArt.category} STORY #${currIdx + 1} OF ${total}</span>
          <span style="font-size: 0.82rem; color: var(--text-muted);">${currArt.source} &bull; ${currArt.readTime}</span>
        </div>

        <img src="${currArt.imageUrl}" alt="${escapeHtml(currArt.title)}" style="width: 100%; height: 200px; object-fit: cover; border-radius: var(--radius-md); margin-bottom: 1rem;" onerror="this.onerror=null; this.src='${DEFAULT_FALLBACK_IMG}';" />

        <h2 style="font-family: var(--font-heading); font-size: 1.45rem; font-weight: 800; line-height: 1.3; margin-bottom: 0.8rem; color: #fff;">${escapeHtml(currArt.title)}</h2>

        <div class="modal-annotation-block" style="margin: 0.8rem 0;">
          <h4 style="color: var(--accent-cyan); font-size: 0.75rem; text-transform: uppercase; margin-bottom: 0.4rem;">✦ Crisp Executive Annotation (${currArt.region})</h4>
          <p style="font-size: 0.88rem; color: var(--text-secondary); line-height: 1.4;">${escapeHtml(currArt.annotation.what)}</p>
        </div>

        <p style="color: var(--text-secondary); font-size: 0.88rem; line-height: 1.5; margin-bottom: 1rem; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;">${escapeHtml(currArt.description)}</p>

        <div style="display: flex; gap: 0.8rem; align-items: center;">
          <a href="${currArt.link}" target="_blank" rel="noopener noreferrer" class="btn-primary" style="flex: 1; justify-content: center; padding: 0.55rem 1rem; font-size: 0.85rem;">
            Read Full Article ↗
          </a>
          <button onclick="speakArticle('${escapeJs(currArt.title)}. ${escapeJs(currArt.annotation.what)}')" class="btn-secondary" style="padding: 0.55rem 1rem; font-size: 0.85rem;">
            🔊 Listen
          </button>
        </div>
      </div>

      <!-- Next Card Stack -->
      <div class="stacked-card next" onclick="navigateStack(1)">
        <div style="font-size: 0.75rem; color: var(--accent-cyan); text-transform: uppercase; margin-bottom: 0.3rem;">NEXT STORY &rsaquo;</div>
        <h4 style="font-family: var(--font-heading); font-size: 1.1rem; font-weight: 700; max-height: 2.8em; overflow: hidden;">${escapeHtml(nextArt.title)}</h4>
      </div>
    </div>

    <!-- Bottom Stack Navigation Bar -->
    <div class="card-stack-controls">
      <button onclick="navigateStack(-1)" class="btn-secondary" style="padding: 0.4rem 0.9rem; font-size: 0.85rem;">&lsaquo; Previous Story</button>
      <span style="font-size: 0.85rem; font-weight: 700; color: var(--accent-cyan);">${currIdx + 1} / ${total}</span>
      <button onclick="navigateStack(1)" class="btn-secondary" style="padding: 0.4rem 0.9rem; font-size: 0.85rem;">Next Story &rsaquo;</button>
    </div>
  `;
}

window.navigateStack = function(step) {
  const pool = state.stackState.articles;
  if (pool.length === 0) return;
  state.stackState.currentIndex = (state.stackState.currentIndex + step + pool.length) % pool.length;
  render3DCardStack();
};

function closeModal() {
  modalBackdrop.classList.remove('active');
}

modalCloseBtn.addEventListener('click', closeModal);
modalBackdrop.addEventListener('click', (e) => {
  if (e.target === modalBackdrop) closeModal();
});

// Bookmarks Manager
window.toggleBookmark = function(id, e) {
  if (e) e.stopPropagation();
  const index = state.bookmarks.indexOf(id);
  if (index >= 0) {
    state.bookmarks.splice(index, 1);
  } else {
    state.bookmarks.push(id);
  }
  localStorage.setItem('nc_bookmarks', JSON.stringify(state.bookmarks));
  updateBookmarkBadge();
  filterAndRender();
  renderSavedList();
};

function isBookmarked(id) {
  return state.bookmarks.includes(id);
}

function updateBookmarkBadge() {
  bookmarkCount.textContent = state.bookmarks.length;
}

document.getElementById('bookmarksBtn').addEventListener('click', () => {
  renderSavedList();
  drawerBackdrop.classList.add('active');
});
drawerCloseBtn.addEventListener('click', () => drawerBackdrop.classList.remove('active'));
drawerBackdrop.addEventListener('click', (e) => {
  if (e.target === drawerBackdrop) drawerBackdrop.classList.remove('active');
});

function renderSavedList() {
  const savedArticles = state.articles.filter(a => state.bookmarks.includes(a.id));
  if (savedArticles.length === 0) {
    savedList.innerHTML = '<p style="color: var(--text-muted); text-align: center;">No saved articles yet. Click ☆ on any card to bookmark.</p>';
    return;
  }
  savedList.innerHTML = savedArticles.map(art => `
    <div style="background: var(--bg-surface-elevated); padding: 1rem; border-radius: var(--radius-sm); border: 1px solid var(--border-color);">
      <h4 style="font-size: 0.95rem; margin-bottom: 0.4rem;">${escapeHtml(art.title)}</h4>
      <div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.78rem;">
        <span style="color: var(--text-muted);">${art.source}</span>
        <button onclick="toggleBookmark('${art.id}')" style="background: none; border: none; color: #ef4444; cursor: pointer;">Remove</button>
      </div>
    </div>
  `).join('');
}

// Web Speech API Audio Player
window.speakArticle = function(text) {
  if ('speechSynthesis' in window) {
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 1.0;
    utterance.pitch = 1.0;
    audioTitle.textContent = text.slice(0, 30) + '...';
    audioPlayBtn.textContent = '⏸';
    state.audioState.isPlaying = true;
    
    utterance.onend = () => {
      audioPlayBtn.textContent = '▶';
      audioTitle.textContent = 'Listen to Top 10 Briefing';
      state.audioState.isPlaying = false;
    };
    
    window.speechSynthesis.speak(utterance);
  }
};

audioPlayBtn.addEventListener('click', () => {
  if ('speechSynthesis' in window) {
    if (state.audioState.isPlaying) {
      window.speechSynthesis.pause();
      audioPlayBtn.textContent = '▶';
      state.audioState.isPlaying = false;
    } else {
      if (window.speechSynthesis.paused) {
        window.speechSynthesis.resume();
        audioPlayBtn.textContent = '⏸';
        state.audioState.isPlaying = true;
      } else {
        const topArt = state.articles[0];
        if (topArt) speakArticle(`${topArt.title}. ${topArt.annotation.what}`);
      }
    }
  }
});

// Event Listeners & Tab Switching
function setupEventListeners() {
  navTabs.addEventListener('click', (e) => {
    if (e.target.classList.contains('tab-btn')) {
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      e.target.classList.add('active');
      state.currentCategory = e.target.getAttribute('data-category');
      filterAndRender();
      scrollToContent();
    }
  });

  regionSelect.addEventListener('change', (e) => {
    state.currentRegion = e.target.value;
    filterAndRender();
    scrollToContent();
  });

  searchInput.addEventListener('input', (e) => {
    state.searchQuery = e.target.value;
    filterAndRender();
  });

  refreshBtn.addEventListener('click', () => {
    refreshBtn.style.transform = 'rotate(360deg)';
    refreshBtn.style.transition = 'transform 0.5s ease';
    loadData().then(() => {
      setTimeout(() => refreshBtn.style.transform = 'none', 500);
    });
  });

  document.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowLeft') {
      if (modalBackdrop.classList.contains('active')) navigateStack(-1);
    }
    if (e.key === 'ArrowRight') {
      if (modalBackdrop.classList.contains('active')) navigateStack(1);
    }
    if (e.key === '/' && document.activeElement !== searchInput) {
      e.preventDefault();
      searchInput.focus();
    }
    if (e.key === 'Escape') {
      closeModal();
      drawerBackdrop.classList.remove('active');
    }
  });
}

function resetFilters() {
  state.currentCategory = 'top10';
  state.currentRegion = 'all';
  state.searchQuery = '';
  searchInput.value = '';
  regionSelect.value = 'all';
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.querySelector('[data-category="top10"]').classList.add('active');
  filterAndRender();
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
