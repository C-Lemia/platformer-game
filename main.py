import pgzrun
import random
from pygame import Rect

#------------ Tamanho da tela
LARGURA = 800
ALTURA = 600
WIDTH = LARGURA
HEIGHT = ALTURA

#------------ Estados do jogo
ESTADO_MENU = "menu"
ESTADO_JOGANDO = "jogando"
ESTADO_GAMEOVER = "gameover"
ESTADO_VITORIA_FINAL = "vitoria_final"

#------------ Recursos
fundos = ["background1", "background2", "background3"]
fundo_menu = "menu_background"
fundo_vitoria = "win_background"
som_ativo = True

tile_chao = "tile_ground"
posicao_chao_y = 550

estado_atual = ESTADO_MENU
fase_atual = 1
fase_concluida = False
temporizador_vitoria = 0

#------------ Classe do Herói
class Heroi:
    def __init__(self, x, y):
        self.ator = Actor("hero_idle_1", (x, y))
        self.vel_y = 0
        self.no_chao = False
        self.frames_parado = ["hero_idle_1", "hero_idle_2"]
        self.frames_correndo = ["hero_run_1", "hero_run_2"]
        self.frame_pulo = "hero_jump"
        self.indice_frame = 0
        self.contador_anim = 0

    def atualizar(self):
        gravidade = 0.5
        self.ator.y += self.vel_y
        self.vel_y += gravidade

        if self.ator.y >= posicao_chao_y:
            self.ator.y = posicao_chao_y
            self.vel_y = 0
            self.no_chao = True
        else:
            self.no_chao = False

        if keyboard.left:
            self.ator.x -= 5
            if self.no_chao:
                self.animar(self.frames_correndo)
        elif keyboard.right:
            self.ator.x += 5
            if self.no_chao:
                self.animar(self.frames_correndo)
        elif self.no_chao:
            self.animar(self.frames_parado)

        if not self.no_chao:
            self.ator.image = self.frame_pulo

        self.ator.x = max(0, min(LARGURA, self.ator.x))

    def animar(self, frames):
        self.contador_anim += 1
        if self.contador_anim >= 10:
            self.contador_anim = 0
            self.indice_frame = (self.indice_frame + 1) % len(frames)
            self.ator.image = frames[self.indice_frame]

    def desenhar(self):
        self.ator.draw()

    def pular(self):
        if self.no_chao:
            self.vel_y = -12
            self.no_chao = False
            self.ator.image = self.frame_pulo
            sounds.jump.play()


#------------ Classe do Inimigo
class Inimigo:
    def __init__(self, x):
        self.ator = Actor("enemy_idle_1", (x, posicao_chao_y))
        self.vel_x = random.choice([-1, 1])
        self.frames_correndo = ["enemy_run_1", "enemy_run_2"]
        self.morto = False
        self.indice_frame = 0
        self.contador_anim = 0

    def atualizar(self):
        if self.morto:
            return
        self.ator.x += self.vel_x
        if self.ator.x < 50 or self.ator.x > LARGURA - 50:
            self.vel_x *= -1
        self.animar(self.frames_correndo)

    def animar(self, frames):
        self.contador_anim += 1
        if self.contador_anim >= 10:
            self.contador_anim = 0
            self.indice_frame = (self.indice_frame + 1) % len(frames)
            self.ator.image = frames[self.indice_frame]

    def desenhar(self):
        self.ator.draw()


heroi = Heroi(100, 500)
inimigos = []

#------------ Reinicia a fase
def reiniciar_fase():
    global heroi, inimigos, fase_atual, fase_concluida, temporizador_vitoria
    heroi = Heroi(100, 500)
    inimigos = []
    espacamento = 150
    inicio_x = max(250, LARGURA // 2 - ((fase_atual - 1) * espacamento // 2))
    for i in range(fase_atual):
        x = min(inicio_x + i * espacamento, LARGURA - 60)
        inimigos.append(Inimigo(x))
    fase_concluida = False
    temporizador_vitoria = 0


def draw():
    screen.clear()
    if estado_atual == ESTADO_MENU:
        screen.blit(fundo_menu, (0, 0))
        screen.draw.text("ZUMBI HERO", center=(LARGURA // 2, 100), fontsize=48, color="white")
        screen.draw.filled_rect(Rect((LARGURA // 2 - 100, 180), (200, 50)), "orange")
        screen.draw.text("START", center=(LARGURA // 2, 205), fontsize=36, color="black")
        screen.draw.filled_rect(Rect((LARGURA // 2 - 100, 260), (200, 50)), "skyblue")
        label = "MUSIC: ON" if som_ativo else "MUSIC: OFF"
        screen.draw.text(label, center=(LARGURA // 2, 285), fontsize=28, color="black")
        screen.draw.filled_rect(Rect((LARGURA // 2 - 100, 340), (200, 50)), "red")
        screen.draw.text("EXIT", center=(LARGURA // 2, 365), fontsize=36, color="white")

    elif estado_atual == ESTADO_JOGANDO:
        fundo_index = min(fase_atual - 1, len(fundos) - 1)
        screen.blit(fundos[fundo_index], (0, 0))
        screen.blit(tile_chao, (0, posicao_chao_y))
        heroi.desenhar()
        for inimigo in inimigos:
            inimigo.desenhar()
        if fase_concluida:
            screen.draw.text("YOU WIN!", center=(LARGURA // 2, 100), fontsize=60, color="yellow")
            screen.draw.filled_rect(Rect((LARGURA // 2 - 100, 160), (200, 50)), "green")
            screen.draw.text("NEXT LEVEL", center=(LARGURA // 2, 185), fontsize=36, color="black")

    elif estado_atual == ESTADO_VITORIA_FINAL:
        screen.blit(fundo_vitoria, (0, 0))
        screen.draw.text("JOGO GANHO!", center=(LARGURA // 2, 150), fontsize=48, color="gold")
        desenhar_trofeu(LARGURA // 2 + 180, 170)
        screen.draw.filled_rect(Rect((LARGURA // 2 - 100, 340), (200, 50)), "orange")
        screen.draw.text("MENU", center=(LARGURA // 2, 365), fontsize=36, color="black")

    elif estado_atual == ESTADO_GAMEOVER:
        screen.fill("black")
        screen.draw.text("GAME OVER", center=(LARGURA // 2, 200), fontsize=60, color="red")
        screen.draw.filled_rect(Rect((LARGURA // 2 - 100, 340), (200, 50)), "orange")
        screen.draw.text("MENU", center=(LARGURA // 2, 365), fontsize=36, color="black")


def update():
    global estado_atual, fase_concluida, temporizador_vitoria, fase_atual

    if estado_atual == ESTADO_JOGANDO:
        heroi.atualizar()
        for inimigo in inimigos:
            inimigo.atualizar()

        for inimigo in inimigos:
            if inimigo.morto:
                continue
            if heroi.ator.colliderect(inimigo.ator):
                if heroi.vel_y > 0:
                    inimigo.ator.image = "enemy_slide"
                    inimigo.morto = True
                    heroi.vel_y = -10
                else:
                    estado_atual = ESTADO_GAMEOVER

        if all(e.morto for e in inimigos) and not fase_concluida:
            fase_concluida = True
            temporizador_vitoria = 120

        if fase_concluida and temporizador_vitoria > 0:
            temporizador_vitoria -= 1
            if temporizador_vitoria == 0:
                if fase_atual < 3:
                    fase_atual += 1
                    reiniciar_fase()
                else:
                    estado_atual = ESTADO_VITORIA_FINAL


def on_key_down(tecla):
    if tecla == keys.SPACE:
        heroi.pular()


def on_mouse_down(posicao):
    global estado_atual, som_ativo, fase_atual
    x, y = posicao
    if estado_atual == ESTADO_MENU:
        if 180 <= y <= 230:
            estado_atual = ESTADO_JOGANDO
            reiniciar_fase()
        elif 260 <= y <= 310:
            som_ativo = not som_ativo
            if som_ativo:
                music.play("music")
            else:
                music.stop()
        elif 340 <= y <= 390:
            exit()

    elif estado_atual == ESTADO_JOGANDO and fase_concluida:
        if 160 <= y <= 210 and LARGURA // 2 - 100 <= x <= LARGURA // 2 + 100:
            fase_atual += 1
            if fase_atual > 3:
                estado_atual = ESTADO_VITORIA_FINAL
            else:
                reiniciar_fase()

    elif estado_atual in [ESTADO_VITORIA_FINAL, ESTADO_GAMEOVER]:
        if 340 <= y <= 390 and LARGURA // 2 - 100 <= x <= LARGURA // 2 + 100:
            estado_atual = ESTADO_MENU
            fase_atual = 1


#------------ Desenha um troféu na tela
def desenhar_trofeu(x, y):
    screen.draw.filled_rect(Rect((x - 15, y), (30, 40)), "gold")
    screen.draw.rect(Rect((x - 15, y), (30, 40)), "orange")
    screen.draw.filled_circle((x - 25, y + 10), 7, "gold")
    screen.draw.filled_circle((x + 25, y + 10), 7, "gold")
    screen.draw.filled_rect(Rect((x - 20, y + 40), (40, 10)), "brown")
    screen.draw.rect(Rect((x - 20, y + 40), (40, 10)), "black")
    screen.draw.filled_circle((x, y + 10), 4, "white")


#------------ Inicia a música de fundo
music.set_volume(0.3)
if som_ativo:
    music.play("music")

#------------ Inicia o jogo com Pygame Zero
pgzrun.go()
