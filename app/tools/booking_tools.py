from app.database.connection import supabase
from datetime import datetime


def buscar_procedimentos(nome_termo: str = None):
    """Busca procedimentos no banco de dados, incluindo imagem_url."""
    try:
        query = supabase.table("procedimentos").select("*")
        if nome_termo:
            query = query.ilike("nome", f"%{nome_termo}%")
        res = query.execute()
        return res.data
    except Exception as e:
        return f"Erro ao buscar procedimentos: {e}"


def buscar_profissionais():
    """Retorna a lista de especialistas da clínica."""
    try:
        res = supabase.table("profissionais").select("*").execute()
        return res.data
    except Exception as e:
        return f"Erro ao buscar profissionais: {e}"


def verificar_horarios_disponiveis(data_desejada: str):
    """Consulta horários livres para uma data (YYYY-MM-DD)."""
    try:
        # Busca todos os agendamentos do dia para comparar
        res = supabase.table("agendamentos") \
            .select("data_hora") \
            .filter("data_hora", "gte", f"{data_desejada}T00:00:00+00:00") \
            .filter("data_hora", "lte", f"{data_desejada}T23:59:59+00:00") \
            .execute()

        # Extrai apenas a HORA:MINUTO para comparar
        ocupados = []
        for a in res.data:
            dt = datetime.fromisoformat(a['data_hora'].replace('Z', '+00:00'))
            ocupados.append(dt.strftime("%H:%M"))

        # Horários de atendimento da clínica
        horarios_clinica = ["08:00", "09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00"]
        disponiveis = [h for h in horarios_clinica if h not in ocupados]

        if not disponiveis:
            return f"Infelizmente não temos horários para {data_desejada}. Poderia sugerir outro dia?"

        return f"Horários disponíveis para {data_desejada}: {', '.join(disponiveis)}"
    except Exception as e:
        return f"Erro ao consultar agenda: {e}"


def criar_agendamento(nome_cliente: str, data_hora: str, procedimento_id: str, profissional_id: str = None):
    """Grava o agendamento final no banco de dados."""
    try:
        # Se não vier profissional, busca o primeiro ID disponível
        if not profissional_id:
            prof = supabase.table("profissionais").select("id").limit(1).execute()
            if prof.data:
                profissional_id = prof.data[0]['id']

        data = {
            "cliente_nome": nome_cliente,
            "data_hora": data_hora,
            "procedimento_id": procedimento_id,
            "profissional_id": profissional_id,
            "status": "confirmado"
        }
        supabase.table("agendamentos").insert(data).execute()
        return "✅ Agendamento realizado com sucesso! Mal podemos esperar para te ver!"
    except Exception as e:
        return f"❌ Erro ao gravar: {e}"