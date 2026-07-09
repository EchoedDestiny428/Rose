from ursina import *
from panda3d.core import ClockObject # pyrefly: ignore [missing-import]
from panda3d.core import loadPrcFileData# pyrefly: ignore [missing-import]


loadPrcFileData('', 'framebuffer-multisample 1')
loadPrcFileData('', 'multisamples 8')

app = Ursina()

from src.environment import setup_environment
from src.ui import UIManager
from src.player import LocalPlayer, RemotePlayer

clock_obj = ClockObject.get_global_clock()
ui_manager = UIManager()
player = LocalPlayer(ui_manager)
stars, dust, lumina, cubes = setup_environment(player)
ui_manager.player = player

# Spawn a dummy remote player
dummy_player = RemotePlayer(position=(0, 0, 50))

player.obstacles = cubes + [dummy_player]
for obj in player.obstacles:
    ui_manager.add_target_marker(obj)

app.run()