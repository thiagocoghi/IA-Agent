import sys
import os
from datetime import datetime
import streamlit as st
import pandas as pd

# Mantendo sua lógica de conexão
from app.database.connection import supabase

# Configuração da página (Layout Wide para melhor visualização em desktops de recepção)
st.set_page_config(page_title="Bella Admin - Gestão de Clínica", page_icon="🌸", layout="wide")

# --- BLOCO DE PERSONALIZAÇÃO DE CORES (CSS) ---
st.markdown("""
    <style>
    /* 1. FUNDO DA PÁGINA */
    .stApp { 
        background-color: #fffafb; /* Cor do fundo geral (Rosa quase branco) */
    }

    /* 2. TEXTOS GERAIS (PARÁGRAFOS E TEXTOS PADRÃO) */
    html, body, [class*="st-"] {
        color: #aaaaaa !important; /* Cor da fonte principal (Marrom café) */
    }

    /* 3. TÍTULOS (H1, H2, H3) */
    h1, h2, h3 { 
        color: #854d5d !important; /* Cor dos títulos (Rosa queimado) */
        font-weight: 700 !important;
    }

    /* 4. TABELA DE AGENDAMENTOS */
    [data-testid="stTable"] {
        background-color: #ffffff !important; /* Fundo da tabela (Branco puro) */
        color: #1a1a1a !important;            /* Cor do texto dentro da tabela (Preto suave) */
    }

    /* Cores das células individuais e cabeçalho da tabela */
    [data-testid="stTable"] td, [data-testid="stTable"] th {
        color: #1a1a1a !important; /* Garante que o texto das células seja legível */
        border-bottom: 1px solid #f0f0f0; /* Cor da linha divisória da tabela */
    }

    /* 5. MÉTRICAS (AQUELES NÚMEROS NO TOPO) */
    [data-testid="stMetricValue"] {
        color: #c26d82 !important; /* Cor do número grande */
    }
    [data-testid="stMetricLabel"] {
        color: #4a2c34 !important; /* Cor da legenda da métrica */
    }

    /* 6. BOTÕES */
    .stButton>button {
        background-color: #ffb7c5; /* Cor de fundo do botão (Rosa pastel) */
        color: #aaaaaa !important;  /* Cor do texto dentro do botão */
        border-radius: 20px;       /* Arredondamento das bordas */
        font-weight: bold;
    }

    /* Cor do botão quando você passa o mouse por cima (Hover) */
    .stButton>button:hover {
        background-color: #ff8fa3; /* Rosa mais forte ao passar o mouse */
        color: #ffffff !important;  /* Texto muda para branco ao passar o mouse */
    }

    /* 7. CAIXAS DE EXPANSÃO E SELECTBOX */
    .stSelectbox div[data-baseweb="select"] {
        background-color: white;
        color: #4a2c34;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CABEÇALHO ---
col_logo, col_titulo = st.columns([1, 6])
with col_titulo:
    st.title("🌸 Painel da Bella")
    st.caption("Central de Agendamentos e Gestão de Clientes")

# --- BARRA LATERAL ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3460/3460335.png", width=100)  # Ícone ilustrativo
    st.header("📅 Agenda")
    data_filtro = st.date_input("Filtrar por dia:", datetime.now())
    st.divider()
    st.info("💡 Dica: Clique no botão cancelar para liberar horários na agenda automaticamente.")


# --- FUNÇÃO DE BUSCA ---
def get_agendamentos(data_alvo):
    data_str = data_alvo.strftime("%Y-%m-%d")
    res = supabase.table("agendamentos") \
        .select("id, cliente_nome, data_hora, status, procedimentos(nome)") \
        .filter("data_hora", "gte", f"{data_str}T00:00:00") \
        .filter("data_hora", "lte", f"{data_str}T23:59:59") \
        .order("data_hora") \
        .execute()
    return res.data


# --- LÓGICA PRINCIPAL ---
agendamentos = get_agendamentos(data_filtro)

if agendamentos:
    # Preparação dos dados para exibição humana
    for a in agendamentos:
        a['Procedimento'] = a['procedimentos']['nome'] if a['procedimentos'] else "Não definido"
        a['Horário'] = a['data_hora'].split('T')[1][:5]
        a['Paciente'] = a['cliente_nome'].title()  # Nome com primeira letra maiúscula
        # Tradução de status para a secretária
        status_map = {
            "confirmado": "✅ Confirmado",
            "pendente": "⏳ Pendente",
            "cancelado_secretaria": "🚫 Cancelado"
        }
        a['Status'] = status_map.get(a['status'], a['status'].capitalize())

    df = pd.DataFrame(agendamentos)

    # Exibição de Métricas Simples
    m1, m2, m3 = st.columns(3)
    m1.metric("Total de Clientes", len(df))
    m2.metric("Confirmados", len(df[df['status'] == 'confirmado']))
    m3.metric("Cancelados", len(df[df['status'] == 'cancelado_secretaria']))

    st.subheader(f"Lista de Atendimentos - {data_filtro.strftime('%d/%m/%Y')}")

    # Seleção de colunas que interessam ao humano
    df_visual = df[['Horário', 'Paciente', 'Procedimento', 'Status']]
    st.table(df_visual)

    # --- ÁREA DE AÇÕES ---
    st.divider()
    with st.expander("🛠️ Gerenciar ou Cancelar Horários", expanded=True):
        col_sel, col_btn = st.columns([3, 1])

        with col_sel:
            # Em vez de ID puro, mostramos Hora + Nome para facilitar a escolha
            agendamento_escolhido = st.selectbox(
                "Selecione o paciente:",
                options=agendamentos,
                format_func=lambda x: f"{x['Horário']} - {x['Paciente']} ({x['Procedimento']})"
            )

        with col_btn:
            st.write("Confirmar Ação")
            if st.button("🚫 Cancelar Agora", use_container_width=True):
                with st.spinner("Atualizando agenda..."):
                    supabase.table("agendamentos") \
                        .update({"status": "cancelado_secretaria"}) \
                        .eq("id", agendamento_escolhido['id']) \
                        .execute()

                    st.toast(f"Agenda de {agendamento_escolhido['Paciente']} atualizada!", icon="🌸")
                    st.rerun()

else:
    st.info(f"Não há agendamentos registrados para o dia {data_filtro.strftime('%d/%m/%Y')}.")
    st.image(
        "https://img.freepik.com/vetores-premium/uma-garota-bonita-com-flores-no-cabelo-estilo-plano-ilustracao-vetorial_515282-3.jpg",
        width=200)