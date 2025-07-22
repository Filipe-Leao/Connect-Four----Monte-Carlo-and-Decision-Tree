# Connect-Four – Monte Carlo and Decision Tree

AI project – 2nd Year, University of Porto

Developed by Diogo Padilha, Rita Nunes

Assisted by ChatGPT and Gemini

---

## Requirements

Instal dependencies in terminal ou comand line

```bash
pip install numpy pandas scikit-learn matplotlib pygame
```

## How to run
  In terminal execute 
```bash
  python3 menu.py
```

## Description

This project allows playing **Connect Four** in multiple modes:

* Player vs Player
* Player vs **Monte Carlo Tree Search (MCTS)**
* Player vs **Decision Tree (ID3)**
* **AI vs AI** (****etween different difficulty levels and models)

Both the **MCTS** and **ID3 Decision Tree** algorithms were implemented from scratch.

The decision tree is trained using `dataset_quatro_em_linha_mcts.csv`, which contains matches of MCTS vs MCTS across various difficulty levels.
To use a different dataset, update the filename in `generate_dataset_accuracy.py`:

```python
df = pd.read_csv("dataset_quatro_em_linha_mcts.csv")
```

To generate new training data or expand an existing dataset, run `generate_dataset_mc.py`.
You can configure the difficulty levels and number of games directly within that file.
