# Projeto LangGraph Agents – Aprendizado de Agentes com LLMs

Este repositório reúne experimentos e exemplos práticos de uso de agentes inteligentes baseados em LLMs (Modelos de Linguagem de Grande Escala) utilizando a biblioteca [LangGraph](https://github.com/langchain-ai/langgraph) e integrações com ferramentas externas, como mecanismos de busca, scraping, checkpoints e colaboração multiagente.

## Objetivo
O objetivo deste projeto é servir como ambiente de aprendizado e demonstração de técnicas modernas de construção de agentes autônomos, interativos e colaborativos, explorando tópicos como:

- **Orquestração de agentes com LangGraph**: Criação de fluxos de decisão, controle de estado e execução de múltiplos agentes.
- **Integração com LLMs**: Uso do Google Gemini (via LangChain) para geração de respostas, planejamento, reflexão e revisão de textos.
- **Ferramentas externas**: Acesso a mecanismos de busca (Tavily), scraping de sites (TripAdvisor), integração com bancos de dados (SQLite para checkpoints), e uso de ferramentas customizadas.
- **Human-in-the-loop**: Exemplos de agentes que permitem intervenção humana para aprovar ou rejeitar ações antes de sua execução.
- **Checkpoints e persistência**: Demonstração de como salvar e restaurar o estado de agentes usando bancos de dados.
- **Multiagentes e colaboração**: Exemplos de múltiplos agentes trabalhando juntos em tarefas complexas, como escrita, pesquisa, revisão e crítica.
- **Prompts estruturados**: Separação de prompts para planejamento, escrita, reflexão e pesquisa, facilitando a customização e reuso.

## Estrutura dos Diretórios e Arquivos

O projeto está organizado em subdiretórios temáticos dentro de `src/`:

- `agentic-search/`: Exemplo de busca agêntica, scraping e integração Tavily + BeautifulSoup + Selenium para extração de dados do TripAdvisor.
- `checkpoints/`: Demonstração de uso de checkpoints para persistência de estado de agentes.
- `human-in-the-loop/`: Exemplo de agente com intervenção humana para aprovação de ações.
- `langgraph/`: Agente de pesquisa interativo usando LangGraph e integração com Tavily.
- `manual-chatbot/`: Exemplo de agente reativo com ferramentas customizadas para inventário (consultar estoque, preço, etc).
- `multiagents/`: Exemplo avançado de orquestração de múltiplos agentes (escritor, crítico, planejador, pesquisador) colaborando em tarefas de escrita, com prompts e estados separados.
	- `AgentState.py`: Definição do estado do agente multiagente.
	- `nodes.py`: Implementação dos nós do grafo (planejamento, pesquisa, geração, reflexão, crítica).
	- `prompts.py`: Prompts estruturados para cada etapa do processo.
	- `Queries.py`: Modelo de queries para pesquisa estruturada.

Arquivos principais:
- `requirements.txt`: Dependências do projeto.
- `.env`: Variáveis de ambiente (chaves de API).
- `checkpoints.db`: Banco de dados SQLite para persistência de estado (ignorado pelo git).

## Exemplos de Funcionalidades

- **Busca e scraping inteligente**: Busca de restaurantes no TripAdvisor, extração de reviews, avaliações e preços usando Tavily, BeautifulSoup e Selenium.
- **Agente de escrita multiagente**: Planejamento, pesquisa, escrita, reflexão e revisão de redações com colaboração entre múltiplos agentes e revisões automáticas.
- **Agente reativo com ferramentas**: Chatbot que responde perguntas sobre inventário, preços e cálculos usando ferramentas customizadas.
- **Checkpoints e persistência**: Salva e recupera o estado de conversas e execuções de agentes.
- **Human-in-the-loop**: Permite intervenção humana para aprovar ou rejeitar ações do agente.

## Temas de Aprendizado Abrangidos
- Fundamentos de agentes LLM e LangGraph
- Planejamento, reflexão e revisão automatizada
- Busca, scraping e integração com ferramentas externas
- Persistência de estado e checkpoints
- Multiagentes e colaboração
- Intervenção humana no loop de decisão
- Prompts estruturados e reutilizáveis