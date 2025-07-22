# generate_dataset_mc.py

import csv
import os
import random
import time
import numpy as np
from collections import defaultdict
import copy
import multiprocessing
import math
from montecarlo import MonteCarlo_Player, MonteCarloNode
from board import Board
from variables import *

def get_valid_moves(board):
    return [c for c in range(COLS) if board.is_valid_move(c)]

def flatten_board(board):
    flat = []
    grid = board.get_board()
    for r in range(ROWS):
        for c in range(COLS):
            flat.append(grid[r][c])
    return flat

def jogador_aleatorio(board):
    valid_moves = get_valid_moves(board)
    return random.choice(valid_moves) if valid_moves else -1

def simular_jogo_e_coletar_dados(args):
    """
    Simula UM jogo completo e retorna uma lista de linhas de dados (estado, melhor_jogada).
    Recebe as *configurações* (strings de dificuldade) e instancia os jogadores aqui.
    """
    modo_jogo, p1_setting, p2_setting, game_id = args

    board = Board()
    dados_jogo = []  # Armazena as linhas (estado, jogada) deste jogo

    # Força o primeiro movimento de jogador 1 numa coluna cíclica
    coluna_inicial_forcada = game_id % COLS
    if board.is_valid_move(coluna_inicial_forcada):
        board.drop_piece(coluna_inicial_forcada)
        board.player = PLAYER2
    jogador1 = None
    jogador2 = None

    try:
        if modo_jogo == 'mcts_vs_random':
            jogador1 = MonteCarlo_Player(difficulty=p1_setting)  # Cria instância aqui
            jogador2 = jogador_aleatorio
        elif modo_jogo == 'mcts_vs_mcts':
            jogador1 = MonteCarlo_Player(difficulty=p1_setting)  
            jogador2 = MonteCarlo_Player(difficulty=p2_setting)  
        elif modo_jogo == 'random_vs_mcts':
            jogador1 = jogador_aleatorio
            jogador2 = MonteCarlo_Player(difficulty=p2_setting)  
        else:
            raise ValueError(f"Modo de jogo inválido: {modo_jogo}")
    except Exception as e:
        print(f"[Game {game_id}] erro ao criar jogadores com settings P1='{p1_setting}', P2='{p2_setting}': {e}")
        print("Verifique se as strings de dificuldade são válidas em MonteCarlo_Player.__init__")
        return []  # Retorna lista vazia se não puder criar jogadores

    # Loop do Jogo 
    while not board.is_game_over():
        current_player_id = board.get_current_player()
        current_player_obj = jogador1 if current_player_id == PLAYER1 else jogador2
        move = -1

        valid_moves = get_valid_moves(board)
        if not valid_moves: break

        is_mcts_player = isinstance(current_player_obj, MonteCarlo_Player)

        if is_mcts_player:
            # Lógica para Jogador MCTS 
            # 1. Obter a melhor jogada usando o método do jogador
            # Passamos um clone para garantir que make_move não altere o estado principal do tabuleiro desta função, caso ele o modifique internamente.
            try:
                # Chama o método que já faz a busca MCTS e retorna a coluna
                best_move_col = current_player_obj.make_move(board.clone())

                if best_move_col in valid_moves:
                    # 2. Achatar o estado ANTES da jogada
                    flat_board = flatten_board(board)
                    # 3. Adicionar à lista de dados
                    dados_jogo.append(flat_board + [best_move_col])
                    # 4. Definir a jogada a ser feita
                    move = best_move_col
                elif valid_moves:
                    move = random.choice(valid_moves)
                else:
                    break  # Sem jogadas válidas e make_move falhou

            except Exception as e:
                print(
                    f"[Game {game_id}] ERRO durante MCTS make_move (J{current_player_id}, diff='{current_player_obj.difficulty}'): {e}")
                if valid_moves:
                    move = random.choice(valid_moves)  # Tenta jogada aleatória se o MCTS falhou
                else:
                    break  # Sem jogadas, termina

        else:
            # Lógica para Jogador Aleatório
            move = current_player_obj(board)

        # Aplicar a Jogada
        if move in valid_moves:
            board.drop_piece(move)
        elif move != -1:
            break
        else:
            break  # Nenhuma jogada definida

    return dados_jogo


def main():
    NUM_GAMES_ESTA_EXECUCAO = 1000  # Jogos a gerar nesta execução

    # Define os matchups usando apenas as strings de dificuldade que MonteCarlo_Player entende
    DESIRED_MATCHUPS = [
        ('easy', 'easy'),
        ('easy', 'medium'),
        ('medium', 'medium'),
        ('medium', 'hard'),
        ('hard', 'hard'),
        ('hard', 'hard'),
        ('hard', 'hard'),
        ('hard', 'hard'),
        ('hard', 'hard'),
        ('hard', 'hard')
    ]
    MODE = 'mcts_vs_mcts'  # Deve ser consistente com os matchups

    FILENAME = 'dataset_quatro_em_linha_mcts.csv'  # Nome do dataset cumulativo
    NUM_PROCESSOS = 6

    if not DESIRED_MATCHUPS:
        print("ERRO: A lista DESIRED_MATCHUPS está vazia.")
        return
    if NUM_PROCESSOS < 1:
        print("ERRO: NUM_PROCESSOS deve ser pelo menos 1.")
        return

    print(f"Preparando {NUM_GAMES_ESTA_EXECUCAO} jogos para adicionar a '{FILENAME}'...")
    print(f"Modo: {MODE}")
    print(f"Matchups a incluir: {DESIRED_MATCHUPS}")

    start_time_prep = time.time()

    # Prepara lista de argumentos para as tarefas (passando strings de dificuldade)
    tasks_args = []
    num_matchups = len(DESIRED_MATCHUPS)
    games_per_matchup = NUM_GAMES_ESTA_EXECUCAO // num_matchups
    extra_games = NUM_GAMES_ESTA_EXECUCAO % num_matchups
    game_id_counter = 0

    for i, matchup_settings in enumerate(DESIRED_MATCHUPS):
        num_jogos_neste_matchup = games_per_matchup + (1 if i < extra_games else 0)
        if num_jogos_neste_matchup == 0: continue

        # Extrai as settings (strings de dificuldade) para P1 e P2
        p1_setting, p2_setting = None, None
        if MODE == 'mcts_vs_mcts':
            p1_setting, p2_setting = matchup_settings  # Espera tuple ('diff1', 'diff2')
        elif MODE == 'mcts_vs_random':
            p1_setting = matchup_settings[0]  # Espera ('diff1',) ou apenas 'diff1'
            p2_setting = None  # Random não tem setting
        elif MODE == 'random_vs_mcts':
            p1_setting = None  # Random não tem setting
            p2_setting = matchup_settings[0]  # Espera ('diff2',) ou apenas 'diff2'

        # Validação básica das settings (não nulas quando esperado)
        if (MODE != 'random_vs_mcts' and p1_setting is None) or \
                (MODE != 'mcts_vs_random' and p2_setting is None and MODE != 'mcts_vs_mcts'):
            continue

        for _ in range(num_jogos_neste_matchup):
            game_id_counter += 1
            # Passa as strings de dificuldade (ou None) para o worker
            tasks_args.append((MODE, p1_setting, p2_setting, game_id_counter))

    if not tasks_args:
        print("Nenhuma tarefa de simulação foi criada.")
        return

    # Executa o Pool
    print("A iniciar Pool...")
    start_time_pool = time.time()
    results_list_of_lists = []
    try:
        with multiprocessing.Pool(processes=NUM_PROCESSOS) as pool:
            results_list_of_lists = pool.map(simular_jogo_e_coletar_dados, tasks_args)
    except Exception as e:
        print(f"\nERRO durante execução do Pool: {e}")

    pool_time = time.time() - start_time_pool

    # Coleta e escreve resultados
    all_rows_data = [row for game_data in results_list_of_lists if game_data for row in game_data]
    total_states_recorded = len(all_rows_data)

    if not all_rows_data:
        print("Nenhum dado gerado nesta execução.")
    else:
        print(f"Adicionados {total_states_recorded} novos estados.")
        file_exists = os.path.isfile(FILENAME)
        is_empty = not file_exists or os.path.getsize(FILENAME) == 0

        try:
            with open(FILENAME, 'a', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                if is_empty:
                    header = [f'cell_{r}_{c}' for r in range(ROWS) for c in range(COLS)] + ['best_move_col']
                    writer.writerow(header)
                writer.writerows(all_rows_data)
        except IOError as e:
            print(f"ERRO ao escrever/anexar em {FILENAME}: {e}")
        except Exception as e:
            print(f"ERRO durante a escrita no CSV: {e}")

    end_time_total = time.time()
    print("-" * 30)
    print(f'Execução concluída.')
    print(f'Novos estados guardados: {total_states_recorded}')
    print(f'Tempo total desta execução: {end_time_total - start_time_prep:.2f}s.')
    print(f"Dataset em '{FILENAME}'.")
    print("-" * 30)


if __name__ == '__main__':
    # Pequena verificação se MonteCarlo_Player pode ser instanciado com dificuldade
    try:
        _ = MonteCarlo_Player(difficulty='easy')
    except TypeError:
        print("=" * 30)
        print("ERRO: Parece que MonteCarlo_Player.__init__ não aceita o argumento 'difficulty'.")
        print("Verifique a definição da classe em montecarlo.py.")
        print("=" * 30)
        exit()
    except Exception as e:
        print(f"Aviso: Erro ao testar instanciação de MonteCarlo_Player: {e}")

    main()