# main.py
import copy
import time
import random
from board import Board, BOARD_HEIGHT, BOARD_WIDTH, PLAYER_1, PLAYER_2, read_benchmarks_from_file
from player import MinMaxPlayer


def main():
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


if __name__ == "__main__":
    main()
