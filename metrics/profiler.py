from __future__ import annotations

from typing import List, Set

from game.board import Board
from search.astar import astar
from search.bfs import bfs
from search.dfs import dfs
from search.ucs import ucs
from utils import Pos


def benchmark_searches(board: Board, start: Pos, goals: Set[Pos], blocked: Set[Pos] | None = None) -> List[str]:
    results = []
    for name, fn in [('BFS', bfs), ('DFS', dfs), ('UCS', ucs), ('A*', astar)]:
        res = fn(board, start, goals, blocked)
        results.append(f'{name}: found={res.found}, path={res.path_len}, expanded={res.expanded}, time={res.runtime_ms:.2f} ms')
    return results
