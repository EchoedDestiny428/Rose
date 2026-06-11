@echo off
REM Compile GLSL shaders to SPIR-V

where glslc >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo glslc not found. Please install Vulkan SDK.
    exit /b 1
)

echo Compiling shaders...
glslc shaders\shader.vert -o shaders\shader.vert.spv
glslc shaders\shader.frag -o shaders\shader.frag.spv

echo Shader compilation complete
