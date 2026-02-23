/**
 * api.js — Fetches prayers from the Intercede backend.
 */

const API_BASE = 'http://localhost:8000';

export async function fetchPrayers() {
    const response = await fetch(`${API_BASE}/api/prayers`);
    if (!response.ok) {
        const err = await response.json().catch(() => ({}));
        throw new Error(err.detail || `Request failed: ${response.status}`);
    }
    return response.json(); // { prayers: [...] }
}
