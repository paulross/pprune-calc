import typing


class Polynomial:
    def __init__(self, coefficients: typing.Sequence[float]):
        if len(coefficients) == 0:
            raise ValueError("Polynomial has no coefficients.")
        self.coefficients = coefficients[:]

    @property
    def degree(self) -> int:
        assert len(self.coefficients) > 0
        return len(self.coefficients) - 1

    def evaluate(self, x: float) -> float:
        """If f(x) = a + b * x + c * x**2 + d * x**3"""
        power = 0
        ret = 0.0
        for coefficient in self.coefficients:
            ret += (x ** power) * coefficient
            power += 1
        return ret

    def derivative_polynomial(self):
        """If f(x) = a + b * x + c * x**2 + d * x**3
        Then the Differential(f(x)) polynomial is b + 2.0 * c * x**1 + 3.0 * d * x**2"""
        mul = 1.0
        coefficients = []
        for coefficient in self.coefficients[1:]:
            coefficients.append(coefficient * mul)
            mul += 1.0
        return Polynomial(coefficients)

    def integral_polynomial(self, offset: float):
        """Given a polynomial f(x) = a + b * x + c * x**2 + d * x**3
        Then the integral is f(x) polynomial is offset + a * x + b * x**2 / 2 + c * x**3 / 3 + d * x**4 / 4
        """
        mul = 1.0
        coefficients = [offset]
        for coefficient in self.coefficients:
            coefficients.append(coefficient / mul)
            mul += 1.0
        return Polynomial(coefficients)

    def derivative(self, x: float) -> float:
        """Returns the derivative (slope) of the polynomial for the value x."""
        ret = 0.0
        for i in range(-1, -len(self.coefficients), -1):
            if i == -(len(self.coefficients) - 1):
                ret += self.coefficients[i]
                break
            ret += self.coefficients[i] * (len(self.coefficients) + i)
            ret *= x
        return ret

    def integral(self, x: float) -> float:
        """Returns the integral of the polynomial from 0 to x."""
        ret = 0.0
        for i in range(-1, -len(self.coefficients) - 1, -1):
            ret += self.coefficients[i] / (len(self.coefficients) + 1 + i)
            ret *= x
        return ret

    def integral_range(self, x: float, y: float) -> float:
        """Returns the integral of the polynomial from x to y."""
        zero_to_x = self.integral(x)
        zero_to_y = self.integral(y)
        return zero_to_y - zero_to_x

    def polynomial_string(self, name: str, x: str, fmt: str) -> str:
        """Returns a string representation of the form:
        NAME(X) =  3.623e+00 +  8.862e+01 * X + -3.788e-01 * X**2 + -1.173e-02 * X**3 Value(0) =  3.623e+00
        """
        ret = [f'{name}({x}) =']
        for i, arg in enumerate(self.coefficients):
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


def polynomial_differential_factors(*args: typing.List[float]) -> typing.List[float]:
    """Returns the differential of the polynomial factors for the value x."""
    ret = []
    for i in range(1, len(args)):
        ret.append(args[i] * i)
    return ret


def polynomial_3(x, a, b, c, d):
    """Polynomial order 3 where f(x) = a + b * x + c * x**2 + d * x**3"""
    return polynomial(x, a, b, c, d)


def polynomial_3_integral(x, a, b, c, d):
    """Integral of polynomial order 3 where f(x) = a + b * x + c * x**2 + d * x**3.
    Integral(f(x)) 0 -> x = a * x + b * x**2 / 2 + c * x**3 / 3 + d * x**4 / 4

    Given a polynomial f(x) = a + b * x + c * x**2 + d * x**3
    Then the integral is f(x) = offset + a * x + b * x**2 / 2 + c * x**3 / 3 + d * x**4 / 4
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
