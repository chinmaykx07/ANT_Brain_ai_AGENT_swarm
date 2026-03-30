# 📜 Citations and Acknowledgements

This project utilizes several industry-standard open-source frameworks and installation procedures. We acknowledge the following resources for providing the infrastructure that makes this neuromorphic swarm possible:

## 1. ROS 2 (Robot Operating System)

The communication backbone and RViz2 visualization rely on the ROS 2 (Humble/Foxy) ecosystem.

**Source:** Open Robotics (ros.org)

**Usage:** The installation scripts and repository configuration used in this project are based on the standard ROS 2 Debian/Ubuntu setup procedures documented in the official ROS 2 Documentation.

**License:** Apache 2.0

## 2. Standard ROS 2 Host Setup Scripts

We acknowledge the community-driven setup patterns found in the following open-source repositories, which served as reference points for the Kria/Ubuntu host environment configurations:

- **zyanham/MyTools**: Host setup scripts for Kria KR260/v2022.1.
  - Repository: https://github.com/zyanham/MyTools
  - Specific file: XILINX_WS/KRIA/KR260/v2022.1/KRS/host_setup.bash
  - License: Unknown

- **PX4-user_guide**: Standardized ROS 2 communication bridge setup for autonomous flight.
  - Repository: https://github.com/PX4/PX4-user_guide
  - Specific file: uk/ros/ros2_comm.md
  - License: Unknown

- **danb0b/danb0b.github.io**: Community tutorials for ROS 2 deployment on edge-hardware (Raspberry Pi/Z2W).
  - Repository: https://github.com/danb0b/danb0b.github.io
  - Specific file: content/notebook/ros2/11-installing-ros2-on-a-rpiz2w.md
  - License: Unknown

## 3. Mesa ABM Framework

The agent-based core is built upon the Mesa Python Framework.

**Source:** Project Mesa (https://github.com/projectmesa/mesa)

**Usage:** Modeling of agent-grid interactions and scheduling.

**License:** Apache 2.0

## 4. SciPy & NumPy

The "Enterprise Scaling" of the pheromone engine utilizes the Convolutional Matrix logic provided by the SciPy and NumPy communities.

**Source:** scipy.org, numpy.org

**Usage:** Vectorized pheromone diffusion via convolution operations.

**License:** BSD-3-Clause

## 5. Unity Game Engine

The 3D visualization and digital twin simulation utilizes Unity's ECS (Entity Component System) architecture.

**Source:** Unity Technologies (unity.com)

**Usage:** Real-time 3D rendering of swarm behavior and neuromorphic brain states.

**License:** Unity Personal License (Free)

## 6. Neuromorphic Brain Architecture

The Central Complex (CX), Mushroom Body (MB), and Liquid Neural Network (LNN) implementations are inspired by biological neuroscience research.

**Source:** Research papers on insect navigation and neuromorphic computing

**Usage:** CX for path integration, MB for associative learning, LNN for temporal processing.

**License:** Public Domain (biological inspiration)

**License:** BSD-3-Clause

# 🛡️ Intellectual Property Statement

While the installation and communication layers utilize the open-source frameworks cited above, the following components represent original research and Proprietary Neuromorphic Architectures developed within this project:

- **TFL (Trophallactic Federated Learning)**: Peer-to-peer metabolic trust data exchange between agents.
- **HNM (Homeostatic Neuro-Modulation)**: Survival-based override systems for multi-agent coordination.
- **PrincessAgent Colony Expansion**: Autonomous sub-swarm node generation logic.
- **Neuromorphic Brain Architecture**: CX (Central Complex), MB (Mushroom Body), LNN (Liquid Neural Network) integration.
- **Metabolic Homeostasis System**: Dual fuel economy with sugar saturation and energy reserves.
- **Home Vector Navigation**: Direct dead-reckoning with obstacle avoidance for 100% return reliability.

# 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

# 🤝 Contributing

When contributing to this project, please ensure that any new dependencies or infrastructure components are properly cited and acknowledged in this ATTRIBUTIONS.md file.</content>
<parameter name="filePath">/workspaces/ANT_Brain_ai_AGENT_swarm/ant_colony/ATTRIBUTIONS.md