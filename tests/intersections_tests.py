from simsound.intersections import Intersection, find_grid_intersections, Direction
from simsound.ray import Ray, Vector2


def test_intersections_horizontal_ray():
    ray = Ray(Vector2(0, 0), Vector2(1, 0))
    intersections = find_grid_intersections(ray)

    assert Intersection(0.0, Direction.VERTICAL).approx(next(intersections))
    assert Intersection(1.0, Direction.VERTICAL).approx(next(intersections))
    assert Intersection(2.0, Direction.VERTICAL).approx(next(intersections))


def test_intersections_vertical_ray():
    ray = Ray(Vector2(0, 0), Vector2(0, 1))
    intersections = find_grid_intersections(ray)

    assert Intersection(0.0, Direction.HORIZONTAL).approx(next(intersections))
    assert Intersection(1.0, Direction.HORIZONTAL).approx(next(intersections))
    assert Intersection(2.0, Direction.HORIZONTAL).approx(next(intersections))


def test_intersections():
    ray = Ray(Vector2(0.5, 0.5), Vector2(4, 1))
    intersections = find_grid_intersections(ray)

    assert Intersection(0.125, Direction.VERTICAL) == next(intersections)
    assert Intersection(0.375, Direction.VERTICAL) == next(intersections)
    assert Intersection(0.5, Direction.HORIZONTAL) == next(intersections)
    assert Intersection(0.625, Direction.VERTICAL) == next(intersections)


def test_intersections_2():
    ray = Ray(Vector2(0.5, 0.5), Vector2(-4, -1))
    intersections = find_grid_intersections(ray)

    assert Intersection(0.125, Direction.VERTICAL) == next(intersections)
    assert Intersection(0.375, Direction.VERTICAL) == next(intersections)
    # assert Intersection(0.5, Direction.HORIZONTAL) == next(intersections)
    # assert Intersection(0.625, Direction.VERTICAL) == next(intersections)