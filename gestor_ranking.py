import json
import os
import logging
import fcntl  
import threading
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from logica_recomendaciones import (
    AnalistaBuild, 
    CONFIG_ROLES, 
    EXCEPCIONES_AGENTES,
    evaluar_calidad_global,
    normalizar_clave_substat,
    calificacion_a_tier
)
from substats_config import calcular_rolls_substat

logger = logging.getLogger(__name__)

class GestorRanking:
    """
    Gestor del ranking global de personajes.
    Calcula y guarda las calificaciones imitando EXACTAMENTE la lógica de la Build Card.
    """
    
    def __init__(self, ruta_guardados: str):
        self.ruta_guardados = ruta_guardados
        self._lock = threading.Lock()
        self._ranking_cache = None
        self.ruta_uids = os.path.join(ruta_guardados, 'uids')
        self.ruta_ranking = os.path.join(ruta_guardados, 'ranking_global.json')
        self.analista = AnalistaBuild()
        os.makedirs(self.ruta_uids, exist_ok=True)
        os.makedirs(ruta_guardados, exist_ok=True)
    
    # ── UIDs guardadas en disco (compartidas entre sesiones) ──────────────────
    def _ruta_uids_json(self) -> str:
        return os.path.join(self.ruta_uids, 'uids.json')

    def cargar_uids_guardados(self) -> Dict:
        ruta = self._ruta_uids_json()
        if os.path.exists(ruta):
            try:
                with open(ruta, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error cargando UIDs: {e}")
        return {}

    def guardar_uid_local(self, apodo: str, uid: str):
        uids = self.cargar_uids_guardados()
        uids[apodo] = uid
        with open(self._ruta_uids_json(), 'w', encoding='utf-8') as f:
            json.dump(uids, f, indent=2, ensure_ascii=False)

    def eliminar_uid_local(self, apodo: str):
        uids = self.cargar_uids_guardados()
        if apodo in uids:
            del uids[apodo]
            with open(self._ruta_uids_json(), 'w', encoding='utf-8') as f:
                json.dump(uids, f, indent=2, ensure_ascii=False)
    
    def _buscar_excepcion_agente(self, nombre_agente: str) -> dict:
        """Busca en EXCEPCIONES_AGENTES con match exacto primero, luego fuzzy."""
        if nombre_agente in EXCEPCIONES_AGENTES:
            return EXCEPCIONES_AGENTES[nombre_agente]
        nombre_lower = nombre_agente.strip().lower()
        for clave in EXCEPCIONES_AGENTES:
            if clave.strip().lower() == nombre_lower:
                return EXCEPCIONES_AGENTES[clave]
        # Match normalizado (sin guiones/espacios extra)
        def _norm(s): return s.lower().replace("-", "").replace("  ", " ").strip()
        nombre_norm = _norm(nombre_agente)
        mejor_match = None
        mejor_len = 0
        for clave in EXCEPCIONES_AGENTES:
            clave_norm = _norm(clave)
            if clave_norm == nombre_norm:
                return EXCEPCIONES_AGENTES[clave]
            if clave_norm in nombre_norm or nombre_norm in clave_norm:
                if len(clave_norm) > mejor_len:
                    mejor_len = len(clave_norm)
                    mejor_match = clave
        return EXCEPCIONES_AGENTES[mejor_match] if mejor_match else {}

    def calcular_eficiencia_wengine(self, nombre_agente: str, wengine_nombre: str, refinamiento: int = 1) -> float:
        if not wengine_nombre or wengine_nombre == "Ninguno": return 0.0
        try: ref = int(refinamiento)
        except: ref = 1
        
        config_agente = self._buscar_excepcion_agente(nombre_agente)
        wengines_config = config_agente.get('wengines', {})
        if not wengines_config: return 0.6 * (1 + (ref - 1) * 0.1)
            
        def extraer_datos_seguros(item, valor_default):
            if isinstance(item, (tuple, list)):
                nombre = str(item[0])
                try: eficiencia = float(item[1]) if len(item) > 1 else valor_default
                except: eficiencia = valor_default
                return nombre, eficiencia
            return str(item), valor_default
        
        for item in wengines_config.get('ideal', []):
            nombre_ideal, eficiencia_base = extraer_datos_seguros(item, 1.0)
            if nombre_ideal.lower() in wengine_nombre.lower():
                return min(1.0, eficiencia_base * (1 + (ref - 1) * 0.1))
        
        for item in wengines_config.get('funcional', []):
            nombre_func, eficiencia_base = extraer_datos_seguros(item, 0.8)
            if nombre_func.lower() in wengine_nombre.lower():
                return min(1.0, eficiencia_base * (1 + (ref - 1) * 0.1))
        
        return 0.4 * (1 + (ref - 1) * 0.1)

    def _evaluar_sets_detallado(self, nombre_agente: str, sets_activos: Dict, rol: str, elemento: str) -> Tuple[float, Dict]:
        if not sets_activos: return 0.0, {'mensaje': 'Sin sets equipados'}
        config_agente = self._buscar_excepcion_agente(nombre_agente)
        sets_config = config_agente.get('sets', {})
        
        contador_sets = {}
        for slot, nombre_set in sets_activos.items():
            if not nombre_set or nombre_set == "Ninguno": continue
            cantidad = 4 if slot == 'set1' else 2
            contador_sets[nombre_set] = contador_sets.get(nombre_set, 0) + cantidad
        
        if not contador_sets: return 0.0, {'mensaje': 'Sin sets válidos'}
            
        def extraer_datos_seguros(item, valor_default):
            if isinstance(item, (tuple, list)):
                nombre = str(item[0])
                try: eficiencia = float(item[1]) if len(item) > 1 else valor_default
                except: eficiencia = valor_default
                return nombre, eficiencia
            return str(item), valor_default
        
        puntos = 0.0
        info = {'sets_equipados': list(contador_sets.keys()), 'configuracion': 'Sin configuración específica'}
        
        if sets_config:
            recom_4pc = sets_config.get('4pc', sets_config.get('ideal', []))
            recom_2pc = sets_config.get('2pc', sets_config.get('funcional', []))
            for nombre_set, cantidad in contador_sets.items():
                if cantidad >= 4:
                    for item in recom_4pc:
                        nombre_ideal, eficiencia = extraer_datos_seguros(item, 1.0)
                        if nombre_ideal.lower() in str(nombre_set).lower():
                            return eficiencia * 25, {**info, 'configuracion': f'4pc {nombre_set} (Ideal)'}
                    for item in recom_2pc:
                        nombre_func, eficiencia = extraer_datos_seguros(item, 0.8)
                        if nombre_func.lower() in str(nombre_set).lower():
                            return eficiencia * 20, {**info, 'configuracion': f'4pc {nombre_set} (Funcional)'}
            
            sets_2pc = [s for s, c in contador_sets.items() if c >= 2]
            if len(sets_2pc) >= 2:
                puntos_2pc = 0
                sets_encontrados = []
                for nombre_set in sets_2pc[:2]:
                    for item in recom_2pc:
                        nombre_func, eficiencia = extraer_datos_seguros(item, 0.8)
                        if nombre_func.lower() in str(nombre_set).lower():
                            puntos_2pc += eficiencia * 10
                            sets_encontrados.append(nombre_set)
                            break
                if puntos_2pc > puntos:
                    return puntos_2pc, {**info, 'configuracion': f'2pc/2pc: {" + ".join(sets_encontrados)}'}
        else:
            if any(c >= 4 for c in contador_sets.values()):
                return 15, {**info, 'configuracion': '4pc genérico'}
            elif len([c for c in contador_sets.values() if c >= 2]) >= 2:
                return 12, {**info, 'configuracion': '2pc/2pc genérico'}
            else:
                return 8, {**info, 'configuracion': 'Sets incompletos'}
        
        return puntos, info

    def _normalizar_nombre_stat_main(self, nombre: str) -> str:
        nombre_lower = str(nombre).lower().strip()
        mapa_mains = {
            'hp': 'hp', 'atk': 'atk', 'def': 'def', 'crit rate': 'crit_rate', 'crit dmg': 'crit_dmg',
            'anomaly mastery': 'anomaly_mastery', 'anomaly proficiency': 'anomaly_proficiency',
            'pen ratio': 'pen_ratio', 'energy regen': 'energy_regen', 'impact': 'impact',
            'physical dmg': 'physical_dmg', 'fire dmg': 'fire_dmg', 'ice dmg': 'ice_dmg',
            'electric dmg': 'electric_dmg', 'ether dmg': 'ether_dmg'
        }
        for clave, valor in mapa_mains.items():
            if clave in nombre_lower: return valor
        return nombre_lower.replace(' ', '_')

    def _evaluar_mains_detallado(self, nombre_agente: str, discos: Dict, rol: str) -> Tuple[float, Dict]:
        if not discos: return 0.0, {}
        config_agente = self._buscar_excepcion_agente(nombre_agente)
        disco4_recom = config_agente.get('disco4_prioritario', [])
        disco5_recom = config_agente.get('disco5_prioritario', [])
        disco6_recom = config_agente.get('disco6_prioritario', [])
        
        puntos_totales = 0.0
        mains_info = {}
        
        for slot_num, recomendaciones in [(4, disco4_recom), (5, disco5_recom), (6, disco6_recom)]:
            slot_key = f'disco{slot_num}'
            main_actual = discos.get(slot_key, 'Ninguno')
            
            if main_actual == 'Ninguno':
                mains_info[slot_key] = {'stat': 'Ninguno', 'puntos': 0}
                continue
            
            main_actual_norm = self._normalizar_nombre_stat_main(main_actual)
            puntos_disco = 0.0
            estado = 'Incorrecta'
            
            if recomendaciones:
                for i, recom in enumerate(recomendaciones):
                    recom_norm = self._normalizar_nombre_stat_main(str(recom))
                    if recom_norm and main_actual_norm and recom_norm in main_actual_norm:
                        if i == 0:
                            puntos_disco = 20 / 3
                            estado = 'Prioritaria'
                        else:
                            puntos_disco = 15 / 3
                            estado = 'Funcional'
                        break
            else:
                puntos_disco = 15 / 3
                estado = 'Genérica'
            
            puntos_totales += puntos_disco
            mains_info[slot_key] = {'stat': main_actual, 'puntos': round(puntos_disco, 2), 'estado': estado}
        return puntos_totales, mains_info
    
    def _normalizar_nombre_stat(self, nombre: str, valor: str = "") -> str:
        """Traduce de Enka (Inglés) a las llaves internas de CONFIG_ROLES/EXCEPCIONES (CON TILDES)."""
        return normalizar_clave_substat(nombre, valor)
    
    def calcular_rolls_sub(self, nombre_sub: str, valor_sub: str) -> int:
        """Matemática exacta extraída de tu generador de cartas."""
        try:
            clave = self._normalizar_nombre_stat(nombre_sub, valor_sub)
            return calcular_rolls_substat(clave, valor_sub)
        except Exception:
            return 1

    def _calcular_tier(self, calificacion: int) -> str:
        """Determina el tier según la calificación de la Build Card."""
        return calificacion_a_tier(calificacion)[0]

    def calcular_calificacion_personaje(self, datos_personaje: Dict, stats_finales: Dict = None) -> Dict:
        """
        Calcula la calificación del personaje usando EXACTAMENTE la misma lógica que generar_build_card.
        
        IMPORTANTE: La calificación final viene directamente del 'calidad_pct' de evaluar_calidad_global,
        que evalúa únicamente los substats (rolls ideales, decentes y basura).
        
        El breakdown incluye puntos de W-Engine, Sets y Mains stats solo para fines informativos,
        pero NO afectan la calificación final ni el tier.
        
        Args:
            datos_personaje: Diccionario con datos del personaje (nivel, rol, wengine, sets, discos, substats)
            stats_finales: Diccionario con stats finales calculados del personaje (HP, ATK, CRIT, etc.)
        
        Returns:
            Dict con calificacion (0-100), tier (GODLIKE/FLAWLESS/etc), breakdown y detalles
        """
        nombre = datos_personaje.get('nombre', 'Desconocido')
        nivel = datos_personaje.get('nivel', 0)
        
        if nivel < 50:
            return {
                'calificacion': max(0, int(nivel * 0.6)), 'tier': 'AVERAGE',
                'detalles': {'nivel_bajo': True, 'mensaje': 'Personaje de bajo nivel'},
                'breakdown': {}, 'consejos': ['Sube de nivel al personaje']
            }
        
        rol = datos_personaje.get('tipo', 'Atacante')
        elemento = datos_personaje.get('elemento', 'Físico')
        wengine = datos_personaje.get('wengine', 'Ninguno')
        wengine_refinamiento = datos_personaje.get('wengine_refinamiento', 1)
        sets_activos = datos_personaje.get('sets', {})
        discos = datos_personaje.get('discos', {})
        substats_counts = datos_personaje.get('substats_counts', {})
        eficiencia_wengine = self.calcular_eficiencia_wengine(nombre, wengine, wengine_refinamiento)
        puntos_sets, info_sets = self._evaluar_sets_detallado(nombre, sets_activos, rol, elemento)
        puntos_mains, mains_correctas = self._evaluar_mains_detallado(nombre, discos, rol)
        
        discos_sets = datos_personaje.get('discos_sets', {})
        conteo_sets = {}
        for slot, set_name in discos_sets.items():
            if set_name:
                conteo_sets[set_name] = conteo_sets.get(set_name, 0) + 1
        tiene_4pc = any(v >= 4 for v in conteo_sets.values())

        try:
            
            resumen_rolls = evaluar_calidad_global(
                nombre_agente=nombre,
                rol_agente=rol,
                rolls_actuales=substats_counts,
                stats_finales=stats_finales if stats_finales else {},
                eficiencia_wengine_actual=eficiencia_wengine * 100,
                excepciones=EXCEPCIONES_AGENTES,
                config_roles=CONFIG_ROLES,
                tiene_4pc=tiene_4pc,
                num_discos=datos_personaje.get('num_discos', 6)
            )
            calidad_pct = resumen_rolls.get('calidad_pct', 0)

        except Exception as e:
            logger.warning(f"Error evaluando calidad para {nombre}: {e}")
            import traceback
            traceback.print_exc()
            resumen_rolls = {'ideal': 0, 'decente': 0, 'basura': 0, 'total_rolls': 0, 'calidad_pct': 0}
            calidad_pct = 0

        calificacion_final = min(100, int(round(calidad_pct)))
        tier = self._calcular_tier(calificacion_final)
        
        breakdown = {
            'wengine': {'puntos': round(eficiencia_wengine * 30, 2), 'eficiencia': round(eficiencia_wengine * 100, 1), 'refinamiento': wengine_refinamiento},
            'sets': {'puntos': round(puntos_sets, 2), 'info': info_sets},
            'mains': {'puntos': round(puntos_mains, 2), 'correctas': mains_correctas},
            'substats': {
                'puntos': round((calidad_pct / 100) * 25, 2),
                'calidad_pct': round(calidad_pct, 1),
                'calidad_clasica_pct': round(resumen_rolls.get('calidad_clasica_pct', calidad_pct), 1),
                'calidad_dinamica_pct': round(resumen_rolls.get('calidad_dinamica_pct', calidad_pct), 1),
                'calidad_dinamica_raw_pct': round(resumen_rolls.get('calidad_dinamica_raw_pct', calidad_pct), 1),
                'penalizacion_dinamica_pct': round(resumen_rolls.get('penalizacion_dinamica_pct', 0), 1),
                'rolls_ideales': resumen_rolls.get('ideal', 0),
                'rolls_decentes': resumen_rolls.get('decente', 0),
                'rolls_basura': resumen_rolls.get('basura', 0),
                'total_rolls': resumen_rolls.get('total_rolls', 0),
                'prioridad_dinamica': resumen_rolls.get('prioridad_dinamica', [])[:5],
                'ajustes_dinamicos': resumen_rolls.get('ajustes_dinamicos', [])
            }
        }
        
        return {
            'calificacion': calificacion_final, 'tier': tier,
            'detalles': {'nivel': nivel, 'rol': rol, 'elemento': elemento, 'wengine': wengine, 'wengine_refinamiento': wengine_refinamiento},
            'breakdown': breakdown, 'consejos': []
        }
    
    def procesar_datos_uid(self, uid: str, datos_api: tuple, datos_agentes: Dict) -> Optional[Dict]:
        try:
            avatar_list, nickname, status = datos_api
            if not avatar_list:
                logger.warning(f"No hay personajes en el UID {uid}")
                return None
            
            MAPA_SETS_ID = {
                31800: "Jazz caótico",32600: "Metal colmilludo",32400: "Metal eléctrico",
                32300: "Metal caótico",32200: "Metal infernal",32500: "Metal Polar",32700: "Balada de la rama y la espada",
                33100: "Fábula Yunkui",31400: "Punk Hormonal",31000: "Tecno Pícido",32800: "Voz Astral",
                31600: "Jazz Oscilante",32900: "Armonía Umbría",31100: "Tecno Tetraodóntido",
                33300: "Floración del alba",33200: "Monarca del Pináculo",33400: "Nana a la Luz Cenicienta",
                33000: "Melodía de Phaeton",31900: "Proto Punk",31200: "Disco sacudestrellas",
                33600: "Aria Radiante",33500: "Balada de Aguas Blancas",31300: "Blues Libre",31500: "Rock espiritual",
                33700: "Conejo en el país de las maravillas", 33800: "Diario de una prisionera",
                33900: "Metal colmilludo", 34000: "Metal infernal"
            }
            
            personajes_procesados = {}
            for personaje in avatar_list:
                nivel = personaje.get('level', 0)
                rank = personaje.get('mindscape', 0)
                nombre_personaje = personaje.get('name', 'Desconocido')
                datos_agente = {}
                nombre_limpio_api = str(nombre_personaje).strip().lower()

                for nombre_db, datos in datos_agentes.items():
                    if str(nombre_db).strip().lower() == nombre_limpio_api:
                        datos_agente = datos
                        break

                # Si no encontró match exacto, intentar match parcial y loguear el mismatch
                if not datos_agente:
                    for nombre_db, datos in datos_agentes.items():
                        if nombre_limpio_api in str(nombre_db).strip().lower() or str(nombre_db).strip().lower() in nombre_limpio_api:
                            datos_agente = datos
                            logger.warning(f"[MATCH PARCIAL] API='{nombre_personaje}' → DB='{nombre_db}' — considera alinear el nombre en agentes.csv")
                            break
                    if not datos_agente:
                        logger.warning(f"[SIN MATCH] '{nombre_personaje}' no encontrado en agentes.csv — usando config genérico. Nombres disponibles: {list(datos_agentes.keys())[:10]}")

                tipo_agente = datos_agente.get('Tipo', datos_agente.get('tipo', 'Atacante'))
                # Normalizar Tipo: el CSV puede traer "Anomalo" sin tilde
                _mapa_tipo = {
                    'anomalo': 'Anómalo', 'anómalo': 'Anómalo',
                    'atacante': 'Atacante', 'soporte': 'Soporte',
                    'aturdidor': 'Aturdidor', 'ruptura': 'Ruptura'
                }
                tipo_agente = _mapa_tipo.get(tipo_agente.strip().lower(), tipo_agente)

                # El CSV tiene columna "elemento" en minúscula
                elemento_agente = datos_agente.get('Elemento', datos_agente.get('elemento', 'Físico'))
                # Normalizar elemento
                _mapa_elem = {
                    'hielo': 'Hielo', 'fuego': 'Fuego', 'electrico': 'Eléctrico',
                    'eléctrico': 'Eléctrico', 'fisico': 'Físico', 'físico': 'Físico',
                    'etereo': 'Etéreo', 'etéreo': 'Etéreo', 'eter': 'Etéreo', 'etereo': 'Etéreo'
                }
                elemento_agente = _mapa_elem.get(elemento_agente.strip().lower(), elemento_agente)
                wengine_data = personaje.get('weapon', {})
                wengine_nombre = wengine_data.get('name', 'Ninguno')
                wengine_refinamiento = wengine_data.get('refinement', 1)
                
                stats_finales = {}
                stats_raw = personaje.get('stats', {})
                for stat_name, stat_data in stats_raw.items():
                    if isinstance(stat_data, dict):
                        stats_finales[stat_name] = stat_data.get('value', 0)
                    else:
                        stats_finales[stat_name] = stat_data
                
                discos_lista = personaje.get('discs', [])
                sets_dict = {}
                discos_mains = {}
                discos_sets = {}
                substats_counts = {}
                contador_sets = {}
                
                for disco in discos_lista:
                    set_id = disco.get('set_id', 0)
                    slot = disco.get('slot', 0)
                    
                    if set_id > 0:
                        nombre_set = MAPA_SETS_ID.get(set_id, str(set_id))
                        contador_sets[nombre_set] = contador_sets.get(nombre_set, 0) + 1
                        
                        if 1 <= slot <= 6:
                            discos_sets[str(slot)] = nombre_set
                    
                    if slot in [4, 5, 6]:
                        main_stat_name = disco.get('main_stat', {}).get('name', 'Desconocido')
                        discos_mains[f'disco{slot}'] = main_stat_name
                    
                    for sub in disco.get('sub_stats', []):
                        sub_name = sub.get('name', '')
                        sub_value = str(sub.get('value', '0'))
                        
                        nombre_normalizado = self._normalizar_nombre_stat(sub_name, sub_value)
                        if nombre_normalizado:
                            rolls = self.calcular_rolls_sub(sub_name, sub_value)
                            substats_counts[nombre_normalizado] = substats_counts.get(nombre_normalizado, 0) + rolls
                
                sets_ordenados = sorted(contador_sets.items(), key=lambda x: x[1], reverse=True)
                if sets_ordenados:
                    sets_dict['set1'] = sets_ordenados[0][0]
                    if len(sets_ordenados) > 1: sets_dict['set2'] = sets_ordenados[1][0]
                    if len(sets_ordenados) > 2: sets_dict['set3'] = sets_ordenados[2][0]
                
                datos_personaje = {
                    'nombre': nombre_personaje, 'nivel': nivel, 'tipo': tipo_agente,
                    'elemento': elemento_agente, 'wengine': wengine_nombre,
                    'wengine_refinamiento': wengine_refinamiento, 'sets': sets_dict,
                    'discos': discos_mains, 
                    'discos_sets': discos_sets,
                    'substats_counts': substats_counts,
                    'mindscapes': rank,
                    'num_discos': len(discos_lista)
                }
                
                calificacion_data = self.calcular_calificacion_personaje(datos_personaje, stats_finales)
                
                personajes_procesados[nombre_personaje] = {
                    **datos_personaje,
                    'calificacion': calificacion_data['calificacion'],
                    'tier': calificacion_data['tier'],
                    'breakdown': calificacion_data.get('breakdown', {}),
                    'detalles': calificacion_data.get('detalles', {}),
                    'consejos': calificacion_data.get('consejos', [])
                }
            
            return {
                'uid': uid, 'nickname': nickname, 'personajes': personajes_procesados,
                'ultima_actualizacion': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error procesando datos del UID {uid}: {e}")
            import traceback
            traceback.print_exc()
            return None

    def cargar_ranking_global(self) -> Dict:
        """Lee siempre desde disco — para que la GUI vea datos frescos."""
        with self._lock:
            if os.path.exists(self.ruta_ranking):
                try:
                    with open(self.ruta_ranking, 'r', encoding='utf-8') as f:
                        return json.load(f)   # ← NO toca _ranking_cache
                except Exception as e:
                    logger.error(f"Error leyendo ranking global: {e}")
                    if self._ranking_cache is not None:
                        return dict(self._ranking_cache)  # fallback
            return {}

    def guardar_ranking_global(self, ranking_data: Dict):
        """Escribe en disco de forma atómica. NO adquiere el lock (ya lo tiene el caller)."""
        ruta_tmp = self.ruta_ranking + ".tmp"
        try:
            with open(ruta_tmp, 'w', encoding='utf-8') as f:
                json.dump(ranking_data, f, indent=2, ensure_ascii=False)
            os.replace(ruta_tmp, self.ruta_ranking)
            logger.info(f"[RANKING] Guardado en disco: {len(ranking_data)} jugadores")
        except Exception as e:
            logger.error(f"Error guardando ranking global: {e}")
            if os.path.exists(ruta_tmp):
                os.remove(ruta_tmp)

    def actualizar_jugador_en_ranking(self, apodo: str, datos_jugador: Dict):
        """Actualiza un jugador — thread-safe, opera sobre el caché en memoria."""
        with self._lock:
            if self._ranking_cache is None:
                # primera vez: cargar del disco sin llamar a cargar_ranking_global (evita deadlock)
                if os.path.exists(self.ruta_ranking):
                    try:
                        with open(self.ruta_ranking, 'r', encoding='utf-8') as f:
                            self._ranking_cache = json.load(f)
                    except Exception as e:
                        logger.error(f"Error cargando caché inicial: {e}")
                        self._ranking_cache = {}
                else:
                    self._ranking_cache = {}
            self._ranking_cache[apodo] = datos_jugador
            self.guardar_ranking_global(self._ranking_cache)
        logger.debug(f"[RANKING] Jugador actualizado: {apodo}")

    # Agregar en gestor_ranking.py después de actualizar_jugador_en_ranking:
    def eliminar_jugador_del_ranking(self, apodo: str):
        """Elimina un jugador del ranking — thread-safe."""
        with self._lock:
            if self._ranking_cache is not None:
                self._ranking_cache.pop(apodo, None)
            ranking = {}
            if os.path.exists(self.ruta_ranking):
                try:
                    with open(self.ruta_ranking, 'r', encoding='utf-8') as f:
                        ranking = json.load(f)
                except:
                    pass
            if apodo in ranking:
                del ranking[apodo]
                self._ranking_cache = ranking
                self.guardar_ranking_global(ranking)
            logger.info(f"[RANKING] Jugador eliminado: {apodo}")

    def limpiar_cache_ranking(self):
        """
        Elimina el ranking_global.json en disco y resetea el caché en memoria.
        Usar cuando se actualiza la lógica de evaluación para forzar recálculo
        completo desde la API en la próxima ejecución del actualizador.
        """
        with self._lock:
            self._ranking_cache = {}
            if os.path.exists(self.ruta_ranking):
                os.remove(self.ruta_ranking)
                logger.info("[RANKING] Cache limpiado — se recalculará todo en la próxima actualización")
            else:
                logger.info("[RANKING] No había cache que limpiar")

    def generar_ranking_por_personaje(self, nombre_personaje: str) -> List[Tuple[str, int, str, str]]:
        ranking = self.cargar_ranking_global()
        resultados = []
        for apodo, datos_jugador in ranking.items():
            personajes = datos_jugador.get('personajes', {})
            if nombre_personaje in personajes:
                calificacion = personajes[nombre_personaje].get('calificacion', 0)
                tier = personajes[nombre_personaje].get('tier', calificacion_a_tier(0)[0])
                uid = datos_jugador.get('uid', '')
                resultados.append((apodo, calificacion, tier, uid))
        resultados.sort(key=lambda x: x[1], reverse=True)
        return resultados
    
    def obtener_ranking_variable(self) -> Dict:
        return self.cargar_ranking_global()
    
    def obtener_datos_completos_uid(self, uid: str, gestor_api, agentes_data: Dict) -> Optional[Dict]:
        try:
            logger.info(f"Obteniendo datos del UID {uid} desde la API...")
            datos_api = gestor_api.obtener_datos_uid(uid)
            
            if not datos_api or datos_api[0] is None:
                logger.error(f"No se pudieron obtener datos de la API para UID {uid}")
                return None
            
            if isinstance(agentes_data, list):
                agentes_dict = {}
                for agente in agentes_data:
                    nombre = agente.get('Nombre', agente.get('nombre', ''))
                    if nombre: agentes_dict[nombre] = agente
            else:
                agentes_dict = agentes_data
            
            datos_procesados = self.procesar_datos_uid(uid, datos_api, agentes_dict)
            if not datos_procesados:
                logger.error(f"Error procesando datos del UID {uid}")
                return None
            
            logger.info(f"Datos obtenidos exitosamente para UID {uid}")
            return datos_procesados
        except Exception as e:
            logger.error(f"Error obteniendo datos completos del UID {uid}: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def obtener_estadisticas_personaje(self, nombre_personaje: str) -> Dict:
        ranking = self.cargar_ranking_global()
        calificaciones = []
        tiers = []
        for datos_jugador in ranking.values():
            personajes = datos_jugador.get('personajes', {})
            if nombre_personaje in personajes:
                calificaciones.append(personajes[nombre_personaje].get('calificacion', 0))
                tiers.append(personajes[nombre_personaje].get('tier', 'MID'))
        if not calificaciones:
            return {'total_jugadores': 0, 'promedio': 0, 'max': 0, 'min': 0, 'distribucion_tiers': {}}
        from collections import Counter
        return {
            'total_jugadores': len(calificaciones), 'promedio': sum(calificaciones) / len(calificaciones),
            'max': max(calificaciones), 'min': min(calificaciones), 'distribucion_tiers': dict(Counter(tiers))
        }
