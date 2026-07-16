"""URL formatting utilities for display purposes."""


def shorten_url(url, max_length=30):
    """
    Shorten a URL for display by removing protocol, www, and truncating if needed.

    Rules applied in order:
    1. Remove https:// or http:// from the start
    2. Remove www. from the start
    3. Abbreviate with ... if longer than max_length characters

    Args:
        url: The URL string to shorten
        max_length: Maximum length before truncating (default: 30)

    Returns:
        Shortened URL string

    Examples:
        >>> shorten_url("https://www.example.com/path")
        'example.com/path'

        >>> shorten_url("https://accounts.google.com/very/long/path/that/exceeds/limit")
        'accounts.google.com/very/lon...'
    """
    if not url:
        return ""

    # Make a copy to work with
    shortened = url

    # Step 1: Remove https:// or http://
    if shortened.startswith("https://"):
        shortened = shortened[8:]  # Remove "https://"
    elif shortened.startswith("http://"):
        shortened = shortened[7:]  # Remove "http://"

    # Step 2: Remove www.
    if shortened.startswith("www."):
        shortened = shortened[4:]  # Remove "www."

    # Step 3: Truncate if longer than max_length
    if len(shortened) > max_length:
        shortened = shortened[: max_length - 3] + "..."

    return shortened
