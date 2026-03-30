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

## 🤖 ROS2 Integration for Robotics

The simulation includes a ROS2 bridge for real-world deployment on drone swarms and robotic systems.

### **ROS2 Setup (Ubuntu 22.04)**
```bash
# Install ROS2 Humble
sudo apt update
sudo apt install software-properties-common
sudo add-apt-repository universe
sudo apt update && sudo apt install curl -y
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null
sudo apt update
sudo apt upgrade
sudo apt install ros-humble-desktop python3-colcon-common-extensions

# Source ROS2
echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
source ~/.bashrc

# Install Python ROS2 packages
pip install rclpy
```

### **Running ROS2 Bridge**
```bash
# Terminal 1: Start ROS2 daemon
ros2 daemon start

# Terminal 2: Launch bridge
python ros2_bridge.py

# Terminal 3: Launch RViz2
rviz2
```

### **Testing ROS2 Bridge (Without ROS2 Installation)**
```bash
# Run the bridge test suite
python test_ros2_bridge.py
```

This validates the complete neuromorphic swarm simulation and ROS2 data publishing logic.

### **RViz2 Configuration**
1. Add `OccupancyGrid` display for pheromones/obstacles
2. Add `MarkerArray` display for agents
3. Set fixed frame to `ant_colony_map`

### **Published Topics**
- `/ant_colony/occupancy_grid`: Pheromone maps and obstacles
- `/ant_colony/markers`: Agent positions (blue=explore, yellow=return, red=queen)
- `/ant_colony/status`: Simulation statistics

## � Citations & Acknowledgements

This project stands on the shoulders of giants in the open-source robotics and scientific computing communities. For full details on citations, licenses, and intellectual property statements, see [ATTRIBUTIONS.md](../ATTRIBUTIONS.md).

**Key Open-Source Dependencies:**
- **ROS 2**: Robotics communication and visualization framework
- **Mesa**: Agent-based modeling framework  
- **SciPy/NumPy**: Scientific computing and convolution operations
- **Tornado**: Web server for the simulation interface

## �📁 Project Structure

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

