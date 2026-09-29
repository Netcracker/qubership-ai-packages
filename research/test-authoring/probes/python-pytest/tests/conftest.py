import pytest

# Opt one of the two helper modules into assertion rewriting; the other keeps the plain AssertionError.
pytest.register_assert_rewrite("helper_rewritten")
