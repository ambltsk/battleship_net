#!/usr/bin/python2
# coding: utf-8

from Tkinter import *
from random import *
from time import time
import socket
import threading

from lib.var import Var
from lib.blocks import *
from lib.ships import *

class Game:

    def __init__(self):
        self.root = Tk()
        self.root.title("Морской бой по сети")
        self.root.resizable(0,0)
        self.var = Var()
        self.ship_select = 0
        self.game_status = "none" #set, ready, ready10, ready01, run, finish
        self.step = "pause" 
        #Переменные подключения
        self.sock = None #Сокет
        self.conn = None #Соединение клиента
        self.addr = None #Адрес клиента
        self.server = None #Выступаем в качестве сервера
        self.msg = None #Сообщения между клиентом и сервером
        self.potok = None #Поток чтения сообщений по сети
        
        self.interface()

    def communication(self):
        while True:
            if self.server:
                self.msg = self.conn.recv(1024)
            else:
                self.msg = self.sock.recv(1024)

    def mainloop(self):
        while 1:
            if self.msg:
                if self.msg == "ready":
                    if self.game_status == "ready":
                        self.game_status = "ready01"
                        self.lbl_info["text"] = "Противник готов"
                    elif self.game_status == "ready10":
                        self.game_status = "run"
                        self.lbl_info["text"] = "Игра началась..."
                        if self.server:
                            if randint(0, 10) % 2 == 0:
                                self.step = "me"
                                self.lbl_info["text"] = "Вы ходите превым"
                                self.conn.send("first me") #Начинает сервер
                            else:
                                self.step = "enemy"
                                self.lbl_info["text"] = "Первым ходит противник"
                                self.conn.send("first you") #Начинает клиент
                elif "first" in self.msg:
                    if "you" in self.msg:
                        self.step = "me"
                        self.lbl_info["text"] = "Вы ходите превым"
                    else:
                        self.step = "enemy"
                        self.lbl_info["text"] = "Первым ходит противник"
                print self.msg
                self.msg = None
            self.root.update()

    def interface(self):
        self.frame_buttons = Frame(self.root, bg='yellow', bd=5)
        self.btn_create_game = Button(self.frame_buttons, text="Создать игру", \
                command=self.create_game)
        self.btn_create_game.pack(side='left')
        self.btn_join_game = Button(self.frame_buttons, text="Присоеденится к игре", \
                command=self.join_game)
        self.btn_join_game.pack(side="left")
        self.btn_ready = Button(self.frame_buttons, text="Готов", relief='sunken',
                command=self.ready)
        self.btn_ready.pack(side="left")
        self.frame_buttons.pack(side="top", fill="x")
        self.canvas = Canvas(self.root, \
            width=2 * self.var.lr_span + 2 * self.var.see_field_width + self.var.center_span, \
            height=self.var.top_span + self.var.bottom_span + self.var.see_field_height, \
            bg= self.var.field_color)
        self.canvas.pack(side="bottom")
        self.canvas.bind("<Button-1>", self.lbutton_click)
        self.canvas.bind("<Button-3>", self.rbutton_click)
        self.canvas.bind("<Motion>", self.mouse_move)
        self.lbl_info = Label(text="Создайте или подключитесь к игре если она уже создана")
        self.lbl_info.pack(side="bottom", fill="x")
        self.draw_see()
        self.canvas.create_text(5, self.var.ship_mini_my_top, \
            text = "Мой флот", anchor="nw")
        self.canvas.create_text(5, self.var.ship_mini_enemy_top, \
            text = "Вражеский флот", anchor="nw")
        self.set_ship()

    def draw_see(self):
        self.my_see = See(self.canvas).index
        self.enemy_see = See(self.canvas, False).index
        self.my_blocks = []
        for r in range(10):
            for c in range(10):
                block = Block(self.canvas, r, c)
                self.my_blocks.append(block.index)
        self.enemy_blocks = []
        for r in range(10):
            for c in range(10):
                block = Block(self.canvas, r, c, my=False, tag="block")
                self.enemy_blocks.append(block.index)
                self.canvas.tag_bind("block", "<Button-1>", \
                    self.enemy_click)

    def set_ship(self):
        self.my_ships = []
        for i in range(10):
            ship = Ship(self.canvas, i)
            self.my_ships.append(ship)
        
        self.enemy_ships = []
        for i in range(10):
            ship = Ship(self.canvas, i, my=False)
            self.enemy_ships.append(ship)

    def lbutton_click(self, event):
        if self.game_status ==  "set":
            self.my_ships[self.ship_select].fix()
            self.ship_select += 1
            if self.ship_select > 9:
                self.game_status = "ready"
                self.btn_ready["relief"] = "raised"
                self.lbl_info["text"] = "Жмите <Готов>"
            else:
                self.my_ships[self.ship_select].select()

    def rbutton_click(self, event):
        if self.game_status == "set":
            for ship in self.my_ships:
                if ship.selected:
                    ship.rotate()

    def mouse_move(self, event):
        if self.game_status == "set":
            for ship in self.my_ships:
                if ship.selected:
                    if event.x < self.var.lr_span + self.var.see_field_border:
                        x = 0
                    elif event.x > self.var.lr_span + self.var.see_field_border + \
                                        self.var.see_field_width:
                        x = 9
                    else:
                        x = event.x
                        x -= self.var.lr_span + self.var.see_field_border
                        x = x // self.var.see_cell_width
                    if event.y < self.var.top_span + self.var.see_field_border:
                        y = 0
                    elif event.y > self.var.top_span + self.var.see_field_border + \
                                        self.var.see_field_width:
                        y = 9
                    else:
                        y = event.y
                        y -= self.var.top_span + self.var.see_field_border
                        y = y // self.var.see_cell_height
                    ship.set_position(x, y)

    def enemy_click(self, event):
        if self.game_status != "run":
            return
        if self.step != "me":
            return
        x = event.x - (self.var.lr_span + self.var.see_field_border + \
                self.var.see_field_width + self.var.center_span)
        y = event.y - (self.var.top_span + self.var.see_field_border)
        x = x // self.var.see_cell_width
        y = y // self.var.see_cell_height
        mes = "shoot " + str(x) + " " + str(y)
        if self.server:
            self.conn.send(mes)
        else:
            self.sock.send(mes)

    def create_game(self):
        if self.btn_create_game["relief"] == "sunken":
            return
        self.lbl_info["text"]="Ждем подключение клиента"
        self.sock = socket.socket()
        self.sock.bind(('localhost', 1978))
        self.sock.listen(1)
        self.conn, self.addr = self.sock.accept()
        print "connected ", self.addr
        self.server = True
        self.potok = threading.Thread(target= self.communication)
        self.potok.start()
        self.set_game()

    def join_game(self):
        if self.btn_create_game["relief"] == "sunken":
            return
        self.lbl_info["text"] = "Ждем ответа от сервера"
        self.sock = socket.socket()
        self.sock.connect(('localhost', 1978))
        self.server = False
        self.potok = threading.Thread(target= self.communication)
        self.potok.start()
        self.set_game()

    def set_game(self):
        self.lbl_info["text"] = "Расставтье свой флот"        
        self.btn_create_game["relief"] = "sunken"
        self.btn_join_game["relief"] = "sunken"
        self.game_status = "set"
        self.my_ships[self.ship_select].select()

    def ready(self):
        if self.btn_ready["relief"] == "sunken":
            return
        self.btn_ready["relief"] = "sunken"
        if self.server:
            self.conn.send('ready')
        else:
            self.sock.send('ready')
        if self.game_status == 'ready':
            self.game_status = 'ready10'
            self.lbl_info["text"] = "Ждем готовности противника"
        elif self.game_status == 'ready01':
            self.game_status = 'run' 
            self.lbl_info["text"] = "Игра началась..."
        

if __name__ == "__main__":
    g = Game()
    g.mainloop()
