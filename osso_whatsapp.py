# -*- coding: utf-8 -*-
# osso_whatsapp.py
# Módulo: OssoWhatsApp (Simulador de Envio)
# Simula a interação com uma API de WhatsApp (como Twilio ou ZapSign/Wati).

from typing import Any, Dict
import os

# Importa as ferramentas essenciais
try:
    from osso_tools import log_evento
    from osso_config import WH_API_URL, WH_TOKEN # Importa configurações da API de Simulação
except ImportError:
    def log_evento(msg, nivel='INFO'): print(f"[{nivel}] osso_whatsapp: {msg}")
    WH_API_URL = "URL_FALSA_API"
    WH_TOKEN = "TOKEN_FALSO"


def enviar_mensagem_whatsapp(numero_destino: str, mensagem: str) -> bool:
    """
    Simula o envio de uma mensagem via WhatsApp para o número de destino (Ponto 9).
    
    Em uma implementação real, esta função faria uma requisição HTTP POST
    para o endpoint da API do WhatsApp, usando o WH_TOKEN e WH_API_URL.
    """
    if not numero_destino or not mensagem:
        log_evento("Tentativa de envio de WhatsApp falhou: Número ou mensagem vazios.", 'ERROR')
        return False

    # 1. Preparação dos Dados (Simulação)
    # data = {
    #     "token": WH_TOKEN,
    #     "to": numero_destino,
    #     "body": mensagem
    # }
    
    # 2. Simulação de Chamada de API
    log_evento("-" * 50, 'INFO')
    log_evento(f"SIMULAÇÃO WHATSAPP: Mensagem para {numero_destino}:", 'INFO')
    log_evento(f"Corpo da Mensagem:\n{mensagem[:150]}...", 'INFO')
    log_evento(f"Endpoint Simulada: {WH_API_URL}", 'DEBUG')
    log_evento("SIMULAÇÃO: API retornou sucesso.", 'INFO')
    log_evento("-" * 50, 'INFO')

    # 3. Retorno (Sempre True na simulação, a menos que os dados sejam inválidos)
    return True

# --- Bloco de Testes ---
if __name__ == '__main__':
    log_evento(f"Iniciando testes do {os.path.basename(__file__)} (Simulação WhatsApp)", 'INFO')
    
    # Teste de sucesso (Mensagem de Orçamento/Agendamento)
    orcamento_pronto = (
        "🎉 Olá! Seu orçamento para a tatuagem de Leão na coxa foi calculado: R$ 850,00! "
        "Você pode agendar seu horário clicando aqui: [LINK_AGENDA_CALENDLY]."
    )
    resultado_sucesso = enviar_mensagem_whatsapp(
        numero_destino="5521999998888",
        mensagem=orcamento_pronto
    )
    print(f"Resultado Sucesso: {resultado_sucesso}")

    # Teste de falha (Número vazio)
    resultado_falha = enviar_mensagem_whatsapp(
        numero_destino="",
        mensagem="Mensagem de teste falha."
    )
    print(f"Resultado Falha: {resultado_falha}")
    
    log_evento("Testes do osso_whatsapp.py concluídos.", 'INFO')