from OpenGL.GL import *
from glfw.GLFW import *
from glfw import _GLFWwindow as GLFWwindow
from pygame import mixer
from breakout.game import Game
from breakout.resource_manager import ResourceManager

import platform

SCREEN_WIDTH: int = 800
SCREEN_HEIGHT: int = 600

Breakout = Game(SCREEN_WIDTH, SCREEN_HEIGHT)

def key_callback(window: GLFWwindow, key: int, scancode: int, action: int, mode: int) -> None:
    # when a user presses the escape key, we set the
    # WindowShouldClose property to true, closing
    # the application
    if key == GLFW_KEY_ESCAPE and action == GLFW_PRESS:
        glfwSetWindowShouldClose(window, True)

    if key >= 0 and key < 1024:
        if action == GLFW_PRESS:
            Breakout.keys[key] = True
        elif action == GLFW_RELEASE:
            Breakout.keys[key] = False

def framebuffer_size_callback(window: GLFWwindow, width: int, height: int) -> None:
    # make sure the viewport matches the new window
    # dimensions; note that width and height will be
    # significantly larger than specified on retina
    # displays.
    glViewport(0, 0, width, height)

def main() -> None:
    glfwInit()
    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3)
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3)
    glfwWindowHint(GLFW_OPENGL_FORWARD_COMPAT, GL_TRUE)

    if platform.system() == "Darwin":  # Apple
        glfwWindowHint(GLFW_OPENGL_FORWARD_COMPAT, GL_TRUE)

    glfwWindowHint(GLFW_RESIZABLE, False)

    # glfw window creation
    window = glfwCreateWindow(SCREEN_WIDTH, SCREEN_HEIGHT, "Breakout", None, None)
    if window == None:
        print("Failed to create GLFW window")
        glfwTerminate()
        return -1
    
    glfwMakeContextCurrent(window)
    glfwSetKeyCallback(window, key_callback)
    glfwSetFramebufferSizeCallback(window, framebuffer_size_callback)

    # OpenGL configuration
    glViewport(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    # initialize audio mixer
    mixer.init()

    # initialize game
    Breakout.init()

    # deltatime variables
    delta_time = 0.0
    last_frame = 0.0

    while not glfwWindowShouldClose(window):
        # calculate delta time
        current_frame = glfwGetTime()
        delta_time = current_frame - last_frame
        last_frame = current_frame
        glfwPollEvents()

        # manage user input
        Breakout.process_input(delta_time)

        # update game state
        Breakout.update(delta_time)

        # render
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)
        Breakout.render()

        glfwSwapBuffers(window)

    ResourceManager.clear()

    glfwTerminate()

if __name__ == "__main__":
    main()
