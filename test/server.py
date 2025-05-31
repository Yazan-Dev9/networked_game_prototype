import socket
import threading
import logging
from colorama import init, Fore, Style
import traceback

init(autoreset=True)

class ColorFormatter(logging.Formatter):
    COLORS = {
        logging.DEBUG: Fore.BLUE,
        logging.INFO: Fore.GREEN,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Fore.RED + Style.BRIGHT,
    }
    def format(self, record):
        color = self.COLORS.get(record.levelno, "")
        message = super().format(record)
        return color + message + Style.RESET_ALL

file_handler = logging.FileHandler("server.log", encoding='utf-8')
file_handler.setFormatter(logging.Formatter('[%(asctime)s][%(levelname)s][%(threadName)s] %(message)s', "%Y-%m-%d %H:%M:%S"))

handler = logging.StreamHandler()
formatter = ColorFormatter('[%(asctime)s][%(levelname)s][%(threadName)s] %(message)s', "%H:%M:%S")
handler.setFormatter(formatter)
logger = logging.getLogger("server")
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)
logger.addHandler(file_handler)

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('localhost', 12345))
server_socket.listen(5)

logger.info("Listening on port 12345")

# قواميس لتخزين بيانات اللاعبين والاتصالات
players = {}   # name -> (x, y)
connections = {}  # name -> client_socket
lock = threading.Lock()

def broadcast_players():
    """إرسال قائمة الإحداثيات لجميع اللاعبين."""
    with lock:
        data = []
        for name, (x, y) in players.items():
            data.append(f"{name}:{x},{y}")
        message = "|".join(data)
        for sock in connections.values():
            try:
                sock.sendall(message.encode('utf-8'))
            except:
                pass  # قد يكون الاتصال أغلق

def handle_client(client_socket, addr):
    try:
        client_socket.send("Welcome! Send your name:".encode('utf-8'))
        name = client_socket.recv(1024).decode('utf-8').strip()
        if not name:
            logger.warning(f"Empty name from {addr}, closing connection.")
            client_socket.close()
            return

        with lock:
            connections[name] = client_socket
        logger.info(f'Connected: {addr} as {name}')
        client_socket.send(f"Hello {name}! Send coordinates (x,y). Send 'exit' to leave.".encode('utf-8'))

        while True:
            data = client_socket.recv(1024).decode('utf-8').strip()
            if not data or data.lower() == "exit":
                logger.warning(f"Client {name} ({addr}) disconnected.")
                break
            logger.debug(f"Coordinates from {name} ({addr}): {data}")
            try:
                # تحقق من أن البيانات على شكل x,y
                parts = data.split(',')
                if len(parts) != 2:
                    raise ValueError("Input must be in format: x,y")
                x, y = float(parts[0].strip()), float(parts[1].strip())
                with lock:
                    players[name] = (x, y)
                broadcast_players()
                logger.info(f"Updated coordinates for {name}: {x},{y} and broadcasted to all clients.")
            except Exception as coord_err:
                client_socket.send(f'Error: {coord_err}'.encode('utf-8'))
                logger.error(f'Error: {coord_err}\n{traceback.format_exc()}')
    except Exception as e:
        logger.error(f"Error with client {addr}: {e}\n{traceback.format_exc()}")
    finally:
        with lock:
            players.pop(name, None)
            connections.pop(name, None)
        broadcast_players()
        client_socket.close()
        logger.info(f"Connection with {addr} closed.")

try:
    while True:
        client_socket, addr = server_socket.accept()
        client_thread = threading.Thread(target=handle_client, args=(client_socket, addr), daemon=True)
        client_thread.start()
except KeyboardInterrupt:
	pass
