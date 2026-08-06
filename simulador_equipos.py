"""
simulador_equipos.py — Simula el impacto de diferentes compañeros de equipo
y calcula scores de daño para rankear soportes sugeridos.

Score por rol (fórmula unificada con optimizador.py):
  Atacante  : ATK × (1 + CR×CD) × (1 + DMG%) × (1 + PEN%)
  Anomalo   : ATK × (1 + AM/100) × tasa_efectiva × (1 + DMG%) × (1 + PEN%)
  Aturdidor : ATK × (1 + CR×CD) × (1 + DMG%) × impacto_factor
  Ruptura   : HP  × (1 + CR×CD) × (1 + DMG%)
"""

import copy
from efectos_soportes import MAPA_SOPORTES_AGENTES


EQUIPOS_IDEALES = {
    "Ellen":          ["Soukaku", "Lycaon", "Rina"],
    "Zhu Yuan":       ["Nicole", "Qingyi", "Anby"],
    "Jane":           ["Seth", "Burnice", "Lucy"],
    "Grace":          ["Astra Yao", "Yuzuha", "Nicole", "Vivian"],
    "Soldier 11":     ["Lucy", "Ben", "Koleda"],
    "Nekomata":       ["Nicole", "Anby", "Lucy"],
    "Miyabi":         ["Soukaku", "Yuzuha", "Lycaon", "Nicole", "Vivian", "Astra Yao"],
    "Anton":          ["Grace", "Rina"],
    "Corin":          ["Lycaon", "Rina", "Soukaku"],
    "Billy":          ["Nicole", "Anby"],
    "Yuzuha":         ["Seth", "Rina"],
    "Astra Yao":      ["Soukaku", "Lucy"],
    "Soldier 0 - Anby": ["Orphie & Magus", "Trigger", "Nicole"],
    "Harumasa":       ["Qingyi", "Rina", "Astra Yao"],
    "Burnice":        ["Lucy", "Caesar", "Seth"],
    "Yanagi":         ["Seth", "Rina", "Astra Yao"],
    "Evelyn":         ["Caesar", "Lucy", "Astra Yao"],
    "Lighter":        ["Lucy", "Caesar"],
    "Piper":          ["Lucy", "Caesar"],
    "Hugo":           ["Astra Yao", "Rina"],
}

PENALIZACIONES_ENEMIGOS = {
    "Autonomous Assault Unit - Typhon Destroyer": ["Hielo", "Congelación"],
}

ELEMENTOS_SOPORTES = {
    "Soukaku": "Hielo",    "Lycaon": "Hielo",   "Yuzuha": "Hielo",
    "Lucy": "Fuego",       "Ben": "Fuego",       "Koleda": "Fuego",  "Burnice": "Fuego",
    "Nicole": "Etereo",    "Zhu Yuan": "Etereo",
    "Anby": "Electrico",   "Grace": "Electrico", "Seth": "Electrico", "Rina": "Electrico",
    "Caesar": "Fisico",    "Qingyi": "Electrico",
    "Astra Yao": "Hielo",  "Vivian": "Fuego",    "Yanagi": "Electrico",
    "Lighter": "Fuego",    "Pan Yinhu": "Fisico", "Lucia": "Fisico",
    "Orphie & Magus": "Etereo", "Trigger": "Electrico",
}

CONFIG_SOPORTES_SUGERIDOS = {
    "Atacante": ["Soukaku", "Lucy", "Rina", "Caesar", "Astra Yao", "Nicole"],
    "Anomalo":  ["Seth", "Rina", "Yanagi", "Burnice", "Grace", "Astra Yao"],
    "Aturdidor":["Soukaku", "Lucy", "Nicole"],
    "Ruptura":  ["Lucia", "Pan Yinhu"],
}

_MOCK_STATS_BASE = {
    "Ataque": 2400, "Maestría_Anomalía": 120, "Defensa": 800,
    "Puntos_Vida": 10000, "Impacto": 140, "Recuperación_energía": 1.2,
    "Probabilidad_crítico": 50.0, "Daño_crítico": 100.0,
}
_MOCK_OVERRIDES = {
    "soukaku":       {"Ataque": 3200},
    "lucy":          {"Ataque": 3000},
    "astra yao":     {"Ataque": 3500, "Probabilidad_crítico": 60.0, "Daño_crítico": 120.0},
    "seth":          {"Ataque": 2200, "Maestría_Anomalía": 380},
    "rina":          {"Tasa_de_Perforación": 45.0, "Recuperación_energía": 1.6},
    "caesar":        {"Impacto": 200, "Ataque": 2800},
    "ben":           {"Defensa": 2800},
    "lighter":       {"Impacto": 220, "Ataque": 2600},
    "pan yinhu":     {"Ataque": 2800},
    "orphie & magus":{"Ataque": 3000, "Recuperación_energía": 2.2},
    "yanagi":        {"Maestría_Anomalía": 320, "Tasa_de_Anomalía": 80.0},
    "lucia":         {"Puntos_Vida": 22000},
}


class SimuladorEquipos:

    def __init__(self):
        pass

    def simular_mejor_soporte(
        self,
        stats_dps_base: dict,
        nombre_agente: str,
        rol_dps: str,
        elemento_dps: str,
        equipo_actual=None,
        enemigo_actual=None,
    ):
        if equipo_actual is None:
            equipo_actual = []

        candidatos    = self._obtener_candidatos(nombre_agente, rol_dps)
        resistencias  = PENALIZACIONES_ENEMIGOS.get(enemigo_actual, [])
        score_base    = self._calcular_score(stats_dps_base, rol_dps)
        ranking       = []

        if set(candidatos).issubset(set(equipo_actual)):
            return [{"soporte": "¡Sinergia Perfecta!", "mejoria": 0,
                     "detalle": "Ya tienes el mejor equipo posible. ¡A reventar!"}]

        for nombre_sup in candidatos:
            if nombre_sup in equipo_actual:
                continue

            elem_sup = ELEMENTOS_SOPORTES.get(nombre_sup, "Desconocido")
            if elem_sup in resistencias or elemento_dps in resistencias:
                continue

            clave      = nombre_sup.lower()
            fn_buff    = MAPA_SOPORTES_AGENTES.get(clave)
            if not fn_buff:
                continue

            stats_sim    = copy.deepcopy(stats_dps_base)
            mock_sup     = self._generar_mock_stats(nombre_sup)

            try:
                descripcion = fn_buff(
                    stats_sim,
                    stats=mock_sup,
                    mindscape=0,
                    datos_equipo={"roles": [rol_dps.lower()], "elementos": [elemento_dps.lower()],
                                  "nombres": [nombre_agente.lower()], "facciones": []},
                    elemento_dps=elemento_dps.lower(),
                )
            except Exception as e:
                descripcion = f"Buff aplicado ({e})"

            nuevo_score       = self._calcular_score(stats_sim, rol_dps)
            mejoria_pct       = ((nuevo_score - score_base) / score_base * 100) if score_base > 0 else 0

            ranking.append({
                "soporte": nombre_sup,
                "mejoria": mejoria_pct,
                "detalle": str(descripcion) if descripcion else "Buff aplicado",
            })

        ranking.sort(key=lambda x: x["mejoria"], reverse=True)

        if not ranking:
            return [{"soporte": "Alerta de Resistencia", "mejoria": 0,
                     "detalle": f"El enemigo {enemigo_actual} resiste las composiciones ideales."}]
        return ranking

    def _calcular_score(self, stats: dict, rol: str) -> float:
        atk      = stats.get("Ataque", 0.0)
        dmg_pct  = 1.0 + (stats.get("Daño_elemental", 0.0) + stats.get("Daño_Adicional", 0.0)) / 100.0
        pen      = 1.0 + stats.get("Tasa_de_Perforación", 0.0) / 100.0
        cr       = min(stats.get("Probabilidad_crítico", 0.0) / 100.0, 1.0)
        cd       = stats.get("Daño_crítico", 0.0) / 100.0
        crit_f   = 1.0 + cr * cd

        if rol in ("Anomalo", "Anomalía"):
            maestria     = stats.get("Maestría_Anomalía", 0.0)
            tasa_efectiva = max(100.0, stats.get("Tasa_de_Anomalía", 100.0)) / 100.0
            bono_acum    = 1.0 + stats.get("Bono_Acumulación", 0.0) / 100.0
            return atk * (1.0 + maestria / 100.0) * tasa_efectiva * bono_acum * dmg_pct * pen

        if rol == "Aturdidor":
            impacto = stats.get("Impacto", 100.0)
            impacto_f = 1.0 + max(0.0, impacto - 100.0) / 200.0
            return atk * crit_f * dmg_pct * pen * impacto_f

        if rol == "Ruptura":
            hp  = stats.get("Puntos_Vida", 0.0)
            return hp * crit_f * dmg_pct

        return atk * crit_f * dmg_pct * pen

    def _obtener_candidatos(self, nombre_agente: str, rol: str) -> list:
        lista = EQUIPOS_IDEALES.get(nombre_agente, [])
        if not lista:
            lista = CONFIG_SOPORTES_SUGERIDOS.get(rol, CONFIG_SOPORTES_SUGERIDOS["Atacante"])
        return lista

    def _generar_mock_stats(self, nombre_sup: str) -> dict:
        stats = copy.deepcopy(_MOCK_STATS_BASE)
        stats.update(_MOCK_OVERRIDES.get(nombre_sup.lower(), {}))
        return stats