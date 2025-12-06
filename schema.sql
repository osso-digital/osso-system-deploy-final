-- schema.sql (execute no Postgres)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Usuários/Admin
CREATE TABLE users (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  name text,
  email text UNIQUE,
  password_hash text,
  role text DEFAULT 'admin',
  created_at timestamptz DEFAULT now()
);

-- Leads (universal)
CREATE TABLE leads (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  nome text NOT NULL,
  email text,
  whatsapp text NOT NULL,
  origem text,           -- landing_tattoo, landing_vet, ads, whatsapp
  nicho text DEFAULT 'tattoo',
  mensagem text,
  status text DEFAULT 'NOVO', -- NOVO, ORCAMENTO_GERADO, RESPONDIDO, AGENDADO, CANCELADO
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- Atendimentos / histórico
CREATE TABLE atendimentos (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  lead_id uuid REFERENCES leads(id) ON DELETE CASCADE,
  tipo text, -- ORCAMENTO, AGENDAMENTO, SEGUIMENTO
  dados jsonb, -- payload completo do atendimento
  status text,
  created_at timestamptz DEFAULT now()
);

-- Orçamentos
CREATE TABLE orcamentos (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  atendimento_id uuid REFERENCES atendimentos(id) ON DELETE CASCADE,
  valor_final numeric,
  servico_base text,
  valor_bruto numeric,
  adicionais jsonb,
  parametros jsonb,
  created_at timestamptz DEFAULT now()
);

-- Agendamentos
CREATE TABLE agendamentos (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  atendimento_id uuid REFERENCES atendimentos(id) ON DELETE CASCADE,
  lead_id uuid REFERENCES leads(id) ON DELETE CASCADE,
  profissional text,
  data_inicio timestamptz,
  data_fim timestamptz,
  status text DEFAULT 'PENDENTE', -- PENDENTE, CONFIRMADO, CANCELADO, CONCLUIDO
  horario_confirmado boolean DEFAULT false,
  created_at timestamptz DEFAULT now()
);

-- Disponibilidade (regras do estúdio)
CREATE TABLE disponibilidade (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  dia_semana int, -- 0..6
  inicio time,
  fim time,
  intervalo_minutos int DEFAULT 30
);

-- Upload de mídias (Spaces)
CREATE TABLE midias (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  lead_id uuid REFERENCES leads(id) ON DELETE SET NULL,
  atendimento_id uuid REFERENCES atendimentos(id) ON DELETE SET NULL,
  filename text,
  url text,
  storage_key text,
  tipo text, -- imagem, foto-referencia, documento
  created_at timestamptz DEFAULT now()
);

-- Anamnese e termos
CREATE TABLE anamneses (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  lead_id uuid REFERENCES leads(id) ON DELETE CASCADE,
  respostas jsonb,
  termo_aceito boolean DEFAULT false,
  termo_versao text,
  termo_hash text,
  created_at timestamptz DEFAULT now()
);

-- Logs de notificações (WhatsApp/Email)
CREATE TABLE notificacoes (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  tipo text,
  destinatario text,
  mensagem text,
  meta jsonb,
  status text DEFAULT 'PENDENTE',
  created_at timestamptz DEFAULT now()
);
