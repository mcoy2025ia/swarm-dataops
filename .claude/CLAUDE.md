# CLAUDE.md · SWARM v2.1
# IEEE-CIS Fraud Detection Pilot

> Este archivo es inmutable. No se edita durante el piloto.
> Lo que cambia semana a semana vive en el Phase-Log activo.
> Tamaño objetivo: < 300 tokens en contexto.

---

## INSTRUCCIÓN DE ARRANQUE

Al inicio de cada sesión, ejecutar en este orden:

```
1. Leer ESTE archivo (CLAUDE.md) — reglas inmutables
2. Leer Phase-Log-S[N].md — solo la semana activa
3. NO cargar Phase-Logs históricos — están en LanceDB
4. Si necesitas contexto histórico → consultar LanceDB con la query específica
5. Reportar a Logfire: sesión iniciada + Phase-Log cargado + tokens de contexto
```

Si no sabes qué semana es la activa, consultar:
```
lancedb.query("fase activa proyecto ieee-cis")
```

---

## IDENTIDAD DEL PROYECTO

**Framework:** SWARM v2.1 — open source para Data Leaders  
**Piloto:** IEEE-CIS Fraud Detection (Vesta Corporation · Kaggle)  
**Objetivo:** Detectar fraude transaccional y traducir el resultado a USD ahorrados  
**Métrica maestra:** Ahorro neto en USD via Matriz de Costos Asimétricos — no AUC  
**Entregables públicos:** Framework cloneable · Dashboard C-level · Endpoint de scoring  
**Budget hard cap:** $30 USD — alerta automática Logfire al 80% ($24 USD)  
**Duración:** 11 semanas · 2–3 horas/día

---

## LOS 5 PRINCIPIOS — INMUTABLES

Toda decisión técnica, todo agente, toda herramienta se evalúa contra estos cinco. Si contradice alguno, no entra al sistema activo.

**1. Local-First**
Todo corre en la máquina del Data Leader. La nube es extensión, no dependencia crítica. Sin costos fijos, sin lock-in.

**2. Revisor, no Ejecutor**
El Data Leader aprueba o rechaza en los nodos de aprobación. Los agentes proponen y ejecutan. El Data Leader no escribe código de pipeline.

**3. Contexto Persistente**
Ninguna sesión empieza desde cero. El estado vive en el Phase-Log activo + LanceDB. El sistema sabe dónde quedó.

**4. Trazabilidad Total**
Cada decisión tiene autor, fecha, justificación y resultado en decision-log.md. Auditable seis meses después sin perder contexto.

**5. Replicable por Diseño**
SWARM es una plantilla. Nuevo proyecto en < 30 minutos. IEEE-CIS es el primer proyecto que la valida — no el producto final.

---

## MODEL-ROUTING TABLE — VINCULANTE

Esta tabla es la única fuente de verdad sobre qué modelo usa cada agente. Desviación = evento de violación en Logfire.

| Tarea | Modelo | Razón |
|---|---|---|
| Feature Selection V1–V339 | DeepSeek R1/V3 | Cadena-de-pensamiento auditable — única tarea que lo justifica |
| Validaciones de estado LangGraph | Groq LPU | >500 t/s — latencia crítica para el grafo |
| Confirmaciones simples · formato · validaciones cortas | Claude Haiku | Costo mínimo para tareas triviales |
| Todo lo demás | Claude Sonnet | Estándar del sistema |

---

## PUNTEROS LANCEDB

No cargar el contenido — solo usar estos punteros para consultas específicas.

```
lancedb://decisions/         → todas las decisiones del proyecto
lancedb://decisions/na/      → decisiones sobre NAs por columna
lancedb://decisions/features/ → feature selection · variables descartadas
lancedb://decisions/models/  → threshold · costos asimétricos aprobados
lancedb://schemas/silver/    → schema validado de tablas Silver
lancedb://schemas/gold/      → schema y lógica de los 5 Gold Marts
lancedb://quality/           → columnas poco confiables · alertas de calidad
lancedb://phase-logs/        → Phase-Logs históricos archivados (S1, S2, ...)
lancedb://stack/rejected/    → herramientas rechazadas con justificación
lancedb://agents/prompts/    → instrucciones base de cada agente
```

---

## STACK ACTIVO

```
Orquestación:    Claude Code · LangGraph · Groq LPU
Razonamiento:    DeepSeek R1/V3 (solo V***) · Claude Sonnet
Memoria:         LanceDB (vectorial local) · Obsidian Vault
Observabilidad:  Pydantic Logfire
Procesamiento:   Airflow · dbt Core · Python 3.11 · DuckDB (local)
ML:              XGBoost · LightGBM · MLflow · DVC · SHAP · GPU RTX 4060
Semántica:       LlamaIndex sobre Gold Marts
Infraestructura: GCP — BigQuery · Cloud Storage · Cloud Run · Artifact Registry
CI/CD:           GitHub Actions
Presentación:    Streamlit (2 apps) · FastAPI · Deck 5 slides
```

## STACK RECHAZADO — NO PROPONER

`CrewAI` · `SQLMesh` · `Spark` · `Kafka` · `Databricks` · `Pinecone` · `Evidence.dev` · `Checkov` · `TFLint`

Justificaciones completas en `lancedb://stack/rejected/`

---

## AGENTES ACTIVOS — 7

| Agente | Fases owner | Modelo |
|---|---|---|
| prompt-engineer | S1–S3 | Sonnet |
| auditor-de-telemetria | S1–S11 | Sonnet |
| data-engineer | S4 · S6 | Sonnet |
| data-scientist | S5 · S7 | Sonnet + DeepSeek (V***) |
| ml-engineer | S8 · S9 | Sonnet |
| data-analyst | S6 · S10 | Sonnet |
| business-analyst | S10 | Sonnet |

Skills completos en `lancedb://agents/prompts/`

---

## PROTOCOLO MMA — REGLAS DE CARGA

**Regla 1 — Solo Phase-Log activo en contexto**
El orquestador carga únicamente el Phase-Log de la semana en curso.
Phase-Logs históricos = embeddings en `lancedb://phase-logs/` — no en contexto.

**Regla 2 — RAG selectivo**
Antes de ejecutar cualquier nodo, LangGraph evalúa qué contexto histórico
necesita ese nodo específico. Solo los fragmentos top-k relevantes se inyectan.
El prompt-engineer calibra el top-k en S1.

**Regla 3 — Modelo correcto para cada tarea**
Ver Model-Routing Table arriba. Violación = evento en Logfire.
El Auditor de Telemetría notifica al Data Leader si hay dos violaciones
consecutivas del mismo agente.

**Reducción objetivo de tokens:** ≥ 65% vs carga completa del proyecto.
Medido por Logfire. Reportado semanalmente por el Auditor de Telemetría.

---

## NODOS DE APROBACIÓN — DATA LEADER

El grafo no avanza sin aprobación explícita del Data Leader en estos puntos:

```
Bronze    → Feature Selection   : calidad de datos suficiente para modelar
Feat.Sel. → Modelado             : decisiones V*** estadísticamente defendibles  
Modelado  → Dashboard            : threshold óptimo válido en contexto Latam
Dashboard → Narrativa            : dashboard responde las 3 preguntas del C-Level
Narrativa → Cierre               : deck inexpugnable · Certificado de Defensibilidad
```

---

## HITOS PÚBLICOS

```
Hito 1 — S6  : Dashboard C-level en Cloud Run · URL pública
Hito 2 — S8  : Endpoint de scoring en vivo · FastAPI · latencia p95 < 500ms
Hito 3 — S11 : Framework público · README · 3 posts LinkedIn
```

---

## ARCHIVOS QUE SÍ SE CARGAN EN CONTEXTO

```
CLAUDE.md              ← este archivo · siempre · < 300 tokens
Phase-Log-S[N].md      ← solo semana activa · < 800 tokens
```

## ARCHIVOS QUE NO SE CARGAN — CONSULTAR VÍA LANCEDB

```
Phase-Log-S[1..N-1].md   → lancedb://phase-logs/
decision-log.md           → lancedb://decisions/
agent-prompts/            → lancedb://agents/prompts/
project-health.md         → lancedb://health/current/
```

---

*SWARM v2.1 · IEEE-CIS Fraud Detection · Manuel Alberto Coy Benavides · Bogotá 2025*
