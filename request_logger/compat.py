# TypeAlias in 3.10 only
try:
    from typing import TypeAlias
except ImportError:
    from typing_extensions import TypeAlias

__all__ = ["TypeAlias"]
