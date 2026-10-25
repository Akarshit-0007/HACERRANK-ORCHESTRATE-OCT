def resolve_user_identity(email: str, case_id: str):
    """
    Pure utility function to handle deterministic identity lookup and alias resolution.
    """
    user_id = f"USR-{case_id}" if case_id else "USR-UNKNOWN"
    resolved_emails = [email] if email else []


    return {
        "user_id": user_id,
        "resolved_emails": resolved_emails,
        "resolved_phone": None,
        "audit_entry": {
            "step": "identity_resolution",
            "status": "SUCCESS",
            "resolved_email_count": len(resolved_emails)
        }
    }