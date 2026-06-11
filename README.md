# VJoy Aim Trainer

A high-performance aim trainer with Star Citizen-style pips, built with C++ (OpenGL) and Python.

## Features

- **3D First-Person Aiming**: 360° free-look camera with mouse control
- **vJoy-Style Input**: Mouse movement translates to velocity (not direct position)
- **Star Citizen Pips**: 
  - Red/green hollow circle pip (red by default, green when cursor on target)
  - Guidance lines ("|" on sides) that rotate with opponent movement
  - Lines width matches opponent width
- **Centerless Crosshair**: Minimal "+" crosshair at screen center
- **Physics-Based Opponent**: Triangle opponent with acceleration and direction changes
- **High Performance**: OpenGL renderer targeting 144+ FPS
- **Cross-platform**: Windows + Linux support

## Requirements

### Windows
- Visual Studio 2019 or later (MSVC) OR GCC/Clang
- CMake 3.16+
- OpenGL 4.5+
- GLFW3
- GLM

### Linux (Ubuntu/Debian)
```bash
sudo apt-get install cmake libglfw3-dev libglm-dev libgl1-mesa-dev
```

### macOS
```bash
brew install cmake glfw3 glm
```

## Building

```bash
mkdir build
cd build
cmake ..
cmake --build . --config Release
cd ..
```

Or use the Python launcher:
```bash
python launcher.py
```

## Running

```bash
./build/vjoy_trainer  # Linux/macOS
build\Release\vjoy_trainer.exe  # Windows
```

Or with launcher:
```bash
python launcher.py
```

## Project Structure

```
Rose/
├── include/          # Header files
│   ├── window.h
│   ├── renderer.h
│   ├── game.h
│   ├── input.h
│   ├── physics.h
│   ├── geometry.h
│   ├── ui.h
│   └── vulkan_utils.h
├── src/              # Source files
│   ├── CMakeLists.txt
│   ├── main.cpp
│   ├── window.cpp
│   ├── renderer.cpp
│   ├── game.cpp
│   ├── input.cpp
│   ├── physics.cpp
│   ├── geometry.cpp
│   └── ui.cpp
├── shaders/          # GLSL shaders
│   ├── shader.vert
│   └── shader.frag
├── CMakeLists.txt
├── launcher.py       # Python build/launch script
├── config.json       # Configuration
└── README.md
```

## Configuration

Edit `config.json` to customize:
- Resolution
- Target FPS
- Mouse sensitivity
- Opponent speed
- Pip and crosshair sizes

## Controls

- **Mouse**: Aim (vJoy-style velocity input)
- **ESC**: Exit

## Architecture

- **C++ Engine**: OpenGL-based renderer
  - Clean separation: headers in `/include`, sources in `/src`
  - Modular design: Window, Input, Renderer, Game, Physics
  - Fast iteration with simple OpenGL pipeline

- **Python Launcher**: Configuration and build management
  - Handles CMake configuration
  - Automatic build
  - Cross-platform support

## Performance

Target: 144+ FPS at 1920x1080 with OpenGL's efficient rendering.

## Future Improvements

- Recording and playback
- Multiple opponent types
- Difficulty scaling
- Statistics tracking
- Custom pip styles
- Network multiplayer
