import csv
import json
import os
import re
from pathlib import Path


def get_base_dir() -> str:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = current_dir
    for _ in range(4):
        if os.path.exists(os.path.join(root_dir, "dataset")):
            return root_dir
        root_dir = os.path.dirname(root_dir)
    return os.getcwd()


def get_evidence_paths(base_dir: str = None) -> dict:
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
    if isinstance(steps_input, str):
        try:
            return json.loads(steps_input)
        except Exception:
            return []
    return list(steps_input) if steps_input else []


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _normalize(value: str) -> str:
    return (value or "").strip().lower()


def _extract_case_number(case_id: str):
    if not case_id:
        return None
    m = re.search(r"(\d+)", str(case_id))
    return int(m.group(1)) if m else None


def _build_aliases(email: str, case_id: str):
    aliases = set()
    email = (email or "").strip()
    if email:
        normalized = _normalize(email)
        aliases.add(normalized)
        aliases.add(email)

    root = _repo_root()
    identities_path = root / "dataset" / "user_identities.csv"
    if identities_path.exists():
        with identities_path.open("r", encoding="utf-8", newline="") as fh:
            for row in csv.DictReader(fh):
                if email and _normalize(row.get("email", "")) == _normalize(email):
                    aliases.add(row.get("user_id", ""))
                    aliases.add(_normalize(row.get("email", "")))
                    phone = (row.get("phone") or "").strip()
                    if phone:
                        aliases.add(phone)
                    name = (row.get("name") or "").strip().lower()
                    if name:
                        aliases.add(name)
    history_path = root / "dataset" / "user_audit_log.csv"
    if history_path.exists():
        with history_path.open("r", encoding="utf-8", newline="") as fh:
            for row in csv.DictReader(fh):
                user_id = (row.get("user_id") or "").strip()
                if email:
                    current_match = False
                    with identities_path.open("r", encoding="utf-8", newline="") as fh2:
                        for person in csv.DictReader(fh2):
                            if _normalize(person.get("email", "")) == _normalize(email) and person.get("user_id") == user_id:
                                current_match = True
                                break
                    if not current_match:
                        continue
                for value in [row.get("old_value", ""), row.get("new_value", "")]:
                    if value:
                        aliases.add(_normalize(value))
                        aliases.add(value.strip())
                        aliases.add((value or "").strip().lower())
    return [alias for alias in sorted(aliases, key=len) if alias and alias.strip()]


def _resolve_file_evidence_id(path: str):
    root = _repo_root()
    manifest_path = root / "dataset" / "evidence_files.csv"
    if not manifest_path.exists():
        return ""
    with manifest_path.open("r", encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            rel = row.get("file_path", "").replace("\\", "/")
            if rel.endswith(path.replace("\\", "/")) or os.path.basename(path) == os.path.basename(rel):
                return row.get("file_id", "")
    return ""


def _infer_system_id(resource_id: str):
    if not resource_id:
        return ""
    resource_id = str(resource_id)
    if resource_id.startswith("account_"):
        return "account_service"
    if resource_id.startswith("search_"):
        return "search_service"
    if resource_id.startswith("support_"):
        return "support_platform"
    if resource_id.startswith("analytics_"):
        return "analytics_platform"
    if resource_id.startswith("export_"):
        return "export_service"
    if resource_id.startswith("backup_"):
        return "backup_service"
    if resource_id.startswith("data_flow_"):
        return "integration_service"
    if resource_id.startswith("audit_record_"):
        return "security_service"
    return ""


def _classify_issue(resource_id: str):
    if not resource_id:
        return None
    if resource_id.startswith("account_") or resource_id.startswith("search_") or resource_id.startswith("export_"):
        return ("REPORT_REMAINING_RECORD", "PRESENT")
    if resource_id.startswith("support_"):
        return ("REPORT_EXPOSED_PII", "PRESENT")
    if resource_id.startswith("analytics_"):
        return ("REPORT_EXPOSED_PII", "PRESENT")
    if resource_id.startswith("data_flow_"):
        return ("REPORT_ACTIVE_DATA_FLOW", "ACTIVE")
    if resource_id.startswith("backup_"):
        return ("REPORT_RESTORE_RISK", "ACTIVE")
    return None


def _iter_relevant_files():
    root = _repo_root() / "dataset"
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        name = path.name
        if name in {"deletion_requests.csv", "sample_deletion_requests.csv", "sample_output.csv", "user_identities.csv", "user_audit_log.csv", "deletion_rules.csv", "evidence_files.csv", "output.csv", "system_activity.csv"}:
            continue
        if path.suffix.lower() in {".csv", ".tsv"}:
            continue
        yield path


def _track_activity_findings(case_id: str, email: str, aliases: list, audit_at=None):
    root = _repo_root()
    activity_path = root / "dataset" / "system_activity.csv"
    matching = []
    if not activity_path.exists():
        return matching
    with activity_path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            if audit_at and row.get("event_time") and row["event_time"] > audit_at:
                continue
            details = row.get("details", "")
            joined = " ".join([details, row.get("resource_id", ""), row.get("source_system", ""), row.get("target_system", "")])
            if not any(alias and alias.lower() in joined.lower() for alias in aliases):
                continue
            resource_id = row.get("resource_id", "")
            system_id = _infer_system_id(resource_id)
            issue = _classify_issue(resource_id)
            if issue and system_id:
                matching.append({
                    "system_id": system_id,
                    "resource_id": resource_id,
                    "operation": issue[0],
                    "state": issue[1],
                    "evidence_id": row.get("activity_id", "")
                })
    return matching


def _track_file_findings(case_id: str, email: str, aliases: list, audit_at=None):
    issues = []
    seen = set()
    for path in _iter_relevant_files():
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        hay = content.lower()
        alias_matches = [alias for alias in aliases if alias and alias.lower() in hay]
        if not alias_matches:
            continue
        resource_ids = re.findall(r"\b(?:account|search|support|analytics|export|backup|data_flow|audit_record)_[A-Za-z0-9_]+\b", content)
        evidence_id = _resolve_file_evidence_id(str(path.relative_to(_repo_root() / "dataset")))
        if not evidence_id:
            evidence_id = _resolve_file_evidence_id(path.name)
        for resource_id in sorted(set(resource_ids)):
            issue = _classify_issue(resource_id)
            if not issue:
                continue
            system_id = _infer_system_id(resource_id)
            if not system_id:
                continue
            key = (system_id, resource_id, issue[0], issue[1], evidence_id)
            if key in seen:
                continue
            seen.add(key)
            issues.append({
                "system_id": system_id,
                "resource_id": resource_id,
                "operation": issue[0],
                "state": issue[1],
                "evidence_id": evidence_id or ""
            })
    return issues


def _request_authorizes_deletion(request_text: str) -> bool:
    if not request_text:
        return False
    text = request_text.lower()
    if re.search(r"\b(?:do not|don't|never|not)\s+(?:delete|deletion|remove|erase|purge)\b", text):
        return False
    if any(token in text for token in ["delete", "deletion", "remove", "erase", "close account", "close my account", "destroy", "purge", "delete my account", "erase my account", "remove my profile"]):
        non_delete_tokens = ["access", "download", "export my data", "export data", "update", "correct", "marketing opt", "opt out", "support request", "billing", "invoice"]
        if any(token in text for token in non_delete_tokens):
            return False
        return True
    return False


def _sort_findings(findings):
    order = {
        "REPORT_REMAINING_RECORD": 0,
        "REPORT_EXPOSED_PII": 1,
        "REPORT_ACTIVE_DATA_FLOW": 2,
        "REPORT_RESTORE_RISK": 3,
    }
    return sorted(findings, key=lambda d: (order.get(d.get("operation", ""), 99), d.get("system_id", ""), d.get("resource_id", "")))


def _dedupe_findings(findings):
    seen = set()
    deduped = []
    for finding in findings:
        key = (finding.get("system_id"), finding.get("resource_id"), finding.get("operation"), finding.get("state"), finding.get("evidence_id"))
        if key in seen:
            continue
        seen.add(key)
        deduped.append(finding)
    return deduped


def scan_evidence_for_case(case_id: str, email: str, evidence_root: str = None, audit_at: str = None, request_text: str = None):
    """Return (status, findings) for a request, using only dataset evidence and audit time cutoff."""
    if request_text is not None and not _request_authorizes_deletion(request_text):
        return "NOT_APPLICABLE", []
    if request_text is None and email:
        # Fallback for compatibility with older call sites.
        if not _request_authorizes_deletion(email):
            return "NOT_APPLICABLE", []

    aliases = _build_aliases(email, case_id)
    matches = []
    matches.extend(_track_activity_findings(case_id, email, aliases, audit_at))
    matches.extend(_track_file_findings(case_id, email, aliases, audit_at))
    matches = _dedupe_findings(matches)
    findings = _sort_findings(matches)
    if findings:
        return "INCOMPLETE", findings
    return "COMPLETE", findings


def scan_evidence_directories(case_id: str, evidence_paths: dict = None) -> list:
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
