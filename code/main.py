import csv
import os
import pandas as pd
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

def main():
    base_dir = get_base_dir()
    csv_path = os.path.join(base_dir, "dataset", "deletion_requests.csv")
    output_path = os.path.join(base_dir, "output.csv")  # Must be at root level per challenge evaluation rules

    if os.path.exists(output_path):
        os.remove(output_path)

    print("--- Starting HackerRank Orchestrate Pipeline (Deterministic Engine) ---")

    df = pd.read_csv(csv_path)
    if "case_id" in df.columns:
        df = df.sort_values(by="case_id").reset_index(drop=True)

    total_rows = len(df)

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
            "request_text": request_text,
            "email": email,
            "steps_json": []
        }

        # Invoke the LangGraph workflow (output_node handles writing to output.csv)
        app.invoke(initial_state)

    # Generate the usage report reflecting a deterministic architecture
    generate_usage_report(base_dir, total_rows)

    print("\n--- Pipeline Execution & Report Generation Complete ---")

if __name__ == "__main__":
    main()