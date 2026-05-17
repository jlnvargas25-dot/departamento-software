# Skills específicos de Stallen

Skills `.claude/skills/` específicos del proyecto Stallen (overrides o
adiciones al Framework universal).

## Diferencia con Framework `.claude/skills/`

- **Framework**: skills universales (`sigma-capture-domain` etc.)
- **Aquí**: skills específicos del dominio/stack Stallen

## Convención

Naming: `stallen-<nombre>` para evitar collision con framework

Sugeridos para Sprint 2+ (si NO los cubre Spec Kit/Supabase Agent Skills):
- `stallen-multitenancy-bootstrap` — huevo-gallina RLS multi-tenant
- `stallen-sql-rules` — reglas SQL específicas Stallen (sobre Framework)
- `stallen-deploy` — workflow deploy Supabase + Vercel

## Estado actual

Vacío — skills específicos se crean cuando se identifique gap concreto
con respecto al ecosistema + Framework universal.
