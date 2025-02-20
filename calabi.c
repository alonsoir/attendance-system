#define GL_SILENCE_DEPRECATION
#include <GLFW/glfw3.h>
#include <OpenGL/gl3.h>  // <-- Añade este header
#include <stdio.h>
#include <math.h>

// Shaders optimizados para macOS
const char* vertex_shader_code =
    "#version 410 core\n"
    "layout(location = 0) in vec3 position;"
    "out vec2 uv;"
    "void main() {"
    "    gl_Position = vec4(position, 1.0);"
    "    uv = position.xy * 0.5 + 0.5;"
    "}";

const char* fragment_shader_code =
    "#version 410 core\n"
    "uniform float time;"
    "uniform vec2 resolution;"
    "in vec2 uv;"
    "out vec4 fragColor;"
    "void main() {"
    "    vec2 coord = uv * 2.0 - 1.0;"
    "    coord.x *= resolution.x / resolution.y;"
    "    fragColor = vec4("
    "        0.5 + 0.5 * sin(time + coord.x * 5.0),"
    "        0.5 + 0.5 * cos(time + coord.y * 5.0),"
    "        1.0,"
    "        1.0"
    "    );"
    "}";

GLuint compile_shader(GLenum type, const char* source) {
    GLuint shader = glCreateShader(type);
    glShaderSource(shader, 1, &source, NULL);
    glCompileShader(shader);

    GLint success;
    glGetShaderiv(shader, GL_COMPILE_STATUS, &success);
    if (!success) {
        char infoLog[512];
        glGetShaderInfoLog(shader, 512, NULL, infoLog);
        printf("ERROR de shader: %s\n", infoLog);
        return 0;
    }
    return shader;
}

int main() {
    // 1. Inicializar GLFW
    if (!glfwInit()) {
        printf("Error inicializando GLFW\n");
        return -1;
    }
    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 4);
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 1);
    glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);
    glfwWindowHint(GLFW_OPENGL_FORWARD_COMPAT, GL_TRUE);
    // 2. Configurar versión de OpenGL
    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 4);
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 1);
    glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);
    glfwWindowHint(GLFW_OPENGL_FORWARD_COMPAT, GL_TRUE);
    glfwWindowHint(GLFW_COCOA_RETINA_FRAMEBUFFER, GL_FALSE);

    // 3. Crear ventana
    GLFWwindow* window = glfwCreateWindow(800, 600, "Calabi-Yau macOS", NULL, NULL);
    if (!window) {
        printf("Error creando ventana\n");
        glfwTerminate();
        return -1;
    }
    glfwMakeContextCurrent(window);

    // 4. Compilar shaders
    GLuint vertex_shader = compile_shader(GL_VERTEX_SHADER, vertex_shader_code);
    GLuint fragment_shader = compile_shader(GL_FRAGMENT_SHADER, fragment_shader_code);

    if (!vertex_shader || !fragment_shader) {
        glfwTerminate();
        return -1;
    }

    // 5. Crear programa
    GLuint program = glCreateProgram();
    glAttachShader(program, vertex_shader);
    glAttachShader(program, fragment_shader);
    glLinkProgram(program);

    GLint link_success;
    glGetProgramiv(program, GL_LINK_STATUS, &link_success);
    if (!link_success) {
        char infoLog[512];
        glGetProgramInfoLog(program, 512, NULL, infoLog);
        printf("Error linkando programa: %s\n", infoLog);
        return -1;
    }

    // 6. Configurar geometría
    float vertices[] = {
        -1.0f, -1.0f, 0.0f,
         1.0f, -1.0f, 0.0f,
        -1.0f,  1.0f, 0.0f,
         1.0f, -1.0f, 0.0f,
         1.0f,  1.0f, 0.0f,
        -1.0f,  1.0f, 0.0f
    };

    GLuint vao, vbo;
    glGenVertexArrays(1, &vao);
    glGenBuffers(1, &vbo);

    glBindVertexArray(vao);
    glBindBuffer(GL_ARRAY_BUFFER, vbo);
    glBufferData(GL_ARRAY_BUFFER, sizeof(vertices), vertices, GL_STATIC_DRAW);
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, NULL);
    glEnableVertexAttribArray(0);

    // 7. Bucle principal
    double start_time = glfwGetTime();
    while (!glfwWindowShouldClose(window)) {
        glClearColor(0.1f, 0.1f, 0.1f, 1.0f);
        glClear(GL_COLOR_BUFFER_BIT);

        glUseProgram(program);
        float time = glfwGetTime() - start_time;
        glUniform1f(glGetUniformLocation(program, "time"), time);
        glUniform2f(glGetUniformLocation(program, "resolution"), 800, 600);

        glDrawArrays(GL_TRIANGLES, 0, 6);

        glfwSwapBuffers(window);
        glfwPollEvents();
    }

    // 8. Limpiar recursos
    glDeleteProgram(program);
    glDeleteShader(vertex_shader);
    glDeleteShader(fragment_shader);
    glDeleteVertexArrays(1, &vao);
    glDeleteBuffers(1, &vbo);
    glfwTerminate();
    return 0;
}