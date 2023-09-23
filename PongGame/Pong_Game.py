import tkinter as tk
import math
import random
import numpy as np

class GameObject(object):
    def __init__(self, canvas, item):
        self.canvas = canvas
        self.item = item

    def get_position(self):
        return self.canvas.coords(self.item)

    def move(self, x, y):
        self.canvas.move(self.item, x, y)

    def delete(self):
        self.canvas.delete(self.item)

class Ball(GameObject):
    def __init__(self, canvas, x, y):
        self.radius = 10
        self.direction = [1 / math.sqrt(2), -1 / math.sqrt(2)]
        self.speed = 10
        self.ball_image = tk.PhotoImage(file = 'ball2.png')
        self.item = canvas.create_image(x, y, anchor=tk.CENTER, image=self.ball_image)
        super(Ball, self).__init__(canvas, self.item)


    def update(self):
        coords = self.get_position()
        width = self.canvas.winfo_width()
        if coords[0] <= 0 or coords[2] >= width:
            self.direction[0] *= -1
        if coords[1] <= 0:
            self.direction[1] *= -1
        x = self.direction[0] * self.speed
        y = self.direction[1] * self.speed
        self.move(x, y)

    def collide(self, game_objects):
        coords = self.get_position()
        x = (coords[0] + coords[2]) * 0.5
        if len(game_objects) > 1:
            self.direction[1] *= -1
        elif len(game_objects) == 1: # 충돌이 발생했을 때
            game_object = game_objects[0] 
            coords = game_object.get_position() # paddle과 brick의 위치
            if x > coords[2]: # 오브젝트 오른쪽
                self.direction[0] *= 1
            elif x < coords[0]: # 오브젝트 왼쪽
                self.direction[0] *= -1
            else:
                self.direction[1] *= -1

            # 원의 중점
            ball_coords = self.get_position()
            x = (ball_coords[0] + ball_coords[2]) * 0.5
            y = (ball_coords[1] + ball_coords[3]) * 0.5

            intersection_point = [0, 0, 0, 0]
            # coords[0] = a1 x = a , coords[1] = b1 y= b, coords[2] = a2, coords[3] = b2

            # x = a1 판별식
            discriminant_x1 = -(math.pow(coords[0], 2)) + (2 * x * coords[0]) - (math.pow(x, 2)) + (math.pow(self.radius, 2))
            if (discriminant_x1 > 0):
                #교점 구하기
                y1 = y - math.sqrt(math.pow(self.radius, 2) + math.pow(coords[0], 2) - (2 * x * coords[0]) + math.pow(x, 2))
                y2 = y + math.sqrt(math.pow(self.radius, 2) + math.pow(coords[0], 2) - (2 * x * coords[0]) + math.pow(x, 2))
                # 리스트에 교점 저장
                if (coords[1] < y1 and y1 < coords[3]): # y1좌표가 b1과 b2사이에 있을 경우
                    intersection_point[0] = coords[0]
                    intersection_point[1] = y1
                    if (coords[1] < y2 and y2 < coords[3]):# y2좌표가 b1과 b2사이에 있을 경우
                        intersection_point[2] = coords[0]
                        intersection_point[3] = y2
                elif (coords[1] < y2 and y2 < coords[3]): # y1좌표가 b1과 b2사이에 없고 y2좌표가 b1과 b2사이에 있을 경우
                    intersection_point[0] = coords[0]
                    intersection_point[1] = y2


            # y = b1 판별식
            discriminant_y1 = -(math.pow(coords[1], 2)) + (2 * y * coords[1]) - (math.pow(y, 2)) + (math.pow(self.radius, 2))
            if (discriminant_y1 > 0):
                #교점 구하기
                x1 = x - math.sqrt(math.pow(self.radius, 2) + math.pow(coords[1], 2) - (2 * y * coords[1]) + math.pow(y, 2))
                x2 = x + math.sqrt(math.pow(self.radius, 2) + math.pow(coords[1], 2) - (2 * y * coords[1]) + math.pow(y, 2))
                #리스트에 교점 저장
                if (coords[0] < x1 and x1 < coords[2]):
                    intersection_point[2] = x1
                    intersection_point[3] = coords[1]
                    if (coords[0] < x2 and x2 < coords[2]):
                        intersection_point[0] = x2
                        intersection_point[1] = coords[1]
                elif (coords[0] < x2 and x2 < coords[2]):
                    intersection_point[2] = x2
                    intersection_point[3] = coords[1]


            # x = a2 판별식
            discriminant_x2 = -(math.pow(coords[2], 2)) + (2 * x * coords[2]) - (math.pow(x, 2)) + (math.pow(self.radius, 2))
            if (discriminant_x2 > 0):
                #교점 구하기
                y1 = y + math.sqrt(math.pow(self.radius, 2) + math.pow(coords[2], 2) - (2 * x * coords[2]) + math.pow(x, 2))
                y2 = y - math.sqrt(math.pow(self.radius, 2) + math.pow(coords[2], 2) - (2 * x * coords[2]) + math.pow(x, 2))
                # 리스트에 교점 저장
                if (coords[1] < y1 and y1 < coords[3]): # y1좌표가 b1과 b2사이에 있을 경우
                    intersection_point[0] = coords[2]
                    intersection_point[1] = y1
                    if (coords[1] < y2 and y2 < coords[3]):# y2좌표가 b1과 b2사이에 있을 경우
                        intersection_point[2] = coords[2]
                        intersection_point[3] = y2
                elif (coords[1] < y2 and y2 < coords[3]): # y1좌표가 b1과 b2사이에 없고 y2좌표가 b1과 b2사이에 있을 경우
                    intersection_point[0] = coords[2]
                    intersection_point[1] = y2

            # y = b2 판별식
            discriminant_y2 = -(math.pow(coords[3], 2)) + (2 * y * coords[3]) - (math.pow(y, 2)) + (math.pow(self.radius, 2))
            if (discriminant_y2 > 0):
                #교점 구하기
                x1 = x + math.sqrt(math.pow(self.radius, 2) + math.pow(coords[3], 2) - (2 * y * coords[3]) + math.pow(y, 2))
                x2 = x - math.sqrt(math.pow(self.radius, 2) + math.pow(coords[3], 2) - (2 * y * coords[3]) + math.pow(y, 2))
                #리스트에 교점 저장
                if (coords[0] < x1 and x1 < coords[2]):
                    intersection_point[2] = x1
                    intersection_point[3] = coords[3]
                    if (coords[0] < x2 and x2 < coords[2]):
                        intersection_point[0] = x2
                        intersection_point[1] = coords[3]
                elif (coords[0] < x2 and x2 < coords[2]):
                    intersection_point[2] = x2
                    intersection_point[3] = coords[3]

            # 두 교점의 위치벡터
            intersection_point_vector = [intersection_point[0] - intersection_point[2], intersection_point[1] - intersection_point[3]]
        
            # 두 교점의 중점
            mid_x = (intersection_point[0] + intersection_point[2]) * 0.5
            mid_y = (intersection_point[1] + intersection_point[3]) * 0.5

            # 충돌한 게임 오브젝트의 중점
            object_x = (coords[0] + coords[2]) * 0.5
            object_y = (coords[1] + coords[3]) * 0.5

            # 교점 중심과 물체 중심의 벡터
            mid_vector = [object_x - mid_x, object_y - mid_y]
            
            # 법선벡터1 [x*cos90 - y*sin90, xsin90 + ycos90] = [-ysin90, xsin90]
            n1_vector = [-intersection_point_vector[1] / np.linalg.norm(intersection_point_vector), intersection_point_vector[0] / np.linalg.norm(intersection_point_vector)]
            # 법선벡터2 [x*cos90 + y*sin90, - xsin90 + ycos90] = [ysin90, -xsin90]
            n2_vector = [intersection_point_vector[1] / np.linalg.norm(intersection_point_vector), -intersection_point_vector[0] / np.linalg.norm(intersection_point_vector)]

            # 법선벡터와 공-물체중심벡터 간의 각 계산
            n1_theta = math.acos((mid_vector[0] * n1_vector[0] + mid_vector[1] * n1_vector[1]) / np.linalg.norm(mid_vector))
            n2_theta = math.acos((mid_vector[0] * n2_vector[0] + mid_vector[1] * n2_vector[1]) / np.linalg.norm(mid_vector))

            print("n1 : ", n1_theta)
            print("n2 : ", n2_theta)

            # 라디안 값을 비교를 위해 각도 값으로 변경
            n1_degrees = math.degrees(n1_theta)
            n2_degrees = math.degrees(n2_theta)

            print(n1_degrees)
            print(n2_degrees)

            # 법선벡터 결정
            if (n1_degrees > n2_degrees):
                #법선벡터가 충돌 전 진행방향 사이각 계산
                collide_theta = math.acos(n1_vector[0] * self.direction[0] + n1_vector[1] * self.direction[1])
                collide_degrees = math.degrees(collide_theta)
                # 사이각이 90도 이상일 때 반응 계산
                if (collide_degrees > 90):
                    dotproduct = (-self.direction[0] * n1_vector[0]) + (-self.direction[1] * n1_vector[1])
                    direction_vector = [2 * dotproduct * n1_vector[0] + self.direction[0], 2 * dotproduct * n1_vector[1] + self.direction[1]]
                    self.direction[0] = direction_vector[0]
                    self.direction[1] = direction_vector[1]  
                
            elif (n1_degrees < n2_degrees):
                #법선벡터와 충돌 전 진행방향 사이각 계산
                collide_theta = math.acos(n2_vector[0] * self.direction[0] + n2_vector[1] * self.direction[1])
                collide_degrees = math.degrees(collide_theta)
                # 사이각이 90도 이상일 때 반응 계산
                if (collide_degrees > 90):
                    dotproduct = (-self.direction[0] * n2_vector[0]) + (-self.direction[1] * n2_vector[1])
                    direction_vector = [2 * dotproduct * n2_vector[0] + self.direction[0], 2 * dotproduct * n2_vector[1] + self.direction[1]]
                    reponse_vector = [direction_vector[0] / np.linalg.norm(direction_vector), direction_vector[1] / np.linalg.norm(direction_vector)]
                    self.direction[0] = reponse_vector[0]
                    self.direction[1] = reponse_vector[1]

        for game_object in game_objects:
            if isinstance(game_object, Brick):
                game_object.hit()

    def get_position(self):
        coords = self.canvas.coords(self.item)*2
        coords[0] = coords[0] - self.radius # X축 -방향
        coords[1] = coords[1] - self.radius # Y축 -방향
        coords[2] = coords[2] + self.radius # X축 +방향
        coords[3] = coords[3] + self.radius # Y축 +방향
        return coords



class Paddle(GameObject):
    def __init__(self, canvas, x, y):
        self.width = 80
        self.height = 10
        self.ball = None
        item = canvas.create_rectangle(x - self.width / 2,
                                       y - self.height / 2,
                                       x + self.width / 2,
                                       y + self.height / 2,
                                       fill='blue')
        super(Paddle, self).__init__(canvas, item)

    def set_ball(self, ball):
        self.ball = ball

    def move(self, offset):
        coords = self.get_position()
        width = self.canvas.winfo_width()
        if coords[0] + offset >= 0 and coords[2] + offset <= width:
            super(Paddle, self).move(offset, 0)
            if self.ball is not None:
                self.ball.move(offset, 0)
    

class Brick(GameObject):
    COLORS = {1: '#999999', 2: '#555555', 3: '#222222'}

    def __init__(self, canvas, x, y, hits):
        self.width = 75
        self.height = 20
        self.hits = hits
        color = Brick.COLORS[hits]
        item = canvas.create_rectangle(x - self.width / 2,
                                       y - self.height / 2,
                                       x + self.width / 2,
                                       y + self.height / 2,
                                       fill=color, tags='brick')
        super(Brick, self).__init__(canvas, item)

    def hit(self):
        self.hits -= 1
        if self.hits == 0:
            self.delete()
        else:
            self.canvas.itemconfig(self.item,
                                   fill=Brick.COLORS[self.hits])


class Game(tk.Frame):
    def __init__(self, master):
        super(Game, self).__init__(master)
        self.lives = 3
        self.width = 610
        self.height = 400
        self.canvas = tk.Canvas(self, bg='#aaaaff',
                                width=self.width,
                                height=self.height,)
        self.canvas.pack()
        self.pack()
        self.level = 1

        self.items = {}
        self.ball = None
        self.paddle = Paddle(self.canvas, self.width/2, 326)
        self.items[self.paddle.item] = self.paddle

        self.setup_level()
        self.hud = None
        self.setup_game()
        self.canvas.focus_set()
        self.canvas.bind('<Left>',
                         lambda _: self.paddle.move(-10))
        self.canvas.bind('<Right>',
                         lambda _: self.paddle.move(10))

    def setup_game(self):
           self.add_ball()
           self.update_lives_text()
           self.text = self.draw_text(300, 200,
                                      'Press Space to start')
           self.canvas.bind('<space>', lambda _: self.start_game())

    def add_ball(self):
        if self.ball is not None:
            self.ball.delete()
        coords = self.paddle.get_position()
        x = (coords[0] + coords[2]) * 0.5
        self.ball = Ball(self.canvas, x, 310)
        self.paddle.set_ball(self.ball)

    def add_brick(self, x, y, hits):
        brick = Brick(self.canvas, x, y, hits)
        self.items[brick.item] = brick

    def draw_text(self, x, y, text, size='40'):
        font = ('Helvetica', size)
        return self.canvas.create_text(x, y, text=text,
                                       font=font)

    def update_lives_text(self):
        text = 'Lives: %s Level: %d' % (self.lives, self.level)
        if self.hud is None:
            self.hud = self.draw_text(80, 20, text, 15)
        else:
            self.canvas.itemconfig(self.hud, text=text)

    def start_game(self):
        self.canvas.unbind('<space>')
        self.canvas.delete(self.text)
        self.paddle.ball = None
        self.game_loop()

    def game_loop(self):
        self.check_collisions()
        num_bricks = len(self.canvas.find_withtag('brick'))
        if num_bricks == 0:
            if self.level == 3:
                self.ball.speed = None
                self.draw_text(300, 200, 'You win!')
            else:
                self.level += 1
                self.setup_game()
                self.setup_level()
        elif self.ball.get_position()[3] >= self.height: 
            self.ball.speed = None
            self.lives -= 1
            if self.lives < 0:
                self.draw_text(300, 200, 'Game Over')
            else:
                self.after(1000, self.setup_game)
        else:
            self.ball.update()
            self.after(50, self.game_loop)

    def check_collisions(self):
        ball_coords = self.ball.get_position()
        items = self.canvas.find_overlapping(*ball_coords)
        objects = [self.items[x] for x in items if x in self.items]
        self.ball.collide(objects)

    def setup_level(self):
        list = []
        if self.level == 1:
            for i in range(0, 5):
                x = random.randint(0, 7)
                while x in list:
                    x = random.randint(0, 7)
                list.append(x)
                x = x * 75 + 5
                self.add_brick(x + 37.5, 50, 1)
            list.clear()
            for j in range(0, 3):
                x = random.randint(0, 7)
                while x in list:
                    x = random.randint(0, 7)
                list.append(x)
                x = x * 75 + 5
                self.add_brick(x + 37.5, 70, 1)
            list.clear()
        if self.level == 2:
            for x in range(5, self.width -5, 75):
                self.add_brick(x + 37.5, 50, 1)
            for j in range(0, 5):
                x = random.randint(0, 7)
                while x in list:
                    x = random.randint(0, 7)
                list.append(x)
                x = x * 75 + 5
                self.add_brick(x + 37.5, 70, 1)
            list.clear()
            for i in range(0, 2):
                x = random.randint(0, 7)
                while x in list:
                    x = random.randint(0, 7)
                list.append(x)
                x = x * 75 + 5
                self.add_brick(x + 37.5, 90, 1)
            list.clear()
        if self.level == 3:
            for x in range(5, self.width - 5, 75):
                self.add_brick(x + 37.5, 50, 2)
                self.add_brick(x + 37.5, 70, 1)
                self.add_brick(x + 37.5, 90, 1)



if __name__ == '__main__':
    root = tk.Tk()
    root.title('Hello, Pong!')
    game = Game(root)
    game.mainloop()
