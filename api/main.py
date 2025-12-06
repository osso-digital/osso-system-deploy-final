# api/main.py – versão FastAPI final, estável e preparada para expansão do SaaS

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from openai import OpenAI

# Schemas (Pydantic)
from api.schemas import WebhookInput

# Lógicas internas
from osso_data import registrar_novo_atendimento, atualizar_status_atendimento
from osso_orcamento import calcular_novo_orcamento

# Carregar variáveis de ambiente (.env)
load_dotenv()


# -----------------------------------------
# OPENAI CLIENT
# -----------------------------------------
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def gerar_resposta_openai(pergunta: str, orcamento: dict) -> str:
    """
    Gera resposta personalizada usando GPT baseado no orçamento calculado.
    """
    try:
        texto = (
            f"Valor estimado: {orcamento['valor_final']}\n"
            f"Serviço base: {orcamento['servico_base']}\n"
            f"Adicionais: {', '.join(orcamento['adicionais_aplicados'])}"
        )

        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Você é o BONE, assistente do estúdio."},
                {"role": "assistant", "content": texto},
                {"role": "user", "content": pergunta}
            ]
        )

        return completion.choices[0].message.content

    except Exception as e:
        return f"[ERRO AO GERAR RESPOSTA OPENAI] {str(e)}"


# -----------------------------------------
# FASTAPI SERVER
# -----------------------------------------
app = FastAPI(
    title="Bone API",
    version="1.0.0",
    description="Backend oficial do SaaS Osso Digital."
)

# CORS — importante para permitir requisições da sua landing page / apps
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # Ajuste depois se quiser restringir
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------------------
# ROTA PRINCIPAL DO ORÇAMENTO
# -----------------------------------------
@app.post("/webhook")
async def webhook(payload: WebhookInput):

    try:
        data = payload.model_dump()

        # -------------------------------
        # Validar dados principais
        # -------------------------------
        nome = data.get("nome")
        whatsapp = data.get("whatsapp")
        pergunta = data.get("pergunta")
        email = data.get("email")  # opcional

        if not nome or not whatsapp or not pergunta:
            return {"erro": "Campos obrigatórios ausentes: nome, whatsapp, pergunta."}

        # -------------------------------
        # Parâmetros para cálculo do orçamento
        # -------------------------------
        parametros_default = {
            "tamanho_cm": data.get("tamanho"),
            "cor_ou_preto": data.get("cor"),
            "complexidade": data.get("complexidade"),
            "local_corpo": data.get("local"),
            "sessao": data.get("sessao")
        }

        # -------------------------------
        # Calcular orçamento
        # -------------------------------
        orcamento = calcular_novo_orcamento(pergunta, parametros_default)

        # -------------------------------
        # Registrar lead / atendimento
        # -------------------------------
        dados_lead = {
            "nome": nome,
            "email": email,
            "whatsapp": whatsapp,
            "mensagem": pergunta,
            "orcamento": orcamento
        }

        atendimento_ref = registrar_novo_atendimento(
            dados_lead,
            "ORCAMENTO_GERADO"
        )

        # -------------------------------
        # Gerar resposta do BONE
        # -------------------------------
        resposta_osso = gerar_resposta_openai(pergunta, orcamento)

        # Atualizar status do atendimento
        atualizar_status_atendimento(atendimento_ref.id, "RESPONDIDO")

        # -------------------------------
        # Retorno final
        # -------------------------------
        return {
            "status": "ok",
            "id_atendimento": atendimento_ref.id,
            "orcamento": orcamento,
            "resposta_do_osso": resposta_osso
        }

    except Exception as e:
        return {"erro": f"Ocorreu um erro interno: {str(e)}"}
