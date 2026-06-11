#include <renderer.h>
#include <window.h>
#include <geometry.h>
#include <iostream>
#include <stdexcept>
#include <glm/glm.hpp>
#include <glm/gtc/matrix_transform.hpp>
#include <glm/gtc/type_ptr.hpp>

const char* vertexShaderSource = R"glsl(
#version 450 core
layout (location = 0) in vec3 aPos;
layout (location = 1) in vec3 aColor;

out vec3 vertexColor;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

void main()
{
    gl_Position = projection * view * model * vec4(aPos, 1.0);
    vertexColor = aColor;
}
)glsl";

const char* fragmentShaderSource = R"glsl(
#version 450 core
in vec3 vertexColor;
out vec4 FragColor;

void main()
{
    FragColor = vec4(vertexColor, 1.0);
}
)glsl";

Renderer::Renderer(Window& window) : window(window) {
    initGL();
    shaderProgram = createShaderProgram();
    
    auto triangle = Geometry::createTriangle();
    std::vector<float> triVerts(reinterpret_cast<float*>(triangle.vertices.data()),
                                 reinterpret_cast<float*>(triangle.vertices.data()) + triangle.vertices.size() * 6);
    std::vector<unsigned int> triInds(triangle.indices.begin(), triangle.indices.end());
    triangleMesh = createMesh(triVerts, triInds);
    
    auto circle = Geometry::createCircle(1.0f, 32, glm::vec3(1.0f, 0.0f, 0.0f));
    std::vector<float> circleVerts(reinterpret_cast<float*>(circle.vertices.data()),
                                    reinterpret_cast<float*>(circle.vertices.data()) + circle.vertices.size() * 6);
    std::vector<unsigned int> circleInds(circle.indices.begin(), circle.indices.end());
    pipCircleMesh = createMesh(circleVerts, circleInds);
    
    auto crosshair = Geometry::createCrosshair(0.1f, glm::vec3(1.0f, 1.0f, 1.0f));
    std::vector<float> crossVerts(reinterpret_cast<float*>(crosshair.vertices.data()),
                                   reinterpret_cast<float*>(crosshair.vertices.data()) + crosshair.vertices.size() * 6);
    std::vector<unsigned int> crossInds(crosshair.indices.begin(), crosshair.indices.end());
    crosshairMesh = createMesh(crossVerts, crossInds);
    
    projMatrix = glm::perspective(glm::radians(45.0f), 1920.0f / 1080.0f, 0.1f, 100.0f);
}

Renderer::~Renderer() {
    destroyMesh(triangleMesh);
    destroyMesh(pipCircleMesh);
    destroyMesh(crosshairMesh);
    destroyMesh(pipGuidlineMesh);
    
    if (shaderProgram) {
        glDeleteProgram(shaderProgram);
    }
}

void Renderer::initGL() {
    glClearColor(0.0f, 0.0f, 0.0f, 1.0f);
    glEnable(GL_DEPTH_TEST);
    glEnable(GL_LINE_SMOOTH);
    glEnable(GL_BLEND);
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
    glHint(GL_LINE_SMOOTH_HINT, GL_NICEST);
}

GLuint Renderer::createShaderProgram() {
    GLuint vertexShader = glCreateShader(GL_VERTEX_SHADER);
    glShaderSource(vertexShader, 1, &vertexShaderSource, nullptr);
    glCompileShader(vertexShader);
    
    int success;
    char infoLog[512];
    glGetShaderiv(vertexShader, GL_COMPILE_STATUS, &success);
    if (!success) {
        glGetShaderInfoLog(vertexShader, 512, nullptr, infoLog);
        throw std::runtime_error(std::string("Vertex shader compilation failed: ") + infoLog);
    }
    
    GLuint fragmentShader = glCreateShader(GL_FRAGMENT_SHADER);
    glShaderSource(fragmentShader, 1, &fragmentShaderSource, nullptr);
    glCompileShader(fragmentShader);
    
    glGetShaderiv(fragmentShader, GL_COMPILE_STATUS, &success);
    if (!success) {
        glGetShaderInfoLog(fragmentShader, 512, nullptr, infoLog);
        throw std::runtime_error(std::string("Fragment shader compilation failed: ") + infoLog);
    }
    
    GLuint program = glCreateProgram();
    glAttachShader(program, vertexShader);
    glAttachShader(program, fragmentShader);
    glLinkProgram(program);
    
    glGetProgramiv(program, GL_LINK_STATUS, &success);
    if (!success) {
        glGetProgramInfoLog(program, 512, nullptr, infoLog);
        throw std::runtime_error(std::string("Shader program linking failed: ") + infoLog);
    }
    
    glDeleteShader(vertexShader);
    glDeleteShader(fragmentShader);
    
    return program;
}

RenderMesh Renderer::createMesh(const std::vector<float>& vertices, const std::vector<unsigned int>& indices) {
    RenderMesh mesh{};
    mesh.indexCount = indices.size();
    
    glGenVertexArrays(1, &mesh.VAO);
    glGenBuffers(1, &mesh.VBO);
    glGenBuffers(1, &mesh.EBO);
    
    glBindVertexArray(mesh.VAO);
    
    glBindBuffer(GL_ARRAY_BUFFER, mesh.VBO);
    glBufferData(GL_ARRAY_BUFFER, vertices.size() * sizeof(float), vertices.data(), GL_STATIC_DRAW);
    
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, mesh.EBO);
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.size() * sizeof(unsigned int), indices.data(), GL_STATIC_DRAW);
    
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 6 * sizeof(float), (void*)0);
    glEnableVertexAttribArray(0);
    
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 6 * sizeof(float), (void*)(3 * sizeof(float)));
    glEnableVertexAttribArray(1);
    
    glBindBuffer(GL_ARRAY_BUFFER, 0);
    glBindVertexArray(0);
    
    return mesh;
}

void Renderer::destroyMesh(RenderMesh& mesh) {
    if (mesh.VAO) {
        glDeleteVertexArrays(1, &mesh.VAO);
        glDeleteBuffers(1, &mesh.VBO);
        glDeleteBuffers(1, &mesh.EBO);
        mesh.VAO = 0;
    }
}

void Renderer::renderMesh(const RenderMesh& mesh, const glm::mat4& model, const glm::vec3& color) {
    glUseProgram(shaderProgram);
    
    GLint modelLoc = glGetUniformLocation(shaderProgram, "model");
    GLint viewLoc = glGetUniformLocation(shaderProgram, "view");
    GLint projLoc = glGetUniformLocation(shaderProgram, "projection");
    
    glUniformMatrix4fv(modelLoc, 1, GL_FALSE, glm::value_ptr(model));
    glUniformMatrix4fv(viewLoc, 1, GL_FALSE, glm::value_ptr(viewMatrix));
    glUniformMatrix4fv(projLoc, 1, GL_FALSE, glm::value_ptr(projMatrix));
    
    glBindVertexArray(mesh.VAO);
    glDrawElements(GL_TRIANGLES, mesh.indexCount, GL_UNSIGNED_INT, 0);
    glBindVertexArray(0);
}

void Renderer::beginFrame() {
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
}

void Renderer::endFrame() {
    window.swapBuffers();
}

void Renderer::renderTriangle(const Transform& transform, float size) {
    glm::mat4 model = glm::mat4(1.0f);
    model = glm::translate(model, transform.position);
    model = glm::scale(model, glm::vec3(size));
    renderMesh(triangleMesh, model, glm::vec3(1.0f, 0.0f, 0.0f));
}

void Renderer::renderPip(const glm::vec3& pipPos, const glm::vec3& opponentDirection, float opponentSize, bool isHit) {
    glm::mat4 pipModel = glm::mat4(1.0f);
    pipModel = glm::translate(pipModel, pipPos);
    pipModel = glm::scale(pipModel, glm::vec3(0.5f));
    
    glm::vec3 pipColor = isHit ? glm::vec3(0.0f, 1.0f, 0.0f) : glm::vec3(1.0f, 0.0f, 0.0f);
    renderMesh(pipCircleMesh, pipModel, pipColor);
    
    if (glm::length(opponentDirection) > 0.001f) {
        glm::vec3 normalizedDir = glm::normalize(opponentDirection);
        glm::vec3 perpendicular = glm::vec3(-normalizedDir.y, normalizedDir.x, 0.0f);
    }
}

void Renderer::renderCrosshair() {
    glm::mat4 model = glm::mat4(1.0f);
    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE);
    renderMesh(crosshairMesh, model, glm::vec3(1.0f, 1.0f, 1.0f));
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL);
}

void Renderer::setCameraMatrix(const glm::mat4& view, const glm::mat4& proj) {
    viewMatrix = view;
    projMatrix = proj;
}
