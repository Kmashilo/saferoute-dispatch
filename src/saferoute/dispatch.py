import heapq
from itertools import count
from .models import EmptyDispatchError, Incident, InvalidIncidentError


class IncidentDispatcher:
    """Priority-based emergency dispatch queue preserving FIFO order within priority tiers."""

    def __init__(self) -> None:
        self._heap: list[tuple[int, int, Incident]] = []
        self._sequence = count()

    def log_incident(self, incident: Incident) -> None:
        """Add a validated incident to the dispatch queue in O(log n) time."""
        if not isinstance(incident, Incident):
            raise InvalidIncidentError("Expected an Incident instance.")
        entry = (-int(incident.severity), next(self._sequence), incident)
        heapq.heappush(self._heap, entry)

    def dispatch_next(self) -> Incident:
        """Remove and return the highest-priority (and oldest) incident in O(log n) time."""
        if self.is_empty():
            raise EmptyDispatchError("Cannot dispatch: no incidents are currently waiting.")
        _, _, incident = heapq.heappop(self._heap)
        return incident

    def peek_next(self) -> Incident:
        """Inspect the next incident to be dispatched without removing it in O(1) time."""
        if self.is_empty():
            raise EmptyDispatchError("Queue is empty.")
        return self._heap[0][2]

    def is_empty(self) -> bool:
        return len(self._heap) == 0

    def __len__(self) -> int:
        return len(self._heap)