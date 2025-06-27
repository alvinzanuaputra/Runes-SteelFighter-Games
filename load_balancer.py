import socket
import threading
import pickle

servers = [
    # Round robin load balancing with 10 servers
    {"host": "localhost", "port": 8890, "clients": 0},
    {"host": "localhost", "port": 8891, "clients": 0},
    {"host": "localhost", "port": 8892, "clients": 0},
    {"host": "localhost", "port": 8893, "clients": 0},
    {"host": "localhost", "port": 8894, "clients": 0},
    {"host": "localhost", "port": 8895, "clients": 0},
    {"host": "localhost", "port": 8896, "clients": 0},
    {"host": "localhost", "port": 8897, "clients": 0},
    {"host": "localhost", "port": 8898, "clients": 0},
    {"host": "localhost", "port": 8899, "clients": 0}
]
lock = threading.Lock()
def forward(src, dst, server_ref):
    try:
        while True:
            data = src.recv(4096)
            if not data:
                break
            dst.sendall(data)
    except:
        pass
    finally:
        src.close()
        dst.close()
        with lock:
            server_ref["clients"] -= 1

def handle_client(client_socket):
    global servers
    with lock:
        selected_server = None
        for server in servers:
            if server["clients"] < 2:
                selected_server = server
                server["clients"] += 1
                break
        if not selected_server:
            client_socket.send(b"FULL")
            client_socket.close()
            return
    try:
        backend = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        backend.connect((selected_server["host"], selected_server["port"]))
    except:
        client_socket.send(b"ERROR CONNECTING TO SERVER")
        client_socket.close()
        return
    threading.Thread(target=forward, args=(client_socket, backend, selected_server)).start()
    threading.Thread(target=forward, args=(backend, client_socket, selected_server)).start()

def main():
    balancer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    balancer.bind(("0.0.0.0", 8888))
    balancer.listen(10)
    print("[LOAD BALANCER] Listening on port 8888...")
    while True:
        client_sock, addr = balancer.accept()
        print(f"[LOAD BALANCER] Client connected from {addr}")
        threading.Thread(target=handle_client, args=(client_sock,)).start()

if __name__ == "__main__":
    main()