import pytest

from cmn import polynomial


@pytest.mark.parametrize(
    'args, x, expected',
    (
            ((4.0, 2.0, 1.0), 8.0, 4.0 + 2.0 * 8.0 + 1.0 * 8.0 ** 2),
    )
)
def test_polynomial_evaluate(args, x, expected):
    poly = polynomial.Polynomial(args)
    result = poly.evaluate(x)
    assert result == expected


@pytest.mark.parametrize(
    'args, expected',
    (
            ((8.0, 4.0, 2.0), [4.0, 4.0]),
    )
)
def test_polynomial_derivative_polynomial(args, expected):
    poly = polynomial.Polynomial(args)
    d_poly = poly.derivative_polynomial()
    assert d_poly.coefficients == expected


@pytest.mark.parametrize(
    'args, offset, expected',
    (
            ((8.0, 4.0, 3.0), 12.0, [12.0, 8.0, 2.0, 1.0]),
    )
)
def test_polynomial_integral_polynomial(args, offset, expected):
    poly = polynomial.Polynomial(args)
    d_poly = poly.integral_polynomial(offset)
    assert d_poly.coefficients == expected
