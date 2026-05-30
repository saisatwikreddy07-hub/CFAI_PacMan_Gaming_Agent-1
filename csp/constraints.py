from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Set

from game.board import Board
from utils import Pos, manhattan


@dataclass
class CSPReport:
    safe_moves: List[Pos]
    blocked_moves: Dict[Pos, str] = field(default_factory=dict)
    chosen_goal: Pos | None = None
    explanation: str = ''


def filter_safe_moves(board: Board, pacman_pos: Pos, ghost_cells: Set[Pos], powered: bool) -> CSPReport:
    legal = board.legal_neighbors(pacman_pos)
    safe: List[Pos] = []
    blocked: Dict[Pos, str] = {}

    for move in legal:
        if move in ghost_cells and not powered:
            blocked[move] = 'predicted ghost collision'
            continue

        if not powered:
            dist = min((manhattan(move, g) for g in ghost_cells), default=999)
            if dist <= 1:
                blocked[move] = 'unsafe proximity to ghost'
                continue

        safe.append(move)

    explanation = 'all legal moves are safe' if safe else 'no safe move found'
    return CSPReport(safe_moves=safe, blocked_moves=blocked, explanation=explanation)


def choose_mrv_food(board: Board, foods: Set[Pos], safe_moves: List[Pos]) -> Pos | None:
    if not foods:
        return None

    if not safe_moves:
        return min(foods, key=lambda food: (food[0], food[1]))

    scored = []
    for food in foods:
        domain_size = sum(1 for m in safe_moves if manhattan(m, food) <= 4)
        min_safe_dist = min(manhattan(m, food) for m in safe_moves)
        scored.append((domain_size, min_safe_dist, food[0], food[1], food))

    scored.sort(key=lambda x: (x[0], x[1], x[2], x[3]))
    return scored[0][4]


def forward_checking(board: Board, pacman_pos: Pos, candidate: Pos, ghost_cells: Set[Pos], powered: bool) -> tuple[bool, str]:
    if candidate in board.walls:
        return False, 'wall'
    if candidate in ghost_cells and not powered:
        return False, 'ghost occupied'
    if not powered and min((manhattan(candidate, g) for g in ghost_cells), default=999) <= 1:
        return False, 'future collision risk'
    return True, 'ok'
