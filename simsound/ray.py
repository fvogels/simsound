from pygame.math import Vector2


class Ray:
    __origin: Vector2
    __direction: Vector2

    def __init__(self, origin: Vector2, direction: Vector2):
        self.__origin = origin
        self.__direction = direction

    @property
    def origin(self) -> Vector2:
        return self.__origin

    @property
    def direction(self) -> Vector2:
        return self.__direction

    def at(self, t: float) -> Vector2:
        return self.__origin + t * self.__direction
