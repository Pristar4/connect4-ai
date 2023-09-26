import random
import time


class Connect4Env:

    def __init__(self, board=None, current_player=1):
        # Initialize the game board (usually a 6x7 grid)
        self.board = [[0] * 7 for _ in range(6)]
        # Todo: more efficient to store a board as value type
        self.current_player = 1  # Player 1 starts
        self.moves_stack = []

    def get_state_repr(self):
        # Flatten the 2D list and convert it to a string
        return ''.join(str(item) for sublist in self.board for item in sublist)

    def simulate_move(self, column, player):
        """Simulates a move without changing the current player"""
        if not self.is_valid_move(column):
            print(f"invalid move: {column}")
            return False
        for row in reversed(self.board):
            if row[column] == 0:
                row[column] = player
                self.moves_stack.append(column)
                # add the move to the stack
                break
        return True

    def undo_move(self, _move):
        """Undoes the last move made"""
        if not self.moves_stack:
            print("No moves to undo")
            return False
        for row in self.board:
            if row[_move] != 0:
                row[_move] = 0
                self.moves_stack.pop()
                break
        return True

    def make_move(self, column):
        # Implement making a move in the specified column for the current player
        valid_moves = self.get_valid_moves()
        if column not in valid_moves:
            print(f"invalid move: {column}")
            return False
        for row in reversed(self.board):
            if row[column] == 0:
                row[column] = self.current_player
                break
        self.current_player = 1 if self.current_player == 2 else 2
        return True

    def is_valid_move(self, column):
        if column < 0 or column > 6:
            return False
        for row in self.board:
            if row[column] == 0:
                return True
        return False

    def _is_horizontal_winner(self, player):
        # Check horizontal
        for row in self.board:
            for i in range(4):
                if row[i] == row[i + 1] == row[i + 2] == row[i + 3] == player:
                    return True

    def _is_vertical_winner(self, player):
        # Check vertical
        for i in range(7):
            for j in range(3):
                if self.board[j][i] == self.board[j + 1][i] == self.board[j + 2][i] == self.board[j + 3][i] == player:
                    return True

    def _is_diagonal_winner(self, player):
        # Check diagonal
        for i in range(4):
            for j in range(3):
                if (self.board[j][i] == self.board[j + 1][i + 1] ==
                        self.board[j + 2][i + 2] == self.board[j + 3][i + 3] == player):
                    return True
        for i in range(3, 7):
            for j in range(3):
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
        if self.is_winner(1) or self.is_winner(2):
            return False
        for row in self.board:
            for col in row:
                if col == 0:
                    return False
        return True

    def get_valid_moves(self):
        # Get a list of valid moves for the current player
        moves = []
        for i in range(7):
            if self.is_valid_move(i):
                moves.append(i)

        return moves

    def print_board(self):
        print("  ".join([str(i + 1) for i in range(7)]))
        print("-" * 20)
        for row in self.board:
            print("  ".join([str(i) for i in row]))


class MinMaxPlayer:
    def __init__(self, ply, time_limit):
        self.ply = ply
        self.depth = ply / 2
        self.max_depth = ply / 2
        self.time_limit = time_limit

        # Profiling properties
        self.counter = 0
        self.start_time = 0
        self.end_time = 0

    def score(self, board, player, depth):
        normalized_ply = depth / self.max_depth

        if board.is_winner(player):
            return 1 + normalized_ply / 2
        elif board.is_winner(1 if player == 2 else 2):
            return -1 - normalized_ply / 2
        else:
            return 0

    def order_moves(self, valid_moves):
        # weighted_moves = [(abs(move - 3), move) for move in valid_moves]
        # weighted_moves.sort()
        # return [move for _, move in weighted_moves]
        # random.shuffle(valid_moves)
        return valid_moves

    def choose_move(self, env):
        self.counter = 0
        self.pruned = 0  # reset the counters
        self.start_time = time.time()  # get the start time
        best_move = None
        best_score = float('-inf')

        for depth in range(1, self.ply + 1):
            valid_moves = self.order_moves(env.get_valid_moves())
            for move in valid_moves:
                # if time.time() - self.start_time > self.time_limit:
                #     # return immediately if time limit exceeded
                #     print("Time limit exceeded ")
                #     print(f"Depth: {depth}, Best move: {best_move}, Best score: {best_score}")
                #     self.time_limit = 5
                #     return best_move

                env.simulate_move(move, 2)
                score = self.minimax(env, depth - 1, float('-inf'), float('inf'), False)  # We are maximizing
                env.undo_move(move)
                if score > best_score:
                    best_score = score
                    best_move = move
                print(f"move: {move}, score: {score}")  # To observe the move and score
                print(f"BEST MOVE: {best_move}, BEST SCORE: {best_score}")

            print(f"Depth: {depth}, Best move: {best_move}, Best score: {best_score}")

        self.end_time = time.time()  # get the end time
        time_taken = self.end_time - self.start_time  # calculate the time taken
        print("Total nodes searched: ", self.counter)
        print("Total nodes pruned: ", self.pruned)
        print("Pruning percentage: ", self.pruned / self.counter * 100)
        print("Nodes searched per second: ", self.counter / time_taken)  # calculate nodes per second

        return best_move

    def minimax(self, env, depth, alpha, beta, maximizingPlayer):
        self.counter += 1
        if env.current_player == 1:
            score = self.score(env, 1, depth)
        else:
            score = self.score(env, 2, depth)
        if depth == 0 or env.is_winner(1) or env.is_winner(2) or env.is_draw():
            return score

        valid_moves = self.order_moves(env.get_valid_moves())
        if maximizingPlayer:
            value = float('-inf')
            for move in valid_moves:
                env.simulate_move(move, 2)
                value = max(value, self.minimax(env, depth - 1, alpha, beta, not maximizingPlayer))
                env.undo_move(move)
                alpha = max(alpha, value)
                if alpha >= beta:
                    self.pruned += 1
                    # increment the pruned counter
                    break
            return value
        else:  # Minimizing player
            value = float('inf')
            for move in valid_moves:
                env.simulate_move(move, 1)
                value = min(value, self.minimax(env, depth - 1, alpha, beta, True))
                env.undo_move(move)
                beta = min(beta, value)
                if beta <= alpha:
                    self.pruned += 1
                    break
            return value


# Main application
if __name__ == '__main__':
    env = Connect4Env()
    while True:
        try:
            difficulty = int(input("Enter difficulty (1-10): "))
            assert 1 <= difficulty <= 10
            break
        except ValueError:
            print("Invalid Difficulty. Please Enter a number between 1 and 10.")
        except AssertionError:
            print("Difficulty should be a number between 1 and 10.")

    player1 = MinMaxPlayer(difficulty, 5)
    player2 = MinMaxPlayer(difficulty, 5)
    # game loop
    env.print_board()
    while not env.is_draw():

        if env.current_player == 1:
            print(f"Current player: {env.current_player}")
            print(f"valid moves: {env.get_valid_moves()}")
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
