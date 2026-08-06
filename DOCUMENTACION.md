# Calculadora ZZZ — Documentación

## ¿Qué es?

Herramienta de análisis y evaluación de builds para Zenless Zone Zero. Permite calcular el daño teórico de un agente, evaluar la calidad de sus discos, comparar builds y mantener un ranking global de jugadores.

---

## Arquitectura general

```
Calculadora_ZZZ.py / Crear_Gui.py   ← Interfaz gráfica (Flet)
api.py                               ← API REST (FastAPI, puerto 8000)
bot_zzz.py                           ← Bot de Discord
actualizador_uids.py                 ← Worker que actualiza el ranking en loop
gestor_ranking.py                    ← Lógica del ranking global
logica_recomendaciones.py            ← Motor de evaluación de builds
gestor_estadisticas.py               ← Cálculo de estadísticas finales
logica_danos.py / logica_combos.py   ← Motor de daño
optimizador.py                       ← Optimizador y proyección de techo
generador_imagenes.py                ← Generación de Build Cards (imágenes)
gestor_api.py / cargar_datos.py      ← Capa de datos y conexión con Enka Network
efectos_*.py                         ← Efectos de W-Engines, sets, pasivas, soportes, etc.
```

---

## Módulos principales

### `Calculadora_ZZZ.py` + `Crear_Gui.py` — Interfaz gráfica

Aplicación de escritorio construida con [Flet](https://flet.dev/). Organizada en pestañas:

**Pestaña DPS**
- Selector de agente, W-Engine (con filtro por compatibilidad), refinamiento y stacks
- Configuración manual de 6 discos (main stat + substats individuales)
- Selector de enemigo y buffs de equipo
- Cálculo en tiempo real de daño normal, sheer force, anomalía y disorder
- Análisis de substats con codificación visual (ideal / decente / basura)
- Potencial de mejora proyectado

**Pestaña Equipo**
- Configuración de hasta 3 agentes con sus W-Engines y sets
- Cálculo de sinergias y buffs de soporte aplicados al DPS principal
- Simulación de combos y rotaciones

**Pestaña Ranking**
- Visualización del ranking global por agente
- Filtros por agente y paginación (50 por página)
- Datos en tiempo real desde `ranking_global.json`

**Pestaña Análisis DA** (Deadly Assault)
- Selector de enemigo específico con resistencias
- Análisis de daño contra jefes del modo DA

**Pestaña Optimizador**
- Encuentra la mejor combinación de W-Engine × set × main stats
- Proyecta el techo teórico con substats perfectos

---

### `logica_recomendaciones.py` — Motor de evaluación

Núcleo del sistema de puntuación. Define:

**`CONFIG_ROLES`** — substats ideales/decentes/basura por rol:
- Atacante, Aturdidor, Anómalo, Soporte, Ruptura

**`EXCEPCIONES_AGENTES`** — overrides por agente específico (W-Engines recomendados, sets, mains y substats propios de cada personaje)

**`evaluar_calidad_global()`** — función principal de scoring:

```
calidad_pct = (calidad_substats × 0.90) + (eficiencia_wengine × 0.10)
```

Con penalizaciones:
- **Sin set 4pc:** `× 0.80` (−20%)
- **Sin W-Engine:** `× 0.60` (−40%)
- **Crit Rate > 100%:** rolls sobrantes cuentan como basura
- **Pen > 100%:** ídem
- **Daño elemental > 75%:** penalización proporcional (soft cap)

El resultado es un porcentaje de 0 a 100 que se convierte en tier:

| Rango | Tier |
|-------|------|
| 90–100 | GODLIKE |
| 80–89 | FLAWLESS |
| 65–79 | GREAT |
| 50–64 | GOOD |
| 35–49 | AVERAGE |
| 0–34 | LOW |

**Factor de indulgencia** según cantidad de substats ideales del agente:
- 1 ideal → `×0.65`
- 2 ideales → `×0.78`
- 3+ ideales → `×0.95`

---

### `gestor_ranking.py` — Ranking global

Gestiona `guardados/ranking_global.json`. Para cada jugador/UID almacena la calificación de cada agente.

**Cálculo de calificación por agente:**
1. Eficiencia del W-Engine (basada en `EXCEPCIONES_AGENTES`)
2. Calidad del set (4pc ideal → 25pts, 4pc funcional → 20pts, 2pc/2pc → hasta 20pts)
3. Main stats de discos 4/5/6 (hasta ~6.67 pts c/u)
4. Substats via `evaluar_calidad_global()` → determina la **calificación final**

> Los puntos de W-Engine, sets y mains son informativos en el breakdown. La calificación final (0–100) viene exclusivamente de `calidad_pct`.

---

### `actualizador_uids.py` — Worker de actualización

Proceso en background que cada N minutos (configurable, default 5):
1. Lee todos los UIDs guardados en `guardados/uids/uids.json`
2. Consulta Enka Network por cada UID
3. Recalcula la calificación de todos sus agentes
4. Actualiza `ranking_global.json`

Se ejecuta con:
```bash
python3 actualizador_uids.py --guardados ./guardados --datos ./datos --intervalo 5
```

Logs con rotación en `actualizador_uids.log` (máx. 3 archivos × 5MB).

---

### `api.py` — API REST

Ejecutar: `uvicorn api:app --host 0.0.0.0 --port 8000`

Rate limit: **10 req/min** por IP en endpoints de Enka.

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/agentes` | Lista todos los agentes con tipo, elemento y rango |
| GET | `/uid/{uid}` | Perfil completo de un UID (agentes del showcase) |
| GET | `/uid/{uid}/evaluar` | Evaluación de calidad de todos los agentes del UID |
| GET | `/uid/{uid}/agente/{nombre}` | Evaluación de un agente específico |
| GET | `/uid/{uid}/resumen` | Nick, promedio, mejor y peor agente |
| GET | `/ranking?page=1&size=20` | Ranking global paginado |
| POST | `/uid/{uid}/buildcard` | Genera imagen Build Card del agente |
| GET | `/download/prepare` | Prepara archivo para descarga |

Caché de UIDs en memoria: TTL de 60 segundos.

---

### `bot_zzz.py` — Bot de Discord

Flujo de 2 pasos:
1. `/calczzz <uid>` → consulta Enka y muestra dropdown con los agentes del showcase
2. Seleccionar agente → evaluación completa con scoring y recomendaciones

---

### `optimizador.py` — Optimizador de builds

- **`encontrar_mejor_build()`**: rankea todas las combinaciones de W-Engine × set × main stats según score de daño
- **`simular_proyeccion_realista()`**: calcula el techo teórico asumiendo substats perfectos y muestra las stats ideales
- **`generar_reporte_detallado()`**: exporta CSV con auditoría de la simulación

Modelo de daño para la proyección:
- Daño normal: ATK × multiplicador × (1 + crit_rate/100 × crit_dmg/100) × resistencias
- Anomalía: escala con Maestría de Anomalía + Tasa de Anomalía
- Sheer Force: daño de ruptura/aturdimiento

---

### `generador_imagenes.py` — Build Cards

Genera imágenes PNG con la información de build de un agente:
- Portrait del agente + W-Engine
- Sets equipados
- Main stats y substats con indicador de rolls y calidad
- Tier y calificación global
- Top 5 del ranking por agente (leaderboard)

---

### `efectos_*.py` — Efectos y pasivas

| Archivo | Contenido |
|---------|-----------|
| `efectos_wengines.py` | Pasivas de todas las W-Engines |
| `efectos_sets.py` | Bonificaciones de sets de discos (2pc y 4pc) |
| `efectos_pasivas.py` | Habilidades pasivas de cada agente |
| `efectos_core.py` | Efectos de las mejoras de núcleo |
| `efectos_mindscapes.py` | Efectos de los Mindscapes (constelaciones) |
| `efectos_soportes.py` | Buffs que los soportes aplican al DPS |
| `efectos_potencial.py` | Cálculo del potencial de mejora de discos |

---

## Datos

```
datos/
  agentes.csv        — Nombre, tipo, elemento, rango, facción de cada agente
  datos/agentes/     — Un CSV por agente con substats recomendados y config específica
  wengine.csv        — Lista de W-Engines con stats base
  sets.csv           — Sets de discos disponibles
  discos.csv         — Slots y tipos de main stats por slot
  substat.csv        — Valores base de cada substat
  enemigos.csv       — Enemigos con resistencias para el modo DA
guardados/
  uids/uids.json     — UIDs registrados (apodo → UID)
  ranking_global.json — Ranking global de todos los jugadores
```

---

## Internacionalización

Soporta español e inglés. Los textos de la UI se cargan desde:
- `locales/es.json`
- `locales/en.json`

El módulo `traductor.py` gestiona la carga y el fallback.

---

## Dependencias principales

```
flet          — UI de escritorio
fastapi       — API REST
uvicorn       — Servidor ASGI
enka          — Cliente de Enka Network (datos de personajes)
Pillow        — Generación de imágenes
discord.py    — Bot de Discord
slowapi       — Rate limiting
```
