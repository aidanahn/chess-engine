from .piece import Piece
import pygame

class Rook(Piece):
    def __init__(self, color):
        super().__init__(color, 'rook')