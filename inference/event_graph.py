try:
    import networkx as nx
except ImportError:
    nx = None

from typing import List, Dict, Any


class EventInteractionGraph:
    def __init__(self):
        self.graph = nx.DiGraph() if nx else None
        self.internal_nodes = {}
        self.internal_edges = []

    def build_graph(self, actions: List[Dict[str, Any]], highlights: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Builds the temporal interaction graph and converts to React Flow node/edge format.
        """
        if self.graph is not None:
            self.graph.clear()
        self.internal_nodes.clear()
        self.internal_edges.clear()

        if highlights is None:
            highlights = []

        def is_hl(s: float, e: float) -> bool:
            return any(
                (s >= h["segment"][0] and s <= h["segment"][1]) or
                (e >= h["segment"][0] and e <= h["segment"][1])
                for h in highlights
            )

        react_nodes = []
        react_edges = []

        # 1. Add Event Nodes
        for i, act in enumerate(actions):
            node_id = f"node-{i+1}"
            s, e = act["segment"]
            in_hl = is_hl(s, e)

            x_pos = 50 + i * 210
            y_pos = 100 + (30 if i % 2 == 0 else -30)

            node_data = {
                "id": node_id,
                "label": f"{act['verb']} {act['noun']}",
                "verb": act["verb"],
                "noun": act["noun"],
                "start": s,
                "end": e,
                "score": act.get("score", 0.8),
                "isHighlight": in_hl,
            }

            if self.graph is not None:
                self.graph.add_node(
                    node_id,
                    verb=act["verb"],
                    noun=act["noun"],
                    start=s,
                    end=e,
                    score=act.get("score", 0.8),
                    is_highlight=in_hl,
                )
            self.internal_nodes[node_id] = node_data

            react_nodes.append({
                "id": node_id,
                "position": {"x": x_pos, "y": y_pos},
                "data": node_data,
                "type": "actionNode",
            })

        # 2. Add Relational Edges
        # Temporal sequence edges
        for i in range(len(actions) - 1):
            src_id = f"node-{i+1}"
            tgt_id = f"node-{i+2}"
            edge_id = f"e-temporal-{i+1}-{i+2}"

            if self.graph is not None:
                self.graph.add_edge(src_id, tgt_id, edge_type="temporal", label="then")
            self.internal_edges.append((src_id, tgt_id, "temporal"))

            react_edges.append({
                "id": edge_id,
                "source": src_id,
                "target": tgt_id,
                "animated": True,
                "data": {"id": edge_id, "source": src_id, "target": tgt_id, "type": "temporal", "label": "then"}
            })

        # Shared noun / tool interaction edges
        for i in range(len(actions)):
            for j in range(i + 1, len(actions)):
                if actions[i]["noun"] == actions[j]["noun"]:
                    src_id = f"node-{i+1}"
                    tgt_id = f"node-{j+1}"
                    edge_id = f"e-shared-{i+1}-{j+1}"

                    if self.graph is not None:
                        self.graph.add_edge(src_id, tgt_id, edge_type="shared_noun", label=f"shared {actions[i]['noun']}")
                    self.internal_edges.append((src_id, tgt_id, "shared_noun"))

                    react_edges.append({
                        "id": edge_id,
                        "source": src_id,
                        "target": tgt_id,
                        "animated": False,
                        "data": {
                            "id": edge_id,
                            "source": src_id,
                            "target": tgt_id,
                            "type": "shared_noun",
                            "label": f"shared {actions[i]['noun']}"
                        }
                    })

        return {
            "nodes": react_nodes,
            "edges": react_edges,
        }

    def get_unique_action_pairs_count(self) -> int:
        pairs = set()
        for node in self.internal_nodes.values():
            v = node.get("verb")
            n = node.get("noun")
            if v and n:
                pairs.add((v, n))
        return len(pairs)
