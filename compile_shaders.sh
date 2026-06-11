#!/bin/bash
# Compile GLSL shaders to SPIR-V

# Check if glslc is available
if ! command -v glslc &> /dev/null; then
    echo "glslc not found. Please install Vulkan SDK."
    exit 1
fi

echo "Compiling shaders..."
glslc shaders/shader.vert -o shaders/shader.vert.spv
glslc shaders/shader.frag -o shaders/shader.frag.spv

echo "Shader compilation complete"
