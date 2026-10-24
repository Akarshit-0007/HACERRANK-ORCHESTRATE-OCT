from typing import TypedDict, List, Dict, Any, Optional

class AuditState(TypedDict):
    # 1. Inputs from deletion_requests.csv
    case_id: str
    email: str
    requested_at: str
    reported_status: str
    request_text: str

    # 2. Identity Resolution Output (populated by identity_node)
    user_id: Optional[str]
    resolved_emails: List[str]          # Current email + all historical email aliases
    resolved_phone: Optional[str]
    identity_audit_trail: List[Dict[str, Any]]

    # 3. Evidence & Audit Findings (populated by audit_node)
    deletion_status: str                # COMPLETE, INCOMPLETE, or NOT_APPLICABLE
    audit_findings: List[Dict[str, Any]] # Raw findings from SQLite .sql snapshots & system_activity.csv
    has_active_sync_risk: bool          # Flag for active ETL jobs/cron restores

    # 4. Action Steps (populated by remediation_node & verification_node)
    remediation_steps: List[Dict[str, Any]]
    verification_steps: List[Dict[str, Any]]

    # 5. Final Output Field
    steps_json: List[Dict[str, Any]]    # Ordered JSON array (FINDING -> REMEDIATION -> VERIFICATION)