/**
 * main.js — Intercede app entry point.
 * Wires together the loading state, API call, and card rendering.
 */

import './style.css';
import { fetchPrayers } from './api.js';
import { createNewsCard } from './newsCard.js';
import { createPrayerCard } from './prayerCard.js';

// ── App state ─────────────────────────────────────────────
let isLoading = false;

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
    <button class="refresh-btn" id="refreshBtn" ${isLoading ? 'disabled' : ''}>
      <svg class="${isLoading ? 'spin' : ''}" xmlns="http://www.w3.org/2000/svg" width="15" height="15"
           viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
           stroke-linecap="round" stroke-linejoin="round">
        <path d="M21 2v6h-6"/><path d="M3 12a9 9 0 0 1 15-6.7L21 8"/>
        <path d="M3 22v-6h6"/><path d="M21 12a9 9 0 0 1-15 6.7L3 16"/>
      </svg>
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
    render();         // re-render to disable button & show spinner on it
    renderLoading();

    try {
        const data = await fetchPrayers();
        renderPrayers(data.prayers || []);
    } catch (err) {
        renderError(err.message || 'Could not connect to the Intercede API. Is the backend running?');
    } finally {
        isLoading = false;
        // Update button state without full re-render
        const btn = document.getElementById('refreshBtn');
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = `
        <svg xmlns="http://www.w3.org/2000/svg" width="15" height="15"
             viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
             stroke-linecap="round" stroke-linejoin="round">
          <path d="M21 2v6h-6"/><path d="M3 12a9 9 0 0 1 15-6.7L21 8"/>
          <path d="M3 22v-6h6"/><path d="M21 12a9 9 0 0 1-15 6.7L3 16"/>
        </svg>
        Refresh Prayers
      `;
        }
    }
}

// Boot
render();
loadPrayers();
