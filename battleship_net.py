#!/usr/bin/python2
# coding: utf-8

from Tkinter import *
from random import *
from time import time
import socket
import threading

from lib.var import *
from lib.blocks import *
from lib.ships import *

class Game:
    """
    Основной класс игры. Содержит интерфейс и логику игры
    """
    def __init__(self):
        """
        Инициализация игры, настройка основного окна программы
        """
        self.run = True
        self.root = Tk()
        self.root.title("Морской бой по сети")
        self.root.resizable(0,0)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.var = Var()
        self.target = Coord(0, 0)
        self.ship_select = 0
        self.game_status = "none" #set, ready, run, finish
        self.enemy_status = "none" #join, ready, wite
        self.step = "pause" 
        self.canva_w = 0
        self.canva_h = 0
        #Переменные подключения
        self.sock = None #Сокет
        self.conn = None #Соединение клиента
        self.addr = None #Адрес клиента
        self.server = None #Выступаем в качестве сервера
        self.msg = None #Сообщения между клиентом и сервером
        self.potok = None #Поток чтения сообщений по сети
        
        self.interface()

    def on_close(self):
        """
        При закрытии окна закрывает сокеты
        """
        if self.sock:
            self.sock.close()
        self.run = False
        self.root.destroy()

    def communication(self):
        """
        Функция поток получения сообщений от клиента или сервера
        """
        while self.run:
            if self.server:
                self.msg = self.conn.recv(1024)
            else:
                self.msg = self.sock.recv(1024)

    def send_msg(self, msg):
        if self.server:
            self.conn.send(msg)
        else:
            self.sock.send(msg)

    def mainloop(self):
        """
        Игровой цикл игры
        """
        while self.run:
            if self.msg:
                print "net:>>> ", self.msg
                if self.msg == "ready":
                    if self.game_status == "set" or self.game_status == "wite":
                        self.enemy_status = "ready"
                        self.lbl_info["text"] = "Противник готов"
                    elif self.game_status == "ready":
                        self.game_status = "run"
                        self.lbl_info["text"] = "Игра началась..."
                        if self.server:
                            if randint(0, 10) % 2 == 0:
                                self.step = "me"
                                self.lbl_info["text"] = "Вы ходите превым"
                                self.send_msg("first me") #Начинает сервер
                            else:
                                self.step = "enemy"
                                self.lbl_info["text"] = "Первым ходит противник"
                                self.send_msg("first you") #Начинает клиент
                elif "first" in self.msg:
                    #Сообщение от сервера кто ходит первым
                    if "you" in self.msg:
                        self.step = "me"
                        self.lbl_info["text"] = "Вы ходите превым"
                    else:
                        self.step = "enemy"
                        self.lbl_info["text"] = "Первым ходит противник"
                elif "shoot" in self.msg:
                    self.lbl_info["text"] = "По нам стрельнули"
                    self.shoot_proccess(self.msg)
                elif self.msg == "miss":
                    self.lbl_info["text"] = "Мы промазали переход"
                    self.miss_proccess()
                elif self.msg == "demage":
                    self.lbl_info["text"] = "Мы попали"
                    self.demage_proccess()
                elif "kill" in self.msg:
                    self.lbl_info["text"] = "Корабль противника потоплен"
                    self.kill_proccess(self.msg)
                elif self.msg == "switch":
                    if self.step == "me":
                        self.step = "enemy"
                    else:
                        self.step = "me"
                elif self.msg == "win":
                    self.lbl_info["text"] = "Конец игры"
                    self.game_status = "finish"
                    self.canvas.create_text(self.canva_w // 2, self.canva_h // 2, 
                            text="Поражение...", fill="red", font="Verdana 60")
                self.msg = None 
            """
            dmsg = "Статусы: Игра-" + self.game_status
            dmsg += " Противник-" +self.enemy_status
            dmsg += " Ход-" + self.step
            self.lbl_debug["text"] = dmsg
            """
            self.root.update()

    def interface(self):
        """
        Настройка интерфейса окна
        """
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
        self.canva_w = 2 * self.var.lr_span + 2 * self.var.see_field_width + self.var.center_span
        self.canva_h = self.var.top_span + self.var.bottom_span + self.var.see_field_height
        self.canvas = Canvas(self.root, \
            width=self.canva_w, height=self.canva_h, bg= self.var.field_color)
        self.canvas.pack(side="bottom")
        self.canvas.bind("<Button-1>", self.lbutton_click)
        self.canvas.bind("<Button-3>", self.rbutton_click)
        self.canvas.bind("<Motion>", self.mouse_move)
        self.lbl_info = Label(text="Создайте или подключитесь к игре если она уже создана")
        self.lbl_info.pack(side="bottom", fill="x")
        """
        self.lbl_debug = Label(text="Debag", fg='blue')
        self.lbl_debug.pack(side="bottom", fill="x")
        """
        self.set_see()
        self.set_label()
        self.canvas.create_text(5, self.var.ship_mini_my_top, \
            text = "Мой флот", anchor="nw")
        self.canvas.create_text(5, self.var.ship_mini_enemy_top, \
            text = "Вражеский флот", anchor="nw")
        self.set_ship()

    def set_see(self):
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

    def set_label(self):
        for i in range(10):
            x1 = self.var.lr_span + i * self.var.see_cell_width + \
                        self.var.see_cell_width // 2 + self.var.see_field_border
            x2 = x1 + self.var.center_span + self.var.see_field_width
            y = self.var.top_span
            self.canvas.create_text(x1, y, text=self.var.label[i], anchor="s", fill="gray30")
            self.canvas.create_text(x2, y, text=self.var.label[i], anchor="s", fill="gray30")
            x1 = self.var.lr_span
            x2 = x1 + self.var.see_field_width + self.var.center_span
            y = self.var.top_span + self.var.see_cell_height // 2 + \
                        self.var.see_field_border + i * self.var.see_cell_height
            self.canvas.create_text(x1, y, text=str(i), anchor="e", fill="gray30")
            self.canvas.create_text(x2, y, text=str(i), anchor="e", fill="gray30")

    def lbutton_click(self, event):
        """
        Щелчком ЛКМ поддтверждаем место положения корабля на поле,
        переходим к растановке следующего корабля
        """
        if self.game_status ==  "set":
            self.my_ships[self.ship_select].fix()
            self.ship_select += 1
            if self.ship_select > 9:
                self.game_status = "wite"
                self.btn_ready["relief"] = "raised"
                self.lbl_info["text"] = "Жмите <Готов>"
            else:
                self.my_ships[self.ship_select].select()

    def rbutton_click(self, event):
        """
        щелчком ПКМ вращаем корабль во время установки на поле
        """
        if self.game_status == "set":
            for ship in self.my_ships:
                if ship.selected:
                    ship.rotate()

    def mouse_move(self, event):
        """
        Перемещение корабля по полю в режиме растановки кораблей
        """
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
        """
        Обработка щелчка ЛКМ по полю противника -> выстрел
        """
        if self.game_status != "run" or self.step != "me":
            return
        x = event.x - (self.var.lr_span + self.var.see_field_border + \
                self.var.see_field_width + self.var.center_span)
        y = event.y - (self.var.top_span + self.var.see_field_border)
        x = x // self.var.see_cell_width
        y = y // self.var.see_cell_height
        mes = "shoot " + str(x) + " " + str(y)
        self.target.set_coord((x, y))
        self.send_msg(mes)


    def create_game(self):
        """
        Создание игры
        """
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
        """
        Подключение к игре
        """
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
        """
        Начало игры с растановки кораблей
        """
        self.enemy_status = "join"
        self.lbl_info["text"] = "Расставтье свой флот"        
        self.btn_create_game["relief"] = "sunken"
        self.btn_join_game["relief"] = "sunken"
        self.game_status = "set"
        self.my_ships[self.ship_select].select()

    def ready(self):
        """
        Готовность к бою, после растанновки всех кораблей
        """
        if self.btn_ready["relief"] == "sunken":
            return
        self.btn_ready["relief"] = "sunken"
        self.game_status = "ready"
        self.send_msg("ready")
        if self.enemy_status == 'join':
            self.lbl_info["text"] = "Ждем готовности противника"
        elif self.enemy_status == 'ready':
            self.game_status = 'run' 
            self.lbl_info["text"] = "Игра началась..."
            if self.server:
                if randint(0, 10) % 2 == 0:
                    self.step = "me"
                    self.lbl_info["text"] = "Вы ходите превым"
                    self.send_msg("first me") #Начинает сервер
                else:
                    self.step = "enemy"
                    self.lbl_info["text"] = "Первым ходит противник"
                    self.send_msg("first you") #Начинает клиент

    def shoot_proccess(self, msg):
        """
        Обработчик выстрелов 
        """
        parts = msg.split(' ')
        if len(parts) < 3:
            return
        x = int(parts[1])
        y = int(parts[2])
        for ship in self.my_ships:
            hit, info = ship.shoot(x, y)
            if hit:
                break
        if hit:
            if info["kill"]:
                self.lbl_info["text"] = "Наш корабль потоплен"
                answer = ['kill',]
                answer.append(str(info["number"]))
                answer.append(str(info["x"]))
                answer.append(str(info["y"]))
                answer.append(info["direction"])
                self.send_msg(' '.join(answer))
                print "me kill ", info["number"]
            else:
                self.lbl_info["text"] = "По нам попали"
                self.send_msg('demage')
                print "me demage ", info["number"], ":", info["block"]
        else:
            self.lbl_info["text"] = "Мазила!!! Наш ход..."
            self.send_msg('miss')
            index = y * 10 + x
            self.canvas.itemconfig(self.my_blocks[index], fill=self.var.see_miss)
            print "me miss"

    def miss_proccess(self):
        #Отметим промах на карте противника
        x = self.target.x
        y = self.target.y
        i = y * 10 + x
        self.canvas.itemconfig(self.enemy_blocks[i], fill=self.var.see_miss)
        self.send_msg("switch")
        self.step = "enemy"
    
    def demage_proccess(self):
        #Отметим попадание
        x = self.target.x
        y = self.target.y
        i = y * 10 + x
        self.canvas.itemconfig(self.enemy_blocks[i], fill=self.var.ship_damage)
    
    def kill_proccess(self, msg):
        #Отметим пораженный корабль
        parts = msg.split(' ')
        number = int(parts[1])
        x = int(parts[2])
        y = int(parts[3])
        direct = parts[4]
        print '*** ', number, ' ', x, ':', y, ' ', direct
        for ship in self.enemy_ships:
            if ship.number == number:
                ship.kill_mini()
                break
        if number == 0:
            l = 4
        elif number > 0 and number <= 2:
            l = 3
        elif number > 2 and number <= 5:
            l = 2
        else:
            l = 1
        for i in range(l):
            pos = y * 10 + x
            self.canvas.itemconfig(self.enemy_blocks[pos], fill=self.var.ship_kill)
            if direct == "h":
                x += 1
            else:
                y += 1
        win = True
        for ship in self.enemy_ships:
            if ship.live != "kill":
                win = False
        if win:
            self.send_msg('win')
            self.game_status = "finish"
            self.canvas.create_text(self.canva_w // 2, self.canva_h // 2, \
                    text="Победа!!!", fill="green", font="Verdana 60")



if __name__ == "__main__":
    g = Game()
    g.mainloop()
