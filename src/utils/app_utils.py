def normalize_symbol(symbol: str) -> str:
    """Helper function to normalize symbol format for Kraken or other exchanges."""
    return f"{symbol[:3]}/{symbol[3:]}" if len(symbol) == 6 else symbol
