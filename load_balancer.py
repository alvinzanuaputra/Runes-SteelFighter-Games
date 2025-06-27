import socket
import threading

# Daftar backend server (bisa ditambah sesuai kebutuhan)
servers = [
    {"host": "localhost", "port": 8890, "clients": 0},
    {"host": "localhost", "port": 8891, "clients": 0},
]

lock = threading.Lock()

# Forward data dari src ke dst
def forward(src, dst):
    try:
        while True:
            data = src.recv(4096)
            if not data:
                break
            dst.sendall(data)
    except:
        pass
    finally:
        try:
            dst.shutdown(socket.SHUT_WR)
        except:
            pass

# Handle koneksi dari satu klien
def handle_client(client_socket):
    global servers
    with lock:
        selected_server = None
        for server in servers:
            if server["clients"] < 100:  # batas klien per backend
                selected_server = server
                server["clients"] += 1
                break
        if not selected_server:
            client_socket.sendall(b"HTTP/1.1 503 Service Unavailable\r\n\r\nServer Full")
            client_socket.close()
            return

    try:
        backend = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        backend.connect((selected_server["host"], selected_server["port"]))

        # Buat thread dua arah forwarding
        t1 = threading.Thread(target=forward, args=(client_socket, backend))
        t2 = threading.Thread(target=forward, args=(backend, client_socket))

        t1.start()
        t2.start()

        # Jangan tutup langsung!
        t1.join()
        t2.join()

        client_socket.close()
        backend.close()


    except Exception as e:
        print("[ERROR]", e)
        try:
            client_socket.sendall(b"HTTP/1.1 500 Internal Server Error\r\n\r\nBackend Error")
        except:
            pass
    finally:
        client_socket.close()
        with lock:
            selected_server["clients"] -= 1

# Entry point main
def main():
    balancer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    balancer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    balancer.bind(("0.0.0.0", 8888))
    balancer.listen(50)

    print("[LOAD BALANCER] Listening on port 8888...")

    while True:
        client_sock, addr = balancer.accept()
        print(f"[LOAD BALANCER] Client connected from {addr}")
        threading.Thread(target=handle_client, args=(client_sock,), daemon=True).start()

if __name__ == "__main__":
    main()
