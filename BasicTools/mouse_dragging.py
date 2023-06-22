import glfw
from OpenGL.GL import *
from glfw.GLFW import *
import glm
import ctypes
import numpy as np

# draw grid
# you can,
# 1. move orbit of view-point by dragging mouse left-button
# 2. zoom in/out by scrolling the mouse_wheel
# 3. toggle the view by pressing 'T'

g_cam_ang_azi = np.radians(70)
g_cam_ang_ele = np.radians(20)
g_zoom = 1.0
g_toggle = 1
g_v_pre_pos = glm.vec2(0., 0.)
g_sensitivity = 0.01

g_vertex_shader_src = '''
#version 330 core

layout (location = 0) in vec3 vin_pos;
layout (location = 1) in vec3 vin_color;

out vec4 vout_color;

uniform mat4 MVP;

void main()
{
    gl_Position = MVP * vec4(vin_pos, 1.0);
    vout_color = vec4(vin_color, 1.0);
}

'''

g_fragment_shader_src = '''
#version 330 core

in vec4 vout_color; 

out vec4 FragColor;

void main()
{
    FragColor = vout_color;
}
'''

def key_callback(window, key, scancode, action, mods):
    global g_toggle

    if key == GLFW_KEY_ESCAPE and action == GLFW_PRESS:
        glfwSetWindowShouldClose(window, GLFW_TRUE)
    if key == GLFW_KEY_T and action == GLFW_PRESS:
        g_toggle = 1 - g_toggle

def scroll_callback(window, xoffset, yoffset):
    global g_zoom
    if yoffset > 0 and g_zoom < 5:
        g_zoom += 0.05
    elif yoffset < 0 and g_zoom > 0.1:
        g_zoom -= 0.05

def mouse_left_drag(window):
    global g_cam_ang_azi, g_cam_ang_ele, g_v_pre_pos, g_sensitivity

    x_pos, y_pos = glfw.get_cursor_pos(window)
    if glfw.get_mouse_button(window, glfw.MOUSE_BUTTON_LEFT) != glfw.PRESS:
        g_v_pre_pos.x, g_v_pre_pos.y = glfw.get_cursor_pos(window)
    if glfw.get_mouse_button(window, glfw.MOUSE_BUTTON_LEFT) == glfw.PRESS:
        if np.cos(g_cam_ang_ele) >= 0:
            g_cam_ang_azi += np.radians((x_pos - g_v_pre_pos.x) * g_sensitivity)
        else:
            g_cam_ang_azi += np.radians(-(x_pos - g_v_pre_pos.x) * g_sensitivity)
        g_cam_ang_ele += np.radians((y_pos - g_v_pre_pos.y) * g_sensitivity)

def prepare_vao_grid_x():
    vertices = glm.array(glm.float32,
                         # position         # color
                         -100.0, 0.0, 0.0, 1.0, 1.0, 1.0,
                          100.0, 0.0, 0.0, 1.0, 1.0, 1.0)

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

def prepare_vao_grid_z():
    vertices = glm.array(glm.float32,
                         # position         # color
                         0.0, 0.0, -100.0, 1.0, 1.0, 1.0,
                         0.0, 0.0,  100.0, 1.0, 1.0, 1.0)

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

    window = glfwCreateWindow(800, 800, 'grid', None, None)
    if not window:
        glfwTerminate()
        return

    glfwMakeContextCurrent(window)

    glfwSetKeyCallback(window, key_callback)
    glfwSetScrollCallback(window, scroll_callback)

    shader_program = load_shaders(g_vertex_shader_src, g_fragment_shader_src)
    MVP_loc = glGetUniformLocation(shader_program, 'MVP')

    vao_gird_x = prepare_vao_grid_x()
    vao_grid_z = prepare_vao_grid_z()

    while not glfwWindowShouldClose(window):
        glClear(GL_COLOR_BUFFER_BIT)

        glUseProgram(shader_program)

        if g_toggle:
            P = glm.perspective(45, 1, 0.1, 100.0)
            S = 7
        else:
            P = glm.ortho(-10, 10, -10, 10, -10, 10)
            S = 1

        mouse_left_drag(window)

        V = glm.lookAt(glm.vec3(
            S * np.cos(g_cam_ang_azi) * np.cos(g_cam_ang_ele) * g_zoom,
            S * np.sin(g_cam_ang_ele) * g_zoom,
            S * np.sin(g_cam_ang_azi) * np.cos(g_cam_ang_ele) * g_zoom),
            glm.vec3(0, 0, 0), glm.vec3(0, 1, 0))

        M = glm.mat4()
        glBindVertexArray(vao_gird_x)
        for i in range(-100,100):
            M = glm.translate((0, 0, i))
            MVP = P * V * M
            glUniformMatrix4fv(MVP_loc, 1, GL_FALSE, glm.value_ptr(MVP))
            glDrawArrays(GL_LINES, 0, 2)

        M = glm.mat4()
        glBindVertexArray(vao_grid_z)
        for i in range(-100,100):
            M = glm.translate((i, 0, 0))
            MVP = P * V * M
            glUniformMatrix4fv(MVP_loc, 1, GL_FALSE, glm.value_ptr(MVP))
            glDrawArrays(GL_LINES, 0, 2)

        glfwSwapBuffers(window)

        glfwPollEvents()

    glfwTerminate()

if __name__ == "__main__":
    main()