import pygame

# Constantes
EMPTY = 0
PLAYER1 = 1
PLAYER2 = 2
ROWS = 6
COLS = 7

# Cores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
YELLOW = (255, 204, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
GRAY = (200, 200, 200)
ORANGE = (244, 162, 97)
ORANGE2 = (244, 190, 123)

#Fundos
FUNDO = pygame.image.load("fundo.png")
FUNDO2 = pygame.image.load("fundo2.png")

# Configurações de tela
SQUARESIZE = 100
WIDTH = COLS * SQUARESIZE
HEIGHT = (ROWS + 1) * SQUARESIZE  # +1 para espaço para mostrar a peça antes de cair
SIZE = (WIDTH, HEIGHT)
width_tree, height_tree = 800, 600  # largura e altura da árvore
NODE_RADIUS = 20
LINE_WIDTH = 2
regras_4_em_linha = (
    "Número de jogadores: 2 (cada um com uma cor distinta,\n"
    " normalmente vermelho e amarelo).\n\n"
    "Tabuleiro: Grade vertical com 6 linhas e 7 colunas.\n\n"
    "Turnos: Os jogadores jogam alternadamente.\n\n"
    "Jogada: Em cada turno, o jogador escolhe uma coluna\n"
    " onde deseja jogar a sua peça.\n"
    " A peça cai até a posição mais baixa disponível\n"
    " nessa coluna (como a gravidade).\n\n"
    "Vitória: Ganha quem for o primeiro a alinhar\n"
    " quatro peças consecutivas da sua cor:\n"
    " Na horizontal,na vertical ou na diagonal.\n\n"
    "Empate: Se o tabuleiro ficar completamente cheio e\n"
    " nenhum jogador conseguir alinhar quatro peças,\n "
    "o jogo termina empatado."
)

pygame.init()

class AnimatedButton:
    def __init__(self, text, font, x, y, width, height, color, hover_color, text_color):
        self.text = text
        self.font = font
        self.base_rect = pygame.Rect(x, y, width, height)
        self.rect = self.base_rect.copy()
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.grow_scale = 1.1
        self.hovered = False

    def draw(self, screen, mouse_pos):
        self.hovered = self.base_rect.collidepoint(mouse_pos)

        # Realce do botão
        if self.hovered:
            scaled_width = int(self.base_rect.width * self.grow_scale)
            scaled_height = int(self.base_rect.height * self.grow_scale)
        else:
            scaled_width = self.base_rect.width
            scaled_height = self.base_rect.height

        self.rect = pygame.Rect(
            self.base_rect.centerx - scaled_width // 2,
            self.base_rect.centery - scaled_height // 2,
            scaled_width,
            scaled_height,
        )

        current_color = self.hover_color if self.hovered else self.color
        pygame.draw.rect(screen, current_color, self.rect, border_radius=12)

        # Desenha o texto
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def is_clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and self.hovered