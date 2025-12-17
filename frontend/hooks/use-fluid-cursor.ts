/**
 * Fluid Cursor Effect Hook
 * Creates an interactive fluid simulation that follows the mouse cursor
 * Based on WebGL fluid dynamics
 */

export default function fluidCursor() {
    const canvas = document.getElementById('fluid') as HTMLCanvasElement;
    if (!canvas) return;

    // Resize canvas to match display size
    function resizeCanvas() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    const gl = canvas.getContext('webgl', { alpha: true });
    if (!gl) {
        console.warn('WebGL not supported');
        return;
    }

    // Enable blending for transparency
    gl.enable(gl.BLEND);
    gl.blendFunc(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA);

    // Vertex shader
    const vertexShaderSource = `
    attribute vec2 a_position;
    void main() {
      gl_Position = vec4(a_position, 0.0, 1.0);
    }
  `;

    // Fragment shader for fluid effect
    const fragmentShaderSource = `
    precision mediump float;
    uniform vec2 u_resolution;
    uniform vec2 u_mouse;
    uniform float u_time;
    
    void main() {
      vec2 st = gl_FragCoord.xy / u_resolution;
      vec2 mouse = u_mouse / u_resolution;
      
      float dist = distance(st, mouse);
      float strength = smoothstep(0.3, 0.0, dist);
      
      // Create fluid-like color gradient
      vec3 color1 = vec3(0.1, 0.2, 0.5);  // Blue
      vec3 color2 = vec3(0.2, 0.4, 0.8);  // Light blue
      vec3 color3 = vec3(0.0, 0.6, 0.4);  // Green
      
      float t = sin(u_time * 0.5) * 0.5 + 0.5;
      vec3 color = mix(mix(color1, color2, t), color3, sin(u_time * 0.3 + dist * 10.0) * 0.5 + 0.5);
      
      // Add some swirl effect
      float swirl = sin(dist * 20.0 - u_time * 2.0) * 0.5 + 0.5;
      color = mix(color, color2, swirl * strength * 0.5);
      
      float alpha = strength * 0.6;
      gl_FragColor = vec4(color, alpha);
    }
  `;

    // Compile shader
    function createShader(gl: WebGLRenderingContext, type: number, source: string) {
        const shader = gl.createShader(type);
        if (!shader) return null;
        gl.shaderSource(shader, source);
        gl.compileShader(shader);
        if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
            console.error('Shader compile error:', gl.getShaderInfoLog(shader));
            gl.deleteShader(shader);
            return null;
        }
        return shader;
    }

    // Create program
    function createProgram(gl: WebGLRenderingContext, vertexShader: WebGLShader, fragmentShader: WebGLShader) {
        const program = gl.createProgram();
        if (!program) return null;
        gl.attachShader(program, vertexShader);
        gl.attachShader(program, fragmentShader);
        gl.linkProgram(program);
        if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
            console.error('Program link error:', gl.getProgramInfoLog(program));
            gl.deleteProgram(program);
            return null;
        }
        return program;
    }

    const vertexShader = createShader(gl, gl.VERTEX_SHADER, vertexShaderSource);
    const fragmentShader = createShader(gl, gl.FRAGMENT_SHADER, fragmentShaderSource);
    if (!vertexShader || !fragmentShader) return;

    const program = createProgram(gl, vertexShader, fragmentShader);
    if (!program) return;

    // Create full-screen quad
    const positionBuffer = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, positionBuffer);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([
        -1, -1,
        1, -1,
        -1, 1,
        -1, 1,
        1, -1,
        1, 1,
    ]), gl.STATIC_DRAW);

    const positionLocation = gl.getAttribLocation(program, 'a_position');
    const resolutionLocation = gl.getUniformLocation(program, 'u_resolution');
    const mouseLocation = gl.getUniformLocation(program, 'u_mouse');
    const timeLocation = gl.getUniformLocation(program, 'u_time');

    let mouseX = 0;
    let mouseY = 0;
    let targetX = 0;
    let targetY = 0;

    canvas.addEventListener('mousemove', (e) => {
        targetX = e.clientX;
        targetY = canvas.height - e.clientY; // Flip Y for WebGL coordinates
    });

    canvas.addEventListener('touchmove', (e) => {
        e.preventDefault();
        const touch = e.touches[0];
        targetX = touch.clientX;
        targetY = canvas.height - touch.clientY;
    });

    let startTime = Date.now();
    let animationId: number;

    function render() {
        // Smooth mouse following
        mouseX += (targetX - mouseX) * 0.1;
        mouseY += (targetY - mouseY) * 0.1;

        gl!.viewport(0, 0, canvas.width, canvas.height);
        gl!.clearColor(0, 0, 0, 0);
        gl!.clear(gl!.COLOR_BUFFER_BIT);

        gl!.useProgram(program);

        gl!.enableVertexAttribArray(positionLocation);
        gl!.bindBuffer(gl!.ARRAY_BUFFER, positionBuffer);
        gl!.vertexAttribPointer(positionLocation, 2, gl!.FLOAT, false, 0, 0);

        gl!.uniform2f(resolutionLocation, canvas.width, canvas.height);
        gl!.uniform2f(mouseLocation, mouseX, mouseY);
        gl!.uniform1f(timeLocation, (Date.now() - startTime) / 1000);

        gl!.drawArrays(gl!.TRIANGLES, 0, 6);

        animationId = requestAnimationFrame(render);
    }

    render();

    // Cleanup function
    return () => {
        cancelAnimationFrame(animationId);
        window.removeEventListener('resize', resizeCanvas);
    };
}
