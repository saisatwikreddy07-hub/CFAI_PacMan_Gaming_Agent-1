from __future__ import annotations

from dataclasses import dataclass, field
import time
from typing import List, Tuple

Pos = Tuple[int, int]


def manhattan(a: Pos, b: Pos) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def neighbors4(pos: Pos):
    r, c = pos
    return [(r - 1, c), (r, c - 1), (r + 1, c), (r, c + 1)]


@dataclass
class TraceLogger:
    max_lines: int = 8
    lines: List[str] = field(default_factory=list)

    def log(self, msg: str) -> None:
        ts = time.strftime('%H:%M:%S')
        self.lines.append(f'[{ts}] {msg}')
        self.lines = self.lines[-self.max_lines:]

    def clear(self) -> None:
        self.lines.clear()


@dataclass
class StepMetrics:
    expanded: int = 0
    runtime_ms: float = 0.0
    path_len: int = 0
    found: bool = False
