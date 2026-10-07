"""Performance adapters are imported explicitly by their consuming instrument.

Keeping this package initializer dependency-free prevents an optional adapter
from becoming a startup dependency for unrelated V3 performance sessions.
"""

__all__: list[str] = []
