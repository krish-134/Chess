"""
Main driver file. Responsible for handling user input and displaying current GameState object
"""

import pygame as p
from Chess import ChessEngine, ChessAI
from multiprocessing import Process, Queue
from tkinter import *

BOARD_WIDTH = BOARD_HEIGHT = 512
MOVE_LOG_PANEL_WIDTH = 250
MOVE_LOG_PANEL_HEIGHT = BOARD_HEIGHT
DIMENSION = 8
SQ_SIZE = BOARD_HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}
COLOURS = (p.Color("grey"), p.Color("steel blue"))

'''
Initialize a global dictionary of images. This will be called exactly once in the main
'''

def load_images():
    pieces = ['B-b', 'K-b', 'N-b', 'P-b', 'Q-b', 'R-b', 'B-w', 'K-w', 'N-w', 'P-w', 'Q-w', 'R-w']
    for piece in pieces:

        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".svg"), (SQ_SIZE * 2.7, SQ_SIZE * 2.7))

'''
Main driver for our code. This will handle user input and updating graphics
'''
def main():
    def choose_mode():
        window = Tk()
        window.title("Choose Game Mode")
        window.geometry("300x200")

        def set_mode(mode):
            nonlocal player_one, player_two, no_choice_made
            if mode == "1": # player vs player
                player_one = True # If a person is playing white, then this is True. If a bot is playing, then false
                player_two = True # same as above for black
            elif mode == "2": # player vs computer
                player_one = True
                player_two = False
            elif mode == "3": # computer vs player
                player_one = False
                player_two = True
            elif mode == "4": # computer vs computer
                player_one = False
                player_two = False
            no_choice_made = False
            window.destroy()

        Label(window, text="Select Game Mode").pack(pady=10)
        Button(window, text="Player vs Player", command=lambda: set_mode("1")).pack(pady=5)
        Button(window, text="Player vs Computer", command=lambda: set_mode("2")).pack(pady=5)
        Button(window, text="Computer vs Player", command=lambda: set_mode("3")).pack(pady=5)
        Button(window, text="Computer vs Computer", command=lambda: set_mode("4")).pack(pady=5)

        window.mainloop()

    p.init()
    screen = p.display.set_mode((BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    move_log_font = p.font.SysFont("Arial", 14, False, False)
    gs = ChessEngine.GameState()
    validMoves = gs.get_valid_moves()
    moveMade = False # flag variable for when move is made
    animate = False # flag variable for when we should animate
    load_images() # only do this once before while loop

    player_one = True
    player_two = True
    no_choice_made = True
    choose_mode()

    running = True
    sq_selected = () # no square is selected, keep track of the last click of user
    player_clicks = [] # keep track of player clicks

    game_over = False
    ai_thinking = False
    chess_ai_process = None
    move_undone = False

    while no_choice_made:
        pass

    while running:
        human_turn = (gs.white_to_move and player_one) or (not gs.white_to_move and player_two)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            # mouse handler
            elif e.type == p.MOUSEBUTTONDOWN:
                if not game_over:
                    location = p.mouse.get_pos()
                    row = location[1] // SQ_SIZE
                    col = location[0] // SQ_SIZE
                    if sq_selected == (row, col) or col >= 8:
                        sq_selected = () # deselect
                        player_clicks = [] # clear player clicks
                    else:
                        sq_selected = (row, col)
                        player_clicks.append(sq_selected)
                    if len(player_clicks) == 2 and human_turn:
                        move = ChessEngine.Move(player_clicks[0], player_clicks[1], gs.board)
                        print(move.get_chess_notation())

                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gs.make_move(validMoves[i])
                                moveMade = True
                                animate = True
                                sq_selected = ()
                                player_clicks = []
                        if not moveMade:
                            player_clicks = [sq_selected]

            #key handlers
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z: #undo when 'z' is pressed
                    gs.undo_move()
                    moveMade = True
                    animate = False
                    game_over = False
                    if ai_thinking:
                         chess_ai_process.terminate()
                         ai_thinking = False
                    move_undone = True
                if e.key == p.K_r: # reset the board when 'r' is pressed
                    gs = ChessEngine.GameState()
                    validMoves = gs.get_valid_moves()
                    sq_selected = ()
                    player_clicks = []
                    moveMade = False
                    animate = False
                    game_over = False
                    # if ai_thinking:
                    #     move_finder_process.terminate()
                    #     ai_thinking = False
                    move_undone = True

        #AI move finder
        if not game_over and not human_turn and not move_undone:
            if not ai_thinking:
                ai_thinking = True
                return_queue = Queue()
                chess_ai_process = Process(target=ChessAI.find_best_move, args=(gs, validMoves, return_queue))
                chess_ai_process.start() # call find_best_move(gs, valid_moves, return_queue)
            if not chess_ai_process.is_alive():
                ai_move = return_queue.get()
                #ai_move = ChessAI.find_best_move(gs, validMoves)
                if ai_move is None:
                    ai_move = ChessAI.find_random_move(validMoves)
                gs.make_move(ai_move)
                moveMade = True
                animate = True
                ai_thinking = False
                print("Done thinking")


        if moveMade:
            if animate:
                animate_move(gs.moveLog[-1], screen, gs.board, clock)
            validMoves = gs.get_valid_moves()
            moveMade = False
            animate = False
            move_undone = False

        draw_game_state(screen, gs, validMoves, sq_selected, move_log_font)

        if gs.checkmate:
            game_over = True
            if gs.stalemate:
                text = 'Stalemate'
            else:
                if gs.white_to_move:
                    text = 'Black wins by checkmate'
                else:
                    text = 'White wins by checkmate'

            draw_end_game_text(screen, text)

        clock.tick(MAX_FPS)
        p.display.flip()



'''
Highlight square selcted and moves for piece selected
'''
def highlight_squares(screen, gs, validMoves, sq_selected):
    if sq_selected != ():
        r, c = sq_selected
        if gs.board[r][c][2] == ('w' if gs.white_to_move else 'b'): # sqSelected is a piece that can be moved
            # highlight selected squares
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100) # transparency value
            s.fill(p.Color('crimson'))
            screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))
            # highlight moves from that square
            s.fill(p.Color('yellow'))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (move.endCol * SQ_SIZE, move.endRow * SQ_SIZE))


'''
Responsible for all graphics within a current game state
'''
def draw_game_state(screen, gs, validMoves, sq_selected, move_log_font):
    draw_board(screen)
    highlight_squares(screen, gs, validMoves, sq_selected)
    draw_pieces(screen, gs.board)
    draw_move_log(screen, gs, move_log_font)


'''
Draw the squares on the board
'''
def draw_board(screen):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            colour = COLOURS[((r + c) % 2)]
            p.draw.rect(screen, colour, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


'''
Draw the pieces on the board
'''
def draw_pieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "---": # not empty square
                screen.blit(IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))

'''
Draws move log
'''
def draw_move_log(screen, gs, font):

    move_log_rect = p.Rect(BOARD_WIDTH, 0, MOVE_LOG_PANEL_WIDTH, MOVE_LOG_PANEL_HEIGHT)
    p.draw.rect(screen, p.Color("black"), move_log_rect)
    move_log = gs.moveLog
    move_texts = []
    for i in range(0, len(move_log), 2):
        move_string = str(i // 2) + ". " + str(move_log[i]) + " "
        if i + 1 < len(move_log): # make sure black made a move
            move_string += str(move_log[i + 1]) + "  "
        move_texts.append(move_string)
    moves_per_row = 3
    padding = 5
    line_spacing = 2
    text_y = padding
    for i in range(0, len(move_texts), moves_per_row):
        text = ""
        for j in range(moves_per_row):
            if i + j < len(move_texts):
                text += move_texts[i + j]
        textObject = font.render(text, True, p.Color('white'))
        textLocation = move_log_rect.move(padding, text_y)
        screen.blit(textObject, textLocation)
        text_y += textObject.get_height() + line_spacing


'''
Animating a move
'''
def animate_move(move, screen, board, clock):
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framesPerSq = 10 # frames to move one square
    frameCount = (abs(dR) + abs(dC)) * framesPerSq
    for frame in range(frameCount + 1):
        r, c = (move.startRow + dR * frame / frameCount, move.startCol + dC * frame / frameCount)
        draw_board(screen)
        draw_pieces(screen, board)

        colour = COLOURS[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(move.endCol * SQ_SIZE, move.endRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, colour, endSquare)

        if move.pieceCaptured != "---":
            if move.isEnpassantMove:
                enPassantRow = move.endRow - 1 if move.pieceMoved[2] == 'b' else move.endRow + 1
                endSquare = p.Rect(move.endCol * SQ_SIZE, enPassantRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
            screen.blit(IMAGES[move.pieceCaptured], endSquare)

        # draw captured piece onto rectangle
        if move.pieceCaptured != "---":
            screen.blit(IMAGES[move.pieceCaptured], endSquare)
        # draw moving piece
        screen.blit(IMAGES[move.pieceMoved], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)


def draw_end_game_text(screen, text):
    font = p.font.SysFont("Helvitca", 32, True, False)
    textObject = font.render(text, 0, p.Color('Gray'))
    textLocation = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(BOARD_WIDTH / 2 - textObject.get_width() / 2, BOARD_HEIGHT / 2 - textObject.get_height() / 2)
    screen.blit(textObject, textLocation)
    textObject = font.render(text, 0, p.Color('Black'))
    screen.blit(textObject, textLocation.move(2, 2))

if __name__ == "__main__":
    main()