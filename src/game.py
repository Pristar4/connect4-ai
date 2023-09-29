import copy
import time
import random

BOARD_WIDTH = 7
BOARD_HEIGHT = 6
PLAYER_1 = 1
PLAYER_2 = 2


class Node:
    def __init__(self, state, parent=None):
        self.state = state
        self.children = []
        self.move = None
        self.parent = parent
        self.value = None


class Board:

    def __init__(self, board=None, current_player=1, move_counter={PLAYER_1: 0, PLAYER_2: 0}):
        # Initialize the game board (usually a 6x7 grid)
        self.board = [[0] * BOARD_WIDTH for _ in range(BOARD_HEIGHT)]

        # Todo: more efficient to store a board as value type
        self.current_player = PLAYER_1  # Player 1 starts
        self.move_history = []
        self.move_counter = {PLAYER_1: 0, PLAYER_2: 0}

    def reset(self):
        self.board = [[0] * BOARD_WIDTH for _ in range(BOARD_HEIGHT)]
        self.current_player = PLAYER_1  # Player 1 starts
        self.move_history = []
        self.move_counter = {PLAYER_1: 0, PLAYER_2: 0}

    def create_children(self, node):
        valid_moves = node.get_valid_moves(node.state)
        for move in valid_moves:
            new_state = copy.deepcopy(node.state)
            self.make_move(new_state, move)
            child_node = Node(new_state, parent=node)
            child_node.move = move
            node.children.append(child_node)

    def simulate_move(self, column, player):
        if not self.is_valid_move(column):
            print(f"invalid move: {column}")
            return False

        for row in reversed(self.board):
            if row[column] == 0:
                row[column] = player
                self.move_history.append(column + 1)
                # add the move to the stack
                break
        return True

    def undo_move(self, _move):
        if not self.move_history:
            print("No moves to undo")
            return False

        for row in self.board:
            if row[_move] != 0:
                row[_move] = 0
                self.move_history.pop()
                break
        return True

    def make_move(self, column):
        valid_moves = self.get_valid_moves()
        if column not in valid_moves:
            print(f"invalid move: {column}")
            return False

        for row in reversed(self.board):
            if row[column] == 0:
                row[column] = self.current_player
                break
        self.move_counter[self.current_player] += 1
        print(f"Move counter: {self.move_counter}")
        self.switch_player()
        return True

    def switch_player(self):
        self.current_player = PLAYER_1 if self.current_player == PLAYER_2 else PLAYER_2

    def is_valid_move(self, column):
        return 0 <= column < BOARD_WIDTH and any(row[column] == 0 for row in self.board)

    def _is_horizontal_winner(self, player):
        # Check horizontal
        for row in self.board:
            for i in range(BOARD_WIDTH - 3):
                if row[i] == row[i + 1] == row[i + 2] == row[i + 3] == player:
                    return True

    def _is_vertical_winner(self, player):
        # Check vertical
        for i in range(BOARD_WIDTH):
            for j in range(BOARD_HEIGHT - 3):
                if self.board[j][i] == self.board[j + 1][i] == self.board[j + 2][i] == self.board[j + 3][i] == player:
                    return True

    def _is_diagonal_winner(self, player):
        # Check diagonal
        for i in range(BOARD_WIDTH - 3):
            for j in range(BOARD_HEIGHT - 3):
                if (self.board[j][i] == self.board[j + 1][i + 1] ==
                        self.board[j + 2][i + 2] == self.board[j + 3][i + 3] == player):
                    return True
        for i in range(BOARD_HEIGHT - 3, BOARD_WIDTH):
            for j in range(BOARD_HEIGHT - 3):
                if (self.board[j][i] == self.board[j + 1][i - 1] ==
                        self.board[j + 2][i - 2] == self.board[j + 3][i - 3] == player):
                    return True
        return False

    def is_winner(self, player):
        # Check if the specified player has won
        if (self._is_vertical_winner(player) or self._is_horizontal_winner(player)
                or self._is_diagonal_winner(player)):
            return True
        return False

    def is_draw(self):
        # Check if the game is a draw
        if self.is_winner(PLAYER_1) or self.is_winner(PLAYER_2):
            return False
        for row in self.board:
            for col in row:
                if col == 0:
                    return False
        return True

    def get_valid_moves(self):
        # Get a list of valid moves for the current player
        moves = []
        for i in range(BOARD_WIDTH):
            if self.is_valid_move(i):
                moves.append(i)

        return moves

    def print_board(self):
        print("  ".join([str(i + 1) for i in range(BOARD_WIDTH)]))
        print("-" * 20)
        for row in self.board:
            print("  ".join([str(i) for i in row]))


def board_from_moves(moves: str, board: Board) -> None:
    """Populate the board according to a sequence of moves"""
    for i, move in enumerate(moves):
        player = PLAYER_1 if i % 2 == 0 else PLAYER_2  # Switch player after each move
        board.move_counter[player] += 1
        board.simulate_move(int(move) - 1, player)  # subtract 1 because columns start from 0


class MinMaxPlayer:
    def __init__(self, ply, time_limit):
        self.pruned_nodes_count = 0
        self.full_search_counter = 0
        self.calculation_depth = ply
        self.max_depth = ply
        self.reached_depth = 1
        self.time_limit = time_limit
        self.move_scores = {}
        self.search_counter = 0
        self.start_time = 0
        self.end_time = 0
        self.best_move = None
        self.best_score = None

        # iterative deepening nodes
        self.nodes_searched = 0

    def run_benchmarks(self, benchmarks: list[tuple[str, int]], board: Board):
        passed_count = 0
        expected_zero = 0
        passed_zero = 0
        for moves, expected_score in benchmarks:
            start_time = time.time()  # Start of computation
            board_from_moves(moves, board)

            # Call the choose_move function which calls minimax internally
            best_move = self.choose_move(board, pruning=True, iterative=True)
            score = self.best_score
            '2252576253462244111563365343671351441'

            time_used = (time.time() - start_time) * 1e6  # Time used in microseconds
            passed = score == expected_score
            if expected_score == 0:
                expected_zero += 1
            if passed:
                passed_count += 1
                if score == 0:
                    passed_zero += 1
            else:
                if expected_score != 0:
                    print(
                        f"For moves {moves}, expected {expected_score}, got {score}. Test {'passed' if passed else 'failed'}.")
            board.reset()
        print(f"Passed {passed_count} out of {len(benchmarks)} tests.")
        print(f"Passed {passed_count / len(benchmarks) * 100}% of tests.")
        print(f"Passed {passed_zero} out of {expected_zero} tests with score 0.")
        # passed without the zeroes
        print(f"Passed {passed_count - passed_zero} out of {len(benchmarks) - expected_zero} tests without the zeroes.")
        print(
            f"Passed {(passed_count - passed_zero) / (len(benchmarks) - expected_zero) * 100}% of tests without the zeroes.")



    def calculate_score(self, board, player, depth):
        smart_score = False


        if board.is_winner(player):
            return 22 - board.move_counter[player]
        elif board.is_winner(PLAYER_2 if player == PLAYER_1 else PLAYER_1):
            # return 22 - board.move_counter[PLAYER_2 if player == PLAYER_1 else PLAYER_1]
            return -22 + board.move_counter[PLAYER_2 if player == PLAYER_1 else PLAYER_1]
        else:
            supplementary_score = 0
            if smart_score:
                for i in range(BOARD_HEIGHT):
                    for j in range(BOARD_WIDTH):
                        if board.board[i][j] == player:
                            # Check cells horizontally, vertically and diagonally
                            directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
                            for dx, dy in directions:
                                for dist in range(1, 4):
                                    x, y = i + dx * dist, j + dy * dist
                                    if 0 <= x < BOARD_HEIGHT and 0 <= y < BOARD_WIDTH and board.board[x][y] == player:
                                        # Increase supplementary score if there are other connected pieces to the current player
                                        supplementary_score += 0.1
                                    else:
                                        # Stop searching further in this direction if this cell is not a piece of the current player
                                        break

            return supplementary_score  # No advantage no punishment

    def order_valid_moves(self, valid_moves, depth):
        # random.shuffle(valid_moves)
        if depth - 1 in self.move_scores:
            return sorted(valid_moves, key=lambda move: self.move_scores[depth - 1].get(move, 0), reverse=True)
        return valid_moves

    def print_search_statistics(self, time_taken):
        print("Total nodes searched with pruning: ", self.search_counter)
        print("Total nodes searched with iterative deepening: ", self.nodes_searched)
        print("Total nodes searched without pruning: ", self.full_search_counter)
        print("Total nodes pruned: ", self.pruned_nodes_count)
        print("Pruning percentage (compared to full search): ",
              (self.search_counter / self.full_search_counter * 100).__round__(4))
        print("Pruning percentage (compared to searched nodes): ",
              (self.pruned_nodes_count / self.search_counter * 100).__round__(4))
        if time_taken > 0:
            print("Nodes searched per second: ", self.search_counter / time_taken)
        else:
            print("Time taken is zero")

    def choose_move(self, board, pruning=True, iterative=False):
        self.search_counter = 0

        best_move = None
        best_score = float('-inf')
        if iterative:
            self.search_counter = 0
            self.start_time = time.time()  # get the start time
            self.nodes_searched = 0  # reset nodes_searched for new iterative deepening
            for depth in range(1, self.calculation_depth + 1):
                self.calculation_depth = depth
                # print(f"\nPerforming Minimax search at depth: {depth}")
                move = self.choose_move(board, iterative=False, pruning=True)
                self.nodes_searched += self.search_counter
                if time.time() - self.start_time > self.time_limit:
                    print(f"Time limit exceeded at depth: {depth}")
                    break
                best_move = move
            return best_move
        else:

            if pruning:

                for depth in range(1, self.calculation_depth + 1):  # Iterate up to the unreachable max_depth
                    best_score = float('-inf')
                    if depth not in self.move_scores:
                        self.move_scores[depth] = {}

                    valid_moves = self.order_valid_moves(board.get_valid_moves(), depth)
                    for move in valid_moves:
                        # if time.time() - self.start_time > self.time_limit * 0.95:  # Check if 95% of the time limit has been reached
                        #     self.reached_depth = depth - 1  # Update the maximum reached depth to the currently finished depth
                        #     print("Time limit nearly reached, reverting to last completed depth")
                        #     print(
                        #         f"Depth: {self.reached_depth}, Best move: {best_prev_move}, Best score: {best_prev_score.__round__(4)}")
                        #     time_taken = time.time() - self.start_time
                        #     self.print_stats(time_taken)
                        #     return best_prev_move

                        board.simulate_move(move, 2)
                        score = self.minimax(board, depth - 1, float('-inf'), float('inf'),
                                             False)  # We are maximizing
                        board.undo_move(move)
                        # Store the move score at the current depth
                        self.move_scores[depth][move] = score
                        if score > best_score:
                            best_score = score
                            best_move = move
                            self.best_score = score
                            best_prev_score = best_score
                            best_prev_move = best_move
                        # print(f"move: {move}, score: {score.__round__(4)}")  # To observe the move and score

                    # print(f"Depth: {depth}, Best move: {best_move}, Best score: {best_score.__round__(4)}")

                self.end_time = time.time()  # get the end time
                time_taken = self.end_time - self.start_time  # calculate the time taken
                # self.print_search_statistics(time_taken)

                return best_move
            else:  # perform a full search
                best_move = None
                best_score = float('-inf')

                valid_moves = board.get_valid_moves()

                # loop over the valid moves
                for move in valid_moves:
                    board.simulate_move(move, 2)
                    score = self.minimax_without_pruning(board, self.calculation_depth - 1)
                    board.undo_move(move)

                    # print(f"move: {move}, score: {score.__round__(4)}")

                    # check if the current move's score is greater than the best_score
                    if score > best_score:
                        best_score = score
                        best_move = move

                # print(f"Best move: {best_move}, Best score: {best_score.__round__(4)}")
                return best_move

    def minimax(self, board, depth, alpha, beta, maximizingPlayer):
        score_win_player = self.calculate_score(board, board.current_player, depth)
        self.search_counter += 1

        # if current board state is a terminal state: return value of the board

        if (depth == 0 or board.is_winner(1) or board.is_winner(2) or board.is_draw() or
                score_win_player >= 1 or score_win_player <= -1):
            return self.calculate_score(board, board.current_player, depth)

        valid_moves = self.order_valid_moves(board.get_valid_moves(), depth)
        if maximizingPlayer:
            max_score = float('-inf')
            for move in valid_moves:
                board.simulate_move(move, 2)
                max_score = max(max_score, self.minimax(board, depth - 1, alpha, beta, False))
                board.undo_move(move)
                alpha = max(alpha, max_score)
                if alpha >= beta:
                    self.pruned_nodes_count += 1
                    # increment the pruned counter
                    break
            return max_score
        else:  # Minimizing player
            min_score = float('inf')
            for move in valid_moves:
                board.simulate_move(move, 1)
                min_score = min(min_score, self.minimax(board, depth - 1, alpha, beta, True))
                board.undo_move(move)
                beta = min(beta, min_score)
                if beta <= alpha:
                    self.pruned_nodes_count += 1
                    break
            return min_score

    def minimax_without_pruning(self, board, depth):
        score_win_player = self.calculate_score(board, board.current_player, depth)
        self.full_search_counter += 1
        valid_moves = board.get_valid_moves()
        if (depth == 0 or board.is_winner(1) or board.is_winner(2) or
                board.is_draw() or score_win_player >= 1 or score_win_player <= -1):
            return self.calculate_score(board, board.current_player, depth)
        if board.current_player == 1:  # assuming player 1 is maximizing
            max_score = float('-inf')
            for move in valid_moves:
                board.simulate_move(move, 1)
                max_score = max(max_score, self.minimax_without_pruning(board, depth - 1))
                board.undo_move(move)
            return max_score
        else:  # minimizing
            min_score = float('inf')
            for move in valid_moves:
                board.simulate_move(move, 2)
                min_score = min(min_score, self.minimax_without_pruning(board, depth - 1))
                board.undo_move(move)
            return min_score


def read_benchmarks_from_file(file_name: str) -> list[tuple[str, int]]:
    with open(file_name, "r") as file:
        lines = file.readlines()
    benchmarks = [(line.split()[0], int(line.split()[1])) for line in lines]
    return benchmarks


# Main application
if __name__ == '__main__':
    play_game = False

    board = Board()
    while True:
        try:
            difficulty = int(input("Enter difficulty (1-50): "))
            assert 1 <= difficulty <= 50
            break
        except ValueError:
            print("Invalid Difficulty. Please Enter a number between 1 and 10.")
        except AssertionError:
            print("Difficulty should be a number between 1 and 10.")

    player2 = MinMaxPlayer(difficulty, 8)
    benchmark_filename = "../benchmark/Test_L3_R1"
    benchmarks = read_benchmarks_from_file(benchmark_filename)
    player2.run_benchmarks(benchmarks, board)

    if play_game:
        # game loop
        board.print_board()
        while not board.is_draw():

            if board.current_player == 1:
                print(f"Current player: {board.current_player}")
                while True:
                    try:
                        move = int(input("Enter a move: ")) - 1
                        assert move in board.get_valid_moves()
                        break
                    except ValueError:
                        print("Invalid move. Please Enter a valid number.")
                    except AssertionError:
                        print("Move is not valid. Choose a move from the list of valid moves.")
            else:  # Player 2
                print(f"Current player: {board.current_player}")
                print("Running full search without pruning...")
                _ = player2.choose_move(board, pruning=False)
                print("Running search with iterative deepening...")
                _ = player2.choose_move(board, pruning=False, iterative=True)
                print("Running search with pruning...")
                move = player2.choose_move(board, pruning=True)
            board.make_move(move)
            player2.full_search_counter = 0
            player2.pruned_nodes_count = 0

            board.print_board()
            if board.is_winner(1):
                print("Player 1 wins!")
                break
            elif board.is_winner(2):
                print("Player 2 wins!")
