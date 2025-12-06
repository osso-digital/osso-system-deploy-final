# -*- coding: utf-8 -*-
# osso_data.py - BANCO DE DADOS FIRESTORE (CORRIGIDO)

import os
import json
from typing import Optional, Dict, Any

from firebase_admin import credentials, firestore
import firebase_admin
from osso_tools import log_evento

# Caminho da chave local
SERVICE_KEY_PATH = os.path.join(os.path.dirname(__file__), "meu-segredo.json")

# --- Inicialização do Firebase Admin SDK ---
try:
    if os.path.exists(SERVICE_KEY_PATH):
        cred = credentials.Certificate(SERVICE_KEY_PATH)
        firebase_admin.initialize_app(cred)
        log_evento("Firebase carregado LOCALMENTE usando meu-segredo.json.", "INFO", "osso_data")
    else:
        firebase_admin.initialize_app()
        log_evento("Firebase carregado AUTOMATICAMENTE (Cloud Run ADC).", "INFO", "osso_data")

except ValueError:
    # Firebase já estava inicializado
    pass

# Cliente Firestore
DB = firestore.client()
ATENDIMENTOS_COLLECTION = "atendimentos"


# ------------------- Estrutura do Atendimento -------------------
class AtendimentoRef:
    def __init__(self, id: str, status: str, dados: Dict[str, Any]):
        self.id = id
        self.status = status
        self.nome_cliente = dados.get("nome_cliente", "")
        self.ideia_tatuagem = dados.get("ideia_tatuagem", "")
        self.telefone = dados.get("telefone", "")
        self.orcamento_base = dados.get("orcamento_base", 0.0)
        self.duracao_estimada = dados.get("duracao_estimada", 0.0)
        self.data_agendamento = dados.get("data_agendamento")
        self.hora_agendamento = dados.get("hora_agendamento")

    def to_dict(self):
        d = self.__dict__.copy()
        d.pop("id", None)
        return d

    @classmethod
    def from_dict(cls, doc_id: str, dados: Dict[str, Any]):
        o = cls(doc_id, dados.get("status", "DESCONHECIDO"), dados)
        for k, v in dados.items():
            setattr(o, k, v)
        return o


# ------------------- Funções de Banco -------------------
def registrar_novo_atendimento(payload: Dict[str, str], status_inicial: str) -> AtendimentoRef:
    data = {
        "status": status_inicial,
        "nome_cliente": payload.get("nome_cliente"),
        "ideia_tatuagem": payload.get("ideia_tatuagem"),
        "telefone": payload.get("telefone"),
        "orcamento_base": 0.0,
        "duracao_estimada": 0.0,
        "data_agendamento": None,
        "hora_agendamento": None
    }

    _, ref = DB.collection(ATENDIMENTOS_COLLECTION).add(data)
    log_evento(f"Novo atendimento criado: {ref.id}", "INFO", "osso_data")
    return AtendimentoRef.from_dict(ref.id, data)


def obter_atendimento_por_id(atendimento_id: str) -> Optional[AtendimentoRef]:
    doc = DB.collection(ATENDIMENTOS_COLLECTION).document(atendimento_id).get()

    if doc.exists:
        return AtendimentoRef.from_dict(doc.id, doc.to_dict())
    return None


def atualizar_status_atendimento(
    atendimento_id: str,
    novo_status: str,
    orcamento_base=None,
    duracao_estimada=None,
    data_agendamento=None,
    hora_agendamento=None
):
    ref = DB.collection(ATENDIMENTOS_COLLECTION).document(atendimento_id)
    data = {"status": novo_status}

    if orcamento_base is not None:
        data["orcamento_base"] = orcamento_base

    if duracao_estimada is not None:
        data["duracao_estimada"] = duracao_estimada

    if data_agendamento is not None:
        data["data_agendamento"] = data_agendamento

    if hora_agendamento is not None:
        data["hora_agendamento"] = hora_agendamento

    ref.update(data)
    log_evento(f"Atendimento {atendimento_id} atualizado em Firestore.", "INFO", "osso_data")
    return True


# Não usado no Firestore, mas necessário para compatibilidade
def reset_bd_simulado():
    log_evento("Reset ignorado. Firestore é persistente.", "DEBUG", "osso_data")


def dump_atendimento(atendimento_id: str):
    doc = obter_atendimento_por_id(atendimento_id)
    if doc:
        print(json.dumps(doc.to_dict(), indent=4, ensure_ascii=False))
    else:
        print("ID não encontrado no Firestore.")
