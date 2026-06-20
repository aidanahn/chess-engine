from .piece import Piece
import pygame

class King(Piece):
    def __init__(self, color):
        super().__init__(color, 'king')