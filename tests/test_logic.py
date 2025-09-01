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
    game = ShogiGame("8k/9/9/9/9/9/9/9/K8 b - 1")
    for _ in range(4):
        assert game.push_usi("1i2i")
        assert game.push_usi("9a8a")
        assert game.push_usi("2i1i")
        assert game.push_usi("8a9a")
    assert game.is_repetition()
