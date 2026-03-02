/**
 * prayerCard.js — Renders a single ESV verse + reflection + prayer card.
 */

export function createPrayerCard(item, index) {
  const card = document.createElement('div');
  card.className = 'prayer-card';

  // esv_verse = verse text, esv_ref = "Book Chapter:Verse" (separate fields)
  let verseHtml = '';
  if (item.esv_verse) {
    verseHtml = `
            <blockquote class="verse">${item.esv_verse}</blockquote>
            ${item.esv_ref ? `<cite class="verse-ref">— ${item.esv_ref}</cite>` : ''}
        `;
  }

  card.innerHTML = `
    <div class="card-label">Intercessory Prayer ${index + 1}</div>
    ${verseHtml}
    ${item.reflection ? `<p class="reflection">${item.reflection}</p>` : ''}
    <p class="prayer-text">${item.prayer || ''}</p>
  `;

  return card;
}
