"""
Módulo para analizar y priorizar mejoras de discos de personajes.
Calcula calificaciones y determina qué agentes necesitan mejoras con más urgencia.
"""

from logica_recomendaciones import CONFIG_ROLES, EXCEPCIONES_AGENTES, evaluar_calidad_global, calificacion_a_tier
from simulador_equipos import SimuladorEquipos
from traductor import traductor_global as i18n
from substats_config import calcular_rolls_substat

MAPEO_SETS = {
    31800: "Jazz caótico",32600: "Metal colmilludo",32400: "Metal eléctrico",
    32300: "Metal caótico",32200: "Metal infernal",32500: "Metal Polar",32700: "Balada de la rama y la espada",
    33100: "Fábula Yunkui",31400: "Punk Hormonal",31000: "Tecno Pícido",32800: "Voz Astral",
    31600: "Jazz Oscilante",32900: "Armonía Umbría",31100: "Tecno Tetraodóntido",
    33300: "Floración del alba",33200: "Monarca del Pináculo",33400: "Nana a la Luz Cenicienta",
    33000: "Melodía de Phaeton",31900: "Proto Punk",31200: "Disco sacudestrellas",
    33600: "Aria Radiante",33500: "Balada de Aguas Blancas",31300: "Blues Libre",31500: "Rock espiritual",
    33700: "Conejo en el país de las maravillas", 33800: "Diario de una prisionera"
}

MAPEO_STATS_MAIN = {
    "ATK": "Ataque",
    "HP": "Puntos_Vida",
    "DEF": "Defensa",
    "CRIT Rate": "Probabilidad_crítico",
    "CRIT DMG": "Daño_crítico",
    "Anomaly Proficiency": "Maestría_Anomalía",
    "PEN Ratio": "Tasa_de_Perforación",
    "Energy Regen": "Recuperación_energía",
    "Impact": "Impacto",
    "Anomaly Buildup Rate": "Tasa_de_Anomalía",
    "Physical DMG": "Daño_elemental",
    "Fire DMG": "Daño_elemental",
    "Ice DMG": "Daño_elemental",
    "Electric DMG": "Daño_elemental",
    "Ether DMG": "Daño_elemental",
}

MAPEO_STATS_SUB = {
    "ATK": "Ataque_porcentual",
    "Flat ATK": "Ataque_plano",
    "HP": "Puntos_Vida_porcentual",
    "Flat HP": "Puntos_Vida_plano",
    "DEF": "Defensa_porcentual",
    "Flat DEF": "Defensa_plano",
    "CRIT Rate": "Probabilidad_crítico_porcentual",
    "CRIT DMG": "Daño_crítico_porcentual",
    "Anomaly Proficiency": "Maestría_Anomalía_plano",
    "PEN": "Perforación_Plana_plano",
    "PEN Ratio": "Tasa_de_Perforación_porcentual",
    "Energy Regen": "Recuperación_energía_porcentual",
}

class AnalizadorPrioridades:
    """Analiza personajes y determina prioridades de mejora de discos."""
    
    def __init__(self, agentes_data=None):
        """
        Inicializa el analizador.
        
        Args:
            agentes_data: Lista de datos de agentes del juego (nombre, tipo, elemento, etc.)
        """
        self.agentes_data = agentes_data or []
        self.simulador = SimuladorEquipos()
        
    def analizar_personajes_uid(self, personajes_uid):
        """
        Analiza todos los personajes obtenidos del UID.
        
        Args:
            personajes_uid: Lista de personajes obtenidos de la API
            
        Returns:
            Lista de análisis ordenados por prioridad (peor a mejor)
        """
        analisis = []
        
        for pj in personajes_uid:
            resultado = self._analizar_personaje(pj)
            if resultado:
                analisis.append(resultado)
        
        analisis.sort(key=lambda x: x['score_global'])
        
        return analisis
    
    def _analizar_personaje(self, personaje):
        """Analiza un personaje individual y calcula su prioridad de mejora."""
        nombre = personaje.get('name', 'Desconocido')
        
        datos_agente = self._obtener_datos_agente(nombre)
        if not datos_agente:
            return None
        
        rol = datos_agente.get('Tipo', 'Atacante')
        elemento = personaje.get('element', 'Físico')
        
        discos = personaje.get('discs', [])
        analisis_discos = self._analizar_discos(discos, nombre, rol)
        sets_equipados = self._obtener_sets_equipados(discos)
        
        from logica_recomendaciones import evaluar_calidad_global, CONFIG_ROLES, EXCEPCIONES_AGENTES
        
        rolls_totales = self._contar_rolls_totales(discos)
        
        resumen_global = evaluar_calidad_global(
            nombre_agente=nombre,
            rol_agente=rol,
            rolls_actuales=rolls_totales,
            stats_finales={},
            eficiencia_wengine_actual=100.0,
            excepciones=EXCEPCIONES_AGENTES,
            config_roles=CONFIG_ROLES
        )
        
        score_promedio = resumen_global.get("calidad_pct", 0)
        
        calificaciones = {slot: info['calificacion'] for slot, info in analisis_discos.items() if info}
        prioridad = self._calcular_prioridad(score_promedio, calificaciones)
        
        recomendaciones = self._generar_recomendaciones(
            nombre, rol, elemento, analisis_discos, sets_equipados
        )
        
        return {
            'nombre': nombre,
            'rol': rol,
            'elemento': elemento,
            'nivel': personaje.get('level', 1),
            'mindscape': personaje.get('mindscape', 0),
            'weapon': personaje.get('weapon', {}).get('name', 'Sin arma'),
            'calificaciones': calificaciones,
            'score_global': score_promedio,
            'prioridad': prioridad,
            'sets_equipados': sets_equipados,
            'analisis_discos': analisis_discos,
            'recomendaciones': recomendaciones
        }
    
    def _obtener_datos_agente(self, nombre):
        """Obtiene los datos del agente desde la base de datos del juego."""
        for agente in self.agentes_data:
            if agente.get('Nombre') == nombre:
                return agente
        return None
    
    def _analizar_discos(self, discos, nombre_agente, rol):
        """
        Analiza cada disco y determina su calidad.
        
        Returns:
            Dict con análisis por slot (1, 2, 3, 4, 5, 6)
        """
        config = self._obtener_config_agente(nombre_agente, rol)
        
        analisis = {}
        
        for disco in discos:
            slot = disco.get('slot', 0)
            if slot < 1 or slot > 6:
                continue
                
            set_id = disco.get('set_id', 0)
            set_nombre = MAPEO_SETS.get(set_id, "Desconocido")
            main_stat = disco.get('main_stat', {})
            main_nombre_raw = main_stat.get('name', '')
            main_nombre = MAPEO_STATS_MAIN.get(main_nombre_raw, main_nombre_raw)
            main_ideal = self._es_main_ideal(main_nombre, slot, config)
            substats = disco.get('sub_stats', [])
            analisis_subs = self._analizar_substats(substats, config)
            tier_disco = self._obtener_tier_disco(substats, main_nombre_raw, slot, config)
            
            analisis[slot] = {
                'set': set_nombre,
                'set_id': set_id,
                'main_stat': main_nombre,
                'main_ideal': main_ideal,
                'nivel': disco.get('level', 0),
                'substats': analisis_subs,
                'num_substats': len(substats),
                'calificacion': tier_disco[0],
                'color_tier': tier_disco[1],
                'disco_completo': disco
            }
        
        return analisis
    
    def _obtener_config_agente(self, nombre, rol):
        """Obtiene la configuración de stats ideal para el agente."""
        if nombre in EXCEPCIONES_AGENTES:
            return EXCEPCIONES_AGENTES[nombre]
        
        return CONFIG_ROLES.get(rol, CONFIG_ROLES["Atacante"])
    
    def _es_main_ideal(self, main_stat, slot, config):
        """Verifica si el main stat es ideal para el slot."""
        slot_key = f"main_{slot}"
        
        if slot_key in config:
            stats_ideales = config[slot_key].get('general', []) + config[slot_key].get('particular', [])
            return main_stat in stats_ideales
        
        return False
    
    def _analizar_substats(self, substats, config):
        """Analiza las substats y las clasifica como ideal/decente/basura."""
        resultado = {
            'ideal': [],
            'decente': [],
            'basura': []
        }
        
        subs_config = config.get('subs', {})
        ideales = subs_config.get('ideal', [])
        decentes = subs_config.get('decente', [])
        basuras = subs_config.get('basura', [])
        
        for sub in substats:
            nombre_raw = sub.get('name', '')
            nombre = MAPEO_STATS_SUB.get(nombre_raw, nombre_raw)
            valor = sub.get('value', '0')
            
            if '%' in valor:
                nombre_comparar = f"{nombre}"
            else:
                nombre_comparar = f"{nombre}"
            
            if any(ideal in nombre_comparar for ideal in ideales):
                resultado['ideal'].append({'nombre': nombre_raw, 'valor': valor})
            elif any(decente in nombre_comparar for decente in decentes):
                resultado['decente'].append({'nombre': nombre_raw, 'valor': valor})
            else:
                resultado['basura'].append({'nombre': nombre_raw, 'valor': valor})
        
        return resultado
    
    def _obtener_tier_disco(self, substats, nombre_main_stat, slot_num, config_rol):
        """Calcula el Tier exacto del disco usando el mismo algoritmo que la interfaz visual."""
        stats_ideales = [s.lower() for s in config_rol.get("subs", {}).get("ideal", [])]
        stats_decentes = [s.lower() for s in config_rol.get("subs", {}).get("decente", [])]
        
        score_total = 0
        clave_main = self._limpiar_nombre_stat(nombre_main_stat, "0%")
        
        if slot_num in [4, 5, 6]:
            main_dict = config_rol.get(f"main_{slot_num}", {"general": [], "particular": []})
            main_ideales = [s.lower() for s in main_dict.get("general", [])]
            main_particulares = [s.lower() for s in main_dict.get("particular", [])]
            
            if any(m in clave_main.lower() for m in main_ideales):
                score_total += 1.7
            elif any(m in clave_main.lower() for m in main_particulares):
                score_total += 1.5
        else:
            score_total += 1.0

        cantidad_ideales = max(1, len(stats_ideales))
        mult_ideal = 1.0   
        mult_decente = 0.75
        
        if cantidad_ideales == 1:
            mult_ideal = 1.20
            mult_decente = 0.95 
        elif cantidad_ideales == 2:
            mult_ideal = 1.02
            mult_decente = 0.8

        for sub in substats:
            raw_name = sub.get('name', '')
            raw_val = sub.get('value', '0')
            clave_interna = self._limpiar_nombre_stat(raw_name, raw_val).lower()
            rolls = self._calcular_rolls_real(raw_name, raw_val)

            if clave_interna in stats_ideales:
                score_total += (rolls * mult_ideal)
            elif clave_interna in stats_decentes:
                score_total += (rolls * mult_decente)
        
        return calificacion_a_tier(score_total * 10)
    
    def _convertir_calificacion_a_numero(self, calificacion):
        """Convierte calificación a número para ordenamiento."""
        valores = {'S': 5, 'A': 4, 'B': 3, 'C': 2, 'D': 1, 'F': 0}
        return valores.get(calificacion, 0)
    
    def _calcular_prioridad(self, score_promedio, calificaciones):
        """Determina la prioridad de mejora basada en el % global y tiers."""
        discos_malos = sum(1 for cal in calificaciones.values() if cal in ['MID', 'AVERAGE'])
        discos_regulares = sum(1 for cal in calificaciones.values() if cal in ['DECENT', 'SOLID'])
        
        if score_promedio < 40 or discos_malos >= 2:
            return "URGENTE"
        elif score_promedio < 65 or discos_malos >= 1:
            return "ALTA"
        elif score_promedio < 80 or discos_regulares >= 2:
            return "MEDIA"
        else:
            return "BAJA"
    
    def _obtener_sets_equipados(self, discos):
        """Determina qué sets están equipados y si hay bonos activos."""
        conteo_sets = {}
        
        for disco in discos:
            set_id = disco.get('set_id', 0)
            set_nombre = MAPEO_SETS.get(set_id, "Desconocido")
            conteo_sets[set_nombre] = conteo_sets.get(set_nombre, 0) + 1
        
        sets_activos = {}
        for set_nombre, cantidad in conteo_sets.items():
            if cantidad >= 4:
                sets_activos[set_nombre] = "4pc"
            elif cantidad >= 2:
                sets_activos[set_nombre] = "2pc"
        
        return sets_activos
    
    def _generar_recomendaciones(self, nombre, rol, elemento, analisis_discos, sets_equipados):
        """Genera recomendaciones específicas de mejora basadas en logica_recomendaciones."""
        config = self._obtener_config_agente(nombre, rol)
        recomendaciones = []
        sets_ideales = self._obtener_sets_ideales(nombre, rol, config)
        
        tiene_set_ideal = any(set_ideal in sets_equipados for set_ideal in sets_ideales)
        
        if sets_ideales and not tiene_set_ideal:
            recomendaciones.append({
                'tipo': 'set',
                'mensaje': i18n.t("ui.mejoras_discos.recom_sets_ideales", default=f"Sets ideales: {', '.join(sets_ideales)}", sets=', '.join(sets_ideales)),
                'prioridad': 'alta'
            })
        
        for slot, info in analisis_discos.items():
            if not info:
                continue
                
            if info['calificacion'] in ['MID', 'AVERAGE']:
                main_ideales = self._obtener_main_ideales(slot, config)
                main_txt = main_ideales[0] if main_ideales else 'ideal'
                recomendaciones.append({
                    'tipo': 'disco',
                    'slot': slot,
                    'mensaje': i18n.t("ui.mejoras_discos.recom_farmear", default=f"Disco {slot} ({info['calificacion']}): Farmear nuevo con main {main_txt}", slot=slot, tier=info['calificacion'], main=main_txt),
                    'prioridad': 'urgente'
                })
            elif info['calificacion'] in ['DECENT', 'SOLID']:
                if not info['main_ideal']:
                    main_ideales = self._obtener_main_ideales(slot, config)
                    main_txt = main_ideales[0] if main_ideales else 'ideal'
                    recomendaciones.append({
                        'tipo': 'disco',
                        'slot': slot,
                        'mensaje': i18n.t("ui.mejoras_discos.recom_buscar_main", default=f"Disco {slot} ({info['calificacion']}): Buscar main {main_txt}", slot=slot, tier=info['calificacion'], main=main_txt),
                        'prioridad': 'media'
                    })
        
        return recomendaciones
    
    def _limpiar_nombre_stat(self, nombre_raw, valor_str):
        """Normaliza los nombres de las stats provenientes de la API."""
        n = str(nombre_raw).lower().strip()
        v = str(valor_str)
        es_pct = "%" in v or "percent" in n or "tasa" in n or "prob" in n or "bono" in n or "ratio" in n
        
        if "ataque" in n or "atk" in n: return "Ataque_porcentual" if es_pct else "Ataque_plano"
        if "vida" in n or "hp" in n or "pv" in n: return "Puntos_Vida_porcentual" if es_pct else "Puntos_Vida_plano"
        if "defensa" in n or "def" in n: return "Defensa_porcentual" if es_pct else "Defensa_plano"
        
        if "crit" in n or "crít" in n:
            if "rate" in n or "prob" in n: return "Probabilidad_crítico_porcentual"
            if "dmg" in n or "daño" in n or "dano" in n: return "Daño_crítico_porcentual"
        
        if "pen" in n or "perf" in n: return "Tasa_de_Perforación" if es_pct else "Perforación_Plana_plano"
        if "anomal" in n and ("prof" in n or "maestr" in n): return "Maestría_Anomalía_plano"
        if "anomal" in n and ("tasa" in n or "mastery" in n): return "Tasa_de_Anomalía"
        if "recup" in n or "energy" in n: return "Recuperación_energía_porcentual"
        if "impact" in n: return "Impacto"
        
        elementos = ["elemental", "físico", "fisico", "fuego", "hielo", "eléctrico", "electrico", "etéreo", "etereo", "physical", "fire", "ice", "ether", "electric", "dmg bonus", "bono de daño"]
        if any(x in n for x in elementos): return "Daño_elemental"
        
        return "Desconocido"

    def _calcular_rolls_real(self, nombre_stat, valor_texto):
        """Calcula cuántas tiradas (rolls) tiene una substat."""
        try:
            clave = self._limpiar_nombre_stat(nombre_stat, valor_texto)
            return calcular_rolls_substat(clave, valor_texto)
        except: return 1

    def _contar_rolls_totales(self, discos):
        """Cuenta el total de rolls de todas las substats para la evaluación global."""
        rolls_totales = {}
        for disco in discos:
            for sub in disco.get('sub_stats', []):
                nombre = sub.get('name', '')
                valor = sub.get('value', '0')
                clave_limpia = self._limpiar_nombre_stat(nombre, valor)
                rolls = self._calcular_rolls_real(nombre, valor)
                rolls_totales[clave_limpia] = rolls_totales.get(clave_limpia, 0) + rolls
        return rolls_totales

    def _obtener_sets_ideales(self, nombre, rol, config):
        """Obtiene los sets ideales para el agente, extrayendo textos limpios de las tuplas si es necesario."""
        from logica_recomendaciones import CONFIG_SETS_ROLES
        
        def extraer_nombre(item): 
            return item[0] if isinstance(item, tuple) else item

        sets_brutos = []
        
        if 'sets' in config:
            sets_config = config['sets']
            if '4pc' in sets_config:
                sets_brutos = sets_config.get('4pc', [])
            elif 'ideal' in sets_config:
                sets_brutos = sets_config.get('ideal', [])
        else:
            sets_rol = CONFIG_SETS_ROLES.get(rol, {})
            sets_brutos = sets_rol.get('ideal', [])
            
        return [extraer_nombre(s) for s in sets_brutos][:3]
    
    def _obtener_main_ideales(self, slot, config):
        """Obtiene las main stats ideales (generales y particulares) para un slot."""
        slot_key = f"main_{slot}"
        ideales = []
        if slot_key in config:
            ideales.extend(config[slot_key].get('general', []))
            ideales.extend(config[slot_key].get('particular', []))

        return [stat.replace("_", " ") for stat in ideales]
