from __future__ import annotations
from typing import Any, Iterable
from simsound.ray import Ray
from pygame.math import Vector2
import enum
import math


class Direction(enum.Enum):
    HORIZONTAL = 0
    VERTICAL = 1


class Intersection:
    __distance: float
    __direction: Direction

    def __init__(self, distance: float, direction: Direction):
        self.__distance = distance
        self.__direction = direction

    @property
    def distance(self) -> float:
        return self.__distance

    @property
    def direction(self) -> Direction:
        return self.__direction

    def approx(self, other: Intersection) -> bool:
        return math.isclose(self.distance, other.distance, abs_tol=0.001) and self.direction is other.direction

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Intersection):
            return NotImplemented
        return self.approx(other)

    def __str__(self) -> str:
        return f"Intersection(distance={self.distance}, direction={self.direction})"

    def __repr__(self) -> str:
        return f"Intersection({self.distance}, {self.direction})"


def find_grid_intersections(ray: Ray) -> Iterable[Intersection]:
    ht: float
    dht: float
    vt: float
    dvt: float

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
            yield Intersection(ht, Direction.VERTICAL)
            ht += dht
        else:
            yield Intersection(vt, Direction.HORIZONTAL)
            vt += dvt