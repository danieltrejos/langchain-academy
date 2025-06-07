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