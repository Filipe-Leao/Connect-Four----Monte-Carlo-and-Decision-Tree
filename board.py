# board.py
from variables import *

class Board:
    
    __slots__ = ['board', 'player', 'moves_played', 'game_over', 'winner']
    
    def __init__(self):
        self.board = self.create_board()
        self.player = PLAYER1  # Começa com o Jogador 1
        self.moves_played = 0  # Contador de peças jogadas
        self.game_over = False
        self.winner = None

    def create_board(self):
        """Cria um tabuleiro vazio"""
        return [[EMPTY for _ in range(COLS)] for _ in range(ROWS)]

    def is_valid_move(self, col):
        """Verifica se é possível jogar na coluna indicada"""
        return 0 <= col < COLS and self.board[0][col] == EMPTY

    def get_next_open_row(self, col):
        """Encontra a próxima posição disponível na coluna"""
        for r in range(ROWS - 1, -1, -1):
            if self.board[r][col] == EMPTY:
                return r
        return -1  # Coluna cheia

    def drop_piece(self, col):
        """Coloca uma peça na coluna especificada e atualiza o estado do jogo"""
        if not self.is_valid_move(col):
            return False
            
        row = self.get_next_open_row(col)
        self.board[row][col] = self.player
        self.moves_played += 1
        
        # Verifica se o jogador atual ganhou
        if self.check_win(self.player):
            self.game_over = True
            self.winner = self.player
            return True
            
        # Verifica se o jogo acabou em empate
        if self.moves_played == ROWS * COLS:
            self.game_over = True
            self.winner = None
            return True
            
        # Alterna o jogador atual
        if self.player == PLAYER1:
            self.player = PLAYER2
        else:  
            self.player = PLAYER1   
        return True

    def check_win(self, piece):
        """Verifica se há uma vitória para a peça especificada"""
        # Verifica vitória horizontal
        for r in range(ROWS):
            for c in range(COLS - 3):
                if (self.board[r][c] == piece and 
                    self.board[r][c + 1] == piece and 
                    self.board[r][c + 2] == piece and 
                    self.board[r][c + 3] == piece):
                    return True

        # Verifica vitória vertical
        for r in range(ROWS - 3):
            for c in range(COLS):
                if (self.board[r][c] == piece and 
                    self.board[r + 1][c] == piece and 
                    self.board[r + 2][c] == piece and 
                    self.board[r + 3][c] == piece):
                    return True

        # Verifica vitória diagonal (ascendente)
        for r in range(ROWS - 3):
            for c in range(COLS - 3):
                if (self.board[r][c] == piece and 
                    self.board[r + 1][c + 1] == piece and 
                    self.board[r + 2][c + 2] == piece and 
                    self.board[r + 3][c + 3] == piece):
                    return True

        # Verifica vitória diagonal (descendente)
        for r in range(3, ROWS):
            for c in range(COLS - 3):
                if (self.board[r][c] == piece and 
                    self.board[r - 1][c + 1] == piece and 
                    self.board[r - 2][c + 2] == piece and 
                    self.board[r - 3][c + 3] == piece):
                    return True

        return False
    
    def get_legal_moves(self):
        """Retorna todas as jogadas válidas no tabuleiro"""
        return [col for col in range(COLS) if self.is_valid_move(col)]  

    def get_board(self):
        """Retorna o tabuleiro atual"""
        return self.board
        
    def get_current_player(self):
        """Retorna o jogador atual"""
        return self.player
        
    def is_game_over(self):
        """Retorna se o jogo acabou"""
        return self.game_over
        
    def get_winner(self):
        """Retorna o vencedor ou None em caso de empate"""
        return self.winner
        
    def reset(self):
        """Reinicia o tabuleiro para um novo jogo"""
        self.board = self.create_board()
        self.player = PLAYER1
        self.moves_played = 0
        self.game_over = False
        self.winner = None

    def clone(self):
        new_board = Board()
        new_board.board = [row[:] for row in self.board]  # copia linha a linha
        new_board.player = self.player
        new_board.moves_played = self.moves_played 
        new_board.game_over = self.game_over
        new_board.winner = self.winner 
        return new_board