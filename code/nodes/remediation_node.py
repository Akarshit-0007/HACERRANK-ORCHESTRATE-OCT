from code.model.state import AuditState

def remediation_node(state: AuditState):
    """
    Generates deterministic remediation steps based on audit findings and active sync risks.
    """
    case_id = state.get("case_id", "")
    deletion_status = state.get("deletion_status", "INCOMPLETE")
    has_active_sync_risk = state.get("has_active_sync_risk", False)

    print(f"Remediation Node: Processing Case ID: {case_id} | Status: {deletion_status}")

    remediation_steps = []

    if deletion_status == "INCOMPLETE" or has_active_sync_risk:
        remediation_steps.append({
            "step_type": "REMEDIATION",
            "action": "Purge lingering user records from active replicas and terminate active cron sync jobs.",
            "status": "PENDING_EXECUTION"
        })
    else:
        remediation_steps.append({
            "step_type": "REMEDIATION",
            "action": "No active remediation required. Deletion verified as complete.",
            "status": "SKIPPED"
        })

    state["remediation_steps"] = remediation_steps
    return state