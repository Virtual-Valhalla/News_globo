/* ════════════════════════════════════════════════════════════════════ */
/* TERMINAL COMPONENT — categories, toggleTerminal                     */
/* ════════════════════════════════════════════════════════════════════ */

let isTerminalCollapsed = false;

const CATEGORIES = [
    { label: 'GENERAL',         api: '' },
    { label: 'TECNOLOGÍA',      api: 'technology' },
    { label: 'NEGOCIOS',        api: 'business' },
    { label: 'DEPORTES',        api: 'sports' },
    { label: 'ENTRETENIMIENTO', api: 'entertainment' },
    { label: 'SALUD',           api: 'health' },
    { label: 'CIENCIA',         api: 'science' },
];
let currentCatIndex = 0;

function prevCategory() {
    currentCatIndex = (currentCatIndex - 1 + CATEGORIES.length) % CATEGORIES.length;
    updateCategoryUI();
    loadNews(selectedCountry || 'global');
}

function nextCategory() {
    currentCatIndex = (currentCatIndex + 1) % CATEGORIES.length;
    updateCategoryUI();
    loadNews(selectedCountry || 'global');
}

function updateCategoryUI() {
    document.getElementById('cat-label').textContent = CATEGORIES[currentCatIndex].label;
}

function toggleTerminal() {
    const box = document.querySelector('.terminal-box');
    const btn = document.querySelector('.terminal-box-btn');
    isTerminalCollapsed = !isTerminalCollapsed;
    box.classList.toggle('terminal-box-collapsed', isTerminalCollapsed);
    btn.textContent = isTerminalCollapsed ? '+' : '−';
}

// Touch swipe on category row
let _swipeStartX = null;
document.addEventListener('DOMContentLoaded', () => {
    const catRow = document.querySelector('.category-row');
    if (!catRow) return;
    catRow.addEventListener('touchstart', e => { _swipeStartX = e.touches[0].clientX; }, { passive: true });
    catRow.addEventListener('touchend', e => {
        if (_swipeStartX === null) return;
        const dx = e.changedTouches[0].clientX - _swipeStartX;
        if (Math.abs(dx) > 40) dx < 0 ? nextCategory() : prevCategory();
        _swipeStartX = null;
    }, { passive: true });
});
