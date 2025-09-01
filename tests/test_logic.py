from __future__ import annotations

from pathlib import Path

from shogi_app.logic import ShogiGame


def test_legal_moves() -> None:
    game = ShogiGame()
    assert len(list(game.board.legal_moves)) == 30


def test_sfen_io(tmp_path: Path) -> None:
    game = ShogiGame()
    assert game.push_usi("7g7f")
    path = tmp_path / "pos.sfen"
    game.save_sfen(path)
    game2 = ShogiGame()
    game2.load_sfen(path)
    assert game.sfen() == game2.sfen()


def test_repetition() -> None:
    game = ShogiGame("4K4/9/9/9/9/9/9/9/4k4 b - 1")
    seq = ["5i5h", "5a5b", "5h5i", "5b5a"] * 2
    for usi in seq:
        assert game.push_usi(usi)
    assert game.is_repetition() or game.board.is_repetition()
