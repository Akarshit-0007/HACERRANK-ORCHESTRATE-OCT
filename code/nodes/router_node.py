from code.model.state import AuditState
import time

def router_node(state: AuditState):
    case_id = state.get('case_id')
    email = state.get('email')

    print(f"Router received - Case ID: {case_id}, Email: {email}")

    time.sleep(4)

    return state