import random

piece_score = {"K": 0, "Q": 10, "R": 5, "B": 3, "N": 3, "P": 1}
knight_scores = [[1, 1, 1, 1, 1, 1, 1, 1],
                 [1, 2, 2, 2, 2, 2, 2, 1],
                 [1, 2, 3, 3, 3, 3, 2, 1],
                 [1, 2, 3, 4, 4, 3, 2, 1],
                 [1, 2, 3, 4, 4, 3, 2, 1],
                 [1, 2, 3, 3, 3, 3, 2, 1],
                 [1, 2, 2, 2, 2, 2, 2, 1],
                 [1, 1, 1, 1, 1, 1, 1, 1]]

bishop_scores = [[4, 3, 2, 1, 1, 2, 3, 4],
                 [3, 4, 3, 2, 2, 3, 4, 3],
                 [2, 3, 4, 3, 3, 4, 3, 2],
                 [1, 2, 3, 4, 4, 3, 2, 1],
                 [1, 2, 3, 4, 4, 3, 2, 1],
                 [2, 3, 4, 3, 3, 4, 2, 2],
                 [3, 4, 3, 2, 2, 3, 4, 3],
                 [4, 3, 2, 1, 1, 2, 3, 4]]

queen_scores = [[1, 1, 1, 3, 1, 1, 1, 1],
                [1, 2, 3, 3, 3, 1, 1, 1],
                [1, 4, 3, 3, 3, 4, 2, 1],
                [1, 2, 3, 3, 3, 2, 2, 1],
                [1, 2, 3, 3, 3, 2, 2, 1],
                [1, 4, 3, 3, 3, 4, 2, 1],
                [1, 1, 2, 3, 3, 1, 1, 1],
                [1, 1, 1, 3, 1, 1, 1, 1]]

rook_scores = [[4, 3, 4, 4, 4, 4, 3, 4],
               [4, 4, 4, 4, 4, 4, 4, 4],
               [1, 1, 2, 3, 3, 2, 1, 1],
               [1, 2, 3, 4, 4, 3, 2, 1],
               [1, 2, 3, 4, 4, 3, 2, 1],
               [1, 1, 2, 2, 2, 2, 1, 1],
               [4, 4, 4, 4, 4, 4, 4, 4],
               [4, 3, 4, 4, 4, 4, 3, 4]]

white_pawn_scores = [[8, 8, 8, 8, 8, 8, 8, 8],
                     [8, 8, 8, 8, 8, 8, 8, 8],
                     [5, 6, 6, 7, 7, 6, 6, 5],
                     [2, 3, 3, 5, 5, 3, 3, 2],
                     [1, 2, 3, 4, 4, 3, 2, 1],
                     [1, 1, 2, 3, 3, 2, 1, 1],
                     [1, 1, 1, 0, 0, 1, 1, 1],
                     [0, 0, 0, 0, 0, 0, 0, 0]]

black_pawn_scores = [[0, 0, 0, 0, 0, 0, 0, 0],
                     [1, 1, 1, 0, 0, 1, 1, 1],
                     [1, 1, 2, 3, 3, 2, 1, 1],
                     [1, 2, 3, 4, 4, 3, 2, 1],
                     [2, 3, 3, 5, 5, 3, 3, 2],
                     [5, 6, 6, 7, 7, 6, 6, 5],
                     [8, 8, 8, 8, 8, 8, 8, 8],
                     [8, 8, 8, 8, 8, 8, 8, 8]]


piece_position_scores = {'N': knight_scores, 'Q': queen_scores, 'B': bishop_scores, 'R': rook_scores,
                         "P-w": white_pawn_scores, "P-b": black_pawn_scores}

CHECKMATE = 1000
STALEMATE = 0
DEPTH = 3

def find_random_move(valid_moves):
    return valid_moves[random.randint(0, len(valid_moves) - 1)]

'''
Find the best move based on material (pieces) alone
'''
def find_best_move_no_recursion(gs, valid_moves):

    turn_multiplier = 1 if gs.white_to_move else -1
    opp_min_max_score = -CHECKMATE
    best_player_move = None
    for player_move in valid_moves:
        gs.make_move(player_move)
        opponents_moves = gs.get_valid_moves()
        opp_max_score = -CHECKMATE
        if gs.stalemate:
            opp_max_score = STALEMATE
        elif gs.checkmate:
            opp_max_score = -CHECKMATE
        else:
            opp_max_score = -CHECKMATE
            for opp_move in opponents_moves:
                gs.make_move(opp_move)
                gs.get_valid_moves()
                if gs.stalemate:
                    score = STALEMATE
                elif gs.checkmate:
                    score = -turn_multiplier * CHECKMATE
                else:
                    score = -turn_multiplier * score_material(gs.board)
                if opp_max_score < score:
                    turn_multiplier = score
                    best_player_move = player_move
                gs.undo_move()
            if opp_min_max_score > opp_max_score:
                opp_min_max_score = opp_max_score
                best_player_move = player_move
        gs.undo_move()
    return best_player_move

def find_best_move(gs, valid_moves, return_queue):
    global next_move, counter
    counter = 0
    next_move = None
    random.shuffle(valid_moves)
    #find_move_min_max(gs, valid_moves, DEPTH, gs.whiteToMove)
    #find_move_nega_max(gs, valid_moves, DEPTH, 1 if gs.white_to_move else -1)
    find_move_nega_max_alpha_beta(gs, valid_moves, DEPTH, -CHECKMATE, CHECKMATE, 1 if gs.white_to_move else -1)
    #find_random_move(valid_moves)
    #find_best_move_no_recursion(gs, valid_moves)
    print(counter)
    return_queue.put(next_move)

def find_best_move_min_max(gs, valid_moves):
    global next_move
    next_move = None
    find_move_min_max(gs, valid_moves, DEPTH, gs.white_to_move)
    return next_move


'''
Helper function for first recursive call
'''
def find_move_min_max(gs, valid_moves, depth, whiteToMove):
    global next_move
    if depth == 0:
        return score_material(gs.board)
    if whiteToMove:
        max_score = -CHECKMATE
        for move in valid_moves:
            gs.make_move(move)
            next_moves = gs.get_valid_moves()
            score = find_move_min_max(gs, next_moves, depth - 1, False)
            if score > max_score:
                max_score = score
                if depth == DEPTH:
                    next_move = move
            gs.undo_move()
        return max_score

    else:
        min_score = CHECKMATE
        for move in valid_moves:
            gs.make_move(move)
            next_moves = gs.get_valid_moves()
            score = find_move_min_max(gs, next_moves, depth - 1, True)
            if score > min_score:
                min_score = score
                if depth == DEPTH:
                    next_move = move
            gs.undo_move()
        return min_score


def find_move_nega_max(gs, valid_moves, depth, turn_multiplier):
    global next_move
    if depth == 0:
        return turn_multiplier * score_board(gs)

    max_score = -CHECKMATE
    for move in valid_moves:
        gs.make_move(move)
        next_moves = gs.get_valid_moves()
        score = -find_move_nega_max(gs, next_moves, depth - 1, -turn_multiplier)
        if score > max_score:
            max_score = score
            if depth == DEPTH:
                next_move = move
        gs.undo_move()

    return max_score

def find_move_nega_max_alpha_beta(gs, valid_moves, depth, alpha, beta, turn_multiplier):
    global next_move, counter
    counter += 1
    if depth == 0:
        return turn_multiplier * score_board(gs)

    max_score = -CHECKMATE
    for move in valid_moves:
        gs.make_move(move)
        next_moves = gs.get_valid_moves()
        score = -find_move_nega_max_alpha_beta(gs, next_moves, depth - 1, -beta, -alpha, -turn_multiplier)
        if score > max_score:
            max_score = score
            if depth == DEPTH:
                next_move = move
                print(move, score)
        gs.undo_move()
        if max_score > alpha: # pruning happens
            alpha = max_score
        if alpha >= beta:
            break

    return max_score

'''
A positive score is good for white, a negative score is good for black
'''
def score_board(gs):
    if gs.checkmate:
        if gs.white_to_move:
            return -CHECKMATE # black wins
        else:
            return CHECKMATE # white wins

    score = 0
    for row in range(len(gs.board)):
        for col in range(len(gs.board[row])):
            square = gs.board[row][col]
            if square != "---":
                # score it positionally
                piece_position_score = 0
                if square[0] != 'K': # no position for king
                    if square[0] == 'P': # for pawns
                        piece_position_score = piece_position_scores[square][row][col]
                    else: # for other pieces
                        piece_position_score = piece_position_scores[square[0]][row][col]
                if square[2] == 'w': # white goes toward positive score
                    score += piece_score[square[0]] + piece_position_score * 0.5
                elif square[2] == 'b': # black goes towards negative score
                    score -= piece_score[square[0]] + piece_position_score * 0.5
    return score


'''
Score the board based on pieces
'''
def score_material(board):
    score = 0
    for row in board:
        for square in row:
            if square[2] == 'w': # white goes toward positive score
                score += piece_score[square[0]]
            elif square[2] == 'b': # black goes towards negative score
                score -= piece_score[square[0]]
    return score