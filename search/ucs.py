from __future__ import annotations

from heapq import heappop, heappush
from time import perf_counter
from typing import Set

from game.board import Board
from search.common import SearchResult, reconstruct
from utils import Pos


def ucs(board: Board, start: Pos, goals: Set[Pos], blocked: Set[Pos] | None = None) -> SearchResult:
    t0 = perf_counter()
    blocked = blocked or set()
    pq: list[tuple[int, Pos]] = [(0, start)]
    came_from: dict[Pos, Pos | None] = {start: None}
    cost_so_far: dict[Pos, int] = {start: 0}
    expanded = 0

    while pq:
        cost, node = heappop(pq)
        expanded += 1
        if node in goals:
            return SearchResult(path=reconstruct(came_from, node), expanded=expanded, runtime_ms=(perf_counter() - t0) * 1000.0, found=True)
        for nxt in board.legal_neighbors(node, blocked):
            new_cost = cost_so_far[node] + 1
            if nxt not in cost_so_far or new_cost < cost_so_far[nxt]:
                cost_so_far[nxt] = new_cost
                came_from[nxt] = node
                heappush(pq, (new_cost, nxt))

    return SearchResult(path=[], expanded=expanded, runtime_ms=(perf_counter() - t0) * 1000.0, found=False)
