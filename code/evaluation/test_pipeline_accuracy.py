import os
import pandas as pd
from code.utils.audit_utils import scan_evidence_for_case


def test_audit_accuracy():
    print("--- Running Deterministic Audit Accuracy Test ---")

    # Explicitly check common paths where deletion_requests.csv might be located
    possible_paths = [
        "dataset/deletion_requests.csv",
        "D:/hackerrank-orchestrate-october26/dataset/deletion_requests.csv",
        "./dataset/deletion_requests.csv"
    ]

    csv_path = None
    for path in possible_paths:
        if os.path.exists(path):
            csv_path = path
            break

    if not csv_path:
        print("Error: deletion_requests.csv not found in specified paths. Please verify dataset location.")
        return

    df = pd.read_csv(csv_path)
    print(f"Loaded dataset from {csv_path} with {len(df)} total records.")

    # Sample a few test cases
    sample_df = df.head(5)

    complete_count = 0
    incomplete_count = 0

    for idx, row in sample_df.iterrows():
        case_id = row.get("case_id", f"case_{idx}")
        email = row.get("email", "")

        status, findings = scan_evidence_for_case(case_id, email)
        print(f"Case ID: {case_id} | Email: {email} => Status: {status}")
        print(f"   -> Findings: {findings}")

        if status == "COMPLETE":
            complete_count += 1
        else:
            incomplete_count += 1

    print("\n--- Test Summary ---")
    print(f"Sampled Complete Count: {complete_count}")
    print(f"Sampled Incomplete Count: {incomplete_count}")


if __name__ == "__main__":
    test_audit_accuracy()