from __future__ import annotations

from time import perf_counter
from typing import Set

from game.board import Board
from search.common import SearchResult
from utils import Pos


def dfs(board: Board, start: Pos, goals: Set[Pos], blocked: Set[Pos] | None = None) -> SearchResult:
    t0 = perf_counter()
    blocked = blocked or set()
    visited: set[Pos] = set()
    path: list[Pos] = []
    expanded = 0

    def visit(node: Pos) -> bool:
        nonlocal expanded
        expanded += 1
        visited.add(node)
        path.append(node)
        if node in goals:
            return True
        for nxt in board.legal_neighbors(node, blocked):
            if nxt not in visited:
                if visit(nxt):
                    return True
        path.pop()
        return False

    found = visit(start)
    return SearchResult(path=path[:] if found else [], expanded=expanded, runtime_ms=(perf_counter() - t0) * 1000.0, found=found)
