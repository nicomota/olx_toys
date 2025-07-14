from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import requests

# === CONFIGURAÇÕES ===
TOKEN = "XXXX"
CHAT_ID = "XXXXX"
FILTROS = ["toy story", "buzz", "woody"]
URL = "https://www.olx.com.br/brasil?q=toy+story&cg=9060"

def buscar_anuncios():
    print("🔍 Buscando anúncios...")

    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--log-level=3")
    options.add_argument("window-size=1920x1080")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36"
    )

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(URL)

    time.sleep(4)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    cards = soup.select("section.olx-adcard")
    print(f"🔎 {len(cards)} anúncios encontrados")

    anuncios = []
    for card in cards:
        a_tag = card.select_one("a.olx-adcard__link")
        h2_tag = card.select_one("h2")
        preco_tag = card.select_one("h3.olx-adcard__price")  # pega o preço
        img_tag = card.select_one("img")

        titulo = h2_tag.text.strip() if h2_tag else "Sem título"
        preco = preco_tag.text.strip() if preco_tag else "Preço não informado"
        href = a_tag.get("href", "") if a_tag else ""
        link = href if href.startswith("http") else f"https://www.olx.com.br{href}"
        imagem = img_tag.get("src", "") if img_tag else ""

        if any(filtro in titulo.lower() for filtro in FILTROS):
            anuncios.append({
                "titulo": titulo,
                "preco": preco,
                "link": link,
                "imagem": imagem
            })

    return anuncios

def enviar_telegram(anuncio):
    legenda = f"""
📢 *Novo anúncio encontrado!*

🧸 *{anuncio['titulo']}*
💰 {anuncio['preco']}
🔗 [Ver na OLX]({anuncio['link']})
"""
    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendPhoto",
        data={
            "chat_id": CHAT_ID,
            "photo": anuncio['imagem'] or "https://via.placeholder.com/300",
            "caption": legenda,
            "parse_mode": "Markdown"
        }
    )
    print(f"✅ Enviado: {anuncio['titulo']}")

def monitorar():
    enviados = set()
    print("📡 Iniciando monitoramento...\n")
    while True:
        try:
            anuncios = buscar_anuncios()
            for anuncio in anuncios:
                if anuncio['link'] not in enviados:
                    enviar_telegram(anuncio)
                    enviados.add(anuncio['link'])
        except Exception as e:
            print(f"⚠️ Erro no monitoramento: {e}")
        time.sleep(300)

if __name__ == "__main__":
    monitorar()
