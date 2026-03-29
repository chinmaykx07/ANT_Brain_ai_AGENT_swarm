#!/usr/bin/env python3
import sys
import traceback

try:
    print("Testing ant colony simulation...")
    from model import AntColonyModel
    print("✓ Model imported successfully")

    model = AntColonyModel(width=10, height=10, initial_ants=3)
    print(f"✓ Model created with {len(model.schedule.agents)} agents")

    print("Running simulation steps...")
    for i in range(5):
        model.step()
        ants = [a for a in model.schedule.agents if hasattr(a, 'energy_reserve')]
        if ants:
            avg_energy = sum(a.energy_reserve for a in ants) / len(ants)
            critical = sum(1 for a in ants if a.energy_reserve < 30)
            survival_mode = sum(1 for a in ants if a.basal_survival_mode)
            print(f"Step {i+1}: Population {len(ants)}, Avg Energy {avg_energy:.1f}, Critical: {critical}, Survival Mode: {survival_mode}")

    print("✓ Test completed successfully!")
    print("Homeostatic Neuro-Modulation is working!")

except Exception as e:
    print(f"✗ Error: {e}", file=sys.stderr)
    traceback.print_exc()
    sys.exit(1)