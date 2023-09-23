import random

from collections import defaultdict
from pyglet.image import load, ImageGrid, Animation
from pyglet.window import key

import cocos.layer
import cocos.sprite
import cocos.collision_model as cm
import cocos.euclid as eu
import cocos.audio
import cocos.audio.pygame
import cocos.audio.pygame.mixer

cocos.audio.pygame.mixer.init()
backgroundsound = cocos.audio.pygame.mixer.Sound("background.wav")
backgroundsound.play(-1) # 반복재생

# Abstruct class
class Actor(cocos.sprite.Sprite):
    def __init__(self, image, x, y):
        super(Actor, self).__init__(image)
        self.position = eu.Vector2(x, y)
        self.cshape = cm.AARectShape(self.position,
                                     self.width * 0.5,
                                     self.height * 0.5)

    # 콜리젼과 포지션을 오프셋만큼 위치 이동.
    def move(self, offset):
        self.position += offset 
        self.cshape.center += offset

    # Null operation 상속용
    def update(self, elapsed):
        pass

    # Null operation 상속용 
    def collide(self, other):
        pass


class PlayerCannon(Actor):
    KEYS_PRESSED = defaultdict(int) # Gamelayer 업데이트
    def __init__(self, x, y):
        super(PlayerCannon, self).__init__('img/cannon.png', x, y)
        self.speed = eu.Vector2(200, 0) # x축으로만 이동
        self.speed2 = eu.Vector2(0, 100) # y축 이동
        self.period = 0.3
        self.reload = 0.0
        self.schedule(self.shoot_cooltime)

    # Call in GameLayer.update
    def update(self, elapsed): 
        pressed = PlayerCannon.KEYS_PRESSED
        movement = pressed[key.RIGHT] - pressed[key.LEFT]
        
        movement2 = pressed[key.UP] - pressed[key.DOWN]
        w = self.width * 0.5
        h = self.height * 0.5

        # 미리 이동할 곳 계산
        self.move(self.speed * movement * elapsed)
        self.move(self.speed2 * movement2 * elapsed)

        if movement != 0 and w <= self.x <= self.parent.width - w: # 정상작동일 경우
            pass
        else: # 벽을 넘어갔을 경우 -> 이동취소
            self.move(-self.speed * movement * elapsed)

        if movement2 != 0 and h <= self.y <= self.parent.height - (self.parent.height * 0.5) - h: # 정상작동일 경우
            pass
        else: # 벽을 넘어갔을 경우 -> 이동취소
            self.move(-self.speed2 * movement2 * elapsed)

    def shoot_cooltime(self, dt):
        if self.reload < self.period:
            self.reload += dt
        else:
            self.reload -= self.period
            pressed = PlayerCannon.KEYS_PRESSED
            space_pressed = pressed[key.SPACE] == 1
            if PlayerShoot.SHOOTINDEX < 5 and space_pressed: # 스페이스가 눌려진 경우 and PlayerShoot이 none인 경우
                # 해결법 인스턴스 멤버로 바꾸기.
                self.parent.add(PlayerShoot(self.x, self.y + 50))
                sound = cocos.audio.pygame.mixer.Sound('shootsound.wav')
                sound.play()

    def collide(self, other):
        other.kill()
        self.kill()


class GameLayer(cocos.layer.Layer):
    is_event_handler = True

    # 플레이어 이동 구현 
    def on_key_press(self, k, _):
        PlayerCannon.KEYS_PRESSED[k] = 1

    def on_key_release(self, k, _):
        PlayerCannon.KEYS_PRESSED[k] = 0
    
    def __init__(self, hud):
        super(GameLayer, self).__init__()
        w, h = cocos.director.director.get_window_size()
        self.hud = hud
        self.width = w
        self.height = h
        self.lives = 3
        self.score = 0
        self.update_score()
        self.create_player()
        self.create_alien_group(100, 300)

        cell = 1.25 * 50
        self.collman = cm.CollisionManagerGrid(0, w, 0, h, cell, cell)

        self.schedule(self.update)
    
    # 플레이어 만들기
    def create_player(self):
        self.player = PlayerCannon(self.width * 0.5, 50)
        self.add(self.player)
        self.hud.update_lives(self.lives)

    # 스코어 업데이트
    def update_score(self, score=0):
        self.score += score
        self.hud.update_score(self.score)

    # Container에서 Iterator를 통해 에일리언 객체를 가져와 생성.
    def create_alien_group(self, x, y):
        self.alien_group = AlienGroup(x, y)
        for alien in self.alien_group:
            self.add(alien)


    def update(self, dt):
        self.collman.clear()
        for _, node in self.children:
            # 스프라이트를 벗어나면 처리 삭제
            self.collman.add(node)
            if not self.collman.knows(node):
                self.remove(node)
        # 총알이 있는 경우 플레이어가 충돌 했을 때 리스폰 
        # 총알과 충돌했는지 배열 전체 검사
        for player_instance in PlayerShoot.SHOOTLIST:
            self.collide(player_instance)
            self.game_win()

        if self.collide(self.player):
            self.respawn_player()

        # 에일리언 미사일 발사
        for column in self.alien_group.columns:
            shoot = column.shoot()
            if shoot is not None:
                self.add(shoot)

        # 그룹을 묶어서 처리.
        for _, node in self.children:
            node.update(dt)
        self.alien_group.update(dt)
        if random.random() < 0.01: # 업데이트 1/1000의 확률로 미스터리쉽 생성.
            self.add(MysteryShip(50, self.height - 50))

    # 충돌 처리
    def collide(self, node):
        if node is not None:
            for other in self.collman.iter_colliding(node):
                node.collide(other) # 대상도 넘겨주어 처리하도록 함.
                return True
        return False
 
    def respawn_player(self):
        self.lives -= 1
        if self.lives < 0:
            self.unschedule(self.update)
            self.hud.show_game_over()
        else:
            self.create_player()

    def game_win(self):
        if self.score >= 1100:
            self.unschedule(self.update)
            self.hud.show_game_win()
        else:
            pass

# 에일리언 클래스
class Alien(Actor):
    def load_animation(imgage):
        seq = ImageGrid(load(imgage), 2, 1) # 이미지 읽기 설정.
        return Animation.from_image_sequence(seq, 0.5) # 무한 루프로 애니메이션
    
    TYPES = {
        '1': (load_animation('img/alien1.png'), 40),
        '2': (load_animation('img/alien2.png'), 20),
        '3': (load_animation('img/alien3.png'), 10)
    } #에일리언이미지와 스코어 값

    # 타입을 구별해서 에일리언을 만들어줌.
    def from_type(x, y, alien_type, column):
        animation, score = Alien.TYPES[alien_type]
        return Alien(animation, x, y, score, column)
   
    def __init__(self, img, x, y, score, column=None):
        super(Alien, self).__init__(img, x, y)
        self.score = score
        self.column = column #에일리언 column 추가

    # 에일리언 삭제.
    def on_exit(self):
        super(Alien, self).on_exit()
        if self.column:
            self.column.remove(self)

# 에일리언column 클래스
class AlienColumn(object):
    def __init__(self, x, y):
        alien_types = enumerate(['3', '3', '2', '2', '1']) # 에일리언의 타입과 인덱스를 가져옴.
        self.aliens = [Alien.from_type(x, y+i*60, alien, self) 
                       for i, alien in alien_types] # 에일리언 리스트 생성.

    # column단위로 맵 끝 확인 처리, 방향정보도 받음.
    def should_turn(self, d):
        if len(self.aliens) == 0: # 하나도 안오는 경우 false
            return False
        alien = self.aliens[0] # 하나만 뽑아서 처리
        x, width = alien.x, alien.parent.width
        return x >= width - 50 and d == 1 or x <= 50 and d == -1
   
    def remove(self, alien):
        self.aliens.remove(alien)

    def shoot(self):
        if random.random() < 0.001 and len(self.aliens) > 0: # 에일리언이 있을 경우 1/1000확률로 처
            pos = self.aliens[0].position
            return Shoot(pos[0], pos[1] - 50)
        return None

class AlienGroup(object):
    def __init__(self, x, y):
        self.columns = [AlienColumn(x + i * 60, y)
                        for i in range(10)]
        self.speed = eu.Vector2(10, 0)
        self.direction = 1
        self.elapsed = 0.0
        self.period = 1.0 #움직이는 타임

    def update(self, elapsed):
        self.elapsed += elapsed
        while self.elapsed >= self.period:
            self.elapsed -= self.period
            offset = self.direction * self.speed
            if self.side_reached():
                self.direction *= -1
                offset = eu.Vector2(0, -10)
            for alien in self:
                alien.move(offset)

    def side_reached(self):
        return any(map(lambda c: c.should_turn(self.direction), 
                       self.columns))

    def __iter__(self):
        for column in self.columns:
            for alien in column.aliens:
                yield alien

class Shoot(Actor):
    def __init__(self, x, y, img='img/shoot.png'):
        super(Shoot, self).__init__(img, x, y)
        self.speed = eu.Vector2(0, -400)

    def update(self, elapsed):
        self.move(self.speed * elapsed)

class PlayerShoot(Shoot):
    INSTANCE = None
    SHOOTINDEX = 0
    SHOOTLIST = []

    def __init__(self, x, y):
        super(PlayerShoot, self).__init__(x, y, 'img/laser.png')
        self.speed *= -1
        PlayerShoot.INSTANCE = self
        PlayerShoot.SHOOTLIST.append(PlayerShoot.INSTANCE)
        PlayerShoot.SHOOTINDEX += 1

    def collide(self, other):
        if isinstance(other, Alien):
            self.parent.update_score(other.score)
            sound = cocos.audio.pygame.mixer.Sound('hitsound.wav')
            sound.play()
            other.kill() 
            self.kill()

    def on_exit(self):
        super(PlayerShoot, self).on_exit()
        PlayerShoot.INSTANCE = None
        PlayerShoot.SHOOTINDEX -= 1
        PlayerShoot.SHOOTLIST.pop(0)


class HUD(cocos.layer.Layer):
    def __init__(self):
        super(HUD, self).__init__()
        w, h = cocos.director.director.get_window_size()
        self.score_text = cocos.text.Label('', font_size=18)
        self.score_text.position = (20, h - 40)
        self.lives_text = cocos.text.Label('', font_size=18)
        self.lives_text.position = (w - 100, h - 40)
        self.add(self.score_text)
        self.add(self.lives_text)

    def update_score(self, score):
        self.score_text.element.text = 'Score: %s' % score

    def update_lives(self, lives):
        self.lives_text.element.text = 'Lives: %s' % lives

    def show_game_over(self):
        w, h = cocos.director.director.get_window_size()
        game_over = cocos.text.Label('Game Over', font_size=50,
                                     anchor_x='center',
                                     anchor_y='center')
        game_over.position = w * 0.5, h * 0.5
        self.add(game_over)

    def show_game_win(self):
        w, h = cocos.director.director.get_window_size()
        game_win = cocos.text.Label('Game Win!', font_size=50,
                                     anchor_x='center',
                                     anchor_y='center')
        game_win.position = w * 0.5, h * 0.5
        self.add(game_win)

class MysteryShip(Alien):
    SCORES = [10, 50, 100, 200]
    def __init__(self, x, y):
        score = random.choice(MysteryShip.SCORES)
        super(MysteryShip, self).__init__('img/alien4.png', x, y, 
                                          score)
        self.speed = eu.Vector2(150, 0)

    def update(self, elapsed):
        self.move(self.speed * elapsed)

if __name__ == '__main__':
    cocos.director.director.init(caption='Cocos Invaders', 
                                 width=800, height=650)
    main_scene = cocos.scene.Scene()
    hud_layer = HUD()
    main_scene.add(hud_layer, z=1)
    game_layer = GameLayer(hud_layer)
    main_scene.add(game_layer, z=0)
    cocos.director.director.run(main_scene)
