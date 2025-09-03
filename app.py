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

    sample_rate, samples = wavfile.read('./sound.wav')
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



class AudioSource:
    __position: pygame.Vector2

    def __init__(self, position: pygame.Vector2):
        self.__position = position

    @property
    def position(self) -> pygame.Vector2:
        return self.__position

    @position.setter
    def position(self, value: pygame.Vector2):
        self.__position = value


@dataclass
class RayTree:
    position: pygame.Vector2
    branching_factor: int
    subtrees : list[RayTree]
    audio_source: list[AudioSource]


def build_ray_tree(grid: Grid, audio_sources: list[AudioSource], origin: pygame.Vector2, branching_factor: int, maximum_distance: float, maximum_steps: int) -> RayTree:
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
                    subtree = build_ray_tree(grid, audio_sources, hit.position, branching_factor, maximum_distance - distance, maximum_steps-1)
                    subtrees.append(subtree)

    reachable_audio_sources = [audio_source for audio_source in audio_sources if audio_source.position == origin or grid.no_obstacles_between(origin, audio_source.position)]

    return RayTree(origin, branching_factor, subtrees, reachable_audio_sources)


def draw_ray_tree(screen, ray_tree: RayTree, block_size: int):
    def draw(tree: RayTree):
        for child in tree.subtrees:
            start = (int(tree.position.x * block_size), int(tree.position.y * block_size))
            stop = (int(child.position.x * block_size), int(child.position.y * block_size))
            pygame.draw.line(screen, "red", start, stop)

        for audio_source in tree.audio_source:
            start = (int(tree.position.x * block_size), int(tree.position.y * block_size))
            stop = (int(audio_source.position.x * block_size), int(audio_source.position.y * block_size))
            pygame.draw.line(screen, "green", start, stop)

        for subtree in tree.subtrees:
            draw(subtree)

    draw(ray_tree)


@dataclass
class AudioReception:
    audio_source: AudioSource
    distance: float
    volume: float


def compute_incoming_audio(ray_tree: RayTree) -> list[AudioReception]:
    incoming_audio = []

    def compute(tree: RayTree, volume_factor: float, extra_distance: float):
        nonlocal incoming_audio
        for audio_source in tree.audio_source:
            distance = tree.position.distance_to(audio_source.position) + extra_distance
            incoming_audio.append(AudioReception(audio_source=audio_source, distance=distance, volume=volume_factor))

        for subtree in tree.subtrees:
            compute(subtree, volume_factor / ray_tree.branching_factor, extra_distance + tree.position.distance_to(subtree.position))

    compute(ray_tree, 1, 0)

    incoming_audio.sort(key=lambda x: x.distance)
    return incoming_audio


def recompute():
    global ray_tree, audio_sources, audio_receptions
    ray_tree = build_ray_tree(grid, audio_sources, player_position, 12, 50, 2)
    audio_receptions = compute_incoming_audio(ray_tree)


grid = Grid(50, 50)
block_size = 16
player_position = pygame.Vector2(4.5, 4.5)
ray_tree: RayTree
audio_sources: list[AudioSource] = [AudioSource(pygame.Vector2(1.5, 1.5))]
audio_receptions: list[AudioReception] = []
recompute()

pygame.init()
screen = pygame.display.set_mode((grid.Width * block_size, grid.Height * block_size))
clock = pygame.time.Clock()
running = True
BUFFER_SIZE = 16384

sample_rate, samples = wavfile.read('./sound.wav')
samples = samples.astype(np.float64)
buffer = np.zeros((BUFFER_SIZE, 2), dtype=np.float64)

sample_index = 0
def audio_callback(output, frames, time, status):
    global sample_index, sample_rate, samples
    total_volume = 0

    buffer.fill(0)
    for audio_reception in audio_receptions:
        distance = audio_reception.distance
        if distance > 0:
            start = sample_index - int(distance * 1000)
            stop = start + frames
            volume = min(1, 1 / distance)
            if total_volume + volume > 1:
                break
            if start < 0:
                buffer[-start:] += samples[:stop] * volume
            else:
                buffer[:] += samples[start:stop] * volume
            total_volume += volume

    np.clip(buffer, -1, 1)
    output[:] = buffer.astype(np.int16)
    sample_index += frames

output_stream = sounddevice.OutputStream(channels=2, callback=audio_callback, blocksize=BUFFER_SIZE, dtype='int16')

with output_stream:
    while running:
        # poll for events
        # pygame.QUIT event means the user clicked X to close your window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # fill the screen with a color to wipe away anything from last frame
        screen.fill("black")

        pressed_keys = pygame.key.get_pressed()
        if pressed_keys[pygame.K_a]:
            x, y = pygame.mouse.get_pos()
            audio_sources[0].position = pygame.Vector2(x / block_size, y / block_size)
            recompute()

        if pygame.mouse.get_pressed()[0]:
            sx, sy = pygame.mouse.get_pos()
            player_position = pygame.Vector2(sx / block_size, sy / block_size)
            recompute()

        if pygame.mouse.get_pressed()[2]:
            x, y = pygame.mouse.get_pos()
            x //= block_size
            y //= block_size
            grid[Position(x, y)] = not pressed_keys[pygame.K_LSHIFT]
            recompute()

        for y in range(grid.Height):
            for x in range(grid.Width):
                if grid[Position(x, y)]:
                    pygame.draw.rect(screen, "blue", (x * block_size, y * block_size, block_size, block_size))


        draw_ray_tree(screen, ray_tree, block_size)
        pygame.draw.circle(screen, "red", (player_position.x * block_size, player_position.y * block_size), 5)
        for audio_source in audio_sources:
            pygame.draw.circle(screen, "green", (audio_source.position.x * block_size, audio_source.position.y * block_size), 5)

        # flip() the display to put your work on screen
        pygame.display.flip()

        clock.tick(60)  # limits FPS to 60

    pygame.quit()
    output_stream.stop()
    output_stream.close()
