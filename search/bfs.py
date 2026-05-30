from __future__ import annotations

from collections import deque
from time import perf_counter
from typing import Set

from game.board import Board
from search.common import SearchResult, reconstruct
from utils import Pos


def bfs(board: Board, start: Pos, goals: Set[Pos], blocked: Set[Pos] | None = None) -> SearchResult:
    t0 = perf_counter()
    blocked = blocked or set()
    q = deque([start])
    came_from: dict[Pos, Pos | None] = {start: None}
    expanded = 0

    while q:
        node = q.popleft()
        expanded += 1
        if node in goals:
            path = reconstruct(came_from, node)
            return SearchResult(path=path, expanded=expanded, runtime_ms=(perf_counter() - t0) * 1000.0, found=True)
        for nxt in board.legal_neighbors(node, blocked):
            if nxt not in came_from:
                came_from[nxt] = node
                q.append(nxt)

    return SearchResult(path=[], expanded=expanded, runtime_ms=(perf_counter() - t0) * 1000.0, found=False)
