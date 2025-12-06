# osso_api.py – versão estável, SEM flask_cors, CORS nativo OK

import json
import os
from flask import Flask, request, jsonify, make_response
from dotenv import load_dotenv

from osso_data import registrar_novo_atendimento, atualizar_status_atendimento
from osso_orcamento import calcular_novo_orcamento
from openai import OpenAI

load_dotenv()

# -----------------------------------------
# OPENAI
# -----------------------------------------
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def gerar_resposta_openai(pergunta, orcamento):
    try:
        texto = (
            f"Valor estimado: {orcamento['valor_final']}\n"
            f"Serviço base: {orcamento['servico_base']}\n"
            f"Adicionais: {', '.join(orcamento['adicionais_aplicados'])}"
        )

        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system",
                 "content": "Você é o BONE, assistente do estúdio."},
                {"role": "assistant", "content": texto},
                {"role": "user", "content": pergunta}
            ]
        )
        return completion.choices[0].message.content

    except Exception as e:
        return f"[ERRO OPENAI] {str(e)}"


# -----------------------------------------
# FLASK
# -----------------------------------------
app = Flask(__name__)


# CORS NATIVO — sem instalar flask_cors
@app.after_request
def aplicar_cors(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    return response


@app.route("/webhook", methods=["POST", "OPTIONS"])
def webhook():
    # Pré-resposta do navegador (CORS)
    if request.method == "OPTIONS":
        return make_response("", 200)

    try:
        data = request.get_json()

        nome = data.get("nome")
        email = data.get("email")
        whatsapp = data.get("whatsapp")
        pergunta = data.get("pergunta")

        if not nome or not whatsapp or not pergunta:
            return jsonify({"erro": "Campos obrigatórios ausentes"}), 400

        # parâmetros do cálculo
        parametros_default = {
            "tamanho_cm": data.get("tamanho", 10),
            "cor_ou_preto": data.get("cor", "Preto e Cinza"),
            "complexidade": data.get("complexidade", "Média"),
            "local_corpo": data.get("local", "Braço"),
            "sessao": data.get("sessao", "Sessão única")
        }

        # calcular orçamento
        orcamento = calcular_novo_orcamento(pergunta, parametros_default)

        # registrar lead
        dados_lead = {
            "nome": nome,
            "email": email,
            "whatsapp": whatsapp,
            "mensagem": pergunta,
            "orcamento": orcamento
        }

        atendimento_ref = registrar_novo_atendimento(dados_lead, "ORCAMENTO_GERADO")

        resposta_osso = gerar_resposta_openai(pergunta, orcamento)

        atualizar_status_atendimento(atendimento_ref.id, "RESPONDIDO")

        return jsonify({
            "status": "ok",
            "id_atendimento": atendimento_ref.id,
            "orcamento": orcamento,
            "resposta_do_osso": resposta_osso
        })

    except Exception as e:
        return jsonify({"erro": str(e)}), 500


if __name__ == "__main__":
    print("[INFO] API BONE iniciada localmente...")
    app.run(host="0.0.0.0", port=5000, debug=True)
