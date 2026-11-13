import unittest

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


# --- 1. Priority Dispatch Queue Tests ---

def test_priority_dispatch_critical_before_routine_with_fifo() -> None:
    dispatcher = IncidentDispatcher()
    inc1 = Incident("INC-001", "Noise complaint", "Hatfield", Severity.ROUTINE)
    inc2 = Incident("INC-002", "Minor fender-bender", "Brooklyn", Severity.ROUTINE)
    inc3 = Incident("INC-003", "Cardiac arrest", "Menlyn", Severity.CRITICAL)
    inc4 = Incident("INC-004", "Structure fire", "Arcadia", Severity.CRITICAL)

    for inc in (inc1, inc2, inc3, inc4):
        dispatcher.log_incident(inc)

    # Critical incidents must dispatch first in FIFO order, followed by routine in FIFO order
    assert dispatcher.dispatch_next().incident_id == "INC-003"
    assert dispatcher.dispatch_next().incident_id == "INC-004"
    assert dispatcher.dispatch_next().incident_id == "INC-001"
    assert dispatcher.dispatch_next().incident_id == "INC-002"
    assert dispatcher.is_empty()


def test_dispatch_empty_queue_raises_error() -> None:
    dispatcher = IncidentDispatcher()
    with unittest.TestCase().assertRaises(EmptyDispatchError):
        dispatcher.dispatch_next()


def test_invalid_incident_severity_raises_error() -> None:
    with unittest.TestCase().assertRaises(InvalidIncidentError):
        Incident("INC-999", "Unknown call", "Centurion", severity="HIGH")  # type: ignore[arg-type]


# --- 2. Fleet Registry Tests ---

def test_fleet_registry_lookup_and_normalization() -> None:
    registry = FleetRegistry()
    amb = Vehicle("rv-101-gp", "Ambulance", crew=["Mokoena", "Botha"])
    registry.register_vehicle(amb)

    found = registry.get_vehicle("  RV-101-GP ")
    assert found.unit_type == "Ambulance"
    assert found.crew == ["Mokoena", "Botha"]


def test_fleet_registry_missing_vehicle_raises_error() -> None:
    registry = FleetRegistry()
    with unittest.TestCase().assertRaises(VehicleNotFoundError):
        registry.get_vehicle("NON-EXISTENT-99")


# --- 3. Custom Suburb Hash Table & BST Tests ---

def test_suburb_hash_table_crud_and_incident_counting() -> None:
    table = SuburbHashTable(initial_capacity=4)  # Small capacity forces resizing
    suburbs = [
        "Hatfield", "Brooklyn", "Menlyn", "Arcadia",
        "Sunnyside", "Lynnwood", "Centurion", "Waterkloof",
    ]
    for s in suburbs:
        table.add_suburb(s, initial_incidents=1)

    assert len(table) == 8
    assert table.find_suburb("menlyn") == {"suburb": "Menlyn", "incident_count": 1}

    new_count = table.record_incident("Menlyn")
    assert new_count == 2
    assert table.find_suburb("UNKNOWN") is None


def test_suburb_bst_alphabetical_listing() -> None:
    bst = SuburbBST()
    unsorted_suburbs = [
        ("Menlyn", 4),
        ("Arcadia", 2),
        ("Waterkloof", 1),
        ("Brooklyn", 5),
        ("Hatfield", 3),
        ("Sunnyside", 6),
        ("Centurion", 2),
        ("Lynnwood", 1),
    ]
    for name, count in unsorted_suburbs:
        bst.add_suburb(name, count)

    alphabetical = [name for name, _ in bst.get_alphabetical_suburbs()]
    assert alphabetical == sorted(name for name, _ in unsorted_suburbs)


# --- 4. Road Network Graph Routing Tests ---

def test_road_network_dfs_and_shortest_paths() -> None:
    net = RoadNetwork()
    net.add_location("Depot", 0.0, 0.0)
    net.add_location("NorthBridge", 2.0, 4.0)
    net.add_location("SouthBridge", 3.0, -2.0)
    net.add_location("Menlyn", 6.0, 3.0)
    net.add_location("IsolatedPark", 10.0, 10.0)

    net.add_road("Depot", "NorthBridge", 5.0, one_way=True)
    net.add_road("NorthBridge", "Menlyn", 4.0)
    net.add_road("Depot", "SouthBridge", 3.0)
    net.add_road("SouthBridge", "Menlyn", 10.0)

    # Reachability via recursive DFS
    assert net.has_path_dfs("Depot", "Menlyn") is not None
    assert net.has_path_dfs("Depot", "IsolatedPark") is None

    # Shortest path comparison (Dijkstra vs A*)
    d_cost, d_path = net.shortest_path_dijkstra("Depot", "Menlyn")
    a_cost, a_path = net.shortest_path_astar("Depot", "Menlyn")
    assert d_cost == a_cost == 9.0
    assert d_path == a_path == ["Depot", "NorthBridge", "Menlyn"]