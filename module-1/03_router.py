import os, getpass
from dotenv import load_dotenv
from typing_extensions import TypedDict # type hinting for state
import random
from typing import Literal
from IPython.display import Image, display
from pprint import pprint
from typing import Annotated

# OpenAI
from langchain_openai import ChatOpenAI
# Messages
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, ToolMessage, AnyMessage
# Graph
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langgraph.graph.message import add_messages
# Import necesario para MessagesState prebuilt
from langgraph.graph import MessagesState

# Cargar variables de entorno desde .env local (en module-0)
load_dotenv(dotenv_path='.env')
def _set_env(var: str):
    if not os.environ.get(var):
        os.environ[var] = getpass.getpass(f"{var}: ")

# Verificar OpenAI API Key
_set_env("OPENAI_API_KEY")
print(f"OpenAI API Key verificada: {os.environ.get('OPENAI_API_KEY', 'NO ENCONTRADA')[:20]}...")
