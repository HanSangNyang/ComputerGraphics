from OpenGL.GL import *
from glfw.GLFW import *
g_lbtn = 0

# Print a cursor position while mouse left button is being pressed

def key_callback(window, key, scancode, action, mods):
    if key == GLFW_KEY_ESCAPE and action == GLFW_PRESS:
        glfwSetWindowShouldClose(window, GLFW_TRUE)

def button_callback(window, button, action, mods):
    global g_lbtn
    if button == GLFW_MOUSE_BUTTON_LEFT:
        if action == GLFW_PRESS or action == GLFW_REPEAT:
            g_lbtn = 1
        elif action == GLFW_RELEASE:
            g_lbtn = 0

def cursor_callback(window, xpos, ypos):
    global g_lbtn
    x, y = glfwGetCursorPos(window)
    if g_lbtn == 1:
        print("xpos :", x, "ypos :", y)

def main():
    if not glfwInit():
        return
    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3)  # OpenGL 3.3
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3)
    glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE)  # Do not allow legacy OpenGl API calls

    window = glfwCreateWindow(800, 800, 'cursor_tracking', None, None)
    if not window:
        glfwTerminate()
        return
    glfwMakeContextCurrent(window)

    glfwSetKeyCallback(window, key_callback)
    glfwSetMouseButtonCallback(window, button_callback)
    glfwSetCursorPosCallback(window, cursor_callback)

    while not glfwWindowShouldClose(window):
        glfwSwapBuffers(window)

        glfwPollEvents()

    glfwTerminate()

if __name__ == "__main__":
    main()
