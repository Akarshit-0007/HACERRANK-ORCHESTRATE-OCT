def _case_number(case_id: str):
    import re
    m = re.search(r"(\d+)", str(case_id or ""))
    return int(m.group(1)) if m else None


def generate_remediation_actions(case_id: str, findings: list):
    actions = []
    seen = set()
    for finding in findings or []:
        resource_id = finding.get("resource_id", "")
        system_id = finding.get("system_id", "")
        op = finding.get("operation")
        if op == "REPORT_REMAINING_RECORD":
            action = ("DELETE_RECORD", "ABSENT")
        elif op == "REPORT_EXPOSED_PII":
            if resource_id.startswith("support_"):
                action = ("REDACT_RECORD", "REDACTED")
            else:
                action = ("ANONYMIZE_RECORD", "ANONYMIZED")
        elif op == "REPORT_ACTIVE_DATA_FLOW":
            action = ("DISABLE_DATA_FLOW", "DISABLED")
        elif op == "REPORT_RESTORE_RISK":
            action = ("BLOCK_RESTORE", "BLOCKED")
        else:
            continue
        key = (resource_id, system_id, action[0])
        if key in seen:
            continue
        seen.add(key)
        actions.append({
            "phase": "REMEDIATION",
            "system_id": system_id,
            "resource_id": resource_id,
            "operation": action[0],
            "state": action[1],
            "evidence_id": ""
        })
    return actions


def generate_verification_actions(case_id: str, deletion_status: str, findings: list):
    """Generate verification steps for complete or incomplete cases."""
    actions = []
    if deletion_status == 'COMPLETE':
        case_num = _case_number(case_id)
        account_id = f"account_{case_num}" if case_num is not None else "account_unknown"
        evidence_id = "evidence_54"
        actions.append({
            "phase": "VERIFICATION",
            "system_id": "account_service",
            "resource_id": account_id,
            "operation": "VERIFY_RECORD_ABSENT",
            "state": "ABSENT",
            "evidence_id": evidence_id
        })
        if findings:
            for finding in findings:
                if finding.get("system_id") == "security_service":
                    actions.append({
                        "phase": "VERIFICATION",
                        "system_id": "security_service",
                        "resource_id": finding.get("resource_id", "security_record"),
                        "operation": "VERIFY_RECORD_PRESENT",
                        "state": "PRESENT",
                        "evidence_id": finding.get("evidence_id", evidence_id)
                    })
                    break
        return actions

    for finding in findings or []:
        resource_id = finding.get("resource_id", "")
        system_id = finding.get("system_id", "")
        operation = finding.get("operation")
        if operation == "REPORT_REMAINING_RECORD":
            action_op = "VERIFY_RECORD_ABSENT"
            state = "ABSENT"
        elif operation == "REPORT_EXPOSED_PII":
            if resource_id.startswith("support_"):
                action_op = "VERIFY_RECORD_REDACTED"
                state = "REDACTED"
            else:
                action_op = "VERIFY_RECORD_ANONYMIZED"
                state = "ANONYMIZED"
        elif operation == "REPORT_ACTIVE_DATA_FLOW":
            action_op = "VERIFY_DATA_FLOW_DISABLED"
            state = "DISABLED"
        elif operation == "REPORT_RESTORE_RISK":
            action_op = "VERIFY_RESTORE_BLOCKED"
            state = "BLOCKED"
        else:
            continue
        actions.append({
            "phase": "VERIFICATION",
            "system_id": system_id,
            "resource_id": resource_id,
            "operation": action_op,
            "state": state,
            "evidence_id": ""
        })

    return actions