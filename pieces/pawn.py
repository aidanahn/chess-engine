from .piece import Piece
import pygame

class Pawn(Piece):
    def __init__(self, color):
        super().__init__(color, 'pawn')