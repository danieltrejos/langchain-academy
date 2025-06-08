import os, getpass
from dotenv import load_dotenv
from typing_extensions import TypedDict # type hinting for state
import random
from typing import Literal
from IPython.display import Image, display

# OpenAI
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START, END

# Cargar variables de entorno desde .env local (en module-0)
load_dotenv(dotenv_path='.env')
def _set_env(var: str):
    if not os.environ.get(var):
        os.environ[var] = getpass.getpass(f"{var}: ")

# Verificar OpenAI API Key
_set_env("OPENAI_API_KEY")
print(f"OpenAI API Key verificada: {os.environ.get('OPENAI_API_KEY', 'NO ENCONTRADA')[:20]}...")

#! State: Definir el estado del graph
# El estado del graph es un schema que sirve como esquema para todos los Nodos y Edges del graph.
class State(TypedDict):
    """Estado del graph"""
    graph_state: str

#! Node: Definir un nodo
# Los nodos son solo funciones de python que representan un paso en el graph.
# El primer argumento de un nodo es el estado del graph, que es un objeto de tipo State. definido arriba.

def node_1(state):
    """Nodo 1 del graph"""
    print("--- Node 1 ---")
    return {"graph_state": state['graph_state'] +"I am"}

def node_2(state):
    """Nodo 2 del graph"""
    print("--- Node 2 ---")
    return {"graph_state": state['graph_state'] +" happy"}

def node_3(state):
    """Nodo 3 del graph"""
    print("--- Node 3 ---")
    return {"graph_state": state['graph_state'] +" sad."}

#! Edge: Definir edges y la logica de las edges
# Las edges son funciones que conectan nodos.
# Los Edges normales son usados si se quiere ir siempres de un nodo a otro. Ejemplo: de node_1 a node_2.
# Los Edges condicionales son usados si se quiere ir de un nodo a otro dependiendo de una condición o si se quiere tener una ruta opcional entre nodos.
# Los Edges son implem,enmtados como funciones que retornan el siiguiente nodo a visitar basado en alguna logica
def decide_mood(state) -> Literal['node_2', 'node_3']:
    """Decide the next node based on the estado"""
    user_input = state['graph_state']
    
    # Aqui, decidimos hacer una decicion 50/50 entre los nodes 2, 3
    if random.random() < 0.5:
        # 50% de las veces, retorna Node 2
        return "node_2"
    
    # 50% de las veces, retorna Node 3
    return "node_3"

#! Graph: Construir el graph
# El graph es un objeto que contiene nuestro componentes definidos anteriormente estado, los nodos y edges del graph.
# 1. Inicializamos un StateGraph con la clase State inicial del graph que definimos.
# 2. Agregamos los nodos y edfes al graph usando los metos add_node, add_edge, add_condicional_edges.
# 3. Usamos los nodos especiales START y END para definir el inicio y fin del graph.
# 4. Se usan las librerias:
#       from IPython.display import Image, display
#       from langgraph.graph import StateGraph, START, END

# Construir el graph
builder = StateGraph(State)
builder.add_node("node_1", node_1)
builder.add_node("node_2", node_2)
builder.add_node("node_3", node_3)

# Logica de las edges
builder.add_edge(START, "node_1")
builder.add_conditional_edges("node_1", decide_mood)
builder.add_edge("node_2", END)
builder.add_edge("node_3", END)

# Compilar el graph
graph = builder.compile()

#! Visualizar el graph
# display(Image(graph.get_graph().draw_mermaid_png())) #Esta linea es para Jupyter Notebook
# Guardar como PNG
with open("graph.png", "wb") as f:
    f.write(graph.get_graph().draw_mermaid_png())
    
# Para visualizar el grafo en un entorno que soporte Mermaid, puedes usar:
# print(graph.get_graph().draw_mermaid())

#! Ejecutar el graph
# El graph compilado implementa el protocolo runnable
# Este provee una forma estandarizada de ejecutar componentes de langChain. 
# invoke es uno de los metods standars de esta interfaz.
# La entrada es un dicionario que contiene el estado inicial del graph: {"graph_state": "I am Daniel. "}.
# El resultado es un dicionario que contiene el estado final del graph. luego de ejecutar el metodo graph.invoke().
# Invoke ejecuta el grafico entero de manera secuencial, pasando el estado de un nodo al siguiente.
# Este esepra a que cada paso se complete antes de pasar al siguiente.
# Retorna el estado final del graph, Despues que cada nodo se ejecuto.
result = graph.invoke({"graph_state": "I am Daniel. "})
print(f"Estado final del graph: {result['graph_state']}")