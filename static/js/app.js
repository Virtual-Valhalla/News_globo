/* ════════════════════════════════════════════════════════════════════ */
/* APP — selectNode, loadNews, resetToGlobal, window.onload            */
/* ════════════════════════════════════════════════════════════════════ */

let selectedCountry     = null;
let selectedCountryName = null;

function selectNode(name, code, lat, lng) {
    if (!name || name === 'undefined' || name === '') {
        logToConsole(`❌ Nombre de país inválido (${name})`, 'error');
        return;
    }
    const normalizedCode = String(code || name).toLowerCase().trim();
    logToConsole(`📍 Seleccionando: ${name} (${normalizedCode})`, 'debug');

    selectedCountry     = normalizedCode;
    selectedCountryName = name;

    document.getElementById('node-label').innerText = `NODE: ${name.toUpperCase()}`;
    document.getElementById('back-button').style.display = 'block';

    const validLat = isNaN(lat) ? 0 : lat;
    const validLng = isNaN(lng) ? 0 : lng;

    world.pointOfView({ lat: validLat, lng: validLng, altitude: 0.6 }, 1000);
    world.controls().autoRotateSpeed = BASE_ROTATION_SPEED * 0.1;
    loadNews(normalizedCode);
}

function loadNews(code) {
    const container = document.getElementById('news-container');

    if (!code || code === 'undefined' || code === '' || code === null) {
        logToConsole(`❌ Intento de cargar noticias con código inválido: "${code}"`, 'error');
        container.innerHTML = `
            <div class="error-box">
                <strong>❌ CÓDIGO INVÁLIDO</strong><br>
                Por favor, selecciona un país válido.
            </div>`;
        return;
    }

    container.innerHTML = `<div class="status-line">> ACCEDIENDO A SECTOR ${code}...</div>`;
    logToConsole(`Solicitando noticias para: ${code}`, 'info');

    const encodedCode = encodeURIComponent(code);
    const cat         = CATEGORIES[currentCatIndex].api;
    const newsUrl     = `/country-news?country=${encodedCode}${cat ? '&category=' + cat : ''}`;
    logToConsole(`📨 Endpoint: ${newsUrl}`, 'debug');

    fetch(newsUrl)
        .then(res => {
            logToConsole(`Status HTTP: ${res.status}`, 'debug');
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            return res.json();
        })
        .then(data => {
            if (data.status === 'error') {
                logToConsole(`❌ ${data.type}: ${data.message}`, 'error');
                container.innerHTML = `
                    <div class="error-box">
                        <strong>❌ ${data.type}</strong><br>
                        ${data.message}<br>
                        <small>${data.details || ''}</small><br>
                        <button class="retry-btn" onclick="loadNews('${code}')">↻ REINTENTAR</button>
                    </div>`;
                return;
            }
            if (data.status === 'warning' || !data.articles || data.articles.length === 0) {
                logToConsole(`⚠️ Sin artículos para ${code}`, 'warning');
                container.innerHTML = `
                    <div class="error-box">
                        <strong>⚠️ SIN RESULTADOS</strong><br>
                        ${data.message}<br>
                        <button class="retry-btn" onclick="loadNews('${code}')">↻ REINTENTAR</button>
                    </div>`;
                return;
            }
            const articles = data.articles;
            const cacheMsg = data.cached
                ? `⚡ CACHÉ (expira en ${data.expires_in})`
                : '🌐 API (datos frescos)';
            logToConsole(`✅ ${articles.length} noticias para ${code.toUpperCase()} — ${cacheMsg}`, 'success');

            container.innerHTML = '';
            articles.forEach((art, idx) => {
                const div = document.createElement('div');
                div.className = 'news-item';
                const src = art.source?.name ? `<span class="news-src">${art.source.name}</span>` : '';
                div.innerHTML = `
                    <div class="news-item-body">
                        <span class="news-rank">${String(idx + 1).padStart(2, '0')}</span>
                        <span class="news-title-text">${art.title}</span>
                        ${src}
                    </div>`;
                div.onclick = () => openReader(art);
                container.appendChild(div);
            });
        })
        .catch(err => {
            logToConsole(`🔌 Error de conexión: ${err.message}`, 'error');
            container.innerHTML = `
                <div class="error-box">
                    <strong>❌ ERROR</strong><br>
                    ${err.message}<br>
                    <button class="retry-btn" onclick="loadNews('${code}')">↻ REINTENTAR</button>
                </div>`;
        });
}

function resetToGlobal() {
    logToConsole('Reseteando a vista global', 'info');
    selectedCountry = null;
    closeReader();
    document.getElementById('node-label').innerText = 'NODE: GLOBAL FEED';
    document.getElementById('back-button').style.display = 'none';
    world.pointOfView({ lat: 20, lng: 0, altitude: 1.5 }, 1000);
    world.controls().autoRotateSpeed = BASE_ROTATION_SPEED;
    loadNews('global');
}

window.onload = () => {
    logToConsole('Aplicación cargada', 'success');
    initIntro();
};
