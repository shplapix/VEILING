from typing import TYPE_CHECKING

from app.scripts.seed_data import ARCHIVE_EXHIBITS, ArchiveExhibit, SeedImageSpec

if TYPE_CHECKING:
    from app.scripts.seed import run_seed, seed_archive_lots, seed_users

__all__ = [
    "ARCHIVE_EXHIBITS",
    "ArchiveExhibit",
    "SeedImageSpec",
    "run_seed",
    "seed_archive_lots",
    "seed_users",
]


def __getattr__(name: str) -> object:
    if name in ("run_seed", "seed_archive_lots", "seed_users"):
        import app.scripts.seed as seed_mod

        return getattr(seed_mod, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
