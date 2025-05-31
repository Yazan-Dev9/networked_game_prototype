import threading
from server import Server
from game import Game
from player import Player
import sys
import time


def main(*args):
    """
    The main entry point for the multiplayer game client.

    - Optionally starts the server in a background thread (currently commented out).
    - Prompts the user for their player name and creates a Player instance.
    - Adds the local player to the game and starts the main game loop.
    - Handles graceful shutdown on keyboard interrupt.

    Args:
        *args: Command line arguments (not used).
    """
    # Optionally start the server in a separate thread
    server = Server()
    threading.Thread(target=server.start, daemon=True).start()

    # Add a local player (optional)
    game = Game()
    name = input("Enter Your Name -> ")
    player = Player(name)
    player.color = "darkgreen"
    game.add_player(player)
    # Start the game (in the main thread)
    try:
        game.start()
    except KeyboardInterrupt:
        print("Exiting game...")
    finally:
        # On exit, make sure to close the server and game
        # server.running = False
        # Wait for the server to shut down (if desired)
        time.sleep(1)
        sys.exit(0)


if __name__ == "__main__":
    main(sys.argv)
