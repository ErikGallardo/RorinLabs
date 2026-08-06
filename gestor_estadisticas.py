import logging
import unicodedata
from efectos_core import MAPA_CORE
from efectos_sets import MAPA_EFECTOS_SETS
from efectos_mindscapes import MAPA_MINDSCAPES
from efectos_soportes import MAPA_SOPORTES_AGENTES, MAPA_SOPORTES_SETS
from efectos_pasivas import MAPA_PASIVAS
from efectos_soportes import MAPA_SOPORTES_WENGINES
from substats_config import valor_substat
try:
    from efectos_wengines import MAPA_WENGINES
except ImportError:
    MAPA_WENGINES = {} 

class GestorEstadisticas:
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)

    def _parse_valor(self, valor, es_porcentual=False):
        if valor is None: return 0.0
        try:
            val_str = str(valor).replace('%', '').replace(',', '.').strip()
            num = float(val_str) if val_str else 0.0
            return num
        except (ValueError, TypeError):
            return 0.0

    def _normalizar(self, texto):
        if not texto: return ""
        try:
            s = str(texto).strip().lower()
            s = ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
            return s
        except Exception:
            return str(texto).strip().lower()
    
    def calcular_totales(self, estado, mapa_discos):
        """
        Calcula las estadísticas finales sumando Base (Personaje + Arma) + Discos + Substats.
        """
        self.resultados_finales = {}
        if hasattr(estado, 'stats_base_personaje') and estado.stats_base_personaje:
            for k, v in estado.stats_base_personaje.items():
                self.resultados_finales[k] = self.resultados_finales.get(k, 0) + v

        stats_arma = getattr(estado, 'stats_base_wengine', getattr(estado, 'stats_base_arma', {}))
        if stats_arma:
            for k, v in stats_arma.items():
                self.resultados_finales[k] = self.resultados_finales.get(k, 0) + v

        acumulado_pct = {}
        acumulado_plano = {}

        for slot, nombre_stat in estado.discos.items():
            if nombre_stat and nombre_stat != "Ninguno":
                info_disco = mapa_discos.get((int(slot), nombre_stat))
                if info_disco:
                    if info_disco['tipo'] == 'porcentual':
                        acumulado_pct[nombre_stat] = acumulado_pct.get(nombre_stat, 0) + info_disco['valor']
                    else:
                        acumulado_plano[nombre_stat] = acumulado_plano.get(nombre_stat, 0) + info_disco['valor']

        for stat_key, cantidad_rolls in estado.substats_counts.items():
            if cantidad_rolls > 0:
                valor = valor_substat(stat_key) * cantidad_rolls
                nombre_real = stat_key.replace("_porcentual", "").replace("_plano", "")
                
                if "_porcentual" in stat_key:
                    acumulado_pct[nombre_real] = acumulado_pct.get(nombre_real, 0) + valor
                else:
                    acumulado_plano[nombre_real] = acumulado_plano.get(nombre_real, 0) + valor


        for stat in ["Ataque", "Defensa", "Puntos_Vida", "Tasa_de_Anomalía", "Recuperación_energía"]:
            base = self.resultados_finales.get(stat, 0)
            if base == 0: continue
            
            pct = acumulado_pct.get(stat, 0)
            plano = acumulado_plano.get(stat, 0)
            self.resultados_finales[stat] = base * (1 + (pct / 100)) + plano

        stats_directas = [
            "Maestría_Anomalía", "Impacto", "Probabilidad_crítico", 
            "Daño_crítico", "Daño_elemental", "Tasa_de_Perforación", 
        ]
        for stat in stats_directas:
            base = self.resultados_finales.get(stat, 0)
            pct = acumulado_pct.get(stat, 0)
            plano = acumulado_plano.get(stat, 0)
            self.resultados_finales[stat] = base + pct + plano

    def obtener_totales(self):
        """Retorna el diccionario con las stats calculadas."""
        if hasattr(self, 'resultados_finales'):
            return self.resultados_finales
        return {}

    def calcular_stats_finales(self, base_stats, estado_build, wengine_db, sets_db, 
                               discos_db, substats_db, elemento_agente, tipo_agente=None, 
                               stacks_core=0, sets_externos=None, estado_enemigo="Normal", **kwargs):
        if not base_stats:
            return {}

        elemento_agente = elemento_agente if elemento_agente else ""
        STATS_ESCALABLES = {'Ataque', 'Defensa', 'Puntos_Vida', 'Impacto', 'Aturdimiento', 'Recuperación_energía', 'Tasa_de_Anomalía', 'Tasa_de_Anomalia'}
        
        bases_wengine = {k: 0.0 for k in STATS_ESCALABLES} 
        
        # --- SEPARACIÓN DE STATS ---

        multiplicadores_pct_inicial = {} 
        sumas_planas_inicial = {}
        multiplicadores_pct_combate = {}
        sumas_planas_combate = {}
        info_especial = {} 
        
        trazas = {
            'pct_inicial': {}, 'plano_inicial': {},
            'pct_combate': {}, 'plano_combate': {}
        }

        def registrar_traza(fase, stat, fuente, valor):
            if stat not in trazas[fase]:
                trazas[fase][stat] = {}
            trazas[fase][stat][fuente] = trazas[fase][stat].get(fuente, 0.0) + valor

        sumas_planas_inicial['Daño_Adicional'] = 0.0
        sumas_planas_inicial['Daño_elemental'] = 0.0
        sumas_planas_inicial['Reduccion_DEF_enemigo'] = 0.0

        tiene_set = (estado_build.sets.get('set1', "Ninguno") != "Ninguno") or \
                    (estado_build.sets.get('set2', "Ninguno") != "Ninguno")
        
        if tiene_set:
            sumas_planas_inicial['Puntos_Vida'] = sumas_planas_inicial.get('Puntos_Vida', 0.0) + 2200.0
            registrar_traza('plano_inicial', 'Puntos_Vida', 'Bonus Base por llevar Sets', 2200.0)
            
            sumas_planas_inicial['Ataque'] = sumas_planas_inicial.get('Ataque', 0.0) + 316.0
            registrar_traza('plano_inicial', 'Ataque', 'Bonus Base por llevar Sets', 316.0)
            
            sumas_planas_inicial['Defensa'] = sumas_planas_inicial.get('Defensa', 0.0) + 184.0
            registrar_traza('plano_inicial', 'Defensa', 'Bonus Base por llevar Sets', 184.0)

        nombre_agente = estado_build.nombre_agente
        core_activo = estado_build.core_activo
        nombre_habilidad = estado_build.nombre_habilidad or ""
        m_level = estado_build.mindscape
        m_stacks = estado_build.mindscape_stacks
        condicion = getattr(estado_build, 'mindscape_cond', "") or estado_build.set_condicion

        def agregar_bono(key, valor, es_pct_flag, es_combate=False, fuente="Desconocido"):
            if valor == 0: return
            key = key.strip()

            if key in STATS_ESCALABLES and es_pct_flag:
                valor_final = valor / 100.0
                if es_combate:
                    multiplicadores_pct_combate[key] = multiplicadores_pct_combate.get(key, 0.0) + valor_final
                    registrar_traza('pct_combate', key, fuente, valor_final)
                else:
                    multiplicadores_pct_inicial[key] = multiplicadores_pct_inicial.get(key, 0.0) + valor_final
                    registrar_traza('pct_inicial', key, fuente, valor_final)
            else:
                if es_combate:
                    sumas_planas_combate[key] = sumas_planas_combate.get(key, 0.0) + valor
                    registrar_traza('plano_combate', key, fuente, valor)
                else:
                    sumas_planas_inicial[key] = sumas_planas_inicial.get(key, 0.0) + valor
                    registrar_traza('plano_inicial', key, fuente, valor)

        if nombre_agente in MAPA_MINDSCAPES:
            func_mindscape = MAPA_MINDSCAPES[nombre_agente]
            niveles_mindscape = [1, 2, 4, 5, 6]
            bonos_previos = {}
            for nivel in niveles_mindscape:
                if nivel > m_level:
                    break
                bonos_nivel = func_mindscape(nivel, stacks=m_stacks, condicion_activa=condicion, nombre_habilidad=nombre_habilidad)
                for stat, valor in bonos_nivel.items():
                    diff = valor - bonos_previos.get(stat, 0.0)
                    if diff != 0:
                        es_pct = (stat in STATS_ESCALABLES)
                        agregar_bono(stat, diff, es_pct, es_combate=True, fuente=f"Mindscape M{nivel} ({nombre_agente})")
                bonos_previos = bonos_nivel

        # --- 1. SUBSTATS (Inicial) ---
        if substats_db and hasattr(estado_build, 'substats_counts'):
            for item in substats_db:
                u_key = item['unique_key']
                cantidad = estado_build.substats_counts.get(u_key, 0)
                if cantidad > 0:
                    stat_key = item['key_interna']
                    tipo = item['tipo']
                    valor_unitario = item['valor']
                    total_bono = cantidad * valor_unitario
                    es_pct = ('porcentual' in tipo)
                    agregar_bono(stat_key, total_bono, es_pct, es_combate=False, fuente=f"Substats ({cantidad} rolls)")

        # --- 2. W-ENGINE MAIN STATS (Inicial) ---
        wengine_data = wengine_db.get(estado_build.nombre_wengine)
        if wengine_data:
            mapeo_wengine = {
                'Ataque wengine': ('Ataque', False),
                'Ataque': ('Ataque', True),
                'Recuperación de energía': ('Recuperación_energía', True),
                'Maestría de Anomalía del agente': ('Maestría_Anomalía', False),
                'Tasa de anomalía': ('Tasa_de_Anomalía' , True),
                'Probabilidad de crítico': ('Probabilidad_crítico', False),
                'Daño crítico': ('Daño_crítico', False),
                'Tasa de perforación': ('Tasa_de_Perforación', False),
                'Puntos de vida': ('Puntos_Vida', True),
                'Defensa': ('Defensa', True),
                'Impacto': ('Impacto', False),
                'Aturdimiento': ('Aturdimiento', False)
            }
            for csv_col, (stat_key, es_pct_csv) in mapeo_wengine.items():
                valor = self._parse_valor(wengine_data.get(csv_col), es_porcentual=es_pct_csv)
                if csv_col == 'Ataque wengine':
                    bases_wengine['Ataque'] += valor
                else:
                    agregar_bono(stat_key, valor, es_pct_csv, es_combate=False, fuente="W-Engine (Main Stat)")

        # --- 3. SETS 2PC (Inicial) ---
        keywords_dash = ["dash"]
        nombre_habilidad_norm = self._normalizar(estado_build.nombre_habilidad or "")

        for set_nombre_usuario in estado_build.sets.values():
            if not set_nombre_usuario or set_nombre_usuario == "Ninguno":
                continue
            
            set_norm_usuario = self._normalizar(set_nombre_usuario).replace(" ", "")
            set_data = None
            
            if sets_db:
                for s in sets_db:
                    n_bruto = s.get('Nombre') or s.get('\ufeffNombre') or s.get('nombre') or ""
                    n_csv = self._normalizar(n_bruto).replace(" ", "")
                    
                    if n_csv == set_norm_usuario:
                        set_data = s
                        break
            
            if set_data:
                stat = str(set_data.get('stat') or set_data.get('Stat') or '').strip()
                tipo = str(set_data.get('Tipo') or set_data.get('tipo') or '').strip().lower()
                es_pct_csv = (tipo == 'porcentual')
                
                valor = self._parse_valor(set_data.get('valor') or set_data.get('Valor'), es_porcentual=es_pct_csv)
                elem_req = str(set_data.get('elemento') or set_data.get('Elemento') or 'todos').strip()

                if stat == 'Bono_Dash':
                    es_dash = any(k in nombre_habilidad_norm for k in keywords_dash)
                    if es_dash:
                        agregar_bono("Daño_elemental", valor, es_pct_csv, es_combate=False) 
                elif stat == 'Daño_elemental':
                    if elem_req.lower() != 'todos' and self._normalizar(elem_req) != self._normalizar(elemento_agente):
                        continue
                    agregar_bono(stat, valor, es_pct_csv, es_combate=False, fuente=f"Set 2pc ({set_data.get('Nombre', 'Set')})")
                else:
                    agregar_bono(stat, valor, es_pct_csv, es_combate=False, fuente=f"Set 2pc ({set_data.get('Nombre', 'Set')})")

        # --- 4. DISCOS MAIN STATS (Inicial) ---
        for slot, disco_nombre in estado_build.discos.items():
            disco_lista = discos_db.get(slot, [])
            disco_norm_usuario = self._normalizar(disco_nombre)
            disco_data = next((d for d in disco_lista if self._normalizar(d.get('nombre')) == disco_norm_usuario), None)
            
            if disco_data:
                stat = disco_data.get('stat')
                tipo = str(disco_data.get('tipo') or '').strip().lower()
                es_pct_csv = (tipo == 'porcentual')
                
                valor = self._parse_valor(disco_data.get('valor'), es_porcentual=es_pct_csv)
                agregar_bono(stat, valor, es_pct_csv, es_combate=False, fuente=f"Disco {slot} (Main Stat)")

        def get_stats_snapshot():
            snap = {}
            todas_keys = set(base_stats.keys()) | set(sumas_planas_inicial.keys()) | set(multiplicadores_pct_inicial.keys()) | set(sumas_planas_combate.keys()) | set(multiplicadores_pct_combate.keys())
            
            for k in todas_keys:
                val_base = base_stats.get(k, 0.0)
                
                if isinstance(val_base, str):
                    try:
                        base = float(val_base)
                    except (ValueError, TypeError):
                        snap[k] = val_base
                        continue
                else:
                    try:
                        base = float(val_base)
                    except (ValueError, TypeError):
                        base = 0.0

                bono_man = estado_build.bonos_manuales_planos.get(k, 0.0)
                if k in STATS_ESCALABLES:
                    base_total = base + bases_wengine.get(k, 0.0)
                    ini = (base_total * (1 + multiplicadores_pct_inicial.get(k, 0.0))) + sumas_planas_inicial.get(k, 0.0) + bono_man
                    tot = (ini * (1 + multiplicadores_pct_combate.get(k, 0.0))) + sumas_planas_combate.get(k, 0.0)
                    snap[k] = tot
                else:
                    snap[k] = base + sumas_planas_inicial.get(k, 0.0) + multiplicadores_pct_inicial.get(k, 0.0) + sumas_planas_combate.get(k, 0.0) + multiplicadores_pct_combate.get(k, 0.0) + bono_man
            return snap

        # --- 2.5 W-ENGINE PASIVA (Combate) ---
        if wengine_data:
            tipo_arma = wengine_data.get('tipow,personaje') or wengine_data.get('tipow', '') 
            match_tipo = self._normalizar(tipo_agente) in self._normalizar(str(tipo_arma).strip())
            if match_tipo:
                nombre_arma_real = estado_build.nombre_wengine
                if nombre_arma_real in MAPA_WENGINES:
                    funcion_pasiva = MAPA_WENGINES[nombre_arma_real]
                    stats_temp_arma = get_stats_snapshot()
                    try:
                        bonos_pasiva = funcion_pasiva(
                            stats_actuales=stats_temp_arma, 
                            refinamiento=getattr(estado_build, 'refinamiento', 1), 
                            nombre_agente=estado_build.nombre_agente,
                            stacks=getattr(estado_build, 'stacks', 0),
                            estado_enemigo=estado_enemigo,
                            elemento_agente=elemento_agente,
                            tipo_agente=tipo_agente
                        )
                    except TypeError:
                        bonos_pasiva = funcion_pasiva(
                            stats_temp_arma, 
                            getattr(estado_build, 'refinamiento', 1), 
                            estado_build.nombre_agente, 
                            getattr(estado_build, 'stacks', 0)
                        )
                    ref_actual = getattr(estado_build, 'refinamiento', 1)
                    stacks_actual = getattr(estado_build, 'stacks', 0)
                    for stat, valor in bonos_pasiva.items():
                        es_pct = (stat in STATS_ESCALABLES)
                        if stat == "Recuperación_energía": es_pct = False
                        fuente_w = f"{nombre_arma_real} R{ref_actual}"
                        if stacks_actual > 0:
                            fuente_w += f" x{stacks_actual}"
                        agregar_bono(stat, valor, es_pct, es_combate=True, fuente=fuente_w)

        # --- 5. SETS X4 (Combate) ---
        nombre_set1 = estado_build.sets.get('set1', "Ninguno")
        nombre_set3 = estado_build.sets.get('set3', "Ninguno")
        es_build_4pc = (nombre_set3 == "Ninguno") and (nombre_set1 != "Ninguno")
        
        if es_build_4pc:
            set1_norm = self._normalizar(nombre_set1)
            funcion_efecto = next((func for key, func in MAPA_EFECTOS_SETS.items() if self._normalizar(key) == set1_norm), None)
            if funcion_efecto:
                bonos_extra = funcion_efecto(
                    get_stats_snapshot(), 
                    elemento=elemento_agente,
                    stacks=getattr(estado_build, 'set_stacks', 0),
                    condicion_activa=getattr(estado_build, 'set_condicion', False),
                    tipo_agente=tipo_agente,  
                    nombre_agente=estado_build.nombre_agente
                )
                if bonos_extra:
                    for stat, valor in bonos_extra.items():
                        es_pct = (stat in STATS_ESCALABLES)
                        agregar_bono(stat, valor, es_pct, es_combate=True, fuente=f"Set 4pc ({nombre_set1})")

        # --- 5.5. SOPORTES Y BUFFS EXTERNOS (Combate) ---
        lista_tipos_soportes = []
        lista_elementos_soportes = []
        lista_facciones_soportes = []
        lista_nombres_soportes = []

        if tipo_agente: lista_tipos_soportes.append(self._normalizar(tipo_agente))
        if elemento_agente: lista_elementos_soportes.append(self._normalizar(elemento_agente))
        if estado_build.nombre_agente: lista_nombres_soportes.append(self._normalizar(estado_build.nombre_agente))
            
        faccion_dps = kwargs.get("faccion_agente", "")
        if faccion_dps: lista_facciones_soportes.append(self._normalizar(faccion_dps))

        if sets_externos:
            for info_set in sets_externos:
                tipo_sup = self._normalizar(info_set.get('tipo_agente', ''))
                if tipo_sup: lista_tipos_soportes.append(tipo_sup)

                elem_sup = self._normalizar(str(info_set.get('elemento_agente', '')))
                if elem_sup: lista_elementos_soportes.append(elem_sup)
                
                facc_sup = self._normalizar(str(info_set.get('faccion_agente', '')))
                if facc_sup: lista_facciones_soportes.append(facc_sup)

                norm_nombre = self._normalizar(str(info_set.get('nombre_agente', '')))
                if norm_nombre: lista_nombres_soportes.append(norm_nombre)

        datos_equipo_completo = {
            "roles": lista_tipos_soportes,
            "elementos": lista_elementos_soportes,
            "facciones": lista_facciones_soportes,
            "nombres": lista_nombres_soportes
        }

        if sets_externos:
            for info_set in sets_externos:
                tipo_sup = self._normalizar(info_set.get('tipo_agente', ''))
                stats_del_soporte = info_set.get('stats', {})
                n_set = self._normalizar(info_set.get('nombre_set', '') or info_set.get('nombre', ''))
                n_agente = self._normalizar(info_set.get('nombre_agente', ''))
                n_arma = self._normalizar(info_set.get('nombre_arma', ''))
                ref_arma = info_set.get('refinamiento_arma', 1)
                stacks_arma = info_set.get('stacks_arma', 0)
                # stacks_arma == -1 → wengine sin stacks desactivado por el usuario → no aplicar
                wengine_activo = (stacks_arma != -1)
                stacks_arma_efectivo = max(0, stacks_arma)  # evitar pasar -1 a funciones
                mindscape_sup = info_set.get('mindscape', info_set.get('mindscape_agente', 0))
                res_soporte_temp = {} 

                for key_agente, funcion in MAPA_SOPORTES_AGENTES.items():
                    if key_agente in n_agente:
                        funcion(res_soporte_temp, tipo_agente=tipo_sup, stats=stats_del_soporte, elemento_dps=elemento_agente, datos_equipo=datos_equipo_completo, estado_enemigo=estado_enemigo, mindscape=mindscape_sup, **kwargs)
                        break

                for key_set, funcion in MAPA_SOPORTES_SETS.items():
                    if key_set in n_set:
                        funcion(res_soporte_temp, tipo_agente=tipo_sup, stats=stats_del_soporte, elemento_dps=elemento_agente, datos_equipo=datos_equipo_completo)
                        break
                
                if wengine_activo:
                    for key_wengine, funcion in MAPA_SOPORTES_WENGINES.items():
                        if key_wengine in n_arma:
                            funcion(res_soporte_temp, refinamiento=ref_arma, stacks=stacks_arma_efectivo, stats=stats_del_soporte, datos_equipo=datos_equipo_completo, elemento_dps=elemento_agente)
                            break
                
                for stat, valor in res_soporte_temp.items():
                    if stat == "Ataque_%":
                        agregar_bono("Ataque", valor, True, es_combate=True, fuente=f"Soporte/Buff ({n_agente or n_set or n_arma})")
                        continue
                        
                    es_pct = (stat in STATS_ESCALABLES)
                    if stat == "Ataque": es_pct = False
                    
                    if isinstance(valor, (int, float)):
                        agregar_bono(stat, valor, es_pct, es_combate=True, fuente=f"Soporte/Buff ({n_agente or n_set or n_arma})")
                    else:
                        info_especial[stat] = valor

        # --- 5.6. PASSIVE (Combate) ---
        if nombre_agente in MAPA_PASIVAS:
            func_pasiva = MAPA_PASIVAS[nombre_agente]
            bonos_pasiva = func_pasiva(
                datos_equipo=datos_equipo_completo,
                roles_equipo=lista_tipos_soportes,
                stats_actuales=get_stats_snapshot(),
                nombre_habilidad=estado_build.nombre_habilidad,
                elemento=elemento_agente,
                **sets_externos if isinstance(sets_externos, dict) else {},
                **kwargs
            )
            for stat, valor in bonos_pasiva.items():
                if isinstance(valor, (int, float)):
                    es_pct = (stat in STATS_ESCALABLES)
                    agregar_bono(stat, valor, es_pct, es_combate=True, fuente=f"Pasiva {nombre_agente}")
                else:
                    info_especial[stat] = valor

        # --- 5.7. CORE (Combate) ---
        if nombre_agente in MAPA_CORE:
            func_core = MAPA_CORE[nombre_agente]
            potencial_actual = getattr(estado_build, 'nivel_potencial', kwargs.get('potencial', 0))
            
            try:
                bonos_core = func_core(
                    condicion_activa=core_activo, 
                    nombre_habilidad=nombre_habilidad,
                    stats_actuales=get_stats_snapshot(),
                    stacks=stacks_core,
                    tipos_soportes=lista_tipos_soportes,
                    potencial=potencial_actual
                )
            except TypeError:
                try:
                    bonos_core = func_core(condicion_activa=core_activo, nombre_habilidad=nombre_habilidad, stacks=stacks_core, stats_actuales=get_stats_snapshot(), potencial=potencial_actual)
                except TypeError:
                    bonos_core = func_core(condicion_activa=core_activo, nombre_habilidad=nombre_habilidad, potencial=potencial_actual)
            
            fuente_core = f"Core {nombre_agente}"
            if stacks_core > 0:
                fuente_core += f" x{stacks_core}"
            for stat, valor in bonos_core.items():
                if stat in ("Ataque_Ben_Conversion", "Ataque_Plano"):
                    agregar_bono("Ataque", valor, False, es_combate=True, fuente=fuente_core)
                    continue
                if isinstance(valor, (int, float)):
                    es_pct = (stat in STATS_ESCALABLES)
                    agregar_bono(stat, valor, es_pct, es_combate=True, fuente=fuente_core)
                else:
                    info_especial[stat] = valor

        # --- 5.8. NODOS DA (Combate) ---
        buffs_nodos = kwargs.get("buffs_nodos", {})
        if buffs_nodos:
            for stat, valor in buffs_nodos.items():
                if valor == 0: continue
                
                if stat == "Ataque_%":
                    agregar_bono("Ataque", valor, True, es_combate=True, fuente="Nodo DA")
                elif stat == "Res_Red":
                    sumas_planas_combate["Resistencia_porcentual"] = sumas_planas_combate.get("Resistencia_porcentual", 0.0) - valor
                elif stat.startswith("Daño_elemental__"):
                    elementos_permitidos = stat.split("__")[1].split("_")
                    elem_norm = str(elemento_agente).lower().strip()
                    if elem_norm in elementos_permitidos:
                        agregar_bono("Daño_elemental", valor, False, es_combate=True, fuente="Nodo DA")
                elif stat in ["DMG_Taken", "Bono_Daño_Anomalia", "Buff_Defensa", "Multiplicador_Aturdimiento", "Daño_Cadena_Ulti", "Resistencia_Anomalía_Enemigo", "Sheer_force", "Abloom_dmg"]:
                    info_especial[stat] = info_especial.get(stat, 0.0) + valor
                else:
                    es_pct = (stat in STATS_ESCALABLES)
                    if stat == "Maestría_Anomalía": es_pct = False 
                    agregar_bono(stat, valor, es_pct, es_combate=True, fuente="Nodo DA")

        # --- 6. CÁLCULO FINAL ---
        resultados = {}
        todas_las_keys = set(base_stats.keys()) | set(sumas_planas_inicial.keys()) | set(multiplicadores_pct_inicial.keys()) | set(sumas_planas_combate.keys()) | set(multiplicadores_pct_combate.keys())
        
        desglose_texto = "\n\n[ DESGLOSE DETALLADO DE ESTADÍSTICAS Y FUENTES ]\n" + "-" * 60

        STATS_PERMITIDAS = [
            "Ataque", "Defensa", "Puntos_Vida", "Impacto",
            "Probabilidad_crítico", "Daño_crítico", "Tasa_de_Perforación",
            "Daño_elemental", "Daño_Adicional", "Daño_Aftershock", "Maestría_Anomalía",
            "Tasa_de_Anomalía", "Recuperación_energía", "Sheer_force"
        ]

        def format_trazas(stat_k, dict_trazas, fase_key, es_pct):
            lineas = []
            dic_fuentes = dict_trazas[fase_key].get(stat_k, {})
            for f, v in dic_fuentes.items():
                if v == 0: continue
                v_str = f"+{v*100:g}%" if es_pct else f"+{v:g}"
                lineas.append(f"      ├─ {f}: {v_str}")
            return "\n".join(lineas)

        for stat_key in sorted(list(todas_las_keys)):
            val_base = base_stats.get(stat_key, 0.0)
            
            if isinstance(val_base, str):
                try: base_agente = float(val_base)
                except (ValueError, TypeError):
                    resultados[stat_key] = val_base
                    continue
            else:
                try: base_agente = float(val_base)
                except (ValueError, TypeError): base_agente = 0.0
                
            bono_manual = estado_build.bonos_manuales_planos.get(stat_key, 0.0)
            
            if stat_key in STATS_ESCALABLES:
                base_arma = bases_wengine.get(stat_key, 0.0)
                base_total = base_agente + base_arma
                
                pct_ini = multiplicadores_pct_inicial.get(stat_key, 0.0)
                flat_ini = sumas_planas_inicial.get(stat_key, 0.0)
                stat_inicial = (base_total * (1 + pct_ini)) + flat_ini + bono_manual
                
                pct_combate = multiplicadores_pct_combate.get(stat_key, 0.0)
                flat_combate = sumas_planas_combate.get(stat_key, 0.0)
                
                valor_final = (stat_inicial * (1 + pct_combate)) + flat_combate
                resultados[stat_key] = valor_final
                
                if valor_final > 0 and stat_key in STATS_PERMITIDAS:
                    nombre_bonito = stat_key.replace('_', ' ')
                    bloque = f"\n🔹 {nombre_bonito.upper()}:\n"
                    bloque += f"   [Fase 0] Base: Agente ({base_agente:g}) + Arma ({base_arma:g}) = {base_total:g}\n"
                    
                    bloque += f"   [Fase 1] Equipamiento y Bonos Iniciales:\n"
                    trazas_pct_ini = format_trazas(stat_key, trazas, 'pct_inicial', True)
                    trazas_plano_ini = format_trazas(stat_key, trazas, 'plano_inicial', False)
                    if trazas_pct_ini: bloque += f"{trazas_pct_ini}\n"
                    if trazas_plano_ini: bloque += f"{trazas_plano_ini}\n"
                    if not trazas_pct_ini and not trazas_plano_ini: bloque += "      └─ (Sin bonos de equipamiento)\n"
                    else: bloque += f"      └─ Total Fase 1: +{pct_ini*100:g}% (Multiplicador) | +{flat_ini:g} (Plano)\n"
                    
                    if bono_manual != 0: bloque += f"      └─ Ajuste Manual Activo: +{bono_manual:g}\n"
                    bloque += f"   >>> Total Inicial (Fuera Combate): {stat_inicial:.2f}\n"
                    
                    bloque += f"   [Fase 2] Pasivas, Cores y Soportes (Combate):\n"
                    trazas_pct_comb = format_trazas(stat_key, trazas, 'pct_combate', True)
                    trazas_plano_comb = format_trazas(stat_key, trazas, 'plano_combate', False)
                    if trazas_pct_comb: bloque += f"{trazas_pct_comb}\n"
                    if trazas_plano_comb: bloque += f"{trazas_plano_comb}\n"
                    if not trazas_pct_comb and not trazas_plano_comb: bloque += "      └─ (Sin bonos de combate aplicables)\n"
                    else: bloque += f"      └─ Total Fase 2: +{pct_combate*100:g}% (Multiplicador) | +{flat_combate:g} (Plano)\n"
                        
                    bloque += f"   >>> TOTAL FINAL EN COMBATE: {valor_final:.2f}\n"
                    desglose_texto += bloque

            else:
                extras_ini = sumas_planas_inicial.get(stat_key, 0.0) + multiplicadores_pct_inicial.get(stat_key, 0.0)
                extras_combate = sumas_planas_combate.get(stat_key, 0.0) + multiplicadores_pct_combate.get(stat_key, 0.0)
                valor_final = base_agente + extras_ini + extras_combate + bono_manual
                resultados[stat_key] = valor_final
                
                if valor_final > 0 and stat_key in STATS_PERMITIDAS:
                    nombre_bonito = stat_key.replace('_', ' ')
                    bloque = f"\n🔸 {nombre_bonito.upper()}:\n"
                    bloque += f"   [Fase 0] Base Personaje: {base_agente:g}\n"
                    
                    bloque += f"   [Fase 1] Equipamiento y Bonos Iniciales:\n"
                    trazas_ini1 = format_trazas(stat_key, trazas, 'plano_inicial', False)
                    trazas_ini2 = format_trazas(stat_key, trazas, 'pct_inicial', False) 
                    if trazas_ini1: bloque += f"{trazas_ini1}\n"
                    if trazas_ini2: bloque += f"{trazas_ini2}\n"
                    if not trazas_ini1 and not trazas_ini2: bloque += "      └─ (Sin bonos iniciales)\n"
                    else: bloque += f"      └─ Suma de Fase 1: +{extras_ini:g}\n"
                    
                    bloque += f"   [Fase 2] Pasivas, Cores y Soportes (Combate):\n"
                    trazas_comb1 = format_trazas(stat_key, trazas, 'plano_combate', False)
                    trazas_comb2 = format_trazas(stat_key, trazas, 'pct_combate', False)
                    if trazas_comb1: bloque += f"{trazas_comb1}\n"
                    if trazas_comb2: bloque += f"{trazas_comb2}\n"
                    if not trazas_comb1 and not trazas_comb2: bloque += "      └─ (Sin bonos de combate aplicables)\n"
                    else: bloque += f"      └─ Suma de Fase 2: +{extras_combate:g}\n"
                    
                    if bono_manual != 0: bloque += f"   Ajuste Manual: +{bono_manual:g}\n"
                    bloque += f"   >>> TOTAL FINAL EN COMBATE: {valor_final:.2f}\n"
                    desglose_texto += bloque
                    
        resultados["_desglose_texto"] = desglose_texto
        resultados.update(info_especial)

        # --- 7. BONOS CONDICIONALES DE HABILIDAD ---
        keywords_basic = ["basico"]
        keywords_dash_extra = ["dash"]
        keywords_ex = ["ex", "especial"]
        keywords_assist = ["asistencia"]
        keywords_ulti = ["definitiva"]

        es_basico = any(k in nombre_habilidad_norm for k in keywords_basic)
        es_dash = any(k in nombre_habilidad_norm for k in keywords_dash_extra)
        es_ex = any(k in nombre_habilidad_norm for k in keywords_ex)
        es_assist = any(k in nombre_habilidad_norm for k in keywords_assist)
        es_ulti = any(k in nombre_habilidad_norm for k in keywords_ulti)
        
        bono_dano_condicional = 0.0
        bono_stun_condicional = 0.0
        bono_crit_dmg_condicional = 0.0

        if es_basico: 
            bono_dano_condicional += resultados.get("Bono_Dano_Basico", 0.0)
            bono_stun_condicional += resultados.get("Bono_Stun_Basico", 0.0)
            bono_crit_dmg_condicional += resultados.get("Bono_Crit_DMG_Basico", 0.0)

        if es_dash:
            bono_dano_condicional += resultados.get("Bono_Dash", 0.0)
            bono_dano_condicional += resultados.get("Bono_Dano_Dash", 0.0)
            bono_stun_condicional += resultados.get("Bono_Stun_Dash", 0.0)

        if es_ex: 
            bono_dano_condicional += resultados.get("Bono_Dano_Ex", 0.0)
            bono_stun_condicional += resultados.get("Bono_Stun_Ex", 0.0)
            bono_crit_dmg_condicional += resultados.get("Bono_Crit_DMG_Ex", 0.0)

        if es_assist: 
            bono_dano_condicional += resultados.get("Bono_Dano_Assist", 0.0)
            bono_stun_condicional += resultados.get("Bono_Stun_Assist", 0.0)

        if es_ulti: 
            bono_dano_condicional += resultados.get("Bono_Dano_Ulti", 0.0)
            bono_stun_condicional += resultados.get("Bono_Stun_Ulti", 0.0)
            bono_crit_dmg_condicional += resultados.get("Bono_Crit_DMG_Ulti", 0.0)

        if bono_dano_condicional > 0:
            resultados["Daño_Adicional"] = resultados.get("Daño_Adicional", 0.0) + bono_dano_condicional

        if bono_stun_condicional > 0:
            stun_actual = resultados.get("Aturdimiento", 0.0)
            resultados["Aturdimiento"] = stun_actual * (1 + (bono_stun_condicional / 100.0))

        if bono_crit_dmg_condicional > 0:
            cd_actual = resultados.get("Daño_crítico", 0.0)
            resultados["Daño_crítico"] = cd_actual + bono_crit_dmg_condicional
        
        tipo_sucio = str(tipo_agente or "").lower()
        atk_total = resultados.get("Ataque", 0.0)
        sheer_val = atk_total * 0.3
        if "ruptura" in tipo_sucio:
            hp_total = resultados.get("Puntos_Vida", 0.0)
            sheer_val += (hp_total * 0.1)
        
        bono_core_sheer = sumas_planas_inicial.get("Sheer_force", 0.0) + sumas_planas_combate.get("Sheer_force", 0.0)
        resultados["Sheer_force"] = sheer_val + bono_core_sheer

        bonoja = resultados.get("Bono_Acumulación", 0.0)
        if bonoja > 0:
            base_anom = resultados.get("Tasa_de_Anomalía", 0.0)
            resultados["Tasa_de_Anomalía"] = base_anom * (1 + (bonoja / 100.0))

        return resultados
