from __future__ import annotations

import sys
import pygame

from config import FPS, GAME_STEP_MS, SCREEN_HEIGHT, SCREEN_WIDTH
from game.game_state import GameState
from game.renderer import Renderer
from integration.decision_engine import DecisionEngine
from probability.markov import move_ghost
from utils import manhattan


def resolve_collisions(state: GameState) -> None:
    pac = state.pacman
    board = state.board

    eaten = board.consume(pac.pos)
    if eaten == 'pellet':
        pac.score += 10
        state.logger.log(f'Pellet collected at {pac.pos}')
    elif eaten == 'power':
        pac.score += 50
        pac.powered_timer = 25
        for g in state.ghosts:
            g.frightened_timer = 25
        state.logger.log(f'Power pellet collected at {pac.pos}')

    for ghost in state.ghosts:
        if ghost.pos == pac.pos:
            if pac.powered_timer > 0:
                pac.score += 200
                ghost.reset()
                state.logger.log(f'{ghost.name} eaten and reset')
            else:
                pac.lives -= 1
                state.logger.log(f'Pac-Man hit by {ghost.name}')
                if pac.lives <= 0:
                    state.game_over = True
                    state.win = False
                    return
                reset_positions(state)
                return

    if board.remaining_food() == 0:
        state.game_over = True
        state.win = True


def reset_positions(state: GameState) -> None:
    state.pacman.reset()
    for ghost in state.ghosts:
        ghost.reset()


def move_ghosts(state: GameState) -> None:
    board = state.board
    pac_pos = state.pacman.pos

    occupied = {g.pos for g in state.ghosts}

    for ghost in state.ghosts:
        occupied.discard(ghost.pos)

        if ghost.frightened_timer > 0:
            ghost.frightened_timer -= 1

        if state.use_markov:
            next_pos = move_ghost(board, ghost.pos, pac_pos)
        else:
            legal = board.legal_neighbors(ghost.pos)
            next_pos = min(
                legal,
                key=lambda p: manhattan(p, pac_pos)
            ) if legal else ghost.pos

        if next_pos in occupied:
            next_pos = ghost.pos

        ghost.pos = next_pos
        occupied.add(ghost.pos)

        if ghost.pos == pac_pos:
            if state.pacman.powered_timer > 0:
                state.pacman.score += 200
                ghost.reset()
            else:
                state.pacman.lives -= 1
                state.logger.log(
                    f'Pac-Man collided with {ghost.name}'
                )

                if state.pacman.lives <= 0:
                    state.game_over = True
                    state.win = False
                    return

                reset_positions(state)
                return


def main() -> None:
    pygame.init()
    pygame.display.set_caption('Pac-Man AI Agent')
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    state = GameState.create()
    renderer = Renderer(screen)
    engine = DecisionEngine()

    accumulator = 0
    running = True

    while running:
        dt = clock.tick(FPS)
        accumulator += dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    state.paused = not state.paused
                elif event.key == pygame.K_r:
                    state.reset()
                elif event.key == pygame.K_1:
                    state.algorithm = 'BFS'
                    state.logger.log('Switched to BFS')
                elif event.key == pygame.K_2:
                    state.algorithm = 'DFS'
                    state.logger.log('Switched to DFS')
                elif event.key == pygame.K_3:
                    state.algorithm = 'UCS'
                    state.logger.log('Switched to UCS')
                elif event.key == pygame.K_4:
                    state.algorithm = 'A*'
                    state.logger.log('Switched to A*')
                elif event.key == pygame.K_5:
                    state.use_minimax = not state.use_minimax
                    state.logger.log(f'Minimax set to {state.use_minimax}')
                elif event.key == pygame.K_6:
                    state.use_markov = not state.use_markov
                    state.logger.log(f'Markov set to {state.use_markov}')
                elif event.key == pygame.K_b:
                    state.benchmark_text = engine.benchmark(state)

        if not state.paused and not state.game_over and accumulator >= GAME_STEP_MS:
            accumulator = 0

            if state.pacman.powered_timer > 0:
                state.pacman.powered_timer -= 1

            next_pos = engine.choose_pacman_move(state)
            if next_pos != state.pacman.pos:
                state.pacman.direction = (next_pos[0] - state.pacman.pos[0], next_pos[1] - state.pacman.pos[1])
                state.pacman.pos = next_pos
            resolve_collisions(state)

            if not state.game_over:
                move_ghosts(state)
                resolve_collisions(state)

        renderer.draw(state)
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()
