#!/usr/bin/env python3
# osso_bot_chat.py
# Chat bot web (BONES) integrado ao projeto OSSO IA SYSTEM
# Frontend simples + endpoints JSON para integração com o site

import os
import re
import json
from flask import Flask, request, jsonify, render_template_string
from typing import Dict, Any, Optional

# tenta integrar com os módulos do seu projeto
try:
    from osso_tools import log_evento, formatar_moeda, obter_data_hora_atual
except ImportError:
    def log_evento(msg, nivel='INFO'): print(f"[{nivel}] {msg}")
    def formatar_moeda(v): return f"R$ {v:.2f}"
    def obter_data_hora_atual(): return "2025-11-10 00:00:00"

try:
    # usamos o orcamento existente para calcular preços
    from osso_orcamento import calcular_novo_orcamento
    from osso_data import registrar_novo_atendimento, atualizar_orcamento_atendimento
except Exception as e:
    log_evento(f"AVISO: não foi possível importar osso_orcamento/osso_data: {e}", 'WARNING')
    # stubs para não quebrar em ambiente de dev
    def calcular_novo_orcamento(pergunta, detalhes):
        return {'status': 'ORÇAMENTO CALCULADO', 'servico_base': 'OUTRO',
                'valor_bruto': 200.0, 'valor_final': formatar_moeda(200.0)}
    def registrar_novo_atendimento(d): 
        class A: id = 999
        log_evento("Stub: registrar_novo_atendimento chamado", 'INFO')
        return A()
    def atualizar_orcamento_atendimento(a, v, i): 
        log_evento("Stub: atualizar_orcamento_atendimento chamado", 'INFO')
        return True

# OpenAI client
try:
    import openai
    OPENAI_KEY = os.getenv('OPENAI_API_KEY')
    if not OPENAI_KEY:
        log_evento("Nenhuma OPENAI_API_KEY encontrada nas variáveis de ambiente.", 'WARNING')
    else:
        openai.api_key = OPENAI_KEY
except Exception as e:
    openai = None
    log_evento(f"OpenAI client não disponível: {e}", 'WARNING')


app = Flask(__name__)

# Simple in-memory "mini-session" so the bot can ask follow-ups while user keeps the same session id.
# For production, persist in DB.
CONVERSATIONS: Dict[str, Dict[str, Any]] = {}

CHAT_HTML = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>OSSO — Chat Bones</title>
  <style>
    body{background:#0b0b0b;color:#eee;font-family:Inter,system-ui,Segoe UI,Arial;margin:0}
    .wrap{max-width:720px;margin:40px auto;padding:20px}
    .card{background:#0f0f10;border-radius:10px;padding:18px;box-shadow:0 6px 24px rgba(0,0,0,.6)}
    .msgs{height:60vh;overflow:auto;padding:10px;border-radius:8px;background:#070707;border:1px solid #1a1a1a}
    .msg{padding:8px 12px;margin:8px 0;border-radius:12px;display:inline-block;max-width:78%}
    .me{background:#1f6feb;color:#fff;margin-left:auto}
    .bot{background:#121212;border:1px solid #2b2b2b;color:#fff}
    .meta{font-size:12px;color:#9aa0a6;margin-top:8px}
    input[type=text]{width:calc(100% - 110px);padding:10px;border-radius:8px;border:1px solid #222;background:#050505;color:#fff}
    button{padding:10px 14px;margin-left:8px;border-radius:8px;border:none;background:#1f6feb;color:#fff}
    .row{display:flex;align-items:center;margin-top:12px}
    .brand{font-weight:700;color:#ff5a5f}
  </style>
</head>
<body>
  <div class="wrap">
    <div class="card">
      <h2 style="margin:0">OSSO — Bones Chat <span class="brand">| Tattoo Até os Ossos</span></h2>
      <p class="meta">Converse com o Bones — pergunta estilo, tamanho e te passa orçamento.</p>
      <div id="msgs" class="msgs"></div>
      <div class="row">
        <input id="name" placeholder="Seu nome (opcional)" type="text" />
        <input id="whatsapp" placeholder="WhatsApp (opcional, ex: 55119...)" style="margin-left:8px" type="text" />
      </div>
      <div class="row">
        <input id="input" placeholder="Escreva aqui... (ex: quero uma tattoo realismo, costas, 20cm)" type="text" />
        <button id="send">Enviar</button>
      </div>
    </div>
  </div>
<script>
const msgs = document.getElementById('msgs');
const input = document.getElementById('input');
const send = document.getElementById('send');

function addBubble(text, cls='bot'){
  const d = document.createElement('div');
  d.className = 'msg ' + cls;
  d.innerText = text;
  msgs.appendChild(d);
  msgs.scrollTop = msgs.scrollHeight;
}

send.onclick = async () => {
  const name = document.getElementById('name').value || '';
  const whatsapp = document.getElementById('whatsapp').value || '';
  const text = input.value.trim();
  if(!text) return;
  addBubble(text, 'me');
  input.value = '';
  addBubble('...pensando', 'bot');
  try {
    const res = await fetch('/chat', {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify({session_id: whatsapp || name || 'guest', name, whatsapp, message:text})
    });
    const data = await res.json();
    // remove the '...pensando' last bot
    const last = msgs.querySelectorAll('.bot');
    if(last.length) last[last.length-1].remove();
    addBubble(data.reply, 'bot');
    if(data.orcamento) addBubble('Orçamento sugerido: ' + data.orcamento, 'bot');
  } catch(e){
    addBubble('Erro no chat: ' + e.message, 'bot');
  }
};
</script>
</body>
</html>
"""

# helper: extract style & size from text (basic)
STYLE_KEYWORDS = ['realismo','realistic','blackwork','black work','fineline','fineline','tradicional','traditional','oriental','fênix','fenix','floral','geométrica','geometrica','aquarela','watercolor']

def detect_style_size(text: str) -> Dict[str, Optional[Any]]:
    txt = text.lower()
    style = None
    for s in STYLE_KEYWORDS:
        if s in txt:
            style = s.upper()
            break
    # try to extract cm number (e.g. "20cm", "20 cm", "20cmx30cm", "20")
    size = None
    m = re.search(r'(\d{1,3})\s?cm', txt)
    if m:
        try:
            size = int(m.group(1))
        except:
            size = None
    else:
        m2 = re.search(r'\b(\d{1,3})\b', txt)
        if m2:
            # only accept small numbers as size guess (<=80)
            n = int(m2.group(1))
            if 1 <= n <= 80:
                size = n
    return {'style': style, 'size_cm': size}

def build_prompt(bones_profile: Dict[str,Any], user_message: str, contexto: Dict[str,Any]) -> str:
    """
    Construimos um prompt sendo Bones: personalidade + contexto do estúdio
    """
    persona = (
        "Você é BONES, 47 anos, braço direito do Coringa há 15 anos. "
        "Toma decisões rápidas, fala de forma descontraída porém técnica. "
        "Explica preços claramente e oferece agendamento e opções de pagamento."
    )
    studio = (
        "Estúdio Tattoo Até os Ossos — Rua Monsenhor Pio Ragazinskas, Vila Zelina. "
        "Horário: 11:00-20:00 seg-sáb. Trabalhos: Realismo, Blackwork, Oriental, Traditional, Fine line, Cover-ups, Piercing. "
        "Sinal p/ agendamento: R$100. Sessão mínima: 3h. Custo médio por sessão 3h = R$600. Valores por tamanho: pequena R$200-400, média R$400-800, grande R$800+."
    )
    # context could include previous questions/answers
    prompt = f"{persona}\n{studio}\n\nContexto: {json.dumps(contexto)}\n\nCliente: {user_message}\n\nResponda como BONES, deixe claro preço estimado se possível, e solicite WhatsApp se precisar enviar orçamento. Seja objetivo e educado."
    return prompt

def ask_openai(prompt: str) -> str:
    if openai is None:
        # fallback simple rule
        return "Salve! Manda mais detalhe: qual estilo (realismo, fineline, blackwork), e um tamanho aproximado em cm? Ex: 12cm"
    try:
        # usamos chat completion
        resp = openai.ChatCompletion.create(
            model = os.getenv('OPENAI_MODEL','gpt-4o-mini'),
            messages = [
                {"role":"system","content":"You are BONES, assistant persona for a tattoo studio. Keep responses concise and helpful."},
                {"role":"user","content": prompt}
            ],
            max_tokens=300,
            temperature=0.2,
        )
        text = resp.choices[0].message.content.strip()
        return text
    except Exception as e:
        log_evento(f"Erro OpenAI: {e}", 'ERROR')
        return "Desculpa, ocorreu um erro ao gerar a resposta. Tenta de novo ou me passa um WhatsApp que eu continuo por lá."

@app.route('/')
def index():
    return render_template_string(CHAT_HTML)

@app.route('/chat', methods=['POST'])
def chat():
    """
    Endpoint principal: recebe {session_id, name, whatsapp, message}
    - detecta se há estilo/tamanho. Se sim: calcula orçamento e salva no BD.
    - responde usando OpenAI (ou fallback) com a persona BONES.
    """
    data = request.get_json(force=True, silent=True) or {}
    session_id = data.get('session_id') or data.get('whatsapp') or data.get('name') or 'guest'
    name = data.get('name') or 'Cliente'
    whatsapp = data.get('whatsapp') or ''
    message = data.get('message','').strip()
    if not message:
        return jsonify({'reply': 'Fala aí! O que você quer tatuar?'}), 200

    conv = CONVERSATIONS.setdefault(session_id, {'history': [], 'collected': {}})
    conv['history'].append({'from':'user','text':message})

    detected = detect_style_size(message)
    # merge detected into collected info if missing
    if detected.get('style') and not conv['collected'].get('style'):
        conv['collected']['style'] = detected['style']
    if detected.get('size_cm') and not conv['collected'].get('size_cm'):
        conv['collected']['size_cm'] = detected['size_cm']

    # If we already have style + size, compute quote
    estilo = conv['collected'].get('style')
    tamanho = conv['collected'].get('size_cm')

    resposta_text = None
    orcamento_text = None
    saved = False

    # If both info available, compute budget
    if estilo and tamanho:
        detalhes = {
            'cor': True if 'color' in message.lower() or 'colorida' in message.lower() else False,
            'tamanho': 'grande' if tamanho >= 20 else ('media' if tamanho >= 10 else 'pequena'),
            'complexidade': 1.4
        }
        try:
            orc = calcular_novo_orcamento(f"{estilo} {tamanho}cm", detalhes)
            orc_val = orc.get('valor_bruto', None)
            orc_str = orc.get('valor_final', formatar_moeda(orc_val or 0))
            orcamento_text = f"Orçamento estimado: {orc_str} (est. para {tamanho}cm, estilo {estilo})."
            # Registrar lead no BD (se não registrado)
            # cria um registro novo no BD com pergunta original e whatsapp (se fornecido)
            registro = registrar_novo_atendimento({
                'nome_cliente': name,
                'whatsapp': whatsapp,
                'pergunta_cliente': f"{estilo} {tamanho}cm"
            })
            if registro:
                # atualiza valor no BD
                try:
                    atualizar_orcamento_atendimento(registro.id, orc_val, f"OSSO-{registro.id}")
                except Exception as e:
                    log_evento(f"Falha ao atualizar orcamento no BD: {e}", 'WARNING')
            saved = True
            conv['history'].append({'from':'bot','text':orcamento_text})
        except Exception as e:
            log_evento(f"Erro ao calcular orcamento: {e}", 'ERROR')
            orcamento_text = None

    # Build prompt for OpenAI using persona & context
    contexto = {
        'collected': conv['collected'],
        'saved_lead': saved
    }
    prompt = build_prompt({}, message, contexto)
    ai_reply = ask_openai(prompt)
    conv['history'].append({'from':'bot','text':ai_reply})

    # If we have an orcamento_text, send it separately in response
    response_payload = {'reply': ai_reply}
    if orcamento_text:
        response_payload['orcamento'] = orcamento_text
    if saved:
        response_payload['saved'] = True

    return jsonify(response_payload), 200

if __name__ == '__main__':
    log_evento("Iniciando osso_bot_chat (Flask)", 'INFO')
    port = int(os.getenv('PORT', 5000))
    # debug False for safer default (you can enable in dev)
    app.run(host='0.0.0.0', port=port, debug=False)
