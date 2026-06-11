#include <game.h>
#include <window.h>
#include <renderer.h>
#include <input.h>
#include <physics.h>
#include <iostream>
#include <chrono>
#include <glm/glm.hpp>

Game::Game() : cameraPos(0, 0, 5), cameraRot(0, 0, 0), deltaTime(0), running(true) {
    window = std::make_unique<Window>(1920, 1080, "VJoy Aim Trainer");
    renderer = std::make_unique<Renderer>(*window);
    input = std::make_unique<Input>(window->getHandle());
    opponent = std::make_unique<Opponent>();
}

Game::~Game() {}

void Game::run() {
    auto lastTime = std::chrono::high_resolution_clock::now();
    
    while (window->isOpen() && running) {
        auto currentTime = std::chrono::high_resolution_clock::now();
        deltaTime = std::chrono::duration<float>(currentTime - lastTime).count();
        lastTime = currentTime;
        
        // Clamp deltaTime to reasonable values
        if (deltaTime > 0.016f) deltaTime = 0.016f; // 60 FPS min
        
        handleInput();
        update(deltaTime);
        render();
        
        window->pollEvents();
    }
}

void Game::handleInput() {
    input->update();
    
    // vJoy-style: mouse movement accumulates as velocity
    glm::vec2 mouseVelocity = input->getMouseDelta() * 0.1f; // Sensitivity
    
    // Apply to camera rotation
    cameraRot.y += mouseVelocity.x; // Yaw from mouse X
    cameraRot.x += mouseVelocity.y; // Pitch from mouse Y
    
    // Clamp pitch to prevent flipping
    cameraRot.x = glm::clamp(cameraRot.x, -glm::pi<float>() / 2.0f, glm::pi<float>() / 2.0f);
}

void Game::update(float dt) {
    opponent->update(dt);
    checkHit();
}

void Game::checkHit() {
    // Check if cursor is on opponent pip
    // This would compare screen-space positions of cursor vs pip
}

void Game::render() {
    renderer->beginFrame();
    
    const auto& opponentTransform = opponent->getTransform();
    renderer->renderTriangle(opponentTransform, opponent->getSize());
    
    // Render pip at opponent position
    bool isHit = false; // TODO: determine from checkHit()
    renderer->renderPip(
        opponentTransform.position,
        opponent->getDirection(),
        opponent->getSize(),
        isHit
    );
    
    // Render centerless crosshair at screen center
    renderer->renderCrosshair();
    
    renderer->endFrame();
}
