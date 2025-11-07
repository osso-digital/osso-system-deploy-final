# osso_whatsapp.py
# Módulo: Gerenciamento da API do WhatsApp (Conecta com Twilio) - VERSÃO FINAL

import requests
import json
from typing import Dict, Any

# Importa as credenciais de segurança
try:
    from osso_tools import log_evento
    # Importa as credenciais do Twilio do osso_secrets
    from osso_secrets import TWILIO_API_URL, TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_NUMBER
except ImportError:
    # Stubs de segurança
    def log_evento(msg, nivel='INFO'): print(f"[{nivel}] osso_whatsapp: Erro de credencial")
    TWILIO_API_URL = "http://ERRO_CREDENCIAIS" 
    TWILIO_ACCOUNT_SID = "ERRO_SID" 
    TWILIO_AUTH_TOKEN = "ERRO_TOKEN" 
    TWILIO_WHATSAPP_NUMBER = "ERRO_NUMERO"


def enviar_mensagem_whatsapp(numero_destino: str, mensagem: str) -> bool:
    """
    Função para enviar a mensagem final do bot para o cliente via Twilio.
    
    Args:
        numero_destino: O número do cliente (Ex: 5511999998888).
        mensagem: O texto gerado pelo osso_api.py.
        
    Returns: True se o envio for bem-sucedido.
    """
    log_evento(f"Tentando enviar mensagem via API Twilio para {numero_destino}...", 'INFO')
    
    # O Twilio exige o número de destino no formato 'whatsapp:+55...'
    numero_destino_twilio = f"whatsapp:{numero_destino}"
    
    # 1. Dados que o Twilio precisa
    payload = {
        "To": numero_destino_twilio, 
        "From": TWILIO_WHATSAPP_NUMBER,
        "Body": mensagem,
    }
    
    # 2. Configuração da Requisição (Autenticação HTTP Básica)
    try:
        response = requests.post(
            TWILIO_API_URL, 
            data=payload,
            auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN), # Autenticação com SID e Token
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            log_evento(f"Mensagem enviada com sucesso para {numero_destino}!", 'INFO')
            return True
        else:
            log_evento(f"Falha ao enviar mensagem. Status: {response.status_code}. Resposta: {response.text}", 'ERROR')
            return False
            
    except requests.exceptions.RequestException as e:
        log_evento(f"Erro de conexão/timeout com API Twilio: {e}", 'CRITICAL')
        return False


# --- Bloco de Testes ---
if __name__ == '__main__':
    log_evento(f"Iniciando Teste de Envio (OssoWhatsapp)", 'INFO')
    
    # Use seu número de teste aqui
    NUMERO_TESTE = "558" 
    MENSAGEM_FINAL = "TESTE FINAL DO OSSO IA SYSTEM: Conexão Twilio estabelecida!"
    
    enviar_mensagem_whatsapp(NUMERO_TESTE, MENSAGEM_FINAL)
    log_evento("Teste de envio de WhatsApp concluído.", 'INFO')