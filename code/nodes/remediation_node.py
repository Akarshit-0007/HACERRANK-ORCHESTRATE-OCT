from code.model.state import AuditState


def remediation_node(state: AuditState):
    """
    This Is generting remediation steps based on audit findings.
    :param state:
    :return:
    """

    case_id = state['case_id']
    audit_findings = state.get('audit_findings', [])

    steps = parse_steps_json(state.get("steps_json", []))
    step_num = len(steps) + 1

    actions = generate_remediation_actions(case_id, audit_findings)

    remediation_steps = []
    for action_item in actions:
        step_item = {
            "step_number": step_num,
            "action": action_item["action"],
            "evidence_id": ""
        }
        steps.append(step_item)
        remediation_steps.append(step_item)
        step_num += 1

    state["remediation_steps"] = remediation_steps
    state["steps_json"] = steps

    return state