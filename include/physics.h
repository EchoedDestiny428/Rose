#ifndef PHYSICS_H
#define PHYSICS_H

#include <glm/glm.hpp>

struct Transform {
    glm::vec3 position;
    glm::vec3 rotation; // Euler angles (pitch, yaw, roll)
    glm::vec3 scale;
    
    Transform() : position(0), rotation(0), scale(1) {}
};

class Opponent {
public:
    Opponent();
    
    void update(float deltaTime);
    void reset();
    
    const Transform& getTransform() const { return transform; }
    glm::vec3 getVelocity() const { return velocity; }
    glm::vec3 getDirection() const { return direction; }
    float getSize() const { return size; }
    
private:
    Transform transform;
    glm::vec3 velocity;
    glm::vec3 acceleration;
    glm::vec3 direction;
    float size;
    
    float maxSpeed;
    float maxAcceleration;
    float changeDirectionChance;
};

#endif // PHYSICS_H
