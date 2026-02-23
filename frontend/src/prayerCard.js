/**
 * prayerCard.js — Renders a single ESV verse + reflection + prayer card.
 */

export function createPrayerCard(item, index) {
    const card = document.createElement('div');
    card.className = 'prayer-card';

    card.innerHTML = `
    <div class="card-label">Intercessory Prayer ${index + 1}</div>
    ${item.esv_verse ? `<blockquote class="verse">${item.esv_verse}</blockquote>` : ''}
    ${item.reflection ? `<p class="reflection">${item.reflection}</p>` : ''}
    <p class="prayer-text">${item.prayer || ''}</p>
  `;

    return card;
}
