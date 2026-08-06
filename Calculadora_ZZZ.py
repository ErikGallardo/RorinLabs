import flet as ft
import os
import logging
import sys
import json
import csv
from cargar_datos import CargadorDatos
from logica_danos import LogicaDmg
from Crear_Gui import CrearGui
import colorsys
from gestor_api import GestorApi
from gestor_ranking import GestorRanking
from traductor import Traductor, traductor_global as _traductor_global
from estado_build import EstadoBuild
from generador_imagenes import GeneradorTarjetas
from optimizador import OptimizadorBuild
from simulador_equipos import SimuladorEquipos
from gestor_estadisticas import GestorEstadisticas
from logica_recomendaciones import AnalistaBuild
from efectos_mindscapes import CONFIG_MINDSCAPES, MAPA_MINDSCAPES
from efectos_potencial import MAPA_POTENCIAL, CONFIG_POTENCIAL
from datos_enemigos_da import obtener_mapa_enemigos_da
from efectos_wengines import MAPA_WENGINES, CONFIG_WENGINES
from efectos_sets import MAPA_EFECTOS_SETS, CONFIG_SETS
from efectos_core import MAPA_CORE, CONFIG_CORE_UI
from efectos_pasivas import CONFIG_PASIVAS_UI
from efectos_soportes import MAPA_SOPORTES_AGENTES, MAPA_SOPORTES_SETS
from efectos_soportes import MAPA_SOPORTES_WENGINES
from substats_config import calcular_rolls_substat

logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CalculadoraZZZ:
    def __init__(self, page: ft.Page, cargador: CargadorDatos = None, logica_dmg: LogicaDmg = None):
        self.logger = logger
        self.page = page
        self.api_base_url = os.environ.get("API_BASE_URL", "http://localhost:8000")
        self.ruta_recursos, self.ruta_usuario = self.configurar_rutas()
        self.base_path = self.ruta_recursos 
        self.target_importacion = "main"
        self.datos_dir = os.path.join(self.base_path, 'datos')
        self.ruta_guardados = os.path.join(self.ruta_usuario, 'guardados')
        self.ruta_buffs_da = os.path.join(self.ruta_guardados, 'buffs')
        if not os.path.exists(self.ruta_buffs_da):
            os.makedirs(self.ruta_buffs_da)
        if not os.path.exists(self.ruta_guardados):
            os.makedirs(self.ruta_guardados)
        self.cargador = cargador or CargadorDatos(self.datos_dir)
        self.gestor_estadisticas = GestorEstadisticas(self.logger)
        self.gestor_stats = GestorEstadisticas()
        self.analista_recomendaciones = AnalistaBuild()
        self.gestor_api = GestorApi()
        self.logica_dmg = logica_dmg or LogicaDmg(logger=logger)
        self.simulador = SimuladorEquipos() 
        self.optimizador = OptimizadorBuild(
            self.gestor_estadisticas, 
            self.cargador, 
            self.logica_dmg
        )
        self.inicializar_ranking()
        self.gestor_ranking = GestorRanking(self.ruta_guardados)
        self.datos_api = GestorApi(self.logger)
        self.datos_importados_temp = {}
        self.estado_actual = EstadoBuild()
        self.agentes_data = [] 
        self.wengine_data = {}
        self.habilidades_agente = {}
        self.enemigos_data = []
        self.sets_data = []
        self.discos_data = {}
        self.tres_leches = False
        self.base_stats = {}
        self.elemento = None 
        self.tipo = None 
        self.faccion = None
        self.substats_db = []
        self.ultimos_stats_calculados = {}
        self.base_enemigo = {}
        self.meta_nombre_actual = None
        self.datos_comp_left = {}
        self.datos_comp_right = {}
        self.i18n = Traductor("en")
        self.optimizador.i18n = self.i18n
        self.gui = CrearGui(self, self.i18n)
        self.tabs_control = None
        self.gui.page = page
        self.build_ui()
        self.cargar_datos()

    def actualizar_color_tema(self, nombre_agente):
        """Actualiza el color primario y secundario del tema según el agente."""
        COLORES_AGENTES = {
            "Nicole": "#FF7CA4", "Anby": "#DCF921", "Billy": "#FF3B3B",
            "Nekomata": "#F6553B", "Koleda": "#FF7A1A", "Anton": "#FF7A1A",
            "Ben": "#F9951B", "Grace": "#FF7B4A", "Lycaon": "#C6E0E5",
            "Rina": "#E83445", "Ellen": "#FC3576", "Corin": "#C86BFF",
            "Zhu Yuan": "#33B5FF", "Qingyi": "#00F5BE", "Seth": "#6FA8FF",
            "Jane": "#FD3476", "Caesar": "#E6C76B", "Lighter": "#FF5A4F",
            "Lucy": "#F5B635", "Burnice": "#E6C76B", "Piper": "#FFBC01",
            "Pulchra": "#FFA94D", "Miyabi": "#1DC0C5", "Yanagi": "#FD7388",
            "Harumasa": "#FFCC00", "Soukaku": "#00E4FF", "Astra Yao": "#FF3A5A",
            "Evelyn": "#B69AE4", "Soldier 0 - Anby": "#FEBF25", "Hugo": "#FF3D57",
            "Vivian": "#9A7BFF", "Orphie & Magus": "#E72D50", "Trigger": "#FDC821",
            "Soldier 11": "#FFE34D", "Seed": "#FFD24D", "Yixuan": "#FFD966",
            "Ye Shunguang": "#FF6A3D", "Ju Fufu": "#FF9000", "Pan Yinhu": "#FDCB7A",
            "Yuzuha": "#F43638", "Alice": "#FDD07C", "Manato": "#FF4A3A",
            "Lucia": "#19CBE4", "Yidhari": "#B266FF", "Dialyn": "#6EFCEB",
            "Banyue": "#E8C98A", "Zhao": "#FF6993", "Sunna": "#D5FF63",
            "Aria": "#FE678A", "Nangong Yu": "#A872EB", "Cissia": "#EB348E", "Promeia": "#8449EF",
            "Starlight - Billy": "#C5454A"
        }
        color_default = "#C78FA8"
        
        nuevo_primary = COLORES_AGENTES.get(nombre_agente, color_default)

        # Guard: no renderizar si el color no cambió
        if getattr(self, '_ultimo_color_tema', None) == nuevo_primary:
            return
        self._ultimo_color_tema = nuevo_primary

        self.page.theme.color_scheme.primary = nuevo_primary

        OPCION_CIAN = "#03CCF0"
        OPCION_AMARILLO = "#F3D400"

        hex_primary = nuevo_primary.lstrip('#')
        r_p, g_p, b_p = tuple(int(hex_primary[i:i+2], 16) / 255.0 for i in (0, 2, 4))

        def calcular_distancia(hex_target):
            h_t = hex_target.lstrip('#')
            r_t, g_t, b_t = tuple(int(h_t[i:i+2], 16) / 255.0 for i in (0, 2, 4))
            return (r_p - r_t)**2 + (g_p - g_t)**2 + (b_p - b_t)**2

        distancia_cian = calcular_distancia(OPCION_CIAN)
        distancia_amarillo = calcular_distancia(OPCION_AMARILLO)

        if distancia_cian < distancia_amarillo:
            mejor_color_secundario = OPCION_AMARILLO
        else:
            mejor_color_secundario = OPCION_CIAN

        self.page.theme.color_scheme.secondary = mejor_color_secundario
        
        # ── MAGIA DINÁMICA DE LOS ORBES (SÓLO EL COLOR DEL AGENTE) ──
        if hasattr(self, 'orbes_dinamicos'):
            for orbe in self.orbes_dinamicos:
                orbe.shadow.color = ft.Colors.with_opacity(0.12, nuevo_primary)
        
        self.page.update()

    def _iniciar_deriva_orbes(self):
        import threading, random, math
        self._orbes_stop = threading.Event()

        def ease_in_out(t):
            return 0.5 - 0.5 * math.cos(math.pi * t)

        def loop_deriva():
            DURACION = 7.0
            PASO = 0.1
            pasos = int(DURACION / PASO)

            while not self._orbes_stop.is_set():
                # Calcular destinos nuevos
                destinos = []
                origenes = []
                for i, orbe in enumerate(self.orbes_dinamicos):
                    x_base, y_base, rx, ry = ORBES_CONFIG[i]
                    origenes.append((orbe.left, orbe.top))
                    destinos.append((x_base + random.uniform(-rx, rx),
                                     y_base + random.uniform(-ry, ry)))

                # Interpolar suavemente
                for step in range(1, pasos + 1):
                    if self._orbes_stop.is_set():
                        return
                    t = ease_in_out(step / pasos)
                    for i, orbe in enumerate(self.orbes_dinamicos):
                        ox, oy = origenes[i]
                        dx, dy = destinos[i]
                        orbe.left = ox + (dx - ox) * t
                        orbe.top = oy + (dy - oy) * t
                    try:
                        for orbe in self.orbes_dinamicos:
                            orbe.update()
                    except Exception:
                        return
                    self._orbes_stop.wait(PASO)

        threading.Thread(target=loop_deriva, daemon=True).start()

    def _detener_deriva_orbes(self):
        if hasattr(self, '_orbes_stop'):
            self._orbes_stop.set()

    def mostrar_mensaje(self, texto):
        """Muestra una notificación tipo SnackBar en la parte inferior."""
        self.page.overlay.append(
            ft.SnackBar(ft.Text(texto), open=True)
        )
        self.page.update()

    def _mostrar_loading(self, texto="Cargando..."):
        """Muestra un overlay semitransparente con spinner de carga."""
        self._loading_overlay = ft.Container(
            content=ft.Column([
                ft.ProgressRing(width=40, height=40, stroke_width=3, color="primary"),
                ft.Text(texto, size=14, weight="bold", color="white"),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=12,
               alignment=ft.MainAxisAlignment.CENTER),
            bgcolor=ft.Colors.with_opacity(0.7, "#000000"),
            expand=True,
            alignment=ft.alignment.center,
            border_radius=12,
        )
        self.page.overlay.append(self._loading_overlay)
        self.page.update()

    def _ocultar_loading(self):
        """Quita el overlay de carga."""
        if hasattr(self, '_loading_overlay') and self._loading_overlay in self.page.overlay:
            self.page.overlay.remove(self._loading_overlay)
            self.page.update()

    def configurar_rutas(self):
        """Determina las rutas de recursos e usuario.
        En la VM web: los guardados van a /home/ubuntu/calculadora/guardados (fijo).
        En exe empaquetado: usa la carpeta del ejecutable.
        En desarrollo local: usa la carpeta del script."""
        if getattr(sys, 'frozen', False):
            ruta_interna = sys._MEIPASS
            ruta_externa = os.path.dirname(sys.executable)
        else:
            ruta_interna = os.path.dirname(os.path.abspath(__file__))
            # En la VM el script está en /home/ubuntu/calculadora/
            # Usamos esa ruta fija para que los guardados sean compartidos entre sesiones.
            vm_guardados = '/home/ubuntu/calculadora'
            ruta_externa = vm_guardados if os.path.isdir(vm_guardados) else ruta_interna

        return ruta_interna, ruta_externa

    def build_ui(self):
        # ── 1. Construimos TODAS las pestañas para que no falte ningún control ──
        self.tabs_control = ft.Tabs(
            tabs=[
                ft.Tab(text=self.i18n.t("ui.tabs.dps", default="DPS"), content=self.gui.create_character_tab()),
                ft.Tab(text=self.i18n.t("ui.tabs.equipo", default="Agentes en tu equipo"), content=self.gui.create_buffs_tab()),
                ft.Tab(text=self.i18n.t("ui.tabs.buffs_da", default="Buffs de DA"), content=self.gui.create_da_buffs_tab()),
                ft.Tab(text=self.i18n.t("ui.tabs.comparador", default="Comparar Builds"), content=self.gui.create_comparator_tab()),
                ft.Tab(text=self.i18n.t("ui.tabs.recomendaciones", default="Recomendaciones"), content=self.gui.create_recommendations_tab()),
                ft.Tab(text=self.i18n.t("ui.tabs.Mejoras", default="Guía de mejoras"), content=self.gui.create_improvement_guide_tab()),
                ft.Tab(text=self.i18n.t("ui.tabs.Ranking", default="Ranking Global"), content=self.gui.create_ranking_tab()),
                ft.Tab(text=self.i18n.t("ui.tabs.graficas", default="Gráficas"), content=self.gui.create_graph_tab()),
                ft.Tab(text="Info", content=self.gui.create_info_tab()),
            ], expand=True, on_change=self._on_tab_change
        )

        # ── 2. Generamos el fondo texturizado premium ──
        fondo_dinamico, self.orbes_dinamicos, self.fondo_base_dinamico = aplicar_fondo_archive_textured(self.page)
        self._iniciar_deriva_orbes()
        self.page.on_close = lambda _: self._detener_deriva_orbes()

        # ── 3. Contenedor de la app con el padding ajustado ──
        contenido_app = ft.Container(
            content=self.tabs_control,
            padding=ft.padding.only(top=10, left=15, right=15, bottom=15),
            expand=True,
        )
        
        # ── 4. Agregamos todo al Stack principal de la página ──
        self.page.add(
            ft.Stack([
                fondo_dinamico, # Capa 0: Fondo texturizado
                contenido_app   # Capa 1: Toda tu calculadora encima
            ], expand=True)
        )

        # ── 5. Configuraciones finales (ahora sí existen los controles) ──
        self.configurar_eventos()
        self.i18n.on_cambio(self._aplicar_cambio_idioma)

    def _on_tab_change(self, e):
        """Lazy load: carga contenido pesado de pestañas solo al seleccionarlas."""
        idx = self.tabs_control.selected_index
        # Ranking es la pestaña índice 6
        if idx == 6 and not getattr(self.gui, '_ranking_tab_loaded', False):
            self.gui._cargar_lista_agentes_ranking()
            self.gui._ranking_tab_loaded = True
            self.gui.ranking_lista_agentes.update()

    def _aplicar_cambio_idioma(self):
        """Reconstruye todas las pestañas con el nuevo idioma y restaura
        el estado completo: agente, wengine, discos, substats, equipo,
        enemigo, DA buffs y paneles del comparador.
        """
        import copy
        try:
            # Sincronizar traductor_global para módulos que lo importan directamente
            _traductor_global.cargar_idioma(self.i18n.idioma_actual)
            self._mostrar_loading(self.i18n.t("ui_dinamico.cambiando_idioma", default="Cambiando idioma..."))
            # ── 0. SNAPSHOT completo antes de tocar nada ─────────────────────
            snapshot = self.obtener_estado_actual_dict()

            snapshot["_enemigo"]         = getattr(self.gui, "enemy_dropdown", None) and self.gui.enemy_dropdown.value or "Ninguno"
            snapshot["_estado_enemigo"]  = getattr(self.gui, "dd_estado_enemigo", None) and self.gui.dd_estado_enemigo.value or "Normal"
            snapshot["_miasma"]          = getattr(self.gui, "dd_miasma", None) and self.gui.dd_miasma.value or "Desactivado"
            snapshot["_da_custom_buffs"] = copy.deepcopy(getattr(self.gui, "da_custom_buffs", {}))
            snapshot["_comp_left"]       = copy.deepcopy(self.datos_comp_left)
            snapshot["_comp_right"]      = copy.deepcopy(self.datos_comp_right)
            snapshot["_meta_nombre"]     = getattr(self, "meta_nombre_actual", None)

            claves_soporte = [
                f"{p}_{campo}"
                for p in ("sup1", "sup2")
                for campo in (
                    "agente", "wengine", "set4",
                    "wengine_ref", "wengine_stacks", "set_stacks",
                    "mindscape", "mindscape_stacks", "mindscape_cond",
                    "stat_atk", "stat_hp", "stat_crit_rate", "stat_crit_dmg",
                    "stat_pen", "stat_am", "stat_er", "stat_imp", "stat_def",
                    "tipo", "elemento", "faccion",
                )
            ]
            snapshot["_soportes"] = {
                k: self.gui.team_controls[k].value
                for k in claves_soporte
                if k in self.gui.team_controls
                and hasattr(self.gui.team_controls[k], "value")
            }
            for p in ("sup1", "sup2"):
                txt_key = f"{p}_txt_busqueda"
                if txt_key in self.gui.team_controls:
                    snapshot[f"_{txt_key}"] = self.gui.team_controls[txt_key].value or ""

            # ── 1. RECONSTRUIR pestañas ───────────────────────────────────────
            tabs_def = [
                ("ui.tabs.dps",             self.gui.create_character_tab),
                ("ui.tabs.equipo",          self.gui.create_buffs_tab),
                ("ui.tabs.buffs_da",        self.gui.create_da_buffs_tab),
                ("ui.tabs.comparador",      self.gui.create_comparator_tab),
                ("ui.tabs.recomendaciones", self.gui.create_recommendations_tab),
                ("ui.tabs.Mejoras",         self.gui.create_improvement_guide_tab),
                ("ui.tabs.Ranking",          self.gui.create_ranking_tab),
                ("ui.tabs.graficas",        self.gui.create_graph_tab),
            ]
            for i, (key, builder) in enumerate(tabs_def):
                # Para la pestaña de mejoras, no traducir (es hardcoded)
                if key == "Guía de mejoras":
                    self.tabs_control.tabs[i].text = key
                else:
                    self.tabs_control.tabs[i].text = self.i18n.t(key)
                self.tabs_control.tabs[i].content = builder()

            # ── 2. RECONECTAR eventos ─────────────────────────────────────────
            self.configurar_eventos()

            # ── 3. REPOBLAR dropdowns con datos + traducciones nuevas ─────────
            if self.agentes_data:
                self._reconstruyendo_idioma = True
                self.actualizar_controles_con_datos()
                self._reconstruyendo_idioma = False

            # ── 4. MONTAR en página (obligatorio antes de cualquier .update()) ─
            self.page.update()

            # ── 5. RESTAURAR build principal ──────────────────────────────────
            self.meta_nombre_actual = snapshot.get("_meta_nombre")
            self._cargar_formato_interno(snapshot)

            # ── 5b. RECARGAR combos del agente activo con el nuevo idioma ────────
            nombre_agente_actual = getattr(self.estado_actual, "nombre_agente", None)
            if nombre_agente_actual and nombre_agente_actual not in ("Ninguno", ""):
                self.cargar_habilidades_agente(nombre_agente_actual)
                self.actualizar_habilidad_ui()

            # ── 6. RESTAURAR enemigo ──────────────────────────────────────────
            enemigo_guardado = snapshot.get("_enemigo", "Ninguno")
            if enemigo_guardado and enemigo_guardado != "Ninguno":
                self.gui.enemy_dropdown.value = enemigo_guardado
            self.cargar_enemigo(enemigo_guardado or "Ninguno")
            if hasattr(self.gui, "dd_estado_enemigo"):
                self.gui.dd_estado_enemigo.value = snapshot.get("_estado_enemigo", "Normal")
            if hasattr(self.gui, "dd_miasma"):
                self.gui.dd_miasma.value = snapshot.get("_miasma", "Desactivado")

            # ── 7. RESTAURAR estado completo de los soportes ─────────────────
            for k, v in snapshot.get("_soportes", {}).items():
                if k in self.gui.team_controls:
                    self.gui.team_controls[k].value = v
            for p in ("sup1", "sup2"):
                txt_key = f"{p}_txt_busqueda"
                saved_txt = snapshot.get(f"_{txt_key}", "")
                if txt_key in self.gui.team_controls and saved_txt:
                    self.gui.team_controls[txt_key].value = saved_txt
            # Imágenes de agente y wengine de cada soporte
            for p in ("sup1", "sup2"):
                agente_val  = snapshot.get("_soportes", {}).get(f"{p}_agente",  "Ninguno")
                wengine_val = snapshot.get("_soportes", {}).get(f"{p}_wengine", "Ninguno")
                self.gui.actualizar_imagen_team(p, "agente",  agente_val)
                self.gui.actualizar_imagen_team(p, "wengine", wengine_val)
                self._disparar_actualizacion_wengine_soporte(p, wengine_val)
            self.recalcular_stats_finales()

            # ── 8. RESTAURAR DA buffs ─────────────────────────────────────────
            if hasattr(self.gui, "da_custom_buffs"):
                self.gui.da_custom_buffs = snapshot.get("_da_custom_buffs", {})
                if hasattr(self.gui, "refrescar_interfaz_da_local"):
                    self.gui.refrescar_interfaz_da_local()

            # ── 9. RESTAURAR paneles del comparador ───────────────────────────
            self.datos_comp_left  = snapshot.get("_comp_left",  {})
            self.datos_comp_right = snapshot.get("_comp_right", {})
            if self.datos_comp_left:
                self.gui.renderizar_panel_comparacion("left",  self.datos_comp_left)
            if self.datos_comp_right:
                self.gui.renderizar_panel_comparacion("right", self.datos_comp_right)

            # ── 10. RE-RENDERIZAR ranking (los datos viven en self.ranking_builds) ─
            if getattr(self, "ranking_builds", None):
                self.gui.renderizar_ranking_ui()

            # ── 11. BOTONES de idioma ──────────────────────────
            if hasattr(self.gui, "actualizar_botones_idioma"):
                self.gui.actualizar_botones_idioma(self.i18n.idioma_actual)
            
            # ── 12. RESTAURAR BOTONES DE UID (PERSONAJES IMPORTADOS) ──
            if hasattr(self, '_stored_personajes') and self._stored_personajes:
                nickname_guardado = getattr(self, '_stored_nickname', 'Desconocido')
                self.mostrar_personajes_como_botones(self._stored_personajes, nickname_guardado)

            self.page.update()
            self._ocultar_loading()

        except Exception as ex:
            self._ocultar_loading()
            import traceback
            traceback.print_exc()
    
    def configurar_eventos(self):
        def cambiar_agente_main(e):
            nuevo_agente = e.control.value
            
            if nuevo_agente != "Ninguno":
                sup1 = self.gui.team_controls["sup1_agente"]
                sup2 = self.gui.team_controls["sup2_agente"]
                
                if sup1.value == nuevo_agente:
                    self.mostrar_mensaje(self.i18n.t("ui_dinamico.movido_a_principal", default=f"{nuevo_agente} movido a Principal. Slot 1 vaciado.", agente=nuevo_agente, num=1))
                    sup1.value = "Ninguno"
                    if hasattr(sup1, "on_change"): sup1.on_change(ft.ControlEvent(target=sup1.uid, name="change", data="Ninguno", control=sup1, page=self.page))
                    sup1.update()

                if sup2.value == nuevo_agente:
                    self.mostrar_mensaje(self.i18n.t("ui_dinamico.movido_a_principal", default=f"{nuevo_agente} movido a Principal. Slot 2 vaciado.", agente=nuevo_agente, num=2))
                    sup2.value = "Ninguno"
                    if hasattr(sup2, "on_change"): sup2.on_change(ft.ControlEvent(target=sup2.uid, name="change", data="Ninguno", control=sup2, page=self.page))
                    sup2.update()

            self.cargar_agente(nuevo_agente)
            self.actualizar_dropdown_abloom()
        self.gui.agent_dropdown.on_change = cambiar_agente_main
        self.gui.wengine_dropdown.on_change = lambda e: self.cargar_wengine(e.control.value)
        self.gui.stacks_dropdown.on_change = self.cambiar_stacks
        self.gui.set_stacks_dropdown.on_change = self.cambiar_set_stacks
        self.gui.set_checkbox.on_change = self.cambiar_set_condicion
        self.gui.habilidad_dropdown.on_change = self.manejador_habilidad
        self.gui.enemy_dropdown.on_change = lambda e: self.cargar_enemigo(e.control.value)
        self.gui.dd_estado_enemigo.on_change = self.calcular_dano
        self.gui.mindscape_dropdown.on_change = self.cambiar_mindscape
        self.gui.mindscape_stacks_dropdown.on_change = self.cambiar_mindscape_stacks
        self.gui.mindscape_cond_dropdown.on_change = self.cambiar_mindscape_cond
        self.gui.core_checkbox.on_change = self.cambiar_core_activo
        self.gui.chk_filtro_wengine.on_change = self.cambiar_filtro_wengines
        for field in self.gui.entry_vars.values():
            if hasattr(field, 'data') and field.data:
                field.on_submit = self.manejar_edicion_stat
        if hasattr(self.gui, 'dd_estado_enemigo'):
            self.gui.dd_estado_enemigo.on_change = self.calcular_dano
        if hasattr(self.gui, 'dd_miasma'):
            self.gui.dd_miasma.on_change = lambda e: self.recalcular_stats_finales()
        if hasattr(self.gui, 'dd_elemento_abloom'):
            self.gui.dd_elemento_abloom.on_change = self.calcular_dano
        self.configurar_eventos_soporte("sup1")
        self.configurar_eventos_soporte("sup2")

        for i in range(1, 7):
            if f"disco_{i}_set" in self.gui.team_controls:
                self.gui.team_controls[f"disco_{i}_set"].on_change = lambda e, slot=i: self.gestionar_disco(slot, "set", valor=e.control.value)
                self.gui.team_controls[f"disco_{i}_main"].on_change = lambda e, slot=i: self.gestionar_disco(slot, "main", valor=e.control.value)
                
                for j in range(1, 5):
                    self.gui.team_controls[f"disco_{i}_sub_{j}_stat"].on_change = lambda e, slot=i, sub=j: self.gestionar_disco(slot, "sub_stat", sub, valor=e.control.value)
                    
                    self.gui.team_controls[f"disco_{i}_sub_{j}_btn_plus"].on_click = lambda e, slot=i, sub=j: self.gestionar_disco(slot, "roll_plus", sub)
                    self.gui.team_controls[f"disco_{i}_sub_{j}_btn_minus"].on_click = lambda e, slot=i, sub=j: self.gestionar_disco(slot, "roll_minus", sub)

    def configurar_eventos_soporte(self, prefijo):
        """
        Lógica inteligente para Soportes:
        """

        def on_change_agente(e):
            nombre_agente = e.control.value
            if nombre_agente != "Ninguno":
                main_agente = self.gui.agent_dropdown.value
                otro_prefijo = "sup2" if prefijo == "sup1" else "sup1"
                otro_soporte = self.gui.team_controls.get(f"{otro_prefijo}_agente").value
                es_duplicado = False
                mensaje_error = ""
                if nombre_agente == main_agente:
                    es_duplicado = True
                    mensaje_error = self.i18n.t("ui_dinamico.agente_es_dps", default=f"¡{nombre_agente} ya es tu DPS Principal!", agente=nombre_agente)
                elif nombre_agente == otro_soporte:
                    es_duplicado = True
                    mensaje_error = self.i18n.t("ui_dinamico.agente_en_otro_slot", default=f"¡{nombre_agente} ya está seleccionado en el otro slot!", agente=nombre_agente)
                if es_duplicado:
                    self.mostrar_mensaje(mensaje_error)
                    e.control.value = "Ninguno"
                    e.control.update()
                    nombre_agente = "Ninguno"

            dd_wengine = self.gui.team_controls.get(f"{prefijo}_wengine")
            dd_set = self.gui.team_controls.get(f"{prefijo}_set4")
            txt_tipo = self.gui.team_controls.get(f"{prefijo}_tipo")
            txt_elemento = self.gui.team_controls.get(f"{prefijo}_elemento")
            txt_faccion = self.gui.team_controls.get(f"{prefijo}_faccion")
            self.gui.actualizar_imagen_team(prefijo, "agente", nombre_agente)

            if nombre_agente == "Ninguno":
                todas_armas = list(self.wengine_data.keys())
                todas_armas.sort()
                
                if dd_wengine:
                    dd_wengine.options = [ft.dropdown.Option("Ninguno")] + [ft.dropdown.Option(w) for w in todas_armas]
                    dd_wengine.value = "Ninguno"
                    self.gui.actualizar_imagen_team(prefijo, "wengine", "Ninguno")
                
                if dd_set: dd_set.value = "Ninguno"
                img_set_ctrl = self.gui.team_controls.get(f"{prefijo}_img_set")
                if img_set_ctrl: img_set_ctrl.src = "images/discos/default.png"; img_set_ctrl.opacity = 0.3
                if txt_tipo: txt_tipo.src = "images/elementos/default.png"; txt_tipo.opacity = 0.3; txt_tipo.tooltip = ""
                if txt_elemento: txt_elemento.src = "images/elementos/default.png"; txt_elemento.opacity = 0.3; txt_elemento.tooltip = ""
                if txt_faccion: txt_faccion.src = "images/faccion/default.png"; txt_faccion.opacity = 0.3; txt_faccion.tooltip = ""

                dd_ms = self.gui.team_controls.get(f"{prefijo}_mindscape_stacks")
                if dd_ms:
                    dd_ms.visible = False
                    if dd_ms.page: dd_ms.update()
                
                self.recalcular_stats_finales()
                self.actualizar_dropdown_abloom()
                self.gui.page.update()
                return

            agente_data = next((a for a in self.agentes_data if a['Nombre'] == nombre_agente), None)
            
            if agente_data:
                if txt_tipo:
                    tipo_raw = agente_data.get("Tipo", "")
                    tipo_norm = tipo_raw.lower().replace("é","e").replace("í","i").replace("ó","o")
                    txt_tipo.src = f"images/elementos/{tipo_norm}.png"
                    txt_tipo.opacity = 1.0
                    txt_tipo.tooltip = tipo_raw
                if txt_elemento:
                    elem_raw = agente_data.get("Elemento", "") or agente_data.get("elemento", "")
                    elem_norm = elem_raw.lower().replace("é","e").replace("í","i").replace("ó","o").replace("á","a").replace("ú","u")
                    txt_elemento.src = f"images/elementos/{elem_norm}.png"
                    txt_elemento.opacity = 1.0
                    txt_elemento.tooltip = elem_raw
                if txt_faccion:
                    facc_raw = agente_data.get("Faccion", "") or agente_data.get("Facción", "")
                    facc_norm = facc_raw.lower().replace("á","a").replace("é","e").replace("í","i").replace("ó","o").replace("ú","u").replace("ñ","n")
                    txt_faccion.src = f"images/faccion/{facc_norm}.png"
                    txt_faccion.opacity = 1.0
                    txt_faccion.tooltip = facc_raw

                if dd_wengine:
                    tipo_agente = agente_data.get("Tipo", "")
                    tipo_agente_norm = self.gestor_stats._normalizar(tipo_agente)
                    
                    armas_filtradas = []
                    for w_nombre, w_datos in self.wengine_data.items():
                        w_tipo = w_datos.get('tipow', '')
                        if self.gestor_stats._normalizar(w_tipo) == tipo_agente_norm:
                            armas_filtradas.append(w_nombre)
                    armas_filtradas.sort()
                    dd_wengine.options = [ft.dropdown.Option("Ninguno")] + [ft.dropdown.Option(w) for w in armas_filtradas]

                    arma_firma = "Ninguno"
                    for w_nombre, w_datos in self.wengine_data.items():
                        if w_datos.get('agente') == nombre_agente:
                            arma_firma = w_nombre
                            break
                    
                    dd_wengine.value = arma_firma if arma_firma in armas_filtradas else "Ninguno"
                    self.gui.actualizar_imagen_team(prefijo, "wengine", dd_wengine.value)
                    self._disparar_actualizacion_wengine_soporte(prefijo, dd_wengine.value)

                if dd_set:
                    set_rec = agente_data.get("Conjunto 4 piezas") or agente_data.get("Set 4pc")
                    existe_set = any(s['Nombre'] == set_rec for s in self.sets_data) if set_rec else False
                    dd_set.value = set_rec if existe_set else "Ninguno"

                dd_ms = self.gui.team_controls.get(f"{prefijo}_mindscape_stacks")
                if dd_ms:
                    cfg_m = CONFIG_MINDSCAPES.get(nombre_agente)
                    m_level = 0
                    try:
                        dd_mind = self.gui.team_controls.get(f"{prefijo}_mindscape")
                        m_level = int(dd_mind.value) if dd_mind else 0
                    except: pass

                    mostrar = False
                    if cfg_m:
                        req = cfg_m.get("min_mindscape", 0)
                        cumple = (m_level in req) if isinstance(req, list) else (m_level >= req)
                        if cumple:
                            max_s = cfg_m.get("max_stacks", 0)
                            if isinstance(max_s, dict):
                                max_s = max(v for k, v in max_s.items() if m_level >= k) if any(m_level >= k for k in max_s) else 0
                            if max_s > 0:
                                dd_ms.options = [ft.dropdown.Option(str(i)) for i in range(int(max_s) + 1)]
                                dd_ms.value = "0"
                                dd_ms.label = self.i18n.t(cfg_m.get("nombre_stack_key", ""), default=cfg_m.get("nombre_stack", "Stacks"))
                                mostrar = True
                    dd_ms.visible = mostrar
                    if dd_ms.page: dd_ms.update()
            
            self.recalcular_stats_finales()
            self.actualizar_dropdown_abloom()
            self.gui.page.update()
        
        CONFIG_SOPORTE_WENGINES_STACKS = {
            "kaboom the cannon": 4,
            "bashful demon": 4,
            "metanukimorphosis": 2,
            "elegant vanity": 2,
            "thoughtbop": 2,
            "blazing laurel": 20,
            "ice-jade teapot": 30,
            "roaring fur-nace": 2,
            "spectral gaze": 3,
            "yesterday calls": 3,
            "neon fantasies": 2,
        }

        def actualizar_stacks_wengine_soporte(nombre_wengine):
            dd  = self.gui.team_controls.get(f"{prefijo}_wengine_stacks")
            chk = self.gui.team_controls.get(f"{prefijo}_wengine_activo")
            if not dd:
                return
            nombre_norm = nombre_wengine.lower().strip() if nombre_wengine else ""
            max_s = CONFIG_SOPORTE_WENGINES_STACKS.get(nombre_norm, 0)

            tiene_wengine = bool(nombre_wengine and nombre_wengine != "Ninguno")

            if not tiene_wengine:
                dd.visible = False
                if chk: chk.visible = False
            elif max_s > 0:
                dd.options = [ft.dropdown.Option(str(i)) for i in range(max_s + 1)]
                dd.value = str(max_s)
                dd.visible = True
                if chk: chk.visible = False
            else:
                dd.options = [ft.dropdown.Option("0")]
                dd.value = "0"
                dd.visible = False
                if chk:
                    chk.value = True
                    chk.visible = True

            if dd.page:   dd.update()
            if chk and chk.page: chk.update()

        def on_change_wengine(e):
            nombre = e.control.value
            
            if nombre != "Ninguno":
                otro_prefijo = "sup2" if prefijo == "sup1" else "sup1"
                otro_wengine_ctrl = self.gui.team_controls.get(f"{otro_prefijo}_wengine")
                
                if otro_wengine_ctrl and otro_wengine_ctrl.value == nombre:
                    self.mostrar_mensaje(self.i18n.t("ui_dinamico.wengine_duplicado", default=f"¡Ese W-Engine ya lo usa el Soporte {otro_prefijo[-1]}!", num=otro_prefijo[-1]))
                    e.control.value = "Ninguno"
                    nombre = "Ninguno"
                    e.control.update()

            actualizar_stacks_wengine_soporte(nombre)
            self.gui.actualizar_imagen_team(prefijo, "wengine", nombre)
            self.recalcular_stats_finales()

        def on_change_arma_stats(e):
            self.recalcular_stats_finales()

        chk_activo = self.gui.team_controls.get(f"{prefijo}_wengine_activo")
        if chk_activo:
            chk_activo.on_change = on_change_arma_stats

        CONFIG_SOPORTE_SETS_STACKS = {
            "voz astral":          {"max": 3, "default": 3},
            "monarca":             {"max": 2, "default": 2},
            "pináculo":            {"max": 2, "default": 2},
            "pinaculo":            {"max": 2, "default": 2},
            "conejo":              {"max": 3, "default": 3},
            "wonderland":         {"max": 3, "default": 3},
        }

        def actualizar_stacks_set_soporte(nombre_set):
            dd = self.gui.team_controls.get(f"{prefijo}_set_stacks")
            if not dd:
                return
            import unicodedata
            def norm(s):
                s = s.lower().strip()
                return ''.join(c for c in unicodedata.normalize('NFD', s)
                               if unicodedata.category(c) != 'Mn')
            nombre_norm = norm(nombre_set) if nombre_set else ""
            cfg = None
            for k, v in CONFIG_SOPORTE_SETS_STACKS.items():
                if norm(k) in nombre_norm:
                    cfg = v
                    break
            if cfg:
                dd.options = [ft.dropdown.Option(str(i)) for i in range(cfg["max"] + 1)]
                dd.value = str(cfg["default"])
                dd.visible = True
            else:
                dd.options = [ft.dropdown.Option("0")]
                dd.value = "0"
                dd.visible = False
            if dd.page:
                dd.update()

        def on_change_set(e):
            nombre = e.control.value

            # Update set image
            img_set_ctrl = self.gui.team_controls.get(f"{prefijo}_img_set")
            if img_set_ctrl:
                if nombre and nombre != "Ninguno":
                    img_set_ctrl.src = f"images/discos/{nombre}.png"
                    img_set_ctrl.opacity = 1.0
                else:
                    img_set_ctrl.src = "images/discos/default.png"
                    img_set_ctrl.opacity = 0.3
                if img_set_ctrl.page: img_set_ctrl.update()

            if nombre != "Ninguno":
                otro_prefijo = "sup2" if prefijo == "sup1" else "sup1"
                otro_set_ctrl = self.gui.team_controls.get(f"{otro_prefijo}_set4")
                
                if otro_set_ctrl and otro_set_ctrl.value == nombre:
                    self.mostrar_mensaje(self.i18n.t("ui_dinamico.set_duplicado", default=f"¡El Set '{nombre}' ya lo usa el Soporte {otro_prefijo[-1]}!", nombre=nombre, num=otro_prefijo[-1]))
                    e.control.value = "Ninguno"
                    e.control.update()
                    if img_set_ctrl: img_set_ctrl.src = "images/discos/default.png"; img_set_ctrl.opacity = 0.3; img_set_ctrl.update()
                    actualizar_stacks_set_soporte("Ninguno")
                    self.recalcular_stats_finales()
                    return

            actualizar_stacks_set_soporte(nombre)
            self.recalcular_stats_finales()

        if f"{prefijo}_set4" in self.gui.team_controls:
                self.gui.team_controls[f"{prefijo}_set4"].on_change = on_change_set
        keys_stats = ["atk", "hp", "crit_rate", "crit_dmg", "er", "am", "pen", "ap", "imp", "def"]

        for key in keys_stats:
                nombre_control = f"{prefijo}_stat_{key}"
                campo = self.gui.team_controls.get(nombre_control)
                
                if campo:
                    campo.on_change = lambda e: self.recalcular_stats_finales()

        def on_change_mindscape_soporte(e):
            """Al cambiar mindscape del soporte, reconfigura el dropdown de stacks."""
            dd_ms = self.gui.team_controls.get(f"{prefijo}_mindscape_stacks")
            nombre_agente_sup = self.gui.team_controls.get(f"{prefijo}_agente", ft.Dropdown()).value
            if dd_ms and nombre_agente_sup and nombre_agente_sup != "Ninguno":
                try: m_level = int(e.control.value)
                except: m_level = 0
                cfg_m = CONFIG_MINDSCAPES.get(nombre_agente_sup)
                mostrar = False
                if cfg_m:
                    req = cfg_m.get("min_mindscape", 0)
                    cumple = (m_level in req) if isinstance(req, list) else (m_level >= req)
                    if cumple:
                        max_s = cfg_m.get("max_stacks", 0)
                        if isinstance(max_s, dict):
                            max_s = max((v for k, v in max_s.items() if m_level >= k), default=0)
                        if max_s > 0:
                            dd_ms.options = [ft.dropdown.Option(str(i)) for i in range(int(max_s) + 1)]
                            dd_ms.value = "0"
                            dd_ms.label = self.i18n.t(cfg_m.get("nombre_stack_key", ""), default=cfg_m.get("nombre_stack", "Stacks"))
                            mostrar = True
                dd_ms.visible = mostrar
                if dd_ms.page: dd_ms.update()
            self.recalcular_stats_finales()

        if f"{prefijo}_mindscape" in self.gui.team_controls:
            self.gui.team_controls[f"{prefijo}_mindscape"].on_change = on_change_mindscape_soporte
            
        if f"{prefijo}_mindscape_stacks" in self.gui.team_controls:
            self.gui.team_controls[f"{prefijo}_mindscape_stacks"].on_change = lambda e: self.recalcular_stats_finales()
            
        if f"{prefijo}_mindscape_cond" in self.gui.team_controls:
            self.gui.team_controls[f"{prefijo}_mindscape_cond"].on_change = lambda e: self.recalcular_stats_finales()

        if f"{prefijo}_wengine" in self.gui.team_controls:
            self.gui.team_controls[f"{prefijo}_wengine"].on_change = on_change_wengine

        if f"{prefijo}_wengine_ref" in self.gui.team_controls:
            self.gui.team_controls[f"{prefijo}_wengine_ref"].on_change = on_change_arma_stats
        
        if f"{prefijo}_wengine_stacks" in self.gui.team_controls:
            self.gui.team_controls[f"{prefijo}_wengine_stacks"].on_change = on_change_arma_stats

        if f"{prefijo}_set_stacks" in self.gui.team_controls:
            self.gui.team_controls[f"{prefijo}_set_stacks"].on_change = lambda e: self.recalcular_stats_finales()
        
        if f"{prefijo}_agente" in self.gui.team_controls:
            self.gui.team_controls[f"{prefijo}_agente"].on_change = on_change_agente

        if f"{prefijo}_set4" in self.gui.team_controls:
            self.gui.team_controls[f"{prefijo}_set4"].on_change = on_change_set

    def traducir_stat_csv(self, nombre_stat):
        """Traduce los nombres crudos de los CSVs usando el diccionario global."""
        mapa_raw = {
            "Puntos_Vida": "puntos_vida", "Ataque": "ataque", "Defensa": "defensa",
            "Maestría_Anomalía": "maestria_anomalia", "Daño_crítico": "dano_crit",
            "Probabilidad_crítico": "prob_crit", "Tasa_de_Perforación": "perforacion",
            "Daño_elemental": "dano_elemental", "Impacto": "impacto",
            "Tasa_de_Anomalía": "tasa_anomalia", "Recuperación_energía": "rec_energia",
            "Perforación_Plana": "perf_plana", "Daño_Adicional": "bono_dmg",
            "Reduccion_DEF_enemigo": "red_def", "Bono_Acumulación": "bono_acumulacion",
            "Recarga_Energía": "rec_energia", "Bono_Dano_Basico": "dmg_basico",
            "Bono_Dano_Dash": "dmg_dash", "Bono_Dano_Ex": "dmg_ex",
            "Bono_Dano_Ulti": "dmg_ulti", "Bono_Dano_Assist": "dmg_assist",
            "Bono_Stun_Basico": "stun_basico", "Bono_Stun_Dash": "stun_dash",
            "Bono_Stun_Ex": "stun_ex", "Bono_Stun_Ulti": "stun_ulti",
            "Bono_Stun_Assist": "stun_assist", "Disorder_Extra_Mult": "disorder_mult",
            "Pen_Res_Fisico": "pen_res_fisico", "Pen_Res_Fuego": "pen_res_fuego",
            "Pen_Res_Hielo": "pen_res_hielo", "Pen_Res_Electrico": "pen_res_electrico",
            "Pen_Res_Etereo": "pen_res_etereo", "Pen_Res_Viento": "pen_res_viento",
            "Pen_Res_Global": "pen_res_global",
            "Valor_Escudo": "valor_escudo", "Aturdimiento": "aturdimiento",
            "Sheer_force": "fuerza_absoluta", "Stun_DMG_Multiplier": "mult_stun",
            "Unstun_DMG_Multiplier": "mult_unstun", "DMG_Taken": "dmg_recibido",
            "Ignorar_Defensa": "ignorar_def", "Bono_Daño_Anomalia": "bono_dano_anomalia",
            "Daño_Aftershock": "dmg_aftershock", "Aumento_Daño_Critico": "aumento_crit_dmg",
            
            "HP": "puntos_vida", "ATK": "ataque", "DEF": "defensa",
            "Percent HP": "puntos_vida", "Percent ATK": "ataque", "Percent DEF": "defensa",
            "CRIT Rate": "prob_crit", "CRIT DMG": "dano_crit",
            "PEN Ratio": "perforacion", "PEN": "perf_plana",
            "Anomaly Proficiency": "maestria_anomalia", "Anomaly Mastery": "tasa_anomalia",
            "Energy Regen": "rec_energia", "Impact": "impacto",
            "Physical DMG Bonus": "dano_elemental", "Fire DMG Bonus": "dano_elemental",
            "Ice DMG Bonus": "dano_elemental", "Electric DMG Bonus": "dano_elemental", 
            "Ether DMG Bonus": "dano_elemental", "Wind DMG Bonus": "dano_elemental"
        }
        
        clave_json = mapa_raw.get(nombre_stat)
        if clave_json:
            return self.i18n.t(f"stats.{clave_json}")
            
        return self.i18n.t(f"stats.{nombre_stat.lower().replace(' ', '_')}", default=nombre_stat.replace('_', ' '))

    def cargar_datos(self):
        try:
            self.agentes_data = self.cargador.cargar_csv('agentes.csv')
            self.wengine_data = self.cargador.cargar_wengine('wengine.csv')
            self.enemigos_data = self.cargador.cargar_csv('enemigos.csv')
            self.sets_data = self.cargador.cargar_csv('sets.csv')

            # Cargar pasivas en inglés
            self.pasivas_en = {}
            try:
                import csv as _csv
                with open(os.path.join(os.path.dirname(__file__), 'wengine_passives.csv'), 'r', encoding='utf-8-sig') as f:
                    for row in _csv.DictReader(f):
                        self.pasivas_en[row['nombre_arma'].strip()] = row['descripcion_pasiva'].strip()
            except Exception:
                pass

            raw_substats = self.cargador.cargar_csv('substat.csv')
            self.substats_db = []
            key_substat_real = 'substat'
            if raw_substats and len(raw_substats) > 0:
                keys = raw_substats[0].keys()
                key_substat_real = next((k for k in keys if "substat" in k.lower()), 'substat')

            for item in raw_substats:
                tipo = item.get('tipo', '').strip().lower()
                nombre_substat = item.get(key_substat_real, "Desconocido")
                unique_key = f"{nombre_substat}_{tipo}"
                
                self.substats_db.append({
                    'key_interna': nombre_substat, 
                    'tipo': tipo,                  
                    'valor': self._parse_valor(item.get('valor', 0)),
                    'unique_key': unique_key,      
                    'label': f"{nombre_substat} ({'%' if 'porcentual' in tipo else 'Flat'})"
                })
                
                if unique_key not in self.estado_actual.substats_counts:
                    self.estado_actual.substats_counts[unique_key] = 0

            raw_discos = self.cargador.cargar_csv('discos.csv')
            self.discos_data = {4: [], 5: [], 6: []}
            for disco in raw_discos:
                slot = int(disco.get('slot', 0))
                if slot in self.discos_data:
                    self.discos_data[slot].append(disco)

            self.actualizar_controles_con_datos()

        except Exception as e:
            logger.error(f"FALLO CRÍTICO EN CARGA DE DATOS: {e}", exc_info=True)

    def cargar_uids_guardados(self):
        """Lee los UIDs guardados desde disco (gestor_ranking)."""
        return self.gestor_ranking.cargar_uids_guardados()

    def guardar_uid_local(self, apodo, uid):
        """Guarda UID en disco y actualiza el ranking global."""
        self.gestor_ranking.guardar_uid_local(apodo, uid)
        datos_completos = self.gestor_ranking.obtener_datos_completos_uid(
            uid, self.gestor_api, self.agentes_data
        )
        if datos_completos:
            datos_completos['apodo'] = apodo
            self.gestor_ranking.actualizar_jugador_en_ranking(apodo, datos_completos)
        self._refrescar_ranking_ui()

    def eliminar_uid_local(self, apodo):
        """Elimina un UID del disco y del ranking global."""
        self.gestor_ranking.eliminar_uid_local(apodo)
        self.gestor_ranking.eliminar_jugador_del_ranking(apodo)

    def _refrescar_ranking_ui(self):
        """Refresca la lista lateral de agentes del tab Ranking Global tras añadir un UID."""
        try:
            if hasattr(self.gui, 'ranking_lista_agentes') and self.gui.ranking_lista_agentes:
                self.gui.ranking_lista_agentes.controls.clear()
                self.gui._cargar_lista_agentes_ranking()
                self.gui.ranking_lista_agentes.update()
        except Exception:
            pass

    def obtener_ranking_para_build_card(self, nombre_personaje=None):
        """Obtiene el ranking global para usar en build cards."""
        return self.gestor_ranking.obtener_ranking_variable()

    def abrir_dialogo_uid(self, e=None, target="main"):
        """
        Diálogo para introducir UID.
        La lista de guardados es estática (no flotante) para evitar conflictos blur/click en web.
        Al seleccionar uno, el número se pone en el campo. Al importar, se guarda automáticamente.
        """
        self.target_importacion = target

        nombres_amigables = {
            "main":  self.i18n.t("ui.dialogo_uid.pestana_principal", default="Pestaña Principal"),
            "left":  self.i18n.t("ui.dialogo_uid.build_a",           default="Build A (Izquierda)"),
            "right": self.i18n.t("ui.dialogo_uid.build_b",           default="Build B (Derecha)")
        }
        titulo_destino = nombres_amigables.get(target, target.capitalize())

        # El campo de texto se recrea fresco cada vez
        # 1. Campo de texto con filtrado en tiempo real
        self.campo_uid_input = ft.TextField(
            label=self.i18n.t("ui.dialogo_uid.label_input", default="UID de la cuenta"),
            hint_text="Ej: 13008800",
            width=270,
            keyboard_type=ft.KeyboardType.NUMBER,
            on_submit=self.ejecutar_busqueda_uid,
            on_change=lambda e: filtrar_lista(e.control.value),
            autofocus=True,
        )

        lista_guardados = ft.Column(spacing=2, scroll=ft.ScrollMode.AUTO)

        def filtrar_lista(texto_busqueda):
            """Filtra la lista de UIDs basada en lo que el usuario escribe."""
            texto_busqueda = texto_busqueda.strip()
            # Si el campo está vacío, pasamos None para mostrar todo
            construir_lista(filtro=texto_busqueda if texto_busqueda else None)
            lista_guardados.update()

        def construir_lista(filtro=None):
            lista_guardados.controls.clear()
            uids = self.cargar_uids_guardados()
            # Filtrar nicks que no empiecen con #
            nicks_base = {k: v for k, v in uids.items() if not k.startswith("#")}

            # 2. Lógica de filtrado
            nicks_filtrados = {}
            if filtro:
                f = filtro.lower()
                for nick, uid_val in nicks_base.items():
                    if f in str(uid_val) or f in nick.lower():
                        nicks_filtrados[nick] = uid_val
            else:
                nicks_filtrados = nicks_base

            if not nicks_filtrados:
                msg = "No hay coincidencias" if filtro else "Sin UIDs guardadas aún"
                lista_guardados.controls.append(
                    ft.Text(msg, size=11, color="outline", italic=True)
                )
            else:
                for nick, uid_val in nicks_filtrados.items():
                    # Capturamos el valor actual de uid_val y nick
                    def hacer_seleccionar(u=uid_val):
                        return lambda _: (
                            setattr(self.campo_uid_input, 'value', u),
                            self.campo_uid_input.update()
                        )

                    # 3. Estructura de la fila corregida
                    fila = ft.Container(
                        content=ft.Row([
                            # Información (Nick y UID)
                            ft.Column([
                                ft.Text(nick, size=13, weight="bold"),
                                ft.Text(uid_val, size=11, color="outline"),
                            ], spacing=0, expand=True),
                            # Botones de acción
                            ft.Row([
                                ft.IconButton(
                                    icon=ft.Icons.ARROW_CIRCLE_RIGHT,
                                    icon_color="primary",
                                    icon_size=20,
                                    tooltip="Usar esta UID",
                                    on_click=hacer_seleccionar(),
                                ),
                            ], spacing=0),
                        ], 
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER),
                        padding=ft.padding.symmetric(horizontal=8, vertical=4),
                        border_radius=6,
                        bgcolor=ft.Colors.with_opacity(0.05, "primary"),
                        ink=True,
                        on_click=hacer_seleccionar(),
                    )
                    lista_guardados.controls.append(fila)

        # Llamada inicial
        construir_lista()

        contenedor_guardados = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("Guardadas", size=12, weight="bold", color="outline"),
                    ft.Container(expand=True),
                ]),
                ft.Container(
                    content=lista_guardados,
                    height=130,
                    border=ft.border.all(1, ft.Colors.with_opacity(0.15, "outline")),
                    border_radius=6,
                    padding=4,
                ),
            ], spacing=4),
            padding=ft.padding.only(top=8),
        )

        dialogo_content = ft.Column([
            ft.Text("💡 Se guarda automáticamente al importar", size=11, color="outline", italic=True),
            self.campo_uid_input,
            contenedor_guardados,
        ], spacing=8, tight=True, width=300)
        
        dialogo_fresco = ft.AlertDialog(
            title=ft.Text(self.i18n.t("ui.dialogo_uid.importar_a",
                          default=f"Importar a {titulo_destino}", destino=titulo_destino)),
            content=dialogo_content,
            actions=[
                ft.TextButton(
                    self.i18n.t("ui.dialogo_uid.cancelar", default="Cancelar"),
                    # 2. Le decimos a la página que cierre ESTE diálogo en específico
                    on_click=lambda e: self.page.close(dialogo_fresco)
                ),
                ft.ElevatedButton(
                    self.i18n.t("ui.dialogo_uid.buscar", default="Buscar"),
                    on_click=self.ejecutar_busqueda_uid,
                    bgcolor="primary", color="background"
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        # 3. Lo guardamos en self por si ejecutar_busqueda_uid necesita cerrarlo
        self.dialogo_uid = dialogo_fresco 
        
        # 4. Lo abrimos directamente desde la variable fresca
        self.page.open(dialogo_fresco)

    def ejecutar_busqueda_uid(self, e):
        uid = self.campo_uid_input.value.strip()
        if not uid:
            self.mostrar_mensaje(self.i18n.t("ui.dialogo_uid.error_vacio", default="Por favor escribe un UID."))
            return

        self.page.close(self.dialogo_uid)
        self.mostrar_mensaje(self.i18n.t("ui.dialogo_uid.consultando", default=f"Consultando UID {uid}...", uid=uid))
        self.page.update()

        personajes, nickname, error = self.gestor_api.obtener_datos_uid(uid)

        if error != "OK":
            self.mostrar_mensaje(self.i18n.t("ui.dialogo_uid.error_consulta", default=f"Error: {error}", error=error))
            return

        if personajes:
            self.lista_personajes_temp = personajes
            self.temp_nickname_importado = nickname
            self.temp_uid_importado = uid

            # ── Auto-guardar UID con el nickname obtenido de la API ──────────
            # Se guarda tanto por nickname como por el número de UID.
            nick_limpio = str(nickname).strip() if nickname else ""
            if nick_limpio and nick_limpio not in ("Desconocido", "Unknown"):
                self._auto_guardar_uid(nick_limpio, uid)
            else:
                self._auto_guardar_uid(f"UID:{uid}", uid)

            self.mostrar_personajes_como_botones(personajes, nickname)
        else:
            self.mostrar_mensaje(self.i18n.t("ui.dialogo_uid.error_sin_personajes", default="UID válido pero sin personajes públicos."))

    def _auto_guardar_uid(self, nick: str, uid: str):
        """Guarda el UID y descarta cualquier nombre antiguo que tuviera este mismo número."""
        uids = self.gestor_ranking.cargar_uids_guardados()
        
        # DESCARTAR COINCIDENCIAS: Buscar si el UID ya existe con otro nombre y borrarlo
        nicks_duplicados = [n for n, u in uids.items() if str(u) == str(uid) and n != nick]
        
        for n_antiguo in nicks_duplicados:
            self.gestor_ranking.eliminar_uid_local(n_antiguo)
            logger.debug(f"[UID] Descartando coincidencia antigua: {n_antiguo}")

        # Guardar la entrada actual si es nueva o cambió el nombre
        if uids.get(nick) != uid:
            self.gestor_ranking.guardar_uid_local(nick, uid)
            logger.debug(f"[UID] Entrada actualizada: {nick} → {uid}")

    def mostrar_personajes_como_botones(self, personajes, nickname):
        """Muestra los personajes encontrados como botones rectangulares organizados horizontalmente, imagen izquierda y selección resaltada"""
        self._stored_personajes = personajes
        self._stored_nickname = nickname

        self.gui.contenedor_personajes_importados.controls.clear()
        
        fila_botones = ft.ResponsiveRow(
            columns=12,
            spacing=8,
            run_spacing=8,
            alignment=ft.MainAxisAlignment.START
        )
        
        if not hasattr(self, 'agente_seleccionado_idx'):
            self.agente_seleccionado_idx = None

        for i, p in enumerate(personajes):
            nombre = p.get("name", "Desconocido")
            nivel = p.get("level", "?")
            esta_seleccionado = (i == self.agente_seleccionado_idx)

            ruta_imagen_personaje = f"images/{nombre}.png"
            ruta_real = os.path.join(self.base_path, "assets", "images", f"{nombre}.png")

            if not os.path.exists(ruta_real):
                ruta_imagen_personaje = "images/default.png"
            
            def crear_handler_importar(indice):
                def handler(e):
                    self.importar_personaje_directo(indice)
                return handler
            
            boton_personaje = ft.Container(
                content=ft.Row([
                    ft.Container(
                        content=ft.Image(src=ruta_imagen_personaje, width=24, height=24, fit=ft.ImageFit.COVER, border_radius=12),
                        border=ft.border.all(1, "primary"),
                        border_radius=12,
                        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                    ),
                    ft.Column([
                        ft.Text(nombre, size=11, weight=ft.FontWeight.BOLD, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                        ft.Text(f"Nv. {nivel}", size=9, color="secondary")
                    ], alignment=ft.MainAxisAlignment.CENTER, spacing=0, expand=True),
                    
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                
                height=32,
                col=2,
                on_click=crear_handler_importar(i),
                tooltip=f"{nombre} (Nv. {nivel})",
                ink=True,
                border_radius=4,
                padding=ft.padding.only(left=8, right=4),
                border=ft.border.all(2, "primary") if esta_seleccionado else ft.border.all(1, "outline"),
                bgcolor="#2A2A2A" if esta_seleccionado else "surface" 
            )
            
            fila_botones.controls.append(boton_personaje)
            
        self.gui.contenedor_personajes_importados.controls.append(fila_botones)
        
        self.gui.contenedor_personajes_importados.visible = True
        self.gui.contenedor_personajes_wrapper.visible = True
        
        try:
            self.gui.contenedor_personajes_importados.update()
            self.gui.contenedor_personajes_wrapper.update()
        except Exception:
            pass
        
        self.mostrar_mensaje(f"{len(personajes)} personajes encontrados para {nickname}. Haz clic en uno para importar.")

    def _actualizar_estado_botones_uid(self):
        """Actualiza visualmente qué botón está seleccionado sin reconstruir todo."""
        if not self.gui.contenedor_personajes_importados.controls:
            return
            
        fila_botones = self.gui.contenedor_personajes_importados.controls[0]
        
        for i, boton in enumerate(fila_botones.controls):
            esta_seleccionado = (i == self.agente_seleccionado_idx)
            boton.border = ft.border.all(2, "primary") if esta_seleccionado else ft.border.all(1, "outline")
            boton.bgcolor = "#2A2A2A" if esta_seleccionado else "surface"
        
        fila_botones.update()

    def importar_personaje_directo(self, indice):
        """Importa el personaje seleccionado directamente sin diálogo adicional"""
        if not hasattr(self, 'lista_personajes_temp') or not self.lista_personajes_temp:
             self.mostrar_mensaje("Error: No hay personajes cargados.")
             return
        
        if indice < 0 or indice >= len(self.lista_personajes_temp):
             self.mostrar_mensaje("Error: Índice de personaje inválido.")
             return

        self.agente_seleccionado_idx = indice
        
        personaje_elegido = self.lista_personajes_temp[indice]
        
        nick_temp = getattr(self, "temp_nickname_importado", "Desconocido")
        uid_temp = getattr(self, "temp_uid_importado", "")
        personaje_elegido["nickname"] = nick_temp
        personaje_elegido["uid"] = uid_temp
        
        target = getattr(self, 'target_importacion', 'main')
        nombre_pers = personaje_elegido.get('name', 'Agente')
        
        if target == "main":
            self._mostrar_loading(self.i18n.t("ui_dinamico.importando_agente", default=f"Importando a {nombre_pers}...", agente=nombre_pers))
            self._cargar_formato_externo(personaje_elegido)
            
            if nick_temp and nick_temp != "Desconocido":
                self.meta_nombre_actual = nick_temp
            else:
                self.meta_nombre_actual = nombre_pers
                
            self._ocultar_loading()
            self.mostrar_mensaje(f"✅ {nombre_pers} importado correctamente a la pestaña principal!")
            
        elif target in ["left", "right"]:
            self.mostrar_mensaje(f"Visualizando a {nombre_pers}...")
            if target == "left":
                self.datos_comp_left = personaje_elegido
            else:
                self.datos_comp_right = personaje_elegido
            self.gui.renderizar_panel_comparacion(target, personaje_elegido)
            self.mostrar_mensaje(f"✅ {nombre_pers} importado al panel {target.upper()}!")
        
        self._actualizar_estado_botones_uid()

    def abrir_selector_personajes(self, nickname="Desconocido"):
        """ Abre un segundo diálogo para elegir qué personaje importar """
        opciones = []
        for i, p in enumerate(self.lista_personajes_temp):
            nombre = p.get("name", "Desconocido")
            nivel = p.get("level", "?")
            nv_str = self.i18n.t("ui.dialogo_uid.nv", default=f"Nv. {nivel}", nivel=nivel)
            texto = f"{nombre} ({nv_str})"
            opciones.append(ft.dropdown.Option(key=str(i), text=texto))

        self.dropdown_selector_uid = ft.Dropdown(
            label=self.i18n.t("ui.dialogo_uid.selecciona_agente", default="Selecciona Agente"),
            options=opciones,
            width=250,
            autofocus=True
        )
        
        if opciones:
            self.dropdown_selector_uid.value = "0"

        self.dialogo_selector = ft.AlertDialog(
            title=ft.Text(self.i18n.t("ui.dialogo_uid.jugador", default=f"Jugador: {nickname}", nickname=nickname)), 
            content=ft.Column([
                ft.Text(self.i18n.t("ui.dialogo_uid.personajes_encontrados", default="Personajes encontrados en el perfil:")),
                self.dropdown_selector_uid
            ], height=100, tight=True, alignment=ft.MainAxisAlignment.CENTER),
            actions=[
                ft.TextButton(self.i18n.t("ui.dialogo_uid.cancelar", default="Cancelar"), on_click=lambda e: self.page.close(self.dialogo_selector)),
                ft.ElevatedButton(self.i18n.t("ui.dialogo_uid.importar", default="IMPORTAR"), on_click=self.confirmar_seleccion_uid, bgcolor="primary", color="background")
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page.open(self.dialogo_selector)
        
    def actualizar_controles_con_datos(self):

        def op_ninguno():
            return ft.dropdown.Option(key="Ninguno", text=self.i18n.t("ui.comun.ninguno", default="Ninguno"))
            
        def crear_lista_sets():
            return [op_ninguno()] + [
                ft.dropdown.Option(key=s['Nombre'], text=self.i18n.t(f"sets.{s['Nombre']}", default=s['Nombre'])) for s in self.sets_data
            ]
            
        def crear_lista_substats():
            def formatear_substat(sub):

                base_str = self.traducir_stat_csv(sub['key_interna'])
                tipo = sub['tipo']
                key = sub['key_interna']
                
                if tipo == 'plano' and key in ['Ataque', 'Puntos_Vida', 'Defensa']:
                    if key == 'Ataque': return self.i18n.t("stats.ataque_plano", default="Ataque Plano")
                    if key == 'Puntos_Vida': return self.i18n.t("stats.vida_plana", default="Vida Plana")
                    if key == 'Defensa': return self.i18n.t("stats.defensa_plana", default="Defensa Plana")
                    
                if tipo == 'porcentual' and '%' not in base_str:
                    return f"{base_str} %"
                    
                return base_str

            return [op_ninguno()] + [
                ft.dropdown.Option(
                    key=sub['unique_key'], 
                    text=formatear_substat(sub)
                ) for sub in self.substats_db
            ]
        self.gui.agent_dropdown.options = [op_ninguno()] + [ft.dropdown.Option(a['Nombre']) for a in self.agentes_data]
        
        # 1. W-Engines
        self.gui.wengine_dropdown.options = [op_ninguno()] + [
            ft.dropdown.Option(key=w, text=self.i18n.t(f"wengines.{w}", default=w)) for w in self.wengine_data.keys()
        ]
        
        # 2. Enemigos
        if self.enemigos_data:
            self.gui.enemy_dropdown.options = [op_ninguno()] + [
                ft.dropdown.Option(key=e['Nombre'], text=self.i18n.t(f"enemigos.{e['Nombre']}", default=e['Nombre'])) for e in self.enemigos_data
            ]
            self.gui.enemy_dropdown.value = "Ninguno"
            if not getattr(self, '_reconstruyendo_idioma', False):
                self.cargar_enemigo("Ninguno")
            
        # 3. Soportes y Sets
        self.gui.team_controls["sup1_agente"].options = [op_ninguno()] + [ft.dropdown.Option(a['Nombre']) for a in self.agentes_data]
        self.gui.team_controls["sup2_agente"].options = [op_ninguno()] + [ft.dropdown.Option(a['Nombre']) for a in self.agentes_data]
        
        self.gui.team_controls["sup1_wengine"].options = [op_ninguno()] + [ft.dropdown.Option(key=w, text=self.i18n.t(f"wengines.{w}", default=w)) for w in self.wengine_data.keys()]
        self.gui.team_controls["sup2_wengine"].options = [op_ninguno()] + [ft.dropdown.Option(key=w, text=self.i18n.t(f"wengines.{w}", default=w)) for w in self.wengine_data.keys()]
        
        self.gui.team_controls["sup1_set4"].options = crear_lista_sets()
        self.gui.team_controls["sup2_set4"].options = crear_lista_sets()
        
        self.gui.team_controls["sup1_set4"].value = "Ninguno"
        self.gui.team_controls["sup2_set4"].value = "Ninguno"
        self.gui.team_controls["sup1_agente"].value = "Ninguno"
        self.gui.team_controls["sup2_agente"].value = "Ninguno"
        self.gui.team_controls["sup1_wengine"].value = "Ninguno"
        self.gui.team_controls["sup2_wengine"].value = "Ninguno"

        # 4. Discos y Substats
        for i in range(1, 7):
            if f"disco_{i}_set" in self.gui.team_controls:
                self.gui.team_controls[f"disco_{i}_set"].options = crear_lista_sets()
                
                if i in [4, 5, 6] and i in self.discos_data:
                    self.gui.team_controls[f"disco_{i}_main"].options = [op_ninguno()] + [
                        ft.dropdown.Option(
                            key=d['nombre'], 
                            text=self.traducir_stat_csv(d['nombre'])
                        ) for d in self.discos_data[i]
                    ]

                for j in range(1, 5):
                    self.gui.team_controls[f"disco_{i}_sub_{j}_stat"].options = crear_lista_substats()

        if not getattr(self, '_reconstruyendo_idioma', False):
            self.gui.actualizar_imagen_team("sup1", "agente", "Ninguno")
            self.gui.actualizar_imagen_team("sup2", "agente", "Ninguno")
            self.gui.actualizar_imagen_team("sup1", "wengine", "Ninguno")
            self.gui.actualizar_imagen_team("sup2", "wengine", "Ninguno")
            self.gui.page.update()

    def confirmar_seleccion_uid(self, e):
        """ Se ejecuta al dar click en IMPORTAR en el selector """
        idx_str = self.dropdown_selector_uid.value
        if not idx_str: return

        try:
            idx = int(idx_str)
            personaje_elegido = self.lista_personajes_temp[idx]

            nick_temp = getattr(self, "temp_nickname_importado", "Desconocido")
            uid_temp = getattr(self, "temp_uid_importado", "")
            personaje_elegido["nickname"] = nick_temp
            personaje_elegido["uid"] = uid_temp
            
            self.page.close(self.dialogo_selector)
            nombre_pers = personaje_elegido.get('name', 'Agente')
            
            if self.target_importacion == "main":
                self._mostrar_loading(self.i18n.t("ui_dinamico.importando_agente", default=f"Importando a {nombre_pers}...", agente=nombre_pers))
                self._cargar_formato_externo(personaje_elegido)
                
                if nick_temp and nick_temp != "Desconocido":
                    self.meta_nombre_actual = nick_temp
                else:
                    self.meta_nombre_actual = nombre_pers
                self._ocultar_loading()
            
            elif self.target_importacion in ["left", "right"]:
                self.mostrar_mensaje(self.i18n.t("ui_dinamico.visualizando_panel", default=f"Visualizando a {nombre_pers}...", agente=nombre_pers, lado=self.target_importacion))
                if self.target_importacion == "left":
                    self.datos_comp_left = personaje_elegido
                else:
                    self.datos_comp_right = personaje_elegido
                self.gui.renderizar_panel_comparacion(self.target_importacion, personaje_elegido)
            
            elif self.target_importacion == "mejoras":
                self.mostrar_mensaje("Analizando personajes...")
                from analizador_prioridades import AnalizadorPrioridades
                analizador = AnalizadorPrioridades(self.agentes_data)
                analisis = analizador.analizar_personajes_uid(self.lista_personajes_temp)
                self._mostrar_analisis_mejoras(analisis, nick_temp, uid_temp)
            
        except Exception as ex:
            self.mostrar_mensaje(self.i18n.t("ui_dinamico.error_carga_seleccion", default=f"Error: {ex}", error=ex))

    def _parse_valor(self, valor, es_porcentual=False):
        if valor is None: return 0.0
        try:
            val_str = str(valor).replace('%', '').replace(',', '.').strip()
            num = float(val_str) if val_str else 0.0
            return num / 100.0 if es_porcentual else num
        except (ValueError, TypeError):
            return 0.0

    def cargar_agente(self, nombre):
        """
        Carga toda la información del agente seleccionado:
        Stats base, Elemento, Habilidades, Arma firma y Configuración de UI (Stacks).
        """
        agente_anterior = self.estado_actual.nombre_agente
        if agente_anterior != nombre and hasattr(self.gui, '_cache_discos_json'):
            self.gui._cache_discos_json = None
        
        self.estado_actual.nombre_agente = nombre
        self.actualizar_color_tema(nombre)
        self.base_stats.clear()
        self.meta_nombre_actual = None
        self.estado_actual.mindscape = 0
        self.estado_actual.mindscape_stacks = 0
        
        if hasattr(self.gui, 'mindscape_dropdown'):
            self.gui.mindscape_dropdown.value = "0"
            self.gui.mindscape_dropdown.update()
        self.actualizar_visibilidad_stacks_agente()

        if nombre == "Ninguno":
            self.elemento = None
            self.tipo = None
            self.faccion = None
            self.habilidades_agente = {}
            self.estado_actual.nombre_habilidad = None
            self.gui.core_stacks_dropdown.visible = False
            self.gui.core_stacks_dropdown.update()
            self.gui.wengine_dropdown.value = "Ninguno"
            self.gui.wengine_dropdown.update()
            self.cargar_wengine("Ninguno")

            if hasattr(self.gui, 'contenedor_potencial') and self.gui.contenedor_potencial:
                self.gui.contenedor_potencial.visible = False
                self.estado_actual.nivel_potencial = 0
                self.gui.slider_potencial.value = 0
                self.gui.contenedor_potencial.update()

        else:
            agente = next((a for a in self.agentes_data if a['Nombre'] == nombre), None)
            
            if agente:
                mapeo = { 
                    'nivel': 'Nivel', 'ataque': 'Ataque', 'puntos de vida': 'Puntos_Vida', 
                    'defensa': 'Defensa', 'probabilidad': 'Probabilidad_crítico', 
                    'daño crítico': 'Daño_crítico', 'daño elemental': 'Daño_elemental', 
                    'Maestría de anomalía': 'Maestría_Anomalía', 'tasa de anomalía': 'Tasa_de_Anomalía', 
                    'Impacto': 'Impacto', 'Tasa de perforación': 'Tasa_de_Perforación', 
                    'Perforación plana': 'Perforación_Plana', 'Recuperación de energía': 'Recuperación_energía' 
                }
                for csv_header, stat_key in mapeo.items(): 
                    self.base_stats[stat_key] = self._parse_valor(agente.get(csv_header, "0"))
                
                self.elemento = agente.get("elemento")
                self.tipo = agente.get("Tipo")
                self.faccion = agente.get("Facción")
                self.gui.actualizar_campo_pen_res(self.elemento)

                self.cargar_habilidades_agente(nombre)
                if self.habilidades_agente: 
                    self.estado_actual.nombre_habilidad = list(self.habilidades_agente.keys())[0]
                
                self.actualizar_lista_wengines()
                arma_firma = None
                for w_nombre, w_datos in self.wengine_data.items():
                    if w_datos.get('agente') == nombre:
                        arma_firma = w_nombre
                        break
                
                if arma_firma:
                    self.gui.wengine_dropdown.value = arma_firma
                    self.cargar_wengine(arma_firma)

                config = CONFIG_CORE_UI.get(nombre, {})
                usa_stacks = config.get("usa_stacks", False)
                self.gui.core_stacks_dropdown.visible = usa_stacks
                
                if nombre in CONFIG_POTENCIAL:
                    self.gui.contenedor_potencial.visible = True
                    self.gui.slider_potencial.value = getattr(self.estado_actual, 'nivel_potencial', 0)
                    self.actualizar_texto_potencial()
                else:
                    self.gui.contenedor_potencial.visible = False
                    self.estado_actual.nivel_potencial = 0
                    self.gui.slider_potencial.value = 0
                self.gui.contenedor_potencial.update()

                if usa_stacks:
                    etiqueta_raw = config.get("label", "Stacks")
                    label_key = config.get("label_key")
                    etiqueta = self.i18n.t(label_key, default=etiqueta_raw) if label_key else etiqueta_raw
                    max_s = config.get("max_stacks", 6)
                    val_def = config.get("default", max_s)
                    usar_slider = (max_s > 10) 
                    
                    self.gui.configurar_input_core(
                        visible=True,
                        usa_slider=usar_slider,
                        label=etiqueta,
                        max_val=max_s,
                        val_def=val_def
                    )
                    
                    self.estado_actual.core_stacks = int(val_def)
                else:
                    self.gui.configurar_input_core(visible=False)
                
                self.gui.core_stacks_dropdown.update()

        self.gui.actualizar_imagen_agente(nombre)
        self.generar_controles_pasivas(nombre)
        self.actualizar_ui_completa()

        # ── Auto-recalcular recomendaciones al cambiar agente ──────────────
        # Se lanza como task async para esperar a que cargar_wengine termine
        if nombre and nombre != "Ninguno":
            async def _auto_recomm():
                import asyncio
                await asyncio.sleep(0.8)  # esperar que cargar_wengine actualice estado
                try:
                    if hasattr(self.gui, '_accion_generar_recomm'):
                        self.gui._accion_generar_recomm(None)
                except Exception:
                    pass
            self.page.run_task(_auto_recomm)

        # ── Auto-recalcular recomendaciones al cambiar agente ──────────────────
        if nombre and nombre != "Ninguno":
            try:
                if hasattr(self.gui, 'area_dinamica_recomm'):
                    # Reusar acción_generar si está expuesta, si no llamar directo
                    if hasattr(self.gui, '_accion_generar_recomm'):
                        self.gui._accion_generar_recomm(None)
                    else:
                        # Llamada directa a construir_interfaz vía area_dinamica
                        pass
            except Exception:
                pass

    def cambiar_mindscape(self, e):
        try:
            val = int(e.control.value)
            self.estado_actual.mindscape = val
            
            self.actualizar_visibilidad_stacks_agente()
            
            self.recalcular_stats_finales()
        except: pass

    def cambiar_mindscape_stacks(self, e):
        try:
            val = int(e.control.value)
            self.estado_actual.mindscape_stacks = val
            self.recalcular_stats_finales()
        except: pass

    def cambiar_mindscape_cond(self, e):
        self.estado_actual.mindscape_cond = e.control.value or ""
        self.recalcular_stats_finales()

    def actualizar_visibilidad_stacks_agente(self):
        nombre = self.estado_actual.nombre_agente
        m_level = self.estado_actual.mindscape
        
        config = CONFIG_MINDSCAPES.get(nombre)
        mostrar_stacks = False
        max_s = 0
        
        if config:
            req = config.get("min_mindscape", 0)
            
            cumple_requisito = False
            if isinstance(req, list):
                cumple_requisito = m_level in req 
            else:
                cumple_requisito = m_level >= req 

            if cumple_requisito:
                mostrar_stacks = True
                _ms_key = config.get("nombre_stack_key")
                self.gui.mindscape_stacks_dropdown.label = self.i18n.t(_ms_key, default=config.get("nombre_stack", "Stacks")) if _ms_key else config.get("nombre_stack", "Stacks")

                config_max = config.get("max_stacks", 1)
                
                if isinstance(config_max, dict):
                    limit_found = 0
                    for nivel_req, limite in sorted(config_max.items()):
                        if m_level >= nivel_req:
                            limit_found = limite
                    max_s = limit_found
                else:
                    max_s = int(config_max)

                self.gui.mindscape_stacks_dropdown.options = [
                    ft.dropdown.Option(str(i)) for i in range(max_s + 1)
                ]
                
                val_actual = int(self.gui.mindscape_stacks_dropdown.value or "0")
                if val_actual > max_s:
                    self.gui.mindscape_stacks_dropdown.value = "0"
                    self.estado_actual.mindscape_stacks = 0

        self.gui.mindscape_stacks_dropdown.visible = mostrar_stacks
        self.gui.mindscape_stacks_dropdown.update()

        # Condition dropdown
        opciones = config.get("opciones_condicion") if config else None
        if opciones and m_level >= (config.get("min_mindscape", 0) if not isinstance(config.get("min_mindscape", 0), list) else min(config.get("min_mindscape", [0]))):
            _trad_cond = {"Ninguno": self.i18n.t("misc.ninguno", default="Ninguno"),
                          "Todo activo": self.i18n.t("misc.todo_activo", default="Todo activo")}
            self.gui.mindscape_cond_dropdown.options = [
                ft.dropdown.Option(key=o, text=_trad_cond.get(o, o)) for o in opciones
            ]
            self.gui.mindscape_cond_dropdown.value = opciones[0]
            self.estado_actual.mindscape_cond = opciones[0]
            self.gui.mindscape_cond_dropdown.visible = True
        else:
            self.gui.mindscape_cond_dropdown.visible = False
            self.estado_actual.mindscape_cond = ""
        self.gui.mindscape_cond_dropdown.update()

    def cargar_enemigo(self, nombre):
        enemigo = next((e for e in self.enemigos_data if e.get('Nombre') == nombre), None)
        if nombre == "Ninguno":
            self.base_enemigo.clear()
            self.gui.actualizar_imagen_enemigo("Ninguno")
            keys_enemigo = [
                            'Defensa_Base', 'Resistencia_porcentual', 'Defensa_Plana', 
                            'Resistencia_Fuego', 'Resistencia_Electrico', 'Resistencia_Hielo', 
                            'Resistencia_Físico', 'Resistencia_Etereo', 'Resistencia_Viento'
                        ]
            for key in keys_enemigo:
                self.base_enemigo[key] = 0.0
                if key in self.gui.entry_vars:
                    self.gui.entry_vars[key].value = "0"
            self.page.update()
            return

        enemigo = next((e for e in self.enemigos_data if e.get('Nombre') == nombre), None)

        mapeo_enemigo = { 'Defensa_Base': 'Defensa base del enemigo', 'Resistencia_porcentual': 'Resistencia porcentual',
                        'Defensa_Plana': 'Defensa plana del enemigo', 'Resistencia_Fuego': 'Resistencia fuego',
                        'Resistencia_Electrico': 'Resistencia electrico', 'Resistencia_Hielo': 'Resistencia hielo',
                        'Resistencia_Físico': 'Resistencia físico', 'Resistencia_Etereo': 'Resistencia etereo',
                        'Resistencia_Viento': 'Resistencia viento' }
        for key_ui, key_csv in mapeo_enemigo.items():
            valor_base = self._parse_valor(enemigo.get(key_csv, '0'))
            self.base_enemigo[key_ui] = valor_base
            
            if key_ui in self.gui.entry_vars: 
                self.gui.entry_vars[key_ui].value = str(valor_base)

        if hasattr(self.gui, 'actualizar_panel_enemigo_da'):
            datos_da = obtener_mapa_enemigos_da().get(nombre)
            
            if datos_da:
                self.gui.actualizar_panel_enemigo_da(
                    nombre_enemigo=nombre,
                    ruta_imagen=datos_da["imagen"],
                    spans_descripcion=datos_da["spans"],
                    opciones_buffs=datos_da["opciones"]
                )
            else:
                ruta_default = f"/images/enemigos/{nombre.lower().replace(' ', '_')}.png"
                self.gui.actualizar_panel_enemigo_da(
                    nombre_enemigo=nombre,
                    ruta_imagen=ruta_default,
                    spans_descripcion=[ft.TextSpan(self.i18n.t("ui_dinamico.sin_efectos_enemigo", default="Sin efectos especiales dinámicos para este enemigo."), style=ft.TextStyle(color=ft.Colors.GREY_500, italic=True))],
                    opciones_buffs=[]
                )

        self.gui.actualizar_imagen_enemigo(nombre)
        self.recalcular_stats_finales()
        self.page.update()

    def cargar_wengine(self, nombre):
        self.estado_actual.nombre_wengine = nombre
        self.gui.actualizar_imagen_wengine(nombre)
        self.estado_actual.refinamiento = 1
        self.gui.refinamiento_dropdown.value = "1"
        self.gui.refinamiento_dropdown.update()

        datos_arma = self.wengine_data.get(nombre)
        if datos_arma:

            descripcion = datos_arma.get('pasiva')
            if self.i18n.idioma_actual != 'es' and hasattr(self, 'pasivas_en'):
                descripcion = self.pasivas_en.get(nombre, descripcion)
            
            # Mostrar descripción visible de la pasiva
            if descripcion and nombre != "Ninguno":
                self.gui.lbl_desc_wengine.value = f"⚙ {descripcion}"
                self.gui.contenedor_desc_wengine.visible = True
            else:
                self.gui.contenedor_desc_wengine.visible = False
            self.gui.contenedor_desc_wengine.update()
        else:
            self.gui.contenedor_desc_wengine.visible = False
            self.gui.contenedor_desc_wengine.update()

        nombre_limpio = nombre.strip()
        if nombre_limpio in CONFIG_WENGINES:
            config = CONFIG_WENGINES[nombre]
            max_stacks = config["max_stacks"]
            key_stack = config.get("nombre_stack_key")
            label = self.i18n.t(key_stack, default=config.get("nombre_stack", "Stacks")) if key_stack else config.get("nombre_stack", "Stacks")
            
            self.gui.stacks_dropdown.label = label
            self.gui.stacks_dropdown.options = [ft.dropdown.Option(str(i)) for i in range(0, max_stacks + 1)]
            
            self.gui.stacks_dropdown.value = "1"
            self.estado_actual.stacks = 1       
            self.gui.stacks_dropdown.visible = True

            self.gui.stacks_dropdown.update()
        else:
            self.estado_actual.stacks = 0
            self.gui.stacks_dropdown.visible = False
            self.gui.stacks_dropdown.update()
        self.page.update()
        self.recalcular_stats_finales()

    def actualizar_desc_wengine_bonos(self):
        """Actualiza la descripción visible del wengine mostrando los bonos actuales según R y stacks."""
        nombre = self.estado_actual.nombre_wengine
        if not nombre or nombre == "Ninguno" or nombre not in MAPA_WENGINES:
            return
        try:
            func_w = MAPA_WENGINES[nombre]
            try:
                bonos = func_w(stats_actuales={}, refinamiento=self.estado_actual.refinamiento, nombre_agente=self.estado_actual.nombre_agente, stacks=self.estado_actual.stacks, estado_enemigo="Normal", elemento_agente=self.elemento or "")
            except TypeError:
                bonos = func_w({}, self.estado_actual.refinamiento, self.estado_actual.nombre_agente, self.estado_actual.stacks)
            datos_arma = self.wengine_data.get(nombre)
            desc_base = datos_arma.get('pasiva', '') if datos_arma else ''
            if self.i18n.idioma_actual != 'es' and hasattr(self, 'pasivas_en'):
                desc_base = self.pasivas_en.get(nombre, desc_base)
            if bonos:
                textos = [f"{self.traducir_stat_csv(k)}: +{v:g}" for k, v in bonos.items() if v != 0]
                linea_bonos = f"  → R{self.estado_actual.refinamiento}"
                if self.estado_actual.stacks > 0:
                    linea_bonos += f" x{self.estado_actual.stacks} stacks"
                linea_bonos += f": {', '.join(textos)}" if textos else ""
                self.gui.lbl_desc_wengine.value = f"⚙ {desc_base}\n{linea_bonos}"
            else:
                self.gui.lbl_desc_wengine.value = f"⚙ {desc_base}"
            self.gui.contenedor_desc_wengine.visible = True
            if self.gui.contenedor_desc_wengine.page:
                self.gui.contenedor_desc_wengine.update()
        except Exception:
            pass

    def cambiar_stacks(self, e):
        try:
            val = int(e.control.value)
            self.estado_actual.stacks = val 
            self.actualizar_desc_wengine_bonos()
            self.recalcular_stats_finales()
        except Exception as ex:
            import traceback
            traceback.print_exc()
            self.mostrar_mensaje(f"Error en stacks: {ex}")

    def cambiar_set_condicion(self, e):
        self.estado_actual.set_condicion = e.control.value
        
        self.recalcular_stats_finales()

    def cambiar_set_stacks(self, e):
        try:
            val = int(e.control.value)
            self.estado_actual.set_stacks = val
            self.recalcular_stats_finales()
        except:
            pass
        
    def aplicar_set(self, nombre, slot):
        
        if nombre != "Ninguno":
            sets_actuales = self.estado_actual.sets
            
            for otro_slot, otro_nombre in sets_actuales.items():
                if otro_slot != slot and otro_nombre == nombre:
                    
                    self.mostrar_mensaje(self.i18n.t('ui_dinamico.set_ya_equipado', default=f"El set '{nombre}' ya está equipado en otro slot.", nombre=nombre))
                    
                    if slot == 'set1': self.gui.set1_dropdown.value = "Ninguno"
                    elif slot == 'set2': self.gui.set2_dropdown.value = "Ninguno"
                    elif slot == 'set3': self.gui.set3_dropdown.value = "Ninguno"
                    
                    self.page.update()
                    return 
        
        self.estado_actual.sets[slot] = nombre
        nombre_set1 = self.estado_actual.sets.get('set1', "").strip()
        
        self.gui.set_checkbox.visible = False
        self.gui.set_checkbox.value = False
        self.estado_actual.set_condicion = False
        
        self.gui.set_stacks_dropdown.visible = False
        self.estado_actual.set_stacks = 0

        if nombre_set1 in CONFIG_SETS:
            config = CONFIG_SETS[nombre_set1]
            
            if config.get("usa_condicion", False):
                self.gui.set_checkbox.label = config.get("texto_condicion", "¿Activo?")
                self.gui.set_checkbox.visible = True
                self.gui.set_checkbox.value = False 
                self.gui.set_checkbox.update()

            max_stacks = config.get("max_stacks", 0)
            if max_stacks > 0:
                _sk = config.get("nombre_stack_key")
                self.gui.set_stacks_dropdown.label = self.i18n.t(_sk, default=config.get("nombre_stack", "Stacks")) if _sk else config.get("nombre_stack", "Stacks")
                self.gui.set_stacks_dropdown.options = [ft.dropdown.Option(str(i)) for i in range(1, max_stacks + 1)]
                
                self.gui.set_stacks_dropdown.visible = True
                self.gui.set_stacks_dropdown.value = "1"
                self.estado_actual.set_stacks = 1
                self.gui.set_stacks_dropdown.update()
        
        self.gui.set_checkbox.update()
        self.gui.set_stacks_dropdown.update()

        self.recalcular_stats_finales()

    def aplicar_disco(self, nombre, slot):
        self.estado_actual.discos[slot] = nombre
        self.recalcular_stats_finales()
        
    def manejador_habilidad(self, e):
        self.estado_actual.nombre_habilidad = e.control.value
        self.actualizar_habilidad_ui()

        self.recalcular_stats_finales()

    def manejar_edicion_stat(self, e):
        stat_key = e.control.data
        try:
            valor_usuario = float(e.control.value)

            keys_enemigo = [
                            'Defensa_Base', 'Resistencia_porcentual', 'Defensa_Plana', 
                            'Resistencia_Fuego', 'Resistencia_Electrico', 'Resistencia_Hielo', 
                            'Resistencia_Físico', 'Resistencia_Etereo', 'Resistencia_Viento'
                        ]
            
            if stat_key in keys_enemigo:
                self.base_enemigo[stat_key] = valor_usuario
            else:
                self.estado_actual.bonos_manuales_planos[stat_key] = 0
                self.recalcular_stats_finales()
                valor_calculado = float(self.gui.entry_vars[stat_key].value)
                self.estado_actual.bonos_manuales_planos[stat_key] = valor_usuario - valor_calculado
            
        except (ValueError, TypeError):
            pass
        
        self.recalcular_stats_finales()

    def _disparar_actualizacion_wengine_soporte(self, prefijo, nombre_wengine):
        """Fuerza la actualización del toggle/dropdown de stacks al cargar un soporte."""

        dd_w = self.gui.team_controls.get(f"{prefijo}_wengine")
        if dd_w and hasattr(dd_w, "on_change") and dd_w.on_change:
            class _FakeEvent:
                def __init__(self, ctrl): self.control = ctrl
            dd_w.value = nombre_wengine
            dd_w.on_change(_FakeEvent(dd_w))

    def recalcular_stats_finales(self):
        self.sincronizar_datos_legacy()
        keys_enemigo_ignorar = [
            'Defensa_Base', 'Resistencia_porcentual', 'Defensa_Plana', 
            'Resistencia_Fuego', 'Resistencia_Electrico', 'Resistencia_Hielo', 
            'Resistencia_Físico', 'Resistencia_Etereo', 'Reduccion_DEF_enemigo'
        ]
        
        if not self.base_stats:
            for key in self.gui.entry_vars:
                if key not in keys_enemigo_ignorar and key not in ["Multiplicador_de_ataques", "Aturdimiento"]:
                    self.gui.entry_vars[key].value = "0"
            self.page.update()
            return
        
        stats_para_calculo = self.base_stats.copy()
        lista_sets_externos = []
        buffs_acumulados_mindscapes = {}
        msgs_sup1 = [] 
        msgs_sup2 = []

        todos_los_efectos = []
        self.buffs_vivian_rescatados = {"Bono_Abloom_Final": 0.0, "Vivian_Prophecy_Tick": 0.0}

        nombre_set1 = self.estado_actual.sets.get('set1')
        if nombre_set1 and nombre_set1 != "Ninguno":
            todos_los_efectos.append(f"Set DPS: {nombre_set1}")

        nivel_potencial = getattr(self.estado_actual, 'nivel_potencial', 0)
        if nivel_potencial > 0 and self.estado_actual.nombre_agente in MAPA_POTENCIAL:
            funcion_potencial = MAPA_POTENCIAL[self.estado_actual.nombre_agente]
            bonos_pot = funcion_potencial(nivel_potencial)
                    
            if bonos_pot:
                textos_pot = []
                for k, v in bonos_pot.items():
                    stats_para_calculo[k] = stats_para_calculo.get(k, 0.0) + v
                    textos_pot.append(f"{self.traducir_stat_csv(k)}: +{v}")
                        
                todos_los_efectos.append(f"Potencial Nv.{nivel_potencial}: {', '.join(textos_pot)}")

        for prefijo in ["sup1", "sup2"]:
            nombre_set = self.gui.team_controls.get(f"{prefijo}_set4", ft.Dropdown()).value
            nombre_agente = self.gui.team_controls.get(f"{prefijo}_agente", ft.Dropdown()).value
            nombre_arma = self.gui.team_controls.get(f"{prefijo}_wengine", ft.Dropdown()).value

            try:ref_arma = int(self.gui.team_controls.get(f"{prefijo}_wengine_ref", ft.Dropdown()).value)
            except:ref_arma = 1
            try:stacks_arma = int(self.gui.team_controls.get(f"{prefijo}_wengine_stacks", ft.Dropdown()).value)
            except:stacks_arma = 0
            chk_act = self.gui.team_controls.get(f"{prefijo}_wengine_activo")
            if chk_act and chk_act.visible and chk_act.value == False:
                stacks_arma = -1
            try:stacks_set = int(self.gui.team_controls.get(f"{prefijo}_set_stacks", ft.Dropdown()).value)
            except:stacks_set = 0
            try: val_m = int(self.gui.team_controls.get(f"{prefijo}_mindscape", ft.Dropdown()).value)
            except: val_m = 0
            try: val_m_stacks = int(self.gui.team_controls.get(f"{prefijo}_mindscape_stacks", ft.Dropdown()).value)
            except: val_m_stacks = 0
            try: val_m_cond = self.gui.team_controls.get(f"{prefijo}_mindscape_cond", ft.Checkbox()).value
            except: val_m_cond = False

            if nombre_agente and nombre_agente != "Ninguno":
                datos_agente = next((a for a in self.agentes_data if a['Nombre'] == nombre_agente), None)
                tipo_agente_sup = datos_agente.get("Tipo", "") if datos_agente else ""
                elem_agente_sup = datos_agente.get("Elemento", "") or datos_agente.get("elemento", "") if datos_agente else ""
                facc_agente_sup = datos_agente.get("Faccion", "") or datos_agente.get("Facción", "") if datos_agente else ""

                stats_soporte = {
                    "Ataque": self._parse_valor(self.gui.team_controls.get(f"{prefijo}_stat_atk").value),
                    "Puntos_de_Vida": self._parse_valor(self.gui.team_controls.get(f"{prefijo}_stat_hp").value),
                    "Probabilidad_de_crítico": self._parse_valor(self.gui.team_controls.get(f"{prefijo}_stat_crit_rate").value),
                    "Daño_crítico": self._parse_valor(self.gui.team_controls.get(f"{prefijo}_stat_crit_dmg").value),
                    "Tasa_de_Perforación": self._parse_valor(self.gui.team_controls.get(f"{prefijo}_stat_pen").value),
                    "Tasa_de_Anomalía": self._parse_valor(self.gui.team_controls.get(f"{prefijo}_stat_am").value),
                    "Maestría_Anomalía": self._parse_valor(self.gui.team_controls.get(f"{prefijo}_stat_ap").value) if f"{prefijo}_stat_ap" in self.gui.team_controls else 0.0,
                    "Recuperación_energía": self._parse_valor(self.gui.team_controls.get(f"{prefijo}_stat_er").value),
                    "Impacto": self._parse_valor(self.gui.team_controls.get(f"{prefijo}_stat_imp").value)
                }

                lista_sets_externos.append({
                    "origen": prefijo,
                    "nombre_set": nombre_set,
                    "nombre_agente": nombre_agente,
                    "tipo_agente": tipo_agente_sup,
                    "elemento_agente": elem_agente_sup,
                    "faccion_agente": facc_agente_sup,
                    "nombre_arma": nombre_arma,
                    "refinamiento_arma": ref_arma,
                    "stacks_arma": stacks_arma,
                    "stacks_set": stacks_set,
                    "stats": stats_soporte,
                    "mindscape": val_m
                })

                if nombre_agente in MAPA_MINDSCAPES:
                    funcion_mindscape = MAPA_MINDSCAPES[nombre_agente]
                    bonos_soporte = funcion_mindscape(mindscape=val_m, stacks=val_m_stacks, condicion_activa=val_m_cond, nombre_habilidad="")
                    
                    if bonos_soporte:
                        _STAT_I18N_KEYS = {
                            'Probabilidad_crítico': 'stats.prob_crit',
                            'Daño_crítico': 'stats.dano_crit',
                            'Ataque_porcentual': 'stats.ataque',
                            'Ataque_plano': 'stats.ataque_plano',
                            'Daño_Adicional': 'stats.bono_dmg',
                            'Tasa_de_Anomalía': 'stats.tasa_anomalia',
                            'Maestría_Anomalía': 'stats.maestria_anomalia',
                            'Tasa_de_Perforación': 'stats.perforacion',
                            'Recuperación_energía': 'stats.rec_energia',
                            'Impacto': 'stats.impacto',
                            'Defensa_porcentual': 'stats.defensa',
                            'Puntos_Vida_porcentual': 'stats.puntos_vida',
                            'Bono_Daño_Anomalia': 'stats.bono_dano_anomalia',
                            'Daño_Aftershock': 'stats.dmg_aftershock',
                            'Aumento_Daño_Critico': 'stats.aumento_crit_dmg',
                            'Pen_Res_Fisico': 'stats.pen_res_fisico',
                            'Pen_Res_Fuego': 'stats.pen_res_fuego',
                            'Pen_Res_Hielo': 'stats.pen_res_hielo',
                            'Pen_Res_Electrico': 'stats.pen_res_electrico',
                            'Pen_Res_Etereo': 'stats.pen_res_etereo',
                            'Pen_Res_Viento': 'stats.pen_res_viento',
                        }
                        _ELEMENTOS = ['Fisico', 'Fuego', 'Hielo', 'Electrico', 'Etereo', 'Viento']
                        _elem_dps = str(self.elemento).capitalize() if self.elemento else ''
                        bonos_soporte = {
                            k: v for k, v in bonos_soporte.items()
                            if not any(k == f'Pen_Res_{el}' for el in _ELEMENTOS)
                            or k == f'Pen_Res_{_elem_dps}'
                        }
                        desc_bonos = ", ".join([f"{self.i18n.t(_STAT_I18N_KEYS.get(k, ''), default=k.replace('_', ' '))}: +{v}" for k, v in bonos_soporte.items()])
                        mensaje = f"{nombre_agente} (M{val_m}): {desc_bonos}"
                        
                        if prefijo == "sup1":
                            msgs_sup1.append(mensaje)
                        else:
                            msgs_sup2.append(mensaje)

                        for stat_key, valor in bonos_soporte.items():
                            buffs_acumulados_mindscapes[stat_key] = buffs_acumulados_mindscapes.get(stat_key, 0.0) + valor

        if hasattr(self.gui, 'lbl_resumen_buffs'):

            for info in lista_sets_externos:
                n_agente_raw = info['nombre_agente']
                n_set_raw = info['nombre_set']
                t_agente_raw = info['tipo_agente']
                stats_del_soporte = info.get('stats', {}) 

                n_agente_norm = self.gestor_stats._normalizar(n_agente_raw)
                n_set_norm = self.gestor_stats._normalizar(n_set_raw)
                
                origen = info.get("origen", "sup1")
                lista_destino = msgs_sup1 if origen == "sup1" else msgs_sup2

                dummy_res = {}

                for key_agente, funcion in MAPA_SOPORTES_AGENTES.items():
                    if key_agente in n_agente_norm:
                        roles_team = [str(self.tipo).lower()] if self.tipo else []
                        elems_team = [str(self.elemento).lower()] if self.elemento else []
                        facs_team = [str(self.faccion).lower()] if self.faccion else []
                        nombres_team = [str(self.estado_actual.nombre_agente).lower()]
                        origen_actual = info.get("origen", "sup1") 
                        otro_prefijo = "sup2" if origen_actual == "sup1" else "sup1"
                        nombre_otro = self.gui.team_controls.get(f"{otro_prefijo}_agente", ft.Dropdown()).value

                        if nombre_otro and nombre_otro != "Ninguno":
                            datos_otro = next((a for a in self.agentes_data if a['Nombre'] == nombre_otro), None)
                            if datos_otro:
                                r_otro = datos_otro.get("Tipo", "").lower()
                                e_otro = (datos_otro.get("Elemento", "") or datos_otro.get("elemento", "")).lower()
                                f_otro = (datos_otro.get("Faccion", "") or datos_otro.get("Facción", "")).lower()

                                if r_otro: roles_team.append(r_otro)
                                if e_otro: elems_team.append(e_otro)
                                if f_otro: facs_team.append(f_otro)
                                nombres_team.append(str(nombre_otro).lower())

                        datos_equipo_ui = {
                            "roles": roles_team,
                            "elementos": elems_team,
                            "nombres": nombres_team,
                            "facciones": facs_team
                        }
                        elemento_actual = str(self.elemento).lower() if self.elemento else ""
                        texto = funcion(
                            dummy_res, 
                            tipo_agente=t_agente_raw, 
                            stats=stats_del_soporte,
                            datos_equipo=datos_equipo_ui,
                            elemento_dps=elemento_actual,
                            mindscape=info.get("mindscape", 0)
                        )
                        if texto: lista_destino.append(texto)
                        break

                if "Bono_Abloom_Final" in dummy_res:
                    self.buffs_vivian_rescatados["Bono_Abloom_Final"] += dummy_res["Bono_Abloom_Final"]
                if "Vivian_Prophecy_Tick" in dummy_res:
                    self.buffs_vivian_rescatados["Vivian_Prophecy_Tick"] += dummy_res["Vivian_Prophecy_Tick"]

                for key_set, funcion in MAPA_SOPORTES_SETS.items():
                    if key_set in n_set_norm:
                        stacks_set_actual = info.get("stacks_set", 0)
                        texto = funcion(dummy_res, tipo_agente=t_agente_raw, stats=stats_del_soporte, stacks_set=stacks_set_actual)
                        if texto: lista_destino.append(texto)
                        break
                
                raw_arma = info.get('nombre_arma', '')
                n_arma_norm = self.gestor_stats._normalizar(raw_arma)

                if info.get('stacks_arma', 0) != -1:
                    for key_w, funcion in MAPA_SOPORTES_WENGINES.items():
                        if key_w in n_arma_norm:
                            elemento_actual = str(self.elemento).lower() if self.elemento else ""
                            texto = funcion(
                                dummy_res,
                                refinamiento=info.get('refinamiento_arma', 1),
                                stacks=info.get('stacks_arma', 0),
                                elemento_dps=elemento_actual
                            )
                            if texto: lista_destino.append(texto)
                            break

            if hasattr(self.gui, 'lbl_resumen_buffs'):
                self.gui.lbl_resumen_buffs.value = ""
                self.gui.lbl_resumen_buffs.spans = [] 
                
                lista_spans = []

                def desaturar_color(color_hex, nueva_sat=0.25):
                    if not color_hex or not color_hex.startswith('#'):
                        return color_hex
                    
                    hex_c = color_hex.lstrip('#')
                    r, g, b = tuple(int(hex_c[i:i+2], 16) / 255.0 for i in (0, 2, 4))
                    h, l, s = colorsys.rgb_to_hls(r, g, b)
                    
                    r_n, g_n, b_n = colorsys.hls_to_rgb(h, l, nueva_sat)
                    return f"#{int(r_n * 255):02X}{int(g_n * 255):02X}{int(b_n * 255):02X}"

                primario_actual = self.page.theme.color_scheme.primary
                secundario_actual = self.page.theme.color_scheme.secondary
                
                primario_suave = desaturar_color(primario_actual, 0.25)
                secundario_suave = desaturar_color(secundario_actual, 0.25)

                if msgs_sup1:
                    lista_spans.append(ft.TextSpan(
                        self.i18n.t("ui.tab_equipo.soporte_1", default="SUPPORT 1:\n"),
                        style=ft.TextStyle(weight=ft.FontWeight.BOLD, color="primary")
                    ))
                    lista_spans.append(ft.TextSpan(
                        " | ".join(msgs_sup1),
                        style=ft.TextStyle(color=primario_suave)
                    ))

                if msgs_sup1 and msgs_sup2:
                    lista_spans.append(ft.TextSpan("\n\n"))

                if msgs_sup2:
                    lista_spans.append(ft.TextSpan(
                        self.i18n.t("ui.tab_equipo.soporte_2", default="SUPPORT 2:\n"),
                        style=ft.TextStyle(weight=ft.FontWeight.BOLD, color="secondary")
                    ))
                    lista_spans.append(ft.TextSpan(
                        " | ".join(msgs_sup2),
                        style=ft.TextStyle(color=secundario_suave)
                    ))

                if lista_spans:
                    self.gui.lbl_resumen_buffs.spans = lista_spans
                else:
                    self.gui.lbl_resumen_buffs.value = self.i18n.t("misc.sin_buffs_equipo", default="• Sin buffs de equipo activos.")
                    self.gui.lbl_resumen_buffs.color = ft.Colors.GREY_300
                
                self.gui.lbl_resumen_buffs.update()

        estado_actual_enemigo = "Normal"
        if hasattr(self.gui, 'dd_estado_enemigo') and self.gui.dd_estado_enemigo.value:
            estado_actual_enemigo = self.gui.dd_estado_enemigo.value

        if self.estado_actual.nombre_habilidad in self.habilidades_agente:
            info_habilidad = self.habilidades_agente[self.estado_actual.nombre_habilidad]
            stats_para_calculo['Aturdimiento'] = float(info_habilidad.get('Aturdimiento', 0.0))
            stats_para_calculo['Multiplicador_de_ataques'] = float(info_habilidad.get('Multiplicador', 0.0))
            stats_para_calculo['Etiqueta_Dano'] = info_habilidad.get('Etiqueta_Dano', 'normal')

        for k, v in buffs_acumulados_mindscapes.items():
            stats_para_calculo[k] = stats_para_calculo.get(k, 0.0) + v

        stacks_core_ui = int(self.gui.core_stacks_dropdown.value or 0)
        kwargs_pasivas = {}

        if hasattr(self.gui, 'controles_pasivas'):
            for key, control in self.gui.controles_pasivas.items():
                kwargs_pasivas[key] = control.value
        
        buffs_nodos_da = {}
        if hasattr(self.gui, 'da_active_buffs') and hasattr(self.gui, 'mapa_stats_da'):
            for stat_ui, valor in self.gui.da_active_buffs.items():
                clave_logica = self.gui.mapa_stats_da.get(stat_ui, stat_ui)
                buffs_nodos_da[clave_logica] = buffs_nodos_da.get(clave_logica, 0.0) + valor

        if msgs_sup1: todos_los_efectos.extend(msgs_sup1)
        if msgs_sup2: todos_los_efectos.extend(msgs_sup2)
        self.mensajes_efectos_actuales = todos_los_efectos
        self.stats_base_buffeadas = stats_para_calculo.copy()

        stats_calculadas = self.gestor_stats.calcular_stats_finales(
            base_stats=stats_para_calculo, 
            estado_build=self.estado_actual,
            wengine_db=self.wengine_data,
            sets_db=self.sets_data,
            discos_db=self.discos_data,
            substats_db=self.substats_db,
            elemento_agente=self.elemento,
            tipo_agente=self.tipo,
            stacks_core=stacks_core_ui,
            sets_externos=lista_sets_externos,
            estado_enemigo=estado_actual_enemigo,
            buffs_nodos=buffs_nodos_da,
            **kwargs_pasivas
        )

        stats_calculadas["Bono_Abloom_Final"] = stats_calculadas.get("Bono_Abloom_Final", 0.0) + self.buffs_vivian_rescatados.get("Bono_Abloom_Final", 0.0)
        stats_calculadas["Vivian_Prophecy_Tick"] = stats_calculadas.get("Vivian_Prophecy_Tick", 0.0) + self.buffs_vivian_rescatados.get("Vivian_Prophecy_Tick", 0.0)

        if hasattr(self.gui, 'campo_pen_res'):
            clave_pen_actual = self.gui.campo_pen_res.data
            pen_global = stats_calculadas.get("Pen_Res_Global", 0.0)
            stats_calculadas[clave_pen_actual] = stats_calculadas.get(clave_pen_actual, 0.0) + pen_global

        elementos_soportes = []
        for info in lista_sets_externos:
            if info.get('elemento_agente'):
                elementos_soportes.append(info['elemento_agente'])
        stats_calculadas["Elementos_Soportes"] = elementos_soportes

        self.ultimos_stats_calculados = stats_calculadas.copy()

        for stat_key, campo_ui in self.gui.entry_vars.items():
            if stat_key in keys_enemigo_ignorar:
                continue
            
            valor_final = stats_calculadas.get(stat_key, 0.0)
            
            valor_visual = valor_final
            if stat_key == "Daño_crítico" and valor_visual < 0:
                valor_visual = 0.0

            es_decimal = False
            label_lower = campo_ui.label.lower()
            if any(x in label_lower for x in ["%", "daño elem", "pen res", "aturdimiento", "rec."]):
                es_decimal = True
            
            campo_ui.value = f"{valor_visual:.2f}" if es_decimal else f"{valor_visual:.0f}"

        keys_enemigo_visual = [
            'Resistencia_Fuego', 'Resistencia_Electrico', 'Resistencia_Hielo', 
            'Resistencia_Físico', 'Resistencia_Etereo', 'Resistencia_porcentual',
            'Defensa_Base', 'Reduccion_DEF_enemigo' 
        ]

        for key in keys_enemigo_visual:
            if key in self.gui.entry_vars:

                base = self.base_enemigo.get(key, 0.0)
                cambio = stats_calculadas.get(key, 0.0)
                
                if key == 'Reduccion_DEF_enemigo':
                    ignorar = stats_calculadas.get('Ignorar_Defensa', 0.0)
                    ignorar_after = stats_calculadas.get('Ignorar_Defensa_Aftershock', 0.0)
                    valor_visual = cambio + ignorar + ignorar_after
                else:
                    valor_visual = base + cambio

                if key == 'Defensa_Base':
                     self.gui.entry_vars[key].value = f"{valor_visual:.0f}"
                else:
                     self.gui.entry_vars[key].value = f"{valor_visual:.2f}"
                
                es_debuff = (cambio != 0 and key != 'Defensa_Base') or (key == 'Reduccion_DEF_enemigo' and cambio > 0)
                if es_debuff:
                     self.gui.entry_vars[key].text_color = ft.Colors.RED_300
                else:
                     self.gui.entry_vars[key].text_color = ft.Colors.WHITE

        self.actualizar_panel_bonos()
        self.page.update()
        self.actualizar_colores_discos_ui()

    def gestionar_disco(self, slot: int, accion: str, sub_idx: int = 1, valor=None, e=None):
        """Maneja todos los eventos de los 6 discos individuales (Sets, Mains, Subs y Rolls)"""
        disco = self.estado_actual.discos_detalles[slot]
        
        if accion == "set":
            disco["set"] = valor
            self.actualizar_imagen_disco_ui(slot, valor)
        elif accion == "main":
            disco["main"] = valor
        elif accion == "sub_stat":
            disco["subs"][sub_idx]["stat"] = valor
            disco["subs"][sub_idx]["rolls"] = 0
            self.gui.team_controls[f"disco_{slot}_sub_{sub_idx}_rolls"].value = "0"
            self.gui.team_controls[f"disco_{slot}_sub_{sub_idx}_rolls"].update()
            
        elif accion in ["roll_plus", "roll_minus"]:
            stat_actual = disco["subs"][sub_idx]["stat"]
            if not stat_actual or stat_actual == "Ninguno":
                self.mostrar_mensaje(self.i18n.t("ui_dinamico.sub_stat_primero", default="¡Selecciona una sub-stat primero!"))
                return
                
            delta = 1 if accion == "roll_plus" else -1
            rolls_actuales = disco["subs"][sub_idx]["rolls"]
            total_rolls_disco = sum(s["rolls"] for s in disco["subs"].values())
            
            if delta > 0 and total_rolls_disco >= 5:
                self.mostrar_mensaje(self.i18n.t("ui_dinamico.disco_mejoras_max", default=f"¡El disco {slot} ya alcanzó sus 5 mejoras máximas!", slot=slot))
                return
            if delta < 0 and rolls_actuales <= 0:
                return
                
            disco["subs"][sub_idx]["rolls"] += delta
            self.gui.team_controls[f"disco_{slot}_sub_{sub_idx}_rolls"].value = str(disco["subs"][sub_idx]["rolls"])
            self.gui.team_controls[f"disco_{slot}_sub_{sub_idx}_rolls"].update()
            
        self.recalcular_stats_finales()

    def actualizar_imagen_disco_ui(self, slot: int, nombre_set: str):
        """Actualiza la imagen del disco basándose en el nombre del set."""
        img_ctrl = self.gui.team_controls.get(f"disco_{slot}_img")
        if not img_ctrl: return
        
        if nombre_set and nombre_set != "Ninguno":
            nombre_archivo = nombre_set.replace(":", "").replace("/", "_").strip()
            
            img_ctrl.src = f"/images/discos/{nombre_archivo}.png"
            img_ctrl.opacity = 1.0
        else:
            img_ctrl.src = "/images/discos/default.png"
            img_ctrl.opacity = 0.3
            
        if img_ctrl.page:
            img_ctrl.update()

    def sincronizar_datos_legacy(self):
        """
        Traduce los 6 discos individuales al formato global antiguo 
        para que las matemáticas (GestorEstadisticas) sigan funcionando intactas.
        """
        self.estado_actual.substats_counts.clear()
        conteo_sets = {}
        
        for slot, datos in self.estado_actual.discos_detalles.items():
            if slot in [4, 5, 6]:
                self.estado_actual.discos[slot] = datos["main"]
            
            nombre_set = datos["set"]
            if nombre_set and nombre_set != "Ninguno":
                conteo_sets[nombre_set] = conteo_sets.get(nombre_set, 0) + 1
                
            for sub_info in datos["subs"].values():
                stat = sub_info["stat"]
                mejoras = sub_info["rolls"]
                if stat and stat != "Ninguno":
                    self.estado_actual.substats_counts[stat] = self.estado_actual.substats_counts.get(stat, 0) + (1 + mejoras)

        self.estado_actual.sets = {'set1': "Ninguno", 'set2': "Ninguno", 'set3': "Ninguno"}
        sets_ordenados = sorted(conteo_sets.items(), key=lambda x: x[1], reverse=True)
        
        idx_set = 1
        for nombre, cant in sets_ordenados:
            if cant >= 4:
                self.estado_actual.sets['set1'] = nombre
                idx_set = 2
            elif cant >= 2:
                if idx_set <= 3:
                    self.estado_actual.sets[f'set{idx_set}'] = nombre
                    idx_set += 1


        nombre_set1 = self.estado_actual.sets.get('set1', "Ninguno")
        set_anterior = getattr(self, '_ultimo_set_4pc', "Ninguno")
        
        if set_anterior != nombre_set1:
            self.estado_actual.set_condicion = False
            self.gui.set_checkbox.value = False
            if nombre_set1 in CONFIG_SETS and CONFIG_SETS[nombre_set1].get("max_stacks", 0) > 0:
                self.estado_actual.set_stacks = 1
                self.gui.set_stacks_dropdown.value = "1"
            else:
                self.estado_actual.set_stacks = 0
                self.gui.set_stacks_dropdown.value = "0"
            self._ultimo_set_4pc = nombre_set1

        if nombre_set1 in CONFIG_SETS:
            config = CONFIG_SETS[nombre_set1]
            
            if config.get("usa_condicion", False):
                self.gui.set_checkbox.label = config.get("texto_condicion", f"Efecto 4x: {nombre_set1}")
                self.gui.set_checkbox.visible = True
            else:
                self.gui.set_checkbox.visible = False
                
            max_stacks = config.get("max_stacks", 0)
            if max_stacks > 0:
                _sk2 = config.get("nombre_stack_key")
                self.gui.set_stacks_dropdown.label = self.i18n.t(_sk2, default=config.get("nombre_stack", "Stacks")) if _sk2 else config.get("nombre_stack", "Stacks")
                self.gui.set_stacks_dropdown.options = [ft.dropdown.Option(str(i)) for i in range(1, max_stacks + 1)]
                self.gui.set_stacks_dropdown.visible = True
            else:
                self.gui.set_stacks_dropdown.visible = False
        else:
            self.gui.set_checkbox.visible = False
            self.gui.set_stacks_dropdown.visible = False

        if self.gui.set_checkbox.page:
            self.gui.set_checkbox.update()
            self.gui.set_stacks_dropdown.update()

        # Actualizar descripción del set 4pc
        if hasattr(self.gui, 'lbl_set_desc_4pc'):
            desc = self.i18n.t(f"set_desc_4pc.{nombre_set1}", default="") if nombre_set1 != "Ninguno" else ""
            if desc:
                import re
                # Colorear números con % o "ptos." y palabras clave de stats
                patron = re.compile(
                    r'(\d+(?:[.,]\d+)?(?:\s*%|\s*ptos\.?)?'  # números con % o ptos
                    r'|Ataque|ATK|Daño Crítico|CRIT DMG|Probabilidad de Crítico|CRIT Rate'
                    r'|Maestría de Anomalía|Anomaly Proficiency|Tasa de Anomalía|Anomaly Mastery'
                    r'|daño bruto|Sheer DMG|daño elemental|Elemental DMG'
                    r'|daño etéreo|Ether DMG|daño ígneo|Fire DMG|daño eléctrico|Electric DMG'
                    r'|Aturdimiento|Daze|Impacto|Impact'
                    r'|Daño de Anomalía|Anomaly DMG|disfunción|Disorder'
                    r'|Perforación|PEN Ratio|Resistencia|RES'
                    r'|daño infligido|DMG|daño del ataque normal|daño recibido'
                    r')',
                    re.IGNORECASE
                )
                spans = []
                last = 0
                for m in patron.finditer(desc):
                    if m.start() > last:
                        spans.append(ft.TextSpan(desc[last:m.start()], style=ft.TextStyle(size=11, color=ft.Colors.WHITE)))
                    spans.append(ft.TextSpan(m.group(), style=ft.TextStyle(size=11, color="primary", weight=ft.FontWeight.BOLD)))
                    last = m.end()
                if last < len(desc):
                    spans.append(ft.TextSpan(desc[last:], style=ft.TextStyle(size=11, color=ft.Colors.WHITE)))
                self.gui.lbl_set_desc_4pc.value = None
                self.gui.lbl_set_desc_4pc.spans = spans
                self.gui.lbl_set_desc_4pc.visible = True
            else:
                self.gui.lbl_set_desc_4pc.value = ""
                self.gui.lbl_set_desc_4pc.spans = []
                self.gui.lbl_set_desc_4pc.visible = False
            if self.gui.lbl_set_desc_4pc.page:
                self.gui.lbl_set_desc_4pc.update()

    def cambiar_refinamiento(self, e):
        try:
            val = int(e.control.value)
            self.estado_actual.refinamiento = val
            logger.info(f"Refinamiento cambiado a R{val}")
            self.actualizar_desc_wengine_bonos()
            self.recalcular_stats_finales()
        except Exception as ex:
            logger.error(f"Error cambiando refinamiento: {ex}")

    def reiniciar_stats(self, e=None):
        self.estado_actual.reiniciar()
        self.base_stats.clear()
        
        if hasattr(self.gui, 'substat_counters'):
            for counter in self.gui.substat_counters.values():
                counter.value = "0"
        
        if hasattr(self.gui, 'contenedor_desc_wengine'):
            self.gui.contenedor_desc_wengine.visible = False
        if hasattr(self.gui, 'contenedor_desc_core'):
            self.gui.contenedor_desc_core.visible = False

        if self.gui.refinamiento_dropdown:
            self.gui.refinamiento_dropdown.value = "1"
            self.gui.refinamiento_dropdown.update()  

        if hasattr(self.gui, 'refinamiento_dropdown') and self.gui.refinamiento_dropdown:
            self.gui.refinamiento_dropdown.value = "1"
        if hasattr(self.gui, 'stacks_dropdown') and self.gui.stacks_dropdown:
            self.gui.stacks_dropdown.value = "1"
            self.gui.stacks_dropdown.visible = False
        if hasattr(self.gui, 'core_checkbox') and self.gui.core_checkbox:
            self.gui.core_checkbox.value = False
        if hasattr(self.gui, 'set_checkbox') and self.gui.set_checkbox:
            self.gui.set_checkbox.value = False
            self.gui.set_checkbox.visible = False 
        if hasattr(self.gui, 'dd_elemento_abloom') and self.gui.dd_elemento_abloom:
            self.gui.dd_elemento_abloom.value = "Automático"
            self.gui.dd_elemento_abloom.visible = False
        if hasattr(self.gui, 'dd_elemento_abloom') and self.gui.dd_elemento_abloom:
            self.gui.dd_elemento_abloom.value = "Automático"

        if hasattr(self.gui, 'slider_potencial') and self.gui.slider_potencial:
            self.gui.slider_potencial.value = 0
            self.estado_actual.nivel_potencial = 0
            self.gui.contenedor_potencial.visible = False
            self.gui.lbl_desc_potencial.value = self.i18n.t("ui.tab_dps.desc_potencial")
            self.gui.contenedor_potencial.update()
        
        self.gui.actualizar_imagen_agente("Ninguno")
        self.gui.actualizar_imagen_wengine("Ninguno")

        for prefijo in ["sup1", "sup2"]:
            self.gui.team_controls[f"{prefijo}_agente"].value = "Ninguno"
            self.gui.team_controls[f"{prefijo}_wengine"].value = "Ninguno"
            self.gui.team_controls[f"{prefijo}_set4"].value = "Ninguno"
            
            self.gui.actualizar_imagen_team(prefijo, "agente", "Ninguno")
            self.gui.actualizar_imagen_team(prefijo, "wengine", "Ninguno")

            if f"{prefijo}_mindscape" in self.gui.team_controls:
                self.gui.team_controls[f"{prefijo}_mindscape"].value = "0"
            if f"{prefijo}_mindscape_stacks" in self.gui.team_controls:
                self.gui.team_controls[f"{prefijo}_mindscape_stacks"].value = "0"
            if f"{prefijo}_mindscape_cond" in self.gui.team_controls:
                self.gui.team_controls[f"{prefijo}_mindscape_cond"].value = False

            for key_text in ["tipo", "elemento", "faccion"]:
                if f"{prefijo}_{key_text}" in self.gui.team_controls:
                    self.gui.team_controls[f"{prefijo}_{key_text}"].value = ""

            keys_stats = ["atk", "hp", "crit_rate", "crit_dmg", "pen", "am", "er", "imp", "def"]
            for k in keys_stats:
                control_key = f"{prefijo}_stat_{k}"
                if control_key in self.gui.team_controls:
                    self.gui.team_controls[control_key].value = "0"

        if hasattr(self.gui, 'lbl_resumen_buffs'):
            self.gui.lbl_resumen_buffs.value = self.i18n.t("misc.selecciona_companeros", default="• Selecciona a tus compañeros de equipo. Si tienen buffs condicionados, rellena los datos.")
            self.gui.lbl_resumen_buffs.spans = [] 
            self.gui.lbl_resumen_buffs.color = ft.Colors.GREY_400 
            self.gui.lbl_resumen_buffs.update()

        self.actualizar_ui_completa()
        self.mostrar_mensaje(self.i18n.t("ui_dinamico.build_reiniciada", default="Build y equipo reiniciados."))

    def reiniciar_soporte(self, prefijo):
        """Reinicia exclusivamente los datos de un panel de soporte (sup1 o sup2)."""
        
        if f"{prefijo}_agente" in self.gui.team_controls:
            self.gui.team_controls[f"{prefijo}_agente"].value = "Ninguno"
        if f"{prefijo}_txt_busqueda" in self.gui.team_controls:
            self.gui.team_controls[f"{prefijo}_txt_busqueda"].value = ""
            self.gui.team_controls[f"{prefijo}_txt_busqueda"].update()
        if f"{prefijo}_wengine" in self.gui.team_controls:
            self.gui.team_controls[f"{prefijo}_wengine"].value = "Ninguno"
        if f"{prefijo}_set4" in self.gui.team_controls:
            self.gui.team_controls[f"{prefijo}_set4"].value = "Ninguno"
        if f"{prefijo}_wengine_ref" in self.gui.team_controls:
            self.gui.team_controls[f"{prefijo}_wengine_ref"].value = "1"
        if f"{prefijo}_wengine_stacks" in self.gui.team_controls:
            self.gui.team_controls[f"{prefijo}_wengine_stacks"].value = "0"
            
        self.gui.actualizar_imagen_team(prefijo, "agente", "Ninguno")
        self.gui.actualizar_imagen_team(prefijo, "wengine", "Ninguno")

        if f"{prefijo}_mindscape" in self.gui.team_controls:
            self.gui.team_controls[f"{prefijo}_mindscape"].value = "0"
        if f"{prefijo}_mindscape_stacks" in self.gui.team_controls:
            self.gui.team_controls[f"{prefijo}_mindscape_stacks"].value = "0"
        if f"{prefijo}_mindscape_cond" in self.gui.team_controls:
            self.gui.team_controls[f"{prefijo}_mindscape_cond"].value = False

        for key_text in ["tipo", "elemento"]:
            ctrl = self.gui.team_controls.get(f"{prefijo}_{key_text}")
            if ctrl:
                ctrl.src = "images/elementos/default.png"
                ctrl.opacity = 0.3
                ctrl.tooltip = ""
        ctrl_facc = self.gui.team_controls.get(f"{prefijo}_faccion")
        if ctrl_facc:
            ctrl_facc.src = "images/faccion/default.png"
            ctrl_facc.opacity = 0.3
            ctrl_facc.tooltip = ""
        ctrl_set = self.gui.team_controls.get(f"{prefijo}_img_set")
        if ctrl_set:
            ctrl_set.src = "images/discos/default.png"
            ctrl_set.opacity = 0.3

        keys_stats = ["atk", "hp", "crit_rate", "crit_dmg", "pen", "am", "er", "imp", "def"]
        for k in keys_stats:
            control_key = f"{prefijo}_stat_{k}"
            if control_key in self.gui.team_controls:
                self.gui.team_controls[control_key].value = "0"

        self.recalcular_stats_finales()
        self.gui.page.update()
        self.mostrar_mensaje(self.i18n.t("ui_dinamico.soporte_reiniciado", default=f"Panel de soporte {prefijo[-1]} reiniciado.", num=prefijo[-1]))

    def cambiar_core_stacks(self, e):
        try:
            val = float(e.control.value)
            self.estado_actual.core_stacks = int(val)
            self.actualizar_desc_core()
            self.recalcular_stats_finales()
        except:
            pass

    def cambiar_potencial(self, e):
        try:
            val = int(e.control.value)
            self.estado_actual.nivel_potencial = val
            self.actualizar_texto_potencial()
            self.recalcular_stats_finales()
        except:
            pass

    def actualizar_texto_potencial(self):
        nivel = getattr(self.estado_actual, 'nivel_potencial', 0)
        agente = self.estado_actual.nombre_agente
        
        if agente in MAPA_POTENCIAL:
            if nivel > 0:
                bonos = MAPA_POTENCIAL[agente](nivel)
                if bonos:
                    textos = [f"{self.traducir_stat_csv(k)}: +{v}" for k, v in bonos.items()]
                    self.gui.lbl_desc_potencial.value = self.i18n.t("ui.potencial.efecto_actual", default=f"Efecto actual (Nv.{nivel}): {{textos}}", nivel=nivel, textos=', '.join(textos))
                    self.gui.lbl_desc_potencial.color = "primary"
                else:
                    self.gui.lbl_desc_potencial.value = self.i18n.t("ui.potencial.desbloqueado", default="Potencial desbloqueado (No afecta a las stats)")
                    self.gui.lbl_desc_potencial.color = "on_primary"
            else:
                bonos_max = MAPA_POTENCIAL[agente](6)
                if bonos_max:
                    textos_max = [self.traducir_stat_csv(k) for k in bonos_max.keys()]
                    self.gui.lbl_desc_potencial.value = self.i18n.t("ui.potencial.aumenta", default=f"Aumenta: {{textos}} (Desliza para activar)", textos=', '.join(textos_max))
                else:
                    self.gui.lbl_desc_potencial.value = self.i18n.t("ui.potencial.desliza", default="Desliza para activar los efectos.")
                self.gui.lbl_desc_potencial.color = "on_primary"
            
            if self.gui.lbl_desc_potencial.page:
                self.gui.lbl_desc_potencial.update()

    def actualizar_panel_bonos(self):
        """Genera recuadros verticales mostrando cada bono activo (arma, core, mindscapes, sets, soportes)."""
        self.gui.panel_bonos_activos.controls.clear()
        chips = []

        # Wengine pasiva
        nombre_w = self.estado_actual.nombre_wengine
        if nombre_w and nombre_w != "Ninguno" and nombre_w in MAPA_WENGINES:
            mostrar_wengine = True
            try:
                if self.wengine_data and self.tipo:
                    datos_w = self.wengine_data.get(nombre_w)
                    if datos_w:
                        tipo_arma = datos_w.get('tipow', '')
                        if tipo_arma:
                            mostrar_wengine = self.gestor_stats._normalizar(self.tipo) in self.gestor_stats._normalizar(tipo_arma)
            except Exception:
                pass
            if mostrar_wengine:
                try:
                    func_w = MAPA_WENGINES[nombre_w]
                    try:
                        bonos = func_w(stats_actuales={}, refinamiento=self.estado_actual.refinamiento, nombre_agente=self.estado_actual.nombre_agente, stacks=self.estado_actual.stacks, estado_enemigo="Normal", elemento_agente=self.elemento or "")
                    except TypeError:
                        bonos = func_w({}, self.estado_actual.refinamiento, self.estado_actual.nombre_agente, self.estado_actual.stacks)
                    if bonos:
                        for k, v in bonos.items():
                            if v == 0: continue
                            chips.append(self._crear_chip_bono(f"{nombre_w}", f"+{v:g} {self.traducir_stat_csv(k)}"))
                except Exception:
                    pass

        # Core
        if self.estado_actual.core_activo and self.estado_actual.nombre_agente in MAPA_CORE:
            try:
                func_core = MAPA_CORE[self.estado_actual.nombre_agente]
                stacks = self.estado_actual.core_stacks
                stats_snapshot = getattr(self, 'ultimos_stats_calculados', {})
                try:
                    bonos = func_core(condicion_activa=True, nombre_habilidad=self.estado_actual.nombre_habilidad or "", stats_actuales=stats_snapshot, stacks=stacks, tipos_soportes=[])
                except TypeError:
                    try:
                        bonos = func_core(condicion_activa=True, nombre_habilidad=self.estado_actual.nombre_habilidad or "", stacks=stacks, stats_actuales=stats_snapshot)
                    except TypeError:
                        bonos = func_core(condicion_activa=True, nombre_habilidad=self.estado_actual.nombre_habilidad or "")
                if bonos:
                    for k, v in bonos.items():
                        if not isinstance(v, (int, float)) or v == 0: continue
                        chips.append(self._crear_chip_bono("Core", f"+{v:g} {self.traducir_stat_csv(k)}"))
            except Exception:
                pass

        # Mindscapes
        if self.estado_actual.mindscape > 0 and self.estado_actual.nombre_agente in MAPA_MINDSCAPES:
            try:
                func_m = MAPA_MINDSCAPES[self.estado_actual.nombre_agente]
                m_level = self.estado_actual.mindscape
                m_stacks = self.estado_actual.mindscape_stacks
                niveles = [1, 2, 4, 5, 6]
                bonos_previos = {}
                for nivel in niveles:
                    if nivel > m_level:
                        break
                    bonos_nivel = func_m(nivel, stacks=m_stacks, condicion_activa=self.estado_actual.mindscape_cond or True, nombre_habilidad=self.estado_actual.nombre_habilidad or "")
                    for k, v in bonos_nivel.items():
                        diff = v - bonos_previos.get(k, 0.0)
                        if diff != 0:
                            chips.append(self._crear_chip_bono(f"Mindscape M{nivel}", f"+{diff:g} {self.traducir_stat_csv(k)}"))
                    bonos_previos = bonos_nivel
            except Exception:
                pass

        # Potencial
        nivel_pot = getattr(self.estado_actual, 'nivel_potencial', 0)
        if nivel_pot > 0 and self.estado_actual.nombre_agente in MAPA_POTENCIAL:
            try:
                bonos = MAPA_POTENCIAL[self.estado_actual.nombre_agente](nivel_pot)
                if bonos:
                    for k, v in bonos.items():
                        if v == 0: continue
                        chips.append(self._crear_chip_bono(f"Potencial Nv.{nivel_pot}", f"+{v:g} {self.traducir_stat_csv(k)}"))
            except Exception:
                pass

        # Set 4pc del DPS
        nombre_set1 = self.estado_actual.sets.get('set1', 'Ninguno')
        nombre_set3 = self.estado_actual.sets.get('set3', 'Ninguno')
        if nombre_set1 != "Ninguno" and nombre_set3 == "Ninguno":
            set_norm = self.gestor_stats._normalizar(nombre_set1)
            func_set = next((func for k, func in MAPA_EFECTOS_SETS.items() if self.gestor_stats._normalizar(k) == set_norm), None)
            if func_set:
                try:
                    bonos = func_set({}, elemento=self.elemento, stacks=self.estado_actual.set_stacks, condicion_activa=self.estado_actual.set_condicion, tipo_agente=self.tipo, nombre_agente=self.estado_actual.nombre_agente)
                    if bonos:
                        for k, v in bonos.items():
                            if v == 0: continue
                            chips.append(self._crear_chip_bono(f"4pc {self.i18n.t(f'sets.{nombre_set1}', default=nombre_set1)}", f"+{v:g} {self.traducir_stat_csv(k)}"))
                except Exception:
                    pass

        # Soportes (agentes, armas, sets, mindscapes, cores)
        for prefijo in ["sup1", "sup2"]:
            nombre_sup = self.gui.team_controls.get(f"{prefijo}_agente", ft.Dropdown()).value
            if not nombre_sup or nombre_sup == "Ninguno":
                continue

            # Buff del agente soporte (ej: ATK de Astra Yao)
            n_sup_norm = self.gestor_stats._normalizar(nombre_sup)
            for key_ag, func_ag in MAPA_SOPORTES_AGENTES.items():
                if key_ag in n_sup_norm:
                    datos_sup = next((a for a in self.agentes_data if a['Nombre'] == nombre_sup), None)
                    tipo_sup = datos_sup.get("Tipo", "") if datos_sup else ""
                    elem_sup = (datos_sup.get("Elemento", "") or datos_sup.get("elemento", "")).lower() if datos_sup else ""
                    stats_sup = {
                        "Ataque": self._parse_valor(self.gui.team_controls.get(f"{prefijo}_stat_atk", ft.TextField()).value),
                        "Puntos_de_Vida": self._parse_valor(self.gui.team_controls.get(f"{prefijo}_stat_hp", ft.TextField()).value),
                        "Maestría_Anomalía": self._parse_valor(self.gui.team_controls.get(f"{prefijo}_stat_ap", ft.TextField()).value) if f"{prefijo}_stat_ap" in self.gui.team_controls else 0,
                    }
                    try: val_m_ag = int(self.gui.team_controls.get(f"{prefijo}_mindscape", ft.Dropdown()).value or 0)
                    except: val_m_ag = 0
                    roles_t = [str(self.tipo).lower()] if self.tipo else []
                    elems_t = [str(self.elemento).lower()] if self.elemento else []
                    facs_t = [str(getattr(self, 'faccion', '')).lower()]
                    nombres_t = [str(self.estado_actual.nombre_agente).lower()]
                    datos_eq = {"roles": roles_t, "elementos": elems_t, "facciones": facs_t, "nombres": nombres_t}
                    dummy = {}
                    try:
                        func_ag(dummy, tipo_agente=tipo_sup, stats=stats_sup, datos_equipo=datos_eq, elemento_dps=str(self.elemento or "").lower(), mindscape=val_m_ag)
                    except Exception:
                        pass
                    for k, v in dummy.items():
                        if isinstance(v, (int, float)) and v != 0:
                            chips.append(self._crear_chip_bono(f"{nombre_sup}", f"+{v:g} {self.traducir_stat_csv(k)}"))
                    break

            # Arma del soporte
            nombre_arma_sup = self.gui.team_controls.get(f"{prefijo}_wengine", ft.Dropdown()).value
            if nombre_arma_sup and nombre_arma_sup != "Ninguno":
                n_arma_norm = self.gestor_stats._normalizar(nombre_arma_sup)
                for key_w, func_w in MAPA_SOPORTES_WENGINES.items():
                    if key_w in n_arma_norm:
                        try:
                            ref = int(self.gui.team_controls.get(f"{prefijo}_wengine_ref", ft.Dropdown()).value or 1)
                        except: ref = 1
                        try:
                            stk = int(self.gui.team_controls.get(f"{prefijo}_wengine_stacks", ft.Dropdown()).value or 0)
                        except: stk = 0
                        dummy = {}
                        try:
                            func_w(dummy, refinamiento=ref, stacks=stk, elemento_dps=str(self.elemento or "").lower())
                        except Exception:
                            pass
                        for k, v in dummy.items():
                            if isinstance(v, (int, float)) and v != 0:
                                chips.append(self._crear_chip_bono(f"{nombre_arma_sup} ({nombre_sup})", f"+{v:g} {self.traducir_stat_csv(k)}"))
                        break

            # Set del soporte
            nombre_set_sup = self.gui.team_controls.get(f"{prefijo}_set4", ft.Dropdown()).value
            if nombre_set_sup and nombre_set_sup != "Ninguno":
                n_set_norm = self.gestor_stats._normalizar(nombre_set_sup)
                for key_s, func_s in MAPA_SOPORTES_SETS.items():
                    if key_s in n_set_norm:
                        try:
                            stk_set = int(self.gui.team_controls.get(f"{prefijo}_set_stacks", ft.Dropdown()).value or 0)
                        except: stk_set = 0
                        datos_sup = next((a for a in self.agentes_data if a['Nombre'] == nombre_sup), None)
                        tipo_sup = datos_sup.get("Tipo", "") if datos_sup else ""
                        stats_sup = {}
                        dummy = {}
                        try:
                            func_s(dummy, tipo_agente=tipo_sup, stats=stats_sup, stacks_set=stk_set)
                        except Exception:
                            pass
                        for k, v in dummy.items():
                            if isinstance(v, (int, float)) and v != 0:
                                chips.append(self._crear_chip_bono(f"4pc {self.i18n.t(f'sets.{nombre_set_sup}', default=nombre_set_sup)} ({nombre_sup})", f"+{v:g} {self.traducir_stat_csv(k)}"))
                        break

            # Mindscape del soporte
            try: val_m = int(self.gui.team_controls.get(f"{prefijo}_mindscape", ft.Dropdown()).value or 0)
            except: val_m = 0
            if val_m > 0 and nombre_sup in MAPA_MINDSCAPES:
                try:
                    try: val_m_stacks = int(self.gui.team_controls.get(f"{prefijo}_mindscape_stacks", ft.Dropdown()).value or 0)
                    except: val_m_stacks = 0
                    try: val_m_cond = self.gui.team_controls.get(f"{prefijo}_mindscape_cond", ft.Checkbox()).value
                    except: val_m_cond = False
                    func_ms = MAPA_MINDSCAPES[nombre_sup]
                    niveles = [1, 2, 4, 5, 6]
                    bonos_previos = {}
                    for nivel in niveles:
                        if nivel > val_m:
                            break
                        bonos_nivel = func_ms(nivel, stacks=val_m_stacks, condicion_activa=val_m_cond, nombre_habilidad="")
                        for k, v in bonos_nivel.items():
                            diff = v - bonos_previos.get(k, 0.0)
                            if isinstance(diff, (int, float)) and diff != 0:
                                chips.append(self._crear_chip_bono(f"M{nivel} {nombre_sup}", f"+{diff:g} {self.traducir_stat_csv(k)}"))
                        bonos_previos = bonos_nivel
                except Exception:
                    pass

        # Nodos DA (positivos y negativos)
        if hasattr(self.gui, 'da_active_buffs') and hasattr(self.gui, 'mapa_stats_da'):
            for stat_ui, valor in self.gui.da_active_buffs.items():
                if valor == 0: continue
                clave_logica = self.gui.mapa_stats_da.get(stat_ui, stat_ui)
                if valor < 0:
                    chips.append(self._crear_chip_bono("Nodo DA", f"{valor:g} {self.traducir_stat_csv(clave_logica)}", debuff=True))
                else:
                    chips.append(self._crear_chip_bono("Nodo DA", f"+{valor:g} {self.traducir_stat_csv(clave_logica)}"))

        # Pasivas de agentes (efectos propios del DPS)
        from efectos_pasivas import MAPA_PASIVAS
        nombre_ag = self.estado_actual.nombre_agente
        if nombre_ag and nombre_ag in MAPA_PASIVAS:
            try:
                func_pas = MAPA_PASIVAS[nombre_ag]
                roles_team = [str(self.tipo).lower()] if self.tipo else []
                elems_team = [str(self.elemento).lower()] if self.elemento else []
                facs_team = [str(getattr(self, 'faccion', '')).lower()]
                nombres_team = [str(nombre_ag).lower()]
                for prefijo in ["sup1", "sup2"]:
                    n_sup = self.gui.team_controls.get(f"{prefijo}_agente", ft.Dropdown()).value
                    if n_sup and n_sup != "Ninguno":
                        d_sup = next((a for a in self.agentes_data if a['Nombre'] == n_sup), None)
                        if d_sup:
                            roles_team.append(d_sup.get("Tipo", "").lower())
                            elems_team.append((d_sup.get("Elemento", "") or d_sup.get("elemento", "")).lower())
                            facs_team.append((d_sup.get("Faccion", "") or d_sup.get("Facción", "")).lower())
                            nombres_team.append(n_sup.lower())
                datos_equipo = {"roles": roles_team, "elementos": elems_team, "facciones": facs_team, "nombres": nombres_team}
                stats_snap = getattr(self, 'ultimos_stats_calculados', {})
                kwargs_pas = {}
                if hasattr(self.gui, 'controles_pasivas'):
                    for key, control in self.gui.controles_pasivas.items():
                        kwargs_pas[key] = True
                try:
                    bonos_pas = func_pas(datos_equipo=datos_equipo, roles_equipo=roles_team, stats_actuales=stats_snap, nombre_habilidad=self.estado_actual.nombre_habilidad or "", elemento=self.elemento or "", **kwargs_pas)
                except TypeError:
                    try:
                        bonos_pas = func_pas(roles_equipo=roles_team, stats_actuales=stats_snap, **kwargs_pas)
                    except TypeError:
                        bonos_pas = func_pas(roles_equipo=roles_team)
                if bonos_pas:
                    for k, v in bonos_pas.items():
                        if isinstance(v, (int, float)) and v != 0:
                            chips.append(self._crear_chip_bono(self.i18n.t("ui.buffs.pasiva_titulo", default="Pasiva {agente}").replace("{agente}", nombre_ag), f"+{v:g} {self.traducir_stat_csv(k)}"))
                        elif isinstance(v, str) and k.startswith("Info_"):
                            chips.append(self._crear_chip_bono(self.i18n.t("ui.buffs.pasiva_titulo", default="Pasiva {agente}").replace("{agente}", nombre_ag), v))
            except Exception:
                pass

        if chips:
            self.gui.panel_bonos_activos.controls = chips
            self.gui.card_bonos_activos.visible = True
        else:
            self.gui.card_bonos_activos.visible = False

    def _crear_chip_bono(self, titulo, valor, debuff=False):
        """Crea un rectángulo con borde primary/secondary para un bono."""
        color_borde = "secondary" if debuff else "primary"
        color_titulo = "secondary" if debuff else "primary"
        return ft.Container(
            content=ft.Column([
                ft.Text(titulo, size=10, weight=ft.FontWeight.BOLD, color=color_titulo),
                ft.Text(valor, size=10, color=ft.Colors.WHITE70),
            ], spacing=0, tight=True),
            border=ft.border.all(1, color_borde),
            border_radius=6,
            padding=ft.padding.symmetric(horizontal=6, vertical=4),
            width=139,
        )

    def actualizar_desc_core(self):
        """Muestra/oculta la descripción de lo que aporta el core activo."""
        nombre = self.estado_actual.nombre_agente
        if not self.estado_actual.core_activo or nombre not in MAPA_CORE:
            self.gui.contenedor_desc_core.visible = False
            if self.gui.contenedor_desc_core.page:
                self.gui.contenedor_desc_core.update()
            return
        try:
            func_core = MAPA_CORE[nombre]
            stacks = self.estado_actual.core_stacks
            try:
                bonos = func_core(condicion_activa=True, nombre_habilidad=self.estado_actual.nombre_habilidad or "", stats_actuales={}, stacks=stacks, tipos_soportes=[])
            except TypeError:
                try:
                    bonos = func_core(condicion_activa=True, nombre_habilidad=self.estado_actual.nombre_habilidad or "", stacks=stacks, stats_actuales={})
                except TypeError:
                    bonos = func_core(condicion_activa=True, nombre_habilidad=self.estado_actual.nombre_habilidad or "")
            if bonos:
                textos = [f"{self.traducir_stat_csv(k)}: +{v:g}" for k, v in bonos.items() if isinstance(v, (int, float)) and v != 0]
                if textos:
                    self.gui.lbl_desc_core.value = self.i18n.t("ui.tab_dps.core_aporta", bonos=', '.join(textos))
                    self.gui.contenedor_desc_core.visible = True
                else:
                    self.gui.contenedor_desc_core.visible = False
            else:
                self.gui.contenedor_desc_core.visible = False
        except Exception:
            self.gui.contenedor_desc_core.visible = False
        if self.gui.contenedor_desc_core.page:
            self.gui.contenedor_desc_core.update()

    def cambiar_core_activo(self, e):
        try:
            self.estado_actual.core_activo = e.control.value
            self.actualizar_desc_core()
            self.recalcular_stats_finales()
        except Exception as ex:
            print(f"Error cambiando core activo: {ex}")

    def generar_controles_pasivas(self, nombre_agente):
        """Genera checkboxes dinámicos basados en CONFIG_PASIVAS_UI"""
        self.gui.contenedor_pasivas_ui.controls.clear()
        self.gui.controles_pasivas.clear()
        
        if nombre_agente in CONFIG_PASIVAS_UI:
            configs = CONFIG_PASIVAS_UI[nombre_agente]
            for conf in configs:
                if conf["tipo"] == "checkbox":
                    key_i18n = conf.get("label_key")
                    label = self.i18n.t(key_i18n, default=conf["label"]) if key_i18n else conf["label"]
                    chk = ft.Checkbox(
                        label=label,
                        value=conf["default"],
                        on_change=lambda e: self.recalcular_stats_finales()
                    )
                    self.gui.contenedor_pasivas_ui.controls.append(chk)
                    self.gui.controles_pasivas[conf["key"]] = chk
            self.gui.contenedor_pasivas_ui.update()
        else:
            self.gui.contenedor_pasivas_ui.update()

    def actualizar_ui_completa(self):
        self.gui.agent_dropdown.value, self.gui.wengine_dropdown.value = self.estado_actual.nombre_agente, self.estado_actual.nombre_wengine
        self.gui.wengine_dropdown.update()
        if hasattr(self.gui, 'txt_agente_dps'):
            valor_mostrar = self.estado_actual.nombre_agente
            if valor_mostrar == "Ninguno" or not valor_mostrar:
                self.gui.txt_agente_dps.value = ""
            else:
                self.gui.txt_agente_dps.value = valor_mostrar
            self.gui.txt_agente_dps.update()
        self.actualizar_habilidad_ui()
        for i in range(1, 7):
            nombre_set = self.estado_actual.discos_detalles[i]["set"]
            self.actualizar_imagen_disco_ui(i, nombre_set)
        self.actualizar_dropdown_abloom()
        self.recalcular_stats_finales()

    def actualizar_habilidad_ui(self):
        # Las claves de habilidades_agente son i18n keys — traducir al mostrar
        try:
            from logica_combos import traducir_combo
        except ImportError:
            traducir_combo = lambda k: k

        opciones = [
            ft.dropdown.Option(key=k, text=traducir_combo(k))
            for k in self.habilidades_agente.keys()
        ]

        if not opciones:
            self.gui.habilidad_dropdown.options = [ft.dropdown.Option("Ninguno")]
            self.gui.habilidad_dropdown.value = "Ninguno"
        else:
            self.gui.habilidad_dropdown.options = opciones
            self.gui.habilidad_dropdown.value = self.estado_actual.nombre_habilidad
            
        habilidad = self.habilidades_agente.get(self.estado_actual.nombre_habilidad, {})
        self.gui.entry_vars["Multiplicador_de_ataques"].value = str(habilidad.get("Multiplicador", 0))
        self.gui.entry_vars["Aturdimiento"].value = str(habilidad.get("Aturdimiento", 0))
        
        self.gui.habilidad_dropdown.update()
        self.page.update()

    def actualizar_lista_wengines(self):
        """
        Filtra la lista de W-Engines según el tipo del agente actual (Atacante, Aturdidor...)
        si el checkbox 'Solo Compatibles' está activo.
        """
        filtrar = self.gui.chk_filtro_wengine.value
        tipo_agente = self.tipo
        
        todas_armas = list(self.wengine_data.keys())
        armas_filtradas = []

        if filtrar and tipo_agente:
            tipo_agente_norm = self.gestor_stats._normalizar(tipo_agente)
            
            for nombre_arma in todas_armas:
                datos = self.wengine_data.get(nombre_arma, {})
                
                tipo_arma = datos.get('tipow', '')
                tipo_arma_norm = self.gestor_stats._normalizar(tipo_arma)

                if tipo_arma_norm == tipo_agente_norm:
                    armas_filtradas.append(nombre_arma)

            if not armas_filtradas:
                armas_filtradas = todas_armas
        else:
            armas_filtradas = todas_armas

        armas_filtradas.sort()

        seleccion_actual = self.gui.wengine_dropdown.value

        self.gui.wengine_dropdown.options = [ft.dropdown.Option("Ninguno")] + [ft.dropdown.Option(w) for w in armas_filtradas]
        if seleccion_actual in armas_filtradas:
            self.gui.wengine_dropdown.value = seleccion_actual
        else:
            self.gui.wengine_dropdown.value = "Ninguno"
            if seleccion_actual != "Ninguno":
                self.cargar_wengine("Ninguno")

        self.gui.wengine_dropdown.update()

    def cambiar_filtro_wengines(self, e):
        """ Evento del Checkbox """
        self.actualizar_lista_wengines()
        
    def cargar_habilidades_agente(self, nombre_agente):
        self.habilidades_agente.clear()
        file_path = os.path.join(self.datos_dir, 'agentes', f"{nombre_agente}.csv")
        if not os.path.exists(file_path): return
        
        habilidades_crudas = {}
        
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f, delimiter=';')
                for row in reader:
                    habilidades_crudas[row['Habilidad']] = { 
                        'Multiplicador': self._parse_valor(row.get('Multiplicador')), 
                        'Aturdimiento': self._parse_valor(row.get('Aturdimiento')),
                        'Etiqueta_Dano': str(row.get('Etiqueta_Dano', 'normal')).strip()
                    }
        except Exception as e:
            self.logger.error(f"Error al leer archivo de habilidad para {nombre_agente}: {e}")
            return

        try:
            from logica_combos import get_combos_genericos, get_combos_especificos, AGENTES_ESTRICTOS
            import unicodedata
            COMBOS_GENERICOS   = get_combos_genericos()
            COMBOS_ESPECIFICOS = get_combos_especificos()
            
            if nombre_agente in AGENTES_ESTRICTOS:
                recetas = {}
            else:
                recetas = COMBOS_GENERICOS.copy()
                
            if nombre_agente in COMBOS_ESPECIFICOS:
                recetas.update(COMBOS_ESPECIFICOS[nombre_agente])
                
            def normalizar(t):
                s = str(t).strip().lower()
                return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')

            for nombre_combo, palabras_clave in recetas.items():
                mult_total = 0.0
                atur_total = 0.0
                etiqueta_maxima = 'normal'
                habilidades_encontradas = 0
                
                for keyword in palabras_clave:
                    key_norm = normalizar(keyword)
                    
                    for nombre_real, datos_hab in habilidades_crudas.items():
                        if key_norm in normalizar(nombre_real):
                            mult_total += datos_hab['Multiplicador']
                            atur_total += datos_hab['Aturdimiento']
                            etiqueta_actual = datos_hab['Etiqueta_Dano'].lower()

                            if etiqueta_actual == 'aftershock':
                                etiqueta_maxima = 'aftershock'
                            elif etiqueta_actual == 'elemental' and etiqueta_maxima == 'normal':
                                etiqueta_maxima = 'elemental'
                            
                            habilidades_encontradas += 1
                            break 
                            
                if habilidades_encontradas > 0:
                    self.habilidades_agente[nombre_combo] = {
                        'Multiplicador': mult_total,
                        'Aturdimiento': atur_total,
                        'Etiqueta_Dano': etiqueta_maxima
                    }
            
        except ImportError:
            self.logger.warning("Falta logica_combos.py. Cargando lista sucia por defecto.")
            self.habilidades_agente.update(habilidades_crudas)
        except Exception as e:
            self.logger.error(f"Error al ensamblar combos: {e}")

    def calcular_dano(self, e):
        params = getattr(self, 'ultimos_stats_calculados', {}).copy()

        for key, field in self.gui.entry_vars.items():
            params[key] = self._parse_valor(field.value)

        for key, field in self.gui.buff_vars.items(): 
            params[key] = self._parse_valor(field.value)

        if hasattr(self.gui, "dd_elemento_vortex") and self.gui.dd_elemento_vortex:
            params["Elemento_Vortex"] = self.gui.dd_elemento_vortex.value or "Automático"

        base_dmg_taken = params.get('DMG_Taken', 0.0)
        if hasattr(self.gui, 'dd_miasma') and self.gui.dd_miasma.value == "Activo":
            params['Miasma'] = 1.8
            params['DMG_Taken'] = base_dmg_taken - 25.0
        else:
            params['Miasma'] = 1.0
            params['DMG_Taken'] = base_dmg_taken

        nombre_habilidad = self.estado_actual.nombre_habilidad
        if nombre_habilidad and nombre_habilidad in self.habilidades_agente:
            datos_hab = self.habilidades_agente[nombre_habilidad]
            etiqueta = datos_hab.get('Etiqueta_Dano', 'normal')
            params['Etiqueta_Dano'] = etiqueta
        else:
            params['Etiqueta_Dano'] = 'normal'
            
        if hasattr(self.gui, 'dd_estado_enemigo'):
             params['Estado_Enemigo'] = self.gui.dd_estado_enemigo.value
             
        if hasattr(self.gui, 'dd_elemento_abloom'):
             params['Elemento_Abloom'] = self.gui.dd_elemento_abloom.value
        
        if not self.elemento:
            self.mostrar_mensaje(self.i18n.t("ui_dinamico.selecciona_agente_primero", default="Selecciona un agente primero."))
            return

        enemigo_seleccionado = self.gui.enemy_dropdown.value
        if not enemigo_seleccionado or enemigo_seleccionado == "Ninguno":
            self.mostrar_mensaje(self.i18n.t("ui_dinamico.selecciona_enemigo_primero", default="¡¡Debes seleccionar un enemigo para calcular!!"))
            return

        try:
            nombre_agente = self.estado_actual.nombre_agente
            tipo_agente = ""
            if isinstance(self.agentes_data, list):
                for agente in self.agentes_data:
                    if agente.get("Nombre") == nombre_agente:
                        tipo_agente = agente.get("Tipo", "")
                        break
            
            params['Tipo'] = tipo_agente
            params['Nombre_Agente'] = nombre_agente
            
            elemento_calculo = self.elemento.lower() if self.elemento else ""

            efectos = getattr(self, 'mensajes_efectos_actuales', [])
            dmg, sheer, anomaly, disorder, abloom, vortex, stats_combate = self.logica_dmg.calcular_todos_danos(params, elemento_calculo)
            stats_completas = params.copy()
            stats_completas.update(stats_combate)
            self.mostrar_resultados(dmg, sheer, anomaly, disorder, abloom, vortex, stats_completas, params['Etiqueta_Dano'], efectos_activos=efectos)
            
            self.ultimos_stats_calculados = params.copy()
            self.ultimos_stats_calculados["_dmg_normal"] = dmg
            self.ultimos_stats_calculados["_dmg_anomalia"] = anomaly
            
        except Exception as ex:
            self.mostrar_mensaje(f"Error al calcular: {ex}")
    
    # ── Helpers de índice (client_storage) ─────────────────────────────
    def _actualizar_indice_buffs(self, nombre, eliminar=False):
        try:
            raw = self.page.client_storage.get("buff_da:__indice__")
            indice = self._safe_json(raw) or []
        except Exception:
            indice = []
        if eliminar:
            indice = [n for n in indice if n != nombre]
        elif nombre not in indice:
            indice.append(nombre)
        self.page.client_storage.set("buff_da:__indice__", json.dumps(indice))

    def _actualizar_indice_builds(self, nombre, eliminar=False):
        try:
            raw = self.page.client_storage.get("build:__indice__")
            indice = self._safe_json(raw) or []
        except Exception:
            indice = []
        if eliminar:
            indice = [n for n in indice if n != nombre]
        elif nombre not in indice:
            indice.append(nombre)
        self.page.client_storage.set("build:__indice__", json.dumps(indice))



    def guardar_buff_da(self, nombre, buffs, imagen):
        datos = {"imagen": imagen, "buffs": buffs}
        self.page.client_storage.set(f"buff_da:{nombre}", json.dumps(datos, ensure_ascii=False))
        self._actualizar_indice_buffs(nombre)
    
    def actualizar_colores_discos_ui(self, e=None):
        """Actualiza los colores (textos y bordes) de los rolls y stats según si la substat/main stat es ideal, decente o basura, y suma los rolls."""
        nombre_agente = self.estado_actual.nombre_agente
        rol = "Atacante"
        if nombre_agente and nombre_agente != "Ninguno":
            datos_agente = next((a for a in self.agentes_data if a['Nombre'] == nombre_agente), None)
            if datos_agente:
                rol = datos_agente.get("Tipo", "Atacante")

        from logica_recomendaciones import CONFIG_ROLES, EXCEPCIONES_AGENTES, evaluar_calidad_global
        config = CONFIG_ROLES.get(rol, CONFIG_ROLES["Atacante"]).copy()
        if nombre_agente in EXCEPCIONES_AGENTES:
            excepcion = EXCEPCIONES_AGENTES[nombre_agente]
            for key in ["main_4", "main_5", "main_6", "subs"]:
                if key in excepcion: config[key] = excepcion[key]
        
        c_subs = config.get("subs", {})
        l_ideal = set(c_subs.get("ideal", []))
        l_decente = set(c_subs.get("decente", []))
        
        huecos_globales = 0
        mejoras_globales = 0

        color_ideal_borde = "#ffb300"
        color_decente_borde = "#00bcd4"

        for slot in range(1, 7):
            
            huecos_disco = 0
            mejoras_disco = 0

            for i in range(1, 5):
                dd_sub = self.gui.team_controls.get(f"disco_{slot}_sub_{i}_stat")
                txt_rolls_sub = self.gui.team_controls.get(f"disco_{slot}_sub_{i}_rolls")

                stat_key = dd_sub.value if dd_sub else None
                
                color_texto = ft.Colors.WHITE
                color_borde = None
                
                if stat_key and stat_key != "Ninguno":
                    huecos_disco += 1

                    try:
                        rolls = int(txt_rolls_sub.value) if txt_rolls_sub else 0
                    except ValueError:
                        rolls = 0
                        
                    mejoras_disco += rolls
                    
                    if stat_key in l_ideal:
                        color_texto = ft.Colors.AMBER_400
                        color_borde = color_ideal_borde
                    elif stat_key in l_decente:
                        color_texto = ft.Colors.CYAN_300
                        color_borde = color_decente_borde
                    else:
                        color_texto = ft.Colors.GREY_500

                if dd_sub:
                    dd_sub.text_style = ft.TextStyle(color=color_texto, weight="bold")
                    dd_sub.border_color = color_borde
                    if dd_sub.page: dd_sub.update()
                if txt_rolls_sub:
                    txt_rolls_sub.color = color_texto
                    if txt_rolls_sub.page: txt_rolls_sub.update()
            
            dd_main = self.gui.team_controls.get(f"disco_{slot}_main")
            if dd_main and slot in [4, 5, 6] and isinstance(dd_main, ft.Dropdown):
                main_val = dd_main.value
                ideales_main = config.get(f"main_{slot}", [])
                
                if main_val and main_val != "Ninguno":
                    if any(ideal.lower() in main_val.lower() for ideal in ideales_main):
                        dd_main.border_color = color_ideal_borde
                    else:
                        dd_main.border_color = None
                else:
                    dd_main.border_color = None
                    
                if dd_main.page: dd_main.update()

            huecos_globales += huecos_disco
            mejoras_globales += mejoras_disco
            
            txt_rolls_disco = self.gui.team_controls.get(f"disco_{slot}_total_rolls")
            if txt_rolls_disco:
                rolls_totales_reales_disco = huecos_disco + mejoras_disco
                txt_rolls_disco.value = f"{rolls_totales_reales_disco}/9"
                if rolls_totales_reales_disco >= 9:
                    txt_rolls_disco.color = ft.Colors.AMBER_400
                elif rolls_totales_reales_disco >= 8:
                    txt_rolls_disco.color = "#FE8D00"
                elif rolls_totales_reales_disco >= 7:
                    txt_rolls_disco.color = "#D326F9"
                elif rolls_totales_reales_disco >= 6:
                    txt_rolls_disco.color = "#21BEFE"
                else:
                    txt_rolls_disco.color = ft.Colors.WHITE
                if txt_rolls_disco.page: txt_rolls_disco.update()
                
        rolls_totales_reales_global = huecos_globales + mejoras_globales
        
        if hasattr(self.gui, "txt_total_rolls_global"):
            self.gui.txt_total_rolls_global.value = f"{rolls_totales_reales_global}/54 Rolls Totales"
            if rolls_totales_reales_global >= 54:
                self.gui.txt_total_rolls_global.color = ft.Colors.AMBER_400
            elif rolls_totales_reales_global >= 48:
                self.gui.txt_total_rolls_global.color = "#FE8D00"
            elif rolls_totales_reales_global >= 42:
                self.gui.txt_total_rolls_global.color = "#D326F9"
            elif rolls_totales_reales_global >= 36:
                self.gui.txt_total_rolls_global.color = "#21BEFE"
            else:
                self.gui.txt_total_rolls_global.color = ft.Colors.WHITE
            if self.gui.txt_total_rolls_global.page: self.gui.txt_total_rolls_global.update()

    def obtener_buffs_da_guardados(self):
        try:
            raw = self.page.client_storage.get("buff_da:__indice__")
            nombres = self._safe_json(raw) or []
            return [f"{n}.json" for n in nombres]
        except Exception:
            return []

    def cargar_buff_da(self, nombre):
        try:
            raw = self.page.client_storage.get(f"buff_da:{nombre}")
            return self._safe_json(raw)
        except Exception:
            return None

    def eliminar_buff_da(self, nombre):
        try:
            self.page.client_storage.remove(f"buff_da:{nombre}")
            self._actualizar_indice_buffs(nombre, eliminar=True)
        except Exception:
            pass

    def inicializar_ranking(self):
        """Llama a esto en el __init__ si quieres persistencia, por ahora en memoria"""
        self.ranking_builds = []

    def _calcular_calidad_substats(self, datos):
        from logica_recomendaciones import CONFIG_ROLES, EXCEPCIONES_AGENTES, evaluar_calidad_global
        
        nombre_agente = datos.get("agente") or datos.get("Nombre_Agente", "Ninguno")
        if not nombre_agente or nombre_agente == "Ninguno": return 0.0
        
        datos_agente = next((a for a in self.agentes_data if a['Nombre'] == nombre_agente), {})
        rol_agente = datos_agente.get("Tipo", "Atacante")
        
        config_rol = CONFIG_ROLES.get(rol_agente, CONFIG_ROLES["Atacante"]).copy()
        if nombre_agente in EXCEPCIONES_AGENTES:
            excep = EXCEPCIONES_AGENTES[nombre_agente]
            if "subs" in excep: config_rol["subs"] = excep["subs"]
        
        # ══════════════════════════════════════════════════════════════════════
        # Componente de evaluación de arma
        # ══════════════════════════════════════════════════════════════════════
        eficiencia_arma = 100.0
        arma_actual = datos.get("wengine", "")
        top_armas = datos.get("top_wengines", [])
        
        if arma_actual and top_armas:
            for nombre_arma, pct_arma in top_armas:
                if nombre_arma == arma_actual:
                    eficiencia_arma = pct_arma
                    break

        resumen_rolls = evaluar_calidad_global(
            nombre_agente=nombre_agente,
            rol_agente=rol_agente,
            rolls_actuales=datos.get("substats_counts", {}),
            stats_finales=datos.get("_stats_reales_calculo", {}),
            eficiencia_wengine_actual=eficiencia_arma,
            excepciones=EXCEPCIONES_AGENTES,
            config_roles=CONFIG_ROLES
        )
        datos["_calidad_substats"] = resumen_rolls
        
        return resumen_rolls["calidad_pct"]

    def agregar_al_ranking(self, e):
        if not self.estado_actual.nombre_agente or self.estado_actual.nombre_agente == "Ninguno":
            self.mostrar_mensaje(self.i18n.t("ui_dinamico.selecciona_agente_primero", default="Selecciona un agente primero."))
            return
            
        if not hasattr(self, 'ultimos_stats_calculados') or not self.ultimos_stats_calculados:
            self.recalcular_stats_finales()

        datos = self.obtener_estado_actual_dict()
        stats_calc = self._normalizar_stats_para_calculo(datos)
        datos["_stats_reales_calculo"] = stats_calc 
        datos["wengine"] = self.estado_actual.nombre_wengine
        
        if hasattr(self, '_ultimo_top_wengines'):
            datos["top_wengines"] = self._ultimo_top_wengines
        
        dmg = self._calcular_dano_interno_ranking(datos, stats_calc, self.elemento)

        dmg["calidad"] = self._calcular_calidad_substats(datos)
        nombre_user = self.gui.config_name_field.value
        
        if nombre_user:
            nombre_build = nombre_user
        elif getattr(self, 'meta_nombre_actual', None):
            nombre_build = self.meta_nombre_actual
        else:
            nombre_build = f"{datos['agente']}"
            
        self._insertar_en_ranking(nombre_build, datos['agente'], dmg, datos)

    def _normalizar_stats_para_calculo(self, datos):
        stats_clean = {}
        fuente = {}
        
        if "_stats_reales_calculo" in datos and isinstance(datos["_stats_reales_calculo"], dict):
            stats_clean = datos["_stats_reales_calculo"].copy()
            stats_clean["Nombre_Agente"] = datos.get("agente") or stats_clean.get("Nombre_Agente", "Desconocido")
        else:
            es_externo = "character" in datos or "name" in datos or "uid" in datos
            
            if es_externo:
                if "stats" in datos: fuente.update(datos["stats"])
                else: fuente.update(datos)
            else:
                if "stats_manuales" in datos: fuente.update(datos["stats_manuales"])
                else: fuente.update(datos)

            MAPA_CLAVES = {
                "Ataque": ["atk", "ATK", "Attack", "Ataque", "Percent ATK"],
                "Puntos_Vida": ["hp", "HP", "Health", "Puntos_Vida", "Percent HP"],
                "Defensa": ["def", "DEF", "Defense", "Defensa", "Percent DEF"],
                "Probabilidad_crítico": ["crit_rate", "CRIT Rate", "CritRate", "Probabilidad_crítico"],
                "Daño_crítico": ["crit_dmg", "CRIT DMG", "CritDMG", "Daño_crítico"],
                "Tasa_de_Perforación": ["pen_ratio", "PEN Ratio", "PenRatio", "Tasa_de_Perforación"],
                "Perforación_Plana": ["pen", "PEN", "Pen", "Perforación_Plana"],
                "Maestría_Anomalía": ["anomaly_proficiency", "Anomaly Proficiency", "Maestría_Anomalía", "ap"],
                "Impacto": ["impact", "Impact", "Impacto"],
                "Recuperación_energía": ["energy_regen", "Energy Regen", "Recuperación_energía"],
                "Daño_elemental": ["elemental_damage", "Ice DMG Bonus", "Fire DMG Bonus", "Electric DMG Bonus", "Ether DMG Bonus", "Physical DMG Bonus", "Wind DMG Bonus", "Daño_elemental"],
                "Daño_Adicional": ["Daño_Adicional", "Bono DMG%"],
                "Reduccion_DEF_enemigo": ["Reduccion_DEF_enemigo", "Red. DEF %", "Reducción DEF"],
                "Pen_Res_Fisico": ["Pen_Res_Fisico", "PEN RES (Fisico)"],
                "Pen_Res_Fuego": ["Pen_Res_Fuego", "PEN RES (Fuego)"],
                "Pen_Res_Hielo": ["Pen_Res_Hielo", "PEN RES (Hielo)"],
                "Pen_Res_Electrico": ["Pen_Res_Electrico", "PEN RES (Electrico)"],
                "Pen_Res_Etereo": ["Pen_Res_Etereo", "PEN RES (Etereo)"],
                "DMG_Taken": ["DMG_Taken", "Vulnerabilidad"]
            }

            for key_calc, keys_posibles in MAPA_CLAVES.items():
                valor_encontrado = 0.0
                for k in keys_posibles:
                    if k in fuente:
                        raw_val = fuente[k]
                        if isinstance(raw_val, dict): raw_val = raw_val.get("value", 0)
                        try:
                            str_val = str(raw_val).replace("%", "").replace(",", ".").strip()
                            valor_encontrado = float(str_val)
                            break 
                        except: continue
                
                if key_calc == "Probabilidad_crítico":
                    if valor_encontrado > 200: valor_encontrado /= 100.0
                    elif 0 < valor_encontrado < 1.0: valor_encontrado *= 100.0
                elif key_calc == "Daño_crítico":
                    if valor_encontrado > 2000: valor_encontrado /= 100.0
                    elif 0 < valor_encontrado < 3.0: valor_encontrado *= 100.0
                elif key_calc in ["Tasa_de_Perforación", "Daño_elemental", "Daño_Adicional", "Reduccion_DEF_enemigo", "Pen_Res_Fisico", "Pen_Res_Fuego", "Pen_Res_Hielo", "Pen_Res_Electrico", "Pen_Res_Etereo"]:
                    if valor_encontrado > 200: valor_encontrado /= 100.0
                    elif 0 < valor_encontrado <= 2.0: valor_encontrado *= 100.0

                stats_clean[key_calc] = valor_encontrado

            stats_clean["Nombre_Agente"] = datos.get("name") or datos.get("agente") or datos.get("character", {}).get("name", "Desconocido")

        try:
            if hasattr(self.gui, 'enemy_dropdown'):
                stats_clean['Nombre_Enemigo'] = self.gui.enemy_dropdown.value or "Ninguno"

            if hasattr(self.gui, 'dd_estado_enemigo'):
                stats_clean['Estado_Enemigo'] = self.gui.dd_estado_enemigo.value

            if hasattr(self.gui, 'dd_miasma') and self.gui.dd_miasma.value == "Activo":
                stats_clean['Miasma'] = 1.8
                stats_clean['DMG_Taken'] = stats_clean.get('DMG_Taken', 0.0) - 25.0
            else:
                stats_clean['Miasma'] = 1.0
                if 'DMG_Taken' not in stats_clean:
                    stats_clean['DMG_Taken'] = 0.0

            claves_enemigo_universales = [
                'Defensa_Base', 'Resistencia_porcentual', 
                'Resistencia_Físico', 'Resistencia_Fuego', 'Resistencia_Hielo', 'Resistencia_Electrico', 'Resistencia_Etereo'
            ]
            
            for key in claves_enemigo_universales:
                if key in self.gui.entry_vars:
                    stats_clean[key] = self._parse_valor(self.gui.entry_vars[key].value)
                elif key not in stats_clean:
                    stats_clean[key] = 950.0 if key == 'Defensa_Base' else 0.0

        except Exception as e:
            print(f"Error inyectando entorno global: {e}")

        if "Elementos_Soportes" in datos.get("_stats_reales_calculo", {}):
            stats_clean["Elementos_Soportes"] = datos["_stats_reales_calculo"]["Elementos_Soportes"]
        elif "Elementos_Soportes" in fuente:
            stats_clean["Elementos_Soportes"] = fuente["Elementos_Soportes"]

        return stats_clean

    def abrir_dialogo_renombrar(self, index, nombre_actual):
        """Abre un popup para cambiar el nombre de la build en el ranking"""
        self.index_renombrar_temp = index
        
        self.campo_nuevo_nombre = ft.TextField(
            value=nombre_actual, 
            label=self.i18n.t("ui_dinamico.nuevo_nombre", default="Nuevo Nombre"), 
            autofocus=True,
            on_submit=self.confirmar_renombre
        )

        self.dialogo_renombrar = ft.AlertDialog(
            title=ft.Text(self.i18n.t("ui_dinamico.renombrar_build", default="Renombrar Build")),
            content=self.campo_nuevo_nombre,
            actions=[
                ft.TextButton(self.i18n.t("ui_dinamico.cancelar", default="Cancelar"), on_click=lambda e: self.page.close(self.dialogo_renombrar)),
                ft.ElevatedButton(self.i18n.t("ui_dinamico.guardar", default="Guardar"), on_click=self.confirmar_renombre)
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )
        self.page.open(self.dialogo_renombrar)

    def eliminar_del_ranking(self, index):
        """Elimina una build específica del ranking por su índice"""
        if 0 <= index < len(self.ranking_builds):
            eliminado = self.ranking_builds.pop(index)
            self.mostrar_mensaje(self.i18n.t("ui_dinamico.eliminada_build", default=f"Eliminada build: {eliminado.get('nombre_build')}", nombre=eliminado.get("nombre_build")))
            self.gui.renderizar_ranking_ui()
        else:
            self.mostrar_mensaje(self.i18n.t("ui_dinamico.error_no_pudo_eliminar", default="Error: No se pudo eliminar."))

    def confirmar_renombre(self, e):
        """Guarda el cambio en la lista y actualiza la UI"""
        nuevo_nombre = self.campo_nuevo_nombre.value.strip()
        idx = getattr(self, 'index_renombrar_temp', -1)

        if idx != -1 and 0 <= idx < len(self.ranking_builds) and nuevo_nombre:

            self.ranking_builds[idx]["nombre_build"] = nuevo_nombre
            self.page.close(self.dialogo_renombrar)
            self.mostrar_mensaje(self.i18n.t("ui_dinamico.renombrado_a", default=f"Renombrado a: {nuevo_nombre}", nombre=nuevo_nombre))
            self.gui.renderizar_ranking_ui()

    def agregar_desde_panel(self, e, lado):
        datos = self.datos_comp_left if lado == "left" else self.datos_comp_right
        if not datos: return

        stats_calc = self._normalizar_stats_para_calculo(datos)
        datos["_stats_reales_calculo"] = stats_calc
        
        nombre_agente = stats_calc.get("Nombre_Agente", "Desconocido")
        elemento_detectado = self._detectar_elemento(nombre_agente, datos)

        dmg = self._calcular_dano_interno_ranking(
            {"agente": nombre_agente}, 
            stats_calc, 
            elemento_detectado
        )
        
        dmg["calidad"] = self._calcular_calidad_substats(datos)
        
        info_stats = f"ATK: {int(stats_calc.get('Ataque', 0))} | CRIT: {stats_calc.get('Probabilidad_crítico', 0):.1f}/{stats_calc.get('Daño_crítico', 0):.1f}"

        meta_nombre = datos.get("_meta_nombre", "")
        nickname = datos.get("nickname", "")
        
        if meta_nombre:
            nombre_build = meta_nombre
        elif nickname and nickname != "Desconocido":
            nombre_build = nickname
        else:
            nombre_build = f"{nombre_agente}"
        
        self._insertar_en_ranking(nombre_build, nombre_agente, dmg, datos, info_stats)

    def _detectar_elemento(self, nombre_agente, datos):
        if not nombre_agente: return "fisico"
        
        nombre_lower = str(nombre_agente).lower().strip()

        if hasattr(self, 'agentes_data') and self.agentes_data:
            for agente in self.agentes_data:
                nombre_csv = str(agente.get("Nombre", "")).lower().strip()
                
                if nombre_csv == nombre_lower or nombre_csv in nombre_lower:
                    elemento = agente.get("elemento") or agente.get("Elemento")
                    
                    if elemento:
                        elem_limpio = str(elemento).lower().strip()
                        if 'eléctrico' in elem_limpio: return 'electrico'
                        if 'etéreo' in elem_limpio: return 'etereo'
                        if 'físico' in elem_limpio: return 'fisico'
                        return elem_limpio
                        
        if datos.get("Electric DMG Bonus", 0) > 0: return "electrico"
        if datos.get("Fire DMG Bonus", 0) > 0: return "fuego"
        if datos.get("Ice DMG Bonus", 0) > 0: return "hielo"
        if datos.get("Ether DMG Bonus", 0) > 0: return "etereo"
        if datos.get("Wind DMG Bonus", 0) > 0: return "viento"
        
        return "fisico"
    
    def _insertar_en_ranking(self, nombre, agente, dmg_dict, datos_completos, info_stats=""):
        if isinstance(dmg_dict, (int, float)):
            dmg_dict = {"maximo": dmg_dict, "normal": dmg_dict, "anomalia": 0, "sheer": 0, "disorder": 0}
            
        item = {
            "id": len(self.ranking_builds),
            "nombre_build": nombre,
            "agente": agente,
            "danos": dmg_dict,
            "dano_raw": dmg_dict["maximo"],
            "score": int(dmg_dict["maximo"]), 
            "pct": 0.0,
            "info_stats": info_stats,
            "datos": datos_completos
        }
        self.ranking_builds.append(item)
        self._actualizar_porcentajes_ranking()
        self.gui.renderizar_ranking_ui()

    def _actualizar_porcentajes_ranking(self):
        if not self.ranking_builds: return
        
        self.ranking_builds.sort(key=lambda x: x["dano_raw"], reverse=True)
        
        self.ranking_builds = self.ranking_builds[:50]

    def reiniciar_ranking(self, e):
        self.ranking_builds = []
        self.mostrar_mensaje(self.i18n.t("ui_dinamico.ranking_reiniciado", default="Ranking reiniciado."))
        self.gui.renderizar_ranking_ui()

    def _calcular_dano_interno_ranking(self, datos, stats, elemento):
        nombre_agente = datos.get("agente") or stats.get("Nombre_Agente", "Desconocido")
        stats_combate = stats.copy()
        
        if 'Multiplicador_de_ataques' not in stats_combate or stats_combate['Multiplicador_de_ataques'] == 0:
            mv = self._obtener_multiplicador_definitiva(nombre_agente)
            stats_combate['Multiplicador_de_ataques'] = mv
            stats_combate['Etiqueta_Dano'] = 'ultimate'
        else:
            mv = stats_combate['Multiplicador_de_ataques']
            
        atk = stats_combate.get('Ataque', 0)
        crit = stats_combate.get('Probabilidad_crítico', 0)
        cd = stats_combate.get('Daño_crítico', 0)
        
        pen_res = stats_combate.get(f'Pen_Res_{str(elemento).capitalize()}', stats_combate.get('Pen_Res_Fisico', 0))
        red_def = stats_combate.get('Reduccion_DEF_enemigo', 0)
        defensa_enemigo = stats_combate.get('Defensa_Base', 950)
        etiqueta = stats_combate.get('Etiqueta_Dano', 'Desconocida')
        
        d_norm, d_sheer, d_anom, d_dis, d_abloom, _, _ = self.calcular_dano_simulado(stats_combate, elemento)
        mejor_dano = max(d_norm, d_anom + d_abloom, d_sheer)
        
        return {
            "maximo": mejor_dano,
            "normal": d_norm,
            "anomalia": d_anom,
            "sheer": d_sheer,
            "disorder": d_dis
        }

    def cargar_desde_ranking(self, indice, lado):
        try:
            if indice < 0 or indice >= len(self.ranking_builds):
                return

            build = self.ranking_builds[indice]
            
            datos = build["datos"]
            if not datos:
                return
            

            if lado == "left":
                self.datos_comp_left = datos
                self.gui.renderizar_panel_comparacion("left", datos)
            else:
                self.datos_comp_right = datos
                self.gui.renderizar_panel_comparacion("right", datos)
                
            self.mostrar_mensaje(self.i18n.t("ui_dinamico.cargado_rank", default=f"Cargado Rank #{indice + 1}", num=indice + 1))

        except Exception as ex:
            import traceback
            traceback.print_exc()
            self.mostrar_mensaje(f"Error: {ex}")

    def _obtener_multiplicador_definitiva(self, nombre_agente):
        if not nombre_agente or nombre_agente == "Ninguno": return 500.0
        
        carpeta_agentes = os.path.join(self.datos_dir, 'agentes')
        archivo_objetivo = None

        if os.path.exists(os.path.join(carpeta_agentes, f"{nombre_agente}.csv")):
            archivo_objetivo = os.path.join(carpeta_agentes, f"{nombre_agente}.csv")
        else:

            try:
                for f in os.listdir(carpeta_agentes):
                    if f.endswith(".csv") and nombre_agente.lower() in f.lower():
                        archivo_objetivo = os.path.join(carpeta_agentes, f)
                        break
            except: pass

        if not archivo_objetivo:
            return 500.0

        try:
            with open(archivo_objetivo, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f, delimiter=';')
                for row in reader:
                    habilidad = row.get('Habilidad', '').lower()
                    if 'definitiva' in habilidad or 'ultimate' in habilidad or 'voidstrike' in habilidad:
                        raw = row.get('Multiplicador', '500')
                        val = float(str(raw).replace(',', '.').replace('%', '').strip())
                        return val
                    
        except Exception as e:
            print(f"Error leyendo CSV {archivo_objetivo}: {e}")
            
        return 500.0

    def mostrar_resultados(self, dmg, sheer, anomaly, disorder, abloom, vortex, stats, etiqueta, efectos_activos=None):
        elem_str = str(self.elemento).lower().replace('é', 'e').replace('í', 'i')
        
        nombre_agente = self.estado_actual.nombre_agente
        nombre_habilidad = self.estado_actual.nombre_habilidad or ""
        
        colores_gradiente = [ft.Colors.WHITE, ft.Colors.GREY_400]

        if etiqueta == 'normal':
            colores_gradiente = ["#F99501", "#FEEC02"]
        else:
            if 'fuego' in elem_str: 
                colores_gradiente = ["#F01A02", "#FC7419"]
            elif 'electrico' in elem_str: 
                colores_gradiente = ["#037CFF", "#26E3FF"]
            elif 'hielo' in elem_str: 
                colores_gradiente = ["#01BAFF", "#01F8B4"]
            elif 'etereo' in elem_str: 
                colores_gradiente = ["#FE1729", "#2F6FF1"]
            elif 'fisico' in elem_str: 
                colores_gradiente = ["#F99501", "#FEEC02"]
            
            if nombre_agente == "Yixuan":
                colores_gradiente = ["#F3D49F", "#E2A748", "#F3D49F"]
            elif nombre_agente == "Miyabi":
                colores_gradiente = ["#25F9FC", "#61B5FC"]
            if nombre_agente == 'Ye Shunguang':
                print(f'[DEBUG color] nombre_habilidad={nombre_habilidad!r} etiqueta={etiqueta!r}')
            elif nombre_agente == "Ye Shunguang" and "Enlightened" in nombre_habilidad:
                colores_gradiente = ["#95B9FD", "#E2DDEE", "#888BFF"]

        max_val = max(dmg, sheer, anomaly + abloom, vortex)

        def actualizar_texto_resultado(control, texto, valor):
            control.content.value = texto
            if valor == max_val and valor > 0:
                control.shader.colors = colores_gradiente
                control.content.color = ft.Colors.WHITE
            else:
                control.shader.colors = [ft.Colors.WHITE54, ft.Colors.WHITE54]
                control.content.color = ft.Colors.WHITE54
            control.update()

        # --- TRADUCCIÓN DE RESULTADOS PRINCIPALES ---
        lbl_crit = self.i18n.t("ui.tab_dps.resultados_normal", default="Crit DMG")
        lbl_sheer = self.i18n.t("ui.tab_dps.resultados_sheer", default="Sheer")
        lbl_anomaly = self.i18n.t("ui.tab_dps.resultados_anomalia", default="Anomaly")
        lbl_abloom = self.i18n.t("ui.tab_dps.resultados_abloom", default="Abloom")
        lbl_disorder = self.i18n.t("ui.tab_dps.resultados_disorder", default="Disorder")
        lbl_ticks = self.i18n.t("ui.tab_dps.ticks_de", default="Ticks de")

        actualizar_texto_resultado(self.gui.resultado_normal, f"{lbl_crit}: {dmg:,.0f}", dmg)
        actualizar_texto_resultado(self.gui.resultado_sheer, f"{lbl_sheer}: {sheer:,.0f}", sheer)
        
        anomaly_total = anomaly + abloom
        if 'fuego' in elem_str:
            texto_anomalia = f"{lbl_anomaly}: {anomaly_total * 20:,.0f} (20 {lbl_ticks} {anomaly_total:,.0f})"
        elif 'electrico' in elem_str:
            texto_anomalia = f"{lbl_anomaly}: {anomaly_total * 10:,.0f} (10 {lbl_ticks} {anomaly_total:,.0f})"
        elif 'etereo' in elem_str:
            texto_anomalia = f"{lbl_anomaly}: {anomaly_total * 10:,.0f} (20 {lbl_ticks} {anomaly_total:,.0f})"
        else:
            texto_anomalia = f"{lbl_anomaly}: {anomaly_total:,.0f}"

        actualizar_texto_resultado(self.gui.resultado_anomaly, texto_anomalia, anomaly + abloom)

        self.gui.resultado_abloom.content.value = f"{lbl_abloom}: {abloom:,.0f}"
        if abloom > 0:
            self.gui.resultado_abloom.shader.colors = [ft.Colors.PURPLE_300, ft.Colors.PURPLE_300]
            self.gui.resultado_abloom.content.color = ft.Colors.WHITE
        else:
            self.gui.resultado_abloom.shader.colors = [ft.Colors.WHITE24, ft.Colors.WHITE24]
            self.gui.resultado_abloom.content.color = ft.Colors.WHITE24
        self.gui.resultado_abloom.update()

        self.gui.resultado_disorder.content.value = f"{lbl_disorder}: {disorder:,.0f}"
        self.gui.resultado_disorder.shader.colors = [ft.Colors.WHITE24, ft.Colors.WHITE24]
        self.gui.resultado_disorder.content.color = ft.Colors.WHITE24
        self.gui.resultado_disorder.update()

        if hasattr(self.gui, "resultado_vortex"):
            lbl_vortex = self.i18n.t("ui.tab_dps.resultados_vortex", default="Vortex")
            self.gui.resultado_vortex.content.value = f"{lbl_vortex}: {vortex:,.0f}"
            if vortex > 0:
                self.gui.resultado_vortex.shader.colors = ["secondary", "primary"]
                self.gui.resultado_vortex.content.color = ft.Colors.WHITE
            else:
                self.gui.resultado_vortex.shader.colors = [ft.Colors.WHITE24, ft.Colors.WHITE24]
                self.gui.resultado_vortex.content.color = ft.Colors.WHITE24
            self.gui.resultado_vortex.update()

        # --- TRADUCCIÓN DEL REPORTE DETALLADO ---
        titulo_rep = self.i18n.t("ui.tab_dps.reporte_titulo", default="REPORTE DE COMBATE DETALLADO").center(60)
        txt_agente = self.i18n.t("ui.tab_dps.agente", default="Agente")
        txt_elemento = self.i18n.t("ui.tab_dps.elemento", default="Elemento")
        txt_rol = self.i18n.t("ui.tab_dps.rol", default="Rol")
        txt_ataque_ev = self.i18n.t("ui.tab_dps.ataque_evaluado", default="Ataque evaluado")

        detalles = f"╔════════════════════════════════════════════════════════════╗\n"
        detalles += f"║{titulo_rep}║\n"
        detalles += f"╠════════════════════════════════════════════════════════════╣\n"
        detalles += f"  {txt_agente}: {self.estado_actual.nombre_agente}\n"
        detalles += f"  {txt_elemento}: {self.elemento.capitalize()} | {txt_rol}: {str(self.tipo).capitalize()}\n"
        detalles += f"  {txt_ataque_ev}: {etiqueta.replace('_', ' ').title()}\n"
        detalles += f"╚════════════════════════════════════════════════════════════╝\n\n"

        def format_stat(k, v):
            k_low = k.lower()
            if any(x in k_low for x in ["%", "crítico", "daño", "tasa", "reduccion", "multiplicador", "aturdimiento", "perforación", "resistencia", "acumulación"]):
                return f"{v:,.2f}%"
            return f"{v:,.2f}"

        txt_fuentes = self.i18n.t("ui.tab_dps.fuentes_stats", default="[ FUENTES DE ESTADÍSTICAS Y EQUIPAMIENTO ]")
        detalles += f"{txt_fuentes}\n"
        detalles += "-" * 60 + "\n"
        
        wengine = self.estado_actual.nombre_wengine
        if wengine != "Ninguno":
            detalles += f" • W-Engine: {wengine} (R{self.estado_actual.refinamiento})\n"
            if self.estado_actual.stacks > 0:
                txt_cargas_activas = self.i18n.t("ui.tab_dps.cargas_activas", default="Cargas activas")
                detalles += f"   └─ {txt_cargas_activas}: {self.estado_actual.stacks}\n"
            
            if wengine in MAPA_WENGINES:
                try:
                    func_w = MAPA_WENGINES[wengine]
                    estado_enemigo_val = self.gui.dd_estado_enemigo.value if hasattr(self.gui, 'dd_estado_enemigo') else "Normal"
                    try:
                        bonos_w = func_w(stats_actuales=stats, refinamiento=self.estado_actual.refinamiento, nombre_agente=self.estado_actual.nombre_agente, stacks=self.estado_actual.stacks, estado_enemigo=estado_enemigo_val)
                    except TypeError:
                        bonos_w = func_w(stats, self.estado_actual.refinamiento, self.estado_actual.nombre_agente, self.estado_actual.stacks)
                    
                    if bonos_w:
                        textos_w = [f"{self.traducir_stat_csv(k)}: +{format_stat(k, v)}" for k, v in bonos_w.items() if v != 0]
                        if textos_w:
                            detalles += f"   {self.i18n.t('misc.aporta', default='└─ Aporta')}: {', '.join(textos_w)}\n"
                except Exception as e:
                    pass

        set1 = self.estado_actual.sets.get('set1', 'Ninguno')
        set2 = self.estado_actual.sets.get('set2', 'Ninguno')
        set3 = self.estado_actual.sets.get('set3', 'Ninguno')
        
        sets_equipados = []
        if set1 != "Ninguno": sets_equipados.append(f"4x {set1}" if set3 == "Ninguno" else f"2x {set1}")
        if set2 != "Ninguno" and set1 != set2: sets_equipados.append(f"2x {set2}")
        if set3 != "Ninguno": sets_equipados.append(f"2x {set3}")

        if sets_equipados:
            txt_sets_discos = self.i18n.t("ui.tab_dps.sets_discos", default="Sets de Discos")
            detalles += f" • {txt_sets_discos}: {', '.join(sets_equipados)}\n"
            if self.estado_actual.set_condicion:
                txt_cond_activa = self.i18n.t("ui.tab_dps.condicion_set", default="Condición Set 4pc: Activa")
                detalles += f"   └─ {txt_cond_activa} \n"
            if self.estado_actual.set_stacks > 0:
                txt_cargas_set = self.i18n.t("ui.tab_dps.cargas_set", default="Cargas Set 4pc")
                detalles += f"   └─ {txt_cargas_set}: {self.estado_actual.set_stacks}\n"

            if set1 != "Ninguno" and set3 == "Ninguno":
                set_norm = self.gestor_stats._normalizar(set1)
                func_set = None
                for k, func in MAPA_EFECTOS_SETS.items():
                    if self.gestor_stats._normalizar(k) == set_norm:
                        func_set = func
                        break
                
                if func_set:
                    try:
                        bonos_set = func_set(stats, elemento=self.elemento, stacks=self.estado_actual.set_stacks, condicion_activa=self.estado_actual.set_condicion, tipo_agente=self.tipo, nombre_agente=self.estado_actual.nombre_agente)
                        if bonos_set:
                            textos_set = [f"{self.traducir_stat_csv(k)}: +{format_stat(k, v)}" for k, v in bonos_set.items() if v != 0]
                            if textos_set:
                                detalles += f"   {self.i18n.t('misc.efecto_4pc', default='└─ Efecto 4pc Activo')}: {', '.join(textos_set)}\n"
                    except Exception:
                        pass

        if self.estado_actual.mindscape > 0:
            detalles += f" • Mindscape: M{self.estado_actual.mindscape}\n"
            if self.estado_actual.nombre_agente in MAPA_MINDSCAPES:
                try:
                    func_m = MAPA_MINDSCAPES[self.estado_actual.nombre_agente]
                    bonos_m = func_m(self.estado_actual.mindscape, stacks=self.estado_actual.mindscape_stacks, condicion_activa=self.estado_actual.mindscape_cond or True, nombre_habilidad=self.estado_actual.nombre_habilidad or "")
                    if bonos_m:
                        textos_m = [f"{self.traducir_stat_csv(k)}: +{format_stat(k, v)}" for k, v in bonos_m.items() if v != 0]
                        if textos_m:
                            detalles += f"   {self.i18n.t('misc.aporta', default='└─ Aporta')}: {', '.join(textos_m)}\n"
                except Exception:
                    pass

        if self.estado_actual.core_activo:
            detalles += f" {self.i18n.t('misc.core_activado', default='• Habilidad Core: Activada (Cargas: {cargas})', cargas=self.estado_actual.core_stacks)}\n"
            if self.estado_actual.nombre_agente in MAPA_CORE:
                try:
                    func_core = MAPA_CORE[self.estado_actual.nombre_agente]
                    try:
                        bonos_c = func_core(condicion_activa=True, nombre_habilidad=self.estado_actual.nombre_habilidad, stats_actuales=stats, stacks=self.estado_actual.core_stacks, tipos_soportes=[])
                    except TypeError:
                        try:
                            bonos_c = func_core(condicion_activa=True, nombre_habilidad=self.estado_actual.nombre_habilidad, stacks=self.estado_actual.core_stacks, stats_actuales=stats)
                        except TypeError:
                            bonos_c = func_core(condicion_activa=True, nombre_habilidad=self.estado_actual.nombre_habilidad)
                    
                    if bonos_c:
                        textos_c = [f"{self.traducir_stat_csv(k)}: +{format_stat(k, v)}" for k, v in bonos_c.items() if v != 0]
                        if textos_c:
                            detalles += f"   {self.i18n.t('misc.aporta', default='└─ Aporta')}: {', '.join(textos_c)}\n"
                except Exception:
                    pass

        detalles += "\n"

        if efectos_activos and len(efectos_activos) > 0:
            txt_buffos = self.i18n.t("ui.tab_dps.buffos_equipo", default="[ BUFFOS DE EQUIPO Y SOPORTES ]")
            detalles += f"{txt_buffos}\n"
            detalles += "-" * 60 + "\n"
            for efecto in efectos_activos:
                if "Set DPS:" in efecto: continue
                efecto_limpio = efecto.replace('\n', ' ')
                detalles += f" • {efecto_limpio}\n"
            detalles += "\n"
        
        txt_stats_finales = self.i18n.t("ui.tab_dps.stats_finales_aplicadas", default="[ ESTADÍSTICAS FINALES APLICADAS AL CÁLCULO ]")
        detalles += f"{txt_stats_finales}\n"
        detalles += "-" * 60 + "\n"

        ofensivas = ["Ataque", "Probabilidad_crítico", "Daño_crítico", "Tasa_de_Perforación", "Perforación_Plana", "Daño_elemental", "Daño_Adicional"]
        anomalia = ["Maestría_Anomalía", "Tasa_de_Anomalía", "Bono_Acumulación", "Sheer_force"]
        multiplicadores = ["Multiplicador_de_ataques", "Aturdimiento", "Stun_DMG_Multiplier", "Unstun_DMG_Multiplier"]
        enemigo = ["Defensa_Base", "Resistencia_porcentual", "Reduccion_DEF_enemigo", "Resistencia_Hielo", "Resistencia_Fuego", "Resistencia_Electrico", "Resistencia_Físico", "Resistencia_Etereo", "Resistencia_Viento"]

        detalles += self.i18n.t("ui_dinamico.header_ofensivos", default="ATRIBUTOS OFENSIVOS:") + "\n"
        for k in ofensivas:
            if k in stats and stats[k] != 0:
                detalles += f"  • {self.traducir_stat_csv(k)}: {format_stat(k, stats[k])}\n"

        detalles += "\n" + self.i18n.t("ui_dinamico.header_anomalia", default="ATRIBUTOS DE ANOMALÍA:") + "\n"
        for k in anomalia:
            if k in stats and stats[k] != 0:
                detalles += f"  • {self.traducir_stat_csv(k)}: {format_stat(k, stats[k])}\n"

        detalles += "\n" + self.i18n.t("ui_dinamico.header_multiplicadores", default="MULTIPLICADORES DE HABILIDAD:") + "\n"
        for k in multiplicadores:
            if k in stats and stats[k] != 0:
                detalles += f"  • {self.traducir_stat_csv(k)}: {format_stat(k, stats[k])}\n"

        detalles += "\n" + self.i18n.t("ui_dinamico.header_enemigo", default="ESTADO DEL ENEMIGO (DEBUFFS):") + "\n"
        for k in enemigo:
            if k in stats and stats[k] != 0:
                detalles += f"  • {self.traducir_stat_csv(k)}: {format_stat(k, stats[k])}\n"

        excluir = ofensivas + anomalia + multiplicadores + enemigo + ["Nivel", "Tipo", "Nombre_Agente", "Etiqueta_Dano", "Estado_Enemigo", "Miasma", "DMG_Taken", "Elementos_Soportes"]
        otras_stats = {k: v for k, v in stats.items() if k not in excluir and v != 0 and not isinstance(v, (str, list)) and not k.startswith("_")}

        if otras_stats:
            detalles += "\n" + self.i18n.t("ui_dinamico.header_stats_finales", default="Stats finales:") + "\n"
            for k, v in otras_stats.items():
                detalles += f"  • {self.traducir_stat_csv(k)}: {format_stat(k, v)}\n"
        
        if "_desglose_texto" in stats:
            detalles += stats["_desglose_texto"]

        self.gui.resultados_text.value = detalles
        self.gui.resultados_text.update()
        self.page.update()

    def guardar_config(self, e):
        nombre_config = self.gui.config_name_field.value.strip()

        if not nombre_config:
            self.mostrar_mensaje(self.i18n.t("ui_dinamico.escribe_nombre_config", default="Escribe un nombre para la configuración."))
            return

        try:
            datos_guardar = self.obtener_estado_actual_dict()
            self.page.client_storage.set(f"build:{nombre_config}", json.dumps(datos_guardar, ensure_ascii=False))
            self._actualizar_indice_builds(nombre_config)
            # Refrescar dropdowns automáticamente sin necesitar "Actualizar lista"
            self._refrescar_dropdowns_builds()
            self.mostrar_mensaje(self.i18n.t('ui_dinamico.config_guardada', default=f"Guardada '{nombre_config}'", nombre=nombre_config))
        except Exception as ex:
            logger.error(f"Error al guardar: {ex}")
            self.mostrar_mensaje(f"Error al guardar: {ex}")

    def _refrescar_dropdowns_builds(self):
        """Recarga las opciones de todos los dropdowns de builds desde client_storage.
        Crea una lista nueva por dropdown para evitar que compartan la misma referencia."""
        try:
            raw = self.page.client_storage.get("build:__indice__")
            nombres = self._safe_json(raw) or []
            # Lista independiente por cada dropdown (misma referencia = bug en Flet)
            def _opciones():
                return [ft.dropdown.Option(n) for n in nombres]
            if hasattr(self.gui, 'archivo_dropdown'):
                self.gui.archivo_dropdown.options = _opciones()
                self.gui.archivo_dropdown.update()
            if hasattr(self.gui, 'dropdown_left'):
                self.gui.dropdown_left.options = _opciones()
                self.gui.dropdown_left.update()
            if hasattr(self.gui, 'dropdown_right'):
                self.gui.dropdown_right.options = _opciones()
                self.gui.dropdown_right.update()
        except Exception as ex:
            logger.error(f"Error refrescando dropdowns builds: {ex}")

    def actualizar_lista_archivos(self, e):
        """Botón manual 'Actualizar lista' — refresca dropdowns y confirma al usuario."""
        self._refrescar_dropdowns_builds()
        self.mostrar_mensaje(self.i18n.t("ui_dinamico.listas_actualizadas", default="Listas actualizadas."))
    
    def cargar_comparacion(self, e, lado):
        """Carga el JSON y llama al renderizador visual de la GUI"""
        dropdown = self.gui.dropdown_left if lado == "left" else self.gui.dropdown_right
        
        nombre_archivo = dropdown.value
        if not nombre_archivo:
            self.mostrar_mensaje(f"Selecciona archivo para el lado {lado}.")
            return

        try:
            raw = self.page.client_storage.get(f"build:{nombre_archivo}")
            datos = self._safe_json(raw)
            if not datos:
                self.mostrar_mensaje(self.i18n.t("ui_dinamico.archivo_no_encontrado", default="Archivo no encontrado."))
                return
            if isinstance(datos, list):
                datos = datos[0] if len(datos) > 0 else {}
            if lado == "left":
                self.datos_comp_left = datos
            else:
                self.datos_comp_right = datos
            self.gui.renderizar_panel_comparacion(lado, datos)
        except Exception as ex:
            self.logger.error(f"Error comparando: {ex}")
            self.mostrar_mensaje(f"Error al leer: {ex}")

    def actualizar_dropdown_abloom(self):
        if not hasattr(self.gui, 'dd_elemento_abloom') or not self.gui.dd_elemento_abloom:
            return

        agente_dps = self.gui.agent_dropdown.value
        agentes_con_abloom = ["Aria", "Vivian", "Grace", "Burnice", "Nangong Yu", "Promeia"]

        if agente_dps not in agentes_con_abloom:
            self.gui.dd_elemento_abloom.visible = False
            self.page.update()
            return

        self.gui.dd_elemento_abloom.visible = True
        elementos_equipo = set()
        
        if self.agentes_data and agente_dps != "Ninguno":
            datos_dps = next((a for a in self.agentes_data if a['Nombre'] == agente_dps), None)
            if datos_dps:
                elemento_dps = datos_dps.get("Elemento", "") or datos_dps.get("elemento", "")
                if elemento_dps:
                    elementos_equipo.add(elemento_dps.capitalize())
                
        if hasattr(self.gui, 'team_controls'):
            for prefijo in ["sup1", "sup2"]:
                nombre_soporte = self.gui.team_controls.get(f"{prefijo}_agente").value
                if nombre_soporte and nombre_soporte != "Ninguno":
                    datos_soporte = next((a for a in self.agentes_data if a['Nombre'] == nombre_soporte), None)
                    if datos_soporte:
                        elemento_soporte = datos_soporte.get("Elemento", "") or datos_soporte.get("elemento", "")
                        if elemento_soporte:
                            elementos_equipo.add(elemento_soporte.capitalize())
                            
        nuevas_opciones = [ft.dropdown.Option("Automático")]
        for elem in elementos_equipo:
            nuevas_opciones.append(ft.dropdown.Option(elem))
            
        self.gui.dd_elemento_abloom.options = nuevas_opciones
        
        valores_permitidos = [opt.key for opt in nuevas_opciones]
        if self.gui.dd_elemento_abloom.value not in valores_permitidos:
            self.gui.dd_elemento_abloom.value = "Automático"
            
        self.gui.dd_elemento_abloom.update()
        self.calcular_dano(None)

    def obtener_estado_actual_dict(self):
        """Empaqueta la configuración actual del Main en un diccionario."""
        import copy
        datos = {
            "agente": self.estado_actual.nombre_agente,
            "wengine": self.estado_actual.nombre_wengine,
            "refinamiento": self.estado_actual.refinamiento,
            "stacks_arma": self.estado_actual.stacks,
            "habilidad": self.estado_actual.nombre_habilidad,
            "sets": self.estado_actual.sets.copy(),
            "set_stacks": self.estado_actual.set_stacks,
            "set_condicion": self.estado_actual.set_condicion,       
            "discos": self.estado_actual.discos.copy(), 
            "discos_detalles": copy.deepcopy(self.estado_actual.discos_detalles) if hasattr(self.estado_actual, 'discos_detalles') else {},
            "substats_counts": self.estado_actual.substats_counts.copy(),        
            "stats_manuales": {k: v.value for k, v in self.gui.entry_vars.items()},
            "bonos_manuales_reales": self.estado_actual.bonos_manuales_planos.copy(),
            "buffs_combate": {k: v.value for k, v in self.gui.buff_vars.items()},
            "mindscape": self.estado_actual.mindscape,
            "elemento_abloom": self.gui.dd_elemento_abloom.value if hasattr(self.gui, 'dd_elemento_abloom') else "Automático",
            "potencial": getattr(self.estado_actual, 'nivel_potencial', 0),
            "core_activo": getattr(self.estado_actual, 'core_activo', False),
            "core_stacks": getattr(self.estado_actual, 'core_stacks', 0),
            "elemento": self.elemento or "",
        }
        
        stats_reales = getattr(self, 'ultimos_stats_calculados', {}).copy()
        
        for key, field in self.gui.entry_vars.items():
            stats_reales[key] = self._parse_valor(field.value)
        for key, field in self.gui.buff_vars.items():
            stats_reales[key] = self._parse_valor(field.value)

        if hasattr(self.gui, 'dd_miasma') and self.gui.dd_miasma.value == "Activo":
            stats_reales['Miasma'] = 1.8
            stats_reales['DMG_Taken'] = stats_reales.get('DMG_Taken', 0.0) - 25.0
        else:
            stats_reales['Miasma'] = 1.0
            
        if self.estado_actual.nombre_habilidad in self.habilidades_agente:
            datos_hab = self.habilidades_agente[self.estado_actual.nombre_habilidad]
            stats_reales['Etiqueta_Dano'] = datos_hab.get('Etiqueta_Dano', 'normal')
        else:
            stats_reales['Etiqueta_Dano'] = 'normal'
            
        if hasattr(self.gui, 'dd_estado_enemigo'):
             stats_reales['Estado_Enemigo'] = self.gui.dd_estado_enemigo.value

        datos["_stats_reales_calculo"] = stats_reales
        
        equipo = []
        for prefijo in ["sup1", "sup2"]:
            agente_ctrl = self.gui.team_controls.get(f"{prefijo}_agente")
            agente_val = agente_ctrl.value if agente_ctrl else "Ninguno"
            if agente_val and agente_val != "Ninguno":
                m_ctrl = self.gui.team_controls.get(f"{prefijo}_mindscape")
                m_val = m_ctrl.value if m_ctrl else "0"
                r_ctrl = self.gui.team_controls.get(f"{prefijo}_wengine_ref")
                r_val = r_ctrl.value if r_ctrl else "1"
                w_ctrl = self.gui.team_controls.get(f"{prefijo}_wengine")
                w_val = w_ctrl.value if w_ctrl else "Ninguno"
                equipo.append({
                    "agente": agente_val,
                    "mindscape": m_val,
                    "refinamiento": r_val,
                    "wengine": w_val
                })
        datos["equipo"] = equipo
        
        return datos

    def transferir_datos(self, e, accion):
        """
        Transfiere datos y MANTIENE el nombre de la build.
        """
        def preparar_paquete_inteligente():
            datos = self.obtener_estado_actual_dict()
            stats_reales = datos["_stats_reales_calculo"]
            
            d_elem = stats_reales.get("Daño_elemental", 0)
            d_adic = stats_reales.get("Daño_Adicional", 0)
            d_after = stats_reales.get("Daño_Aftershock", 0)
            datos["stats_manuales"]["Daño_elemental"] = d_elem + d_adic + d_after
            
            if getattr(self, 'meta_nombre_actual', None):
                datos["_meta_nombre"] = self.meta_nombre_actual
            
            if hasattr(self, 'datos_importados_temp') and self.datos_importados_temp:
                if "discs" in self.datos_importados_temp:
                    datos["_discos_json"] = self.datos_importados_temp.get("discs", [])
                    datos["_nombre_importado"] = self.datos_importados_temp.get("name", "")
                else:
                    print(f"DEBUG preparar_paquete: datos_importados_temp existe pero NO tiene 'discs'. Keys: {list(self.datos_importados_temp.keys())}")
            elif "discos_detalles" in datos:
                discos_json = self._convertir_discos_detalles_a_json(datos)
                if discos_json:
                    datos["_discos_json"] = discos_json
                    datos["_nombre_importado"] = datos.get("agente", "")
            else:
                print(f"DEBUG preparar_paquete: NO hay datos_importados_temp ni discos_detalles")
            
            return datos

        if accion == "main_to_left":
            datos = preparar_paquete_inteligente()
            self.datos_comp_left = datos
            self.gui.renderizar_panel_comparacion("left", datos)
            self.mostrar_mensaje(self.i18n.t("ui_dinamico.enviado_izquierda", default="Enviado a Izquierda."))
            
        elif accion == "main_to_right":
            datos = preparar_paquete_inteligente()
            self.datos_comp_right = datos
            self.gui.renderizar_panel_comparacion("right", datos)
            self.mostrar_mensaje(self.i18n.t("ui_dinamico.enviado_derecha", default="Enviado a Derecha."))

        elif accion == "left_to_main":
            if not self.datos_comp_left:
                self.mostrar_mensaje(self.i18n.t("ui_dinamico.vacio", default="Vacío."))
                return
            if hasattr(self.gui, "cache_datos_left") and self.gui.cache_datos_left:
                 nombre_cache = self.gui.cache_datos_left.get("_meta_nombre")
                 if nombre_cache:
                     self.meta_nombre_actual = nombre_cache
            self._cargar_inteligente(self.datos_comp_left)
            self.mostrar_mensaje(self.i18n.t("ui_dinamico.cargado_izquierda", default="Cargado desde Izquierda."))
            self.tabs_control.selected_index = 0
            self.page.update()
            
        elif accion == "right_to_main":
            if not self.datos_comp_right:
                self.mostrar_mensaje("Vacío.")
                return
            if hasattr(self.gui, "cache_datos_right") and self.gui.cache_datos_right:
                 nombre_cache = self.gui.cache_datos_right.get("_meta_nombre")
                 if nombre_cache:
                     self.meta_nombre_actual = nombre_cache
            self._cargar_inteligente(self.datos_comp_right)
            self.mostrar_mensaje(self.i18n.t("ui_dinamico.cargado_derecha", default="Cargado desde Derecha."))
            self.tabs_control.selected_index = 0
            self.page.update()

    def _cargar_inteligente(self, datos):
        """Detecta si es formato interno o externo y lo carga en el Main"""

        es_interno = "agente" in datos
        
        if es_interno:
            print("DEBUG: Cargando formato INTERNO...")
            self._cargar_formato_interno(datos)
        else:
            print("DEBUG: Cargando formato EXTERNO (API)...")
            self._cargar_formato_externo(datos)

    def generar_resumen_texto(self, datos):
        """Extrae datos del JSON y crea un string bonito para mostrar"""
        lines = []
        
        es_externo = "character" in datos or "discs" in datos
        
        if es_externo:
            nombre = datos.get("name") or datos.get("character", {}).get("name", "Desc.")
            arma = datos.get("weapon", {}).get("name", "Ninguno")
            lines.append(f"AGENTE: {nombre}")
            lines.append(f"ARMA: {arma}")
            lines.append("-" * 20)
            discos = datos.get("discs", [])
            lines.append(f"Discos equipados: {len(discos)}")
            
        else:
            lines.append(f"AGENTE: {datos.get('agente', '-')}")
            lines.append(f"ARMA: {datos.get('wengine', '-')}")
            lines.append(f"Ref: {datos.get('refinamiento', 1)} | Stacks: {datos.get('stacks_arma', 0)}")
            lines.append(f"Habilidad: {datos.get('habilidad', '-')}")
            lines.append("-" * 20)
            
            sets = datos.get("sets", {})
            lines.append(f"SETS: {sets.get('set1')} / {sets.get('set2')}")
            
            lines.append("-" * 20)
            lines.append("DISCOS MAIN STATS:")
            discos = datos.get("discos", {})
            for k, v in discos.items():
                lines.append(f"  [{k}]: {v}")
                
            lines.append("-" * 20)
            lines.append("SUBSTATS (Rolls):")
            subs = datos.get("substats_counts", {})
            for k, v in subs.items():
                if v > 0:
                    lines.append(f"  {k}: {v}")
        
        lines.append("\n" + "="*20)
        lines.append("NOTA: Para ver el daño total")
        lines.append("carga esta build en la pestaña principal.")
        
        return "\n".join(lines)

    @staticmethod
    def _safe_json(raw):
        """Deserializa raw de client_storage independientemente de si ya es dict o sigue siendo str."""
        if raw is None:
            return None
        if isinstance(raw, (dict, list)):
            return raw
        try:
            return json.loads(raw)
        except Exception:
            return None

    def cargar_config(self, e):
        nombre_archivo = self.gui.archivo_dropdown.value
        if not nombre_archivo:
            self.mostrar_mensaje(self.i18n.t("ui_dinamico.selecciona_archivo_primero", default="Selecciona un archivo primero."))
            return

        try:
            raw = self.page.client_storage.get(f"build:{nombre_archivo}")
            datos = self._safe_json(raw)
            if not datos:
                self.mostrar_mensaje("Archivo no encontrado.")
                return
            self._cargar_inteligente(datos)
            self.meta_nombre_actual = nombre_archivo
            self.mostrar_mensaje(f"✅ Cargado: {nombre_archivo}")
        except Exception as ex:
            self.mostrar_mensaje(f"Error al cargar: {ex}")

    def _cargar_formato_interno(self, datos):
        agente = datos.get("agente", "Ninguno")
        self.gui.agent_dropdown.value = agente
        self.cargar_agente(agente) 

        wengine = datos.get("wengine", "Ninguno")
        self.gui.wengine_dropdown.value = wengine
        self.cargar_wengine(wengine) 

        ref = str(datos.get("refinamiento", 1))
        stacks_arma = str(datos.get("stacks_arma", 0))
        self.gui.refinamiento_dropdown.value = ref
        self.estado_actual.refinamiento = int(ref)
        if self.gui.stacks_dropdown.visible:
            self.gui.stacks_dropdown.value = stacks_arma
            self.estado_actual.stacks = int(stacks_arma)

        habilidad = datos.get("habilidad")
        if habilidad:
            self.gui.habilidad_dropdown.value = habilidad
            self.estado_actual.nombre_habilidad = habilidad
            self.manejador_habilidad(type('obj', (object,), {'control': type('c', (object,), {'value': habilidad})}))

        set_stacks = str(datos.get("set_stacks", 0))
        set_cond = datos.get("set_condicion", False)
        
        if hasattr(self.gui, 'dd_elemento_abloom'):
            self.gui.dd_elemento_abloom.value = datos.get("elemento_abloom", "Automático")
        if self.gui.set_stacks_dropdown.visible:
            self.gui.set_stacks_dropdown.value = set_stacks
            self.estado_actual.set_stacks = int(set_stacks)
        if self.gui.set_checkbox.visible:
            self.gui.set_checkbox.value = set_cond
            self.estado_actual.set_condicion = set_cond

        m_count = int(datos.get("mindscape", 0))
        self.estado_actual.mindscape = m_count
        if hasattr(self.gui, 'mindscape_dropdown'):
            self.gui.mindscape_dropdown.value = str(m_count)
            self.gui.mindscape_dropdown.update()
        self.actualizar_visibilidad_stacks_agente()

        for i in range(1, 7):
            self.estado_actual.discos_detalles[i]["set"] = "Ninguno"
            self.estado_actual.discos_detalles[i]["main"] = "Vida Plana" if i == 1 else "Ataque Plano" if i == 2 else "Defensa Plana" if i == 3 else "Ninguno"
            if f"disco_{i}_set" in self.gui.team_controls:
                self.gui.team_controls[f"disco_{i}_set"].value = "Ninguno"
                self.actualizar_imagen_disco_ui(i, "Ninguno")
            if i in [4, 5, 6] and f"disco_{i}_main" in self.gui.team_controls:
                self.gui.team_controls[f"disco_{i}_main"].value = "Ninguno"
            for j in range(1, 5):
                self.estado_actual.discos_detalles[i]["subs"][j]["stat"] = "Ninguno"
                self.estado_actual.discos_detalles[i]["subs"][j]["rolls"] = 0
                if f"disco_{i}_sub_{j}_stat" in self.gui.team_controls:
                    self.gui.team_controls[f"disco_{i}_sub_{j}_stat"].value = "Ninguno"
                    self.gui.team_controls[f"disco_{i}_sub_{j}_rolls"].value = "0"

        discos_detalles_guardados = datos.get("discos_detalles", {})
        if discos_detalles_guardados:
            for slot_str, info in discos_detalles_guardados.items():
                slot_int = int(slot_str)
                if slot_int < 1 or slot_int > 6: continue
                
                set_val = info.get("set", "Ninguno")
                self.estado_actual.discos_detalles[slot_int]["set"] = set_val
                if f"disco_{slot_int}_set" in self.gui.team_controls:
                    self.gui.team_controls[f"disco_{slot_int}_set"].value = set_val
                    self.actualizar_imagen_disco_ui(slot_int, set_val)

                main_val = info.get("main", "Ninguno")
                self.estado_actual.discos_detalles[slot_int]["main"] = main_val
                if slot_int in [4, 5, 6] and f"disco_{slot_int}_main" in self.gui.team_controls:
                    self.gui.team_controls[f"disco_{slot_int}_main"].value = main_val
                
                subs_guardadas = info.get("subs", {})
                for sub_idx_str, sub_info in subs_guardadas.items():
                    sub_idx = int(sub_idx_str)
                    if sub_idx < 1 or sub_idx > 4: continue
                    
                    stat_val = sub_info.get("stat", "Ninguno")
                    rolls_val = sub_info.get("rolls", 0)
                    
                    self.estado_actual.discos_detalles[slot_int]["subs"][sub_idx]["stat"] = stat_val
                    self.estado_actual.discos_detalles[slot_int]["subs"][sub_idx]["rolls"] = rolls_val
                    
                    if f"disco_{slot_int}_sub_{sub_idx}_stat" in self.gui.team_controls:
                        self.gui.team_controls[f"disco_{slot_int}_sub_{sub_idx}_stat"].value = stat_val
                        self.gui.team_controls[f"disco_{slot_int}_sub_{sub_idx}_rolls"].value = str(rolls_val)
        else:
            self.estado_actual.substats_counts.clear()
            for key, val in datos.get("substats_counts", {}).items():
                self.estado_actual.substats_counts[key] = val
                
            s1 = datos.get("sets", {}).get("set1", "Ninguno")
            s2 = datos.get("sets", {}).get("set2", "Ninguno")
            discos_viejos = datos.get("discos", {})
            
            for slot_int in range(1, 7):
                set_asignar = s1 if slot_int <= 4 else s2
                if set_asignar == "Ninguno" and s2 != "Ninguno": set_asignar = s2
                
                self.estado_actual.discos_detalles[slot_int]["set"] = set_asignar
                if f"disco_{slot_int}_set" in self.gui.team_controls:
                    self.gui.team_controls[f"disco_{slot_int}_set"].value = set_asignar
                    self.actualizar_imagen_disco_ui(slot_int, set_asignar)
                    
                if slot_int in [4, 5, 6]:
                    main_val = discos_viejos.get(str(slot_int), discos_viejos.get(slot_int, "Ninguno"))
                    self.estado_actual.discos_detalles[slot_int]["main"] = main_val
                    if f"disco_{slot_int}_main" in self.gui.team_controls:
                        self.gui.team_controls[f"disco_{slot_int}_main"].value = main_val

        for slot_int in range(1, 7):
            if f"disco_{slot_int}_set" in self.gui.team_controls:
                self.gui.team_controls[f"disco_{slot_int}_set"].update()
            if slot_int in [4, 5, 6] and f"disco_{slot_int}_main" in self.gui.team_controls:
                self.gui.team_controls[f"disco_{slot_int}_main"].update()
            for sub_idx in range(1, 5):
                if f"disco_{slot_int}_sub_{sub_idx}_stat" in self.gui.team_controls:
                    self.gui.team_controls[f"disco_{slot_int}_sub_{sub_idx}_stat"].update()
                    self.gui.team_controls[f"disco_{slot_int}_sub_{sub_idx}_rolls"].update()
                    
        self.estado_actual.bonos_manuales_planos.clear()
        bonos_reales = datos.get("bonos_manuales_reales", {})
        for k, v in bonos_reales.items():
            self.estado_actual.bonos_manuales_planos[k] = float(v)

        buffs_guardados = datos.get("buffs_combate", {})
        for k, v in buffs_guardados.items():
            if k in self.gui.buff_vars:
                self.gui.buff_vars[k].value = str(v)
        
        if "_discos_json" in datos:
            self.datos_importados_temp = {
                "discs": datos["_discos_json"],
                "name": datos.get("_nombre_importado", datos.get("agente", ""))
            }

            if hasattr(self.gui, '_cache_discos_json'):
                self.gui._cache_discos_json = {
                    "agente": datos.get("agente", ""),
                    "discos": datos["_discos_json"]
                }

        elif "discos_detalles" in datos:
            discos_json = self._convertir_discos_detalles_a_json(datos)
            if discos_json:
                self.datos_importados_temp = {
                    "discs": discos_json,
                    "name": datos.get("agente", "")
                }
                if hasattr(self.gui, '_cache_discos_json'):
                    self.gui._cache_discos_json = {
                        "agente": datos.get("agente", ""),
                        "discos": discos_json
                    }
        else:
            print(f"DEBUG _cargar_formato_interno: NO hay _discos_json en datos. Keys: {list(datos.keys())[:10]}")



        self.actualizar_ui_completa()

    def _convertir_discos_detalles_a_json(self, datos):
        """
        Convierte el formato interno discos_detalles al formato JSON externo
        para visualización en el panel de recomendaciones.
        """
        discos_detalles = datos.get("discos_detalles", {})
        if not discos_detalles:
            return []
        
        MAPA_SETS_NOMBRES_A_ID = {
            "Jazz caótico": 31800, "Metal colmilludo": 32600, "Metal eléctrico": 32400,
            "Metal caótico": 32300, "Metal infernal": 32200, "Metal Polar": 32500,
            "Balada de la rama y la espada": 32700, "Fábula Yunkui": 33100,
            "Punk Hormonal": 31400, "Tecno Pícido": 31000, "Voz Astral": 32800,
            "Jazz Oscilante": 31600, "Armonía Umbría": 32900, "Tecno Tetraodóntido": 31100,
            "Floración del alba": 33300, "Monarca del Pináculo": 33200,
            "Nana a la Luz Cenicienta": 33400, "Melodía de Phaeton": 33000,
            "Proto Punk": 31900, "Disco sacudestrellas": 31200, "Aria Radiante": 33600,
            "Balada de Aguas Blancas": 33500, "Blues Libre": 31300, "Rock espiritual": 31500,
            "Conejo en el país de las maravillas": 33700, "Diario de una prisionera": 33800
        }
        
        MAPA_STATS_INTERNO_A_API = {
            "Ataque_porcentual": "Percent ATK",
            "Ataque_plano": "ATK",
            "Puntos_Vida_porcentual": "Percent HP",
            "Puntos_Vida_plano": "HP",
            "Defensa_porcentual": "Percent DEF",
            "Defensa_plano": "DEF",
            "Probabilidad_crítico_porcentual": "CRIT Rate",
            "Daño_crítico_porcentual": "CRIT DMG",
            "Tasa_de_Perforación_porcentual": "PEN Ratio",
            "Perforación_Plana_plano": "PEN",
            "Maestría_Anomalía_plano": "Anomaly Proficiency",
            "Recuperación_energía_porcentual": "Energy Regen",
            "Daño_crítico": "CRIT DMG",
            "Tasa_de_Perforación": "PEN Ratio",
            "Ataque": "Percent ATK"
        }
        
        VALORES_BASE = {
            "ATK": 19, "HP": 112, "DEF": 15,
            "Percent ATK": 3.0, "Percent HP": 3.0, "Percent DEF": 4.8,
            "CRIT Rate": 2.4, "CRIT DMG": 4.8,
            "PEN Ratio": 2.4, "PEN": 9,
            "Anomaly Proficiency": 9, "Energy Regen": 1.2
        }
        
        discos_json = []
        
        for slot_str, disco_info in discos_detalles.items():
            slot_num = int(slot_str)
            if slot_num < 1 or slot_num > 6:
                continue
            
            nombre_set = disco_info.get("set", "Ninguno")
            if nombre_set == "Ninguno":
                continue
            
            set_id = MAPA_SETS_NOMBRES_A_ID.get(nombre_set, 0)
            main_stat_interno = disco_info.get("main", "")
            main_stat_api = MAPA_STATS_INTERNO_A_API.get(main_stat_interno, main_stat_interno)
            
            if slot_num <= 3:
                valores_fijos = {1: 2660, 2: 434, 3: 84}
                main_value = valores_fijos.get(slot_num, 0)
            else:
                valores_main = {
                    "CRIT DMG": 48.0, "CRIT Rate": 24.0,
                    "PEN Ratio": 24.0, "Percent ATK": 30.0,
                    "Percent HP": 30.0, "Percent DEF": 48.0,
                    "Anomaly Proficiency": 30.0, "Energy Regen": 30.0
                }
                main_value = valores_main.get(main_stat_api, 0)
            
            sub_stats_json = []
            subs_dict = disco_info.get("subs", {})
            
            for sub_idx_str, sub_info in subs_dict.items():
                stat_interno = sub_info.get("stat", "Ninguno")
                if stat_interno == "Ninguno":
                    continue
                
                rolls = sub_info.get("rolls", 0)
                total_rolls = rolls + 1
                
                stat_api = MAPA_STATS_INTERNO_A_API.get(stat_interno, stat_interno)
                valor_base = VALORES_BASE.get(stat_api, 0)
                valor_total = valor_base * total_rolls
                
                if "Percent" in stat_api or stat_api in ["CRIT Rate", "CRIT DMG", "PEN Ratio", "Energy Regen"]:
                    valor_str = f"{valor_total:.1f}%"
                else:
                    valor_str = str(int(valor_total))
                
                sub_stats_json.append({
                    "name": stat_api,
                    "value": valor_str
                })

            if slot_num <= 3:
                main_value_str = str(int(main_value))
            else:
                main_value_str = f"{main_value:.1f}%"
            
            disco_json = {
                "slot": slot_num,
                "set_id": set_id,
                "brand": nombre_set,
                "main_stat": {
                    "name": main_stat_api,
                    "value": main_value_str
                },
                "sub_stats": sub_stats_json
            }
            
            discos_json.append(disco_json)
        
        return discos_json

    def _cargar_formato_externo(self, datos):
        self.logger.info("Iniciando importación inteligente desde JSON externo...")

        self.datos_importados_temp = datos
        nombre_agente = datos.get("name")
        if not nombre_agente:
            nombre_agente = datos.get("character", {}).get("name", "Ninguno")

        self.gui.agent_dropdown.value = nombre_agente
        self.cargar_agente(nombre_agente)

        # Desactivar filtro de compatibilidad para poder cargar cualquier arma
        filtro_previo = self.gui.chk_filtro_wengine.value
        arma_data = datos.get("weapon", {})
        nombre_arma = arma_data.get("name", "Ninguno")

        if nombre_arma != "Ninguno" and nombre_arma not in [o.key for o in self.gui.wengine_dropdown.options]:
            self.gui.chk_filtro_wengine.value = False
            self.actualizar_lista_wengines()

        self.gui.wengine_dropdown.value = nombre_arma
        self.cargar_wengine(nombre_arma)

        # Restaurar filtro
        if self.gui.chk_filtro_wengine.value != filtro_previo:
            self.gui.chk_filtro_wengine.value = filtro_previo
            self.gui.chk_filtro_wengine.update()
        ref = int(arma_data.get("refinement", 1))
        if ref < 1: ref = 1
        if ref > 5: ref = 5
        self.gui.refinamiento_dropdown.value = str(ref)
        self.estado_actual.refinamiento = ref
        self.gui.refinamiento_dropdown.update()

        for i in range(1, 7):
            self.estado_actual.discos_detalles[i]["set"] = "Ninguno"
            self.estado_actual.discos_detalles[i]["main"] = "Vida Plana" if i == 1 else "Ataque Plano" if i == 2 else "Defensa Plana" if i == 3 else "Ninguno"
            
            if f"disco_{i}_set" in self.gui.team_controls:
                self.gui.team_controls[f"disco_{i}_set"].value = "Ninguno"
            if i in [4, 5, 6] and f"disco_{i}_main" in self.gui.team_controls:
                self.gui.team_controls[f"disco_{i}_main"].value = "Ninguno"
            
            for j in range(1, 5):
                self.estado_actual.discos_detalles[i]["subs"][j]["stat"] = "Ninguno"
                self.estado_actual.discos_detalles[i]["subs"][j]["rolls"] = 0
                if f"disco_{i}_sub_{j}_stat" in self.gui.team_controls:
                    self.gui.team_controls[f"disco_{i}_sub_{j}_stat"].value = "Ninguno"
                    self.gui.team_controls[f"disco_{i}_sub_{j}_rolls"].value = "0"

        discos_json = datos.get("discs", [])
        for disco in discos_json:
            slot = int(disco.get("slot", 0))
            if slot < 1 or slot > 6: continue

            nombre_set = "Ninguno"
            if "set_id" in disco:
                set_id = int(disco.get("set_id"))
                nombre_set = MAPA_SETS_ID.get(set_id, "Desconocido")
            
            if nombre_set == "Desconocido" or nombre_set == "Ninguno":
                brand = disco.get("brand")
                if brand:
                    nombre_set = MAPA_SETS_JSON.get(brand, brand)

            self.estado_actual.discos_detalles[slot]["set"] = nombre_set
            if f"disco_{slot}_set" in self.gui.team_controls:
                self.gui.team_controls[f"disco_{slot}_set"].value = nombre_set

            main_stat_data = disco.get("main_stat", {})
            nombre_ingles = main_stat_data.get("name")
            nombre_es = "Ninguno"
            for k, v in MAPA_STATS_JSON.items():
                if k.lower() == str(nombre_ingles).lower():
                    nombre_es = v
                    break
            
            if slot in [4, 5, 6]:
                self.estado_actual.discos_detalles[slot]["main"] = nombre_es
                if f"disco_{slot}_main" in self.gui.team_controls:
                    self.gui.team_controls[f"disco_{slot}_main"].value = nombre_es

            substats = disco.get("sub_stats", [])
            for sub_idx, sub in enumerate(substats, start=1):
                if sub_idx > 4: break

                nombre_ingles_sub = sub.get("name")
                valor_raw = str(sub.get("value", "0"))
                
                es_porcentual = "%" in valor_raw or "Percent" in str(nombre_ingles_sub)
                sufijo = "porcentual" if es_porcentual else "plano"
                valor_limpio = valor_raw.replace("%", "").replace(",", "").strip()
                
                try: valor_float = float(valor_limpio)
                except: continue

                clave_base = None
                for k, v in MAPA_STATS_JSON.items():
                    if k.lower() == str(nombre_ingles_sub).lower():
                        clave_base = v
                        break
                
                unique_key = None
                if clave_base:
                    stats_planas_forzadas = [
                        "Maestría_Anomalía", "Tasa_de_Anomalía", "Impacto", 
                        "Probabilidad_crítico", "Daño_crítico", "Recuperación_energía",
                        "Tasa_de_Perforación", "Perforación_Plana"
                    ]
                    
                    if clave_base in stats_planas_forzadas:
                        if es_porcentual:
                            unique_key = f"{clave_base}_porcentual"
                        else:
                            unique_key = f"{clave_base}_plano"
                            if clave_base == "Maestría_Anomalía": unique_key = "Maestría_Anomalía_plano"
                    else:
                        unique_key = f"{clave_base}_{sufijo}"

                    valor_unitario = 0
                    for item_db in self.substats_db:
                        if item_db['unique_key'] == unique_key:
                            valor_unitario = item_db['valor'] 
                            break
                    
                    if valor_unitario > 0:
                        total_rolls = int(round(valor_float / valor_unitario))
                        rolls_mejoras = max(0, total_rolls - 1) 
                        
                        self.estado_actual.discos_detalles[slot]["subs"][sub_idx]["stat"] = unique_key
                        self.estado_actual.discos_detalles[slot]["subs"][sub_idx]["rolls"] = rolls_mejoras
                        
                        if f"disco_{slot}_sub_{sub_idx}_stat" in self.gui.team_controls:
                            self.gui.team_controls[f"disco_{slot}_sub_{sub_idx}_stat"].value = unique_key
                            self.gui.team_controls[f"disco_{slot}_sub_{sub_idx}_rolls"].value = str(rolls_mejoras)

        try:
            m_count = int(datos.get("mindscape", 0))
            if m_count < 0: m_count = 0
            if m_count > 6: m_count = 6
            self.estado_actual.mindscape = m_count
            self.gui.mindscape_dropdown.value = str(m_count)
            self.gui.mindscape_dropdown.update()
            self.actualizar_visibilidad_stacks_agente()
        except Exception as e:
            self.logger.error(f"Error cargando mindscapes: {e}")

        self.sincronizar_datos_legacy() 
        self.actualizar_ui_completa()
        
        if "discs" in datos and len(datos.get("discs", [])) > 0:
            if hasattr(self.gui, '_cache_discos_json') or True:
                self.gui._cache_discos_json = {
                    "agente": nombre_agente,
                    "discos": datos.get("discs", [])
                }
                print(f"DEBUG _cargar_formato_externo: Caché GUI inicializado con {len(datos['discs'])} discos para {nombre_agente}")
        
        self.mostrar_mensaje(self.i18n.t("ui_dinamico.build_enka_importada", default="¡Build de Enka importada con sus 6 discos!"))

    def calcular_dano_simulado(self, stats_dict, elemento_agente):
        if not stats_dict: return 0, 0, 0, 0, 0, {}

        params = {}
        
        for k, v in stats_dict.items():
            if isinstance(k, str) and k.startswith("_"): continue
            if isinstance(v, str):
                v_clean = v.strip()
                try:
                    params[k] = float(v_clean)
                except ValueError:
                    params[k] = v_clean
            elif isinstance(v, list):
                params[k] = v
            else:
                try:
                    params[k] = float(v)
                except:
                    params[k] = v

        if 'Multiplicador_de_ataques' not in params:
            params['Multiplicador_de_ataques'] = 100.0
        
        if 'Etiqueta_Dano' not in params:
             params['Etiqueta_Dano'] = 'normal'

        if 'Defensa_Base' not in params:
             params['Defensa_Base'] = params.get('Defensa_Enemigo_Base', 950.0)
        
        if 'Resistencia_porcentual' not in params:
            params['Resistencia_porcentual'] = params.get('Resistencia_Enemigo', 0.0)

        if 'Estado_Enemigo' not in params:
            params['Estado_Enemigo'] = params.get('Estado_Enemigo_Guardado', "Normal")
            
        elementos = ['Fuego', 'Electrico', 'Hielo', 'Físico', 'Etereo']
        for elem in elementos:
            key_res = f"Resistencia_{elem}"
            if key_res not in params:
                params[key_res] = 0.0

        return self.logica_dmg.calcular_todos_danos(params, elemento_agente)

    def mostrar_recomendaciones_en_tab(self, rol, consejos):
        try:
            tab_recomendaciones = self.tabs_control.tabs[4]
            
            mitad = (len(consejos) + 1) // 2
            items_izq = consejos[:mitad]
            items_der = consejos[mitad:]

            def crear_fila(item):
                icono, titulo, subtitulo, color_icon = item
                return ft.Container(
                    content=ft.Row([
                        ft.Icon(icono, color=color_icon, size=28),
                        ft.Column([
                            ft.Text(titulo, weight=ft.FontWeight.BOLD, size=15),
                            ft.Text(subtitulo, size=13, color="outline", selectable=True)
                        ], spacing=4, expand=True)
                    ], alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=ft.padding.symmetric(vertical=15, horizontal=10),
                    border=ft.border.only(bottom=ft.BorderSide(1, "outline")),
                    bgcolor="surface"
                )

            grid_layout = ft.Row([
                ft.Column(controls=[crear_fila(i) for i in items_izq], expand=True, scroll=ft.ScrollMode.AUTO),
                ft.VerticalDivider(width=1, color=ft.Colors.WHITE24),
                ft.Column(controls=[crear_fila(i) for i in items_der], expand=True, scroll=ft.ScrollMode.AUTO)
            ], expand=True, alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.START)

            nuevo_contenido = ft.Column([
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.ANALYTICS, color="secondary"),
                        ft.Text(f"Reporte de Optimización Exacta ({rol})", size=20, weight=ft.FontWeight.BOLD)
                    ]),
                    padding=ft.padding.only(bottom=15, top=10)
                ),
                grid_layout
            ], expand=True, scroll=ft.ScrollMode.AUTO)

            tab_recomendaciones.content = nuevo_contenido
            tab_recomendaciones.update()
            
            self.tabs_control.selected_index = 4
            self.tabs_control.update()
            
        except Exception as e:
            import traceback
            print(f"[ERROR UI] Fallo al inyectar recomendaciones: {traceback.format_exc()}")
            self.mostrar_mensaje(f"Error de interfaz: {e}")

    def generar_recomendaciones(self, e):
        import traceback
        self.mostrar_mensaje(self.i18n.t("ui_dinamico.simulando_millones", default="Simulando millones de posibilidades..."))
        self.page.update()

        try:
            if not hasattr(self.cargador, 'mapa_discos') or not self.cargador.mapa_discos:
                self.cargador.mapa_discos = {}
                try:
                    ruta_discos = os.path.join(self.datos_dir, "discos.csv")
                    if os.path.exists(ruta_discos):
                        with open(ruta_discos, encoding='utf-8-sig') as f:
                            import csv 
                            reader = csv.DictReader(f, delimiter=';')
                            if reader.fieldnames:
                                reader.fieldnames = [name.strip().lower() for name in reader.fieldnames]
                            for row in reader:
                                try:
                                    slot = int(row['slot'])
                                    nombre = row['nombre']
                                    tipo = row['tipo']
                                    valor = float(row['valor'].replace(',', '.'))
                                    self.cargador.mapa_discos[(slot, nombre)] = {'tipo': tipo, 'valor': valor}
                                except: continue 
                except Exception as e_disc:
                    self.logger.error(f"Error cargando mapa_discos: {e_disc}")

            self.gestor_estadisticas.calcular_totales(self.estado_actual, self.cargador.mapa_discos)
            stats_raw = self.gestor_estadisticas.obtener_totales()
            
            stats_finales = stats_raw.copy()
            if "stats_manuales" in stats_raw and isinstance(stats_raw["stats_manuales"], dict):
                stats_finales.update(stats_raw["stats_manuales"])
            
            if hasattr(self, 'gui') and hasattr(self.gui, 'entry_vars'):
                for k_gui, v_field in self.gui.entry_vars.items():
                    try:
                        raw_val = str(v_field.value).strip().replace('%', '').replace(',', '.')
                        if raw_val:
                            val_float = float(raw_val)
                            if val_float > 0: stats_finales[k_gui] = val_float
                    except: pass

            datos_agente = next((a for a in self.agentes_data if a['Nombre'] == self.estado_actual.nombre_agente), {})
            rol_agente = datos_agente.get("Tipo", "Atacante")
            
            etiqueta_actual = "normal"
            if self.estado_actual.nombre_habilidad in self.habilidades_agente:
                 etiqueta_actual = self.habilidades_agente[self.estado_actual.nombre_habilidad].get('Etiqueta_Dano', 'normal')

            estado_enemigo_val = self.gui.dd_estado_enemigo.value if hasattr(self.gui, 'dd_estado_enemigo') else "Normal"
            stacks_core_ui = int(self.gui.core_stacks_dropdown.value or 0) if hasattr(self.gui, 'core_stacks_dropdown') else 0
            kwargs_pasivas = {}
            if hasattr(self.gui, 'controles_pasivas'):
                for key, control in self.gui.controles_pasivas.items():
                    kwargs_pasivas[key] = control.value
            
            base_buffeada = getattr(self, 'stats_base_buffeadas', self.base_stats).copy()
            lista_sets_externos = []
            soportes_nombres = []
            wengines_soportes = []
            
            for prefijo in ["sup1", "sup2"]:
                if f"{prefijo}_agente" in self.gui.team_controls:
                    n_agente = self.gui.team_controls[f"{prefijo}_agente"].value
                    n_arma = self.gui.team_controls[f"{prefijo}_wengine"].value
                    n_set = self.gui.team_controls[f"{prefijo}_set4"].value
                    
                    if n_agente and n_agente != "Ninguno":
                        soportes_nombres.append(n_agente)
                        wengines_soportes.append(n_arma)
                        
                        try: ref_arma = int(self.gui.team_controls[f"{prefijo}_wengine_ref"].value)
                        except: ref_arma = 1
                        try: stacks_arma = int(self.gui.team_controls[f"{prefijo}_wengine_stacks"].value)
                        except: stacks_arma = 0
                        chk_act2 = self.gui.team_controls.get(f"{prefijo}_wengine_activo")
                        if chk_act2 and chk_act2.visible and chk_act2.value == False:
                            stacks_arma = -1
                        try: val_m = int(self.gui.team_controls[f"{prefijo}_mindscape"].value)
                        except: val_m = 0
                        
                        d_agente = next((a for a in self.agentes_data if a['Nombre'] == n_agente), {})
                        
                        stats_soporte = {
                            "Ataque": self._parse_valor(self.gui.team_controls.get(f"{prefijo}_stat_atk").value) if f"{prefijo}_stat_atk" in self.gui.team_controls else 0.0,
                            "Puntos_de_Vida": self._parse_valor(self.gui.team_controls.get(f"{prefijo}_stat_hp").value) if f"{prefijo}_stat_hp" in self.gui.team_controls else 0.0,
                            "Probabilidad_de_crítico": self._parse_valor(self.gui.team_controls.get(f"{prefijo}_stat_crit_rate").value) if f"{prefijo}_stat_crit_rate" in self.gui.team_controls else 0.0,
                            "Daño_crítico": self._parse_valor(self.gui.team_controls.get(f"{prefijo}_stat_crit_dmg").value) if f"{prefijo}_stat_crit_dmg" in self.gui.team_controls else 0.0,
                            "Tasa_de_Perforación": self._parse_valor(self.gui.team_controls.get(f"{prefijo}_stat_pen").value) if f"{prefijo}_stat_pen" in self.gui.team_controls else 0.0,
                            "Tasa_de_Anomalía": self._parse_valor(self.gui.team_controls.get(f"{prefijo}_stat_am").value) if f"{prefijo}_stat_am" in self.gui.team_controls else 0.0,
                            "Maestría_Anomalía": self._parse_valor(self.gui.team_controls.get(f"{prefijo}_stat_ap").value),
                            "Recuperación_energía": self._parse_valor(self.gui.team_controls.get(f"{prefijo}_stat_er").value) if f"{prefijo}_stat_er" in self.gui.team_controls else 0.0,
                            "Impacto": self._parse_valor(self.gui.team_controls.get(f"{prefijo}_stat_imp").value) if f"{prefijo}_stat_imp" in self.gui.team_controls else 0.0
                        }

                        lista_sets_externos.append({
                            "origen": prefijo,
                            "nombre_set": n_set,
                            "nombre_agente": n_agente,
                            "tipo_agente": d_agente.get("Tipo", ""),
                            "elemento_agente": d_agente.get("Elemento", "") or d_agente.get("elemento", ""),
                            "faccion_agente": d_agente.get("Faccion", "") or d_agente.get("Facción", ""),
                            "nombre_arma": n_arma,
                            "refinamiento_arma": ref_arma,
                            "stacks_arma": stacks_arma,
                            "stats": stats_soporte,
                            "mindscape": val_m
                        })
                        
            buffs_nodos_da = {}
            if hasattr(self.gui, 'da_active_buffs') and hasattr(self.gui, 'mapa_stats_da'):
                for stat_ui, valor in self.gui.da_active_buffs.items():
                    clave_logica = self.gui.mapa_stats_da.get(stat_ui)
                    if clave_logica:
                        buffs_nodos_da[clave_logica] = valor
            mejor_build = self.optimizador.encontrar_mejor_build(
                self.estado_actual,
                datos_agente,
                stats_finales,
                etiqueta_dano=etiqueta_actual,
                elemento_input=self.elemento,
                base_stats=self.base_stats,
                stacks_core=stacks_core_ui,
                estado_enemigo=estado_enemigo_val,
                faccion_agente=self.faccion,
                sets_externos=lista_sets_externos,
                soportes_nombres=soportes_nombres,
                wengines_soportes=wengines_soportes,
                buffs_nodos=buffs_nodos_da,
                **kwargs_pasivas
            )

            consejos_limpios = []
            
            if mejor_build:
                proyeccion = None
                try:
                    proyeccion = self.optimizador.simular_proyeccion_realista(
                        mejor_config=mejor_build,
                        elemento=self.elemento,
                        delta_stats=None,
                        rol_agente=rol_agente,
                        nombre_agente=self.estado_actual.nombre_agente,
                        estado_base=self.estado_actual,
                        min_basura=1,
                        etiqueta_dano=etiqueta_actual,
                        ranking_completo=mejor_build.get("ranking_completo", []),
                        base_stats=self.base_stats,
                    )
                except Exception as e_proy:
                    print(f"[!] Aviso: No se pudo generar la proyeccion: {e_proy}")
                
                if proyeccion and proyeccion.get("mensaje"):
                    aumento_proy = proyeccion.get("aumento_pct", 0)
                    titulo_proy  = (f"STATS IDEALES TEÓRICAS (+{aumento_proy:.1f}% DAÑO POTENCIAL)"
                                    if aumento_proy > 0 else "STATS IDEALES TEÓRICAS (Build Óptima)")
                    consejos_limpios.append((
                        ft.Icons.AUTO_FIX_HIGH,
                        titulo_proy,
                        proyeccion["mensaje"],
                        "tertiary"
                    ))

                ranking_completo = mejor_build.get("ranking_completo", [])
                if ranking_completo:
                    top_1_score = ranking_completo[0]["score"]
                    texto_ranking = ""
                    
                    armas_mostradas = set()
                    contador = 0
                    
                    for res in ranking_completo:
                        arma = res["wengine"]
                        if arma not in armas_mostradas:
                            armas_mostradas.add(arma)
                            contador += 1
                            pct = (res["score"] / top_1_score) * 100 if top_1_score > 0 else 0
                            texto_ranking += f"{contador}º {arma}\n    └ {res['sets']} ➔ {pct:.1f}%\n"
                            
                        if contador >= 7:
                            break

                    s = mejor_build.get('stats', {})
                    stats_str = f"ATK: {int(s.get('Ataque', 0))} | CR: {s.get('Probabilidad_crítico', 0):.1f}% | AM: {int(s.get('Maestría_Anomalía', 0))}"

                    consejos_limpios.append((
                        ft.Icons.AUTO_AWESOME, 
                        "RANKING EXACTO DE SIMULACIÓN (Top 7 Armas)", 
                        f"{texto_ranking}\n\nDiscos Recomendados (IV / V / VI): {mejor_build['discos']}\nStats Base Estimadas: {stats_str}",
                        "primary"
                    ))
                else:
                    consejos_limpios.append((
                    ft.Icons.WARNING,
                    "Ranking Incompleto",
                    "No se pudo generar la tabla comparativa de armas en memoria.",
                    "error"
                    ))
            else:
                consejos_limpios.append((
                    ft.Icons.WARNING,
                    "Ranking Incompleto",
                    "No se pudo generar la tabla comparativa de armas en memoria.",
                    "error"
                    ))

            self.mostrar_recomendaciones_en_tab(rol_agente, consejos_limpios)
            self.mostrar_mensaje("¡Análisis completado en Recomendaciones!")

        except Exception as e_main:
            error_trace = traceback.format_exc()
            self.mostrar_mensaje(f"Error crítico, revisa la consola.")
            
            self.mostrar_recomendaciones_en_tab("Fallo Crítico", [(
                ft.Icons.BUG_REPORT,
                "Excepción en el sistema",
                f"{e_main}\nRevisa la consola para más detalles.",
                ft.Colors.RED
            )])

    def ejecutar_analisis_grafico(self, e):
        from modulo_graficas import GeneradorGraficas
        
        if not self.estado_actual.nombre_agente or self.estado_actual.nombre_agente == "Ninguno":
            self.mostrar_mensaje("Selecciona un agente primero para graficar.")
            return

        graficador = GeneradorGraficas(self.logica_dmg, translator=self.i18n.t)
        
        stats_actuales = self.ultimos_stats_calculados.copy()
        if hasattr(self.gui, 'enemy_dropdown'):
            stats_actuales['Nombre_Enemigo'] = self.gui.enemy_dropdown.value

        self.gui.contenedor_grafica_dispersion.content = None
        
        tipo_seleccionado = self.gui.dd_tipo_dano_grafica.value

        grafica = graficador.generar_analisis_buffs_interactivo(
            stats_base=stats_actuales,
            elemento=self.elemento,
            tipo_dano=tipo_seleccionado
        )
        
        self.gui.contenedor_grafica_dispersion.content = grafica
        self.page.update()
        self.mostrar_mensaje(f"¡Análisis de daño {tipo_seleccionado} generado!")

    def boton_generar_tarjeta(self, e):
        import os
        import base64
        from io import BytesIO
        from logica_recomendaciones import CONFIG_ROLES, EXCEPCIONES_AGENTES, evaluar_calidad_global
        from generador_imagenes import GeneradorTarjetas 

        agente_actual = self.estado_actual.nombre_agente
        if not agente_actual or agente_actual == "Ninguno":
            self.mostrar_mensaje(self.i18n.t("ui_dinamico.boton_error_agente", default="¡Error! Selecciona un agente primero."))
            return
        
        stats_principales = {}
        stats_raw = {}
        
        datos_enka = getattr(self, 'datos_importados_temp', {})
        nickname_jugador = str(datos_enka.get("nickname", "Jugador"))
        uid_jugador = str(datos_enka.get("uid", "Sin UID"))


        nivel_agente = "60"
        if datos_enka and "stats" in datos_enka:
            stats_crudas = datos_enka["stats"]
    
            MAPA_ENKA_A_TARJETA = {
                "HP": "Puntos Vida", 
                "ATK": "Ataque", 
                "DEF": "Defensa",
                "Impact": "Impacto", 
                "CRIT Rate": "Prob. Crítica",
                "CRIT DMG": "Daño Crítico", 
                "Anomaly Mastery": "Tasa Anomalía",
                "Anomaly Proficiency": "Maestría Anom.", 
                "PEN Ratio": "Perforación %",
                "Energy Regen": "Recup. Energía",
                "PEN": "Perf. Plana",
                "Sheer Force": "Sheer"
            }
            
            for key_enka, nombre_bonito in MAPA_ENKA_A_TARJETA.items():
                if key_enka in stats_crudas:
                    v_raw = stats_crudas[key_enka]
                    v = float(v_raw.get("value", 0)) if isinstance(v_raw, dict) else float(v_raw)
                    es_decimal = key_enka in ["CRIT Rate", "CRIT DMG", "PEN Ratio", "Energy Regen"]
                    
                    if es_decimal:
                        if v > 100:  
                            v /= 100.0
                        elif 0 < v < 2.0: 
                            v *= 100.0
                            
                    stats_principales[nombre_bonito] = f"{v:.1f}%" if es_decimal else f"{v:.0f}"
                    stats_raw[key_enka] = v
                    
            bono_maximo = 0.0
            for key_cruda, v_raw in stats_crudas.items():
                key_upper = str(key_cruda).upper()
                if "DMG" in key_upper and any(e in key_upper for e in ["PHYSICAL", "FIRE", "ICE", "ELECTRIC", "ETHER"]):
                    v = float(v_raw.get("value", 0)) if isinstance(v_raw, dict) else float(v_raw)
                    
                    if v > 100:
                        v /= 100.0
                    elif 0 < v < 2.0:
                        v *= 100.0
                        
                    if v > bono_maximo:
                        bono_maximo = v
            
            stats_principales["Daño Elem."] = f"{bono_maximo:.1f}%"

        else:
            MAPA_GUI = {
                "Puntos_Vida": "Puntos Vida", "Ataque": "Ataque", "Defensa": "Defensa", 
                "Impacto": "Impacto", "Probabilidad_crítico": "Prob. Crítica",
                "Daño_crítico": "Daño Crítico", "Tasa_de_Anomalía": "Tasa Anomalía", 
                "Maestría_Anomalía": "Maestría Anom.", "Tasa_de_Perforación": "Perforación %",
                "Perforación_Plana": "Perf. Plana", "Recuperación_energía": "Recup. Energía", 
                "Daño_elemental": "Daño Elem.",
                "Sheer_force": "Sheer"
            }
            for stat_gui, nombre_bonito in MAPA_GUI.items():
                if stat_gui in self.gui.entry_vars and self.gui.entry_vars[stat_gui].value:
                    val = float(self.gui.entry_vars[stat_gui].value)
                    es_decimal = stat_gui in ["Probabilidad_crítico", "Daño_crítico", "Tasa_de_Perforación", "Recuperación_energía", "Daño_elemental"]
                    stats_principales[nombre_bonito] = f"{val:.1f}%" if es_decimal else f"{val:.0f}"
                    stats_raw[stat_gui] = val

        ORDEN_DESEADO = [
            "Puntos Vida", 
            "Ataque", 
            "Defensa", 
            "Impacto", 
            "Prob. Crítica", 
            "Daño Crítico", 
            "Tasa Anomalía", 
            "Maestría Anom.", 
            "Perforación %", 
            "Recup. Energía",
            "Perf. Plana",  
            "Daño Elem.",
            "Sheer"
        ]
        
        stats_ordenadas = {}
        for stat_vip in ORDEN_DESEADO:
            if stat_vip in stats_principales:
                stats_ordenadas[stat_vip] = stats_principales[stat_vip]

        stats_principales = stats_ordenadas

        datos_agente = next((a for a in self.agentes_data if a['Nombre'] == agente_actual), {})
        rango_agente = str(datos_agente.get("Rango", datos_agente.get("rango", "S")))
        faccion_agente = str(datos_agente.get("Facción", datos_agente.get("facción", "liebres astutas")))
        rol_agente = datos_agente.get("Tipo", "Atacante")
        config_rol = CONFIG_ROLES.get(rol_agente, CONFIG_ROLES["Atacante"]).copy()
        
        if agente_actual in EXCEPCIONES_AGENTES:
            excep = EXCEPCIONES_AGENTES[agente_actual]
            if "subs" in excep: config_rol["subs"] = excep["subs"]
            if "main_4" in excep: config_rol["main_4"] = excep["main_4"]
            if "main_5" in excep: config_rol["main_5"] = excep["main_5"]
            if "main_6" in excep: config_rol["main_6"] = excep["main_6"]

        def normalizar_stat(key_sucia):
            import unicodedata
            k = str(key_sucia).lower().strip()
            k = ''.join(c for c in unicodedata.normalize('NFD', k) if unicodedata.category(c) != 'Mn')
            es_pct = "%" in k or "porcentual" in k or "tasa" in k or "prob" in k or "dano" in k or "recup" in k or "ratio" in k or "percent" in k or "rate" in k or "dmg" in k
            sufijo = "_porcentual" if es_pct else "_plano"
            base = ''.join([i for i in k.replace("porcentual", "").replace("plano", "").replace("_", "").replace("%", "").replace("+", "") if not i.isdigit()]).strip()
            
            if "ataque" in base or "atk" in base: return f"Ataque{sufijo}"
            if "vida" in base or "hp" in base: return f"Puntos_Vida{sufijo}"
            if "defensa" in base or "def" in base: return f"Defensa{sufijo}"
            if "anomal" in base or "maestria" in base or "prof" in base: return "Maestría_Anomalía_plano"
            if "prob" in base or "rate" in base: return "Probabilidad_crítico_porcentual"
            if "crit" in base and ("dano" in base or "dmg" in base): return "Daño_crítico_porcentual"
            if "pen" in base or "perf" in base: return "Tasa_de_Perforación_porcentual" if "ratio" in base or es_pct else "Perforación_Plana_plano"
            if "recup" in base or "energy" in base or "regen" in base: return "Recuperación_energía_porcentual"
            if "elemental" in base or "fisico" in base or "fuego" in base or "hielo" in base or "electrico" in base or "etereo" in base or "viento" in base or "physical" in base or "fire" in base or "ice" in base or "ether" in base or "wind" in base: return "Daño_elemental"
            if "impact" in base: return "Impacto"
            
            return "Desconocido"

        ideales = {normalizar_stat(k) for k in config_rol["subs"]["ideal"]}
        decentes = {normalizar_stat(k) for k in config_rol["subs"]["decente"]}
        
        MAPA_STATS_TRADUCCION = {
            "HP": "Vida", "ATK": "Ataque", "DEF": "Defensa", "Percent HP": "Vida %", "Percent ATK": "Ataque %", "Percent DEF": "Defensa %",
            "CRIT Rate": "Prob. Crítica", "CRIT DMG": "Daño Crítico", "PEN Ratio": "Perforación %", "Anomaly Proficiency": "Maestría",
            "Anomaly Mastery": "Tasa Anom.", "Energy Regen": "Recup. Energía", "Physical DMG Bonus": "Daño Físico", "Fire DMG Bonus": "Daño Fuego",
            "Ice DMG Bonus": "Daño Hielo", "Electric DMG Bonus": "Daño Eléctrico", "Ether DMG Bonus": "Daño Etéreo", "Wind DMG Bonus": "Daño Viento", "Impact": "Impacto", "PEN": "Perforación"
        }

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

        discos_procesados = []
        puntos_totales_build = 0
        conteo_rolls = {}

        if hasattr(self, 'datos_importados_temp') and self.datos_importados_temp:
            nombre_api = str(self.datos_importados_temp.get("name", "")).lower()
            if nombre_api in agente_actual.lower() or agente_actual.lower() in nombre_api:
                discos_crudos = self.datos_importados_temp.get("discs", [])
                
                MAPA_MAIN_CORTAS = {
                    "CRIT Rate": "CRIT RATE.", "CRIT DMG": "CRIT DMG", 
                    "Anomaly Proficiency": "AP", "PEN Ratio": "PEN RATIO",
                    "Energy Regen": "ER", "PEN": "PEN",
                    "Physical DMG Bonus": "DMG%", "Fire DMG Bonus": "DMG%",
                    "Ice DMG Bonus": "DMG%", "Electric DMG Bonus": "DMG%", "Ether DMG Bonus": "DMG%",
                    "Anomaly Mastery": "AM"
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
                    "Melodía de Phaeton": "Phaethon's Melody",
                    "Metal caótico": "Chaotic Metal",
                    "Metal colmilludo": "Fanged Metal",
                    "Metal infernal": "Inferno Metal",
                    "Metal Polar": "Polar Metal",
                    "Punk Hormonal": "Hormone Punk",
                    "Rock espiritual": "Soul Rock",
                    "Tecno Pícido": "Woodpecker Electro",
                    "Voz Astral": "Astral Voice",
                    "Aria Radiante": "Shining Aria",
                    "Conejo en el país de las maravillas": "Bunny in Wonderland",
                    "Diario de una prisionera": "Notes From the Chained"
                }

                for d in sorted(discos_crudos, key=lambda x: int(x.get("slot", 0))):
                    slot = int(d.get("slot", 0))
                    if slot < 1 or slot > 6: continue
                    
                    nombre_set_original = MAPA_SETS_ID.get(int(d.get("set_id", 0)), d.get("brand", "Desconocido"))
                    nombre_set_corto = MAPA_SETS_CORTOS.get(nombre_set_original, nombre_set_original)
                    
                    main_api = str(d.get("main_stat", {}).get("name", ""))
                    api_upper = main_api.upper()
                    if "DMG" in api_upper and any(elem in api_upper for elem in ["ELECTRIC", "FIRE", "ICE", "ETHER", "PHYSICAL"]):
                        main_trad = "DMG%"
                    else:
                        main_api_limpio = main_api.replace("\xa0", " ").strip()
                        main_trad = MAPA_MAIN_CORTAS.get(main_api_limpio, MAPA_STATS_TRADUCCION.get(main_api_limpio, main_api_limpio))

                    subs_procesados = []
                    rolls_ideales_totales = 0

                    if slot in [4, 5, 6]:
                        main_dict = config_rol.get(f"main_{slot}", {"general": [], "particular": []})
                        main_ideales = [normalizar_stat(s) for s in main_dict.get("general", [])]
                        main_partic = [normalizar_stat(s) for s in main_dict.get("particular", [])]
                        
                        main_api_raw = str(d.get("main_stat", {}).get("name", ""))
                        main_norm = normalizar_stat(main_api_raw)
                        
                        if "DMG Bonus" in main_api_raw:
                            main_norm = "Daño_elemental"
                            
                        if main_norm in main_ideales:
                            rolls_ideales_totales += 2.0
                        elif main_norm in main_partic:
                            rolls_ideales_totales += 1.3
                    
                    for sub in d.get("sub_stats", []):
                        sub_api = sub.get("name", "")
                        sub_trad = MAPA_STATS_TRADUCCION.get(sub_api, sub_api)
                        sub_val_float = float(str(sub.get("value", "0")).replace("%", ""))
                        
                        sub_norm = normalizar_stat(sub_api)
                        rolls = calcular_rolls_substat(sub_norm, sub_val_float)
                        conteo_rolls[sub_norm] = conteo_rolls.get(sub_norm, 0) + rolls
                        
                        color_sub = "#616161"
                        if sub_norm in ideales:
                            color_sub = "#ffc107"
                            rolls_ideales_totales += rolls
                        elif sub_norm in decentes:
                            color_sub = "#00bcd4"
                            
                        val_display = str(sub.get("value", "0"))
                        if "%" not in val_display and ("Percent" in sub_api or "Rate" in sub_api or "DMG" in sub_api or "Ratio" in sub_api):
                            val_display += "%"
                            
                        upgrades = rolls - 1
                        txt_rolls = f"+{upgrades}" if upgrades > 0 else ""
                            
                        subs_procesados.append({"nombre": sub_trad, "valor": val_display, "rolls": txt_rolls, "color": color_sub})
                        
                    puntos_totales_build += rolls_ideales_totales

                    tier = "A"
                    color_tier = "#bdbdbd"
                    if rolls_ideales_totales >= 4:
                        tier = "GODLIKE"
                        color_tier = "#ff003c"
                    elif rolls_ideales_totales == 3:
                        tier = "SSS"
                        color_tier = "#ffea00"
                    elif rolls_ideales_totales == 2:
                        tier = "SS"
                        color_tier = "#00ff2a"
                    
                    discos_procesados.append({
                        "slot": slot, 
                        "set": nombre_set_corto, 
                        "set_original": nombre_set_original,
                        "main_stat": main_trad, 
                        "main_val": str(d.get("main_stat", {}).get("value", "0")), 
                        "tier": tier, "color_tier": color_tier, "subs": subs_procesados
                    })

        if puntos_totales_build >= 40: evaluacion_build = "SSS"
        elif puntos_totales_build >= 35: evaluacion_build = "SS"
        elif puntos_totales_build >= 30: evaluacion_build = "S"
        elif puntos_totales_build >= 25: evaluacion_build = "A+"
        elif puntos_totales_build >= 20: evaluacion_build = "A"
        else: evaluacion_build = "B"

        # DESPUÉS de calcular evaluacion_build y ANTES de datos_tarjeta:

        # =========================================================================
        # OBTENER CALIFICACIÓN DEL RANKING GLOBAL
        # =========================================================================
        calificacion_ranking = None
        breakdown_ranking = None
        posicion_ranking = None
        total_jugadores = None

        if hasattr(self, 'gestor_ranking'):
            try:
                # Buscar mi apodo basándome en el UID actual
                uids = self.gestor_ranking.cargar_uids_guardados()
                mi_apodo = None
                
                for apodo, uid_guardado in uids.items():
                    if uid_guardado == uid_jugador:
                        mi_apodo = apodo
                        break
                
                if mi_apodo:
                    # 👇 EL FIX ESTÁ AQUÍ: Cargar el ranking completo y buscar el apodo 👇
                    ranking_completo = self.gestor_ranking.cargar_ranking_global()
                    datos_jugador = ranking_completo.get(mi_apodo)
                    
                    if datos_jugador:
                        personajes = datos_jugador.get('personajes', {})
                        
                        if agente_actual in personajes:
                            calificacion_ranking = personajes[agente_actual].get('calificacion', None)
                            breakdown_ranking = personajes[agente_actual].get('breakdown', {})
                            
                            # Obtener posición en ranking global (Ya sin el top_n que rompía todo)
                            ranking_personaje = self.gestor_ranking.generar_ranking_por_personaje(agente_actual)
                            total_jugadores_calculado = len(ranking_personaje)
                            
                            for i, (apodo, cal, tier, uid) in enumerate(ranking_personaje, 1):
                                if apodo == mi_apodo:
                                    posicion_ranking = i
                                    total_jugadores = total_jugadores_calculado
                                    break
                                    
                logger.debug(f"[RANKING] Apodo:{mi_apodo} | Agente:{agente_actual} | Pos:{posicion_ranking}/{total_jugadores} | Cal:{calificacion_ranking}")
                
            except Exception as e:
                import traceback
                print(f"🚨 ERROR CRÍTICO OBTENIENDO RANKING 🚨: {e}")
                traceback.print_exc()

        # =========================================================================
        # Ahora sí, crear datos_tarjeta
        # =========================================================================
        datos_tarjeta = {
            "agente": agente_actual,
            "rango_agente": rango_agente,
            "faccion_agente": faccion_agente,
            "evaluacion_build": evaluacion_build,
            "puntos_build": puntos_totales_build,
            "elemento": self.elemento, 
            "tipo": self.tipo,
            "rol": rol_agente, 
            "wengine": self.estado_actual.nombre_wengine,
            "refinamiento": self.estado_actual.refinamiento,
            "stats_principales": stats_principales,
            "discos": discos_procesados,
            "mindscape": self.estado_actual.mindscape,
            "nickname": nickname_jugador,
            "uid": uid_jugador,
            "nivel_agente": nivel_agente,
            "substats_counts": conteo_rolls,
            "_stats_reales_calculo": stats_raw, 
            "eficiencia_arma": getattr(self, 'eficiencia_arma', 100.0),
            
            # NUEVOS DATOS DEL RANKING
            "calificacion_ranking": calificacion_ranking,
            "breakdown_ranking": breakdown_ranking,
            "posicion_ranking": posicion_ranking,
            "total_jugadores": total_jugadores if posicion_ranking else None
        }

        nickname_limpio = nickname_jugador.replace(' ', '_')
        
        if nickname_limpio and nickname_limpio != "Jugador":
            nombre_archivo = f"Build_{agente_actual.replace(' ', '_')}_{nickname_limpio}.png"
        else:
            nombre_archivo = f"Build_{agente_actual.replace(' ', '_')}.png"
        
        # Generar imagen en memoria
        generador = GeneradorTarjetas(self.base_path)
        exito, resultado = generador.generar_build_card(datos_tarjeta, ruta_salida=None)
        
        if exito and isinstance(resultado, BytesIO):
            try:
                # Convertir BytesIO a base64
                imagen_bytes = resultado.getvalue()
                imagen_base64 = base64.b64encode(imagen_bytes).decode('utf-8')
                
                # 1. Crear previsualización de imagen
                imagen_preview = ft.Image(
                    src_base64=imagen_base64,
                    fit=ft.ImageFit.CONTAIN,
                    height=450  # Puedes ajustar el tamaño visual del "coso" aquí
                )

                # 2. Definimos la función para cerrar el pop-up
                def cerrar_dialogo(e):
                    self.page.close(dialogo)

                # 3. Definimos la función para descargar (via API con Content-Disposition: attachment)
                def click_descargar(e, _nombre=nombre_archivo):
                    import httpx
                    try:
                        buf = imagen_bytes if isinstance(imagen_bytes, bytes) else imagen_bytes.getvalue()
                        resp = httpx.post(f"{self.api_base_url}/download/prepare", files={"file": (_nombre, buf, "image/png")}, timeout=10)
                        if resp.status_code != 200:
                            self.mostrar_mensaje(f"❌ Error API: {resp.status_code} - {resp.text}")
                            return
                        dl_id = resp.json()["id"]
                        self.page.launch_url(f"{self.api_base_url}/download/{dl_id}", web_window_name="_blank")
                        self.mostrar_mensaje(f"⬇️ Descargando {_nombre}...")
                    except Exception as ex:
                        self.mostrar_mensaje(f"❌ Error al preparar descarga: {ex}")

                # 4. Construimos la ventana emergente
                dialogo = ft.AlertDialog(
                    title=ft.Text(f"Tarjeta de {agente_actual}"),
                    content=imagen_preview,
                    actions=[
                        # Botón destacado para descargar
                        ft.ElevatedButton(
                            text="Descargar", 
                            icon=ft.Icons.DOWNLOAD, 
                            bgcolor=ft.Colors.BLUE_700, 
                            color=ft.Colors.WHITE,
                            on_click=click_descargar
                        ),
                        # Botón sutil para cerrar
                        ft.TextButton("Cerrar", on_click=cerrar_dialogo)
                    ],
                    # Espaciado a los extremos
                    actions_alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                )

                # 5. Abrimos la ventana en la pantalla actual
                self.page.open(dialogo)
                self.mostrar_mensaje("✅ ¡Tarjeta generada con éxito!")
                
            except Exception as ex:
                import traceback
                traceback.print_exc()
                self.mostrar_mensaje(f"❌ Error al mostrar tarjeta: {ex}")
        else:
            self.mostrar_mensaje(f"❌ Error generando tarjeta: {resultado}")
            
    def _on_save_build_result(self, e: ft.FilePickerResultEvent, default_name):
        """Descarga la build card via API (Content-Disposition: attachment)."""
        try:
            if hasattr(self, '_temp_build_buffer'):
                import httpx
                buf = self._temp_build_buffer
                buf.seek(0)
                filename = getattr(self, '_temp_build_filename', default_name)
                resp = httpx.post(f"{self.api_base_url}/download/prepare", files={"file": (filename, buf.read(), "image/png")})
                dl_id = resp.json()["id"]
                self.page.launch_url(f"{self.api_base_url}/download/{dl_id}", web_window_name="_blank")
                self.mostrar_mensaje(f"⬇️ Descargando {filename}...")
                del self._temp_build_buffer
                if hasattr(self, '_temp_build_filename'):
                    del self._temp_build_filename
        except Exception as ex:
            self.mostrar_mensaje(f"❌ Error al preparar descarga: {ex}")


    def cargar_personajes_para_mejoras_directo(self, e):
        """Carga personajes del UID directamente sin diálogo, y muestra análisis de prioridades de mejora."""
        uid = self.gui.txt_uid_mejoras.value
        
        if not uid or not uid.strip():
            self.mostrar_mensaje(self.i18n.t("ui.mejoras_discos.error_uid", default="❌ Por favor ingresa un UID válido"))
            return
        
        # Mostrar indicador de carga
        self.gui.contenedor_mejoras.controls.clear()
        self.gui.contenedor_mejoras.controls.append(
            ft.Container(
                content=ft.Column([
                    ft.ProgressRing(),
                    ft.Text(self.i18n.t("ui.mejoras_discos.cargando", default="Cargando personajes..."), size=16)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                alignment=ft.alignment.center,
                height=200
            )
        )
        self.gui.contenedor_mejoras.update()
        
        # Obtener datos del UID
        personajes, nickname, mensaje = self.gestor_api.obtener_datos_uid(uid)
        
        if not personajes:
            self.gui.contenedor_mejoras.controls.clear()
            self.gui.contenedor_mejoras.controls.append(
                ft.Container(
                    content=ft.Text(
                        f"❌ {mensaje}",
                        size=16,
                        color=ft.Colors.RED_400
                    ),
                    padding=20
                )
            )
            self.gui.contenedor_mejoras.update()
            return
        
        # Analizar personajes
        from analizador_prioridades import AnalizadorPrioridades
        analizador = AnalizadorPrioridades(self.agentes_data)
        analisis = analizador.analizar_personajes_uid(personajes)
        
        # Mostrar resultados
        self._mostrar_analisis_mejoras(analisis, nickname, uid)
    
    def _mostrar_analisis_mejoras(self, analisis, nickname, uid):
        """Muestra los resultados del análisis de mejoras en la interfaz."""
        self.gui.contenedor_mejoras.controls.clear()

        # ── Header ────────────────────────────────────────────────────────────
        # Agente mejor evaluado para el ícono del perfil
        import os as _os
        agente_mejor = max(analisis, key=lambda a: a.get("score_global", 0)) if analisis else None
        nombre_mejor = agente_mejor["nombre"] if agente_mejor else None

        def _ruta_icone(nombre_ag):
            for ruta in [f"images/Iconos/{nombre_ag}.png", f"images/iconos/{nombre_ag}.png", f"images/{nombre_ag}.png"]:
                if nombre_ag and _os.path.exists(ruta):
                    return ruta
            return None

        ruta_icono = _ruta_icone(nombre_mejor) if nombre_mejor else None

        if ruta_icono:
            icono_perfil = ft.Container(
                content=ft.Image(src=ruta_icono, width=56, height=56, fit=ft.ImageFit.COVER),
                width=56, height=56, border_radius=28,
                clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                border=ft.border.all(2, "primary"),
                shadow=ft.BoxShadow(blur_radius=12, spread_radius=0,
                                    color=ft.Colors.with_opacity(0.4, ft.Colors.PRIMARY)),
            )
        else:
            icono_perfil = ft.Container(
                content=ft.Icon(ft.Icons.PERSON, size=22, color="background"),
                bgcolor="primary",
                padding=ft.padding.all(10),
                border_radius=28,
                shadow=ft.BoxShadow(blur_radius=12, spread_radius=0,
                                    color=ft.Colors.with_opacity(0.4, ft.Colors.PRIMARY))
            )

        # Stats del perfil
        total_agentes  = len(analisis)
        score_promedio = sum(a.get("score_global", 0) for a in analisis) / total_agentes if total_agentes else 0
        urgentes       = sum(1 for a in analisis if a.get("prioridad") == "URGENTE")
        color_prom     = ft.Colors.GREEN_400 if score_promedio >= 75 else (ft.Colors.ORANGE_400 if score_promedio >= 50 else ft.Colors.RED_400)

        header = ft.Container(
            content=ft.Row([
                icono_perfil,
                ft.Column([
                    ft.Text(nickname, size=22, weight="bold"),
                    ft.Text(f"UID: {uid}", size=12, color=ft.Colors.GREY_400),
                ], spacing=1),
                ft.Container(expand=True),
                ft.Column([
                    ft.Row([
                        ft.Text(self.i18n.t("ui.mejoras_discos.agentes", default="Agentes:"), size=11, color=ft.Colors.GREY_500),
                        ft.Text(str(total_agentes), size=13, weight="bold"),
                    ], spacing=6),
                    ft.Row([
                        ft.Text(self.i18n.t("ui.mejoras_discos.promedio", default="Promedio:"), size=11, color=ft.Colors.GREY_500),
                        ft.Text(f"{score_promedio:.1f}%", size=13, weight="bold", color=color_prom),
                    ], spacing=6),
                    ft.Row([
                        ft.Text(self.i18n.t("ui.mejoras_discos.urgentes", default="Urgentes:"), size=11, color=ft.Colors.GREY_500),
                        ft.Text(str(urgentes), size=13, weight="bold",
                                color=ft.Colors.RED_400 if urgentes > 0 else ft.Colors.GREEN_400),
                    ], spacing=6),
                ], spacing=3, horizontal_alignment=ft.CrossAxisAlignment.END),
            ], spacing=14, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.padding.symmetric(horizontal=20, vertical=16),
            bgcolor="surface",
            border_radius=14,
            border=ft.border.all(1, "outline"),
            shadow=ft.BoxShadow(blur_radius=14, spread_radius=0,
                                color=ft.Colors.BLACK26, offset=ft.Offset(0, 3)),
        )
        self.gui.contenedor_mejoras.controls.append(header)

        if not analisis:
            self.gui.contenedor_mejoras.controls.append(
                ft.Text(self.i18n.t("ui.mejoras_discos.sin_personajes",
                                     default="No se encontraron personajes en exposición"), size=16)
            )
            self.gui.contenedor_mejoras.update()
            return

        # ── Panel global de farmeo ─────────────────────────────────────────────
        panel_farmeo = self._crear_panel_farmeo_global(analisis)
        self.gui.contenedor_mejoras.controls.append(panel_farmeo)

        # ── Divider con título ─────────────────────────────────────────────────
        self.gui.contenedor_mejoras.controls.append(
            ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.PERSON_SEARCH, size=16, color="primary"),
                    ft.Text(self.i18n.t("ui.mejoras_discos.analisis_por_agente",
                                         default="Análisis por agente"),
                            size=15, weight="bold", color="primary"),
                ], spacing=8),
                padding=ft.padding.only(top=8, bottom=4),
            )
        )

        # ── Tarjetas por agente ────────────────────────────────────────────────
        for i, agente in enumerate(analisis):
            tarjeta = self._crear_tarjeta_agente_mejora(agente, i + 1)
            self.gui.contenedor_mejoras.controls.append(tarjeta)

        self.gui.contenedor_mejoras.update()

    def _crear_panel_farmeo_global(self, analisis):
        """Panel resumen de dónde farmear — máx 5, solo agentes con mejora real de daño."""
        JEFES_FARMEO = {
            self.i18n.t("ui.mejoras_discos.jefe_1",  default="Un monstruo y un visitante"):   ["Jazz Oscilante",                       "Metal caótico"],
            self.i18n.t("ui.mejoras_discos.jefe_2",  default="Puños y balas"):                ["Punk Hormonal",                        "Metal colmilludo"],
            self.i18n.t("ui.mejoras_discos.jefe_3",  default="Cazador y sabueso"):            ["Disco sacudestrellas",                 "Metal eléctrico"],
            self.i18n.t("ui.mejoras_discos.jefe_4",  default="La torre y el cañón"):          ["Tecno Pícido",                         "Rock espiritual"],
            self.i18n.t("ui.mejoras_discos.jefe_5",  default="El loco y el adepto"):          ["Tecno Tetraodóntido",                  "Metal infernal"],
            self.i18n.t("ui.mejoras_discos.jefe_6",  default="Colmillo y hacha"):             ["Blues Libre",                          "Metal Polar"],
            self.i18n.t("ui.mejoras_discos.jefe_7",  default="El cazador y la bestia"):       ["Jazz caótico",                         "Proto Punk"],
            self.i18n.t("ui.mejoras_discos.jefe_8",  default="Dueto monstruoso"):             ["Balada de la rama y la espada",        "Voz Astral"],
            self.i18n.t("ui.mejoras_discos.jefe_9",  default="Hidalgo y escudero"):           ["Armonía Umbría",                       "Melodía de Phaeton"],
            self.i18n.t("ui.mejoras_discos.jefe_10", default="De boca y espada"):             ["Fábula Yunkui",                        "Monarca del Pináculo"],
            self.i18n.t("ui.mejoras_discos.jefe_11", default="La ley del hierro y rebeldes"): ["Floración del alba",                   "Nana a la Luz Cenicienta"],
            self.i18n.t("ui.mejoras_discos.jefe_12", default="Engaños y baluartes"):          ["Balada de Aguas Blancas",              "Aria Radiante"],
            self.i18n.t("ui.mejoras_discos.jefe_13", default="Cuadriga sometedragones"):      ["Conejo en el país de las maravillas",  "Diario de una prisionera"],
        }

        from logica_recomendaciones import CONFIG_SETS_ROLES, EXCEPCIONES_AGENTES as EXC

        # Acumular puntaje por jefe
        # score_jefe = suma de (100 - score_global) por cada agente que lo necesita
        # Solo agentes con score_global < 80 y prioridad no BAJA
        jefe_score   = {}   # jefe -> puntaje total
        jefe_detalle = {}   # jefe -> [(drop, nombre_agente, score_agente), ...]

        for agente in analisis:
            nombre    = agente['nombre']
            rol       = agente['rol']
            prioridad = agente.get('prioridad', 'BAJA')
            score     = agente.get('score_global', 100)

            # Filtrar: solo agentes que realmente se beneficiarían de mejorar
            if prioridad == 'BAJA' or score >= 80:
                continue

            config_sets = EXC.get(nombre, {}).get("sets", CONFIG_SETS_ROLES.get(rol, {}))
            sets_ideales = set()
            for lista in config_sets.values():
                for s in lista:
                    sets_ideales.add(s[0] if isinstance(s, tuple) else s)

            # También sets que tiene pero con tier bajo
            for slot in range(1, 7):
                info = agente.get('analisis_discos', {}).get(slot, {})
                if info.get('calificacion', 'MID') in ('MID', 'C', 'B'):
                    sn = info.get('set', '')
                    if sn and sn != 'Sin disco':
                        sets_ideales.add(sn)

            ganancia = 100 - score  # cuanto más bajo el score, más urgente

            for jefe, drops in JEFES_FARMEO.items():
                relevantes = [d for d in drops if d in sets_ideales]
                if not relevantes:
                    continue
                jefe_score[jefe] = jefe_score.get(jefe, 0) + ganancia
                if jefe not in jefe_detalle:
                    jefe_detalle[jefe] = []
                for d in relevantes:
                    jefe_detalle[jefe].append((d, nombre, score))

        if not jefe_score:
            return ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.CHECK_CIRCLE, size=18, color=ft.Colors.GREEN_400),
                    ft.Text(self.i18n.t("ui.mejoras_discos.sin_farmeo",
                                         default="✓ No se requiere farmeo adicional"),
                            size=13, color=ft.Colors.GREEN_400),
                ], spacing=10),
                padding=ft.padding.all(18),
                bgcolor="surface",
                border_radius=14,
                border=ft.border.all(1, "outline"),
            )

        # Ordenar por puntaje y tomar top 5
        top5 = sorted(jefe_score.items(), key=lambda x: x[1], reverse=True)[:5]

        # Calcular umbral para definir nivel de urgencia dinámicamente
        scores_vals = [v for _, v in top5]
        max_s = scores_vals[0]
        umbral_urgente    = max_s * 0.65
        umbral_recomend   = max_s * 0.30

        def nivel_color_icono(score_val):
            if score_val >= umbral_urgente:
                return ft.Colors.RED_400,    ft.Icons.PRIORITY_HIGH
            elif score_val >= umbral_recomend:
                return ft.Colors.ORANGE_400, ft.Icons.ARROW_UPWARD
            else:
                return ft.Colors.YELLOW_700, ft.Icons.REMOVE

        import os as _os2
        filas = []
        for jefe, score_val in top5:
            color, icono = nivel_color_icono(score_val)
            detalles = jefe_detalle[jefe]

            # Agrupar por drop → lista de agentes
            por_drop = {}
            for drop, agente_n, ag_score in detalles:
                por_drop.setdefault(drop, []).append((agente_n, ag_score))

            def _icono_agente_farm(nombre_ag, score_ag, size=36):
                """Foto del agente con borde según prioridad."""
                for ruta in [f"images/Iconos/{nombre_ag}.png", f"images/iconos/{nombre_ag}.png", f"images/{nombre_ag}.png"]:
                    if _os2.path.exists(ruta):
                        c_borde = ft.Colors.RED_400 if score_ag < 50 else (ft.Colors.ORANGE_400 if score_ag < 70 else ft.Colors.GREEN_400)
                        return ft.Container(
                            content=ft.Image(src=ruta, width=size, height=size, fit=ft.ImageFit.COVER),
                            width=size, height=size, border_radius=size,
                            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                            border=ft.border.all(2, c_borde),
                            tooltip=f"{nombre_ag} ({score_ag:.0f}%)",
                        )
                return ft.Container(
                    content=ft.Text(nombre_ag[0].upper(), size=12, weight="bold",
                                    color=ft.Colors.WHITE, text_align=ft.TextAlign.CENTER),
                    width=size, height=size, border_radius=size,
                    bgcolor=ft.Colors.GREY_800, alignment=ft.alignment.center,
                    tooltip=f"{nombre_ag} ({score_ag:.0f}%)",
                )

            # Recopilar todos los agentes únicos del jefe (a nivel jefe, no por drop)
            FARM_SZ = 72
            agentes_jefe = {}  # nombre -> score (el peor score si aparece varias veces)
            for drop, agentes in por_drop.items():
                for n, s in agentes:
                    if n not in agentes_jefe or s < agentes_jefe[n]:
                        agentes_jefe[n] = s

            # Ordenar por score ascendente (más urgentes primero)
            todos_jefe = sorted(agentes_jefe.items(), key=lambda x: x[1])

            def _fila_grid(agentes_fila):
                return ft.Row(
                    [_icono_agente_farm(n, s, FARM_SZ) for n, s in agentes_fila],
                    spacing=6, tight=True,
                )

            grid_agentes_jefe = ft.Column(
                [_fila_grid(todos_jefe[i:i+3]) for i in range(0, len(todos_jefe), 3)],
                spacing=6, tight=True,
            )

            # Líneas de sets (solo ícono + nombre, sin repetir agentes)
            lineas_sets = []
            for drop, agentes in por_drop.items():
                ruta_set = f"images/discos/{drop}.png"
                if _os2.path.exists(ruta_set):
                    icono_set = ft.Image(src=ruta_set, width=40, height=40,
                                        fit=ft.ImageFit.CONTAIN, gapless_playback=True)
                else:
                    icono_set = ft.Icon(ft.Icons.ALBUM, size=18, color=color)
                nombre_set_traducido = self.i18n.t(f"sets.{drop}", default=drop)
                lineas_sets.append(
                    ft.Row([
                        ft.Container(
                            content=icono_set,
                            width=44, height=44,
                            bgcolor=ft.Colors.BLACK54,
                            border_radius=22,
                            border=ft.border.all(1, ft.Colors.with_opacity(0.3, color)),
                            alignment=ft.alignment.center,
                            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                        ),
                        ft.Text(nombre_set_traducido, size=11, weight="bold", color=ft.Colors.WHITE),
                    ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER)
                )

            filas.append(
                ft.Container(
                    content=ft.Row([
                        ft.Container(
                            content=ft.Icon(icono, size=14, color=color),
                            bgcolor=ft.Colors.with_opacity(0.15, color),
                            padding=ft.padding.all(6),
                            border_radius=20,
                        ),
                        ft.Column([
                            ft.Text(jefe, size=12, weight="bold", color=color),
                            ft.Row(lineas_sets, spacing=8, wrap=True),
                            ft.Divider(height=6, color=ft.Colors.GREY_800),
                            ft.Row([
                                ft.Container(
                                    content=ft.Text(self.i18n.t("ui.mejoras_discos.badge_urgente", default="🔴 URGENTE"), size=9, weight="bold",
                                                    color=ft.Colors.RED_300),
                                    bgcolor=ft.Colors.with_opacity(0.15, ft.Colors.RED_400),
                                    border_radius=4, padding=ft.padding.symmetric(horizontal=6, vertical=2),
                                ) if any(s < 50 for _, s in todos_jefe) else
                                ft.Container(
                                    content=ft.Text(self.i18n.t("ui.mejoras_discos.badge_prioridad", default="🟠 PRIORIDAD"), size=9, weight="bold",
                                                    color=ft.Colors.ORANGE_300),
                                    bgcolor=ft.Colors.with_opacity(0.15, ft.Colors.ORANGE_400),
                                    border_radius=4, padding=ft.padding.symmetric(horizontal=6, vertical=2),
                                ) if any(s < 70 for _, s in todos_jefe) else
                                ft.Container(
                                    content=ft.Text(self.i18n.t("ui.mejoras_discos.badge_mejora", default="🟢 MEJORA"), size=9, weight="bold",
                                                    color=ft.Colors.GREEN_300),
                                    bgcolor=ft.Colors.with_opacity(0.15, ft.Colors.GREEN_400),
                                    border_radius=4, padding=ft.padding.symmetric(horizontal=6, vertical=2),
                                ),
                                ft.Text(self.i18n.t("ui.mejoras_discos.leyenda_bordes", default="borde rojo <50% · naranja <70% · verde ≥70%"),
                                        size=9, color=ft.Colors.GREY_600, italic=True),
                            ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                            grid_agentes_jefe,
                        ], spacing=4, tight=True, expand=True),
                    ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.START),
                    padding=ft.padding.symmetric(horizontal=12, vertical=10),
                    bgcolor=ft.Colors.with_opacity(0.04, color),
                    border=ft.border.only(left=ft.BorderSide(3, color)),
                    border_radius=8,
                    width=520,
                    height=320,
                )
            )

        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Container(
                        content=ft.Icon(ft.Icons.MAP, size=18, color="background"),
                        bgcolor=ft.Colors.AMBER_700,
                        padding=ft.padding.all(8),
                        border_radius=20,
                        shadow=ft.BoxShadow(blur_radius=10, spread_radius=0,
                                            color=ft.Colors.with_opacity(0.4, ft.Colors.AMBER_700))
                    ),
                    ft.Text(self.i18n.t("ui.mejoras_discos.seccion_farmeo",
                                         default="🗺️ Dónde farmear"),
                            size=16, weight="bold"),
                    ft.Container(expand=True),
                    ft.Container(
                        content=ft.Text(
                            self.i18n.t("ui.mejoras_discos.top5_hint",
                                         default="Top 5 · mayor impacto primero"),
                            size=10, color=ft.Colors.GREY_500, italic=True
                        ),
                    ),
                ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Divider(height=8, color="outline"),
                # Grid 3 columnas x 2 filas de tarjetas
                ft.Column([
                    ft.Row(filas[i:i+3], spacing=10,
                           vertical_alignment=ft.CrossAxisAlignment.START)
                    for i in range(0, len(filas), 3)
                ], spacing=10, tight=True),
            ], spacing=10, tight=True),
            padding=ft.padding.all(20),
            bgcolor="surface",
            border_radius=14,
            border=ft.border.all(1, "outline"),
            shadow=ft.BoxShadow(blur_radius=14, spread_radius=0,
                                color=ft.Colors.BLACK26, offset=ft.Offset(0, 3)),
        )
    
    def _icono_elemento_flet(self, elemento: str, size: int = 18) -> ft.Control:
        """Devuelve un ft.Image con el ícono del elemento o un ícono genérico."""
        import os as _ose
        _mapa_elem = {
            "hielo": "hielo", "ice": "hielo",
            "fuego": "fuego", "fire": "fuego",
            "electrico": "electrico", "electric": "electrico", "eléctrico": "electrico",
            "etereo": "etereo", "ether": "etereo", "etéreo": "etereo",
            "fisico": "fisico", "physical": "fisico", "físico": "fisico",
            "frost": "frost",
        }
        key = _mapa_elem.get(elemento.lower().replace("é","e").replace("í","i").replace("ó","o").replace("ú","u"), elemento.lower())
        ruta = f"images/elementos/{key}.png"
        if _ose.path.exists(ruta):
            return ft.Image(src=ruta, width=size, height=size, fit=ft.ImageFit.CONTAIN, tooltip=elemento)
        return ft.Icon(ft.Icons.CIRCLE, size=size, color=ft.Colors.GREY_600, tooltip=elemento)

    def _icono_rol_flet(self, rol: str, size: int = 18) -> ft.Control:
        """Devuelve un ft.Image con el ícono del rol o un ícono de texto."""
        import os as _osr
        key = rol.lower().replace("é","e").replace("ó","o").replace("ó","o").replace("á","a")
        ruta = f"images/elementos/{key}.png"
        if _osr.path.exists(ruta):
            return ft.Image(src=ruta, width=size, height=size, fit=ft.ImageFit.CONTAIN, tooltip=rol)
        # Fallback: badge de texto pequeño
        _colores_rol = {
            "atacante": ft.Colors.RED_400, "aturdidor": ft.Colors.CYAN_400,
            "anómalo": ft.Colors.ORANGE_400, "anomalo": ft.Colors.ORANGE_400,
            "soporte": ft.Colors.GREEN_400, "ruptura": ft.Colors.PURPLE_400,
        }
        color_r = _colores_rol.get(rol.lower(), ft.Colors.GREY_400)
        return ft.Container(
            content=ft.Text(rol[0].upper(), size=size - 4, weight="bold", color=color_r),
            width=size, height=size, border_radius=size,
            bgcolor=ft.Colors.with_opacity(0.2, color_r),
            alignment=ft.alignment.center, tooltip=rol,
        )

    def _crear_tarjeta_agente_mejora(self, agente, posicion):
        """Crea una tarjeta visual para un agente con su análisis de mejoras."""
        import os
        import random
        nombre = agente['nombre']
        prioridad = agente['prioridad']
        score = agente['score_global']
        calificaciones = agente['calificaciones']
        recomendaciones = agente['recomendaciones']
        sets_equipados = agente['sets_equipados']
        analisis_discos = agente['analisis_discos']
        
        # Obtener color del agente
        COLORES_AGENTES = {
            "Nicole": "#FF7CA4", "Anby": "#DCF921", "Billy": "#FF3B3B",
            "Nekomata": "#F6553B", "Koleda": "#FF7A1A", "Anton": "#FF7A1A",
            "Ben": "#F9951B", "Grace": "#FF7B4A", "Lycaon": "#C6E0E5",
            "Rina": "#E83445", "Ellen": "#FC3576", "Corin": "#C86BFF",
            "Zhu Yuan": "#33B5FF", "Qingyi": "#00F5BE", "Seth": "#6FA8FF",
            "Jane": "#FD3476", "Caesar": "#E6C76B", "Lighter": "#FF5A4F",
            "Lucy": "#F5B635", "Burnice": "#E6C76B", "Piper": "#FFBC01",
            "Pulchra": "#FFA94D", "Miyabi": "#1DC0C5", "Yanagi": "#FD7388",
            "Harumasa": "#FFCC00", "Soukaku": "#00E4FF", "Astra Yao": "#FF3A5A",
            "Evelyn": "#B69AE4", "Soldier 0 - Anby": "#FEBF25", "Hugo": "#FF3D57",
            "Vivian": "#9A7BFF", "Orphie & Magus": "#E72D50", "Trigger": "#FDC821",
            "Soldier 11": "#FFE34D", "Seed": "#FFD24D", "Yixuan": "#FFD966",
            "Ye Shunguang": "#FF6A3D", "Ju Fufu": "#FF9000", "Pan Yinhu": "#FDCB7A",
            "Yuzuha": "#F43638", "Alice": "#FDD07C", "Manato": "#FF4A3A",
            "Lucia": "#19CBE4", "Yidhari": "#B266FF", "Dialyn": "#6EFCEB",
            "Banyue": "#E8C98A", "Zhao": "#FF6993", "Sunna": "#D5FF63",
            "Aria": "#FE678A", "Nangong Yu": "#A872EB", "Starlight - Billy": "#C5454A"
        }
        color_agente = COLORES_AGENTES.get(nombre, "#C78FA8")
        
        # Color según prioridad
        colores_prioridad = {
            "URGENTE": ft.Colors.RED_400,
            "ALTA": ft.Colors.ORANGE_400,
            "MEDIA": ft.Colors.YELLOW_700,
            "BAJA": ft.Colors.GREEN_400
        }
        color_prioridad = colores_prioridad.get(prioridad, ft.Colors.GREY_400)
        
        iconos_prioridad = {
            "URGENTE": ft.Icons.PRIORITY_HIGH,
            "ALTA": ft.Icons.ARROW_UPWARD,
            "MEDIA": ft.Icons.REMOVE,
            "BAJA": ft.Icons.ARROW_DOWNWARD
        }
        icono_prioridad = iconos_prioridad.get(prioridad, ft.Icons.HELP)
        
        # Función para obtener color y sombra de tier
        def obtener_color_y_sombra_tier(tier):
            from logica_recomendaciones import calificacion_a_tier, construir_sombra_tier
            # Mapear tier_clave a un pct para obtener color_hex
            _tier_to_pct = {'GODLIKE': 95, 'FLAWLESS': 85, 'GREAT': 75, 'SOLID': 60, 'DECENT': 50, 'AVERAGE': 40, 'MID': 0}
            pct = _tier_to_pct.get(tier, 0)
            clave, color_hex = calificacion_a_tier(pct)
            color_texto = "white" if clave == "GODLIKE" else color_hex
            sombra = construir_sombra_tier(clave, color_hex) if clave != "MID" else None
            sombra = sombra[0] if isinstance(sombra, list) else sombra
            print(f'[DEBUG tier] tier={tier} clave={clave} color_hex={color_hex} color_texto={color_texto} sombra={sombra}')
            return color_texto, sombra
        
        MAPEO_SETS = {
            31800: "Jazz caótico", 32600: "Metal colmilludo", 32400: "Metal eléctrico",
            32300: "Metal caótico", 32200: "Metal infernal", 32500: "Metal Polar",
            32700: "Balada de la rama y la espada", 33100: "Fábula Yunkui",
            31400: "Punk Hormonal", 31000: "Tecno Pícido", 32800: "Voz Astral",
            31600: "Jazz Oscilante", 32900: "Armonía Umbría", 31100: "Tecno Tetraodóntido",
            33300: "Floración del alba", 33200: "Monarca del Pináculo",
            33400: "Nana a la Luz Cenicienta", 33000: "Melodía de Phaeton",
            31900: "Proto Punk", 31200: "Disco sacudestrellas", 33600: "Aria Radiante",
            33500: "Balada de Aguas Blancas", 31300: "Blues Libre",
            31500: "Rock espiritual", 33700: "Conejo en el país de las maravillas",
            33800: "Diario de una prisionera", 33900: "Metal colmilludo",
            34000: "Metal infernal"
        }
        
        # Función para obtener substats sugeridas según rol
        def obtener_substats_sugeridas(rol_agente):
            from logica_recomendaciones import CONFIG_ROLES, EXCEPCIONES_AGENTES
            
            # Obtener config del agente
            config = EXCEPCIONES_AGENTES.get(nombre, CONFIG_ROLES.get(rol_agente, CONFIG_ROLES["Atacante"]))
            
            if "subs" in config:
                ideales = config["subs"].get("ideal", [])
                decentes = config["subs"].get("decente", [])
                
                # Priorizar las 3 más importantes
                top_stats = []
                for stat in ideales[:3]:
                    # Limpiar nombre de stat
                    stat_limpio = stat.replace("_", " ").replace("porcentual", "%").replace("plano", "").strip()
                    top_stats.append(stat_limpio)
                
                if top_stats:
                    return f"{self.i18n.t('ui.mejoras_discos.busca', default='Busca')}: {', '.join(top_stats)}"
                    
            return self.i18n.t("ui.mejoras_discos.busca_substats", default="Busca substats ideales para tu rol")
        
        # Imagen del agente
        img_agente = ft.Image(src=f"images/{nombre}.png", width=80, height=86, fit=ft.ImageFit.CONTAIN, border_radius=8)
        
        info_basica = ft.Column([
            ft.Text(nombre, size=18, weight="bold", color=color_agente),
            ft.Text(f"{agente['rol']} • {agente['elemento']}", size=12, color=ft.Colors.GREY_400),
            ft.Row([
                ft.Text(self.i18n.t("ui.mejoras_discos.nivel", default="Nivel:"), size=12),
                ft.Text(str(agente['nivel']), size=12, weight="bold", color=color_agente),
                ft.Text(self.i18n.t("ui.mejoras_discos.mindscape", default="M:"), size=12),
                ft.Text(str(agente['mindscape']), size=12, weight="bold", color=color_agente),
            ], spacing=5),
            ft.Text(agente['weapon'], size=11, italic=True, color=ft.Colors.GREY_500),
        ], spacing=3)
        
        # Badge de prioridad
        badge_prioridad = ft.Container(
            content=ft.Row([
                ft.Icon(icono_prioridad, size=16, color=color_prioridad),
                ft.Text(prioridad, size=12, weight="bold", color=color_prioridad)
            ], spacing=4),
            padding=ft.padding.symmetric(horizontal=8, vertical=4),
            bgcolor=ft.Colors.with_opacity(0.2, color_prioridad),
            border_radius=12,
        )
        
        # Barra de progreso
        barra_progreso = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text(self.i18n.t("ui.mejoras_discos.calidad", default="Calidad:"), size=11, color=ft.Colors.GREY_400),
                    ft.Container(expand=True),
                    ft.Text(f"{score:.1f}%", size=14, weight="bold", color=color_prioridad)
                ], spacing=5),
                ft.ProgressBar(
                    value=score / 100.0,
                    color=color_prioridad,
                    bgcolor=ft.Colors.with_opacity(0.2, color_prioridad),
                    height=14,
                    border_radius=7,
                )
            ], spacing=4, tight=True),
            expand=True,
            padding=ft.padding.only(left=15, right=10),
        )
        
        # Header
        header = ft.Row([
            img_agente,
            info_basica,
            barra_progreso,
            badge_prioridad,
        ], alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.START, spacing=10)
        
        # Discos - BADGE ABAJO Y CENTRADO
        sin_disco_txt = self.i18n.t("ui.mejoras_discos.sin_disco", default="Sin disco")
        discos_controles = []
        for slot in range(1, 7):
            disco_info = analisis_discos.get(slot, {})
            
            if disco_info:
                tier = disco_info.get('calificacion', 'MID')
                set_nombre = disco_info.get('set', sin_disco_txt)
                set_id = disco_info.get('set_id', 0)
                nivel = disco_info.get('nivel', 0)
            else:
                tier = "MID"
                set_nombre = sin_disco_txt
                set_id = 0
                nivel = 0
            
            tier_color, tier_shadow = obtener_color_y_sombra_tier(tier)
            
            # Cargar imagen del disco
            img_disco = None
            if set_id > 0 and set_nombre != sin_disco_txt:
                nombre_archivo_set = MAPEO_SETS.get(set_id, set_nombre)
                ruta_imagen = f"images/discos/{nombre_archivo_set}.png"
                if os.path.exists(ruta_imagen):
                    img_disco = ft.Image(src=ruta_imagen, width=70, height=70, fit=ft.ImageFit.CONTAIN)
            
            if not img_disco:
                img_disco = ft.Icon(ft.Icons.ALBUM, size=40, color=ft.Colors.GREY_700)
            
            # Badge del tier
            if tier == "GODLIKE":
                letras_dios = ft.Text(
                    spans=[
                        ft.TextSpan("G", style=ft.TextStyle(color="#FF85A2", weight="bold", font_family="Consolas")),
                        ft.TextSpan("O", style=ft.TextStyle(color="#FFEA75", weight="bold", font_family="Consolas")),
                        ft.TextSpan("D", style=ft.TextStyle(color="#85FF9E", weight="bold", font_family="Consolas")),
                    ],
                    size=10, text_align="center"
                )
                badge_tier = ft.Container(
                    padding=1, border_radius=6,
                    gradient=ft.LinearGradient(
                        colors=["#FF003C", "#FFD500", "#00FF2A", "#0066FF"],
                        begin=ft.alignment.center_left, end=ft.alignment.center_right
                    ),
                    content=ft.Container(
                        bgcolor=ft.Colors.with_opacity(0.9, ft.Colors.BLACK),
                        padding=ft.padding.symmetric(horizontal=5, vertical=1),
                        border_radius=5, alignment=ft.alignment.center, content=letras_dios
                    )
                )
            else:
                badge_tier = ft.Container(
                    content=ft.Text(tier, size=10, weight="bold", color=tier_color, font_family="Consolas"),
                    bgcolor=ft.Colors.with_opacity(0.85, ft.Colors.BLACK),
                    padding=ft.padding.symmetric(horizontal=5, vertical=1),
                    border=ft.border.all(1, tier_color), border_radius=5
                )
            
            # Disco: imagen circular + slot number + badge tier
            circulo_disco = ft.Container(
                content=img_disco,
                width=72, height=72,
                bgcolor=ft.Colors.with_opacity(0.15, ft.Colors.WHITE),
                border_radius=36,
                border=ft.border.all(2, ft.Colors.TRANSPARENT if tier == 'GODLIKE' else (tier_color if tier_color != 'secondary' else ft.Colors.GREY_800)),
                shadow=tier_shadow if tier != 'GODLIKE' else None,
                alignment=ft.alignment.center,
                clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
            )

            if tier == 'GODLIKE':
                stack_circulo = ft.Stack([
                    ft.Container(width=72, height=72, bgcolor='surface', border_radius=36,
                        shadow=ft.BoxShadow(blur_radius=15, spread_radius=1, color='#FF003C', offset=ft.Offset(-10, 0))),
                    ft.Container(width=72, height=72, bgcolor='surface', border_radius=36,
                        shadow=ft.BoxShadow(blur_radius=15, spread_radius=1, color='#FFD500', offset=ft.Offset(-5, 0))),
                    ft.Container(width=72, height=72, bgcolor='surface', border_radius=36,
                        shadow=ft.BoxShadow(blur_radius=15, spread_radius=1, color='#00FF2A', offset=ft.Offset(5, 0))),
                    ft.Container(width=72, height=72, bgcolor='surface', border_radius=36,
                        shadow=ft.BoxShadow(blur_radius=15, spread_radius=1, color='#0066FF', offset=ft.Offset(10, 0))),
                    circulo_disco,
                ], width=72, height=72, clip_behavior=ft.ClipBehavior.NONE)
            else:
                stack_circulo = circulo_disco

            disco_visual = ft.Container(
                content=ft.Column([
                    ft.Container(content=ft.Text(str(slot), size=9, color=ft.Colors.GREY_500, text_align=ft.TextAlign.CENTER), alignment=ft.alignment.center),
                    stack_circulo,
                    ft.Container(content=badge_tier, alignment=ft.alignment.center),
                ], spacing=2, horizontal_alignment=ft.CrossAxisAlignment.CENTER, tight=True),
                tooltip=self.i18n.t("ui.mejoras_discos.tooltip_disco", default=f"Disco {slot}: {set_nombre} (Nv.{nivel})", slot=slot, set_nombre=set_nombre, nivel=nivel),
                width=80,
            )
            discos_controles.append(disco_visual)
        
        # Fila horizontal de 6 discos
        discos_grid = ft.Container(
            content=ft.Row(
                discos_controles,
                spacing=8,
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.symmetric(vertical=6),
        )
        
        # Sets equipados
        sets_text = ", ".join([f"{set_n} ({bonus})" for set_n, bonus in sets_equipados.items()]) if sets_equipados else self.i18n.t("ui.mejoras_discos.sin_sets", default="Sin sets completos")
        
        # Substats sugeridas
        substats_sugerencia = obtener_substats_sugeridas(agente['rol'])
        
        # Recomendaciones con substats específicas
        recom_column = ft.Column(spacing=6, tight=True)
        
        recom_criticas = [r for r in recomendaciones if r['prioridad'] == 'urgente']
        recom_altas = [r for r in recomendaciones if r['prioridad'] == 'alta']
        recom_medias = [r for r in recomendaciones if r['prioridad'] == 'media']
        
        # Si NO hay recomendaciones críticas pero tiene discos mejorables
        if not (recom_criticas or recom_altas) and any(
            analisis_discos.get(slot, {}).get('calificacion', 'MID') in ['GREAT', 'SOLID', 'DECENT', 'AVERAGE', 'MID']
            for slot in range(1, 7)
        ):
            recom_medias.append({
                'prioridad': 'media',
                'mensaje': f"{substats_sugerencia} {self.i18n.t('ui.mejoras_discos.potencial_dmg', default='(+3-7% daño potencial)')}"
            })
        
        def traducir_mensaje_recom(msg):
            """Traduce mensajes hardcodeados del analizador de prioridades."""
            TRADUCCIONES = self.i18n.t("ui.mejoras_discos.mensajes_recom", default={})
            if isinstance(TRADUCCIONES, dict):
                for clave, traduccion in TRADUCCIONES.items():
                    if clave.lower() in msg.lower():
                        return msg.lower().replace(clave.lower(), traduccion)
            return msg

        def crear_recom_item(recom, color_rec):
            return ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.ARROW_FORWARD, size=13, color=color_rec),
                    ft.Text(traducir_mensaje_recom(recom['mensaje']), size=11, expand=True)
                ], spacing=6),
                padding=6,
                bgcolor=ft.Colors.with_opacity(0.05, color_rec),
                border=ft.border.only(left=ft.BorderSide(2, color_rec)), 
                border_radius=4,
            )
        
        if recom_criticas:
            recom_column.controls.append(ft.Text(self.i18n.t("ui.mejoras_discos.prioridad_urgente", default="🔴 Urgente (+15-25%)"), size=10, weight="bold", color=ft.Colors.RED_300))
            for recom in recom_criticas[:2]:
                recom_column.controls.append(crear_recom_item(recom, ft.Colors.RED_400))
        
        if recom_altas:
            recom_column.controls.append(ft.Text(self.i18n.t("ui.mejoras_discos.prioridad_alta", default="🟠 Alta (+10-15%)"), size=10, weight="bold", color=ft.Colors.ORANGE_300))
            for recom in recom_altas[:2]:
                recom_column.controls.append(crear_recom_item(recom, ft.Colors.ORANGE_400))
        
        if recom_medias:
            recom_column.controls.append(ft.Text(self.i18n.t("ui.mejoras_discos.prioridad_media", default="🟡 Media (+3-10%)"), size=10, weight="bold", color=ft.Colors.YELLOW_600))
            for recom in recom_medias[:2]:
                recom_column.controls.append(crear_recom_item(recom, ft.Colors.YELLOW_700))
        
        if not recom_column.controls:
            recom_column.controls.append(ft.Text(self.i18n.t("ui.mejoras_discos.build_optima", default="✓ Build óptima"), size=12, color=ft.Colors.GREEN_400, weight="bold"))

        # Contenido completo (sin header — ya está en la cabecera colapsable)
        contenido = ft.Column([
            ft.Text(self.i18n.t("ui.mejoras_discos.seccion_discos", default="📀 Discos"), size=13, weight="bold"),
            discos_grid,
            ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.STYLE, size=14),
                    ft.Text(sets_text, size=11, expand=True)
                ], spacing=6),
                padding=6, bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.BLUE),
                border_radius=5,
            ),
            ft.Divider(height=1, color=ft.Colors.GREY_800),
            ft.Text(self.i18n.t("ui.mejoras_discos.seccion_recomendaciones", default="💡 Recomendaciones"), size=13, weight="bold"),
            recom_column,
        ], spacing=10, tight=True)
        
        # ── TARJETA COLAPSABLE ──────────────────────────────────────────────────
        # Cabecera siempre visible (imagen + nombre + barra + badge)
        cabecera = ft.Container(
            content=ft.Row([
                # Imagen del agente
                ft.Container(
                    content=ft.Image(
                        src=f"images/{nombre}.png",
                        width=48, height=48, fit=ft.ImageFit.COVER,
                        error_content=ft.Icon(ft.Icons.PERSON, size=28, color=color_agente),
                    ),
                    width=48, height=48, border_radius=24,
                    clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                    border=ft.border.all(2, color_agente),
                ),
                # Info básica — ancho fijo para que no empuje la barra
                ft.Container(
                    content=ft.Column([
                        ft.Text(nombre, size=15, weight="bold", color=color_agente,
                                overflow=ft.TextOverflow.ELLIPSIS, max_lines=1),
                        ft.Row([
                            # Ícono elemento
                            self._icono_elemento_flet(agente.get('elemento', ''), size=26),
                            # Ícono rol
                            self._icono_rol_flet(agente.get('rol', ''), size=26),
                            ft.Text(self.i18n.t("ui.mejoras_discos.nv_valor", default=f"Nv.{agente['nivel']}", nivel=agente['nivel']), size=11, color=ft.Colors.GREY_500),
                            ft.Text(self.i18n.t("ui.mejoras_discos.m_valor", default=f"M:{agente['mindscape']}", mindscape=agente['mindscape']), size=11, color=ft.Colors.GREY_500),
                        ], spacing=4, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    ], spacing=3, tight=True),
                    width=170,
                ),
                # Barra de calidad — expand para llenar el espacio restante
                ft.Column([
                    ft.Row([
                        ft.Text(self.i18n.t("ui.mejoras_discos.calidad", default="Calidad:"), size=11, color=ft.Colors.GREY_400),
                        ft.Container(expand=True),
                        ft.Text(f"{score:.1f}%", size=13, weight="bold", color=color_prioridad),
                    ]),
                    ft.ProgressBar(
                        value=score / 100.0,
                        color=color_prioridad,
                        bgcolor=ft.Colors.with_opacity(0.2, color_prioridad),
                        height=10, border_radius=5,
                    ),
                ], spacing=4, tight=True, expand=True),
                # Badge de prioridad
                badge_prioridad,
                # Flecha expandir/colapsar
                ft.Icon(ft.Icons.KEYBOARD_ARROW_DOWN, size=20, color=ft.Colors.GREY_400),
            ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.padding.symmetric(horizontal=14, vertical=10),
            ink=True,
        )

        # Panel de detalles (colapsado por defecto)
        panel_detalles = ft.Container(
            content=ft.Column([
                ft.Divider(height=1, color=ft.Colors.GREY_800),
                ft.Container(content=contenido, padding=ft.padding.only(top=8)),
            ], spacing=0, tight=True),
            visible=False,
            padding=ft.padding.only(left=14, right=14, bottom=12),
        )

        tarjeta_col = ft.Column([cabecera, panel_detalles], spacing=0, tight=True)

        def toggle_detalle(e):
            panel_detalles.visible = not panel_detalles.visible
            # Rotar flecha
            flecha = cabecera.content.controls[-1]
            flecha.name = ft.Icons.KEYBOARD_ARROW_UP if panel_detalles.visible else ft.Icons.KEYBOARD_ARROW_DOWN
            tarjeta_col.update()

        cabecera.on_click = toggle_detalle

        return ft.Container(
            content=tarjeta_col,
            bgcolor="surface",
            border=ft.border.all(2, color_prioridad),
            border_radius=12,
            shadow=[
                ft.BoxShadow(spread_radius=0, blur_radius=16,
                             color=ft.Colors.with_opacity(0.5, color_prioridad)),
            ],
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        )
    
    def _obtener_color_calificacion(self, calificacion):
        """Retorna el color correspondiente a una calificación."""
        colores = {
            'S': ft.Colors.PURPLE_400,
            'A': ft.Colors.BLUE_400,
            'B': ft.Colors.GREEN_400,
            'C': ft.Colors.YELLOW_700,
            'D': ft.Colors.ORANGE_400,
            'F': ft.Colors.RED_400,
        }
        return colores.get(calificacion, ft.Colors.GREY_400)
            
MAPA_STATS_JSON ={
    "HP": "Puntos_Vida","ATK": "Ataque","DEF": "Defensa",
    "CRIT Rate": "Probabilidad_crítico","CRIT DMG": "Daño_crítico","PEN Ratio": "Tasa_de_Perforación",
    "PEN": "Perforación_Plana","Anomaly Proficiency": "Maestría_Anomalía","Physical DMG Bonus": "Daño_elemental",
    "Fire DMG Bonus": "Daño_elemental","Ice DMG Bonus": "Daño_elemental","Electric DMG Bonus": "Daño_elemental",
    "Ether DMG Bonus": "Daño_elemental","Anomaly Mastery": "Tasa_de_Anomalía","Impact": "Impacto",
    "Energy Regen": "Recuperación_energía","Percent ATK": "Ataque","Percent HP": "Puntos_Vida","Percent DEF": "Defensa",
    "Sheer Force": "Sheer_force",
}

MAPA_SETS_JSON ={
    "Chaos Jazz": "Jazz caótico","Fanged Metal": "Metal colmilludo",
    "Thunder Metal": "Metal eléctrico","Chaotic Metal": "Metal caótico",
    "Inferno Metal": "Metal infernal","Polar Metal": "Metal Polar",
    "Branch & Blade Song": "Balada de la rama y la espada","Yunkui Tales": "Fábula Yunkui",
    "Hormone Punk": "Punk Hormonal","Woodpecker Electro": "Tecno Pícido","Astral Voice": "Voz Astral",
    "Swing jazz": "Jazz Oscilante","Shadow Harmony": "Armonía Umbría","Puffer Electro": "Tecno Tetraodóntido",
    "Dawn's Bloom": "Floración del alba","King of summit": "Monarca del Pináculo","Moonlight Lullaby": "Nana a la Luz Cenicienta",
    "Phaethon's Melody": "Melodía de Phaeton","Proto Punk": "Proto Punk","Shockstar Disco": "Disco sacudestrellas",
    "Shining Aria": "Aria Radiante","White Water Ballad": "Balada de Aguas Blancas","Freedom Blues": "Blues Libre",
    "Soul Rock": "Rock espiritual","Bunny in Wonderland": "Conejo en el país de las maravillas","Notes From the Chained": "Diario de una prisionera"
}

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

import flet as ft
# ==============================================================================
# ── SISTEMA DE FONDO OPTIMIZADO (sin blur general, sin loops, sin fetch externo)
# ==============================================================================

def crear_orbe_estatico(color, tamano, x, y):
    """Orbe con sombra suave y deriva animada manualmente."""
    return ft.Container(
        width=tamano,
        height=tamano,
        left=x,
        top=y,
        border_radius=1000,
        bgcolor=ft.Colors.TRANSPARENT,
        shadow=ft.BoxShadow(
            spread_radius=6,
            blur_radius=40,
            color=ft.Colors.with_opacity(0.10, color),
            blur_style=ft.ShadowBlurStyle.NORMAL,
        ),
    )

ORBES_CONFIG = [
    (1400 * 0.55, 1000 * 0.05, 90, 70),
    (1400 * 0.10, 1000 * 0.50, 70, 80),
    (1400 * 0.40, 1000 * 0.70, 80, 60),
]

def aplicar_fondo_archive_textured(page: ft.Page):
    page.bgcolor = "#161616"
    fondo_base = ft.Container(expand=True, bgcolor="#1E1E1E")

    W, H = 1400, 1000
    color = page.theme.color_scheme.primary

    orbes = [
        crear_orbe_estatico(color, 480, W * 0.55, H * 0.05),
        crear_orbe_estatico(color, 340, W * 0.1, H * 0.5),
        crear_orbe_estatico(color, 380, W * 0.4, H * 0.7),
    ]

    fondo_stack = ft.Stack([
        fondo_base,
        *orbes,
        ft.Container(
            expand=True,
            gradient=ft.RadialGradient(
                center=ft.alignment.center,
                radius=1.2,
                colors=[ft.Colors.with_opacity(0.0, ft.Colors.BLACK),
                        ft.Colors.with_opacity(0.55, ft.Colors.BLACK)],
            ),
        ),
    ])

    return ft.Container(content=fondo_stack, expand=True), orbes, fondo_base
# ==============================================================================

def main(page: ft.Page):
    page.window.maximized = True
    page.title = "Rorin Labs"
    
    page.theme_mode = ft.ThemeMode.DARK
    
    page.theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary="#C78FA8",
            on_primary="#161616",
            secondary="#AFAFAF",
            on_secondary="#161616",
            background="#161616",
            surface="#1E1E1E",
            error="#FF6B6F",
            tertiary="#F4FF4D",
            on_surface_variant="#FFFFFF",
            outline="#3A3A3A",
        ),
        card_theme=ft.CardTheme(
            color="#1E1E1E",
            elevation=5
        ),
    )
    
    # IMPORTANTE: Esto asegura que las "auroras" lleguen hasta el borde del programa
    page.padding = 0 

    CalculadoraZZZ(page)

if __name__ == "__main__":
    if getattr(sys, 'frozen', False):
        ruta_assets = sys._MEIPASS
    else:
        ruta_assets = "."
    ft.app(target=main, assets_dir="assets", view=ft.AppView.WEB_BROWSER, port=8080, host="0.0.0.0")
