using Unity.Entities;
using Unity.Mathematics;
using Unity.Burst;
using Unity.Transforms;
using Unity.Collections;
using Unity.Jobs;
using System;

namespace AntColony
{
    /// <summary>
    /// High-performance neuromorphic brain system using Unity ECS and Burst compiler.
    /// Implements the core ant behavior logic at near-native C++ speeds.
    /// </summary>
    [BurstCompile]
    public partial struct AntBrainSystem : ISystem
    {
        private Random _random;

        [BurstCompile]
        public void OnCreate(ref SystemState state)
        {
            _random = new Random(42); // Deterministic seed for reproducibility
        }

        [BurstCompile]
        public void OnUpdate(ref SystemState state)
        {
            var deltaTime = SystemAPI.Time.DeltaTime;
            var randomSeed = (uint)(_random.NextInt() + SystemAPI.Time.ElapsedTime);

            // Schedule parallel job for all ant entities
            new AntBrainJob
            {
                DeltaTime = deltaTime,
                RandomSeed = randomSeed,
                PheromoneMap = SystemAPI.GetSingleton<PheromoneMapData>()
            }.ScheduleParallel();
        }
    }

    /// <summary>
    /// Singleton component containing the global pheromone map
    /// </summary>
    public struct PheromoneMapData : IComponentData
    {
        public int Width;
        public int Height;
        // Note: In a real implementation, this would be a NativeArray or BlobAsset
        // For simplicity, we're using a placeholder
    }

    /// <summary>
    /// Burst-compiled job that processes all ant brain logic in parallel
    /// </summary>
    [BurstCompile]
    public partial struct AntBrainJob : IJobEntity
    {
        public float DeltaTime;
        public uint RandomSeed;
        public PheromoneMapData PheromoneMap;

        void Execute(ref AntData ant, ref LocalTransform transform, ref DynamicBuffer<PheromoneBuffer> pheromoneBuffer)
        {
            // Metabolic homeostasis: Energy decay
            ant.EnergyReserve = math.max(0.0f, ant.EnergyReserve - 0.5f * DeltaTime);

            // Sugar decay
            ant.SugarLevel = math.max(0.0f, ant.SugarLevel - 0.01f * DeltaTime);

            // Homeostatic Neuro-Modulation: Survival override
            bool basalSurvivalMode = ant.EnergyReserve < 30.0f;
            float currentMaxSpeed = basalSurvivalMode ? ant.MaxSpeed * 0.5f : ant.MaxSpeed;

            // State machine logic
            switch (ant.State)
            {
                case 0: // EXPLORE
                    ExecuteExploreLogic(ref ant, currentMaxSpeed);
                    break;

                case 1: // RETURN
                    ExecuteReturnLogic(ref ant, currentMaxSpeed);
                    break;

                case 2: // EXPLOIT_MEMORY
                    ExecuteExploitLogic(ref ant, currentMaxSpeed);
                    break;
            }

            // Update position based on velocity
            ant.Position += ant.Velocity * DeltaTime;

            // Boundary checking (assuming 100x100 world)
            ant.Position.x = math.clamp(ant.Position.x, 0.0f, 99.0f);
            ant.Position.z = math.clamp(ant.Position.z, 0.0f, 99.0f);

            // Update transform
            transform.Position = ant.Position;

            // Update heading based on velocity
            if (math.lengthsq(ant.Velocity) > 0.001f)
            {
                ant.Heading = math.atan2(ant.Velocity.x, ant.Velocity.z);
            }

            // Age the ant
            ant.Age++;

            // Death check
            if (ant.Age >= ant.Lifespan)
            {
                // Mark for death (would be handled by a separate death system)
                ant.EnergyReserve = -1.0f;
            }
        }

        /// <summary>
        /// Execute exploration logic with antennal tropotaxis
        /// </summary>
        private void ExecuteExploreLogic(ref AntData ant, float maxSpeed)
        {
            // Antennal tropotaxis steering
            float leftPheromone = GetPheromoneAtAntenna(ref ant, -math.PI / 6.0f); // Left antenna
            float rightPheromone = GetPheromoneAtAntenna(ref ant, math.PI / 6.0f); // Right antenna

            // Steering torque based on pheromone gradient
            float steeringTorque = (rightPheromone - leftPheromone) * ant.AntennaSensitivity * ant.SteeringFluidity;

            // Update heading
            ant.Heading += steeringTorque * DeltaTime;

            // Add some random wandering
            var random = new Random((uint)(RandomSeed + ant.UniqueId));
            float randomTurn = (random.NextFloat() - 0.5f) * 0.1f;
            ant.Heading += randomTurn * DeltaTime;

            // Update velocity based on heading
            ant.Velocity.x = math.cos(ant.Heading) * maxSpeed;
            ant.Velocity.z = math.sin(ant.Heading) * maxSpeed;
        }

        /// <summary>
        /// Execute return logic with home vector navigation
        /// </summary>
        private void ExecuteReturnLogic(ref AntData ant, float maxSpeed)
        {
            // Home vector: Direct calculation to nest
            float3 directionToNest = math.normalize(ant.NestPos - ant.Position);
            float distanceToNest = math.distance(ant.Position, ant.NestPos);

            // If close to nest, slow down
            float speedMultiplier = math.saturate(distanceToNest / 5.0f);
            float3 targetVelocity = directionToNest * maxSpeed * speedMultiplier;

            // Smooth velocity interpolation
            ant.Velocity = math.lerp(ant.Velocity, targetVelocity, DeltaTime * 5.0f);

            // Arrival check
            if (distanceToNest < 1.0f)
            {
                // Transfer sugar to colony (would be handled by colony system)
                ant.SugarLevel = 0.0f;
                ant.State = 0; // Switch back to explore
                ant.TargetMemory = float3.zero; // Reset memory
            }
        }

        /// <summary>
        /// Execute memory exploitation logic
        /// </summary>
        private void ExecuteExploitLogic(ref AntData ant, float maxSpeed)
        {
            if (math.all(ant.TargetMemory != float3.zero))
            {
                // Move towards target memory
                float3 directionToTarget = math.normalize(ant.TargetMemory - ant.Position);
                float distanceToTarget = math.distance(ant.Position, ant.TargetMemory);

                if (distanceToTarget < 1.0f)
                {
                    // Reached target, switch back to explore
                    ant.State = 0;
                    ant.TargetMemory = float3.zero;
                }
                else
                {
                    // Move towards target
                    ant.Velocity = directionToTarget * maxSpeed;
                }
            }
            else
            {
                // No valid target, switch to explore
                ant.State = 0;
            }
        }

        /// <summary>
        /// Get pheromone value at antenna position
        /// </summary>
        private float GetPheromoneAtAntenna(ref AntData ant, float angleOffset)
        {
            // Calculate antenna position
            float antennaAngle = ant.Heading + angleOffset;
            float2 antennaOffset = new float2(
                math.cos(antennaAngle) * 0.5f,
                math.sin(antennaAngle) * 0.5f
            );

            float2 antennaPos = new float2(ant.Position.x, ant.Position.z) + antennaOffset;

            // Clamp to map bounds
            int x = (int)math.clamp(antennaPos.x, 0, PheromoneMap.Width - 1);
            int y = (int)math.clamp(antennaPos.y, 0, PheromoneMap.Height - 1);

            // In a real implementation, this would sample from the actual pheromone map
            // For now, return a placeholder value
            return math.sin(x * 0.1f) * math.cos(y * 0.1f) + 1.0f;
        }
    }
}