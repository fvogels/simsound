from simsound.intersections import HorizontalIntersection, VerticalIntersection, find_grid_intersections
from simsound.ray import Ray, Vector2
import itertools
import pytest


@pytest.mark.parametrize("x", range(-10, 10))
@pytest.mark.parametrize("y", range(-10, 10))
def test_intersections_horizontal_ray(x, y):
    ray = Ray(Vector2(x, y), Vector2(1, 0))
    intersections = find_grid_intersections(ray)
    for index, intersection in enumerate(itertools.islice(intersections, 10)):
        assert VerticalIntersection(index, x + index).approx(intersection)


@pytest.mark.parametrize("x", range(-10, 10))
@pytest.mark.parametrize("y", range(-10, 10))
def test_intersections_vertical_ray(x, y):
    ray = Ray(Vector2(x, y), Vector2(0, 1))
    intersections = find_grid_intersections(ray)
    for index, intersection in enumerate(itertools.islice(intersections, 10)):
        assert HorizontalIntersection(index, y + index).approx(intersection)


def test_intersections():
    ray = Ray(Vector2(0.5, 0.5), Vector2(4, 1))
    intersections = find_grid_intersections(ray)

    assert VerticalIntersection(0.125, 1) == next(intersections)
    assert VerticalIntersection(0.375, 2) == next(intersections)
    assert HorizontalIntersection(0.5, 1) == next(intersections)
    assert VerticalIntersection(0.625, 3) == next(intersections)
    assert VerticalIntersection(0.875, 4) == next(intersections)


def test_intersections_2():
    ray = Ray(Vector2(0.5, 0.5), Vector2(-4, -1))
    intersections = find_grid_intersections(ray)

    assert VerticalIntersection(0.125, 0) == next(intersections)
    assert VerticalIntersection(0.375, -1) == next(intersections)
    assert HorizontalIntersection(0.5, 0) == next(intersections)
    assert VerticalIntersection(0.625, -2) == next(intersections)