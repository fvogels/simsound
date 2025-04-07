from typing import Tuple
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


def cast_sound_rays(grid: Grid, origin: pygame.Vector2, steps: int = 1) -> list[Tuple[pygame.Vector2, pygame.Vector2]]:
    result: list[Tuple[pygame.Vector2, pygame.Vector2]] = []

    if steps > 0:
        for phi in range(0, 360, 10):
            angle = math.radians(phi)
            direction = pygame.Vector2(math.cos(angle), math.sin(angle))
            ray = Ray(origin, direction)
            collision, reflected = grid.find_hit(ray)
            result.append((origin, collision))

    return result



grid = Grid(10, 10)
block_size = 64
position = pygame.Vector2(1, 1)
rays = cast_sound_rays(grid, position)

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
        rays = cast_sound_rays(grid, position)

    if pygame.mouse.get_just_pressed()[2]:
        x, y = pygame.mouse.get_pos()
        x //= block_size
        y //= block_size
        grid[Position(x, y)] = not grid[Position(x, y)]
        rays = cast_sound_rays(grid, position)

    for y in range(grid.Height):
        for x in range(grid.Width):
            if grid[Position(x, y)]:
                pygame.draw.rect(screen, "blue", (x * block_size, y * block_size, block_size, block_size))

    for (p, q) in rays:
        pygame.draw.line(screen, "red", (int(p.x * block_size), int(p.y * block_size)), (int(q.x * block_size), int(q.y * block_size)))

    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(60)  # limits FPS to 60

pygame.quit()