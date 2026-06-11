#ifndef GAME_H
#define GAME_H

#include <memory>
#include <glm/glm.hpp>

class Window;
class Renderer;
class Input;
class Opponent;

class Game {
public:
    Game();
    ~Game();
    
    void run();
    
private:
    std::unique_ptr<Window> window;
    std::unique_ptr<Renderer> renderer;
    std::unique_ptr<Input> input;
    std::unique_ptr<Opponent> opponent;
    
    glm::vec3 cameraPos; // First-person camera position
    glm::vec3 cameraRot; // Pitch, yaw, roll
    
    float deltaTime;
    bool running;
    
    void update(float dt);
    void render();
    void handleInput();
    void checkHit();
};

#endif // GAME_H
