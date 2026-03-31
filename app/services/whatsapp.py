import os
import re
import requests
import logging


def enviar_mensagem_whatsapp(numero, bot_response):
    """
    Analisa a resposta do bot, identifica se há imagens e envia
    pelo método correto da Z-API.
    """
    # Configurações
    ZAPI_ID = os.getenv("ZAPI_INSTANCE_ID")
    ZAPI_TOKEN = os.getenv("ZAPI_INSTANCE_TOKEN")
    ZAPI_CLIENT = os.getenv("ZAPI_CLIENT_TOKEN")

    headers = {
        "client-token": ZAPI_CLIENT,
        "Content-Type": "application/json"
    }
    base_url = f"https://api.z-api.io/instances/{ZAPI_ID}/token/{ZAPI_TOKEN}"

    # Regex para identificar URLs de imagem
    urls = re.findall(r'(https?://[^\s]+\.(?:jpg|jpeg|png|gif|webp))', bot_response)

    try:
        if urls:
            # LÓGICA DE IMAGEM
            url_para_envio = urls[0]
            # Remove o link do texto para a legenda ficar limpa
            texto_legenda = re.sub(r'(https?://[^\s]+\.(?:jpg|jpeg|png|gif|webp))', '', bot_response).strip()

            payload = {
                "phone": numero,
                "image": url_para_envio,
                "caption": texto_legenda if texto_legenda else "Olha só! ✨"
            }
            endpoint = f"{base_url}/send-image"
        else:
            # LÓGICA DE TEXTO PURO
            payload = {
                "phone": numero,
                "message": bot_response.strip()
            }
            endpoint = f"{base_url}/send-text"

        res = requests.post(endpoint, json=payload, headers=headers)
        logging.info(f"🤖 Resposta enviada. Status Z-API: {res.status_code}")
        return res.status_code

    except Exception as e:
        logging.error(f"❌ Erro ao conectar com Z-API: {e}")
        return None