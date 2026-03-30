from mesa.visualization.modules import CanvasGrid, ChartModule, TextElement
from mesa.visualization.ModularVisualization import ModularServer
from model import AntColonyModel
from agent import AntAgent, RockAgent, GarbageAgent, PheromoneAgent, QueenAgent, PrincessAgent


def agent_portrayal(agent):
    if isinstance(agent, PheromoneAgent):
        # Color based on pheromone value: 0 = white, >5 = bright yellow
        intensity = min(agent.value / 5.0, 1.0)
        r = int(255 * intensity)
        g = int(255 * intensity)
        b = int(255 * (1 - intensity * 0.5))  # White to yellow
        color = f"#{r:02x}{g:02x}{b:02x}"
        return {"Shape": "rect", "Filled": "true", "Layer": 0, "Color": color, "w": 1, "h": 1}

    if isinstance(agent, RockAgent):
        return {"Shape": "rect", "Filled": "true", "Layer": 1, "Color": "#333333", "w": 1, "h": 1}

    if isinstance(agent, GarbageAgent):
        # 2026 Frontier: Different colors for garbage vs nectar
        # Check if this is a nectar agent by checking the agent's position in nectar_map
        if hasattr(agent, 'model') and agent.pos and agent.model.nectar_map[agent.pos[0], agent.pos[1]] > 0:
            color = "magenta"  # Glowing magenta for nectar
        else:
            color = "saddlebrown"  # Brown for regular garbage
        return {"Shape": "rect", "Filled": "true", "Layer": 1, "Color": color, "w": 1, "h": 1}

    if isinstance(agent, AntAgent):
        ratio = min(1.0, agent.age / agent.lifespan) if hasattr(agent, "age") and hasattr(agent, "lifespan") else 0.0
        base_colors = ["00", "33", "66", "99", "CC", "FF"]
        tribe = getattr(agent, "tribe_id", 0) % len(base_colors)
        base = base_colors[tribe]
        if agent.state == "EXPLORE":
            color = f"#{base}00FF"
        elif agent.state == "RETURN":
            color = f"#{base}0000"
        elif agent.state == "EXPLOIT_MEMORY":
            color = "yellow"
            # EBGL Lock Visualization: Show commitment level
            if hasattr(agent, 'goal_locked') and agent.goal_locked:
                # Locked ants have a pulsing border based on lock persistence
                persistence_ratio = min(1.0, agent.goal_persistence_bonus / 10.0)
                stroke_width = 2
                stroke_color = "orange" if persistence_ratio > 0.5 else "red"
                # Add escrow amount as text overlay
                escrow_text = f"{agent.goal_escrow:.1f}" if agent.goal_escrow > 0 else ""
            else:
                stroke_width = 0
                stroke_color = None
                escrow_text = ""
        # Age fading towards gray
        gray_level = int(150 + 105 * ratio)
        if ratio > 0.7:
            color = f"#{gray_level:02x}{gray_level:02x}{gray_level:02x}"

        # Initialize stroke variables
        stroke_width = 0
        stroke_color = None
        escrow_text = ""

        # EBGL Lock Visualization: Show commitment level
        if agent.state == "EXPLOIT_MEMORY" and hasattr(agent, 'goal_locked') and agent.goal_locked:
            # Locked ants have a pulsing border based on lock persistence
            persistence_ratio = min(1.0, agent.goal_persistence_bonus / 10.0)
            stroke_width = 2
            stroke_color = "orange" if persistence_ratio > 0.5 else "red"
            escrow_text = f"{agent.goal_escrow:.1f}" if agent.goal_escrow > 0 else ""

        # 2026 Frontier: Metabolic Glow for High Sugar Ants (only if not EBGL locked)
        if agent.sugar_saturation > 0.8 and stroke_width == 0:
            stroke_width = 2
            stroke_color = "magenta"
        elif agent.sugar_saturation > 0.5 and stroke_width == 0:
            stroke_width = 1
            stroke_color = "cyan"

        # Homeostatic Neuro-Modulation: Critical energy visualization (red flashing)
        if agent.energy_reserve < 30.0:
            color = "red"
            # Flashing effect: alternate opacity based on step counter
            if hasattr(agent.model, 'schedule') and agent.model.schedule.steps % 2 == 0:
                color = "#FF6666"  # Lighter red for flash

        portrayal = {
            "Shape": "circle",
            "Filled": "true",
            "Layer": 2,
            "r": 0.5,
            "Color": color,
            "Stroke": stroke_width,
        }
        if stroke_color:
            portrayal["StrokeColor"] = stroke_color
        return portrayal

    if isinstance(agent, PrincessAgent):
        color = "purple" if agent.state == "INCUBATE" else "magenta"
        return {
            "Shape": "circle",
            "Filled": "true",
            "Layer": 4,
            "Color": color,
            "r": 0.8,
        }

    if isinstance(agent, QueenAgent):
        # Founder Queen Visual Distinction: Cyan/White aura vs Gold
        if hasattr(agent, 'is_founder') and agent.is_founder:
            color = "cyan"  # Founder queens have cyan aura
            stroke_color = "white"
            stroke_width = 2
        else:
            color = "gold"  # Original queen is gold
            stroke_color = None
            stroke_width = 0
            
        portrayal = {
            "Shape": "circle",
            "Filled": "true",
            "Layer": 3,
            "Color": color,
            "r": 1.0,
            "Stroke": stroke_width,
        }
        if stroke_color:
            portrayal["StrokeColor"] = stroke_color
            
        # Homeostatic Neuro-Modulation: Distress signal when population low
        worker_count = sum(1 for a in agent.model.schedule.agents if isinstance(a, AntAgent) and a.role in ["worker", "scavenger", "scout"])
        if worker_count < 10:
            portrayal["Stroke"] = 3
            portrayal["StrokeColor"] = "red"
        
        return portrayal

    return None


class PopulationText(TextElement):
    def render(self, model):
        population = sum(1 for a in model.schedule.agents if isinstance(a, AntAgent))
        return f"Population: {population}"


class GenerationText(TextElement):
    def render(self, model):
        return f"Generation (Queens born): {model.queens_born}"


class HomeostasisText(TextElement):
    def render(self, model):
        # Calculate average energy reserve across all ants
        ants = [a for a in model.schedule.agents if isinstance(a, AntAgent)]
        if ants:
            avg_energy = sum(a.energy_reserve for a in ants) / len(ants)
            critical_count = sum(1 for a in ants if a.energy_reserve < 30.0)
            return f"Colony Energy: {avg_energy:.1f} | Critical Ants: {critical_count}"
        return "Colony Energy: N/A"


class SwarmIntellectText(TextElement):
    def render(self, model):
        return f"🧠 Swarm Intellect: {int(model.swarm_intellect)}/1000"


class EvolutionText(TextElement):
    def render(self, model):
        unlocked = []
        if model.unlocked_abilities['global_communication']:
            unlocked.append("📡")
        if model.unlocked_abilities['super_intelligence']:
            unlocked.append("🚀")
        if model.unlocked_abilities['hero_scout']:
            unlocked.append("⭐")
        abilities = " ".join(unlocked) if unlocked else "🔒"
        return f"Evolution Points: {model.evolution_points}/1000 | Unlocked: {abilities}"


class NectarText(TextElement):
    def render(self, model):
        return f"🍯 Nectar Collected: {model.total_nectar_collected} | 🗑️ Garbage: {model.total_garbage_collected}"


class ColonyHealthText(TextElement):
    def render(self, model):
        mpi = f"{model.metabolic_persistence_index:.2f}"
        entropy = f"{model.colony_entropy:.2f}"
        density = f"{model.colony_density:.3f}"
        liberation = model.liberation_events
        return f"🏥 MPI: {mpi} | Σ: {entropy} | Density: {density} | Liberations: {liberation}"


class InhibitoryPheromoneText(TextElement):
    def render(self, model):
        strength = f"{model.inhibitory_pheromone_strength:.2f}"
        kdr = f"{model.knowledge_diffusion_rate:.2f}"
        return f"🧠 Inhibitory: {strength} | KDR: {kdr}"


class LifespanText(TextElement):
    def render(self, model):
        active_workers = [a for a in model.schedule.agents if isinstance(a, AntAgent)]
        if not active_workers:
            avg_life = 0
        else:
            avg_life = int(sum(a.lifespan for a in active_workers) / len(active_workers))
        return f"Average Lifespan: {avg_life}"


class RecycledText(TextElement):
    def render(self, model):
        return f"Total Garbage Recycled: {model.total_garbage_collected}"


class HeroBrainText(TextElement):
    def render(self, model):
        return f"Queens Born: {model.queens_born}, Biomass: {model.colony_biomass}"


grid = CanvasGrid(agent_portrayal, 100, 100, 800, 800)
population_text = PopulationText()
generation_text = GenerationText()
lifespan_text = LifespanText()
recycled_text = RecycledText()
swarm_intellect_text = SwarmIntellectText()
evolution_text = EvolutionText()
nectar_text = NectarText()
colony_health_text = ColonyHealthText()
inhibitory_text = InhibitoryPheromoneText()

population_chart = ChartModule(
    [{"Label": "Population", "Color": "#0000FF"}],
    data_collector_name="datacollector"
)

intellect_chart = ChartModule(
    [{"Label": "SwarmIntellect", "Color": "#FF00FF"}],
    data_collector_name="datacollector"
)

evolution_chart = ChartModule(
    [{"Label": "EvolutionPoints", "Color": "#00FF00"}],
    data_collector_name="datacollector"
)

hero_brain_text = HeroBrainText()
homeostasis_text = HomeostasisText()

server = ModularServer(
    AntColonyModel,
    [grid, 
     population_text, 
     generation_text, 
     swarm_intellect_text,
     evolution_text,
     nectar_text,
     colony_health_text,
     inhibitory_text,
     lifespan_text, 
     recycled_text, 
     hero_brain_text,
     homeostasis_text,
     population_chart,
     intellect_chart,
     evolution_chart],
    "🐜 2026 Frontier: Metabolic Neuromorphic Ant Swarm 🧠🍯",
    {
        "width": 30,
        "height": 30,
        "initial_ants": 20,
    },
)
