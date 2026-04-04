from app.database.connection import supabase

try:
    # Tenta ler a tabela de profissionais (que deve estar vazia, mas existente)
    res = supabase.table("profissionais").select("*").execute()
    print("✅ Conexão com Supabase realizada com sucesso!")
except Exception as e:
    print(f"❌ Erro na conexão: {e}")