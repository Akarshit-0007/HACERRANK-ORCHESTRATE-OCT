from code.model.state import AuditState


def identity_node(state: AuditState):
    """
        Identity node wrapper that delegates to utility functions.
        """
    email = state.get("email", "")
    case_id = state.get("case_id", "")

    print(f"Identity Node: Processing Case ID: {case_id} | Email: {email}")

    # Call the clean utility function
    result = resolve_user_identity(email, case_id)

    # Populate state
    state["user_id"] = result["user_id"]
    state["resolved_emails"] = result["resolved_emails"]
    state["resolved_phone"] = result["resolved_phone"]

    audit_trail = state.get("identity_audit_trail", [])
    audit_trail.append(result["audit_entry"])
    state["identity_audit_trail"] = audit_trail

    return state
