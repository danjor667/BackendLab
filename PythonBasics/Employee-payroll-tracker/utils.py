"""helper functions"""


def format_currency(amount, symbol="$"):
    """Format a number as a currency string, e.g. 1234.5 -> '$1,234.50'."""
    return f"{symbol}{amount:,.2f}"


def format_percent(rate):
    """Format a 0..1 rate as a percentage string, e.g. 0.2 -> '20.0%'."""
    return f"{rate * 100:.1f}%"
