import os
import requests
import re
from fastapi import FastAPI, Request
from dotenv import load_dotenv
from app.agents.assistant import agente

load_dotenv()

app = FastAPI()

# Configurações Z-API
ZAPI_ID = os.getenv("ZAPI_INSTANCE_ID")
ZAPI_TOKEN = os.getenv("ZAPI_INSTANCE_TOKEN")
ZAPI_CLIENT = os.getenv("ZAPI_CLIENT_TOKEN")

# Print de verificação (QA Debug)
print(f"🚀 Iniciando com Instância: {ZAPI_ID}")


@app.post("/webhook/zapi")
async def webhook_zapi(request: Request):
    data = await request.json()

    # 1. Filtro de Segurança / Loop (Z-API usa 'fromMe')
    if data.get("fromMe") is True:
        return {"status": "ignored"}

    try:
        # 2. Extração de Dados (Estrutura Correta da Z-API)
        remote_jid = data.get("phone")
        # A Z-API envia o texto dentro de 'text' -> 'message'
        user_message = data.get("text", {}).get("message")

        if user_message and remote_jid:
            print(f"📩 Mensagem de {remote_jid}: {user_message}")

            # 🧠 CHAMA O AGENTE (Passando o ID para a Memória de Chat funcionar)
            bot_response = agente.responder(remote_jid, user_message)

            # --- LÓGICA DE MÍDIA (Antes e Depois) ---
            # Procura por URLs de imagem na resposta da IA
            urls = re.findall(r'(https?://[^\s]+\.(?:jpg|jpeg|png|gif|webp))', bot_response)

            headers = {
                "client-token": ZAPI_CLIENT,
                "Content-Type": "application/json"
            }

            if urls:
                for url in urls:
                    img_url = f"https://api.z-api.io/instances/{ZAPI_ID}/token/{ZAPI_TOKEN}/send-image"
                    img_payload = {
                        "phone": remote_jid,
                        "image": url,
                        "caption": "Dá uma olhadinha nesse resultado incrível! ✨"
                    }
                    requests.post(img_url, json=img_payload, headers=headers)

                # Remove a URL do texto final para o chat ficar limpo
                bot_response = re.sub(r'(https?://[^\s]+\.(?:jpg|jpeg|png|gif|webp))', '', bot_response)

            print(f"🤖 Bella respondeu: {bot_response}")
            # 📡 3. ENVIO DO TEXTO FINAL VIA Z-API
            send_url = f"https://api.z-api.io/instances/{ZAPI_ID}/token/{ZAPI_TOKEN}/send-text"
            payload = {"phone": remote_jid, "message": bot_response.strip()}

            res = requests.post(send_url, json=payload, headers=headers)
            print(f"📡 Status Z-API: {res.status_code}")

        return {"status": "success"}

    except Exception as e:
        print(f"⚠️ Erro no processamento: {e}")
        return {"status": "error"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=5000)