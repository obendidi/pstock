import logging
import typing as tp
from functools import lru_cache

try:
    from rich.logging import RichHandler
except ImportError:
    RichHandler = logging.StreamHandler  # type: ignore


@lru_cache
def setup_logging(level: tp.Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "DEBUG"):
    logging.basicConfig(
        level=level, format="%(message)s", datefmt="[%X]", handlers=[RichHandler()]
    )
