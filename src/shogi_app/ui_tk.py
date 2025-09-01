"""Tkinter based user interface for the shogi game."""

from __future__ import annotations

import tkinter as tk
from functools import partial
from tkinter import filedialog, messagebox
from typing import Optional

import shogi

from .logic import ShogiGame

SQUARE_SIZE = 60
BOARD_SIZE = SQUARE_SIZE * 9
PIECE_SYMBOLS = {
    shogi.PAWN: "歩",
    shogi.LANCE: "香",
    shogi.KNIGHT: "桂",
    shogi.SILVER: "銀",
    shogi.GOLD: "金",
    shogi.BISHOP: "角",
    shogi.ROOK: "飛",
    shogi.KING: "王",
    shogi.PRO_PAWN: "と",
    shogi.PRO_LANCE: "成香",
    shogi.PRO_KNIGHT: "成桂",
    shogi.PRO_SILVER: "成銀",
    shogi.HORSE: "馬",
    shogi.DRAGON: "龍",
}


class ShogiUI:
    """Tkinter based UI to interact with :class:`ShogiGame`."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.game = ShogiGame()
        self.selected_square: Optional[int] = None
        self.drop_piece_type: Optional[int] = None

        self.root.title("Shogi App")
        self._build_menu()

        self.top_hand = tk.Frame(root)
        self.top_hand.pack()
        self.canvas = tk.Canvas(
            root, width=BOARD_SIZE, height=BOARD_SIZE, bg="saddlebrown"
        )
        self.canvas.pack()
        self.bottom_hand = tk.Frame(root)
        self.bottom_hand.pack()
        self.info = tk.Label(root, text="Turn: Black")
        self.info.pack()

        self.canvas.bind("<Button-1>", self.on_board_click)
        self.draw_board()
        self.update_hands()

    # Menu -----------------------------------------------------------------
    def _build_menu(self) -> None:
        menu = tk.Menu(self.root)
        file_menu = tk.Menu(menu, tearoff=0)
        file_menu.add_command(label="Save SFEN", command=self.save_sfen)
        file_menu.add_command(label="Load SFEN", command=self.load_sfen)
        file_menu.add_command(label="Save KIF", command=self.save_kif)
        file_menu.add_command(label="Load KIF", command=self.load_kif)
        file_menu.add_command(label="Save CSA", command=self.save_csa)
        file_menu.add_command(label="Load CSA", command=self.load_csa)
        menu.add_cascade(label="File", menu=file_menu)
        self.root.config(menu=menu)

    # Board ----------------------------------------------------------------
    def draw_board(self) -> None:
        self.canvas.delete("all")
        for sq in shogi.SQUARES:
            file = shogi.square_file(sq)
            rank = shogi.square_rank(sq)
            x1 = file * SQUARE_SIZE
            y1 = (8 - rank) * SQUARE_SIZE
            x2 = x1 + SQUARE_SIZE
            y2 = y1 + SQUARE_SIZE
            color = "burlywood" if (file + rank) % 2 == 0 else "#DEB887"
            self.canvas.create_rectangle(x1, y1, x2, y2, fill=color)
            piece = self.game.board.piece_at(sq)
            if piece:
                text = PIECE_SYMBOLS.get(piece.piece_type, piece.symbol().upper())
                if piece.color == shogi.WHITE:
                    text = text[::-1] if len(text) > 1 else text
                    fill = "red"
                else:
                    fill = "black"
                self.canvas.create_text(
                    x1 + SQUARE_SIZE / 2,
                    y1 + SQUARE_SIZE / 2,
                    text=text,
                    font=("TakaoPGothic", 20),
                    tags="piece",
                    fill=fill,
                )

        if self.selected_square is not None:
            for opt in self.game.legal_moves_from(self.selected_square):
                file = shogi.square_file(opt.move.to_square)
                rank = shogi.square_rank(opt.move.to_square)
                x1 = file * SQUARE_SIZE
                y1 = (8 - rank) * SQUARE_SIZE
                x2 = x1 + SQUARE_SIZE
                y2 = y1 + SQUARE_SIZE
                self.canvas.create_rectangle(
                    x1,
                    y1,
                    x2,
                    y2,
                    outline="blue",
                    width=3,
                    tags="highlight",
                )

    def on_board_click(self, event: tk.Event[tk.Canvas]) -> None:
        file = int(event.x // SQUARE_SIZE)
        rank = 8 - int(event.y // SQUARE_SIZE)
        square = shogi.square(file, rank)
        piece = self.game.board.piece_at(square)

        if self.drop_piece_type is not None:
            symbol = shogi.PIECE_SYMBOLS[self.drop_piece_type]
            move = shogi.Move.from_usi(f"{symbol}*{shogi.SQUARE_NAMES[square]}")
            if move in self.game.board.legal_moves:
                self.game.push(move)
                self.drop_piece_type = None
                self.after_move()
            return

        if self.selected_square is None:
            if piece and piece.color == self.game.board.turn:
                self.selected_square = square
                self.draw_board()
            return

        if square == self.selected_square:
            self.selected_square = None
            self.draw_board()
            return

        moves = [
            m
            for m in self.game.board.legal_moves
            if m.from_square == self.selected_square and m.to_square == square
        ]
        if not moves:
            self.selected_square = None
            self.draw_board()
            return
        if len(moves) == 1:
            self.game.push(moves[0])
        else:
            if messagebox.askyesno("Promotion", "Promote?"):
                move = [m for m in moves if m.promotion][0]
            else:
                move = [m for m in moves if not m.promotion][0]
            self.game.push(move)
        self.selected_square = None
        self.after_move()

    def after_move(self) -> None:
        if self.game.is_checkmate():
            messagebox.showinfo("Game Over", "Checkmate")
        elif self.game.is_repetition():
            messagebox.showinfo("Game Over", "Repetition")
        self.draw_board()
        self.update_hands()
        turn = "Black" if self.game.board.turn == shogi.BLACK else "White"
        self.info.config(text=f"Turn: {turn}")

    # Hands ---------------------------------------------------------------
    def update_hands(self) -> None:
        for frame, color in (
            (self.top_hand, shogi.WHITE),
            (self.bottom_hand, shogi.BLACK),
        ):
            for widget in frame.winfo_children():
                widget.destroy()
            pieces = self.game.pieces_in_hand(color)
            for pt, count in pieces.items():
                txt = f"{PIECE_SYMBOLS.get(pt, '?')}x{count}"
                btn = tk.Button(frame, text=txt, command=partial(self.select_drop, pt))
                btn.pack(side=tk.LEFT)

    def select_drop(self, piece_type: int) -> None:
        self.drop_piece_type = piece_type
        self.selected_square = None
        self.draw_board()

    # File operations -----------------------------------------------------
    def save_sfen(self) -> None:
        path = filedialog.asksaveasfilename(defaultextension=".sfen")
        if path:
            self.game.save_sfen(path)

    def load_sfen(self) -> None:
        path = filedialog.askopenfilename(filetypes=[("SFEN", "*.sfen"), ("All", "*")])
        if path:
            self.game.load_sfen(path)
            self.after_move()

    def save_kif(self) -> None:
        path = filedialog.asksaveasfilename(defaultextension=".kif")
        if path:
            self.game.save_kif(path)

    def load_kif(self) -> None:
        path = filedialog.askopenfilename(filetypes=[("KIF", "*.kif"), ("All", "*")])
        if path:
            self.game.load_kif(path)
            self.after_move()

    def save_csa(self) -> None:
        path = filedialog.asksaveasfilename(defaultextension=".csa")
        if path:
            self.game.save_csa(path)

    def load_csa(self) -> None:
        path = filedialog.askopenfilename(filetypes=[("CSA", "*.csa"), ("All", "*")])
        if path:
            self.game.load_csa(path)
            self.after_move()
