from __future__ import annotations

from math import inf
from typing import List, Sequence, Set, Tuple

from game.board import Board
from utils import Pos, manhattan


def alphabeta_move(board: Board, pacman_pos: Pos, ghost_positions: List[Pos], food: Set[Pos], powered: bool, depth: int = 3) -> Pos:
    if not board.legal_neighbors(pacman_pos):
        return pacman_pos

    ghosts0: Tuple[Pos, ...] = tuple(ghost_positions)

    def eval_state(p: Pos, ghosts: Sequence[Pos]) -> float:
        if not food:
            return 10000.0

        food_dist = min(manhattan(p, f) for f in food)
        ghost_dist = min((manhattan(p, g) for g in ghosts), default=999)

        if not powered and ghost_dist == 0:
            return -10000.0

        score = -5.0 * food_dist + 6.0 * ghost_dist

        if p in food:
            score += 35.0

        if powered:
            score += 15.0
            if ghost_dist <= 2:
                score += 40.0

        if not powered and ghost_dist <= 1:
            score -= 60.0

        return score

    def ghost_turn(p: Pos, ghosts: Tuple[Pos, ...], ghost_index: int, ply: int, alpha: float, beta: float) -> float:
        if not food:
            return 10000.0

        if ply <= 0:
            return eval_state(p, ghosts)

        if not powered and p in ghosts:
            return -10000.0
        if powered and p in ghosts:
            return 10000.0

        if ghost_index >= len(ghosts):
            return pacman_turn(p, ghosts, ply - 1, alpha, beta)

        g_pos = ghosts[ghost_index]
        legal = board.legal_neighbors(g_pos)
        if not legal:
            return ghost_turn(p, ghosts, ghost_index + 1, ply, alpha, beta)

        best = inf
        for mv in legal:
            new_ghosts = list(ghosts)
            new_ghosts[ghost_index] = mv
            new_ghosts_t = tuple(new_ghosts)

            if not powered and mv == p:
                value = -10000.0
            elif powered and mv == p:
                value = 10000.0
            else:
                value = ghost_turn(p, new_ghosts_t, ghost_index + 1, ply, alpha, beta)

            best = min(best, value)
            beta = min(beta, best)
            if beta <= alpha:
                break

        return best

    def pacman_turn(p: Pos, ghosts: Tuple[Pos, ...], ply: int, alpha: float, beta: float) -> float:
        if not food:
            return 10000.0

        if ply <= 0:
            return eval_state(p, ghosts)

        if not powered and p in ghosts:
            return -10000.0
        if powered and p in ghosts:
            return 10000.0

        legal = board.legal_neighbors(p)
        if not legal:
            return eval_state(p, ghosts)

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

    legal_moves = board.legal_neighbors(pacman_pos)
    if not legal_moves:
        return pacman_pos

    best_move = legal_moves[0]
    best_score = -inf
    alpha = -inf
    beta = inf

    for mv in legal_moves:
        if not powered and mv in ghosts0:
            score = -10000.0
        elif powered and mv in ghosts0:
            score = 10000.0
        else:
            score = ghost_turn(mv, ghosts0, 0, depth, alpha, beta)

        if score > best_score:
            best_score = score
            best_move = mv

        alpha = max(alpha, best_score)

    return best_move
