from __future__ import annotations

from heapq import heappop, heappush
from time import perf_counter
from typing import Set

from game.board import Board
from search.common import SearchResult, min_heuristic, reconstruct
from utils import Pos


def astar(board: Board, start: Pos, goals: Set[Pos], blocked: Set[Pos] | None = None) -> SearchResult:
    t0 = perf_counter()
    blocked = blocked or set()
    pq: list[tuple[int, int, Pos]] = [(min_heuristic(start, goals), 0, start)]
    came_from: dict[Pos, Pos | None] = {start: None}
    gscore: dict[Pos, int] = {start: 0}
    expanded = 0

    while pq:
        _, g, node = heappop(pq)
        expanded += 1
        if node in goals:
            return SearchResult(path=reconstruct(came_from, node), expanded=expanded, runtime_ms=(perf_counter() - t0) * 1000.0, found=True)
        for nxt in board.legal_neighbors(node, blocked):
            tentative = gscore[node] + 1
            if nxt not in gscore or tentative < gscore[nxt]:
                gscore[nxt] = tentative
                came_from[nxt] = node
                heappush(pq, (tentative + min_heuristic(nxt, goals), tentative, nxt))

    return SearchResult(path=[], expanded=expanded, runtime_ms=(perf_counter() - t0) * 1000.0, found=False)
