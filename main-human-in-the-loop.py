import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, List, Any, Dict
import operator
from typing_extensions import TypedDict
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, ToolMessage, AIMessage, BaseMessage
from langchain_community.tools.tavily_search import TavilySearchResults
import sqlite3
from tavily import TavilyClient
from langgraph.checkpoint.sqlite import SqliteSaver
conn = sqlite3.connect("checkpoints.db", check_same_thread=False)
memory = SqliteSaver(conn)
from dataclasses import dataclass, field

from datetime import date
current_date = date.today().strftime("%d/%m/%Y")

from dotenv import load_dotenv

load_dotenv()

os.environ['TAVILY_API_KEY'] = os.getenv('TAVILY_API_KEY')

from uuid import uuid4

def reduce_messages(left: list[AnyMessage], right: list[AnyMessage]) -> list[AnyMessage]:

    for message in right:
        if not message.id:
            message.id = str(uuid4())

    merged = left.copy()
    for message in right:
        for i, existing in enumerate(merged):
            
            if existing.id == message.id:
                merged[i] = message
                break
        else:
            merged.append(message)
    return merged


class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], reduce_messages]

class Agent:
    def __init__(self, model, tools, checkpointer, system=""):
        self.system = system
        
        graph = StateGraph(AgentState)
        
        graph.add_node("llm", self.call_gemini)
        
        graph.add_node("action", self.take_action)
        
        graph.add_conditional_edges("llm", self.exists_action, {True: "action", False: END})
        
        graph.add_edge("action", "llm")
        
        graph.set_entry_point("llm")
        
        self.graph = graph.compile(
            checkpointer=checkpointer,
            interrupt_before=["action"]
            )
        self.tools = {t.name: t for t in tools}
        self.model = model.bind_tools(tools)
        
    def call_gemini(self, state: AgentState):
        messages = state['messages']
        if self.system:
            messages = [SystemMessage(content=self.system)] + messages
            
        print("Mensagens enviadas ao modelo:", messages)
        message = self.model.invoke(messages)
        return {'messages': [message]}
    
    def exists_action(self, state: AgentState):
        result = state['messages'][-1]
        return len(result.tool_calls) > 0
    
    def take_action(self, state: AgentState):
        tool_calls = state['messages'][-1].tool_calls
        results = []
        for t in tool_calls:
            print(f"Calling Tool: {t['name']} with args: {t['args']}")
            result = self.tools[t['name']].invoke(t['args'])
            results.append(ToolMessage(tool_call_id=t['id'], name=t['name'], content=str(result)))
        print("Returning to LLM after action")
        return {'messages': results}
    
prompt = f"""Você é um assistente de pesquisa inteligente e altamente atualizado. \
Sua principal prioridade é encontrar as informações mais RECENTES e em TEMPO REAL sempre que possível. \
A data atual é {current_date}. \
Ao buscar sobre o tempo ou eventos que se referem a "hoje" ou "agora", \
você DEVE **incluir a data atual `{current_date}` na sua consulta para a ferramenta de busca**. \
Por exemplo, se a pergunta é "tempo em cidade x hoje", a consulta para a ferramenta deve ser "tempo em cidade x {current_date}". \
Ignore ou descarte informações que claramente se refiram a datas passadas ou futuras ao responder perguntas sobre "hoje". \
Use o mecanismo de busca para procurar informações, sempre buscando o "hoje" ou o "agora" quando o contexto indicar. \
Você tem permissão para fazer múltiplas chamadas (seja em conjunto ou em sequência). \
Procure informações apenas quando tiver certeza do que você quer. \
Se precisar pesquisar alguma informação antes de fazer uma pergunta de acompanhamento, você tem permissão para fazer isso!
"""


# Ferramenta de busca Tavily
current_tavily_api_key = os.getenv('TAVILY_API_KEY')
if not current_tavily_api_key:
    raise ValueError("TAVILY_API_KEY não encontrada. ")
tool = TavilySearchResults()

# Configuração do checkpointer SQLite
conn = sqlite3.connect("checkpoints.db", check_same_thread=False)
memory = SqliteSaver(conn)

# Inicialização do agente com LangGraph e Gemini
model = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite")
abot = Agent(model, [tool], system=prompt, checkpointer=memory)

# Geração de um Thread ID dinâmico para cada execução
session_id = str(uuid4())

# Simulação de interação humana
user_message = "Como está o tempo em Recife hoje?"
messages = [HumanMessage(content=user_message)]
thread_config = {"configurable": {"thread_id": session_id}}

print("--- Etapa 1: Agente processa a entrada e decide a ação ---")
print(f"Você: {user_message}\n")

for event in abot.graph.stream({"messages": messages}, thread_config):    
    for key, value in event.items():
        if key == "llm":
            last_message = value['messages'][-1]
            if isinstance(last_message, AIMessage) and last_message.tool_calls:
                print(f"Agente decidiu chamar a ferramenta com: {last_message.tool_calls}\n")
                print(f"--- AGENTE PAUSADO: Intervenção humana necessária para continuar ---\n")
            else:
                print(f"Agente respondeu sem ação: {last_message.content}\n")
                print(f"--- FIM DA INTERAÇÃO ---\n")

current_state = abot.graph.get_state(thread_config)

last_state_message = current_state.values['messages'][-1]

if current_state and current_state.next == ('action',) and isinstance(last_state_message, AIMessage) and last_state_message.tool_calls:
    tool_calls_pending = last_state_message.tool_calls

    if tool_calls_pending:
        print(f"\nO agente decidiu executar a seguinte ação de ferramenta:")
        for tool_call in tool_calls_pending:
            print(f"Ferramenta: {tool_call['name']} com argumentos {tool_call['args']}")

    human_approval = input("Aprovar a chamada da ferramenta? (s/N): ")
    if human_approval.lower() == 's':
        print("\n--- Continuando a execução do agente após aprovação humana ---\n")
        for event in abot.graph.stream(None, thread_config):
            for key, value in event.items():
                if key == "action":
                    print(f"Ferramenta executada, resultados retornados ao agente: {value['messages']}\n")
                elif key == "llm":
                    final_message = value['messages'][-1]
                    if isinstance(final_message, AIMessage):
                        print(f"\n\n- Agente respondeu: {final_message.content}\n")
                elif key == END:
                    print(f"DEBUG: GRafo terminou a execução.")        
            print(f"--- FIM DA INTERAÇÃO ---\n")
    else:
        print("Chamada da ferramenta rejeitada pelo humano. Encerrando interação.")
        print(f"--- FIM DA INTERAÇÃO ---\n")
else:
    print("Nenhuma ação de ferramenta pendente para aprovação. Encerrando interação.")
    if current_state:
        final_response_message = current_state.values['messages'][-1].content
        print(f"\n\n- Agente respondeu: {final_response_message}\n")
    print(f"--- FIM DA INTERAÇÃO ---\n")

from IPython.display import display, Image

try:
    image_data = abot.graph.get_graph().draw_mermaid_png()
    with open("grafo.png", "wb") as f:
        f.write(image_data)
    print("Diagrama salvo como grafo.png. Abrindo imagem...")
    import webbrowser, os
    webbrowser.open("grafo.png")  
except Exception as e:
    print(f"Erro ao gerar o diagrama do grafo: {e}")