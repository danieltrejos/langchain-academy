import os, getpass
from dotenv import load_dotenv
from langchain_community.tools.tavily_search import TavilySearchResults

# Test OpenAI
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

# Cargar variables de entorno desde .env local (en module-0)
load_dotenv(dotenv_path='.env')
def _set_env(var: str):
    if not os.environ.get(var):
        os.environ[var] = getpass.getpass(f"{var}: ")

# Verificar OpenAI API Key
_set_env("OPENAI_API_KEY")
print(f"OpenAI API Key verificada: {os.environ.get('OPENAI_API_KEY', 'NO ENCONTRADA')[:20]}...")

# Verificar Tavily API Key
_set_env("TAVILY_API_KEY")
print(f"Tavily API Key verificada: {os.environ.get('TAVILY_API_KEY', 'NO ENCONTRADA')[:20]}...")


gpt4o_chat = ChatOpenAI(model="gpt-4o-mini", temperature=0)
msg = HumanMessage(content="Hello world", name="Lance")
messages = [msg]

try:
    result = gpt4o_chat.invoke(messages)
    print("✅ OpenAI - Respuesta exitosa:")
    print(f"   {result.content}")
except Exception as e:
    print(f"❌ OpenAI Error: {e}")

# Test Tavily
print("\n" + "="*50)
print("PROBANDO TAVILY SEARCH API")
print("="*50)

try:
    tavily_search = TavilySearchResults(max_results=3)
    search_docs = tavily_search.invoke("What is LangGraph?")
    
    print("✅ Tavily - Búsqueda exitosa:")
    print(f"   Número de resultados: {len(search_docs)}")
    
    for i, doc in enumerate(search_docs, 1):
        print(f"\n   Resultado {i}:")
        print(f"   Título: {doc.get('title', 'Sin título')}")
        print(f"   URL: {doc.get('url', 'Sin URL')}")
        print(f"   Contenido: {doc.get('content', 'Sin contenido')[:100]}...")
        
except Exception as e:
    print(f"❌ Tavily Error: {e}")
    print(f"   Tipo de error: {type(e)}")
    print(f"   API Key actual: {os.environ.get('TAVILY_API_KEY', 'NO ENCONTRADA')[:30]}...")