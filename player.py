import attr
from typing import Any


@attr.s
class Player:
    """
    Represents a player in the game.

    Attributes:
        name (str): The player's name.
        color (Any): The player's color (can be a string, tuple, or pygame.Color).
        health (int): The player's health points.
        x (int): The player's x-coordinate.
        y (int): The player's y-coordinate.
    """

    name: str = attr.ib(default="Player")
    color: Any = attr.ib(default="red")
    health: int = attr.ib(default=100)
    x: int = attr.ib(default=0)
    y: int = attr.ib(default=0)

    def move(self, dx: int, dy: int) -> None:
        """
        Move the player by the specified delta values.

        Args:
            dx (int): Change in the x-coordinate.
            dy (int): Change in the y-coordinate.
        """
        self.x += dx
        self.y += dy

    def position(self) -> tuple[int, int]:
        """
        Get the current position of the player.

        Returns:
            tuple[int, int]: The (x, y) position of the player.
        """
        return (self.x, self.y)
