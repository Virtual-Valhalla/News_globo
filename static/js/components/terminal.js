/* ════════════════════════════════════════════════════════════════════ */
/* TERMINAL COMPONENT — categories, dropdown, toggleTerminal           */
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
    document.getElementById('cat-label').textContent = CATEGORIES[currentCatIndex].label + ' ▾';
    closeCatDropdown();
}

function toggleCatDropdown() {
    const dd = document.getElementById('cat-dropdown');
    if (dd.style.display === 'block') {
        closeCatDropdown();
        return;
    }
    dd.innerHTML = '';
    CATEGORIES.forEach((cat, i) => {
        const item = document.createElement('div');
        item.className = 'cat-dd-item' + (i === currentCatIndex ? ' cat-dd-active' : '');
        item.textContent = cat.label;
        item.addEventListener('click', e => {
            e.stopPropagation();
            currentCatIndex = i;
            updateCategoryUI();
            loadNews(selectedCountry || 'global');
        });
        dd.appendChild(item);
    });
    dd.style.display = 'block';
}

function closeCatDropdown() {
    const dd = document.getElementById('cat-dropdown');
    if (dd) dd.style.display = 'none';
}

document.addEventListener('click', e => {
    const dd    = document.getElementById('cat-dropdown');
    const label = document.getElementById('cat-label');
    if (dd && label && !dd.contains(e.target) && e.target !== label) {
        closeCatDropdown();
    }
}, true);

function toggleTerminal() {
    const box = document.querySelector('.terminal-box');
    const btn = document.querySelector('.terminal-box-btn');
    isTerminalCollapsed = !isTerminalCollapsed;
    box.classList.toggle('terminal-box-collapsed', isTerminalCollapsed);
    btn.textContent = isTerminalCollapsed ? '+' : '−';
    if (isTerminalCollapsed) closeCatDropdown();
}

// Touch swipe on category row
let _swipeStartX = null;
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('cat-label').textContent = CATEGORIES[0].label + ' ▾';
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
