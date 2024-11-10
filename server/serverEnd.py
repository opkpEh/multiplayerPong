import socket
import threading
import time

class GameServer:
    def __init__(self, host='localhost', port=5555):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen()
        self.clients = []
        self.running = True
        print(f"Server started on {host}:{port}")

    def handle_client(self, client_socket, addr):
        while self.running:
            try:
                message = client_socket.recv(1024).decode('utf-8')
                if not message:
                    break
                print(f"Received from {addr}: {message}")
                #game code 
                if message == 'W':
                    print("Player moved up")
                elif message == 'S':
                    print("Player moved down")
            except:
                break
        
        print(f"Client {addr} disconnected")
        self.clients.remove(client_socket)
        client_socket.close()

    def start(self):
        while self.running:
            try:
                client_socket, addr = self.server.accept()
                self.clients.append(client_socket)
                print(f"Connected with {addr}")
                client_thread = threading.Thread(target=self.handle_client, args=(client_socket, addr))
                client_thread.start()
            except:
                break

    def stop(self):
        self.running = False
        for client in self.clients:
            client.close()
        self.server.close()

