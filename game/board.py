from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Set, Tuple

from config import GRID_COLS, GRID_ROWS
from utils import Pos, neighbors4


@dataclass
class Board:
    rows: int = GRID_ROWS
    cols: int = GRID_COLS
    walls: Set[Pos] = field(default_factory=set)
    pellets: Set[Pos] = field(default_factory=set)
    power_pellets: Set[Pos] = field(default_factory=set)
    pacman_start: Pos = (7, 9)
    ghost_starts: List[Pos] = field(default_factory=lambda: [(1, 1), (1, 17), (13, 1), (13, 17)])

    @classmethod
    def create_default(cls) -> 'Board':
        board = cls()
        board._generate_layout()
        return board

    def _generate_layout(self) -> None:
        self.walls.clear()
        self.pellets.clear()
        self.power_pellets.clear()

        for r in range(self.rows):
            for c in range(self.cols):
                if r in {0, self.rows - 1} or c in {0, self.cols - 1}:
                    self.walls.add((r, c))

        for c in range(2, self.cols - 2):
            if c not in {8, 10}:
                self.walls.add((4, c))
                self.walls.add((10, c))
        for r in range(2, self.rows - 2):
            if r not in {5, 9}:
                self.walls.add((r, 4))
                self.walls.add((r, 14))

        for c in range(6, 13):
            if c not in {9}:
                self.walls.add((7, c))
        for r in range(5, 10):
            if r not in {7}:
                self.walls.add((r, 9))

        for pos in [(4, 8), (4, 10), (10, 8), (10, 10), (5, 4), (9, 4), (5, 14), (9, 14), (7, 6), (7, 12), (6, 9), (8, 9)]:
            self.walls.discard(pos)

        self.pacman_start = (7, 9)
        self.ghost_starts = [(1, 1), (1, 17), (13, 1), (13, 17)]
        self.power_pellets = {(1, 1), (1, 17), (13, 1), (13, 17)}

        for r in range(self.rows):
            for c in range(self.cols):
                pos = (r, c)
                if pos not in self.walls and pos not in self.power_pellets:
                    self.pellets.add(pos)

        self.pellets.discard(self.pacman_start)
        for g in self.ghost_starts:
            self.pellets.discard(g)

    def in_bounds(self, pos: Pos) -> bool:
        r, c = pos
        return 0 <= r < self.rows and 0 <= c < self.cols

    def is_wall(self, pos: Pos) -> bool:
        return pos in self.walls

    def legal_neighbors(self, pos: Pos, blocked: Set[Pos] | None = None) -> List[Pos]:
        blocked = blocked or set()
        out: List[Pos] = []
        for n in neighbors4(pos):
            if self.in_bounds(n) and n not in self.walls and n not in blocked:
                out.append(n)
        return out

    def remaining_food(self) -> int:
        return len(self.pellets) + len(self.power_pellets)

    def all_food(self) -> Set[Pos]:
        return set(self.pellets) | set(self.power_pellets)

    def consume(self, pos: Pos) -> str | None:
        if pos in self.power_pellets:
            self.power_pellets.remove(pos)
            return 'power'
        if pos in self.pellets:
            self.pellets.remove(pos)
            return 'pellet'
        return None
