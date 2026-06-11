#!/usr/bin/env python3
"""
VJoy Aim Trainer Launcher
Handles configuration and launching the C++ game engine.
"""

import json
import os
import subprocess
import sys
from pathlib import Path


class TrainerConfig:
    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return self.get_defaults()
    
    def get_defaults(self):
        return {
            "resolution": {"width": 1920, "height": 1080},
            "target_fps": 144,
            "mouse_sensitivity": 0.5,
            "opponent_speed": 1.0,
            "pip_size": 30,
            "crosshair_size": 20,
        }
    
    def save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def get(self, key, default=None):
        return self.config.get(key, default)
    
    def set(self, key, value):
        self.config[key] = value
        self.save_config()


def build_project():
    """Build C++ project with CMake."""
    build_dir = Path("build")
    build_dir.mkdir(exist_ok=True)
    
    print("Building project...")
    
    # Configure
    result = subprocess.run(
        ["cmake", "-B", str(build_dir), "-S", "."],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        print("CMake configuration failed:")
        print(result.stderr)
        return False
    
    # Build
    result = subprocess.run(
        ["cmake", "--build", str(build_dir), "--config", "Release"],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        print("Build failed:")
        print(result.stderr)
        return False
    
    print("Build successful!")
    return True


def run_trainer(config):
    """Launch the trainer."""
    build_dir = Path("build")
    
    # Determine executable name
    if sys.platform == "win32":
        executable = build_dir / "Release" / "vjoy_trainer.exe"
    else:
        executable = build_dir / "vjoy_trainer"
    
    if not executable.exists():
        print(f"Executable not found: {executable}")
        return False
    
    print(f"Launching trainer: {executable}")
    
    try:
        subprocess.run(str(executable), check=True)
    except subprocess.CalledProcessError as e:
        print(f"Trainer exited with error: {e}")
        return False
    
    return True


def main():
    config = TrainerConfig()
    
    # Check if rebuild is needed
    if not Path("build/CMakeCache.txt").exists():
        if not build_project():
            sys.exit(1)
    
    # Run trainer
    if not run_trainer(config):
        sys.exit(1)


if __name__ == "__main__":
    main()
