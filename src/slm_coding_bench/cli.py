"""Command-line interface for slm-coding-bench.

Fleshed out in a later build phase; this module always exposes a Typer `app` so the
`slm-bench` entry point resolves.
"""

from __future__ import annotations

import typer

app = typer.Typer(
    add_completion=False,
    help="slm-coding-bench — a small, high-signal coding benchmark for (small) LLMs.",
)


@app.callback()
def _main() -> None:
    """slm-coding-bench."""


if __name__ == "__main__":
    app()
