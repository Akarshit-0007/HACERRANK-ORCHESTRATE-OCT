from code.model.state import AuditState


def output_node(state: AuditState):
    """Return state without mutating the CSV on each per-case graph run.

    The final root-level output.csv is written once from main.py after all cases
    are processed to avoid duplicate rows and to preserve a clean evaluation file.
    """
    return state