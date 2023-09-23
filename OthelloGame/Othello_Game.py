import cocos
from cocos.menu import *
import numpy as np
import cocos.euclid as eu

class HUD(cocos.layer.Layer):
    def __init__(self):
        super(HUD, self).__init__()
        w, h = cocos.director.director.get_window_size()
        self.score_text = cocos.text.Label('', font_size=18, color=(50, 50, 255, 255))
        self.score_text.position = (20, h - 40)
        self.add(self.score_text)

    def update_score(self, person, computer):
        self.score_text.element.text = 'You: %s, Computer: %s' % (person, computer)

    def show_game_over(self, winner):
        w, h = cocos.director.director.get_window_size()
        game_over = cocos.text.Label(winner, font_size=50,
                                     anchor_x='center',
                                     anchor_y='center',
                                     color=(50, 50, 255, 255))
        game_over.position = w * 0.5, h * 0.5
        self.add(game_over)

class GameLayer(cocos.layer.Layer):
    is_event_handler = True

    PERSON = -1
    COMPUTER = 1
    
    def __init__(self, difficulty, hud_layer):
        super(GameLayer, self).__init__()
        self.difficulty = difficulty

        #self.levelDepth = self.difficulty*2+2 # Depth로 분석 개수 조정
        self.hud = hud_layer
        self.square = 75
        self.row = 8
        self.column = 8
        self.height = self.row*self.square
        self.width = self.column*self.square

        # 돌의 정보가 저장된 테이블
        self.table = np.arange(self.row*self.column).reshape(self.row, self.column)

        # minmax에 사용할 수치값
        #self.weight = np.array(     [   [ 50,  -10,   15,   15,   15,   15,  -10,   50], 
        #                                [-10,  -20,  -10,  -10,  -10,  -10,  -20,  -10], 
        #                                [ 15,  -10,    1,    1,    1,    1,  -10,   15], 
        #                                [ 15,  -10,    1,    1,    1,    1,  -10,   15], 
        #                                [ 15,  -10,    1,    1,    1,    1,  -10,   15], 
        #                                [ 15,  -10,    1,    1,    1,    1,  -10,   15], 
        #                                [-10,  -20,  -10,  -10,  -10,  -10,  -20,  -10], 
        #                                [ 50,  -10,   15,   15,   15,   15,  -10,   50]])

        self.level_setup() # easy 코인패러티 normal 가중치 hard 복합

        # 선 그리는 동작
        for x in range  (0, self.column+1) :
            line = cocos.draw.Line((x*self.square, 0), (x*self.square, self.height), (255, 0, 255, 255))
            self.add(line)
        for y in range  (0, self.row+1) :
            line = cocos.draw.Line((0, y*self.square), (self.width, y*self.square), (255, 0, 255, 255))
            self.add(line)

        # Sprite로 사용할 변수
        self.disk = [[None for i in range(self.column)] for j in range(self.row)]

        for y in range (0, self.row) :
            for x in range (0, self.column) :
                centerPt = eu.Vector2(x*self.square + self.square/2, y*self.square + self.square/2)
                self.disk[y][x] = cocos.sprite.Sprite('ball.png', position = centerPt, color = (255, 255, 255))
                self.add(self.disk[y][x])

        self.setup()
        self.turn = GameLayer.PERSON # 사람먼저 두도록 함
        self.count = 0 # 컴퓨터에게 딜레이를 주기 위함.
        self.schedule(self.update)

    def level_setup(self):
        self.levelDepth = self.difficulty*2+2
        if self.difficulty == 0:
            self.easy_evalution_difficulty()
        elif self.difficulty == 1:
            self.normal_evalution_difficulty()
        else:
            self.hard_evalution_difficulty()

    # 난이도 EASY : Coin Parity로만 판단
    def easy_evalution_difficulty(self):
        self.weight = np.array(     [ [ 1, 1, 1, 1, 1, 1, 1, 1], 
                                    [   1, 1, 1, 1, 1, 1, 1, 1], 
                                    [   1, 1, 1, 1, 1, 1, 1, 1], 
                                    [   1, 1, 1, 1, 1, 1, 1, 1], 
                                    [   1, 1, 1, 1, 1, 1, 1, 1], 
                                    [   1, 1, 1, 1, 1, 1, 1, 1], 
                                    [   1, 1, 1, 1, 1, 1, 1, 1], 
                                    [   1, 1, 1, 1, 1, 1, 1, 1]])

    # 난이도 NORMAL : 기본 가중치로 스코어 판단
    def normal_evalution_difficulty(self):
        self.weight = np.array(     [   [ 20,  -3,   11,   8,   8,   11,  -3,  20], 
                                        [ -3,  -7,   -4,   1,   1,   -4,  -7,  -3], 
                                        [ 11,  -4,    2,   2,   2,    2,  -4,  11], 
                                        [  8,   1,    2,  -3,  -3,    2,   1,   8], 
                                        [  8,   1,    2,  -3,  -3,    2,   1,   8], 
                                        [ 11,  -4,    2,   2,   2,    2,  -4,  11], 
                                        [ -3,  -7,   -4,   1,   1,   -4,  -7,  -3], 
                                        [ 20,  -3,   11,   8,   8,   11,  -3,  20]])
    # 난이도 HARD : 가중치 + dynamic heuristic score 계산
    def hard_evalution_difficulty(self):
        self.weight = np.array(     [   [ 20,  -3,   11,   8,   8,   11,  -3,  20], 
                                        [ -3,  -7,   -4,   1,   1,   -4,  -7,  -3], 
                                        [ 11,  -4,    2,   2,   2,    2,  -4,  11], 
                                        [  8,   1,    2,  -3,  -3,    2,   1,   8], 
                                        [  8,   1,    2,  -3,  -3,    2,   1,   8], 
                                        [ 11,  -4,    2,   2,   2,    2,  -4,  11], 
                                        [ -3,  -7,   -4,   1,   1,   -4,  -7,  -3], 
                                        [ 20,  -3,   11,   8,   8,   11,  -3,  20]])

    # 테이블 초기화, 돌 4개 생성.
    def setup(self):
        for y in range (0, self.row) :
            for x in range (0, self.column) :
                self.table[y][x] = 0

        self.table[3][3] = GameLayer.PERSON
        self.table[3][4] = GameLayer.COMPUTER
        self.table[4][3] = GameLayer.COMPUTER
        self.table[4][4] = GameLayer.PERSON
        
    # 매프레임마다 업데이트
    def update(self, dt):
        computer = 0
        person = 0
        self.count += 1
        
        # 판 전체도 그냥 업데이트 할 겸 Display
        for y in range  (0, self.row) :
            for x in range  (0, self.column) :
                if self.table[y][x] == GameLayer.COMPUTER:
                    self.disk[y][x].color = (255, 255, 255)
                    self.disk[y][x].visible = True
                    computer += 1
                elif self.table[y][x] == GameLayer.PERSON:
                    self.disk[y][x].color = (0, 0, 0)
                    self.disk[y][x].visible = True
                    person += 1
                else:
                    self.disk[y][x].visible = False

        # 스코어 업데이트
        self.hud.update_score(person, computer)

        # 둘 수 있는 전체 위치 찾기
        moves1 = self.getMoves(GameLayer.PERSON, self.table)
        moves2 = self.getMoves(GameLayer.COMPUTER, self.table)

        # 둘 곳이 없어지면 턴이 넘어감.
        if self.turn == GameLayer.PERSON and len(moves1) == 0:
            self.turn *= -1

        # 둘 곳이 사라지면 게임 끝
        if computer+person == self.row*self.column or (len(moves1) == 0 and len(moves2) == 0):
            if computer > person:
                self.hud.show_game_over('Computer win')
            elif computer < person:
                self.hud.show_game_over('You win')
            else:
                self.hud.show_game_over('Draw')

        # 컴퓨터도 둘 곳 없어지면 턴 넘김.
        if self.turn == GameLayer.COMPUTER and self.count > 100:
            self.computer()

    # 8방향 확인
    def isPossible(self, x, y, turn, board):
        rtnList = list()
        
        if board[y][x] != 0: return rtnList # 둘 수 없는 경우 

        for dirX in range(-1, 2):
            for dirY in range(-1,2):
                if dirX == 0 and dirY == 0: continue
                if(x+dirX < 0 or x+dirX >= self.column): continue # 경계 처리
                if(y+dirY < 0 or y+dirY >= self.row): continue # 경계 처리

                # 리버스 시킬 XY 쌍좌표
                xList = list()
                yList = list()
                # 좌표쌍 저장 과정
                if dirX == 0:
                    for yy in range(y+dirY, self.row*dirY,dirY):
                        if(yy < 0 or yy >= self.row): break
                        xList.append(x)
                        yList.append(yy)
                elif dirY == 0:
                    for xx in range(x+dirX, self.column*dirX,dirX):
                        if(xx < 0 or xx >= self.column): break
                        xList.append(xx)
                        yList.append(y)
                else:
                    for xx, yy in zip(range(x+dirX, self.column*dirX,dirX), range(y+dirY, self.row*dirY,dirY)):
                        if(xx < 0 or xx >= self.column): break
                        if(yy < 0 or yy >= self.row): break
                        xList.append(xx)
                        yList.append(yy)

                bDetected = False
                revList = []
                if board[y+dirY][x+dirX] == turn*-1: # 상대방 돌인지 판단
                    #revList.append((x+dirX, y+dirY))
                    for xx, yy in zip(xList, yList): 
                        if xx >= self.column or xx < 0 or yy >= self.row or yy < 0: # 경계이거나
                            break
                        if board[yy][xx] == turn*-1: #상대방의 돌일 경우 리스트 추가
                            revList.append((xx, yy))
                        if board[yy][xx] == turn: # Detected true
                            bDetected = True
                            break
                        if board[yy][xx] == 0: # 비어있는 경우 끝내기
                            break
                    if(bDetected == False): revList = [] # 뒤질힐 리스트가 아니면 빈 리스트

                rtnList += revList; # 한 방향에서 뒤집힐 리스트

        return rtnList # 8방향에 대하여 뒤집힐 리스트

    # 테이블 전체 검사
    def getMoves(self, turn, board):
        moves = []
        for y in range  (0, self.row) :
            for x in range  (0, self.column) :
                if board[y][x] != 0: continue # 둘 수 있는 위치가 아니므로 pass

                revList = self.isPossible(x, y, turn, board) # 둘 수 있는 경우인지 위치 판단 & 뒤집히는 좌표의 리스트
                if len(revList) > 0 :
                    moves.append((x, y, revList)) # 리스트에 추가

        return moves

    # 둘 수 있는 위치 계산 함수 Mobility 계산에 필요.
    def num_moves(self, turn, board):
        moves = 0
        for y in range  (0, self.row) :
            for x in range  (0, self.column) :
                if board[y][x] != 0: continue # 둘 수 있는 위치가 아니므로 pass

                revList = self.isPossible(x, y, turn, board) # 둘 수 있는 경우인지 위치 판단 & 뒤집히는 좌표의 리스트
                if len(revList) > 0 :
                    moves += 1
        return moves

    # 마우스 클릭 이벤트
    def on_mouse_release(self, x, y, buttons, mod):
        if self.turn != GameLayer.PERSON:
            return

        moves = self.getMoves(GameLayer.PERSON, self.table)

        if len(moves) > 0:    
            xx = x//self.square
            yy = y//self.square

            revList = self.isPossible(xx, yy, GameLayer.PERSON, self.table)

            if len(revList) == 0: return

            self.table[yy][xx] = GameLayer.PERSON
            for revX, revY in revList:
                self.table[revY][revX] = GameLayer.PERSON
            
        self.turn *= -1
        self.count = 0    
            
    # 컴퓨터 턴인 경우
    def computer(self):       
        move = self.minimax(GameLayer.COMPUTER) # 컴퓨터 좌표 판단

        if len(move) > 0:
            self.table[move[1]][move[0]] = GameLayer.COMPUTER

            for revX, revY in move[2]:
                self.table[revY][revX] = GameLayer.COMPUTER

        self.turn *= -1
        
    def minimax(self, player):
        moves = self.getMoves(player, self.table)

        if len(moves) == 0: return moves
        
        scores = np.zeros(len(moves))
    
        alpha = float("-inf")
        beta = float("inf")

        # Maxmove의 실행이 한번 이루어짐
        for i, move in enumerate(moves): # i는 depth, move는 뒤질힐 열
            # Numpy를 이용한 Deep copy를 통해 테이블 변환 방지
            boardCopy = self.getNewBoard(move[0], move[1], move[2], GameLayer.COMPUTER, np.copy(self.table))
            #scores[i] = self.maxMove(boardCopy, 1, alpha, beta)
            
            if 1 >= self.levelDepth: 
                scores[i] = self.boardScore(boardCopy)
            else:
                scores[i] = self.minMove(boardCopy, 2, alpha, beta)

        maxIndex = np.argmax(scores)

        return moves[maxIndex]

    # X, Y 좌표에 새로 둔 경우를 진행한 새로운 보드
    def getNewBoard(self, x, y, revList, player, table):   
        table[y][x] = player
        
        for (x,y) in revList:
            table[y][x] = player

        return table    

    # MinMax처리
    def maxMove(self, board, depth, alpha, beta):
        moves = self.getMoves(GameLayer.COMPUTER, board)
        scores = np.zeros(len(moves))

        if len(moves)==0:
            if depth<=self.levelDepth:
                return self.minMove(board, depth+1, alpha, beta)
            else:
                return self.boardScore(board)

        for i, move in enumerate(moves):
            boardCopy = self.getNewBoard(move[0], move[1], move[2], GameLayer.COMPUTER, np.copy(board))
            if depth>=self.levelDepth:
                scores[i] = self.boardScore(boardCopy)
            else:
                scores[i] = self.minMove(boardCopy, depth+1, alpha, beta)
                if scores[i] > alpha:
                    alpha = scores[i]
                if beta <= alpha:
                    return scores[i]
        return max(scores)

    # MinMax처리
    def minMove(self, board, depth, alpha, beta):
        moves = self.getMoves(GameLayer.PERSON, board)
        scores = np.zeros(len(moves))

        if len(moves)==0:
            if depth<=self.levelDepth:
                return self.maxMove(board, depth+1, alpha, beta)
            else:
                return self.boardScore(board)

        for i, move in enumerate(moves):
            boardCopy = self.getNewBoard(move[0], move[1], move[2], GameLayer.PERSON, np.copy(board))
            if depth>=self.levelDepth:
                scores[i] = self.boardScore(boardCopy)
            else:
                scores[i] = self.maxMove(boardCopy, depth+1, alpha, beta)
                if beta > scores[i]:
                    beta = scores[i]
                if beta <= alpha:
                    return scores[i]
        return min(scores)

    def boardScore(self, board):
        if self.difficulty != 2:
            computerWeightSum = 0
            personWeightSum = 0

            for y in range(0, self.row):
                for x in range(0, self.column):
                    if board[y][x] == GameLayer.COMPUTER:
                        computerWeightSum += self.weight[y][x]

                    if board[y][x] == GameLayer.PERSON:
                        personWeightSum += self.weight[y][x]
            return computerWeightSum - personWeightSum;
        else:
            person_tiles = 0
            computer_tiles = 0
            person_front_tiles = 0
            computer_front_tiles = 0
            # 8방향 검사를 위한 배열
            x1 = np.array([-1, -1, 0, 1, 1, 1, 0, -1])
            y1 = np.array([0, 1, 1, 1, 0, -1, -1, -1])

            # 코인 차이, 코너 계산
            piece_difference = 0.0
            frontier_disks = 0.0
            disk_squares = 0.0
            for y in range(0, self.row):
                for x in range(0, self.column):
                    if board[y][x] == GameLayer.PERSON:
                        disk_squares += self.weight[y][x]
                        person_tiles += 1
                    elif board[y][x] == GameLayer.COMPUTER:
                        disk_squares -= self.weight[y][x]
                        computer_tiles += 1
                    if board[y][x] != 0:
                        for i in range (0, self.row):
                            a = y + x1[i]
                            b = x + y1[i]
                            if a >= 0 and a < 8 and b >= 0 and b < 8 and board[a][b] != 0:
                                if board[y][x] == GameLayer.PERSON:
                                    person_front_tiles += 1
                                else:
                                    computer_front_tiles +=1
                                break

            if person_tiles > computer_tiles:
                piece_difference = (100.0 * person_tiles)/(person_tiles + computer_tiles)
            elif person_tiles < computer_tiles:
                piece_difference = -(100.0 * computer_tiles)/(person_tiles + computer_tiles)
            else:
                piece_difference = 0

            if person_front_tiles > computer_front_tiles:
                frontier_disks = -(100.0 * person_front_tiles)/(person_front_tiles + computer_front_tiles)
            elif person_front_tiles < computer_front_tiles:
                frontier_disks = (100.0 * person_front_tiles)/(person_front_tiles + computer_front_tiles)
            else:
                frontier_disks = 0

            # 코너 점유 검사
            corner_occupancy = 0
            person_tiles = 0
            computer_tiles = 0
            if board[0][0] == GameLayer.PERSON:
                person_tiles += 1
            elif board[0][0] == GameLayer.COMPUTER:
                computer_tiles += 1
            if board[0][7] == GameLayer.PERSON:
                person_tiles += 1
            elif board[0][7] == GameLayer.COMPUTER:
                computer_tiles += 1
            if board[7][0] == GameLayer.PERSON:
                person_tiles += 1
            elif board[7][0] == GameLayer.COMPUTER:
                computer_tiles += 1
            if board[7][7] == GameLayer.PERSON:
                person_tiles += 1
            elif board[7][7] == GameLayer.COMPUTER:
                computer_tiles += 1
            corner_occupancy = 25 * (person_tiles - computer_tiles)

            # 코너 근접성 검사
            corner_closeness = 0
            person_tiles = 0
            computer_tiles = 0
            # 코너 4개 근접한 곳 검사
            if board[0][0] == 0:
                if board[0][1] == person_tiles:
                    person_tiles += 1
                elif board[0][1] == computer_tiles:
                    computer_tiles += 1
                if board[1][0] == person_tiles:
                    person_tiles += 1
                elif board[1][0] == computer_tiles:
                    computer_tiles += 1
                if board[1][1] == person_tiles:
                    person_tiles += 1
                elif board[1][1] == computer_tiles:
                    computer_tiles += 1

            if board[0][7] == 0:
                if board[0][6] == person_tiles:
                    person_tiles += 1
                elif board[0][6] == computer_tiles:
                    computer_tiles += 1
                if board[1][6] == person_tiles:
                    person_tiles += 1
                elif board[1][6] == computer_tiles:
                    computer_tiles += 1
                if board[1][7] == person_tiles:
                    person_tiles += 1
                elif board[1][7] == computer_tiles:
                    computer_tiles += 1

            if board[7][0] == 0:
                if board[7][1] == person_tiles:
                    person_tiles += 1
                elif board[7][1] == computer_tiles:
                    computer_tiles += 1
                if board[6][1] == person_tiles:
                    person_tiles += 1
                elif board[6][1] == computer_tiles:
                    computer_tiles += 1
                if board[6][0] == person_tiles:
                    person_tiles += 1
                elif board[6][0] == computer_tiles:
                    computer_tiles += 1

            if board[7][7] == 0:
                if board[6][7] == person_tiles:
                    person_tiles += 1
                elif board[6][7] == computer_tiles:
                    computer_tiles += 1
                if board[6][6] == person_tiles:
                    person_tiles += 1
                elif board[6][6] == computer_tiles:
                    computer_tiles += 1
                if board[7][6] == person_tiles:
                    person_tiles += 1
                elif board[7][6] == computer_tiles:
                    computer_tiles += 1

            corner_closeness = -12.5 * (person_tiles - computer_tiles)

            # 이동 차이 검사
            mobility = 0
            person_tiles = self.num_moves(GameLayer.PERSON, board)
            computer_tiles = self.num_moves(GameLayer.COMPUTER, board)
            if person_tiles > computer_tiles:
                mobility = (100.0 * person_tiles)/(person_tiles + computer_tiles)
            elif person_tiles < computer_tiles:
                mobility = -(100.0 * person_tiles)/(person_tiles + computer_tiles)
            else:
                mobility = 0

            score = (10 * piece_difference) + (801.724 * corner_occupancy) + (382.026 * corner_closeness) + (78.922 * mobility) + (74.396 * frontier_disks) + (10 * disk_squares)
            return score
                
        
class MainMenu(Menu):
    def __init__(self):
        super(MainMenu, self).__init__('Menu')
        self.font_title['font_name'] = 'Times New Roman'
        self.font_title['font_size'] = 60
        self.font_title['bold'] = True
        self.font_item['font_name'] = 'Times New Roman'
        self.font_item_selected['font_name'] = 'Times New Roman'

        self.selDifficulty = 0
        self.difficulty = ['Easy', 'Normal', 'Hard']

        items = list()
        items.append(MenuItem('New Game', self.start_game))
        items.append(MultipleMenuItem('Difficuly: ', self.set_difficulty, self.difficulty, 0))
        items.append(MenuItem('Quit', exit))
        self.create_menu(items, shake(), shake_back())

    def start_game(self):
        scene = cocos.scene.Scene()
        color_layer = cocos.layer.ColorLayer(0, 100, 0, 255)
        hud_layer = HUD()
        scene.add(hud_layer, z=2)
        scene.add(GameLayer(self.selDifficulty, hud_layer), z=1)
        scene.add(color_layer, z=0)
        cocos.director.director.push(scene)
        

    def set_difficulty(self, index):
        self.selDifficulty = index

if __name__ == '__main__':
    cocos.director.director.init(caption='Othello', width = 75*8, height = 75*8)

    scene = cocos.scene.Scene()
    scene.add(MainMenu())
    
    cocos.director.director.run(scene)
