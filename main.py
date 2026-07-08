from ursina import *
from panda3d.core import ClockObject # pyrefly: ignore [missing-import]

app = Ursina()

from src.environment import setup_environment
from src.ui import UIManager
from src.player import PlayerController

clock_obj = ClockObject.get_global_clock()
stars, dust, lumina, cubes = setup_environment()
ui_manager = UIManager()
player = PlayerController(ui_manager)
ui_manager.player = player

app.run()