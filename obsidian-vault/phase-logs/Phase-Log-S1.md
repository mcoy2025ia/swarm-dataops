# Phase-Log · S1 · Setup v2.1

**Semana:** S1  
**Fecha inicio:** [completar al arrancar]  
**Fecha cierre:** [completar al cerrar]  
**Agente owner:** prompt-engineer  
**Agentes colaboradores:** auditor-de-telemetria  
**Nodo LangGraph:** `calibration`  
**Status:** EN CURSO

---

## Objetivo de la semana

Dejar el sistema SWARM operativo antes de tocar un solo dato de IEEE-CIS.
Al cierre de S1, el enjambre puede arrancar S2 sin configuración adicional.

Definición de "operativo":
- LanceDB inicializado con el contexto base del proyecto
- LangGraph skeleton con los 6 nodos y sus transiciones definidas
- Logfire recibiendo eventos de todos los agentes
- Model-Routing Table activa y validada
- Los 7 archivos `.md` de agentes cargados y coherentes con CLAUDE.md

---

## Estado al inicio

Repositorio clonado. CLAUDE.md, Protocol.md y los 7 skills de agentes existen como archivos estáticos. Ningún sistema de memoria ni orquestación está inicializado. El proyecto no puede arrancar hasta que esta semana cierre.

---

## Contexto recuperado de LanceDB

```
— LanceDB no está inicializado aún —
Esta es la semana que lo inicializa.
Al cierre de S1 este bloque tendrá punteros reales.
```

---

## Tareas

### T1 · Inicializar LanceDB

**Status:** pendiente  
**Agente:** prompt-engineer  
**Descripción:** Crear la estructura de colecciones en LanceDB y fragmentar los documentos base del proyecto.

Documentos a fragmentar y vectorizar:

```
CLAUDE.md              → colección: project/config
Protocol.md            → colección: project/rules  
PRD v2.1               → colección: project/prd (por sección)
agents/*.md            → colección: agents/prompts (un fragmento por agente)
decision-log.md (base) → colección: decisions/ (vacío al inicio, crece con el proyecto)
```

Verificación:
```python
# Test de recuperación — ejecutar al finalizar T1
queries_de_prueba = [
    "principios inmutables del framework",
    "model routing table deepseek",
    "criterios de rechazo de herramientas",
    "protocolo handoff vectorial",
    "budget hard cap alertas",
]
# Cada query debe devolver el fragmento correcto con score > 0.80
```

**Decisión:** [completar al ejecutar]  
**Puntero LanceDB:** lancedb://project/config · lancedb://project/rules  
**Traza Logfire:** [run_id al completar]

---

### T2 · Configurar LangGraph skeleton

**Status:** pendiente  
**Agente:** prompt-engineer  
**Descripción:** Definir los 6 nodos del grafo con sus condiciones de transición.

```python
# Estructura del grafo — definir en langgraph_config.py
nodos = {
    "calibration":       {"owner": "prompt-engineer",    "fase": "S1-S3"},
    "ingestion":         {"owner": "data-engineer",      "fase": "S4"},
    "feature_selection": {"owner": "data-scientist",     "fase": "S5"},
    "modeling":          {"owner": "ml-engineer",        "fase": "S7-S8"},
    "dashboard":         {"owner": "data-analyst",       "fase": "S6-S10"},
    "narrative":         {"owner": "business-analyst",   "fase": "S10"},
}

# Transiciones con condiciones verificables
transiciones = {
    "calibration → ingestion":          "tests_end_to_end_3_agentes == PASS",
    "ingestion → feature_selection":    "dbt_tests_bronze == ALL_PASS AND logfire_telemetry == ACTIVE",
    "feature_selection → modeling":     "features_V_en_lancedb == TRUE AND matriz_costos_aprobada == TRUE",
    "modeling → dashboard":             "modelo_en_mlflow_registry == TRUE AND threshold_aprobado == TRUE",
    "dashboard → narrative":            "dashboard_url_estable == TRUE AND llamaindex_queries == PASS",
    "narrative → close":                "certificado_defensibilidad == EMITIDO AND deck_aprobado == TRUE",
}

# Rutas de escape
rutas_escape = {
    "3_fallos_dbt_consecutivos":    "pausar ingestion → reporte al Data Leader",
    "deepseek_timeout":             "usar Sonnet para variables no-V → marcar V pendientes",
    "budget_24usd":                 "pausar APIs externas → notificar Data Leader",
    "budget_30usd":                 "hard stop → piloto pausado",
}
```

**Decisión:** [completar al ejecutar]  
**Puntero LanceDB:** lancedb://project/langgraph  
**Traza Logfire:** [run_id al completar]

---

### T3 · Activar Pydantic Logfire

**Status:** pendiente  
**Agente:** auditor-de-telemetria  
**Descripción:** Inicializar Logfire y configurar las 5 alertas de presupuesto.

```python
# Alertas a configurar en Logfire — obligatorias antes de S2
alertas = [
    {"umbral": 20.00, "tipo": "informativa",  "accion": "revisar proyección al cierre"},
    {"umbral": 24.00, "tipo": "critica",      "accion": "notificar Data Leader · aprobación requerida"},
    {"umbral": 28.00, "tipo": "emergencia",   "accion": "suspender APIs externas · solo local"},
    {"umbral": 30.00, "tipo": "hard_stop",    "accion": "pausar piloto · siguiente iteración"},
]

# Paneles del dashboard Logfire a configurar
paneles = [
    "Panel 1: Budget acumulado vs $30 USD",
    "Panel 2: Estado del grafo LangGraph",
    "Panel 3: Calidad del pipeline (cuando S4+)",
    "Panel 4: Decisiones pendientes de aprobación del Data Leader",
]

# Evento de prueba — verificar que Logfire recibe
logfire.info("swarm.session.start",
    proyecto="ieee-cis-fraud",
    fase="S1",
    agente="auditor-de-telemetria",
    tokens_contexto=850,
    costo_sesion_estimado=0.002
)
```

**Decisión:** [completar al ejecutar]  
**Traza Logfire:** [confirmar evento de prueba visible en dashboard]

---

### T4 · Validar Model-Routing Table

**Status:** pendiente  
**Agente:** prompt-engineer  
**Descripción:** Confirmar que la Model-Routing Table de CLAUDE.md es ejecutable — no solo declarativa.

Test de validación por modelo:

```python
# Groq — latencia de validación de estado
groq_test = groq.complete("Estado del nodo calibration: ¿condiciones de salida cumplidas?")
assert groq_test.latencia_ms < 300, "Groq no cumple el requisito de velocidad para LangGraph"

# DeepSeek — razonamiento sobre variable V de prueba
deepseek_test = deepseek.complete(
    "Variable V001: missing_rate=0.72, correlacion_isFraud=0.043, p_value=0.31. "
    "¿Conservar o descartar para modelado de fraude? Razona paso a paso."
)
assert deepseek_test.tiene_cadena_pensamiento == True

# Claude Haiku — confirmación simple
haiku_test = claude_haiku.complete("¿El Phase-Log S1 está en contexto? Responde solo: sí o no.")
assert len(haiku_test.respuesta.split()) <= 3

# Logfire — registrar resultado de cada test
logfire.info("swarm.model_routing.validation", resultados=resultados_tests)
```

**Decisión:** [completar al ejecutar — registrar modelos que no pasaron y acción tomada]  
**Puntero LanceDB:** lancedb://project/model-routing-validated  
**Traza Logfire:** [run_id]

---

### T5 · Test end-to-end con 3 agentes

**Status:** pendiente  
**Agente:** prompt-engineer  
**Descripción:** Ejecutar el ciclo completo de 4 pasos con prompt-engineer, data-engineer y auditor-de-telemetria para verificar que el grafo, LanceDB y Logfire funcionan integrados.

Escenario de prueba:
```
1. prompt-engineer propone: "Fragmentar CLAUDE.md en LanceDB"
2. Data Leader aprueba
3. prompt-engineer ejecuta y registra en Logfire
4. Handoff vectorial al data-engineer con metadata-tag correcto
5. data-engineer consulta LanceDB con los punteros del handoff
6. Auditor verifica en Logfire que el ciclo completo ocurrió
7. decision-log.md tiene la entrada con los 4 campos obligatorios
```

Criterio de éxito: el ciclo completo ocurre sin intervención manual del Data Leader más allá de la aprobación en el paso 2.

**Decisión:** [completar al ejecutar]  
**Traza Logfire:** [run_id del ciclo completo]

---

## Métricas de la semana (completar al cierre)

```
Tokens consumidos S1:          [N]
Costo acumulado del piloto:    $[X] USD  (objetivo: < $1 USD en S1)
Violaciones MCV:               [N]       (objetivo: 0)
Tests Model-Routing:           [N/4]     (objetivo: 4/4)
Fragmentos en LanceDB:         [N]       (objetivo: > 50)
```

---

## Kill criteria — ¿S1 puede cerrar?

- [ ] LanceDB inicializado · test de recuperación con 5 queries pasando con score > 0.80
- [ ] LangGraph skeleton con 6 nodos y transiciones definidas en código
- [ ] Logfire dashboard activo · 4 alertas de budget configuradas · evento de prueba visible
- [ ] Model-Routing Table validada · los 4 modelos respondiendo en sus rangos
- [ ] Test end-to-end de 3 agentes completado · ciclo de 4 pasos sin intervención manual
- [ ] Costo S1 ≤ $1 USD

Si algún criterio está en ⚠️ parcial, documentar el riesgo y proponer al Data Leader si se avanza de todas formas o se extiende S1.

---

## Handoff a S2

```yaml
handoff:
  agente_origen: prompt-engineer
  agente_destino: prompt-engineer  # S2 sigue siendo del PE
  fase: S1 → S2
  nodo_origen: calibration
  nodo_destino: calibration  # el nodo no cambia hasta S3

  lancedb_refs:
    - key: lancedb://project/config
      descripcion: CLAUDE.md fragmentado — base de todo el contexto del proyecto
    - key: lancedb://project/rules
      descripcion: Protocol.md fragmentado — reglas operativas del framework
    - key: lancedb://project/langgraph
      descripcion: configuración del grafo — nodos, transiciones, rutas de escape
    - key: lancedb://project/model-routing-validated
      descripcion: resultado del test de los 4 modelos — usar para S2

  phase_log_ref: Phase-Log-S1.md#test-end-to-end
  tokens_contexto_recomendados: ~700

  condiciones_de_entrada_verificadas:
    - LanceDB operativo con fragmentos base del proyecto
    - Logfire recibiendo eventos de todos los agentes
    - Model-Routing Table validada en código

  advertencias:
    - Si algún kill criteria quedó en ⚠️, documentarlo aquí antes de archivar
    - Los Phase-Logs históricos no se cargan en S2 — consultar via LanceDB
```

---

## Para archivar en LanceDB al cierre

```
Phase-Log-S1 completo     → lancedb://phase-logs/S1
Decisiones T1–T5          → lancedb://decisions/S1/setup
Resultado Model-Routing   → lancedb://project/model-routing-validated
Config LangGraph          → lancedb://project/langgraph
Test end-to-end resultado → lancedb://decisions/S1/e2e-test
```

---

*Phase-Log S1 · SWARM v2.1 · IEEE-CIS Fraud Detection*
