"""
Responsible for storing all the information about current state of chess game. Also determines valid moves and
has a move log.
"""
from tkinter import *
import numpy as np

class GameState():
    def __init__(self):
        # Board is 8x8 2D list
        # The first character represents the piece (i.e King or Pawn, etc) and the third character
        # represents the colour (i.e., "b" or "w" for black or white).
        # The second character is a dash, thus these are 3 character strings
        self.board = np.array([
            ["R-b", "N-b", "B-b", "Q-b", "K-b", "B-b", "N-b", "R-b"],
            ["P-b", "P-b", "P-b", "P-b", "P-b", "P-b", "P-b", "P-b"],
            ["---", "---", "---", "---", "---", "---", "---", "---"],
            ["---", "---", "---", "---", "---", "---", "---", "---"],
            ["---", "---", "---", "---", "---", "---", "---", "---"],
            ["---", "---", "---", "---", "---", "---", "---", "---"],
            ["P-w", "P-w", "P-w", "P-w", "P-w", "P-w", "P-w", "P-w"],
            ["R-w", "N-w", "B-w", "Q-w", "K-w", "B-w", "N-w", "R-w"]])
        self.moveFunctions = {'P': self.get_pawn_moves, 'R': self.get_rook_moves, 'N': self.get_knight_moves,
        'B': self.get_bishop_moves, 'K': self.get_king_moves, 'Q': self.get_queen_moves}
        self.white_to_move = True
        self.moveLog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)

        self.pins = []
        self.checks = []
        self.checkmate = False
        self.stalemate = False
        self.enpassantPossible = () # coordinates for the square where en passant capture is possible
        self.enPassantPossibleLog = [self.enpassantPossible]
        self.currentCastlingRight = CastleRights(True, True, True, True)
        self.castleRightsLog = [CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                           self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)]


    def make_move(self, move):
        self.board[move.startRow, move.startCol] = "---"
        self.board[move.endRow, move.endCol] = move.pieceMoved
        self.moveLog.append(move)
        self.white_to_move = not self.white_to_move  # switch player turn
        # update king position
        if move.pieceMoved == "K-w":
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == "K-b":
            self.blackKingLocation = (move.endRow, move.endCol)

        # pawn promotion
        if move.isPawnPromotion:
            promo_window = Tk()
            promo_window.title("Choose Pawn Promotion")
            promo_window.geometry("200x150")

            def promote_piece(piece):
                move.promotedPiece = piece + '-' + move.pieceMoved[2]
                promo_window.destroy()
                self.board[move.endRow][move.endCol] = move.promotedPiece

            Label(promo_window, text="Pawn Promotion").pack()
            Button(promo_window, text="Queen", command=lambda: promote_piece("Q")).pack(fill=X)
            Button(promo_window, text="Rook", command=lambda: promote_piece("R")).pack(fill=X)
            Button(promo_window, text="Bishop", command=lambda: promote_piece("B")).pack(fill=X)
            Button(promo_window, text="Knight", command=lambda: promote_piece("N")).pack(fill=X)

            promo_window.mainloop()

        # enpassant
        if move.isEnpassantMove:
            self.board[move.startRow, move.endCol] = "---" # capturing pawn

        # update enpassantPossible variable
        if move.pieceMoved[0] == 'P' and abs(move.startRow - move.endRow) == 2: # only on 2 square pawn advances
            self.enpassantPossible = ((move.startRow + move.endRow) // 2, move.endCol)
        else:
            self.enpassantPossible = () # reset

        self.enPassantPossibleLog.append(self.enpassantPossible)

        # castle move
        if move.isCastleMove:
            if move.endCol - move.startCol == 2: # king side castle
                self.board[move.endRow, move.endCol - 1] = self.board[move.endRow, move.endCol + 1]
                self.board[move.endRow, move.endCol + 1] = "---" # remove old rook
            else: # queenside
                self.board[move.endRow, move.endCol + 1] = self.board[move.endRow, move.endCol - 2]
                self.board[move.endRow, move.endCol - 2] = "---" # remove old rook

        # castling rights - update whenever there is rook or king move
        self.updateCastleRights(move)
        self.castleRightsLog.append(CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                           self.currentCastlingRight.wqs, self.currentCastlingRight.bqs))


    '''
    Undo previous move made
    '''
    def undo_move(self):
        if len(self.moveLog) != 0: # make sure there is a move to undo
            move = self.moveLog.pop()
            self.board[move.startRow, move.startCol] = move.pieceMoved
            self.board[move.endRow, move.endCol] = move.pieceCaptured
            #self.moveLog.append(move)
            self.white_to_move = not self.white_to_move
            # if needed, update the king's position
            if move.pieceMoved == "K-w":
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == "K-b":
                self.blackKingLocation = (move.startRow, move.startCol)

            #undo enpassant
            if move.isEnpassantMove:
                self.board[move.endRow, move.endCol] = "---" # remove the pawn that was on wrong square
                self.board[move.startRow, move.endCol] = move.pieceCaptured # puts the pawn back on correct square

            self.enPassantPossibleLog.pop()
            self.enpassantPossible = self.enPassantPossibleLog[-1]

            # undo 2 square pawn advance
            if move.pieceMoved[0] == 'P' and abs(move.startRow - move.endRow):
                self.enpassantPossible = ()

            # undo castling rights
            self.castleRightsLog.pop() # get rid of new castle rights from recent move
            new_rights = self.castleRightsLog[-1]
            self.currentCastlingRight = CastleRights(new_rights.wks, new_rights.bks, new_rights.wqs, new_rights.bqs) # set the current castle rights to the one before the recent move

            # undo castle move
            if move.isCastleMove:
                if move.endCol - move.startCol == 2: # kingside
                    self.board[move.endRow, move.endCol + 1] = self.board[move.endRow, move.endCol - 1]
                    self.board[move.endRow, move.endCol - 1] = "---" # remove old rook
                else: # queenside
                    self.board[move.endRow, move.endCol - 2] = self.board[move.endRow, move.endCol + 1]
                    self.board[move.endRow, move.endCol + 1] = "---" # remove old rook

            self.checkmate = False
            self.stalemate = False

    '''
    update the castle rights given the move
    '''
    def updateCastleRights(self, move):
        if move.pieceMoved == "K-w":
            self.currentCastlingRight.wks = False
            self.currentCastlingRight.wqs = False
        elif move.pieceMoved == "K-b":
            self.currentCastlingRight.bks = False
            self.currentCastlingRight.bqs = False
        elif move.pieceMoved == "R-w":
            if move.startRow == 7:
                if move.startCol == 0: # left rook
                    self.currentCastlingRight.wqs = False
                elif move.startCol == 7: # right rook
                    self.currentCastlingRight.wks = False
        elif move.pieceMoved == "R-b":
            if move.startRow == 0:
                if move.startCol == 0: # left rook
                    self.currentCastlingRight.bqs = False
                elif move.startCol == 7: # right rook
                    self.currentCastlingRight.bks = False

        #if rook is captured
        if move.pieceCaptured == "R-w":
            if move.endRow == 7:
                if move.endCol == 0:
                    self.currentCastlingRight.wqs = False
                elif move.endCol == 7:
                    self.currentCastlingRight.wks = False
        elif move.pieceCaptured == "R-b":
            if move.endRow == 0:
                if move.endCol == 0:
                    self.currentCastlingRight.bqs = False
                elif move.endCol == 7:
                    self.currentCastlingRight.bks = False


    '''
    All moves without considering checks
    '''
    def get_all_possible_moves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r, c][2]
                if (turn == 'w' and self.white_to_move) or (turn == 'b' and not self.white_to_move):
                    piece = self.board[r, c][0]
                    self.moveFunctions[piece](r, c, moves)
        return moves

    '''
    All moves considering checks
    '''
    def get_valid_moves(self):
        # for log in self.castleRightsLog:
        #     print(log.wks, log.wqs, log.bks, log.bqs, end=", ")
        #     print()

        tempEnpassantPosssible = self.enpassantPossible
        tempCastleRights = CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                        self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)

        #self.inCheck, self.pins, self.checks = self.check_for_pins_and_checks()
        #1) generate all possible moves
        moves = self.get_all_possible_moves()

        #2) for each move, make the move
        for i in range(len(moves) - 1, -1, -1):
            self.make_move(moves[i])
            #3) generate all opponent's moves
            #opp_moves = self.get_all_possible_moves()
            #4 for each of your opponent's moves, see if they attack your king
            self.white_to_move = not self.white_to_move
            if self.in_check():
                moves.remove(moves[i])
                #5) if they do attack your king, not a valid move
            self.white_to_move = not self.white_to_move
            self.undo_move()
        if len(moves) == 0: # either checkmate or stalemate
            if self.in_check():
                self.checkmate = True
            else:
                self.stalemate = True

        if self.white_to_move:
            self.getCastleMoves(self.whiteKingLocation[0], self.whiteKingLocation[1], moves)
        else:
            self.getCastleMoves(self.blackKingLocation[0], self.blackKingLocation[1], moves)

        self.enpassantPossible = tempEnpassantPosssible
        self.currentCastlingRight = tempCastleRights

        return moves

    '''
    Determine if enemy can attack the square
    '''
    def squareUnderAttack(self, r, c):
        self.white_to_move = not self.white_to_move # switch turns
        oppMoves = self.get_all_possible_moves()
        self.white_to_move = not self.white_to_move # switch turns back
        for move in oppMoves:
            if move.endRow == r and move.endCol == c: # square is under attack
                return True
        return False

    ''' 
    Determine if current player is in check
    '''
    def in_check(self):
        if self.white_to_move:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])



    def get_pawn_moves(self, r, c, moves):

        if self.white_to_move:
            moveAmount = -1
            startRow = 6
            backRow = 0
            oppColour = 'b'
            king_row, king_col = self.whiteKingLocation
        else:
            moveAmount = 1
            startRow = 1
            backRow = 7
            oppColour = 'w'
            king_row, king_col = self.blackKingLocation
        isPawnPromotion = False


        if self.board[r + moveAmount, c] == "---":
            #if not piecePinned or pinDirection == (moveAmount, 0):
                if r + moveAmount == backRow: # if piece gets to back rank then it's pawn promo
                    isPawnPromotion = True
                moves.append(Move((r, c), (r + moveAmount, c), self.board, is_pawn_promotion= isPawnPromotion))
                if r == startRow and self.board[r + 2 * moveAmount, c] == "---":
                    moves.append(Move((r, c), (r + 2 * moveAmount, c), self.board))
        # captures
        if (c - 1) >= 0: # capture to the left
            #if not piecePinned or pinDirection == (moveAmount, -1):
                if self.board[r + moveAmount, c - 1][2] == oppColour: #enemy piece to capture
                    if r + moveAmount == backRow:
                        isPawnPromotion = True
                    moves.append(Move((r, c), (r + moveAmount, c - 1), self.board, is_pawn_promotion= isPawnPromotion))
                if (r + moveAmount, c - 1) == self.enpassantPossible:
                    attacking_piece = blocking_piece = False
                    if king_row == r:
                        if king_col < c: # king is left of pawn
                            # inside between king and pawn; outside range between pawn border
                            inside_range = range(king_col + 1, c)
                            outside_range = range(c + 2, 8)
                        else: # king right of pawn
                            inside_range = range(king_col - 1, c + 1, - 1)
                            outside_range = range(c - 1, -1, -1)
                        for i in inside_range:
                            if self.board[r, i] != "---":
                                blocking_piece = True
                        for i in outside_range:
                            square = self.board[r, i]
                            if square[2] == oppColour and (square[0] == 'R' or square[0] == 'Q'): # attacking piece
                                attacking_piece = True
                            elif square != "---":
                                blocking_piece = True
                    if not attacking_piece or blocking_piece:
                        moves.append(Move((r, c), (r + moveAmount, c - 1), self.board, is_enpassant_move= True))
        if (c + 1) <= 7: # capture to the right
            #if not piecePinned or pinDirection == (moveAmount, 1):
                if self.board[r + moveAmount, c + 1][2] == oppColour:
                    moves.append(Move((r, c), (r + moveAmount, c + 1), self.board, is_pawn_promotion= isPawnPromotion))
                if (r + moveAmount, c + 1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r + moveAmount, c + 1), self.board, is_enpassant_move= True))



    '''
    Get all rook moves for the rook located at row, col, and add these moves to the list
    '''
    def get_rook_moves(self, r, c, moves):
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
        friendlyColour = 'w' if self.white_to_move else 'b'
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow <= 7 and 0 <= endCol <= 7:
                    #if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                    endPiece = self.board[endRow, endCol]
                    if endPiece == "---":
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[2] != friendlyColour:
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else:
                        break # friendly piece invalid
                else:
                    break # off board


    '''
    Get all bishop moves for the bishop located at row, col, and add these moves to the list
    '''
    def get_bishop_moves(self, r, c, moves):
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        friendlyColour = 'w' if self.white_to_move else 'b'
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    #if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                    endPiece = self.board[endRow, endCol]
                    if endPiece == "---":
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[2] != friendlyColour:
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else:
                        break # friendly piece invalid

                else:
                    break # off board

    '''
    Get all knight moves for the knight located at row, col, and add these moves to the list
    '''
    def get_knight_moves(self, r, c, moves):

        knight_moves = ((-2, -1), (-2, 1), (2, -1), (2, 1),
                      (-1, -2), (-1, 2), (1, -2), (1, 2))
        friendlyColour = 'w' if self.white_to_move else 'b'
        for m in knight_moves:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow <= 7 and 0 <= endCol <= 7:
                #if not piecePinned:
                    endPiece = self.board[endRow, endCol]
                    if endPiece[2] != friendlyColour:
                        moves.append(Move((r, c), (endRow, endCol), self.board))


    '''
    Get all king moves for the king located at row, col, and add these moves to the list
    '''
    def get_king_moves(self, r, c, moves):
        king_moves = ((-1, -1), (-1, 0), (-1, 1), (1, -1),
                 (1, 1), (1, 0), (0, -1), (0, 1))
        friendlyColour = 'w' if self.white_to_move else 'b'
        for i in range(8):
            endRow = r + king_moves[i][0]
            endCol = c + king_moves[i][1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow, endCol]
                if endPiece[2] != friendlyColour:

                    moves.append(Move((r, c), (endRow, endCol), self.board))




    '''
    Generate all valid castle moves for king at (r, c) and add them to the valid list of moves
    '''
    def getCastleMoves(self, row, col, moves):
        #in_check = self.squareUnderAttack(row, col)
        # get the castle moves for the king
        if self.squareUnderAttack(row, col):
            return  # can't castle while in check

        if (self.white_to_move and self.currentCastlingRight.wks) or (not self.white_to_move and self.currentCastlingRight.bks):
            self.getKingsideCastleMoves(row, col, moves)
        if (self.white_to_move and self.currentCastlingRight.wqs) or (not self.white_to_move and self.currentCastlingRight.bqs):
            self.getQueensideCastleMoves(row, col, moves)

    def getKingsideCastleMoves(self, row, col, moves):
        if self.board[row, col + 1] == '--' and self.board[row, col + 2] == '---':
            if not self.squareUnderAttack(row, col + 1) and not self.squareUnderAttack(row, col + 2):
                moves.append(Move((row, col), (row, col + 2), self.board, is_castle_move=True))

    def getQueensideCastleMoves(self, row, col, moves):
        if self.board[row, col - 1] == '--' and self.board[row, col - 2] == '---' and self.board[row, col - 3] == '---':
            if not self.squareUnderAttack(row, col - 1) and not self.squareUnderAttack(row, col - 2):
                moves.append(Move((row, col), (row, col - 2), self.board, is_castle_move=True))

    '''
    Get all queen moves for the queen located at row, col, and add these moves to the list
    '''
    def get_queen_moves(self, r, c, moves):
        self.get_rook_moves(r, c, moves)
        self.get_bishop_moves(r, c, moves)

class CastleRights():
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs

class Move:
    # maps keys to values
    # key : value

    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    tilesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    colsToTiles = {v: k for k, v in tilesToCols.items()}

    def __init__(self, StartSq, endSq, board, is_pawn_promotion = False, is_enpassant_move = False,
                 is_castle_move = False, is_check = False, is_checkmate = False):
        self.startRow = StartSq[0]
        self.startCol = StartSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.board = board
        self.pieceMoved = board[self.startRow, self.startCol]
        self.pieceCaptured = board[self.endRow, self.endCol]
        # pawn promo
        self.isPawnPromotion = is_pawn_promotion
        if (self.pieceMoved == "P-w" and self.endRow == 0) or (self.pieceMoved == "P-b" and self.endRow == 7):
            self.isPawnPromotion = True

        # en passant
        self.isEnpassantMove = is_enpassant_move
        if is_enpassant_move:
             self.pieceCaptured = "P-b" if self.pieceMoved == "P-w" else "P-w"

        # castle move
        self.isCastleMove = is_castle_move

        self.isCapture = self.pieceCaptured != "---"

        self.is_check = is_check
        self.is_checkmate = is_checkmate

        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol


    '''
    Overriding the equals method
    '''
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False
    def get_chess_notation(self):
        return self.get_rank_tile(self.startRow, self.startCol) + self.get_rank_tile(self.endRow, self.endCol)

    def get_rank_tile(self, r, c):
        return self.colsToTiles[c] + self.rowsToRanks[r]

    # override the  str() function
    def __str__(self):
        # castle move
        if self.isCastleMove:
            return "O-O" if self.endCol == 6 else "O-O-O"
            #"O-O" # kingside castle
            #"O-O-O" # queenside castle

        end_square = self.get_rank_tile(self.endRow, self.endCol)

        # pawn moves
        if self.pieceMoved[0] == 'P':
            if self.isCapture:
                return self.colsToTiles[self.startCol] + "x" + end_square
            else:
                return end_square

        # pawn promotion
        if self.isPawnPromotion:
            return self.colsToTiles[self.startCol] + "x" + end_square


        move_string = self.pieceMoved[0]
        same_type_pieces = self.get_same_type_pieces(self.pieceMoved[0])
        if len(same_type_pieces) > 1:
            move_string += self.get_disambiguation_string(same_type_pieces)
        if self.isCapture:
            move_string += "x"
        move_string += end_square



        if self.is_check:
            move_string += "+"
        elif self.is_checkmate:
            return self.colsToTiles[self.startCol] + "#" + end_square

        return move_string

    def get_rank_file(self, r, c):
        return self.colsToTiles[c] + self.rowsToRanks[r]

    def get_same_type_pieces(self, piece_type):
        same_type_pieces = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                if self.board[r, c][0] == piece_type and (r, c) != (self.startRow, self.startCol):
                    same_type_pieces.append((r, c))
        return same_type_pieces

    def get_disambiguation_string(self, same_type_pieces):
        disambiguation_string = ""
        for piece in same_type_pieces:
            if piece[1] == self.startCol:
                disambiguation_string += self.colsToTiles[self.startCol]
            else:
                disambiguation_string += self.rowsToRanks[self.startRow]
        return disambiguation_string