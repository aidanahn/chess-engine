from .piece import Piece
import pygame

class Queen(Piece):
    def __init__(self, color):
        super().__init__(color, 'queen')