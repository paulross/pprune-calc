import typing


def polynomial(x: float, *args: typing.List[float]) -> float:
    """Returns the evaluation of the polynomial factors for the value x."""
    ret = 0.0
    for i in range(-1, -len(args) - 1, -1):
        ret += args[i]
        if i == -len(args):
            break
        ret *= x
    return ret


def polynomial_differential(x: float, *args: typing.List[float]) -> float:
    """Returns the differential of the polynomial factors for the value x."""
    ret = 0.0
    for i in range(-1, -len(args), -1):
        if i == -(len(args) - 1):
            ret += args[i]
            break
        ret += args[i] * (len(args) + i)
        ret *= x
    return ret


def polynomial_integral(x: float, *args: typing.List[float]) -> float:
    """Returns the integral of the polynomial factors from 0 to x."""
    ret = 0.0
    for i in range(-1, -len(args) - 1, -1):
        ret += args[i] / (len(args) + 1 + i)
        ret *= x
    return ret


def polynomial_3(x, a, b, c, d):
    """Polynomial order 3 where f(x) = a + b * x + c * x**2 + d * x**3"""
    return polynomial(x, a, b, c, d)


def polynomial_3_integral(x, a, b, c, d):
    """Integral of polynomial order 3 where f(x) = a + b * x + c * x**2 + d * x**3.
    Integral(f(x)) 0 -> x = a * x + b * x**2 / 2 + c * x**3 / 3 + d * x**4 / 4
    """
    return polynomial_integral(x, a, b, c, d)


def polynomial_3_differential(x, a, b, c, d):
    """Polynomial order 3 where f(x) = a + b * x + c * x**2 + d * x**3
    Differential(f(x) = b + 2.0 * c * x**1 + 3.0 * d * x**2
    """
    return polynomial_differential(x, a, b, c, d)


def polynomial_4(x, a, b, c, d, e):
    return polynomial(x, a, b, c, d, e)


def polynomial_4_integral(x, a, b, c, d, e):
    return polynomial_integral(x, a, b, c, d, e)


def polynomial_4_differential(x, a, b, c, d, e):
    return polynomial_differential(x, a, b, c, d, e)


def polynomial_string(name: str, x: str, fmt: str, *args) -> str:
    ret = [
        f'{name}({x}) ='
    ]
    for i, arg in enumerate(args):
        sub_str = []
        if i:
            sub_str.append('+')
        sub_str.append(f'{arg:{fmt}}')
        if i == 1:
            sub_str.append(f'* {x}')
        elif i > 1:
            sub_str.append(f'* {x}**{i:d}')
        ret.append(' '.join(sub_str))
    return ' '.join(ret)
