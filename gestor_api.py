import asyncio
import enka
import logging
from traductor import traductor_global as i18n
import aiohttp
import csv
import os
from mapeos_enka import AVATAR_ID_MAP

try:
    from enka.enums import zzz as zzz_enums
    from enka.calc import zzz as zzz_calc

    def _elemento_zzz_desconocido(cls, value):
        if value == "Wind":
            return cls.UNKNOWN
        return None

    def _stat_zzz_desconocida(cls, value):
        if value in (32301, 32303, 32305):
            miembro = int.__new__(cls, value)
            miembro._name_ = f"WIND_DMG_BONUS_{value}"
            miembro._value_ = value
            cls._value2member_map_[value] = miembro
            return miembro
        return None

    zzz_enums.Element._missing_ = classmethod(_elemento_zzz_desconocido)
    zzz_enums.StatType._missing_ = classmethod(_stat_zzz_desconocida)
    zzz_calc.PROP_ID_TO_NAME.update({
        32301: "AddedDamageRatio_Wind_Base",
        32303: "AddedDamageRatio_Wind_Delta",
        32305: "AddedDamageRatio_Wind_Delta",
    })
    zzz_calc.DEFAULT_PROPS.update({
        "AddedDamageRatio_Wind_Base": 0,
        "AddedDamageRatio_Wind_Delta": 0,
    })
except Exception:
    pass

_original_json = aiohttp.ClientResponse.json

async def patched_json(self, *args, **kwargs):

    data = await _original_json(self, *args, **kwargs)
    def limpiar_medallas(obj):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if key.lower() in ["medallist", "medal_list"] and isinstance(value, list):
                    obj[key] = [m for m in value if m]
                else:
                    limpiar_medallas(value)
        elif isinstance(obj, list):
            for item in obj:
                limpiar_medallas(item)

    try:
        limpiar_medallas(data)
    except Exception as e:
        print(f"Error al limpiar JSON: {e}")
            
    return data

aiohttp.ClientResponse.json = patched_json

def _cargar_elementos_locales():
    ruta = os.path.join(os.path.dirname(__file__), "datos", "agentes.csv")
    elementos = {}
    mapa = {
        "fisico": "PHYSICAL",
        "físico": "PHYSICAL",
        "fuego": "FIRE",
        "hielo": "ICE",
        "electrico": "ELECTRIC",
        "eléctrico": "ELECTRIC",
        "etereo": "ETHER",
        "etéreo": "ETHER",
        "viento": "WIND",
    }
    try:
        with open(ruta, "r", encoding="utf-8-sig", newline="") as f:
            for fila in csv.DictReader(f, delimiter=";"):
                nombre = (fila.get("Nombre") or "").strip()
                elemento = (fila.get("elemento") or fila.get("Elemento") or "").strip().lower()
                if nombre and elemento:
                    elementos[nombre.lower()] = mapa.get(elemento, elemento.upper())
    except Exception:
        pass
    return elementos


ELEMENTOS_LOCALES = _cargar_elementos_locales()


def obtener_elemento_agente(agent):
    nombre = str(getattr(agent, "name", "") or "").strip().lower()
    elemento_local = ELEMENTOS_LOCALES.get(nombre)
    if elemento_local == "WIND":
        return elemento_local

    if agent.elements:
        elemento = agent.elements[0]
        nombre_elemento = str(getattr(elemento, "name", elemento))
        if nombre_elemento != "UNKNOWN":
            return nombre_elemento

    return elemento_local or i18n.t("ui.comun.desconocido", default="Unknown")


def procesar_agente(agent):
    stats_dict = {}
    if agent.stats:
        for stat_obj in agent.stats.values():
            stats_dict[str(stat_obj.name)] = {
                "value": stat_obj.value,
                "formatted": stat_obj.formatted_value
            }

    weapon_data = {} 
    if agent.w_engine:
        w = agent.w_engine
        ref_val = w.phase if hasattr(w, "phase") else 1
        weapon_data = {
            "name": str(w.name),
            "rarity": w.rarity_num, 
            "level": w.level,
            "refinement": int(ref_val),
            "main_stat": {
                "name": str(w.main_stat.name),
                "value": w.main_stat.formatted_value
            }
        }

    discs_list = []
    
    equipos_raw = getattr(agent, "equipments", getattr(agent, "discs", []))

    for disc in equipos_raw:
        subs = []
        raw_subs = getattr(disc, "sub_stats", [])
        
        for sub in raw_subs:
            subs.append({
                "name": str(sub.name), 
                "value": str(sub.formatted_value)
            })

        try: slot_int = int(disc.slot)
        except: slot_int = 0
            
        try: set_id_int = int(disc.set_id)
        except: set_id_int = 0

        m_name = "Desconocido"
        m_val = "0"
        if hasattr(disc, "main_stat") and disc.main_stat:
            m_name = str(disc.main_stat.name)
            m_val = str(disc.main_stat.formatted_value)

        discs_list.append({
            "slot": slot_int,
            "set_id": set_id_int,
            "level": disc.level,
            "main_stat": {
                "name": m_name,
                "value": m_val
            },
            "sub_stats": subs
        })

    mindscape_raw = getattr(agent, "mindscape", [])
    if isinstance(mindscape_raw, list):
        mindscape_count = len(mindscape_raw)
    else:
        mindscape_count = int(mindscape_raw) if mindscape_raw else 0

    return {
        "name": str(agent.name),
        "level": agent.level,
        "element": obtener_elemento_agente(agent),
        "specialty": str(agent.specialty.name) if agent.specialty else i18n.t("ui.comun.desconocido", default="Unknown"),
        "stats": stats_dict,
        "weapon": weapon_data,
        "discs": discs_list,
        "mindscape": mindscape_count,
        "uid": getattr(agent.w_engine, "uid", ""),
    }

class GestorApi:
    def __init__(self, logger=None):
        self.logger = logging.getLogger(__name__)
        self._ultimo_error = None

    def obtener_datos_uid(self, uid):
        try:
            uid_int = int(uid)
            self._ultimo_error = None
            resultado = asyncio.run(self._fetch_async(uid_int))
            if self._ultimo_error:
                return None, None, i18n.t("ui.dialogo_uid.error_consulta", default=f"Error: {self._ultimo_error}", error=self._ultimo_error)
            return resultado[0], resultado[1], "OK"
        except Exception as e:
            return None, None, i18n.t("ui.dialogo_uid.error_consulta", default=f"Error: {e}", error=str(e))

    async def _fetch_async(self, uid):
        personajes = []
        nick = i18n.t("ui.comun.desconocido", default="Desconocido")
        
        async with enka.ZZZClient(lang="en") as client:
            try:
                try: await client.update_assets()                 
                except: pass
                
                data = await client.fetch_showcase(uid)
                
                if data.player: nick = data.player.nickname
                if data.agents:
                    for agent in data.agents:
                        personajes.append(procesar_agente(agent))
                        
            except Exception as e:
                error_str = str(e)
                if "validation" in error_str or "MedalList" in error_str:
                    print(f"Error de validación detectado (Medallas): {e}")
                else:
                    print(f"API Error: {e}")
                self._ultimo_error = error_str
        return personajes, nick
