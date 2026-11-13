from dataclasses import dataclass


class SuburbHashTable:
    """Custom Hash Table with separate chaining for O(1) average suburb lookup and incident counting."""

    def __init__(self, initial_capacity: int = 16) -> None:
        self._capacity = max(4, initial_capacity)
        self._buckets: list[list[list]] = [[] for _ in range(self._capacity)]
        self._size = 0

    def _hash(self, key: str) -> int:
        """Polynomial rolling hash mapped into current bucket capacity."""
        normalized = key.strip().lower()
        hash_val = 0
        for char in normalized:
            hash_val = (hash_val * 31 + ord(char)) % self._capacity
        return hash_val

    def _resize(self) -> None:
        """Double bucket capacity and rehash entries when load factor > 0.75."""
        old_buckets = self._buckets
        self._capacity *= 2
        self._buckets = [[] for _ in range(self._capacity)]
        self._size = 0
        for bucket in old_buckets:
            for suburb_name, count in bucket:
                self.add_suburb(suburb_name, count)

    def add_suburb(self, suburb_name: str, initial_incidents: int = 0) -> None:
        """Insert a new suburb or update its incident count if it already exists."""
        clean_name = suburb_name.strip()
        if not clean_name:
            raise ValueError("Suburb name cannot be empty.")

        if (self._size + 1) / self._capacity > 0.75:
            self._resize()

        index = self._hash(clean_name)
        bucket = self._buckets[index]
        for entry in bucket:
            if entry[0].lower() == clean_name.lower():
                entry[0] = clean_name
                entry[1] = initial_incidents
                return

        bucket.append([clean_name, initial_incidents])
        self._size += 1

    def find_suburb(self, suburb_name: str) -> dict[str, str | int] | None:
        """Look up a suburb record in O(1) average time."""
        index = self._hash(suburb_name)
        target = suburb_name.strip().lower()
        for name, count in self._buckets[index]:
            if name.lower() == target:
                return {"suburb": name, "incident_count": count}
        return None

    def record_incident(self, suburb_name: str) -> int:
        """Increment the incident counter for a suburb (auto-adding if new) and return new total."""
        index = self._hash(suburb_name)
        clean_name = suburb_name.strip()
        for entry in self._buckets[index]:
            if entry[0].lower() == clean_name.lower():
                entry[1] += 1
                return entry[1]

        self.add_suburb(clean_name, initial_incidents=1)
        return 1

    def get_all_suburbs(self) -> list[tuple[str, int]]:
        """Return all stored (suburb, incident_count) pairs in bucket order."""
        records: list[tuple[str, int]] = []
        for bucket in self._buckets:
            for name, count in bucket:
                records.append((name, count))
        return records

    def __len__(self) -> int:
        return self._size


@dataclass
class BSTNode:
    """Node in a Binary Search Tree storing a suburb name and its incident count."""
    suburb: str
    incident_count: int = 0
    left: "BSTNode | None" = None
    right: "BSTNode | None" = None


class SuburbBST:
    """Binary Search Tree maintaining suburbs in natural lexicographical order."""

    def __init__(self) -> None:
        self.root: BSTNode | None = None
        self._size = 0

    def add_suburb(self, suburb_name: str, incident_count: int = 0) -> None:
        """Insert a suburb into the BST in O(log n) average time."""
        clean_name = suburb_name.strip()
        if not clean_name:
            raise ValueError("Suburb name cannot be empty.")
        self.root = self._insert_recursive(self.root, clean_name, incident_count)

    def _insert_recursive(
        self, node: BSTNode | None, suburb_name: str, incident_count: int
    ) -> BSTNode:
        if node is None:
            self._size += 1
            return BSTNode(suburb=suburb_name, incident_count=incident_count)

        key_new = suburb_name.lower()
        key_cur = node.suburb.lower()

        if key_new < key_cur:
            node.left = self._insert_recursive(node.left, suburb_name, incident_count)
        elif key_new > key_cur:
            node.right = self._insert_recursive(node.right, suburb_name, incident_count)
        else:
            node.incident_count = incident_count
        return node

    def find_suburb(self, suburb_name: str) -> BSTNode | None:
        """Search for a suburb node in O(log n) average time."""
        target = suburb_name.strip().lower()
        current = self.root
        while current is not None:
            cur_key = current.suburb.lower()
            if target == cur_key:
                return current
            current = current.left if target < cur_key else current.right
        return None

    def get_alphabetical_suburbs(self) -> list[tuple[str, int]]:
        """Perform an in-order traversal (Left -> Root -> Right) to return suburbs alphabetically."""
        ordered: list[tuple[str, int]] = []
        self._in_order(self.root, ordered)
        return ordered

    def _in_order(self, node: BSTNode | None, acc: list[tuple[str, int]]) -> None:
        if node is None:
            return
        self._in_order(node.left, acc)
        acc.append((node.suburb, node.incident_count))
        self._in_order(node.right, acc)

    def __len__(self) -> int:
        return self._size