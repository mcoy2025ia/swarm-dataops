# decision-log.md · SWARM v2.1
# IEEE-CIS Fraud Detection Pilot

> Registro inmutable de todas las decisiones del proyecto.
> Cada entrada tiene: agente · fecha · decisión · justificación · evidencia · puntero LanceDB.
> Entradas sin alguno de esos campos = deuda de documentación.
> Mantenido por: auditor-de-telemetria · alimentado por todos los agentes.

---

## Formato de entrada

```markdown
## [FECHA] · [AGENTE] · [TIPO]

**Decisión:** descripción concisa
**Justificación:** por qué esta opción y no las alternativas
**Alternativas consideradas:** opción A → descartada porque X · opción B → descartada porque Y
**Evidencia:** query SQL / traza Logfire / resultado estadístico
**Impacto en:** agentes o fases downstream afectados
**Puntero LanceDB:** lancedb://decisions/[categoria]/[id]
**Aprobado por:** Data Leader | consenso-enjambre
**Tags:** [tipo] [fase] [status: activo|archivado]
```

---

## RONDA 0 · Decisiones de Diseño del Framework

### 2025-S0 · orquestador · stack

**Decisión:** Adoptar LangGraph como framework de orquestación de agentes.  
**Justificación:** Convierte el flujo de handoffs manuales en una máquina de estados determinista. El Data Leader deja de ser mensajero entre agentes — ese era el cuello de botella principal de v1.2. LangGraph hace las transiciones verificables y registrables en Logfire.  
**Alternativas consideradas:** CrewAI → rechazado (duplica el rol de orquestación con LangGraph · rompe el principio de agentes como archivos .md versionables en Git).  
**Evidencia:** PRD v2.1 · sección arquitectura · decisión de diseño documentada.  
**Impacto en:** todos los agentes · protocolo de handoff · ciclo de trabajo completo.  
**Puntero LanceDB:** lancedb://stack/rejected/crewai · lancedb://decisions/framework/langgraph  
**Aprobado por:** Data Leader  
**Tags:** stack S0 activo

---

### 2025-S0 · orquestador · stack

**Decisión:** Adoptar LanceDB como sistema de memoria vectorial del enjambre.  
**Justificación:** Resuelve el problema de Contexto Persistente siendo local-first ($0 de costo). Pinecone fue evaluado y rechazado — resuelve el mismo problema pero con costo mensual y dependencia cloud, contradiciendo el Principio 1 del framework.  
**Alternativas consideradas:** Pinecone → rechazado (costo mensual + cloud dependency · contradice Local-First) · ChromaDB → descartado (madurez menor · ecosistema más limitado para RAG en producción).  
**Evidencia:** PRD v2.1 · principio Local-First · comparativa de costo.  
**Impacto en:** prompt-engineer (diseño MMA) · todos los agentes (recuperación de contexto).  
**Puntero LanceDB:** lancedb://stack/rejected/pinecone · lancedb://decisions/framework/lancedb  
**Aprobado por:** Data Leader  
**Tags:** stack S0 activo

---

### 2025-S0 · orquestador · stack

**Decisión:** Adoptar Pydantic Logfire como sistema de observabilidad nativa.  
**Justificación:** En v1.2 fue rechazado porque no había agentes corriendo desatendidos — sin flujos autónomos, el monitoreo no era necesario. En v2.1 LangGraph ejecuta flujos autónomos: el contexto cambió, no el criterio. El Auditor de Telemetría necesita una fuente de verdad para el control de budget en tiempo real.  
**Alternativas consideradas:** Monitoring manual → rechazado (no escalable con 7 agentes corriendo) · Prometheus/Grafana → rechazado (overhead de setup innecesario para el scope del piloto).  
**Evidencia:** PRD v2.1 · cambio de rol Project-Manager → Auditor de Telemetría.  
**Impacto en:** auditor-de-telemetria · todos los agentes (instrumentación obligatoria).  
**Puntero LanceDB:** lancedb://stack/rejected/logfire-v12 · lancedb://decisions/framework/logfire  
**Aprobado por:** Data Leader  
**Tags:** stack S0 activo

---

### 2025-S0 · orquestador · stack

**Decisión:** Adoptar DeepSeek R1/V3 exclusivamente para Feature Selection de variables V1–V339.  
**Justificación:** Las 339 variables V de Vesta Corporation están enmascaradas — sin documentación pública. El razonamiento cadena-de-pensamiento de DeepSeek hace cada decisión de inclusión/exclusión auditable. No es sustituible por Claude Sonnet para esta tarea específica porque la trazabilidad del razonamiento es el requisito, no solo el resultado.  
**Alternativas consideradas:** Claude Sonnet para todo → rechazado (razonamiento no visible · decisiones sobre V*** no son auditables) · análisis manual → rechazado (339 variables × análisis individual es inviable en 11 semanas).  
**Evidencia:** PRD v2.1 · dataset IEEE-CIS · 339 variables V sin documentación pública.  
**Impacto en:** data-scientist (S5) · model-routing table · presupuesto (~$3–5 USD del piloto).  
**Puntero LanceDB:** lancedb://decisions/framework/deepseek  
**Aprobado por:** Data Leader  
**Tags:** stack S0 activo

---

### 2025-S0 · orquestador · stack

**Decisión:** Adoptar Groq LPU para validaciones de estado en LangGraph.  
**Justificación:** LangGraph requiere validaciones frecuentes entre nodos. Con latencia de inferencia estándar (~800ms–2s), el grafo se vuelve lento en sesiones de trabajo real. Groq resuelve esto a >500 t/s a costo controlado (~$2–4 USD del piloto).  
**Alternativas consideradas:** Claude Haiku para validaciones → descartado (más lento que Groq para este caso · no está optimizado para respuestas de estado) · validaciones síncronas sin LLM → descartado (requiere lógica de reglas hardcodeada que contradice la flexibilidad del grafo).  
**Evidencia:** PRD v2.1 · benchmark de latencia Groq vs estándar.  
**Impacto en:** prompt-engineer (calibración del grafo) · flujo de handoffs · presupuesto (~$2–4 USD).  
**Puntero LanceDB:** lancedb://decisions/framework/groq  
**Aprobado por:** Data Leader  
**Tags:** stack S0 activo

---

### 2025-S0 · orquestador · stack

**Decisión:** Adoptar LlamaIndex como capa semántica sobre Gold Marts.  
**Justificación:** El dashboard ejecutivo necesita ser consultable en lenguaje natural para que el C-Level pueda usarlo sin asistencia técnica. LlamaIndex traduce preguntas en NL a SQL sobre BigQuery. Eso transforma el dashboard de estático a conversacional — diferenciador clave del portafolio.  
**Alternativas consideradas:** Dashboard solo con filtros visuales → descartado (requiere conocimiento técnico del usuario) · custom NL-to-SQL → descartado (costo de desarrollo innecesario cuando LlamaIndex resuelve el caso).  
**Evidencia:** PRD v2.1 · skill data-analyst · escenarios de demo C-Level.  
**Impacto en:** data-analyst (S6) · data-engineer (schema Gold Marts debe ser compatible).  
**Puntero LanceDB:** lancedb://decisions/framework/llamaindex  
**Aprobado por:** Data Leader  
**Tags:** stack S0 activo

---

### 2025-S0 · orquestador · stack

**Decisión:** Rechazar Spark, Kafka y Databricks del stack activo del piloto.  
**Justificación:** El dataset IEEE-CIS tiene ~600 MB. Ese volumen cabe en pandas + DuckDB + BigQuery sin necesidad de procesamiento distribuido. Activar Spark o Databricks para 600 MB es sobredimensionar la solución — señal visible de inmadurez técnica para cualquier revisor. Permanecen en el CV como certificados; no entran al sistema activo.  
**Alternativas consideradas:** N/A — rechazado por ausencia de caso de uso que lo justifique.  
**Evidencia:** tamaño del dataset · principio de Mínimo Contexto Viable · Filtro 1 de admisión de herramientas.  
**Impacto en:** ninguno — herramientas no entran al stack.  
**Puntero LanceDB:** lancedb://stack/rejected/spark-kafka-databricks  
**Aprobado por:** Data Leader  
**Tags:** stack S0 archivado

---

### 2025-S0 · orquestador · stack

**Decisión:** Rechazar SQLMesh del stack activo.  
**Justificación:** SQLMesh es técnicamente superior a dbt Core en planes virtuales y lineage automático. Sin embargo, el mercado Latam fintech solicita dbt en el 90%+ de las posiciones relevantes. El ROI de reemplazar dbt por SQLMesh en un piloto de 11 semanas es negativo: más tiempo de setup, menos señal para reclutadores. Reevaluar en v3 si SWARM escala a proyectos con requerimientos de lineage complejos.  
**Alternativas consideradas:** SQLMesh como reemplazo completo → rechazado · SQLMesh en paralelo con dbt → rechazado (duplica superficie de mantenimiento).  
**Evidencia:** análisis de mercado Latam fintech · Filtro 2 de admisión (costo > valor en 11 semanas).  
**Impacto en:** ninguno — dbt Core se mantiene.  
**Puntero LanceDB:** lancedb://stack/rejected/sqlmesh  
**Aprobado por:** Data Leader  
**Tags:** stack S0 archivado

---

### 2025-S0 · orquestador · arquitectura

**Decisión:** Implementar Memory Modular Architecture (MMA) con tres reglas de carga.  
**Justificación:** Sin MMA, el contexto del orquestador crece con cada sesión hasta consumir el presupuesto en tokens antes de que el proyecto cierre. MMA garantiza que el costo por sesión se mantiene constante independientemente del avance del proyecto.  
**Reglas adoptadas:** (1) Solo Phase-Log activo en contexto. (2) RAG selectivo por nodo. (3) Modelo correcto por tipo de tarea.  
**Evidencia:** PRD v2.1 · cálculo de tokens proyectados sin MMA vs con MMA · reducción objetivo ≥ 65%.  
**Impacto en:** todos los agentes · prompt-engineer (calibración de top-k) · auditor-de-telemetria (medición semanal).  
**Puntero LanceDB:** lancedb://decisions/framework/mma  
**Aprobado por:** Data Leader  
**Tags:** arquitectura S0 activo

---

### 2025-S0 · orquestador · arquitectura

**Decisión:** Métrica maestra del piloto = ahorro neto en USD, no AUC-ROC.  
**Justificación:** AUC-ROC mide la capacidad discriminativa del modelo pero no responde la pregunta de negocio: ¿cuánto vale este modelo para la institución financiera? El ahorro neto en USD con Matriz de Costos Asimétricos responde esa pregunta directamente y permite que el C-Level tome una decisión sin traducción técnica.  
**Alternativas consideradas:** F1-score → descartado (mismo problema que AUC · no habla de dinero) · Precision @ K → descartado (relevante para ranking · no para threshold de decisión binaria).  
**Evidencia:** PRD v2.1 · skill business-analyst · estructura del deck ejecutivo.  
**Impacto en:** data-scientist (threshold tuning) · ml-engineer (business-value logging) · data-analyst (dashboard) · business-analyst (Certificado de Defensibilidad).  
**Puntero LanceDB:** lancedb://decisions/framework/metrica-maestra  
**Aprobado por:** Data Leader  
**Tags:** arquitectura S0 activo

---

## RONDA 1 · Decisiones de Setup — S1

> [Las entradas de S1 se agregan aquí durante la ejecución de T1–T5]
> Formato: fecha real · agente · tipo

---

## RONDA 2 · Decisiones de Ingesta — S4

> [Las entradas de S4 se agregan aquí]
> Decisiones esperadas: tipificación de columnas · joins Bronze · tests dbt

---

## RONDA 3 · Decisiones de Feature Selection — S5

> [Las entradas de S5 se agregan aquí]
> Decisiones esperadas: variables V conservadas/descartadas · tratamiento de NAs · Matriz de Costos

---

## RONDA 4 · Decisiones de Modelado — S7

> [Las entradas de S7 se agregan aquí]
> Decisiones esperadas: algoritmo ganador · threshold óptimo · justificación de hiperparámetros

---

## RONDA 5 · Decisiones de Deployment — S8–S9

> [Las entradas de S8–S9 se agregan aquí]
> Decisiones esperadas: configuración Cloud Run · PSI threshold · estrategia de drift

---

## RONDA 6 · Decisiones de Narrativa — S10

> [Las entradas de S10 se agregan aquí]
> Decisiones esperadas: mapping Latam · supuestos del deck · Certificado de Defensibilidad

---

## Índice de herramientas rechazadas

| Herramienta | Ronda | Puntero LanceDB |
|---|---|---|
| CrewAI | S0 | lancedb://stack/rejected/crewai |
| Pinecone | S0 | lancedb://stack/rejected/pinecone |
| Spark / Kafka / Databricks | S0 | lancedb://stack/rejected/spark-kafka-databricks |
| SQLMesh | S0 | lancedb://stack/rejected/sqlmesh |
| Evidence.dev | S0 | lancedb://stack/rejected/evidence-dev |
| Checkov / TFLint | S0 | lancedb://stack/rejected/checkov-tflint |

> Si un agente propone cualquiera de estas herramientas, el auditor-de-telemetria
> recupera el fragmento de LanceDB y bloquea la propuesta con la justificación original.

---

*decision-log.md · SWARM v2.1 · IEEE-CIS Fraud Detection*  
*Última actualización: [completar automáticamente] · Entradas totales: [N]*
