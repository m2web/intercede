/**
 * newsCard.js — Renders a single news headline card.
 */

export function createNewsCard(item, index) {
    const card = document.createElement('div');
    card.className = 'news-card';

    const titleHtml = item.link
        ? `<a href="${item.link}" target="_blank" rel="noopener noreferrer">${item.title}</a>`
        : item.title;

    card.innerHTML = `
    <div class="card-label">News ${index + 1}</div>
    <h2>${titleHtml}</h2>
    <div class="news-meta">
      <span class="source">${item.source || 'Google News'}</span>
      ${item.published ? `<span class="sep"></span><span>${formatDate(item.published)}</span>` : ''}
    </div>
  `;

    return card;
}

function formatDate(raw) {
    try {
        const d = new Date(raw);
        return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
    } catch {
        return raw;
    }
}
