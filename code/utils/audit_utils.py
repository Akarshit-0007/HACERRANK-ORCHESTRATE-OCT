import os
import glob
import json


def get_base_dir() -> str:
    """Resolves the absolute path to the workspace root directory."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = current_dir
    for _ in range(4):
        if os.path.exists(os.path.join(root_dir, "dataset")):
            return root_dir
        root_dir = os.path.dirname(root_dir)
    return os.getcwd()


def get_evidence_paths(base_dir: str = None) -> dict:
    """Returns exact mapping of evidence subdirectories with robust path resolution."""
    if not base_dir:
        base_dir = os.path.join(get_base_dir(), "dataset", "evidence")
    else:
        base_dir = os.path.join(base_dir, "evidence")

    return {
        "databases": os.path.join(base_dir, "databases"),
        "documents": os.path.join(base_dir, "documents"),
        "images": os.path.join(base_dir, "images"),
        "logs": os.path.join(base_dir, "logs"),
        "records": os.path.join(base_dir, "records")
    }


def parse_steps_json(steps_input) -> list:
    """Safely parses steps from string or list format."""
    if isinstance(steps_input, str):
        try:
            return json.loads(steps_input)
        except Exception:
            return []
    return list(steps_input) if steps_input else []


def scan_evidence_directories(case_id: str, evidence_paths: dict = None) -> list:
    """Scans evidence directories for files matching case ID."""
    if not evidence_paths:
        evidence_paths = get_evidence_paths()

    audit_findings = []
    for ev_type, path in evidence_paths.items():
        if os.path.exists(path):
            matching_files = [f for f in os.listdir(path) if case_id in f]
            if matching_files:
                audit_findings.append({
                    "evidence_id": f"ev_{ev_type}_{case_id}",
                    "type": ev_type,
                    "filename": matching_files[0],
                    "path": os.path.join(path, matching_files[0])
                })
    return audit_findings


def scan_evidence_for_case(case_id: str, email: str, evidence_root: str = None) -> tuple[str, str]:
    """
    Scans local evidence files (SQL replicas, logs, txt, json) deterministically
    for residual user data matching case_id or email.
    """
    if not evidence_root:
        evidence_root = os.path.join(get_base_dir(), "dataset")

    if not email:
        return "COMPLETE", f"No email associated with {case_id} to audit."

    is_found_in_replicas = False
    found_file = ""

    # Search all SQL logs, data dumps, and log files in the dataset directory
    search_extensions = ["*.sql", "*.log", "*.txt", "*.json"]
    replica_files = []
    for ext in search_extensions:
        replica_files.extend(glob.glob(os.path.join(evidence_root, "**", ext), recursive=True))

    email_lower = email.strip().lower()

    for file_path in replica_files:
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read().lower()

                # Check if user email exists anywhere in active replica/logs
                if email_lower in content:
                    # Exclude pure deletion confirmation audit entries if needed
                    is_found_in_replicas = True
                    found_file = os.path.basename(file_path)
                    break
        except Exception:
            continue

    if is_found_in_replicas:
        return "INCOMPLETE", f"Residual records found for {case_id} ({email}) in evidence file: {found_file}."
    else:
        return "COMPLETE", f"Zero residual records found for {case_id}. Deletion verified."