import os
import requests
import re
from dotenv import load_dotenv
from tavily import TavilyClient
from bs4 import BeautifulSoup
from ddgs import DDGS


load_dotenv()
api_key = os.getenv("TAVILY_API_KEY")

if not api_key:
    raise ValueError("TAVILY_API_KEY not found in environment variables.")

tavily_client = TavilyClient(api_key=api_key)

cidade = "Recife"

query = f"Restaurantes em {cidade} tripadvisor com maior quantidade de reviews e faixa de preço"

ddg = DDGS()

def search(query, max_results=6):
    try:
        results = ddg.text(query, max_results=max_results)
        return [i["href"] for i in results]
    except Exception as e:
        raise e
        
print("Iniciando busca agêntica por URLs do Tripadvisor com Tavily")
tripadvisor_url = None
try:
    tavily_results = tavily_client.search(query, max_results=5)

    if tavily_results and tavily_results['results']:
        print(f"Tavily encontrou {len(tavily_results['results'])} resultados.")

        for resultado in tavily_results['results']:
            url = resultado['url']
            if "tripadvisor.com.br" in url or "tripadvisor.com" in url:
                tripadvisor_url = url
                print(f"URL do Tripadvisor encontrada: {tripadvisor_url}")
                break
        
        if not tripadvisor_url:
            print("Nenhum URL relevante do Tripadvisor nos primeiros resultados.")

    else: 
        print("Nenhum resultado encontrado com Tavily.")

except Exception as e:
    print(f"Erro ao usar Tavily: {e}")

if tripadvisor_url:
    clean_url = re.sub(r'-o\d+-', '-', tripadvisor_url)
    tripadvisor_url = clean_url
    print(f"✅ URL encontrada limpa de paginação.")

print("-" * 50)
print(f"URL Final do Tripadvisor para raspagem: {tripadvisor_url if tripadvisor_url else 'NÃO ENCONTRADO'}")
print("-" * 50)