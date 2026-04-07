# 🌸 Bella: AI-Driven Booking Agent
> **Agente de Inteligência Artificial para Automação de Clínicas de Estética.**

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-009688.svg)](https://fastapi.tiangolo.com/)
[![Supabase](https://img.shields.io/badge/Supabase-Database-3ECF8E.svg)](https://supabase.com/)
[![Gemini](https://img.shields.io/badge/Google-Gemini_2.5-4285F4.svg)](https://ai.google.dev/)
[![Tests](https://img.shields.io/badge/Pytest-Passing-green.svg)](https://docs.pytest.org/)

A **Bella** não é apenas um chatbot; é uma assistente executiva que integra **LLMs (Large Language Models)** com APIs de mensageria e bancos de dados relacionais para transformar conversas de WhatsApp em agendamentos reais.

---

## 🎯 O Diferencial do Projeto
Diferente de fluxos de bot engessados, a Bella utiliza **RAG (Retrieval-Augmented Generation)** para consultar procedimentos e horários em tempo real, garantindo respostas dinâmicas, humanas e precisas.

### 🌟 Funcionalidades Principais
- **🧠 Agente Cognitivo:** Identifica intenções, trata desvios de assunto (papo furado) e mantém o foco na conversão de agendamento.
- **📅 Gestão de Agenda E2E:** Consulta disponibilidade, identifica conflitos de horário e realiza a reserva no Supabase.
- **🖼️ Smart Media Delivery:** Envia fotos de resultados (antes/depois) de forma contextualizada, utilizando legendas inteligentes via Z-API.
- **🕒 Inteligência Temporal:** Converte termos naturais ("amanhã às 10h") em objetos de data ISO-8601 para validação no banco de dados.

---

## 🏗️ Arquitetura e Fluxo de Dados

O sistema opera em um ciclo fechado onde a IA atua como o orquestrador entre o usuário e o banco de dados:

1. **Entrada:** Mensagem via WhatsApp -> Gatilho Webhook Z-API.
2. **Processamento:** FastAPI roteia para o Agente (LangChain/Gemini).
3. **Ação:** O Agente decide se precisa consultar o Supabase ou responder ao usuário.
4. **Saída:** Resposta formatada (Texto ou Imagem+Legenda) enviada via Z-API.

---

## 🧪 Quality Assurance (QA)
Como foco em estabilidade e confiabilidade, o projeto foi desenvolvido sob a ótica de testes rigorosos:

- **Integration Tests:** Validação do fluxo de conversa completo e lógica de ferramentas.
- **Error Handling:** Tratamento de falhas de conexão e dados ausentes.
- **Logs de Execução:** Monitoramento detalhado de cada interação do Agente no terminal.

**Para rodar a suíte de testes:**
```powershell
python -m pytest tests/test_agent.py -s
```

## 🛠️ Configuração Técnica
Instalação
Clone o repositório:
```Bash
git clone [https://github.com/seu-usuario/bella-ai-agent.git](https://github.com/seu-usuario/bella-ai-agent.git)
```

Instale as dependências:

```Bash
pip install -r requirements.txt
```

Configure o .env seguindo o modelo:
```Code snippet
GEMINI_API_KEY=sua_chave
SUPABASE_URL=sua_url
SUPABASE_KEY=sua_key
ZAPI_INSTANCE_ID=id_instancia
ZAPI_INSTANCE_TOKEN=token_instancia
ZAPI_CLIENT_TOKEN=token_cliente
```
### 📂 Estrutura do Projeto
```
Plaintext
├── app/
│   ├── agents/      # Lógica do Agente e Instruções de Sistema
│   ├── core/        # Configurações de ambiente (Pydantic Settings)
│   ├── database/    # Conexão e Queries do Supabase
│   ├── tools/       # Funções executáveis pela IA (Busca, Agendamento)
│   └── main.py      # Entrypoint FastAPI & Lógica de Webhooks
├── tests/           # Suíte de testes automatizados (Pytest)
└── requirements.txt # Lista de dependências do projeto
```

### 🚀 Roadmap de Evolução
- [x] Dashboard Admin: Painel Web para a clínica gerenciar ou cancelar horários manualmente.

- [ ] Google Calendar Sync: Sincronização automática com a agenda do Google.

- [ ] Notifications: Envio automático de lembretes de agendamento 24h antes.

### 👨‍💻 Desenvolvedor
Thiago Coghi - QA Automation Engineer 🚀
