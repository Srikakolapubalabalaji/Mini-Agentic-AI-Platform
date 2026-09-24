import json
from pathlib import Path

import networkx as nx


class KnowledgeGraph:
    """
    Lightweight NetworkX knowledge graph for dependency and blast radius calculation.
    """

    def __init__(self, data_path: str):
        self.graph = nx.DiGraph()
        self._load(data_path)

    def _load(self, data_path: str):
        path = Path(data_path)
        if not path.exists():
            return

        with open(path) as f:
            data = json.load(f)

        for svc in data.get("services", []):
            self.graph.add_node(svc["id"], **svc)

        for dep in data.get("dependencies", []):
            self.graph.add_edge(dep["source"], dep["target"])

    def get_downstream_dependencies(self, service: str) -> list[str]:
        if service not in self.graph:
            return []
        # Downstream = nodes reachable from this service
        return list(nx.descendants(self.graph, service))

    def get_upstream_dependencies(self, service: str) -> list[str]:
        if service not in self.graph:
            return []
        # Upstream = nodes that can reach this service (reverse graph)
        rev_graph = self.graph.reverse()
        return list(nx.descendants(rev_graph, service))

    def check_blast_radius(self, service: str) -> str:
        downstream = self.get_downstream_dependencies(service)
        if len(downstream) > 5:
            return "high"
        elif len(downstream) > 1:
            return "medium"
        return "low"
