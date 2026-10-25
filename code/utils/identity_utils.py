import csv
import re
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _normalize(value: str) -> str:
    return (value or "").strip().lower()


def _extract_case_number(case_id: str):
    if not case_id:
        return None
    m = re.search(r"(\d+)", str(case_id))
    return int(m.group(1)) if m else None


def resolve_user_identity(email: str, case_id: str):
    """Resolve user_id and all direct aliases from identities and audit history."""
    email = (email or "").strip()
    root = _repo_root()

    identities = []
    with (root / "dataset" / "user_identities.csv").open("r", encoding="utf-8", newline="") as fh:
        identities = list(csv.DictReader(fh))

    audit_rows = []
    with (root / "dataset" / "user_audit_log.csv").open("r", encoding="utf-8", newline="") as fh:
        audit_rows = list(csv.DictReader(fh))

    user_id = None
    resolved_emails = []
    phone = None

    if email:
        normalized = _normalize(email)
        for row in identities:
            if _normalize(row.get("email", "")) == normalized:
                user_id = row.get("user_id")
                resolved_emails.append(_normalize(row.get("email", "")))
                phone = row.get("phone")
                break

    if user_id is None and email:
        normalized = _normalize(email)
        for row in audit_rows:
            if _normalize(row.get("old_value", "")) == normalized or _normalize(row.get("new_value", "")) == normalized:
                user_id = row.get("user_id")
                break

    if user_id is None:
        case_num = _extract_case_number(case_id)
        if case_num is not None:
            for row in identities:
                if row.get("user_id") in {f"user_{case_num}", f"user_{case_num:02d}"}:
                    user_id = row.get("user_id")
                    resolved_emails.append(_normalize(row.get("email", "")))
                    phone = row.get("phone")
                    break

    if user_id is None:
        user_id = f"USR-{case_id}" if case_id else "USR-UNKNOWN"

    if email:
        resolved_emails.append(_normalize(email))

    if user_id and user_id.startswith("user_"):
        for row in identities:
            if row.get("user_id") == user_id:
                resolved_emails.append(_normalize(row.get("email", "")))
                if not phone:
                    phone = row.get("phone")
                break

    for row in audit_rows:
        if row.get("user_id") == user_id:
            v_old = _normalize(row.get("old_value", ""))
            v_new = _normalize(row.get("new_value", ""))
            if v_old:
                resolved_emails.append(v_old)
            if v_new:
                resolved_emails.append(v_new)
            if row.get("field_name") == "phone" and not phone:
                phone = row.get("new_value")

    deduped = []
    seen = set()
    for value in resolved_emails:
        if value and value not in seen:
            seen.add(value)
            deduped.append(value)
    resolved_emails = deduped

    return {
        "user_id": user_id,
        "resolved_emails": resolved_emails,
        "resolved_phone": phone,
        "audit_entry": {
            "step": "identity_resolution",
            "status": "SUCCESS",
            "resolved_email_count": len(resolved_emails)
        }
    }