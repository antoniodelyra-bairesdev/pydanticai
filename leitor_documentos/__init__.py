# Import base classes and ensure extractors are registered
from .base import DocumentExtractor
from .impl import *  # This will import all extractors and register them

__all__ = [
    "DocumentExtractor",
]
