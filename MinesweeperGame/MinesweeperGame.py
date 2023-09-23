import tkinter as tk
from tkinter import messagebox
import numpy as np
import random

class Game(tk.Frame):
    mine = {"NONMINE":0, "MINE":1}
    mark = {"NONMARK":0, "MARK":1}
    object = {"0":0, "1":1, "2":2, "3":3, "4":4, "5":5, "6":6, "7":7, "8":8, "MINE":9}
    element = {"BOMB":0, "OBJECT":1, "MARK":2}
    def __init__(self, width = 9, height = 9, bomb = 10):
        self.root = tk.Tk()
        self.root.title('Hello, Mine!')
        super(Game, self).__init__(self.root)

        #메뉴바 처리
        self.menubar = tk.Menu(self.root)
        self.filemenu = tk.Menu(self.menubar, tearoff = 0)
        self.filemenu.add_command(label = "9*9", command = self.begin)
        self.filemenu.add_command(label = "16*16", command = self.normal)
        self.filemenu.add_command(label = "30*16", command = self.hard)
        self.filemenu.add_separator()
        self.filemenu.add_command(label = "Exit", command = self.root.destroy)
        self.menubar.add_cascade(label = "File", menu = self.filemenu)
        self.root.config(menu = self.menubar)
        

        self.square = 40
        self.column = width
        self.row = height
        self.bomb = bomb
        self.flag = 0
        self.score = bomb

        self.check = np.arange(width*height).reshape(height, width)
        self.check[0][0] = 0
        self.check = [[0] * width for j in range(height)]

        self.pattern = np.arange(width*height*3).reshape(height, width, 3)
        self.pattern[0][0][0] = Game.mine["NONMINE"] # 0 : 클릭체크, 1 : 오브젝트 표시
        self.pattern = [[[0]*3 for i in range(width)] for k in range(height)]

        self.mapwidth = width * self.square
        self.mapheight = height * self.square
        self.canvas = tk.Canvas(self, bg = '#aaafff', width = self.mapwidth, height = self.mapheight)
        self.canvas.pack()
        self.pack()
        self.canvas.bind('<Button-1>', self.left_button)
        self.canvas.bind('<Button-3>', self.right_button)
        self.create_mine()
        self.board_activate()

    # 메뉴 9*9
    def begin(self):
        self.root.destroy()
        game = Game(9, 9, 10)
        
    # 메뉴 16*16
    def normal(self):
        self.root.destroy()
        game = Game(16, 16, 40)

    # 메뉴 30*16
    def hard(self):
        self.root.destroy()
        game = Game(30, 16, 99)

    # 보드 생성 함수
    def board_activate(self):
        for x in range(self.square, self.mapwidth, self.square):
            self.canvas.create_line(x, 0, x, self.mapheight, fill = '#000000')
        for y in range(self.square, self.mapheight, self.square):
            self.canvas.create_line(0, y, self.mapwidth, y, fill = '#000000')
        for x in range(self.column):
            for y in range(self.row):
                if self.pattern[y][x][Game.element["BOMB"]] == Game.mine["MINE"]:
                    continue
                else:
                    for yy in range(-1, 2):
                        for xx in range(-1, 2):
                            if x + xx < 0: continue
                            if x + xx >= self.column: continue

                            if y + yy < 0: continue
                            if y + yy >= self.row: continue

                            if self.pattern[y+yy][x+xx][2] != 0:
                                continue

                            if self.pattern[y+yy][x+xx][Game.element["BOMB"]] == Game.mine["MINE"]:
                                self.pattern[y][x][Game.element["OBJECT"]] += 1

    def create_mine(self):
        for i in range(self.bomb):
            x = random.randint(0, self.column - 1)
            y = random.randint(0, self.row - 1)
            while self.pattern[y][x][Game.element["BOMB"]] != Game.mine["NONMINE"]:
                x = random.randint(0, self.column - 1)
                y = random.randint(0, self.row - 1)
            self.pattern[y][x][Game.element["BOMB"]] = Game.mine["MINE"]
            self.pattern[y][x][Game.element["OBJECT"]] = Game.object["MINE"]

    def check_board(self):
        for x in range(self.column):
            for y in range(self.row):
                if self.check[y][x] == 0:
                    return False
                    break
                else:
                    return True

    # 왼쪽 클릭 이벤트처리
    def left_button(self, event):
        x = event.x//self.square
        y = event.y//self.square

        # 폭탄을 클릭했을 때
        if self.pattern[y][x][Game.element["BOMB"]] == Game.mine["MINE"] and self.check[y][x] == 0:
            self.canvas.create_text(x * self.square + (self.square/2), y * self.square + (self.square/2), text = "⚛", font = ('Arial', int(self.square/2)), fill = 'red')
            self.check[y][x] = 1
            for x in range(self.column):
                for y in range(self.row):
                    if self.check[y][x] == 0:
                        if self.pattern[y][x][Game.element["OBJECT"]] == Game.object["MINE"]:
                            self.canvas.create_text(x * self.square + (self.square/2), y * self.square + (self.square/2), text = "⚛", font = ('Arial', int(self.square/2)), fill = 'blue')
                        else:
                            self.canvas.create_text(x * self.square + (self.square/2), y * self.square + (self.square/2), text = self.pattern[y][x][Game.element["OBJECT"]], font = ('Arial', int(self.square/2)), fill = 'blue')
            tk.messagebox.showinfo('Lose', 'You Failed!')
            exit(0)

        # 0이 아닌 숫자를 입력했을 때
        if self.pattern[y][x][Game.element["OBJECT"]] != 0 and self.check[y][x] == 0:
            self.check[y][x] = 1;
            self.canvas.create_text(x * self.square + (self.square/2), y * self.square + (self.square/2), text = self.pattern[y][x][Game.element["OBJECT"]], font = ('Arial', int(self.square/2)))

        # 0을 클릭했을 때
        if self.pattern[y][x][Game.element["OBJECT"]] == 0 and self.check[y][x] == 0:
            self.detect_region(x,y)

        # 끝나는 거 판정
        if self.score == 0:
            if self.check_board() == True:
                tk.messagebox.showinfo('Win', 'You win!')

    # 오른쪽 클릭 이벤트 처리 (깃발 꽂기)
    def right_button(self, event):
        x = event.x//self.square
        y = event.y//self.square
        # 깃발 해제
        if self.pattern[y][x][Game.element["MARK"]] == Game.mark["MARK"]:
            self.pattern[y][x][Game.element["MARK"]] = Game.mark["NONMARK"]
            self.flag -= 1
            self.canvas.delete(self.check[y][x])
            self.check[y][x] = 0
        # 깃발 생성
        else:
            if self.flag < self.bomb:
                self.check[y][x] = self.canvas.create_text(x * self.square + (self.square/2), y * self.square + (self.square/2), text = '⚐', font = ('Arial', int(self.square/2)), fill = 'red')
                self.pattern[y][x][Game.element["MARK"]] = Game.mark["MARK"]
                self.flag += 1
                if self.pattern[y][x][Game.element["MARK"]] == self.pattern[y][x][Game.element["BOMB"]]:
                    self.score -= 1

    # 클릭 지역 탐지
    def detect_region(self, x, y):
        for yy in range(-1, 2):
            for xx in range(-1, 2):
                if x + xx < 0: continue
                if x + xx >= self.column: continue

                if y + yy < 0: continue
                if y + yy >= self.row: continue

                if self.pattern[y+yy][x+xx][2] != 0:
                    continue
                if self.pattern[y][x][Game.element["OBJECT"]] != 0:
                    self.check[y][x] = 1
                    self.canvas.create_text(x * self.square + (self.square/2), y * self.square + (self.square/2), text = self.pattern[y][x][Game.element["OBJECT"]], font = ('Arial', int(self.square/2)))
                elif self.pattern[y][x][Game.element["OBJECT"]] == 0 and self.check[y+yy][x+xx] == 0:
                    self.check[y][x] = 1
                    self.canvas.create_text(x * self.square + (self.square/2), y * self.square + (self.square/2), text = self.pattern[y][x][Game.element["OBJECT"]], font = ('Arial', int(self.square/2)))
                    self.detect_region(x+xx, y+yy)


if __name__ == '__main__':
    game = Game()
    game.mainloop()
