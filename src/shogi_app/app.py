"""Entry point for running the Shogi application."""

import tkinter as tk

from .ui_tk import ShogiUI


def main() -> None:
    """Launch the Tkinter user interface."""

    root = tk.Tk()
    ShogiUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
