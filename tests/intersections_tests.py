from simsound.intersections import Intersection, find_grid_intersections, Direction
from simsound.ray import Ray, Vector2
import itertools
import pytest


@pytest.mark.parametrize("y", range(-10, 10))
def test_intersections_horizontal_ray(y):
    ray = Ray(Vector2(0, y), Vector2(1, 0))
    intersections = find_grid_intersections(ray)
    for index, intersection in enumerate(itertools.islice(intersections, 10)):
        assert Intersection(index, Direction.VERTICAL).approx(intersection)


@pytest.mark.parametrize("x", range(-10, 10))
def test_intersections_vertical_ray(x):
    ray = Ray(Vector2(x, 0), Vector2(0, 1))
    intersections = find_grid_intersections(ray)
    for index, intersection in enumerate(itertools.islice(intersections, 10)):
        assert Intersection(index, Direction.HORIZONTAL).approx(intersection)


def test_intersections():
    ray = Ray(Vector2(0.5, 0.5), Vector2(4, 1))
    intersections = find_grid_intersections(ray)

    assert Intersection(0.125, Direction.VERTICAL) == next(intersections)
    assert Intersection(0.375, Direction.VERTICAL) == next(intersections)
    assert Intersection(0.5, Direction.HORIZONTAL) == next(intersections)
    assert Intersection(0.625, Direction.VERTICAL) == next(intersections)
    assert Intersection(0.875, Direction.VERTICAL) == next(intersections)


def test_intersections_2():
    ray = Ray(Vector2(0.5, 0.5), Vector2(-4, -1))
    intersections = find_grid_intersections(ray)

    assert Intersection(0.125, Direction.VERTICAL) == next(intersections)
    assert Intersection(0.375, Direction.VERTICAL) == next(intersections)
    assert Intersection(0.5, Direction.HORIZONTAL) == next(intersections)
    assert Intersection(0.625, Direction.VERTICAL) == next(intersections)