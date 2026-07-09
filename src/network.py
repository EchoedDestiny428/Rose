from ursina import *
from ursinanetworking import UrsinaNetworkingClient
from src.player import RemotePlayer, LaserProjectile
import src.settings as cfg

class NetworkManager:
    def __init__(self, local_player, ui_manager):
        self.local_player = local_player
        self.ui_manager = ui_manager
        
        self.client = UrsinaNetworkingClient(cfg.MULTIPLAYER_SERVER_IP, cfg.MULTIPLAYER_SERVER_PORT)
        self.remote_players = {}
        
        self.last_sync = 0.0
        self.sync_rate = 1.0 / 20.0 # 20 Hz
        
        self.debug_text = Text(text='', position=(-0.7, 0.45), origin=(-0.5, 0.5), color=color.yellow, scale=0.8, parent=camera.ui)
        
        # Bind events
        self.client.event(self.player_joined)
        self.client.event(self.player_left)
        self.client.event(self.sync_pos)
        self.client.event(self.spawn_laser)
        self.client.event(self.welcome)

    def welcome(self, data):
        self.ui_manager.show_notification(f"Connected as {data}!")
        self.local_player_id = data

    def player_joined(self, p_id):
        print(f"Player joined: {p_id}")
        if p_id not in self.remote_players:
            rp = RemotePlayer(position=(0, -9999, 0))
            self.remote_players[p_id] = rp
            self.local_player.obstacles.append(rp)
            self.ui_manager.add_target_marker(rp)
            self.ui_manager.show_notification(f"Player {p_id} joined!")

    def player_left(self, p_id):
        print(f"Player left: {p_id}")
        if p_id in self.remote_players:
            rp = self.remote_players[p_id]
            if rp in self.local_player.obstacles:
                self.local_player.obstacles.remove(rp)
            self.ui_manager.remove_target_marker(rp)
            destroy(rp)
            del self.remote_players[p_id]
            self.ui_manager.show_notification(f"Player {p_id} left.")

    def sync_pos(self, data):
        p_id = data["id"]
        if p_id in self.remote_players:
            rp = self.remote_players[p_id]
            # Convert tuples back to Vec3
            rp.target_position = Vec3(*data["pos"])
            rp.target_rotation = Vec3(*data["rot"])

    def spawn_laser(self, data):
        p_id = data["id"]
        if p_id in self.remote_players:
            rp = self.remote_players[p_id]
            pos = Vec3(*data["pos"])
            vel = Vec3(*data["vel"])
            # Create a laser projectile owned by the remote player
            LaserProjectile(position=pos, velocity=vel, owner=rp)

    def fire_laser(self, pos, vel):
        if not hasattr(self, 'local_player_id'):
            return
        self.client.send_message("fire_laser", {
            "id": self.local_player_id,
            "pos": (pos.x, pos.y, pos.z),
            "vel": (vel.x, vel.y, vel.z)
        })

    def update(self):
        self.client.process_net_events()
        
        self.last_sync += time.dt
        if self.last_sync >= self.sync_rate:
            self.last_sync = 0.0
            
            if not hasattr(self, 'local_player_id'):
                return
                
            p = self.local_player.position
            r = self.local_player.rotation
            
            self.client.send_message("update_pos", {
                "id": self.local_player_id,
                "pos": (p.x, p.y, p.z),
                "rot": (r.x, r.y, r.z)
            })
            
        debug_str = f"Local: {self.local_player.position.x:.1f}, {self.local_player.position.y:.1f}, {self.local_player.position.z:.1f}\n"
        for p_id, rp in self.remote_players.items():
            debug_str += f"Remote {p_id}: {rp.target_position.x:.1f}, {rp.target_position.y:.1f}, {rp.target_position.z:.1f}\n"
        self.debug_text.text = debug_str
