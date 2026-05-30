from __future__ import annotations

from dataclasses import dataclass
from typing import List, Set

from utils import Pos, manhattan


@dataclass
class SearchResult:
    path: List[Pos]
    expanded: int
    runtime_ms: float
    found: bool

    @property
    def path_len(self) -> int:
        return max(0, len(self.path) - 1)


def reconstruct(came_from: dict[Pos, Pos | None], goal: Pos) -> List[Pos]:
    path = [goal]
    cur = goal
    while came_from[cur] is not None:
        cur = came_from[cur]
        path.append(cur)
    path.reverse()
    return path


def min_heuristic(pos: Pos, goals: Set[Pos]) -> int:
    if not goals:
        return 0
    return min(manhattan(pos, g) for g in goals)
