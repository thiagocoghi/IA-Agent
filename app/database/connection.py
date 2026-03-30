from supabase import create_client, Client
from app.core.config import settings

def get_supabase_client() -> Client:
    # Cria a conexão usando as variáveis do seu .env
    url = settings.SUPABASE_URL
    key = settings.SUPABASE_KEY
    return create_client(url, key)

# Instância global para uso no projeto
supabase = get_supabase_client()