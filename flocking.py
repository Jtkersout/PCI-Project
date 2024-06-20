import matplotlib.pyplot as plt
import random
from enum import Enum, auto
import pygame as pg
from pygame.math import Vector2
from vi import Agent, Simulation,metrics,HeadlessSimulation
from vi.config import Config, dataclass, deserialize
import polars as pl


@deserialize
@dataclass
class PredatorPreyConfig(Config):
    rabbit_reproduction_rate: float = 0.001
    fox_reproduction_rate: float = 1
    fox_death_rate: float = 0.1
    energy_gain_from_food: float = 50
    initial_energy: float = 100


class Rabbit(Agent):
    config: PredatorPreyConfig

   
    def update(self, delta_time=0.5):
        if random.random() < self.config.rabbit_reproduction_rate:
            self.reproduce()
        
        self.save_data("kind","rabbit")


class Fox(Agent):
    config: PredatorPreyConfig
    timer = random.randint(0,10)
    

    def update(self, delta_time=0.5):
        self.timer += delta_time
        self.save_data("kind", "fox")
        if self.timer > 15:
            for rabbit in self.in_proximity_accuracy().without_distance():
                    if isinstance(rabbit, Rabbit):
                        rabbit.kill()
                        self.reproduce()
                        break
        if self.timer > 100:
            if random.random() < self.config.fox_death_rate:
                self.kill()
            else:
                self.timer = 0


config = PredatorPreyConfig(
    image_rotation=True, movement_speed=1, radius=50, seed=1)
#simulation = Simulation(config)

# Spawning initial agents

#simulation.batch_spawn_agents(100, Rabbit, images=[r"C:\Users\jahre\green.png"])
#simulation.batch_spawn_agents(5, Fox, images=[r"C:\Users\jahre\red.png"])
#simulation.run()
metrics

df = Simulation(config).batch_spawn_agents(13, Rabbit, images=[r"C:\Users\jahre\green.png"]).batch_spawn_agents(2,Fox,images=[r"C:\Users\jahre\red.png"]).run().snapshots
print(df.filter(pl.col("frame") == 10))


def counting(df):
    Frames = df.get_column("frame").unique()
    population = dict()
    for _ in Frames:
        fdf = df.filter(pl.col("frame") == _)
        filtered_by_kind_and_frame_df = fdf.get_column("kind")
        counterR = 0
        counterF = 0
        for animal in filtered_by_kind_and_frame_df:
            if animal == "rabbit":
                counterR +=1
            else:
                counterF +=1
        population[_] = (counterR,counterF)
    
    return population
            
    

counting(df)