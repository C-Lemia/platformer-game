import pgzrun
import random
from pygame import Rect

WIDTH = 800
HEIGHT = 600

# Estados do jogo
STATE_MENU = "menu"
STATE_PLAYING = "playing"
STATE_GAMEOVER = "gameover"
STATE_WIN = "win"

# Recursos
backgrounds = ["background1", "background2", "background3"]
menu_background = "menu_background"
win_background = "win_background"
music_on = True

tile_ground = "tile_ground"
floor_y = 550

state = STATE_MENU
level = 1
game_won = False
win_timer = 0


class Hero:
    def __init__(self, x, y):
        self.actor = Actor("hero_idle_1", (x, y))
        self.vy = 0
        self.on_ground = False
        self.idle_frames = ["hero_idle_1", "hero_idle_2"]
        self.run_frames = ["hero_run_1", "hero_run_2"]
        self.jump_frame = "hero_jump"
        self.frame_index = 0
        self.anim_timer = 0

    def update(self):
        gravity = 0.5
        self.actor.y += self.vy
        self.vy += gravity

        if self.actor.y >= floor_y:
            self.actor.y = floor_y
            self.vy = 0
            self.on_ground = True
        else:
            self.on_ground = False

        if keyboard.left:
            self.actor.x -= 5
            if self.on_ground:
                self.animate(self.run_frames)
        elif keyboard.right:
            self.actor.x += 5
            if self.on_ground:
                self.animate(self.run_frames)
        elif self.on_ground:
            self.animate(self.idle_frames)

        if not self.on_ground:
            self.actor.image = self.jump_frame

        self.actor.x = max(0, min(WIDTH, self.actor.x))

    def animate(self, frames):
        self.anim_timer += 1
        if self.anim_timer >= 10:
            self.anim_timer = 0
            self.frame_index = (self.frame_index + 1) % len(frames)
            self.actor.image = frames[self.frame_index]

    def draw(self):
        self.actor.draw()

    def jump(self):
        if self.on_ground:
            self.vy = -12
            self.on_ground = False
            self.actor.image = self.jump_frame
            sounds.jump.play()


class Enemy:
    def __init__(self, x):
        self.actor = Actor("enemy_idle_1", (x, floor_y))
        self.vx = random.choice([-1, 1]) * 1
        self.idle_frames = ["enemy_idle_1", "enemy_idle_2"]
        self.run_frames = ["enemy_run_1", "enemy_run_2"]
        self.dead = False
        self.frame_index = 0
        self.anim_timer = 0

    def update(self):
        if self.dead:
            return
        self.actor.x += self.vx
        if self.actor.x < 50 or self.actor.x > WIDTH - 50:
            self.vx *= -1
        self.animate(self.run_frames)

    def animate(self, frames):
        self.anim_timer += 1
        if self.anim_timer >= 10:
            self.anim_timer = 0
            self.frame_index = (self.frame_index + 1) % len(frames)
            self.actor.image = frames[self.frame_index]

    def draw(self):
        self.actor.draw()


hero = Hero(100, 500)
enemies = []


def reset_game():
    global hero, enemies, level, game_won, win_timer
    hero = Hero(100, 500)
    enemies = []
    spacing = 150
    start_x = max(250, WIDTH // 2 - ((level - 1) * spacing // 2))
    for i in range(level):
        x = start_x + i * spacing
        x = min(x, WIDTH - 60)
        enemies.append(Enemy(x))
    game_won = False
    win_timer = 0


def draw():
    screen.clear()
    if state == STATE_MENU:
        screen.blit(menu_background, (0, 0))
        screen.draw.text("ZUMBI HERO", center=(WIDTH // 2, 100), fontsize=48, color="white")
        screen.draw.filled_rect(Rect((WIDTH // 2 - 100, 180), (200, 50)), "orange")
        screen.draw.text("START", center=(WIDTH // 2, 205), fontsize=36, color="black")
        screen.draw.filled_rect(Rect((WIDTH // 2 - 100, 260), (200, 50)), "skyblue")
        label = "MUSIC: ON" if music_on else "MUSIC: OFF"
        screen.draw.text(label, center=(WIDTH // 2, 285), fontsize=28, color="black")
        screen.draw.filled_rect(Rect((WIDTH // 2 - 100, 340), (200, 50)), "red")
        screen.draw.text("EXIT", center=(WIDTH // 2, 365), fontsize=36, color="white")

    elif state == STATE_PLAYING:
        bg_index = min(level - 1, len(backgrounds) - 1)
        screen.blit(backgrounds[bg_index], (0, 0))
        screen.blit(tile_ground, (0, floor_y))
        hero.draw()
        for enemy in enemies:
            enemy.draw()
        if game_won:
            screen.draw.text("YOU WIN!", center=(WIDTH // 2, 100), fontsize=60, color="yellow")
            screen.draw.filled_rect(Rect((WIDTH // 2 - 100, 160), (200, 50)), "green")
            screen.draw.text("NEXT LEVEL", center=(WIDTH // 2, 185), fontsize=36, color="black")

    elif state == STATE_WIN:
        screen.blit(win_background, (0, 0))
        screen.draw.text("JOGO GANHO!", center=(WIDTH // 2, 150), fontsize=48, color="gold")
        draw_trophy(WIDTH // 2 + 180, 170)
        screen.draw.filled_rect(Rect((WIDTH // 2 - 100, 340), (200, 50)), "orange")
        screen.draw.text("MENU", center=(WIDTH // 2, 365), fontsize=36, color="black")

    elif state == STATE_GAMEOVER:
        screen.fill("black")
        screen.draw.text("GAME OVER", center=(WIDTH // 2, 200), fontsize=60, color="red")
        screen.draw.filled_rect(Rect((WIDTH // 2 - 100, 340), (200, 50)), "orange")
        screen.draw.text("MENU", center=(WIDTH // 2, 365), fontsize=36, color="black")


def update():
    global state, game_won, win_timer, level

    if state == STATE_PLAYING:
        hero.update()
        for enemy in enemies:
            enemy.update()

        for enemy in enemies:
            if enemy.dead:
                continue
            if hero.actor.colliderect(enemy.actor):
                if hero.vy > 0:
                    enemy.actor.image = "enemy_slide"
                    enemy.dead = True
                    hero.vy = -10
                else:
                    state = STATE_GAMEOVER

        if all(e.dead for e in enemies) and not game_won:
            game_won = True
            win_timer = 120

        if game_won and win_timer > 0:
            win_timer -= 1
            if win_timer == 0:
                if level < 3:
                    level += 1
                    reset_game()
                else:
                    state = STATE_WIN


def on_key_down(key):
    if key == keys.SPACE:
        hero.jump()


def on_mouse_down(pos):
    global state, music_on, level
    x, y = pos
    if state == STATE_MENU:
        if 180 <= y <= 230:
            state = STATE_PLAYING
            reset_game()
        elif 260 <= y <= 310:
            music_on = not music_on
            if music_on:
                music.play("music")
            else:
                music.stop()
        elif 340 <= y <= 390:
            exit()

    elif state == STATE_PLAYING and game_won:
        if 160 <= y <= 210 and WIDTH // 2 - 100 <= x <= WIDTH // 2 + 100:
            level += 1
            if level > 3:
                state = STATE_WIN
            else:
                reset_game()

    elif state in [STATE_WIN, STATE_GAMEOVER]:
        if 340 <= y <= 390 and WIDTH // 2 - 100 <= x <= WIDTH // 2 + 100:
            state = STATE_MENU
            level = 1


def draw_trophy(x, y):
    screen.draw.filled_rect(Rect((x - 15, y), (30, 40)), "gold")
    screen.draw.rect(Rect((x - 15, y), (30, 40)), "orange")
    screen.draw.filled_circle((x - 25, y + 10), 7, "gold")
    screen.draw.filled_circle((x + 25, y + 10), 7, "gold")
    screen.draw.filled_rect(Rect((x - 20, y + 40), (40, 10)), "brown")
    screen.draw.rect(Rect((x - 20, y + 40), (40, 10)), "black")
    screen.draw.filled_circle((x, y + 10), 4, "white")


# Música de fundo
music.set_volume(0.3)
if music_on:
    music.play("music")

pgzrun.go()
