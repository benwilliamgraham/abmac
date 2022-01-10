"""abmac general test module."""

import pytest

from abmac import expand


@expand({"RETURN": "return 0"})
def macro_ret():
    RETURN


def lit_ret():
    return 0


C = 10


@expand({"COND": "return 0" if C % 3 else "return 1"})
def macro_cond():
    COND


def lit_cond():
    if C % 3:
        return 0
    else:
        return 1


@expand({"LOOP": "\n".join(f"i += {i + 1}" for i in range(5))})
def macro_loop():
    i = 7
    LOOP
    i += 1
    return i


def lit_loop():
    i = 7
    i += 1
    i += 2
    i += 3
    i += 4
    i += 5
    i += 1
    return i


@pytest.mark.parametrize(
    "macro_func,lit_func,args",
    [(macro_ret, lit_ret, []), (macro_cond, lit_cond, []), (macro_loop, lit_loop, []),],
)
def test_macro_funcs(macro_func, lit_func, args):
    """Test macro functions."""
    assert macro_func(*args) == lit_func(*args)


@expand({"EXCEPT": "raise Exception('test')"})
def err_runtime():
    a = 10
    EXCEPT
    return a


@pytest.mark.parametrize(
    "macro_func,args,err",
    [
        (err_runtime, [], r"test"),
    ],
)
def test_macro_funcs_err(macro_func, args, err):
    """Test macro functions."""
    with pytest.raises(Exception) as excinfo:
        macro_func(*args)
    assert str(excinfo.value) == err
