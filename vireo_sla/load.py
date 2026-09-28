"""Locate and read the data pack."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

PACK_FILES = {
    "tickets": "tickets.csv",
    "agents": "agents.csv",
    "customers": "customers.csv",
    "orders": "orders.csv",
    "products": "products.csv",
}


def data_dir() -> Path:
    here = Path(__file__).resolve().parent.parent / "data"
    if (here / "tickets.csv").exists():
        return here
    cwd = Path.cwd() / "data"
    if (cwd / "tickets.csv").exists():
        return cwd
    raise FileNotFoundError(
        "Could not find data/tickets.csv. Run from the repo root after "
        "keeping the pack in the data/ folder. See README.md."
    )


def load_pack(root: Path | None = None) -> dict[str, pd.DataFrame]:
    folder = Path(root) if root is not None else data_dir()
    missing = [name for name, fname in PACK_FILES.items() if not (folder / fname).exists()]
    if missing:
        raise FileNotFoundError(f"Missing pack files in {folder}: {missing}")
    return {key: pd.read_csv(folder / fname) for key, fname in PACK_FILES.items()}
