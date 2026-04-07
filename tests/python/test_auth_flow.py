import pytest
import os
import time
import uuid
from supabase import create_client

# Configurações do ambiente
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

def test_fluxo_criacao_usuario_completo():
    """
    QA Test: Valida se o SignUp aciona a Trigger e cria Empresa/Perfil.
    """
    # Geramos um e-mail único
    unique_id = str(uuid.uuid4())[:8]
    email_teste = f"qa_robot_{unique_id}@example.com"
    senha_teste = "qa_password_123"
    nome_teste = f"Robô QA {unique_id}"
    clinica_teste = f"Clínica Automação {unique_id}"

    # 1. SignUp no Auth
    auth_response = supabase.auth.sign_up({
        "email": email_teste,
        "password": senha_teste,
        "options": {
            "data": {
                "full_name": nome_teste,
                "company_name": clinica_teste
            }
        }
    })

    assert auth_response.user is not None, "Falha ao criar usuário no Auth"
    user_id = auth_response.user.id

    # 2. Validação com Retry para a Trigger
    empresa_data = None
    for i in range(5):
        try:
            # Busca a empresa vinculada ao novo user_id
            response = supabase.table("empresas").select("*").eq("user_id", user_id).single().execute()
            if response.data:
                empresa_data = response.data
                break
        except Exception as e:
            print(f"Tentativa {i + 1} falhou: {str(e)}")
            time.sleep(1)

    # Asserção Final
    assert empresa_data is not None, f"Trigger falhou: Empresa não encontrada para {user_id}"
    assert empresa_data["nome_fantasia"] == clinica_teste

    print(f"\n✅ Sucesso: Usuário {email_teste} validado!")