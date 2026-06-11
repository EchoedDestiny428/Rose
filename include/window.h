#ifndef WINDOW_H
#define WINDOW_H

#include <GLFW/glfw3.h>
#include <memory>

class Window {
public:
    Window(int width, int height, const char* title);
    ~Window();

    bool isOpen() const;
    void pollEvents();
    void swapBuffers();
    GLFWwindow* getHandle() const { return window; }
    
    int getWidth() const { return width; }
    int getHeight() const { return height; }
    void makeContextCurrent() const;

private:
    GLFWwindow* window;
    int width, height;
};

#endif // WINDOW_H
