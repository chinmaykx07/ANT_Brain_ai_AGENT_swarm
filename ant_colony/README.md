# 🧠 2026 Frontier: Metabolic Neuromorphic Ant Swarm Intelligence

This project is a cutting-edge multi-agent AI simulation that models the complete biological brain structures of ants, featuring **Homeostatic Neuro-Modulation (HNM)** to prevent extinction through metabolic homeostasis.

## 🧬 Advanced Biological AI Features

### **Neuromorphic Brain Structures**
1. **Central Complex (CX)**: Vector-based path integration for dead reckoning navigation
2. **Mushroom Body (MB)**: Sparse coding neural network for associative learning
3. **Antennal Tropotaxis**: Differential steering based on pheromone gradients
4. **Liquid Neural Networks (LNN)**: ODE-based neural dynamics with metabolic time constants

### **Metabolic Homeostasis System**
1. **Dual Fuel Economy**: Sugar saturation (intellect boost) vs Energy reserve (survival fuel)
2. **Homeostatic Neuro-Modulation**: Survival overrides when energy < 30
3. **Emergency Reproduction**: Biomass-based spawning when population < 10
4. **Stigmergic Memory**: Death beacons preserve knowledge across generations

### **Evolution & Adaptation**
1. **Genetic Optimization**: Queen genome evolution with trait inheritance
2. **Trophallaxis**: Social learning through neural weight sharing
3. **Evolutionary Milestones**: Unlocked abilities at evolution points thresholds
4. **Swarm Intellect**: Collective intelligence scaling with colony performance

## 🚀 How to Run

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Launch the simulation:**
   ```bash
   python run.py
   ```

3. **Access the web interface at:** `http://localhost:8521`

## 📊 What to Observe

- **Red Flashing Ants**: Critical energy levels (< 30)
- **Queen Distress Signal**: Red outline when population < 10
- **Metabolic Auras**: Magenta glow (high sugar), cyan glow (moderate sugar)
- **J-Curve Recovery**: Population drops → emergency spawning → stable homeostasis
- **Evolution Dashboard**: Track intellect, evolution points, and unlocked abilities

## 🧪 Testing Homeostasis

Run the homeostasis test:
```bash
python test_hnm.py
```

This verifies the HNM system prevents the "Too Smart to Survive" extinction spiral.

## 📁 Project Structure

- `agent.py`: AntAgent, QueenAgent, PrincessAgent with neuromorphic brains
- `model.py`: Simulation environment with pheromone maps and evolution tracking
- `server.py`: Web visualization with homeostasis dashboard
- `test_hnm.py`: Homeostatic Neuro-Modulation verification
- `hero_brain.json`: Exported ant brain data
- `AntBrain.cs`: Unity/C# implementation for game engines

## 🎯 2026 Prime Best AI Achievement

This simulation demonstrates **true metabolic homeostasis** in swarm intelligence, where individual agents sacrifice intellect for survival when needed, ensuring long-term colony viability through biological accuracy.

When the browser tab opens, hit **Start**. Watch the blue dots. As soon as one randomly bumps into the corner with the food, it will turn red and run back to the center. Very shortly after, you will see the swarm completely lock onto that trail.

Let me know when you have it running or if you want to tweak the ant's "brain" further (like adding obstacle avoidance or multiple food sources)!

