from langgraph.graph import StateGraph, START,END
from code.model.state import AuditState
from code.nodes.audit_node import audit_node
from code.nodes.identity_node import identity_node
from code.nodes.remediation_node import remediation_node
from code.nodes.router_node import router_node
from code.nodes.verification_node import verification_node
from code.nodes.output_node import output_node


def is_applicable(state: AuditState):
    if state.get("is_invalid", False):
        return END

    return "identity_node"

builder = StateGraph(AuditState)

builder.add_node("router_node", router_node)
builder.add_node("identity_node", identity_node)
builder.add_node("audit_node", audit_node)
builder.add_node("remediation_node", remediation_node)
builder.add_node("verification_node", verification_node)
builder.add_node("output_node", output_node)


builder.add_edge(START,'router_node')
builder.add_conditional_edges(
    "router_node",
    is_applicable,
    {
        "identity_node": "identity_node",  # Continues the normal flow
        END: END                     # Stops processing and exits directly to END
    }
)
builder.add_edge('router_node', 'identity_node')
builder.add_edge('identity_node', 'audit_node')
builder.add_edge('audit_node', 'remediation_node')
builder.add_edge('remediation_node', 'verification_node')
builder.add_edge('verification_node', 'output_node')
builder.add_edge('output_node', END)

app = builder.compile()

with open("graph_visualization.png", "wb") as f:
    f.write(app.get_graph().draw_mermaid_png())