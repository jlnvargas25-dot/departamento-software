# Features de Stallen

Cada feature de Stallen vive en su propia carpeta.

## Convención

```
features/
├── feature-001-<slug>/
│   ├── spec.md         # qué se construye
│   ├── plan.md         # cómo se construye
│   ├── tasks.md        # descomposición
│   ├── implementation/ # código del feature
│   ├── tests/          # tests adversariales A15
│   └── retro.md        # retrospectiva post-implementación
├── feature-002-<slug>/
└── ...
```

## Slug

Formato sugerido: `feature-NNN-<dominio>-<accion>`

Ejemplos:
- `feature-001-auth-login`
- `feature-002-inventory-crud-products`
- `feature-003-caja-daily-summary`

## Estado actual

Vacío — primer feature pendiente (H-1.3 del HORIZONTE).
