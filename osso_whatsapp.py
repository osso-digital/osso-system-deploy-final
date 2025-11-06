# osso_whatsapp.py
# Módulo: Gerenciamento da API do WhatsApp (Conecta com osso_secrets)

import requests
import json
from typing import Dict, Any

# Importa as credenciais de segurança e as ferramentas
try:
    from osso_tools import log_evento
    from osso_secrets import WHATSAPP_API_URL, WHATSAPP_API_TOKEN
except ImportError:
    # Stubs para evitar quebrar o sistema se o arquivo de segredos não existir
    def log_evento(msg, nivel='INFO'): print(f"[{nivel}] osso_whatsapp: {msg}")
    WHATSAPP_API_URL = "http://ERRO_URL_SECRETS_NOT_FOUND" 
    WHATSAPP_API_TOKEN = "ERRO_TOKEN_NOT_FOUND" 


def enviar_mensagem_whatsapp(numero_destino: str, mensagem: str) -> bool:
    """
    Função para enviar a mensagem final do bot para o cliente.
    
    Args:
        numero_destino: O número do cliente.
        mensagem: O texto gerado pelo osso_api.py (Orçamento/Agendamento).
        
    Returns: True se o envio for bem-sucedido.
    """
    log_evento(f"Tentando enviar mensagem via API para {numero_destino}...", 'INFO')
    
    # 1. Dados que a API precisa (formato varia por provedor, este é um exemplo comum)
    payload = {
        "to": numero_destino,
        "body": mensagem,
        # Se fosse Twilio, incluiria o 'from' number também
    }
    
    # 2. Configuração da Requisição
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {WHATSAPP_API_TOKEN}"
    }

    try:
        # Tenta enviar a requisição POST
        response = requests.post(WHATSAPP_API_URL, headers=headers, json=payload, timeout=10)
        
        if response.status_code == 200:
            log_evento(f"Mensagem enviada com sucesso para {numero_destino}!", 'INFO')
            return True
        else:
            log_evento(f"Falha ao enviar mensagem. Status: {response.status_code}. Resposta: {response.text}", 'ERROR')
            return False
            
    except requests.exceptions.RequestException as e:
        log_evento(f"Erro de conexão/timeout com API do WhatsApp: {e}", 'CRITICAL')
        return False

# --- Bloco de Testes ---
if __name__ == '__main__':
    log_evento(f"Iniciando Teste de Envio (OssoWhatsapp)", 'INFO')
    
    # Este teste falhará propositalmente, pois a URL é falsa
    NUMERO_TESTE = "5511999998888" 
    MENSAGEM_FINAL = "Seu orçamento é R$ 2500,00 e seu agendamento provisório é amanhã às 10h!"
    
    enviar_mensagem_whatsapp(NUMERO_TESTE, MENSAGEM_FINAL)
    log_evento("Teste de envio de WhatsApp concluído.", 'INFO')