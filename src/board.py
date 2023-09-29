BOARD_HEIGHT = 6
BOARD_WIDTH = 7
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

    def __init__(self):
        # Initialize the game board (usually a 6x7 grid)
        self.width = BOARD_WIDTH
        self.height = BOARD_HEIGHT
        self.board = [[0] * self.width for _ in range(self.height)]

        # Todo: more efficient to store a board as value type
        self.current_player = PLAYER_1  # Player 1 starts
        self.move_history = []
        self.move_counter = {PLAYER_1: 0, PLAYER_2: 0}

    def reset(self):
        self.board = [[0] * self.width for _ in range(self.height)]
        self.current_player = PLAYER_1  # Player 1 starts
        self.move_history = []
        self.move_counter = {PLAYER_1: 0, PLAYER_2: 0}

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
        return 0 <= column < self.width and any(row[column] == 0 for row in self.board)

    def _is_horizontal_winner(self, player):
        # Check horizontal
        for row in self.board:
            for i in range(self.width - 3):
                if row[i] == row[i + 1] == row[i + 2] == row[i + 3] == player:
                    return True

    def _is_vertical_winner(self, player):
        # Check vertical
        for i in range(self.width):
            for j in range(self.height - 3):
                if self.board[j][i] == self.board[j + 1][i] == self.board[j + 2][i] == self.board[j + 3][i] == player:
                    return True

    def _is_diagonal_winner(self, player):
        # Check diagonal
        for i in range(self.width - 3):
            for j in range(self.height - 3):
                if (self.board[j][i] == self.board[j + 1][i + 1] ==
                        self.board[j + 2][i + 2] == self.board[j + 3][i + 3] == player):
                    return True
        for i in range(self.height - 3, self.width):
            for j in range(self.height - 3):
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
        for i in range(self.width):
            if self.is_valid_move(i):
                moves.append(i)

        return moves

    def print_board(self):
        print("  ".join([str(i + 1) for i in range(self.width)]))
        print("-" * 20)
        for row in self.board:
            print("  ".join([str(i) for i in row]))


def board_from_moves(moves: str, board: Board) -> None:
    """Populate the board according to a sequence of moves"""
    for i, move in enumerate(moves):
        player = PLAYER_1 if i % 2 == 0 else PLAYER_2  # Switch player after each move
        board.move_counter[player] += 1
        board.simulate_move(int(move) - 1, player)  # subtract 1 because columns start from 0


def read_benchmarks_from_file(file_name: str) -> list[tuple[str, int]]:
    with open(file_name, "r") as file:
        lines = file.readlines()
    benchmarks = [(line.split()[0], int(line.split()[1])) for line in lines]
    return benchmarks
