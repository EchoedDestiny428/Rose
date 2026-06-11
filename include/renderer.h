#ifndef RENDERER_H
#define RENDERER_H

#include <glad/glad.h>
#include <GLFW/glfw3.h>
#include <glm/glm.hpp>
#include <glm/gtc/matrix_transform.hpp>
#include <glm/gtc/type_ptr.hpp>
#include <vector>
#include <memory>

class Window;
struct Transform;

struct RenderMesh {
    GLuint VAO;
    GLuint VBO;
    GLuint EBO;
    GLuint indexCount;
};

class Renderer {
public:
    Renderer(Window& window);
    ~Renderer();

    void beginFrame();
    void endFrame();
    void renderTriangle(const Transform& transform, float size);
    void renderPip(const glm::vec3& pipPos, const glm::vec3& opponentDirection, float opponentSize, bool isHit);
    void renderCrosshair();
    void setCameraMatrix(const glm::mat4& view, const glm::mat4& proj);
    
private:
    Window& window;
    GLuint shaderProgram;
    
    // Meshes
    RenderMesh triangleMesh;
    RenderMesh pipCircleMesh;
    RenderMesh pipGuidlineMesh;
    RenderMesh crosshairMesh;
    
    // Matrices
    glm::mat4 viewMatrix;
    glm::mat4 projMatrix;
    
    void initGL();
    GLuint createShaderProgram();
    RenderMesh createMesh(const std::vector<float>& vertices, const std::vector<unsigned int>& indices);
    void destroyMesh(RenderMesh& mesh);
    void renderMesh(const RenderMesh& mesh, const glm::mat4& model, const glm::vec3& color);
};

#endif // RENDERER_H
