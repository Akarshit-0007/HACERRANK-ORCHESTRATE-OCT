from code.model.state import AuditState
from code.utils.verification_utils import generate_remediation_actions


def remediation_node(state: AuditState):
    case_id = state.get("case_id", "")
    findings = state.get("audit_findings", [])
    deletion_status = state.get("deletion_status", "COMPLETE")
    print(f"Remediation Node: Processing Case ID: {case_id} | Status: {deletion_status}")
    state["remediation_steps"] = generate_remediation_actions(case_id, findings) if deletion_status == "INCOMPLETE" else []
    return state