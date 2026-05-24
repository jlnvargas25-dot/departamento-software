-- Fixture: MIGRATION-NAMING (filename 0001_initial.sql -> YYYYMMDDHHmm_initial.sql)
-- El patron a fixear es el FILENAME, no el contenido. Contenido es valido SQL.

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX users_email_idx ON users(email);
