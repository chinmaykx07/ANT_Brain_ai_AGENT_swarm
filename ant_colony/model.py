import numpy as np
import math
import mesa
from mesa.space import MultiGrid
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
from agent import AntAgent, RockAgent, GarbageAgent, PheromoneAgent, QueenAgent, PrincessAgent
from scipy.signal import convolve2d
import json


class AntColonyModel(mesa.Model):
    def __init__(self, width=100, height=100, initial_ants=20, seed=None):
        super().__init__(seed=seed)
        self.width = width
        self.height = height
        self.grid = MultiGrid(width, height, torus=False)
        self.schedule = RandomActivation(self)

        # Vectorized pheromone diffusion kernel
        self.diffusion_kernel = np.array([[0.05, 0.1, 0.05],[0.1, 0.4, 0.1],[0.05, 0.1, 0.05]])

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

        # 2026 Ultimate Stabilization: Colony Health Dashboard
        self.metabolic_persistence_index = 1.0  # MPI: energy_collected / energy_burned
        self.knowledge_diffusion_rate = 0.0  # KDR: speed of TFL wave propagation
        self.colony_entropy = 0.0  # Σ: measure of task disorder
        
        # Liberation Threshold System
        self.inhibitory_pheromone_strength = 1.0  # Queen's inhibitory signal
        self.colony_density = 0.0  # ants per unit area
        self.liberation_events = 0  # Number of colony splits
        
        # Metabolic tracking for MPI calculation
        self.total_energy_burned = 0.0
        self.total_energy_collected = 0.0

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
                # 2026 Ultimate Stabilization: Colony Health Dashboard
                "MetabolicPersistenceIndex": lambda m: m.metabolic_persistence_index,
                "KnowledgeDiffusionRate": lambda m: m.knowledge_diffusion_rate,
                "ColonyEntropy": lambda m: m.colony_entropy,
                "ColonyDensity": lambda m: m.colony_density,
                "InhibitoryPheromoneStrength": lambda m: m.inhibitory_pheromone_strength,
                "LiberationEvents": lambda m: m.liberation_events,
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

        # Generate random trash heaps: 5 scattered 3x3 blocks of garbage
        np.random.seed(seed)
        
        for _ in range(5):
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
        self.pheromone_map = convolve2d(self.pheromone_map, self.diffusion_kernel, mode='same', boundary='wrap')

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
        # Diffuse home pheromone (vectorized)
        self.home_pheromone_map = convolve2d(self.home_pheromone_map, self.diffusion_kernel, mode='same', boundary='wrap')

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

        # 2026 Ultimate Stabilization: Liberation Threshold System
        self.update_liberation_thresholds()

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

    def update_liberation_thresholds(self):
        """Calculate colony health metrics and trigger liberation events."""
        # Calculate colony density (ants per unit area)
        ant_count = sum(1 for agent in self.schedule.agents if isinstance(agent, AntAgent))
        self.colony_density = ant_count / (self.width * self.height)
        
        # Calculate Metabolic Persistence Index (MPI)
        if self.total_energy_burned > 0:
            self.metabolic_persistence_index = self.total_energy_collected / self.total_energy_burned
        else:
            self.metabolic_persistence_index = 1.0
        
        # Calculate Knowledge Diffusion Rate (KDR) - speed of TFL wave propagation
        # Simplified: measure pheromone spread rate as proxy for knowledge diffusion
        pheromone_coverage = np.sum(self.pheromone_map > 0.1) / (self.width * self.height)
        self.knowledge_diffusion_rate = pheromone_coverage
        
        # Calculate Colony Entropy (Σ) - measure of task disorder
        # Simplified: variance in ant roles as proxy for task specialization
        role_counts = {}
        for agent in self.schedule.agents:
            if isinstance(agent, AntAgent):
                role = agent.role
                role_counts[role] = role_counts.get(role, 0) + 1
        
        if role_counts:
            total_ants = sum(role_counts.values())
            role_proportions = [count / total_ants for count in role_counts.values()]
            # Shannon entropy calculation
            self.colony_entropy = -sum(p * np.log(p) for p in role_proportions if p > 0)
        else:
            self.colony_entropy = 0.0
        
        # Liberation Threshold Logic
        # Threshold 1: Colony density exceeds sustainable limit
        density_threshold = 0.05  # 5% of grid occupied by ants
        
        # Threshold 2: Metabolic stress (MPI drops below threshold)
        mpi_threshold = 0.8  # Energy collected < 80% of energy burned
        
        # Threshold 3: Task disorder (high entropy indicates lack of specialization)
        entropy_threshold = 1.5  # High entropy = chaotic behavior
        
        # Threshold 4: Inhibitory pheromone strength (Queen's control weakening)
        inhibitory_threshold = 2.0  # Queen's signal strength
        
        if (self.colony_density > density_threshold or 
            self.metabolic_persistence_index < mpi_threshold or
            self.colony_entropy > entropy_threshold or
            self.inhibitory_pheromone_strength > inhibitory_threshold):
            
            self.trigger_liberation_event()
            
            # Reset inhibitory pheromone strength after liberation
            self.inhibitory_pheromone_strength = max(1.0, self.inhibitory_pheromone_strength * 0.8)
    
    def trigger_liberation_event(self):
        """Spawn founder queens to create new colonies."""
        self.liberation_events += 1
        
        # Find mature ants to become founder queens (high XP ants)
        potential_founders = []
        for agent in self.schedule.agents:
            if isinstance(agent, AntAgent) and agent.xp > 50:  # Experienced ants
                potential_founders.append(agent)
        
        # Spawn up to 3 founder queens
        founders_to_spawn = min(3, len(potential_founders))
        
        for i in range(founders_to_spawn):
            if potential_founders:
                founder_ant = potential_founders.pop(0)
                founder_pos = founder_ant.pos
                
                # Remove the ant (becomes queen)
                self.grid.remove_agent(founder_ant)
                self.schedule.remove(founder_ant)
                
                # Spawn founder queen at ant's location
                founder_queen = QueenAgent(
                    self.next_id(),
                    self,
                    founder_pos,
                    genome=founder_ant.weights,  # Use ant's brain as queen genome
                    tribe_id=self.current_generation + self.liberation_events,
                    is_founder=True
                )
                self.grid.place_agent(founder_queen, founder_pos)
                self.schedule.add(founder_queen)
                
                # Give founder queen initial seed swarm (3-5 ants)
                seed_swarm_size = np.random.randint(3, 6)
                for _ in range(seed_swarm_size):
                    seed_ant = AntAgent(
                        self.next_id(),
                        self,
                        founder_pos,
                        role="worker",
                        tribe_id=founder_queen.tribe_id,
                        parent_queen=founder_queen
                    )
                    # Place near queen
                    dx, dy = np.random.randint(-2, 3), np.random.randint(-2, 3)
                    seed_pos = (max(0, min(self.width-1, founder_pos[0] + dx)),
                               max(0, min(self.height-1, founder_pos[1] + dy)))
                    self.grid.place_agent(seed_ant, seed_pos)
                    self.schedule.add(seed_ant)

