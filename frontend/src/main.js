/**
 * main.js — Intercede app entry point.
 * Wires together the loading state, API call, and card rendering.
 */

import './style.css';
import { fetchPrayers } from './api.js';
import { createNewsCard } from './newsCard.js';
import { createPrayerCard } from './prayerCard.js';

// ── Constants ─────────────────────────────────────────────
const COOLDOWN_MS = 30 * 60 * 1000; // 30 minutes
const STORAGE_KEY = 'intercede_last_fetch';

// ── App state ─────────────────────────────────────────────
let isLoading = false;
let cooldownInterval = null;

/** Returns milliseconds remaining in cooldown, or 0 if expired. */
function cooldownRemaining() {
  const last = parseInt(localStorage.getItem(STORAGE_KEY) || '0', 10);
  const elapsed = Date.now() - last;
  return Math.max(0, COOLDOWN_MS - elapsed);
}

/** Formats milliseconds as "mm:ss". */
function formatCountdown(ms) {
  const totalSec = Math.ceil(ms / 1000);
  const m = Math.floor(totalSec / 60).toString().padStart(2, '0');
  const s = (totalSec % 60).toString().padStart(2, '0');
  return `${m}:${s}`;
}

/**
 * Stamps the current time as the last fetch, then starts a countdown
 * interval that updates the button label and re-enables it when done.
 */
function startCooldown() {
  localStorage.setItem(STORAGE_KEY, Date.now().toString());
  applyCooldownToButton();
}

/** Disables the button and ticks a countdown until the cooldown expires. */
function applyCooldownToButton() {
  if (cooldownInterval) clearInterval(cooldownInterval);

  const tick = () => {
    const btn = document.getElementById('refreshBtn');
    if (!btn) { clearInterval(cooldownInterval); return; }

    const remaining = cooldownRemaining();
    if (remaining <= 0) {
      clearInterval(cooldownInterval);
      cooldownInterval = null;
      btn.disabled = false;
      btn.innerHTML = refreshIcon() + ' Refresh Prayers';
      return;
    }
    btn.disabled = true;
    btn.innerHTML = refreshIcon() + ` Available in ${formatCountdown(remaining)}`;
  };

  tick(); // run immediately so there's no 1-second blank
  cooldownInterval = setInterval(tick, 1000);
}

/** Returns the SVG refresh icon markup. */
function refreshIcon(spinning = false) {
  return `<svg class="${spinning ? 'spin' : ''}" xmlns="http://www.w3.org/2000/svg" width="15" height="15"
         viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
         stroke-linecap="round" stroke-linejoin="round">
      <path d="M21 2v6h-6"/><path d="M3 12a9 9 0 0 1 15-6.7L21 8"/>
      <path d="M3 22v-6h6"/><path d="M21 12a9 9 0 0 1-15 6.7L3 16"/>
    </svg>`;
}

// ── DOM root ──────────────────────────────────────────────
const root = document.getElementById('app');

function render() {
  root.innerHTML = '';

  // Header
  const header = document.createElement('header');
  header.className = 'app-header';
  header.innerHTML = `
    <div class="logo-mark"><span class="dot"></span> Intercede</div>
    <h1>Intercede Now</h1>
    <p class="tagline">AI reasoning over current headlines to help you lift up the world in prayer.</p>
    <button class="refresh-btn" id="refreshBtn">
      ${refreshIcon(isLoading)}
      ${isLoading ? 'Generating prayers…' : 'Refresh Prayers'}
    </button>
  `;
  root.appendChild(header);

  // Date badge
  const dateBadge = document.createElement('div');
  dateBadge.className = 'date-badge';
  dateBadge.textContent = new Date().toLocaleDateString('en-US', {
    weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'
  });
  root.appendChild(dateBadge);

  // Content area (loading / error / prayers managed dynamically)
  const content = document.createElement('div');
  content.id = 'content';
  root.appendChild(content);

  // Footer
  const footer = document.createElement('footer');
  footer.className = 'app-footer';
  footer.innerHTML = `
    <p>"I urge that supplications, prayers, intercessions, and thanksgivings be made for all people…" — 1 Timothy 2:1 (ESV)</p>
    <a class="github-link" href="https://github.com/m2web/intercede" target="_blank" rel="noopener noreferrer">
      <svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
        <path d="M12 2C6.477 2 2 6.477 2 12c0 4.418 2.865 8.166 6.839 9.489.5.092.682-.217.682-.482
          0-.237-.009-.868-.013-1.703-2.782.604-3.369-1.342-3.369-1.342-.454-1.154-1.11-1.462-1.11-1.462
          -.908-.62.069-.608.069-.608 1.003.07 1.531 1.03 1.531 1.03.892 1.529 2.341 1.087 2.91.832
          .092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.11-4.555-4.943 0-1.091.39-1.984 1.029-2.683
          -.103-.253-.446-1.27.098-2.647 0 0 .84-.269 2.75 1.025A9.578 9.578 0 0 1 12 6.836a9.59 9.59 0
          0 1 2.504.337c1.909-1.294 2.747-1.025 2.747-1.025.546 1.377.202 2.394.1 2.647.64.699 1.028
          1.592 1.028 2.683 0 3.842-2.339 4.687-4.566 4.935.359.309.678.919.678 1.852 0 1.336-.012
          2.415-.012 2.743 0 .267.18.579.688.481C19.138 20.163 22 16.418 22 12c0-5.523-4.477-10-10-10z"/>
      </svg>
      View on GitHub
    </a>
  `;
  root.appendChild(footer);

  // Wire refresh button
  document.getElementById('refreshBtn').addEventListener('click', loadPrayers);
}

function renderLoading() {
  const content = document.getElementById('content');
  content.innerHTML = `
    <div class="loading-container">
      <div class="neural-loader">
        <span></span><span></span><span></span>
      </div>
      <p class="loading-text">Gathering today's headlines and crafting prayers...this will take time...builds patience. 😊</p>
    </div>
  `;
}

function renderError(message) {
  const content = document.getElementById('content');
  content.innerHTML = `
    <div class="error-box">
      <strong>Something went wrong</strong>
      <p>${message}</p>
    </div>
  `;
}

function renderPrayers(prayers) {
  const content = document.getElementById('content');
  content.innerHTML = '';

  const grid = document.createElement('div');
  grid.className = 'prayers-grid';

  prayers.forEach((item, i) => {
    const block = document.createElement('div');
    block.className = 'prayer-block';
    block.appendChild(createNewsCard(item, i));
    block.appendChild(createPrayerCard(item, i));
    grid.appendChild(block);
  });

  content.appendChild(grid);
}

async function loadPrayers() {
  if (isLoading) return;
  isLoading = true;

  // Show spinner on the button without re-rendering the whole page
  const btn = document.getElementById('refreshBtn');
  if (btn) {
    btn.disabled = true;
    btn.innerHTML = refreshIcon(true) + ' Generating prayers…';
  }

  renderLoading();

  try {
    const data = await fetchPrayers();

    // Treat an empty prayers array as a failure — don't start the countdown
    if (!data.prayers || data.prayers.length === 0) {
      throw new Error('The server returned no prayers. Please try again.');
    }

    renderPrayers(data.prayers);

    // ✅ Only on complete success: lock the button for 30 minutes
    startCooldown();
    applyCooldownToButton();

  } catch (err) {
    renderError(err.message || 'Could not connect to the Intercede API. Is the backend running?');

    // ❌ On any error: re-enable button immediately, no countdown
    const errBtn = document.getElementById('refreshBtn');
    if (errBtn) {
      errBtn.disabled = false;
      errBtn.innerHTML = refreshIcon() + ' Refresh Prayers';
    }

  } finally {
    isLoading = false;
  }
}

// Boot
render();
// Restore any existing cooldown (disables button if still within 30-min window)
if (cooldownRemaining() > 0) applyCooldownToButton();
