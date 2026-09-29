def test_string():
    assert "Hello world" == "Hello, world"


def test_list():
    assert [1, 2, 3] == [1, 2, 4]


def test_dict():
    assert {"a": 1, "b": 2} == {"a": 1, "b": 3}


def test_set():
    assert {1, 2, 3} == {1, 2, 4}


def test_long_list():
    assert list(range(20)) == [*range(19), 99]
