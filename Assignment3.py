"""
Artificial Intelligence – Assignment 3
Submission Deadline - 05/09/2025
--------------------------------------

Topic: Chess AI with Minimax (Alpha-Beta) and Evaluation Function

INSTRUCTIONS TO STUDENTS
------------------------
1. Install the required libraries:
   In your terminal/command prompt, type:
       pip install python-chess chess-board pygame

   (Mac/Linux users may need: python3 -m pip install python-chess chess-board pygame)

   NOTE: "python-chess" is for chess rules,
         "chess-board" is for showing the GUI board,
         "pygame" is needed by the chess-board library to open the display window.

2. Run the program:
       python chess_ai.py
   (or python3 chess_ai.py on Mac/Linux)

3. How the chessboard works:
   - The chessboard is 8x8 squares.
   - Columns are called FILES and are labeled with letters: a, b, c, d, e, f, g, h
        (a = leftmost, h = rightmost from White’s view)
   - Rows are called RANKS and are numbered 1 to 8
        (1 = White’s back row, 8 = Black’s back row)

   Example of square names:
       a1 = bottom-left corner (White’s rook starts here)
       h1 = bottom-right corner (White’s rook)
       e2 = White’s king’s pawn start
       e4 = two squares forward from there

   So the board squares look like this from White’s view:

        8 | a8 b8 c8 d8 e8 f8 g8 h8
        7 | a7 b7 c7 d7 e7 f7 g7 h7
        6 | a6 b6 c6 d6 e6 f6 g6 h6
        5 | a5 b5 c5 d5 e5 f5 g5 h5
        4 | a4 b4 c4 d4 e4 f4 g4 h4
        3 | a3 b3 c3 d3 e3 f3 g3 h3
        2 | a2 b2 c2 d2 e2 f2 g2 h2
        1 | a1 b1 c1 d1 e1 f1 g1 h1
           -------------------------
             a  b  c  d  e  f  g  h
    See more at: https://www.chess.com/learn-how-to-play-chess

4. How to give moves:
   - Use **UCI format** (Universal Chess Interface).
   - A move is written as: <from-square><to-square>
   - Examples:
       "e2e4" → move the piece from e2 to e4 (common pawn opening)
       "g1f3" → move the knight from g1 to f3
       "a7a8q" → pawn moves from a7 to a8 and becomes a Queen (promotion)
   - Type 'quit' to stop the game.

5. Your Task:
   Complete the `evaluate` function in the `State` class.
   This is the "brain" of the AI which scores how good or bad a board position is.

   - If you do nothing, the program still works (it just plays very badly).
   - Improve the function by counting material (pieces), center control, mobility, etc.
   - Read the comments inside `evaluate` carefully.

6. Useful documentation:
   - python-chess (PyPI page): https://pypi.org/project/python-chess/
   - python-chess (full API reference): https://python-chess.readthedocs.io/en/latest/core.html

   You may also use ChatGPT to clarify how a function from python-chess works,
   BUT you should NOT ask it to complete the evaluation code for you.
   The design of the evaluation function is YOUR task.
   You can read the paper on Deepblue: https://www.mimuw.edu.pl/~ewama/zsi/deepBlue.pdf
   Other resouces on Deepblue: https://stanford.edu/~cpiech/cs221/apps/deepBlue.html
                               https://www.chess.com/blog/Rinckens/how-does-the-deep-blue-algorithm-work

"""

import chess
from chessboard import display
import time

class State:
    def __init__(self, board=None, player=True):
        if board is None:
            self.board = chess.Board()
        else:
            self.board = board
        self.player = player  # True = White's turn, False = Black's turn

    def goalTest(self):
        # Check if the game is over
        if self.board.is_checkmate():
            return not self.player  # The opponent just made a winning move
        return None

    def isTerminal(self):
        return self.board.is_game_over()

    def moveGen(self):
        # Generate next states
        children = []
        for move in self.board.legal_moves:
            new_board = self.board.copy()
            new_board.push(move)
            children.append(State(new_board, not self.player))
        return children

    def __str__(self):
        return str(self.board)

    def __eq__(self, other):
        return self.board.fen() == other.board.fen() and self.player == other.player

    def __hash__(self):
        return hash((self.board.fen(), self.player))

    def evaluate(self):
        """
        Evaluation function for chess positions.

        IMPORTANT:
        - Return a number.
        - Positive = good for White.
        - Negative = good for Black (AI).

        Step 1 (already done):
          Handle end of game:
            - Checkmate = very big positive/negative score
            - Draw = 0

        Step 2 (YOUR TASK):
          If the game is not over, add features like:

        (a) MATERIAL (pieces):
            - Use board.piece_map()
              -> returns a dictionary: {square : Piece}
            - Each Piece has:
                  .piece_type (e.g. chess.PAWN, chess.ROOK)
                  .color      (True = White, False = Black)
            - Example code:
                  for sq, piece in self.board.piece_map().items():
                      if piece.piece_type == chess.PAWN:
                          value = 1
                      elif piece.piece_type == chess.ROOK:
                          value = 5
                      ...
                      if piece.color == chess.WHITE:
                          score += value
                      else:
                          score -= value

        (b) CENTER CONTROL:
            - The 4 central squares are: d4, e4, d5, e5
              (in python-chess: chess.D4, chess.E4, chess.D5, chess.E5)
            - Idea: a piece standing in the center is more powerful.
            - Example code:
                  center_squares = [chess.D4, chess.E4, chess.D5, chess.E5]
                  for sq in center_squares:
                      piece = self.board.piece_at(sq)
                      if piece:
                          if piece.color == chess.WHITE:
                              score += 0.2
                          else:
                              score -= 0.2

        (c) MOBILITY:
            - Mobility = number of legal moves available.
            - Steps:
                1. Make a copy of the board: b = self.board.copy()
                2. Count legal moves for White:
                      b.turn = chess.WHITE
                      white_moves = len(list(b.legal_moves))
                3. Count legal moves for Black:
                      b.turn = chess.BLACK
                      black_moves = len(list(b.legal_moves))
                4. Add to score:
                      score += 0.05 * (white_moves - black_moves)

        (d) KING SAFETY (optional but fun):
            - Find king square:
                  white_king = self.board.king(chess.WHITE)
                  black_king = self.board.king(chess.BLACK)
            - Who attacks the king?
                  attackers = self.board.attackers(chess.BLACK, white_king)
              (This gives all Black pieces attacking the White king square)
            - Example:
                  if attackers:
                      score -= 0.5 * len(attackers)  # White king under attack
            - Do the same for Black king (attackers from White).

        For now, the function just returns 0.
        Replace with your material calculation and add improvements.
        """

        # Step 1: Handle finished games
        if self.board.is_checkmate():
            return -1000 if self.player else 1000  # Current player is mated
        if self.board.is_stalemate() or self.board.is_insufficient_material() or self.board.can_claim_draw():
            return 0

        # Step 2: YOUR WORK STARTS HERE
        # ------------------------------------
        # Right now we return 0 for all positions.
        # This means the AI plays randomly.
        # Replace this with your own scoring rules!
        return 0
        # ------------------------------------


def minimax(state, depth, alpha, beta, maximizingPlayer, maxDepth):
    if state.isTerminal() or depth == maxDepth:
        return state.evaluate(), None

    best_move = None

    if maximizingPlayer:  # MAX node (White)
        maxEval = float('-inf')
        for child in state.moveGen():
            eval_score, _ = minimax(child, depth + 1, alpha, beta, False, maxDepth)

            if eval_score > maxEval:
                maxEval = eval_score
                best_move = child.board.peek()  # Last move made

            alpha = max(alpha, eval_score)
            if alpha >= beta:
                break  # Alpha-beta pruning

        return maxEval, best_move

    else:  # MIN node (Black)
        minEval = float('inf')
        for child in state.moveGen():
            eval_score, _ = minimax(child, depth + 1, alpha, beta, True, maxDepth)

            if eval_score < minEval:
                minEval = eval_score
                best_move = child.board.peek()

            beta = min(beta, eval_score)
            if alpha >= beta:
                break

        return minEval, best_move


def play_game():
    current_state = State(player=True)  # White starts
    maxDepth = 3  # Try experimenting with the Search depth for more inteligent ai
    game_board = display.start()  # Initialize the GUI

    print("Artificial Intelligence – Assignment 3")
    print("Simple Chess AI")
    print("You are playing as White (enter moves in UCI format, e.g., e2e4)")

    while not current_state.isTerminal():
        # Update the display
        display.update(current_state.board.fen(), game_board)

        # Check for quit event
        if display.check_for_quit():
            break

        if current_state.player:  # Human move (White)
            try:
                move_uci = input("Enter your move (e.g., e2e4, g1f3, a7a8q) or 'quit': ")

                if move_uci.lower() == 'quit':
                    break

                move = chess.Move.from_uci(move_uci)

                if move in current_state.board.legal_moves:
                    new_board = current_state.board.copy()
                    new_board.push(move)
                    current_state = State(new_board, False)
                else:
                    print("Invalid move! Try again.")
                    continue
            except ValueError:
                print("Invalid input format! Use UCI format like 'e2e4'.")
                continue
        else:  # AI move (Black)
            print("AI is thinking...")
            start_time = time.time()
            eval_score, best_move = minimax(current_state, 0, float('-inf'), float('inf'), False, maxDepth)
            end_time = time.time()

            print(f"AI thought for {end_time - start_time:.2f} seconds")

            if best_move:
                new_board = current_state.board.copy()
                new_board.push(best_move)
                current_state = State(new_board, True)
                print(f"AI plays: {best_move.uci()}")
            else:
                # Fallback
                legal_moves = list(current_state.board.legal_moves)
                if legal_moves:
                    move = legal_moves[0]
                    new_board = current_state.board.copy()
                    new_board.push(move)
                    current_state = State(new_board, True)
                    print(f"AI plays (fallback): {move.uci()}")
                else:
                    break

    # Game over
    print("\nGame over!")
    display.update(current_state.board.fen(), game_board)

    if current_state.board.is_checkmate():
        print("Checkmate! " + ("White" if not current_state.player else "Black") + " wins!")
    elif current_state.board.is_stalemate():
        print("Stalemate! It's a draw.")
    elif current_state.board.is_insufficient_material():
        print("Insufficient material! It's a draw.")
    elif current_state.board.can_claim_draw():
        print("Draw by repetition or 50-move rule!")

    # Keep the window open for a moment
    time.sleep(3)
    display.terminate()


if __name__ == "__main__":
    play_game()
