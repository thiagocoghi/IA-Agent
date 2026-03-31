import os
import json
import holidays
import re
from pathlib import Path
from datetime import datetime, timedelta
from app.database.connection import supabase

# 1. Configuração de caminhos absoluta e robusta
CAMINHO_ATUAL = Path(__file__).resolve().parent
BASE_DIR = CAMINHO_ATUAL.parent.parent
FERIADOS_PATH = BASE_DIR / "data" / "feriados_municipais.json"


def carregar_feriados_municipais():
    try:
        if FERIADOS_PATH.exists():
            with open(FERIADOS_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        print(f"⚠️ Erro ao carregar feriados: {e}")
    return {}


def validar_regras_clinica(data_dt, hora_str):
    """Valida feriados e horários com limpeza rigorosa de strings."""
    estado_env = os.getenv("CLINICA_ESTADO", "SP").upper()
    cidade_env = os.getenv("CLINICA_CIDADE", "Sorocaba").strip().lower()
    dia_mes = data_dt.strftime("%m-%d")

    # Feriados Municipais
    feriados_municipais = carregar_feriados_municipais()
    feriados_norm = {k.lower(): v for k, v in feriados_municipais.items()}

    if cidade_env in feriados_norm:
        if dia_mes in feriados_norm[cidade_env]:
            nome_feriado = feriados_norm[cidade_env][dia_mes]
            return False, f"feriado municipal de {nome_feriado} (clínica fechada)"

    # Feriados Estaduais/Nacionais
    try:
        br_holidays = holidays.BR(subdiv=estado_env) if estado_env not in ["BR", "NACIONAL"] else holidays.BR()
    except:
        br_holidays = holidays.BR()

    if data_dt in br_holidays:
        return False, f"feriado de {br_holidays.get(data_dt)} (clínica fechada)"

    if data_dt.weekday() == 6:
        return False, "domingo (não abrimos)"

    # Trava de Horários
    try:
        hora_limpa = re.sub(r'[^0-9:]', '', hora_str).strip()
        if hora_limpa.count(':') >= 2:
            hora_limpa = ":".join(hora_limpa.split(':')[:2])
        if ":" not in hora_limpa:
            hora_limpa = f"{hora_limpa.zfill(2)}:00"

        hora_dt = datetime.strptime(hora_limpa[:5], "%H:%M").time()
        h9, h12, h18 = [datetime.strptime(t, "%H:%M").time() for t in ["09:00", "12:00", "18:00"]]

        if data_dt.weekday() == 5:  # Sábado
            if hora_dt >= h12 or hora_dt < h9:
                return False, "infelizmente sábado só atendemos até as 12:00"
        else:  # Semana
            if not (h9 <= hora_dt < h18):
                return False, "infelizmente atendemos apenas das 09h às 18h"
        return True, None
    except Exception:
        return False, "horário inválido"


def verificar_horarios_disponiveis(data_desejada: str):
    """Versão única e blindada com limpeza de Regex."""
    try:
        # Limpeza radical da string de data
        data_limpa = re.sub(r'[^0-9-]', '', data_desejada).strip()
        data_dt = datetime.strptime(data_limpa[:10], "%Y-%m-%d").date()

        aberto, motivo = validar_regras_clinica(data_dt, "09:00")
        if not aberto and "horário" not in motivo:
            return f"FECHADO: No dia {data_desejada} é {motivo}."

        res = supabase.table("agendamentos") \
            .select("data_hora") \
            .filter("data_hora", "gte", f"{data_limpa[:10]}T00:00:00.000Z") \
            .filter("data_hora", "lte", f"{data_limpa[:10]}T23:59:59.999Z") \
            .execute()

        horarios_base = ["09:00", "10:00", "11:00"] if data_dt.weekday() == 5 else [f"{h:02d}:00" for h in range(9, 18)]
        ocupados = [a['data_hora'].split('T')[1].strip()[:5] for a in res.data if 'T' in a['data_hora']]
        disponiveis = [h for h in horarios_base if h not in ocupados]

        if not disponiveis:
            return "LOTADO: Infelizmente não temos horários para este dia."
        return f"DISPONIVEL: Temos esses horários: {', '.join(disponiveis)}."
    except Exception as e:
        print(f"ERRO NO BOOKING_TOOLS: {e}")
        return "ERRO: Tive um problema técnico ao acessar a agenda."


def buscar_procedimentos(nome_termo: str = None):
    try:
        query = supabase.table("procedimentos").select("*")
        if nome_termo: query = query.ilike("nome", f"%{nome_termo}%")
        return query.execute().data
    except Exception as e:
        return f"Erro ao consultar procedimentos: {e}"


def buscar_profissionais():
    try:
        return supabase.table("profissionais").select("*").execute().data
    except Exception as e:
        return f"Erro ao consultar profissionais: {e}"


def criar_agendamento(nome_cliente: str, data_hora: str, procedimento_id: str, profissional_id: str = None):
    try:
        dt_obj = datetime.fromisoformat(data_hora.replace('Z', '+00:00'))
        aberto, motivo = validar_regras_clinica(dt_obj.date(), dt_obj.strftime("%H:%M"))
        if not aberto:
            return f"Ah! Infelizmente não conseguimos marcar nesse horário por conta de {motivo}. Vamos escolher outro?"

        if not profissional_id:
            prof = supabase.table("profissionais").select("id").limit(1).execute()
            if prof.data: profissional_id = prof.data[0]['id']

        data = {
            "cliente_nome": nome_cliente,
            "data_hora": data_hora,
            "procedimento_id": procedimento_id,
            "profissional_id": profissional_id,
            "status": "confirmado"
        }
        supabase.table("agendamentos").insert(data).execute()
        return f"Tudo pronto, {nome_cliente}! ✨ Horário confirmado."
    except Exception:
        return "Houve um probleminha ao salvar seu horário. Pode confirmar os dados?"


def sugerir_proximo_horario(data_falha_dt):
    if isinstance(data_falha_dt, str):  # Garantia caso venha string
        data_falha_dt = datetime.strptime(re.sub(r'[^0-9-]', '', data_falha_dt)[:10], "%Y-%m-%d").date()

    proxima_data = data_falha_dt + timedelta(days=1)
    if proxima_data.weekday() == 6: proxima_data += timedelta(days=1)

    valido, _ = validar_regras_clinica(proxima_data, "09:00")
    if not valido: return sugerir_proximo_horario(proxima_data)
    return proxima_data.strftime("%d/%m (%A)")