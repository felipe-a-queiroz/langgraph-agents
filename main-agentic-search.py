import os
import requests
import re
from dotenv import load_dotenv
from tavily import TavilyClient
from bs4 import BeautifulSoup
from ddgs import DDGS

from selenium import webdriver
from selenium.common.exceptions import WebDriverException, TimeoutException


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

def scrape_restaurantes_info(url):
    if not url:
        print("Erro: URL vazia ou não localizada para raspagem.")
        return None
    
    try:
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126")
        
        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(30)
    
    except Exception as e:
        print(f"Erro ao configurar o WebDriver: {e}")
        return None
    
    try:
        print(f"Tentando carregar a página com Selenium: {url}")
        driver.get(url)
        
        driver.implicitly_wait(10)
        
        response_text = driver.page_source

    except TimeoutException:
        print("Erro: Tempo de carregamento da página excedido.")
        return None
    except WebDriverException as e:
        print(f"Erro ao carregar a página com Selenium: {e}")
        return None
    finally:
        driver.quit()
    
    soup = BeautifulSoup(response_text, 'html.parser')
    return soup

soup_tripadvisor = None

if 'tripadvisor_url' in locals() and tripadvisor_url:
    print(f"\nTentando raspar a página identificada: {tripadvisor_url}")
    soup_tripadvisor = scrape_restaurantes_info(tripadvisor_url)

    if soup_tripadvisor:
        print("HTML da página do Tripadvisor obtido com sucesso!")
        page_title_tag = soup_tripadvisor.find('title')
        if page_title_tag:
            print(f"Título da página: {page_title_tag.get_text(strip=True)}")
        else:
            print("Não foi possível encontrar o título da página.")


# Encontrar todos os blocos de restaurante
restaurant_blocks = soup_tripadvisor.find_all('div', class_=lambda c: c and 'XIWnB' in c)

if not restaurant_blocks:
    print("Tentando estratégia alternativa de seletores...")
    # Procura divs que contenham o link do título com a classe específica do seu HTML
    restaurant_blocks = [
        link.find_parent('div', class_='XIWnB') 
        for link in soup_tripadvisor.find_all('a', class_=lambda c: c and 'BMQDV' in c and 'ukgoS' in c)
        if link.find_parent('div', class_='XIWnB')
    ]

print(f"Blocos de restaurante encontrados: {len(restaurant_blocks)}")

top_n_restaurants = restaurant_blocks[:5]

print("Iniciando a extração detalhada de cada restaurante:")
restaurantes_detalhados = [] # Lista para armazenar os dados estruturados

for block in top_n_restaurants:

    nome_link_tag = block.find('a', class_=lambda c: c and 'BMQDV' in c and 'ukgos' in c)
    nome = "Nome não encontrado"
    if nome_link_tag:
        nome_div_tag = nome_link_tag.find('div', class_=lambda c: c and 'biGQs' in c and 'fiohW' in c)
        if nome_div_tag:
            nome = nome_div_tag.get_text(strip=True)

    reviews_tag = block.find('div', {'data-automation': 'bubbleReviewCount'})
    reviews = reviews_tag.find('span').get_text(strip=True) if reviews_tag and reviews_tag.find('span') else "Reviews não encontrado"

    rating_tag = block.find('div', {'data-automation': 'bubbleRatingValue'})
    rating = rating_tag.find('span').get_text(strip=True) if rating_tag and rating_tag.find('span') else "Avaliação não encontrada"

    culinaria_preco_div = block.find('div', class_=lambda c: c and 'ZvrsW' in c and 'biqBm' in c)
    
    tipo_culinaria = "Tipo de Culinária não encontrado"
    preco = "Preço não encontrado"

    if culinaria_preco_div:

        spans_info = culinaria_preco_div.find_all('span', class_=lambda c: c and 'biGQs' in c and 'pZUbB' in c)
        
        if len(spans_info) > 1:
            tipo_culinaria = spans_info[0].get_text(strip=True)

        for i in range(1, len(spans_info)):
            text = spans_info[i].get_text(strip=True)
            if '$' in text:
                preco = text
                break

    localizacao = "Localização não especificada (do nome)"
    if ' - ' in nome:
        partes_nome = nome.split(' - ')
        if len(partes_nome) > 1:
            localizacao = partes_nome[-1].strip()

    link = "Link não encontrado"
    if nome_link_tag and 'href' in nome_link_tag.attrs:
        link = "https://www.tripadvisor.com.br" + nome_link_tag['href']

    restaurantes_detalhados.append({
        "Nome": nome,
        "Avaliacao": rating,
        "Reviews": reviews,
        "Preco": preco,
        "Tipo Culinária": tipo_culinaria,
        "Localizacao": localizacao,
        "Link": link
    })


if restaurantes_detalhados:
    print(f"\n--- {len(restaurantes_detalhados)} Restaurantes Extraidos do Tripadvisor ---")
    for i, r in enumerate(restaurantes_detalhados):
        print(f"--- Restaurante #{i+1} ---")
        for key, value in r.items():
            print(f"{key}: {r[key]}")
        print("-" * 40)
else:
    print("Nenhum detalhe de restaurante foi extraido. **Verifique os seletores HTML no Bloco 4**.")