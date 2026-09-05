# fleet_utils.py
# Catch-all helpers since 2013. Cleaned up with IBM Bob.

KM_PER_MILE = 1.60934          # 1 mile = 1.60934 km; divide to convert km → miles


def km_to_miles(km: float) -> float:
    """Convert kilometres to miles."""
    return km / KM_PER_MILE


def format_number(value: float) -> str:
    """Format a number to one decimal place."""
    return f"{value:.1f}"


def format_percent(value: float) -> str:
    """Format a number as a whole-number percentage string."""
    return f"{int(value)}%"


def mean(values: list[float]) -> float:
    """Return the arithmetic mean of a list, or 0 for an empty list."""
    if not values:
        return 0
    return sum(values) / len(values)


def is_due(pct: float, threshold: float) -> bool:
    """Return True if pct is at or above threshold."""
    return pct >= threshold


def parse_service_date(text: str) -> tuple | None:
    """Parse a DD.MM.YYYY string into a (year, month, day) tuple, or None."""
    parts = text.split(".")
    if len(parts) != 3:
        return None
    day = int(parts[0])
    month = int(parts[1])
    year = int(parts[2])
    return (year, month, day)


def chunk_list(items: list, size: int) -> list[list]:
    """Split a list into chunks of at most `size` items each."""
    return [items[i:i + size] for i in range(0, len(items), size)]
