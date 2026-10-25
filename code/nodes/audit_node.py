from code.model.state import AuditState
from code.utils.audit_utils import scan_evidence_for_case
from code.utils.verification_utils import generate_remediation_actions


def _normalize_evidence_step(step):
    if not isinstance(step, dict):
        return step
    normalized = {"step_no": step.get("step_no"), "phase": step.get("phase"), "system_id": step.get("system_id"), "resource_id": step.get("resource_id"), "operation": step.get("operation"), "state": step.get("state"), "evidence_id": step.get("evidence_id", "")}
    normalized = {k: v for k, v in normalized.items() if v is not None}
    return normalized


def audit_node(state: AuditState) -> AuditState:
    case_id = state.get("case_id", "")
    email = state.get("email", "")
    request_text = state.get("request_text", "")
    audit_at = state.get("audit_at")

    print(f"Audit Node: Scanning evidence for Case ID: {case_id}")
    deletion_status, findings = scan_evidence_for_case(case_id, email, audit_at=audit_at, request_text=request_text)

    state["deletion_status"] = deletion_status
    state["audit_findings"] = findings

    steps = []
    for idx, finding in enumerate(findings, start=1):
        step = {
            "step_no": idx,
            "phase": "FINDING",
            "system_id": finding.get("system_id", ""),
            "resource_id": finding.get("resource_id", ""),
            "operation": finding.get("operation", ""),
            "state": finding.get("state", ""),
            "evidence_id": finding.get("evidence_id", "")
        }
        steps.append(step)

    if deletion_status == "INCOMPLETE":
        remediation = generate_remediation_actions(case_id, findings)
        for r_idx, remediation_step in enumerate(remediation, start=len(steps) + 1):
            steps.append({"step_no": r_idx, "phase": "REMEDIATION", "system_id": remediation_step.get("system_id"), "resource_id": remediation_step.get("resource_id"), "operation": remediation_step.get("operation"), "state": remediation_step.get("state"), "evidence_id": remediation_step.get("evidence_id", "")})
    state["steps_json"] = [_normalize_evidence_step(step) for step in steps]
    return state