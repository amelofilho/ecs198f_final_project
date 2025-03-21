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
        
        self.last_pawn_move = None  # Stores the last move that could trigger en passant

        self.move_history = []  # Stores move strings like "e2e4"

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

        # print(f"Parsed Move: {move} -> Start: ({start_row}, {start_col}), End: ({end_row}, {end_col})")

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
        
        # Check if the move is an En Passant capture
        if piece.lower() == "p" and target_piece == "" and start_col != end_col:
            if self.last_pawn_move and self.last_pawn_move == (start_row, end_col):
                print(f"En Passant executed: {move}")
                self.board[start_row][end_col] = ""  # Remove captured pawn
            else:
                print("Invalid Move: En Passant not possible.")
                return ""
        
        # Reset last pawn move before checking
        self.last_pawn_move = None  

        # Track last pawn move for En Passant
        if piece.lower() == "p" and abs(start_row - end_row) == 2:
            self.last_pawn_move = (end_row, end_col)  # Store new position of moved pawn
            print(f"Last pawn move recorded for En Passant: {self.last_pawn_move}")

        # Check if a pawn is reaching the last rank for promotion
        if piece.lower() == "p" and (end_row == 0 or end_row == 7):
            print(f"Pawn promoted at {move[2:]}!")
            piece = "Q" if piece.isupper() else "q"  # Auto-promote to queen
        
        # Capture message if an enemy piece is captured
        if target_piece != "":
            print(f"{piece} captured {target_piece} at {move[2:]}")

        # Check if move is a castling attempt
        if piece.lower() == "k" and abs(start_col - end_col) == 2:
            return self.handle_castling(piece, start_row, start_col, end_row, end_col)
        
        # Backup board state before making the move
        original_piece = self.board[end_row][end_col]
        self.board[end_row][end_col] = piece  # Simulate the move
        self.board[start_row][start_col] = ""

        # Check if the move puts the player in check
        if self.is_king_in_check("w" if piece.isupper() else "b"):
            print("Invalid Move: This move puts your king in check.")
            # Undo the move
            self.board[start_row][start_col] = piece
            self.board[end_row][end_col] = original_piece
            return ""

        # If move is valid, finalize the board update
        self.board[end_row][end_col] = piece
        self.board[start_row][start_col] = ""

        # Print board update confirmation
        print("Board Updated:")
        # for row in self.board:
        #     print(row)

        # Check if opponent is in checkmate
        opponent_color = "w" if piece.islower() else "b"
        if self.is_checkmate(opponent_color):
            self.result = opponent_color  # 'w' if White wins, 'b' if Black wins
            print(f"Checkmate! {'White' if self.result == 'w' else 'Black'} wins!")
            return move
        
        if self.is_stalemate(opponent_color):
            self.result = "d"  # Draw
            print("Stalemate! The game is a draw.")
            return move
        
        return move 



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
            
            # Allow En Passant capture
            if self.board[end_row][end_col] == "" and start_col != end_col and self.last_pawn_move == (start_row, end_col):
                return True  

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

        # King Movement (One square in any direction OR castling)
        if piece.lower() == "k":
            if row_diff <= 1 and col_diff <= 1:
                return True  # Normal one-square move
            if col_diff == 2 and row_diff == 0:  
                return True  # Allow castling (checked separately in handle_castling)
            return False  # Any other move is illegal


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
    
    def handle_castling(self, piece, start_row, start_col, end_row, end_col):
        """
        Handles castling move if all conditions are met.

        Returns:
            str: Castling notation ("O-O" or "O-O-O") if valid, "" if invalid.
        """
        kingside = end_col > start_col  # True if moving right (kingside)
        
        rook_col = 7 if kingside else 0  # Find correct rook position
        new_rook_col = 5 if kingside else 2  # New position for the rook

        # Ensure the king and rook have not moved
        if self.board[start_row][rook_col].lower() != "r":
            print("Invalid Castling: No rook available.")
            return ""

        # Ensure path between king and rook is clear
        if not self.is_path_clear(start_row, start_col, start_row, rook_col):
            print("Invalid Castling: Path between king and rook is not clear.")
            return ""

        # Ensure the king's new position is **next to the rook**
        if abs(rook_col - end_col) != 1:
            print("Invalid Castling: King must land directly next to the rook.")
            return ""

        # Perform castling move
        self.board[end_row][end_col] = piece  # Move king
        self.board[start_row][start_col] = ""  # Remove king from old position
        self.board[start_row][new_rook_col] = "R" if piece.isupper() else "r"  # Move rook
        self.board[start_row][rook_col] = ""  # Remove rook from old position

        notation = "O-O" if kingside else "O-O-O"
        print(f"Castling executed: {notation}")
        return notation

    def is_king_in_check(self, color: str) -> bool:
        """
        Determines if the king of the given color is in check.
        
        Args:
            color (str): 'w' for white, 'b' for black.

        Returns:
            bool: True if the king is in check, False otherwise.
        """
        # Find the king's position
        king_symbol = "K" if color == "w" else "k"
        king_position = None

        for row in range(8):
            for col in range(8):
                if self.board[row][col] == king_symbol:
                    king_position = (row, col)
                    break

        if not king_position:
            return False  # King not found (should never happen in a valid game)

        king_row, king_col = king_position

        # Check if any enemy piece can attack the king
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece.isupper() != (color == "w"):  # Opponent's piece
                    if self.is_valid_piece_move(piece, row, col, king_row, king_col):
                        return True  # King is in check

        return False

    def is_checkmate(self, color: str) -> bool:
        """
        Determines if the given player is in checkmate.
        
        Args:
            color (str): 'w' for white, 'b' for black.

        Returns:
            bool: True if the player is in checkmate, False otherwise.
        """
        if not self.is_king_in_check(color):
            return False  # Not in check, so it's not checkmate

        # Try every possible move to escape check
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and (piece.isupper() == (color == "w")):  # Only the player's pieces
                    for new_row in range(8):
                        for new_col in range(8):
                            if self.is_valid_piece_move(piece, row, col, new_row, new_col):
                                # Simulate the move
                                original_piece = self.board[new_row][new_col]
                                self.board[new_row][new_col] = piece
                                self.board[row][col] = ""

                                # Check if king is still in check
                                still_in_check = self.is_king_in_check(color)

                                # Undo the move
                                self.board[row][col] = piece
                                self.board[new_row][new_col] = original_piece

                                if not still_in_check:
                                    return False  # Found a legal escape move

        return True  # No escape moves found → Checkmate

    def is_stalemate(self, color: str) -> bool:
        """
        Determines if the game is in stalemate (no legal moves and not in check).

        Args:
            color (str): 'w' for white, 'b' for black.

        Returns:
            bool: True if it's stalemate, False otherwise.
        """
        if self.is_king_in_check(color):
            return False  # If in check, it's not stalemate

        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and (piece.isupper() == (color == "w")):
                    for new_row in range(8):
                        for new_col in range(8):
                            if self.is_valid_piece_move(piece, row, col, new_row, new_col):
                                # Simulate the move
                                original_piece = self.board[new_row][new_col]
                                self.board[new_row][new_col] = piece
                                self.board[row][col] = ""

                                still_in_check = self.is_king_in_check(color)

                                # Undo move
                                self.board[row][col] = piece
                                self.board[new_row][new_col] = original_piece

                                if not still_in_check:
                                    return False  # Legal move exists
        return True  # No legal moves and not in check
