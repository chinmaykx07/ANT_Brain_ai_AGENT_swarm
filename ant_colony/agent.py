import random
import math
import hashlib
from mesa.agent import Agent
from typing import Tuple, Any

class RockAgent(Agent):
    def __init__(self, unique_id: int, model: Any, pos: Tuple[int, int]):
        super().__init__(unique_id, model)
        self.pos = pos

class GarbageAgent(Agent):
    """Represents a garbage cell for visualization"""
    def __init__(self, unique_id: int, model: Any, pos: Tuple[int, int]):
        super().__init__(unique_id, model)
        self.pos = pos

class PheromoneAgent(Agent):
    """Represents a pheromone cell for visualization"""
    def __init__(self, unique_id: int, model: Any, pos: Tuple[int, int], value: float):
        super().__init__(unique_id, model)
        self.pos = pos
        self.value = value

class QueenAgent(Agent):
    def __init__(self, unique_id: int, model: Any, pos: Tuple[int, int], tribe_id: int = 0, lifespan_multiplier: float = 1.0, scent_sensitivity: float = 1.0):
        super().__init__(unique_id, model)
        self.pos = pos
        self.spawn_cost = 20
        self.health = 100
        self.hunger = 0
        self.tribe_id = tribe_id
        self.lifespan_multiplier = lifespan_multiplier
        self.scent_sensitivity = scent_sensitivity
        self.step_counter = 0
        # Genome for genetic optimization
        self.genome = {
            'antenna_sensitivity': 1.0,
            'max_speed': 1.0,
            'steering_fluidity': 0.1,
        }
        self.weights = [random.uniform(-1, 1) for _ in range(6)]  # Neural weights for inheritance
        self.previous_garbage = 0
        self.colony_reserves = 0
        self.last_food_count = 0

    def step(self):
        self.step_counter += 1
        self.hunger += 1

        # Queen consumes food every 10 ticks to conserve resources; if no food, health drops
        if self.step_counter % 10 == 0:
            if self.model.resource_inventory.get("food", 0) > 0:
                self.model.resource_inventory["food"] -= 1
                self.health = min(100, self.health + 2)
                self.hunger = max(0, self.hunger - 2)
                # Status update: praise nearby worker ants for good job
                nearby_ants = self.model.grid.get_neighbors(self.pos, moore=True, include_center=False, radius=3)
                for agent in nearby_ants:
                    if isinstance(agent, AntAgent) and agent.role in ["worker", "scavenger", "scout"]:
                        agent.xp += 5  # Status update bonus
                        agent.energy_reserve = min(100.0, agent.energy_reserve + 5.0)  # Energy boost
            else:
                self.health -= 5

        if self.health <= 0:
            self.model.colony_biomass += 10
            self.model.grid.remove_agent(self)
            self.model.schedule.remove(self)
            return

        # 2026 Frontier: Check for evolutionary milestones
        if self.model.evolution_points >= 100 and not self.model.unlocked_abilities['global_communication']:
            self.model.unlocked_abilities['global_communication'] = True
            # Ants can now see pheromones twice as far
        
        if self.model.evolution_points >= 500 and not self.model.unlocked_abilities['super_intelligence']:
            self.model.unlocked_abilities['super_intelligence'] = True
            # Expand LNN hidden layer
            for agent in list(self.model.schedule.agents):
                if isinstance(agent, AntAgent) and agent.tribe_id == self.tribe_id:
                    agent.neural_state = [0.0] * 50  # Upgrade from 10 to 50 neurons

        # Emergency spawn when population low
        worker_count = sum(1 for a in self.model.schedule.agents if isinstance(a, AntAgent) and a.role in ["worker", "scavenger", "scout"])
        effective_spawn_cost = self.spawn_cost * (0.5 if worker_count < 10 else 1.0)

        # Homeostatic Neuro-Modulation: Critical biomass emergency spawning
        if worker_count < 10 and self.model.colony_biomass >= 50:
            # Emergency reproduction using biomass
            self.model.colony_biomass -= 50
            emergency_ant = AntAgent(
                self.model.next_id(),
                self.model,
                self.model.recycling_center,
                role="worker",
                tribe_id=self.tribe_id,
                lifespan_multiplier=self.lifespan_multiplier,
                scent_sensitivity=self.scent_sensitivity,
                antenna_sensitivity=self.genome['antenna_sensitivity'],
                max_speed=self.genome['max_speed'],
                steering_fluidity=self.genome['steering_fluidity'],
            )
            # Find empty adjacent position
            neighbors = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False)
            empty_neighbors = [n for n in neighbors if not any(self.model.grid.get_cell_list_contents([n])) and not self.model.obstacle_map[n[0], n[1]] and self.model.garbage_map[n[0], n[1]] == 0]
            if empty_neighbors:
                spawn_pos = self.random.choice(empty_neighbors)
                self.model.grid.place_agent(emergency_ant, spawn_pos)
                self.model.schedule.add(emergency_ant)

        # Spawn workers with building material + food
        if self.model.resource_inventory.get("building_material", 0) >= 5 and self.model.resource_inventory.get("food", 0) >= 1:
            self.model.resource_inventory["building_material"] -= 5
            self.model.resource_inventory["food"] -= 1
            child_weights = [w + random.uniform(-0.05, 0.05) for w in self.weights]
            new_ant = AntAgent(
                self.model.next_id(),
                self.model,
                self.model.recycling_center,
                role="worker",
                tribe_id=self.tribe_id,
                lifespan_multiplier=self.lifespan_multiplier,
                scent_sensitivity=self.scent_sensitivity,
                antenna_sensitivity=self.genome['antenna_sensitivity'],
                max_speed=self.genome['max_speed'],
                steering_fluidity=self.genome['steering_fluidity'],
            )
            new_ant.weights = child_weights
            # Find empty adjacent position
            neighbors = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False)
            empty_neighbors = [n for n in neighbors if not any(self.model.grid.get_cell_list_contents([n])) and not self.model.obstacle_map[n[0], n[1]] and self.model.garbage_map[n[0], n[1]] == 0]
            if empty_neighbors:
                spawn_pos = self.random.choice(empty_neighbors)
                self.model.grid.place_agent(new_ant, spawn_pos)
                self.model.schedule.add(new_ant)

        if self.model.resource_inventory.get("scouting", 0) >= 10:
            self.model.resource_inventory["scouting"] -= 10
            scout = AntAgent(
                self.model.next_id(),
                self.model,
                self.model.recycling_center,
                role="scout",
                tribe_id=self.tribe_id,
                lifespan_multiplier=self.lifespan_multiplier,
                scent_sensitivity=self.scent_sensitivity,
                antenna_sensitivity=self.genome['antenna_sensitivity'],
                max_speed=self.genome['max_speed'],
                steering_fluidity=self.genome['steering_fluidity'],
            )
            scout.weights = [w + random.uniform(-0.05, 0.05) for w in self.weights]
            # Find empty adjacent position
            neighbors = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False)
            empty_neighbors = [n for n in neighbors if not any(self.model.grid.get_cell_list_contents([n])) and not self.model.obstacle_map[n[0], n[1]] and self.model.garbage_map[n[0], n[1]] == 0]
            if empty_neighbors:
                spawn_pos = self.random.choice(empty_neighbors)
                self.model.grid.place_agent(scout, spawn_pos)
                self.model.schedule.add(scout)

        if self.model.resource_inventory.get("scavenger", 0) >= 10:
            self.model.resource_inventory["scavenger"] -= 10
            scav = AntAgent(
                self.model.next_id(),
                self.model,
                self.model.recycling_center,
                role="scavenger",
                tribe_id=self.tribe_id,
                lifespan_multiplier=self.lifespan_multiplier,
                scent_sensitivity=self.scent_sensitivity,
                antenna_sensitivity=self.genome['antenna_sensitivity'],
                max_speed=self.genome['max_speed'],
                steering_fluidity=self.genome['steering_fluidity'],
            )
            scav.weights = [w + random.uniform(-0.05, 0.05) for w in self.weights]
            # Find empty adjacent position
            neighbors = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False)
            empty_neighbors = [n for n in neighbors if not any(self.model.grid.get_cell_list_contents([n])) and not self.model.obstacle_map[n[0], n[1]] and self.model.garbage_map[n[0], n[1]] == 0]
            if empty_neighbors:
                spawn_pos = self.random.choice(empty_neighbors)
                self.model.grid.place_agent(scav, spawn_pos)
                self.model.schedule.add(scav)

        # Build design/ecosystem: reduce hunger decay
        if self.model.resource_inventory.get("design", 0) >= 20 and self.model.resource_inventory.get("ecosystem", 0) >= 20:
            self.model.resource_inventory["design"] -= 20
            self.model.resource_inventory["ecosystem"] -= 20
            self.model.colony_hunger = max(0.0, self.model.colony_hunger - 0.05)

        # Metabolic Surplus tracking
        current_food = self.model.resource_inventory.get("food", 0)
        if current_food > self.last_food_count:
            self.colony_reserves += (current_food - self.last_food_count)
        self.last_food_count = current_food

        # Spawn princess when prosperous (queen birthing) - OR founder queens during liberation
        worker_count = sum(1 for a in self.model.schedule.agents if isinstance(a, AntAgent) and a.role in ["worker", "scavenger", "scout"])
        
        # Check if liberation event is active (high inhibitory pheromone = stress signal)
        liberation_active = self.model.inhibitory_pheromone_strength > 1.5
        
        if self.colony_reserves > 500 and worker_count > 50:
            if liberation_active:
                # Liberation Mode: Spawn founder queens instead of princesses
                self.colony_reserves -= 300  # Spend reserves
                founder_queen = QueenAgent(
                    self.model.next_id(),
                    self.model,
                    self.pos,
                    tribe_id=self.model.current_generation + self.model.liberation_events + 1,
                    lifespan_multiplier=self.lifespan_multiplier,
                    scent_sensitivity=self.scent_sensitivity,
                )
                founder_queen.genome = self.genome.copy()  # Inherit genome
                founder_queen.weights = [w + random.uniform(-0.1, 0.1) for w in self.weights]  # Mutate weights
                
                # Find empty adjacent position
                neighbors = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False)
                empty_neighbors = [n for n in neighbors if not any(self.model.grid.get_cell_list_contents([n])) and not self.model.obstacle_map[n[0], n[1]] and self.model.garbage_map[n[0], n[1]] == 0]
                if empty_neighbors:
                    spawn_pos = self.random.choice(empty_neighbors)
                    self.model.grid.place_agent(founder_queen, spawn_pos)
                    self.model.schedule.add(founder_queen)
                    
                    # Give founder queen initial seed swarm (2-4 ants)
                    seed_swarm_size = np.random.randint(2, 5)
                    for _ in range(seed_swarm_size):
                        seed_ant = AntAgent(
                            self.model.next_id(),
                            self.model,
                            spawn_pos,
                            role="worker",
                            tribe_id=founder_queen.tribe_id,
                            parent_queen=founder_queen
                        )
                        # Place near founder queen
                        dx, dy = np.random.randint(-1, 2), np.random.randint(-1, 2)
                        seed_pos = (max(0, min(self.model.width-1, spawn_pos[0] + dx)),
                                   max(0, min(self.model.height-1, spawn_pos[1] + dy)))
                        self.model.grid.place_agent(seed_ant, seed_pos)
                        self.model.schedule.add(seed_ant)
            else:
                # Normal Mode: Spawn princesses
                self.colony_reserves -= 300  # Spend reserves
                princess = PrincessAgent(
                    self.model.next_id(),
                    self.model,
                    self.pos,
                    parent_tribe=self.tribe_id,
                    parent_lifespan_multiplier=self.lifespan_multiplier,
                    parent_scent_sensitivity=self.scent_sensitivity,
                    parent_genome=self.genome,
                )
                # Find empty adjacent position
                neighbors = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False)
                empty_neighbors = [n for n in neighbors if not any(self.model.grid.get_cell_list_contents([n])) and not self.model.obstacle_map[n[0], n[1]] and self.model.garbage_map[n[0], n[1]] == 0]
                if empty_neighbors:
                    spawn_pos = self.random.choice(empty_neighbors)
                    self.model.grid.place_agent(princess, spawn_pos)
                    self.model.schedule.add(princess)

        # If there's extra garbage currency, also produce support workers
        if self.model.total_garbage_collected >= effective_spawn_cost:
            self.model.total_garbage_collected -= effective_spawn_cost
            new_ant = AntAgent(
                self.model.next_id(),
                self.model,
                self.model.recycling_center,
                role="worker",
                tribe_id=self.tribe_id,
                lifespan_multiplier=self.lifespan_multiplier,
                scent_sensitivity=self.scent_sensitivity,
                antenna_sensitivity=self.genome['antenna_sensitivity'],
                max_speed=self.genome['max_speed'],
                steering_fluidity=self.genome['steering_fluidity'],
            )
            # Find empty adjacent position
            neighbors = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False)
            empty_neighbors = [n for n in neighbors if not any(self.model.grid.get_cell_list_contents([n])) and not self.model.obstacle_map[n[0], n[1]] and self.model.garbage_map[n[0], n[1]] == 0]
            if empty_neighbors:
                spawn_pos = self.random.choice(empty_neighbors)
                self.model.grid.place_agent(new_ant, spawn_pos)
                self.model.schedule.add(new_ant)

        # Evolution: If colony performance improves, mutate genome
        if self.model.total_garbage_collected > self.previous_garbage:
            for key in self.genome:
                self.genome[key] *= random.uniform(0.95, 1.05)
        self.previous_garbage = self.model.total_garbage_collected

        # Royal pheromone pulse every 50 ticks
        if self.step_counter % 50 == 0:
            neighbors = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=True, radius=5)
            for n in neighbors:
                for agent in self.model.grid.get_cell_list_contents([n]):
                    if isinstance(agent, AntAgent):
                        agent.age = max(0, int(agent.age - 50))

class PrincessAgent(Agent):
    def __init__(self, unique_id: int, model: Any, pos: Tuple[int, int], parent_tribe: int = 0, parent_lifespan_multiplier: float = 1.0, parent_scent_sensitivity: float = 1.0, parent_genome: dict = None):
        super().__init__(unique_id, model)
        self.pos = pos
        self.state = "INCUBATE"
        self.stored_energy = 0
        self.nest_origin = pos  # Remember where she was born
        self.flight_vector = None  # For straight-line flight
        self.parent_tribe = parent_tribe
        self.parent_lifespan_multiplier = parent_lifespan_multiplier
        self.parent_scent_sensitivity = parent_scent_sensitivity
        self.parent_genome = parent_genome or {
            'antenna_sensitivity': 1.0,
            'max_speed': 1.0,
            'steering_fluidity': 0.1,
        }

    def step(self):
        if self.state == "INCUBATE":
            # Stay at nest, passively drain colony hunger
            if self.model.colony_hunger > 0:
                self.model.colony_hunger = max(0, self.model.colony_hunger - 0.1)
                self.stored_energy += 0.1
            if self.stored_energy > 100:
                self.state = "NUPTIAL_FLIGHT"
                # Choose random straight-line direction away from nest
                self.flight_vector = (random.uniform(-1, 1), random.uniform(-1, 1))
                # Normalize
                mag = math.sqrt(self.flight_vector[0]**2 + self.flight_vector[1]**2)
                self.flight_vector = (self.flight_vector[0]/mag, self.flight_vector[1]/mag)

        elif self.state == "NUPTIAL_FLIGHT":
            # Walk in straight line, ignoring pheromones and obstacles
            new_x = self.pos[0] + self.flight_vector[0]
            new_y = self.pos[1] + self.flight_vector[1]
            new_pos = (int(round(new_x)), int(round(new_y)))
            # Check bounds
            if 0 <= new_pos[0] < self.model.width and 0 <= new_pos[1] < self.model.height:
                # Move even through obstacles for nuptial flight
                self.model.grid.move_agent(self, new_pos)
            
            # Check distance from nest
            dist = math.sqrt((self.pos[0] - self.nest_origin[0])**2 + (self.pos[1] - self.nest_origin[1])**2)
            if dist >= self.model.width // 4:
                # Check for clear spot
                cell_contents = self.model.grid.get_cell_list_contents([self.pos])
                if len(cell_contents) == 1:  # Only herself
                    self.state = "FOUND_COLONY"

        elif self.state == "FOUND_COLONY":
            # Spawn new Queen and remove self
            new_tribe = self.model.next_tribe_id
            new_queen = QueenAgent(
                self.model.next_id(),
                self.model,
                self.pos,
                tribe_id=new_tribe,
                lifespan_multiplier=self.parent_lifespan_multiplier,
                scent_sensitivity=self.parent_scent_sensitivity,
            )
            new_queen.genome = self.parent_genome.copy()
            self.model.grid.place_agent(new_queen, self.pos)
            self.model.schedule.add(new_queen)
            self.model.queens_born += 1
            self.model.current_generation = self.model.queens_born
            self.model.next_tribe_id += 1
            # Celebration
            nearby_ants = self.model.grid.get_neighbors(self.pos, moore=True, include_center=False, radius=5)
            for agent in nearby_ants:
                if isinstance(agent, AntAgent):
                    agent.xp += 10
                    agent.energy_reserve = min(100.0, agent.energy_reserve + 10.0)
                    agent.sugar_saturation = min(1.0, agent.sugar_saturation + 0.2)
            self.model.grid.remove_agent(self)
            self.model.schedule.remove(self)

class AntAgent(Agent):
    def __init__(
        self,
        unique_id: int,
        model: Any,
        recycling_center: Tuple[int, int],
        role: str = "worker",
        tribe_id: int = 0,
        lifespan_multiplier: float = 1.0,
        scent_sensitivity: float = 1.0,
        antenna_sensitivity: float = 1.0,
        max_speed: float = 1.0,
        steering_fluidity: float = 0.1,
        is_hero: bool = False,
    ):
        super().__init__(unique_id, model)
        self.state = "EXPLORE"
        self.recycling_center = recycling_center
        self.role = role
        self.tribe_id = tribe_id
        self.carrying_resource = None
        self.is_hero = is_hero
        self.foraging_threshold = random.uniform(0.1, 0.9)
        if role == "scavenger":
            self.foraging_threshold *= 0.5
        elif role == "scout":
            self.foraging_threshold *= 0.2
        self.age = 0
        base_lifespan = random.randint(500, 1000)
        if is_hero:
            self.lifespan = 100000  # Infinite for heroes
        else:
            self.lifespan = int(base_lifespan * lifespan_multiplier)
        self.scent_sensitivity = scent_sensitivity
        self.last_pos = None
        self.steps_in_place = 0
        self.pickup_pos = None
        self.xp = 0

        # Neuromorphic Brain Structures
        # Central Complex (CX): Path Integration Vector
        self.cx_vector = [0.0, 0.0]

        # Heading and speed for vector-based movement
        self.heading = random.uniform(0, 2 * math.pi)  # radians
        self.speed = max_speed

        self.max_speed = max_speed

        # Antennal Tropotaxis parameters
        self.antenna_sensitivity = antenna_sensitivity
        self.steering_fluidity = steering_fluidity

        # Mushroom Body (MB): Sparse Coding for Learning
        self.kenyon_cells = [0.0] * 100  # 100 Kenyon cells, sparse (5% active)
        self.mb_weights = {}  # dict of (idx, action) -> strength

        # 2026 Frontier: Metabolic Liquid Neural Network (LNN)
        self.sugar_saturation = 0.1  # 0-1.0, intellect fuel level
        self.energy_reserve = 100.0  # 0-100, ATP/survival fuel (DISTINCT from sugar)
        self.neural_state = [0.0] * 10  # LNN hidden state (10 neurons base, 50 if super_intelligence)
        self.learning_rate = 0.1  # Modified by sugar level
        self.basal_survival_mode = False  # Emergency low-energy mode
        
        # Internal position for float precision
        self.internal_pos = None

        self.weights = [random.uniform(-1, 1) for _ in range(6)]
        
        # Track trophallaxis partners for visualization
        self.last_trophallaxis_partner = None
        
        # Trophallactic Federated Learning: store best resource location
        self.best_target_memory = None
        
        # 2026 Ultimate Stabilization: Energy-Backed Goal Locking (EBGL)
        self.goal_escrow = 0.0  # Staked sugar for goal commitment
        self.goal_locked = False  # Whether current goal is metabolically locked
        self.goal_lock_time = 0  # Steps since goal was locked
        self.goal_persistence_bonus = 0.0  # Reward for successful goal completion

    def step(self):
        if self.internal_pos is None:
            self.internal_pos = [float(self.pos[0]), float(self.pos[1])]
        self.age += 1
        if self.age >= self.lifespan:
            # Death: drop carried resource back onto the map
            if self.carrying_resource is not None:
                x, y = self.pos
                self.model.garbage_map[x, y] += 1
                self.model.garbage_type_map[x, y] = self.carrying_resource
                self.carrying_resource = None
            # Homeostatic Neuro-Modulation: Death beacon for stigmergic memory
            # Leave persistent pheromone trail (500 steps) to mark knowledge location
            neighbors = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=True, radius=3)
            for n in neighbors:
                self.model.death_beacon_map[n[0], n[1]] = max(self.model.death_beacon_map[n[0], n[1]], 500)
            self.model.colony_biomass += 5
            self.model.grid.remove_agent(self)
            self.model.schedule.remove(self)
            return

        # Threshold Logic: Only work if colony needs it
        if self.model.colony_hunger < self.foraging_threshold and self.state == "EXPLORE":
            return

        if self.state == "EXPLORE":
            self.explore_logic()
        elif self.state == "RETURN":
            self.return_logic()

        # Stuck detection and random jump
        if self.last_pos == self.pos:
            self.steps_in_place += 1
        else:
            self.last_pos = self.pos
            self.steps_in_place = 0

        if self.steps_in_place > 10:
            alternatives = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False)
            alternatives = [n for n in alternatives if not self.model.obstacle_map[n[0], n[1]]]
            if alternatives:
                jump = self.random.choice(alternatives)
                self.model.grid.move_agent(self, jump)
            self.steps_in_place = 0

        # 2026 Frontier: Metabolic Logic
        self.update_lnn_dynamics()
        self.perform_trophallaxis()
        
        # Trophallactic Federated Learning: Check for collision-based knowledge sharing
        cell_mates = self.model.grid.get_cell_list_contents([self.pos])
        for mate in cell_mates:
            if isinstance(mate, AntAgent) and mate.unique_id != self.unique_id:
                self.trophallaxis(mate)
                break  # Only share with one agent per step
        
        # 2026 Ultimate Stabilization: Energy-Backed Goal Locking (EBGL) Management
        if self.goal_locked:
            self.goal_lock_time += 1
            
            # Goal Failure Check: If energy drops too low before reaching target
            if self.energy_reserve < 20.0 and self.state == "EXPLOIT_MEMORY":
                # Metabolic Proof-of-Failure: Lose the staked sugar
                self.goal_locked = False
                self.state = "EXPLORE"
                self.best_target_memory = None
                self.goal_escrow = 0.0
                # Penalty for goal failure
                self.xp = max(0, self.xp - 5)
                self.model.colony_hunger += 0.05  # Slight colony stress
        
        # Sugar decay over time
        self.sugar_saturation = max(0.0, self.sugar_saturation - 0.01)
        
        # Energy reserve decay and consumption
        energy_burned = 0.5  # Basal metabolic rate
        self.energy_reserve = max(0.0, self.energy_reserve - energy_burned)
        if self.state == "EXPLORE" or self.state == "RETURN":
            movement_cost = 0.2
            self.energy_reserve = max(0.0, self.energy_reserve - movement_cost)
            energy_burned += movement_cost
        
        # Track total energy burned for MPI calculation
        self.model.total_energy_burned += energy_burned
        
        # Homeostatic Neuro-Modulation: Survival override
        if self.energy_reserve < 30.0:
            self.basal_survival_mode = True
            self.speed = self.max_speed * 0.5  # Slow down to conserve energy
        else:
            self.basal_survival_mode = False
            self.speed = self.max_speed

    def update_lnn_dynamics(self):
        """Update Liquid Neural Network with ODE dynamics based on metabolic state."""
        # Time constant tau inversely proportional to sugar saturation
        tau = 1.0 / (0.1 + self.sugar_saturation)
        
        # Simple ODE: dh/dt = -h/tau + input
        sensory_input = self.get_sensory_input()
        for i in range(len(self.neural_state)):
            dt = 0.1
            self.neural_state[i] += dt * (-self.neural_state[i] / tau + sensory_input)
        
        # Update learning rate based on sugar (high sugar = fast learning)
        self.learning_rate = 0.05 + (self.sugar_saturation * 0.45)

    def get_sensory_input(self):
        """Get combined sensory input for LNN."""
        left_pos, right_pos = self.get_antenna_positions()
        left_val = self.get_pheromone_at(left_pos)
        right_val = self.get_pheromone_at(right_pos)
        return (left_val + right_val) / 2.0

    def perform_trophallaxis(self):
        """Share sugar and neural weights with nearby nestmates (social learning)."""
        neighbors = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False)
        for neighbor_pos in neighbors:
            for agent in self.model.grid.get_cell_list_contents([neighbor_pos]):
                if isinstance(agent, AntAgent) and agent.tribe_id == self.tribe_id:
                    # Payload Protection: Agents in RETURN state guard their sugar
                    if self.state != "RETURN" and agent.state != "RETURN":
                        # Share 50% of sugar only if neither is carrying payload
                        avg_sugar = (self.sugar_saturation + agent.sugar_saturation) / 2.0
                        self.sugar_saturation = avg_sugar
                        agent.sugar_saturation = avg_sugar
                    
                    # Always share neural weights for social learning
                    for i in range(len(self.neural_state)):
                        avg_state = (self.neural_state[i] + agent.neural_state[i]) / 2.0
                        self.neural_state[i] = avg_state
                        agent.neural_state[i] = avg_state
                    
                    self.last_trophallaxis_partner = agent.unique_id
                    break

    def trophallaxis(self, other_agent):
        """Trophallactic Federated Learning: Proof-of-Success Data Transfer with Payload Protection"""
        sugar_diff = self.sugar_saturation - other_agent.sugar_saturation
        
        # Payload Protection Protocol: Agents carrying payload (RETURN state) guard their sugar
        if self.state != "RETURN" and sugar_diff > 0.2:
            # Metabolic sharing (only for non-returning agents)
            transfer_amount = self.sugar_saturation * 0.10
            self.sugar_saturation -= transfer_amount
            other_agent.sugar_saturation += transfer_amount
        
        # Knowledge sharing: Always transfer best_target_memory if available
        if self.best_target_memory is not None:
            # Energy-Backed Goal Locking (EBGL): Stake sugar to commit to goal
            stake_amount = min(0.2, other_agent.sugar_saturation * 0.5)  # Stake up to 20% or half available
            
            if other_agent.sugar_saturation >= stake_amount and not other_agent.goal_locked:
                # Lock the goal with metabolic commitment
                other_agent.best_target_memory = self.best_target_memory
                other_agent.state = "EXPLOIT_MEMORY"
                other_agent.goal_escrow = stake_amount
                other_agent.goal_locked = True
                other_agent.goal_lock_time = 0
                other_agent.sugar_saturation -= stake_amount
                
                # Metabolic commitment signal
                self.model.swarm_intellect += 5.0  # Knowledge transfer boosts colony intellect

    def get_metabolic_preference(self):
        """Softmax utility to choose between Nectar and Garbage based on sugar level."""
        # High sugar = ambitious (target nectar); Low sugar = desperate (take garbage)
        nectar_utility = self.sugar_saturation * 2.0  # Prefer nectar when full
        garbage_utility = 1.0 - self.sugar_saturation  # Prefer garbage when hungry
        
        import numpy as np
        utilities = np.array([nectar_utility, garbage_utility])
        probs = np.exp(utilities) / np.sum(np.exp(utilities))
        return "nectar" if probs[0] > probs[1] else "garbage"

    def get_valid_neighbors(self):
        neighbors = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False)
        # Filter out obstacles AND garbage (garbage is now a physical barrier)
        valid = [n for n in neighbors if not self.model.obstacle_map[n[0], n[1]] and self.model.garbage_map[n[0], n[1]] == 0]
        return valid

    def get_antenna_positions(self):
        """Calculate left and right antenna positions based on heading."""
        forward_x = math.cos(self.heading)
        forward_y = math.sin(self.heading)
        left_x = forward_x * math.cos(math.pi/2) - forward_y * math.sin(math.pi/2)
        left_y = forward_x * math.sin(math.pi/2) + forward_y * math.cos(math.pi/2)
        right_x = forward_x * math.cos(-math.pi/2) - forward_y * math.sin(-math.pi/2)
        right_y = forward_x * math.sin(-math.pi/2) + forward_y * math.cos(-math.pi/2)
        
        left_pos = (self.internal_pos[0] + forward_x + left_x * 0.5, self.internal_pos[1] + forward_y + left_y * 0.5)
        right_pos = (self.internal_pos[0] + forward_x + right_x * 0.5, self.internal_pos[1] + forward_y + right_y * 0.5)
        return left_pos, right_pos

    def get_pheromone_at(self, pos):
        """Get pheromone value at a float position, nearest neighbor."""
        x, y = pos
        x0, y0 = round(x), round(y)
        if 0 <= x0 < self.model.width and 0 <= y0 < self.model.height:
            return self.model.pheromone_map[x0, y0]
        return 0.0

    def update_mushroom_body(self, view, action):
        """Hebbian learning with sparse coding."""
        # Project view to Kenyon cells (sparse: only 5% active)
        view_str = str(view)
        hash_val = int(hashlib.md5(view_str.encode()).hexdigest(), 16)
        active_indices = []
        for i in range(100):
            if (hash_val >> i) & 1:  # Simple way to get sparse activation
                active_indices.append(i)
            if len(active_indices) >= 5:  # 5% of 100
                break
        # Strengthen connections from active Kenyon cells to action
        for idx in active_indices:
            key = (idx, action)
            if key not in self.mb_weights:
                self.mb_weights[key] = 0.0
            self.mb_weights[key] += 0.1

    def get_mb_action(self, view):
        """Get action from Mushroom Body."""
        view_str = str(view)
        hash_val = int(hashlib.md5(view_str.encode()).hexdigest(), 16)
        active_indices = []
        for i in range(100):
            if (hash_val >> i) & 1:
                active_indices.append(i)
            if len(active_indices) >= 5:
                break
        actions = ['forward', 'left', 'right']
        scores = [0.0] * len(actions)
        for idx in active_indices:
            for j, action in enumerate(actions):
                key = (idx, action)
                scores[j] += self.mb_weights.get(key, 0.0)
        max_idx = scores.index(max(scores))
        return actions[max_idx]

    def explore_logic(self):
        # Handle EXPLOIT_MEMORY state: move towards best_target_memory
        if self.state == "EXPLOIT_MEMORY" and self.best_target_memory is not None:
            target_x, target_y = self.best_target_memory
            dx = target_x - self.internal_pos[0]
            dy = target_y - self.internal_pos[1]
            dist = math.sqrt(dx**2 + dy**2)
            if dist < 1.0:  # Reached target
                # Goal Success: Unlock and reward
                self.state = "EXPLORE"
                self.best_target_memory = None
                self.goal_locked = False
                # Metabolic reward for success
                if self.goal_escrow > 0:
                    reward = self.goal_escrow * 1.5  # 50% bonus
                    self.sugar_saturation = min(1.0, self.sugar_saturation + reward)
                    energy_collected = reward * 10
                    self.energy_reserve = min(100.0, self.energy_reserve + energy_collected)
                    self.model.total_energy_collected += energy_collected
                    self.xp += 25  # Experience bonus
                    self.goal_escrow = 0.0
                    self.goal_persistence_bonus = reward
                return
            else:
                # Goal Persistence: Stay locked on target
                if self.goal_locked:
                    self.heading = math.atan2(dy, dx)
                    # Proceed with movement below - no distractions allowed
                else:
                    self.heading = math.atan2(dy, dx)
                    # Proceed with movement below
        
        # 2026 Frontier: Check for Nectar first (premium resource) unless in survival mode
        all_neighbors = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False)
        
        # Homeostatic Neuro-Modulation: In survival mode, ignore nectar and prioritize garbage
        if not self.basal_survival_mode:
            # Look for adjacent nectar (high priority)
            for neighbor in all_neighbors:
                if self.model.nectar_map[neighbor[0], neighbor[1]] > 0:
                    # Consume nectar!
                    self.model.nectar_map[neighbor[0], neighbor[1]] -= 1
                    self.sugar_saturation = min(1.0, self.sugar_saturation + 0.5)  # Massive sugar boost
                    energy_collected = 20.0  # Energy boost from nectar
                    self.energy_reserve = min(100.0, self.energy_reserve + energy_collected)
                    self.model.total_energy_collected += energy_collected
                    self.model.total_nectar_collected += 1
                    self.model.swarm_intellect += 10.0  # Boost colony intellect
                    self.state = "RETURN"
                    self.carrying_resource = 200  # Special nectar marker
                    self.pickup_pos = self.pos
                    self.best_target_memory = neighbor  # Store best resource location
                    return
        
        # Look for adjacent garbage to mine (always priority in survival mode)
        for neighbor in all_neighbors:
            if self.model.garbage_map[neighbor[0], neighbor[1]] > 0:
                # Mine the garbage!
                self.model.garbage_map[neighbor[0], neighbor[1]] -= 1
                if self.model.garbage_map[neighbor[0], neighbor[1]] == 0:
                    # Remove garbage agent
                    garbage_agent = self.model.garbage_agents.pop(neighbor, None)
                    if garbage_agent:
                        self.model.grid.remove_agent(garbage_agent)
                    # Add pheromone agent
                    pheromone_agent = PheromoneAgent(self.model.next_id(), self.model, neighbor, 0.0)
                    self.model.pheromone_agents[neighbor] = pheromone_agent
                    self.model.grid.place_agent(pheromone_agent, neighbor)
                self.pickup_pos = self.pos
                self.carrying_resource = self.model.garbage_type_map[neighbor[0], neighbor[1]]
                self.model.garbage_type_map[neighbor[0], neighbor[1]] = 0
                self.model.total_garbage_collected += 1
                self.sugar_saturation = min(1.0, self.sugar_saturation + 0.1)  # Small sugar boost
                energy_collected = 10.0  # Energy boost from garbage
                self.energy_reserve = min(100.0, self.energy_reserve + energy_collected)
                self.model.total_energy_collected += energy_collected
                self.state = "RETURN"
                # Learn success: strengthen MB for current view and 'pickup'
                left_pos, right_pos = self.get_antenna_positions()
                view = [self.get_pheromone_at(left_pos), self.get_pheromone_at(right_pos), self.model.colony_hunger]
                self.update_mushroom_body(view, 'pickup')
                self.best_target_memory = neighbor  # Store best resource location
                return

        # No resources; use Antennal Tropotaxis for steering
        left_pos, right_pos = self.get_antenna_positions()
        left_val = self.get_pheromone_at(left_pos)
        right_val = self.get_pheromone_at(right_pos)

        # Steering torque
        steering_torque = (left_val - right_val) * self.antenna_sensitivity * self.steering_fluidity
        self.heading += steering_torque

        # Mushroom Body influence
        view = [left_val, right_val, self.model.colony_hunger]
        mb_action = self.get_mb_action(view)
        if mb_action == 'left':
            self.heading -= 0.1
        elif mb_action == 'right':
            self.heading += 0.1

        # Move using trigonometry
        dx = math.cos(self.heading) * self.speed
        dy = math.sin(self.heading) * self.speed
        new_x = self.internal_pos[0] + dx
        new_y = self.internal_pos[1] + dy

        # Update CX vector
        self.cx_vector[0] += dx
        self.cx_vector[1] += dy

        # Round to grid for Mesa
        grid_x = round(new_x)
        grid_y = round(new_y)

        if 0 <= grid_x < self.model.width and 0 <= grid_y < self.model.height and not self.model.obstacle_map[grid_x, grid_y] and self.model.garbage_map[grid_x, grid_y] == 0:
            self.internal_pos = [new_x, new_y]
            self.model.grid.move_agent(self, (grid_x, grid_y))
        else:
            # Bounce or random
            self.heading += math.pi  # Turn around
            # Try again with new heading
            dx = math.cos(self.heading) * self.speed
            dy = math.sin(self.heading) * self.speed
            new_x = self.internal_pos[0] + dx
            new_y = self.internal_pos[1] + dy
            grid_x = round(new_x)
            grid_y = round(new_y)
            if 0 <= grid_x < self.model.width and 0 <= grid_y < self.model.height and not self.model.obstacle_map[grid_x, grid_y] and self.model.garbage_map[grid_x, grid_y] == 0:
                self.internal_pos = [new_x, new_y]
                self.model.grid.move_agent(self, (grid_x, grid_y))
            # Else stay

        # Stuck detection
        if self.last_pos == self.pos:
            self.steps_in_place += 1
        else:
            self.last_pos = self.pos
            self.steps_in_place = 0

        if self.steps_in_place > 10:
            self.heading = random.uniform(0, 2 * math.pi)
            self.steps_in_place = 0

    def return_logic(self):
        # Home Vector: Calculate normalized direction to nest
        nest_x, nest_y = self.recycling_center
        dx = nest_x - self.internal_pos[0]
        dy = nest_y - self.internal_pos[1]
        dist = math.sqrt(dx**2 + dy**2)
        if dist > 0:
            self.heading = math.atan2(dy, dx)
        
        # Pheromone Reinforcement: Drop Home-Trail pheromone
        self.model.home_pheromone_map[self.pos[0], self.pos[1]] += 5.0
        
        # Obstacle Avoidance: If direct path blocked, implement right-hand rule
        # For simplicity, check if next position is obstacle, if so, turn right
        next_x = self.internal_pos[0] + math.cos(self.heading) * self.speed
        next_y = self.internal_pos[1] + math.sin(self.heading) * self.speed
        next_pos = (int(round(next_x)), int(round(next_y)))
        if (0 <= next_pos[0] < self.model.width and 0 <= next_pos[1] < self.model.height and
            self.model.obstacle_map[next_pos[0], next_pos[1]]):
            # Turn right (90 degrees)
            self.heading += math.pi / 2
        
        # Move using calculated heading
        dx = math.cos(self.heading) * self.speed
        dy = math.sin(self.heading) * self.speed
        new_x = self.internal_pos[0] + dx
        new_y = self.internal_pos[1] + dy
        grid_x = round(new_x)
        grid_y = round(new_y)
        if 0 <= grid_x < self.model.width and 0 <= grid_y < self.model.height and not self.model.obstacle_map[grid_x, grid_y] and self.model.garbage_map[grid_x, grid_y] == 0:
            self.internal_pos = [new_x, new_y]
            self.model.grid.move_agent(self, (grid_x, grid_y))
        else:
            # If blocked, try turning right and moving
            self.heading += math.pi / 2
            dx = math.cos(self.heading) * self.speed
            dy = math.sin(self.heading) * self.speed
            new_x = self.internal_pos[0] + dx
            new_y = self.internal_pos[1] + dy
            grid_x = round(new_x)
            grid_y = round(new_y)
            if 0 <= grid_x < self.model.width and 0 <= grid_y < self.model.height and not self.model.obstacle_map[grid_x, grid_y] and self.model.garbage_map[grid_x, grid_y] == 0:
                self.internal_pos = [new_x, new_y]
                self.model.grid.move_agent(self, (grid_x, grid_y))
        
        # Arrival Check: If at nest, transfer sugar and switch to EXPLORE
        if abs(self.internal_pos[0] - nest_x) < 1.0 and abs(self.internal_pos[1] - nest_y) < 1.0:
            # Transfer sugar to colony reserves
            if hasattr(self.model, 'queens') and self.model.queens:
                queen = self.model.queens[0]  # Assuming one queen
                queen.colony_reserves += self.sugar_saturation
            self.sugar_saturation = 0.0
            self.state = "EXPLORE"
            self.cx_vector = [0.0, 0.0]  # Reset vector
            self.model.colony_hunger = max(0.0, self.model.colony_hunger - 0.1)
            # Handle resource delivery as before
            if self.carrying_resource is not None:
                # 2026 Frontier: Handle Nectar Delivery (Special resource)
                if self.carrying_resource == 200:
                    # Nectar delivered to Queen!
                    self.model.evolution_points += 100  # Major evolution boost
                    self.model.swarm_intellect += 50  # Strong intellect boost
                    # Find queen and boost her
                    for agent in self.model.schedule.agents:
                        if isinstance(agent, QueenAgent) and agent.tribe_id == self.tribe_id:
                            agent.health = min(100, agent.health + 30)
                            break
                    # Status update: reward the worker for bringing nectar
                    self.xp += 50
                    energy_collected = 20.0
                    self.energy_reserve = min(100.0, self.energy_reserve + energy_collected)
                    self.model.total_energy_collected += energy_collected
                    self.sugar_saturation = min(1.0, self.sugar_saturation + 0.5)
                elif self.carrying_resource == 99:
                    # ultra resource event
                    self.model.colony_biomass += 200
                    # Find empty positions for spawning
                    neighbors = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False, radius=3)
                    empty_neighbors = [n for n in neighbors if not any(self.model.grid.get_cell_list_contents([n])) and not self.model.obstacle_map[n[0], n[1]] and self.model.garbage_map[n[0], n[1]] == 0]
                    if empty_neighbors:
                        for i in range(min(50, len(empty_neighbors))):
                            spawn_pos = empty_neighbors[i % len(empty_neighbors)]
                            # Double-check the position is still empty
                            if not any(self.model.grid.get_cell_list_contents([spawn_pos])):
                                child = AntAgent(
                                    self.model.next_id(),
                                    self.model,
                                    self.model.recycling_center,
                                    role="worker",
                                    tribe_id=self.model.current_generation,
                                    lifespan_multiplier=1.2,
                                    scent_sensitivity=1.2,
                                    antenna_sensitivity=self.antenna_sensitivity,
                                    max_speed=self.speed,
                                    steering_fluidity=self.steering_fluidity,
                                )
                                child.weights = [w + random.uniform(-0.02, 0.02) for w in self.weights]
                                self.model.grid.place_agent(child, spawn_pos)
                                self.model.schedule.add(child)
                    # Status update: reward the worker for bringing ultra resource
                    self.xp += 100
                    energy_collected = 50.0
                    self.energy_reserve = min(100.0, self.energy_reserve + energy_collected)
                    self.model.total_energy_collected += energy_collected
                    self.sugar_saturation = min(1.0, self.sugar_saturation + 1.0)
                else:
                    resource_name = self.model.resource_type_map.get(self.carrying_resource, "food")
                    self.model.resource_inventory[resource_name] += 1
                    distance = abs(self.pos[0] - self.pickup_pos[0]) + abs(self.pos[1] - self.pickup_pos[1])
                    if distance > 20:
                        self.xp += 10
                        self.model.colony_biomass += 10
                    else:
                        self.xp += 1
                        self.model.colony_biomass += 1
                self.carrying_resource = None
            return
