"""Example usage for GenPark Graph Cycle Deadlock Detector."""
from client import GraphCycleDeadlockDetector

def main():
    print("Validating DAG workflow...")
    dag = GraphCycleDeadlockDetector.validate_dag(
        nodes=["fetcher", "transformer", "summarizer"],
        edges=[{"from": "fetcher", "to": "transformer"}, {"from": "transformer", "to": "summarizer"}]
    )
    print("DAG Valid:", dag["is_dag"], "| Order:", dag["topological_order"])

    print("
Detecting Cyclic Deadlocks...")
    deadlock = GraphCycleDeadlockDetector.detect_deadlocks(
        active_locks={"db_table": "agent_alpha", "file_lock": "agent_beta"},
        waiting_locks={"agent_alpha": "file_lock", "agent_beta": "db_table"}
    )
    print("Deadlock Detected:", deadlock["deadlock_detected"])
    print("Involved Deadlocks:", deadlock["deadlocks"])

if __name__ == "__main__":
    main()
