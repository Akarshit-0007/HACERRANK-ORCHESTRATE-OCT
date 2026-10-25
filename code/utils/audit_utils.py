import os
import json

def get_evidence_paths(base_dir="dataset/evidence"):
    """Returns exact mapping of evidence subdirectories."""
    return {
        "databases": os.path.join(base_dir, "databases"),
        "documents": os.path.join(base_dir, "documents"),
        "images": os.path.join(base_dir, "images"),
        "logs": os.path.join(base_dir, "logs"),
        "records": os.path.join(base_dir, "records")
    }

def parse_steps_json(steps_input) -> list:
    """Safely parses steps  from string or list format."""
    if isinstance(steps_input, str):
        try:
            return json.loads(steps_input)
        except Exception:
            return []
    return list(steps_input) if steps_input else []

def scan_evidence_directories(case_id: str, evidence_paths: dict) -> list:
    """Scans evidence directories for files containing the case ID."""
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