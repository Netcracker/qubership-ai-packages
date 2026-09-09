# pytest

What pytest prints, how its assertion rewriting changes the rules, and how a case is named. pytest is both the engine
and the assertion mechanism, so one file covers both roles. The rules that use it are in `SKILL.md` §7 and §8.

## What the runner prints

The progress line and the short summary carry the node id (`test_stream.py::TestEnsureBytes::test_negative_count`)
and the first line of the failure; the failure section prints the test's source with a `>` at the failing line, the
docstring included, then the `E` lines. The node id is the whole name the T1 reader sees first, so the module, the
class, and the function each carry their slot of §7.

## Which assertion prints the operands

pytest rewrites a bare `assert` so that the operands and the call that produced them are printed:

| Test line | `E` lines |
| --- | --- |
| `assert ensure_bytes(-1) == 0` | `assert -1 == 0` and `+  where -1 = ensure_bytes(-1)` |
| `ok = ensure_bytes(-1) == 0` then `assert ok` | `assert False` |
| `assert ensure_bytes(-1) == 0, "ensure_bytes(-1)"` | `AssertionError: ensure_bytes(-1)` above the same two lines |
| `pytest.fail()` | `Failed` |
| `with pytest.raises(ValueError): ensure_bytes(-1)` when nothing raises | `Failed: DID NOT RAISE ValueError` |

So the rule of §7 takes this shape here: **put the comparison in the `assert` statement.** A boolean computed one line
earlier prints `assert False` and nothing else. Strings, sequences, dicts, and sets get a diff. The message is the
second operand of `assert`, and it is printed above the introspection, never instead of it. There is no operand
order to keep; write the call on whichever side reads better.

The rewriting reaches only the test modules pytest collects. A bare `assert` in a helper module the test imports
raises a plain `AssertionError` with no operands, so a validation helper prints nothing the reader can use unless
the root `conftest.py` opts the module in with `pytest.register_assert_rewrite("helper")` before it is imported.

## Parameterized cases

`@pytest.mark.parametrize("n", [-1, -2])` names each case from the value (`test_param[-1]`); for a value with no
useful `repr`, or where the condition is the name, pass `ids=["minus one", "minus two"]` or `pytest.param(-1,
id="minus one")`. The id becomes the node id suffix, is printed in the `FAILED` line, and is selectable with `-k`. Two
cases with the same id are disambiguated by an index, which is a location.

## Grouping assertions

There is no soft assert in pytest itself; a test with several assertions on one result stops at the first. Where the
fields are independent, `pytest-check` or a parametrized test over the fields keeps them reporting together.

## Errors

`pytest.raises(ValueError, match=r"negative")` asserts the type and, with `match=`, a regular expression over the
message; match only the part the behavior defines. Assert on `excinfo.value` for a code or a cause.

## Order and flakiness

`pytest-randomly` shuffles modules, classes, and functions and prints `Using --randomly-seed=…`; replay with the
same flag. `pytest -p no:randomly` disables it for one run and is not a fix. Fix an order dependence by removing the
shared state: a module-level mutable, a class attribute a test writes, a fixture with `scope="session"` that a test
mutates.
