import os
import re
from google import genai
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from typing import TypedDict

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
client = genai.Client(api_key=api_key)

class Agent:
    def __init__(self, system=""):
        self.system = system
        self.messages = []
        if self.system:
            self.messages.append({"role": "system", "content": self.system})

    def __call__(self, message):
        self.messages.append({"role": "user", "content": message})
        result = self.execute()
        self.messages.append({"role": "assistant", "content": result})
        return result

    def execute(self):
        # Constrói o prompt com todo o histórico de mensagens
        prompt = ""
        for msg in self.messages:
            prompt += f"{msg['role']}: {msg['content']}\n"
        
        # Envia para o Gemini
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt)
        return response.text
    

PROMPT_REACT = """
Você funciona em um ciclo de Pensamento, Ação, Pausa e Observação.
Ao final do ciclo, você fornece uma Resposta.
Use "Pensamento" para descrever seu raciocínio.
Use "Ação" para executar ferramentas - e então retorne "PAUSA".
A "Observação" será o resultado da ação executada.
Se não tiver "Ação" a ser retornada, forneça diretamente a "Resposta".
Ações disponíveis:
    - consultar_estoque: retorna a quantidade disponível de um item no inventário (ex: "consultar_estoque: teclado")
    - consultar_preco_produto: retorna o preço unitário de um produto (ex: "consultar_preco_produto: mouse gamer")
    - encontrar_produto_mais_caro: retorna o nome e o preço do produto mais caro no inventário (não requer argumentos)
    - calcular_valor_total_lista: calcula o valor total de uma lista de itens de compra. Recebe uma string com itens separados por virgula.

Exemplo:
Pergunta: Quantos monitores temos em estoque?
Pensamento: Devo consultar a ação consultar_estoque para saber a quantidade de monitores.
Ação: consultar_estoque: monitor
PAUSA

Observação: Temos 75 monitores em estoque.
Resposta: Há 75 monitores em estoque.

Exemplo:
Pergunta: Qual é o produto mais caro?
Pensamento: Devo usar a ação encontrar_produto_mais_caro para descobrir qual é o produto mais caro.
Ação: encontrar_produto_mais_caro
PAUSA

Observação: O produto mais caro é o(a) monitor com preço de R$ 999.90.
Resposta: O produto mais caro é o monitor, que custa R$ 999.90.

Exemplo:
Pergunta: Quanto custa um teclado e um mouse gamer?
Pensamento: O usuário quer saber o valor total de vários itens. Devo usar a ação calcular_valor_total_lista com os itens "teclado, mouse gamer".
Ação: calcular_valor_total_lista: teclado, mouse gamer
PAUSA

Observação: O valor total dos itens encontrados é R$ 249.50.
Resposta: O valor total do teclado e do mouse gamer é R$ 249.50.
""".strip()

# Criando o Agent State
class AgentState(TypedDict):
    pergunta: str # Armazena a pergunta inicial
    historico: list[str] # Armazena o histórico de interações
    acao_pendente: str # Armazena a próxima ação a ser executada
    resposta_final: str # Armazena a resposta final do agente

# Criando as ferramentas que serão usadas pelo agente
def consultar_estoque(item: str) -> str:
    item = item.lower()
    estoque = {
        "monitor": 75,
        "teclado": 120,
        "mouse gamer": 80,
        "webcam": 40,
        "headset": 60,
        "impressora": 15
    }

    if item in estoque:
        return f"Temos {estoque[item]} {item}s em estoque."
    else:
        return f"Item '{item}' não encontrado no inventário."
    
def consultar_preco_produto(produto: str) -> str:
    produto = produto.lower()
    precos = {
        "monitor": 999.90,
        "teclado": 150.00,
        "mouse gamer": 99.50,
        "webcam": 120.00,
        "headset": 180.00,
        "impressora": 750.00
    }

    if produto in precos:
        return f"O preço de um(a) {produto} é R$ {precos[produto]:.2f}."
    else:
        return f"Produto '{produto}' não encontrado na lista de preços."


def encontrar_produto_mais_caro() -> str:
    # dicionário de preços do inventário:
    precos_do_inventario = {
        "monitor": 999.90,
        "teclado": 150.00,
        "mouse gamer": 99.50,
        "webcam": 120.00,
        "headset": 180.00,
        "impressora": 750.00
    }

    if not precos_do_inventario:  # verificação de segurança
        return "Nenhum produto encontrado na lista de preços para comparação."

    # busca do produto mais caro
    nome_produto_mais_caro = max(precos_do_inventario, key=precos_do_inventario.get)
    valor_produto_mais_caro = precos_do_inventario[nome_produto_mais_caro]

    return f"O produto mais caro é o(a) {nome_produto_mais_caro} com preço de R$ {valor_produto_mais_caro:.2f}."

def run_react_agent(pergunta: str, max_iterations: int = 5) -> str:
    # Inicializa o agente com o prompt do sistema
    agent = Agent(system=PROMPT_REACT)
    # Primeira mensagem do usuário
    current_prompt = f"Pergunta: {pergunta}"

    for i in range(max_iterations):
        response_text = agent(current_prompt).strip()

        print(f"--- Iteração {i+1} ---")
        print(f"Modelo pensou/respondeu:\n{response_text}\n")

        if response_text.startswith("Resposta:"):
            return response_text.replace("Resposta:", "").strip()

        # Verifica se a resposta final está presente, mesmo que haja Pensamento antes.
        response_match_final = re.search(r"Resposta:\s*(.*)", response_text, re.DOTALL)
        if response_match_final:
            return response_match_final.group(1).strip()

        # Ajuste para lidar com ações com ou sem argumento (e sem o ':' para ações sem argumento)
        # Ex: "Ação: nome_da_acao: argumento" OU "Ação: nome_da_acao"
        match = re.search(r"Ação:\s*(\w+)(?::\s*([^\n\r]*))?", response_text)

        if match:
            action_name = match.group(1).strip()
            action_arg = match.group(2).strip() if match.group(2) is not None else ""

            observacao = ""
            if action_name == "consultar_estoque":
                observacao = consultar_estoque(action_arg)
            elif action_name == "consultar_preco_produto":
                observacao = consultar_preco_produto(action_arg)
            elif action_name == "encontrar_produto_mais_caro":
                observacao = encontrar_produto_mais_caro()
            elif action_name == "calcular_valor_total_lista":
                observacao = calcular_valor_total_lista(action_arg)
            else:
                observacao = f"Erro: Ação '{action_name}' desconhecida."

            current_prompt = f"Observação: {observacao}"

            print(f"Executou ação: {action_name} com argumento '{action_arg}'")
            print(f"Observação: {observacao}\n")

        else:
            # Se não encontrou ação nem resposta formal, mas a resposta parece ser direta, retorne-a
            if not any(tag in response_text for tag in ["Pensamento:", "Ação:", "PAUSA", "Observação:"]):
                return response_text.strip()
            return f"Erro: O agente não conseguiu extrair uma Ação ou Resposta final após {i+1} iterações. Última resposta: {response_text}"

    return "Erro: Limite máximo de iterações atingido sem uma resposta final."

def calcular_valor_total_lista(lista_itens: str) -> str:
    precos_do_inventario = {
        "monitor": 999.90,
        "teclado": 150.00,
        "mouse gamer": 99.50,
        "webcam": 120.00,
        "headset": 180.00,
        "impressora": 750.00
    }

    itens_processados = [item.strip().lower() for item in lista_itens.split(',')]
    
    valor_total = 0.0
    itens_nao_encontrados = []

    for item in itens_processados:
        if item in precos_do_inventario:
            valor_total += precos_do_inventario[item]
        else:
            itens_nao_encontrados.append(item)

    resposta = f"O valor total dos itens encontrados é R$ {valor_total:.2f}."
    if itens_nao_encontrados:
        resposta += f" Os seguintes itens não foram encontrados e não foram incluídos no cálculo: {', '.join(itens_nao_encontrados)}"
        
    return resposta


def iniciar_conversacao_com_agente():
    print("--- Agente de Inventário Interativo ---")
    print("Digite sua pergunta sobre o inventário, ou digite 'sair' para encerrar.")
    print("*" * 50)

    while True:
        pergunta_usuario = input("\nVocê: ")

        if pergunta_usuario.lower().strip() == 'sair':
            print("Encerrando a conversa. Até logo!")
            break
        
        print("\nAgente: Processando...")
        try:
            # Chama a sua função run_react_agent com a pergunta do usuário
            resposta_agente = run_react_agent(pergunta_usuario)
            print(f"\nAgente: {resposta_agente}")
        except Exception as e:
            # Captura erros para evitar que o loop seja interrompido
            print(f"\nAgente: Ocorreu um erro ao processar sua pergunta: {e}")
            print("Por favor, tente novamente ou digite 'sair'.")

if __name__ == "__main__": #EXECUTA A CONVERSAÇÃO QUANDO O SCRIPT É INICIADO
    iniciar_conversacao_com_agente()