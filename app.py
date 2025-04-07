from __future__ import annotations
from typing import Tuple
from dataclasses import dataclass
import sounddevice
import numpy as np
import math
import pygame
from simsound.grid import Grid, Position
from scipy.io import wavfile

from simsound.ray import Ray


def audio_test():
    duration = 5  # seconds
    frequency = 44100  # Hz

    sample_rate, samples = wavfile.read('./cash.wav')
    # samples = samples[:, 0]  # Use only one channel if stereo
    sample_count = frequency * duration
    samples = samples[:sample_count]
    samples = samples.astype(np.int16)  # Ensure the data type is int16

    # delay = 5000
    # zeros = np.zeros(delay, dtype=np.int16)
    # s = samples // 2
    # samples = s + np.concatenate((zeros, s))[:sample_count]


    def create_callback(samples):
        index = 0
        def callback(outdata, frames, time, status):
            nonlocal index
            outdata[:] = samples[index:index+frames]
            index += frames
        return callback


    with sounddevice.OutputStream(channels=2, callback=create_callback(samples), blocksize=16384, dtype='int16'):
        sounddevice.sleep(int(duration * 1000))


@dataclass
class RayTree:
    position: pygame.Vector2
    subtrees : list[RayTree]


def build_ray_tree(grid: Grid, origin: pygame.Vector2, branching_factor: int, maximum_distance: float, maximum_steps: int) -> RayTree:
    subtrees = []

    if maximum_steps > 0:
        for phi in range(0, 360, 360 // branching_factor):
            angle = math.radians(phi)
            direction = pygame.Vector2(math.cos(angle), math.sin(angle))
            ray = Ray(origin, direction)
            hit = grid.find_hit(ray)

            if hit is not None:
                distance = origin.distance_to(hit.position)
                if hit.reflection > 0 and 0.01 < distance < maximum_distance:
                    subtree = build_ray_tree(grid, hit.position, branching_factor, maximum_distance - distance, maximum_steps-1)
                    subtrees.append(subtree)

    return RayTree(origin, subtrees)


def draw_ray_tree(screen, ray_tree: RayTree, block_size: int):
    def draw(origin: pygame.Vector2, subtree: RayTree):
        start = (int(origin.x * block_size), int(origin.y * block_size))
        stop = (int(subtree.position.x * block_size), int(subtree.position.y * block_size))
        pygame.draw.line(screen, "red", start, stop)
        for child in subtree.subtrees:
            draw(subtree.position, child)
    for child in ray_tree.subtrees:
        draw(ray_tree.position, child)


def cast_sound_rays(grid: Grid, origin: pygame.Vector2, steps: int = 1) -> list[Tuple[pygame.Vector2, pygame.Vector2]]:
    result: list[Tuple[pygame.Vector2, pygame.Vector2]] = []

    if steps > 0:
        for phi in range(0, 360, 10):
            angle = math.radians(phi)
            direction = pygame.Vector2(math.cos(angle), math.sin(angle))
            ray = Ray(origin, direction)
            hit = grid.find_hit(ray)
            if hit is not None:
                result.append((origin, hit.position))

    return result


def rebuild_tree():
    global ray_tree
    ray_tree = build_ray_tree(grid, position, 12, 50, 1)

ray_tree: RayTree

grid = Grid(10, 10)
block_size = 64
position = pygame.Vector2(1, 1)
# rays = cast_sound_rays(grid, position)
rebuild_tree()

pygame.init()
screen = pygame.display.set_mode((grid.Width * block_size, grid.Height * block_size))
clock = pygame.time.Clock()
running = True

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("black")

    if pygame.mouse.get_pressed()[0]:
        sx, sy = pygame.mouse.get_pos()
        x = sx / block_size
        y = sy / block_size
        position = pygame.Vector2(x, y)
        rebuild_tree()

    if pygame.mouse.get_just_pressed()[2]:
        x, y = pygame.mouse.get_pos()
        x //= block_size
        y //= block_size
        grid[Position(x, y)] = not grid[Position(x, y)]
        rebuild_tree()

    for y in range(grid.Height):
        for x in range(grid.Width):
            if grid[Position(x, y)]:
                pygame.draw.rect(screen, "blue", (x * block_size, y * block_size, block_size, block_size))

    # for (p, q) in rays:
    #     pygame.draw.line(screen, "red", (int(p.x * block_size), int(p.y * block_size)), (int(q.x * block_size), int(q.y * block_size)))

    draw_ray_tree(screen, ray_tree, block_size)

    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(60)  # limits FPS to 60

pygame.quit()