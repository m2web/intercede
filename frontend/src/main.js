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
    <h1>Daily Intercessory Prayer</h1>
    <p class="tagline">Reasoning over today's headlines to lift up the world in prayer.</p>
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
      <p class="loading-text">Gathering today's headlines and crafting prayers…</p>
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
