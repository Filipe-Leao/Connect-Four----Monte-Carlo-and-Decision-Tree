#montecarlo.py

import time
import numpy as np
from collections import defaultdict
from board import Board
import random
from variables import *


class MonteCarloNode:
    
    __slots__ = ['state', 'player', 'parent', 'parent_action', 'children', 'visits', 'results', 'untried_actions']
    
    def __init__(self, state, player, parent=None, parent_action=None):
        self.state = state                 
        self.player = player               
        self.parent = parent
        self.parent_action = parent_action        # ação que levou ao estado atual
        self.children = []
        self.visits = 0
        self.results = [0, 0, 0]  # ao aceder a uma chave que não existe, inicia-a com 0
        self.untried_actions = self.get_legal_actions()

    def get_legal_actions(self): 
        '''Retorna todas as jogadas válidas no estado atual'''
        return [col for col in range(COLS) if self.state.is_valid_move(col)]

    def expand(self): 
        '''Expande o nó atual, adicionando um filho'''
        action = self.untried_actions.pop()   # Remove a jogada ainda não expandida da lista das jogadas possíveis
        next_state = self.move(action)        # Aplica a jogada ao estado atual
        next_player = PLAYER2 if self.player == PLAYER1 else PLAYER1
        child_node = MonteCarloNode(next_state, next_player, parent=self, parent_action=action)   # Cria o nó filho
        self.children.append(child_node)      # Adiciona o nó filho à lista de filhos do nó atual
        return child_node

    def is_terminal_node(self): 
        '''Verifica se o jogo acabou no estado atual'''
        return self.state.is_game_over()

    def rollout(self): 
        '''Simula um jogo aleatório a partir do estado atual até um estado terminal'''
        current_rollout_state = self.state.clone()   # Cópia do estado atual do jogo, não modificando o original
        current_player = self.player

        while not current_rollout_state.is_game_over():
            valid_moves = [col for col in range(COLS) if current_rollout_state.is_valid_move(col)]    # Verifica as jogadas válidas no estado simulado
            if not valid_moves:
                break

            action = random.choice(valid_moves)   # Escolha aleatória de uma jogada válida

            current_rollout_state.player = current_player  # Atualiza o jogador no estado simulado
            current_rollout_state.drop_piece(action)       # Aplica a jogada ao estado simulado

            current_player = PLAYER1 if current_player == PLAYER2 else PLAYER2   # Alterna o jogador

        return self.game_result(current_rollout_state)   

    def backpropagate(self, result): 
        '''Propaga os resultados para cima na árvore'''
        self.visits += 1              # Cada vez que o nó é alcançado numa simulação
        self.results[result] += 1     # Atualiza o nr de vitórias, de derrotas e de empates para o nó atual
        if self.parent:
            self.parent.backpropagate(result)    # Propaga o resultado para o nó pai

    def is_fully_expanded(self): 
        '''Verifica se todos os movimentos possíveis foram explorados'''
        return len(self.untried_actions) == 0

    def best_child(self, c_param=np.sqrt(2)): 
        '''Seleciona o melhor filho usando a fórmula UCB1 = exploitation + exploration'''
        if not self.children:    # Nenhuma jogada foi expandida
            return None
            
        # Cálculo do UCB para cada filho
        ucb_values = []
        for child in self.children:
            # Evitar divisão por zero
            if child.visits == 0:
                ucb_values.append(float('inf'))    # Se um filho nunca foi visitado, damos-lhe valor infinito para que seja logo escolhido
            else:
                exploitation = child.results[self.player] / child.visits              # Taxa de vitórias do nó filho
                exploration = c_param * np.sqrt(np.log(self.visits) / child.visits)   # Quanto mais visitas tem o pai e menos visitas tem o filho, maior o incentivo para explorar
                ucb_values.append(exploitation + exploration)
        
        return self.children[np.argmax(ucb_values)]   # Expande o filho com o maior valor UCB

    def _tree_policy(self):  
        ''' Percorre a árvore e vai retornando os melhores filhos até chegar a um nó terminal ou um nó não expandido'''
        current_node = self
        while not current_node.is_terminal_node():    
            if not current_node.is_fully_expanded():    # Se ainda houver jogadas não exploradas
                return current_node.expand()            # Expande o nó atual
            else:
                next_node = current_node.best_child()   # Já está totalmente expandido, então escolhe o melhor filho
                if next_node is None:                   
                    return current_node                 # Se não houver filhos, retorna o nó atual
                current_node = next_node                # Avança na árvore para o nó filho escolhido
        return current_node

    def best_action(self, simulations=1000): 
        '''Executa várias simulações e escolhe a jogada que foi mais visitada'''
        for _ in range(simulations):
            v = self._tree_policy()   # Seleciona um nó promissor
            reward = v.rollout()      # Faz uma simulação a partir desse nó
            v.backpropagate(reward)   # Propaga o resultado da simulação até à raiz

        # Retorna o filho com mais visitas
        if not self.children:
            return random.choice(self.get_legal_actions())  # Se não tiver filhos, retorna uma jogada aleatória válida
        
        visits = [child.visits for child in self.children]  # Escolhe o filho com mais visitas
        return self.children[np.argmax(visits)].parent_action, self.children[np.argmax(visits)].results[self.player] / self.children[np.argmax(visits)].visits if self.children[np.argmax(visits)].visits > 0 else 0      # Devolve a ação que levou a esse filho
    
    def best_action_by_winrate(self, simulations=1000):    # PARA TESTAR
        '''Executa várias simulações e escolhe a jogada com a maior taxa de vitórias'''
        for _ in range(simulations):
            v = self._tree_policy()
            reward = v.rollout()
            v.backpropagate(reward)

        if not self.children:
            return random.choice(self.get_legal_actions())

        win_rates = [
            child.results[self.player] / child.visits if child.visits > 0 else 0
            for child in self.children
        ]
        return self.children[np.argmax(win_rates)].parent_action, np.argmax(win_rates)

    def move(self, action):  
        '''Aplica uma ação ao estado atual e retorna o novo estado'''
        new_state = self.state.clone() 
        new_state.player = self.player     # Define o jogador atual que vai fazer a jogada
        new_state.drop_piece(action)
        return new_state       # Retorna o novo estado após a jogada
     
    def game_result(self, board):
        '''Recompensa para o resultado de uma simulação'''
        if board.winner is not None:
            return board.winner  # 1 se ganhou o PLAYER1, 2 se ganhou o PLAYER2
        elif board.is_game_over():
            return 0  # Empate
        return None
    
        

class MonteCarlo_Player: 
    def __init__(self, difficulty='medium', c_param=np.sqrt(2)):
        self.difficulty = difficulty
        if difficulty == 'easy':
            self.simulations = 500   
        elif difficulty == 'medium':
            self.simulations = 2000  
        elif difficulty == 'hard':
            self.simulations = 10000
        self.c_param = c_param

    def make_move(self, board): 
        '''Representa um jogador que usa MCTS para fazer a sua jogada'''
        root = MonteCarloNode(board.clone(), board.get_current_player())    # Cria o nó raiz da árvore
        legal_actions = root.get_legal_actions()
        if not legal_actions:
            return -1            # Sem jogadas possíveis
        if len(legal_actions) == 1:
            return legal_actions[0]    # Se houver apenas uma jogada possível, retorna essa jogada
        
        start_time = time.time()
        action, win_rate = root.best_action(self.simulations)     # Executa o MCTS para encontrar a melhor jogada
        end_time = time.time()
        print(f"[{self.difficulty}] Jogada escolhida: {action} em {end_time - start_time:.4f} segundos")
        return action


class MonteCarlo_Player_WinRate:    # PARA TESTAR
    def __init__(self, difficulty='medium', c_param=np.sqrt(2)):
        self.difficulty = difficulty
        if difficulty == 'easy':
            self.simulations = 500
        elif difficulty == 'medium':
            self.simulations = 2000
        elif difficulty == 'hard':
            self.simulations = 10000

    def make_move(self, board): 
        root = MonteCarloNode(board.clone(), board.get_current_player())
        legal_actions = root.get_legal_actions()
        if not legal_actions:
            return -1, 0.0
        if len(legal_actions) == 1:
            return legal_actions[0], 0.0
        
        start_time = time.time()
        action, win_rate = root.best_action_by_winrate(self.simulations)
        end_time = time.time()
        print(f"[{self.difficulty} - WINRATE] Jogada escolhida: {action} em {end_time - start_time:.4f} segundos")
        return action