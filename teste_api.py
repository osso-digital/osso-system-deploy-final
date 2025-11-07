# teste_api.py

import requests
import json
import time

def enviar_teste_webhook():
    # URL do seu servidor Flask
    url = "http://192.168.15.17:5000/webhook/orcamento-instantaneo"
    
    # Dados que simulam o cliente Webhook
    dados_json = {
        "nome_cliente": "Cliente Requests Sucesso",
        "whatsapp": "5511939369778",
        "pergunta_cliente": "Quero uma tattoo de leão na coxa, preta e branca.",
        "detalhes": {
            "tamanho": "grande",
            "complexidade": 1.4
        }
    }
    
    headers = {
        "Content-Type": "application/json"
    }

    print("--- Tentando enviar requisição Webhook via Python Requests ---")
    
    try:
        # Envia a requisição POST
        response = requests.post(url, headers=headers, json=dados_json, timeout=10)
        
        print("\n--- RESPOSTA DA API ---")
        print(f"Status HTTP: {response.status_code}")
        
        # Tenta decodificar a resposta JSON do seu Flask
        if response.status_code == 200:
            try:
                resposta_json = response.json()
                print("JSON Recebido (Sucesso):")
                print(json.dumps(resposta_json, indent=4, ensure_ascii=False))
            except json.JSONDecodeError:
                print("Erro ao decodificar JSON da resposta.")
                print("Texto da resposta:", response.text)
        else:
            print("Resposta de erro da API. Texto:", response.text)

    except requests.exceptions.ConnectionError:
        print("\nERRO: Não foi possível conectar. O servidor Flask (osso_api.py) está rodando?")
    except Exception as e:
        print(f"Erro inesperado: {e}")

if __name__ == "__main__":
    enviar_teste_webhook()