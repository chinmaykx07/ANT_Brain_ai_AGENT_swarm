#!/usr/bin/env python3
"""
ROS2 Bridge for ANT_Brain_ai_AGENT_swarm
Translates Mesa simulation to ROS2 messages for RViz2 visualization and hardware deployment.

This bridge publishes:
- nav_msgs/OccupancyGrid: Pheromone maps and obstacles
- visualization_msgs/MarkerArray: Agent positions and states
- std_msgs/String: Simulation status updates

Requirements:
- ROS2 Humble Hawksbill or newer
- Python packages: rclpy, numpy, scipy

Installation (Ubuntu 22.04):
sudo apt update
sudo apt install software-properties-common
sudo add-apt-repository universe
sudo apt update && sudo apt install curl -y
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null
sudo apt update
sudo apt upgrade
sudo apt install ros-humble-desktop python3-colcon-common-extensions
echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
source ~/.bashrc

# Install Python dependencies
pip install rclpy numpy scipy

Usage:
1. Start ROS2: ros2 daemon start
2. Run bridge: python ros2_bridge.py
3. Launch RViz2: rviz2
4. Add OccupancyGrid and MarkerArray displays
"""

import rclpy
from rclpy.node import Node
from nav_msgs.msg import OccupancyGrid
from visualization_msgs.msg import Marker, MarkerArray
from std_msgs.msg import String
import numpy as np
import time
import threading
import sys
import os

# Add the ant_colony directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from model import AntColonyModel

class AntColonyROS2Bridge(Node):
    def __init__(self):
        super().__init__('ant_colony_bridge')

        # Publishers
        self.occupancy_pub = self.create_publisher(OccupancyGrid, 'ant_colony/occupancy_grid', 10)
        self.marker_pub = self.create_publisher(MarkerArray, 'ant_colony/markers', 10)
        self.status_pub = self.create_publisher(String, 'ant_colony/status', 10)

        # Initialize Mesa model
        self.model = AntColonyModel(width=100, height=100, num_ants=50)

        # Timer for publishing at 10Hz (100ms intervals)
        self.timer = self.create_timer(0.1, self.publish_data)

        # Marker IDs for tracking
        self.marker_id_counter = 0
        self.agent_markers = {}  # agent_id -> marker_id

        self.get_logger().info('ANT Colony ROS2 Bridge initialized')

    def publish_data(self):
        """Publish simulation data to ROS2 topics."""
        try:
            # Step the simulation
            self.model.step()

            # Publish occupancy grid (pheromones + obstacles)
            self.publish_occupancy_grid()

            # Publish agent markers
            self.publish_agent_markers()

            # Publish status
            status_msg = String()
            status_msg.data = f"Step: {self.model.schedule.steps}, Agents: {len(self.model.schedule.agents)}, Hunger: {self.model.colony_hunger:.2f}"
            self.status_pub.publish(status_msg)

        except Exception as e:
            self.get_logger().error(f'Error in publish_data: {str(e)}')

    def publish_occupancy_grid(self):
        """Publish pheromone and obstacle data as OccupancyGrid."""
        grid_msg = OccupancyGrid()
        grid_msg.header.stamp = self.get_clock().now().to_msg()
        grid_msg.header.frame_id = "ant_colony_map"

        grid_msg.info.resolution = 1.0  # 1 meter per cell
        grid_msg.info.width = self.model.width
        grid_msg.info.height = self.model.height
        grid_msg.info.origin.position.x = 0.0
        grid_msg.info.origin.position.y = 0.0
        grid_msg.info.origin.position.z = 0.0
        grid_msg.info.origin.orientation.w = 1.0

        # Create occupancy data (0-100, -1 for unknown)
        # Combine pheromones, obstacles, and garbage
        occupancy_data = []

        for y in range(self.model.height):
            for x in range(self.model.width):
                # Obstacles are 100 (occupied)
                if self.model.obstacle_map[x, y]:
                    occupancy_data.append(100)
                # Garbage is 50 (semi-occupied)
                elif self.model.garbage_map[x, y] > 0:
                    occupancy_data.append(50)
                # Pheromones: scale 0-100 based on intensity
                else:
                    pheromone_intensity = min(100, self.model.pheromone_map[x, y] * 10)
                    occupancy_data.append(int(pheromone_intensity))

        grid_msg.data = occupancy_data
        self.occupancy_pub.publish(grid_msg)

    def publish_agent_markers(self):
        """Publish agent positions and states as MarkerArray."""
        marker_array = MarkerArray()
        current_agents = set()

        # Create markers for all agents
        for agent in self.model.schedule.agents:
            if hasattr(agent, 'pos') and hasattr(agent, 'state'):
                agent_id = agent.unique_id
                current_agents.add(agent_id)

                # Get or create marker ID
                if agent_id not in self.agent_markers:
                    self.agent_markers[agent_id] = self.marker_id_counter
                    self.marker_id_counter += 1

                marker_id = self.agent_markers[agent_id]

                # Create marker
                marker = Marker()
                marker.header.stamp = self.get_clock().now().to_msg()
                marker.header.frame_id = "ant_colony_map"
                marker.id = marker_id
                marker.type = Marker.SPHERE
                marker.action = Marker.ADD

                # Position
                marker.pose.position.x = float(agent.pos[0])
                marker.pose.position.y = float(agent.pos[1])
                marker.pose.position.z = 0.0
                marker.pose.orientation.w = 1.0

                # Scale
                marker.scale.x = 0.8
                marker.scale.y = 0.8
                marker.scale.z = 0.8

                # Color based on agent type and state
                if isinstance(agent, self.model.AntAgent):
                    if agent.state == "RETURN":
                        # Yellow for returning with resources
                        marker.color.r = 1.0
                        marker.color.g = 1.0
                        marker.color.b = 0.0
                    elif agent.is_hero:
                        # Purple for heroes
                        marker.color.r = 1.0
                        marker.color.g = 0.0
                        marker.color.b = 1.0
                    else:
                        # Blue for exploring
                        marker.color.r = 0.0
                        marker.color.g = 0.0
                        marker.color.b = 1.0
                elif isinstance(agent, self.model.QueenAgent):
                    # Red for queens
                    marker.color.r = 1.0
                    marker.color.g = 0.0
                    marker.color.b = 0.0
                    marker.scale.x = 1.5
                    marker.scale.y = 1.5
                    marker.scale.z = 1.5
                elif isinstance(agent, self.model.PrincessAgent):
                    # Pink for princesses
                    marker.color.r = 1.0
                    marker.color.g = 0.5
                    marker.color.b = 0.5
                else:
                    # Gray for others
                    marker.color.r = 0.5
                    marker.color.g = 0.5
                    marker.color.b = 0.5

                marker.color.a = 1.0
                marker.lifetime = rclpy.duration.Duration(seconds=1).to_msg()  # Refresh every second

                marker_array.markers.append(marker)

        # Mark disappeared agents for deletion
        disappeared_agents = set(self.agent_markers.keys()) - current_agents
        for agent_id in disappeared_agents:
            marker_id = self.agent_markers[agent_id]
            delete_marker = Marker()
            delete_marker.header.stamp = self.get_clock().now().to_msg()
            delete_marker.header.frame_id = "ant_colony_map"
            delete_marker.id = marker_id
            delete_marker.action = Marker.DELETE
            marker_array.markers.append(delete_marker)
            del self.agent_markers[agent_id]

        self.marker_pub.publish(marker_array)

def main(args=None):
    rclpy.init(args=args)

    try:
        bridge = AntColonyROS2Bridge()
        rclpy.spin(bridge)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Error: {e}")
    finally:
        rclpy.shutdown()

if __name__ == '__main__':
    main()