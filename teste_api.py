import requests
import json

URL = "http://127.0.0.1:5000/webhook/orcamento-instantaneo"

payload = {
    "nome_cliente": "Teste Local",
    "whatsapp": "11999999999",
    "pergunta_cliente": "Quero orçamento de uma tatuagem média colorida"
}

print("📡 Enviando requisição para API...\n")

response = requests.post(URL, json=payload)

print("📥 Resposta da API:")
print(response.status_code)
try:
    print(response.json())
except:
    print(response.text)
