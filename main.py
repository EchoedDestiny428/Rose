from ursina import *
from panda3d.core import ClockObject # pyrefly: ignore [missing-import]

# Initialize Ursina app before creating any entities
app = Ursina()

# Import our custom modules
from src.environment import setup_environment
from src.ui import UIManager
from src.player import PlayerController

# Global clock
clock_obj = ClockObject.get_global_clock()

# Setup the environment (lighting, space dust)
stars, dust, lumina, cubes = setup_environment()

# Initialize the UI Manager (sliders, crosshair, arrow)
ui_manager = UIManager()

# Initialize the Player Controller (6DOF flight, physics, inputs)
player = PlayerController(ui_manager)
ui_manager.player = player

app.run()