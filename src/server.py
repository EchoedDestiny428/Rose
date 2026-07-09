from ursinanetworking import UrsinaNetworkingServer
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import src.settings as cfg

server = UrsinaNetworkingServer("0.0.0.0", cfg.MULTIPLAYER_SERVER_PORT)


players = {}

@server.event
def onClientConnected(client):
    print(f"[{client.id}] connected!")
    players[client.id] = {"position": (0, 0, 0), "rotation": (0, 0, 0)}
    
    for p_id in players:
        if p_id != client.id:
            client.send_message("player_joined", p_id)
            client.send_message("sync_pos", {"id": p_id, "pos": players[p_id]["position"], "rot": players[p_id]["rotation"]})
            
    server.broadcast("player_joined", client.id)
    client.send_message("welcome", client.id)

@server.event
def onClientDisconnected(client):
    print(f"[{client.id}] disconnected!")
    if client.id in players:
        del players[client.id]
    server.broadcast("player_left", client.id)

@server.event
def update_pos(client, data):
    if client.id in players:
        players[client.id]["position"] = data["pos"]
        players[client.id]["rotation"] = data["rot"]

        sync_data = {"id": client.id, "pos": data["pos"], "rot": data["rot"]}
        
        for c in server.get_clients():
            if c.id != client.id:
                c.send_message("sync_pos", sync_data)

@server.event
def fire_laser(client, data):
    sync_data = {"id": client.id, "pos": data["pos"], "vel": data["vel"]}
    for c in server.get_clients():
        if c.id != client.id:
            c.send_message("spawn_laser", sync_data)

print(f"Server starting on 0.0.0.0:{cfg.MULTIPLAYER_SERVER_PORT} (Accepting LAN connections)...")
while True:
    server.process_net_events()
