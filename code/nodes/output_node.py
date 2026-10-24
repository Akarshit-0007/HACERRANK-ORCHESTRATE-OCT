import csv
import os

from code.model.state import AuditState


def output_node(state: AuditState):
    """
    Appends final results matching the exact required schema: case_id, deletion_status, steps_json.
    :param state:
    :return:
    """

    output_path =r"dataset\output.csv"

    row_data = {
        "case_id": state["case_id"],
        "deletion_status": state["deletion_status", "PENDING"],
        "steps_json": state["steps_json", "[]"]
    }

    file_exists = os.path.isfile(output_path)

    try:
        with open(output_path, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=row_data.keys())

            if not file_exists:
                writer.writeheader()

            writer.writerow(row_data)

    except Exception as e:
        print(f"Error failed to write the output CSV: {e}")

    return state
