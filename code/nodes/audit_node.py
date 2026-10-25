from code.model.state import AuditState
from code.utils.audit_utils import (
    get_evidence_paths,
    parse_steps_json,
    scan_evidence_directories
)


def audit_node(state: AuditState):
    """
    LangGraph node for auditing evidence directories based on case ID.
    """
    case_id = state.get("case_id")

    # Get paths and parse steps using utility functions
    evidence_paths = get_evidence_paths()
    steps = parse_steps_json(state.get("steps_json", []))

    step_num = len(steps) + 1

    # Scan evidence using utility
    audit_findings = scan_evidence_directories(case_id, evidence_paths)

    # Append structured audit step
    steps.append({
        "step_number": step_num,
        "action": f"Audited evidence directories for case {case_id}",
        "evidence_id": audit_findings[0]["evidence_id"] if audit_findings else ""
    })

    # Update state fields
    state["audit_findings"] = audit_findings
    state["steps_json"] = steps
    state["deletion_status"] = "COMPLETE" if audit_findings else "INCOMPLETE"
    state["has_active_sync_risk"] = False

    return state