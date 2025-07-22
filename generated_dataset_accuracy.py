# generated_dataset_accuracy.py

# Cada estado do jogo foi achatado (flattened) para um vetor com 42 atributos (6x7), onde:
# - 0 = célula vazia
# - 1 = peça do jogador 1
# - 2 = peça do jogador 2

from decisiontree import DecisionTree
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import numpy as np
import pandas as pd

if __name__ == "__main__":
    # Carregar o dataset
    df = pd.read_csv("dataset_quatro_em_linha_mcts.csv")

    # Separar os atributos (X) e o alvo (y)
    X = df.iloc[:, :-1].values  # Os 42 atributos do estado do jogo
    y = df.iloc[:, -1].values   # A última coluna é a ação/jogada ideal

    # Dividir o dataset em treino e teste (80% treino, 20% teste)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, shuffle=True
    )

    # Criar e treinar a árvore
    tree = DecisionTree(max_depth=12)
    tree.fit(X_train, y_train)

    # Fazer previsões no conjunto de teste
    y_pred = tree.predict(X_test)

    # Calcular accuracy
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Accuracy no conjunto de teste: {accuracy:.2f}")
    print(f"Nº de amostras de treino: {len(X_train)}")
    print(f"Nº de amostras de teste: {len(X_test)}")

    # Guardar a árvore treinada
    tree.save()