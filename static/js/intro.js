// static/js/intro.js
console.log("%c[INTRO] Sistema estable cargado", "color:#00ffff; font-weight:bold");

let centralPoint;
let isIntroActive = true;

window.initIntro = function() {
    if (!window.myGlobe) {
        console.warn("[INTRO] Esperando globo...");
        setTimeout(window.initIntro, 500);
        return;
    }

    const globe = window.myGlobe;
    const scene = globe.scene();

    // Crear punto (más grande y visible)
    centralPoint = new THREE.Mesh(
        new THREE.SphereGeometry(0.028, 32, 32),
        new THREE.MeshBasicMaterial({ 
            color: 0x77eeff, 
            transparent: true, 
            opacity: 1 
        })
    );
    scene.add(centralPoint);

    // Parpadeo más pronunciado
    gsap.to(centralPoint.material, {
        opacity: 0.15,
        duration: 0.6,
        repeat: -1,
        yoyo: true,
        ease: "power2.inOut"
    });

    console.log("%c[INTRO] ✅ Punto central creado y visible", "color:#00ffcc; font-size:15px");
};

// Click para zoom
document.addEventListener('click', () => {
    if (!isIntroActive) return;
    isIntroActive = false;

    const globe = window.myGlobe;
    if (!globe || !centralPoint) return;

    console.log("%c[INTRO] Click detectado → Zoom", "color:#ff00ff");

    // Desaparecer punto
    gsap.to(centralPoint.scale, {
        x: 0.01,
        y: 0.01,
        z: 0.01,
        duration: 1.4,
        ease: "power2.in"
    });

    // Zoom al globo
    gsap.to(globe.pointOfView(), {
        altitude: 1.65,
        duration: 4.0,
        ease: "power2.inOut",
        onStart: () => globe.controls().autoRotate = false,
        onUpdate: () => globe.controls().update(),
        onComplete: () => {
            globe.controls().autoRotate = true;
            globe.controls().autoRotateSpeed = 0.5;
            logToConsole('🔓 INTRO COMPLETADA - BIENVENIDO AL GLOBO', 'success');
            resetToGlobal();
        }
    });
});