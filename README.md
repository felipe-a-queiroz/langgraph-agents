# Projeto LangGraph Agents – Aprendizado de Agentes com LLMs

Este repositório reúne experimentos e exemplos práticos de uso de agentes inteligentes baseados em LLMs (Modelos de Linguagem de Grande Escala) utilizando a biblioteca [LangGraph](https://github.com/langchain-ai/langgraph) e integrações com ferramentas externas, como mecanismos de busca e armazenamento de checkpoints.

## Objetivo
O objetivo deste projeto é servir como ambiente de aprendizado e demonstração de técnicas modernas de construção de agentes autônomos, interativos e colaborativos, explorando tópicos como:

- **Orquestração de agentes com LangGraph**: Criação de fluxos de decisão, controle de estado e execução de múltiplos agentes.
- **Integração com LLMs**: Uso do Google Gemini (via LangChain) para geração de respostas, planejamento, reflexão e revisão de textos.
- **Ferramentas externas**: Acesso a mecanismos de busca (Tavily), integração com bancos de dados (SQLite para checkpoints), e uso de ferramentas customizadas.
- **Human-in-the-loop**: Exemplos de agentes que permitem intervenção humana para aprovar ou rejeitar ações antes de sua execução.
- **Checkpoints e persistência**: Demonstração de como salvar e restaurar o estado de agentes usando bancos de dados.
- **Multiagentes e colaboração**: Exemplos de múltiplos agentes trabalhando juntos em tarefas complexas, como escrita, pesquisa e revisão.

## Estrutura dos Arquivos
- `main.py`: Exemplo básico de agente reativo com ferramentas customizadas para inventário.
- `main-langgraph.py`: Agente de pesquisa interativo usando LangGraph e integração com Tavily.
- `main-checkpoints.py`: Demonstração de uso de checkpoints para persistência de estado de agentes.
- `main-human-in-the-loop.py`: Exemplo de agente com intervenção humana para aprovação de ações.
- `main-multiagents.py`: Exemplo de orquestração de múltiplos agentes (escritor, crítico, planejador, pesquisador) colaborando em tarefas de escrita.
- `requirements.txt`: Dependências do projeto.
- `.env`: Variáveis de ambiente (chaves de API).

## Temas de Aprendizado Abrangidos
- Fundamentos de agentes LLM e LangGraph
- Planejamento, reflexão e revisão automatizada
- Busca e integração com ferramentas externas
- Persistência de estado e checkpoints
- Multiagentes e colaboração
- Intervenção humana no loop de decisão