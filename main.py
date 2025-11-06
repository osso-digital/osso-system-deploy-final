# main.py

import os

# Importa as funções principais dos módulos
try:
    from osso_tools import log_evento
    from osso_bot import iniciar_processamento_bot
except ImportError as e:
    # Fallback simples
    def log_evento(msg, nivel='INFO'):
        print(f"[{nivel}] main: {msg}")
    def iniciar_processamento_bot():
        log_evento("ERRO: Módulo osso_bot não encontrado para iniciar.", 'CRITICAL')
        return None

def main():
    """
    Função principal do projeto OSSO-PROJETO-NUCLEO.
    Inicia o ciclo de processamento do bot.
    """
    log_evento("Iniciando a aplicação principal (main.py)", 'INFO')
    
    # Chama a função principal de orquestração do bot
    relatorio = iniciar_processamento_bot()
    
    if relatorio:
        # Exibe uma mensagem de conclusão simples
        total_respostas = len(relatorio.get('respostas_geradas', []))
        log_evento(f"Processo finalizado com sucesso. {total_respostas} orçamentos concluídos.", 'INFO')
    else:
        log_evento("O processo não pôde ser concluído devido a erros anteriores.", 'ERROR')

if __name__ == '__main__':
    # Executa a aplicação quando o script main.py é chamado
    main()