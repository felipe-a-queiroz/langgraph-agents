import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
from typing_extensions import TypedDict, Literal, Annotated
from langchain.chat_models import init_chat_model
from Router import Router
from prompts import triage_system_prompt, triage_user_prompt, agent_system_prompt
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.tools import tool
from langchain.agents import create_agent

# Configurando o ambiente e definindo variáveis
load_dotenv()

# Configurando o modelo de linguagem
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite")

# Configurando o roteador
llm_router = llm.with_structured_output(Router)

profile = {
    "name": "Sarah",
    "full_name":"Sarah Chen",
    "user_profile_background": "Engenheira de software sênior liderando uma equipe de 5 desenvolvedores",
}

# Criando instruções de prompt e simulando e-mails
prompt_instructions = {
    "triage_rules": {
        "ignore": "Newsletters de marketing, e-mails de spam, comunicados gerais da empresa",
        "notify": "Membro da equipe doente, notificações do sistema de build, atualizações de status de projeto",
        "respond": "Perguntas diretas de membros da equipe, solicitações de reunião, relatórios de bugs críticos",
    },
    "agent_instructions": "Use estas ferramentas quando apropriado para ajudar a gerenciar as tarefas de Sarah de forma eficiente."
}

email = {
    "from": "Alice Smith <alice.smith@company.com>",
    "to": "Sarah Chen <sarah.chen@company.com>",
    "subject": "Dúvida rápida sobre a documentação da API",
    "body": """
Olá Sarah,

Eu estava revisando a documentação da API para o novo serviço de autenticação e notei que alguns endpoints parecem estar faltando nas especificações. Você poderia me ajudar a esclarecer se isso foi intencional ou se devemos atualizar a documentação?

Especificamente, estou procurando por:
- /auth/refresh
- /auth/validate

Obrigada!
Alice
""",
}

# Montando o prompt do sistema e do usuário
system_prompt = triage_system_prompt.format(
    full_name=profile["full_name"],
    name=profile["name"],
    examples=None,
    user_profile_background=profile["user_profile_background"],
    triage_no=prompt_instructions["triage_rules"]["ignore"],
    triage_notify=prompt_instructions["triage_rules"]["notify"],
    triage_email=prompt_instructions["triage_rules"]["respond"],
)

user_prompt = triage_user_prompt.format(
    author=email["from"],
    to=email["to"],
    subject=email["subject"],
    email_thread=email["body"],
)

# Executando o agente e analisando os resultados
result = llm_router.invoke(
    [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt),
    ]
)

@tool
def write_email(to: str, subject: str, content: str) -> str:
    """Escreve e envia um e-mail."""
    # Resposta de placeholder - em um aplicativo real, enviaria o e-mail
    return f"E-mail enviado para {to} com o assunto '{subject}'"

@tool
def schedule_meeting(
    attendees: list[str],
    subject: str,
    duration_minutes: int,
    preferred_day: str
) -> str:
    """Agenda uma reunião no calendário."""
    
    return f"Reunião '{subject}' agendada para {preferred_day} com {len(attendees)} participantes"

@tool
def check_calendar_availability(day: str) -> str:
    """Verifica a disponibilidade do calendário para um determinado dia."""
    
    return f"Horários disponíveis em {day}: 9:00 AM, 2:00 PM, 4:00 PM"

def create_prompt(state):
    return [
        {
            "role": "system",
            "content": agent_system_prompt.format(
                instructions=prompt_instructions["agent_instructions"],
                **profile
            ),
        }
        + state["messages"]
    ]

# Definindo as ferramentas disponíveis para o agente
tools = [write_email, schedule_meeting, check_calendar_availability]

# Construindo e acionando o agente
agent = create_agent(
    model=llm,
    tools=tools,
)

response = agent.invoke(
    {
        "messages": [{
            "role": "user",
            "content": "qual é minha disponibilidade para 01/01/2026?"
        }]
    }
)

response["messages"][-1].pretty_print()