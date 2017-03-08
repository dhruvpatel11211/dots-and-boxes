import numpy as np

PLAYER1 = -1
PLAYER2 = 1
PLAYERS = {'B': -1, 'W': 1}

def board_shape(board_string):
    lines = board_string.split("|")
    rows, cols = (len(lines)+1)/2, (len(lines[0])+1)/2
    return rows, cols

class DotsAndBoxes(object):
    def __init__(self, initial_player=None, rows=None, cols=None, board_string=None, game_obj=None):
        if isinstance(board_string, str):      # construct from string
            self._from_string(initial_player, board_string)
        elif isinstance(game_obj, DotsAndBoxes):  # copy constructor
            self._copy(game_obj)
        else:
            self.rows, self.cols = rows, cols
            self.score = [0, 0] # B, W
            self.turn = initial_player
            self.board = np.zeros((2*rows-1, 2*cols-1), dtype=np.int)
            r, c = self.board.shape
            self._edges = np.reshape([i%2 != j%2 for j in range(c) for i in range(r)], (r, c))

    def _from_string(self, initial_player, board_string):
        lines = board_string.split("|")
        rows, cols = board_shape(board_string)
        self.__init__(initial_player, rows, cols)
        for i, r in enumerate(lines):
            for j, s in enumerate(r):
                edge, box = i%2 != j%2, i%2 == j%2 == 1
                if edge and s == 'x':      # is a filled edge
                    self.board[i, j] += 1
                elif box and s in PLAYERS: # is a filled box
                    self.board[i, j] = PLAYERS[s]
                    self.score[PLAYERS[s] == 1] += 1

    def _copy(self, game_obj):
        self.__dict__.update(game_obj.__dict__)
        self.board = np.array(game_obj.board)
        self.score = game_obj.score[:]

    def play(self, move=None, i=None, j=None, player=None):
        if not player:
            player = self.turn
        if isinstance(move, np.ndarray):
            i, j = move[0], move[1]
        if self._is_valid(player, i, j):
            self.board[i, j] = player
            self._update(player, i, j)
        else:
            raise Exception('Invalid move %d,%d' % (i, j))

    def get_available_moves(self):
        unplayed = np.logical_not(self.board)
        return np.transpose(np.where(np.logical_and(unplayed, self._edges)))

    def _is_valid(self, player, i, j):
        turn = self.turn == player   # is players' turn
        edge = i%2 != j%2            # i xor j are even
        free = self.board[i, j] == 0 # edge is not already filled
        over = self.is_over()        # game is over
        return not over and turn and edge and free

    def is_over(self):
        return sum(self.score) == (self.rows-1) * (self.cols-1)

    def _update(self, player, i, j):
        vertical = i%2 > j%2
        a = self._check_box(player, i, j-1) if vertical else self._check_box(player, i-1, j)
        b = self._check_box(player, i, j+1) if vertical else self._check_box(player, i+1, j)
        if not (a or b): # did not fill any box
            self.turn *= -1

    def _check_box(self, player, i, j):
        irange = i > 0 and i < 2*self.rows-1
        jrange = j > 0 and j < 2*self.cols-1
        box = i%2 == j%2 == 1        # i and j are odd
        if irange and jrange: # and box:
            filled = self.board[i-1, j] and self.board[i+1, j] and self.board[i, j-1] and self.board[i, j+1]
            if filled:
                self.board[i, j] = player
                self.score[player == 1] += 1
            return filled
