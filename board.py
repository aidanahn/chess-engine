from pieces import Rook, Knight, Bishop, Pawn, King, Queen

class Board:
    def __init__(self):
        self.board = [[None] * 8 for _ in range(8)]
        self.board[0] = [
            Rook('black'), Knight('black'), Bishop('black'), Queen('black'), 
            King('black'), Bishop('black'), Knight('black'), Rook('black')
        ]
        self.board[7] = [
            Rook('white'), Knight('white'), Bishop('white'), Queen('white'), 
            King('white'), Bishop('white'), Knight('white'), Rook('white')
        ]
        self.board[1] = [Pawn('black') for _ in range(8)]
        self.board[6] = [Pawn('white') for _ in range(8)]