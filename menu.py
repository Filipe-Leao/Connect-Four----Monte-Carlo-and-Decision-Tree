# menu.py
import math
import sys
from board import Board
from game import ConnectedFourGame
from montecarlo import MonteCarlo_Player
from decisiontree import DecisionTree_Player
from variables import *
import numpy as np
import random


class Menu:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(SIZE)
        pygame.display.set_caption("Quatro em Linha - Menu")
        self.font_large = pygame.font.SysFont("monospace", 50)  # Titulo
        self.font_medium = pygame.font.SysFont("monospace", 30)  # Botões
        self.font_small = pygame.font.SysFont("monospace", 20)  # Instruções
        self.clock = pygame.time.Clock()
        self.game = ConnectedFourGame()  # Chama o jogo

    def show_main_menu(self):
        running = True

        button_width = 300
        button_height = 50
        button_x = WIDTH // 2 - button_width // 2

        imagem_pergunta = pygame.image.load("ponto.png").convert_alpha()  # Ponto de interrogação
        imagem_pergunta = pygame.transform.scale(imagem_pergunta, (50, 50))  # Redimensionamento

        # Obtem retângulo da imagem (serve para detectar cliques)
        botao_rect = imagem_pergunta.get_rect(topleft=(610, 510))  # Posição do botão
        # Cria botões animados
        human_vs_human_btn = AnimatedButton("Humano vs Humano", self.font_medium, button_x, 225, button_width,
                                            button_height, RED, (200, 0, 0), BLACK)
        human_vs_ai_btn = AnimatedButton("Humano vs IA", self.font_medium, button_x, 325, button_width, button_height,
                                         YELLOW, (220, 180, 0), BLACK)
        ai_vs_ai_btn = AnimatedButton("IA vs IA", self.font_medium, button_x, 425, button_width, button_height, ORANGE,
                                      (224, 122, 63), BLACK)
        exit_btn = AnimatedButton("Sair", self.font_medium, button_x, 525, button_width, button_height, GRAY,
                                  (100, 100, 100), BLACK)

        buttons = [human_vs_human_btn, human_vs_ai_btn, ai_vs_ai_btn, exit_btn]

        while running:
            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if human_vs_human_btn.is_clicked(event):
                    self.start_game_mode("human_vs_human")
                elif human_vs_ai_btn.is_clicked(event):
                    self.start_game_mode("human_vs_ai")
                elif ai_vs_ai_btn.is_clicked(event):
                    self.start_game_mode("ai_vs_ai")
                elif event.type == pygame.MOUSEBUTTONDOWN and botao_rect.collidepoint(event.pos):
                    self.start_game_mode("regras")
                elif exit_btn.is_clicked(event):
                    pygame.quit()
                    sys.exit()

            self.fundo = pygame.transform.scale(FUNDO, (700, 700))
            self.screen.blit(self.fundo, (0, 0))

            nomes = self.font_small.render("Diogo Padilha, Filipe Leão, Rita Nunes", True, WHITE)
            nomes_rect = nomes.get_rect(center=(WIDTH // 2, 650))
            self.screen.blit(nomes, nomes_rect)

            title = self.font_large.render("QUATRO EM LINHA", True, BLACK)
            title_rect = title.get_rect(center=(WIDTH // 2, 165))
            self.screen.blit(title, title_rect)

            # Desenha todos os botões
            for btn in buttons:
                btn.draw(self.screen, mouse_pos)
            self.screen.blit(imagem_pergunta, botao_rect)
            instruction = self.font_small.render("Escolha um modo de jogo", True, WHITE)
            instruction_rect = instruction.get_rect(center=(WIDTH // 2, 55))
            self.screen.blit(instruction, instruction_rect)

            pygame.display.update()
            self.clock.tick(60)

    def show_human_vs_ai_screen(self):
        running = True
        button_width = 300
        button_height = 50
        button_x = WIDTH // 2 - button_width // 2
        # Cria os botões animados
        mcts_easy_btn = AnimatedButton("MCTS fácil", self.font_medium, button_x, 225, button_width, button_height,
                                       RED, (200, 0, 0), BLACK)
        mcts_medium_btn = AnimatedButton("MCTS médio", self.font_medium, button_x, 300, button_width, button_height,
                                         YELLOW, (220, 180, 0), BLACK)
        mcts_hard_btn = AnimatedButton("MCTS difícil", self.font_medium, button_x, 375, button_width, button_height,
                                       ORANGE, (224, 122, 63), BLACK)
        decision_tree_btn = AnimatedButton("Decision Tree", self.font_medium, button_x, 450, button_width,
                                           button_height, ORANGE2, (255, 159, 107), BLACK)
        back_btn = AnimatedButton("Voltar", self.font_medium, button_x, 525, button_width, button_height, GRAY,
                                  (100, 100, 100), BLACK)
        buttons = [mcts_easy_btn, mcts_medium_btn, mcts_hard_btn, decision_tree_btn, back_btn]

        while running:
            mouse_pos = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if mcts_easy_btn.is_clicked(event):
                    print("Escolhido: MCTS fácil")
                    self.show_first_player_choice("easy")
                elif mcts_medium_btn.is_clicked(event):
                    print("Escolhido: MCTS médio")
                    self.show_first_player_choice("medium")
                elif mcts_hard_btn.is_clicked(event):
                    print("Escolhido: MCTS difícil")
                    self.show_first_player_choice("hard")
                elif decision_tree_btn.is_clicked(event):
                    print("Escolhido: Decision Tree")
                    self.show_first_player_choice("DT")
                elif back_btn.is_clicked(event):
                    running = False
                    self.show_main_menu()

            self.screen.blit(pygame.transform.scale(FUNDO, (700, 700)), (0, 0))
            title = self.font_large.render("Escolha a IA", True, BLACK)
            title_rect = title.get_rect(center=(WIDTH // 2, 150))
            self.screen.blit(title, title_rect)
            for btn in buttons:
                btn.draw(self.screen, mouse_pos)
            pygame.display.update()
            self.clock.tick(60)

    def show_ai_vs_ai_screen(self):
        running = True
        button_width = 300
        button_height = 50
        button_x = WIDTH // 2 - button_width // 2
        mcts_easy_1_btn = AnimatedButton("MCTS fácil", self.font_medium, button_x, 225, button_width, button_height,
                                         RED, (200, 0, 0), BLACK)
        mcts_medium_1_btn = AnimatedButton("MCTS médio", self.font_medium, button_x, 300, button_width, button_height,
                                           YELLOW, (220, 180, 0), BLACK)
        mcts_hard_1_btn = AnimatedButton("MCTS difícil", self.font_medium, button_x, 375, button_width, button_height,
                                         ORANGE, (224, 122, 63), BLACK)
        decision_tree_1_btn = AnimatedButton("Decision Tree", self.font_medium, button_x, 450, button_width,
                                             button_height, ORANGE2, (255, 159, 107), BLACK)
        back_btn = AnimatedButton("Voltar", self.font_medium, button_x, 525, button_width, button_height, GRAY,
                                  (100, 100, 100), BLACK)
        buttons = [mcts_easy_1_btn, mcts_medium_1_btn, mcts_hard_1_btn, decision_tree_1_btn, back_btn]
        while running:
            mouse_pos = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if mcts_easy_1_btn.is_clicked(event):
                    print("AI1 Escolhida: MCTS fácil")
                    running = False
                    self.show_second_ai_choice("easy")
                elif mcts_medium_1_btn.is_clicked(event):
                    print("AI1 Escolhida: MCTS médio")
                    running = False
                    self.show_second_ai_choice("medium")
                elif mcts_hard_1_btn.is_clicked(event):
                    print("AI1 Escolhida: MCTS difícil")
                    running = False
                    self.show_second_ai_choice("hard")
                elif decision_tree_1_btn.is_clicked(event):
                    print("AI1 Escolhida: Decision Tree")
                    running = False
                    self.show_second_ai_choice("DT")
                elif back_btn.is_clicked(event):
                    running = False
                    self.show_main_menu()

            self.screen.blit(pygame.transform.scale(FUNDO, (700, 700)), (0, 0))
            title = self.font_large.render("Escolha a IA1", True, BLACK)
            title_rect = title.get_rect(center=(WIDTH // 2, 160))
            self.screen.blit(title, title_rect)
            for btn in buttons:
                btn.draw(self.screen, mouse_pos)
            pygame.display.update()
            self.clock.tick(60)

    def show_rules_screen(self):
        running = True
        button_width = 300
        button_height = 50
        button_x = WIDTH // 2 - button_width // 2
        back_btn = AnimatedButton("Voltar", self.font_medium, button_x, 575, button_width, button_height, GRAY,
                                  (100, 100, 100), BLACK)
        while running:
            mouse_pos = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif back_btn.is_clicked(event):
                    running = False
                    self.show_main_menu()
                self.screen.blit(pygame.transform.scale(FUNDO2, (700, 700)), (0, 0))
                linhas = regras_4_em_linha.split('\n')
                xi = 40
                yi = 20
                espaco_entre_linhas = 28  # Espaçamento vertical
                for linha in linhas:
                    texto = self.font_small.render(linha, True, BLACK)
                    texto_rect = texto.get_rect(topleft=(xi, yi))
                    self.screen.blit(texto, texto_rect)
                    yi += espaco_entre_linhas
                back_btn.draw(self.screen, mouse_pos)
                pygame.display.update()
                self.clock.tick(60)

    def start_game_mode(self, mode):
        if mode == "human_vs_human":
            self.play_human_vs_human()
        elif mode == "human_vs_ai":
            self.show_human_vs_ai_screen()
        elif mode == "ai_vs_ai":
            self.show_ai_vs_ai_screen()
        elif mode == "regras":
            self.show_rules_screen()

    #    -------------------
    #    HUMANO VS. HUMANO
    #    -------------------

    def play_human_vs_human(self):
        """Inicia jogo Humano vs Humano"""
        self.game.board.reset()
        play_again = True
        while play_again:
            play_again = self.game.play_game()  # Jogar novamente
        self.show_main_menu()  # Retorna ao menu principal após o jogo

    #    -------------------
    #    HUMANO VS. AI
    #    -------------------

    def show_first_player_choice(self, difficulty):
        running = True
        button_width = 300
        button_height = 50
        button_x = WIDTH // 2 - button_width // 2
        # Cria botões animados
        human_btn = AnimatedButton("Humano", self.font_medium, button_x, 250, button_width, button_height, RED,
                                   (200, 0, 0), BLACK)
        ai_btn = AnimatedButton("AI", self.font_medium, button_x, 350, button_width, button_height, YELLOW,
                                (220, 180, 0), BLACK)
        back_btn = AnimatedButton("Voltar", self.font_medium, button_x, 450, button_width, button_height, GRAY,
                                  (100, 100, 100), BLACK)
        buttons = [human_btn, ai_btn, back_btn]
        while running:
            mouse_pos = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if human_btn.is_clicked(event):
                    print("Jogador 1: humano")
                    self.play_human_vs_ai(difficulty, human_first=True)
                elif ai_btn.is_clicked(event):
                    print("Jogador 1: ai")
                    self.play_human_vs_ai(difficulty, human_first=False)
                elif back_btn.is_clicked(event):
                    running = False
                    self.show_human_vs_ai_screen()

            self.screen.blit(pygame.transform.scale(FUNDO, (700, 700)), (0, 0))
            title = self.font_large.render("Escolha o", True, BLACK)
            title_rect = title.get_rect(center=(WIDTH // 2, 160))
            title2 = self.font_large.render("primeiro jogador", True, BLACK)
            title2_rect = title2.get_rect(center=(WIDTH // 2, 205))
            self.screen.blit(title, title_rect)
            self.screen.blit(title2, title2_rect)
            for btn in buttons:
                btn.draw(self.screen, mouse_pos)
            pygame.display.update()
            self.clock.tick(60)

    def show_second_ai_choice(self, difficulty1):
        running = True
        button_width = 300
        button_height = 50
        button_x = WIDTH // 2 - button_width // 2
        self.screen.blit(pygame.transform.scale(FUNDO, (700, 700)), (0, 0))
        mcts_easy_2_btn = AnimatedButton("MCTS fácil", self.font_medium, button_x, 225, button_width, button_height,
                                         RED, (200, 0, 0), BLACK)
        mcts_medium_2_btn = AnimatedButton("MCTS médio", self.font_medium, button_x, 300, button_width, button_height,
                                           YELLOW, (220, 180, 0), BLACK)
        mcts_hard_2_btn = AnimatedButton("MCTS difícil", self.font_medium, button_x, 375, button_width, button_height,
                                         ORANGE, (224, 122, 63), BLACK)
        decision_tree_2_btn = AnimatedButton("Decision Tree", self.font_medium, button_x, 450, button_width,
                                             button_height, ORANGE2, (255, 159, 107), BLACK)
        back_btn = AnimatedButton("Voltar", self.font_medium, button_x, 525, button_width, button_height, GRAY,
                                  (100, 100, 100), BLACK)
        buttons = [mcts_easy_2_btn, mcts_medium_2_btn, mcts_hard_2_btn, decision_tree_2_btn, back_btn]
        while running:
            mouse_pos = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if mcts_easy_2_btn.is_clicked(event):
                    print("AI2 Escolhida: MCTS fácil")
                    self.play_ai_vs_ai(difficulty1, difficulty2="easy")
                elif mcts_medium_2_btn.is_clicked(event):
                    print("AI2 Escolhida: MCTS médio")
                    self.play_ai_vs_ai(difficulty1, difficulty2="medium")
                elif mcts_hard_2_btn.is_clicked(event):
                    print("AI2 Escolhida: MCTS difícil")
                    self.play_ai_vs_ai(difficulty1, difficulty2="hard")
                elif decision_tree_2_btn.is_clicked(event):
                    print("AI2 Escolhida: DT")
                    self.play_ai_vs_ai(difficulty1, difficulty2="DT")
                elif back_btn.is_clicked(event):
                    running = False
                    self.show_ai_vs_ai_screen()
            self.screen.blit(pygame.transform.scale(FUNDO, (700, 700)), (0, 0))
            title = self.font_large.render("Escolha a IA2", True, BLACK)
            title_rect = title.get_rect(center=(WIDTH // 2, 160))
            self.screen.blit(title, title_rect)
            for btn in buttons:
                btn.draw(self.screen, mouse_pos)
            pygame.display.update()
            self.clock.tick(60)

    def play_human_vs_ai(self, difficulty, human_first=True):
        """Inicia jogo Humano vs AI"""
        self.game.board.reset()
        human_player = PLAYER1 if human_first else PLAYER2
        if difficulty == "DT":
            self.play_with_dt(human_player=human_player)
        else:
            self.play_with_ai(human_player=human_player, difficulty=difficulty)
        self.show_main_menu()

    def play_with_ai(self, human_player, difficulty):
        """Implementação do modo humano vs Monte Carlo Tree Search"""
        self.game.board.reset()
        self.game.draw_board()
        if difficulty == "easy":
            c_param = 1
        elif difficulty == "medium":
            c_param = 1
        else:
            c_param = math.sqrt(2)
        ai = MonteCarlo_Player(difficulty,c_param)  # IA com dificuldade escolhida

        # Define a mensagem que explica o modo
        message = self.font_small.render("Modo Humano vs Monte Carlo Tree Search", True, WHITE)
        message_rect = message.get_rect(center=(WIDTH // 2, SQUARESIZE // 2))
        self.screen.blit(message, message_rect)
        pygame.display.update()

        play_again = True

        while play_again:
            running = True
            while running and not self.game.board.is_game_over():
                # Se for a vez da IA, joga automaticamente
                if self.game.board.get_current_player() != human_player:
                    thinking_msg = self.font_small.render("IA está a pensar...", True, WHITE)
                    thinking_rect = thinking_msg.get_rect(center=(WIDTH // 2, SQUARESIZE // 2))
                    pygame.draw.rect(self.screen, BLACK, (0, 0, WIDTH, SQUARESIZE))
                    self.screen.blit(thinking_msg, thinking_rect)
                    pygame.display.update()
                    ai_col = ai.make_move(self.game.board)
                    if ai_col >= 0:
                        self.game.board.drop_piece(ai_col)
                        self.game.draw_board()
                    continue  # Volta ao início do loop
                #  Caso contrário, espera por eventos (jogador humano)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()

                    # Mostra a peça que segue o movimento do rato se for a vez do humano
                    if event.type == pygame.MOUSEMOTION and not self.game.board.is_game_over():
                        if self.game.board.get_current_player() == human_player:
                            posx = event.pos[0]
                            self.game.draw_moving_piece(posx)

                    # Processa o clique para colocar uma peça (apenas para o jogador humano)
                    if event.type == pygame.MOUSEBUTTONDOWN and not self.game.board.is_game_over():
                        if self.game.board.get_current_player() == human_player:
                            posx = event.pos[0]
                            col = int(posx // SQUARESIZE)

                            # Tenta colocar a peça
                            move_successful = self.game.board.drop_piece(col)

                            if move_successful:
                                self.game.draw_board()

                                # Verifica se o jogo acabou após a jogada humana
                                if self.game.board.is_game_over():
                                    continue

                                # Mostra que a IA está a pensar
                                thinking_msg = self.font_small.render("IA está a pensar...", True, WHITE)
                                thinking_rect = thinking_msg.get_rect(center=(WIDTH // 2, SQUARESIZE // 2))
                                pygame.draw.rect(self.screen, BLACK, (0, 0, WIDTH, SQUARESIZE))
                                self.screen.blit(thinking_msg, thinking_rect)
                                pygame.display.update()

                                # IA faz sua jogada
                                ai_col = ai.make_move(self.game.board)
                                if ai_col >= 0:  # Jogada válida
                                    self.game.board.drop_piece(ai_col)
                                    self.game.draw_board()

                    # Voltar ao menu com a tecla Esc
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            return

                self.clock.tick(60)

            # Jogo acabou, mostra resultado
            if self.game.board.is_game_over():

                # Mostra menu de fim de jogo
                play_again = self.game.show_end_game_menu()
                if play_again:
                    self.game.board.reset()
                    self.game.draw_board()
                    pygame.display.update()


    def board_to_features(self, board):
        """Humano vs Decision Tree"""
        return [cell for row in board.board for cell in row]

    def play_human_vs_dt(self, human_first=True):
        """Inicia jogo Humano vs Decision Tree"""
        self.game.board.reset()
        human_player = PLAYER1 if human_first else PLAYER2
        self.play_with_dt(human_player)
        self.show_main_menu()

    def play_with_dt(self, human_player):
        """Implementação do modo humano vs Decision Tree"""
        self.game.board.reset()
        self.game.draw_board()

        ai = DecisionTree_Player(random=False)  # IA com dificuldade escolhida

        # Define mensagem a explicar o modo
        message = self.font_small.render("Modo Humano vs Decision Tree", True, WHITE)
        message_rect = message.get_rect(center=(WIDTH // 2, SQUARESIZE // 2))
        self.screen.blit(message, message_rect)
        pygame.display.update()

        play_again = True

        while play_again:
            running = True
            while running and not self.game.board.is_game_over():
                # Se for a vez da IA, joga automaticamente
                if self.game.board.get_current_player() != human_player:
                    thinking_msg = self.font_small.render("IA está a pensar...", True, WHITE)
                    thinking_rect = thinking_msg.get_rect(center=(WIDTH // 2, SQUARESIZE // 2))
                    pygame.draw.rect(self.screen, BLACK, (0, 0, WIDTH, SQUARESIZE))
                    self.screen.blit(thinking_msg, thinking_rect)
                    pygame.display.update()
                    moves = self.game.board.get_legal_moves()
                    state = self.board_to_features(self.game.board)
                    ai_col = ai.play(state, moves)
                    if ai_col >= 0 and self.game.board.is_valid_move(ai_col):
                        self.game.board.drop_piece(ai_col)
                        self.game.draw_board()
                    else:
                        self.game.board.drop_piece(random.choice(moves))
                        self.game.draw_board()
                    continue  # Volta ao início do loop
                #  Caso contrário, espera por eventos (jogador humano)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()

                    # Mostra a peça que segue o movimento do rato se for a vez do humano
                    if event.type == pygame.MOUSEMOTION and not self.game.board.is_game_over():
                        if self.game.board.get_current_player() == human_player:
                            posx = event.pos[0]
                            self.game.draw_moving_piece(posx)

                    # Processa o clique para colocar uma peça (apenas para o jogador humano)
                    if event.type == pygame.MOUSEBUTTONDOWN and not self.game.board.is_game_over():
                        if self.game.board.get_current_player() == human_player:
                            posx = event.pos[0]
                            col = int(posx // SQUARESIZE)

                            # Tenta colocar a peça
                            move_successful = self.game.board.drop_piece(col)

                            if move_successful:
                                self.game.draw_board()

                                # Verifica se o jogo acabou após a jogada humana
                                if self.game.board.is_game_over():
                                    continue

                                # Mostra que a IA está a pensar
                                thinking_msg = self.font_small.render("IA está a pensar...", True, WHITE)
                                thinking_rect = thinking_msg.get_rect(center=(WIDTH // 2, SQUARESIZE // 2))
                                pygame.draw.rect(self.screen, BLACK, (0, 0, WIDTH, SQUARESIZE))
                                self.screen.blit(thinking_msg, thinking_rect)
                                pygame.display.update()

                                # IA faz sua jogada
                                state = self.board_to_features(self.game.board)
                                moves = self.game.board.get_legal_moves()

                                ai_col = ai.play(state, moves)
                                if ai_col >= 0:  # Jogada válida
                                    self.game.board.drop_piece(ai_col)
                                    self.game.draw_board()
                                    continue

                    # Volta ao menu com a tecla Esc
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            return

                self.clock.tick(60)

            # Jogo acabou, mostra resultado
            if self.game.board.is_game_over():

                # Mostra menu de fim de jogo
                play_again = self.game.show_end_game_menu()
                if play_again:
                    self.game.board.reset()
                    self.game.draw_board()
                    pygame.display.update()

    #    -------------------
    #    AI VS. AI
    #    -------------------

    def play_ai_vs_ai(self, difficulty1, difficulty2):
        """Inicia jogo AI vs AI"""
        self.game.board.reset()
        self.play_ai_simulation(difficulty1, difficulty2)
        self.show_main_menu()

    def play_ai_simulation(self, difficulty1, difficulty2):
        """Implementação do modo AI vs AI"""
        self.game.board.reset()
        self.screen.blit(self.fundo, (0, 0))
        self.game.draw_board()
        if difficulty1 == "DT":
            ai1 = DecisionTree_Player(random=False)
        else:
            if difficulty1 == "easy":
                c_param = 1
            elif difficulty1 == "medium":
                c_param = 1
            else:
                c_param = math.sqrt(2)
            ai1 = MonteCarlo_Player(difficulty=difficulty1,c_param=c_param)
        if difficulty2 == "DT":
            ai2 = DecisionTree_Player(random=False)
        else:
            if difficulty2 == "easy":
                c_param = 1
            elif difficulty2 == "medium":
                c_param = 1
            else:
                c_param = math.sqrt(2)
            ai2 = MonteCarlo_Player(difficulty=difficulty2, c_param=c_param)

        # Define mensagem a explicar o modo
        message = self.font_small.render("AI1 vs AI2", True, WHITE)
        message_rect = message.get_rect(center=(WIDTH // 2, SQUARESIZE // 2))
        self.screen.blit(message, message_rect)
        pygame.display.update()

        play_again = True

        while play_again:
            running = True

            while running and not self.game.board.is_game_over():
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()

                    # Volta ao menu com a tecla Esc
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            return

                # Determina o jogador atual
                current_player = self.game.board.get_current_player()
                current_ai = ai1 if current_player == PLAYER1 else ai2

                # Mostra que a IA está a pensar
                ai_name = "IA 1 (VERMELHO)" if current_player == PLAYER1 else "IA 2 (AMARELO)"
                thinking_msg = self.font_small.render(f"{ai_name} está a pensar...", True, WHITE)
                thinking_rect = thinking_msg.get_rect(center=(WIDTH // 2, SQUARESIZE // 2))
                pygame.draw.rect(self.screen, BLACK, (0, 0, WIDTH, SQUARESIZE))
                self.screen.blit(thinking_msg, thinking_rect)
                pygame.display.update()

                # IA faz sua jogada
                if isinstance(current_ai, MonteCarlo_Player):
                    col = current_ai.make_move(self.game.board)
                else:
                    moves = self.game.board.get_legal_moves()
                    state = self.board_to_features(self.game.board)
                    col = current_ai.play(state, moves)
                if col >= 0:  # Jogada válida
                    # Adicionamos um pequeno delay para visualizar as jogadas
                    pygame.time.wait(800)
                    self.game.board.drop_piece(col)
                    self.game.draw_board()

                self.clock.tick(30)  # Framerate mais baixo para este modo

            # Jogo acabou, mostrar resultado
            if self.game.board.is_game_over():

                # Mostra menu de fim de jogo
                play_again = self.game.show_end_game_menu()
                if play_again:
                    self.game.board.reset()
                    self.game.draw_board()
                    pygame.display.update()



if __name__ == "__main__":
    menu = Menu()
    menu.show_main_menu()