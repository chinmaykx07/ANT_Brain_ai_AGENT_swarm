import numpy as np
import math
import mesa
from mesa.space import MultiGrid
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
from agent import AntAgent, RockAgent, GarbageAgent, PheromoneAgent, QueenAgent, PrincessAgent
import json


class AntColonyModel(mesa.Model):
    def __init__(self, width=30, height=30, initial_ants=20, seed=None):
        super().__init__(seed=seed)
        self.width = width
        self.height = height
        self.grid = MultiGrid(width, height, torus=False)
        self.schedule = RandomActivation(self)

        self.pheromone_map = np.zeros((width, height), dtype=float)
        self.home_pheromone_map = np.zeros((width, height), dtype=float)
        self.garbage_map = np.zeros((width, height), dtype=int)
        self.garbage_type_map = np.zeros((width, height), dtype=int)
        self.nectar_map = np.zeros((width, height), dtype=int)  # High-value resource
        self.pheromone_garbage = np.zeros((width, height), dtype=float)  # Yellow trails
        self.pheromone_nectar = np.zeros((width, height), dtype=float)  # Magenta trails
        self.death_beacon_map = np.zeros((width, height), dtype=int)  # Persistent knowledge markers
        self.obstacle_map = np.zeros((width, height), dtype=bool)
        self.garbage_agents = {}  # Track garbage agent positions
        self.pheromone_agents = {}  # Track pheromone agent positions
        
        # 2026 Frontier: Swarm Intelligence & Metabolic Tracking
        self.swarm_intellect = 0.0  # Collective intelligence level (0-1000)
        self.evolution_points = 0  # Queen's evolution points
        self.unlocked_abilities = {
            'global_communication': False,  # At 100 evolution points
            'super_intelligence': False,  # At 500 evolution points
            'hero_scout': False,  # At 1000 evolution points
        }

        self.resource_type_map = {
            1: "food",
            2: "food",
            3: "food",
            4: "building_material",
            5: "building_material",
            6: "building_material",
        }

        self.resource_inventory = {
            "food": 0,
            "building_material": 0,
            "design": 0,
            "scavenger": 0,
            "scouting": 0,
            "ecosystem": 0,
        }

        self.colony_hunger = 1.0
        self.total_garbage_collected = 0
        self.colony_biomass = 0
        self.queens_born = 0
        self.current_generation = 0
        self.next_tribe_id = 1
        self.total_nectar_collected = 0  # Track premium resource

        self.datacollector = DataCollector(
            model_reporters={
                "Population": lambda m: sum(1 for a in m.schedule.agents if isinstance(a, AntAgent)),
                "TotalGarbage": lambda m: m.total_garbage_collected,
                "Biomass": lambda m: m.colony_biomass,
                "SwarmIntellect": lambda m: m.swarm_intellect,
                "EvolutionPoints": lambda m: m.evolution_points,
            }
        )

        # Recycling center in center
        self.recycling_center = (width // 2, height // 2)

        # instantiate ants at positions around recycling_center
        center_x, center_y = self.recycling_center
        for i in range(initial_ants):
            # Place ants in a circle around the center
            angle = 2 * math.pi * i / initial_ants
            offset_x = int(2 * math.cos(angle))
            offset_y = int(2 * math.sin(angle))
            ant_x = max(0, min(width - 1, center_x + offset_x))
            ant_y = max(0, min(height - 1, center_y + offset_y))
            ant = AntAgent(self.next_id(), self, self.recycling_center)
            self.schedule.add(ant)
            self.grid.place_agent(ant, (ant_x, ant_y))

        # Create the Queen at the recycling center with initial tribe
        queen = QueenAgent(self.next_id(), self, self.recycling_center, tribe_id=self.next_tribe_id)
        self.schedule.add(queen)
        self.grid.place_agent(queen, self.recycling_center)
        self.queens_born += 1
        self.current_generation = self.queens_born
        self.next_tribe_id += 1

        # Queen starts with a small credit of food to be stable
        self.resource_inventory["food"] = 100

        # Generate random trash heaps: 15 scattered 3x3 blocks of garbage
        np.random.seed(seed)
        
        for _ in range(15):
            trash_x = np.random.randint(max(1, width//4), min(width-1, width - width//4))
            trash_y = np.random.randint(max(1, height//4), min(height-1, height - height//4))
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    x, y = trash_x + dx, trash_y + dy
                    if 0 <= x < width and 0 <= y < height:
                        self.garbage_map[x, y] = 10
                        garbage_type = np.random.randint(1, 7)
                        self.garbage_type_map[x, y] = garbage_type

                        # Create a visual garbage agent
                        garbage_agent = GarbageAgent(self.next_id(), self, (x, y))
                        self.garbage_agents[(x, y)] = garbage_agent
                        self.grid.place_agent(garbage_agent, (x, y))

        # Golden garbage to trigger swarm surge
        golden_x = np.random.randint(0, width)
        golden_y = np.random.randint(0, height)
        self.golden_resource_pos = (golden_x, golden_y)
        self.garbage_map[golden_x, golden_y] = 1
        self.garbage_type_map[golden_x, golden_y] = 99
        golden_agent = GarbageAgent(self.next_id(), self, self.golden_resource_pos)
        self.garbage_agents[self.golden_resource_pos] = golden_agent
        self.grid.place_agent(golden_agent, self.golden_resource_pos)

        # 2026 Frontier: Create rare Nectar clusters (high-value resources)
        for _ in range(3):  # 3 nectar clusters
            nectar_x = np.random.randint(max(1, width//4), min(width-1, width - width//4))
            nectar_y = np.random.randint(max(1, height//4), min(height-1, height - height//4))
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    x, y = nectar_x + dx, nectar_y + dy
                    if 0 <= x < width and 0 <= y < height:
                        self.nectar_map[x, y] = 50  # High value
                        # Create visual nectar agent (magenta)
                        nectar_agent = GarbageAgent(self.next_id(), self, (x, y))
                        self.garbage_agents[(x, y)] = nectar_agent
                        self.grid.place_agent(nectar_agent, (x, y))

        # Build obstacle wall between recycling center and area with two gaps
        wall_x = max(1, self.width // 3)
        for y in range(self.height):
            # small left gap (close to food corner) and larger right gap
            if y == 2 or y in range(12, 15):
                continue
            self.obstacle_map[wall_x, y] = True
            rock = RockAgent(self.next_id(), self, (wall_x, y))
            self.grid.place_agent(rock, (wall_x, y))

        # Create pheromone agents for visualization
        for x in range(width):
            for y in range(height):
                if self.garbage_map[x, y] == 0 and not self.obstacle_map[x, y]:
                    pheromone_agent = PheromoneAgent(self.next_id(), self, (x, y), self.pheromone_map[x, y])
                    self.pheromone_agents[(x, y)] = pheromone_agent
                    self.grid.place_agent(pheromone_agent, (x, y))

    def step(self):
        self.schedule.step()

        # Evaporate pheromones
        self.pheromone_map *= 0.98
        self.pheromone_map[self.pheromone_map < 0.01] = 0.0

        # Homeostatic Neuro-Modulation: Decay death beacons (stigmergic memory persistence)
        self.death_beacon_map[self.death_beacon_map > 0] -= 1

        # Diffusion: spread 10% to neighbors
        new_map = self.pheromone_map.copy()
        for x in range(self.width):
            for y in range(self.height):
                value = self.pheromone_map[x, y]
                if value > 0:
                    spread = value * 0.1
                    for dx, dy in [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < self.width and 0 <= ny < self.height:
                            new_map[nx, ny] += spread
        self.pheromone_map = new_map

        # Update pheromone agent values
        for pos, agent in self.pheromone_agents.items():
            agent.value = self.pheromone_map[pos[0], pos[1]]

        # Queen home pheromone emission (non-evaporating, but diffuses)
        for agent in list(self.schedule.agents):
            if isinstance(agent, QueenAgent):
                x, y = agent.pos
                self.home_pheromone_map[x, y] = 10.0

        # Diffuse home pheromone (slow decay, never disappears fully)
        self.home_pheromone_map *= 0.995
        self.home_pheromone_map[self.home_pheromone_map < 0.01] = 0.01
        home_new = self.home_pheromone_map.copy()
        for x in range(self.width):
            for y in range(self.height):
                value = self.home_pheromone_map[x, y]
                spread = value * 0.05
                for dx, dy in [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.width and 0 <= ny < self.height:
                        home_new[nx, ny] += spread
        self.home_pheromone_map = home_new

        # Hunger increases over time toward 1.0
        self.colony_hunger = min(1.0, self.colony_hunger + 0.005)

        # 2026 Frontier: Swarm Intellect Decay (decays unless boosted by Nectar)
        self.swarm_intellect = max(0.0, self.swarm_intellect - 0.1)

        # Evolution Point Milestones (unlock abilities)
        if self.evolution_points >= 100 and not self.unlocked_abilities['global_communication']:
            self.unlocked_abilities['global_communication'] = True
            # Ants can see pheromones 2x further
        
        if self.evolution_points >= 500 and not self.unlocked_abilities['super_intelligence']:
            self.unlocked_abilities['super_intelligence'] = True
            # LNN hidden layer increases from 10 to 50
        
        if self.evolution_points >= 1000 and not self.unlocked_abilities['hero_scout']:
            self.unlocked_abilities['hero_scout'] = True
            # Spawn a Hero Scout
            self.spawn_hero_scout()

        # Dual-Frequency Pheromone Management
        self.pheromone_garbage *= 0.98
        self.pheromone_garbage[self.pheromone_garbage < 0.01] = 0.0
        self.pheromone_nectar *= 0.98
        self.pheromone_nectar[self.pheromone_nectar < 0.01] = 0.0

        # Collect statistics
        self.datacollector.collect(self)

        # Auto export every 500 steps
        if self.schedule.time % 500 == 0:
            self.export_best_brain()
            self.save_colony_dna()

    def export_best_brain(self):
        best_ant = None
        best_xp = -1
        for agent in self.schedule.agents:
            if isinstance(agent, AntAgent) and agent.xp > best_xp:
                best_xp = agent.xp
                best_ant = agent

        if best_ant is None:
            return

        data = {
            "tribe_id": best_ant.tribe_id,
            "xp": best_ant.xp,
            "weights": best_ant.weights,
            "lifespan": best_ant.lifespan,
            "scent_sensitivity": best_ant.scent_sensitivity,
        }

        with open("hero_brain.json", "w") as f:
            json.dump(data, f)

    def spawn_hero_scout(self):
        """Spawn a Hero Scout with infinite lifespan and maximum abilities."""
        hero = AntAgent(
            self.next_id(),
            self,
            self.recycling_center,
            role="scout",
            tribe_id=self.current_generation,
            lifespan_multiplier=float('inf'),  # Infinite lifespan
            is_hero=True
        )
        hero.speed = 2.0  # Double speed
        hero.antenna_sensitivity = 2.0  # Enhanced senses
        self.grid.place_agent(hero, self.recycling_center)
        self.schedule.add(hero)

    def save_colony_dna(self, filename='best_ant_dna.json'):
        # Find the Queen with the most ants in her tribe
        tribe_counts = {}
        for agent in self.schedule.agents:
            if isinstance(agent, AntAgent):
                tribe = agent.tribe_id
                tribe_counts[tribe] = tribe_counts.get(tribe, 0) + 1
        
        if not tribe_counts:
            return
        
        best_tribe = max(tribe_counts, key=tribe_counts.get)
        
        # Find the Queen of that tribe
        best_queen = None
        for agent in self.schedule.agents:
            if isinstance(agent, QueenAgent) and agent.tribe_id == best_tribe:
                best_queen = agent
                break
        
        if best_queen is None:
            return
        
        # Collect one representative ant's MB weights (since MB is per ant, but for export, take from a worker)
        representative_ant = None
        for agent in self.schedule.agents:
            if isinstance(agent, AntAgent) and agent.tribe_id == best_tribe and agent.role == "worker":
                representative_ant = agent
                break
        
        mb_weights = representative_ant.mb_weights if representative_ant else {}
        
        data = {
            "queen_genome": best_queen.genome,
            "tribe_id": best_tribe,
            "ant_count": tribe_counts[best_tribe],
            "mb_weights": mb_weights,
            "total_garbage_collected": self.total_garbage_collected,
            "colony_biomass": self.colony_biomass,
        }
        
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)

