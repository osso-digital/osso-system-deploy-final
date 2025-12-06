# processar_orcamento.py
from osso_tools import log_evento
from osso_orcamento import processar_atendimentos_pendentes

log_evento("Iniciando processamento de orçamentos pendentes...", 'INFO')

resultados = processar_atendimentos_pendentes()

if resultados:
    for res in resultados:
        print("-" * 30)
        print(f"CLIENTE: {res['cliente']}")
        print(f"SERVIÇO: {res['servico_base']}")
        print(f"VALOR CALCULADO: {res['valor_final']}")
else:
    print("Nenhum atendimento pendente encontrado.")

log_evento("Processamento concluído.", 'INFO')
