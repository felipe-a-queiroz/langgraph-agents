from typing_extensions import TypedDict, Annotated, List

# Definindo o estado do agente com TypedDict
class AgentState(TypedDict):
    task: str
    plan: str
    draft: str
    critique: str
    content: List[str]
    revision_number: int
    max_revisions: int