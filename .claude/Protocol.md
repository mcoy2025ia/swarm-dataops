# Protocol.md · SWARM v2.1
# Reglas operativas del framework — reutilizables en cualquier proyecto

> Este archivo es el corazón replicable de SWARM.
> CLAUDE.md es específico al proyecto activo.
> Protocol.md aplica a cualquier proyecto que use el framework.

---

## 1. EL CICLO DE TRABAJO — 4 PASOS INMUTABLES

Cada interacción entre el Data Leader y un agente sigue este protocolo.
No hay excepciones. Si un agente saltea un paso, el handoff es inválido.

```
PASO 1 — SISTEMA RETOMA
  LangGraph activa el nodo del agente correspondiente
  El agente carga: CLAUDE.md + Phase-Log activo + fragmentos LanceDB del nodo
  El agente confirma en Logfire: sesión iniciada + contexto cargado + tokens usados

PASO 2 — AGENTE PROPONE
  Formato obligatorio de propuesta:
    QUÉ:     descripción concisa de la tarea a ejecutar
    CÓMO:    método técnico propuesto
    ASUME:   supuestos explícitos que el agente está haciendo
    RIESGOS: qué puede salir mal y cómo se detectaría
    NECESITA: qué requiere del Data Leader para ejecutar (si algo)

PASO 3 — DATA LEADER DECIDE
  Opciones exactas — no hay otras:
    ✅ Aprobado    → el agente ejecuta · LangGraph registra la transición
    🔄 Ajustar     → el agente modifica la propuesta según instrucción específica
    ❌ Rechazado   → el agente documenta en decision-log.md y cierra el nodo

PASO 4 — QUEDA DOCUMENTADO (automático)
  LangGraph registra la transición de estado
  El agente crea entrada en decision-log.md con: agente, fecha, decisión, justificación
  La entrada se vectoriza en LanceDB con los tags correspondientes
  Logfire registra: agente, nodo, duración, tokens, costo, status
```

---

## 2. MEMORY MODULAR ARCHITECTURE — PROTOCOLO MMA

### El problema que MMA resuelve

Un proyecto de datos de 11 semanas genera entre 50,000 y 150,000 tokens de contexto acumulado. Si el orquestador carga todo ese contexto en cada sesión, el costo escala exponencialmente y el modelo pierde foco en las decisiones recientes.

MMA resuelve esto con una regla simple: **el orquestador solo conoce lo que necesita para la sesión actual**. Todo lo histórico existe — pero en LanceDB, no en contexto activo.

### Las tres reglas

**Regla 1 — Solo Phase-Log activo en contexto**

```
EN CONTEXTO:
  CLAUDE.md           (~300 tokens · inmutable)
  Phase-Log-S[N].md   (~500-800 tokens · semana activa únicamente)
  
EN LANCEDB (no en contexto):
  Phase-Log-S[1].md   archivado como embeddings
  Phase-Log-S[2].md   archivado como embeddings
  ...
  Phase-Log-S[N-1].md archivado como embeddings
  decision-log.md     vectorizado por entrada
  Todos los demás     fragmentados y vectorizados
```

**Regla 2 — RAG selectivo por nodo**

Antes de ejecutar cualquier nodo, LangGraph determina qué contexto histórico necesita ese nodo específico y recupera solo esos fragmentos:

```python
# Lógica de recuperación por nodo — calibrada por prompt-engineer en S1
CONTEXT_BY_NODE = {
  "ingestion":         ["schema_decisions", "na_decisions_prev"],
  "feature_selection": ["na_decisions", "schema_silver", "quality_flags"],
  "modeling":          ["features_final", "cost_matrix_approved", "na_decisions"],
  "dashboard":         ["gold_schema", "cost_matrix", "threshold_approved"],
  "narrative":         ["business_context", "latam_mapping", "defensibility"],
}

# top-k fragmentos por categoría — calibrar según presupuesto
TOP_K = 3
```

**Regla 3 — Modelo correcto para cada tarea**

Ver Model-Routing Table en CLAUDE.md.
Violación = evento `[MCV-VIOLATION]` en Logfire.
Dos violaciones consecutivas del mismo agente = notificación al Data Leader.

### Ciclo de vida de un Phase-Log

```
INICIO DE SEMANA:
  1. Crear Phase-Log-S[N].md con plantilla estándar (ver sección 5)
  2. El Phase-Log anterior (S[N-1]) se archiva en LanceDB como embeddings
  3. El orquestador carga solo S[N].md — no S[N-1]

DURANTE LA SEMANA:
  4. Cada decisión de agente se agrega al Phase-Log activo en tiempo real
  5. Cada entrada se vectoriza simultáneamente en LanceDB (no al final)

CIERRE DE SEMANA:
  6. Auditor de Telemetría ejecuta MMA-AUDIT: verificar coherencia S[N] vs LanceDB
  7. Phase-Log S[N] se cierra con tag [COMPLETED] y se archiva en LanceDB
  8. Kill criteria de la fase evaluados con métricas de Logfire
  9. Si la fase cerró: Data Leader aprueba transición al siguiente nodo
```

---

## 3. HANDOFF VECTORIAL — PROTOCOLO DE ENTREGA ENTRE AGENTES

Cada output de agente que pasa al siguiente incluye un metadata-tag estructurado.
Este tag es lo que permite al agente receptor recuperar exactamente lo necesario
de LanceDB sin leer el historial completo.

### Formato estándar del metadata-tag

```yaml
# HANDOFF — incluir al final de cada output de agente
handoff:
  agente_origen: [nombre del agente]
  agente_destino: [nombre del agente]
  fase: S[N]
  nodo_origen: [nodo LangGraph]
  nodo_destino: [nodo LangGraph]
  
  lancedb_refs:
    - key: [lancedb://path/to/fragment]
      descripcion: [qué contiene este fragmento y por qué lo necesita el receptor]
    - key: [lancedb://path/to/fragment]
      descripcion: [...]
  
  phase_log_ref: Phase-Log-S[N].md#[sección específica]
  
  tokens_contexto_recomendados: [estimado para la siguiente tarea]
  
  condiciones_de_entrada_verificadas:
    - [criterio 1 que el receptor puede asumir como cumplido]
    - [criterio 2]
  
  advertencias:
    - [algo que el receptor debe saber antes de empezar]
```

### Ejemplo concreto — handoff data-engineer → data-scientist

```yaml
handoff:
  agente_origen: data-engineer
  agente_destino: data-scientist
  fase: S5
  nodo_origen: ingestion
  nodo_destino: feature_selection
  
  lancedb_refs:
    - key: lancedb://decisions/na/S4-S5
      descripcion: decisiones documentadas sobre cada columna con NA — leer antes de EDA
    - key: lancedb://schemas/silver/v1
      descripcion: schema validado de las 3 tablas Silver — usar para contrato de features
    - key: lancedb://quality/unreliable/S4
      descripcion: columnas marcadas como poco confiables — NO modelar sin aprobación
  
  phase_log_ref: Phase-Log-S5.md#reporte-salud-silver
  
  tokens_contexto_recomendados: ~600
  
  condiciones_de_entrada_verificadas:
    - Todos los tests dbt pasando (N/N) — verificado en Logfire
    - 3 tablas Silver en BigQuery con row counts documentados
    - DVC hash registrado y consistente con Bronze
  
  advertencias:
    - V127, V128, V130 tienen missing rate > 90% — decisión de eliminar ya en LanceDB
    - silver.identity_features tiene 15% de registros sin match con transactions — documentado
```

---

## 4. DECISION LOG — FORMATO ESTÁNDAR

Cada entrada en decision-log.md sigue este formato.
Entradas sin alguno de los campos obligatorios = deuda de documentación.

```markdown
## [FECHA] · [AGENTE] · [TIPO]

**Decisión:** [descripción concisa de qué se decidió]

**Justificación:** [por qué esta opción y no las alternativas]

**Alternativas consideradas:**
- [opción A] → descartada porque [razón]
- [opción B] → descartada porque [razón]

**Evidencia:** [query SQL / traza Logfire / resultado estadístico que respalda]

**Impacto en:** [qué agentes o fases downstream se ven afectados]

**Puntero LanceDB:** lancedb://decisions/[categoria]/[id]

**Aprobado por:** [Data Leader | consenso-enjambre]

**Tags:** [tipo: arquitectura|na|feature|modelo|costo|stack] [fase: S[N]] [status: activo|archivado]
```

### Tipos de decisión y sus tags

| Tag | Aplica cuando |
|---|---|
| `arquitectura` | Cambio en el stack, herramientas, o diseño del pipeline |
| `na` | Decisión sobre tratamiento de valores faltantes |
| `feature` | Variable incluida, descartada o transformada |
| `modelo` | Algoritmo, hiperparámetro, threshold, o métrica de evaluación |
| `costo` | Valores de FN_cost, FP_cost, o presupuesto del proyecto |
| `stack` | Herramienta aceptada o rechazada del sistema |
| `calibration` | Cambio en instrucciones de agente detectado via Logfire |
| `drift` | Deriva semántica o de modelo detectada y corregida |

---

## 5. PHASE-LOG — PLANTILLA ESTÁNDAR

Cada Phase-Log tiene esta estructura. El tamaño objetivo es 500–800 tokens.
Si supera 800 tokens, dividir en dos semanas o archivar decisiones ya cerradas en LanceDB.

```markdown
# Phase-Log · S[N] · [Nombre de la fase]

**Semana:** S[N]  
**Fecha inicio:** [fecha]  
**Fecha cierre:** [fecha | EN CURSO]  
**Agente owner:** [agente]  
**Agentes colaboradores:** [lista]  
**Nodo LangGraph:** [nodo]  
**Status:** EN CURSO | COMPLETADO | BLOQUEADO

---

## Estado al inicio de la semana

[2-3 frases: qué había al cierre de la semana anterior y qué debe lograrse esta semana]

## Contexto recuperado de LanceDB

[Lista de punteros y fragmentos recuperados al inicio de esta semana]
- lancedb://[path] → [qué se usó y para qué]

## Tareas y decisiones

### [Tarea 1]
- **Status:** completada | en progreso | bloqueada
- **Decisión tomada:** [descripción]
- **Puntero LanceDB:** lancedb://decisions/[id]
- **Traza Logfire:** [run_id o timestamp]

### [Tarea 2]
[mismo formato]

## Métricas de la semana (Logfire)

- Tokens consumidos: [N]
- Costo acumulado del piloto: $[X] USD
- Tests dbt en verde: [N/N]
- Violaciones MCV: [N]

## Kill criteria — ¿la fase puede cerrar?

- [ ] [criterio 1]: [medición] → ✅ cumplido | ⚠️ parcial | ❌ no cumplido
- [ ] [criterio 2]: [medición] → ✅ | ⚠️ | ❌
- [ ] [criterio 3]: [medición] → ✅ | ⚠️ | ❌

## Handoff

[metadata-tag de handoff al siguiente agente — ver sección 3]

## Para archivar en LanceDB

[Lista de fragmentos que deben vectorizarse al cerrar este Phase-Log]
- [fragmento] → lancedb://[path]
```

---

## 6. CRITERIOS DE ADMISIÓN DE HERRAMIENTAS

Toda herramienta o agente propuesto para entrar al sistema activo debe pasar estos tres filtros en orden. Si falla cualquiera, va al stack rechazado con justificación documentada.

```
FILTRO 1 — Problema real
  ¿Resuelve un problema documentado en el proyecto activo?
  ¿El problema existe ahora o es hipotético?
  Si es hipotético → rechazado · registrar en lancedb://stack/rejected/

FILTRO 2 — Costo de mantenimiento
  ¿Su costo de mantenimiento (mental, económico, tokens) es menor
  al valor que aporta en el horizonte del proyecto?
  ¿Agrega superficie de debugging sin ROI demostrable?
  Si el costo supera el valor → rechazado

FILTRO 3 — Coherencia con los 5 principios
  ¿Contradice Local-First? (depende de nube pagada innecesariamente)
  ¿Contradice Revisor-no-Ejecutor? (requiere que el Data Leader lo opere)
  ¿Contradice Contexto Persistente? (no se integra con LanceDB)
  ¿Contradice Trazabilidad Total? (no reporta a Logfire)
  ¿Contradice Replicable por Diseño? (no funciona en el template base)
  Si contradice cualquiera → rechazado
```

---

## 7. PRESUPUESTO — PROTOCOLO DE CONTROL

El presupuesto es una restricción de diseño, no una estimación.

### Alertas escalonadas (configurar en Logfire al inicio del proyecto)

```
$0   → inicio · Logfire empieza a trackear
$20  → (67%) alerta informativa · revisar proyección al cierre
$24  → (80%) alerta crítica · Data Leader notificado · aprobación para continuar
$28  → (93%) modo emergencia · suspender APIs externas · solo local
$30  → hard stop · piloto pausado hasta siguiente iteración
```

### Prioridad de reducción de costo si se activa alerta en $24

```
1. Suspender llamadas a DeepSeek — sustituir por Claude Sonnet para tareas pendientes
2. Reducir Cloud Run a min_instances=0 si no estaba ya así
3. Revisar si hay tareas de Groq que puedan hacerse con Haiku
4. Evaluar si algún hito puede descalificarse sin impactar los entregables públicos
5. Documentar la decisión en decision-log.md con tag [BUDGET-CONSTRAINT]
```

---

## 8. ARRANQUE DE UN NUEVO PROYECTO CON SWARM

Para clonar SWARM en un proyecto nuevo, estos son los únicos pasos:

```
PASO 1 — Repositorio (5 min)
  git clone swarm-template
  Reemplazar ieee-cis en CLAUDE.md por el nombre del nuevo proyecto
  Definir dataset, objetivo y métrica maestra

PASO 2 — Infraestructura de memoria (10 min)
  Inicializar LanceDB local
  Ejecutar script de fragmentación del PRD del nuevo proyecto
  Verificar que las 4 categorías base existen: decisions/ · schemas/ · quality/ · phase-logs/

PASO 3 — Logfire (5 min)
  Crear proyecto en Logfire
  Configurar las 5 alertas de presupuesto
  Verificar que el SDK recibe eventos de prueba

PASO 4 — Calibración (10 min)
  Ejecutar prompt-engineer S1:
    - Revisar Model-Routing Table para el nuevo proyecto
    - Ajustar top-k de RAG si el dataset tiene características diferentes
    - Definir los 6 nodos del grafo con sus condiciones de entrada/salida

PASO 5 — Arranque (0 min adicionales)
  El sistema está listo para S1
  Total: < 30 minutos desde cero
```

---

*SWARM v2.1 · Protocol.md · Framework open source para Data Leaders*  
*Este documento es la parte reutilizable — CLAUDE.md es la parte específica del proyecto*
