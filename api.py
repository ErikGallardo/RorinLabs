"""
API REST - Calculadora ZZZ
Expone la funcionalidad de la calculadora para bots externos.

Ejecutar: uvicorn api:app --host 0.0.0.0 --port 8000
"""
import os
import sys
import asyncio
import time

from fastapi import FastAPI, HTTPException, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from starlette.responses import JSONResponse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from cargar_datos import CargadorDatos
from gestor_api import GestorApi, procesar_agente, AVATAR_ID_MAP
from mapeos_enka import MAPA_SETS_ID as MAPA_SETS_ID_ENKA
from logica_recomendaciones import EXCEPCIONES_AGENTES, CONFIG_ROLES, evaluar_calidad_global
import enka

# ─── Datos ────────────────────────────────────────────────────────────────────
DATOS_DIR = os.path.join(BASE_DIR, "datos")
cargador = CargadorDatos(DATOS_DIR)
agentes_data = cargador.cargar_csv("agentes.csv")
NOMBRE_MAP = {a["Nombre"].lower(): a["Nombre"] for a in agentes_data}


# ─── Helpers (réplica del bot) ────────────────────────────────────────────────
def resolver_nombre(nombre_enka):
    n = nombre_enka.lower().strip()
    if n in NOMBRE_MAP:
        return NOMBRE_MAP[n]
    for k, v in NOMBRE_MAP.items():
        if n in k or k in n:
            return v
    return nombre_enka


def normalizar_stat(key_sucia):
    k = str(key_sucia).lower().strip()
    es_pct = "%" in k or "porcentual" in k or "tasa" in k or "prob" in k or "daño" in k or "recup" in k
    sufijo = "_porcentual" if es_pct else "_plano"
    base = k.replace("porcentual", "").replace("plano", "").replace("_", "").replace("%", "").replace("+", "")
    base = ''.join(i for i in base if not i.isdigit()).strip()
    if "ataque" in base or "atk" in base:
        return "Ataque" + sufijo
    if "vida" in base or "hp" in base:
        return "Puntos_Vida" + sufijo
    if "defensa" in base or "def" in base:
        return "Defensa" + sufijo
    if "maestria" in base or ("anomal" in base and ("prof" in base or "maestr" in base)):
        return "Maestría_Anomalía_plano"
    if "anomal" in base:
        return "Tasa_de_Anomalía"
    if "prob" in base:
        return "Probabilidad_crítico_porcentual"
    if ("daño" in base or "dano" in base) and "crit" in base:
        return "Daño_crítico_porcentual"
    if "pen" in base or "perf" in base:
        return "Tasa_de_Perforación" if es_pct else "Perforación_Plana_plano"
    if "recup" in base or "energy" in base:
        return "Recuperación_energía_porcentual"
    if "impact" in base:
        return "Impacto"
    return "Desconocido"


def limpiar_nombre_stat(nombre_raw, valor_str):
    n = str(nombre_raw).lower().strip()
    v = str(valor_str)
    es_pct = "%" in v or "percent" in n or "tasa" in n or "prob" in n or "bono" in n or "ratio" in n
    if "ataque" in n or "atk" in n:
        return "Ataque_porcentual" if es_pct else "Ataque_plano"
    if "vida" in n or "hp" in n or "pv" in n:
        return "Puntos_Vida_porcentual" if es_pct else "Puntos_Vida_plano"
    if "defensa" in n or "def" in n:
        return "Defensa_porcentual" if es_pct else "Defensa_plano"
    if "crit" in n or "crít" in n:
        if "rate" in n or "prob" in n:
            return "Probabilidad_crítico_porcentual"
        if "dmg" in n or "daño" in n or "dano" in n:
            return "Daño_crítico_porcentual"
    if "pen" in n or "perf" in n:
        return "Tasa_de_Perforación" if es_pct else "Perforación_Plana_plano"
    if "anomal" in n and ("prof" in n or "maestr" in n):
        return "Maestría_Anomalía_plano"
    if "anomal" in n and ("tasa" in n or "mastery" in n):
        return "Tasa_de_Anomalía"
    if "recup" in n or "energy" in n:
        return "Recuperación_energía_porcentual"
    if "impact" in n:
        return "Impacto"
    return "Desconocido"


def calcular_rolls_real(nombre_stat, valor_texto):
    try:
        clave = limpiar_nombre_stat(nombre_stat, valor_texto)
        return calcular_rolls_substat(clave, valor_texto)
    except Exception:
        return 1


def calcular_calidad(discos, nombre_agente):
    datos_ag = next((a for a in agentes_data if a["Nombre"] == nombre_agente), None)
    rol = datos_ag.get("Tipo", "Atacante") if datos_ag else "Atacante"

    # Construir rolls_actuales desde los discos (igual que el bot)
    rolls_actuales = {}
    for disco in discos:
        for sub in disco.get("sub_stats", []):
            nombre_sub = sub.get("name", "")
            valor_sub = sub.get("value", "0")
            clave = limpiar_nombre_stat(nombre_sub, valor_sub)
            rolls = calcular_rolls_real(nombre_sub, valor_sub)
            rolls_actuales[clave] = rolls_actuales.get(clave, 0) + rolls

    r = evaluar_calidad_global(
        nombre_agente, rol, rolls_actuales,
        stats_finales=None, eficiencia_wengine_actual=100,
        excepciones=EXCEPCIONES_AGENTES, config_roles=CONFIG_ROLES
    )
    return {
        "calidad_pct": round(r["calidad_pct"], 2),
        "calidad_clasica_pct": round(r.get("calidad_clasica_pct", r["calidad_pct"]), 2),
        "calidad_dinamica_pct": round(r.get("calidad_dinamica_pct", r["calidad_pct"]), 2),
        "calidad_dinamica_raw_pct": round(r.get("calidad_dinamica_raw_pct", r["calidad_pct"]), 2),
        "penalizacion_dinamica_pct": round(r.get("penalizacion_dinamica_pct", 0), 2),
        "rolls_ideal": r["ideal"],
        "rolls_decente": r["decente"],
        "rolls_basura": r["basura"],
        "total_rolls": r["total_rolls"],
        "prioridad_dinamica": r.get("prioridad_dinamica", [])[:3],
        "ajustes_dinamicos": r.get("ajustes_dinamicos", []),
    }


# ─── Fetch UID desde Enka ────────────────────────────────────────────────────
async def fetch_uid(uid: int):
    personajes = []
    nick = "Desconocido"
    async with enka.ZZZClient(lang="en") as client:
        try:
            await client.update_assets()
        except Exception:
            pass
        data = await client.fetch_showcase(uid)
        if data.player:
            nick = data.player.nickname
        if data.agents:
            for agent in data.agents:
                personajes.append(procesar_agente(agent))
    return personajes, nick


# ─── FastAPI ──────────────────────────────────────────────────────────────────
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="Calculadora ZZZ API", version="1.1.0")
app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(status_code=429, content={"detail": "Rate limit excedido. Espera un momento."})


app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# ─── Caché de UIDs ────────────────────────────────────────────────────────────
_uid_cache: dict = {}  # {uid: (timestamp, personajes, nick)}
CACHE_TTL = 60


async def fetch_uid_cached(uid: int):
    now = time.time()
    if uid in _uid_cache and (now - _uid_cache[uid][0]) < CACHE_TTL:
        return _uid_cache[uid][1], _uid_cache[uid][2]
    personajes, nick = await fetch_uid(uid)
    _uid_cache[uid] = (now, personajes, nick)
    return personajes, nick


from fastapi.responses import FileResponse

FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

@app.get("/")
def root():
    if os.path.isdir(FRONTEND_DIR):
        return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))
    return {"status": "ok", "message": "Calculadora ZZZ API"}


@app.get("/agentes")
def listar_agentes():
    """Lista todos los agentes disponibles con sus datos base."""
    return [{"nombre": a["Nombre"], "tipo": a.get("Tipo", ""), "elemento": a.get("elemento", ""), "rango": a.get("Rango", "")} for a in agentes_data]


@app.get("/uid/{uid}")
@limiter.limit("10/minute")
async def obtener_perfil(request: Request, uid: int):
    """Consulta un UID en Enka Network y devuelve todos los agentes del showcase."""
    try:
        personajes, nick = await fetch_uid_cached(uid)
    except Exception as e:
        err = str(e).lower()
        if "does not exist" in err or "404" in err:
            raise HTTPException(status_code=404, detail="UID no encontrado")
        if "maintenance" in err:
            raise HTTPException(status_code=503, detail="Enka en mantenimiento")
        raise HTTPException(status_code=500, detail=str(e))

    if not personajes:
        raise HTTPException(status_code=404, detail="El perfil no tiene agentes públicos")

    return {"uid": uid, "nick": nick, "agentes": personajes}


@app.get("/uid/{uid}/evaluar")
@limiter.limit("10/minute")
async def evaluar_uid(request: Request, uid: int):
    """Consulta un UID y devuelve la evaluación de calidad de cada agente."""
    try:
        personajes, nick = await fetch_uid_cached(uid)
    except Exception as e:
        err = str(e).lower()
        if "does not exist" in err or "404" in err:
            raise HTTPException(status_code=404, detail="UID no encontrado")
        if "maintenance" in err:
            raise HTTPException(status_code=503, detail="Enka en mantenimiento")
        raise HTTPException(status_code=500, detail=str(e))

    if not personajes:
        raise HTTPException(status_code=404, detail="El perfil no tiene agentes públicos")

    resultados = []
    for p in personajes:
        nombre = resolver_nombre(p["name"])
        discos = p.get("discs", [])
        evaluacion = calcular_calidad(discos, nombre)
        resultados.append({
            "nombre": nombre,
            "level": p.get("level"),
            "element": p.get("element"),
            "weapon": p.get("weapon", {}).get("name", ""),
            "evaluacion": evaluacion,
        })

    return {"uid": uid, "nick": nick, "evaluaciones": resultados}


@app.get("/uid/{uid}/agente/{nombre_agente}")
@limiter.limit("10/minute")
async def evaluar_agente(request: Request, uid: int, nombre_agente: str):
    """Evalúa un agente específico de un UID."""
    try:
        personajes, nick = await fetch_uid_cached(uid)
    except Exception as e:
        err = str(e).lower()
        if "does not exist" in err or "404" in err:
            raise HTTPException(status_code=404, detail="UID no encontrado")
        if "maintenance" in err:
            raise HTTPException(status_code=503, detail="Enka en mantenimiento")
        raise HTTPException(status_code=500, detail=str(e))

    # Buscar el agente
    char_dict = None
    for p in personajes:
        if resolver_nombre(p["name"]).lower() == nombre_agente.lower():
            char_dict = p
            break

    if not char_dict:
        disponibles = [resolver_nombre(p["name"]) for p in personajes]
        raise HTTPException(status_code=404, detail=f"Agente '{nombre_agente}' no encontrado. Disponibles: {disponibles}")

    nombre = resolver_nombre(char_dict["name"])
    discos = char_dict.get("discs", [])
    evaluacion = calcular_calidad(discos, nombre)

    return {
        "uid": uid,
        "nick": nick,
        "agente": char_dict,
        "evaluacion": evaluacion,
    }


@app.get("/ranking")
def obtener_ranking(page: int = Query(1, ge=1), size: int = Query(20, ge=1, le=100)):
    """Devuelve el ranking global paginado."""
    import json
    ranking_path = os.path.join(BASE_DIR, "guardados", "ranking_global.json")
    if not os.path.exists(ranking_path):
        raise HTTPException(status_code=404, detail="Ranking no disponible")
    with open(ranking_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, list):
        items = data
    else:
        items = list(data.values())
    total = len(items)
    start = (page - 1) * size
    return {"total": total, "page": page, "size": size, "ranking": items[start:start + size]}


@app.get("/uid/{uid}/resumen")
@limiter.limit("10/minute")
async def resumen_uid(request: Request, uid: int):
    """Resumen compacto: nick, promedio, mejor y peor agente."""
    try:
        personajes, nick = await fetch_uid_cached(uid)
    except Exception as e:
        err = str(e).lower()
        if "does not exist" in err or "404" in err:
            raise HTTPException(status_code=404, detail="UID no encontrado")
        if "maintenance" in err:
            raise HTTPException(status_code=503, detail="Enka en mantenimiento")
        raise HTTPException(status_code=500, detail=str(e))

    if not personajes:
        raise HTTPException(status_code=404, detail="El perfil no tiene agentes públicos")

    evals = []
    for p in personajes:
        nombre = resolver_nombre(p["name"])
        ev = calcular_calidad(p.get("discs", []), nombre)
        evals.append({"nombre": nombre, "calidad_pct": ev["calidad_pct"]})

    evals.sort(key=lambda x: x["calidad_pct"], reverse=True)
    promedio = round(sum(e["calidad_pct"] for e in evals) / len(evals), 2)

    return {
        "uid": uid,
        "nick": nick,
        "total_agentes": len(evals),
        "promedio": promedio,
        "mejor": evals[0],
        "peor": evals[-1],
    }


# ─── Build Card ───────────────────────────────────────────────────────────────
from fastapi.responses import StreamingResponse
from io import BytesIO
from generador_imagenes import GeneradorTarjetas

generador = GeneradorTarjetas(BASE_DIR)

MAPA_SETS_ID = dict(MAPA_SETS_ID_ENKA)

MAPA_ELEMENTOS = {
    "ICE": "hielo", "FIRE": "fuego", "ELECTRIC": "electrico",
    "PHYSICAL": "fisico", "ETHER": "etereo", "WIND": "viento",
    "ZHEN_ASSAULT": "tinta aurica",
}

MAPA_SPECIALTY = {
    "ATTACK": "Atacante", "STUN": "Aturdidor", "ANOMALY": "Anomalo",
    "SUPPORT": "Soporte", "DEFENSE": "Defensor",
}

MAPA_MAIN_CORTAS = {
    "CRIT Rate": "CRIT RATE", "CRIT DMG": "CRIT DMG",
    "Anomaly Proficiency": "AP", "PEN Ratio": "PEN RATIO",
    "Energy Regen": "ER", "PEN": "PEN",
    "Physical DMG Bonus": "DMG%", "Fire DMG Bonus": "DMG%",
    "Ice DMG Bonus": "DMG%", "Electric DMG Bonus": "DMG%", "Ether DMG Bonus": "DMG%",
    "Wind DMG Bonus": "DMG%",
    "Anomaly Mastery": "AM", "HP": "HP", "ATK": "ATK", "DEF": "DEF",
    "Impact": "Impact",
}

MAPA_SETS_CORTOS = {
    "Balada de la rama y la espada": "Branch & Blade Song",
    "Nana a la Luz Cenicienta": "Moonlight Lullaby",
    "Monarca del Pináculo": "King of the Summit",
    "Floración del alba": "Dawn's Bloom",
    "Tecno Tetraodóntido": "Puffer Electro",
    "Disco sacudestrellas": "Shockstar Disco",
    "Balada de Aguas Blancas": "White Water Ballad",
    "Melodía de Phaeton": "Phaethon's Melody",
    "Metal eléctrico": "Thunder Metal",
    "Armonía Umbría": "Shadow Harmony",
    "Blues Libre": "Freedom Blues",
    "Fábula Yunkui": "Yunkui Tales",
    "Jazz caótico": "Chaos Jazz",
    "Jazz Oscilante": "Swing Jazz",
    "Metal caótico": "Chaotic Metal",
    "Metal colmilludo": "Fanged Metal",
    "Metal infernal": "Inferno Metal",
    "Metal Polar": "Polar Metal",
    "Punk Hormonal": "Hormone Punk",
    "Rock espiritual": "Soul Rock",
    "Tecno Pícido": "Woodpecker Electro",
    "Voz Astral": "Astral Voice",
    "Aria Radiante": "Shining Aria",
    "Proto Punk": "Proto Punk",
    "Conejo en el país de las maravillas": "Bunny in Wonderland",
    "Diario de una prisionera": "Notes From the Chained",
}


def construir_datos_tarjeta(personaje, nombre, nick, uid):
    """Transforma datos de Enka al formato que espera GeneradorTarjetas."""
    datos_ag = next((a for a in agentes_data if a["Nombre"] == nombre), None)
    rol = datos_ag.get("Tipo", "Atacante") if datos_ag else "Atacante"
    elemento = MAPA_ELEMENTOS.get(personaje.get("element", ""), "fisico")
    rango = datos_ag.get("Rango", "S") if datos_ag else "S"
    faccion = datos_ag.get("Faccion", datos_ag.get("faccion", "")) if datos_ag else ""

    config_rol = CONFIG_ROLES.get(rol, CONFIG_ROLES.get("Atacante", {})).copy()
    if nombre in EXCEPCIONES_AGENTES and "subs" in EXCEPCIONES_AGENTES[nombre]:
        config_rol["subs"] = EXCEPCIONES_AGENTES[nombre]["subs"]

    ideales = {normalizar_stat(k) for k in config_rol.get("subs", {}).get("ideal", [])}
    decentes = {normalizar_stat(k) for k in config_rol.get("subs", {}).get("decente", [])}

    # Procesar discos
    discos_procesados = []
    conteo_rolls = {}
    for d in sorted(personaje.get("discs", []), key=lambda x: int(x.get("slot", 0))):
        set_name_orig = MAPA_SETS_ID.get(int(d.get("set_id", 0)), "Desconocido")
        set_name = MAPA_SETS_CORTOS.get(set_name_orig, set_name_orig)

        # Main stat como string formateado (igual que la Calculadora)
        main_api = str(d.get("main_stat", {}).get("name", ""))
        main_val = str(d.get("main_stat", {}).get("value", ""))
        api_upper = main_api.upper()
        if "DMG" in api_upper and any(e in api_upper for e in ["ELECTRIC", "FIRE", "ICE", "ETHER", "PHYSICAL"]):
            main_trad = "DMG%"
        else:
            main_trad = MAPA_MAIN_CORTAS.get(main_api.replace("\xa0", " ").strip(), main_api)

        subs_procesados = []
        for sub in d.get("sub_stats", []):
            sub_name = sub.get("name", "")
            sub_val = sub.get("value", "0")
            clave = limpiar_nombre_stat(sub_name, sub_val)
            clave_norm = normalizar_stat(clave)
            rolls = calcular_rolls_real(sub_name, sub_val)
            conteo_rolls[clave] = conteo_rolls.get(clave, 0) + rolls

            if clave_norm in ideales:
                color = "#ffc107"
            elif clave_norm in decentes:
                color = "#00bcd4"
            else:
                color = "#616161"

            upgrades = rolls - 1
            subs_procesados.append({
                "nombre": sub_name,
                "valor": sub_val,
                "rolls": f"+{upgrades}" if upgrades > 0 else "",
                "color": color,
            })

        discos_procesados.append({
            "slot": int(d.get("slot", 0)),
            "set": set_name,
            "set_original": set_name_orig,
            "main_stat": f"{main_trad} {main_val}",
            "subs": subs_procesados,
        })

    # Evaluar calidad
    ev = evaluar_calidad_global(
        nombre, rol, conteo_rolls,
        stats_finales=None, eficiencia_wengine_actual=100,
        excepciones=EXCEPCIONES_AGENTES, config_roles=CONFIG_ROLES
    )
    calidad = ev["calidad_pct"]
    if calidad >= 85: eval_letter = "SSS"
    elif calidad >= 70: eval_letter = "SS"
    elif calidad >= 55: eval_letter = "S"
    elif calidad >= 40: eval_letter = "A"
    else: eval_letter = "B"

    # Stats principales (para la sidebar) - formato string como la Calculadora
    MAPA_ENKA_A_TARJETA = {
        "HP": "Puntos Vida", "ATK": "Ataque", "DEF": "Defensa",
        "Impact": "Impacto", "CRIT Rate": "Prob. Crítica",
        "CRIT DMG": "Daño Crítico", "Anomaly Mastery": "Tasa Anomalía",
        "Anomaly Proficiency": "Maestría Anom.", "PEN Ratio": "Perforación %",
        "Energy Regen": "Recup. Energía", "PEN": "Perf. Plana",
        "Sheer Force": "Sheer",
    }
    stats_principales = {}
    stats_crudas = personaje.get("stats", {})
    for key_enka, nombre_bonito in MAPA_ENKA_A_TARJETA.items():
        if key_enka in stats_crudas:
            v_raw = stats_crudas[key_enka]
            v = float(v_raw.get("value", 0)) if isinstance(v_raw, dict) else float(v_raw)
            es_decimal = key_enka in ["CRIT Rate", "CRIT DMG", "PEN Ratio", "Energy Regen"]
            if es_decimal:
                if v > 100: v /= 100.0
                elif 0 < v < 2.0: v *= 100.0
            stats_principales[nombre_bonito] = f"{v:.1f}%" if es_decimal else f"{v:.0f}"

    # Daño elemental
    bono_max = 0.0
    for key_cruda, v_raw in stats_crudas.items():
        key_upper = str(key_cruda).upper()
        if "DMG" in key_upper and any(e in key_upper for e in ["PHYSICAL", "FIRE", "ICE", "ELECTRIC", "ETHER"]):
            v = float(v_raw.get("value", 0)) if isinstance(v_raw, dict) else float(v_raw)
            if 0 < v < 2.0: v *= 100.0
            bono_max = max(bono_max, v)
    if bono_max > 0:
        stats_principales["Daño Elem."] = f"{bono_max:.1f}%"

    weapon = personaje.get("weapon", {})

    # Calcular posición en ranking global
    posicion_ranking = None
    total_jugadores = None
    calificacion_ranking = ev["calidad_pct"]
    import json as _json
    ranking_path = os.path.join(BASE_DIR, "guardados", "ranking_global.json")
    if os.path.exists(ranking_path):
        try:
            with open(ranking_path, "r", encoding="utf-8") as f:
                ranking_data = _json.load(f)
            # Buscar el apodo por UID
            mi_apodo = None
            for apodo, datos_j in ranking_data.items():
                if str(datos_j.get("uid", "")) == str(uid):
                    mi_apodo = apodo
                    break
            if mi_apodo:
                # Generar ranking del personaje
                resultados = []
                for apodo, datos_j in ranking_data.items():
                    personajes_r = datos_j.get("personajes", {})
                    if nombre in personajes_r:
                        cal = personajes_r[nombre].get("calificacion", 0)
                        resultados.append((apodo, cal))
                resultados.sort(key=lambda x: x[1], reverse=True)
                total_jugadores = len(resultados)
                for i, (ap, _) in enumerate(resultados, 1):
                    if ap == mi_apodo:
                        posicion_ranking = i
                        break
        except Exception:
            pass

    return {
        "agente": nombre,
        "rango_agente": rango,
        "faccion_agente": faccion,
        "evaluacion_build": eval_letter,
        "elemento": elemento,
        "tipo": rol,
        "rol": rol,
        "wengine": weapon.get("name", ""),
        "refinamiento": weapon.get("refinement", 1),
        "stats_principales": stats_principales,
        "discos": discos_procesados,
        "mindscape": personaje.get("mindscape", 0),
        "nickname": nick,
        "uid": str(uid),
        "nivel_agente": personaje.get("level", 60),
        "substats_counts": conteo_rolls,
        "_stats_reales_calculo": None,
        "eficiencia_arma": 100,
        "calificacion_ranking": calificacion_ranking,
        "calidad_clasica_pct": round(ev.get("calidad_clasica_pct", calificacion_ranking), 2),
        "calidad_dinamica_pct": round(ev.get("calidad_dinamica_pct", calificacion_ranking), 2),
        "calidad_dinamica_raw_pct": round(ev.get("calidad_dinamica_raw_pct", calificacion_ranking), 2),
        "penalizacion_dinamica_pct": round(ev.get("penalizacion_dinamica_pct", 0), 2),
        "prioridad_dinamica": ev.get("prioridad_dinamica", [])[:3],
        "ajustes_dinamicos": ev.get("ajustes_dinamicos", []),
        "breakdown_ranking": None,
        "posicion_ranking": posicion_ranking,
        "total_jugadores": total_jugadores,
    }


@app.get("/uid/{uid}/agente/{nombre_agente}/buildcard")
@limiter.limit("5/minute")
async def buildcard_agente(request: Request, uid: int, nombre_agente: str):
    """Genera y devuelve la build card como imagen PNG."""
    try:
        personajes, nick = await fetch_uid_cached(uid)
    except Exception as e:
        err = str(e).lower()
        if "does not exist" in err or "404" in err:
            raise HTTPException(status_code=404, detail="UID no encontrado")
        if "maintenance" in err:
            raise HTTPException(status_code=503, detail="Enka en mantenimiento")
        raise HTTPException(status_code=500, detail=str(e))

    char_dict = None
    for p in personajes:
        if resolver_nombre(p["name"]).lower() == nombre_agente.lower():
            char_dict = p
            break

    if not char_dict:
        disponibles = [resolver_nombre(p["name"]) for p in personajes]
        raise HTTPException(status_code=404, detail=f"Agente '{nombre_agente}' no encontrado. Disponibles: {disponibles}")

    nombre = resolver_nombre(char_dict["name"])
    datos_tarjeta = construir_datos_tarjeta(char_dict, nombre, nick, uid)

    try:
        exito, resultado = generador.generar_build_card(datos_tarjeta, ruta_salida=None)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando imagen: {e}")

    if not exito:
        raise HTTPException(status_code=500, detail="No se pudo generar la build card")

    resultado.seek(0)
    return StreamingResponse(resultado, media_type="image/png", headers={
        "Content-Disposition": f'inline; filename="Build_{nombre}.png"'
    })


# ─── Descarga temporal de build cards ──────────────────────────────────────────
import uuid
from fastapi import UploadFile, File

_temp_downloads = {}  # {id: (bytes, filename, timestamp)}

@app.post("/download/prepare")
async def prepare_download(file: UploadFile = File(...)):
    """Recibe una imagen y devuelve un ID temporal para descargarla."""
    contenido = await file.read()
    dl_id = str(uuid.uuid4())[:8]
    _temp_downloads[dl_id] = (contenido, file.filename, time.time())
    # Limpiar descargas viejas (>5 min)
    ahora = time.time()
    for k in list(_temp_downloads):
        if ahora - _temp_downloads[k][2] > 300:
            del _temp_downloads[k]
    return {"id": dl_id}

@app.get("/download/{dl_id}")
async def descargar_temp(dl_id: str):
    """Descarga directa del archivo temporal."""
    if dl_id not in _temp_downloads:
        raise HTTPException(status_code=404, detail="Descarga expirada o no encontrada")
    contenido, filename, _ = _temp_downloads.pop(dl_id)
    from io import BytesIO
    return StreamingResponse(BytesIO(contenido), media_type="image/png", headers={
        "Content-Disposition": f'attachment; filename="{filename}"'
    })


# ─── Assets estáticos ─────────────────────────────────────────────────────────
from fastapi.staticfiles import StaticFiles

ASSETS_DIR = os.path.join(BASE_DIR, "assets")
IMAGES_DIR = os.path.join(BASE_DIR, "images")


@app.get("/assets/list")
def listar_assets(categoria: str = Query(None, description="Subcarpeta: images, images/Iconos, images/wengine, etc.")):
    """Lista los archivos disponibles en /assets. Filtrar por categoría opcional."""
    base = ASSETS_DIR
    if categoria:
        base = os.path.join(ASSETS_DIR, categoria)
    if not os.path.isdir(base):
        raise HTTPException(status_code=404, detail=f"Categoría '{categoria}' no encontrada")
    archivos = []
    for root, dirs, files in os.walk(base):
        for f in files:
            ruta_rel = os.path.relpath(os.path.join(root, f), ASSETS_DIR)
            archivos.append(ruta_rel)
    return {"total": len(archivos), "archivos": sorted(archivos)}


@app.get("/images/list")
def listar_images(categoria: str = Query(None, description="Subcarpeta: Iconos, wengine, discos, elementos, etc.")):
    """Lista los archivos disponibles en /images. Filtrar por categoría opcional."""
    base = IMAGES_DIR
    if categoria:
        base = os.path.join(IMAGES_DIR, categoria)
    if not os.path.isdir(base):
        raise HTTPException(status_code=404, detail=f"Categoría '{categoria}' no encontrada")
    archivos = []
    for root, dirs, files in os.walk(base):
        for f in files:
            ruta_rel = os.path.relpath(os.path.join(root, f), IMAGES_DIR)
            archivos.append(ruta_rel)
    return {"total": len(archivos), "archivos": sorted(archivos)}


# ─── Endpoints para Frontend Web ──────────────────────────────────────────────
from logica_danos import LogicaDmg
from efectos_wengines import MAPA_WENGINES, CONFIG_WENGINES
from efectos_sets import MAPA_EFECTOS_SETS, CONFIG_SETS
from efectos_core import MAPA_CORE, CONFIG_CORE_UI
from efectos_mindscapes import CONFIG_MINDSCAPES, MAPA_MINDSCAPES
from efectos_potencial import MAPA_POTENCIAL, CONFIG_POTENCIAL
from substats_config import calcular_rolls_substat, valor_substat

logica_dmg = LogicaDmg()
wengines_data = cargador.cargar_wengine("wengine.csv", campos_numericos=["Ataque wengine"])
sets_data = cargador.cargar_csv("sets.csv", campos_numericos=["valor"])
discos_data_raw = cargador.cargar_csv("discos.csv", campos_numericos=["valor"])
substats_data = cargador.cargar_csv("substat.csv", campos_numericos=["valor"])
enemigos_data = cargador.cargar_csv("enemigos.csv")


@app.get("/api/agentes/lista")
def api_listar_agentes():
    """Lista agentes con sus datos básicos para los dropdowns."""
    return [{"nombre": a["Nombre"], "elemento": a.get("elemento", ""), "tipo": a.get("Tipo", ""), "rango": a.get("Rango", "")} for a in agentes_data]


@app.get("/api/agentes/{nombre}/detalle")
def api_detalle_agente(nombre: str):
    """Devuelve stats base, habilidades, wengines compatibles, etc."""
    agente = next((a for a in agentes_data if a["Nombre"].lower() == nombre.lower()), None)
    if not agente:
        raise HTTPException(status_code=404, detail="Agente no encontrado")

    # Stats base
    mapeo = {
        'nivel': 'Nivel', 'ataque': 'Ataque', 'puntos de vida': 'Puntos_Vida',
        'defensa': 'Defensa', 'probabilidad': 'Probabilidad_crítico',
        'daño crítico': 'Daño_crítico', 'daño elemental': 'Daño_elemental',
        'Maestría de anomalía': 'Maestría_Anomalía', 'tasa de anomalía': 'Tasa_de_Anomalía',
        'Impacto': 'Impacto', 'Tasa de perforación': 'Tasa_de_Perforación',
        'Perforación plana': 'Perforación_Plana', 'Recuperación de energía': 'Recuperación_energía'
    }
    base_stats = {}
    for csv_h, stat_k in mapeo.items():
        val = agente.get(csv_h, "0")
        try:
            base_stats[stat_k] = float(str(val).replace(",", "."))
        except:
            base_stats[stat_k] = 0.0

    # Habilidades
    import pandas as pd
    hab_path = os.path.join(DATOS_DIR, "agentes", f"{agente['Nombre']}.csv")
    habilidades = []
    if os.path.exists(hab_path):
        try:
            df = pd.read_csv(hab_path, delimiter=';', encoding='utf-8-sig', dtype=str)
            df = df.rename(columns=lambda x: x.strip())
            for _, row in df.iterrows():
                habilidades.append({
                    "nombre": row.get("Habilidad", ""),
                    "multiplicador": float(str(row.get("Multiplicador", "0")).replace(",", ".")),
                    "aturdimiento": float(str(row.get("Aturdimiento", "0")).replace(",", ".")),
                    "etiqueta": row.get("Etiqueta_Dano", "normal")
                })
        except:
            pass

    # Wengines compatibles
    tipo_agente = agente.get("Tipo", "")
    wengines_compat = []
    for w_nombre, w_datos in wengines_data.items():
        if w_datos.get("tipow", "") == tipo_agente or w_datos.get("agente", "") == agente["Nombre"]:
            wengines_compat.append({
                "nombre": w_nombre,
                "ataque": float(str(w_datos.get("Ataque wengine", "0")).replace(",", ".")),
                "es_firma": w_datos.get("agente", "") == agente["Nombre"],
                "pasiva": w_datos.get("pasiva", "")
            })

    # Core config
    core_config = CONFIG_CORE_UI.get(agente["Nombre"], {})
    tiene_potencial = agente["Nombre"] in CONFIG_POTENCIAL

    return {
        "nombre": agente["Nombre"],
        "elemento": agente.get("elemento", ""),
        "tipo": tipo_agente,
        "faccion": agente.get("Facción", ""),
        "rango": agente.get("Rango", ""),
        "base_stats": base_stats,
        "habilidades": habilidades,
        "wengines": wengines_compat,
        "core_config": core_config,
        "tiene_potencial": tiene_potencial,
        "tiene_mindscape": agente["Nombre"] in MAPA_MINDSCAPES,
    }


@app.get("/api/enemigos")
def api_listar_enemigos():
    """Lista enemigos disponibles."""
    return [{"nombre": e["Nombre"]} for e in enemigos_data]


@app.get("/api/sets")
def api_listar_sets():
    """Lista sets de discos."""
    return [{"nombre": s["Nombre"], "stat": s.get("stat", ""), "valor": s.get("valor", 0), "elemento": s.get("elemento", "")} for s in sets_data]


@app.get("/api/discos")
def api_datos_discos():
    """Devuelve main stats por slot y substats disponibles."""
    discos_por_slot = {}
    for d in discos_data_raw:
        slot = int(d.get("slot", 0))
        if slot not in discos_por_slot:
            discos_por_slot[slot] = []
        discos_por_slot[slot].append({"nombre": d.get("nombre", ""), "stat": d.get("stat", ""), "tipo": d.get("tipo", ""), "valor": d.get("valor", 0)})
    return {"slots": discos_por_slot, "substats": substats_data}


@app.get("/api/uids")
def api_uids_guardadas():
    """Devuelve las UIDs guardadas."""
    import json as _j
    uids_path = os.path.join(BASE_DIR, "guardados", "uids", "uids.json")
    if not os.path.exists(uids_path):
        return {}
    with open(uids_path, "r", encoding="utf-8") as f:
        return _j.load(f)


MAPA_STATS_JSON_FE = {
    "HP": "Puntos_Vida", "ATK": "Ataque", "DEF": "Defensa",
    "Percent HP": "Puntos_Vida", "Percent ATK": "Ataque", "Percent DEF": "Defensa",
    "CRIT Rate": "Probabilidad_crítico", "CRIT DMG": "Daño_crítico",
    "PEN Ratio": "Tasa_de_Perforación", "PEN": "Perforación_Plana",
    "Anomaly Proficiency": "Maestría_Anomalía", "Physical DMG Bonus": "Daño_elemental",
    "Fire DMG Bonus": "Daño_elemental", "Ice DMG Bonus": "Daño_elemental",
    "Electric DMG Bonus": "Daño_elemental", "Ether DMG Bonus": "Daño_elemental",
    "Wind DMG Bonus": "Daño_elemental",
    "Anomaly Mastery": "Tasa_de_Anomalía", "Impact": "Impacto",
    "Energy Regen": "Recuperación_energía",
}

def parsear_discos_importados(discos_raw):
    """Parsea discos de Enka al formato del frontend."""
    resultado = {}
    for disco in discos_raw:
        slot = int(disco.get("slot", 0))
        if slot < 1 or slot > 6:
            continue
        set_name = MAPA_SETS_ID.get(int(disco.get("set_id", 0)), "Ninguno")
        main_stat_data = disco.get("main_stat", {})
        main_name_en = main_stat_data.get("name", "")
        main_es = MAPA_STATS_JSON_FE.get(main_name_en, "")
        subs = []
        for sub in disco.get("sub_stats", []):
            sub_name_en = sub.get("name", "")
            valor_raw = str(sub.get("value", "0"))
            es_pct = "%" in valor_raw or "Percent" in sub_name_en
            try:
                valor_float = float(valor_raw.replace("%", "").replace(",", "").strip())
            except:
                continue
            clave_base = MAPA_STATS_JSON_FE.get(sub_name_en, "")
            if not clave_base:
                continue
            stats_planas = ["Maestría_Anomalía", "Perforación_Plana", "Impacto"]
            stats_pct = ["Probabilidad_crítico", "Daño_crítico", "Tasa_de_Anomalía", "Tasa_de_Perforación", "Recuperación_energía"]
            if clave_base in stats_planas:
                unique_key = f"{clave_base}_plano"
            elif clave_base in stats_pct:
                unique_key = f"{clave_base}_porcentual"
            else:
                unique_key = f"{clave_base}_{'porcentual' if es_pct else 'plano'}"
            base_val = valor_substat(unique_key)
            if base_val <= 0:
                continue
            total_rolls = max(1, round(valor_float / base_val))
            subs.append({"stat": unique_key, "rolls": max(0, total_rolls - 1), "value": valor_float})
        resultado[str(slot)] = {"set": set_name, "main": main_es, "subs": subs}
    return resultado


@app.get("/api/uid/{uid}/completo")
@limiter.limit("10/minute")
async def api_uid_completo(request: Request, uid: int):
    """Devuelve datos completos con discos parseados para el frontend."""
    try:
        personajes, nick = await fetch_uid_cached(uid)
    except Exception as e:
        err = str(e).lower()
        if "does not exist" in err or "404" in err:
            raise HTTPException(status_code=404, detail="UID no encontrado")
        if "maintenance" in err:
            raise HTTPException(status_code=503, detail="Enka en mantenimiento")
        raise HTTPException(status_code=500, detail=str(e))
    resultado = []
    for p in personajes:
        weapon = p.get("weapon", {})
        w_name = weapon.get("name", "")
        w_atk = 0
        if w_name and w_name in wengines_data:
            w_atk = float(str(wengines_data[w_name].get("Ataque wengine", "0")).replace(",", "."))
        resultado.append({
            "name": resolver_nombre(p["name"]),
            "level": p.get("level", 60),
            "mindscape": p.get("mindscape", 0),
            "weapon": {"name": w_name, "refinement": weapon.get("refinement", 1), "ataque": w_atk},
            "discos_parseados": parsear_discos_importados(p.get("discs", [])),
        })
    return {"uid": uid, "nick": nick, "agentes": resultado}


@app.get("/api/locales/{lang}")
def api_locales(lang: str):
    """Devuelve el archivo de traducciones."""
    import json as _j
    path = os.path.join(BASE_DIR, "locales", f"{lang}.json")
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail=f"Idioma '{lang}' no disponible")
    with open(path, "r", encoding="utf-8") as f:
        return _j.load(f)


class CalcularRequest(BaseModel):
    agente: str
    habilidad: str = ""
    wengine: str = "Ninguno"
    refinamiento: int = 1
    wengine_stacks: int = 0
    enemigo: str = ""
    mindscape: int = 0
    core_activo: bool = False
    core_stacks: int = 1
    nivel_potencial: int = 0
    set1: str = "Ninguno"
    set2: str = "Ninguno"
    discos: dict = {}
    buffs: dict = {}
    miasma: bool = False
    estado_enemigo: str = "Normal"
    elemento_vortex: str = "Automático"
    vortex_tiempo: float = 3.0
    vortex_additional_mv: float = 0.0
    vortex_buff: float = 0.0


@app.post("/api/calcular")
def api_calcular(req: CalcularRequest):
    """Calcula DPS con los parámetros dados."""
    # Obtener agente
    agente = next((a for a in agentes_data if a["Nombre"].lower() == req.agente.lower()), None)
    if not agente:
        raise HTTPException(status_code=404, detail="Agente no encontrado")

    # Stats base
    mapeo = {
        'ataque': 'Ataque', 'puntos de vida': 'Puntos_Vida', 'defensa': 'Defensa',
        'probabilidad': 'Probabilidad_crítico', 'daño crítico': 'Daño_crítico',
        'daño elemental': 'Daño_elemental', 'Maestría de anomalía': 'Maestría_Anomalía',
        'tasa de anomalía': 'Tasa_de_Anomalía', 'Impacto': 'Impacto',
        'Tasa de perforación': 'Tasa_de_Perforación', 'Perforación plana': 'Perforación_Plana',
        'Recuperación de energía': 'Recuperación_energía'
    }
    params = {}
    for csv_h, stat_k in mapeo.items():
        val = agente.get(csv_h, "0")
        try:
            params[stat_k] = float(str(val).replace(",", "."))
        except:
            params[stat_k] = 0.0

    elemento = agente.get("elemento", "").lower()
    tipo_agente = agente.get("Tipo", "")

    # Wengine stats
    if req.wengine and req.wengine != "Ninguno" and req.wengine in wengines_data:
        w = wengines_data[req.wengine]
        params["Ataque"] = params.get("Ataque", 0) + float(str(w.get("Ataque wengine", "0")).replace(",", "."))
        stat_map_w = {
            "Ataque": "Ataque", "Recuperación de energía": "Recuperación_energía",
            "Maestría de Anomalía del agente": "Maestría_Anomalía", "Tasa de anomalía": "Tasa_de_Anomalía",
            "Probabilidad de crítico": "Probabilidad_crítico", "Daño crítico": "Daño_crítico",
            "Tasa de perforación": "Tasa_de_Perforación", "Puntos de vida": "Puntos_Vida",
            "Defensa": "Defensa", "Impacto": "Impacto"
        }
        for w_key, p_key in stat_map_w.items():
            v = float(str(w.get(w_key, "0")).replace(",", "."))
            if v != 0:
                params[p_key] = params.get(p_key, 0) + v

    # Habilidad (multiplicador)
    import pandas as pd
    hab_path = os.path.join(DATOS_DIR, "agentes", f"{agente['Nombre']}.csv")
    etiqueta_dano = "normal"
    if req.habilidad and os.path.exists(hab_path):
        try:
            df = pd.read_csv(hab_path, delimiter=';', encoding='utf-8-sig', dtype=str)
            df = df.rename(columns=lambda x: x.strip())
            for _, row in df.iterrows():
                if row.get("Habilidad", "").strip() == req.habilidad.strip():
                    params["Multiplicador_de_ataques"] = float(str(row.get("Multiplicador", "0")).replace(",", "."))
                    params["Aturdimiento"] = float(str(row.get("Aturdimiento", "0")).replace(",", "."))
                    etiqueta_dano = row.get("Etiqueta_Dano", "normal")
                    break
        except:
            pass

    params["Etiqueta_Dano"] = etiqueta_dano

    # Enemigo
    if req.enemigo:
        enemigo = next((e for e in enemigos_data if e["Nombre"].lower() == req.enemigo.lower()), None)
        if enemigo:
            params["Defensa_Base"] = float(str(enemigo.get("Defensa base del enemigo", "953")).replace(",", "."))
            params["Defensa_Plana"] = float(str(enemigo.get("Defensa plana del enemigo", "0")).replace(",", "."))
            params["Resistencia_Fuego"] = float(str(enemigo.get("Resistencia fuego", "0")).replace(",", "."))
            params["Resistencia_Electrico"] = float(str(enemigo.get("Resistencia electrico", "0")).replace(",", "."))
            params["Resistencia_Hielo"] = float(str(enemigo.get("Resistencia hielo", "0")).replace(",", "."))
            params["Resistencia_Físico"] = float(str(enemigo.get("Resistencia físico", "0")).replace(",", "."))
            params["Resistencia_Etereo"] = float(str(enemigo.get("Resistencia etereo", "0")).replace(",", "."))
            params["Resistencia_Viento"] = float(str(enemigo.get("Resistencia viento", "0")).replace(",", "."))

    # Discos main stats
    for slot_str, disco_info in req.discos.items():
        main = disco_info.get("main", "")
        if main:
            for d in discos_data_raw:
                if int(d.get("slot", 0)) == int(slot_str) and d.get("nombre", "") == main:
                    stat_key = d.get("stat", "")
                    valor = float(d.get("valor", 0))
                    if d.get("tipo") == "porcentual":
                        params[stat_key] = params.get(stat_key, 0) + valor
                    else:
                        params[stat_key] = params.get(stat_key, 0) + valor
                    break
        # Substats
        for sub in disco_info.get("subs", []):
            stat_key = sub.get("stat", "")
            rolls = int(sub.get("rolls", 1))
            if stat_key:
                base_val = valor_substat(stat_key)
                if base_val:
                    param_key = stat_key.replace("_porcentual", "").replace("_plano", "")
                    params[param_key] = params.get(param_key, 0) + (base_val * rolls)

    # Sets (bono 2 piezas)
    for set_name in [req.set1, req.set2]:
        if set_name and set_name != "Ninguno":
            set_info = next((s for s in sets_data if s["Nombre"] == set_name), None)
            if set_info:
                stat_key = set_info.get("stat", "")
                valor = float(set_info.get("valor", 0))
                elem_set = set_info.get("elemento", "todos")
                if elem_set == "todos" or elem_set.lower() == elemento:
                    params[stat_key] = params.get(stat_key, 0) + valor

    # Buffs manuales del usuario
    for k, v in req.buffs.items():
        try:
            params[k] = params.get(k, 0) + float(v)
        except:
            pass

    # Miasma
    if req.miasma:
        params['Miasma'] = 1.8
        params['DMG_Taken'] = params.get('DMG_Taken', 0) - 25.0
    else:
        params['Miasma'] = 1.0

    params['Tipo'] = tipo_agente
    params['Nombre_Agente'] = agente['Nombre']
    params['Estado_Enemigo'] = req.estado_enemigo
    params['Elemento_Vortex'] = req.elemento_vortex
    params['Vortex_Tiempo'] = req.vortex_tiempo
    params['Vortex_Additional_MV'] = req.vortex_additional_mv
    params['Vortex_Buff'] = req.vortex_buff

    # Calcular
    try:
        dmg, sheer, anomaly, disorder, abloom, vortex, stats_combate = logica_dmg.calcular_todos_danos(params, elemento)
        return {
            "dano_general": round(dmg, 1),
            "dano_sheer": round(sheer, 1),
            "dano_anomalia": round(anomaly, 1),
            "dano_disorder": round(disorder, 1),
            "dano_abloom": round(abloom, 1),
            "dano_vortex": round(vortex, 1),
            "stats_combate": {k: str(v) if not isinstance(v, (int, float)) else round(v, 2) for k, v in stats_combate.items()},
            "params_usados": {k: round(v, 2) if isinstance(v, float) else v for k, v in params.items() if isinstance(v, (int, float))}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en cálculo: {str(e)}")


# ─── Frontend estático ────────────────────────────────────────────────────────
if os.path.isdir(FRONTEND_DIR):
    @app.get("/app")
    async def serve_frontend_app():
        return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

    app.mount("/frontend", StaticFiles(directory=FRONTEND_DIR), name="frontend")

app.mount("/assets", StaticFiles(directory=ASSETS_DIR), name="assets")
app.mount("/images", StaticFiles(directory=IMAGES_DIR), name="images")
