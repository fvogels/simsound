from typing import Iterable, Optional, Tuple
from simsound.intersections import Intersection, Direction, find_grid_intersections, Vector2, Ray
import math
from dataclasses import dataclass


@dataclass
class Position:
    x: int
    y: int

@dataclass
class Hit:
    position: Vector2
    reflection: float
    distance: float


class Grid:
    __grid: list[list[bool]]

    def __init__(self, width: int, height: int):
        self.__grid = [[False for _ in range(width)] for _ in range(height)]

    def __getitem__(self, pos: Position) -> bool:
        return self.__grid[pos.y][pos.x]

    def __setitem__(self, pos: Position, value: bool):
        self.__grid[pos.y][pos.x] = value

    @property
    def Width(self) -> int:
        return len(self.__grid[0])

    @property
    def Height(self) -> int:
        return len(self.__grid)

    def __contains_block(self, position: Position) -> bool:
        if 0 <= position.x < self.Width and 0 <= position.y < self.Height:
            return self[position]
        else:
            return False

    def __hits_horizontally(self, position: Vector2) -> bool:
        x = int(position.x)
        y = round(position.y)
        return self.__contains_block(Position(x, y-1)) or self.__contains_block(Position(x, y))

    def __hits_vertically(self, position: Vector2) -> bool:
        x = round(position.x)
        y = int(position.y)
        return self.__contains_block(Position(x-1, y)) or self.__contains_block(Position(x, y))

    def __outside_grid(self, position: Vector2) -> bool:
        return not self.__inside_grid(position)

    def __inside_grid(self, position: Vector2) -> bool:
        return 0 <= position.x <= self.Width and 0 <= position.y <= self.Height

    def __on_horizontal_border(self, position: Vector2) -> bool:
        return round(position.y) == 0 or round(position.y) == self.Height

    def __on_vertical_border(self, position: Vector2) -> bool:
        return round(position.x) == 0 or round(position.x) == self.Width

    def find_hits(self, ray: Ray) -> Iterable[Hit]:
        for intersection in find_grid_intersections(ray):
            position = ray.at(intersection.distance)
            if intersection.direction == Direction.HORIZONTAL:
                if self.__on_horizontal_border(position):
                    break

                above_position = Position(math.floor(position.x), round(position.y) - 1)
                below_position = Position(math.floor(position.x), round(position.y))

                if ray.direction.y > 0:
                    exited_block = self.__contains_block(above_position)
                    entered_block = self.__contains_block(below_position)
                else:
                    exited_block = self.__contains_block(below_position)
                    entered_block = self.__contains_block(above_position)

                if not exited_block and entered_block:
                    yield Hit(position, 1, intersection.distance)
            else:
                if self.__on_vertical_border(position):
                    break

                left_position = Position(round(position.x) - 1, math.floor(position.y))
                right_position = Position(round(position.x), math.floor(position.y))

                if ray.direction.x > 0:
                    exited_block = self.__contains_block(left_position)
                    entered_block = self.__contains_block(right_position)
                else:
                    exited_block = self.__contains_block(right_position)
                    entered_block = self.__contains_block(left_position)

                if not exited_block and entered_block:
                    yield Hit(position, 1, intersection.distance)


    def find_hit(self, ray: Ray, minimum_distance: float = 0.01) -> Optional[Hit]:
        for hit in self.find_hits(ray):
            if hit.distance > minimum_distance:
                return hit
        return None

    def no_obstacles_between(self, start: Vector2, stop: Vector2) -> bool:
        ray = Ray(start, stop - start)
        for hit in self.find_hits(ray):
            if hit.distance < 1:
                return False
            else:
                return True
        return True
