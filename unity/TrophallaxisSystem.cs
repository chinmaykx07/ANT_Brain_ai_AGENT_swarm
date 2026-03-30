using Unity.Entities;
using Unity.Mathematics;
using Unity.Burst;
using Unity.Collections;
using Unity.Jobs;
using Unity.Collections.LowLevel.Unsafe;

namespace AntColony
{
    /// <summary>
    /// High-performance Trophallaxis Federated Learning system.
    /// Uses spatial hashing to efficiently detect ant collisions for knowledge sharing.
    /// </summary>
    [BurstCompile]
    public partial struct TrophallaxisSystem : ISystem
    {
        [BurstCompile]
        public void OnUpdate(ref SystemState state)
        {
            // Create spatial hash map for collision detection
            var spatialHashMap = new NativeParallelMultiHashMap<int2, Entity>(1000, Allocator.TempJob);

            // First pass: Hash all ant positions
            new SpatialHashJob
            {
                SpatialHashMap = spatialHashMap.AsParallelWriter()
            }.ScheduleParallel();

            // Second pass: Process collisions and TFL
            new TrophallaxisJob
            {
                SpatialHashMap = spatialHashMap,
                DeltaTime = SystemAPI.Time.DeltaTime
            }.Schedule();

            // Dispose the hash map
            spatialHashMap.Dispose(state.Dependency);
        }
    }

    /// <summary>
    /// Job to spatially hash ant positions for efficient collision detection
    /// </summary>
    [BurstCompile]
    public partial struct SpatialHashJob : IJobEntity
    {
        public NativeParallelMultiHashMap<int2, Entity>.ParallelWriter SpatialHashMap;

        void Execute(ref AntData ant, Entity entity)
        {
            // Convert position to grid cell (assuming 1 unit = 1 cell)
            int2 cell = new int2(
                (int)math.floor(ant.Position.x),
                (int)math.floor(ant.Position.z)
            );

            // Add entity to spatial hash
            SpatialHashMap.Add(cell, entity);
        }
    }

    /// <summary>
    /// Job to process Trophallaxis Federated Learning between colliding ants
    /// </summary>
    [BurstCompile]
    public partial struct TrophallaxisJob : IJob
    {
        [ReadOnly] public NativeParallelMultiHashMap<int2, Entity> SpatialHashMap;
        public float DeltaTime;

        public void Execute()
        {
            // Iterate through all cells in the spatial hash
            var iterator = SpatialHashMap.GetEnumerator();

            while (iterator.MoveNext())
            {
                var cellEntities = iterator.Current.Value;

                // Get all entities in this cell
                var entitiesInCell = new NativeList<Entity>(Allocator.Temp);

                // Collect all entities in this cell
                if (SpatialHashMap.TryGetFirstValue(cellEntities.Key, out Entity firstEntity, out var it))
                {
                    entitiesInCell.Add(firstEntity);

                    while (SpatialHashMap.TryGetNextValue(out Entity nextEntity, ref it))
                    {
                        entitiesInCell.Add(nextEntity);
                    }
                }

                // Process collisions between entities in this cell
                ProcessCellCollisions(entitiesInCell);

                entitiesInCell.Dispose();
            }
        }

        /// <summary>
        /// Process TFL between all ants in a single grid cell
        /// </summary>
        private void ProcessCellCollisions(NativeList<Entity> entitiesInCell)
        {
            int count = entitiesInCell.Length;

            // Check each pair of ants in the cell
            for (int i = 0; i < count; i++)
            {
                for (int j = i + 1; j < count; j++)
                {
                    Entity antA = entitiesInCell[i];
                    Entity antB = entitiesInCell[j];

                    // Process TFL between these two ants
                    ProcessAntPair(antA, antB);
                }
            }
        }

        /// <summary>
        /// Process Trophallaxis Federated Learning between two specific ants
        /// </summary>
        private void ProcessAntPair(Entity antA, Entity antB)
        {
            // In a real implementation, we would access the AntData components here
            // For now, this is a placeholder showing the logic structure

            // Payload Protection Protocol:
            // - Only share knowledge (TargetMemory), not sugar if in RETURN state
            // - Transfer best resource locations for decentralized learning

            // Pseudocode for the actual implementation:
            /*
            ref AntData dataA = SystemAPI.GetComponent<AntData>(antA);
            ref AntData dataB = SystemAPI.GetComponent<AntData>(antB);

            // Check if they belong to the same tribe
            if (dataA.TribeId == dataB.TribeId)
            {
                // Metabolic sharing (only for non-returning agents)
                if (dataA.State != 1 && dataB.State != 1) // Neither is returning
                {
                    // Share sugar levels (averaging)
                    float avgSugar = (dataA.SugarLevel + dataB.SugarLevel) * 0.5f;
                    dataA.SugarLevel = avgSugar;
                    dataB.SugarLevel = avgSugar;
                }

                // Knowledge sharing: Always transfer best target memory
                if (dataA.State == 1 && math.all(dataA.TargetMemory != float3.zero))
                {
                    // Ant A is returning with valuable knowledge
                    if (dataB.State == 0) // Ant B is exploring
                    {
                        // Transfer knowledge
                        dataB.TargetMemory = dataA.TargetMemory;
                        dataB.State = 2; // Switch to EXPLOIT_MEMORY

                        // Reward the knowledge donor
                        dataA.Xp += 1;
                    }
                }
                else if (dataB.State == 1 && math.all(dataB.TargetMemory != float3.zero))
                {
                    // Ant B is returning with valuable knowledge
                    if (dataA.State == 0) // Ant A is exploring
                    {
                        // Transfer knowledge
                        dataA.TargetMemory = dataB.TargetMemory;
                        dataA.State = 2; // Switch to EXPLOIT_MEMORY

                        // Reward the knowledge donor
                        dataB.Xp += 1;
                    }
                }
            }
            */
        }
    }

    /// <summary>
    /// System for processing ant deaths and biomass recycling
    /// </summary>
    [BurstCompile]
    public partial struct AntDeathSystem : ISystem
    {
        private EntityCommandBufferSystem _ecbSystem;

        [BurstCompile]
        public void OnCreate(ref SystemState state)
        {
            _ecbSystem = state.World.GetOrCreateSystem<EntityCommandBufferSystem>();
        }

        [BurstCompile]
        public void OnUpdate(ref SystemState state)
        {
            var ecb = _ecbSystem.CreateCommandBuffer();

            // Schedule job to process dead ants
            new DeathProcessingJob
            {
                ECB = ecb,
                DeltaTime = SystemAPI.Time.DeltaTime
            }.Schedule();
        }
    }

    /// <summary>
    /// Job to process ant deaths and trigger biomass recycling
    /// </summary>
    [BurstCompile]
    public partial struct DeathProcessingJob : IJobEntity
    {
        public EntityCommandBuffer ECB;
        public float DeltaTime;

        void Execute(Entity entity, ref AntData ant)
        {
            // Check for death conditions
            if (ant.EnergyReserve <= 0.0f || ant.Age >= ant.Lifespan)
            {
                // Death: Drop carried resource and recycle biomass
                // In a real implementation, this would:
                // 1. Create a resource entity at current position
                // 2. Add biomass to colony reserves
                // 3. Destroy the ant entity

                ECB.DestroyEntity(entity);
            }
        }
    }
}