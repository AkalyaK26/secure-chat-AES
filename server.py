import socket
import threading

HOST = '127.0.0.1'
PORT = 65432
clients = []

def broadcast(message, sender_socket):
    for client in clients:
        if client != sender_socket:
            try:
                client.send(message)
            except Exception:
                remove_client(client)

def handle_client(client_socket, client_address):
    print(f"[CONNECTED] Client {client_address} online.")
    while True:
        try:
            data = client_socket.recv(4096)
            if not data:
                break
            broadcast(data, client_socket)
        except Exception:
            break
    remove_client(client_socket)

def remove_client(client_socket):
    if client_socket in clients:
        clients.remove(client_socket)
        client_socket.close()
        print("[DISCONNECTED] Client left.")

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(2)
    print(f"[SERVER STARTED] Listening on {HOST}:{PORT}...")

    while len(clients) < 2:
        client_socket, client_address = server.accept()
        clients.append(client_socket)
        thread = threading.Thread(target=handle_client, args=(client_socket, client_address), daemon=True)
        thread.start()
        print(f"[CONNECTIONS] {len(clients)}/2 connected.")

    print("[READY] Both clients connected. Relay active.")
    while len(clients) > 0:
        pass

if __name__ == "__main__":
    start_server()
