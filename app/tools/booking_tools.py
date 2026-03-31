import os
import json
import holidays
from pathlib import Path
from datetime import datetime
from app.database.connection import supabase

# Configuração de caminhos para o JSON
BASE_DIR = Path(__file__).parent
FERIADOS_PATH = BASE_DIR / "feriados_municipais.json"


def carregar_feriados_municipais():
    """Lê o arquivo JSON de feriados locais."""
    try:
        if FERIADOS_PATH.exists():
            with open(FERIADOS_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        print(f"⚠️ Erro ao carregar feriados municipais: {e}")
    return {}


def validar_regras_clinica(data_dt, hora_str):
    """
    Valida feriados (JSON Municipal + Biblioteca Estadual/Nacional) e horários.
    """
    # 1. Configurações de Localização do Ambiente
    estado_env = os.getenv("CLINICA_ESTADO", "SP").upper()
    cidade_env = os.getenv("CLINICA_CIDADE", "Sorocaba").lower()
    dia_mes = data_dt.strftime("%m-%d")

    # 2. Validação de Feriados Municipais (Via JSON)
    feriados_municipais = carregar_feriados_municipais()
    if cidade_env in feriados_municipais:
        # Verifica se o dia atual está no mapeamento daquela cidade
        if dia_mes in feriados_municipais[cidade_env]:
            nome_feriado = feriados_municipais[cidade_env][dia_mes]
            return False, f"feriado municipal de {nome_feriado} (clínica fechada)"

    # 3. Validação de Feriados Estaduais/Nacionais (Biblioteca Holidays)
    try:
        if estado_env in ["BR", "NACIONAL"]:
            br_holidays = holidays.BR()
        else:
            br_holidays = holidays.BR(subdiv=estado_env)
    except:
        br_holidays = holidays.BR()

    if data_dt in br_holidays:
        return False, f"feriado de {br_holidays.get(data_dt)} (clínica fechada)"

    # 4. Trava de Domingos
    if data_dt.weekday() == 6:
        return False, "domingo (não abrimos)"

    # 5. Trava de Horários
    try:
        # Normalização da string de hora (ex: "10h" -> "10:00")
        hora_limpa = hora_str.lower().replace("h", ":").split()[0]
        if ":" not in hora_limpa: hora_limpa += ":00"

        hora_dt = datetime.strptime(hora_limpa, "%H:%M").time()

        h9 = datetime.strptime("09:00", "%H:%M").time()
        h12 = datetime.strptime("12:00", "%H:%M").time()
        h18 = datetime.strptime("18:00", "%H:%M").time()

        if data_dt.weekday() == 5:  # Sábado
            if hora_dt >= h12 or hora_dt < h9:
                return False, "infelizmente sábado só atendemos até as 12:00"
        else:  # Semana
            if not (h9 <= hora_dt < h18):
                return False, "infelizmente atendemos apenas das 09h às 18h"

        return True, None
    except Exception:
        return False, "horário inválido"


def buscar_procedimentos(nome_termo: str = None):
    """Mantém a lógica original de busca por termo ou listagem total."""
    try:
        query = supabase.table("procedimentos").select("*")
        if nome_termo:
            query = query.ilike("nome", f"%{nome_termo}%")
        res = query.execute()
        return res.data
    except Exception as e:
        return f"Puxa, não consegui consultar os procedimentos agora: {e}"


def buscar_profissionais():
    """Mantém a listagem original de profissionais."""
    try:
        res = supabase.table("profissionais").select("*").execute()
        return res.data
    except Exception as e:
        return f"Não consegui ver nossos profissionais disponíveis: {e}"


def verificar_horarios_disponiveis(data_desejada: str):
    try:
        # Converte a string para objeto date
        data_dt = datetime.strptime(data_desejada, "%Y-%m-%d").date()

        # Validação de feriado/domingo ANTES de ir no banco
        # Usamos um horário padrão (09:00) apenas para checar se o dia está aberto
        aberto, motivo = validar_regras_clinica(data_dt, "09:00")

        if not aberto and "horário" not in motivo:
            # Retorno claro para a Bella humanizar
            return f"FECHADO: No dia {data_desejada} é {motivo}."

        # Busca agendamentos (Ajuste de fuso horário para o Supabase)
        res = supabase.table("agendamentos") \
            .select("data_hora") \
            .filter("data_hora", "gte", f"{data_desejada}T00:00:00.000Z") \
            .filter("data_hora", "lte", f"{data_desejada}T23:59:59.999Z") \
            .execute()

        # Lógica de horários disponíveis
        horarios_base = ["09:00", "10:00", "11:00"] if data_dt.weekday() == 5 else [f"{h:02d}:00" for h in range(9, 18)]

        # Limpa o 'Z' ou '+00:00' para comparar strings de hora
        ocupados = []
        for a in res.data:
            hora_limpa = a['data_hora'].split('T')[1][:5]
            ocupados.append(hora_limpa)

        disponiveis = [h for h in horarios_base if h not in ocupados]

        if not disponiveis:
            return "LOTADO: Infelizmente não temos horários para este dia."

        return f"DISPONIVEL: Temos esses horários: {', '.join(disponiveis)}."

    except Exception as e:
        # Se cair aqui, o teste falha com a mensagem de "probleminha"
        print(f"ERRO NO BOOKING_TOOLS: {e}")  # Para você ver no console do PyCharm
        return "ERRO: Tive um problema técnico ao acessar a agenda."


def criar_agendamento(nome_cliente: str, data_hora: str, procedimento_id: str, profissional_id: str = None):
    """
    Reintegra a lógica original de fallback para profissional_id
    e mantém a validação final de segurança.
    """
    try:
        # Normalização e Validação final (Segurança de QA)
        dt_obj = datetime.fromisoformat(data_hora.replace('Z', '+00:00'))
        aberto, motivo = validar_regras_clinica(dt_obj.date(), dt_obj.strftime("%H:%M"))

        if not aberto:
            return f"Ah! Infelizmente não conseguimos marcar nesse horário por conta de {motivo}. Vamos escolher outro?"

        # Lógica Original: Se não informou profissional, pega o primeiro disponível
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
        return f"Tudo pronto, {nome_cliente}! ✨ Seu horário está confirmadíssimo. Mal podemos esperar para te receber!"

    except Exception as e:
        return "Houve um probleminha ao salvar seu horário, mas não desiste de mim! Pode confirmar os dados uma última vez? 💖"