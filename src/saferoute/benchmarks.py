import time
from saferoute.fleet import FleetRegistry
from saferoute.models import Vehicle


def linear_search_vehicle(vehicles: list[Vehicle], target_fleet: str) -> Vehicle | None:
    """O(n) sequential scan through an unsorted list of vehicles."""
    target = target_fleet.strip().upper()
    for vehicle in vehicles:
        if vehicle.registration == target:
            return vehicle
    return None


def benchmark_vehicle_lookup(
    sizes: tuple[int, ...] = (1_000, 50_000),
    iterations: int = 1_000,
) -> list[dict[str, float | int]]:
    """Compare average lookup latency between FleetRegistry (hash table) and list linear search."""
    results: list[dict[str, float | int]] = []

    for size in sizes:
        registry = FleetRegistry()
        vehicle_list: list[Vehicle] = []

        for i in range(size):
            v = Vehicle(
                registration=f"RV-{i:06d}-GP",
                vehicle_type="Ambulance" if i % 2 == 0 else "Fire",
                crew=[f"Officer_{i}_A", f"Officer_{i}_B"],
            )
            registry.register_vehicle(v)
            vehicle_list.append(v)

        # Search for the last element (worst-case for linear search)
        target_key = f"RV-{size - 1:06d}-GP"

        start_hash = time.perf_counter()
        for _ in range(iterations):
            registry.get_vehicle(target_key)
        hash_elapsed_ms = (time.perf_counter() - start_hash) * 1000

        start_linear = time.perf_counter()
        for _ in range(iterations):
            linear_search_vehicle(vehicle_list, target_key)
        linear_elapsed_ms = (time.perf_counter() - start_linear) * 1000

        results.append(
            {
                "dataset_size": size,
                "iterations": iterations,
                "hash_total_ms": round(hash_elapsed_ms, 4),
                "linear_total_ms": round(linear_elapsed_ms, 4),
                "speedup_factor": round(linear_elapsed_ms / max(hash_elapsed_ms, 1e-9), 1),
            }
        )

    return results