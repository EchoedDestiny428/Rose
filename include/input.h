#ifndef INPUT_H
#define INPUT_H

#include <glm/glm.hpp>
#include <GLFW/glfw3.h>

class Input {
public:
    Input(GLFWwindow* window);
    
    void update();
    
    glm::vec2 getMouseDelta() const { return mouseDelta; }
    glm::vec2 getMousePos() const { return mousePos; }
    bool isKeyPressed(int key) const;
    
    // vJoy-style: velocity from mouse movement
    glm::vec2 getVelocity() const { return velocity; }

private:
    GLFWwindow* window;
    glm::vec2 mousePos;
    glm::vec2 lastMousePos;
    glm::vec2 mouseDelta;
    glm::vec2 velocity;
    
    static void mouseCallback(GLFWwindow* window, double x, double y);
};

#endif // INPUT_H
