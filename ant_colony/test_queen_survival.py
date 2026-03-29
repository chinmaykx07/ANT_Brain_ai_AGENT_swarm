#!/usr/bin/env python3
import sys
import traceback

try:
    print("Testing queen survival for 2000+ cycles...")
    from model import AntColonyModel
    from agent import QueenAgent
    print("✓ Model imported successfully")

    # Use smaller grid for faster testing
    model = AntColonyModel(width=20, height=20, initial_ants=10)
    print(f"✓ Model created with {len(model.schedule.agents)} agents")

    queen = None
    for agent in model.schedule.agents:
        if isinstance(agent, QueenAgent):
            queen = agent
            break

    if not queen:
        print("✗ No queen found!")
        sys.exit(1)

    print("Running simulation for 2000 steps...")
    queen_survival_steps = 0
    max_population = 0
    min_population = float('inf')
    food_history = []

    for step in range(2000):
        model.step()

        # Check if queen is still alive
        if queen not in model.schedule.agents:
            print(f"Queen died at step {step}")
            break

        queen_survival_steps = step + 1

        # Track population and food
        ant_count = len([a for a in model.schedule.agents if hasattr(a, 'energy_reserve')])
        max_population = max(max_population, ant_count)
        min_population = min(min_population, ant_count)
        food_inventory = model.resource_inventory.get("food", 0)
        food_history.append(food_inventory)

        # Print progress every 100 steps
        if step % 100 == 0:
            queen_health = queen.health
            print(f"Step {step}: Queen Health {queen_health}, Food Inventory {food_inventory}, Population {ant_count}")

    # Analyze food production
    if food_history:
        avg_food = sum(food_history) / len(food_history)
        min_food = min(food_history)
        max_food = max(food_history)
        print(f"Food stats: Avg {avg_food:.1f}, Min {min_food}, Max {max_food}")

    if queen_survival_steps >= 2000:
        print("✓ SUCCESS: Queen survived 2000+ cycles!")
    else:
        print(f"✗ FAILURE: Queen only survived {queen_survival_steps} cycles")

    print(f"Max Population: {max_population}, Min Population: {min_population}")

except Exception as e:
    print(f"✗ Error: {e}", file=sys.stderr)
    traceback.print_exc()
    sys.exit(1)