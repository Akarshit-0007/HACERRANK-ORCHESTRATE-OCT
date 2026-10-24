import csv
from code.graph import app


def main():
    csv_path = r"D:\hackerrank-orchestrate-october26\dataset\deletion_requests.csv"

    print("--- Starting HackerRank Orchestrate Pipeline ---")

    with open(csv_path, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for index, row in enumerate(reader):
            case_id = row["case_id"]
            requested_at = row["requested_at"]
            reported_status = row["reported_status"]
            request_text = row["request_text"]
            email = row["email"]



            print(f"\nProcessing Row {index + 1} | Case ID: {case_id}")

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

            # Print or capture results to write to your output.csv later
            # print(f"Status: {final_state.get('deletion_status', 'UNKNOWN')}")


if __name__ == "__main__":
    main()