import socket
import threading

# Daftar backend server
servers = [
    {"host": "localhost", "port": 8890, "clients": 0},
    {"host": "localhost", "port": 8891, "clients": 0}
]

lock = threading.Lock()
rr_index = 0  # Round-robin index

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
    global servers, rr_index

    with lock:
        # Cari server berikutnya secara round-robin
        num_servers = len(servers)
        for _ in range(num_servers):
            server = servers[rr_index]
            rr_index = (rr_index + 1) % num_servers
            if server["clients"] < 100:
                selected_server = server
                selected_server["clients"] += 1
                break
        else:
            client_socket.sendall(b"HTTP/1.1 503 Service Unavailable\r\n\r\nServer Full")
            client_socket.close()
            return

    try:
        backend = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        backend.connect((selected_server["host"], selected_server["port"]))

        t1 = threading.Thread(target=forward, args=(client_socket, backend))
        t2 = threading.Thread(target=forward, args=(backend, client_socket))

        t1.start()
        t2.start()

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
