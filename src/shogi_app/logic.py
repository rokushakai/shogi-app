"""Game logic built on python-shogi."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, cast

import shogi
import shogi.CSA
import shogi.KIF


@dataclass
class MoveOption:
    """A legal move with optional promotion flag."""

    move: shogi.Move
    promotion: bool


class ShogiGame:
    """Wrapper around :class:`shogi.Board` to manage game state."""

    def __init__(self, sfen: str | None = None) -> None:
        self.board = shogi.Board(sfen) if sfen else shogi.Board()

    def legal_moves_from(self, square: int) -> List[MoveOption]:
        """Return legal moves originating from ``square``."""

        return [
            MoveOption(move=m, promotion=m.promotion)
            for m in self.board.legal_moves
            if m.from_square == square
        ]

    def push(self, move: shogi.Move) -> None:
        """Push ``move`` onto the board."""

        self.board.push(move)

    def push_usi(self, usi: str) -> bool:
        """Push move described in USI notation if legal."""

        mv = shogi.Move.from_usi(usi)
        if mv in self.board.legal_moves:
            self.board.push(mv)
            return True
        return False

    def is_checkmate(self) -> bool:
        """Return ``True`` if the side to move is checkmated."""

        return bool(self.board.is_checkmate())

    def is_repetition(self) -> bool:
        """Return ``True`` if the position is fourfold repetition."""

        return bool(self.board.is_fourfold_repetition())

    def sfen(self) -> str:
        """Return current position in SFEN."""

        return cast(str, self.board.sfen())

    def set_sfen(self, sfen: str) -> None:
        """Load position from SFEN string."""

        self.board.set_sfen(sfen)

    def save_sfen(self, path: str | Path) -> None:
        """Save current position to ``path`` in SFEN format."""

        Path(path).write_text(self.board.sfen(), encoding="utf8")

    def load_sfen(self, path: str | Path) -> None:
        """Load position from ``path`` in SFEN format."""

        sfen = Path(path).read_text(encoding="utf8").strip()
        self.board.set_sfen(sfen)

    def save_kif(self, path: str | Path) -> None:
        """Save current position to ``path`` in KIF format."""

        Path(path).write_text(self.board.kif_dump(), encoding="utf8")

    def load_kif(self, path: str | Path) -> None:
        """Load position from ``path`` in KIF format."""

        parser = shogi.KIF.Parser()
        records = parser.parse_file(Path(path))
        record = records[0]
        board = record["initial_position"]
        for mv in record["moves"]:
            board.push(mv["move"])
        self.board = board

    def save_csa(self, path: str | Path) -> None:
        """Save current position to ``path`` in CSA format."""

        Path(path).write_text(self.board.csa_dump(), encoding="utf8")

    def load_csa(self, path: str | Path) -> None:
        """Load position from ``path`` in CSA format."""

        parser = shogi.CSA.Parser()
        records = parser.parse_file(Path(path))
        record = records[0]
        board = record["initial_position"]
        for mv in record["moves"]:
            board.push(mv["move"])
        self.board = board

    def pieces_in_hand(self, color: shogi.Color) -> dict[int, int]:
        """Return pieces in hand for ``color``."""

        counts = self.board.pieces_in_hand[color]
        return {pt: counts[pt] for pt in range(1, len(counts)) if counts[pt]}
