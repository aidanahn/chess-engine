from .piece import Piece
import pygame

class Bishop(Piece):
    def __init__(self, color):
        super().__init__(color, 'bishop')