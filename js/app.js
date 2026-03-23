/* ── State ──────────────────────────────────── */
const state = {
  images: [],
  games: [],
  activeGames: new Set(),
  activeTab: 'all',
  currentItem: null,
};

const $ = (id) => document.getElementById(id);

/* ── Boot ───────────────────────────────────── */
async function init() {
  try {
    const [imgRes, gameRes] = await Promise.all([
      fetch('data/images.json'),
      fetch('data/games.json'),
    ]);

    if (!imgRes.ok || !gameRes.ok) throw new Error('Fetch failed');

    const imgData  = await imgRes.json();
    const gameData = await gameRes.json();

    state.images = imgData.images || [];
    state.games  = gameData.games || [];
    state.activeGames = new Set(state.games.map((g) => g.id));

    if (imgData.lastUpdated) {
      const d = new Date(imgData.lastUpdated);
      $('updated').textContent = `업데이트 ${d.toLocaleDateString('ko-KR')}`;
    }

    renderSidebar();
    renderGrid();
  } catch (err) {
    console.error(err);
    $('loader').hidden = true;
    const empty = $('empty');
    empty.hidden = false;
    empty.textContent = '데이터를 불러오지 못했습니다. data/ 폴더를 확인해주세요.';
  }
}

/* ── Sidebar ────────────────────────────────── */
function renderSidebar() {
  const list = $('game-list');
  list.innerHTML = '';

  const countMap = {};
  state.images.forEach((img) => {
    countMap[img.game] = (countMap[img.game] || 0) + 1;
  });

  // "All" entry
  const allEl = makeGameItem('__all__', '🎮', '전체', state.images.length, true);
  list.appendChild(allEl);

  const divider = document.createElement('div');
  divider.className = 'sidebar-divider';
  list.appendChild(divider);

  state.games.forEach((game) => {
    const isActive = state.activeGames.has(game.id);
    const el = makeGameItem(game.id, game.icon, game.name, countMap[game.id] || 0, isActive);
    list.appendChild(el);
  });
}

function makeGameItem(id, icon, name, count, active) {
  const el = document.createElement('div');
  el.className = 'game-item' + (active ? ' active' : '');
  el.dataset.id = id;
  el.innerHTML = `
    <span class="game-icon">${icon}</span>
    <span class="game-name">${name}</span>
    <span class="game-badge">${count.toLocaleString()}</span>
  `;
  el.addEventListener('click', () => onGameClick(id));
  return el;
}

function onGameClick(id) {
  const allSelected = state.activeGames.size === state.games.length;

  if (id === '__all__') {
    state.activeGames = new Set(state.games.map((g) => g.id));
  } else if (allSelected) {
    // First click on a specific game → filter to only that game
    state.activeGames = new Set([id]);
  } else if (state.activeGames.has(id) && state.activeGames.size === 1) {
    // Only game selected → click again to show all
    state.activeGames = new Set(state.games.map((g) => g.id));
  } else {
    if (state.activeGames.has(id)) {
      state.activeGames.delete(id);
      if (state.activeGames.size === 0) {
        state.activeGames = new Set(state.games.map((g) => g.id));
      }
    } else {
      state.activeGames.add(id);
    }
  }

  // Sync active classes
  const allActive = state.activeGames.size === state.games.length;
  document.querySelectorAll('.game-item').forEach((el) => {
    const gid = el.dataset.id;
    if (gid === '__all__') {
      el.classList.toggle('active', allActive);
    } else {
      el.classList.toggle('active', state.activeGames.has(gid));
    }
  });

  renderGrid();
}

/* ── Tabs ───────────────────────────────────── */
$('tabs').addEventListener('click', (e) => {
  const tab = e.target.closest('.tab');
  if (!tab) return;
  document.querySelectorAll('.tab').forEach((t) => t.classList.remove('active'));
  tab.classList.add('active');
  state.activeTab = tab.dataset.tab;
  renderGrid();
});

/* ── Grid ───────────────────────────────────── */
const BADGE_CLASS = {
  character:    'badge-character',
  skin:         'badge-skin',
  illustration: 'badge-illustration',
};

const BADGE_LABEL = {
  character:    '캐릭터',
  skin:         '스킨',
  illustration: '일러스트',
};

function filteredImages() {
  return state.images
    .filter((img) => state.activeGames.has(img.game))
    .filter((img) => state.activeTab === 'all' || img.category === state.activeTab)
    .sort((a, b) => new Date(b.date) - new Date(a.date));
}

function renderGrid() {
  const grid  = $('grid');
  const loader = $('loader');
  const empty = $('empty');
  const items = filteredImages();

  $('count').textContent = `${items.length.toLocaleString()}개`;

  if (items.length === 0) {
    grid.innerHTML = '';
    loader.hidden = true;
    empty.hidden = false;
    empty.textContent = '해당 조건에 맞는 이미지가 없습니다.';
    return;
  }

  loader.hidden = true;
  empty.hidden = true;

  const frag = document.createDocumentFragment();

  items.forEach((item) => {
    const card = document.createElement('div');
    card.className = 'card';
    card.innerHTML = `
      <div class="card-thumb">
        <img src="${escapeAttr(item.thumbnail)}" alt="${escapeAttr(item.name)}" loading="lazy">
      </div>
      <span class="badge ${BADGE_CLASS[item.category] || ''}">${BADGE_LABEL[item.category] || item.category}</span>
      <span class="card-date">${item.date}</span>
      <div class="card-info">
        <div class="card-name">${escapeHTML(item.name)}</div>
        <div class="card-sub">${escapeHTML(item.characterName)} · ${escapeHTML(item.gameName)}</div>
      </div>
    `;
    card.addEventListener('click', () => openModal(item));
    frag.appendChild(card);
  });

  grid.innerHTML = '';
  grid.appendChild(frag);
}

/* ── Modal ──────────────────────────────────── */
const overlay = $('overlay');

function openModal(item) {
  state.currentItem = item;
  $('modal-game').textContent = item.gameName;
  $('modal-char').textContent = item.characterName;
  $('modal-name').textContent = '· ' + item.name;
  const img = $('modal-img');
  img.src = '';
  img.src = item.original || item.thumbnail;
  img.alt = item.name;
  overlay.classList.add('open');
  document.body.style.overflow = 'hidden';
}

function closeModal() {
  overlay.classList.remove('open');
  document.body.style.overflow = '';
  // Delay clearing src so transition completes
  setTimeout(() => {
    if (!overlay.classList.contains('open')) {
      $('modal-img').src = '';
      state.currentItem = null;
    }
  }, 220);
}

// Close on overlay background click
overlay.addEventListener('click', (e) => {
  if (e.target === overlay) closeModal();
});

$('btn-close').addEventListener('click', closeModal);

// Keyboard
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape' && overlay.classList.contains('open')) closeModal();
});

/* ── Download ───────────────────────────────── */
$('btn-download').addEventListener('click', async () => {
  const item = state.currentItem;
  if (!item) return;

  const url = item.original || item.thumbnail;
  const ext = url.split('?')[0].split('.').pop() || 'jpg';
  const filename = `${item.game}-${item.id}.${ext}`;

  try {
    const res = await fetch(url, { mode: 'cors' });
    if (!res.ok) throw new Error('CORS blocked');
    const blob = await res.blob();
    const blobUrl = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = blobUrl;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    setTimeout(() => URL.revokeObjectURL(blobUrl), 1000);
  } catch {
    // Fallback: open in new tab (user can save manually)
    window.open(url, '_blank', 'noopener');
  }
});

/* ── Helpers ────────────────────────────────── */
function escapeHTML(str) {
  return String(str ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function escapeAttr(str) {
  return String(str ?? '').replace(/"/g, '&quot;').replace(/'/g, '&#39;');
}

/* ── Start ──────────────────────────────────── */
init();
