from typing import Tuple
from simsound.intersections import Intersection, Direction, find_grid_intersections, Vector2, Ray


class Position:
    __x: int
    __y: int

    def __init__(self, x: int, y: int):
        self.__x = x
        self.__y = y

    @property
    def x(self) -> int:
        return self.__x

    @property
    def y(self) -> int:
        return self.__y


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

    def __on_horizontal_border(self, position: Vector2) -> bool:
        y = round(position.y)
        return y == 0 or y == self.Height

    def __on_vertical_border(self, position: Vector2) -> bool:
        x = round(position.x)
        return x == 0 or x == self.Width

    def find_hit(self, ray: Ray) -> Tuple[Vector2, bool]:
        for intersection in find_grid_intersections(ray):
            position = ray.at(intersection.distance)
            if intersection.direction == Direction.HORIZONTAL:
                if self.__hits_horizontally(position):
                    return position, True
                if self.__on_horizontal_border(position):
                    return position, False
            else:
                if self.__hits_vertically(position):
                    return position, True
                if self.__on_vertical_border(position):
                    return position, False
        raise ValueError("Should never happen")
