# osso_legal.py
# Módulo: OssoLegal (Agente de Conformidade e Saúde)
# Gerencia o envio de Fichas de Anamnese e Termos Legais.

from typing import Dict, Any
import os

# Importa as ferramentas e o novo módulo de dados baseado em BD
try:
    from osso_tools import log_evento
    # OBS: Usamos 'pass' nas funções de BD pois este é um módulo de lógica, não de dados.
    # A atualização do BD será feita pelo osso_data.py
    from osso_config import WH_FICHA_ANAMNESE, WH_TERMO_CONSENTIMENTO 
except ImportError as e:
    def log_evento(msg, nivel='INFO'):
        print(f"[{nivel}] osso_legal: {msg}")
    WH_FICHA_ANAMNESE = "URL_DO_FORMULÁRIO_FALSO"
    WH_TERMO_CONSENTIMENTO = "URL_DO_TERMO_FALSO"


def enviar_link_anamnese(atendimento_id: int, whatsapp_cliente: str, nome_cliente: str) -> str:
    """
    Simula o envio do link da Ficha de Anamnese Digital (Ponto 3).
    """
    
    # 1. Cria a URL do formulário com parâmetros pré-preenchidos
    url_formulario = (
        f"{WH_FICHA_ANAMNESE}?"
        f"att_id={atendimento_id}&"
        f"cliente={nome_cliente.replace(' ', '+')}"
    )
    
    log_evento(f"URL de Anamnese gerada para {nome_cliente}: {url_formulario}", 'INFO')
    
    # 2. Simulação de Mensagem para o Cliente
    mensagem_whatsapp = (
        f"Olá, {nome_cliente}! Seu agendamento foi confirmado. "
        f"Por favor, preencha sua Ficha de Anamnese Digital (Saúde) antes da sessão: {url_formulario}"
    )
    
    return mensagem_whatsapp

def gerar_termo_consentimento(atendimento_id: int, nome_cliente: str) -> str:
    """
    Simula a geração e envio do link do Termo de Consentimento de Imagem (Ponto 4).
    """
    
    # Simula a criação de um PDF ou link para assinatura eletrônica
    url_termo = (
        f"{WH_TERMO_CONSENTIMENTO}?"
        f"id={atendimento_id}"
    )
    
    log_evento(f"Termo Legal gerado para {nome_cliente}.", 'INFO')
    
    mensagem_legal = (
        f"Seu Termo Legal de Consentimento e Uso de Imagem está pronto para assinatura digital. "
        f"Acesse: {url_termo}"
    )
    
    return mensagem_legal

def receber_dados_anamnese(atendimento_id: int, dados_formulario: Dict[str, Any]) -> bool:
    """
    Simula o recebimento do Webhook do Google Forms/Typeform com os dados preenchidos.
    """
    log_evento(f"Dados de Anamnese recebidos para ID {atendimento_id}.", 'INFO')
    
    # Lógica de Alerta (Diferencial de Venda)
    if dados_formulario.get('alergias_graves', False):
        log_evento(f"ALERTA: Cliente ID {atendimento_id} reportou alergias graves!", 'WARNING')
        
    # OBS: Aqui seria o ponto onde chamamos o osso_data.py para salvar na tabela FichaAnamnese do BD
    
    return True

# --- Bloco de Testes ---
if __name__ == '__main__':
    log_evento(f"Iniciando testes do {os.path.basename(__file__)} (OssoLegal)", 'INFO')
    
    # ID de teste que usamos no sistema
    ATT_ID = 4
    CLIENTE_NOME = "Cliente Requests Sucesso"
    CLIENTE_WHATSAPP = "5511998765432"

    # Ação 1: Envio da Ficha de Anamnese
    mensagem_ficha = enviar_link_anamnese(ATT_ID, CLIENTE_WHATSAPP, CLIENTE_NOME)
    print("\n--- Ação 1: Envio da Ficha de Anamnese ---")
    print(f"Mensagem Gerada: {mensagem_ficha}")
    
    # Ação 2: Envio do Termo Legal
    mensagem_termo = gerar_termo_consentimento(ATT_ID, CLIENTE_NOME)
    print("\n--- Ação 2: Envio do Termo Legal ---")
    print(f"Mensagem Gerada: {mensagem_termo}")
    
    # Ação 3: Simulação de Recebimento dos Dados de Saúde
    dados_recebidos = {
        'atendimento_id': ATT_ID,
        'alergias_graves': True, # Simula o preenchimento que dispara o alerta
        'medicamentos': 'Nenhum',
        'assinatura_digital': True
    }
    
    print("\n--- Ação 3: Recebimento dos Dados de Saúde ---")
    if receber_dados_anamnese(ATT_ID, dados_recebidos):
        log_evento("Ficha de Anamnese processada com sucesso. Dados prontos para o tatuador.", 'INFO')

    log_evento("Testes do osso_legal.py concluídos.", 'INFO')