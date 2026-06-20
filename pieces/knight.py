from .piece import Piece
import pygame

class Knight(Piece):
    def __init__(self, color):
        super().__init__(color, 'knight')