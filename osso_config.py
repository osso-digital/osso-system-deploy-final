# -*- coding: utf-8 -*-
# osso_config.py
# Módulo: OssoConfig (Configurações e Variáveis de Ambiente)
# Centraliza todas as constantes e credenciais do sistema.

import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env (se existir)
load_dotenv()

# --- Configurações de API e Credenciais ---

# WATI / WhatsApp Business API
WH_TOKEN = os.getenv("OSSO_WATI_TOKEN", "SIMULATED_WATI_TOKEN")
WH_API_URL = os.getenv("OSSO_WATI_URL", "https://api.wati.com/api/v1/sendTemplateMessage")
WH_ID_TEMPL_ORCAMENTO = os.getenv("WH_ID_TEMPL_ORCAMENTO", "template_orcamento_pronto")

# URLs de Formulários Legais e Agendamento (Links que seriam gerados pelo sistema)
# Simulam URLs de Google Forms, Typeform, ou sistemas de agendamento (Ex: Calendly)
WH_FICHA_ANAMNESE = os.getenv("WH_FICHA_ANAMNESE", "https://forms.google.com/osso/anamnese_digital_v2")
WH_TERMO_CONSENTIMENTO = os.getenv("WH_TERMO_CONSENTIMENTO", "https://docusign.com/osso/termo_consentimento")
WH_LINK_AGENDA = os.getenv("WH_LINK_AGENDA", "https://calendly.com/osso-tatuaria/agendamento")

# --- Configurações de IA ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "") 

# --- Configurações de Negócio ---
VALOR_MIN_TATOO = 250.00
FATOR_COR_PERCENTUAL = 0.35 # Aumento de 35% para tatuagens coloridas
FATOR_LOCAL_COMPLEXIDADE = {
    "braço": 1.0, 
    "perna": 1.0, 
    "costas": 1.2, 
    "mão/pé": 1.3, 
    "pescoço": 1.5
}