from code.model.state import AuditState
from code.utils.audit_utils import parse_steps_json
from code.utils.verification_utils import generate_verification_actions


def verification_node(state: AuditState):
    """
    LangGraph node for generating final verification steps and completing the sequence.
    """
    case_id = state["case_id"]
    deletion_status = state["deletion_status"]
    audit_findings = state.get("audit_findings", [])

    # Parse existing steps using utility
    steps = parse_steps_json(state.get("steps_json", []))
    step_num = len(steps) + 1

    # Generate verification actions via utility
    actions = generate_verification_actions(case_id, deletion_status, audit_findings)

    verification_steps = []
    for action_item in actions:
        step_item = {
            "step_number": step_num,
            "action": action_item["action"],
            "evidence_id": action_item["evidence_id"]
        }
        steps.append(step_item)
        verification_steps.append(step_item)
        step_num += 1

    # Update state fields
    state["verification_steps"] = verification_steps
    state["steps_json"] = steps

    return state