import socket
import threading
import pickle
import sys

players = [{}, {}] 
lock = threading.Lock()

def handle_client(conn, player_id):
    players[player_id] = {
        "x": 100 if player_id == 0 else 700,
        "y": 300,
        "health": 100,
        "action": 0,
        "flip": False,
        "attack_type": 0
    }
    conn.send(pickle.dumps({"player": player_id}))
    while True:
        try:
            data = pickle.loads(conn.recv(4096))
            with lock:
                for key in data:
                    if key != "health":
                        players[player_id][key] = data[key]
                
                enemy_id = 1 - player_id

                if players[enemy_id]:
                    att_x = players[player_id].get("x", 0)
                    att_y = players[player_id].get("y", 0)
                    target_x = players[enemy_id].get("x", 0)
                    target_y = players[enemy_id].get("y", 0)

                    if players[player_id].get("attack_type", 0) in [1, 2]:
                        if abs(att_x - target_x) < 150 and abs(att_y - target_y) < 100:
                            players[enemy_id]["health"] = max(0, players[enemy_id].get("health", 100) - 10)
                        players[player_id]["attack_type"] = 0  # reset agar tidak spam hit

                reply = {
                    "self": players[player_id],
                    "enemy": players[enemy_id] if players[enemy_id] else {}
                }
                conn.sendall(pickle.dumps(reply))
        except:
            break
    conn.close()

def main():
    PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8889
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", PORT))
    server.listen(2)
    print(f"[SERVER] Running on port {PORT}...")

    player_id = 0
    while player_id < 2:
        conn, addr = server.accept()
        print(f"[SERVER] Player {player_id} connected from {addr}")
        thread = threading.Thread(target=handle_client, args=(conn, player_id))
        thread.start()
        player_id += 1

if __name__ == "__main__":
    main()
