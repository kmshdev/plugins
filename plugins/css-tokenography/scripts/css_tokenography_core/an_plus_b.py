"""CSS Syntax An+B parsing shared by selector-facing tools."""

from __future__ import annotations

import re


class AnPlusBError(ValueError):
    pass


CSS_WHITESPACE = frozenset(" \t\r\n\f")
_CSS_WS_PATTERN = r"[ \t\r\n\f]"
_ANB_RE = re.compile(
    rf"^{_CSS_WS_PATTERN}*(?:(?P<keyword>odd|even)|(?P<integer>[+-]?[0-9]+)|"
    rf"(?P<a>[+-]?(?:[0-9]+)?)n(?:{_CSS_WS_PATTERN}*(?P<b_sign>[+-])"
    rf"{_CSS_WS_PATTERN}*(?P<b_digits>[0-9]+))?){_CSS_WS_PATTERN}*$",
    re.IGNORECASE | re.ASCII,
)


def _canonical_expression(a_value: int, b_value: int) -> str:
    if a_value == 0:
        return str(b_value)
    if a_value == 1:
        expression = "n"
    elif a_value == -1:
        expression = "-n"
    else:
        expression = f"{a_value}n"
    if b_value > 0:
        return f"{expression}+{b_value}"
    if b_value < 0:
        return f"{expression}{b_value}"
    return expression


def parse_an_plus_b(value: object) -> dict[str, object]:
    """Parse CSS An+B without erasing token-significant whitespace."""

    if not isinstance(value, str):
        raise AnPlusBError("expression must be a string")
    match = _ANB_RE.fullmatch(value)
    if match is None:
        raise AnPlusBError("expression must be odd, even, an integer, or An+B")

    keyword = match.group("keyword")
    try:
        if keyword is not None:
            a_value, b_value = (2, 1) if keyword.lower() == "odd" else (2, 0)
        elif match.group("integer") is not None:
            a_value, b_value = 0, int(match.group("integer"))
        else:
            coefficient = match.group("a")
            if coefficient in (None, "", "+"):
                a_value = 1
            elif coefficient == "-":
                a_value = -1
            else:
                a_value = int(coefficient)
            digits = match.group("b_digits")
            b_value = 0 if digits is None else int(digits)
            if match.group("b_sign") == "-":
                b_value = -b_value
    except ValueError as error:
        raise AnPlusBError("expression contains an integer that is too large") from error

    return {
        "a": a_value,
        "b": b_value,
        "expression": _canonical_expression(a_value, b_value),
    }
