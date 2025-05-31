from __future__ import annotations
from typing import Optional, TYPE_CHECKING
import os
import pygame
from networking import NetWorking
from player import Player

# if TYPE_CHECKING:
#     from player import Player


class Game:
    """
    Multiplayer Game class using pygame for graphics and sound, and a custom networking module for communication.

    Handles the main game loop, player movement, rendering, network synchronization,
    and player management in a simple multiplayer environment.
    """

    WIDTH: int = 400
    HEIGHT: int = 300
    FPS: int = 60
    TITLE: str = "Multiplayer Game"
    SIZE: tuple = (WIDTH, HEIGHT)
    SPEED: int = 5
    SCREEN_COLOR: str = "darkblue"
    PLAYER_RADIUS: int = 20

    def __init__(self) -> None:
        """
        Initialize the game window, sound, networking, and internal state.
        """
        pygame.init()
        self.players: list[Player] = []
        self.player: Optional[Player] = None
        self.running: bool = True
        self.init_screen()
        self.init_sound()
        self.connect()
        self.show_main_menu()

    def connect(self) -> None:
        """
        Connection to the network.
        """
        self.network = NetWorking()
        self.network.connect()

    def init_sound(self) -> None:
        """
        Initialize sound settings and load movement sound effect.
        """
        pygame.mixer.init()
        move_file: str = "./assets/sounds/move.ogg"
        if os.path.exists(move_file):
            self.move_sound = pygame.mixer.Sound(move_file)
            self.move_sound.set_volume(0.5)
        else:
            print(f"File {move_file} not found")
            self.move_sound = None

    def init_screen(self) -> None:
        """
        Set up the pygame screen, window caption, and frame rate clock.
        """
        self.screen = pygame.display.set_mode(self.SIZE)
        pygame.display.set_caption(self.TITLE)
        self.fps_clock = pygame.time.Clock()

    def show_main_menu(self) -> None:
        """
        Main menu loop to get player name and join the game.
        """
        input_active = True
        player_name = ""
        input_box = pygame.Rect(self.WIDTH // 2 - 100, self.HEIGHT // 2, 200, 36)
        active = False
        font = pygame.font.SysFont("Arial", 28)
        small_font = pygame.font.SysFont("Arial", 18)
        color_inactive = "lightskyblue"
        color_active = "dodgerblue"
        input_color = color_inactive

        while input_active:
            active, input_color, player_name, input_active = (
                self.handle_main_menu_events(
                    input_box,
                    active,
                    color_inactive,
                    color_active,
                    player_name,
                    input_active,
                )
            )
            self.draw_main_menu(font, small_font, input_box, input_color, player_name)
            pygame.display.flip()
            self.fps_clock.tick(self.FPS)

        player_name = player_name.strip()
        self.add_player(Player(player_name, "darkgreen"))

    def draw_main_menu(
        self,
        font: pygame.font.Font,
        small_font: pygame.font.Font,
        input_box: pygame.rect.Rect,
        input_color: str,
        player_name: str,
    ):
        """
        Draw main menu elements on the screen.
        """
        self.screen.fill(self.SCREEN_COLOR)
        # Title
        title_text = font.render(self.TITLE, True, "white")
        self.screen.blit(
            title_text,
            (self.WIDTH // 2 - title_text.get_width() // 2, self.HEIGHT // 2 - 100),
        )
        # Info
        info_text = small_font.render("Enter Your Name", True, "yellow")
        self.screen.blit(
            info_text,
            (self.WIDTH // 2 - info_text.get_width() // 2, self.HEIGHT // 2 - 40),
        )
        # Input box
        txt_surface = font.render(player_name, True, "black")
        width = max(200, txt_surface.get_width() + 20)
        input_box.w = width
        pygame.draw.rect(self.screen, input_color, input_box, 2)
        self.screen.blit(txt_surface, (input_box.x + 10, input_box.y + 5))
        # Start button
        if self.valid_player_name(player_name):
            start_text = small_font.render("Press Enter To Start", True, "green")
            self.screen.blit(
                start_text,
                (self.WIDTH // 2 - start_text.get_width() // 2, self.HEIGHT // 2 + 50),
            )

    def handle_main_menu_events(
        self,
        input_box,
        active: bool,
        color_inactive: str,
        color_active: str,
        player_name: str,
        input_active: bool,
    ) -> tuple[bool, str, str, bool]:
        """
        Handle main menu events and return updated values

        Args:
            input_box (pygame.rect.Rect): The input box rectangle.
            active (bool): Whether the input box is active.
            color_inactive (str): The color of the input box when inactive.
            color_active (str): The color of the input box when active.
            player_name (str): The player's name.
            input_active (bool): Whether the input box is active.

        Returns:
                tuple[bool, str, str, bool]: Updated values for active, input_color, player_name, and input_active.
        """
        input_color = color_active if active else color_inactive
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = True
                else:
                    active = False
                input_color = color_active if active else color_inactive
            elif event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        if self.valid_player_name(player_name):
                            input_active = False
                    elif event.key == pygame.K_BACKSPACE:
                        player_name = player_name[:-1]
                    else:
                        if len(player_name) < 16 and (
                            event.unicode.isalnum() or event.unicode == "_"
                        ):
                            player_name += event.unicode
        return (active, input_color, player_name, input_active)

    def valid_player_name(self, name: str) -> bool:
        """
        Check if the player name is valid.

        Args:
            name (str): The player's name.
        Returns:
                bool: True if the player name is valid, False otherwise.
        """
        return name.strip() != ""

    def handle_move(self) -> None:
        """
        Handle user keyboard input for movement and update player position accordingly.
        """
        keys = pygame.key.get_pressed()
        if self.player is not None:
            dx = dy = 0
            if keys[pygame.K_UP]:
                dy -= self.SPEED
            if keys[pygame.K_DOWN]:
                dy += self.SPEED
            if keys[pygame.K_LEFT]:
                dx -= self.SPEED
            if keys[pygame.K_RIGHT]:
                dx += self.SPEED
            if dx != 0 or dy != 0:
                self.move_player(self.player, dx, dy)

    def handle_quit(self) -> None:
        """
        Handle quit events (window close or ESC key).
        """
        for events in pygame.event.get():
            if events.type == pygame.QUIT or (
                events.type == pygame.KEYDOWN and events.key == pygame.K_ESCAPE
            ):
                self.running = False

    def add_player(self, player: Player) -> None:
        """
        Add a new player to the game and notify the server if it's the main player.

        Args:
            player (Player): The player object to add.
        """
        # Make player in center of screen
        player.x = self.WIDTH // 2
        player.y = self.HEIGHT // 2

        if not self.players:
            self.player = player
            self.players.append(player)
            self.network.send(f"JOIN,{player.name}")
        else:
            if player not in self.players:
                self.players.insert(0, player)

    def move_player(self, player: Player, dx: int, dy: int) -> None:
        """
        Move the player within the game border and send position updates to the server.

        Args:
            player (Player): The player to move.
            dx (int): Change in X position.
            dy (int): Change in Y position.
        """
        new_x = max(
            self.PLAYER_RADIUS, min(self.WIDTH - self.PLAYER_RADIUS, player.x + dx)
        )
        new_y = max(
            self.PLAYER_RADIUS, min(self.HEIGHT - self.PLAYER_RADIUS, player.y + dy)
        )

        moved: bool = (new_x != player.x) or (new_y != player.y)
        player.move(new_x - player.x, new_y - player.y)

        if moved:
            self.send_position()
            if self.move_sound:
                self.move_sound.stop()
                self.move_sound.play()

    def draw_text(
        self,
        text: str,
        x: int,
        y: int,
        color: str = "white",
        size: int = 16,
        name: str = "Arial",
    ) -> None:
        """
        Draw text on the game screen.

        Args:
            text (str): Text to display.
            x (int): X position.
            y (int): Y position.
            color (str): Text color.
            size (int): Font size.
            name (str): Font name.
        """
        text_font = pygame.font.SysFont(name, size)
        img = text_font.render(text, True, color)
        rect = img.get_rect(center=(x, y))
        self.screen.blit(img, rect)

    def draw_screen(self) -> None:
        """
        Render all players and UI elements on the screen.
        """
        self.screen.fill(self.SCREEN_COLOR)

        for player in self.players:
            if self.player is not None and player.name == self.player.name:
                continue
            self.draw_player(self.screen, player)
            self.draw_text(player.name, player.x, player.y - self.PLAYER_RADIUS - 15)

        if self.player is not None:
            self.draw_player(self.screen, self.player)
            self.draw_text(
                self.player.name,
                self.player.x,
                self.player.y - self.PLAYER_RADIUS - 15,
                color="green",
            )
        # Update screen rendering
        pygame.display.flip()
        self.fps_clock.tick(self.FPS)

    def draw_player(self, screen: pygame.Surface, player: Player) -> None:
        """
        Draw a player as a circle on the screen.

        Args:
            screen (pygame.Surface): The surface to draw on.
            player (Player): The player object.
        """
        pygame.draw.circle(screen, player.color, player.position(), self.PLAYER_RADIUS)

    def send_position(self) -> None:
        """
        Send the current player's position to the server.
        """
        if self.player is not None:
            data = f"MOVE,{self.player.name},{self.player.x},{self.player.y}"
            self.network.send(data)

    def handle_joined(self, data: str) -> None:
        """
        Handle a 'JOINED' message from the server.

        Args:
            data (str): The server message.
        """
        name = data.split(",", 1)[1]
        print(f"{name} joined the game!")

    def handle_left(self, data: str) -> None:
        """
        Handle a 'LEFT' message from the server.

        Args:
            data (str): The server message.
        """
        name = data.split(",", 1)[1]
        print(f"{name} left the game.")
        self.players = [player for player in self.players if player.name != name]

    def _extract_all_data(self, data: str) -> list[str]:
        """
        Extract player data from an 'UPDATE' message.

        Args:
            data (str): The server message.

        Returns:
            list[str]: List of player data strings.
        """
        return [
            players_data.strip()
            for players_data in data[7:].split(";")
            if players_data.strip()
        ]

    def _update_or_add_player(self, name: str, x: int, y: int) -> None:
        """
        Update an existing player's position or add a new player.

        Args:
            name (str): Player's name.
            x (int): Player's X position.
            y (int): Player's Y position.
        """
        player = next((player for player in self.players if player.name == name), None)
        if player:
            player.x = x
            player.y = y
        else:
            self.add_player(Player(name, x=x, y=y))

    def _process_player_data(self, player_data: str) -> None:
        """
        Parse and process individual player data from the server.

        Args:
            player_data (str): Formatted player data string.
        """
        try:
            name, x, y = self._parse_player_data(player_data)
        except ValueError:
            print(f"Malformed player data: {player_data}")
            return None

        if not (self.player and name == self.player.name):
            self._update_or_add_player(name, x, y)

    def _parse_player_data(self, player_data: str) -> tuple[str, int, int]:
        """
        Parse player data string into name and coordinates.

        Args:
            player_data (str): Formatted player data string.

        Returns:
                tuple[str, int, int]: (name, x, y)
        """
        name, x_str, y_str = player_data.split(",")
        x, y = int(x_str), int(y_str)
        return (name, x, y)

    def handle_update(self, data: str) -> None:
        """
        Handle an 'UPDATE' message from the server.

        Args:
            data (str): The server message.
        """
        all_data = self._extract_all_data(data)
        for player_data in all_data:
            self._process_player_data(player_data)

    def update_players(self) -> None:
        """
        Receive and process messages from the server.
        """
        data: str = self.network.recv()
        if data:
            if data.startswith("JOINED,"):
                self.handle_joined(data)
            elif data.startswith("LEFT,"):
                self.handle_left(data)
            elif data.startswith("UPDATE;"):
                self.handle_update(data)

    def start(self) -> None:
        """
        Main game loop: handle events, update state, and render.
        """
        while self.running:
            self.draw_screen()
            self.handle_quit()
            self.handle_move()
            self.update_players()
        pygame.quit()


if __name__ == "__main__":
    Game().start()
