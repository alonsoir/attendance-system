from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import pygame
import numpy as np

# Shaders ajustados para compatibilidad con macOS
vertex_shader_code = """#version 120
attribute vec3 position;
varying vec2 v_uv;

void main() {
    gl_Position = vec4(position, 1.0);
    v_uv = position.xy * 0.5 + 0.5;
}"""

fragment_shader_code = """#version 120
uniform float time;
uniform vec2 resolution;
varying vec2 v_uv;

float calabiYau(vec3 p) {
    float scale = 1.0;
    for (int i = 0; i < 5; i++) {  // Reducir iteraciones para mejor rendimiento
        p = abs(p) * scale - 1.0;
        scale *= 0.75;
        p = mod(p + 1.5, 3.0) - 1.5;
    }
    return length(p) - 0.2;
}

void main() {
    vec2 uv = (v_uv - 0.5) * 2.0;
    uv.x *= resolution.x / resolution.y;

    // Animación intensa (x3 velocidad)
    vec3 p = vec3(uv * 3.0, time * 3.0);  // Movimiento rápido en Z

    // Rotación 2D visible
    float angle = time * 2.5;
    p.xy = mat2(cos(angle), -sin(angle), sin(angle), cos(angle)) * p.xy;

    float d = calabiYau(p);
    float intensity = smoothstep(0.03, 0.0, abs(d));

    // Colores altamente dinámicos
    vec3 color = mix(
        vec3(0.1, 0.1, 0.5),
        vec3(1.0, 0.3, 0.7),
        intensity * (1.5 + sin(time * 4.0))
    );

    gl_FragColor = vec4(color * intensity * 2.5, 1.0);
}"""


def compile_shaders():
    vertex_shader = compileShader(vertex_shader_code, GL_VERTEX_SHADER)
    fragment_shader = compileShader(fragment_shader_code, GL_FRAGMENT_SHADER)
    return compileProgram(vertex_shader, fragment_shader)


def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600), pygame.OPENGL | pygame.DOUBLEBUF)
    pygame.display.set_caption("Calabi-Yau Animación Intensa - macOS")

    # Forzar contexto OpenGL 2.1 (compatible con macOS)
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 2)
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 1)

    shader = compile_shaders()

    # Geometría del quad
    vertices = np.array([
        -1.0, -1.0, 0.0, 1.0, -1.0, 0.0, -1.0, 1.0, 0.0,
        1.0, -1.0, 0.0, 1.0, 1.0, 0.0, -1.0, 1.0, 0.0
    ], dtype=np.float32)

    vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

    position = glGetAttribLocation(shader, "position")
    glEnableVertexAttribArray(position)
    glVertexAttribPointer(position, 3, GL_FLOAT, False, 0, None)

    time_loc = glGetUniformLocation(shader, "time")
    res_loc = glGetUniformLocation(shader, "resolution")

    clock = pygame.time.Clock()
    start_time = pygame.time.get_ticks() / 1000.0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        glClear(GL_COLOR_BUFFER_BIT)
        glUseProgram(shader)

        current_time = pygame.time.get_ticks() / 1000.0 - start_time
        glUniform1f(time_loc, current_time)
        glUniform2f(res_loc, 800.0, 600.0)

        glDrawArrays(GL_TRIANGLES, 0, 6)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()