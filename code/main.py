import csv
from code.graph import app


def main():
    csv_path = r"dataset\deletion_requests.csv"
    output_path = r"dataset\output.csv"

    if os.path.exists(output_path):
        os.remove(output_path)

    print("--- Starting HackerRank Orchestrate Pipeline ---")

    df = pd.read_csv(csv_path)
    if "case_id" in df.columns:
        df = df.sort_values(by="case_id").reset_index(drop=True)

    total_rows = len(df)
    total_input_tokens = 0
    total_output_tokens = 0

    for index, row in df.iterrows():
        case_id = row["case_id"]
        requested_at = row["requested_at"]
        reported_status = row["reported_status"]
        request_text = row["request_text"]
        email = row["email"]

        (f"\nProcessing Row {index + 1} | Case ID: {case_id}")

        # Form the initial state payload for this request
        initial_state = {
            "case_id": case_id,
            "requested_at" : requested_at,
            "reported_status": reported_status,
            "request_text": request_text,
            "email": email,
        }

        # Invoke the LangGraph app
        final_state = app.invoke(initial_state)

        # Accumulate token metrics returned or estimated from execution
        total_input_tokens += final_state.get("input_tokens", 150)
        total_output_tokens += final_state.get("output_tokens", 50)

        time.sleep(4)

    project_root = os.path.join(os.path.dirname(csv_path), "..")
    generate_usage_report(project_root, total_rows, total_input_tokens, total_output_tokens)

    print("\n--- Pipeline Execution & Report Generation Complete ---")


if __name__ == "__main__":
    main()