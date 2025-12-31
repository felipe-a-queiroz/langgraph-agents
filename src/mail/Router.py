from pydantic import BaseModel, Field
from typing_extensions import TypedDict, Literal, Annotated

class Router(BaseModel):
    """Analisa o e-mail não lido e o roteia de acordo com seu conteúdo."""
    
    reasoning: str = Field(
        description="Raciocínio passo a passo por trás da classificação."
    )
    classification: Literal["ignore", "respond", "notify"] = Field(
        description="A classificação de um e-mail: `ignore` para e-mails irrelevantes, `notify` para informações importantes que não precisam de resposta, `respond` para e-mails que precisam de uma resposta",
    )