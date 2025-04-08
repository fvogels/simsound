from __future__ import annotations
from typing import Any, Iterable
from simsound.ray import Ray
from pygame.math import Vector2
import enum
import math


class Intersection:
    __distance: float

    def __init__(self, distance: float):
        self.__distance = distance

    @property
    def distance(self) -> float:
        return self.__distance


class VerticalIntersection(Intersection):
    __x: int

    def __init__(self, distance: float, x: int):
        super().__init__(distance)
        self.__x = x

    @property
    def x(self) -> int:
        return self.__x

    def __str__(self) -> str:
        return f"VerticalIntersection(distance={self.distance})"

    def __repr__(self) -> str:
        return f"VerticalIntersection({self.distance}, {self.x})"

    def approx(self, other: VerticalIntersection) -> bool:
        return math.isclose(self.distance, other.distance, abs_tol=0.001) and self.x == other.x

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, VerticalIntersection):
            return NotImplemented
        return self.approx(other)


class HorizontalIntersection(Intersection):
    __y: int

    def __init__(self, distance: float, y: int):
        super().__init__(distance)
        self.__y = y

    @property
    def y(self) -> int:
        return self.__y

    def __str__(self) -> str:
        return f"HorizontalIntersection(distance={self.distance})"

    def __repr__(self) -> str:
        return f"HorizontalIntersection({self.distance}, {self.y})"

    def approx(self, other: HorizontalIntersection) -> bool:
        return math.isclose(self.distance, other.distance, abs_tol=0.001) and self.y == other.y

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, HorizontalIntersection):
            return NotImplemented
        return self.approx(other)


def find_grid_intersections(ray: Ray) -> Iterable[Intersection]:
    ht: float
    dht: float
    vt: float
    dvt: float

    x = math.floor(ray.origin.x) if ray.direction.x < 0 else math.ceil(ray.origin.x)
    y = math.floor(ray.origin.y) if ray.direction.y < 0 else math.ceil(ray.origin.y)
    dx = 1 if ray.direction.x > 0 else -1
    dy = 1 if ray.direction.y > 0 else -1

    if ray.direction.x == 0:
        ht = float('inf')
        dht = float('inf')
    else:
        target_x = math.ceil(ray.origin.x) if ray.direction.x > 0 else math.floor(ray.origin.x)
        ht = (target_x - ray.origin.x) / ray.direction.x
        dht = abs(1 / ray.direction.x)

    if ray.direction.y == 0:
        vt = float('inf')
        dvt = float('inf')
    else:
        target_y = math.ceil(ray.origin.y) if ray.direction.y > 0 else math.floor(ray.origin.y)
        vt = (target_y - ray.origin.y) / ray.direction.y
        dvt = abs(1 / ray.direction.y)

    while True:
        if ht < vt:
            yield VerticalIntersection(ht, x)
            x += dx
            ht += dht
        else:
            yield HorizontalIntersection(vt, y)
            y += dy
            vt += dvt
