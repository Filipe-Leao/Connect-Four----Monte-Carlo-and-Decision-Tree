# game.py
from board import *
from variables import *

class ConnectedFourGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(SIZE)
        pygame.display.set_caption("Quatro em Linha")
        self.myfont = pygame.font.SysFont("monospace", 75)
        self.board = Board()
        self.clock = pygame.time.Clock()

    def draw_board(self):
        """Desenha o tabuleiro e as peças na tela"""
        # Limpa a área acima do tabuleiro (para mostrar peça antes de cair)
        pygame.draw.rect(self.screen, BLACK, (0, 0, WIDTH, SQUARESIZE))
        # Desenha o tabuleiro
        for c in range(COLS):
            for r in range(ROWS):
                # Desenha o retângulo azul
                self.screen.blit(FUNDO2, (c * SQUARESIZE, r * SQUARESIZE + SQUARESIZE))
                # Desenha o círculo branco (espaço vazio)
                pygame.draw.circle(self.screen, WHITE,
                                   (int(c * SQUARESIZE + SQUARESIZE / 2),
                                    int(r * SQUARESIZE + SQUARESIZE + SQUARESIZE / 2)),
                                   SQUARESIZE / 2 - 5)
        # Desenha as peças
        board_state = self.board.get_board()
        for c in range(COLS):
            for r in range(ROWS):
                if board_state[r][c] == PLAYER1:
                    pygame.draw.circle(self.screen, RED,
                                       (int(c * SQUARESIZE + SQUARESIZE / 2),
                                        int(r * SQUARESIZE + SQUARESIZE + SQUARESIZE / 2)),
                                       SQUARESIZE / 2 - 5)
                elif board_state[r][c] == PLAYER2:
                    pygame.draw.circle(self.screen, YELLOW,
                                       (int(c * SQUARESIZE + SQUARESIZE / 2),
                                        int(r * SQUARESIZE + SQUARESIZE + SQUARESIZE / 2)),
                                       SQUARESIZE / 2 - 5)
        pygame.display.update()

    def draw_moving_piece(self, posx):
        """Desenha a peça que acompanha o movimento do mouse antes de cair"""
        # Limpa a área acima do tabuleiro
        pygame.draw.rect(self.screen, BLACK, (0, 0, WIDTH, SQUARESIZE))
        
        if self.board.get_current_player() == PLAYER1: # Desenha a peça do jogador atual
            pygame.draw.circle(self.screen, RED, (posx, int(SQUARESIZE / 2)), SQUARESIZE / 2 - 5)
        else:
            pygame.draw.circle(self.screen, YELLOW, (posx, int(SQUARESIZE / 2)), SQUARESIZE / 2 - 5)

        pygame.display.update()

    def show_message(self, message, color=RED):
        """Mostra uma mensagem no ecrã"""
        label = self.myfont.render(message, 1, color)
        text_rect = label.get_rect(center=(WIDTH / 2, SQUARESIZE / 2)) # Centraliza a mensagem
        self.screen.blit(label, text_rect)
        pygame.display.update()

    def play_game(self, return_to_menu_callback=None):
        """Loop principal do jogo"""
        self.draw_board()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()
                    return

                # Mostra a peça que segue o movimento do rato
                if event.type == pygame.MOUSEMOTION and not self.board.is_game_over():
                    posx = event.pos[0]
                    self.draw_moving_piece(posx)

                # Processa o clique para colocar uma peça
                if event.type == pygame.MOUSEBUTTONDOWN and not self.board.is_game_over():
                    posx = event.pos[0]
                    col = int(posx // SQUARESIZE)

                    # Tenta colocar a peça
                    move_successful = self.board.drop_piece(col)

                    if move_successful:
                        self.draw_board()

                        # Verifica se o jogo acabou
                        if self.board.is_game_over():
                            winner = self.board.get_winner()
                            if winner:
                                message = f"Jogador {winner} venceu!"
                            else:
                                message = "Empate!"
                            return self.show_end_game_menu()  # Menu de fim de jogo

                # Reinicia o jogo com tecla 'r'
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.board.reset()
                        self.draw_board()
                        if self.board.is_game_over():
                            self.show_message("Novo jogo!")
                            pygame.time.wait(1000)
                            self.draw_board()
                    elif event.key == pygame.K_ESCAPE:
                        return False

            self.clock.tick(60)  # Limita o framerate a 60 FPS

        return False  # Sair do jogo

    def show_end_game_menu(self):
        """Mostra o menu de fim de jogo com botões animados"""
        winner = self.board.get_winner()
        if winner:
            message = f"Jogador {winner} venceu!"
            color = RED if winner == PLAYER1 else YELLOW
        else:
            message = "Empate!"
            color = (150, 150, 150)  # Cinza para empate

        # Mensagem
        message_font = pygame.font.SysFont("monospace", 35)
        button_font = pygame.font.SysFont("monospace", 25)
        message_text = message_font.render(message, True, WHITE)
        message_rect = message_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100))

        # Botões animados
        button_width = 230
        button_height = 60
        restart_btn = AnimatedButton("Recomeçar", button_font,
                                     WIDTH // 2 - button_width - 20, HEIGHT // 2,
                                     button_width, button_height,
                                     (100, 200, 100), (50, 180, 50), BLACK)

        menu_btn = AnimatedButton("Menu Principal", button_font,
                                  WIDTH // 2 + 20, HEIGHT // 2,
                                  button_width, button_height,
                                  (200, 100, 100), (180, 50, 50), BLACK)

        buttons = [restart_btn, menu_btn]

        waiting = True
        while waiting:
            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return False
                if restart_btn.is_clicked(event):
                    self.board.reset()
                    self.draw_board()
                    return True  # Recomeçar o jogo
                elif menu_btn.is_clicked(event):
                    return False  # Volta ao menu principal

            # Caixa atrás da mensagem
            msg_box = pygame.Rect(WIDTH // 2 - 200, HEIGHT // 2 - 140, 400, 80)
            pygame.draw.rect(self.screen, (50, 50, 50), msg_box)
            pygame.draw.rect(self.screen, color, msg_box, 4)
            self.screen.blit(message_text, message_rect)

            # Desenha botões animados
            for btn in buttons:
                btn.draw(self.screen, mouse_pos)

            pygame.display.update()
            pygame.time.wait(10)

        return False


if __name__ == "__main__":
    game = ConnectedFourGame()
    game.play_game()