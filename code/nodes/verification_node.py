from code.model.state import AuditState
from code.utils.audit_utils import parse_steps_json
from code.utils.verification_utils import generate_verification_actions


def verification_node(state: AuditState):
    case_id = state["case_id"]
    deletion_status = state["deletion_status"]
    audit_findings = state.get("audit_findings", [])
    steps = parse_steps_json(state.get("steps_json", []))
    step_num = len(steps) + 1

    actions = generate_verification_actions(case_id, deletion_status, audit_findings)
    verification_steps = []
    for action in actions:
        step_item = {
            "step_no": step_num,
            "phase": action.get("phase", "VERIFICATION"),
            "system_id": action.get("system_id", ""),
            "resource_id": action.get("resource_id", ""),
            "operation": action.get("operation", ""),
            "state": action.get("state", ""),
            "evidence_id": action.get("evidence_id", "")
        }
        steps.append(step_item)
        verification_steps.append(step_item)
        step_num += 1

    state["verification_steps"] = verification_steps
    state["steps_json"] = steps
    return state