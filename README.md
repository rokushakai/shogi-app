# Shogi App

Simple local two-player shogi application built with Tkinter and [python-shogi](https://github.com/niklasf/python-shogi).

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
make run
```

## Test

```bash
make test
```

## Usage

- Click a piece to see its legal moves.
- Click a highlighted square to move.
- Captured pieces appear above/below the board; click one and then a square to drop.
- Promotion is prompted when applicable.
- Positions can be saved/loaded in SFEN, KIF, or CSA formats from the *File* menu.

## License

[MIT](LICENSE)
