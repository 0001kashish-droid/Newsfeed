// News Colossal Application Engine

const state = {
  articles: [],
  filteredArticles: [],
  currentCategory: 'top10',
  currentRegion: 'all',
  searchQuery: '',
  bookmarks: JSON.parse(localStorage.getItem('nc_bookmarks') || '[]'),
  theme: localStorage.getItem('nc_theme') || 'dark',
  audioState: { isPlaying: false, utterance: null, currentIndex: 0 }
};

// DOM Elements
const newsGrid = document.getElementById('newsGrid');
const heroSection = document.getElementById('heroSection');
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
const drawerContent = document.getElementById('drawerContent');
const drawerCloseBtn = document.getElementById('drawerCloseBtn');
const savedList = document.getElementById('savedList');
const bookmarkCount = document.getElementById('bookmarkCount');
const themeToggleBtn = document.getElementById('themeToggleBtn');
const refreshBtn = document.getElementById('refreshBtn');
const audioPlayBtn = document.getElementById('audioPlayBtn');
const audioTitle = document.getElementById('audioTitle');
const svgMapContainer = document.getElementById('svgMapContainer');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
  initTheme();
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
  filterAndRender();
  renderTicker();
  updateBookmarkBadge();
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
        imageUrl: item.thumbnail || 'https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?auto=format&fit=crop&w=1200&q=80',
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

// Filtering & Rendering
function filterAndRender() {
  let list = [...state.articles];

  // Category filter
  if (state.currentCategory === 'top10') {
    list = list.slice(0, 10);
    gridTitle.textContent = 'Top 10 Global News Digest';
  } else {
    list = list.filter(a => a.category.toLowerCase() === state.currentCategory.toLowerCase());
    gridTitle.textContent = `${state.currentCategory} Coverage`;
  }

  // Region filter
  if (state.currentRegion !== 'all') {
    list = list.filter(a => a.region.toLowerCase() === state.currentRegion.toLowerCase());
  }

  // Search filter
  if (state.searchQuery.trim() !== '') {
    const q = state.searchQuery.toLowerCase();
    list = list.filter(a => 
      a.title.toLowerCase().includes(q) || 
      a.description.toLowerCase().includes(q) || 
      a.source.toLowerCase().includes(q)
    );
  }

  state.filteredArticles = list;

  renderHeroSpotlight(state.articles[0]);
  renderGrid(list);
}

// Render Hero Spotlight
function renderHeroSpotlight(article) {
  if (!article) {
    heroSection.innerHTML = '';
    return;
  }
  const isSaved = isBookmarked(article.id);
  heroSection.innerHTML = `
    <div class="hero-card">
      <img src="${article.imageUrl}" alt="${escapeHtml(article.title)}" class="hero-img" />
      <div class="hero-overlay">
        <div class="hero-badge-row">
          <span class="tag-badge">TOP SPOTLIGHT</span>
          <span class="source-tag">✦ ${article.source} &bull; ${article.readTime}</span>
        </div>
        <h1 class="hero-title">${escapeHtml(article.title)}</h1>
        <p class="hero-desc">${escapeHtml(article.description)}</p>
        <div class="hero-actions">
          <button onclick="openModal('${article.id}')" class="btn-primary">
            <span>Read Crisp Annotation</span> &rarr;
          </button>
          <a href="${article.link}" target="_blank" rel="noopener noreferrer" class="btn-secondary">
            Visit Original Source ↗
          </a>
        </div>
      </div>
    </div>
  `;
}

// Render Main Grid
function renderGrid(articles) {
  if (articles.length === 0) {
    newsGrid.innerHTML = `
      <div style="grid-column: 1/-1; text-align: center; padding: 4rem 1rem; color: var(--text-muted);">
        <p style="font-size: 1.2rem;">No matching articles found for your criteria.</p>
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
          <img src="${art.imageUrl}" alt="${escapeHtml(art.title)}" class="card-thumb" loading="lazy" />
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
            <div class="annotation-title">✦ Crisp Annotation</div>
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
  tickerTrack.innerHTML = itemsHTML + ' &bull; ' + itemsHTML; // duplicate for infinite scrolling loop
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

// Modal Reader
window.openModal = function(id) {
  const art = state.articles.find(a => a.id === id);
  if (!art) return;

  modalContent.innerHTML = `
    <div class="modal-header">
      <span class="tag-badge">${art.category}</span>
      <h2 class="modal-title">${escapeHtml(art.title)}</h2>
      <div style="font-size: 0.85rem; color: var(--text-muted); margin-top: 0.5rem;">
        Published by <strong>${art.source}</strong> &bull; ${art.readTime}
      </div>
    </div>

    <img src="${art.imageUrl}" alt="${escapeHtml(art.title)}" style="width: 100%; height: 260px; object-fit: cover; border-radius: var(--radius-md); margin-bottom: 1rem;" />

    <div class="modal-annotation-block">
      <h4>✦ Crisp Executive Annotation</h4>
      <ul class="modal-bullet-list">
        <li><strong>What Happened:</strong> ${escapeHtml(art.annotation.what)}</li>
        <li><strong>Impact & Context:</strong> ${escapeHtml(art.annotation.why)}</li>
      </ul>
    </div>

    <p style="color: var(--text-secondary); line-height: 1.6; margin-bottom: 1.5rem;">${escapeHtml(art.description)}</p>

    <!-- Multi-source perspective chips -->
    <div class="sources-matrix">
      <h4>Explore Perspective Across Related Credible Outlets:</h4>
      <div class="sources-chips">
        ${art.relatedSources.map(s => `
          <a href="${s.url}" target="_blank" rel="noopener noreferrer" class="source-chip">
            <span>${s.name} Coverage</span> ↗
          </a>
        `).join('')}
      </div>
    </div>

    <div style="margin-top: 2rem; display: flex; gap: 1rem;">
      <a href="${art.link}" target="_blank" rel="noopener noreferrer" class="btn-primary" style="flex: 1; justify-content: center;">
        Read Full Story on ${art.source} ↗
      </a>
      <button onclick="speakArticle('${escapeJs(art.title)}. ${escapeJs(art.annotation.what)}')" class="btn-secondary">
        🔊 Listen Audio
      </button>
    </div>
  `;

  modalBackdrop.classList.add('active');
};

modalCloseBtn.addEventListener('click', () => modalBackdrop.classList.remove('active'));
modalBackdrop.addEventListener('click', (e) => {
  if (e.target === modalBackdrop) modalBackdrop.classList.remove('active');
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
        // Read Top 1 Article Annotation
        const topArt = state.articles[0];
        if (topArt) speakArticle(`${topArt.title}. ${topArt.annotation.what}`);
      }
    }
  }
});

// Event Listeners & Keyboard Shortcuts
function setupEventListeners() {
  // Tabs
  navTabs.addEventListener('click', (e) => {
    if (e.target.classList.contains('tab-btn')) {
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      e.target.classList.add('active');
      state.currentCategory = e.target.getAttribute('data-category');
      filterAndRender();
    }
  });

  // Region
  regionSelect.addEventListener('change', (e) => {
    state.currentRegion = e.target.value;
    filterAndRender();
  });

  // Search input
  searchInput.addEventListener('input', (e) => {
    state.searchQuery = e.target.value;
    filterAndRender();
  });

  // Refresh btn
  refreshBtn.addEventListener('click', () => {
    refreshBtn.style.transform = 'rotate(360deg)';
    refreshBtn.style.transition = 'transform 0.5s ease';
    loadData().then(() => {
      setTimeout(() => refreshBtn.style.transform = 'none', 500);
    });
  });

  // Global Keyboard Shortcuts
  document.addEventListener('keydown', (e) => {
    if (e.key === '/' && document.activeElement !== searchInput) {
      e.preventDefault();
      searchInput.focus();
    }
    if (e.key === 'Escape') {
      modalBackdrop.classList.remove('active');
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

// Helpers
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
