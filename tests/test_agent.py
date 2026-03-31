import pytest
import os
from app.agents.assistant import agente
from app.core.config import settings


# --- FIXTURES PARA REUTILIZAÇÃO ---

@pytest.fixture
def mock_env_location(monkeypatch):
    """Auxiliar para injetar localização dinamicamente nos testes."""

    def _set_location(estado="SP", cidade="Sorocaba"):
        monkeypatch.setenv("CLINICA_ESTADO", estado)
        monkeypatch.setenv("CLINICA_CIDADE", cidade)

    return _set_location


# --- TESTES DE INFRAESTRUTURA ---

def test_debug_env():
    """Valida se o ambiente de teste tem acesso às chaves necessárias."""
    assert settings.SUPABASE_URL, "Erro: SUPABASE_URL não encontrada no .env do Pytest"
    assert settings.SUPABASE_KEY, "Erro: SUPABASE_KEY não encontrada no .env do Pytest"
    print(f"\n✅ Infra OK: Conectado a {settings.SUPABASE_URL}")


# --- TESTES DE CONTEÚDO E MÍDIA ---

def test_fluxo_procedimentos():
    """Valida se a IA lista os serviços principais."""
    pergunta = "Quais procedimentos vocês fazem?"
    resposta = agente.responder("user_test_123", pergunta)

    servicos_esperados = ["Botox", "Limpeza", "Peeling"]
    assert any(x in resposta for x in servicos_esperados), "IA não listou os procedimentos core."


def test_envio_imagem_url():
    """Verifica se a entrega de mídia (URLs) está funcional."""
    pergunta = "Me mostra foto do Botox"
    resposta = agente.responder("user_test_123", pergunta)

    assert "http" in resposta, "URL de imagem não encontrada na resposta."
    assert any(ext in resposta.lower() for ext in [".jpg", ".png", "gstatic"]), "Formato de imagem inválido."


# --- TESTES DE REGRA DE NEGÓCIO NACIONAL (O MOTOR DO AGENTE) ---

@pytest.mark.parametrize("estado, cidade, data_feriado, nome_feriado", [
    ("SP", "Sorocaba", "2026-08-15", "Aniversário de Sorocaba"),
    ("RJ", "Rio de Janeiro", "2026-04-23", "Dia de São Jorge"),
    ("RS", "Porto Alegre", "2026-09-20", "Revolução Farroupilha"),
    ("BR", "Nacional", "2026-12-25", "Natal")
])
def test_resiliencia_feriados_nacionais(estado, cidade, data_feriado, nome_feriado, mock_env_location):
    """
    Testa se a Bella bloqueia agendamentos em feriados de diferentes regiões.
    Garante escalabilidade para venda nacional do produto.
    """
    mock_env_location(estado, cidade)

    pergunta = f"Quero agendar para o dia {data_feriado} às 10h"
    resposta = agente.responder("test_user_nacional", pergunta)

    print(f"\n[TESTE {cidade}] Resposta: {resposta}")

    # Falha o teste se a IA der erro de sistema (Problema no código ou banco)
    if "erro ao consultar" in resposta.lower() or "erro no sistema" in resposta.lower():
        pytest.fail(f"🔴 ERRO TÉCNICO: A função quebrou em {cidade}. Verifique o booking_tools.py")

    # Garante que ela NÃO confirmou o agendamento
    negativas = ["não temos", "infelizmente", "fechada", "feriado", "indisponível", "comemoramos"]
    agendou_indevidamente = "confirmado" in resposta.lower() or "agendado" in resposta.lower()

    assert not agendou_indevidamente, f"❌ FALHA CRÍTICA: IA agendou em pleno feriado de {nome_feriado}!"
    assert any(word in resposta.lower() for word in negativas), f"IA não foi clara ao negar o feriado de {nome_feriado}"


def test_regra_horario_limite_sabado(mock_env_location):
    """Valida a trava de horário diferenciado para sábados (até 12h)."""
    mock_env_location("SP", "Sorocaba")

    # Sábado, 04/04/2026 às 15:00 (Fora do horário)
    pergunta = "Agendar para sábado dia 2026-04-04 às 15:00"
    resposta = agente.responder("user_test_qa", pergunta)

    assert any(word in resposta.lower() for word in ["fechada", "12:00", "horário", "infelizmente"]), \
        "IA permitiu agendamento no sábado à tarde (deveria estar fechado)."

def test_proatividade_feriado(mock_env_location):
        mock_env_location("SP", "Sorocaba")
        pergunta = "Quero agendar para 15/08 às 10h"
        resposta = agente.responder("user_teste", pergunta)

        # O teste agora exige que ela ofereça uma alternativa
        assert "Infelizmente" in resposta
        assert any(palavra in resposta.lower() for palavra in ["próximo", "sugerir", "que tal", "posso", "segunda"])
        print(f"Bella Proativa: {resposta}")