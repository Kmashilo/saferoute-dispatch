# SafeRoute: Emergency Dispatch & Road Network Routing Engine

A modular Python 3 backend engine for municipal emergency response dispatch, high-throughput fleet lookup, suburb incident indexing, and directed road-network routing.

## Architecture & Data Structure Design

| Subsystem | Module | Data Structure / Algorithm | Time Complexity | Engineering Rationale |
| :--- | :--- | :--- | :--- | :--- |
| **Incident Intake** | `saferoute.dispatch` | Binary Min-Heap (`heapq`) + Monotonic Sequence Tie-Breaker | $O(\log n)$ push/pop | Guarantees `CRITICAL` incidents preempt `ROUTINE` calls while preserving strict FIFO order within identical priority tiers. |
| **Fleet Registry** | `saferoute.fleet` | Hash Table (`dict`) with Key Normalization | $O(1)$ average lookup | Eliminates $O(n)$ sequential scans across provincial fleets of 50,000+ vehicles. |
| **Suburb Reporting** | `saferoute.suburbs` | Custom Separate-Chaining Hash Table & Binary Search Tree | $O(1)$ hash / $O(n)$ in-order traversal | Hash table handles high-frequency incident counter increments; BST produces naturally sorted alphabetical suburb reports without post-sort overhead. |
| **Road Routing** | `saferoute.routing` | Directed Weighted Adjacency List + Recursive DFS, Dijkstra & $A^*$ | $O((V + E) \log V)$ | Models one-way roads and river crossings accurately; Euclidean heuristic guides $A^*$ toward incident coordinates. |

## Project Structure

```text
saferoute-dispatch/
├── src/saferoute/
│   ├── models.py       # Typed domain dataclasses, IntEnum priorities, custom exceptions
│   ├── dispatch.py     # Priority dispatch queue with FIFO tie-breaking
│   ├── fleet.py        # O(1) vehicle & crew registry
│   ├── suburbs.py      # From-scratch Hash Table (separate chaining) & Binary Search Tree
│   ├── routing.py      # Directed graph with recursive DFS, Dijkstra, and A* search
│   └── benchmarks.py   # Empirical latency comparison (Hash lookup vs Linear search)
├── tests/
│   └── test_saferoute.py
├── main.py
└── pyproject.toml

## Empirical Lookup Benchmarks (1,000 Iterations)

| Fleet Dataset Size | Hash Table (`FleetRegistry`) | List Linear Search | Speedup Factor |
| :--- | :--- | :--- | :--- |
| **1,000 vehicles** | `0.1639 ms` | `31.0172 ms` | **189.2x faster** |
| **50,000 vehicles** | `0.1793 ms` | `1939.9076 ms` | **10,819.3x faster** |