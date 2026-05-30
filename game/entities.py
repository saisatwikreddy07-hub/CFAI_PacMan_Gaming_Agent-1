from __future__ import annotations

from dataclasses import dataclass
from utils import Pos


@dataclass
class Pacman:
    pos: Pos
    direction: Pos = (0, 0)
    lives: int = 3
    score: int = 0
    powered_timer: int = 0
    start_pos: Pos = (0, 0)

    def reset(self) -> None:
        self.pos = self.start_pos
        self.direction = (0, 0)
        self.powered_timer = 0


@dataclass
class Ghost:
    name: str
    pos: Pos
    start_pos: Pos
    color: tuple[int, int, int]
    direction: Pos = (0, 0)
    frightened_timer: int = 0

    def reset(self) -> None:
        self.pos = self.start_pos
        self.direction = (0, 0)
        self.frightened_timer = 0
