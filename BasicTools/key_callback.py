from OpenGL.GL import *
from glfw.GLFW import *


def key_callback(window, key, scancode, action, mods):
    if key == GLFW_KEY_ESCAPE and action == GLFW_PRESS:
        glfwSetWindowShouldClose(window, GLFW_TRUE)
    if key == GLFW_KEY_SPACE and action == GLFW_PRESS:
        print("Space bar pressed")
    if key == GLFW_KEY_SPACE and action == GLFW_RELEASE:
        print("Space bar release")

# def cursor_callback(window, xpos, ypos):

def button_callback(window, button, action, mods):
    x, y = glfwGetCursorPos(window)
    if button == GLFW_MOUSE_BUTTON_LEFT and action == GLFW_PRESS:
        print("Left Btn; xpos :",x, "& ypos :",y)
    elif button == GLFW_MOUSE_BUTTON_RIGHT and action == GLFW_PRESS:
        print("Right Btn; xpos :", x, "& ypos :", y)

def main():
    if not glfwInit():
        return
    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3)  # OpenGL 3.3
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3)
    glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE)  # Do not allow legacy OpenGl API calls

    window = glfwCreateWindow(800, 800, 'callback', None, None)
    if not window:
        glfwTerminate()
        return
    glfwMakeContextCurrent(window)

    glfwSetKeyCallback(window, key_callback)
    glfwSetMouseButtonCallback(window, button_callback)

    while not glfwWindowShouldClose(window):
        glfwSwapBuffers(window)

        glfwPollEvents()

    glfwTerminate()


if __name__ == "__main__":
    main()