import matplotlib.pyplot as plt
import random
from enum import Enum, auto
import pygame as pg
from pygame.math import Vector2
from vi import Agent, Simulation
from vi.config import Config, dataclass, deserialize


@deserialize
@dataclass
class PredatorPreyConfig(Config):
    rabbit_reproduction_rate: float = 0.015
    fox_reproduction_rate: float = 1
    fox_death_rate: float = 0.01
    energy_gain_from_food: float = 50
    initial_energy: float = 100


class Rabbit(Agent):
    config: PredatorPreyConfig

    def on_spawn(self):
        self.energy = self.config.initial_energy

    def update(self, delta_time=0.5):
        self.energy -= 1
        if self.energy <= 0:
            self.kill()
        if random.random() < self.config.rabbit_reproduction_rate:
            self.reproduce()


class Fox(Agent):
    config: PredatorPreyConfig

    def on_spawn(self):
        self.energy = self.config.initial_energy
        self.hunger = 0

    def update(self, delta_time=0.5):
        self.energy -= 0.01
        self.hunger -= 0.01
        if self.energy <= 0:
            self.kill()
        for rabbit in self.in_proximity_accuracy().without_distance():
            if self.hunger < 0:
                if isinstance(rabbit, Rabbit):
                    rabbit.kill()
                    self.energy += self.config.energy_gain_from_food
                    self.reproduce()
                    self.hunger = 3
                    break
        if random.random() < self.config.fox_death_rate:
            self.kill()


config = PredatorPreyConfig(
    image_rotation=True, movement_speed=5, radius=50, seed=1)
simulation = Simulation(config)

# Spawning initial agents
simulation.batch_spawn_agents(100, Rabbit, images=[r"C:\Users\jahre\green.png"])
simulation.batch_spawn_agents(5, Fox, images=[r"C:\Users\jahre\red.png"])

simulation.run()
