def generate_remediation_actions(case_id: str, audit_findings: list):
    """
    Generate Structures remdiation steps based on audit findings.
    :param case_id:
    :param audit_findings:
    :return:
    """

    remediation_actions = []

    if audit_findings:
        for finding in audit_findings:
            env_type = finding['type']
            remediation_actions.append({
                'action' : f"Purge remaining data for case {case_id} from {env_type} storage",
            })

    else:

        remediation_actions.append({
            "action": f"Verify compliance state and ensure no orphaned records exist for case {case_id}"
        })

    return remediation_actions