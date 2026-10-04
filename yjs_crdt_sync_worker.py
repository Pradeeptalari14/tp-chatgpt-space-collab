"""CRDT State Synchronization Worker for Multi-Agent Canvas.

Provides Conflict-free Replicated Data Type (CRDT) merge semantics and vector clock
tracking for simultaneous human-agent canvas manipulations.
"""

import logging
from typing import Any, Dict, List

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("crdt_sync_worker")


class VectorClock:
    """Logical clock keeping track of distributed participant update causality."""

    def __init__(self, node_id: str):
        self.node_id = node_id
        self.clock: Dict[str, int] = {node_id: 0}

    def increment(self) -> Dict[str, int]:
        self.clock[self.node_id] = self.clock.get(self.node_id, 0) + 1
        return dict(self.clock)

    def merge(self, incoming: Dict[str, int]) -> Dict[str, int]:
        for k, v in incoming.items():
            self.clock[k] = max(self.clock.get(k, 0), v)
        return dict(self.clock)


class CRDTCanvasStore:
    """Manages conflict-free document graph updates with Last-Write-Wins (LWW) registers."""

    def __init__(self):
        self.registers: Dict[str, Dict[str, Any]] = {}

    def set_property(
        self,
        element_id: str,
        prop_key: str,
        prop_value: Any,
        timestamp: float,
        author: str,
    ) -> bool:
        key = f"{element_id}:{prop_key}"
        current = self.registers.get(key)
        if current is None or timestamp >= current["timestamp"]:
            self.registers[key] = {
                "element_id": element_id,
                "prop_key": prop_key,
                "value": prop_value,
                "timestamp": timestamp,
                "author": author,
            }
            logger.info("CRDT Register updated: %s = %s by %s", key, prop_value, author)
            return True
        logger.warning("Stale update rejected for %s: incoming %f < current %f", key, timestamp, current["timestamp"])
        return False

    def export_elements(self) -> List[Dict[str, Any]]:
        elements: Dict[str, Dict[str, Any]] = {}
        for entry in self.registers.values():
            elem_id = entry["element_id"]
            if elem_id not in elements:
                elements[elem_id] = {"id": elem_id}
            elements[elem_id][entry["prop_key"]] = entry["value"]
        return list(elements.values())


def run_crdt_demo() -> None:
    vc1 = VectorClock("agent-coder")
    vc2 = VectorClock("agent-security")

    store = CRDTCanvasStore()
    store.set_property("card-1", "title", "Draft Architecture", 100.0, "agent-coder")
    store.set_property("card-1", "title", "Approved Architecture", 101.5, "agent-security")
    # Simulate an out-of-order stale network packet
    store.set_property("card-1", "title", "Old Draft Title", 99.0, "agent-coder")

    vc1.increment()
    vc2.merge(vc1.clock)

    logger.info("Reconciled canvas elements: %s", store.export_elements())


if __name__ == "__main__":
    run_crdt_demo()
