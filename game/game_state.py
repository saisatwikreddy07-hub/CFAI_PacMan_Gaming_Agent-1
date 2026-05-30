from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from config import GHOST_COLORS, GHOST_NAMES
from game.board import Board
from game.entities import Ghost, Pacman
from utils import TraceLogger


@dataclass
class GameState:
    board: Board
    pacman: Pacman
    ghosts: List[Ghost]
    algorithm: str = 'A*'
    use_minimax: bool = True
    use_markov: bool = True
    paused: bool = False
    game_over: bool = False
    win: bool = False
    benchmark_text: List[str] = field(default_factory=list)
    logger: TraceLogger = field(default_factory=TraceLogger)

    @classmethod
    def create(cls) -> 'GameState':
        board = Board.create_default()
        pacman = Pacman(pos=board.pacman_start, start_pos=board.pacman_start)
        ghosts = [Ghost(name=GHOST_NAMES[i], pos=pos, start_pos=pos, color=GHOST_COLORS[i]) for i, pos in enumerate(board.ghost_starts)]
        return cls(board=board, pacman=pacman, ghosts=ghosts)

    def reset(self) -> None:
        self.board = Board.create_default()
        self.pacman = Pacman(pos=self.board.pacman_start, start_pos=self.board.pacman_start)
        self.ghosts = [Ghost(name=GHOST_NAMES[i], pos=pos, start_pos=pos, color=GHOST_COLORS[i]) for i, pos in enumerate(self.board.ghost_starts)]
        self.algorithm = 'A*'
        self.use_minimax = True
        self.use_markov = True
        self.paused = False
        self.game_over = False
        self.win = False
        self.benchmark_text.clear()
        self.logger.clear()
