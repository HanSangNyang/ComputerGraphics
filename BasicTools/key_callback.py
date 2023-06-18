from OpenGL.GL import *
from glfw.GLFW import *

def key_callback(window, key, scancode, action, mods):
    if key == GLFW_KEY_ESCAPE and action == GLFW_PRESS:
        glfwSetWindowShouldClose(window, GLFW_TRUE)
    if key == GLFW_KEY_SPACE and action == GLFW_PRESS:
        print("Space bar pressed")
    if key == GLFW_KEY_SPACE and action == GLFW_RELEASE:
        print("Space bar release")
        
def main():
    if not glfwInit():
        return
    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3)  # OpenGL 3.3
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3)
    glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE)  # Do not allow legacy OpenGl API calls
    
    window = glfwCreateWindow(800, 800, 'Key_callback', None, None)
    if not window:
        glfwTerminate()
        return
    glfwMakeContextCurrent(window)

    glfwSetKeyCallback(window, key_callback)

    while not glfwWindowShouldClose(window):
        glfwSwapBuffers(window)

        glfwPollEvents()
    
    glfwTerminate()

if __name__ == "__main__":
    main()