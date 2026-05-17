# Workspace — Código real de Stallen

Acá vive el código real del producto Stallen.

## Estructura tentativa (a definir cuando arranque feature 1)

```
workspace/
├── apps/
│   ├── web/        # Frontend Next.js + Vercel
│   └── (otros si aplican)
├── packages/
│   ├── ui/         # Componentes compartidos
│   ├── lib/        # Utilities compartidas
│   └── types/      # TypeScript types compartidos
├── supabase/
│   ├── migrations/ # Migraciones SQL
│   ├── functions/  # Edge functions
│   └── seed/       # Seeds para development
├── tests/          # Tests E2E (adversariales A15)
└── infra/          # IaC si aplica (Terraform, etc.)
```

**Esto se define al arrancar feature 1**, no preventivamente.

## Estado actual

Vacío — código real arranca con feature 1 del HORIZONTE H-1.3.
