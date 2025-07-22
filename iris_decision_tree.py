# iris_decision_tree.py

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from decisiontree import DecisionTree
from variables import *

# Carrega o dataset Iris
def load_iris_dataset(filepath):
    df = pd.read_csv(filepath)
    return df

# Função de Grid Search para escolher melhores parâmetros
def grid_search_decision_tree(X, y):
    best_params = None
    best_accuracy = 0
    best_dt = None

    # Separa treino/validação para avaliação dos hiperparâmetros
    X_train_split, X_val_split, y_train_split, y_val_split = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    for max_depth in [2, 3, 4, 5]:
        for min_samples_split in [2, 5, 10]:
            #print(f"A testar max_depth={max_depth}, min_samples_split={min_samples_split}")
            dt = DecisionTree(max_depth=max_depth, min_samples_split=min_samples_split, random_state=42)
            dt.fit(X_train_split, y_train_split)
            y_pred_val = dt.predict(X_val_split)
            acc = (y_pred_val == y_val_split).mean()
            #print(f"Accuracy treino: {acc:.4f}")

            if acc > best_accuracy or (acc == best_accuracy and (best_params is None or max_depth < best_params[0])):
                best_accuracy = acc
                best_params = (max_depth, min_samples_split)
                best_dt = dt

    print(f"\nMelhor combinação encontrada: max_depth={best_params[0]}, min_samples_split={best_params[1]} com accuracy {best_accuracy:.4f}")
    return best_dt

# Função principal
def iris_decision_tree():
    # Carregar e preparar os dados
    iris_df = load_iris_dataset('C:/Users/Asus/OneDrive/Desktop/IA/ConnectedFour/iris.csv')
    print("Primeiras linhas do dataset original:")
    print(iris_df.head())

    # Remover coluna do ID
    iris_df = iris_df.drop(columns=["ID"])

    # Separar atributos e classificação
    X = iris_df.iloc[:, :-1]
    y = iris_df.iloc[:, -1]

    # Dividir uma vez para treino/teste
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42
    )

    print("\nDistribuição de classes no conjunto de treino:")
    print(y_train.value_counts())

    # Grid search para encontrar melhor árvore
    best_dt = grid_search_decision_tree(X_train, y_train)

    print("\nÁrvore de Decisão (print no terminal):")
    best_dt.print_tree(feature_names=X.columns.tolist())

    print("\nÁrvore de Decisão (visualização gráfica):")
    best_dt.draw_tree(feature_names=X.columns.tolist())

    # Accuracy de teste
    y_pred = best_dt.predict(X_test)
    accuracy = (y_pred == y_test).mean()
    print(f"\nTest Accuracy: {accuracy:.4f}")

    return best_dt

iris_tree = iris_decision_tree()
