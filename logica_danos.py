import logging
import math
from formulas_dano import cargar_formulas_dano

### HOLA

class LogicaDmg:
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.formulas_dano = cargar_formulas_dano()

    def _get_param(self, params, key, default=0.0):
        """Función segura para obtener parámetros numéricos del diccionario de la UI."""
        try:
            return float(params.get(key, default))
        except (ValueError, TypeError):
            self.logger.warning(f"No se pudo convertir el parámetro '{key}' a float. Usando valor por defecto: {default}.")
            return float(default)

    def _calcular_atk_combate(self, params):
        """
        Calcula el ATK inicial en combate.
        """
        initial_atk = self._get_param(params, "Ataque")

        return initial_atk

    def _calcular_base_dmg(self, params, scaling_stat):
        """
        Calcula el Daño Base de una habilidad.
        Fórmula: Skill MV * Scaling Stat + Flat MV
        """
        skill_mv = self._get_param(params, "Multiplicador_de_ataques") / 100.0
        flat_mv = self._get_param(params, "Flat_MV", 0)
        return skill_mv * scaling_stat + flat_mv

    def _calcular_dmg_mod(self, params):
        """
        Suma bonos de daño basándose en la jerarquía de la etiqueta del ataque.
        Jerarquía:
            - aftershock: Suma Base + Elemental + Aftershock
            - elemental: Suma Base + Elemental
            - normal: Suma Base (Daño Adicional Global)
        """
        val_etiqueta = params.get("Etiqueta_Dano", "normal")
        etiqueta = str(val_etiqueta).lower().strip()

        additional_dmg_bonus = self._get_param(params, "Daño_Adicional") / 100.0
        elemental_dmg_bonus = self._get_param(params, "Daño_elemental") / 100.0
        aftershock_dmg_bonus = self._get_param(params, "Daño_Aftershock") / 100.0
        modificador_total = 1.0 + additional_dmg_bonus

        if etiqueta in ["elemental", "aftershock"]:
            modificador_total += elemental_dmg_bonus
        
        if etiqueta == "aftershock":
            modificador_total += aftershock_dmg_bonus

        return modificador_total

    def _calcular_crit_mod(self, params):
        """
        Calcula el multiplicador de daño promedio por críticos.
        Fórmula: 1 + Prob. Crítico * Daño Crítico
        """
        crit_rate = min(self._get_param(params, "Probabilidad_crítico") / 100.0, 1.0)
        crit_dmg = self._get_param(params, "Daño_crítico") / 100.0

        crit_dmg_increase = self._get_param(params, "Aumento_Daño_Critico") / 100.0

        total_crit_dmg = crit_dmg + crit_dmg_increase

        return 1 + (crit_rate * total_crit_dmg)

    def _calcular_res_mod(self, params, elemento):
        
        elemento_norm = str(elemento).lower().replace('í', 'i').replace('é', 'e').strip()

        res_map = {
            "fuego": "Resistencia_Fuego", "electrico": "Resistencia_Electrico",
            "hielo": "Resistencia_Hielo", "fisico": "Resistencia_Físico",
            "etereo": "Resistencia_Etereo", "viento": "Resistencia_Viento"
        }

        red_map = {
            "fuego": "Red_Resistencia_Fuego", "electrico": "Red_Resistencia_Electrico",
            "hielo": "Red_Resistencia_Hielo", "fisico": "Red_Resistencia_Físico",
            "etereo": "Red_Resistencia_Etereo", "viento": "Red_Resistencia_Viento"
        }

        player_penres_map = {
            "fuego": "Pen_Res_Fuego", 
            "electrico": "Pen_Res_Electrico",
            "hielo": "Pen_Res_Hielo", 
            "fisico": "Pen_Res_Fisico",
            "etereo": "Pen_Res_Etereo",
            "viento": "Pen_Res_Viento"
        }

        attribute_res = self._get_param(params, res_map.get(elemento_norm, "Resistencia_Físico")) / 100.0
        all_type_res = self._get_param(params, "Resistencia_porcentual") / 100.0

        res_reduction_especifica = self._get_param(params, red_map.get(elemento_norm, "Red_Resistencia_Físico")) / 100.0
        res_reduction_global = self._get_param(params, "Red_Resistencia_Global", 0.0) / 100.0
        res_reduction = res_reduction_especifica + res_reduction_global

        key_pen = player_penres_map.get(elemento_norm, "Pen_Res_Fisico")
        res_pen_especifico = self._get_param(params, key_pen) / 100.0
        res_pen_global = self._get_param(params, "Pen_Res_Global", 0.0) / 100.0
        res_pen = res_pen_especifico + res_pen_global

        return 1 - (attribute_res + all_type_res - res_reduction - res_pen)

    def _calcular_def_mod(self, params):
        """
        Calcula el multiplicador de defensa del enemigo.
        Fórmula: CoefNivel / (CoefNivel + DEF Efectiva)
        """
        target_base_def = self._get_param(params, "Defensa_Base")
        def_reduction = self._get_param(params, "Reduccion_DEF_enemigo") / 100.0
        pen_ratio = self._get_param(params, "Tasa_de_Perforación") / 100.0
        flat_pen = self._get_param(params, "Perforación_Plana")
        def_ignored = self._get_param(params, "Ignorar_Defensa") / 100
        def_ignored_aftershock = self._get_param(params, "Ignorar_Defensa_Aftershock") / 100
        buff_def = self._get_param(params, "Buff_Defensa")
        miasma = self._get_param(params, "Miasma", 1.0)

        level_coefficient = 794

        target_def = target_base_def * (1 + buff_def - def_reduction - def_ignored - def_ignored_aftershock) * miasma
        effective_def = max(0, target_def * (1 - pen_ratio) - flat_pen)

        return level_coefficient / (level_coefficient + effective_def)

    def _calcular_anomaly_mod(self, params):
        """
        Calcula el bono de daño específico para Anomalías.
        """
        anomaly_dmg_bonus = self._get_param(params, "Bono_Daño_Anomalia", 0) / 100.0
        return 1 + anomaly_dmg_bonus

    def _calcular_ap_bonus_mod(self, params):
        """
        Calcula el bono de daño por Anomaly Proficiency (Maestría de Anomalía).
        Fórmula: AP / 100
        """
        anomaly_proficiency = self._get_param(params, "Maestría_Anomalía")
        return anomaly_proficiency / 100.0

    def _calcular_buff_level_mod(self, params):
        """
        Calcula el bono de daño por el nivel del atacante.
        Fórmula: 1 + ((Nivel Atacante - 1) / 59)
        """
        attacker_level = self._get_param(params, "Nivel", 1)
        return 1 + ((attacker_level - 1) / 59.0)
    
    def _calcular_stun_mod(self, params):
        """
        Calcula el multiplicador de daño por aturdimiento.
        - No Aturdido (Normal): 1.0 + Stun_DMG_Multiplier + Unstun_DMG_Multiplier
        - Aturdido (Stun_Boss): 1.5 + Stun_DMG_Multiplier + Unstun_DMG_Multiplier
        """
        estado = params.get("Estado_Enemigo", "Normal")
        
        stun_bonus = self._get_param(params, "Stun_DMG_Multiplier", 0.0) / 100.0
        unstun_bonus = self._get_param(params, "Unstun_DMG_Multiplier", 0.0) / 100.0

        if estado == "Stun_Boss":
            base_mult = 1.50
        else:
            base_mult = 1.00

        return base_mult + stun_bonus + unstun_bonus

    def calcular_dano_general(self, params, elemento, atk_combate):
        """
        Calcula el daño normal, no-Anomalía.
        Fórmula: BaseDMG * DMG%Mod * CritMod * RESMod * DEFMod * ...
        """
        base_dmg = self._calcular_base_dmg(params, atk_combate)
        dmg_mod = self._calcular_dmg_mod(params)
        crit_mod = self._calcular_crit_mod(params)
        res_mod = self._calcular_res_mod(params, elemento)
        def_mod = self._calcular_def_mod(params)
        stun_mod = self._calcular_stun_mod(params)
        dmg_taken_mod = 1 + self._get_param(params, "DMG_Taken", 0) / 100.0

        return base_dmg * dmg_mod * crit_mod * res_mod * def_mod * stun_mod * dmg_taken_mod

    def calcular_dano_sheer(self, params, elemento, atk_combate):
        """
        Calcula el daño Sheer. Es idéntico al general pero IGNORA la defensa.
        Su daño base escala con Sheer Force (30% del ATK).
        """
        sheer_force = self._get_param(params, "Sheer_force")
        
        base_dmg = self._calcular_base_dmg(params, sheer_force) 
        dmg_mod = self._calcular_dmg_mod(params) 
        crit_mod = self._calcular_crit_mod(params)
        res_mod = self._calcular_res_mod(params, elemento)
        def_mod = self._calcular_def_mod(params)

        def_sheer = def_mod/def_mod

        stun_mod = self._calcular_stun_mod(params)
        dmg_taken_mod = 1 + self._get_param(params, "DMG_Taken", 0) / 100.0

        return base_dmg * dmg_mod * crit_mod * res_mod * stun_mod * dmg_taken_mod * def_sheer
    
    def _calcular_assaults_jane(self, params, elemento):
        """
        NUEVO: Calcula el multiplicador de crítico EXCLUSIVO para Anomalías.
        Actualmente solo aplica a 'Assault' (Físico) por Jane Doe .
        """
        if elemento not in ["fisico", "físico"]:
            return 1.0

        assault_rate = self._get_param(params, "Assault_Crit_Rate", 0.0)

        if assault_rate <= 0:
            return 1.0

        assault_dmg = self._get_param(params, "Assault_Crit_DMG", 50.0)

        rate_dec = min(assault_rate / 100.0, 1.0)
        dmg_dec = assault_dmg / 100.0

        return 1 + (rate_dec * dmg_dec)

    def calcular_dano_anomalia(self, params, elemento, atk_combate):
        """
        Calcula el daño de una Anomalía elemental.
        """
        base_dmg_multipliers = {
            "fuego": 0.50,    
            "electrico": 1.25, 
            "hielo": 5.00,    
            "físico": 7.13,   
            "etereo": 0.625   
        }

        elemento_key = elemento.lower().replace("í", "i") if elemento else ""
        if "fisico" in elemento_key: elemento_key = "físico"
        
        base_dmg = atk_combate * base_dmg_multipliers.get(elemento_key, 0.0)
        
        if base_dmg == 0: return 0 

        dmg_mod = self._calcular_dmg_mod(params)
        res_mod = self._calcular_res_mod(params, elemento)
        def_mod = self._calcular_def_mod(params)
        anomaly_mod = self._calcular_anomaly_mod(params)
        ap_bonus = self._calcular_ap_bonus_mod(params)
        buff_level_mod = self._calcular_buff_level_mod(params)


        crit_anomalia_mod = self._calcular_assaults_jane(params, elemento)

        return base_dmg * dmg_mod * res_mod * def_mod * anomaly_mod * ap_bonus * buff_level_mod * crit_anomalia_mod

    def calcular_dano_disorder(self, params, elemento, atk_combate):
        """
        Calcula el daño de Disorder. Su daño base depende del tiempo 't' restante.
        Como 't' no está en la UI, se asume un valor promedio (ej. t=5s).
        """
        t = 3.0

        elemento_key = elemento.lower().replace("í", "i") if elemento else ""
        if "fisico" in elemento_key: elemento_key = "físico"

        disorder_multipliers = {
            "fuego": (4.50 + (math.floor(t / 0.5) * 0.50)), 
            "electrico": (4.50 + (t * 1.25)),                 
            "hielo": (4.50 + (t * 0.075)),                    
            "físico": (4.50 + (t * 0.075)),                   
            "etereo": (4.50 + (math.floor(t / 0.5) * 0.625)) 
        }
        
        base_mult = disorder_multipliers.get(elemento_key, 0.0)
        extra_mult = self._get_param(params, "Disorder_Extra_Mult", 0.0) / 100.0
        final_mult = base_mult + extra_mult
        base_dmg = atk_combate * final_mult
        if base_dmg == 0: return 0

        tasa_por_segundo = self._get_param(params, "Bono_Disorder_Seg", 0.0)
        bono_pct = min(180.0, tasa_por_segundo * t)
        disorder_mod = 1 + (bono_pct / 100.0)

        dmg_mod = self._calcular_dmg_mod(params)
        res_mod = self._calcular_res_mod(params, elemento)
        def_mod = self._calcular_def_mod(params)
        anomaly_mod = self._calcular_anomaly_mod(params)
        ap_bonus = self._calcular_ap_bonus_mod(params)
        buff_level_mod = self._calcular_buff_level_mod(params)

        return base_dmg * dmg_mod * res_mod * def_mod * anomaly_mod * ap_bonus * buff_level_mod * disorder_mod

    def calcular_dano_vortex(self, params, elemento, atk_combate):
        """
        Calcula Vortex, el disorder especial asociado a Windswept.

        Vortex usa el atributo de la anomalía removida, no viento. Si no se
        indica Elemento_Vortex y el elemento actual es viento, no se dispara.
        """
        elemento_vortex = (
            params.get("Elemento_Vortex")
            or params.get("Vortex_Elemento_Removido")
            or ""
        )
        elemento_key = str(elemento_vortex).lower().replace("í", "i").replace("é", "e").strip()
        if not elemento_key or elemento_key in ["auto", "automatico", "automático", "viento", "wind"]:
            return 0
        if "fisico" in elemento_key:
            elemento_key = "físico"
        elif "electrico" in elemento_key or "elec" in elemento_key:
            elemento_key = "electrico"
        elif "eter" in elemento_key or "ether" in elemento_key:
            elemento_key = "etereo"

        t = self._get_param(params, "Vortex_Tiempo", self._get_param(params, "Disorder_Tiempo", 3.0))
        additional_mv = self._get_param(params, "Vortex_Additional_MV", 0.0) / 100.0

        formula = self.formulas_dano.get("vortex", {}).get(elemento_key, {})
        base_pct = float(formula.get("base_pct", 0.0))
        tick_pct = float(formula.get("tick_pct", 0.0))
        tick_seg = max(0.001, float(formula.get("tick_seg", 1.0)))
        if formula.get("usar_intervalos", False):
            tiempo_mult = math.floor(t / tick_seg)
        else:
            tiempo_mult = t / tick_seg

        base_mult = ((base_pct + (tiempo_mult * tick_pct)) / 100.0) + additional_mv
        if base_mult <= 0:
            return 0

        base_dmg = atk_combate * base_mult
        dmg_mod = 1 + (
            self._get_param(params, "Daño_elemental", 0.0)
            + self._get_param(params, "Vortex_DMG", 0.0)
        ) / 100.0
        buff_mod = 1 + (self._get_param(params, "Vortex_Buff", 0.0) / 100.0)
        res_mod = self._calcular_res_mod(params, elemento_key)
        def_mod = self._calcular_def_mod(params)
        stun_mod = self._calcular_stun_mod(params)
        dmg_taken_mod = 1 + self._get_param(params, "DMG_Taken", 0) / 100.0
        ap_bonus = self._calcular_ap_bonus_mod(params)
        buff_level_mod = self._calcular_buff_level_mod(params)

        return base_dmg * dmg_mod * buff_mod * res_mod * def_mod * stun_mod * dmg_taken_mod * ap_bonus * buff_level_mod

    def calcular_dano_abloom(self, params, elemento, dano_anomalia):
        bono_abloom_soporte = self._get_param(params, "Bono_Abloom_Final", 0.0)
        
        elementos_soportes = params.get("Elementos_Soportes", [])
        elemento_dps = str(params.get("Elemento_Agente", elemento)).lower()
        
        elemento_elegido = str(params.get("Elemento_Abloom", "Automático")).lower()
        bono_abloom = self._get_param(params, "Abloom_dmg") / 100.0
        
        mejor_bono_core = 0.0
        elementos_a_evaluar = []
        
        if "auto" in elemento_elegido:
            elementos_a_evaluar.append(elemento_dps)
            elementos_a_evaluar.extend(elementos_soportes)
        else:
            elementos_a_evaluar.append(elemento_elegido)

            
        for elem in elementos_a_evaluar:
            if not elem: continue
            
            elemento_key = str(elem).lower().replace("í", "i").replace("é", "e")
            if "fisico" in elemento_key: elemento_key = "phys"
            elif "fuego" in elemento_key: elemento_key = "fire"
            elif "viento" in elemento_key: elemento_key = "wind"
            elif "hielo" in elemento_key: elemento_key = "ice"
            elif "electrico" in elemento_key or "elec" in elemento_key: elemento_key = "elec"
            elif "etereo" in elemento_key or "eter" in elemento_key: elemento_key = "ether"

            clave_core_buscada = f"Abloom_{elemento_key.capitalize()}_Add"
            bono_core_parcial = self._get_param(params, clave_core_buscada, 0.0)
            
            if bono_core_parcial > mejor_bono_core:
                mejor_bono_core = bono_core_parcial
                
        total_abloom_pcta = bono_abloom_soporte + mejor_bono_core
        total_abloom_pct = total_abloom_pcta * (1 + bono_abloom)
        return dano_anomalia * (total_abloom_pct / 100.0)

    def calcular_todos_danos(self, params, elemento):
        """Función principal que se comunica con la UI."""
        try:
            atk_combate = self._calcular_atk_combate(params)
            dano_general = self.calcular_dano_general(params, elemento, atk_combate)
            dano_sheer = self.calcular_dano_sheer(params, elemento, atk_combate)
            
            dano_anomalia = self.calcular_dano_anomalia(params, elemento, atk_combate)
            dano_abloom = self.calcular_dano_abloom(params, elemento, dano_anomalia)
            
            dano_disorder = self.calcular_dano_disorder(params, elemento, atk_combate)
            dano_vortex = self.calcular_dano_vortex(params, elemento, atk_combate)
            
            dmg_mod_val = self._calcular_dmg_mod(params)
            crit_mod_val = self._calcular_crit_mod(params)
            res_mod_val = self._calcular_res_mod(params, elemento)
            def_mod_val = self._calcular_def_mod(params)
            stun_mod_val = self._calcular_stun_mod(params)
            anomaly_mod_val = self._calcular_anomaly_mod(params)
            ap_bonus_val = self._calcular_ap_bonus_mod(params)

            stats_finales = {
                "Ataque en combate": atk_combate,
                "Bono Aftershock": self._get_param(params, "Daño_Aftershock"),
                "Bono de DMG% total": f"x{dmg_mod_val:.4f}",
                "Probabilidad final": min(self._get_param(params, "Probabilidad_crítico")/100, 1.0),
                "Daño Crítico final": (self._get_param(params, "Daño_crítico") + self._get_param(params, "Aumento_Daño_Critico"))/100,
                "Modificador Crítico promedio": f"x{crit_mod_val:.3f}",
                "Modificador de defensa": f"{ (1 - def_mod_val) * 100:.2f}%",
                "Reducción de resistencia": f"{ (1 - res_mod_val) * 100:.2f}%",
                "Multiplicador de Stun": f"x{stun_mod_val:.2f}",
                "Bono de Tasa": f"x{ap_bonus_val:.2f}",
                "Bono de Anomalía": f"x{anomaly_mod_val:.2f}",
                "Daño Inflingido": 1 + (self._get_param(params, "DMG_Taken", 0) / 100.0),
                "Daño General": dano_general,
                "Daño Sheer": dano_sheer,
                "Daño de Anomalía": dano_anomalia,
                "Daño de Abloom": dano_abloom,
                "Daño por Disorder": dano_disorder,
                "Daño por Vortex": dano_vortex
            }

            return dano_general, dano_sheer, dano_anomalia, dano_disorder, dano_abloom, dano_vortex, stats_finales

        except Exception as e:
            self.logger.error(f"Error catastrófico en el cálculo de daños: {e}", exc_info=True)
            return 0, 0, 0, 0, 0, 0, {"Error": str(e)}
        
    def Anomaly_build_up(self, params, elemento):
            """
            Calcula cuánta anomalía se aplica por golpe.
            Basado en: Base * (Maestría/100) * (1 + %Bonos) * (1 - Resistencia)
            """
            
            base_build_up = 100 

            maestria_stat = self._get_param(params, "Tasa_de_Anomalía")
            am_bonus_multiplier = maestria_stat / 100.0

            bono_acumulacion_pct = self._get_param(params, "Bono_Acumulación")
            buildup_mod = 1 + (bono_acumulacion_pct / 100.0)

            target_res = params.get("Resistencia_Anomalía_Enemigo", 0.0)
            res_reduction = params.get("Reducción_Resistencia_Anomalía", 0.0)
            
            res_final_pct = max(0.0, target_res - res_reduction) 
            res_mod = 1.0 - (res_final_pct / 100.0)

            total_buildup = base_build_up * am_bonus_multiplier * buildup_mod * res_mod
            
            return total_buildup
