/* ══════════════════════════════════════════════════════════════════════ */
/* READER / DATA-DECRYPTOR COMPONENT — openReader, closeReader          */
/* Media priority: 1) Video  2) Image  3) No media                     */
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

    // Initial image from article data (may be replaced by video after fetch)
    const imageUrl = article.urlToImage || article.imagen || null;

    // Show loading state for media while we fetch the full article
    body.innerHTML = `
        <div class="reader-media-wrap reader-media-loading" id="reader-media">
            <span class="reader-media-spinner">⟳ BUSCANDO MEDIA...</span>
        </div>
        <div class="reader-meta">
            <span class="reader-source">▶ ${sourceName.toUpperCase()}</span>
            ${pubDate ? `<span class="reader-date">${pubDate}</span>` : ''}
        </div>
        <p class="reader-title">${article.title || ''}</p>
        <p class="reader-desc">${article.description || 'Sin resumen disponible.'}</p>
        <div id="reader-full-content" class="reader-full-content"></div>
        <a href="${article.url}" target="_blank" class="news-link">[ ACCEDER A FUENTE EXTERNA → ]</a>
    `;

    // Show existing image immediately while fetching full content
    if (imageUrl) {
        const mediaEl = document.getElementById('reader-media');
        if (mediaEl) {
            mediaEl.classList.remove('reader-media-loading');
            mediaEl.innerHTML = `<img class="reader-image" src="${imageUrl}" alt=""
                onerror="this.closest('.reader-media-wrap').classList.add('reader-media-empty'); this.closest('.reader-media-wrap').innerHTML='<span class=\\'reader-no-media\\'>[SIN IMAGEN DISPONIBLE]</span>'">`;
        }
    }

    // Fetch full article content and upgrade media if possible
    fetch(`/article?url=${encodeURIComponent(article.url)}`)
        .then(r => r.json())
        .then(data => {
            const mediaEl = document.getElementById('reader-media');

            // ── PRIORIDAD 1: VIDEO ──────────────────────────────────────────
            const multimedia = Array.isArray(data.multimedia) ? data.multimedia : [];
            const videoItem  = multimedia.find(m => m.type === 'video');

            if (videoItem && videoItem.embed_url) {
                const src    = videoItem.embed_url;
                const isYT   = src.includes('youtube.com') || src.includes('youtu.be');
                const isVimeo = src.includes('vimeo.com');

                if (isYT || isVimeo) {
                    if (mediaEl) {
                        mediaEl.classList.remove('reader-media-loading');
                        mediaEl.innerHTML = `
                            <iframe class="reader-video"
                                src="${src}" frameborder="0"
                                allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                                allowfullscreen></iframe>`;
                    }
                    logToConsole('▶ Video embebido encontrado', 'success');
                } else {
                    // HTML5 video
                    if (mediaEl) {
                        mediaEl.classList.remove('reader-media-loading');
                        mediaEl.innerHTML = `
                            <video class="reader-video" controls preload="metadata">
                                <source src="${src}">
                            </video>`;
                    }
                    logToConsole('▶ Video HTML5 encontrado', 'success');
                }
            }
            // ── PRIORIDAD 2: IMAGEN ─────────────────────────────────────────
            else {
                const finalImage = data.imagen || imageUrl;
                if (finalImage && mediaEl) {
                    mediaEl.classList.remove('reader-media-loading');
                    // Only update if we have a better image from the extractor
                    if (data.imagen && data.imagen !== imageUrl) {
                        mediaEl.innerHTML = `<img class="reader-image" src="${data.imagen}" alt=""
                            onerror="this.closest('.reader-media-wrap').classList.add('reader-media-empty'); this.closest('.reader-media-wrap').innerHTML='<span class=\\'reader-no-media\\'>[SIN IMAGEN DISPONIBLE]</span>'">`;
                    }
                }
                // ── PRIORIDAD 3: SIN MEDIA ──────────────────────────────────
                else if (!finalImage && mediaEl) {
                    mediaEl.classList.add('reader-media-empty');
                    mediaEl.innerHTML = `<span class="reader-no-media">[ SIN MEDIA DISPONIBLE ]</span>`;
                    logToConsole('ℹ️ Sin media disponible para este artículo', 'info');
                }
            }

            // ── CONTENIDO COMPLETO ──────────────────────────────────────────
            const contentEl = document.getElementById('reader-full-content');
            if (contentEl) {
                // Priority: full contenido → resumen fallback → nothing
                const contenido = data.contenido || data.content || '';
                const resumen   = data.resumen || '';
                const text      = (contenido.length >= resumen.length) ? contenido : resumen;
                if (text && text.length > 30) {
                    const label = contenido.length > 30 ? '── CONTENIDO COMPLETO ──' : '── RESUMEN ──';
                    contentEl.innerHTML = `
                        <div class="reader-content-divider">${label}</div>
                        <div class="reader-content-text">${escapeHtml(text)}</div>`;
                }
            }
        })
        .catch(err => {
            logToConsole(`⚠️ Error cargando artículo: ${err.message}`, 'warning');
            const mediaEl = document.getElementById('reader-media');
            if (mediaEl) {
                if (!imageUrl) {
                    mediaEl.classList.add('reader-media-empty');
                    mediaEl.innerHTML = `<span class="reader-no-media">[ ERROR CARGANDO MEDIA ]</span>`;
                } else {
                    mediaEl.classList.remove('reader-media-loading');
                }
            }
        });
}

function escapeHtml(text) {
    return text
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/\n/g, '<br>');
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
                <h2 style="color:#00ffff;">${data.titulo || data.title || ''}</h2>
                <hr>
                <p style="white-space:pre-line;">${data.contenido || data.content || ''}</p>
                <br>
                <a href="${url}" target="_blank" style="color:#ff00ff;">🔗 Ver original</a>
            `;
        })
        .catch(err => {
            viewer.innerHTML = 'Error cargando artículo';
            console.error(err);
        });
}
