import csv
import json
import os
import re
import sys
import time
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from code.graph import app
from code.utils.report_helper import generate_usage_report


def get_base_dir() -> str:
    """Resolves the absolute path to the workspace root directory."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = current_dir
    for _ in range(3):
        if os.path.exists(os.path.join(root_dir, "dataset")):
            return root_dir
        root_dir = os.path.dirname(root_dir)
    return os.getcwd()


def _case_sort_key(case_id):
    match = re.search(r"(\d+)", str(case_id or ""))
    if match:
        return int(match.group(1))
    return 0


def _serialize_steps(steps):
    if isinstance(steps, str):
        try:
            return json.loads(steps)
        except Exception:
            return []
    return steps or []


def write_output_csv(base_dir: str, states):
    output_path = os.path.join(base_dir, "output.csv")
    with open(output_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["case_id", "deletion_status", "steps_json"])
        writer.writeheader()
        for state in sorted(states, key=lambda s: _case_sort_key(s.get("case_id", ""))):
            case_id = state.get("case_id", "")
            status = state.get("deletion_status", "PENDING")
            steps = _serialize_steps(state.get("steps_json", []))
            writer.writerow({
                "case_id": case_id,
                "deletion_status": status,
                "steps_json": json.dumps(steps, separators=(",", ":"))
            })


def main():
    started_at = time.perf_counter()
    base_dir = get_base_dir()
    csv_path = os.path.join(base_dir, "dataset", "deletion_requests.csv")
    output_path = os.path.join(base_dir, "output.csv")

    if os.path.exists(output_path):
        os.remove(output_path)

    print("--- Starting HackerRank Orchestrate Pipeline (Deterministic Engine) ---")

    df = pd.read_csv(csv_path)
    if "case_id" in df.columns:
        df = df.sort_values(by="case_id", key=lambda s: s.map(_case_sort_key)).reset_index(drop=True)

    total_rows = len(df)
    processed_states = []

    for index, row in df.iterrows():
        case_id = row["case_id"]
        requested_at = row["requested_at"]
        reported_status = row["reported_status"]
        request_text = row["request_text"]
        email = row["email"]

        print(f"Processing Row {index + 1}/{total_rows} | Case ID: {case_id}")

        initial_state = {
            "case_id": case_id,
            "requested_at": requested_at,
            "reported_status": reported_status,
            "audit_at": row.get("audit_at", ""),
            "request_text": request_text,
            "email": email,
            "steps_json": []
        }

        result_state = app.invoke(initial_state)
        processed_states.append(result_state)

    write_output_csv(base_dir, processed_states)
    elapsed_seconds = time.perf_counter() - started_at
    generate_usage_report(base_dir, total_rows, elapsed_seconds)

    print("\n--- Pipeline Execution & Report Generation Complete ---")


if __name__ == "__main__":
    main()