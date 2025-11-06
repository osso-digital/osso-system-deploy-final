# osso_api.py
# Módulo: OssoAPI (O Portão de Entrada/Webhook) - Versão com Agendamento e Envio WhatsApp

from flask import Flask, request, jsonify
import os
import random
import datetime # Necessário para cálculo de data
from typing import Dict, Any
import requests # << NOVO: Necessário para comunicação com API do WhatsApp

# Importa os módulos de Lógica de Negócio
try:
    from osso_tools import log_evento
    from osso_orcamento import calcular_novo_orcamento
    from osso_data import registrar_novo_atendimento, atualizar_orcamento_atendimento
    from osso_agenda import agendar_horario 
    # NOVO: Importa a função de envio de mensagem
    from osso_whatsapp import enviar_mensagem_whatsapp 
except ImportError as e:
    # Fallback simples (Stubs) para que o sistema não quebre
    def log_evento(msg, nivel='CRITICAL'): print(f"[{nivel}] osso_api: {e}")
    def calcular_novo_orcamento(p, d): return {'valor_final': 'R$ 0,00', 'servico_base': 'ERRO', 'valor_bruto': 0}
    def registrar_novo_atendimento(d): return type('Att', (object,), {'id': 999})()
    def atualizar_orcamento_atendimento(a, v, i): return False
    def agendar_horario(a, d, h, c): return False 
    # NOVO: Fallback para a função de envio
    def enviar_mensagem_whatsapp(n, m): return False 
    exit(1)

# Inicializa o aplicativo Flask
app = Flask(__name__)

# --- FUNÇÃO AUXILIAR PARA O BOT (Simula o Agendamento) ---
def _simular_agendamento_automatico(atendimento_id: int, nome: str, whatsapp: str):
    """ Tenta agendar o cliente automaticamente para um horário fictício. """
    
    data_alvo = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    hora_alvo = 10 
    
    if agendar_horario(atendimento_id, data_alvo, hora_alvo, nome):
        return f"Seu horário foi reservado provisoriamente para **{data_alvo} às {hora_alvo}h**! Por favor, confirme."
    else:
        return "Nossos horários estão cheios. Responderemos em breve para agendar manualmente."


@app.route('/webhook/orcamento-instantaneo', methods=['POST'])
def webhook_orcamento_instantaneo():
    """ ENDPOINT Webhook para receber pedidos de orçamento. """
    log_evento("Requisição POST recebida no endpoint /webhook/orcamento-instantaneo.", 'INFO')
    
    try:
        dados_webhook = request.get_json(silent=True)
        
        nome = dados_webhook.get('nome_cliente', 'Novo Cliente')
        whatsapp = dados_webhook.get('whatsapp', 'N/A')
        pergunta = dados_webhook.get('pergunta_cliente', '')
        
        if not pergunta or whatsapp == 'N/A':
             return jsonify({"status": "erro", "mensagem": "Campos 'whatsapp' e 'pergunta_cliente' são obrigatórios."}), 400

        # 1. REGISTRA O NOVO LEAD NO BD
        registro_lead = registrar_novo_atendimento({'nome_cliente': nome, 'whatsapp': whatsapp, 'pergunta_cliente': pergunta})
        atendimento_id = registro_lead.id
        
        # 2. CALCULA O ORÇAMENTO
        cor = 'colorida' in pergunta.lower() 
        detalhes_calculo = {'cor': cor, 'tamanho': 'grande', 'complexidade': 1.6}
        resultado_orcamento = calcular_novo_orcamento(pergunta, detalhes_calculo)
        
        # 3. ATUALIZA O STATUS E VALOR NO BD
        id_orcamento = f"OSSO-{atendimento_id}-{random.randint(100,999)}"
        atualizar_orcamento_atendimento(atendimento_id=atendimento_id, 
                                         valor=resultado_orcamento['valor_bruto'], id_orcamento=id_orcamento)
        
        # 4. TENTA AGENDAR AUTOMATICAMENTE (Agente OssoAgenda)
        mensagem_agendamento = _simular_agendamento_automatico(atendimento_id, nome, whatsapp)
        
        # 5. PREPARA A RESPOSTA FINAL
        mensagem_final_formatada = (
            f"🤖 Olá {nome}! O Orçamento Osso System analisou seu pedido de {resultado_orcamento['servico_base']}. "
            f"O valor inicial é de {resultado_orcamento['valor_final']}. "
            f"\n\n{mensagem_agendamento} Utilize o ID {id_orcamento}."
        )
        
        # 6. NOVO: Tenta ENVIAR a mensagem para o WhatsApp
        if enviar_mensagem_whatsapp(whatsapp, mensagem_final_formatada):
             log_evento(f"Mensagem de WhatsApp enviada com sucesso para {whatsapp}.", 'INFO')
        else:
             log_evento(f"Falha no envio da mensagem de WhatsApp para {whatsapp}.", 'WARNING')
        
        
        # 7. Retorno do Webhook (Retorno simples de sucesso para o provedor)
        resposta_para_webhook = {
            "status_processamento": "sucesso",
            "id_atendimento": atendimento_id,
            "valor_final": resultado_orcamento['valor_final'],
            "mensagem_final": mensagem_final_formatada
        }
        
        return jsonify(resposta_para_webhook), 200

    except Exception as e:
        log_evento(f"Erro interno no processamento do webhook: {e}", 'CRITICAL')
        return jsonify({"status": "erro", "mensagem": "Erro interno do servidor."}), 500


# Ponto de entrada do script para rodar o servidor Flask
if __name__ == '__main__':
    log_evento("Iniciando o servidor Flask (osso_api.py)", 'INFO')
    app.run(debug=True, host='0.0.0.0', port=5000)