import socket
from colorama import init, Fore, Style

init(autoreset=True)

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    client_socket.connect(('localhost', 12345))
    name = input(Fore.YELLOW + "Enter your name: ")
    client_socket.send(name.encode('utf-8'))
    
    print(Fore.CYAN + "Connected to server. Type 'exit' to quit.")

    while True:
        message = input(Fore.YELLOW + "Enter message (e.g. 3+4) -> ")
        if message.lower() == "exit":
            print(Fore.MAGENTA + "Closing connection...")
            break
        if message.strip() == "":
            print(Fore.RED + "Empty message! Please enter something.")
            continue

        client_socket.send(message.encode('utf-8'))

        response = client_socket.recv(1024).decode('utf-8')
        if response.startswith('Error'):
            print(Fore.RED + f"Server response {response}")
        else:
            print(Fore.GREEN + f"Server response: {response}")

except ConnectionRefusedError:
    print(Fore.RED + "Could not connect to the server. Is it running?")
except Exception as e:
    print(Fore.RED + f"An error occurred: {e}")
finally:
    client_socket.close()
    print(Style.DIM + "Connection closed.")
