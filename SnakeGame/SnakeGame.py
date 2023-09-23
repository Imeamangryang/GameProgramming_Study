import random
import os
import time
import msvcrt

class Snake:
    def __init__(self, n):
        self.length = n
        self.head = []
        self.tail = []

class SnakeGame:
    direction = {"LEFT":-2, "DOWN":-1, "NON_DIR":0, "UP":1, "RIGHT":2}
    sprite = {"EMPTY":0, "BODY":1, "HEAD":2, "FOOD":3, "BLOCK":4}
    element = {"SPRITE":0, "DIRECTION":1}
    
    def __init__(self, w, h, length, delay):
        self.W = w
        self.H = h
        self.initLen = length
        self.snake = Snake(length)
        self.delay = delay  
        self.board = [[[0]*2 for x in range(self.W)] for y in range(self.H)]
        #self.board[a][b][c]

        self.snake.head = [self.H//2, self.snake.length-1]
        self.snake.tail = [self.H//2, 0]

        for i in range(0, self.snake.length):
            self.board[self.H//2][i][SnakeGame.element["SPRITE"]] = SnakeGame.sprite["BODY"]
            self.board[self.H//2][i][SnakeGame.element["DIRECTION"]] = SnakeGame.direction["RIGHT"]

        self.board[self.H//2][self.snake.length-1][SnakeGame.element["SPRITE"]] = SnakeGame.sprite["HEAD"]
        self.board[self.H//2][self.snake.length-1][SnakeGame.element["DIRECTION"]] = SnakeGame.direction["RIGHT"]

        
        x = random.randint(0, self.W-1)
        y = random.randint(0, self.H-1)
        while self.board[y][x][SnakeGame.element["SPRITE"]]\
              != SnakeGame.sprite["EMPTY"]:
            x = random.randint(0, self.W-1)
            y = random.randint(0, self.H-1)

        self.board[y][x][SnakeGame.element["SPRITE"]] = SnakeGame.sprite["FOOD"]

        #추가코드 장애물 구현
        block_x = random.randint(0, self.W-1)
        block_y = random.randint(0, self.H-1)
        while self.board[block_y][block_x][SnakeGame.element["SPRITE"]]\
              != SnakeGame.sprite["EMPTY"]:
            block_x = random.randint(0, self.W-1)
            block_y = random.randint(0, self.H-1)

        self.board[block_y][block_x][SnakeGame.element["SPRITE"]] = SnakeGame.sprite["BLOCK"]

    def DrawScene(self):
        os.system('cls||clear')
        for x in range(0, self.W+2):
            print("=", end="")
        print("")
        for y in range(0, self.H):
            print("|", end="")
            for x in range(0, self.W):
                if self.board[y][x][SnakeGame.element["SPRITE"]]\
                   == SnakeGame.sprite["BODY"]:
                    print("+", end="")
                elif  self.board[y][x][SnakeGame.element["SPRITE"]]\
                     == SnakeGame.sprite["HEAD"]:
                    print("@", end="")
                elif  self.board[y][x][SnakeGame.element["SPRITE"]]\
                     == SnakeGame.sprite["FOOD"]:
                    print("*", end="")
                elif  self.board[y][x][SnakeGame.element["SPRITE"]]\
                     == SnakeGame.sprite["BLOCK"]:
                    print("O", end="")
                else:
                    print(" ", end="")
            print("|")

        for x in range(0, self.W+2):
            print("=", end="")
        print("")
                

    @staticmethod
    def GetDirection():
        rtn = SnakeGame.direction["NON_DIR"]
        msvcrt.getch()
        ch = msvcrt.getch().decode()
        
        if ch == chr(72):
            print("UP")
            rtn = SnakeGame.direction["UP"]
        elif ch == chr(75):
            print("LEFT")
            rtn = SnakeGame.direction["LEFT"]
        elif ch == chr(77):
            print("RIGHT")
            rtn = SnakeGame.direction["RIGHT"]
        elif ch == chr(80):
            print("DOWN")
            rtn = SnakeGame.direction["DOWN"]

        return rtn
        
    def GameLoop(self):
        self.DrawScene()

        current = SnakeGame.direction["RIGHT"]
        ret = SnakeGame.direction["RIGHT"]
        block_count = 1
        
        while True:
            start = time.time()
            while (time.time() - start) <= self.delay/1000:
                if msvcrt.kbhit():
                    current = SnakeGame.GetDirection()

                    #역방향 입력 막기
                    while True:
                        if (ret + current == 0):
                            current = SnakeGame.GetDirection()
                        else:
                            break
                    ret = current
                    
                    self.board[self.snake.head[0]][self.snake.head[1]][SnakeGame.element["DIRECTION"]] = current #머리 방향 처리
                    self.board[self.snake.head[0]][self.snake.head[1]][SnakeGame.element["SPRITE"]] = SnakeGame.sprite["BODY"] #몸통위치 설정
                    self.board[self.snake.tail[0]][self.snake.tail[1]][SnakeGame.element["SPRITE"]] = SnakeGame.sprite["EMPTY"] #꼬리 스프라이트 제거
                   
                    #FAIL 판정
                    if (self.snake.head[0] == 0 and self.board[self.snake.head[0]][self.snake.head[1]][SnakeGame.element["DIRECTION"]] == SnakeGame.direction["UP"]):
                        break
                    elif (self.snake.head[0] == self.H - 1 and self.board[self.snake.head[0]][self.snake.head[1]][SnakeGame.element["DIRECTION"]] == SnakeGame.direction["DOWN"]):
                        break
                    elif (self.snake.head[1] == 0 and self.board[self.snake.head[0]][self.snake.head[1]][SnakeGame.element["DIRECTION"]] == SnakeGame.direction["LEFT"]):
                        break
                    elif (self.snake.head[1] == self.W - 1 and self.board[self.snake.head[0]][self.snake.head[1]][SnakeGame.element["DIRECTION"]] == SnakeGame.direction["RIGHT"]):
                        break                   


                    #머리 좌표 설정 
                    if (self.board[self.snake.head[0]][self.snake.head[1]][SnakeGame.element["DIRECTION"]] == SnakeGame.direction["RIGHT"]):
                        self.snake.head[1] += 1 
                        
                    elif (self.board[self.snake.head[0]][self.snake.head[1]][SnakeGame.element["DIRECTION"]] == SnakeGame.direction["LEFT"]):
                        self.snake.head[1] -= 1
                       
                    elif (self.board[self.snake.head[0]][self.snake.head[1]][SnakeGame.element["DIRECTION"]] == SnakeGame.direction["UP"]):
                        self.snake.head[0] -= 1
                      
                    elif (self.board[self.snake.head[0]][self.snake.head[1]][SnakeGame.element["DIRECTION"]] == SnakeGame.direction["DOWN"]):
                        self.snake.head[0] += 1
                    
                    #몸통 FAIL판정
                    if (self.board[self.snake.head[0]][self.snake.head[1]][SnakeGame.element["SPRITE"]] == SnakeGame.sprite["BODY"]):
                        break
                    elif (self.board[self.snake.head[0]][self.snake.head[1]][SnakeGame.element["SPRITE"]] == SnakeGame.sprite["BLOCK"]):
                        break
         
                    #빈 곳을 갔을 때            
                    if (self.board[self.snake.head[0]][self.snake.head[1]][SnakeGame.element["SPRITE"]] == SnakeGame.sprite["EMPTY"]):
                        self.board[self.snake.head[0]][self.snake.head[1]][SnakeGame.element["SPRITE"]] = SnakeGame.sprite["HEAD"]

                        #꼬리 방향 처리
                        if (self.board[self.snake.tail[0]][self.snake.tail[1]][SnakeGame.element["DIRECTION"]] == SnakeGame.direction["RIGHT"]):
                            self.board[self.snake.tail[0]][self.snake.tail[1]][SnakeGame.element["DIRECTION"]] = SnakeGame.direction["NON_DIR"]
                            self.snake.tail[1] += 1

                        elif (self.board[self.snake.tail[0]][self.snake.tail[1]][SnakeGame.element["DIRECTION"]] == SnakeGame.direction["LEFT"]):
                            self.board[self.snake.tail[0]][self.snake.tail[1]][SnakeGame.element["DIRECTION"]] = SnakeGame.direction["NON_DIR"]
                            self.snake.tail[1] -= 1

                        elif (self.board[self.snake.tail[0]][self.snake.tail[1]][SnakeGame.element["DIRECTION"]] == SnakeGame.direction["UP"]):
                            self.board[self.snake.tail[0]][self.snake.tail[1]][SnakeGame.element["DIRECTION"]] = SnakeGame.direction["NON_DIR"]
                            self.snake.tail[0] -= 1

                        elif (self.board[self.snake.tail[0]][self.snake.tail[1]][SnakeGame.element["DIRECTION"]] == SnakeGame.direction["DOWN"]):
                            self.board[self.snake.tail[0]][self.snake.tail[1]][SnakeGame.element["DIRECTION"]] = SnakeGame.direction["NON_DIR"]
                            self.snake.tail[0] += 1

                    #먹이를 먹었을 때
                    elif (self.board[self.snake.head[0]][self.snake.head[1]][SnakeGame.element["SPRITE"]] == SnakeGame.sprite["FOOD"]):
                        self.board[self.snake.head[0]][self.snake.head[1]][SnakeGame.element["SPRITE"]] = SnakeGame.sprite["HEAD"]
                        self.snake.length += 1

                        #먹이 생성
                        x = random.randint(0, self.W-1)
                        y = random.randint(0, self.H-1)
                        while self.board[y][x][SnakeGame.element["SPRITE"]]\
                                != SnakeGame.sprite["EMPTY"]:
                            x = random.randint(0, self.W-1)
                            y = random.randint(0, self.H-1)

                        self.board[y][x][SnakeGame.element["SPRITE"]] = SnakeGame.sprite["FOOD"]

                        #장애물 추가 생성
                        if (block_count < 20):
                            block_x = random.randint(0, self.W-1)
                            block_y = random.randint(0, self.H-1)
                            while self.board[block_y][block_x][SnakeGame.element["SPRITE"]]\
                                    != SnakeGame.sprite["EMPTY"]:
                                block_x = random.randint(0, self.W-1)
                                block_y = random.randint(0, self.H-1)

                            self.board[block_y][block_x][SnakeGame.element["SPRITE"]] = SnakeGame.sprite["BLOCK"]
                            block_count += 1

            
            #게임 이벤트처리
            if (1416 <= self.snake.length):
                print("GAME CLEAR")
                break
            elif (self.snake.head[0] == 0 and self.board[self.snake.head[0]][self.snake.head[1]][SnakeGame.element["DIRECTION"]] == SnakeGame.direction["UP"]):
                print("GAME OVER :: Out of The Wall")
                break
            elif (self.snake.head[0] == self.H -1 and self.board[self.snake.head[0]][self.snake.head[1]][SnakeGame.element["DIRECTION"]] == SnakeGame.direction["DOWN"]):
                print("GAME OVER :: Out of The Wall")
                break
            elif (self.snake.head[1] == 0 and self.board[self.snake.head[0]][self.snake.head[1]][SnakeGame.element["DIRECTION"]] == SnakeGame.direction["LEFT"]):
                print("GAME OVER :: Out of The Wall")
                break
            elif (self.snake.head[1] == self.W -1 and self.board[self.snake.head[0]][self.snake.head[1]][SnakeGame.element["DIRECTION"]] == SnakeGame.direction["RIGHT"]):
                print("GAME OVER :: Out of The Wall")
                break
            elif (self.board[self.snake.head[0]][self.snake.head[1]][SnakeGame.element["SPRITE"]] == SnakeGame.sprite["BODY"]):
                print("GAME OVER :: Hit Own Body")
                break
            elif (self.board[self.snake.head[0]][self.snake.head[1]][SnakeGame.element["SPRITE"]] == SnakeGame.sprite["BLOCK"]):
                print("GAME OVER :: Hit The Block")
                break

            self.DrawScene()
            print("Score: {}".format(self.snake.length - self.initLen))

if __name__ == '__main__' :
    game = SnakeGame(60, 24, 4, 300)
    game.GameLoop()