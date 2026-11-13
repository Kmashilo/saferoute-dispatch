from saferoute.benchmarks import benchmark_vehicle_lookup
from saferoute.dispatch import IncidentDispatcher
from saferoute.fleet import FleetRegistry
from saferoute.models import (
    EmptyDispatchError,
    Incident,
    InvalidIncidentError,
    Severity,
    Vehicle,
    VehicleNotFoundError,
)
from saferoute.routing import RoadNetwork
from saferoute.suburbs import SuburbBST, SuburbHashTable


def run_demo() -> None:
    print("=== 1. PRIORITY INCIDENT DISPATCH (FIFO WITHIN PRIORITY) ===")
    dispatcher = IncidentDispatcher()
    calls = [
        Incident("INC-101", "Noise complaint", "Hatfield", Severity.ROUTINE),
        Incident("INC-102", "Minor fender-bender", "Brooklyn", Severity.ROUTINE),
        Incident("INC-103", "Cardiac arrest", "Menlyn", Severity.CRITICAL),
        Incident("INC-104", "Structure fire with trapped occupants", "Arcadia", Severity.CRITICAL),
    ]
    for call in calls:
        dispatcher.log_incident(call)

    while not dispatcher.is_empty():
        nxt = dispatcher.dispatch_next()
        print(f"Dispatched [{nxt.severity.name}] {nxt.incident_id}: {nxt.description} ({nxt.suburb})")

    print("\n=== 2. FLEET REGISTRY & DEFENSIVE ERROR HANDLING ===")
    fleet = FleetRegistry()
    fleet.register_vehicle(Vehicle("RV-001-GP", "Ambulance", ["T. Nkosi", "L. van Wyk"]))
    fleet.register_vehicle(Vehicle("RV-002-GP", "Fire Engine", ["S. Naidoo", "K. Mashilo"]))
    fleet.register_vehicle(Vehicle("RV-003-GP", "Traffic Unit", ["M. Dlamini"]))

    unit = fleet.get_vehicle("rv-002-gp")
    print(f"Lookup RV-002-GP -> {unit.unit_type} | Status: {unit.status} | Crew: {unit.crew}")

    for label, action in [
        ("Empty queue dispatch", lambda: dispatcher.dispatch_next()),
        ("Missing vehicle lookup", lambda: fleet.get_vehicle("RV-999-GP")),
        ("Invalid incident severity", lambda: Incident("INC-ERR", "Test", "CBD", "URGENT")),  # type: ignore[arg-type]
    ]:
        try:
            action()
        except (EmptyDispatchError, VehicleNotFoundError, InvalidIncidentError) as err:
            print(f"Handled [{label}]: {type(err).__name__} -> {err}")

    print("\n=== 3. EMPIRICAL BENCHMARK: HASH TABLE O(1) vs LINEAR SEARCH O(n) ===")
    for row in benchmark_vehicle_lookup(sizes=(1_000, 50_000), iterations=1_000):
        print(
            f"Size: {row['dataset_size']:>6} | "
            f"Hash: {row['hash_total_ms']:>7.4f} ms | "
            f"Linear: {row['linear_total_ms']:>8.4f} ms | "
            f"Speedup: {row['speedup_factor']}x"
        )

    print("\n=== 4. SUBURB INDEXING (CUSTOM HASH TABLE & BST) ===")
    suburb_data = [
        ("Menlyn", 5), ("Arcadia", 3), ("Waterkloof", 1), ("Brooklyn", 4),
        ("Hatfield", 6), ("Sunnyside", 7), ("Centurion", 2), ("Lynnwood", 2),
    ]
    hash_index = SuburbHashTable()
    bst_index = SuburbBST()
    for name, count in suburb_data:
        hash_index.add_suburb(name, count)
        bst_index.add_suburb(name, count)

    updated = hash_index.record_incident("Menlyn")
    print(f"Hash Table lookup 'Menlyn' after new incident: {hash_index.find_suburb('Menlyn')} (updated={updated})")
    print("BST Alphabetical Suburb Report:")
    for suburb, count in bst_index.get_alphabetical_suburbs():
        print(f"  - {suburb:<12} ({count} incidents)")

    print("\n=== 5. ROAD NETWORK ROUTING (DFS, DIJKSTRA & A*) ===")
    road_net = RoadNetwork()
    road_net.add_location("Depot", 0.0, 0.0)
    road_net.add_location("NorthBridge", 2.0, 4.0)
    road_net.add_location("SouthBridge", 3.0, -2.0)
    road_net.add_location("Menlyn", 6.0, 3.0)

    road_net.add_road("Depot", "NorthBridge", 5.0, one_way=True)
    road_net.add_road("NorthBridge", "Menlyn", 4.0)
    road_net.add_road("Depot", "SouthBridge", 3.0)
    road_net.add_road("SouthBridge", "Menlyn", 10.0)

    print("DFS Reachable Path:", " -> ".join(road_net.has_path_dfs("Depot", "Menlyn") or []))
    cost, route = road_net.shortest_path_astar("Depot", "Menlyn")
    print(f"A* Fastest Route ({cost} mins):", " -> ".join(route))


if __name__ == "__main__":
    run_demo()