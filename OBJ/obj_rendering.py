import re
from OpenGL.GL import *
from glfw.GLFW import *
import glm
import ctypes
import numpy as np

# draw obj model by drag-drop the obj file on window

g_cam_ang_x = 0.
g_cam_ang_y = 0.
g_cam_ang_z = 0.
g_toggle_ortho = 1
g_toggle_poly = 1

v_array = []
vn_array = []
fv_array = []
fn_array = []
f_count = 0

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

g_vertex_shader_normal_src = '''
#version 330 core

layout (location = 0) in vec3 vin_pos; 
layout (location = 1) in vec3 vin_normal;

out vec4 vout_color;
out vec3 vout_surface_pos;
out vec3 vout_normal;

uniform mat4 MVP;
uniform mat4 M;
uniform vec3 color;

void main()
{
    // 3D points in homogeneous coordinates
    vec4 p3D_in_hcoord = vec4(vin_pos.xyz, 1.0);

    gl_Position = MVP * p3D_in_hcoord;

    vout_color = vec4(color, 1.);
    // vout_color = vec4(1,1,1,1);
    vout_surface_pos = vec3(vec4(vin_pos, 1));
    vout_normal = normalize( mat3(inverse(transpose(M)) ) * vin_normal);
}
'''

g_fragment_shader_normal_src = '''
#version 330 core

in vec4 vout_color;
in vec3 vout_surface_pos;
in vec3 vout_normal;

out vec4 FragColor;

uniform vec3 view_pos;

void main()
{
    // light and material properties
    vec3 light_pos = vec3(3,2,4);
    vec3 light_pos2 = vec3(-3,-2,-4);
    vec3 light_color = vec3(1,1,1);
    vec3 light_color2 = vec3(1,1,1);
    vec3 material_color = vec3(vout_color.x,vout_color.y,vout_color.z);
    float material_shininess = 32.0;

    // light components
    vec3 light_ambient = 0.1*light_color;
    vec3 light_diffuse = light_color;
    vec3 light_specular = light_color;
    vec3 light_ambient2 = 0.1*light_color2;
    vec3 light_diffuse2 = light_color2;
    vec3 light_specular2 = light_color2;

    // material components
    vec3 material_ambient = material_color;
    vec3 material_diffuse = material_color;
    vec3 material_specular = light_color;  // for non-metal material

    // ambient
    vec3 ambient = (light_ambient+light_ambient2) * material_ambient;

    // for diffiuse and specular
    vec3 normal = normalize(vout_normal);
    vec3 surface_pos = vout_surface_pos;
    vec3 light_dir = normalize(light_pos - surface_pos);
    vec3 light_dir2 = normalize(light_pos2 - surface_pos);

    // diffuse
    float diff = max(dot(normal, light_dir), 0);
    float diff2 = max(dot(normal, light_dir2), 0);
    vec3 diffuse1 = diff * light_diffuse * material_diffuse;
    vec3 diffuse2 = diff2 * light_diffuse * material_diffuse;
    vec3 diffuse = diffuse1 + diffuse2;

    // specular
    vec3 view_dir = normalize(view_pos - surface_pos);
    vec3 reflect_dir = reflect(-light_dir, normal);
    vec3 reflect_dir2 = reflect(-light_dir2, normal);
    float spec = pow( max(dot(view_dir, reflect_dir), 0.0), material_shininess);
    float spec2 = pow( max(dot(view_dir, reflect_dir2), 0.0), material_shininess);

    vec3 specular1 = spec * light_specular * material_specular;
    vec3 specular2 = spec2 * light_specular * material_specular;
    vec3 specular = specular1 + specular2;

    vec3 color = ambient + diffuse + specular;
    FragColor = vec4(color, 1.);

}
'''

def key_callback(window, key, scancode, action, mods):
    global g_cam_ang_x, g_cam_ang_y, g_cam_ang_z, g_toggle_ortho, g_toggle_poly

    if key == GLFW_KEY_ESCAPE and action == GLFW_PRESS:
        glfwSetWindowShouldClose(window, GLFW_TRUE)
    if key == GLFW_KEY_1:
        if action == GLFW_PRESS or action == GLFW_REPEAT:
            g_cam_ang_x += 1
    if key == GLFW_KEY_3:
        if action == GLFW_PRESS or action == GLFW_REPEAT:
            g_cam_ang_x += -1
    if key == GLFW_KEY_Q:
        if action == GLFW_PRESS or action == GLFW_REPEAT:
            g_cam_ang_z += 1
    if key == GLFW_KEY_E:
        if action == GLFW_PRESS or action == GLFW_REPEAT:
            g_cam_ang_z += -1
    if key == GLFW_KEY_2:
        if action == GLFW_PRESS or action == GLFW_REPEAT:
            g_cam_ang_y += 1
    if key == GLFW_KEY_W:
        if action == GLFW_PRESS or action == GLFW_REPEAT:
            g_cam_ang_y += -1
    if key == GLFW_KEY_T and action == GLFW_PRESS:
        g_toggle_ortho = 1 - g_toggle_ortho
    if key == GLFW_KEY_Z and action == GLFW_PRESS:
        g_toggle_poly = 1 - g_toggle_poly

def drop_callback(window, paths):
    global v_array, vn_array, fv_array, fn_array, f_count

    obj = paths[0].split('\\')
    obj_name = obj[-1]
    f = open(paths[0], 'r', encoding='UTF-8')

    v_count = vn_count = f_count = f3_count = f4_count = f5_count = 0
    v_array = []
    vn_array = []
    f_array = []
    fv_array = []
    fn_array = []

    while True:
        line = f.readline()

        if not line: break

        if line[0] == 'v' and line[1] == ' ':
            v_count += 1
            v_array.extend(line[2:].split())
        elif line[0] == 'v' and line[1] == 'n':
            vn_count += 1
            vn_array.extend(line[2:].split())
        elif line[0] == 'f' and line[1] == ' ':
            temp = line[2:].split()
            f_count += len(temp) - 2
            for i in range(1, len(temp) - 1):
                f_array.extend([temp[0], temp[i], temp[i+1]])
            if len(temp) == 3:
                f3_count += 1
            elif len(temp) == 4:
                f4_count += 1
            elif len(temp) == 5:
                f5_count += 1

    for item in f_array:
        fv_array.extend(re.split(r'/.*', item))
        fn_array.extend(re.split(r'.*/', item))

    for item in fv_array:
        if item == '':
            fv_array.remove('')

    for item in fn_array:
        if item == '':
            fn_array.remove('')

    print("==========================================================")
    print("Obj file name : ", obj_name)
    print("Total number of faces : ", f3_count+f4_count+f5_count)
    print("Result number of Triangle faces : ", f_count)
    print("Number of faces with 3 vertices : ", f3_count)
    print("Number of faces with 4 vertices : ", f4_count)
    print("Number of faces with more than 4 vertices  : ", f5_count)
    print("==========================================================")

    v_array = list(map(float, v_array))
    vn_array = list(map(float, vn_array))
    fv_array = list(map(int, fv_array))
    fn_array = list(map(int, fn_array))

    f.close()

def prepare_vao_obj():
    global v_array, vn_array, fv_array, fn_array

    varr = []
    for i in range(0, len(fv_array)):
        varr.append(v_array[3 * (fv_array[i] - 1)])
        varr.append(v_array[3 * (fv_array[i] - 1) + 1])
        varr.append(v_array[3 * (fv_array[i] - 1) + 2])
        varr.append(vn_array[3 * (fn_array[i] - 1)])
        varr.append(vn_array[3 * (fn_array[i] - 1) + 1])
        varr.append(vn_array[3 * (fn_array[i] - 1) + 2])

    vertices = glm.array(glm.float32, *varr)

    VAO = glGenVertexArrays(1)  # create a vertex array object ID and store it to VAO variable
    glBindVertexArray(VAO)  # activate VAO

    # create and activate VBO (vertex buffer object)
    VBO = glGenBuffers(1)  # create a buffer object ID and store it to VBO variable
    glBindBuffer(GL_ARRAY_BUFFER, VBO)  # activate VBO as a vertex buffer object

    # copy vertex data to VBO
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices.ptr,
                 GL_STATIC_DRAW)  # allocate GPU memory for and copy vertex data to the currently bound vertex buffer

    # configure vertex positions
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 6 * glm.sizeof(glm.float32), None)
    glEnableVertexAttribArray(0)

    # configure vertex normals
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 6 * glm.sizeof(glm.float32),
                          ctypes.c_void_p(3 * glm.sizeof(glm.float32)))
    glEnableVertexAttribArray(1)

    return VAO

def draw_rendering(shader_program, vao, M, MVP):
    global f_count

    glBindVertexArray(vao)

    MVP_loc = glGetUniformLocation(shader_program, 'MVP')
    M_loc = glGetUniformLocation(shader_program, 'M')
    color_loc = glGetUniformLocation(shader_program, 'color')

    glUniformMatrix4fv(MVP_loc, 1, GL_FALSE, glm.value_ptr(MVP))
    glUniformMatrix4fv(M_loc, 1, GL_FALSE, glm.value_ptr(M))
    glUniform3f(color_loc, 1, 1, 1)

    glDrawArrays(GL_TRIANGLES, 0, f_count * 3)

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

def draw_grid(shader_program, vao, MVP):
    MVP_loc = glGetUniformLocation(shader_program, 'MVP')
    glUniformMatrix4fv(MVP_loc, 1, GL_FALSE, glm.value_ptr(MVP))

    glDrawArrays(GL_LINES, 0, 2)

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
    glfwSetDropCallback(window, drop_callback)

    shader_program = load_shaders(g_vertex_shader_src, g_fragment_shader_src)
    MVP_loc = glGetUniformLocation(shader_program, 'MVP')

    shader_program_nor = load_shaders(g_vertex_shader_normal_src, g_fragment_shader_normal_src)

    vao_grid_x = prepare_vao_grid_x()
    vao_grid_z = prepare_vao_grid_z()

    while not glfwWindowShouldClose(window):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glEnable(GL_DEPTH_TEST)


        glUseProgram(shader_program)

        if g_toggle_ortho:
            P = glm.perspective(45, 1, 0.1, 100.0)
        else:
            P = glm.ortho(-10, 10, -10, 10, -10, 10)

        if g_toggle_poly:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

        V = glm.lookAt(glm.vec3(10+g_cam_ang_x,5+g_cam_ang_y,10+g_cam_ang_z),
                       glm.vec3(0,0,0),glm.vec3(0,1,0))

        M = glm.mat4()
        glBindVertexArray(vao_grid_x)
        for i in range(-100,100):
            M = glm.translate((0, 0, i))
            draw_grid(shader_program, vao_grid_x, P*V*M)

        glBindVertexArray(vao_grid_z)
        for i in range(-100,100):
            M = glm.translate((i, 0, 0))
            draw_grid(shader_program, vao_grid_z, P*V*M)

        glUseProgram(shader_program_nor)

        vao_obj = prepare_vao_obj()
        draw_rendering(shader_program_nor, vao_obj, glm.mat4(), P*V)

        glfwSwapBuffers(window)

        glfwPollEvents()

    glfwTerminate()

if __name__ == "__main__":
    main()