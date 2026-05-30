from __future__ import annotations

import random
from typing import Dict, List

from game.board import Board
from utils import Pos, manhattan


def transition_distribution(board: Board, ghost_pos: Pos, pacman_pos: Pos, reverse_bias: float = 0.15) -> Dict[Pos, float]:
    neighbors = board.legal_neighbors(ghost_pos)
    if not neighbors:
        return {ghost_pos: 1.0}

    weights = []
    current_dist = manhattan(ghost_pos, pacman_pos)

    for n in neighbors:
        dist = manhattan(n, pacman_pos)
        chase = 1.0 / (dist + 1)
        wander = 0.25
        reverse_penalty = 0.8 if dist > current_dist else 1.0
        weight = (chase + wander) * reverse_penalty
        weights.append((n, weight))

    total = sum(w for _, w in weights)
    if total <= 0:
        return {ghost_pos: 1.0}

    return {p: w / total for p, w in weights}


def expected_position(dist: Dict[Pos, float]) -> Pos:
    if not dist:
        return (0, 0)
    return max(dist.items(), key=lambda item: item[1])[0]


def sample_next(dist: Dict[Pos, float]) -> Pos:
    roll = random.random()
    acc = 0.0
    last = next(iter(dist))
    for pos, prob in dist.items():
        last = pos
        acc += prob
        if roll <= acc:
            return pos
    return last


def predict_ghosts(board: Board, ghost_positions: List[Pos], pacman_pos: Pos) -> dict[Pos, float]:
    predicted: dict[Pos, float] = {}
    if not ghost_positions:
        return predicted

    weight_per_ghost = 1.0 / len(ghost_positions)
    for ghost in ghost_positions:
        dist = transition_distribution(board, ghost, pacman_pos)
        for pos, prob in dist.items():
            predicted[pos] = predicted.get(pos, 0.0) + prob * weight_per_ghost

    return predicted


def move_ghost(board: Board, ghost_pos: Pos, pacman_pos: Pos) -> Pos:
    dist = transition_distribution(board, ghost_pos, pacman_pos)
    return sample_next(dist)
