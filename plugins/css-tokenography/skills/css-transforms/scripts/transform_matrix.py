"""Small dependency-free 4x4 matrix helpers for typed CSS transforms."""

from __future__ import annotations

import math
from typing import Sequence

Matrix = list[list[float]]


def identity() -> Matrix:
    return [[1.0 if row == column else 0.0 for column in range(4)] for row in range(4)]


def multiply(left: Matrix, right: Matrix) -> Matrix:
    return [[sum(left[row][k] * right[k][column] for k in range(4)) for column in range(4)] for row in range(4)]


def translate(x: float, y: float, z: float) -> Matrix:
    result = identity()
    result[0][3], result[1][3], result[2][3] = x, y, z
    return result


def scale(x: float, y: float, z: float) -> Matrix:
    result = identity()
    result[0][0], result[1][1], result[2][2] = x, y, z
    return result


def rotate_axis(x: float, y: float, z: float, angle: float) -> Matrix:
    length = math.sqrt(x * x + y * y + z * z)
    if length == 0:
        raise ValueError("rotate3d axis must not be the zero vector")
    x, y, z = x / length, y / length, z / length
    cosine, sine, inverse = math.cos(angle), math.sin(angle), 1 - math.cos(angle)
    return [
        [cosine + x*x*inverse, x*y*inverse - z*sine, x*z*inverse + y*sine, 0.0],
        [y*x*inverse + z*sine, cosine + y*y*inverse, y*z*inverse - x*sine, 0.0],
        [z*x*inverse - y*sine, z*y*inverse + x*sine, cosine + z*z*inverse, 0.0],
        [0.0, 0.0, 0.0, 1.0],
    ]


def skew(x_angle: float, y_angle: float) -> Matrix:
    result = identity()
    result[0][1], result[1][0] = math.tan(x_angle), math.tan(y_angle)
    return result


def perspective(distance: float) -> Matrix:
    result = identity()
    result[3][2] = -1.0 / distance
    return result


def from_matrix2d(values: Sequence[float]) -> Matrix:
    a, b, c, d, e, f = values
    return [[a, c, 0.0, e], [b, d, 0.0, f], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]]


def from_matrix3d(values: Sequence[float]) -> Matrix:
    return [[values[column * 4 + row] for column in range(4)] for row in range(4)]


def clean(matrix: Matrix) -> Matrix:
    return [[0.0 if abs(value) < 1e-12 else round(float(value), 12) for value in row] for row in matrix]
