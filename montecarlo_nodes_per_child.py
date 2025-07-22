# montecarlo_nodes_per_child.py

import time
import numpy as np
from collections import defaultdict
from board import Board
import random
import copy
from variables import *


class MonteCarloNode:

    __slots__ = ['state', 'player', 'parent', 'parent_action', 'children', 'visits', 'results', 'c_param', 'max_children_to_explore', 'untried_actions']
    def __init__(self, state, player, parent=None, parent_action=None, c_param=np.sqrt(2), max_children_to_explore=None):
        self.state = state
        self.player = player
        self.parent = parent
        self.parent_action = parent_action
        self.children = []
        self.visits = 0
        self.results = [0, 0, 0]
        self.c_param = c_param
        self.max_children_to_explore = max_children_to_explore
        self.untried_actions = self._get_limited_legal_actions()

    def _get_limited_legal_actions(self):
        '''Retorna uma lista potencialmente limitada de jogadas válidas no estado atual'''
        legal_actions = [col for col in range(COLS) if self.state.is_valid_move(col)]
        if self.max_children_to_explore is not None and len(legal_actions) > self.max_children_to_explore:
            # Se há mais jogadas legais do que o limite, escolhe um subconjunto aleatório.
            # Poderia também ser as primeiras N, mas aleatórias podem promover mais diversidade.
            return random.sample(legal_actions, self.max_children_to_explore)
        return legal_actions

    def get_legal_actions(self): # Mantido por consistência, mas não usado diretamente para untried_actions
        '''Retorna todas as jogadas válidas no estado atual'''
        return [col for col in range(COLS) if self.state.is_valid_move(col)]

    def expand(self):
        '''Expande o nó atual, adicionando um filho'''
        action = self.untried_actions.pop()
        next_state = self.move(action)
        next_player = PLAYER2 if self.player == PLAYER1 else PLAYER1
        # Propaga c_param e max_children_to_explore para os filhos
        child_node = MonteCarloNode(next_state, next_player, parent=self, parent_action=action,
                                   c_param=self.c_param, max_children_to_explore=self.max_children_to_explore)
        self.children.append(child_node)
        return child_node

    def is_terminal_node(self):
        '''Verifica se o jogo acabou no estado atual'''
        return self.state.is_game_over()

    def rollout(self):
        '''Simula um jogo aleatório a partir do estado atual até um estado terminal'''
        current_rollout_state = copy.deepcopy(self.state)
        current_player_rollout = self.player # Jogador que FAZ a primeira jogada do rollout a partir deste nó

        while not current_rollout_state.is_game_over():
            valid_moves = [col for col in range(COLS) if current_rollout_state.is_valid_move(col)]
            if not valid_moves:
                break
            action = random.choice(valid_moves)
            current_rollout_state.player = current_player_rollout # Define quem joga na cópia
            current_rollout_state.drop_piece(action) # drop_piece alterna o jogador na cópia
            current_player_rollout = current_rollout_state.player # Pega o jogador que fará a PROXIMA jogada no rollout

        # game_result avalia do ponto de vista do self.player (jogador do nó que iniciou o rollout)
        return self.game_result_for_mcts(current_rollout_state)

    def backpropagate(self, result): 
        '''Propaga os resultados para cima na árvore'''
        self.visits += 1              # Cada vez que o nó é alcançado numa simulação
        self.results[result] += 1     # Atualiza o nr de vitórias, de derrotas e de empates para o nó atual
        if self.parent:
            self.parent.backpropagate(result)    # Propaga o resultado para o nó pai

    def is_fully_expanded(self):
        '''Verifica se todos os movimentos (limitados) possíveis foram explorados'''
        return len(self.untried_actions) == 0

    def best_child(self): # Removido c_param daqui, usa self.c_param
        '''Seleciona o melhor filho usando a fórmula UCB1 = exploitation + exploration'''
        if not self.children:
            return None

        ucb_values = []
        for child in self.children:
            if child.visits == 0:
                ucb_values.append(float('inf'))
            else:
                exploitation = child.results[self.player] / child.visits
                exploration = self.c_param * np.sqrt(np.log(self.visits) / child.visits)
                ucb_values.append(exploitation + exploration)

        return self.children[np.argmax(ucb_values)]

    def _tree_policy(self):
        ''' Percorre a árvore e vai retornando os melhores filhos até chegar a um nó terminal ou um nó não expandido'''
        current_node = self
        while not current_node.is_terminal_node():
            if not current_node.is_fully_expanded():
                return current_node.expand()
            else:
                next_node = current_node.best_child() # Usa self.c_param internamente
                if next_node is None: # Pode acontecer se current_node é terminal mas não tem filhos (empate?)
                    return current_node # Ou se best_child retornou None por não haver filhos
                current_node = next_node
        return current_node

    def best_action(self, simulations=1000):
        '''Executa várias simulações e escolhe a jogada que foi mais visitada'''
        for _ in range(simulations):
            v = self._tree_policy()
            reward_idx = v.rollout() # rollout agora chama game_result_for_mcts
            v.backpropagate(reward_idx)

        if not self.children:
            legal_actions = self.get_legal_actions() # Usa get_legal_actions original para fallback
            return random.choice(legal_actions) if legal_actions else -1

        visits = [child.visits for child in self.children]
        return self.children[np.argmax(visits)].parent_action

    def move(self, action):
        '''Aplica uma ação ao estado atual e retorna o novo estado'''
        new_state = self.state.clone()
        new_state.player = self.player # Jogador do nó atual faz a jogada
        new_state.drop_piece(action) # drop_piece alterna o jogador em new_state
        return new_state

    def game_result_for_mcts(self, board):
        '''Recompensa para o resultado de uma simulação'''
        if board.winner is not None:
            return board.winner  # 1 se ganhou o PLAYER1, 2 se ganhou o PLAYER2
        elif board.is_game_over():
            return 0  # Empate
        return None
    
class MonteCarlo_Player:
    def __init__(self, difficulty='medium', c_param=np.sqrt(2), max_children_to_explore=None):
        self.difficulty = difficulty
        if difficulty == 'easy':
            self.simulations = 2000
        elif difficulty == 'medium':
            self.simulations = 5000
        elif difficulty == 'hard':
            self.simulations = 10000
        self.c_param = c_param
        self.max_children_to_explore = max_children_to_explore

    def make_move(self, board):
        '''Representa um jogador que usa MCTS para fazer a sua jogada'''
        # Passa c_param e max_children_to_explore para o nó raiz
        root = MonteCarloNode(board.clone(), board.get_current_player(), c_param=self.c_param, max_children_to_explore=self.max_children_to_explore)
        
        legal_actions = root.get_legal_actions() # Usa get_legal_actions original para estes checks
        if not legal_actions:
            return -1
        if len(legal_actions) == 1:
            return legal_actions[0]
        
        start_time = time.time()
        action = root.best_action(self.simulations)
        end_time = time.time()
        print(f"[{self.difficulty}] Jogada escolhida: {action} em {end_time - start_time:.4f} segundos")
        return action