import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


@pytest.mark.parametrize("mensagem_usuario, resposta_bot, tem_imagem", [
    ("Olá", "Olá! Sou a Bella. Como posso ajudar?", False),
    ("O que é peeling?", "O Peeling é ótimo! Veja: https://site.com/foto.jpg", True),
    ("Quero pizza", "Adoro pizza, mas aqui focamos em beleza! ✨", False)
])
def test_fluxo_completo_webhook_para_whatsapp(mensagem_usuario, resposta_bot, tem_imagem):
    """
    Testa se o Webhook recebe a mensagem, o agente responde e
    o serviço de WhatsApp envia o payload correto.
    """

    # 1. Mockamos o Agente (Bella) para não gastar tokens do Gemini
    # 2. Mockamos o requests.post para não enviar mensagem real para a Z-API
    with patch("app.agents.assistant.agente.responder") as mock_bella, \
            patch("requests.post") as mock_post:

        # Configuramos a resposta que a Bella vai dar
        mock_bella.return_value = resposta_bot

        # Configuramos o retorno do POST da Z-API (Simulando sucesso 200)
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"status": "success"}

        # Simula o JSON que a Z-API envia para o seu Webhook
        payload_webhook = {
            "fromMe": False,
            "phone": "5515991555763",
            "text": {"message": mensagem_usuario}
        }

        # 3. Dispara a requisição para o seu FastAPI
        response = client.post("/webhook/zapi", json=payload_webhook)

        # --- ASSERTS DE QA ---

        # Garante que o endpoint respondeu OK
        assert response.status_code == 200

        # Verifica se o método de envio correto foi chamado na Z-API
        call_args = mock_post.call_args[0][0]  # Pega a URL chamada

        if tem_imagem:
            assert "send-image" in call_args, "Deveria ter chamado o endpoint de imagem"
            # Verifica se a URL da imagem foi extraída do texto e enviada no JSON
            json_enviado = mock_post.call_args[1]['json']
            assert "image" in json_enviado
            assert "https://" in json_enviado["image"]
        else:
            assert "send-text" in call_args, "Deveria ter chamado o endpoint de texto"