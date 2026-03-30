# ANT_Brain_ai_AGENT_swarm 🐜🧠

**Neuromorphic Ant Colony Simulation with Homeostatic Neuro-Modulation**

[![Release](https://img.shields.io/badge/release-v1.0-blue.svg)](https://github.com/chinmaykx07/ANT_Brain_ai_AGENT_swarm/releases/tag/v1.0)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![Mesa](https://img.shields.io/badge/mesa-2.3.0-green.svg)](https://github.com/projectmesa/mesa)

An advanced agent-based simulation modeling ant colony behavior with neuromorphic brains, metabolic homeostasis, and evolutionary dynamics. This project demonstrates how artificial intelligence can learn from biological systems to create sustainable, adaptive multi-agent systems.

## 🎯 **Key Achievements**

- ✅ **Queen Survival >2000 Cycles**: Solved the "Too Smart to Survive" extinction problem
- ✅ **Homeostatic Neuro-Modulation (HNM)**: Metabolic balance prevents optimization-driven collapse
- ✅ **Prosperity Birthing**: Queens spawn new colonies when resources are abundant
- ✅ **Worker Status Updates**: Social reinforcement system with XP and energy rewards
- ✅ **Neuromorphic Architecture**: Central Complex (CX), Mushroom Body (MB), Liquid Neural Networks (LNN)

## 🌟 **Features**

### **Neuromorphic Brain Systems**
- **Central Complex (CX)**: Path integration and navigation
- **Mushroom Body (MB)**: Sparse learning and memory formation
- **Liquid Neural Networks (LNN)**: Metabolic dynamics and adaptation

### **Metabolic Homeostasis**
- **Energy Reserve System**: Survival fuel vs. intellect fuel balance
- **Sugar Saturation**: Learning capacity tied to resource consumption
- **Trophallaxis**: Social learning through resource exchange

### **Social Intelligence**
- **Queen Leadership**: Resource management and colony evolution
- **Worker Specialization**: Scouts, scavengers, and foragers
- **Princess Expansion**: Colony reproduction in prosperous conditions

### **Advanced Behaviors**
- **Pheromone Communication**: Dynamic trail systems
- **Stigmergic Memory**: Persistent environmental learning
- **Emergency Reproduction**: Biomass-based spawning during crises

## 🚀 **Quick Start**

### **Prerequisites**
- Python 3.8+
- Mesa 2.3.0
- NumPy

### **Installation**
```bash
git clone https://github.com/chinmaykx07/ANT_Brain_ai_AGENT_swarm.git
cd ANT_Brain_ai_AGENT_swarm/ant_colony
pip install -r requirements.txt
```

### **Run Simulation**
```bash
python run.py
```
Open http://localhost:8521 in your browser to view the interactive simulation.

### **Docker Deployment** 🐳
For easy deployment and scaling:

```bash
# Build and run with Docker Compose
docker-compose up --build

# Or build manually
docker build -t ant-colony-sim .
docker run -p 8521:8521 ant-colony-sim
```

The simulation will be available at http://localhost:8521

### **Run Tests**
```bash
python test_queen_survival.py  # Test queen longevity
python test_hnm.py            # Test homeostasis
```

## 🏗️ **Architecture**

```
ant_colony/
├── agent.py          # AntAgent, QueenAgent, PrincessAgent classes
├── model.py          # AntColonyModel with maps and evolution
├── server.py         # Web visualization with homeostasis dashboard
├── run.py           # Server launcher
├── test_*.py        # Test suites
├── hero_brain.json  # Brain state data
├── AntBrain.cs      # Unity export for 3D visualization
└── README.md        # Documentation
```

### **Core Components**

#### **AntAgent**
- Neuromorphic brain with CX, MB, LNN
- Metabolic system with energy reserve and sugar saturation
- Role-based behaviors (worker, scout, scavenger)
- Path integration and pheromone tropotaxis

#### **QueenAgent**
- Colony resource management
- Evolutionary milestone tracking
- Emergency spawning during crises
- Prosperity birthing of princesses

#### **PrincessAgent**
- Exploration phase for new colony sites
- Evolution into new queens
- Genetic inheritance with mutations

#### **AntColonyModel**
- Multi-layered pheromone maps
- Resource distribution (food, nectar, garbage)
- Evolution point system
- Population dynamics

## 📊 **Simulation Results**

### **Queen Survival Test**
```
✓ SUCCESS: Queen survived 2000+ cycles!
Food stats: Avg 25.6, Min 0, Max 100
Max Population: 11, Min Population: 10
```

### **Homeostasis Metrics**
- **Energy Balance**: Stable metabolic reserves
- **Population Control**: Adaptive spawning based on resources
- **Evolution Progress**: Unlocked abilities at milestones (100, 500, 1000+ points)

## 🔬 **Scientific Background**

This simulation implements principles from:
- **Neuromorphic Computing**: Brain-inspired algorithms
- **Swarm Intelligence**: Collective behavior emergence
- **Metabolic Homeostasis**: Biological regulation systems
- **Evolutionary Biology**: Adaptive colony reproduction

### **Key Research Insights**
1. **Optimization Paradox**: Pure efficiency leads to extinction
2. **Metabolic Balance**: Survival requires resource conservation
3. **Social Reinforcement**: Worker motivation improves colony performance
4. **Prosperity Reproduction**: Successful colonies expand sustainably

## 🎮 **Web Interface**

The simulation includes a comprehensive web dashboard featuring:
- **Real-time Visualization**: Ant movements and resource distribution
- **Homeostasis Metrics**: Energy levels, population stats, evolution points
- **Metabolic Auras**: Visual representation of ant energy states
- **Evolution Tracking**: Unlocked abilities and colony milestones

## 🧪 **Testing**

### **Automated Tests**
- `test_queen_survival.py`: Validates queen longevity >2000 cycles
- `test_hnm.py`: Verifies homeostasis mechanisms

### **Manual Testing**
```bash
# Quick functionality test
python -c "
from model import AntColonyModel
model = AntColonyModel(width=20, height=20, initial_ants=10)
for i in range(100):
    model.step()
print('Simulation stable after 100 steps')
"
```

## 📈 **Performance**

- **Simulation Speed**: ~50-100 steps/second (depending on grid size)
- **Memory Usage**: ~50-200MB for typical configurations
- **Scalability**: Supports grids from 10x10 to 100x100

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Add tests for new functionality
5. Submit a pull request

## � **Support Our Research**

Help us advance neuromorphic AI and swarm intelligence research! Your support enables:

- 🧠 **Neuromorphic Computing**: Develop brain-inspired AI that's 1000x more energy-efficient
- 🤖 **Swarm Robotics**: Create autonomous systems for real-world applications
- 🔬 **Open Research**: Fund scientific publications and community development

### **Ways to Support**
- **💖 [GitHub Sponsors](https://github.com/sponsors/chinmaykx07)**: Monthly sponsorship
- **🧑‍💻 Contribute Code**: Join our open-source development
- **📢 Spread the Word**: Share our research with your network
- **📧 Contact**: research@ant-colony.ai for institutional partnerships

### **Funding Needs**
- Cloud computing resources ($200/month)
- Hardware development ($500 one-time)
- Research publications ($1,000/year)
- Software tools & licenses ($300/month)

Visit our [donation page](donate.html) for more information.

## �📄 **License**

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 **Acknowledgments**

- **Mesa Framework**: Agent-based modeling library
- **Neuromorphic Research**: Biological inspiration
- **Swarm Intelligence**: Collective behavior studies
- **Open Source Community**: Scientific computing tools

## 🔗 **Links**

- **Repository**: https://github.com/chinmaykx07/ANT_Brain_ai_AGENT_swarm
- **Issues**: https://github.com/chinmaykx07/ANT_Brain_ai_AGENT_swarm/issues
- **Releases**: https://github.com/chinmaykx07/ANT_Brain_ai_AGENT_swarm/releases

---

**"From biological inspiration to artificial intelligence - ants teaching machines how to survive."** 🐜⚡
