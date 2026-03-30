using Unity.Entities;
using Unity.Mathematics;

namespace AntColony
{
    /// <summary>
    /// Component data for ant entities in Unity ECS.
    /// Contains all the state information needed for neuromorphic behavior.
    /// </summary>
    public struct AntData : IComponentData
    {
        /// <summary>Current 3D position of the ant</summary>
        public float3 Position;

        /// <summary>Current velocity vector</summary>
        public float3 Velocity;

        /// <summary>Current behavioral state: 0=EXPLORE, 1=RETURN, 2=EXPLOIT_MEMORY</summary>
        public int State;

        /// <summary>Current sugar saturation level (0.0-1.0)</summary>
        public float SugarLevel;

        /// <summary>Position of the nest/recycling center</summary>
        public float3 NestPos;

        /// <summary>Best resource target memory for TFL sharing</summary>
        public float3 TargetMemory;

        /// <summary>Energy reserve level (0.0-100.0)</summary>
        public float EnergyReserve;

        /// <summary>Antennal sensitivity for pheromone detection</summary>
        public float AntennaSensitivity;

        /// <summary>Maximum speed capability</summary>
        public float MaxSpeed;

        /// <summary>Current heading angle in radians</summary>
        public float Heading;

        /// <summary>Steering fluidity parameter</summary>
        public float SteeringFluidity;

        /// <summary>Unique identifier for this ant</summary>
        public int UniqueId;

        /// <summary>Tribe identifier for colony management</summary>
        public int TribeId;

        /// <summary>Age in simulation steps</summary>
        public int Age;

        /// <summary>Lifespan in simulation steps</summary>
        public int Lifespan;

        /// <summary>Experience points for evolution</summary>
        public int Xp;

        /// <summary>Whether this ant is carrying a resource</summary>
        public int CarryingResource;

        /// <summary>Pickup position for distance calculations</summary>
        public float3 PickupPos;
    }

    /// <summary>
    /// Buffer element for storing local pheromone values around an ant.
    /// Used for antennal tropotaxis steering.
    /// </summary>
    public struct PheromoneBuffer : IBufferElementData
    {
        /// <summary>Pheromone intensity value</summary>
        public float Value;

        /// <summary>Position relative to ant (for local sensing)</summary>
        public float2 RelativePosition;
    }

    /// <summary>
    /// Component for queen-specific data
    /// </summary>
    public struct QueenData : IComponentData
    {
        /// <summary>Colony reserves for reproduction</summary>
        public float ColonyReserves;

        /// <summary>Queen's health level</summary>
        public float Health;

        /// <summary>Number of princesses spawned</summary>
        public int PrincessesSpawned;
    }

    /// <summary>
    /// Component for princess-specific data
    /// </summary>
    public struct PrincessData : IComponentData
    {
        /// <summary>Current lifecycle state</summary>
        public int State; // 0=INCUBATE, 1=NUPTIAL_FLIGHT, 2=FOUND_COLONY

        /// <summary>Flight vector for nuptial flight</summary>
        public float3 FlightVector;

        /// <summary>Origin nest position</summary>
        public float3 NestOrigin;

        /// <summary>Parent genome data</summary>
        public float4 ParentGenome; // Simplified genome representation
    }
}