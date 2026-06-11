cmake_minimum_required(VERSION 3.16)
project(VJoyAimTrainer)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find required packages
find_package(OpenGL REQUIRED)   
find_package(glfw3 REQUIRED)    
find_package(glm REQUIRED)

# Source files
set(SOURCES
    main.cpp
    window.cpp
    renderer.cpp
    game.cpp
    input.cpp
    physics.cpp
    geometry.cpp
    ui.cpp
)

# Create executable
add_executable(vjoy_trainer ${SOURCES})

# Link libraries
target_link_libraries(vjoy_trainer
    OpenGL::GL
    glfw
    glm::glm
)

# Include directories
target_include_directories(vjoy_trainer PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/../include)

# Optimization flags
if(MSVC)
    target_compile_options(vjoy_trainer PRIVATE /O2 /W4 /fp:fast)
else()
    target_compile_options(vjoy_trainer PRIVATE -O3 -Wall -Wextra -ffast-math)
endif()
