#ifndef GEOMETRY_H
#define GEOMETRY_H

#include <glm/glm.hpp>
#include <vector>

struct Vertex {
    glm::vec3 pos;
    glm::vec3 color;
};

namespace Geometry {
    struct Mesh {
        std::vector<Vertex> vertices;
        std::vector<uint32_t> indices;
    };
    
    Mesh createTriangle();
    Mesh createCircle(float radius, int segments, glm::vec3 color);
    Mesh createLine(glm::vec3 start, glm::vec3 end, glm::vec3 color, float thickness = 1.0f);
    Mesh createCrosshair(float size, glm::vec3 color);
}

#endif // GEOMETRY_H
