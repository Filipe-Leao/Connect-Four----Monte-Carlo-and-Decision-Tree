# decisiontree.py

import numpy as np
from collections import Counter
import pickle
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
import random

class Node:
    __slots__ = ['feature', 'threshold', 'branches', 'value']
    def __init__(self, feature=None, threshold=None, branches=None, value=None):
        '''Estrutura de cada nó da árvore de decisão'''
        self.feature = feature           # Índice/Posição do atributo para o split
        self.threshold = threshold       # Limitador escolhido, utilizado apenas para atributos numéricos
        self.branches = branches or {}   # Dicionário com ramos da árvore. Para atributos categóricos, a chave é o valor do atributo
        self.value = value               # Classe se for folha

    def is_leaf_node(self):
        '''Verifica se o nó é folha'''
        return self.value is not None     # Se o nó é folha, retorna True


class DecisionTree:
    def __init__(self, random_state=None, min_samples_split=2, max_depth=100):
        '''Parâmetros da árvore de decisão'''
        self.root = None                                # Raiz da árvore
        self.random_state = random_state                # Para garantir aleatoriedade
        self.most_common_class = None                   # Classe mais comum para previsões
        self.min_samples_split = min_samples_split      # Número mínimo de amostras para dividir um nó
        self.max_depth = max_depth                      # Profundidade máxima da árvore

        if random_state is not None:
            np.random.seed(random_state)

    def fit(self, X, y):
        '''Constrói a árvore de decisão a partir dos dados'''
        X = np.array(X)    # Converte para numpy 
        y = np.array(y)

        n_feats = X.shape[1]                                    # Número de atributos é o número de colunas do dataset

        # Determina os tipos dos atributos
        self.feature_types = []
        for i in range(n_feats):
            if self.is_categorical(X[:, i]):
                self.feature_types.append("categorical")
            else:
                self.feature_types.append("numerical")
        self.root = self.grow_tree(X, y, n_feats=n_feats)       # Começa a construir a árvore
        self.most_common_class = self.most_common_label(y)      # Garante que a árvore tem sempre uma resposta possível

    def grow_tree(self, X, y, depth=0, n_feats=None, used_features_count=None):
        '''Cria a árvore de decisão recursivamente'''
        n_samples, n_features = X.shape
        n_labels = len(np.unique(y))

        if used_features_count is None:
            used_features_count = {}

        # Critérios de paragem
        if (depth >= self.max_depth or n_labels == 1 or n_samples < self.min_samples_split):
            return Node(value=self.most_common_label(y))

        if n_feats is None:
            n_feats = n_features

        # Só considerar atributos com uso < 2 neste caminho
        feat_idxs = [i for i in range(n_feats) if used_features_count.get(i, 0) < 2]

        # Se nenhum atributo está disponível, parar
        if not feat_idxs:
            return Node(value=self.most_common_label(y))

        # Encontrar melhor split
        best_feat, best_thresh, best_gain, best_split = self.best_split(X, y, feat_idxs)

        if best_gain == 0:
            return Node(value=self.most_common_label(y))

        # Atualizar contador de atributos usados neste caminho
        updated_used_counts = used_features_count.copy()
        updated_used_counts[best_feat] = updated_used_counts.get(best_feat, 0) + 1

        if self.feature_types[best_feat] == "categorical":
            branches = {}
            for val, idxs in best_split.items():
                child = self.grow_tree(X[idxs, :], y[idxs], depth + 1, n_feats, updated_used_counts)
                branches[val] = child
            return Node(feature=best_feat, threshold=None, branches=branches)

        else:  # numérico
            left_idxs, right_idxs = best_split
            left = self.grow_tree(X[left_idxs, :], y[left_idxs], depth + 1, n_feats, updated_used_counts)
            right = self.grow_tree(X[right_idxs, :], y[right_idxs], depth + 1, n_feats, updated_used_counts)
            branches = {'left': left, 'right': right}
            return Node(feature=best_feat, threshold=best_thresh, branches=branches)

    def best_split(self, X, y, feat_idxs):
        '''Cálculo dos ganhos de informação para escolher o melhor split'''
        best_gain = -1
        best_feat, best_split = None, None
        #print(f"A procurar o melhor split entre {len(feat_idxs)} atributos")
        for feat in feat_idxs:
            X_column = X[:, feat]

            if self.is_categorical(X_column):
                splits = self.split_categorical(X_column)
                gain = self.information_gain(y, list(splits.values()))
                #print(f"Atributo {feat} (categórico): ganho = {gain:.4f}")
                if gain > best_gain:
                    best_gain = gain
                    best_feat = feat
                    best_split = splits

            else:  # Numérico
                threshold, entropy_value = self.conditional_entropy_split(X_column, y)
                if threshold is not None:
                    gain = self.entropy(y) - entropy_value
                    #print(f"Atributo {feat} (numérico) com threshold {threshold:.3f}: ganho = {gain:.4f}")
                    if gain > best_gain:
                        best_gain = gain
                        best_feat = feat
                        best_split = threshold

        #print(f"Melhor split: atributo={best_feat}, ganho={best_gain:.4f}")
        if self.is_categorical(X[:, best_feat]):
            return best_feat, None, best_gain, best_split
        else:
            return best_feat, best_split, best_gain, self.split_numerical(X[:, best_feat], best_split)

    def is_categorical(self, column):
        '''Verifica se a coluna é categórica'''
        dtype = column.dtype
        if dtype == object or np.issubdtype(dtype, np.integer):    # Se o tipo for object ou qualquer tipo de inteiro é categórico
            return True
        else:
            return False

    def split_numerical(self, column, threshold):
        '''Divide os dados em dois subconjuntos com base no threshold'''
        left_idxs = np.argwhere(column <= threshold).flatten()    # indices dos exemplos à esquerda do threshold, numa lista 1D
        right_idxs = np.argwhere(column > threshold).flatten()    # indices dos exemplos à direita do threshold, numa lista 1D
        return left_idxs, right_idxs

    def split_categorical(self, column):
        '''Divide os dados em subconjuntos com base nos valores únicos'''
        values = np.unique(column)             # Valores únicos da coluna
        splits = {}                            # Dicionário para armazenar os índices dos exemplos para cada valor
        for val in values: 
            splits[val] = np.argwhere(column == val).flatten()    # indices dos exemplos com o valor atual, numa lista 1D
        return splits

    def information_gain(self, y, branches_indices):
        '''Calcula o ganho de informação para um conjunto de dados'''
        parent_entropy = self.entropy(y)      # Entropia do conjunto pai
        n = len(y)                            # Tamanho do conjunto pai
        weighted_child_entropy = 0            # Inicializa a entropia ponderada dos filhos
        for indices in branches_indices:
            if len(indices) == 0:
                continue
            branch_y = y[indices]             # Extrai as classes do ramo atual
            weight = len(indices) / n         # Calcula o peso do ramo
            weighted_child_entropy += weight * self.entropy(branch_y)    # Calcula a entropia ponderada deste ramo e adiciona à entropia total dos filhos
        
        gain = parent_entropy - weighted_child_entropy        # Ganho de informação = Entropia(pai) - Entropia média ponderada(filhos)
        return gain

    def entropy(self, y):
        '''Calcula a entropia H(X) conforme a fórmula dada em aula:
                H(X) = sum(-P(x_i) * log2(P(x_i)))'''
        if len(y) == 0:         # Se o array estiver vazio, a entropia é 0
            return 0
        values, counts = np.unique(y, return_counts=True)                  # Conta a frequência de cada classe
        probabilities = counts / len(y)                                    # Calcula as probabilidades P(x_i)
        entropy_value = -np.sum(probabilities * np.log2(probabilities))    # Calcula a entropia usando a fórmula
        return entropy_value

    def conditional_entropy_split(self, X_column, y):
        '''Encontra o melhor threshold para dividir X_column minimizando H(Class|Split)'''
        sorted_indices = np.argsort(X_column)
        X_sorted = X_column[sorted_indices]
        y_sorted = y[sorted_indices]

        best_threshold = None
        best_entropy = float('inf')
        n = len(y)

        for i in range(1, n):
            if y_sorted[i] != y_sorted[i-1]:  # Só considera splits entre classes diferentes
                threshold = (X_sorted[i] + X_sorted[i-1]) / 2

                left_mask = X_column <= threshold
                right_mask = X_column > threshold

                left_y = y[left_mask]
                right_y = y[right_mask]

                left_entropy = self.entropy(left_y)
                right_entropy = self.entropy(right_y)
                weighted_entropy = (len(left_y) / n) * left_entropy + (len(right_y) / n) * right_entropy

                if weighted_entropy < best_entropy:
                    best_entropy = weighted_entropy
                    best_threshold = threshold

        return best_threshold, best_entropy

    def most_common_label(self, y):
        '''Retorna a classe mais comum num subconjunto'''
        return Counter(y).most_common(1)[0][0]     # garante que a árvore nunca fica sem resposta

    def predict(self, X):
        '''Aplica a árvore a cada exemplo do conjunto de teste'''
        predictions = []     # Lista para guardar as previsões de cada exemplo
        if isinstance(X, pd.DataFrame):  # Forma como itera os exemplos, suporta DataFrames e numpy arrays
            iterator = X.iterrows()
        else:
            iterator = enumerate(X)

        for _, x in iterator:
            prediction = self.traverse_tree(x, self.root)      # Percorre a árvore para chegar a uma previsão
            predictions.append(prediction if prediction is not None else self.most_common_class)
        return np.array(predictions)
   
    def traverse_tree(self, x, node):
        '''Percorre a árvore a partir da raiz até chegar a um nó folha para fazer uma previsão'''
        if node.is_leaf_node():       # Se o nó for folha, retorna a classe
            return node.value
        val = x[node.feature]      # Vai buscar o valor do atributo usado neste nó

        if node.threshold is not None:  # Numérico
            branch = 'left' if val <= node.threshold else 'right'    # Decide se vai para a esquerda ou direita dependendo do threshold
        else:                           # Categórico
            branch = val

        child = node.branches.get(branch)    # Vai buscar o nó filho correspondente ao ramo escolhido
        if child is None:
            return None            
        return self.traverse_tree(x, child)  # Se encontrou um filho, continua a percorrer a árvore recursivamente

    def print_tree(self, feature_names):
        '''Desenha a árvore de decisão no terminal'''
        if feature_names is None:
            raise ValueError("Nome dos atributos deve ser dado para imprimir a árvore")

        def print_node(node, indent=""):
            if node.is_leaf_node():
                print(f"{indent} Previsão: {node.value}")
                return

            feature_name = feature_names[node.feature]
            if node.threshold is not None:  # Numérico
                print(f"{indent}{feature_name} <= {node.threshold}")
                print(f"{indent}├── Esquerda:")
                print_node(node.branches['left'], indent + "│   ")
                print(f"{indent}└── Direita:")
                print_node(node.branches['right'], indent + "    ")
            else:  # Categórico
                for val, branch in node.branches.items():
                    print(f"{indent}{feature_name} == {val}")
                    print_node(branch, indent + "    ")

        print("Decision Tree:")
        print_node(self.root)

    def draw_tree(self, feature_names):
        if feature_names is None:
            raise ValueError("Feature names must be provided to draw the tree.")
        texts, connections = self._plot_tree(self.root, feature_names, x=0)
        # Dinâmico baseado nos nós
        max_depth = max(-y for (_, y) in [pos for pos, _ in texts]) if texts else 1
        num_nodes = len(texts)
        fig_width = max(20, num_nodes * 2)   # Largura agora mais generosa
        fig_height = max(10, max_depth * 3)  # Altura também
        fig, ax = plt.subplots(figsize=(fig_width, fig_height))
        for (start, end) in connections:
            ax.plot([start[0], end[0]], [start[1], end[1]], 'k-', linewidth=1.5)
        for (x, y), label in texts:
            ax.text(x, y, label, ha='center', va='center',
                    bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.5'),
                    fontsize=13)
        ax.set_axis_off()
        ax.relim()
        ax.autoscale_view()
        plt.tight_layout()
        plt.show()

    def _plot_tree(self, node, feature_names, depth=0, x=0, y_step=2.5, x_offset=6.0):
        if node is None:
            return [], []
        texts = []
        connections = []
        if node.is_leaf_node():
            label = f"Predict: {node.value}"
        elif node.threshold is not None:
            label = f"{feature_names[node.feature]} <= {node.threshold:.2f}"
        else:
            label = f"{feature_names[node.feature]}"
        this_pos = (x, -depth * y_step)
        texts.append((this_pos, label))
        if not node.is_leaf_node():
            if node.threshold is not None:  # Numérico
                spread = x_offset / (depth + 1)  # <--- maior spread quanto mais fundo
                left_x = x - spread
                right_x = x + spread

                left_texts, left_connections = self._plot_tree(node.branches['left'], feature_names, depth + 1, left_x, y_step, x_offset)
                right_texts, right_connections = self._plot_tree(node.branches['right'], feature_names, depth + 1, right_x, y_step, x_offset)

                texts += left_texts + right_texts
                connections += left_connections + right_connections
                connections.append((this_pos, (left_x, -(depth + 1) * y_step)))
                connections.append((this_pos, (right_x, -(depth + 1) * y_step)))

            else:  # Categórico
                num_branches = len(node.branches)
                spacing = x_offset * 2 / (num_branches + 1)
                for i, (val, branch) in enumerate(node.branches.items()):
                    child_x = x - x_offset + (i + 1) * spacing
                    branch_texts, branch_connections = self._plot_tree(branch, feature_names, depth + 1, child_x, y_step, x_offset)
                    texts += branch_texts
                    connections += branch_connections
                    connections.append((this_pos, (child_x, -(depth + 1) * y_step)))
        return texts, connections

    def save(self):
        '''Guarda a árvore num ficheiro'''
        filename = "decision_tree.pkl"
        with open(filename, 'wb') as f:
            pickle.dump(self, f)
        print(f"Árvore guardada em '{filename}'.")
    
    def load(self):
        '''Carrega a árvore de um ficheiro'''
        filename = "decision_tree.pkl"
        try:
            with open(filename, 'rb') as f:
                tree = pickle.load(f)
            print(f"Árvore carregada de '{filename}'.")
            return tree
        except FileNotFoundError:
            print(f"Erro: Ficheiro '{filename}' não encontrado. Execute primeiro 'decision_tree.py'.")
            exit()
            
        
class DecisionTree_Player:
    def __init__(self, random = True):
        '''Constrói um jogador a partir de uma árvore de decisão'''
        if not random:
            temp_tree = DecisionTree()
            self.tree = temp_tree.load()  # Usa o return do método `load`
        else:
            self.tree = DecisionTree()
            filename = "dataset_quatro_em_linha_mcts.csv"
            df = pd.read_csv(filename)
            X = df.iloc[:, :-1].values  # Todas as colunas exceto a última
            y = df.iloc[:, -1].values  # Última coluna
            size = 0.2
            X_sample, _, y_sample, _ = train_test_split(X, y, test_size=size, random_state=42)
            print(f"a treinar a árvore com {1 - size} do dataset")
            self.tree.fit(X_sample, y_sample)
            print("Árvore treinada com dados aleatórios.")

    def play(self, state, legal_moves):
        '''Faz uma jogada com base no estado atual do jogo'''
        prediction = self.tree.predict([state])
        print(f"Jogada prevista: {prediction}")
        if prediction is not None and prediction[0] in legal_moves:
            return prediction[0]
        else:
            return random.choice(legal_moves)  # Se a previsão não for válida, escolhe aleatoriamente entre as jogadas válidas