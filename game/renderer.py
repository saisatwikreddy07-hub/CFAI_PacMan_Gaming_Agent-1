from __future__ import annotations

import math
import pygame

from config import (
    BLACK,
    BLUE,
    CELL_SIZE,
    DARK_BLUE,
    GRAY,
    GREEN,
    HUD_HEIGHT,
    LIGHT_GRAY,
    PURPLE,
    RED,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    WHITE,
    YELLOW,
)
from game.game_state import GameState
from utils import Pos


class Renderer:
    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen
        self.font = pygame.font.SysFont("arial", 18)
        self.font_small = pygame.font.SysFont("arial", 14)
        self.font_big = pygame.font.SysFont("arial", 26, bold=True)

    def draw_cell_center(self, pos: Pos) -> tuple[int, int]:
        r, c = pos
        x = c * CELL_SIZE + CELL_SIZE // 2
        y = r * CELL_SIZE + CELL_SIZE // 2
        return x, y

    def draw_pacman(self, pos: Pos, direction: tuple[int, int]) -> None:
        px, py = self.draw_cell_center(pos)

        radius = CELL_SIZE // 2 - 3

        pygame.draw.circle(
            self.screen,
            YELLOW,
            (px, py),
            radius,
        )

        mouth = 12 + abs(
            math.sin(
                pygame.time.get_ticks() * 0.01
            )
        ) * 10

        if direction == (-1, 0):
            angle = 90
        elif direction == (1, 0):
            angle = 270
        elif direction == (0, -1):
            angle = 180
        else:
            angle = 0

        a1 = math.radians(angle - mouth)
        a2 = math.radians(angle + mouth)

        pygame.draw.polygon(
            self.screen,
            BLACK,
            [
                (px, py),
                (
                    px + radius * math.cos(a1),
                    py - radius * math.sin(a1),
                ),
                (
                    px + radius * math.cos(a2),
                    py - radius * math.sin(a2),
                ),
            ],
        )

        if angle == 0:
            eye_x = px
            eye_y = py - radius // 2
        elif angle == 180:
            eye_x = px
            eye_y = py - radius // 2
        elif angle == 90:
            eye_x = px + radius // 3
            eye_y = py
        else:
            eye_x = px + radius // 3
            eye_y = py

        pygame.draw.circle(
            self.screen,
            BLACK,
            (int(eye_x), int(eye_y)),
            2,
        )

    def draw_ghost(self, pos: Pos, color: tuple[int, int, int]) -> None:
        gx, gy = self.draw_cell_center(pos)

        radius = CELL_SIZE // 2 - 4

        pygame.draw.circle(
            self.screen,
            color,
            (gx, gy - 2),
            radius,
        )

        body = [
            (gx - radius, gy),
            (gx + radius, gy),
            (gx + radius, gy + radius),
            (gx + radius // 2, gy + radius - 4),
            (gx, gy + radius),
            (gx - radius // 2, gy + radius - 4),
            (gx - radius, gy + radius),
        ]

        pygame.draw.polygon(
            self.screen,
            color,
            body,
        )

        pygame.draw.circle(
            self.screen,
            WHITE,
            (gx - 6, gy - 4),
            4,
        )

        pygame.draw.circle(
            self.screen,
            WHITE,
            (gx + 6, gy - 4),
            4,
        )

        pygame.draw.circle(
            self.screen,
            BLACK,
            (gx - 6, gy - 4),
            2,
        )

        pygame.draw.circle(
            self.screen,
            BLACK,
            (gx + 6, gy - 4),
            2,
        )

    def draw(self, state: GameState) -> None:
        self.screen.fill(BLACK)

        board = state.board

        for r in range(board.rows):
            for c in range(board.cols):
                rect = pygame.Rect(
                    c * CELL_SIZE,
                    r * CELL_SIZE,
                    CELL_SIZE,
                    CELL_SIZE,
                )

                if (r, c) in board.walls:
                    pygame.draw.rect(
                        self.screen,
                        BLUE,
                        rect,
                    )
                else:
                    pygame.draw.rect(
                        self.screen,
                        DARK_BLUE,
                        rect,
                        1,
                    )

        for p in board.pellets:
            x, y = self.draw_cell_center(p)
            pygame.draw.circle(
                self.screen,
                WHITE,
                (x, y),
                3,
            )

        for p in board.power_pellets:
            x, y = self.draw_cell_center(p)
            pygame.draw.circle(
                self.screen,
                YELLOW,
                (x, y),
                7,
            )

        self.draw_pacman(
            state.pacman.pos,
            state.pacman.direction,
        )

        for ghost in state.ghosts:
            color = (
                (180, 180, 255)
                if ghost.frightened_timer > 0
                or state.pacman.powered_timer > 0
                else ghost.color
            )

            self.draw_ghost(
                ghost.pos,
                color,
            )

        hud_y = board.rows * CELL_SIZE

        pygame.draw.rect(
            self.screen,
            LIGHT_GRAY,
            pygame.Rect(
                0,
                hud_y,
                SCREEN_WIDTH,
                HUD_HEIGHT,
            ),
        )

        pygame.draw.line(
            self.screen,
            GRAY,
            (0, hud_y),
            (SCREEN_WIDTH, hud_y),
            2,
        )

        lines = [
            f"Algorithm: {state.algorithm}",
            f"Score: {state.pacman.score}",
            f"Lives: {state.pacman.lives}",
            f"Food left: {board.remaining_food()}",
            f"Powered: {state.pacman.powered_timer}",
            f'Minimax: {"ON" if state.use_minimax else "OFF"}',
            f'Markov: {"ON" if state.use_markov else "OFF"}',
        ]

        for i, text in enumerate(lines):
            surf = self.font.render(text, True, BLACK)
            self.screen.blit(
                surf,
                (12 + (i % 4) * 220, hud_y + 8 + (i // 4) * 26),
            )

        if state.benchmark_text:
            for i, text in enumerate(state.benchmark_text[:4]):
                surf = self.font_small.render(text, True, PURPLE)
                self.screen.blit(surf, (12, hud_y + 56 + i * 16))

        if state.game_over:
            txt = "YOU WIN" if state.win else "GAME OVER"
            color = GREEN if state.win else RED

            overlay = self.font_big.render(
                txt,
                True,
                color,
            )

            rect = overlay.get_rect(
                center=(
                    SCREEN_WIDTH // 2,
                    SCREEN_HEIGHT // 2 - 20,
                )
            )

            self.screen.blit(
                overlay,
                rect,
            )

        help_text = self.font_small.render(
            "1 BFS  2 DFS  3 UCS  4 A*  5 Minimax  6 Markov  B Benchmark  SPACE Pause  R Reset",
            True,
            BLACK,
        )

        self.screen.blit(
            help_text,
            (12, hud_y + HUD_HEIGHT - 22),
        )