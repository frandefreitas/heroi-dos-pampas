# ================================
# Author: Francisco de Freitas Kemle
# JOGO: Herói dos Pampas
# Desenvolvido em Python com Pygame
# O jogador controla um gaúcho que atira chimarrões nos inimigos.
# As fases fazem alusão a cidades do Rio Grande do Sul.
# ================================

# Importação das bibliotecas essenciais
import pygame   # Biblioteca principal para jogos 2D em Python
import random   # Para gerar posições aleatórias dos inimigos
import sys      # Para encerrar o jogo corretamente
import os       # Para lidar com caminhos de arquivos

# Inicializa todos os módulos do Pygame
pygame.init()

# Define as dimensões da tela do jogo
LARGURA, ALTURA = 1536, 1024  # Largura e altura da janela
TELA = pygame.display.set_mode((LARGURA, ALTURA))  # Cria a janela do jogo
pygame.display.set_caption("Herói dos Pampas")  # Define o título da janela

# Define o caminho da pasta onde estão os assets (imagens, sons, etc.)
CAMINHO_ASSETS = os.path.join(os.path.dirname(__file__), 'assets')

# Lista com os arquivos dos fundos de cada fase
# As imagens são redimensionadas para o tamanho da tela
# A última imagem é usada como tela final de sucesso
# (e.g., quando o jogador termina o jogo com vitória)
diretorios_fundos = [
    'fundo_pampa.jpg',     # Menu
    'fundo_pampa-2.jpg',   # Fase 1
    'fundo_pampa-3.jpg',   # Fase 2
    'fundo_pampa-4.jpg',   # Fase 3
    'fundo_pampa-5.jpg',   # Fase 4
    'fundo_pampa-6.jpg',   # Fase 5
    'fundo_pampa-7.jpg',   # Fase 6
    'fundo_pampa-8.jpg',   # Fase 7
    'fundo_pampa-9.jpg',   # Fase 8
    'fundo_pampa-10.jpg',  # Fase 9
    'fundo_pampa-11.jpg',  # Fase 10
    'fundo_pampa-12.jpg',  # Fase 11
    'fundo_pampa-13.jpg',  # Fase 12
    'fundo_pampa-14.jpg',  # Fase 13
    'success.jpg'          # Fundo final (usado para proteção de índice)
]

BANDEIRA_IMG = pygame.image.load(os.path.join(CAMINHO_ASSETS, 'bandeira.png'))

fundos = [
    pygame.transform.scale(pygame.image.load(os.path.join(CAMINHO_ASSETS, fundo)), (LARGURA, ALTURA))
    for fundo in diretorios_fundos
]

# Carrega a imagem do jogador (Gaúcho) e redimensiona
GAUCHO_ORIGINAL = pygame.image.load(os.path.join(CAMINHO_ASSETS, 'gaucho.png'))
GAUCHO = pygame.transform.scale(GAUCHO_ORIGINAL, (
    int(GAUCHO_ORIGINAL.get_width() * 0.11),
    int(GAUCHO_ORIGINAL.get_height() * 0.11)
))


# Carrega múltiplos sprites de inimigos com tamanhos fixos
nomes_inimigos = [
    'inimigo.png', 'inimigo-2.png', 'inimigo-3.png', 'inimigo-4.png',
    'inimigo-5.png', 'inimigo-6.png', 'inimigo-7.png', 'inimigo-8.png',
    'inimigo-9.png', 'inimigo-10.png', 'inimigo-11.png', 'inimigo-12.png'
]

sprites_inimigos = []
for nome in nomes_inimigos:
    img = pygame.image.load(os.path.join(CAMINHO_ASSETS, nome))
    img = pygame.transform.scale(img, (
        int(img.get_width() * 0.11),
        int(img.get_height() * 0.11)
    ))
    sprites_inimigos.append(img)

# Carrega o sprite do chimarrão (projetil) e redimensiona
BALA = pygame.transform.scale(pygame.image.load(os.path.join(CAMINHO_ASSETS, 'bala.png')), (65, 65))

# Tenta carregar os arquivos de som (tiro e impacto)
try:
    TIRO_SOM = pygame.mixer.Sound(os.path.join(CAMINHO_ASSETS, 'tiro.wav'))
    IMPACTO_SOM = pygame.mixer.Sound(os.path.join(CAMINHO_ASSETS, 'impacto.wav'))
except:
    TIRO_SOM = IMPACTO_SOM = None  # Se der erro, desativa os sons

# Carrega imagem de Game Over redimensionada
GAME_OVER_IMG = pygame.transform.scale(pygame.image.load(os.path.join(CAMINHO_ASSETS, 'game-over.jpg')), (LARGURA, ALTURA))

# Carrega imagem final de sucesso redimensionada
FINAL_SUCCESS_IMG = pygame.transform.scale(pygame.image.load(os.path.join(CAMINHO_ASSETS, 'success.jpg')), (LARGURA, ALTURA))

# Define os frames por segundo do jogo
FPS = 60
clock = pygame.time.Clock()

# Função auxiliar para desenhar texto branco com sombra preta
def desenhar_texto_com_sombra(texto, fonte, cor_texto, posicao, superficie):
    sombra = fonte.render(texto, True, (0, 0, 0))
    texto_surface = fonte.render(texto, True, cor_texto)
    x, y = posicao
    superficie.blit(sombra, (x + 2, y + 2))
    superficie.blit(texto_surface, (x, y))

# Exibe vinheta de transição entre fases
def mostrar_vinheta(fase_num, vidas):
    TELA.blit(fundos[min(fase_num, len(fundos)-1)], (0, 0))
    nome_fase = nomes_fase.get(fase_num, "")
    texto_fase = fonte.render(nome_fase, True, (255, 255, 255))
    texto_vida = fonte_pequena.render(f"Vida: {vidas}", True, (255, 255, 255))

    x_fase = (LARGURA - texto_fase.get_width()) // 2
    y_fase = (ALTURA - texto_fase.get_height()) // 2 - 30
    x_vida = (LARGURA - texto_vida.get_width()) // 2
    y_vida = y_fase + 80

    desenhar_texto_com_sombra(nome_fase, fonte, (255, 255, 255), (x_fase, y_fase), TELA)
    desenhar_texto_com_sombra(f"Vida: {vidas}", fonte_pequena, (255, 255, 255), (x_vida, y_vida), TELA)

    pygame.display.flip()
    pygame.time.wait(3000)

# ================================
# CLASSES PRINCIPAIS DO JOGO
# ================================

# Classe que representa o jogador (Gaúcho)
class Jogador(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = GAUCHO
        self.rect = self.image.get_rect()
        self.rect.center = (100, ALTURA // 2)
        self.vida = 5

    def update(self, keys):
        if keys[pygame.K_UP] and self.rect.top > 50:
            self.rect.y -= 5
        if keys[pygame.K_DOWN] and self.rect.bottom < ALTURA - 50:
            self.rect.y += 5
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= 5
        if keys[pygame.K_RIGHT] and self.rect.right < LARGURA:
            self.rect.x += 5

class Inimigo(pygame.sprite.Sprite):
    ultimas_y = []

    def __init__(self):
        super().__init__()
        self.image = random.choice(sprites_inimigos)
        self.rect = self.image.get_rect()
        self.rect.x = LARGURA
        self.velocidade = random.randint(3, 8)

        tentativa = 0
        
        while tentativa < 10:
            y = random.randint(50, ALTURA - self.rect.height - 50)

            if all(abs(y - usado) > 130 for usado in Inimigo.ultimas_y):
                self.rect.y = y
                Inimigo.ultimas_y.append(y)
                if len(Inimigo.ultimas_y) > 10:
                    Inimigo.ultimas_y.pop(0)
                break
            tentativa += 1
        else:
            self.rect.y = random.randint(0, ALTURA - self.rect.height)

    def update(self):
        self.rect.x -= self.velocidade
        
        if self.rect.right < 0:
            self.kill()

class Bandeira(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.base_image = pygame.transform.scale(
            BANDEIRA_IMG,
            (int(BANDEIRA_IMG.get_width() * 0.2), int(BANDEIRA_IMG.get_height() * 0.2))
        )
        self.image = self.base_image.copy()

        # Posição inicial: completamente fora da tela na base
        self.target_y = ALTURA - 20
        self.rect = self.image.get_rect(bottomright=(LARGURA - 30, ALTURA + self.base_image.get_height()))
        self.alpha = 0
        self.velocidade_subida = 6

    def update(self):
        # Subida vertical até a posição final
        if self.rect.bottom > self.target_y:
            self.rect.y -= self.velocidade_subida

        # Fade-in
        if self.alpha < 255:
            self.alpha += 5
            self.alpha = min(self.alpha, 255)

        self.image = self.base_image.copy()
        self.image.set_alpha(self.alpha)

bandeira_group = pygame.sprite.Group()
inicio_fase = 0
bandeira_ativa = False
primeira_bandeira_mostrada = False

# Menu principal atualizado com seleção
menu_opcoes = ["Jogar", "Instruções", "Créditos", "Sair"]
indice_opcao = 0

# Novas telas para instruções e créditos
def mostrar_instrucoes():
    TELA.blit(fundos[0], (0, 0))
    instrucoes = [
        "Setas para mover o Gaúcho", 
        "Espaço para jogar chimarrão nos inimigos"
    ]
    base_y = 500  # mais abaixo

    for i, linha in enumerate(instrucoes):
        txt = fonte.render(linha, True, (255, 255, 255))
        desenhar_texto_com_sombra(
            linha, fonte, (255, 255, 255),
            ((LARGURA - txt.get_width()) // 2, base_y + i * 60), TELA
        )

    voltar = fonte.render('"Esc" para Voltar', True, (255, 255, 255))
    desenhar_texto_com_sombra(
        '"Esc" para Voltar', fonte, (255, 255, 255),
        ((LARGURA - voltar.get_width()) // 2, base_y + len(instrucoes) * 60 + 40), TELA
    )

    pygame.display.flip()
    aguardar_voltar()


def resetar_jogo():
    global pontos, fase_atual, vinheta_mostrada
    pontos = 0
    jogador.vida = 5
    fase_atual = 0
    vinheta_mostrada = False
    inimigos.empty()
    balas.empty()
    jogador.rect.center = (100, ALTURA // 2)
    Inimigo.ultimas_y.clear()

    # ⚠️ Redesenha fundo inicial e personagem para evitar "sombra visual"
    TELA.blit(fundos[0], (0, 0))
    jogador_group.draw(TELA)
    desenhar_texto_com_sombra(f"Pontos: {pontos}  Vida: {jogador.vida}", fonte, (255, 255, 255), (20, 90), TELA)
    pygame.display.flip()
    pygame.time.wait(1000)


def mostrar_creditos():
    TELA.blit(fundos[0], (0, 0))

    creditos = [
        "Idealizado e desenvolvido pelo Engenheiro de Software",
        "Francisco de Freitas Kemle, em junho de 2025."
    ]

    for i, linha in enumerate(creditos):
        txt = fonte.render(linha, True, (255, 255, 255))
        desenhar_texto_com_sombra(linha, fonte, (255, 255, 255), ((LARGURA - txt.get_width()) // 2, 530 + i * 60), TELA)

    voltar = fonte.render('"Esc" para Voltar', True, (255, 255, 255))
    desenhar_texto_com_sombra('"Esc" para Voltar', fonte, (255, 255, 255), ((LARGURA - voltar.get_width()) // 2, 710), TELA)
    pygame.display.flip()
    aguardar_voltar()

def aguardar_voltar():
    global fase_atual
    esperando = True
    while esperando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                fase_atual = 0
                esperando = False

class Bala(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = BALA
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self):
        self.rect.x += 10
        if self.rect.left > LARGURA:
            self.kill()

# ================================
# CONFIGURAÇÕES E VARIÁVEIS DO JOGO
# ================================

jogador = Jogador()
jogador_group = pygame.sprite.Group(jogador)
inimigos = pygame.sprite.Group()
balas = pygame.sprite.Group()

fonte = pygame.font.SysFont("calibri", 40, bold=True)
fonte_pequena = pygame.font.SysFont("calibri", 30, bold=True)

TIMER_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(TIMER_EVENT, 400)

pontos = 0
fase_atual = 0

nomes_fase = {
    1: "Fase Bagé",
    2: "Fase Pelotas",
    3: "Fase Rio Grande",
    4: "Fase Aceguá",
    5: "Fase Lajeado",
    6: "Fase Gramado",
    7: "Fase Quaraí",
    8: "Fase Farroupilha",
    9: "Fase Torres",
    10: "Fase Bento Gonçalves",
    11: "Fase Porto Alegre",
    12: "Fase Santa Vitória do Palmar",
    13: "Fase Piratini"
}

rodando = True

rodando = True
vinheta_mostrada = False

while rodando:
    clock.tick(FPS)
    keys = pygame.key.get_pressed()

    if jogador.vida > 0:
        tempo_atual = pygame.time.get_ticks() - inicio_fase
        if not primeira_bandeira_mostrada and tempo_atual >= 24000 and fase_atual > 0:
            inicio_fase = pygame.time.get_ticks()
            bandeira_group.empty()
            bandeira_group.add(Bandeira())
            bandeira_ativa = True

    bandeira = pygame.sprite.spritecollideany(jogador, bandeira_group)
    if bandeira and jogador.rect.colliderect(bandeira.rect):
        # Animação leve
        for i in range(5):
            TELA.blit(fundos[min(fase_atual, len(fundos)-1)], (0, 0))
            jogador_group.draw(TELA)
            bandeira_group.draw(TELA)
            pygame.display.flip()
            pygame.time.delay(60)

        if fase_atual < 13:
            fase_atual += 1
            bandeira_group.empty()
            vinheta_mostrada = False
            bandeira_ativa = False
            primeira_bandeira_mostrada = False
            inicio_fase = pygame.time.get_ticks()
        else:
            fase_atual = 14

            # Exibir sucesso final imediatamente
            TELA.blit(FINAL_SUCCESS_IMG, (0, 0))
            pygame.display.flip()
            pygame.time.wait(5000)

            pontos = 0
            jogador.vida = 5
            fase_atual = 0
            vinheta_mostrada = False
            inimigos.empty()
            balas.empty()
            jogador.rect.center = (100, ALTURA // 2)
            indice_opcao = 0 
            inicio_fase = pygame.time.get_ticks()
        vinheta_mostrada = False
        bandeira_ativa = False
        primeira_bandeira_mostrada = False
        inicio_fase = pygame.time.get_ticks()

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False
        if evento.type == pygame.KEYDOWN:
            if fase_atual == 0:
                if evento.key == pygame.K_UP:
                    indice_opcao = (indice_opcao - 1) % len(menu_opcoes)
                elif evento.key == pygame.K_DOWN:
                    indice_opcao = (indice_opcao + 1) % len(menu_opcoes)
                elif evento.key == pygame.K_RETURN:
                    if menu_opcoes[indice_opcao] == "Jogar":
                        fase_atual = 1      
                        bandeira_ativa = False
                        primeira_bandeira_mostrada = False
                        vinheta_mostrada = False
                        inicio_fase = pygame.time.get_ticks()
                    elif menu_opcoes[indice_opcao] == "Instruções":
                        mostrar_instrucoes()
                    elif menu_opcoes[indice_opcao] == "Créditos":
                        mostrar_creditos()
                    elif menu_opcoes[indice_opcao] == "Sair":
                        rodando = False
            else:
                if evento.key == pygame.K_SPACE:
                    nova_bala = Bala(jogador.rect.right, jogador.rect.centery)
                    balas.add(nova_bala)
                    if TIRO_SOM:
                        TIRO_SOM.play()
        if evento.type == TIMER_EVENT and fase_atual > 0:
            inimigos.add(Inimigo())

    if fase_atual == 0:
        TELA.blit(fundos[0], (0, 0))
        for i, opcao in enumerate(menu_opcoes):
            if i == indice_opcao:
                cor = (0, 100, 0)
                sombra = (255, 255, 255)
            else:
                cor = (255, 255, 255)
                sombra = (0, 0, 0)
            texto = fonte.render(opcao, True, cor)
            x = (LARGURA - texto.get_width()) // 2
            y = 500 + i * 80
            sombra_surface = fonte.render(opcao, True, sombra)
            TELA.blit(sombra_surface, (x + 2, y + 2))
            TELA.blit(texto, (x, y))
        pygame.display.flip()
        continue

    # Exibir vinheta uma vez ao mudar de fase
    if not vinheta_mostrada:
        inimigos.empty()
        balas.empty()
        jogador.rect.center = (100, ALTURA // 2)
        Inimigo.ultimas_y.clear()

        mostrar_vinheta(fase_atual, jogador.vida)
        vinheta_mostrada = True
        continue  # Garante que não atualize nada nesse frame ainda


    # Atualizações do jogo
    jogador.update(keys)
    inimigos.update()
    balas.update()

    TELA.blit(fundos[min(fase_atual, len(fundos)-1)], (0, 0))
    jogador_group.draw(TELA)
    inimigos.draw(TELA)
    balas.draw(TELA)
    bandeira_group.draw(TELA)
    bandeira_group.update()

    for bala in pygame.sprite.groupcollide(balas, inimigos, True, True):
        pontos += 1
        if IMPACTO_SOM:
            IMPACTO_SOM.play()
        if pontos >= 100:
            jogador.vida += 1
            pontos = 0

    if pygame.sprite.spritecollideany(jogador, inimigos):
        jogador.vida -= 1
        bandeira_group.empty()
        inimigos.empty()
        balas.empty()
        jogador.rect.center = (100, ALTURA // 2) 
        inicio_fase = pygame.time.get_ticks()
        primeira_bandeira_mostrada = False

        Inimigo.ultimas_y.clear()

        if jogador.vida in [5, 4, 3, 2, 1]:
            mostrar_vinheta(fase_atual, jogador.vida)

    # HUD
    desenhar_texto_com_sombra(f"Pontos: {pontos}  Vida: {jogador.vida}", fonte_pequena, (255, 255, 255), (20, 90), TELA)


    if fase_atual <= 13:
        nome = nomes_fase.get(fase_atual, "")
        x_f = (LARGURA - fonte.size(nome)[0]) // 2
        desenhar_texto_com_sombra(nome, fonte, (255, 255, 255), (x_f, 90), TELA)

    pygame.display.flip()

    # Game over
    if jogador.vida <= 0:
        TELA.blit(GAME_OVER_IMG, (0, 0))
        pygame.display.flip()
        pygame.time.wait(5000)
        pontos = 0
        jogador.vida = 5
        fase_atual = 0
        inicio_fase = pygame.time.get_ticks()
        vinheta_mostrada = False
        inimigos.empty()
        balas.empty()
        jogador.rect.center = (100, ALTURA // 2)
        indice_opcao = 0 
        bandeira_group.empty()
        continue

    # Fim de jogo com sucesso
    if fase_atual == 14:
        TELA.blit(FINAL_SUCCESS_IMG, (0, 0))
        pygame.display.flip()
        pygame.time.wait(5000)
        pontos = 0
        jogador.vida = 5
        fase_atual = 0
        inicio_fase = pygame.time.get_ticks()
        vinheta_mostrada = False
        inimigos.empty()
        balas.empty()
        jogador.rect.center = (100, ALTURA // 2)
        indice_opcao = 0 
        bandeira_group.empty()
        continue

pygame.quit()
sys.exit()
