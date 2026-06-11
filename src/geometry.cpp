#include <geometry.h>
#include <glm/glm.hpp>
#include <cmath>

namespace Geometry {
    Mesh createTriangle() {
        Mesh mesh;
        // Triangle shape (equilateral)
        mesh.vertices = {
            {{0.0f, 1.0f, 0.0f}, {1.0f, 0.0f, 0.0f}},      // Top (red)
            {{-0.866f, -0.5f, 0.0f}, {1.0f, 0.0f, 0.0f}},   // Bottom-left
            {{0.866f, -0.5f, 0.0f}, {1.0f, 0.0f, 0.0f}},    // Bottom-right
        };
        mesh.indices = {0, 1, 2};
        return mesh;
    }
    
    Mesh createCircle(float radius, int segments, glm::vec3 color) {
        Mesh mesh;
        
        // Center point
        mesh.vertices.push_back({{0.0f, 0.0f, 0.0f}, color});
        
        // Circle points
        for (int i = 0; i <= segments; i++) {
            float angle = 2.0f * 3.14159f * i / segments;
            float x = radius * cos(angle);
            float y = radius * sin(angle);
            mesh.vertices.push_back({{x, y, 0.0f}, color});
        }
        
        // Create line segments (hollow circle)
        for (int i = 0; i < segments; i++) {
            mesh.indices.push_back(i + 1);
            mesh.indices.push_back(i + 2);
        }
        
        return mesh;
    }
    
    Mesh createLine(glm::vec3 start, glm::vec3 end, glm::vec3 color, float thickness) {
        Mesh mesh;
        // Simple line as two triangles (quad)
        glm::vec3 dir = glm::normalize(end - start);
        glm::vec3 perp = glm::vec3(-dir.y, dir.x, 0.0f) * thickness;
        
        mesh.vertices = {
            {start + perp, color},
            {start - perp, color},
            {end + perp, color},
            {end - perp, color},
        };
        mesh.indices = {0, 1, 2, 1, 3, 2};
        
        return mesh;
    }
    
    Mesh createCrosshair(float size, glm::vec3 color) {
        Mesh mesh;
        // "+" crosshair - two perpendicular lines, small gap at center
        float gap = size * 0.3f;
        float len = size * 0.5f;
        float thick = 0.5f;
        
        // Horizontal line
        mesh.vertices.push_back({{-len - gap, 0.0f, 0.0f}, color});
        mesh.vertices.push_back({{-gap, 0.0f, 0.0f}, color});
        mesh.vertices.push_back({{gap, 0.0f, 0.0f}, color});
        mesh.vertices.push_back({{len + gap, 0.0f, 0.0f}, color});
        
        // Vertical line
        mesh.vertices.push_back({{0.0f, -len - gap, 0.0f}, color});
        mesh.vertices.push_back({{0.0f, -gap, 0.0f}, color});
        mesh.vertices.push_back({{0.0f, gap, 0.0f}, color});
        mesh.vertices.push_back({{0.0f, len + gap, 0.0f}, color});
        
        mesh.indices = {
            0, 1, 1, 2,
            2, 3, 4, 5,
            5, 6, 6, 7
        };
        
        return mesh;
    }
}
