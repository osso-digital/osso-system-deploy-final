
# PAINEL ADMINISTRATIVO — OSSO IA SYSTEM

Este documento define as **regras oficiais do Painel Administrativo** do OSSO IA SYSTEM.

O painel é o **ponto de controle humano** do sistema.
Nenhuma automação pode substituir decisões tomadas neste painel.

---

## 🎯 Objetivo do painel

- Centralizar atendimentos
- Visualizar leads e status
- Validar valores e decisões
- Controlar operação multi-nicho
- Garantir conformidade legal e comercial
- Preparar o sistema para modelo SaaS

---

## 🧩 Módulos obrigatórios do painel

### 1️⃣ LEADS

Exibição de todos os atendimentos registrados.

**Campos mínimos obrigatórios:**
- ID do atendimento
- Nome do lead
- Contato (WhatsApp / Email)
- Nicho
- Status atual
- Data de criação
- Última interação
- Origem do lead (site, WhatsApp, social)

---

### 2️⃣ ATENDIMENTO

Visualização detalhada da conversa.

**O painel deve permitir:**
- Ler todo o histórico
- Ver perguntas feitas pelo BONE
- Ver respostas do lead
- Ver pré-orçamento apresentado

⚠️ O painel **não edita** mensagens já enviadas.

---

### 3️⃣ PRÉ-ORÇAMENTO

Área de validação humana.

**Regras obrigatórias:**
- Visualizar critérios usados pela IA
- Visualizar valores estimativos
- Confirmar, ajustar ou recusar orçamento

⚠️ Apenas humanos podem:
- Confirmar valores finais
- Alterar preços
- Aprovar condições comerciais

---

### 4️⃣ STATUS DO ATENDIMENTO

Controle manual de status.

**Regras:**
- Humanos podem alterar qualquer status
- IA não pode alterar status após AGUARDANDO_HUMANO
- Todo atendimento deve ser finalizado corretamente

---

### 5️⃣ MÉTRICAS

Indicadores mínimos:
- Total de leads
- Leads por nicho
- Conversões
- Não convertidos
- Tempo médio de atendimento
- Taxa de resposta

---

## 🔐 Regras de acesso

### Tipos de usuários

- **Admin**
  - Acesso total
- **Operador**
  - Atendimento e validação
- **Leitura**
  - Apenas visualização

---

## 🧠 Regras absolutas

- IA **não acessa** o painel
- IA **não valida valores**
- IA **não fecha vendas**
- Decisão final **sempre humana**

---

## 🧩 Multi-nicho

O painel deve permitir:
- Separação por nicho
- Filtro por cliente (SaaS)
- Operação white-label

---

## 🧾 Observação final

O Painel Admin é a **camada de segurança do sistema**.  
Ele garante que a IA opere como suporte, não como decisor.

Este documento é válido para **todos os nichos** do OSSO IA SYSTEM.
