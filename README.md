# ⬡ SWARM
### Scalable Workflow for Analytics, Research & Modeling

**Un framework open source que cualquier Data Leader senior puede clonar, adaptar a su proyecto, y usar para orquestar agentes IA especializados — con resultados que un C-level entiende sin traducción técnica.**

---

## El problema que resuelve

Un Data Leader senior pierde entre el 40% y el 60% de su tiempo en trabajo que no debería hacer.

Busca contexto de proyectos anteriores que nunca quedó documentado. Repite decisiones que ya tomó hace tres meses porque no hay registro. Ejecuta tareas técnicas de nivel junior porque no hay sistema que las delegue. Y cuando llega un proyecto nuevo, empieza desde cero — otra vez.

SWARM elimina ese desperdicio. No es una app, no es un chatbot, no es un agente de IA. Es una **metodología de trabajo aumentada por IA** que vive en el terminal, el editor y el sistema de notas del Data Leader. Los agentes ejecutan el trabajo técnico. El líder decide.

---

## Para quién es

- **Data Leaders con 10+ años de experiencia** que siguen ejecutando trabajo técnico que deberían delegar
- **Consultores de datos** que necesitan replicar el mismo nivel de arquitectura y documentación en cada cliente sin depender de la memoria
- **Heads de data construyendo portafolio** que quieren demostrar cómo operan a nivel VP — no solo qué modelos saben hacer

---

## Cómo funciona en una sesión

```
1. El sistema retoma    →  Claude Code lee el Phase-Log de la semana activa
                           Sabe exactamente dónde quedó el proyecto y qué sigue
                           ~1,000 tokens de contexto (vs 15,000-40,000 sin MMA)

2. El agente propone    →  Qué · Cómo · Asume · Riesgos · Qué necesita del líder

3. El líder decide      →  ✅ Aprobado · 🔄 Ajustar · ❌ Rechazado
                           Solo esto. No ejecuta.

4. Queda documentado    →  Decisión + autor + fecha + justificación
                           Automáticamente en decision-log.md y en LanceDB
```

El Data Leader aparece en 5 momentos del proyecto — los nodos de aprobación del grafo. En todos los demás, el sistema corre solo.

---

## El piloto — IEEE-CIS Fraud Detection

SWARM v2.1 se valida con el dataset de Vesta Corporation: **590k transacciones, 433 columnas, 76% de NAs, clase desbalanceada al 3.5%, y 339 variables enmascaradas** cuyo significado hay que inferir estadísticamente.

No es un tutorial de Kaggle. Es el tipo de problema que una institución financiera real enfrenta — y que la mayoría de los portafolios de data evita porque es difícil.

**La métrica no es AUC-ROC. Es ahorro neto en USD.**

```
ahorro_neto = (fraudes_detectados × costo_fraude_evitado)
            − (falsos_positivos   × costo_bloqueo_legítimo)
```

El modelo ganador es el que maximiza ese número con el threshold correcto — no el que tiene la curva más bonita.

---

## Los 3 entregables públicos

| Entregable | Qué es | Para quién |
|---|---|---|
| **Este repo** | Framework completo con protocolos, agentes y plantillas. Nuevo proyecto en < 30 min | Otro Data Leader que quiere replicar la metodología |
| **[Dashboard ejecutivo](#)** | Streamlit con slider de threshold → impacto en USD. Consultable en lenguaje natural | Headhunter o cliente que quiere ver el resultado en contexto real |
| **[Endpoint de scoring](#)** | FastAPI: transacción → probabilidad de fraude + explicación SHAP en lenguaje natural | Equipo técnico que evalúa si el modelo es deployable en producción |

---

## La arquitectura en 5 capas

```
L4 — Presentación      Streamlit (dashboard ejecutivo + demo ML) · FastAPI · Deck 5 slides
L3 — Infraestructura   BigQuery · Cloud Storage · Cloud Run · GitHub Actions CI/CD
L2 — Procesamiento     Airflow · dbt Core · Python 3.11 · MLflow · DVC · LlamaIndex
L1 — Orquestación      Claude Code · LangGraph · Groq LPU · DeepSeek R1/V3 · 7 agentes
L0 — Conocimiento      LanceDB (memoria vectorial) · Phase-Logs · Pydantic Logfire
```

### Por qué cada herramienta — en una línea

| Herramienta | Por qué está, no por qué existe |
|---|---|
| **LangGraph** | Convierte los handoffs manuales entre agentes en una máquina de estados. El Data Leader deja de ser mensajero. |
| **LanceDB** | Memoria vectorial local-first ($0). El sistema sabe dónde quedó sin cargar el historial completo. |
| **Groq LPU** | LangGraph valida estados frecuentemente. Con latencia estándar, el flujo se vuelve lento e inusable. |
| **DeepSeek R1/V3** | Solo para las 339 variables V enmascaradas. El razonamiento cadena-de-pensamiento hace cada decisión auditable. |
| **Pydantic Logfire** | El Auditor de Telemetría controla el budget de $30 USD en tiempo real. Sin esto, el costo es invisible. |
| **LlamaIndex** | El CFO pregunta en lenguaje natural. LlamaIndex traduce a SQL sobre BigQuery. El dashboard deja de ser estático. |
| **dbt Core** | Estándar del mercado Latam fintech. Cada transformación documentada, testeada y versionada. |

---

## Los 7 agentes activos

```
prompt-engineer        →  S1–S3   Diseña el grafo, fragmenta LanceDB, define model-routing
auditor-telemetría     →  S1–S11  Monitorea budget y trazabilidad en tiempo real (Logfire)
data-engineer          →  S4, S6  Pipeline Bronze→Silver→Gold · 5 marts · DuckDB-first
data-scientist         →  S5, S7  EDA · Feature Selection V*** (DeepSeek) · modelo USD
ml-engineer            →  S8, S9  FastAPI · Docker · Cloud Run · drift monitoring
data-analyst           →  S6, S10 Dashboard ejecutivo · LlamaIndex · Filtro Cero-Slang
business-analyst       →  S10     Defensibilidad financiera · mapping Latam · Certificado
```

El catálogo completo tiene 23 agentes. Solo 7 activos en este piloto — más agentes = más tokens, contradice el KPI principal del sistema.

---

## Memory Modular Architecture — por qué importa

El problema invisible de trabajar con LLMs en proyectos largos es el costo de tokens. Sin control, el contexto crece con el tiempo hasta que cada sesión cuesta más de lo que produce.

SWARM resuelve esto con tres reglas:

```
Regla 1  Solo el Phase-Log de la semana activa va en contexto
         Los históricos viven en LanceDB como embeddings

Regla 2  LangGraph recupera de LanceDB solo los fragmentos que
         cada nodo necesita — no el historial completo

Regla 3  Modelo correcto para cada tarea
         Groq para validaciones rápidas · DeepSeek solo para V***
         Claude Sonnet para lo demás · Claude Haiku para confirmaciones
```

**Reducción proyectada: ≥ 65% de tokens vs carga completa.**  
Medido por Logfire. Reportado semanalmente por el Auditor de Telemetría.

---

## El Decision Log — la prueba de que funciona

Cada herramienta que se propuso para SWARM y no entró tiene su justificación documentada. Esto no es un apéndice — es la demostración más directa del criterio técnico de quien diseñó el framework.

| Propuesta | Decisión | Por qué |
|---|---|---|
| CrewAI | ❌ Rechazado | LangGraph ya es el framework de orquestación. Dos sistemas para el mismo rol crean deuda conceptual. |
| Pinecone | ❌ Rechazado | LanceDB resuelve el mismo problema siendo local-first y gratuito. |
| Spark / Databricks | ❌ Rechazado | 600 MB caben en pandas + DuckDB + BigQuery. Activarlos sería sobredimensionar visible para cualquier revisor técnico. |
| SQLMesh | ❌ Rechazado | Superior técnico a dbt. Pero el mercado Latam fintech pide dbt. ROI negativo en 11 semanas. |
| Logfire (v1.2) | ✅ Revertido | En v1.2 no había agentes desatendidos. En v2.1 LangGraph corre flujos autónomos — el contexto cambió, no el criterio. |

Adoptar todo lo que sugieren externos es señal junior. Descartar con justificación documentada es señal senior.

---

## Roadmap — 11 semanas

```
S1–S3   Setup + calibración    LanceDB · LangGraph · Logfire · 7 agentes calibrados
S4      Bronze                 4 CSVs en BigQuery · Airflow · DVC · telemetría activa
S4–S5   Silver + EDA           DeepSeek analiza V1–V339 · decisiones NA en LanceDB
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
S5–S6   🌐 Hito 1              Gold Marts + LlamaIndex + Dashboard C-level en Cloud Run
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
S7      Modelado               XGBoost · LightGBM · threshold en USD · SHAP · GPU RTX 4060
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
S8      🤖 Hito 2              FastAPI + SHAP + Docker + Cloud Run · Endpoint en vivo
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
S9–S10  Hardening + narrativa  Drift monitoring · Deck 5 slides en USD · Certificado
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
S11     📢 Hito 3              Framework público · README · 3 posts LinkedIn
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Budget total: $30 USD hard cap.** Alerta automática en Logfire al 80% ($24 USD).

---

## Cómo clonar SWARM para tu proyecto

```bash
git clone https://github.com/mcoy/swarm
cd swarm
```

Luego 4 pasos — menos de 30 minutos:

```
1. Editar CLAUDE.md        →  reemplazar IEEE-CIS por tu proyecto
                               definir dataset, objetivo, métrica maestra

2. Inicializar LanceDB     →  python setup/init_lancedb.py
                               fragmenta tu PRD en embeddings recuperables

3. Configurar Logfire      →  python setup/init_logfire.py
                               configura las 5 alertas de presupuesto

4. Calibrar agentes        →  ejecutar prompt-engineer S1
                               model-routing table · nodos del grafo · top-k RAG
```

El sistema está listo. Sin más configuración.

---

## Estructura del repositorio

```
swarm/
├── CLAUDE.md                    ←  archivo de arranque del proyecto · < 300 tokens
├── Protocol.md                  ←  reglas operativas reutilizables del framework
├── README.md                    ←  este archivo
│
├── agents/                      ←  skills de los 7 agentes activos
│   ├── prompt-engineer.md
│   ├── auditor-de-telemetria.md
│   ├── data-engineer.md
│   ├── data-scientist.md
│   ├── ml-engineer.md
│   ├── data-analyst.md
│   ├── business-analyst.md
│   └── orquestador.md
│
├── phase-logs/                  ←  estado semanal del proyecto
│   ├── Phase-Log-S1.md          ←  activo durante S1 · archivado en LanceDB al cerrar
│   └── ...
│
├── decision-log.md              ←  cada decisión con autor, fecha y justificación
├── project-health.md            ←  estado del proyecto actualizado por el Auditor
│
├── pipeline/                    ←  código del piloto IEEE-CIS
│   ├── airflow/                 ←  DAGs de ingesta
│   ├── dbt/                     ←  modelos Bronze → Silver → Gold
│   ├── ml/                      ←  entrenamiento, SHAP, threshold tuning
│   └── api/                     ←  FastAPI endpoint de scoring
│
├── dashboard/                   ←  Streamlit apps
│   ├── ejecutivo/               ←  dashboard C-level con LlamaIndex
│   └── demo/                    ←  simulador de transacción
│
└── setup/                       ←  scripts de arranque para nuevo proyecto
    ├── init_lancedb.py
    ├── init_logfire.py
    └── new_project.md           ←  checklist completo de onboarding
```

---

## Criterios de éxito — en orden de importancia

**1. El framework es realmente cloneable**
Otro Data Leader puede tomar este repo, leer este README, y tener el sistema corriendo con su propio dataset en menos de 30 minutos. Sin asistencia.

**2. El resultado habla en USD**
El dashboard muestra cuánto ahorra el modelo, no el AUC. Un CRO puede tomar una decisión con ese número sin traducir nada.

**3. Las decisiones son auditables**
El `decision-log.md` del proyecto cuenta la historia completa: qué se decidió, quién lo propuso, cuándo, y por qué. Incluyendo lo que se rechazó.

---

## Sobre el autor

**Manuel Alberto Coy Benavides**  
Senior Data & Analytics · Bogotá, Colombia  
15+ años en banca, seguros, retail y fintech

Experiencia relevante para este framework: modelo antifraude SOAT en Transfiriendo S.A. con ahorro documentado superior a COP 2B · Subdirector de Inteligencia Comercial en Tostao · Data Engineer en Sodimac Homecenter · consultoría para MetLife, AIG, Banco Santander, Falabella, Citibank.

SWARM nació de una pregunta simple: ¿por qué cada proyecto de datos empieza desde cero si el 70% del trabajo es siempre el mismo?

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Manuel_Coy-0077B5?style=flat&logo=linkedin)](https://linkedin.com/in/manuelcoy)

---

## Licencia

MIT — usa, modifica y distribuye libremente.  
Si SWARM te ahorra tiempo en un proyecto real, una mención en LinkedIn es suficiente.

---

*⬡ SWARM v2.1 · Framework open source para Data Leaders · 2025*
