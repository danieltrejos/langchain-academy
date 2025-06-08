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

print("\n-------------------------------------")
print("Modulo sobre Chain de con langraph")
print("-------------------------------------")

print("\n--- Objetivo: Construir un chain simple que combine 4 conceptos ---")
print("""
    1. Usar chat messages como nuestro estado del graph
    2. Usar chat models en nodos del graph
    3. Vincular herramientas (tools) a nuestro chat model
    4. Ejecutar tools call en los nodos del graph
    """)

#! Message
# Los modelos de chat usan la clase messages, la cual capturan diferentes roles dentro de una conversacion.
# LangChain soporta varios tipos de mensajes, incluyendo:
# - HumanMessage: Mensajes enviados por el usuario
# - AIMessage: Mensajes enviados por el modelo de IA
# - SystemMessage: Mensajes que definen el contexto o instrucciones para el modelo
# - ToolMessage: Mensajes que representan llamadas a herramientas (tools)
print("\n--- Mensajes ---")

print("""
    Crearmos una lista de mensajes. Cada mensaje puede ser proveid con diferentes campos:
    - content: El contenido del mensaje
    - name: El nombre del remitente quien crea el mensaje(opcional)
    response_metadata: Metadatos de la respuesta (opcional)
    - additional_kwargs: Cualquier otro argumento adicional (opcional)
    """)

messages = [AIMessage(content=f"So you said you are rearching ocean mammals?", name="Model")]

messages.extend([(HumanMessage(content=f"Yes, thats right.",name="Lance"))])
messages.extend([AIMessage(content=f"Great! What what would you like to learn about.", name="Model")])
messages.extend([HumanMessage(content=f"I would like to learn the best place to see Orcas in Colombia.", name="Lance")])

for m in messages:
    m.pretty_print()
print("\n--- Mensajes creados ---")

#! A continuacion, vamos a crear un modelo de chat que pueda interactuar con estos mensajes.
# Instanciar el modelo de chat
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.5)
""" #Comentado para probar las tools
# Invocar el modelo de chat con pasandole la lista de mensajes
print("\n--- Invocando el modelo de chat con los mensajes---")
result = llm.invoke(messages)

# El resultado es un mensaje de AIMessage que contiene la respuesta del modelo
type(result)
print(result)
print("\n--- Resultado del modelo de chat ---")
result.pretty_print()
print(result.response_metadata)
"""

#! Tools
# Las herramientas (tools) son funciones que pueden ser invocadas por el modelo de chat.
# Las tools son necesasitdas cuando se quiere que el model tome parte del control de la ejecucion o llamar una api externa
# La mayorias de los llms modernos soportan tools, pero es importante verificar la documentacion del modelo que se esta usando.
# La tool calling interface de LangChain permite definir herramientas que pueden ser invocadas por el modelo de chat facilmente.
# Se puede pasar cualquier funcion de python como una herramienta, y el modelo de chat puede invocarla cuando sea necesario. dentro de ChatModel.bind_tools(tools)

# Definir una herramienta (tool) que multiplica dos numeros
def multiply(a: int, b: int) -> int:
    """Multiply a and b.

    Args:
        a: first int
        b: second int
    """
    return a * b

# bindear la herramienta al modelo de chat previamente definido, sino se puede definir el llm en la misma linea que la herramienta
# llm_with_tools = ChatOpenAI(model="gpt-4o-mini", temperature=0.5).bind_tools([multiply])
llm_with_tools = llm.bind_tools([multiply])

# Hacer una llamada a la herramienta
print("\n--- Invocando la herramienta, pasandole un mensaje ---")
tool_call = llm_with_tools.invoke(
    [HumanMessage(content=f"What is 2 multipled by 3?", name="Lance")],
)
print("\n--- Resultado de la herramienta ---")
tool_call.pretty_print()
""" 
# Imprimir el AIMessage y additional_kwargs
print("\n--- Detalles del AIMessage ---")
print(f"Tipo: {type(tool_call)}")
print(f"Contenido: {tool_call.content}")
print(f"ID: {tool_call.id}")

print("\n--- Additional kwargs ---")
print("Additional kwargs:")
pprint(tool_call.additional_kwargs)

print("\n--- Tool calls (si existen) ---")
if hasattr(tool_call, 'tool_calls') and tool_call.tool_calls:
    print("Tool calls encontradas:")
    for i, tc in enumerate(tool_call.tool_calls):
        print(f"  Tool call {i+1}:")
        print(f"    ID: {tc['id']}")
        print(f"    Función: {tc['name']}")
        print(f"    Argumentos: {tc['args']}")
else:
    print("No hay tool calls en este mensaje")

print("\n--- Response metadata ---")
print("Response metadata:")
pprint(tool_call.response_metadata) 
"""

# Crear el ToolNode con las herramientas disponibles
tool_node = ToolNode([multiply])

# Si hay tool calls, ejecutarlos
if hasattr(tool_call, 'tool_calls') and tool_call.tool_calls:
    # Crear el estado con el mensaje que contiene tool calls
    state = {"messages": [tool_call]}
    
    # Ejecutar las herramientas
    result = tool_node.invoke(state)
    
    print("Resultados de las herramientas:")
    for msg in result["messages"]:
        if isinstance(msg, ToolMessage):
            print(f"Tool ID: {msg.tool_call_id}")
            print(f"Resultado: {msg.content}")

print("\n--- Response metadata ---")
print("Response metadata:")
pprint(tool_call.response_metadata)

#! --- Usando Mensajes como estado
# Con los fundamentos definidos, ahora podemos construir un graph que use mensajes como estado.

# Definamos nuestro state  MessagesState, que es un schema que sirve como esquema para todos los Nodos y Edges del graph.

#class MessagesState(TypedDict):
#    """Estado del graph"""
#    messages: list[AnyMessage]


#! Reducer
# Reducer es una funcion que permite especificar como son desarrolladas las actualziaciones del estado.
# Si no se especifica, el estado es actualizado y sobreescrito con el resultado del nodo. 
# Como queremos agregar mensajes al estado, podemos usar el pre-build  add_messages reducer
# Esto asegura que los mensajes sean agregados al estado en lugar de sobreescribirlo a la lista de mensajes existente.
# Nosotro anotamos via Annotated nuestro key con un reducer function como metadata

""" 
class MesssagesState(TypedDict):
    # Estado del graph
    messages: Annotated[list[AnyMessage], add_messages]
"""
class State(MessagesState):
    # Add any keys needed mas alla de messages, que esta prebuilt
    pass

# -------Ver como funciona el reducer add_messages de forma aislada
# Initial state
initial_messages = [AIMessage(content="Hello! How can I assist you?", name="Model"),
                    HumanMessage(content="I'm looking for information on marine biology.", name="Lance")
                ]

# New message to add
new_message = AIMessage(content="Sure, I can help with that. What specifically are you interested in?", name="Model")

# Test
result = add_messages(initial_messages , new_message)

print("\n--- Mensajes con pretty_print ---")
for i, msg in enumerate(result, 1):
    print(f"Mensaje {i}:")
    msg.pretty_print()
    print()  # Línea en blanco para separar
    
# ---
# Visualizar el resultado
""" 
result = add_messages(initial_messages , new_message)
print(f"Tipo: {type(result)}")
print(f"Longitud: {len(result)}")
print("Contenido:")
for i, msg in enumerate(result):
    print(f"  {i}: {type(msg).__name__} - {getattr(msg, 'name', 'Sin nombre')}: {msg.content}")
"""
#! Graph
# Usar el MessagesState como estado del graph
# State
class MessagesState(MessagesState):
    """Estado del graph"""
    pass

# Node
def tool_callin_llm(state: MessagesState) -> MessagesState:
    """Node that invokes the LLM with tools."""
    # Invocar el modelo de chat con los mensajes del estado
    response = llm_with_tools.invoke(state["messages"])
    
    # Retornar el nuevo estado con el mensaje de respuesta
    # return {"messages": [llm_with_tools.invoke(state["messages"])]}
    return {"messages": [response]}

#! Build graph
builder = StateGraph(MessagesState)
builder.add_node("tool_callin_llm", tool_callin_llm)
builder.add_edge(START, "tool_callin_llm")
builder.add_edge("tool_callin_llm", END)

# Compile graph
graph = builder.compile()

# Generar y guardar el graph
print("Generando imagen del graph...")
try:
    with open("02-graph-chain.png", "wb") as f:
        f.write(graph.get_graph().draw_mermaid_png())
    print("✅ Archivo '02-graph-chain.png' creado exitosamente!")
except Exception as e:
    print(f"❌ Error al crear el archivo: {e}")
    
#! Probar el graph
print("\n--- Probando el graph ---")
try:
    # Test con saludo simple
    messages = graph.invoke({"messages": [HumanMessage(content="Hello!", name="User")]})
    print("Respuesta a 'Hello!':")
    for m in messages['messages']:
        m.pretty_print()
    
    print("\n" + "="*50)
    
    # Test con multiplicación (usará la tool)
    messages = graph.invoke({"messages": [HumanMessage(content="What is 5 multiplied by 7?", name="User")]})
    print("Respuesta a multiplicación:")
    for m in messages['messages']:
        m.pretty_print()
    [print(f"{m.name}: {m.content}") for m in messages['messages']]
        
    
except Exception as e:
    print(f"❌ Error al ejecutar el graph: {e}")