from __future__ import annotations

from adversarial.alphabeta import alphabeta_move
from adversarial.minimax import choose_best_move
from csp.constraints import filter_safe_moves
from game.game_state import GameState
from metrics.profiler import benchmark_searches
from probability.markov import predict_ghosts
from search.astar import astar
from search.bfs import bfs
from search.dfs import dfs
from search.ucs import ucs
from utils import Pos, manhattan


class DecisionEngine:
    def __init__(self) -> None:
        self.last_summary: list[str] = []
        self.current_target: Pos | None = None
        self.current_path: list[Pos] = []

    def _search(self, state: GameState, start: Pos, goal: Pos, blocked: set[Pos]):
        goals = {goal}
        algo = state.algorithm
        if algo == 'BFS':
            return bfs(state.board, start, goals, blocked)
        if algo == 'DFS':
            return dfs(state.board, start, goals, blocked)
        if algo == 'UCS':
            return ucs(state.board, start, goals, blocked)
        return astar(state.board, start, goals, blocked)

    def _choose_food_target(self, board, pac_pos: Pos, foods: set[Pos], ghost_positions: list[Pos]) -> Pos | None:
        if not foods:
            return None

        best_food = None
        best_score = float('-inf')

        for food in foods:
            food_dist = manhattan(pac_pos, food)
            ghost_dist = min((manhattan(food, g) for g in ghost_positions), default=999)
            power_bonus = 8 if food in board.power_pellets else 0
            score = (ghost_dist * 6) - food_dist + power_bonus
            if ghost_dist <= 2:
                score -= 20

            if score > best_score:
                best_score = score
                best_food = food

        return best_food

    def choose_pacman_move(self, state: GameState) -> Pos:
        board = state.board
        pac = state.pacman
        ghost_positions = [g.pos for g in state.ghosts]
        foods = board.all_food()

        if state.use_markov:
            ghost_predictions = predict_ghosts(board, ghost_positions, pac.pos)
            danger_cells = {
                pos for pos, prob in ghost_predictions.items()
                if prob >= 0.20
            }
        else:
            danger_cells = set(ghost_positions)

        safe_report = filter_safe_moves(
            board,
            pac.pos,
            danger_cells,
            powered=pac.powered_timer > 0,
        )
        safe_moves = safe_report.safe_moves or board.legal_neighbors(pac.pos)

        if self.current_target not in foods:
            self.current_target = None
            self.current_path = []

        if self.current_path:
            while self.current_path and self.current_path[0] == pac.pos:
                self.current_path.pop(0)

            if self.current_path:
                next_step = self.current_path[0]
                legal_now = board.legal_neighbors(pac.pos)
                if next_step in legal_now and (pac.powered_timer > 0 or next_step not in danger_cells):
                    return next_step

            self.current_path = []
            self.current_target = None

        if self.current_target is None:
            self.current_target = self._choose_food_target(board, pac.pos, foods, ghost_positions)

        target = self.current_target
        if target is None:
            return pac.pos

        blocked = set()
        if pac.powered_timer <= 0:
            blocked = danger_cells

        nearest_ghost_dist = min((manhattan(pac.pos, g) for g in ghost_positions), default=999)

        if state.use_minimax and pac.powered_timer <= 0 and nearest_ghost_dist <= 4:
            best = choose_best_move(board, pac.pos, ghost_positions, foods, powered=False, depth=1)
            if best.best_move != pac.pos:
                self.current_path = []
                return best.best_move

        if state.use_minimax and pac.powered_timer > 0 and nearest_ghost_dist <= 5:
            move = alphabeta_move(board, pac.pos, ghost_positions, foods, powered=True, depth=1)
            if move != pac.pos:
                self.current_path = []
                return move

        result = self._search(state, pac.pos, target, blocked)
        if result.found and len(result.path) > 1:
            state.logger.log(f'{state.algorithm} -> target {target} | expanded {result.expanded} | path {result.path_len}')
            self.current_path = result.path[1:]
            return result.path[1]

        self.current_path = []
        self.current_target = None

        best = pac.pos
        best_score = float('-inf')
        for mv in safe_moves:
            ghost_dist = min((manhattan(mv, g) for g in ghost_positions), default=999)
            target_dist = manhattan(mv, target)
            score = (ghost_dist * 5) - target_dist
            if score > best_score:
                best_score = score
                best = mv

        state.logger.log('fallback safe move used')
        return best

    def benchmark(self, state: GameState) -> list[str]:
        foods = state.board.all_food()
        if not foods:
            return ['no food remaining']
        target = min(foods, key=lambda f: manhattan(state.pacman.pos, f))
        lines = benchmark_searches(state.board, state.pacman.pos, {target}, set())
        self.last_summary = lines
        return lines
