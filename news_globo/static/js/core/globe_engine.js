/* ════════════════════════════════════════════════════════════════════ */
/* GLOBE ENGINE — Three.js / Globe.gl initialization & GeoJSON loader  */
/* ════════════════════════════════════════════════════════════════════ */

let world;
let hoverD = null;
const BASE_ROTATION_SPEED = 0.5;

world = Globe()(document.getElementById('globeViz'))
    .globeImageUrl('//unpkg.com/three-globe/example/img/earth-night.jpg')
    .backgroundImageUrl('//unpkg.com/three-globe/example/img/night-sky.png')
    .polygonSideColor(() => 'rgba(255, 0, 255, 0.2)')
    .polygonStrokeColor(() => '#ff00ff')
    .polygonCapColor(d => d === hoverD ? 'rgba(0, 255, 255, 0.3)' : 'rgba(0, 255, 255, 0.00)')
    .polygonAltitude(d => d === hoverD ? 0.05 : 0.00175)
    .pointColor(() => '#ff00ff')
    .pointAltitude(0.07)
    .pointRadius(0.5)
    .pointsMerge(true)
    .onPolygonHover(poly => {
        hoverD = poly;
        world.polygonAltitude(world.polygonAltitude());
    })
    .onPolygonClick((polygon, event, { lat, lng }) => {
        logToConsole('🖱️ Polígono clickeado. Inspeccionando propiedades...', 'debug');
        const d = polygon.properties;
        const name = d.ADMIN || d.name || d.NAME || 'Unknown Country';
        let code = d.ISO_A2 || d.iso_a2 || '-99';
        if (code === '-99' || !code) code = d.ISO_A2_EH || '-99';
        if (code === '-99' || !code) code = d.WB_A2     || '-99';
        if (code === '-99' || !code) {
            code = name.toLowerCase().replace(/[\s,.'()]+/g, '_');
            logToConsole(`⚠️ Sin código ISO para "${name}", buscando por nombre`, 'warning');
        }
        selectNode(name, code.toLowerCase(), lat, lng);
    })
    .onPointClick(pt => selectNode(pt.name, pt.id, pt.lat, pt.lng))
    .onGlobeClick(() => { if (selectedCountry) resetToGlobal(); });

window.myGlobe = world;

world.pointOfView({ lat: 25, lng: 0, altitude: 100.0 }, 0);
world.controls().autoRotate = false;

window.addEventListener('resize', () => {
    const container = document.getElementById('globeViz');
    world.width(container.clientWidth);
    world.height(container.clientHeight);
});

world.controls().autoRotate = true;
world.controls().autoRotateSpeed = BASE_ROTATION_SPEED;

const tiltAng = 0.05;
world.scene().rotation.z = tiltAng;
world.scene().rotation.x = 0.1;

// ── GeoJSON loader ────────────────────────────────────────────────────────────
logToConsole('Cargando GeoJSON...', 'info');

fetch('https://raw.githubusercontent.com/martynafford/natural-earth-geojson/refs/heads/master/110m/cultural/ne_110m_admin_0_countries_lakes.json')
    .then(res => {
        if (!res.ok) throw new Error('No se pudo cargar GeoJSON');
        return res.json();
    })
    .then(countries => {
        const cleanFeatures = countries.features.filter(f =>
            f.properties &&
            (f.properties.ADMIN || f.properties.name || f.properties.NAME)
        );
        if (cleanFeatures.length === 0) {
            logToConsole('❌ No se encontraron países válidos en el GeoJSON', 'error');
            return;
        }
        logToConsole(`✅ ${cleanFeatures.length} países cargados correctamente`, 'success');
        world.polygonsData(cleanFeatures);
    })
    .catch(err => {
        logToConsole(`Error cargando GeoJSON: ${err.message}`, 'error');
        console.error('GeoJSON Error:', err);
    });
