# osso_bot.py
# Módulo: OssoBot (O Orquestrador) - Versão FINAL BD

from typing import List, Dict, Any
import os

# Importa os módulos que já estão funcionando
try:
    from osso_tools import log_evento, obter_data_hora_atual, formatar_moeda
    from osso_orcamento import processar_atendimentos_pendentes
    # CORRIGIDO: Importa a nova estrutura do osso_data para trabalhar com objetos BD
    from osso_data import carregar_todos_atendimentos, obter_resumo_atendimentos 
    from osso_models import iniciar_estrutura_banco # Inicializa o BD
except ImportError as e:
    # Fallback simples
    def log_evento(msg, nivel='INFO'):
        print(f"[{nivel}] osso_bot: {msg}")
    def obter_data_hora_atual():
        return "2025-11-01 12:00:00"
    def formatar_moeda(v): return "R$ 0,00"
    def processar_atendimentos_pendentes():
        log_evento("AVISO: Módulo osso_orcamento não carregado.", 'ERROR')
        return []
    def carregar_todos_atendimentos():
        return []
    def obter_resumo_atendimentos(atendimentos):
        return {'total_atendimentos': 'N/A'}
    def iniciar_estrutura_banco(): pass


def iniciar_processamento_bot() -> Dict[str, Any]:
    """
    Função principal do bot que orquestra a leitura de dados, processamento
    de orçamentos pendentes e simulação de resposta ao cliente.
    """
    log_evento("Iniciando o ciclo de processamento do OssoBot.", 'INFO')
    
    # NOVO: Garante que o BD exista antes de tudo
    iniciar_estrutura_banco() 

    # 1. Obter Resumo de Atendimentos
    atendimentos_bd = carregar_todos_atendimentos() # Puxa objetos do BD
    resumo_dados = obter_resumo_atendimentos(atendimentos_bd) # Gera resumo usando os objetos
    
    # CORRIGIDO: Acesso seguro à chave do dicionário
    total_atendimentos = resumo_dados.get('total_atendimentos', 'N/A')
    log_evento(f"Resumo de dados obtido: {total_atendimentos} total.", 'INFO')

    # 2. Processar a fila de orçamentos pendentes
    try:
        resultados_orcamento = processar_atendimentos_pendentes()
        log_evento(f"Processamento de orçamento concluído. {len(resultados_orcamento)} orçamentos calculados.", 'INFO')
    except Exception as e:
        log_evento(f"ERRO CRÍTICO ao processar orçamentos: {e}", 'CRITICAL')
        resultados_orcamento = []

    # 3. Simulação de Respostas
    respostas_simuladas = []
    for res in resultados_orcamento:
        cliente = res['cliente']
        valor = res['valor_final']
        servico = res['servico_base']
        
        # Simula a mensagem final que o bot enviaria
        mensagem_final = (
            f"Olá {cliente}! Analisei seu pedido de {servico}. "
            f"O orçamento inicial é de {valor}. "
            f"Entre em contato para agendar uma conversa detalhada!"
        )
        
        respostas_simuladas.append({
            'cliente': cliente,
            'valor': valor,
            'mensagem': mensagem_final,
            'status': 'RESPOSTA PRONTA'
        })
        log_evento(f"Resposta gerada para {cliente}: {valor}", 'INFO')

    log_evento("Ciclo de processamento do OssoBot concluído.", 'INFO')
    
    return {
        'timestamp': obter_data_hora_atual(),
        'resumo_dados': resumo_dados,
        'respostas_geradas': respostas_simuladas
    }

# --- Bloco de Testes ---
if __name__ == '__main__':
    log_evento(f"Iniciando testes do {os.path.basename(__file__)} (Ciclo Final)", 'INFO')
    
    relatorio = iniciar_processamento_bot()

    print("\n" + "="*50)
    print("        RELATÓRIO FINAL DO PROCESSO DO OSSOBOT")
    print("="*50)
    print(f"Total de Atendimentos no BD: {relatorio['resumo_dados'].get('total_atendimentos', 'N/A')}")
    print("\n--- Respostas Geradas (Orçamentos Concluídos) ---")

    if relatorio['respostas_geradas']:
        for i, resp in enumerate(relatorio['respostas_geradas']):
            print(f"\n[{i+1}] Cliente: {resp['cliente']} ({resp['status']})")
            print(f"    Valor: {resp['valor']}")
            print(f"    Mensagem: {resp['mensagem'][:100]}...")
    else:
        print("Nenhuma resposta de orçamento gerada neste ciclo.")
    
    print("="*50)
    log_evento("Testes do osso_bot.py concluídos.", 'INFO')