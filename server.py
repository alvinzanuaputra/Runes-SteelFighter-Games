import socket
import threading
from http import HttpServer

httpserver = HttpServer()

def ProcessTheClient(connection, address):
    rcv = ""
    while True:
        try:
            data = connection.recv(1024)
            if data:
                # Konversi dari bytes ke string agar bisa deteksi \r\n
                d = data.decode()
                rcv += d

                # Akhiran HTTP selalu kosong setelah \r\n\r\n (end of headers + body)
                if "\r\n\r\n" in rcv:
                    # Proses request lengkap
                    hasil = httpserver.proses(rcv)
                    hasil += b"\r\n\r\n"

                    connection.sendall(hasil)
                    rcv = ""
                    connection.close()
                    return
            else:
                break
        except OSError as e:
            break

    connection.close()
    return

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("localhost", 8888))
    server.listen(5)

    print("Server started on port 8888...")

    while True:
        conn, addr = server.accept()
        print(f"Accepted connection from {addr}")
        thread = threading.Thread(target=ProcessTheClient, args=(conn, addr))
        thread.start()

if __name__ == "__main__":
    main()
