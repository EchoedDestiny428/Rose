cmake_minimum_required(VERSION 3.16)
project(VJoyAimTrainer)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find required packages
find_package(OpenGL REQUIRED)   
find_package(glfw3 REQUIRED)    
find_package(glm REQUIRED)
find_package(glad CONFIG REQUIRED)

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
    glad::glad
)

# Include directories
target_include_directories(vjoy_trainer PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/../include)

# Optimization flags
if(MSVC)
    # Only apply /O2 optimization if we are NOT in Debug mode
    target_compile_options(vjoy_trainer PRIVATE 
        $<$<NOT:$<CONFIG:Debug>>:/O2> 
        /W4 
        /fp:fast
    )
else()
    # For GCC/Clang, only apply -O3 if we are NOT in Debug mode
    target_compile_options(vjoy_trainer PRIVATE 
        $<$<NOT:$<CONFIG:Debug>>:-O3> 
        -Wall 
        -Wextra 
        -ffast-math
    )
endif()