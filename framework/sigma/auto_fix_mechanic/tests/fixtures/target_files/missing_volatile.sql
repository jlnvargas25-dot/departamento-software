-- Fixture: PGSQL-MISSING-VOLATILE (funciones plpgsql sin VOLATILE/STABLE/IMMUTABLE marker)

-- Violation 1: set_updated_at sin VOLATILE
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Violation 2: tenant_id_from_jwt sin marker
CREATE OR REPLACE FUNCTION tenant_id_from_jwt()
RETURNS UUID AS $$
BEGIN
    RETURN (auth.jwt() ->> 'tenant_id')::UUID;
END;
$$ LANGUAGE plpgsql;

-- Control negativo: esta funcion ya tiene STABLE explicito y NO deberia ser fixeada
CREATE OR REPLACE FUNCTION get_current_tenant()
RETURNS UUID AS $$
BEGIN
    RETURN current_setting('app.tenant_id')::UUID;
END;
$$ LANGUAGE plpgsql STABLE;
