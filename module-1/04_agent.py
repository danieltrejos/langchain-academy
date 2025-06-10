import os, getpass
from dotenv import load_dotenv
# from typing_extensions import TypedDict # type hinting for state
# from typing import Literal
# from typing import Annotated

from IPython.display import Image, display # Para mostrar el grafico
from pprint import pprint # Para mejor formato del print para los mensajes

# OpenAI
from langchain_openai import ChatOpenAI
# Messages
# from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, ToolMessage, AnyMessage

# Graph
from langgraph.graph import StateGraph, START, END # Importar StateGraph para crear el grafo de estados y los nodos de inicio y fin
from langgraph.graph.message import add_messages

# Import necesario para MessagesState prebuilt
from langgraph.graph import MessagesState

# Import necesario para el toolnode preconstruido
from langgraph.prebuilt import ToolNode
# Import necesario para ConditionalEdge prebuilt
from langgraph.prebuilt import tools_condition


# Cargar variables de entorno desde .env local (en module-0)
load_dotenv(dotenv_path='.env')
def _set_env(var: str):
    if not os.environ.get(var):
        os.environ[var] = getpass.getpass(f"{var}: ")

# Verificar OpenAI API Key
_set_env("OPENAI_API_KEY")
print(f"OpenAI API Key verificada: {os.environ.get('OPENAI_API_KEY', 'NO ENCONTRADA')[:20]}...")

#! --- AGENT ---
# Review: Anteriormente se construyo un router 
""" 
Nuestro modelo de chat decide hacer un llamado a una herramienta o no basado en la entrada del usuario.
Usamos un conditional edge para decidir si el modelo toma un nodo que llama la herramienta o simplemente termina.
"""

# Objetivo> Extender la funcionalidad a una arquitectura generica de agente
""" 
En el ejemplo anterior, invocamos el modelo y si este elige llamar una herramienta, nosotros retornamos ToolMessage al usuario.
Pero, que pasa si simplemente pasamos el ToolMessage de vuelta al modelo?
Podemos permitir alguna de las siguientes opciones:
1. El modelo puede decidir si llama a otra herramienta o
2. El modelo puede decidir si responde directamente al usuario.
Esa es la idea detras de un Reactive Agent (ReAct), una arquitectura de agente general
    - act - Le permite al modello llamar herramientas especificas
    - observe - pasar la salida de la herramienta al modelo
    - reason - permitir al modelo razonar sobre la salida de la herramienta y decidir que hacer a continuacion si llama a otra herramienta o responde al usuario.
Este arquitectura de proposito general puede ser usada para muchos tipos de herramientas y tareas.

"""
