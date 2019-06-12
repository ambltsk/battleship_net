#!/usr/bin/python
# coding: utf-8

class Var:

    def __init__(self):
        self.see_cell_width = 25
        self.see_cell_height = 25
        self.see_field_border = 3
        self.see_field_width = self.see_cell_width * 10 + 2 *self.see_field_border
        self.see_field_height = self.see_cell_height * 10 + 2 *self.see_field_border
        self.top_span = 15
        self.bottom_span = 60
        self.lr_span = 15
        self.center_span = 20
        self.ship_mini_width = 15
        self.ship_mini_height = 15
        self.ship_mini_position = 130
        self.ship_mini_span =10
        self.ship_mini_my_top = self.top_span + self.see_field_height + 10
        self.ship_mini_enemy_top = self.ship_mini_my_top + self.ship_mini_height + \
                self.ship_mini_span
        
        self.field_color = 'CadetBlue1'
        self.see_color = 'SteelBlue1'
        self.see_outline = 'Blue'
        self.see_active_fill = 'SteelBlue3'
        self.see_miss = 'light cyan'
        self.ship_color = "olive drab"
        self.ship_damage = "yellow"
        self.ship_kill = "red"
        self.ship_outline = "gold3"
        self.ship_select = "green"
        
        self.label = ['А','Б','В','Г','Д','Е','Ж','З','И','К']

class Coord:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def set_coord(self, crd):
        self.x = crd[0]
        self.y = crd[1]
