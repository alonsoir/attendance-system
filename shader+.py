import moderngl
import numpy as np
import glfw

# Inicializar GLFW
if not glfw.init():
    raise Exception("No se pudo inicializar GLFW")

# Establecer la versión de OpenGL que queremos usar (por ejemplo, OpenGL 3.3)
glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)

# Crear ventana y contexto
width, height = 800, 600
window = glfw.create_window(width, height, "Shader GLSL", None, None)
if not window:
    glfw.terminate()
    raise Exception("No se pudo crear la ventana")

# Hacer el contexto de OpenGL actual
glfw.make_context_current(window)

# Crear contexto ModernGL, ya que GLFW ha configurado OpenGL
ctx = moderngl.create_context()  # Aquí creamos el contexto ModernGL basado en GLFW

# Verificar la versión de OpenGL disponible
print("Versión de OpenGL:", ctx.version_code)

# Shader GLSL
vertex_shader = """
#version 330 core
in vec2 in_position;
out vec2 texCoord;

void main() {
    gl_Position = vec4(in_position, 0.0, 1.0);
    texCoord = in_position * 0.5 + 0.5;
}
"""

fragment_shader = """
#version 330 core
in vec2 texCoord;
out vec4 FragColor;

void main() {
    vec3 color = vec3(texCoord.x, texCoord.y, 0.5);
    FragColor = vec4(color, 1.0);
}
"""

# Crear el programa de shaders
prog = ctx.program(vertex_shader=vertex_shader, fragment_shader=fragment_shader)

# Cuadrado de pantalla completa
vertices = np.array([
    -1.0, -1.0,
     1.0, -1.0,
    -1.0,  1.0,
     1.0,  1.0,
], dtype='f4')

vbo = ctx.buffer(vertices.tobytes())
vao = ctx.simple_vertex_array(prog, vbo, 'in_position')

# Loop de renderizado
while not glfw.window_should_close(window):
    ctx.clear(0.0, 0.0, 0.0)
    vao.render(moderngl.TRIANGLE_STRIP)
    glfw.swap_buffers(window)
    glfw.poll_events()

# Cleanup
glfw.terminate()
