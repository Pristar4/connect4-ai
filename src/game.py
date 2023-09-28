import time
import random

BOARD_WIDTH = 7
BOARD_HEIGHT = 6
PLAYER_1 = 1
PLAYER_2 = 2


class Connect4Env:

    def __init__(self, board=None, current_player=1):
        # Initialize the game board (usually a 6x7 grid)
        self.board = [[0] * BOARD_WIDTH for _ in range(BOARD_HEIGHT)]
        # Todo: more efficient to store a board as value type
        self.current_player = PLAYER_1  # Player 1 starts
        self.move_history = []

    def simulate_move(self, column, player):
        if not self.is_valid_move(column):
            print(f"invalid move: {column}")
            return False

        for row in reversed(self.board):
            if row[column] == 0:
                row[column] = player
                self.move_history.append(column)
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


class MinMaxPlayer:
    def __init__(self, ply, time_limit):
        self.pruned_nodes_count = 0  # reset the counters
        self.calculation_depth = ply
        self.max_depth = ply
        self.reached_depth = 1
        self.time_limit = time_limit
        self.move_scores = {}
        self.search_counter = 0
        self.start_time = 0
        self.end_time = 0

    def calculate_score(self, board, player, depth):
        normalized_ply = depth / self.reached_depth

        if board.is_winner(player):
            return 1 + normalized_ply / 2
        elif board.is_winner(PLAYER_1 if player == PLAYER_2 else PLAYER_1):
            return -1 - normalized_ply / 2
        else:
            return 0

    def order_valid_moves(self, valid_moves, depth):
        # random.shuffle(valid_moves)
        if depth - 1 in self.move_scores:
            return sorted(valid_moves, key=lambda move: self.move_scores[depth - 1].get(move, 0), reverse=True)
        return valid_moves

    def print_search_statistics(self, time_taken):
        print("Total nodes searched: ", self.search_counter)
        print("Total nodes pruned: ", self.pruned_nodes_count)
        print("Pruning percentage: ", (self.pruned_nodes_count / self.search_counter * 100).__round__(4))
        print("Nodes searched per second: ", self.search_counter / time_taken)

    def choose_move(self, env):
        self.search_counter = 0
        self.start_time = time.time()  # get the start time
        best_move = None

        for depth in range(1, self.max_depth + 1):  # Iterate up to the unreachable max_depth
            best_score = float('-inf')
            if depth not in self.move_scores:
                self.move_scores[depth] = {}

            valid_moves = self.order_valid_moves(env.get_valid_moves(), depth)
            for move in valid_moves:
                # if time.time() - self.start_time > self.time_limit * 0.95:  # Check if 95% of the time limit has been reached
                #     self.reached_depth = depth - 1  # Update the maximum reached depth to the currently finished depth
                #     print("Time limit nearly reached, reverting to last completed depth")
                #     print(
                #         f"Depth: {self.reached_depth}, Best move: {best_prev_move}, Best score: {best_prev_score.__round__(4)}")
                #     time_taken = time.time() - self.start_time
                #     self.print_stats(time_taken)
                #     return best_prev_move

                env.simulate_move(move, 2)
                score, won_game = self.simulate_minimax(env, depth - 1, float('-inf'), float('inf'),
                                                        False)  # We are maximizing
                env.undo_move(move)
                # Store the move score at the current depth
                self.move_scores[depth][move] = score
                if score > best_score:
                    best_score = score
                    best_move = move
                    best_prev_score = best_score
                    best_prev_move = best_move
                print(f"move: {move}, score: {score.__round__(4)}")  # To observe the move and score

            print(f"Depth: {depth}, Best move: {best_move}, Best score: {best_score.__round__(4)}")

        self.end_time = time.time()  # get the end time
        time_taken = self.end_time - self.start_time  # calculate the time taken
        self.print_search_statistics(time_taken)
        return best_move

    def simulate_minimax(self, board, depth, alpha, beta, maximizingPlayer):
        score_win_player = self.calculate_score(board, board.current_player, depth)
        self.search_counter += 1

        # Todo change 5 and -5 to the maximum possible score which is the pieces left which can be placed from from a player
        opponent = PLAYER_1 if board.current_player == PLAYER_2 else PLAYER_2
        player = env.current_player
        if score_win_player >= 5:
            print(f"Winning score found: {score_win_player}, depth: {depth}")
            return score_win_player, True  # return the score and the game is won

        if depth == 0 or env.is_draw() or env.is_winner(1 if player == 2 else 2) or score_win_player <= -5:
            return score_win_player, False  # return the score and the game is not won

        valid_moves = self.order_valid_moves(board.get_valid_moves(), depth)
        if maximizingPlayer:
            max_score = float('-inf')
            for move in valid_moves:
                board.simulate_move(move, 2)
                score, won_game = self.simulate_minimax(board, depth - 1, alpha, beta, False)
                max_score = max(max_score, score)
                board.undo_move(move)
                if won_game:
                    return max_score, True  # if the game is won, return the score and the game is won
                alpha = max(alpha, max_score)
                if alpha >= beta:
                    self.pruned_nodes_count += 1
                    # increment the pruned counter
                    break
            return max_score, False
        else:  # Minimizing player
            max_score = float('inf')
            for move in valid_moves:
                board.simulate_move(move, 1)
                score, won_game = self.simulate_minimax(board, depth - 1, alpha, beta, True)
                max_score = min(max_score, score)
                board.undo_move(move)
                if won_game:
                    # print("Minimizing player won")
                    return max_score, False  # if the game is won, return the score and the game is won

                beta = min(beta, max_score)
                if beta <= alpha:
                    self.pruned_nodes_count += 1
                    break
            return max_score, False


class MinMaxPlayerImproved(MinMaxPlayer):
    def __init__(self, ply, time_limit):
        super().__init__(ply, time_limit)

    def calculate_score(self, board, player, depth):
        normalized_ply = (21 - depth)

        if board.is_winner(player):
            return 1 + normalized_ply  # Award max score of 2 down to min score of 1
        elif board.is_winner(3 - player):
            return -1 - normalized_ply  # Punish by max score of -2 up to min score of -1
            # Iterate through all cells of the board
        supplementary_score = 0
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


# Main application
if __name__ == '__main__':
    env = Connect4Env()
    while True:
        try:
            difficulty = int(input("Enter difficulty (1-50): "))
            assert 1 <= difficulty <= 50
            break
        except ValueError:
            print("Invalid Difficulty. Please Enter a number between 1 and 10.")
        except AssertionError:
            print("Difficulty should be a number between 1 and 10.")

    player1 = MinMaxPlayer(difficulty, 8)
    player2 = MinMaxPlayerImproved(difficulty, 8)
    # game loop
    env.print_board()
    while not env.is_draw():

        if env.current_player == 1:
            print(f"Current player: {env.current_player}")
            while True:
                try:
                    move = int(input("Enter a move: ")) - 1
                    # move = player1.choose_move(env)
                    assert move in env.get_valid_moves()
                    break
                except ValueError:
                    print("Invalid move. Please Enter a valid number.")
                except AssertionError:
                    print("Move is not valid. Choose a move from the list of valid moves.")
        else:  # Player 2
            print(f"Current player: {env.current_player}")
            move = player2.choose_move(env)
        env.make_move(move)
        env.print_board()
        if env.is_winner(1):
            print("Player 1 wins!")
            break
        elif env.is_winner(2):

            print("Player 2 wins!")
            break
        # wait for space to be pressed
        # input("Press Enter to continue...")
