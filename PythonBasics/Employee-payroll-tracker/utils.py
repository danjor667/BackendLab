"""helper functions"""

def format_currency(amount, symbol="$"):
    """Format a number as a currency string, e.g. 1234.5 -> '$1,234.50'."""
    return f"{symbol}{amount:,.2f}"
