from OpenGL.GL import *
from glfw.GLFW import *
import glm
import ctypes
import numpy as np

# draw a basic 3-color triangle on window

g_vertex_shader_src = '''
#version 330 core

layout (location = 0) in vec3 vin_pos;
layout (location = 1) in vec3 vin_color;

out vec4 vout_color;

uniform float time;
uniform mat4 M;

void main()
{
    gl_Position = M * vec4(vin_pos.x + time, vin_pos.yz , 1.0);
    vout_color = vec4(vin_color, 1.0);
}

'''

g_fragment_shader_src = '''
#version 330 core

in vec4 vout_color; 

out vec4 FragColor;

uniform float C;

void main()
{
    FragColor = vec4(vout_color.x + C, vout_color.y + C, vout_color.z + C, 1.0);
}
'''

def key_callback(window, key, scancode, action, mods):
    if key == GLFW_KEY_ESCAPE and action == GLFW_PRESS:
        glfwSetWindowShouldClose(window, GLFW_TRUE)

def prepare_vao_triangle():
    vertices = glm.array(glm.float32,
                         # position         # color
                         -0.5, -0.3, 0.0, 1.0, 0.0, 0.0,
                          0.5, -0.3, 0.0, 0.0, 1.0, 0.0,
                          0.0,  0.5, 0.0, 0.0, 0.0, 1.0)

    VAO = glGenVertexArrays(1)
    glBindVertexArray(VAO)

    VBO = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, VBO)

    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices.ptr, GL_STATIC_DRAW)

    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 6 * glm.sizeof(glm.float32), None)
    glEnableVertexAttribArray(0)

    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 6 * glm.sizeof(glm.float32), ctypes.c_void_p(3 * glm.sizeof(glm.float32)))
    glEnableVertexAttribArray(1)

    return VAO

def load_shaders(vertex_shader_source, fragment_shader_source):
    vertex_shader = glCreateShader(GL_VERTEX_SHADER)
    glShaderSource(vertex_shader, vertex_shader_source)
    glCompileShader(vertex_shader)

    success = glGetShaderiv(vertex_shader, GL_COMPILE_STATUS)
    if not success:
        infoLog = glGetShaderInfoLog(vertex_shader)
        print("ERROR::SHADER::VERTEX::COMPILATION_FAILED\n" + infoLog.decode())

    fragment_shader = glCreateShader(GL_FRAGMENT_SHADER)
    glShaderSource(fragment_shader, fragment_shader_source)
    glCompileShader(fragment_shader)

    success = glGetShaderiv(fragment_shader, GL_COMPILE_STATUS)
    if not success:
        infoLog = glGetShaderInfoLog(fragment_shader)
        print("ERROR::SHADER::FRAGMENT::COMPILATION_FAILED\n" + infoLog.decode())

    shader_program = glCreateProgram()
    glAttachShader(shader_program, vertex_shader)
    glAttachShader(shader_program, fragment_shader)
    glLinkProgram(shader_program)

    success = glGetProgramiv(shader_program, GL_LINK_STATUS)
    if not success:
        infoLog = glGetProgramInfoLog(shader_program)
        print("ERROR::PROGRAM::LINKING_FAILED\n" + infoLog.decode())

    glDeleteShader(vertex_shader)
    glDeleteShader(fragment_shader)

    return shader_program

def main():
    if not glfwInit():
        return
    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3)  # OpenGL 3.3 (means →3 . 3)
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3)  # OpenGL 3.3 (means 3 . →3)
    glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE)  # Do not allow legacy OpenGl API calls

    window = glfwCreateWindow(800, 800, '3-color triangle', None, None)
    if not window:
        glfwTerminate()
        return

    glfwMakeContextCurrent(window)

    glfwSetKeyCallback(window, key_callback)

    shader_program = load_shaders(g_vertex_shader_src, g_fragment_shader_src)
    time_loc = glGetUniformLocation(shader_program, 'time')
    M_loc = glGetUniformLocation(shader_program, 'M')
    C_loc = glGetUniformLocation(shader_program, 'C')

    vao_triangle = prepare_vao_triangle()


    while not glfwWindowShouldClose(window):
        glClear(GL_COLOR_BUFFER_BIT)

        glUseProgram(shader_program)

        t = glfwGetTime()
        glUniform1f(time_loc, np.sin(t) * 0.5) # move left and right
        glUniform1f(C_loc, (np.sin(t) - 1) / 2) # change color

        # M = glm.mat4()
        M = glm.rotate(t,glm.vec3(0,0,1)) # rotate
        glUniformMatrix4fv(M_loc, 1, GL_TRUE, glm.value_ptr(M))

        glBindVertexArray(vao_triangle)
        glDrawArrays(GL_TRIANGLES, 0, 3)

        glfwSwapBuffers(window)

        glfwPollEvents()

    glfwTerminate()

if __name__ == "__main__":
    main()