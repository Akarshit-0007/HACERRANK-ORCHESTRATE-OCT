from code.model.state import AuditState
from code.utils.audit_utils import scan_evidence_for_case

def audit_node(state: AuditState) -> AuditState:
    """
    Audit node wrapper that delegates evidence scanning to utility functions.
    """
    case_id = state.get("case_id", "")
    email = state.get("email", "")

    print(f"Audit Node: Scanning evidence for Case ID: {case_id}")

    # Call the utility function
    deletion_status, findings = scan_evidence_for_case(case_id, email)

    state["deletion_status"] = deletion_status
    state["steps_json"] = [
        {
            "step_number": 1,
            "action": f"Audited evidence directories for case {case_id}",
            "findings": findings
        },
        {
            "step_number": 2,
            "action": "Confirm zero-state compliance and verify no residual artifacts exist",
            "status": deletion_status
        }
    ]

    return state