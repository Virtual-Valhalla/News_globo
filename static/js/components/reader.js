/* ══════════════════════════════════════════════════════════════════════ */
/* READER / DATA-DECRYPTOR COMPONENT — openReader, closeReader         */
/* ══════════════════════════════════════════════════════════════════════ */

function openReader(article) {
    const reader = document.getElementById('news-reader');
    const body   = document.getElementById('reader-body');
    reader.classList.add('reader-visible');

    const pubDate    = article.publishedAt
        ? new Date(article.publishedAt).toLocaleDateString('es-ES',
            { day: 'numeric', month: 'short', year: 'numeric' })
        : '';
    const sourceName = article.source?.name || 'FUENTE DESCONOCIDA';

    // Busca imagen: primero urlToImage (NewsAPI), luego imagen (BD)
    const imageUrl = article.urlToImage || article.imagen;

    const imgHtml = imageUrl
        ? `<div class="reader-media-wrap" id="reader-media">
               <img class="reader-image" src="${imageUrl}" alt=""
                    onerror="this.style.display='none'">
           </div>`
        : `<div class="reader-media-wrap reader-media-loading" id="reader-media">
               <span class="reader-media-spinner">⟳ BUSCANDO MEDIA...</span>
           </div>`;

    body.innerHTML = `
        ${imgHtml}
        <div class="reader-meta">
            <span class="reader-source">▶ ${sourceName.toUpperCase()}</span>
            ${pubDate ? `<span class="reader-date">${pubDate}</span>` : ''}
        </div>
        <p class="reader-title">${article.title || ''}</p>
        <p class="reader-desc">${article.description || 'Sin resumen disponible.'}</p>
        <a href="${article.url}" target="_blank" class="news-link">[ ACCEDER A FUENTE EXTERNA → ]</a>
    `;

    fetch(`/article?url=${encodeURIComponent(article.url)}`)
        .then(r => r.json())
        .then(data => {
            const mediaEl = document.getElementById('reader-media');
            if (!mediaEl) return;
            const v = data.video;
            if (v && v.type === 'youtube' && v.url) {
                mediaEl.innerHTML = `
                    <iframe class="reader-video"
                        src="${v.url}" frameborder="0"
                        allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                        allowfullscreen></iframe>`;
                mediaEl.classList.remove('reader-media-loading');
                logToConsole('▶ Video de YouTube encontrado y embebido', 'success');
            } else if (v && v.type === 'video' && v.url) {
                mediaEl.innerHTML = `
                    <video class="reader-video" controls preload="metadata">
                        <source src="${v.url}">
                    </video>`;
                mediaEl.classList.remove('reader-media-loading');
                logToConsole('▶ Video HTML5 encontrado', 'success');
            } else if (!imageUrl) {
                mediaEl.classList.add('reader-media-empty');
                mediaEl.innerHTML = `<span class="reader-no-media">[ SIN MEDIA DISPONIBLE ]</span>`;
            } else {
                mediaEl.classList.remove('reader-media-loading');
            }
        })
        .catch(() => {
            const mediaEl = document.getElementById('reader-media');
            if (mediaEl && !imageUrl) {
                mediaEl.innerHTML = `<span class="reader-no-media">[ ERROR CARGANDO MEDIA ]</span>`;
            }
        });
}

function closeReader() {
    document.getElementById('news-reader').classList.remove('reader-visible');
}

function loadArticle(url) {
    const viewer = document.getElementById('articleViewer');
    viewer.style.display = 'block';
    viewer.innerHTML = 'Cargando artículo...';
    fetch(`/article?url=${encodeURIComponent(url)}`)
        .then(res => res.json())
        .then(data => {
            viewer.innerHTML = `
                <h2 style="color:#00ffff;">${data.title}</h2>
                <hr>
                <p style="white-space:pre-line;">${data.content}</p>
                <br>
                <a href="${url}" target="_blank" style="color:#ff00ff;">🔗 Ver original</a>
            `;
        })
        .catch(err => {
            viewer.innerHTML = 'Error cargando artículo';
            console.error(err);
        });
}
