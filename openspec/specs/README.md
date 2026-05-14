# Specs source of truth

Este directorio contiene las specs aprobadas y mergeadas (source of truth).

Las specs se organizan por **domain** (ver `../config.yaml` sección `domains`).

Estructura típica:

```
specs/
├── departamento-core/
│   └── spec.md
├── mcp-servers/
│   └── spec.md
└── ...
```

Las specs vacías (placeholders) NO se versionan. Solo se crean cuando hay una change archivada que produce contenido para ese domain.
