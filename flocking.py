import matplotlib.pyplot as plt
import random
from enum import Enum, auto
import pygame as pg
from pygame.math import Vector2
from vi import Agent, Simulation, HeadlessSimulation
from vi.config import Config, dataclass, deserialize
import polars as pl


@deserialize
@dataclass
class PredatorPreyConfig(Config):
    rabbit_reproduction_rate: float = 0.004
    fox_reproduction_rate: float = 0.5
    fox_death_rate: float = 0.001
    deer_reproduction_rate: float = 0.005
    hawk_reproduction_rate: float = 0.3
    hawk_death_rate: float = 0.05
    energy_gain_from_food: float = 50
    initial_energy: float = 1000
    grass_energy: float = 300  # Energy gained by eating grass
    grass_regrow_time: int = 100
    



class Grass(Agent):
    config: PredatorPreyConfig

    def on_spawn(self):
        self.is_grown = True
        self.regrow_timer = 0
        self.age = 0

    def update(self, delta_time=0.5):
        self.save_data("kind", "grass")
        self.age += delta_time
        if not self.is_grown:
            self.regrow_timer += 1
            self.continue_movement()
            if self.regrow_timer >= self.config.grass_regrow_time:
                self.is_grown = True
                self.freeze_movement()
                self.regrow_timer = 0

    


class RabbitM(Agent):
    config: PredatorPreyConfig

    def on_spawn(self):
        self.energy = self.config.initial_energy
        self.age = 0
        self.reproduction_timer = 0

    def update(self, delta_time=0.5):
        self.save_data("kind", "rabbitm")
        self.energy -= 1
        self.age += delta_time
        if self.reproduction_timer >= 1:
            self.reproduction_timer += delta_time
        
        if self.reproduction_timer > 30:
            self.reproduction_timer = 0

        

        if self.energy <= 0:
            self.kill()
            print("i have dead because of lack of energy") #marker of energy death
        for grass in self.in_proximity_performance():
            if isinstance(grass, Grass) and grass.is_grown:
                grass.is_grown = False
                self.energy += self.config.grass_energy
        for rabbit in self.in_proximity_performance():
            if isinstance(rabbit, RabbitF):
                
                if random.random() < self.config.rabbit_reproduction_rate and self.reproduction_timer == 0:
                    self.reproduce() #rabbits have a litter of two children and afterwards have a reproduction timer to avoid expontential rabbit growth
                    self.reproduction_timer +=1
                

        
        runaway = self.RunAwayRabbit()
        if runaway != None:
            self.move = runaway * self.config.movement_speed
            self.pos += self.move * delta_time
    

    def RunAwayRabbit(self):

      
        config = Config(fps_limit=0)
        x, y = config.window.as_tuple()
        obstacles = [] #Inside of this are the positions of the foxes

        for foxHawk in self.in_proximity_performance():
            if isinstance(foxHawk,Fox):
                obstacles.append(foxHawk.pos) #position of the foxes get put into the obstacles.
            elif isinstance(foxHawk, Hawk):
                obstacles.append(foxHawk.pos)



        if len(obstacles) > 0 and self.age < 600: #if there are foxes as obstacles and if they are young they will avoid the fox
            closest_obstacle = min(obstacles, key=lambda obstacle: self.pos.distance_to(obstacle))
        

       
            obstacle_direction = self.pos - closest_obstacle
            obstacle_direction.normalize_ip()  
            return obstacle_direction


class RabbitF(Agent):
    config: PredatorPreyConfig

    def on_spawn(self):
        self.energy = self.config.initial_energy
        self.age =0
        self.reproduction_timer = 0

    def update(self, delta_time=0.5):
        self.save_data("kind", "rabbitF")
        self.energy -= 1
        self.age += delta_time

        if self.reproduction_timer >= 1:
            self.reproduction_timer += delta_time
        
        if self.reproduction_timer > 30:
            self.reproduction_timer = 0

        if self.energy <= 0:
            self.kill()
            print("i have dead because of lack of energy") #gives us an idea of whats happening
        for grass in self.in_proximity_performance():
            if isinstance(grass, Grass) and grass.is_grown:
                grass.is_grown = False
                self.energy += self.config.grass_energy

        for rabbit in self.in_proximity_performance():
            if isinstance(rabbit, RabbitM):
                if random.random() < self.config.rabbit_reproduction_rate and self.reproduction_timer == 0:
                    self.reproduce()
                    self.reproduction_timer += 1

        runaway = self.RunAwayRabbit()
        if runaway != None:
            self.move = runaway * self.config.movement_speed
            self.pos += self.move * delta_time

    def RunAwayRabbit(self):

      
        config = Config(fps_limit=0)
        x, y = config.window.as_tuple()
        obstacles = [] #Inside of this are the positions of the foxes

        for foxHawk in self.in_proximity_performance():
            if isinstance(foxHawk,Fox):
                obstacles.append(foxHawk.pos) #position of the foxes get put into the obstacles.
            elif isinstance(foxHawk, Hawk):
                obstacles.append(foxHawk.pos)



        if len(obstacles) > 0 and self.age < 600: #if there are foxes as obstacles and if they are young they will avoid the fox
            closest_obstacle = min(obstacles, key=lambda obstacle: self.pos.distance_to(obstacle))
        

       
            obstacle_direction = self.pos - closest_obstacle
            obstacle_direction.normalize_ip()  
            return obstacle_direction


class Fox(Agent):
    config: PredatorPreyConfig

    def on_spawn(self):
        self.energy = 1000
        self.age = random.randint(0, 10)

    def update(self, delta_time=0.5):
        self.energy -= 0.1
        self.age += delta_time
        self.save_data("kind", "fox")
        if self.energy <= 25:
            self.kill()
            print("i have dead because of lack of energy")
        if self.age > 15:
           for rabbit in self.in_proximity_performance():
                if isinstance(rabbit, RabbitF) or isinstance(rabbit, RabbitM):
                    if rabbit.age > 300:
                        print("i am to old to run away")
                    if self.pos.distance_to(rabbit.pos) < 40:
                        rabbit.kill()
                        self.energy += self.config.energy_gain_from_food
                        if random.random() < self.config.fox_reproduction_rate:
                            self.reproduce()
                    break

        if self.age > 365:
            if random.random() < self.config.fox_death_rate:
                self.kill()

        runaway = self.RunAwayfox()
        if runaway != None:
            self.move = runaway * self.config.movement_speed
            self.pos += self.move * delta_time

    def RunAwayfox(self):

      
        config = Config(fps_limit=0)
        x, y = config.window.as_tuple()
        obstacles = [] #Inside of this are the positions of the hawks

        for hawk in self.in_proximity_performance():
            if isinstance(hawk,Hawk):
                obstacles.append(hawk.pos) #position of the hawks get put into the obstacles.
    

        if len(obstacles) > 0 and self.age < 600: #if there are hawks as obstacles and if they are young they will avoid the hawk
            closest_obstacle = min(obstacles, key=lambda obstacle: self.pos.distance_to(obstacle))
        

       
            obstacle_direction = self.pos - closest_obstacle
            obstacle_direction.normalize_ip()  
            return obstacle_direction
    
   


class Hawk(Agent):
    config: PredatorPreyConfig

    def on_spawn(self):
        self.energy = self.config.initial_energy
        self.age = random.randint(0, 8)

    def update(self, delta_time=0.5):
        self.energy -= 0.1
        self.age += delta_time
        self.save_data("kind", "hawk")
        if self.energy <= 25:
            self.kill()
        if self.age > 15:
            for prey in self.in_proximity_performance():
                if isinstance(prey, RabbitF) or isinstance(prey, Fox) or isinstance(prey, RabbitM):
                    if self.pos.distance_to(prey.pos) < 40:
                        prey.kill()
                        self.energy += self.config.energy_gain_from_food
                        if random.random() < self.config.hawk_reproduction_rate:
                            self.reproduce()
                    break

        if self.age > 730:
            if random.random() < self.config.hawk_death_rate:
                self.kill()





config = PredatorPreyConfig(
    image_rotation=True, movement_speed=1, radius=50, seed=654,duration=60*100)

x, y = config.window.as_tuple()

df = HeadlessSimulation(config).batch_spawn_agents(15, RabbitF, images=[r"C:\Users\jahre\white.png"]).batch_spawn_agents(15, RabbitM, images=[r"C:\Users\jahre\white.png"]).batch_spawn_agents(4, Fox, images=[r"C:\Users\jahre\red.png"]).batch_spawn_agents(10, Grass, images=[r"C:\Users\jahre\green.png"]).batch_spawn_agents(2, Hawk, images=[r"C:\Users\jahre\bird.jpeg"]).run().snapshots
print(df.filter(pl.col("frame") == 10))

# .spawn_site(r"/Users/anastasiaaliani/Desktop/UNI/SEM 2/Project Collective Intelligence/Assignment_0 2/images/triangle@200px.png", 150, y // 2).spawn_site(r"/Users/anastasiaaliani/Desktop/UNI/SEM 2/Project Collective Intelligence/Assignment_0 2/images/triangle@50px.png", 550, y // 2)


def counting(df):
    Frames = df.get_column("frame").unique()
    population = dict()
    for _ in Frames:
        fdf = df.filter(pl.col("frame") == _)
        filtered_by_kind_and_frame_df = fdf.get_column("kind")
        counterRf = 0
        counterRm = 0
        counterD = 0
        counterH = 0
        counterF = 0
        for animal in filtered_by_kind_and_frame_df:
            if animal == "rabbitF":
                counterRm += 1
            elif animal == "rabbitm":
                counterRf += 1
            elif animal == "hawk":
                counterH += 1
            elif animal == "fox":
                counterF += 1
        population[_] = (counterRm, counterRf, counterH, counterF)

    return population


population_data = counting(df)
print(population_data)

frames = sorted(population_data.keys())
print(frames)
rabbitsm = [population_data[frame][0] for frame in frames]
rabbitsf = [population_data[frame][1] for frame in frames]
hawk = [population_data[frame][2] for frame in frames]
foxes = [population_data[frame][3] for frame in frames]

plt.plot(frames, rabbitsm, label='Rabbit Male Population')
plt.plot(frames, rabbitsf, label='Rabbit Female Population')
plt.plot(frames, hawk, label='Hawk Population')
plt.plot(frames, foxes, label='Fox Population')

plt.xlabel('Frames')
plt.ylabel('Population')
plt.title('Rabbit, Hawk and Fox Population Over Time')
plt.legend()
plt.show()