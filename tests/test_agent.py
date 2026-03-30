import pytest
from app.agents.assistant import agente


def test_fluxo_procedimentos():
    """Valida se a Bella lista os procedimentos corretamente."""
    pergunta = "Quais procedimentos vocês fazem?"
    resposta = agente.responder("user_test_123", pergunta)

    # Validações de QA
    assert "Botox" in resposta or "Preenchimento" in resposta
    assert "R$" in resposta or "valor" in resposta.lower()
    print("\n✅ Teste de listagem de procedimentos: PASSOU")


def test_envio_imagem_url():
    """Valida se a URL da imagem está presente na resposta quando solicitada."""
    pergunta = "Me mostra foto do Botox"
    resposta = agente.responder("user_test_123", pergunta)

    # Verifica se existe um padrão de URL de imagem na resposta
    assert "http" in resposta
    assert ".jpg" in resposta or ".png" in resposta or "gstatic" in resposta
    print("✅ Teste de verificação de mídia: PASSOU")


def test_agendamento_lotado():
    """Valida se a Bella reconhece quando não há horários (Baseado no seu bloqueio SQL)."""
    # Testando para uma data que sabemos que você lotou no SQL
    data_lotada = "2026-03-30"
    pergunta = f"Tem horário para o dia {data_lotada} às 10:00?"
    resposta = agente.responder("user_test_123", pergunta)

    assert "Infelizmente" in resposta or "lotada" in resposta or "não temos" in resposta
    print("✅ Teste de lógica de agenda lotada: PASSOU")