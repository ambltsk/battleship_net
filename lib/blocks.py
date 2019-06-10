#!/usr/bin/python
# coding: utf-8

from Tkinter import *
from var import Var

class Block:

    def __init__(self, canvas, row, col, my=True, tag="empty"):
        self.c = canvas
        self.row = row
        self.col = col
        self.my = my
        self.var = Var()
        self.tag = tag
        self.index = None
        self.draw()

    def draw(self):
        for r in range(10):
            for c in range(10):
                x1 = self.var.lr_span + self.var.see_field_border + \
                    c * self.var.see_cell_width
                y1 = self.var.top_span + self.var.see_field_border + \
                    r * self.var.see_cell_height
                if not self.my:
                    x1 += self.var.center_span + self.var.see_field_width
                x2 = x1 + self.var.see_cell_width
                y2 = y1 + self.var.see_cell_height
                self.index = self.c.create_rectangle(x1, y1, x2, y2, \
                    fill = self.var.see_color, outline = self.var.see_outline, \
                    width = 1, activefill=self.var.see_active_fill, tag=self.tag )

class See:

    def __init__(self, canvas, my=True):
        self.c = canvas
        self.my = my
        self.var = Var()
        if my:
            x = self.var.lr_span
        else:
            x = self.var.lr_span + self.var.center_span + self.var.see_field_width
        self.index = self.c.create_rectangle(x, self.var.top_span, \
            x + self.var.see_field_width, \
            self.var.top_span + self.var.see_field_height, \
            fill = self.var.see_color, outline = self.var.see_color)
