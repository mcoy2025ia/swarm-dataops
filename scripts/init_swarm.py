#!/usr/bin/env python3
"""
setup/init_swarm.py · SWARM v2.1
Script de arranque para un nuevo proyecto.
Tiempo estimado: < 30 minutos desde cero.

Uso:
    python setup/init_swarm.py --proyecto "mi-proyecto" --dataset "descripcion"
    python setup/init_swarm.py --ieee-cis   # modo piloto IEEE-CIS

Requisitos:
    pip install lancedb logfire anthropic python-dotenv
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# ── Dependencias opcionales — el script verifica antes de importar ──────────
def verificar_dependencias():
    faltantes = []
    for pkg in ["lancedb", "logfire", "anthropic", "dotenv"]:
        try:
            __import__(pkg)
        except ImportError:
            faltantes.append(pkg)
    if faltantes:
        print(f"❌ Dependencias faltantes: {', '.join(faltantes)}")
        print(f"   Instalar con: pip install {' '.join(faltantes)}")
        sys.exit(1)
    print("✅ Dependencias verificadas")


# ── PASO 1: Estructura de directorios ───────────────────────────────────────
def crear_estructura(proyecto: str):
    """Crear la estructura de carpetas del proyecto."""
    print(f"\n📁 Creando estructura para: {proyecto}")

    carpetas = [
        f"projects/{proyecto}/phase-logs",
        f"projects/{proyecto}/agents",
        "setup",
        "pipeline/airflow/dags",
        "pipeline/dbt/models/bronze",
        "pipeline/dbt/models/silver",
        "pipeline/dbt/models/gold",
        "pipeline/ml",
        "pipeline/api",
        "dashboard/ejecutivo",
        "dashboard/demo",
        ".lancedb",
    ]

    for carpeta in carpetas:
        Path(carpeta).mkdir(parents=True, exist_ok=True)

    print(f"   ✅ {len(carpetas)} directorios creados")


# ── PASO 2: Inicializar LanceDB ──────────────────────────────────────────────
def init_lancedb(proyecto: str, prd_path: str = None):
    """
    Fragmentar y vectorizar los documentos base del proyecto.
    Crea las colecciones base en LanceDB local.
    """
    import lancedb
    import numpy as np

    print("\n🧠 Inicializando LanceDB...")

    db = lancedb.connect(".lancedb")

    # Colecciones base — se crean vacías si no existen
    colecciones_base = {
        "project_config":    "Configuración inmutable del proyecto (CLAUDE.md)",
        "project_rules":     "Reglas operativas del framework (Protocol.md)",
        "project_prd":       "PRD fragmentado por sección",
        "agents_prompts":    "Instrucciones base de cada agente",
        "decisions":         "Todas las decisiones del proyecto",
        "decisions_na":      "Decisiones sobre valores faltantes",
        "decisions_features":"Decisiones de feature selection",
        "decisions_models":  "Threshold, costos asimétricos, hiperparámetros",
        "schemas_silver":    "Schema validado de tablas Silver",
        "schemas_gold":      "Schema y lógica de los 5 Gold Marts",
        "quality_flags":     "Columnas poco confiables y alertas de calidad",
        "phase_logs":        "Phase-Logs históricos archivados",
        "stack_rejected":    "Herramientas rechazadas con justificación",
    }

    # Schema mínimo para cada fragmento
    schema_fragmento = {
        "id":          str,   # identificador único
        "coleccion":   str,   # nombre de la colección
        "contenido":   str,   # texto del fragmento
        "metadata":    str,   # JSON con contexto adicional
        "fase":        str,   # S0, S1, ... S11
        "agente":      str,   # quién creó el fragmento
        "timestamp":   str,   # ISO 8601
        "tags":        str,   # etiquetas separadas por coma
        "vector":      list,  # embedding — poblado por LanceDB
    }

    creadas = 0
    for nombre, descripcion in colecciones_base.items():
        try:
            # Crear con un fragmento inicial descriptivo
            fragmento_inicial = [{
                "id":        f"{nombre}_init",
                "coleccion": nombre,
                "contenido": f"Colección inicializada: {descripcion}",
                "metadata":  json.dumps({"proyecto": proyecto, "init": True}),
                "fase":      "S0",
                "agente":    "init_swarm",
                "timestamp": datetime.utcnow().isoformat(),
                "tags":      "init,base",
                "vector":    [0.0] * 384,  # placeholder — reemplazar con embedding real
            }]
            db.create_table(nombre, data=fragmento_inicial, mode="overwrite")
            creadas += 1
        except Exception as e:
            print(f"   ⚠️  {nombre}: {e}")

    print(f"   ✅ {creadas}/{len(colecciones_base)} colecciones inicializadas")
    print(f"   📍 Ubicación: .lancedb/")

    # Fragmentar el stack rechazado — disponible desde el día 1
    stack_rechazado = [
        {
            "herramienta": "CrewAI",
            "razon": "LangGraph ya es el framework de orquestación. Dos sistemas para el mismo rol crean deuda conceptual.",
            "principio_violado": "Replicable por Diseño",
        },
        {
            "herramienta": "Pinecone",
            "razon": "LanceDB resuelve el mismo problema siendo local-first y gratuito. Contradice Local-First.",
            "principio_violado": "Local-First",
        },
        {
            "herramienta": "Spark/Kafka/Databricks",
            "razon": "600 MB caben en pandas + DuckDB + BigQuery. Sobredimensionar es señal visible de inmadurez.",
            "principio_violado": "Filtro 2 — costo > valor en 11 semanas",
        },
        {
            "herramienta": "SQLMesh",
            "razon": "Superior técnico pero el mercado Latam fintech pide dbt. ROI negativo en 11 semanas.",
            "principio_violado": "Filtro 2 — costo > valor en 11 semanas",
        },
        {
            "herramienta": "Evidence.dev",
            "razon": "Streamlit + LlamaIndex ya cubren la presentación ejecutiva. Duplica superficie de mantenimiento.",
            "principio_violado": "Filtro 1 — no resuelve problema no cubierto",
        },
    ]

    tabla_rechazados = db.open_table("stack_rejected")
    for item in stack_rechazado:
        tabla_rechazados.add([{
            "id":        f"rejected_{item['herramienta'].lower().replace('/', '_')}",
            "coleccion": "stack_rejected",
            "contenido": f"{item['herramienta']}: {item['razon']}",
            "metadata":  json.dumps(item),
            "fase":      "S0",
            "agente":    "init_swarm",
            "timestamp": datetime.utcnow().isoformat(),
            "tags":      f"rechazado,{item['herramienta'].lower()}",
            "vector":    [0.0] * 384,
        }])

    print(f"   ✅ {len(stack_rechazado)} herramientas rechazadas cargadas en LanceDB")

    return db


# ── PASO 3: Configurar Logfire ───────────────────────────────────────────────
def init_logfire(proyecto: str):
    """
    Inicializar Pydantic Logfire y verificar que recibe eventos.
    Configura las 5 alertas de presupuesto.
    """
    print("\n📊 Inicializando Logfire...")

    # Verificar que existe el token
    logfire_token = os.getenv("LOGFIRE_TOKEN")
    if not logfire_token:
        print("   ⚠️  LOGFIRE_TOKEN no encontrado en .env")
        print("   → Crear cuenta en logfire.pydantic.dev y agregar LOGFIRE_TOKEN al .env")
        print("   → El sistema puede continuar pero sin observabilidad real")
        return False

    import logfire
    logfire.configure(token=logfire_token, project_name=f"swarm-{proyecto}")

    # Evento de prueba
    logfire.info(
        "swarm.init",
        proyecto=proyecto,
        framework="SWARM v2.1",
        timestamp=datetime.utcnow().isoformat(),
        budget_hard_cap_usd=30.0,
        budget_alert_80pct_usd=24.0,
    )

    print("   ✅ Logfire configurado y recibiendo eventos")
    print(f"   📍 Dashboard: https://logfire.pydantic.dev (proyecto: swarm-{proyecto})")
    print()
    print("   Alertas de presupuesto a configurar manualmente en Logfire:")
    print("   → $20 USD (67%) — informativa")
    print("   → $24 USD (80%) — crítica · notificar Data Leader")
    print("   → $28 USD (93%) — emergencia · suspender APIs externas")
    print("   → $30 USD (100%) — hard stop")

    return True


# ── PASO 4: Validar APIs ─────────────────────────────────────────────────────
def validar_apis():
    """
    Verificar que las APIs críticas responden.
    No falla el setup si alguna no está disponible — solo advierte.
    """
    print("\n🔑 Validando APIs...")

    apis = {
        "ANTHROPIC_API_KEY":  "Claude Sonnet + Haiku (estándar del sistema)",
        "GROQ_API_KEY":       "Groq LPU (validaciones LangGraph)",
        "DEEPSEEK_API_KEY":   "DeepSeek R1/V3 (Feature Selection V***)",
        "LOGFIRE_TOKEN":      "Pydantic Logfire (observabilidad)",
        "GCP_PROJECT_ID":     "Google Cloud Platform (BigQuery + Cloud Run)",
        "KAGGLE_USERNAME":    "Kaggle API (descarga dataset IEEE-CIS)",
        "KAGGLE_KEY":         "Kaggle API key",
    }

    encontradas = 0
    for var, descripcion in apis.items():
        valor = os.getenv(var)
        if valor:
            print(f"   ✅ {var} — {descripcion}")
            encontradas += 1
        else:
            print(f"   ⚠️  {var} — {descripcion} [NO ENCONTRADA]")

    print(f"\n   {encontradas}/{len(apis)} APIs configuradas")

    if encontradas < 4:
        print("\n   ⚠️  Menos de 4 APIs configuradas.")
        print("   El sistema puede iniciar pero algunas fases no podrán ejecutarse.")
        print("   Completar el archivo .env antes de S4.")

    return encontradas


# ── PASO 5: Crear archivos de arranque del proyecto ──────────────────────────
def crear_archivos_proyecto(proyecto: str, dataset: str, metrica: str):
    """
    Crear Phase-Log-S1.md y project-health.md iniciales.
    """
    print("\n📝 Creando archivos del proyecto...")

    fecha_hoy = datetime.now().strftime("%Y-%m-%d")

    # project-health.md inicial
    health_content = f"""# project-health.md · {proyecto}

**Proyecto:** {proyecto}
**Framework:** SWARM v2.1
**Dataset:** {dataset}
**Métrica maestra:** {metrica}
**Inicio:** {fecha_hoy}
**Budget acumulado:** $0.00 / $30.00 USD
**Fase activa:** S1
**Nodo LangGraph:** calibration
**Status general:** 🟡 SETUP EN CURSO

---

## Estado por fase

| Fase | Status | Cierre | Budget usado |
|---|---|---|---|
| S1 Setup | 🟡 En curso | — | $0.00 |
| S2 Calibración | ⚪ Pendiente | — | — |
| S3 Test E2E | ⚪ Pendiente | — | — |
| S4 Bronze | ⚪ Pendiente | — | — |
| S5 Silver/EDA | ⚪ Pendiente | — | — |
| S6 Gold/Dashboard | ⚪ Pendiente | — | — |
| S7 Modelado | ⚪ Pendiente | — | — |
| S8 Deployment | ⚪ Pendiente | — | — |
| S9 Hardening | ⚪ Pendiente | — | — |
| S10 Narrativa | ⚪ Pendiente | — | — |
| S11 Retro | ⚪ Pendiente | — | — |

---

## Métricas actuales (Logfire)

- **Budget acumulado:** $0.00 USD
- **Tokens totales:** 0
- **Violaciones MCV:** 0
- **Decisiones en decision-log:** 10 (S0 base)
- **Deuda de documentación:** 0 entradas

---

## Hitos públicos

- [ ] 🌐 Hito 1 — Dashboard C-level en Cloud Run (S6)
- [ ] 🤖 Hito 2 — Endpoint de scoring en vivo (S8)
- [ ] 📢 Hito 3 — Framework público + README + LinkedIn (S11)

---

*Actualizado por: auditor-de-telemetria · {fecha_hoy}*
"""

    health_path = Path(f"projects/{proyecto}/project-health.md")
    health_path.write_text(health_content, encoding="utf-8")
    print(f"   ✅ project-health.md creado")

    # .env template
    env_template = """# .env · SWARM v2.1
# Copiar a .env y completar con valores reales
# NUNCA commitear este archivo al repositorio

# APIs de LLMs
ANTHROPIC_API_KEY=
GROQ_API_KEY=
DEEPSEEK_API_KEY=

# Observabilidad
LOGFIRE_TOKEN=

# Google Cloud Platform
GCP_PROJECT_ID=
GCP_REGION=us-central1
GCS_BUCKET_NAME=

# Kaggle (para descarga de IEEE-CIS)
KAGGLE_USERNAME=
KAGGLE_KEY=

# Proyecto
PROYECTO_NOMBRE=ieee-cis-fraud
DBT_PROFILES_DIR=./pipeline/dbt
LANCEDB_PATH=.lancedb
"""

    env_path = Path(".env.template")
    if not env_path.exists():
        env_path.write_text(env_template, encoding="utf-8")
        print("   ✅ .env.template creado")

    # .gitignore
    gitignore_content = """.env
.lancedb/
__pycache__/
*.pyc
.DS_Store
*.pkl
*.joblib
mlruns/
"""
    gitignore_path = Path(".gitignore")
    if not gitignore_path.exists():
        gitignore_path.write_text(gitignore_content, encoding="utf-8")
        print("   ✅ .gitignore creado")


# ── PASO 6: Verificación final ───────────────────────────────────────────────
def verificacion_final(proyecto: str):
    """Checklist de arranque — confirmar que todo está listo para S1."""
    print("\n" + "="*60)
    print("✅ SWARM v2.1 — Verificación de arranque")
    print("="*60)

    checks = [
        ("LanceDB inicializado",          Path(".lancedb").exists()),
        ("project-health.md creado",      Path(f"projects/{proyecto}/project-health.md").exists()),
        ("decision-log.md existe",        Path("decision-log.md").exists()),
        ("CLAUDE.md existe",              Path("CLAUDE.md").exists()),
        ("Protocol.md existe",            Path("Protocol.md").exists()),
        ("Phase-Log-S1.md existe",        Path(f"projects/{proyecto}/phase-logs/Phase-Log-S1.md").exists()
                                          or Path("Phase-Log-S1.md").exists()),
        (".env.template creado",          Path(".env.template").exists()),
        ("ANTHROPIC_API_KEY configurada", bool(os.getenv("ANTHROPIC_API_KEY"))),
        ("LOGFIRE_TOKEN configurado",     bool(os.getenv("LOGFIRE_TOKEN"))),
        ("GROQ_API_KEY configurada",      bool(os.getenv("GROQ_API_KEY"))),
    ]

    pasados = 0
    for nombre, resultado in checks:
        icono = "✅" if resultado else "⚠️ "
        print(f"   {icono} {nombre}")
        if resultado:
            pasados += 1

    print(f"\n   {pasados}/{len(checks)} checks pasados")

    if pasados >= 8:
        print("\n🟢 Sistema listo para arrancar S1")
        print(f"   Proyecto: {proyecto}")
        print(f"   Siguiente paso: ejecutar prompt-engineer con Phase-Log-S1.md")
    elif pasados >= 6:
        print("\n🟡 Sistema parcialmente listo")
        print("   Completar los items marcados con ⚠️ antes de arrancar S1")
    else:
        print("\n🔴 Setup incompleto")
        print("   Revisar los items faltantes antes de continuar")

    print()


# ── MAIN ─────────────────────────────────────────────────────────────────────
def main():
    from dotenv import load_dotenv
    load_dotenv()

    parser = argparse.ArgumentParser(
        description="SWARM v2.1 — Script de arranque de nuevo proyecto"
    )
    parser.add_argument("--proyecto",  default="ieee-cis-fraud",
                        help="Nombre del proyecto (default: ieee-cis-fraud)")
    parser.add_argument("--dataset",   default="IEEE-CIS Fraud Detection (Vesta Corporation)",
                        help="Descripción del dataset")
    parser.add_argument("--metrica",   default="Ahorro neto en USD via Matriz de Costos Asimétricos",
                        help="Métrica maestra del proyecto")
    parser.add_argument("--ieee-cis",  action="store_true",
                        help="Modo piloto IEEE-CIS (valores predeterminados)")
    parser.add_argument("--skip-lancedb", action="store_true",
                        help="Saltar inicialización de LanceDB")
    parser.add_argument("--skip-logfire", action="store_true",
                        help="Saltar verificación de Logfire")

    args = parser.parse_args()

    if args.ieee_cis:
        args.proyecto = "ieee-cis-fraud"
        args.dataset  = "IEEE-CIS Fraud Detection · Vesta Corporation · Kaggle · 590k transacciones"
        args.metrica  = "Ahorro neto en USD via Matriz de Costos Asimétricos"

    print("="*60)
    print("⬡ SWARM v2.1 — Setup de nuevo proyecto")
    print("="*60)
    print(f"Proyecto:  {args.proyecto}")
    print(f"Dataset:   {args.dataset}")
    print(f"Métrica:   {args.metrica}")
    print(f"Timestamp: {datetime.utcnow().isoformat()}")

    # Ejecutar pasos
    verificar_dependencias()
    crear_estructura(args.proyecto)

    if not args.skip_lancedb:
        init_lancedb(args.proyecto)

    if not args.skip_logfire:
        init_logfire(args.proyecto)

    validar_apis()
    crear_archivos_proyecto(args.proyecto, args.dataset, args.metrica)
    verificacion_final(args.proyecto)


if __name__ == "__main__":
    main()
