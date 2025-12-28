from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, List
import operator
import os

from dotenv import load_dotenv
from google import genai 
from langchain_google_genai import ChatGoogleGenerativeAI

from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, ToolMessage, BaseMessage
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_tavily import TavilySearch

load_dotenv()

os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY")
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

tool = TavilySearch(max_results=3)
print(type(tool))
print(tool.name)

class AgentState(TypedDict):
    messages: Annotated[List[AnyMessage], operator.add]