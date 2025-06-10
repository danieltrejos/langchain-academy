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

# --- Router ---
# --- Goals ---

"""Router para dirigir las peticiones a los diferentes módulos de la aplicación.
Este router utiliza un grafo de estados para manejar las interacciones con el usuario y dirigir las peticiones a los módulos correspondientes.

Ahora se extendera el grafo para incluir un nodo de herramientas que permita al al modelo seleccionar el nodo al que desea acceder.
Para esto, usaremos dos ideas
1. Añadir un nodo que llamara a nuestra herramienta
2. Añadir un conditional edge que revisara la salidad del modelo y lo enrutara a nuestro nodo de llamado de erramienta o simplemente finalizara si
no se dearrolla un llamado a la herramienta.
"""
# Funcion que sera la herramienta
def multiply(a:int, b:int) -> int:
    """Multiply a and b.
    
    Arg:
        a: first int
        b: second int
    """
    return a * b

# Instanciar el modelo y bindear la tool
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
llm_with_tools = llm.bind_tools([multiply])

# Nodo para llamado de la tool
def tool_calling_llm(state: MessagesState):
    response = llm_with_tools.invoke(state["messages"])
    return {"messages":[response]}
# Usaremos la clase preconstruida ToolNode y simplemente pasaremos una lista de nuestras herramientas para inicializarlo
# Usaremos la clase preconstruida tools_condition como nuestro conditional edge

# Construir el graph
builder = StateGraph(MessagesState)
builder.add_node("tool_calling_llm", tool_calling_llm)# Nodo llamado:"tool_calling_llm"
builder.add_node("tools", ToolNode([multiply]))
builder.add_edge(START,"tool_calling_llm")
builder.add_conditional_edges(
    "tool_calling_llm",
    # If the latest message (result) from assistant contains a tool call -> tools_condition route to the tools
    # If the latest message (result) from assistant is a not a tool call -> tools_condition route to END,
    tools_condition,
)
builder.add_edge("tools", END)
graph = builder.compile()

# Generar y guardar el graph
""" 
print("Generando imagen del graph...")
try:
    with open("03-graph-tool_calling_llm.png", "wb") as f:
        f.write(graph.get_graph().draw_mermaid_png())
    print("✅ Archivo '02-graph-chain.png' creado exitosamente!")
except Exception as e:
    print(f"❌ Error al crear el archivo: {e}")
"""    

from langchain_core.messages import HumanMessage
messages = [HumanMessage(content="Hello, what is 2 multiplied by 2?")]
messages = graph.invoke({"messages": messages})
for m in messages['messages']:
    m.pretty_print()