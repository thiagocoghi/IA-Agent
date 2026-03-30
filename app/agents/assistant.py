import os
import traceback  # Para ver a linha exata do erro
from google import genai
from dotenv import load_dotenv
from app.tools.booking_tools import (
    buscar_procedimentos,
    buscar_profissionais,
    verificar_horarios_disponiveis,
    criar_agendamento
)
from app.agents.prompts import get_system_prompt_clinica

load_dotenv()


class ClinicaAgent:
    def __init__(self):
        self.client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
        self.model_id = "gemini-2.5-flash"

        # 🔧 Ferramentas
        self.tools = [
            buscar_procedimentos,
            buscar_profissionais,
            verificar_horarios_disponiveis,
            criar_agendamento
        ]

        self.sessions = {}

    def responder(self, user_id: str, mensagem_usuario: str) -> str:
        try:
            # 1. Recupera ou cria a sessão
            if user_id not in self.sessions:
                prompt_sistema = get_system_prompt_clinica()

                # Criamos a config separada para garantir clareza
                chat_config = {
                    'system_instruction': prompt_sistema,
                    'tools': self.tools,
                    'temperature': 0.7
                }

                self.sessions[user_id] = self.client.chats.create(
                    model=self.model_id,
                    config=chat_config
                )

            chat_session = self.sessions[user_id]

            # 2. Envio da mensagem
            response = chat_session.send_message(mensagem_usuario)

            if response and response.text:
                return response.text

            return "🌸 Olá! Sou a Bella. Como posso ajudar com sua estética hoje?"

        except Exception as e:
            # 🔥 ISSO É O QUE PRECISAMOS VER NO SEU TERMINAL:
            print(f"❌ ERRO IDENTIFICADO PELO QA:")
            traceback.print_exc()

            if user_id in self.sessions:
                del self.sessions[user_id]

            return "🌸 Oi! Sou a Bella. Tive um pequeno soluço, mas já estou aqui! Como posso te ajudar com nossos procedimentos de beleza? 😊"


agente = ClinicaAgent()

# import os
# import traceback
# from google import genai
# from dotenv import load_dotenv
# # Importamos mas não vamos usar no 'tools' por enquanto para testar
# from app.tools.booking_tools import buscar_procedimentos, buscar_profissionais, verificar_horarios_disponiveis, \
#     criar_agendamento
# from app.agents.prompts import get_system_prompt_clinica
#
# load_dotenv()
#
#
# class ClinicaAgent:
#     def __init__(self):
#         self.client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
#         # IMPORTANTE: Garanta que o modelo seja exatamente este ou 'gemini-1.5-flash'
#         self.model_id = "gemini-2.5-flash"
#         self.sessions = {}
#
#     def responder(self, user_id: str, mensagem_usuario: str) -> str:
#         try:
#             if user_id not in self.sessions:
#                 prompt_sistema = get_system_prompt_clinica()
#
#                 # TESTE: Estamos rodando SEM as tools para isolar o erro
#                 chat_config = {
#                     'system_instruction': prompt_sistema,
#                     'tools': [],  # <--- DEIXE VAZIO PARA TESTAR
#                     'temperature': 0.7
#                 }
#
#                 self.sessions[user_id] = self.client.chats.create(
#                     model=self.model_id,
#                     config=chat_config
#                 )
#
#             chat_session = self.sessions[user_id]
#             response = chat_session.send_message(mensagem_usuario)
#
#             if response and response.text:
#                 return response.text
#             return "🌸 Olá! Sou a Bella. Como posso ajudar?"
#
#         except Exception as e:
#             # 🕵️ OLHE O SEU TERMINAL AGORA!
#             # O erro real vai aparecer entre estas linhas:
#             print("\n" + "=" * 50)
#             print("❌ ERRO REAL CAPTURADO PELO QA:")
#             traceback.print_exc()
#             print("=" * 50 + "\n")
#
#             if user_id in self.sessions:
#                 del self.sessions[user_id]
#             return "🌸 Erro persistente. Verifique o terminal do VSCode/PyCharm."
#
#
# agente = ClinicaAgent()