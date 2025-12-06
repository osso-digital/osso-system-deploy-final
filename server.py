from flask import Flask, request, jsonify
# Importa o módulo do agente e o módulo de dados (para reset_bd_simulado, se precisar)
import osso_agent 
from osso_data import reset_bd_simulado, dump_atendimento

app = Flask(__name__)

# Rota de teste simples para garantir que o servidor está no ar
# Esta rota DEVE responder para que possamos descartar o problema do gunicorn/path
@app.route('/', methods=['GET'])
def health_check():
    # Isso confirmará que o Flask carregou sem erros de importação.
    return jsonify({"status": "Servidor OssoAgent Online. Rotas carregadas!"}), 200

# Rota para receber dados da landing page e processar
@app.route('/iniciar_atendimento', methods=['POST'])
def iniciar_atendimento():
    # ATENÇÃO: Em ambiente de teste com BD local simulado, é necessário resetar.
    # Em produção com Firestore, esta linha deve ser removida.
    reset_bd_simulado() 
    
    # Aqui você pega os dados da requisição (ex: ideia, nome, contato)
    data = request.get_json()
    
    # Simulação de um lead novo:
    dados_lead = {
        'nome_cliente': data.get('nome', 'Cliente de Teste'),
        'ideia_tatuagem': data.get('ideia', 'Uma flor minimalista'),
        'telefone': data.get('telefone', '00000000000')
    }
    
    # 🚨 PONTO CHAVE: Chama a lógica do seu osso_agent.py
    try:
        # Inicia a simulação do atendimento (ORCAMENTO_PENDENTE)
        resposta_orcamento, ref_orcamento = osso_agent.processar_atendimento(dados_lead, 'ORCAMENTO_PENDENTE')
        
        # Simula a confirmação de pagamento para ir para o agendamento
        resposta_agendamento, ref_agendamento = osso_agent.processar_atendimento(
            dados_lead, 
            'AGENDADO',
            atendimento_id_existente=ref_orcamento.id
        )

        return jsonify({
            "status": "SUCESSO",
            "orcamento_apresentado": resposta_orcamento,
            "agendamento_confirmado": resposta_agendamento,
            "dados_finais": dump_atendimento(ref_agendamento.id)
        }), 200
    except Exception as e:
        # Se houver qualquer falha no osso_agent ou em seus submódulos
        return jsonify({"erro": "Falha no Processamento do Agente", "detalhe": str(e)}), 500

# O Gunicorn (que está no Dockerfile) vai rodar essa variável 'app'