using UnityEngine;
using Unity.Robotics.ROSTCPConnector;
using Unity.Robotics.ROSTCPConnector.ROSGeometry;
using RosMessageTypes.Nav;
using RosMessageTypes.Visualization;
using RosMessageTypes.Std;
using System.Collections.Generic;
using Unity.Entities;
using Unity.Mathematics;
using Unity.Transforms;

namespace AntColony
{
    /// <summary>
    /// ROS2 Bridge for Unity Digital Twin.
    /// Subscribes to ROS2 topics from the Python simulation and updates Unity ECS entities.
    /// Creates a true Digital Twin where Unity mirrors the Python swarm behavior.
    /// </summary>
    public class RosAntBridge : MonoBehaviour
    {
        [Header("ROS2 Settings")]
        [Tooltip("ROS2 IP address (leave empty for localhost)")]
        public string rosIP = "127.0.0.1";

        [Tooltip("ROS2 port")]
        public int rosPort = 10000;

        [Header("Unity ECS Settings")]
        [Tooltip("Entity prefab for ants")]
        public GameObject antPrefab;

        [Tooltip("Entity prefab for queens")]
        public GameObject queenPrefab;

        [Tooltip("Material for pheromone visualization")]
        public Material pheromoneMaterial;

        [Header("Simulation Settings")]
        [Tooltip("Maximum number of ants to visualize")]
        public int maxAnts = 1000;

        [Tooltip("Pheromone map resolution")]
        public int pheromoneResolution = 100;

        // ROS2 connection
        private ROSConnection _ros;

        // Entity management
        private World _world;
        private EntityManager _entityManager;
        private Dictionary<int, Entity> _antEntities = new Dictionary<int, Entity>();
        private Dictionary<int, Entity> _queenEntities = new Dictionary<int, Entity>();

        // Pheromone visualization
        private Texture2D _pheromoneTexture;
        private Renderer _pheromoneRenderer;

        void Start()
        {
            // Initialize ROS2 connection
            _ros = ROSConnection.GetOrCreateInstance();
            _ros.Connect(rosIP, rosPort);

            // Subscribe to ROS2 topics
            _ros.Subscribe<MarkerArrayMsg>("/ant_colony/markers", OnAntMarkersReceived);
            _ros.Subscribe<OccupancyGridMsg>("/ant_colony/occupancy_grid", OnOccupancyGridReceived);
            _ros.Subscribe<StringMsg>("/ant_colony/status", OnStatusReceived);

            // Initialize ECS
            _world = World.DefaultGameObjectInjectionWorld;
            _entityManager = _world.EntityManager;

            // Initialize pheromone visualization
            InitializePheromoneVisualization();

            Debug.Log("ROS2 Ant Bridge initialized. Waiting for simulation data...");
        }

        void Update()
        {
            // Update pheromone texture if needed
            if (_pheromoneTexture != null && _pheromoneRenderer != null)
            {
                _pheromoneRenderer.material.mainTexture = _pheromoneTexture;
            }
        }

        void OnDestroy()
        {
            // Clean up entities
            foreach (var entity in _antEntities.Values)
            {
                if (_entityManager.Exists(entity))
                {
                    _entityManager.DestroyEntity(entity);
                }
            }

            foreach (var entity in _queenEntities.Values)
            {
                if (_entityManager.Exists(entity))
                {
                    _entityManager.DestroyEntity(entity);
                }
            }

            _antEntities.Clear();
            _queenEntities.Clear();
        }

        /// <summary>
        /// Handle incoming ant marker data from ROS2
        /// </summary>
        private void OnAntMarkersReceived(MarkerArrayMsg markerArray)
        {
            foreach (var markerMsg in markerArray.markers)
            {
                int uniqueId = markerMsg.id;
                Vector3 position = markerMsg.pose.position.From<FLU>();
                string markerType = markerMsg.ns; // Type encoded in namespace

                // Update or create entity based on marker type
                if (markerType.Contains("queen"))
                {
                    UpdateQueenEntity(uniqueId, position, markerMsg);
                }
                else
                {
                    UpdateAntEntity(uniqueId, position, markerMsg);
                }
            }
        }

        /// <summary>
        /// Handle incoming occupancy grid (pheromone map) from ROS2
        /// </summary>
        private void OnOccupancyGridReceived(OccupancyGridMsg occupancyGrid)
        {
            UpdatePheromoneVisualization(occupancyGrid);
        }

        /// <summary>
        /// Handle status messages from ROS2
        /// </summary>
        private void OnStatusReceived(StringMsg statusMsg)
        {
            // Parse status message (format: "Step: X, Agents: Y, Hunger: Z")
            Debug.Log($"ROS2 Status: {statusMsg.data}");
        }

        /// <summary>
        /// Update or create an ant entity
        /// </summary>
        private void UpdateAntEntity(int uniqueId, Vector3 position, RosMessageTypes.Visualization.MarkerMsg markerMsg)
        {
            Entity entity;

            if (!_antEntities.TryGetValue(uniqueId, out entity) || !_entityManager.Exists(entity))
            {
                // Create new ant entity
                if (_antEntities.Count >= maxAnts)
                {
                    // Limit total ants for performance
                    return;
                }

                entity = CreateAntEntity(uniqueId);
                _antEntities[uniqueId] = entity;
            }

            // Update ant data from ROS2 marker
            UpdateAntFromMarker(entity, position, markerMsg);
        }

        /// <summary>
        /// Update or create a queen entity
        /// </summary>
        private void UpdateQueenEntity(int uniqueId, Vector3 position, RosMessageTypes.Visualization.MarkerMsg markerMsg)
        {
            Entity entity;

            if (!_queenEntities.TryGetValue(uniqueId, out entity) || !_entityManager.Exists(entity))
            {
                // Create new queen entity
                entity = CreateQueenEntity(uniqueId);
                _queenEntities[uniqueId] = entity;
            }

            // Update queen data from ROS2 marker
            UpdateQueenFromMarker(entity, position, markerMsg);
        }

        /// <summary>
        /// Create a new ant entity
        /// </summary>
        private Entity CreateAntEntity(int uniqueId)
        {
            // Convert GameObject prefab to entity
            GameObjectConversionSettings settings = GameObjectConversionSettings.FromWorld(_world, null);
            Entity entity = GameObjectConversionUtility.ConvertGameObjectHierarchy(antPrefab, settings);

            // Add ant data component
            _entityManager.AddComponentData(entity, new AntData
            {
                UniqueId = uniqueId,
                Position = float3.zero,
                Velocity = float3.zero,
                State = 0, // EXPLORE
                SugarLevel = 0.1f,
                EnergyReserve = 100.0f,
                MaxSpeed = 1.0f,
                AntennaSensitivity = 1.0f,
                SteeringFluidity = 0.1f,
                Age = 0,
                Lifespan = 1000,
                Xp = 0,
                CarryingResource = 0
            });

            return entity;
        }

        /// <summary>
        /// Create a new queen entity
        /// </summary>
        private Entity CreateQueenEntity(int uniqueId)
        {
            // Convert GameObject prefab to entity
            GameObjectConversionSettings settings = GameObjectConversionSettings.FromWorld(_world, null);
            Entity entity = GameObjectConversionUtility.ConvertGameObjectHierarchy(queenPrefab, settings);

            // Add queen data component
            _entityManager.AddComponentData(entity, new QueenData
            {
                ColonyReserves = 0.0f,
                Health = 100.0f,
                PrincessesSpawned = 0
            });

            return entity;
        }

        /// <summary>
        /// Update ant entity data from ROS2 marker
        /// </summary>
        private void UpdateAntFromMarker(Entity entity, Vector3 position, RosMessageTypes.Visualization.MarkerMsg markerMsg)
        {
            if (!_entityManager.HasComponent<AntData>(entity))
                return;

            AntData antData = _entityManager.GetComponentData<AntData>(entity);

            // Update position
            antData.Position = new float3(position.x, position.y, position.z);

            // Update state based on marker color
            // Yellow = RETURN (1), Blue = EXPLORE (0), Purple = EXPLOIT_MEMORY (2)
            var color = markerMsg.color;
            if (color.r > 0.8f && color.g > 0.8f && color.b < 0.2f)
            {
                antData.State = 1; // RETURN - Yellow
            }
            else if (color.r > 0.8f && color.g < 0.2f && color.b > 0.8f)
            {
                antData.State = 2; // EXPLOIT_MEMORY - Purple
            }
            else
            {
                antData.State = 0; // EXPLORE - Blue or other
            }

            // Update sugar level based on marker scale (larger = more sugar)
            antData.SugarLevel = markerMsg.scale.x / 0.8f; // Normalize to 0-1 range

            _entityManager.SetComponentData(entity, antData);

            // Update transform
            if (_entityManager.HasComponent<LocalTransform>(entity))
            {
                LocalTransform transform = _entityManager.GetComponentData<LocalTransform>(entity);
                transform.Position = antData.Position;
                _entityManager.SetComponentData(entity, transform);
            }
        }

        /// <summary>
        /// Update queen entity data from ROS2 marker
        /// </summary>
        private void UpdateQueenFromMarker(Entity entity, Vector3 position, RosMessageTypes.Visualization.MarkerMsg markerMsg)
        {
            if (!_entityManager.HasComponent<QueenData>(entity))
                return;

            QueenData queenData = _entityManager.GetComponentData<QueenData>(entity);

            // Update position if needed
            if (_entityManager.HasComponent<LocalTransform>(entity))
            {
                LocalTransform transform = _entityManager.GetComponentData<LocalTransform>(entity);
                transform.Position = new float3(position.x, position.y, position.z);
                _entityManager.SetComponentData(entity, transform);
            }

            _entityManager.SetComponentData(entity, queenData);
        }

        /// <summary>
        /// Initialize pheromone visualization
        /// </summary>
        private void InitializePheromoneVisualization()
        {
            // Create a quad or plane for pheromone visualization
            GameObject pheromonePlane = GameObject.CreatePrimitive(PrimitiveType.Quad);
            pheromonePlane.name = "PheromoneMap";
            pheromonePlane.transform.position = new Vector3(pheromoneResolution / 2f, 0, pheromoneResolution / 2f);
            pheromonePlane.transform.rotation = Quaternion.Euler(90, 0, 0);
            pheromonePlane.transform.localScale = new Vector3(pheromoneResolution, pheromoneResolution, 1);

            _pheromoneRenderer = pheromonePlane.GetComponent<Renderer>();
            _pheromoneRenderer.material = pheromoneMaterial;

            // Create pheromone texture
            _pheromoneTexture = new Texture2D(pheromoneResolution, pheromoneResolution, TextureFormat.RGBA32, false);
            _pheromoneTexture.filterMode = FilterMode.Point;
        }

        /// <summary>
        /// Update pheromone visualization from ROS2 occupancy grid
        /// </summary>
        private void UpdatePheromoneVisualization(OccupancyGridMsg occupancyGrid)
        {
            if (_pheromoneTexture == null)
                return;

            int width = occupancyGrid.info.width;
            int height = occupancyGrid.info.height;

            // Resize texture if needed
            if (_pheromoneTexture.width != width || _pheromoneTexture.height != height)
            {
                _pheromoneTexture.Resize(width, height);
            }

            // Convert occupancy data to colors
            Color[] colors = new Color[width * height];
            for (int i = 0; i < occupancyGrid.data.Length; i++)
            {
                sbyte occupancy = occupancyGrid.data[i];

                if (occupancy == -1)
                {
                    // Unknown - transparent
                    colors[i] = Color.clear;
                }
                else
                {
                    // Scale 0-100 to color intensity
                    float intensity = Mathf.Clamp01(occupancy / 100.0f);

                    if (occupancy >= 50)
                    {
                        // Obstacles/Garbage - Red
                        colors[i] = new Color(intensity, 0, 0, 0.8f);
                    }
                    else
                    {
                        // Pheromones - White to yellow gradient
                        colors[i] = new Color(intensity, intensity, intensity * 0.5f, 0.6f);
                    }
                }
            }

            _pheromoneTexture.SetPixels(colors);
            _pheromoneTexture.Apply();
        }
    }
}