"""
optimizador.py — Simulador de builds y proyección de techo teórico para ZZZ.

Flujo principal:
  encontrar_mejor_build()       — rankea combos (arma × set × discos) por score de daño
  simular_proyeccion_realista() — calcula el techo con build perfecta y muestra las stats ideales
  generar_reporte_detallado()   — exporta CSV de auditoría
"""

import copy
import csv
import os
import gc
from logica_recomendaciones import (
    CONFIG_ROLES,
    CONFIG_SETS_ROLES,
    MAPA_SETS_ELEMENTALES,
    EXCEPCIONES_AGENTES,
)
from substats_config import VALORES_SUBSTATS
from analizador_marginal import AnalizadorMarginal

ROLLS_BASE_POR_DISCO  = 4 
MEJORAS_POR_DISCO     = 5 
TOTAL_DISCOS          = 6


def _calcular_score_build(stats_f: dict, meta_dano: str, elemento: str,
                          logica_dmg) -> tuple:
    """
    Devuelve (score, d_norm, d_sheer, d_anom) para un estado de stats dado.

    Modelo de anomalía mejorado:
    ─────────────────────────────
    La Tasa de Anomalía determina con qué frecuencia se aplica la anomalía.
    Base = 100 %; cada punto extra reduce el intervalo de aplicación.
    Multiplicador efectivo = tasa / 100  (lineal, no raíz cuadrada).
    El Bono de Acumulación escala cuánto se acumula por ataque, por lo que
    también multiplica linealmente el DPS de anomalía.
    """
    try:
        res = logica_dmg.calcular_todos_danos(stats_f, elemento)
        d_norm   = res[0] if len(res) > 0 else 0.0
        d_sheer  = res[1] if len(res) > 1 else 0.0
        d_anom   = res[2] if len(res) > 2 else 0.0
        d_abloom = res[4] if len(res) > 4 else 0.0
        d_vortex = res[5] if len(res) > 5 else 0.0

        tasa_efectiva = max(100.0, stats_f.get("Tasa_de_Anomalía", 100.0)) / 100.0
        bono_acum     = 1.0 + stats_f.get("Bono_Acumulación", 0.0) / 100.0

        d_anom_dps = (d_anom + d_abloom) * tasa_efectiva * bono_acum

        if meta_dano == "anomalia":
            score = d_anom_dps
        elif meta_dano == "sheer":
            score = d_sheer
        elif meta_dano == "vortex":
            score = d_vortex
        else:
            score = max(d_norm, d_anom_dps, d_sheer, d_vortex)

        return score, d_norm, d_sheer, d_anom_dps

    except Exception:
        return 0.0, 0.0, 0.0, 0.0


class OptimizadorBuild:

    def __init__(self, gestor_estadisticas, cargador, logica_dmg, traductor=None):
        self.gestor    = gestor_estadisticas
        self.cargador  = cargador
        self.logica_dmg = logica_dmg
        self.i18n = traductor
        self.analizador_marginal = AnalizadorMarginal(gestor_estadisticas, logica_dmg)

    def _obtener_bases_de_datos(self) -> dict:
        for obj in gc.get_objects():
            if type(obj).__name__ == "CalculadoraZZZ":
                return {
                    "wengines":  getattr(obj, "wengine_data", {}),
                    "sets":      getattr(obj, "sets_data", []),
                    "discos":    getattr(obj, "discos_data", {}),
                    "substats":  getattr(obj, "substats_db", []),
                }
        return {
            "wengines": getattr(self.cargador, "wengine_data",
                         getattr(self.cargador, "wengines_data", {})),
            "sets":     getattr(self.cargador, "sets_data", []),
            "discos":   getattr(self.cargador, "discos_data",
                         getattr(self.cargador, "mapa_discos", {})),
            "substats": getattr(self.cargador, "substats_db", []),
        }

    def encontrar_mejor_build(
        self,
        estado_base,
        agente_data,
        stats_gui_reales=None,
        elemento_input="Físico",
        etiqueta_dano="general",
        **kwargs,
    ):
        if not agente_data or not estado_base:
            return None

        nombre_agente = str(agente_data.get("Nombre", "Desconocido")).strip()
        rol_agente    = agente_data.get("Tipo", "Atacante")
        elemento      = elemento_input or agente_data.get("Elemento", "Físico")
        base_pura_dict = kwargs.get("base_stats") or copy.deepcopy(
            getattr(estado_base, "base_stats", {})
        )

        config_rol      = copy.deepcopy(CONFIG_ROLES.get(rol_agente, CONFIG_ROLES["Atacante"]))
        sets_permitidos = CONFIG_SETS_ROLES.get(rol_agente, {"ideal": [], "funcional": []})
        lista_sets_4pc  = sets_permitidos.get("ideal", []) + MAPA_SETS_ELEMENTALES.get(elemento, [])
        lista_sets_2pc  = sets_permitidos.get("funcional", []) + lista_sets_4pc

        wengines_info  = []
        meta_dano      = "general"
        etiqueta_dano  = "elemental"

        if nombre_agente in EXCEPCIONES_AGENTES:
            exc = EXCEPCIONES_AGENTES[nombre_agente]
            meta_dano     = exc.get("meta_dano", meta_dano)
            etiqueta_dano = exc.get("etiqueta_dano", etiqueta_dano)

            for key in ("main_4", "main_5", "main_6"):
                if key in exc:
                    config_rol[key] = exc[key]

            if "subs" in exc:
                config_rol["subs"] = exc["subs"]

            if "sets" in exc:
                if "4pc" in exc["sets"]:
                    lista_sets_4pc = exc["sets"]["4pc"]
                    lista_sets_2pc = exc["sets"].get("2pc", lista_sets_4pc)
                elif "ideal" in exc["sets"]:
                    lista_sets_4pc = exc["sets"]["ideal"]
                    lista_sets_2pc = exc["sets"].get("funcional", []) + lista_sets_4pc

            for w in exc.get("wengines", {}).get("ideal", []) + \
                     exc.get("wengines", {}).get("funcional", []):
                if isinstance(w, tuple) and len(w) >= 2:
                    wengines_info.append({"nombre": str(w[0]).strip(), "instruccion": w[1]})
                else:
                    wengines_info.append({"nombre": str(w).strip(), "instruccion": "max"})

        w_act = getattr(estado_base, "nombre_wengine", None)
        if w_act and w_act != "Ninguno":
            if not any(w["nombre"] == w_act for w in wengines_info):
                wengines_info.append({"nombre": w_act, "instruccion": "actual"})
        if not wengines_info:
            wengines_info.append({"nombre": "W-Engine Generico", "instruccion": "max"})

        db_refs   = self._obtener_bases_de_datos()
        w_keys    = list(db_refs["wengines"].keys())
        for w_info in wengines_info:
            target = w_info["nombre"].strip().lower()
            for key in w_keys:
                if key.strip().lower() == target:
                    w_info["nombre"] = key
                    break

        for s in (estado_base.sets.get("set1"), estado_base.sets.get("set2")):
            if s and s != "Ninguno":
                lista_sets_2pc.append(s)

        def _opts(key):
            return list(dict.fromkeys(
                config_rol.get(key, {}).get("general", []) +
                config_rol.get(key, {}).get("particular", [])
            ))

        main_4_opts = _opts("main_4") or ["Probabilidad_crítico"]
        main_5_opts = _opts("main_5") or ["Daño_elemental"]
        main_6_opts = _opts("main_6") or ["Ataque"]

        for slot, opts in ((4, main_4_opts), (5, main_5_opts), (6, main_6_opts)):
            val = estado_base.discos.get(slot)
            if val and val not in opts:
                opts.append(val)

        lista_sets_4pc = list(dict.fromkeys(lista_sets_4pc))
        lista_sets_2pc = list(dict.fromkeys(lista_sets_2pc))

        from efectos_wengines import CONFIG_WENGINES
        try:
            from efectos_sets import CONFIG_SETS
        except ImportError:
            CONFIG_SETS = {}

        kwargs_sim = kwargs.copy()
        kwargs_sim.pop("base_stats", None)
        w_db   = kwargs_sim.pop("wengine_db",  db_refs["wengines"])
        s_db   = kwargs_sim.pop("sets_db",     db_refs["sets"])
        d_db   = kwargs_sim.pop("discos_db",   db_refs["discos"])
        sub_db = kwargs_sim.pop("substats_db", db_refs["substats"])
        kwargs_sim["buffs_nodos"] = kwargs_sim.get("buffs_nodos", {})

        resultados = []

        for arma_info in wengines_info:
            arma       = arma_info["nombre"]
            instruccion = arma_info["instruccion"]
            cfg_arma   = CONFIG_WENGINES.get(arma, {})
            ref        = getattr(estado_base, "refinamiento", 1) if arma == w_act else 1

            for set4 in lista_sets_4pc:
                cfg_set4 = CONFIG_SETS.get(set4, {})
                for set2 in lista_sets_2pc:
                    if set4 == set2:
                        continue
                    for m4 in main_4_opts:
                        for m5 in main_5_opts:
                            for m6 in main_6_opts:
                                try:
                                    ev = copy.deepcopy(estado_base)
                                    ev.nombre_wengine = arma
                                    ev.sets  = {"set1": set4, "set2": set2, "set3": "Ninguno"}
                                    ev.discos[4] = m4
                                    ev.discos[5] = m5
                                    ev.discos[6] = m6
                                    ev.refinamiento = ref

                                    if instruccion == "actual":
                                        ev.stacks = getattr(estado_base, "stacks", 0)
                                    elif instruccion == "max":
                                        ev.stacks = cfg_arma.get("max_stacks", 5)
                                    elif str(instruccion).lstrip("-").isdigit():
                                        ev.stacks = int(instruccion)
                                    else:
                                        ev.stacks = getattr(estado_base, "stacks", 0)

                                    ev.set_condicion = True
                                    ev.set_stacks    = cfg_set4.get("max_stacks", 5) if isinstance(cfg_set4, dict) else 5
                                    ev.core_activo   = True
                                    ev.core_stacks   = 6

                                    stats_f = self.gestor.calcular_stats_finales(
                                        base_stats   = copy.deepcopy(base_pura_dict),
                                        estado_build = ev,
                                        wengine_db   = w_db,
                                        sets_db      = s_db,
                                        discos_db    = d_db,
                                        substats_db  = sub_db,
                                        elemento_agente = elemento,
                                        tipo_agente  = rol_agente,
                                        **kwargs_sim,
                                    )

                                    if stats_gui_reales:
                                        CLAVES_ENTORNO = {
                                            "Defensa_Base", "Resistencia_porcentual",
                                            "Reduccion_DEF_enemigo", "DMG_Taken", "Miasma",
                                            "Multiplicador_de_ataques", "Aturdimiento",
                                            "Pen_Res_Fisico", "Pen_Res_Fuego", "Pen_Res_Hielo",
                                            "Pen_Res_Electrico", "Pen_Res_Etereo", "Pen_Res_Viento",
                                            "Resistencia_Fuego", "Resistencia_Electrico",
                                            "Resistencia_Hielo", "Resistencia_Físico",
                                            "Resistencia_Etereo", "Resistencia_Viento",
                                        }
                                        for k, v in stats_gui_reales.items():
                                            if k in CLAVES_ENTORNO:
                                                try:
                                                    stats_f[k] = float(str(v).replace("%", "").replace(",", "."))
                                                except Exception:
                                                    stats_f[k] = v

                                    if "Nivel_Enemigo" not in stats_f:
                                        stats_f["Nivel_Enemigo"] = stats_f.get("Nivel_Agente", 60.0)
                                    estado_enemigo_val = kwargs.get("estado_enemigo", "Normal")
                                    if "Multiplicador_Aturdimiento" not in stats_f:
                                        stats_f["Multiplicador_Aturdimiento"] = (
                                            150.0 if estado_enemigo_val == "Stun_Boss" else 100.0
                                        )
                                    stats_f["Etiqueta_Dano"] = etiqueta_dano

                                    score, d_norm, d_sheer, d_anom = _calcular_score_build(
                                        stats_f, meta_dano, elemento, self.logica_dmg
                                    )

                                    resultados.append({
                                        "wengine":          arma,
                                        "wengine_stacks":   ev.stacks,
                                        "set4":             set4,
                                        "set2":             set2,
                                        "sets":             f"4pz {set4} + 2pz {set2}",
                                        "main_4":           m4,
                                        "main_5":           m5,
                                        "main_6":           m6,
                                        "discos":           f"IV: {m4} | V: {m5} | VI: {m6}",
                                        "score":            score,
                                        "danos_detallados": {"normal": d_norm, "anomalia": d_anom, "sheer": d_sheer},
                                        "stats":            stats_f,
                                    })
                                except Exception:
                                    pass

        resultados.sort(key=lambda x: x["score"], reverse=True)
        if not resultados:
            return None

        vistos = {}
        for r in resultados:
            clave = (r["wengine"], r["set4"], r["set2"])
            if clave not in vistos:
                vistos[clave] = r

        ranking = sorted(vistos.values(), key=lambda x: x["score"], reverse=True)
        mejor   = ranking[0]
        mejor["ranking_completo"] = ranking[:150]

        #try:
        #    self.generar_reporte_detallado(ranking[:150], nombre_agente)
        #except Exception:
        #    pass

        return mejor

    def analizar_valor_marginal_substats(
        self,
        estado_base,
        agente_data,
        stats_gui_reales=None,
        elemento_input="Físico",
        **kwargs,
    ):
        """Calcula cuánto rinde +1 roll de cada substat candidata en la build actual."""
        if not agente_data or not estado_base:
            return None

        nombre_agente = str(agente_data.get("Nombre", "Desconocido")).strip()
        rol_agente = agente_data.get("Tipo", "Atacante")
        elemento = elemento_input or agente_data.get("Elemento", agente_data.get("elemento", "Físico"))
        base_pura = kwargs.pop("base_stats", None) or copy.deepcopy(getattr(estado_base, "base_stats", {}))

        db_refs = self._obtener_bases_de_datos()
        w_db = kwargs.pop("wengine_db", db_refs["wengines"])
        s_db = kwargs.pop("sets_db", db_refs["sets"])
        d_db = kwargs.pop("discos_db", db_refs["discos"])
        sub_db = kwargs.pop("substats_db", db_refs["substats"])

        stats_entorno = {}
        if stats_gui_reales:
            claves_entorno = {
                "Defensa_Base", "Resistencia_porcentual",
                "Reduccion_DEF_enemigo", "DMG_Taken", "Miasma",
                "Multiplicador_de_ataques", "Aturdimiento",
                "Pen_Res_Fisico", "Pen_Res_Fuego", "Pen_Res_Hielo",
                "Pen_Res_Electrico", "Pen_Res_Etereo", "Pen_Res_Viento",
                "Resistencia_Fuego", "Resistencia_Electrico",
                "Resistencia_Hielo", "Resistencia_Físico",
                "Resistencia_Etereo", "Resistencia_Viento",
                "Etiqueta_Dano", "Estado_Enemigo",
            }
            for k, v in stats_gui_reales.items():
                if k in claves_entorno:
                    try:
                        stats_entorno[k] = float(str(v).replace("%", "").replace(",", "."))
                    except Exception:
                        stats_entorno[k] = v

        return self.analizador_marginal.analizar(
            estado_build=estado_base,
            base_stats=base_pura,
            elemento=elemento,
            rol_agente=rol_agente,
            nombre_agente=nombre_agente,
            wengine_db=w_db,
            sets_db=s_db,
            discos_db=d_db,
            substats_db=sub_db,
            stats_entorno=stats_entorno,
            **kwargs,
        )

    def simular_proyeccion_realista(
        self,
        mejor_config,
        elemento,
        delta_stats,
        rol_agente,
        nombre_agente,
        estado_base,
        min_basura=1,
        etiqueta_dano="normal",
        ranking_completo=None,
        set4_override=None,
        set2_override=None,
        **kwargs,
    ):
        """
        Calcula el techo teórico distribuyendo los 54 rolls (6 discos × 9)
        de forma determinista y óptima respetando las reglas del juego.

        Reglas de ZZZ por disco:
        • 4 subs distintas (cada una empieza con 1 roll)
        • 5 upgrades extra que pueden ir a cualquier sub del mismo disco

        La proyección no usa random: primero llena ideales, luego decentes,
        luego basura en cada disco según las restricciones de main stat.
        """

        _db_pre = self._obtener_bases_de_datos()
        _base_pura_pre = kwargs.get("base_stats",
                         copy.deepcopy(getattr(estado_base, "base_stats", {})))
        try:
            _stats_actual_pre = self.gestor.calcular_stats_finales(
                base_stats      = copy.deepcopy(_base_pura_pre),
                estado_build    = copy.deepcopy(estado_base),
                wengine_db      = _db_pre["wengines"],
                sets_db         = _db_pre["sets"],
                discos_db       = _db_pre["discos"],
                substats_db     = _db_pre["substats"],
                elemento_agente = elemento,
                tipo_agente     = rol_agente,
                sets_externos   = None,
                buffs_nodos     = {},
                stacks_core     = 0,
            )
            score_base, *_ = _calcular_score_build(
                _stats_actual_pre, meta_dano, elemento, self.logica_dmg
            )
        except Exception:
            score_base = mejor_config.get("score", 1)
        config_rol = copy.deepcopy(CONFIG_ROLES.get(rol_agente, CONFIG_ROLES["Atacante"]))
        meta_dano  = "general"

        if nombre_agente in EXCEPCIONES_AGENTES:
            exc = EXCEPCIONES_AGENTES[nombre_agente]
            if "subs"      in exc: config_rol["subs"]  = exc["subs"]
            if "meta_dano" in exc: meta_dano            = exc["meta_dano"]

        lista_ideal  = config_rol["subs"].get("ideal",  [])
        lista_decente = config_rol["subs"].get("decente", [])
        lista_basura  = config_rol["subs"].get("basura",  [])

        if not lista_ideal:
            lista_ideal = ["Ataque_porcentual", "Probabilidad_crítico_porcentual", "Daño_crítico_porcentual"]
        if not lista_decente:
            lista_decente = ["Ataque_plano", "Perforación_Plana_plano"]
        if not lista_basura:
            lista_basura = ["Puntos_Vida_plano", "Defensa_plano"]

        ev = copy.deepcopy(estado_base)
        ev.nombre_wengine = mejor_config["wengine"]
        _set4 = set4_override if set4_override else mejor_config["set4"]
        _set2 = set2_override if set2_override else mejor_config["set2"]
        ev.sets           = {"set1": _set4, "set2": _set2, "set3": "Ninguno"}
        ev.discos[4]      = mejor_config["main_4"]
        ev.discos[5]      = mejor_config["main_5"]
        ev.discos[6]      = mejor_config["main_6"]
        ev.refinamiento   = (
            getattr(estado_base, "refinamiento", 1)
            if mejor_config["wengine"] == getattr(estado_base, "nombre_wengine", None)
            else 1
        )
        ev.stacks         = mejor_config.get("wengine_stacks", 0)
        ev.set_condicion  = True
        ev.set_stacks     = 5
        ev.core_activo    = True
        ev.core_stacks    = 6
        ev.substats_counts = {}

        mains_por_slot = [
            "Puntos_Vida_plano",
            "Ataque_plano",
            "Defensa_plano",
            mejor_config["main_4"],
            mejor_config["main_5"],
            mejor_config["main_6"], 
        ]

        def stat_base(s):
            return s.replace("_porcentual", "").replace("_plano", "").lower()

        resumen_rolls = {}
        discos_ideales = {}

        for slot_idx, main_actual in enumerate(mains_por_slot):
            slot_num = slot_idx + 1
            main_b = stat_base(main_actual)

            def pool(lista):
                return [s for s in lista if stat_base(s) not in main_b and main_b not in stat_base(s)]

            p_ideal   = pool(lista_ideal)
            p_decente = pool(lista_decente)
            p_basura  = pool(lista_basura)

            subs_disco = []
            for cand_list in (p_ideal, p_decente, p_basura):
                for s in cand_list:
                    if s not in subs_disco:
                        subs_disco.append(s)
                    if len(subs_disco) == ROLLS_BASE_POR_DISCO:
                        break
                if len(subs_disco) == ROLLS_BASE_POR_DISCO:
                    break

            subs_slot = {}
            for s in subs_disco:
                ev.substats_counts[s] = ev.substats_counts.get(s, 0) + 1
                resumen_rolls[s]      = resumen_rolls.get(s, 0) + 1
                subs_slot[s]          = subs_slot.get(s, 0) + 1

            candidatos_upgrade = [s for s in p_ideal if s in subs_disco]
            if not candidatos_upgrade:
                candidatos_upgrade = [s for s in p_decente if s in subs_disco]
            if not candidatos_upgrade and subs_disco:
                candidatos_upgrade = subs_disco[:1]

            if candidatos_upgrade:
                for i in range(MEJORAS_POR_DISCO):
                    target = candidatos_upgrade[i % len(candidatos_upgrade)]
                    ev.substats_counts[target] = ev.substats_counts.get(target, 0) + 1
                    resumen_rolls[target]       = resumen_rolls.get(target, 0) + 1
                    subs_slot[target]           = subs_slot.get(target, 0) + 1

            discos_ideales[slot_num] = {"main": main_actual, "subs": subs_slot}

        db_refs  = self._obtener_bases_de_datos()
        base_pura = kwargs.get("base_stats", copy.deepcopy(getattr(estado_base, "base_stats", {})))

        ev.set_condicion = False
        ev.set_stacks    = 0
        ev.core_activo   = False
        ev.core_stacks   = 0

        try:
            stats_nuevas = self.gestor.calcular_stats_finales(
                base_stats      = copy.deepcopy(base_pura),
                estado_build    = ev,
                wengine_db      = db_refs["wengines"],
                sets_db         = db_refs["sets"],
                discos_db       = db_refs["discos"],
                substats_db     = db_refs["substats"],
                elemento_agente = elemento,
                tipo_agente     = rol_agente,
                sets_externos   = None,
                buffs_nodos     = {},
                stacks_core     = 0,
            )
        except Exception as e:
            print(f"[Optimizador] Error calculando techo: {e}")
            stats_nuevas = copy.deepcopy(mejor_config["stats"])

        for k, v in mejor_config["stats"].items():
            if k not in stats_nuevas:
                stats_nuevas[k] = v
        stats_nuevas["Etiqueta_Dano"] = mejor_config["stats"].get("Etiqueta_Dano", etiqueta_dano)

        score_nuevo, *_ = _calcular_score_build(stats_nuevas, meta_dano, elemento, self.logica_dmg)
        aumento = ((score_nuevo - score_base) / score_base * 100) if score_base > 0 else 0.0
        _overcap_warnings = {}
        try:
            ev_combat = copy.deepcopy(ev)
            ev_combat.set_condicion = True
            ev_combat.set_stacks    = 5
            ev_combat.core_activo   = True
            ev_combat.core_stacks   = 6
            ev_combat.substats_counts = dict(resumen_rolls)

            stats_combat = self.gestor.calcular_stats_finales(
                base_stats      = copy.deepcopy(base_pura),
                estado_build    = ev_combat,
                wengine_db      = db_refs["wengines"],
                sets_db         = db_refs["sets"],
                discos_db       = db_refs["discos"],
                substats_db     = db_refs["substats"],
                elemento_agente = elemento,
                tipo_agente     = rol_agente,
                sets_externos   = None,
                buffs_nodos     = {},
                stacks_core     = 6,
            )

            CAPS_REALES = {"Probabilidad_crítico": 100.0}
            for stat_k, cap_v in CAPS_REALES.items():
                val = stats_combat.get(stat_k, 0)
                if val > cap_v:
                    exceso = val - cap_v
                    _overcap_warnings[stat_k] = {
                        "valor": val, "cap": cap_v, "exceso": exceso,
                        "rolls_desperdiciados": round(exceso / 2.4)
                    }
        except Exception as e:
            print(f"[Optimizador] Error calculando overcap: {e}")

        _t = (lambda k, d: self.i18n.t(k, default=d)) if self.i18n else (lambda k, d: d)
        _ts = lambda s: self.i18n.t(f"substats.{s}", default=s.replace("_porcentual", " %").replace("_plano", "").replace("_", " ")) if self.i18n else s.replace("_porcentual", " %").replace("_plano", "").replace("_", " ")

        lineas = []
        for cat_label, cat_list in (
            (_t("recom.cat_ideal", "⭐ Ideal"),    lista_ideal),
            (_t("recom.cat_decente", "○ Decent"),  lista_decente),
            (_t("recom.cat_basura", "✗ Junk"),     lista_basura),
        ):
            entries = []
            for s in cat_list:
                cant = resumen_rolls.get(s, 0)
                if cant > 0:
                    nombre = _ts(s)
                    entries.append(f"  {nombre}: {cant} roll{'s' if cant > 1 else ''}")
            if entries:
                lineas.append(cat_label)
                lineas.extend(entries)

        texto_rolls = "\n".join(lineas) if lineas else "Sin distribución calculada."
        stats_teoricas = _formatear_stats_ideales(stats_nuevas, rol_agente, nombre_agente, meta_dano, self.i18n)

        ranking_ref = ranking_completo or mejor_config.get("ranking_completo", [])
        armas_vistas = {}
        for r in ranking_ref:
            arma = r.get("wengine", "")
            if arma and arma not in armas_vistas:
                armas_vistas[arma] = r.get("score", 0)
            if len(armas_vistas) >= 3:
                break

        top_armas = list(armas_vistas.keys())
        if top_armas:
            score_top1 = list(armas_vistas.values())[0]
            lineas_armas = []
            for i, (arma, score) in enumerate(armas_vistas.items()):
                pct = (score / score_top1 * 100) if score_top1 > 0 else 100
                medal = ("🥇", "🥈", "🥉")[i]
                lineas_armas.append(f"  {medal} {arma}  ({pct:.0f}%)")
            texto_armas = "\n".join(lineas_armas)
        else:
            texto_armas = f"  {mejor_config['wengine']}"

        def _calcular_tier(pct_objetivo, resumen_rolls_full, ev_base, lista_i, lista_d, lista_b):
            """Simula la build con menos rolls ideales para representar el tier objetivo."""
            total_ideal_full = sum(resumen_rolls_full.get(s, 0) for s in lista_i)
            if total_ideal_full == 0:
                return resumen_rolls_full, stats_nuevas

            factor = pct_objetivo / 100.0
            target_ideal = max(0, int(total_ideal_full * factor))
            delta = total_ideal_full - target_ideal

            ev_tier = copy.deepcopy(ev_base)
            ev_tier.substats_counts = {}

            rolls_tier = {}
            for k, v in resumen_rolls_full.items():
                rolls_tier[k] = v

            quitados = 0
            for s in lista_i:
                if quitados >= delta:
                    break
                disponible = rolls_tier.get(s, 0)
                quitar = min(disponible, delta - quitados)
                rolls_tier[s] = disponible - quitar
                quitados += quitar
                if lista_b:
                    basura_s = lista_b[0]
                    rolls_tier[basura_s] = rolls_tier.get(basura_s, 0) + quitar

            for k, v in rolls_tier.items():
                if v > 0:
                    ev_tier.substats_counts[k] = v

            try:
                stats_tier = self.gestor.calcular_stats_finales(
                    base_stats      = copy.deepcopy(base_pura),
                    estado_build    = ev_tier,
                    wengine_db      = db_refs["wengines"],
                    sets_db         = db_refs["sets"],
                    discos_db       = db_refs["discos"],
                    substats_db     = db_refs["substats"],
                    elemento_agente = elemento,
                    tipo_agente     = rol_agente,
                    sets_externos   = None,
                    buffs_nodos     = {},
                    stacks_core     = 0,
                )
            except Exception:
                stats_tier = stats_nuevas
            return rolls_tier, stats_tier

        ev_100 = copy.deepcopy(ev)
        ev_100.substats_counts = dict(resumen_rolls)

        rolls_90, stats_90 = _calcular_tier(90, resumen_rolls, ev_100, lista_ideal, lista_decente, lista_basura)
        rolls_80, stats_80 = _calcular_tier(80, resumen_rolls, ev_100, lista_ideal, lista_decente, lista_basura)

        def _fmt_rolls(rolls_dict, lista_i, lista_d, lista_b):
            lineas = []
            for cat_label, cat_list in (
                (_t("recom.cat_ideal", "⭐ Ideal"),    lista_i),
                (_t("recom.cat_decente", "○ Decent"),  lista_d),
                (_t("recom.cat_basura", "✗ Junk"),     lista_b),
            ):
                entries = []
                for s in cat_list:
                    cant = rolls_dict.get(s, 0)
                    if cant > 0:
                        nombre = _ts(s)
                        entries.append(f"  {nombre}: {cant} roll{'s' if cant > 1 else ''}")
                if entries:
                    lineas.append(cat_label)
                    lineas.extend(entries)
            return "\n".join(lineas) if lineas else "Sin distribución."

        texto_rolls_90 = _fmt_rolls(rolls_90, lista_ideal, lista_decente, lista_basura)
        texto_rolls_80 = _fmt_rolls(rolls_80, lista_ideal, lista_decente, lista_basura)

        stats_t90 = _formatear_stats_ideales(stats_90, rol_agente, nombre_agente, meta_dano, self.i18n)
        stats_t80 = _formatear_stats_ideales(stats_80, rol_agente, nombre_agente, meta_dano, self.i18n)

        _set4 = mejor_config['set4']
        _discos = mejor_config['discos']
        _l1 = self.i18n.t('recom.techo_teorico', set4=_set4) if self.i18n else f"TECHO TEÓRICO con {_set4}"
        _l2 = self.i18n.t('recom.discos_ideales', discos=_discos) if self.i18n else f"Discos ideales: {_discos}"
        encabezado = f"{_l1}\n{_l2}"

        mensaje = (
            f"{encabezado}\n\n"
            f"DISTRIBUCIÓN DE 54 ROLLS (100% perfecto):\n{texto_rolls}\n\n"
            f"STATS IDEALES TEÓRICAS (pre-combate) (100%):\n{stats_teoricas}"
        )

        def _discos_para_tier(discos_full, rolls_tier_dict):
            """Reconstruye discos_ideales ajustado a los rolls del tier dado.
            Garantiza que el total de rolls por disco nunca supere 9 (4 base + 5 mejoras)."""
            MAX_ROLLS_DISCO = 9
            result = {}
            for sn, info in discos_full.items():
                subs_adj = {}
                for s, r in info["subs"].items():
                    r_tier = rolls_tier_dict.get(s, 0)
                    ratio = r_tier / max(resumen_rolls.get(s, r), 1)
                    subs_adj[s] = max(1 if r > 0 else 0, round(r * ratio))
                total = sum(subs_adj.values())
                if total > MAX_ROLLS_DISCO:
                    exceso = total - MAX_ROLLS_DISCO
                    for s in sorted(subs_adj, key=lambda x: -subs_adj[x]):
                        if exceso <= 0:
                            break
                        reducible = subs_adj[s] - 1 
                        quitar = min(reducible, exceso)
                        subs_adj[s] -= quitar
                        exceso -= quitar
                result[sn] = {"main": info["main"], "subs": subs_adj}
            return result

        discos_ideales_90 = _discos_para_tier(discos_ideales, rolls_90)
        discos_ideales_80 = _discos_para_tier(discos_ideales, rolls_80)

        return {
            "score_nuevo":  score_nuevo,
            "aumento_pct":  aumento,
            "stats_nuevas": stats_nuevas,
            "encabezado":   encabezado,
            "resumen_rolls_100": resumen_rolls,
            "resumen_rolls_90":  rolls_90,
            "resumen_rolls_80":  rolls_80,
            "discos_ideales_100": discos_ideales,
            "discos_ideales_90":  discos_ideales_90,
            "discos_ideales_80":  discos_ideales_80,
            "overcap_warnings":   _overcap_warnings,
            "set4_usado":         _set4,
            "set2_usado":         _set2,
            "stats_100": stats_nuevas,
            "stats_90":  stats_90,
            "stats_80":  stats_80,
            "texto_rolls_100": texto_rolls,
            "texto_rolls_90":  texto_rolls_90,
            "texto_rolls_80":  texto_rolls_80,
            "stats_str_100": stats_teoricas,
            "stats_str_90":  stats_t90,
            "stats_str_80":  stats_t80,
            "lista_ideal":   lista_ideal,
            "lista_decente": lista_decente,
            "lista_basura":  lista_basura,
            "mains_config":  {
                "main_4": mejor_config["main_4"],
                "main_5": mejor_config["main_5"],
                "main_6": mejor_config["main_6"],
                "set4":   mejor_config["set4"],
                "set2":   mejor_config["set2"],
            },
            "mensaje":      mensaje,
        }

    def generar_reporte_detallado(self, resultados, nombre_agente, proyeccion=None):
        carpeta   = os.path.dirname(os.path.abspath(__file__))
        ruta_csv  = os.path.join(carpeta, f"Reporte_Auditoria_{nombre_agente.replace(' ', '_')}.csv")

        if isinstance(resultados, dict):
            resultados = resultados.get("ranking_completo", [resultados])

        try:
            with open(ruta_csv, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f, delimiter=";")
                writer.writerow([f"REPORTE DE AUDITORIA — {nombre_agente}"])
                writer.writerow([])
                writer.writerow(["Puesto", "W-Engine", "Sets", "Discos (IV/V/VI)",
                                  "Score", "Daño Normal", "Anomalía", "Sheer"])
                for i, r in enumerate(resultados[:50]):
                    d = r.get("danos_detallados", {})
                    writer.writerow([
                        i + 1,
                        r.get("wengine"),
                        r.get("sets"),
                        r.get("discos"),
                        f"{r.get('score', 0):,.0f}",
                        f"{d.get('normal', 0):,.0f}",
                        f"{d.get('anomalia', 0):,.0f}",
                        f"{d.get('sheer', 0):,.0f}",
                    ])
        except Exception:
            pass

def _formatear_stats_ideales(stats: dict, rol: str, nombre_agente: str, meta_dano: str, i18n=None) -> str:
    """
    Devuelve un string con las stats más relevantes para el agente,
    ordenadas y con unidades correctas, listo para mostrar en la UI.
    """
    lines = []
    _t = (lambda k, d: i18n.t(k, default=d)) if i18n else (lambda k, d: d)

    def añadir(label: str, key: str, decimales: int = 0, sufijo: str = ""):
        val = stats.get(key, 0.0)
        if val > 0:
            fmt = f"{val:.{decimales}f}{sufijo}"
            lines.append(f"  {label}: {fmt}")

    añadir(_t("recom.stat_atk", "ATK"),             "Ataque",               0)
    añadir(_t("recom.stat_crit_rate", "CRIT Rate"), "Probabilidad_crítico",  1, " %")
    añadir(_t("recom.stat_crit_dmg", "CRIT DMG"),   "Daño_crítico",          1, " %")
    añadir(_t("recom.stat_elemental", "Elemental DMG"), "Daño_elemental",    1, " %")
    añadir(_t("recom.stat_bono_dmg", "DMG Bonus"),  "Daño_Adicional",        1, " %")
    añadir(_t("recom.stat_pen_ratio", "PEN Ratio"), "Tasa_de_Perforación",   1, " %")
    añadir(_t("recom.stat_pen_flat", "Flat PEN"),   "Perforación_Plana",     0)

    if meta_dano == "anomalia" or rol in ("Anomalo", "Anomalía"):
        añadir(_t("recom.stat_maestria", "Anomaly Prof."),  "Maestría_Anomalía",   0)
        añadir(_t("recom.stat_tasa_anom", "Anomaly Mastery"), "Tasa_de_Anomalía",  1, " %")
        añadir(_t("recom.stat_bono_acum", "Buildup Bonus"), "Bono_Acumulación",    1, " %")

    if meta_dano == "sheer" or rol == "Ruptura":
        añadir(_t("recom.stat_hp", "HP"),             "Puntos_Vida",    0)
        añadir(_t("recom.stat_sheer", "Sheer Force"), "Sheer_force",    0)
        añadir(_t("recom.stat_impacto", "Impact"),    "Impacto",        0)

    añadir(_t("recom.stat_regen", "Energy Regen"),   "Recuperación_energía", 1, " %")

    return "\n".join(lines) if lines else "  (Sin datos disponibles)"
