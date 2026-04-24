# orquestador · Data Leader

**Versión:** 2.1  
**Framework:** SWARM — open source para Data Leaders  
**Proyecto activo:** IEEE-CIS Fraud Detection  
**Rol:** Director de Orquesta — aprueba, no ejecuta  
**Capa:** L1 — Orquestación · todos los nodos de aprobación  
**Herramienta principal:** Logfire dashboard · LangGraph estado del grafo · LanceDB decision-log  
**Estado:** Activo transversal S1–S11

---

## Identidad

Eres el único humano en el enjambre.

Los demás roles son agentes — ejecutan, proponen, documentan. Tú haces exactamente una cosa: **decidir**. Apruebas o rechazas cada propuesta en los nodos de aprobación del grafo. No escribes código de pipeline. No corriges queries SQL. No redactas el deck. No actúas como mensajero entre agentes.

En v1.2 el Data Leader pasaba el 40% de su tiempo coordinando manualmente: llevando el reporte del data-engineer al data-scientist, revisando si el modelo del ml-engineer usaba las features correctas, preguntando al business-analyst si los números del deck estaban validados. Ese tiempo se perdía en trabajo de mensajería que no requería juicio senior.

En v2.1 LangGraph hace esa coordinación. Logfire muestra el estado en tiempo real. LanceDB guarda el histórico. El Data Leader mira el dashboard y decide — nada más. El tiempo recuperado es para lo que sí requiere juicio senior: evaluar si el threshold óptimo es realmente el correcto para el mercado Latam, decidir si un riesgo de negocio justifica retrasar un hito, o determinar si el deck está listo para mostrarse a un CRO real.

---

## El grafo que gobiernas

El grafo de LangGraph no es un diagrama — es el contrato de trabajo del enjambre. Cada nodo tiene un agente responsable, una condición de entrada medible y una condición de salida verificable. Tu trabajo es revisar los nodos de aprobación cuando el sistema te lo indica — no los demás.

```
[calibration] ──→ [ingestion] ──→ [feature_selection] ──→ [modeling]
     PE                DE                  DS                  ML
     
     ──→ [dashboard] ──→ [narrative] ──→ [close]
              DA              BA           Data Leader
```

**Nodos de aprobación obligatoria — solo en estos intervienes activamente:**

| Punto de aprobación | Qué evalúas | Fuente de información |
|---|---|---|
| Bronze → Feature Selection | ¿Los datos tienen la calidad suficiente para modelar? | Reporte de Salud del data-engineer + tests dbt en Logfire |
| Feature Selection → Modelado | ¿Las decisiones sobre las 339 variables V son estadísticamente defendibles? | LanceDB: decisiones del data-scientist + Certificado DeepSeek |
| Modelado → Dashboard | ¿El threshold óptimo tiene sentido de negocio en el contexto Latam? | MLflow: ahorro_neto_usd + matriz de costos validada por business-analyst |
| Dashboard → Narrativa | ¿El dashboard responde las tres preguntas del C-Level sin ambigüedad? | URL pública + test de queries NL en lenguaje natural |
| Narrativa → Cierre | ¿El deck es inexpugnable ante un CRO colombiano? | Certificado de Defensibilidad del business-analyst |

En todos los demás momentos, el grafo corre solo.

---

## Cómo lees el estado del proyecto

Tu fuente de información principal no son los reportes de los agentes — es el dashboard de Logfire. Los reportes de los agentes son la interpretación; Logfire es la evidencia.

**Lo que ves en Logfire en cualquier momento:**

```
Panel 1 — Budget
  Costo acumulado: $X.XX / $30.00 USD
  Proyección al cierre: $XX.XX
  Agente con mayor consumo esta semana: [agente]
  Alerta activa: NO | SÍ — [descripción]

Panel 2 — Estado del grafo
  Nodo activo: [nodo]
  Nodo completado más reciente: [nodo] · [timestamp]
  Tests dbt en verde: [N/N]
  Modelos dbt con error: [lista o "ninguno"]

Panel 3 — Calidad del pipeline
  Última ejecución Bronze: [timestamp] · [filas] · [status]
  Última ejecución Silver: [timestamp] · [filas] · [status]
  Último refresh Gold Marts: [timestamp] · [status]
  Latencia endpoint (si S8+): p50=[Xms] p95=[Xms]

Panel 4 — Decisiones pendientes de aprobación
  [lista de propuestas de agentes que esperan tu respuesta]
  [cada una con: agente, tarea, propuesta resumida, punteros LanceDB]
```

Si Panel 4 está vacío, el enjambre está trabajando autónomamente. No interrumpas.

---

## El protocolo de decisión en los nodos de aprobación

Cuando un agente llega a un nodo de aprobación, el grafo te presenta exactamente lo necesario para decidir — no el trabajo completo, sino la pregunta de negocio que requiere tu juicio.

**Formato de presentación de propuesta al Data Leader:**

```
PROPUESTA DE APROBACIÓN
Agente: [agente]
Nodo: [nodo actual] → [nodo siguiente]
Fase: S[N]

CONTEXTO RECUPERADO DE LANCEDB:
  [fragmentos relevantes de decisiones anteriores que aplican]

PROPUESTA:
  [qué el agente propone hacer o ha completado]

EVIDENCIA:
  [métricas de Logfire / resultados de tests / números clave]

RIESGO SI SE APRUEBA:
  [qué puede salir mal y cómo se detectaría]

RIESGO SI SE RECHAZA:
  [impacto en timeline y presupuesto]

TU DECISIÓN:
  [ ] Aprobado — el grafo avanza al siguiente nodo
  [ ] Ajustar — [especifica qué cambiar · el agente vuelve al nodo actual]
  [ ] Rechazado — [especifica por qué · el agente documenta en decision-log.md]
```

**Tu respuesta es una de tres opciones.** No hay opción de "revisar más tarde" — si el grafo está esperando tu aprobación, el enjambre está bloqueado. Revisar el dashboard de Logfire y tomar la decisión es la única tarea que el sistema no puede hacer por ti.

---

## Lo que ya no haces en v2.1

Esta lista es tan importante como la de lo que sí haces. Cada ítem representa tiempo recuperado que ahora se invierte en decisiones reales.

**Ya no eres el mensajero:**  
El data-engineer ya no te envía un reporte para que tú se lo pases al data-scientist. El data-engineer publica los metadatos de calidad en LanceDB. El data-scientist consulta LanceDB cuando necesita esa información. Tú no intervienes en esa transferencia.

**Ya no haces seguimiento manual de tareas:**  
El estado de cada agente está en el grafo de LangGraph visible en tiempo real. Si quieres saber si el data-engineer terminó los tests de Silver, miras Logfire — no preguntas.

**Ya no validas que el decision-log esté actualizado:**  
El Auditor de Telemetría hace ese trabajo. Su KPI primario es deuda cero de documentación. Si el decision-log tiene una entrada faltante, el Auditor lo detecta y corrige — tú solo lo ves en el reporte semanal.

**Ya no corriges el trabajo técnico de los agentes:**  
Si el código de un modelo dbt está mal, el data-engineer lo corrige. Si un prompt está generando resultados inconsistentes, el prompt-engineer lo recalibra. Tu rol es evaluar si el output de negocio es correcto — no auditar el código que lo produce.

---

## Las cinco decisiones de negocio que solo tú puedes tomar

Hay cinco momentos en el piloto donde el juicio técnico no es suficiente y se necesita juicio de negocio senior. Estos son los momentos para los que existe el rol de Data Leader en SWARM:

**1. Validar la Matriz de Costos Asimétricos (S5)**  
Los valores de FN_cost y FP_cost que el data-scientist y el business-analyst proponen son estimaciones basadas en el dataset de Kaggle. Tú apruebas esos valores con plena consciencia de su limitación: son ilustrativos para el portafolio, no costos reales de producción en Latam. Esa distinción tiene que estar en el Certificado de Defensibilidad.

**2. Aprobar el threshold óptimo (entre S7 y S8)**  
El data-scientist entrega el threshold que maximiza `ahorro_neto_usd` según el modelo. Pero un threshold más agresivo (más detecciones, más falsos positivos) puede tener sentido en un contexto de alto riesgo regulatorio, y uno más conservador en un contexto de experiencia de usuario prioritaria. Esa decisión de contexto es tuya — el modelo no la puede tomar.

**3. Aprobar el mapping a Latam (S10)**  
El business-analyst propone los casos de uso de Nequi, Daviplata y BNPL. Tú validas que esos casos son realistas dado tu conocimiento del mercado colombiano y que las limitaciones regulatorias (SARLAFT, Habeas Data, Circular 052 SFC) están tratadas con la precisión correcta para la audiencia del deck.

**4. Decidir si el deck está listo para una audiencia real (S10)**  
El business-analyst emite el Certificado de Defensibilidad. Tú decides si ese certificado es suficiente para presentar ante un CRO o CFO real. Esta es la única decisión del proyecto que no tiene criterio técnico — es juicio sobre riesgo reputacional.

**5. Aprobar el README como representación pública del framework (S11)**  
El README del repo es la carta de presentación de SWARM ante headhunters, clientes potenciales y otros Data Leaders. Tú apruebas que representa honestamente lo que el framework hace y lo que no hace — sin sobre-prometer ni sub-representar.

---

## Protocolos operativos

### Revisión semanal del dashboard — el único ritual fijo
Cada viernes, antes de que el Auditor de Telemetría genere el reporte semanal, revisar el dashboard de Logfire durante 15 minutos con este checklist:

```
[ ] Budget acumulado vs proyección: ¿estamos en línea?
[ ] Nodo activo del grafo: ¿es el correcto para la semana?
[ ] Decisiones pendientes de aprobación: ¿hay alguna bloqueada?
[ ] Alertas activas en Logfire: ¿requieren intervención?
[ ] decision-log.md: ¿el Auditor reportó deuda cero esta semana?
```

Si todo está verde y no hay decisiones pendientes, la revisión termina en 15 minutos. Si hay algo que requiere intervención, la tarea es tomar la decisión — no investigar el problema técnico.

### El hard stop de presupuesto — la única intervención no planificada
Si el Auditor de Telemetría dispara la alerta de $24 USD (80% del hard cap), esta es la única situación donde el Data Leader interviene fuera del ciclo normal de aprobaciones.

Protocolo de emergencia de presupuesto:

```
1. Revisar en Logfire qué agente y qué tarea están consumiendo más
2. Evaluar tres opciones:
   a. Pausar las llamadas a DeepSeek y Groq · usar solo Claude Sonnet para el resto del piloto
   b. Reducir el scope de alguna fase para liberar presupuesto
   c. Aceptar que el piloto termina en $30 USD y ajustar los hitos restantes
3. Documentar la decisión en decision-log.md con la justificación
4. Comunicar al Auditor de Telemetría la opción elegida para que reconfigure las alertas
```

No hay opción 4 (aumentar el presupuesto). El hard cap es una condición de diseño del framework, no una estimación revisable.

---

## Anti-patrones — prohibido

**Mensajería manual**  
Si te encuentras reenviando un output de un agente a otro, algo está mal en el grafo o en LanceDB. La solución es arreglarlo ahí — no convertirte en el canal de comunicación.

**Micromanagement técnico**  
Revisar el código de dbt que escribió el data-engineer o sugerir cambios en el modelo de ML del data-scientist. Tu función es evaluar el output de negocio, no el código que lo produce.

**Aprobaciones sin evidencia**  
Aprobar una propuesta de agente sin haber revisado la evidencia en Logfire o LanceDB. "Parece bien" no es una aprobación — es un riesgo de trazabilidad. Si no puedes citar la fuente que respalda la aprobación, pide que el agente la provea antes de aprobar.

**Intervenciones fuera de los nodos de aprobación**  
Comentar el trabajo de un agente mientras está en ejecución — antes de que llegue al nodo de aprobación — interrumpe el flujo del grafo sin agregar valor. El agente completa su nodo, propone el output, y en ese momento se evalúa.

---

## Lo que SWARM demuestra sobre cómo operas

Para el headhunter o cliente que llega al repo y lee el README, el rol del Data Leader en SWARM comunica algo específico sobre el nivel de madurez de quien lo diseñó:

Un portafolio donde el Data Leader escribe el código demuestra que sabe programar.

Un portafolio donde el Data Leader diseñó el sistema que orquesta a otros agentes, definió los criterios de aprobación, estableció los protocolos de gobernanza, y construyó la narrativa financiera que un CRO puede usar para tomar una decisión — ese portafolio demuestra que sabe operar a nivel VP.

Esa es la diferencia que SWARM está construyendo.
