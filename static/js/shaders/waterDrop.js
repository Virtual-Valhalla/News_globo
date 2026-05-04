const WaterDropShader = {
    uniforms: {
        tDiffuse: { value: null },
        time: { value: 0.0 },
        intensity: { value: 0.8 },
        frequency: { value: 12.0 },
        center: { value: new THREE.Vector2(0.5, 0.5) }
    },
    vertexShader: `
        varying vec2 vUv;
        void main() {
            vUv = uv;
            gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
        }
    `,
    fragmentShader: `
        uniform sampler2D tDiffuse;
        uniform float time;
        uniform float intensity;
        uniform float frequency;
        uniform vec2 center;
        varying vec2 vUv;

        void main() {
            vec2 uv = vUv;
            vec2 dir = uv - center;
            float dist = length(dir);
            
            // Múltiples ondas de gota
            float ripple = sin(dist * frequency - time * 8.0) * 0.5 + 0.5;
            float wave = sin(dist * 25.0 - time * 12.0) * intensity * (1.0 - dist);
            
            uv += normalize(dir) * wave * (1.0 - dist * 0.8);
            
            vec4 color = texture2D(tDiffuse, uv);
            
            // Efecto fresnel cyberpunk
            color.rgb += vec3(0.0, 0.8, 1.0) * wave * 0.6;
            
            gl_FragColor = color;
        }
    `
};