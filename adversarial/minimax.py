from __future__ import annotations

from dataclasses import dataclass
from math import inf
from typing import List, Sequence, Set, Tuple

from game.board import Board
from utils import Pos, manhattan


@dataclass
class MiniMaxResult:
    best_move: Pos
    score: float
    explored: int


def evaluate(board: Board, pacman_pos: Pos, ghost_positions: Sequence[Pos], food: Set[Pos], powered: bool) -> float:
    if not food:
        return 10000.0

    food_dist = min(manhattan(pacman_pos, f) for f in food)
    ghost_dist = min((manhattan(pacman_pos, g) for g in ghost_positions), default=999)

    if not powered and ghost_dist == 0:
        return -10000.0

    score = -5.0 * food_dist + 6.0 * ghost_dist

    if pacman_pos in food:
        score += 35.0

    if powered:
        score += 15.0
        if ghost_dist <= 2:
            score += 40.0

    if not powered and ghost_dist <= 1:
        score -= 60.0

    return score


def choose_best_move(
    board: Board,
    pacman_pos: Pos,
    ghost_positions: List[Pos],
    food: Set[Pos],
    powered: bool,
    depth: int = 2
) -> MiniMaxResult:
    explored = 0
    legal_moves = board.legal_neighbors(pacman_pos)
    if not legal_moves:
        return MiniMaxResult(best_move=pacman_pos, score=-inf, explored=explored)

    ghosts0: Tuple[Pos, ...] = tuple(ghost_positions)

    def ghost_turn(p_pos: Pos, ghosts: Tuple[Pos, ...], ghost_index: int, ply: int, alpha: float, beta: float) -> float:
        nonlocal explored
        explored += 1

        if not food:
            return 10000.0

        if ply <= 0:
            return evaluate(board, p_pos, ghosts, food, powered)

        if not powered and p_pos in ghosts:
            return -10000.0
        if powered and p_pos in ghosts:
            return 10000.0

        if ghost_index >= len(ghosts):
            return pacman_turn(p_pos, ghosts, ply - 1, alpha, beta)

        g_pos = ghosts[ghost_index]
        legal = board.legal_neighbors(g_pos)
        if not legal:
            return ghost_turn(p_pos, ghosts, ghost_index + 1, ply, alpha, beta)

        best = inf
        for mv in legal:
            new_ghosts = list(ghosts)
            new_ghosts[ghost_index] = mv
            new_ghosts_t = tuple(new_ghosts)

            if not powered and mv == p_pos:
                value = -10000.0
            elif powered and mv == p_pos:
                value = 10000.0
            else:
                value = ghost_turn(p_pos, new_ghosts_t, ghost_index + 1, ply, alpha, beta)

            best = min(best, value)
            beta = min(beta, best)
            if beta <= alpha:
                break

        return best

    def pacman_turn(p_pos: Pos, ghosts: Tuple[Pos, ...], ply: int, alpha: float, beta: float) -> float:
        nonlocal explored
        explored += 1

        if not food:
            return 10000.0

        if ply <= 0:
            return evaluate(board, p_pos, ghosts, food, powered)

        if not powered and p_pos in ghosts:
            return -10000.0
        if powered and p_pos in ghosts:
            return 10000.0

        legal = board.legal_neighbors(p_pos)
        if not legal:
            return evaluate(board, p_pos, ghosts, food, powered)

        best = -inf
        for mv in legal:
            if not powered and mv in ghosts:
                value = -10000.0
            elif powered and mv in ghosts:
                value = 10000.0
            else:
                value = ghost_turn(mv, ghosts, 0, ply, alpha, beta)

            best = max(best, value)
            alpha = max(alpha, best)
            if beta <= alpha:
                break

        return best

    best_move = legal_moves[0]
    best_score = -inf
    alpha = -inf
    beta = inf

    for move in legal_moves:
        if not powered and move in ghosts0:
            score = -10000.0
        elif powered and move in ghosts0:
            score = 10000.0
        else:
            score = ghost_turn(move, ghosts0, 0, depth, alpha, beta)

        if score > best_score:
            best_score = score
            best_move = move
        alpha = max(alpha, best_score)

    return MiniMaxResult(best_move=best_move, score=best_score, explored=explored)
