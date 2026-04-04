from google import genai

# Teste direto e rápido
client = genai.Client(api_key="AIzaSyC9Qr2V2kbObez76vsGniF6_e-9RQ78Hmk")

try:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="Oi, você está me ouvindo?"
    )
    print("✅ SUCESSO! A chave funciona:", response.text)
except Exception as e:
    print("❌ ERRO: A chave continua inválida.")
    print(e)