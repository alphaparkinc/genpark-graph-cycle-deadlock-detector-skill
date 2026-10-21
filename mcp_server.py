"""MCP Stdio Server for Graph Cycle Deadlock Detector.
100% Python Standard Library.
"""
import sys
import json
from client import GraphCycleDeadlockDetector

detector = GraphCycleDeadlockDetector()

def handle_rpc(line):
    try:
        req = json.loads(line)
    except Exception:
        return
    req_id = req.get("id")
    method = req.get("method")
    params = req.get("params", {})

    if method == "initialize":
        res = {
            "protocolVersion": "2024-11-05",
            "serverInfo": {"name": "genpark-graph-cycle-deadlock-detector-skill", "version": "1.0.1"},
            "capabilities": {"tools": {}}
        }
        send_response(req_id, res)
    elif method == "tools/list":
        tools = [
            {
                "name": "validate_dag",
                "description": "Run Tarjan SCC check and topological sort on agent dependency graph",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "nodes": {"type": "array", "items": {"type": "string"}},
                        "edges": {"type": "array", "items": {"type": "object"}}
                    },
                    "required": ["nodes", "edges"]
                }
            },
            {
                "name": "detect_deadlocks",
                "description": "Detect cyclic lock acquisition deadlocks in a Wait-For Graph",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "active_locks": {"type": "object"},
                        "waiting_locks": {"type": "object"}
                    },
                    "required": ["active_locks", "waiting_locks"]
                }
            },
            {
                "name": "suggest_cycle_resolution",
                "description": "Calculate minimum feedback arc set heuristics to resolve cycles",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "cycles": {"type": "array", "items": {"type": "array", "items": {"type": "string"}}}
                    },
                    "required": ["cycles"]
                }
            }
        ]
        send_response(req_id, {"tools": tools})
    elif method == "tools/call":
        name = params.get("name")
        args = params.get("arguments", {})
        if name == "validate_dag":
            out = detector.validate_dag(args.get("nodes", []), args.get("edges", []))
        elif name == "detect_deadlocks":
            out = detector.detect_deadlocks(args.get("active_locks", {}), args.get("waiting_locks", {}))
        elif name == "suggest_cycle_resolution":
            out = detector.suggest_cycle_resolution(args.get("cycles", []))
        else:
            send_error(req_id, -32601, f"Unknown tool: {name}")
            return
        send_response(req_id, {"content": [{"type": "text", "text": json.dumps(out, indent=2)}]})

def send_response(req_id, result):
    sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": req_id, "result": result}) + "\n")
    sys.stdout.flush()

def send_error(req_id, code, message):
    sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}}) + "\n")
    sys.stdout.flush()

def main():
    for line in sys.stdin:
        if line.strip():
            handle_rpc(line.strip())

if __name__ == "__main__":
    main()
