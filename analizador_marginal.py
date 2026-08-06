import copy

from logica_recomendaciones import CONFIG_ROLES, EXCEPCIONES_AGENTES, normalizar_clave_substat
from substats_config import VALORES_SUBSTATS, valor_substat

MAX_SUBSTATS_POR_DISCO = 4
MAX_ROLLS_POR_DISCO = 9
MAX_ROLLS_POR_SUBSTAT = 6


def _normalizar_texto(texto):
    return str(texto or "").strip().lower().replace("-", "").replace("  ", " ")


def _base_stat(clave):
    return str(clave or "").replace("_porcentual", "").replace("_plano", "")


def _resolver_excepcion(nombre_agente, excepciones=None):
    excepciones = excepciones or EXCEPCIONES_AGENTES
    if nombre_agente in excepciones:
        return excepciones[nombre_agente]
    nombre_norm = _normalizar_texto(nombre_agente)
    mejor = None
    mejor_len = 0
    for clave in excepciones:
        clave_norm = _normalizar_texto(clave)
        if clave_norm == nombre_norm:
            return excepciones[clave]
        if clave_norm in nombre_norm or nombre_norm in clave_norm:
            if len(clave_norm) > mejor_len:
                mejor = clave
                mejor_len = len(clave_norm)
    return excepciones.get(mejor, {}) if mejor else {}


def _resolver_config(nombre_agente, rol_agente, config_roles=None, excepciones=None):
    config_roles = config_roles or CONFIG_ROLES
    config = copy.deepcopy(config_roles.get(rol_agente, config_roles.get("Atacante", {})))
    excep = _resolver_excepcion(nombre_agente, excepciones)
    if excep:
        for key in ("main_4", "main_5", "main_6", "subs"):
            if key in excep:
                config[key] = copy.deepcopy(excep[key])
    return config, excep


def candidatos_desde_config(nombre_agente, rol_agente, config_roles=None, excepciones=None,
                            incluir_decente=True, incluir_basura=False):
    """Devuelve substats candidatas existentes en datos/substat.csv, guiadas por diccionarios."""
    config, _ = _resolver_config(nombre_agente, rol_agente, config_roles, excepciones)
    subs_cfg = config.get("subs", {})
    listas = [subs_cfg.get("ideal", [])]
    if incluir_decente:
        listas.append(subs_cfg.get("decente", []))
    if incluir_basura:
        listas.append(subs_cfg.get("basura", []))

    candidatos = []
    for lista in listas:
        for stat in lista:
            clave = normalizar_clave_substat(stat)
            if clave and clave in VALORES_SUBSTATS and clave not in candidatos:
                candidatos.append(clave)
    return candidatos


def main_stat_slot(slot, estado_build):
    """Devuelve la clave base del main stat del slot, sin sufijo porcentual/plano."""
    if int(slot) == 1:
        return "Puntos_Vida"
    if int(slot) == 2:
        return "Ataque"
    if int(slot) == 3:
        return "Defensa"

    detalles = getattr(estado_build, "discos_detalles", {}) or {}
    main = (detalles.get(int(slot), {}) or {}).get("main")
    if not main or main == "Ninguno":
        main = (getattr(estado_build, "discos", {}) or {}).get(int(slot), "")
    return _base_stat(normalizar_clave_substat(main))


def substat_choca_con_main(substat_key, slot, estado_build):
    main_base = main_stat_slot(slot, estado_build)
    sub_base = _base_stat(substat_key)
    return bool(main_base and sub_base and main_base == sub_base)


def estado_slot_substats(slot, estado_build):
    detalles = getattr(estado_build, "discos_detalles", {}) or {}
    disco = detalles.get(int(slot), {}) or {}
    subs = disco.get("subs", {}) or {}
    resultado = {}
    for info in subs.values():
        stat = info.get("stat")
        if not stat or stat == "Ninguno":
            continue
        mejoras = int(info.get("rolls", 0) or 0)
        resultado[stat] = max(resultado.get(stat, 0), 1 + mejoras)
    return resultado


def ubicaciones_validas(substat_key, estado_build):
    """Lista slots donde puede existir o mejorar esa substat sin violar reglas de disco."""
    ubicaciones = []
    for slot in range(1, 7):
        if substat_choca_con_main(substat_key, slot, estado_build):
            continue

        subs = estado_slot_substats(slot, estado_build)
        total_rolls = sum(subs.values())
        if total_rolls >= MAX_ROLLS_POR_DISCO:
            continue

        if substat_key in subs:
            if subs[substat_key] < MAX_ROLLS_POR_SUBSTAT:
                ubicaciones.append({"slot": slot, "tipo": "mejorar_substat", "rolls_actuales": subs[substat_key]})
        elif len(subs) < MAX_SUBSTATS_POR_DISCO:
            ubicaciones.append({"slot": slot, "tipo": "nueva_substat", "rolls_actuales": 0})
    return ubicaciones


class AnalizadorMarginal:
    def __init__(self, gestor_estadisticas, logica_dmg):
        self.gestor = gestor_estadisticas
        self.logica_dmg = logica_dmg

    def _calcular_score(self, stats, elemento, meta_dano="general"):
        res = self.logica_dmg.calcular_todos_danos(stats, elemento)
        d_norm = res[0] if len(res) > 0 else 0.0
        d_sheer = res[1] if len(res) > 1 else 0.0
        d_anom = res[2] if len(res) > 2 else 0.0
        d_abloom = res[4] if len(res) > 4 else 0.0
        d_vortex = res[5] if len(res) > 5 else 0.0

        tasa_efectiva = max(100.0, stats.get("Tasa_de_Anomalía", 100.0)) / 100.0
        bono_acum = 1.0 + stats.get("Bono_Acumulación", 0.0) / 100.0
        d_anom_dps = (d_anom + d_abloom) * tasa_efectiva * bono_acum

        if meta_dano == "anomalia":
            score = d_anom_dps
        elif meta_dano == "sheer":
            score = d_sheer
        else:
            score = max(d_norm, d_sheer, d_anom_dps)

        return score, {"normal": d_norm, "sheer": d_sheer, "anomalia": d_anom_dps, "vortex": d_vortex}

    def _calcular_stats(self, estado_build, base_stats, elemento, rol_agente,
                        wengine_db, sets_db, discos_db, substats_db, **kwargs):
        return self.gestor.calcular_stats_finales(
            base_stats=copy.deepcopy(base_stats),
            estado_build=estado_build,
            wengine_db=wengine_db,
            sets_db=sets_db,
            discos_db=discos_db,
            substats_db=substats_db,
            elemento_agente=elemento,
            tipo_agente=rol_agente,
            **kwargs,
        )

    def analizar(self, estado_build, base_stats, elemento, rol_agente, nombre_agente,
                 wengine_db, sets_db, discos_db, substats_db, candidatos=None,
                 stats_entorno=None, meta_dano=None, config_roles=None,
                 excepciones=None, **kwargs):
        config, excep = _resolver_config(nombre_agente, rol_agente, config_roles, excepciones)
        if meta_dano is None:
            meta_dano = excep.get("meta_dano", "general")

        if candidatos is None:
            candidatos = candidatos_desde_config(nombre_agente, rol_agente, config_roles, excepciones)
        candidatos = [c for c in candidatos if c in VALORES_SUBSTATS]

        estado_base = copy.deepcopy(estado_build)
        stats_base = self._calcular_stats(
            estado_base, base_stats, elemento, rol_agente,
            wengine_db, sets_db, discos_db, substats_db, **kwargs
        )
        if stats_entorno:
            stats_base.update(stats_entorno)
        score_base, danos_base = self._calcular_score(stats_base, elemento, meta_dano)

        resultados = []
        descartadas = []
        for substat in candidatos:
            ubicaciones = ubicaciones_validas(substat, estado_base)
            if not ubicaciones:
                descartadas.append({"substat": substat, "motivo": "sin_ubicacion_valida"})
                continue

            estado_sim = copy.deepcopy(estado_base)
            estado_sim.substats_counts = dict(getattr(estado_sim, "substats_counts", {}) or {})
            estado_sim.substats_counts[substat] = estado_sim.substats_counts.get(substat, 0) + 1

            stats_sim = self._calcular_stats(
                estado_sim, base_stats, elemento, rol_agente,
                wengine_db, sets_db, discos_db, substats_db, **kwargs
            )
            if stats_entorno:
                stats_sim.update(stats_entorno)
            score_sim, danos_sim = self._calcular_score(stats_sim, elemento, meta_dano)
            delta = score_sim - score_base
            delta_pct = (delta / score_base * 100.0) if score_base > 0 else 0.0

            resultados.append({
                "substat": substat,
                "valor_roll": valor_substat(substat),
                "score_base": score_base,
                "score_simulado": score_sim,
                "delta": delta,
                "delta_pct": delta_pct,
                "danos_base": danos_base,
                "danos_simulados": danos_sim,
                "ubicaciones": ubicaciones,
                "categoria_diccionario": self._categoria_diccionario(substat, config),
            })

        resultados.sort(key=lambda x: x["delta_pct"], reverse=True)
        return {
            "score_base": score_base,
            "danos_base": danos_base,
            "meta_dano": meta_dano,
            "resultados": resultados,
            "descartadas": descartadas,
        }

    def _categoria_diccionario(self, substat, config):
        subs = config.get("subs", {})
        for categoria in ("ideal", "decente", "basura"):
            normalizadas = {normalizar_clave_substat(s) for s in subs.get(categoria, [])}
            if substat in normalizadas:
                return categoria
        return "fuera_diccionario"
