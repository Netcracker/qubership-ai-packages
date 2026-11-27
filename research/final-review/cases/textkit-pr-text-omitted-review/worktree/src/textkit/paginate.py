"""Splitting a sequence of items into fixed-size pages."""


def page_count(total, per_page):
    """Return the number of pages needed to show ``total`` items, ``per_page`` to a page.

    Raises ``ValueError`` if ``per_page`` is less than 1 or ``total`` is negative.
    """
    if per_page < 1:
        raise ValueError(f"per_page must be at least 1, got {per_page}")
    if total < 0:
        raise ValueError(f"total must not be negative, got {total}")
    return (total + per_page - 1) // per_page


def page(items, number, per_page):
    """Return the items on page ``number``, counting pages from 1.

    Returns an empty list for a page past the last one.
    """
    if number < 1:
        raise ValueError(f"number must be at least 1, got {number}")
    start = (number - 1) * per_page
    return list(items[start:start + per_page])


def page_range(number, per_page):
    """Return the indexes of the first and the last item on page ``number``, counting pages from 1.

    Raises ``ValueError`` if ``number`` is less than 1.
    """
    if number < 1:
        raise ValueError(f"number must be at least 1, got {number}")
    start = (number - 1) * per_page
    return start, start + per_page - 1
