#include <input.h>
#include <GLFW/glfw3.h>
#include <glm/glm.hpp>

Input::Input(GLFWwindow* window) 
    : window(window), mousePos(0), lastMousePos(0), mouseDelta(0), velocity(0) {
    glfwSetInputMode(window, GLFW_CURSOR, GLFW_CURSOR_DISABLED);
    glfwSetCursorPosCallback(window, mouseCallback);
    glfwSetWindowUserPointer(window, this);
}

void Input::update() {
    lastMousePos = mousePos;
    
    // Mouse position is updated via callback
    mouseDelta = mousePos - lastMousePos;
    
    // Accumulate velocity from mouse delta (vJoy-style)
    velocity = mouseDelta;
}

bool Input::isKeyPressed(int key) const {
    return glfwGetKey(window, key) == GLFW_PRESS;
}

void Input::mouseCallback(GLFWwindow* window, double x, double y) {
    Input* input = static_cast<Input*>(glfwGetWindowUserPointer(window));
    if (input) {
        input->mousePos = glm::vec2(x, y);
    }
}
