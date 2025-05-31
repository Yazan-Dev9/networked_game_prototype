import socket
import threading


class Server:
    """
    A simple TCP server for multiplayer game synchronization.

    Handles client connections, player state management, and broadcasting updates to all clients.
    """

    def __init__(self, host="localhost", port=12345):
        """
        Initialize the server and prepare to accept connections.

        Args:
            host (str): The IP address or hostname to bind the server. Defaults to "localhost".
            port (int): The port number to listen on. Defaults to 12345.
        """
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.host = host
        self.port = port
        self.clients = []
        self.players = {}
        self.lock = threading.Lock()
        self.running = True

    def broadcast(self, message, exclude_socket=None):
        """
        Send a message to all connected clients, optionally excluding one socket.

        Args:
            message (str): The message to broadcast.
            exclude_socket (socket.socket, optional): A client socket to exclude from broadcast.
        """
        with self.lock:
            for client in self.clients[:]:
                if client != exclude_socket:
                    try:
                        client.sendall(message.encode("utf-8"))
                    except Exception:
                        self.clients.remove(client)
                        if client in self.players:
                            del self.players[client]
                        client.close()

    def handle_client(self, client_socket, address):
        """
        Handle communication with a single client.

        Processes JOIN and MOVE commands, updates player state,
        and broadcasts changes to all clients.

        Args:
            client_socket (socket.socket): The client's socket.
            address (tuple): The client's (IP, port) address.
        """
        try:
            while True:
                data = client_socket.recv(1024).decode("utf-8")
                if not data:
                    break
                parts = data.split(",")
                if parts[0] == "JOIN" and len(parts) == 2:
                    name = parts[1].strip()
                    with self.lock:
                        self.players[client_socket] = {"name": name, "x": 0, "y": 0}
                    join_msg = f"JOINED,{name}"
                    self.broadcast(join_msg, exclude_socket=None)
                elif parts[0] == "MOVE" and len(parts) == 4:
                    name, x, y = parts[1], parts[2], parts[3]
                    try:
                        x = int(x)
                        y = int(y)
                        with self.lock:
                            self.players[client_socket] = {"name": name, "x": x, "y": y}
                        with self.lock:
                            all_data = ";".join(
                                f"{info['name']},{info['x']},{info['y']}"
                                for info in self.players.values()
                            )
                        self.broadcast(f"UPDATE;{all_data}")
                    except Exception:
                        continue
                else:
                    continue
        except Exception as e:
            print(f"Error with {address}: {e}")
        finally:
            with self.lock:
                if client_socket in self.clients:
                    self.clients.remove(client_socket)
                player = self.players.pop(client_socket, None)
            client_socket.close()
            if player:
                leave_msg = f"LEFT,{player['name']}"
                self.broadcast(leave_msg, exclude_socket=None)

    def start(self):
        """
        Start the server and accept incoming connections.

        For each new client, a separate thread is started to handle communication.
        """
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print("Server started.")
        try:
            while self.running:
                try:
                    client_socket, address = self.server_socket.accept()
                    print("New connection from:", address)
                except OSError:
                    break
                with self.lock:
                    self.clients.append(client_socket)
                threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, address),
                    daemon=True,
                ).start()
        finally:
            print("Server shutting down.")
            with self.lock:
                for client in self.clients:
                    try:
                        client.close()
                    except Exception:
                        pass
                self.clients.clear()
                self.players.clear()
            self.server_socket.close()

    def stop(self):
        """
        Stop the server and close all connections.
        """
        self.running = False
        self.server_socket.close()


if __name__ == "__main__":
    server = None
    try:
        server = Server()
        server.start()
    except KeyboardInterrupt:
        print("Stopping server...")
        if server is not None:
            server.stop()
        print("Server stopped.")
