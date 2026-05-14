# Domain Captures

Capturas estructuradas del dominio del negocio, producidas por la skill `sigma-capture-domain`.

## Propósito

Aplicación del **3° principio rector** (dominio-first): no se implementa lógica de negocio sin que el dominio esté capturado **explícitamente** primero.

Cada archivo en este directorio representa el **contrato del dominio** para un módulo, feature, o componente. Los validators, tests, y código deben respetar este contrato.

## Convención de nombres

`<nombre-en-kebab-case>-domain.md`

Ejemplos:
- `validator-r01-domain.md` — dominio del validator R01 de SigmaControl
- `feature-soft-delete-domain.md` — dominio de la feature soft delete
- `module-billing-domain.md` — dominio del módulo de facturación

## Estructura obligatoria

Cada captura tiene 10 secciones (ver `.claude/skills/sigma-capture-domain/SKILL.md`):

1. Propósito del módulo
2. Entidades
3. Reglas del negocio (BR-N)
4. Invariantes (INV-N)
5. Casos edge (EC-N)
6. Glosario
7. Asunciones declaradas
8. Lo que NO está en scope
9. Preguntas pendientes
10. Referencias

## Estados de una captura

- **borrador**: recién capturada, sin validar
- **revisado**: leída con stakeholder o por humano informado
- **aprobado**: lista para usar como contrato de implementación
- **superado**: existe versión más nueva (referencia desde la nueva al ID superado)

## Cómo invocar la skill

Dentro de Claude Code en este repo:

```
Capturá el dominio de <nombre> usando la skill sigma-capture-domain
```

O explícitamente:

```
/sigma-capture-domain <nombre>
```

La skill guía el proceso paso a paso. NO auto-aprueba — el usuario decide cuándo marcar la captura como aprobada.

## Integración con OpenSpec

Cuando una change OpenSpec toca lógica de negocio, su `proposal.md` DEBE referenciar la captura de dominio correspondiente. Si no existe, hay que capturarla ANTES de escribir el proposal.

Pattern:
```
1. /sigma-capture-domain <nombre>
2. Validar captura con stakeholder (humano)
3. Marcar captura como "aprobada"
4. sdd-propose para la change → referencia el dominio capturado
```

## Referencias

- Skill: `.claude/skills/sigma-capture-domain/SKILL.md`
- AGENTS.md regla G-7 (Captura de dominio explícita)
- 3° principio rector en `CLAUDE.md`
- ADR-005 Plan Sprint 2 (T1)
