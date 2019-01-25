from helpers import omit


def test_omit():
    d = {'a': 1, 'b': 2, 'c': 3, 'd': 4}
    assert omit(d, ['a', 'b']) == {'c': 3, 'd': 4}
