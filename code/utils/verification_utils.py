

def generate_verification_actions(case_id: str, deletion_status: str, audit_findings: list):
    """
    generates structure verification steps basend on deletion status findings.
    :param case_id:
    :param deletion_status:
    :param audit_findings:
    :return:
    """

    verification_actions = []

    if deletion_status == 'COMPLETE' and audit_findings:

        evidence_id = audit_findings[0].get('evidence_id', '')
        verification_actions.append(
            {
            "action": f"Verify complete removal and sanitization of records for case {case_id}",
            "evidence_id": evidence_id
            }
        )
    else:

        verification_actions.append(
            {
            "action": f"Confirm zero-state compliance and verify no residual artifacts exist for case {case_id}",
            "evidence_id": ""
            }
        )

    return verification_actions