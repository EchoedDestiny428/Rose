#include <physics.h>
#include <glm/glm.hpp>
#include <glm/gtc/random.hpp>
#include <cmath>
#include <cstdlib>

Opponent::Opponent() 
    : transform(), velocity(0), acceleration(0), direction(1, 0, 0), 
      size(1.0f), maxSpeed(5.0f), maxAcceleration(10.0f), changeDirectionChance(0.02f) {
    
    // Random starting position in front of camera
    transform.position = glm::vec3(
        glm::linearRand(-5.0f, 5.0f),
        glm::linearRand(-3.0f, 3.0f),
        glm::linearRand(5.0f, 15.0f)
    );
}

void Opponent::update(float deltaTime) {
    // Randomly change direction with small probability
    if (rand() / (float)RAND_MAX < changeDirectionChance) {
        direction = glm::normalize(glm::vec3(
            glm::linearRand(-1.0f, 1.0f),
            glm::linearRand(-0.5f, 0.5f),
            glm::linearRand(-1.0f, 1.0f)
        ));
    }
    
    // Apply acceleration in current direction
    acceleration = direction * maxAcceleration;
    
    // Update velocity
    velocity += acceleration * deltaTime;
    
    // Clamp velocity to max speed
    float speed = glm::length(velocity);
    if (speed > maxSpeed) {
        velocity = glm::normalize(velocity) * maxSpeed;
    }
    
    // Update position
    transform.position += velocity * deltaTime;
    
    // Keep opponent within view bounds (prevent flying off screen)
    if (glm::length(transform.position) > 30.0f) {
        transform.position = glm::normalize(transform.position) * 20.0f;
        velocity = glm::vec3(0);
    }
}

void Opponent::reset() {
    transform.position = glm::vec3(0, 0, 10);
    velocity = glm::vec3(0);
    acceleration = glm::vec3(0);
}
