"""Graph Cycle Deadlock Detector.
100% Python Standard Library.
"""
from typing import Dict, Any, List, Set

class GraphCycleDeadlockDetector:
    """Tarjan SCC and cycle detector for multi-agent DAG validation and resource deadlocks."""

    @staticmethod
    def validate_dag(nodes: List[str], edges: List[Dict[str, str]]) -> Dict[str, Any]:
        adj: Dict[str, List[str]] = {n: [] for n in nodes}
        in_degree: Dict[str, int] = {n: 0 for n in nodes}

        for e in edges:
            u = e["from"]
            v = e["to"]
            if u not in adj:
                adj[u] = []
                nodes.append(u)
                in_degree[u] = 0
            if v not in adj:
                adj[v] = []
                nodes.append(v)
                in_degree[v] = 0
            adj[u].append(v)
            in_degree[v] += 1

        idx = 0
        indices: Dict[str, int] = {}
        lowlinks: Dict[str, int] = {}
        on_stack: Set[str] = set()
        stack: List[str] = []
        sccs: List[List[str]] = []

        def strongconnect(v: str):
            nonlocal idx
            indices[v] = idx
            lowlinks[v] = idx
            idx += 1
            stack.append(v)
            on_stack.add(v)

            for w in adj[v]:
                if w not in indices:
                    strongconnect(w)
                    lowlinks[v] = min(lowlinks[v], lowlinks[w])
                elif w in on_stack:
                    lowlinks[v] = min(lowlinks[v], indices[w])

            if lowlinks[v] == indices[v]:
                scc = []
                while True:
                    w = stack.pop()
                    on_stack.remove(w)
                    scc.append(w)
                    if w == v:
                        break
                sccs.append(scc)

        for n in nodes:
            if n not in indices:
                strongconnect(n)

        cycles = []
        for scc in sccs:
            if len(scc) > 1:
                cycles.append(scc)
            elif len(scc) == 1:
                node = scc[0]
                if node in adj[node]:
                    cycles.append([node, node])

        is_dag = (len(cycles) == 0)
        topo_order: List[str] = []

        if is_dag:
            queue = [n for n in nodes if in_degree[n] == 0]
            curr_in = dict(in_degree)
            while queue:
                curr = queue.pop(0)
                topo_order.append(curr)
                for neighbor in adj[curr]:
                    curr_in[neighbor] -= 1
                    if curr_in[neighbor] == 0:
                        queue.append(neighbor)

        return {
            "is_dag": is_dag,
            "has_cycles": not is_dag,
            "total_nodes": len(nodes),
            "total_edges": len(edges),
            "cycles_detected": cycles,
            "topological_order": topo_order if is_dag else None
        }

    @staticmethod
    def detect_deadlocks(active_locks: Dict[str, str], waiting_locks: Dict[str, str]) -> Dict[str, Any]:
        agents = set(list(waiting_locks.keys()) + list(active_locks.values()))
        wfg_edges = []
        for waiting_agent, res in waiting_locks.items():
            if res in active_locks:
                holding_agent = active_locks[res]
                if waiting_agent != holding_agent:
                    wfg_edges.append({"from": waiting_agent, "to": holding_agent, "resource": res})

        nodes = list(agents)
        res = GraphCycleDeadlockDetector.validate_dag(nodes, [{"from": e["from"], "to": e["to"]} for e in wfg_edges])

        deadlocks = []
        if res["has_cycles"]:
            for cyc in res["cycles_detected"]:
                deadlocks.append({
                    "involved_agents": cyc,
                    "deadlock_type": "cyclic_wait"
                })

        return {
            "deadlock_detected": res["has_cycles"],
            "deadlock_count": len(deadlocks),
            "deadlocks": deadlocks,
            "wait_for_edges": wfg_edges
        }

    @staticmethod
    def suggest_cycle_resolution(cycles: List[List[str]]) -> Dict[str, Any]:
        suggestions = []
        for cyc in cycles:
            if len(cyc) >= 2:
                suggestions.append({
                    "cycle": cyc,
                    "recommended_break_edge": {"from": cyc[-1], "to": cyc[0]},
                    "rationale": "Breaking the feedback arc restores DAG acyclicity."
                })
            elif len(cyc) == 1:
                suggestions.append({
                    "cycle": cyc,
                    "recommended_break_edge": {"from": cyc[0], "to": cyc[0]},
                    "rationale": "Eliminate self-loop dependency."
                })
        return {
            "resolution_count": len(suggestions),
            "suggestions": suggestions
        }
