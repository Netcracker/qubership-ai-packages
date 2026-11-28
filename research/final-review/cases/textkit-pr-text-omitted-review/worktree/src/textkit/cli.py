"""The ``textkit-pages`` command: print how many pages a count of items takes."""

import sys

from textkit.paginate import page_count


def main(argv=None):
    """Print ``page_count(total, per_page)`` for the two integers on the command line."""
    args = sys.argv[1:] if argv is None else argv
    total, per_page = (int(a) for a in args)
    print(page_count(total, per_page))
    return 0
