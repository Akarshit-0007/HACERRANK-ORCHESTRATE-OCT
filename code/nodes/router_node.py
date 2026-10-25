from code.model.state import AuditState
import time

def router_node(state: AuditState) -> AuditState:
    """
    Validates initial request parameters and sets validation flags.
    """
    case_id = state.get("case_id")

    # Check if the case_id is missing or the request text is completely empty
    if not case_id or not str(case_id).strip():
        print(f"Router Warning: Invalid or missing case_id ({case_id}). Marking as invalid.")
        state["is_invalid"] = True
    else:
        state["is_invalid"] = False

    return state