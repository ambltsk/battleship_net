#!/usr/bin/python
# coding: utf-8

from Tkinter import *
from var import Var

class Ship:

    def __init__(self, canvas, number, direction = 'h', my=True):
        #number: 0 - 4, 1..2  - 3, 3..5 - 2, 6..9 - 1 палубный
        self.c = canvas
        self.my = my
        self.var = Var()
        self.number = number
        self.direction = direction
        self.see_blocks = []
        self.mini_blocks = []
        self.live = "live" #demage, kill
        self.block_status = []
        self.status = "none"
        self.x = 0
        self.y = 0
        self.drawed = False
        self.selected = False
        self.draw_mini()

    def draw_mini(self):
        if self.my:
            top = self.var.ship_mini_my_top
        else:
            top = self.var.ship_mini_enemy_top
        left = self.get_left()
        if self.number == 0:
            for i in range(4):
                x1 = left + i * self.var.ship_mini_width
                y1 = top
                x2 = x1 + self.var.ship_mini_width
                y2 = y1 + self.var.ship_mini_height
                block = self.c.create_rectangle(x1, y1, x2, y2, \
                    fill = self.var.ship_color, \
                    outline = self.var.ship_outline)
                self.mini_blocks.append(block)
                self.block_status.append("live")
        elif self.number == 1 or self.number == 2:
            for i in range(3):
                x1 = left + i * self.var.ship_mini_width
                y1 = top
                x2 = x1 + self.var.ship_mini_width
                y2 = y1 + self.var.ship_mini_height
                block = self.c.create_rectangle(x1, y1, x2, y2, \
                    fill = self.var.ship_color, \
                    outline = self.var.ship_outline)
                self.mini_blocks.append(block)
                self.block_status.append("live")
        elif self.number >= 3 and self.number <= 5:
            for i in range(2):
                x1 = left + i * self.var.ship_mini_width
                y1 = top
                x2 = x1 + self.var.ship_mini_width
                y2 = y1 + self.var.ship_mini_height
                block = self.c.create_rectangle(x1, y1, x2, y2, \
                    fill = self.var.ship_color, \
                    outline = self.var.ship_outline)
                self.mini_blocks.append(block)
                self.block_status.append("live")
        else:
            x1 = left
            y1 = top
            x2 = x1 + self.var.ship_mini_width
            y2 = y1 + self.var.ship_mini_height
            block = self.c.create_rectangle(x1, y1, x2, y2, \
                fill = self.var.ship_color, \
                outline = self.var.ship_outline)
            self.mini_blocks.append(block)
            self.block_status.append("live")

    def get_left(self):
        left = self.var.ship_mini_position
        if self.number == 1:
            left += 4 * self.var.ship_mini_width + self.var.ship_mini_span
        elif self.number == 2:
            left += 7 * self.var.ship_mini_width + 2 * self.var.ship_mini_span
        elif self.number == 3:
            left += 10 * self.var.ship_mini_width + 3 * self.var.ship_mini_span
        elif self.number == 4:
            left += 12 * self.var.ship_mini_width + 4 * self.var.ship_mini_span
        elif self.number == 5:
            left += 14 * self.var.ship_mini_width + 5 * self.var.ship_mini_span
        elif self.number == 6:
            left += 16 * self.var.ship_mini_width + 6 * self.var.ship_mini_span
        elif self.number == 7:
            left += 17 * self.var.ship_mini_width + 7 * self.var.ship_mini_span
        elif self.number == 8:
            left += 18 * self.var.ship_mini_width + 8 * self.var.ship_mini_span
        elif self.number == 9:
            left += 19 * self.var.ship_mini_width + 9 * self.var.ship_mini_span
        return left

    def draw(self):
        if self.drawed:
            return
        for i in range(len(self.mini_blocks)):
            if self.direction == "h":
                x1 = (i + self.x) * self.var.see_cell_width
                y1 = self.y * self.var.see_cell_height
            else:
                x1 = self.x * self.var.see_cell_width
                y1 = (i + self.y) * self.var.see_cell_height
            x1 += self.var.lr_span + self.var.see_field_border
            y1 += self.var.top_span + self.var.see_field_border
            x2 = x1 + self.var.see_cell_width
            y2 = y1 + self.var.see_cell_height
            block = self.c.create_rectangle(x1, y1, x2, y2, \
                    fill = self.var.ship_color, \
                    outline = self.var.ship_outline)
            self.see_blocks.append(block)
        self.drawed = True
        self.status = "move"

    def set_position(self, x, y):
        if self.status != "move":
            return
        l = len(self.see_blocks)
        self.x, self.y = x, y
        if self.direction == 'h' and x + l > 10:
            self.x = 10 - l
        if self.direction == 'v' and  y + l > 10:
            self.y = 10 - l
        for i in range(len(self.see_blocks)):
            if self.direction == "h":
                x1 = (i + self.x) * self.var.see_cell_width
                y1 = self.y * self.var.see_cell_height
            else:
                x1 = self.x * self.var.see_cell_width
                y1 = (i + self.y) * self.var.see_cell_height
            x1 += self.var.lr_span + self.var.see_field_border
            y1 += self.var.top_span + self.var.see_field_border
            x2 = x1 + self.var.see_cell_width
            y2 = y1 + self.var.see_cell_height
            self.c.coords(self.see_blocks[i], x1, y1, x2, y2)

    def rotate(self):
        if self.status != "move":
            return
        l = len(self.see_blocks)
        if self.direction == 'h':
            self.direction = 'v'
        else:
            self.direction = 'h'
        self.set_position(self.x, self.y)

    def fix(self):
        self.status = "fix"
        self.unselect()

    def select(self):
        for block in self.mini_blocks:
            self.c.itemconfig(block, fill=self.var.ship_select)
        self.selected = True
        if not self.drawed:
            self.draw()

    def unselect(self):
        for i in range(len(self.mini_blocks)):
            if self.block_status[i] == 'live':
                color = self.var.ship_color
            elif self.block_status[i] == 'damage':
                color = self.var.ship_damage
            else:
                color = self.var.ship_kill
            self.c.itemconfig(self.mini_blocks[i], fill=color)
        self.selected = False

    def block_click(self,event):
        pass

    def shoot(self, x, y):
        x1 = self.x
        y1 = self.y
        if self.direction == 'h':
            y2 = y1
            x2 = x1 + (len(self.mini_blocks) - 1)
        else:
            x2 = x1
            y2 = y1 + (len(self.mini_blocks) - 1)
        if x >= x1 and x <= x2 and y >= y1 and y <= y2:
            if self.direction == 'h':
                num = x - x1
            else:
                num = y - y1
            self.block_status[num] = "damage"
            print "shoots number = ", self.number, " block = ", num
            return True, num, self.redraw()
        else:
            return False, None, None

    def redraw(self):
        live = False
        for i in range(len(self.mini_blocks)):
            if self.block_status[i] == "live":
                live = True
        if live:
            for i in range(len(self.mini_blocks)):
                if self.block_status[i] == "live":
                    color = self.var.ship_color
                else:
                    color = self.var.ship_damage
                self.c.itemconfig(self.mini_blocks[i], fill=color)
                if len(self.see_blocks) > 0:
                    self.c.itemconfig(self.see_blocks[i], fill=color)
        else:
            for i in range(len(self.mini_blocks)):
                self.block_status[i] = "kill"
                color = self.var.ship_kill
                self.c.itemconfig(self.mini_blocks[i], fill=color)
                if len(self.see_blocks) > 0:
                    self.c.itemconfig(self.see_blocks[i], fill=color)
        return live
