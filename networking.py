import socket
import threading


class NetWorking:
    """
    Handles TCP network connection for the game client.

    This class manages connecting to a server, sending and receiving messages,
    and buffering incoming data using a background thread.

    Attributes:
        host (str): The server host address.
        port (int): The server port.
        socket (socket.socket): The TCP socket for communication.
        connected (bool): Connection status.
        lock (threading.Lock): Threading lock for safe access to shared data.
        recv_buffer (list[str]): Buffer for received messages.
        running (bool): Indicates if the receive thread should keep running.
    """

    def __init__(self, host="localhost", port=12345):
        """
        Initialize the networking client with the specified host and port.

        Args:
            host (str): The server host address. Defaults to "localhost".
            port (int): The server port. Defaults to 12345.
        """
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected = False
        self.lock = threading.Lock()
        self.recv_buffer = []
        self.running = True

    def connect(self):
        """
        Connect to the server using the specified host and port.

        Starts a background thread to receive messages from the server.
        """
        try:
            self.socket.connect((self.host, self.port))
            self.connected = True
            threading.Thread(target=self._receive_thread, daemon=True).start()
        except Exception as e:
            print(f"Connection error: {e}")
            self.connected = False

    def send(self, message: str):
        """
        Send a string message to the server.

        Args:
            message (str): The message to send.
        """
        if self.connected:
            try:
                with self.lock:
                    self.socket.sendall(message.encode("utf-8"))
            except Exception as e:
                print(f"Send error: {e}")
                self.connected = False

    def _receive_thread(self):
        """
        Internal method: Continuously receive messages from the server in a background thread.

        Splits incoming data by newlines and stores complete messages in the receive buffer.
        """
        while self.connected and self.running:
            try:
                data = self.socket.recv(4096)
                if not data:
                    self.connected = False
                    break
                text = data.decode("utf-8")

                for msg in text.split("\n"):
                    if msg.strip():
                        with self.lock:
                            self.recv_buffer.append(msg.strip())
            except Exception as e:
                print(f"Receive error: {e}")
                self.connected = False
                break

    def recv(self) -> str:
        """
        Retrieve the oldest message from the receive buffer, if available.

        Returns:
            str: The next message from the server, or an empty string if no messages are available.
        """
        with self.lock:
            if self.recv_buffer:
                return self.recv_buffer.pop(0)
        return ""

    def close(self):
        """
        Close the network connection and stop the receive thread.
        """
        self.running = False
        self.connected = False
        try:
            self.socket.close()
        except Exception:
            pass


# Example usage (for testing only):
if __name__ == "__main__":
    net = NetWorking()
    net.connect()
    net.send("JOIN,Ali")
