class ChessLogic:
    def __init__(self):
        """
        Initalize the ChessLogic Object. External fields are board and result

        board -> Two Dimensional List of string Representing the Current State of the Board
            P, R, N, B, Q, K - White Pieces

            p, r, n, b, q, k - Black Pieces

            '' - Empty Square

        result -> The current result of the game
            w - White Win

            b - Black Win

            d - Draw

            '' - Game In Progress
        """
        self.board = [
			['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'],
			['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],
			['','','','','','','',''],
			['','','','','','','',''],
			['','','','','','','',''],
			['','','','','','','',''],
			['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
			['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R'],
		]
        self.result = "" 
        # Debugging Output
        print("Initial Board State:")
        for row in self.board:
            print(row)

    def play_move(self, move: str) -> str:
        """
        Function to execute a valid move by updating the board.

        Args:
            move (str): Move in chess notation (e.g., "e2e4").

        Returns:
            str: Move in extended chess notation if valid, empty string if invalid.
        """
        if len(move) != 4:
            return ""

        # Convert chess notation to board indices
        start_col = ord(move[0]) - ord('a')
        start_row = 8 - int(move[1])
        end_col = ord(move[2]) - ord('a')
        end_row = 8 - int(move[3])

        print(f"Parsed Move: {move} -> Start: ({start_row}, {start_col}), End: ({end_row}, {end_col})")

        # Get the piece at the starting position
        piece = self.board[start_row][start_col]

        # Ensure a piece exists at the starting position
        if piece == "":
            print("Invalid Move: No piece at the starting position.")
            return ""

        # Ensure the move is legal
        if not self.is_valid_piece_move(piece, start_row, start_col, end_row, end_col):
            print("Invalid Move: Illegal movement for this piece.")
            return ""

        # Ensure path is clear for non-knight pieces BEFORE updating the board
        if piece.lower() != "n" and not self.is_path_clear(start_row, start_col, end_row, end_col):
            print("Invalid Move: Path is blocked.")
            return ""
        
        # Get the piece at the destination square
        target_piece = self.board[end_row][end_col]

        # Prevent moving onto a friendly piece
        if target_piece != "" and piece.isupper() == target_piece.isupper():
            print("Invalid Move: Cannot capture own piece.")
            return ""
        
        # Capture message if an enemy piece is captured
        if target_piece != "":
            print(f"{piece} captured {target_piece} at {move[2:]}")

        # Move is valid, Update board state
        self.board[end_row][end_col] = piece  # Place piece in new position
        self.board[start_row][start_col] = ""  # Remove piece from old position

        print("Board Updated:")
        for row in self.board:
            print(row)

        return move  # Returning move notation

    

    def is_valid_piece_move(self, piece, start_row, start_col, end_row, end_col):
        """
        Checks if the move follows the basic movement rules of the given piece.

        Args:
            piece (str): The piece being moved.
            start_row, start_col: The starting position.
            end_row, end_col: The target position.

        Returns:
            bool: True if the move is valid, False otherwise.
        """
        row_diff = abs(end_row - start_row)
        col_diff = abs(end_col - start_col)

        # Pawn Movement (Basic)
        if piece.lower() == "p":
            direction = -1 if piece.isupper() else 1  # White moves up (-1), Black moves down (+1)
            
            # Standard pawn move (1 square forward)
            if start_col == end_col and row_diff == 1 and (end_row - start_row) == direction:
                return True

            # Initial 2-square pawn move
            if start_col == end_col and row_diff == 2 and (start_row == 6 or start_row == 1):
                return True

            # Pawns cannot move sideways unless capturing (we'll handle captures later)
            return False

        # Knight Movement (L-shape)
        if piece.lower() == "n":
            return (row_diff, col_diff) in [(2, 1), (1, 2)]

        # Rook Movement (Straight lines)
        if piece.lower() == "r":
            return start_row == end_row or start_col == end_col  # Moves in a straight line

        # Bishop Movement (Diagonal)
        if piece.lower() == "b":
            return row_diff == col_diff  # Moves diagonally

        # Queen Movement (Diagonal or straight)
        if piece.lower() == "q":
            return row_diff == col_diff or start_row == end_row or start_col == end_col

        # King Movement (One square in any direction)
        if piece.lower() == "k":
            return row_diff <= 1 and col_diff <= 1

        return False  # If piece type is unknown


    def is_path_clear(self, start_row, start_col, end_row, end_col):
        """
        Checks if the path between start and end positions is clear for pieces that cannot jump.

        Args:
            start_row, start_col: The starting position.
            end_row, end_col: The target position.

        Returns:
            bool: True if the path is clear, False if any piece is blocking the way.
        """
        row_step = 0 if start_row == end_row else (1 if end_row > start_row else -1)
        col_step = 0 if start_col == end_col else (1 if end_col > start_col else -1)

        current_row, current_col = start_row + row_step, start_col + col_step

        while (current_row, current_col) != (end_row, end_col):
            if self.board[current_row][current_col] != "":
                print(f"Move blocked at ({current_row}, {current_col})")
                return False  # Path is blocked
            current_row += row_step
            current_col += col_step

        return True  # Path is clear
