import flet as ft
import os
import time
import math
import random
import pyperclip
from traductor import Traductor
from logica_recomendaciones import CONFIG_ROLES, EXCEPCIONES_AGENTES, evaluar_calidad_global, calificacion_a_tier, calificacion_a_color_semaforo, construir_sombra_tier
from substats_config import calcular_rolls_substat, valor_substat

class CrearGui:
    def __init__(self, app_instance, traductor: Traductor):
        self.app = app_instance
        self.i18n = traductor
        self.FS = {'xs': 11, 'sm': 13, 'md': 14, 'lg': 16, 'xl': 20, 'xxl': 24}
        self.entry_vars = {}
        self.buff_vars = {}
        self.team_controls = {}
        self.contenedor_pasivas_ui = ft.Column()
        self.botones_idioma = {}
        self.controles_pasivas = {}
        self.agent_dropdown = None
        self.wengine_dropdown = None
        self.refinamiento_dropdown = None 
        self.stacks_dropdown = None       
        self.habilidad_dropdown = None
        self.core_stacks_dropdown = None
        self.core_stacks_slider = None
        self.slider_potencial = None
        self.contenedor_potencial = None
        self.enemy_dropdown = None
        self.set_stacks_dropdown = None  
        self.set_checkbox = None
        self.img_agente = None
        self.img_wengine = None  
        self.img_enemigo = None
        self.resultado_normal = None
        self.resultado_sheer = None
        self.resultado_anomaly = None
        self.resultado_disorder = None
        self.dd_elemento_abloom = None
        self.dd_miasma = None
        self.resultados_text = None
        self.config_name_field = None
        self.cache_datos_left = {}
        self.cache_datos_right = {}
        self.contenedor_analisis = ft.Column()
        self.da_img_enemigo_detalle = None
        self.da_txt_detalle_enemigo = None
        self.da_opciones_enemigo_ui = None
        self.da_enemy_checkboxes = {}
        self.ranking_agente_seleccionado = None
        self.ranking_contenido_derecha = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)
        self.ranking_pagina_actual = 0
        self.ranking_items_por_pagina = 50
        self._ranking_cache_gui = None
        self._ranking_cache_ts = 0
        
        self.contenedor_personajes_importados = ft.Row(
            spacing=8,
            wrap=True,
            alignment=ft.MainAxisAlignment.START,
            visible=False
        )
        self.contenedor_personajes_wrapper = None
        
    def create_character_tab(self):
        """
        Pestaña principal 'DPS' COMPLETA con nuevo sistema de discos individuales.
        """
        self.set_stacks_dropdown = ft.Dropdown(width=120, dense=True, text_size=12, visible=False)
        self.set_checkbox = ft.Checkbox(visible=False, label_style=ft.TextStyle(color="primary", weight=ft.FontWeight.BOLD))
        self.img_agente = ft.Image(src="images/default.png", width=121, height=131, fit=ft.ImageFit.CONTAIN, border_radius=8, opacity=0.2, animate_opacity=ft.Animation(300, ft.AnimationCurve.EASE_OUT))
        self.img_wengine = ft.Image(
            src="images/wengine/default_wengine.png", width=100, height=100,
            fit=ft.ImageFit.CONTAIN, border_radius=8, opacity=0.2,
            tooltip=self.i18n.t("ui.tab_dps.wengine"),
            animate_opacity=ft.Animation(300, ft.AnimationCurve.EASE_OUT)
        )

        self.agent_dropdown = ft.Dropdown(visible=False)

        lista_resultados_dps = ft.ListView(spacing=0)

        contenedor_lista_dps = ft.Container(
            content=lista_resultados_dps,
            bgcolor="background",
            border_radius=ft.border_radius.only(bottom_left=8, bottom_right=8),
            border=ft.border.all(1, "primary"),
            shadow=ft.BoxShadow(spread_radius=2, blur_radius=14, color=ft.Colors.BLACK87),
            visible=False,
            top=60, left=155, right=135
        )

        self.txt_agente_dps = ft.TextField(
            label=self.i18n.t("ui.tab_dps.buscar_agente"),
            dense=True,
            text_size=14,
            prefix_icon=ft.Icons.SEARCH,
        )

        class EventoSimuladoDPS:
            def __init__(self, control):
                self.control = control
                self.data = control.value

        def seleccionar_agente_dps(e):
            seleccion = e.control.data
            self.txt_agente_dps.value = seleccion
            contenedor_lista_dps.visible = False
            self.agent_dropdown.value = seleccion
            if self.agent_dropdown.on_change:
                self.agent_dropdown.on_change(EventoSimuladoDPS(self.agent_dropdown))
            self.txt_agente_dps.update()
            contenedor_lista_dps.update()

        def crear_item_dps(texto):
            return ft.Container(
                content=ft.Text(texto, size=13),
                padding=ft.padding.symmetric(horizontal=14, vertical=11),
                ink=True, data=texto, on_click=seleccionar_agente_dps
            )

        def obtener_opciones_dps():
            if self.agent_dropdown.options:
                return [opt.key if opt.key else opt.text for opt in self.agent_dropdown.options]
            return []

        def filtrar_agentes_dps(e):
            texto = self.txt_agente_dps.value.lower()
            lista_resultados_dps.controls.clear()
            opciones = obtener_opciones_dps()
            sugerencias = opciones if texto == "" else [a for a in opciones if texto in str(a).lower()]
            for s in sugerencias:
                lista_resultados_dps.controls.append(crear_item_dps(s))
            cantidad = len(sugerencias)
            if cantidad > 0:
                lista_resultados_dps.height = min(200, cantidad * 40)
                contenedor_lista_dps.visible = True
            else:
                contenedor_lista_dps.visible = False
            contenedor_lista_dps.update()

        def mostrar_todo_dps(e):
            filtrar_agentes_dps(e)

        self.txt_agente_dps.on_change = filtrar_agentes_dps
        self.txt_agente_dps.on_focus  = mostrar_todo_dps

        def on_blur_buscador_dps(e):
            import threading, time
            def cerrar():
                time.sleep(0.15)
                contenedor_lista_dps.visible = False
                contenedor_lista_dps.update()
            threading.Thread(target=cerrar, daemon=True).start()

        self.txt_agente_dps.on_blur = on_blur_buscador_dps

        bloque_buscador = ft.Column([self.txt_agente_dps, self.agent_dropdown], spacing=0, expand=True)

        btn_importar = ft.IconButton(
            icon=ft.Icons.CLOUD_DOWNLOAD,
            tooltip=self.i18n.t("ui.tab_dps.importar_uid"),
            on_click=self.app.abrir_dialogo_uid
        )

        self.mindscape_dropdown = ft.Dropdown(
            label=self.i18n.t("ui.tab_dps.dupe"),
            width=100, dense=True, text_size=14, value="0",
            options=[ft.dropdown.Option(str(i), text=f"M{i}") for i in range(7)],
            on_change=self.app.cambiar_mindscape,
            bgcolor="background",
            border_radius=ft.border_radius.only(bottom_left=8, bottom_right=8),
            border_color=ft.Colors.with_opacity(0.25, ft.Colors.WHITE),
            focused_border_color="primary"
        )
        self.mindscape_stacks_dropdown = ft.Dropdown(
            label=self.i18n.t("ui.tab_dps.cargas"),
            width=160, dense=True, text_size=14, visible=False,
            on_change=self.app.cambiar_mindscape_stacks,
            bgcolor="background",
            border_radius=ft.border_radius.only(bottom_left=8, bottom_right=8),
            border_color=ft.Colors.with_opacity(0.25, ft.Colors.WHITE),
            focused_border_color="primary"
        )

        self.mindscape_cond_dropdown = ft.Dropdown(
            label=self.i18n.t("ui.tab_dps.condicion", default="Condición"),
            width=180, dense=True, text_size=12, visible=False,
            bgcolor="background",
            border_radius=ft.border_radius.only(bottom_left=8, bottom_right=8),
            border_color=ft.Colors.with_opacity(0.25, ft.Colors.WHITE),
            focused_border_color="primary"
        )

        row_agente = ft.Row(
            controls=[bloque_buscador, btn_importar],
            spacing=8,
            vertical_alignment=ft.CrossAxisAlignment.CENTER
        )

        self.row_mindscape = ft.Row(
            controls=[self.mindscape_dropdown, self.mindscape_stacks_dropdown, self.mindscape_cond_dropdown],
            spacing=8,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        self.wengine_dropdown = ft.Dropdown(
            label=self.i18n.t("ui.tab_dps.wengine"),
            dense=True, width=204, text_size=14,
            max_menu_height=200,
            bgcolor="background",
            border_radius=ft.border_radius.only(bottom_left=8, bottom_right=8),
            border_color=ft.Colors.with_opacity(0.25, ft.Colors.WHITE),
            focused_border_color="primary",
        )

        self.chk_filtro_wengine = ft.Checkbox(
            label=self.i18n.t("ui.tab_dps.solo_compatibles"),
            value=True,
            tooltip=self.i18n.t("ui.tab_dps.tooltip_compatibles"),
            on_change=self.app.cambiar_filtro_wengines
        )

        self.refinamiento_dropdown = ft.Dropdown(
            label=self.i18n.t("ui.tab_dps.refinamiento"),
            width=100, dense=True, text_size=14, value="1",
            options=[ft.dropdown.Option(str(i)) for i in range(1, 6)],
            on_change=self.app.cambiar_refinamiento,
            bgcolor="background",
            border_radius=ft.border_radius.only(bottom_left=8, bottom_right=8),
            border_color=ft.Colors.with_opacity(0.25, ft.Colors.WHITE),
            focused_border_color="primary"
        )

        self.stacks_dropdown = ft.Dropdown(
            label=self.i18n.t("ui.tab_dps.stacks"),
            width=80, dense=True, text_size=12, visible=False,
            bgcolor="background",
            border_radius=ft.border_radius.only(bottom_left=8, bottom_right=8),
            border_color=ft.Colors.with_opacity(0.25, ft.Colors.WHITE),
            focused_border_color="primary"
        )

        self.lbl_desc_wengine = ft.Text("", size=self.FS['xs'], italic=True, color=ft.Colors.WHITE70, max_lines=3)

        row_wengine = ft.Row(
            controls=[self.wengine_dropdown, self.stacks_dropdown, self.chk_filtro_wengine],
            spacing=8,
            vertical_alignment=ft.CrossAxisAlignment.CENTER
        )

        self.contenedor_desc_wengine = ft.Container(
            content=self.lbl_desc_wengine,
            padding=ft.padding.only(left=8, bottom=4),
            visible=False
        )

        self.habilidad_dropdown = ft.Dropdown(
            label=self.i18n.t("ui.tab_dps.habilidad"),
            dense=True, expand=True, text_size=14,
            on_change=self.app.manejador_habilidad,
            bgcolor="background",
            border_radius=ft.border_radius.only(bottom_left=8, bottom_right=8),
            border_color=ft.Colors.with_opacity(0.25, ft.Colors.WHITE),
            focused_border_color="primary"
        )
        self.core_checkbox = ft.Checkbox(
            label=self.i18n.t("ui.tab_dps.activar_core"),
            value=False,
            on_change=self.app.cambiar_core_activo,
            tooltip=self.i18n.t("ui.tab_dps.tooltip_core")
        )

        self.core_stacks_dropdown = ft.Dropdown(
            label=self.i18n.t("ui.tab_dps.stacks"),
            width=80, dense=True, text_size=12, visible=False,
            options=[ft.dropdown.Option(str(i)) for i in range(1, 10)],
            value="1",
            on_change=self.app.cambiar_core_stacks
        )

        self.core_stacks_slider = ft.Slider(
            min=0, max=100, divisions=100, label="{value}",
            width=150, visible=False,
            on_change=self.app.cambiar_core_stacks
        )

        row_habilidad = ft.Row(
            controls=[self.habilidad_dropdown, self.core_checkbox, self.core_stacks_dropdown, self.core_stacks_slider],
            spacing=10,
            vertical_alignment=ft.CrossAxisAlignment.CENTER
        )

        self.lbl_desc_core = ft.Text("", size=self.FS['xs'], italic=True, color=ft.Colors.WHITE70, max_lines=2)
        self.contenedor_desc_core = ft.Container(
            content=self.lbl_desc_core,
            padding=ft.padding.only(left=8, bottom=4),
            visible=False
        )

        self.slider_potencial = ft.Slider(
            min=0, max=6, divisions=6, label=self.i18n.t("ui.tab_dps.nv_potencial"),
            expand=True, value=0, on_change=self.app.cambiar_potencial
        )

        self.lbl_desc_potencial = ft.Text(self.i18n.t("ui.tab_dps.desc_potencial"), size=self.FS['xs'], italic=True)

        self.contenedor_potencial = ft.Column([
            ft.Row([
                ft.Text(self.i18n.t("ui.tab_dps.potencial"), weight=ft.FontWeight.BOLD, color="primary", size=14),
                self.slider_potencial
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            ft.Container(content=self.lbl_desc_potencial, padding=ft.padding.only(left=30, top=0, bottom=6))
        ], visible=False, spacing=0)

        self.contenedor_pasivas_ui = ft.Column(spacing=6)

        columna_central = ft.Column(
            controls=[row_agente, self.row_mindscape, row_wengine, self.contenedor_desc_wengine, row_habilidad, self.contenedor_desc_core, self.contenedor_potencial, self.contenedor_pasivas_ui],
            expand=True, spacing=10
        )

        stack_central = ft.Stack(
            controls=[columna_central, contenedor_lista_dps],
            expand=True,
            clip_behavior=ft.ClipBehavior.NONE
        )

        # ── Imágenes de agente y wengine con hover ────────────────────
        marco_agente = ft.Container(
            content=self.img_agente,
            padding=6,
            border=ft.border.all(1, ft.Colors.OUTLINE),
            border_radius=12,
            bgcolor="surface",
            shadow=ft.BoxShadow(blur_radius=12, spread_radius=0, color=ft.Colors.BLACK26),
            animate_scale=ft.Animation(280, ft.AnimationCurve.EASE_OUT),
        )
        def on_hover_agente(e):
            marco_agente.scale = 1.04 if e.data == "true" else 1.0
            marco_agente.update()
        marco_agente.on_hover = on_hover_agente

        marco_wengine = ft.Container(
            content=self.img_wengine,
            padding=6,
            border=ft.border.all(1, ft.Colors.OUTLINE),
            border_radius=12,
            bgcolor="surface",
            shadow=ft.BoxShadow(blur_radius=12, spread_radius=0, color=ft.Colors.BLACK26),
            animate_scale=ft.Animation(280, ft.AnimationCurve.EASE_OUT),
        )
        def on_hover_wengine(e):
            marco_wengine.scale = 1.04 if e.data == "true" else 1.0
            marco_wengine.update()
        marco_wengine.on_hover = on_hover_wengine

        top_card_content = ft.Row(
            controls=[marco_agente, columna_central, ft.Column(
                controls=[marco_wengine, self.refinamiento_dropdown],
                spacing=6,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )],
            spacing=12,
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.START
        )

        parametros_agente = [
            (self.i18n.t("stats.nivel"), "Nivel"),
            (self.i18n.t("stats.ataque"), "Ataque"),
            (self.i18n.t("stats.puntos_vida"), "Puntos_Vida"),
            (self.i18n.t("stats.defensa"), "Defensa"),
            (self.i18n.t("stats.prob_crit"), "Probabilidad_crítico"),
            (self.i18n.t("stats.dano_crit"), "Daño_crítico"),
            (self.i18n.t("stats.bono_dmg"), "Daño_Adicional"),
            (self.i18n.t("stats.dano_elemental"), "Daño_elemental"),
            (self.i18n.t("stats.maestria_anomalia"), "Maestría_Anomalía"),
            (self.i18n.t("stats.tasa_anomalia"), "Tasa_de_Anomalía"),
            (self.i18n.t("stats.bono_dmg_anomalia"), "Bono_Daño_Anomalia"),
            (self.i18n.t("stats.impacto"), "Impacto"),
            (self.i18n.t("stats.perforacion"), "Tasa_de_Perforación"),
            (self.i18n.t("stats.perf_plana"), "Perforación_Plana"),
            (self.i18n.t("stats.rec_energia"), "Recuperación_energía"),
            (self.i18n.t("stats.skill_mult"), "Multiplicador_de_ataques"),
            (self.i18n.t("stats.aturdimiento"), "Aturdimiento"),
            (self.i18n.t("stats.fuerza_absoluta"), "Sheer_force")
        ]

        agent_fields = []
        for label, key in parametros_agente:
            field = ft.TextField(
                label=label, read_only=False, dense=True, data=key,
                text_size=13, height=40, content_padding=10
            )
            self.entry_vars[key] = field
            agent_fields.append(field)

        stats_columns = ft.Row(
            controls=[
                ft.Column(agent_fields[0:6],  spacing=8, expand=1),
                ft.Column(agent_fields[6:12], spacing=8, expand=1),
                ft.Column(agent_fields[12:18],spacing=8, expand=1)
            ], spacing=16
        )

        bloques_discos = []
        for i in range(1, 7):
            bloque = self.crear_bloque_disco_ui(i)
            bloques_discos.append(ft.Column([bloque], col={"xl": 4, "lg": 6, "md": 6, "sm": 12}))

        grid_discos = ft.ResponsiveRow(
            controls=bloques_discos,
            spacing=14, run_spacing=14
        )

        btn_reiniciar_discos = ft.ElevatedButton(
            self.i18n.t("ui.tab_dps.reiniciar_todo"),
            on_click=self.app.reiniciar_stats,
            style=ft.ButtonStyle(bgcolor="error", color="surface"),
            height=32
        )

        self.txt_total_rolls_global = ft.Text(
            self.i18n.t("ui.tab_dps.rolls_totales"),
            size=16, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER
        )

        btn_generar_tarjeta = ft.Container(
            content=ft.ElevatedButton(
                text=self.i18n.t("ui.tab_dps.generar_buildcard"),
                icon=ft.Icons.CAMERA_ALT,
                color="primary",
                on_click=self.app.boton_generar_tarjeta
            ),
            animate_scale=ft.Animation(250, ft.AnimationCurve.EASE_OUT),
        )
        def on_hover_btn_tarjeta(e):
            btn_generar_tarjeta.scale = 1.05 if e.data == "true" else 1.0
            btn_generar_tarjeta.update()
        btn_generar_tarjeta.on_hover = on_hover_btn_tarjeta

        # ── Card de discos con sombra y bordes redondeados ────────────
        self.lbl_set_desc_4pc = ft.Text("", size=11, color="secondary", italic=True, visible=False)

        tarjeta_discos_nueva = ft.Card(
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text(self.i18n.t("ui.tab_dps.equipamiento_ranura"),
                                weight=ft.FontWeight.BOLD, size=16),
                        btn_reiniciar_discos
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),

                    ft.Row([self.set_checkbox, self.set_stacks_dropdown],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    self.lbl_set_desc_4pc,

                    ft.Divider(height=6),
                    grid_discos,
                    ft.Container(
                        content=ft.Row([
                            self.txt_total_rolls_global,
                            btn_generar_tarjeta
                        ], alignment=ft.MainAxisAlignment.SPACE_AROUND),
                        padding=ft.padding.symmetric(horizontal=10, vertical=12)
                    )
                ], spacing=12),
                padding=ft.padding.all(18)
            ),
            elevation=3,
        )

        # ── Enemigo ───────────────────────────────────────────────────
        self.img_enemigo = ft.Image(
            src="images/enemigos/default_enemy.png",
            width=181, height=227,
            fit=ft.ImageFit.CONTAIN, border_radius=8, opacity=0.2,
            animate_opacity=ft.Animation(300, ft.AnimationCurve.EASE_OUT)
        )
        self.enemy_dropdown = ft.Dropdown(
            label=self.i18n.t("ui.tab_dps.selecciona_enemigo"),
            dense=True, text_size=14, expand=True,
            bgcolor="background",
            border_color=ft.Colors.with_opacity(0.25, ft.Colors.WHITE),
            focused_border_color="primary",
            border_radius=ft.border_radius.only(bottom_left=8, bottom_right=8),
        )

        self.dd_estado_enemigo = ft.Dropdown(
            label=self.i18n.t("ui.tab_dps.estado_enemigo"),
            dense=True, text_size=13,
            options=[
                ft.dropdown.Option("Normal",     text=self.i18n.t("ui.tab_dps.estado_normal")),
                ft.dropdown.Option("Stun_Boss",  text=self.i18n.t("ui.tab_dps.estado_aturdido")),
            ],
            value="Normal",
            bgcolor="background",
            border_radius=ft.border_radius.only(bottom_left=8, bottom_right=8),
            border_color=ft.Colors.with_opacity(0.25, ft.Colors.WHITE),
            focused_border_color="primary"
        )

        self.dd_miasma = ft.Dropdown(
            label=self.i18n.t("ui.tab_dps.miasma"),
            dense=True, text_size=13,
            options=[
                ft.dropdown.Option("Desactivado", text=self.i18n.t("ui.tab_dps.desactivado")),
                ft.dropdown.Option("Activo",       text=self.i18n.t("ui.tab_dps.activo")),
            ],
            value="Desactivado",
            bgcolor="background",
            border_radius=ft.border_radius.only(bottom_left=8, bottom_right=8),
            border_color=ft.Colors.with_opacity(0.25, ft.Colors.WHITE),
            focused_border_color="primary"
        )

        marco_enemigo = ft.Container(
            content=self.img_enemigo,
            padding=5,
            border=ft.border.all(1, ft.Colors.OUTLINE),
            border_radius=12,
            bgcolor="surface",
            shadow=ft.BoxShadow(blur_radius=12, spread_radius=0, color=ft.Colors.BLACK26),
            animate_scale=ft.Animation(280, ft.AnimationCurve.EASE_OUT),
        )
        def on_hover_enemigo(e):
            marco_enemigo.scale = 1.04 if e.data == "true" else 1.0
            marco_enemigo.update()
        marco_enemigo.on_hover = on_hover_enemigo

        enemy_header = ft.Column([
            ft.Row([
                self.enemy_dropdown,
                marco_enemigo
            ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            ft.Row([self.dd_estado_enemigo, self.dd_miasma], spacing=6)
        ], spacing=6)

        parametros_enemigo_base = [
            (self.i18n.t("stats.defensa_base"),    "Defensa_Base"),
            (self.i18n.t("stats.resistencia"),      "Resistencia_porcentual"),
            (self.i18n.t("stats.defensa_plana"),    "Defensa_Plana"),
            (self.i18n.t("stats.res_fuego"),        "Resistencia_Fuego"),
            (self.i18n.t("stats.res_elec"),         "Resistencia_Electrico"),
            (self.i18n.t("stats.res_hielo"),        "Resistencia_Hielo"),
            (self.i18n.t("stats.res_fisico"),       "Resistencia_Físico"),
            (self.i18n.t("stats.res_etereo"),       "Resistencia_Etereo"),
            (self.i18n.t("stats.res_viento"),       "Resistencia_Viento")
        ]
        enemy_fields_readonly = []
        for label, key in parametros_enemigo_base:
            field = ft.TextField(
                label=label, read_only=True, dense=True,
                text_size=12, height=40, content_padding=10, bgcolor="surface"
            )
            self.entry_vars[key] = field
            enemy_fields_readonly.append(field)

        self.campo_pen_res = ft.TextField(
            label=self.i18n.t("ui.tab_dps.resistencia_perforada"),
            expand=True, read_only=True, dense=True,
            data="Pen_Res_Fisico", text_size=13, height=40, content_padding=10,
            bgcolor=ft.Colors.with_opacity(0.04, ft.Colors.WHITE),
            border_color=ft.Colors.with_opacity(0.1, ft.Colors.WHITE)
        )
        self.entry_vars["Pen_Res_Fisico"] = self.campo_pen_res

        field_def_shred = ft.TextField(
            label=self.i18n.t("ui.tab_dps.reduccion_def"),
            expand=True, read_only=True, dense=True,
            data="Reduccion_DEF_enemigo", text_size=13, height=40, content_padding=10,
            bgcolor=ft.Colors.with_opacity(0.04, ft.Colors.WHITE),
            border_color=ft.Colors.with_opacity(0.1, ft.Colors.WHITE)
        )
        self.entry_vars["Reduccion_DEF_enemigo"] = field_def_shred

        self.campo_red_res = ft.TextField(
            label=self.i18n.t("ui.tab_dps.reduccion_res"),
            expand=True, read_only=True, dense=True,
            data="Red_Resistencia_Global", text_size=13, height=40, content_padding=10,
            bgcolor=ft.Colors.with_opacity(0.04, ft.Colors.WHITE),
            border_color=ft.Colors.with_opacity(0.1, ft.Colors.WHITE)
        )
        self.entry_vars["Red_Resistencia_Global"] = self.campo_red_res

        enemy_grid = ft.GridView(
            runs_count=2, max_extent=150, child_aspect_ratio=2.5,
            spacing=6, run_spacing=6, controls=enemy_fields_readonly
        )

        debuffs_row = ft.Row(
            controls=[self.campo_pen_res, field_def_shred, self.campo_red_res],
            spacing=6
        )

        self.dd_elemento_vortex = ft.Dropdown(
            label="Vortex",
            dense=True, text_size=12, width=150, value="Automático",
            options=[
                ft.dropdown.Option("Automático"),
                ft.dropdown.Option("fuego", text="Fuego"),
                ft.dropdown.Option("electrico", text="Eléctrico"),
                ft.dropdown.Option("hielo", text="Hielo"),
                ft.dropdown.Option("frost", text="Frost"),
                ft.dropdown.Option("fisico", text="Físico"),
                ft.dropdown.Option("etereo", text="Éter"),
            ],
            bgcolor="surface",
            focused_border_color="primary",
            on_change=self.app.calcular_dano,
        )
        vortex_tiempo = ft.TextField(label="t Vortex", value="3", dense=True, text_size=12, height=40, content_padding=10, width=90, on_change=self.app.calcular_dano)
        vortex_mv = ft.TextField(label="MV extra %", value="0", dense=True, text_size=12, height=40, content_padding=10, width=110, on_change=self.app.calcular_dano)
        vortex_buff = ft.TextField(label="Buff Vortex %", value="0", dense=True, text_size=12, height=40, content_padding=10, width=120, on_change=self.app.calcular_dano)
        self.entry_vars["Vortex_Tiempo"] = vortex_tiempo
        self.entry_vars["Vortex_Additional_MV"] = vortex_mv
        self.entry_vars["Vortex_Buff"] = vortex_buff
        vortex_row = ft.Row(
            controls=[self.dd_elemento_vortex, vortex_tiempo, vortex_mv, vortex_buff],
            spacing=6,
            wrap=True,
        )

        # ── Cards izquierda ───────────────────────────────────────────
        card_agente = ft.Card(
            ft.Container(content=top_card_content, padding=ft.padding.all(14)),
            elevation=2,
        )

        card_stats = ft.Card(
            ft.Container(
                content=ft.Column([
                    ft.Text(self.i18n.t("ui.tab_dps.estadisticas_base"),
                            weight=ft.FontWeight.BOLD, size=14),
                    ft.Divider(height=6),
                    stats_columns
                ], spacing=6),
                padding=ft.padding.all(18)
            ),
            elevation=2,
        )

        # ── Panel de bonos activos (vertical) ─────────────────────────
        self.panel_bonos_activos = ft.Column(spacing=4)
        self.card_bonos_activos = ft.Card(
            ft.Container(
                content=ft.Column([
                    ft.Text(self.i18n.t("ui.tab_dps.buffs"),
                            weight=ft.FontWeight.BOLD, size=12),
                    self.panel_bonos_activos
                ], spacing=6),
                padding=ft.padding.all(8),
                width=155,
            ),
            elevation=2,
            visible=False
        )

        columna_izquierda = ft.Column(
            spacing=12,
            controls=[card_agente, card_stats, tarjeta_discos_nueva]
        )

        left_content = ft.Stack(
            controls=[columna_izquierda, contenedor_lista_dps],
            clip_behavior=ft.ClipBehavior.NONE
        )

        # ── Resultados ────────────────────────────────────────────────
        style_res = ft.TextStyle(size=15, weight=ft.FontWeight.BOLD)

        def crear_texto_sombreado(texto_inicial):
            return ft.ShaderMask(
                content=ft.Text(texto_inicial, style=style_res, color=ft.Colors.WHITE),
                blend_mode=ft.BlendMode.SRC_IN,
                shader=ft.LinearGradient(
                    begin=ft.alignment.top_center,
                    end=ft.alignment.bottom_center,
                    colors=["outline", "outline"]
                )
            )

        self.resultado_normal   = crear_texto_sombreado(self.i18n.t("ui.tab_dps.resultados_normal"))
        self.resultado_sheer    = crear_texto_sombreado(self.i18n.t("ui.tab_dps.resultados_sheer"))
        self.resultado_anomaly  = crear_texto_sombreado(self.i18n.t("ui.tab_dps.resultados_anomalia"))
        self.resultado_abloom   = crear_texto_sombreado(self.i18n.t("ui.tab_dps.resultados_abloom"))
        self.resultado_disorder = crear_texto_sombreado(self.i18n.t("ui.tab_dps.resultados_disorder"))
        self.resultado_vortex   = crear_texto_sombreado(self.i18n.t("ui.tab_dps.resultados_vortex", default="Vortex"))

        self.resultados_text = ft.TextField(
            label=self.i18n.t("ui.tab_dps.detalles"),
            multiline=True, read_only=True, text_size=12, height=675,
            bgcolor=ft.Colors.with_opacity(0.04, ft.Colors.WHITE),
            border_color=ft.Colors.with_opacity(0.1, ft.Colors.WHITE)
        )

        self.dd_elemento_abloom = ft.Dropdown(
            label=self.i18n.t("ui.tab_dps.elemento_abloom"),
            dense=True, text_size=12, width=140, visible=False,
            options=[ft.dropdown.Option("Automático", text=self.i18n.t("ui.tab_dps.automatico"))],
            value="Automático",
            bgcolor="background",
            border_color=ft.Colors.with_opacity(0.25, ft.Colors.WHITE),
            focused_border_color="primary",
            border_radius=ft.border_radius.only(bottom_left=8, bottom_right=8)
        )

        header_resultados = ft.Row([
            ft.Text(self.i18n.t("ui.tab_dps.resultados"), weight=ft.FontWeight.BOLD, size=16),
            self.dd_elemento_abloom
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        # ── Botón calcular con hover ──────────────────────────────────
        btn_calcular = ft.Container(
            content=ft.ElevatedButton(
                content=ft.Text(self.i18n.t("ui.tab_dps.btn_calcular"), weight="bold"),
                on_click=self.app.calcular_dano,
                bgcolor="primary",
                color="background",
                height=48,
                width=190,
            ),
            animate_scale=ft.Animation(250, ft.AnimationCurve.EASE_OUT),
        )
        def on_hover_btn_calcular(e):
            btn_calcular.scale = 1.05 if e.data == "true" else 1.0
            btn_calcular.update()
        btn_calcular.on_hover = on_hover_btn_calcular

        right_content = ft.Column(
            spacing=12,
            controls=[
                # Card enemigo
                ft.Card(
                    ft.Container(
                        content=ft.Column([
                            ft.Text(self.i18n.t("ui.tab_dps.stats_enemigo"),
                                    weight=ft.FontWeight.BOLD, size=14),
                            enemy_header,
                            enemy_grid,
                            ft.Divider(height=10, thickness=1),
                            ft.Text(self.i18n.t("ui.tab_dps.modificadores_def_res"),
                                    size=self.FS['xs'], italic=True),
                            debuffs_row,
                            vortex_row
                        ], spacing=12),
                        padding=ft.padding.all(14)
                    ),
                    elevation=2,
                ),

                # Card resultados
                ft.Card(
                    ft.Container(
                        content=ft.Column([
                            header_resultados,
                            ft.Divider(height=6),
                            self.resultado_normal,
                            self.resultado_sheer,
                            self.resultado_anomaly,
                            self.resultado_abloom,
                            self.resultado_disorder,
                            self.resultado_vortex,
                            ft.Container(height=12),
                            ft.Row([btn_calcular], alignment=ft.MainAxisAlignment.CENTER),
                            self.resultados_text
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=6),
                        padding=ft.padding.all(14)
                    ),
                    elevation=2,
                )
            ]
        )

        contenido_responsivo = ft.Row(
            controls=[
                self.card_bonos_activos,
                ft.ResponsiveRow(
                    controls=[
                        ft.Column(controls=[left_content],  col={"xl": 6, "lg": 7, "md": 7, "sm": 12}),
                        ft.Column(controls=[right_content], col={"xl": 6, "lg": 5, "md": 5, "sm": 12})
                    ],
                    spacing=14,
                    run_spacing=14,
                    expand=True,
                ),
            ],
            spacing=4,
            vertical_alignment=ft.CrossAxisAlignment.START,
        )

        selector_idioma = self._crear_selector_idioma()

        self.contenedor_personajes_wrapper = ft.Container(
            content=self.contenedor_personajes_importados,
            padding=ft.padding.symmetric(horizontal=12, vertical=10),
            border=ft.border.all(1, ft.Colors.OUTLINE),
            border_radius=12,
            visible=False
        )

        return ft.Column(
            controls=[
                selector_idioma,
                self.contenedor_personajes_wrapper,
                contenido_responsivo
            ],
            scroll=ft.ScrollMode.AUTO, expand=True
        )

    def _crear_selector_idioma(self):
        """Crea la fila de botones para cambiar el idioma de la interfaz.
        Aparece en la parte superior de la pestaña DPS.
        """
        from traductor import IDIOMAS_DISPONIBLES
        disponibles = self.i18n.idiomas_disponibles()
        self.botones_idioma = {}

        etiquetas = {"es": "🇪🇸 ES", "en": "🇺🇸 EN", "ja": "🇯🇵 JA", "zh": "🇨🇳 ZH"}
        botones = []
        for codigo in ["es", "en", "ja", "zh"]:
            if codigo not in disponibles:
                continue
            es_activo = codigo == self.i18n.idioma_actual
            btn = ft.ElevatedButton(
                text=etiquetas.get(codigo, codigo.upper()),
                on_click=lambda e, c=codigo: self.app.i18n.cambiar_idioma(c),
                style=ft.ButtonStyle(
                    bgcolor=ft.Colors.PRIMARY if es_activo else ft.Colors.SURFACE,
                    color=ft.Colors.ON_PRIMARY if es_activo else ft.Colors.ON_SURFACE,
                    shape=ft.RoundedRectangleBorder(radius=8),
                    padding=ft.padding.symmetric(horizontal=12, vertical=6),
                ),
                height=32,
            )
            self.botones_idioma[codigo] = btn
            botones.append(btn)

        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.LANGUAGE, size=16, color="secondary", tooltip="Idioma / Language / 言語"),
                ] + botones,
                spacing=6,
                alignment=ft.MainAxisAlignment.END,
            ),
            padding=ft.padding.only(right=8, top=4, bottom=4),
        )

    def actualizar_botones_idioma(self, idioma_activo):
        """Actualiza el estilo visual del botón activo tras un cambio de idioma."""
        for codigo, btn in self.botones_idioma.items():
            es_activo = codigo == idioma_activo
            btn.style.bgcolor = ft.Colors.PRIMARY if es_activo else ft.Colors.SURFACE
            btn.style.color = ft.Colors.ON_PRIMARY if es_activo else ft.Colors.ON_SURFACE
            btn.update()

    def actualizar_colores_discos_ui(self, e=None):
        """Evalúa los dropdowns de los discos y les asigna un color si son ideales o decentes."""
        
        nombre_agente = self.app.estado_actual.nombre_agente if hasattr(self.app, 'estado_actual') else "Ninguno"
        
        if not nombre_agente or nombre_agente == "Ninguno":
            return 

        rol_agente = "Atacante"
        if hasattr(self.app, 'agentes_data') and self.app.agentes_data:
            datos_agente = next((a for a in self.app.agentes_data if a['Nombre'] == nombre_agente), None)
            if datos_agente:
                rol_agente = datos_agente.get("Tipo", "Atacante")

        config_rol = CONFIG_ROLES.get(rol_agente, CONFIG_ROLES["Atacante"])
        ideales_raw = config_rol.get("subs", {}).get("ideal", [])
        decentes_raw = config_rol.get("subs", {}).get("decente", [])

        if nombre_agente in EXCEPCIONES_AGENTES:
            excep = EXCEPCIONES_AGENTES[nombre_agente]
            if "subs" in excep:
                ideales_raw = excep["subs"].get("ideal", ideales_raw)
                decentes_raw = excep["subs"].get("decente", decentes_raw)

        def normalizar_stat(k):
            if not k: return "nada"
            k = str(k).lower().strip()
            if "prob" in k or "rate" in k: return "probabilidad"
            if "daño cr" in k or "crit dmg" in k: return "daño_crítico"
            if "ataque" in k or "atk" in k: return "ataque"
            if "vida" in k or "hp" in k: return "vida"
            if "defensa" in k or "def" in k: return "defensa"
            if "anomalía" in k or "anom" in k: 
                if "tasa" in k: return "tasa_anomalia"
                return "maestria_anomalia"
            if "perf" in k or "pen" in k:
                if "plana" in k: return "perforacion_plana"
                return "tasa_perforacion"
            if "recup" in k or "energ" in k: return "recuperacion"
            return k

        ideales_clean = [normalizar_stat(s) for s in ideales_raw]
        decentes_clean = [normalizar_stat(s) for s in decentes_raw]

        color_ideal = "#ffb300"
        color_decente = "#00bcd4" 
        
        controles_a_actualizar = []

        for slot in range(1, 7):
            for i in range(1, 5):
                dd = self.team_controls.get(f"disco_{slot}_sub_{i}_stat")
                if dd and dd.value:
                    val_norm = normalizar_stat(dd.value)
                    if any(ideal in val_norm for ideal in ideales_clean):
                        dd.border_color = color_ideal
                    elif any(dec in val_norm for dec in decentes_clean):
                        dd.border_color = color_decente
                    else:
                        dd.border_color = None
                    controles_a_actualizar.append(dd)

            dd_main = self.team_controls.get(f"disco_{slot}_main")
            if dd_main and dd_main.value and isinstance(dd_main, ft.Dropdown):
                val_norm = normalizar_stat(dd_main.value)
                if any(ideal in val_norm for ideal in ideales_clean):
                    dd_main.border_color = color_ideal
                elif any(dec in val_norm for dec in decentes_clean):
                    dd_main.border_color = color_decente
                else:
                    dd_main.border_color = None
                controles_a_actualizar.append(dd_main)

        if e and e.control.page:
            e.control.page.update()
        elif hasattr(self, 'app') and hasattr(self.app, 'page'):
            self.app.page.update()

    def crear_bloque_disco_ui(self, slot: int):
        """Genera un panel individual para un disco (1 al 6). — VISUAL REFACTOR"""

        dd_set = ft.Dropdown(
            label=self.i18n.t("ui.tab_dps.set_disco"), options=[],
            dense=False,
            text_size=12,
            text_style=ft.TextStyle(weight="bold"),
            content_padding=15,
            expand=True,
            bgcolor="background",
            border_radius=ft.border_radius.only(bottom_left=8, bottom_right=8),
            border_color=ft.Colors.with_opacity(0.25, ft.Colors.WHITE),
            focused_border_color="primary",
        )
        self.team_controls[f"disco_{slot}_set"] = dd_set

        if slot in [1, 2, 3]:
            stats_fijas = {
                1: self.i18n.t("stats.vida_plana"),
                2: self.i18n.t("stats.ataque_plano"),
                3: self.i18n.t("stats.defensa_plana")
            }
            ctrl_main = ft.TextField(
                label=self.i18n.t("ui.tab_dps.main_stat"), value=stats_fijas[slot],
                read_only=True,
                dense=False,
                text_size=12,
                text_style=ft.TextStyle(weight="bold"),
                content_padding=15,
                expand=True,
                bgcolor=ft.Colors.with_opacity(0.04, ft.Colors.WHITE),
                border_color=ft.Colors.with_opacity(0.1, ft.Colors.WHITE)
            )
        else:
            ctrl_main = ft.Dropdown(
                label=self.i18n.t("ui.tab_dps.main_stat"), options=[],
                dense=False,
                text_size=12,
                text_style=ft.TextStyle(weight="bold"),
                content_padding=15,
                expand=True,
                bgcolor="background",
                border_radius=ft.border_radius.only(bottom_left=8, bottom_right=8),
                border_color=ft.Colors.with_opacity(0.25, ft.Colors.WHITE),
                focused_border_color="primary",
            )
        self.team_controls[f"disco_{slot}_main"] = ctrl_main

        img_disco = ft.Image(
            src="images/discos/default.png",
            width=88,
            height=88,
            fit=ft.ImageFit.COVER,
            opacity=0.3
        )
        self.team_controls[f"disco_{slot}_img"] = img_disco

        container_imagen = ft.Container(
            content=img_disco,
            padding=0,
            width=88,
            height=88,
            border_radius=44,
            bgcolor="surface",
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
            border=ft.border.all(2, "outline"),
            shadow=ft.BoxShadow(blur_radius=10, spread_radius=1, color=ft.Colors.BLACK38),
        )

        row_superior = ft.Row([
            ft.Column([
                ft.Row([dd_set]),
                ft.Row([ctrl_main])
            ], expand=True, spacing=6),
            container_imagen
        ], vertical_alignment=ft.CrossAxisAlignment.CENTER)

        filas_subs = []
        for i in range(1, 5):
            dd_sub = ft.Dropdown(
                hint_text=f"Sub {i}",
                dense=True,
                text_size=12,
                text_style=ft.TextStyle(weight="bold"),
                expand=True,
                bgcolor="background",
                border_radius=ft.border_radius.only(bottom_left=8, bottom_right=8),
                border_color=ft.Colors.with_opacity(0.25, ft.Colors.WHITE),
                focused_border_color="primary",
                content_padding=12,
                on_change=self.actualizar_colores_discos_ui
            )
            txt_rolls = ft.Text(
                "0", width=16, text_align="center", size=12,
                weight="bold", color="primary"
            )
            btn_minus = ft.IconButton(
                ft.Icons.REMOVE, icon_size=14, padding=0, width=32, height=32,
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=6))
            )
            btn_plus = ft.IconButton(
                ft.Icons.ADD, icon_size=14, padding=0, width=32, height=32,
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=6))
            )

            fila = ft.Row([
                dd_sub, btn_minus, txt_rolls, btn_plus
            ], spacing=2, vertical_alignment=ft.CrossAxisAlignment.CENTER)
            filas_subs.append(fila)

            self.team_controls[f"disco_{slot}_sub_{i}_stat"] = dd_sub
            self.team_controls[f"disco_{slot}_sub_{i}_rolls"] = txt_rolls
            self.team_controls[f"disco_{slot}_sub_{i}_btn_minus"] = btn_minus
            self.team_controls[f"disco_{slot}_sub_{i}_btn_plus"] = btn_plus

        romanos = {1: "I", 2: "II", 3: "III", 4: "IV", 5: "V", 6: "VI"}

        txt_rolls_disco = ft.Text("0/9", size=12, weight="bold")
        self.team_controls[f"disco_{slot}_total_rolls"] = txt_rolls_disco

        header = ft.Row([
            ft.Row([
                ft.Container(
                    content=ft.Text(romanos[slot], weight="bold", size=11, color="background"),
                    bgcolor="primary",
                    padding=ft.padding.symmetric(horizontal=7, vertical=3),
                    border_radius=8,
                    shadow=ft.BoxShadow(blur_radius=6, spread_radius=0, color=ft.Colors.with_opacity(0.4, ft.Colors.PRIMARY))
                ),
                ft.Text(
                    f"{self.i18n.t('ui.tab_dps.ranura')} {slot}",
                    weight="bold", color="primary", size=12
                )
            ], spacing=6),
            txt_rolls_disco
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        # ── Hover effect ──────────────────────────────────────────────
        tarjeta = ft.Container(
            padding=ft.padding.all(15),
            bgcolor="surface",
            border_radius=12,
            border=ft.border.all(1, "outline"),
            shadow=ft.BoxShadow(
                blur_radius=12, spread_radius=0,
                color=ft.Colors.BLACK26,
                offset=ft.Offset(0, 3)
            ),
            animate_scale=ft.Animation(280, ft.AnimationCurve.EASE_OUT),
            content=ft.Column([
                header,
                row_superior,
                ft.Divider(height=6, color="outline"),
                ft.Text(
                    self.i18n.t("ui.tab_dps.sub_stats_desc"),
                    size=10, color="secondary"
                ),
                *filas_subs
            ], spacing=12)
        )

        def on_hover_disco(e):
            tarjeta.scale = 1.015 if e.data == "true" else 1.0
            tarjeta.shadow = ft.BoxShadow(
                blur_radius=22 if e.data == "true" else 12,
                spread_radius=1 if e.data == "true" else 0,
                color=ft.Colors.with_opacity(
                    0.45 if e.data == "true" else 0.25,
                    ft.Colors.PRIMARY
                ),
                offset=ft.Offset(0, 4 if e.data == "true" else 3)
            )
            tarjeta.update()

        tarjeta.on_hover = on_hover_disco

        return tarjeta

    def _crear_panel_soporte(self, titulo, prefijo_key, lista_agentes, lista_wengines, lista_sets, color_tema="primary"):
        """Crea una tarjeta visual para un personaje de soporte. — VISUAL REFACTOR"""

        img_agente  = ft.Image(src="images/default.png", width=60, height=65, fit=ft.ImageFit.CONTAIN, opacity=0.3, border_radius=5)
        img_wengine = ft.Image(src="images/wengine/default_wengine.png", width=60, height=60, fit=ft.ImageFit.CONTAIN, opacity=0.3, border_radius=5)
        img_set     = ft.Image(src="images/discos/default.png", width=60, height=60, fit=ft.ImageFit.CONTAIN, opacity=0.3, border_radius=4)

        marco_agente = ft.Container(
            content=img_agente,
            padding=5,
            border=ft.border.all(1, "outline"),
            border_radius=12,
            bgcolor="surface",
            shadow=ft.BoxShadow(blur_radius=8, spread_radius=0, color=ft.Colors.BLACK26),
            animate_scale=ft.Animation(260, ft.AnimationCurve.EASE_OUT),
        )
        def on_hover_marco_agente(e):
            marco_agente.scale = 1.06 if e.data == "true" else 1.0
            marco_agente.update()
        marco_agente.on_hover = on_hover_marco_agente

        marco_wengine = ft.Container(
            content=img_wengine,
            padding=5,
            border=ft.border.all(1, "outline"),
            border_radius=12,
            bgcolor="surface",
            shadow=ft.BoxShadow(blur_radius=8, spread_radius=0, color=ft.Colors.BLACK26),
            animate_scale=ft.Animation(260, ft.AnimationCurve.EASE_OUT),
        )
        def on_hover_marco_wengine(e):
            marco_wengine.scale = 1.06 if e.data == "true" else 1.0
            marco_wengine.update()
        marco_wengine.on_hover = on_hover_marco_wengine

        dd_agente_oculto = ft.Dropdown(visible=False)
        lista_resultados_agente = ft.ListView(spacing=0)

        contenedor_lista_agente = ft.Container(
            content=lista_resultados_agente,
            bgcolor="background",
            border_radius=ft.border_radius.only(bottom_left=8, bottom_right=8),
            border=ft.border.all(1, "primary"),
            shadow=ft.BoxShadow(spread_radius=2, blur_radius=12, color=ft.Colors.BLACK87),
            visible=False,
            top=100, left=82, right=82
        )

        txt_agente = ft.TextField(
            label=self.i18n.t("ui.tab_equipo.buscar_agente"),
            dense=True, text_size=13,
            prefix_icon=ft.Icons.SEARCH,
        )

        class EventoSimulado:
            def __init__(self, control):
                self.control = control
                self.data = control.value

        def seleccionar_agente(e):
            seleccion = e.control.data
            txt_agente.value = seleccion
            contenedor_lista_agente.visible = False
            dd_agente_oculto.value = seleccion
            if dd_agente_oculto.on_change:
                dd_agente_oculto.on_change(EventoSimulado(dd_agente_oculto))
            txt_agente.update()
            contenedor_lista_agente.update()

        def crear_item_lista(texto):
            return ft.Container(
                content=ft.Text(texto, size=13),
                padding=ft.padding.symmetric(horizontal=14, vertical=11),
                ink=True, data=texto, on_click=seleccionar_agente
            )

        def obtener_opciones_reales():
            if dd_agente_oculto.options:
                return [opt.key if opt.key else opt.text for opt in dd_agente_oculto.options]
            return []

        def filtrar_agentes(e):
            texto = txt_agente.value.lower()
            lista_resultados_agente.controls.clear()
            opciones = obtener_opciones_reales()
            sugerencias = opciones if texto == "" else [a for a in opciones if texto in str(a).lower()]
            for s in sugerencias:
                lista_resultados_agente.controls.append(crear_item_lista(s))
            cantidad = len(sugerencias)
            if cantidad > 0:
                lista_resultados_agente.height = min(150, cantidad * 40)
                contenedor_lista_agente.visible = True
            else:
                contenedor_lista_agente.visible = False
            contenedor_lista_agente.update()

        def mostrar_todo_al_hacer_clic(e):
            filtrar_agentes(e)

        txt_agente.on_change = filtrar_agentes
        txt_agente.on_focus  = mostrar_todo_al_hacer_clic

        def on_blur_buscador_agente(e):
            import threading, time
            def cerrar():
                time.sleep(0.15)
                contenedor_lista_agente.visible = False
                contenedor_lista_agente.update()
            threading.Thread(target=cerrar, daemon=True).start()

        txt_agente.on_blur = on_blur_buscador_agente

        dd_mindscape = ft.Dropdown(
            label=self.i18n.t("ui.tab_equipo.dupe"), width=90, dense=True, text_size=12,
            options=[ft.dropdown.Option(str(i), text=f"M{i}") for i in range(7)],
            value="0",
            tooltip=self.i18n.t("ui.tab_equipo.tooltip_dupe"),
            bgcolor="background",
            border_radius=ft.border_radius.only(bottom_left=8, bottom_right=8),
            border_color=ft.Colors.with_opacity(0.25, ft.Colors.WHITE),
            focused_border_color="primary"
        )

        dd_m_stacks = ft.Dropdown(
            label=self.i18n.t("ui.tab_equipo.cargas"), width=90, dense=True, text_size=12,
            options=[ft.dropdown.Option("0")], value="0", visible=False,
            tooltip=self.i18n.t("ui.tab_equipo.tooltip_cargas"),
            bgcolor="background",
            border_radius=ft.border_radius.only(bottom_left=8, bottom_right=8),
            border_color=ft.Colors.with_opacity(0.25, ft.Colors.WHITE),
            focused_border_color="primary"
        )

        chk_m_cond = ft.Checkbox(
            label=self.i18n.t("ui.tab_equipo.activar_dupes"),
            value=False,
            tooltip=self.i18n.t("ui.tab_equipo.tooltip_activar_dupes")
        )

        dd_wengine = ft.Dropdown(
            label=self.i18n.t("ui.tab_equipo.wengine"),
            options=[ft.dropdown.Option(w) for w in lista_wengines],
            expand=True, dense=True, text_size=13,
            max_menu_height=200, editable=True,
            bgcolor="background",
            border_color=ft.Colors.with_opacity(0.25, ft.Colors.WHITE),
            focused_border_color="primary",
            border_radius=ft.border_radius.only(bottom_left=8, bottom_right=8)
        )

        dd_ref = ft.Dropdown(
            label=self.i18n.t("ui.tab_equipo.ref"), width=90, dense=True, text_size=12,
            options=[ft.dropdown.Option(str(i)) for i in range(1, 6)],
            value="1",
            bgcolor="background",
            border_radius=ft.border_radius.only(bottom_left=8, bottom_right=8),
            border_color=ft.Colors.with_opacity(0.25, ft.Colors.WHITE),
            focused_border_color="primary"
        )

        dd_stacks = ft.Dropdown(
            label=self.i18n.t("ui.tab_equipo.w_stacks"), width=120, dense=True, text_size=12,
            options=[ft.dropdown.Option(key="0", text="0")], value="0", visible=False,
            bgcolor="background",
            border_radius=ft.border_radius.only(bottom_left=8, bottom_right=8),
            border_color=ft.Colors.with_opacity(0.25, ft.Colors.WHITE),
            focused_border_color="primary"
        )

        chk_wengine_activo = ft.Checkbox(
            label=self.i18n.t("ui.tab_equipo.wengine_activo", default="W-Engine"),
            value=True, visible=False,
            tooltip=self.i18n.t("ui.tab_equipo.tooltip_wengine_activo", default="Activar/desactivar el efecto del W-Engine"),
        )

        dd_set_stacks = ft.Dropdown(
            label=self.i18n.t("ui.tab_equipo.cargas"), width=110, dense=True, text_size=12,
            options=[ft.dropdown.Option(key="0", text="0")], value="0", visible=False,
            bgcolor="background",
            border_radius=ft.border_radius.only(bottom_left=8, bottom_right=8),
            border_color=ft.Colors.with_opacity(0.25, ft.Colors.WHITE),
            focused_border_color="primary"
        )

        dd_set4 = ft.Dropdown(
            label=self.i18n.t("ui.tab_equipo.set_4_piezas"),
            options=[ft.dropdown.Option(s) for s in lista_sets],
            dense=True, text_size=13, enable_filter=True, editable=True,
            max_menu_height=200,
            bgcolor="background",
            border_radius=ft.border_radius.only(bottom_left=8, bottom_right=8),
            border_color=ft.Colors.with_opacity(0.25, ft.Colors.WHITE),
            focused_border_color="primary"
        )

        txt_tipo     = ft.Image(src="images/elementos/default.png", width=32, height=32, fit=ft.ImageFit.CONTAIN, opacity=0.3, tooltip=self.i18n.t("ui.tab_equipo.tipo"))
        txt_elemento = ft.Image(src="images/elementos/default.png", width=32, height=32, fit=ft.ImageFit.CONTAIN, opacity=0.3, tooltip=self.i18n.t("ui.tab_equipo.elemento"))
        txt_faccion  = ft.Image(src="images/faccion/default.png",   width=32, height=32, fit=ft.ImageFit.CONTAIN, opacity=0.3, tooltip=self.i18n.t("ui.tab_equipo.faccion"))

        txt_ataque  = ft.TextField(label=self.i18n.t("stats.ataque"),           suffix_text="",  expand=True, dense=True, text_size=12, value="0")
        txt_pv      = ft.TextField(label=self.i18n.t("stats.puntos_vida"),      suffix_text="",  expand=True, dense=True, text_size=12, value="0")
        txt_prob    = ft.TextField(label=self.i18n.t("stats.prob_crit"),        suffix_text="%", expand=True, dense=True, text_size=12, value="0")
        txt_dano    = ft.TextField(label=self.i18n.t("stats.dano_crit"),        suffix_text="%", expand=True, dense=True, text_size=12, value="0")
        txt_perfo   = ft.TextField(label=self.i18n.t("stats.perforacion"),      suffix_text="%", expand=True, dense=True, text_size=12, value="0")
        txt_tasa    = ft.TextField(label=self.i18n.t("stats.tasa_anomalia"),    suffix_text="",  expand=True, dense=True, text_size=12, value="0")
        txt_recarga = ft.TextField(label=self.i18n.t("stats.rec_energia"),      suffix_text="%", expand=True, dense=True, text_size=12, value="0")
        txt_imp     = ft.TextField(label=self.i18n.t("stats.impacto"),          suffix_text="",  expand=True, dense=True, text_size=12, value="0")
        txt_am      = ft.TextField(label=self.i18n.t("stats.maestria_anomalia"),suffix_text="",  expand=True, dense=True, text_size=12, value="0")
        txt_def     = ft.TextField(label=self.i18n.t("stats.defensa"),          suffix_text="",  expand=True, dense=True, text_size=12, value="0")

        # ── Registro en team_controls (intocable) ─────────────────────
        self.team_controls[f"{prefijo_key}_agente"]           = dd_agente_oculto
        self.team_controls[f"{prefijo_key}_mindscape"]        = dd_mindscape
        self.team_controls[f"{prefijo_key}_mindscape_stacks"] = dd_m_stacks
        self.team_controls[f"{prefijo_key}_mindscape_cond"]   = chk_m_cond
        self.team_controls[f"{prefijo_key}_wengine"]          = dd_wengine
        self.team_controls[f"{prefijo_key}_wengine_ref"]      = dd_ref
        self.team_controls[f"{prefijo_key}_wengine_stacks"]   = dd_stacks
        self.team_controls[f"{prefijo_key}_wengine_activo"]   = chk_wengine_activo
        self.team_controls[f"{prefijo_key}_set4"]             = dd_set4
        self.team_controls[f"{prefijo_key}_set_stacks"]       = dd_set_stacks
        self.team_controls[f"{prefijo_key}_img_agente"]       = img_agente
        self.team_controls[f"{prefijo_key}_img_wengine"]      = img_wengine
        self.team_controls[f"{prefijo_key}_img_set"]          = img_set
        self.team_controls[f"{prefijo_key}_tipo"]             = txt_tipo
        self.team_controls[f"{prefijo_key}_elemento"]         = txt_elemento
        self.team_controls[f"{prefijo_key}_faccion"]          = txt_faccion
        self.team_controls[f"{prefijo_key}_stat_atk"]         = txt_ataque
        self.team_controls[f"{prefijo_key}_stat_hp"]          = txt_pv
        self.team_controls[f"{prefijo_key}_stat_crit_rate"]   = txt_prob
        self.team_controls[f"{prefijo_key}_stat_crit_dmg"]    = txt_dano
        self.team_controls[f"{prefijo_key}_stat_pen"]         = txt_perfo
        self.team_controls[f"{prefijo_key}_stat_am"]          = txt_tasa
        self.team_controls[f"{prefijo_key}_stat_er"]          = txt_recarga
        self.team_controls[f"{prefijo_key}_stat_imp"]         = txt_imp
        self.team_controls[f"{prefijo_key}_stat_am"]          = txt_am
        self.team_controls[f"{prefijo_key}_stat_def"]         = txt_def
        self.team_controls[f"{prefijo_key}_txt_busqueda"]     = txt_agente

        columna_central = ft.Column([
            txt_agente,
            ft.Row([dd_mindscape, dd_m_stacks, chk_m_cond], spacing=6, alignment=ft.MainAxisAlignment.START),
            ft.Row([dd_wengine, dd_ref, dd_stacks, chk_wengine_activo], spacing=6),
            dd_agente_oculto
        ], spacing=8, expand=True)

        btn_reiniciar_sup = ft.IconButton(
            icon=ft.Icons.RESTART_ALT,
            icon_color="error",
            tooltip=self.i18n.t("ui.tab_equipo.reiniciar_soporte"),
            on_click=lambda e: self.app.reiniciar_soporte(prefijo_key)
        )

        # ── Separador coloreado en el header ─────────────────────────
        header_tarjeta = ft.Container(
            content=ft.Row([
                ft.Row([
                    ft.Icon(ft.Icons.PERSON, size=16, color=color_tema),
                    ft.Text(titulo, weight="bold", color=color_tema, size=14)
                ], spacing=6),
                btn_reiniciar_sup
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=ft.padding.only(bottom=6),
            border=ft.border.only(bottom=ft.BorderSide(2, ft.Colors.with_opacity(0.35, color_tema))),
        )

        contenido_tarjeta = ft.Column([
            header_tarjeta,
            ft.Container(height=4),
            ft.Row([
                marco_agente,
                columna_central,
                marco_wengine
            ], alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.START, spacing=10),

            ft.Row([txt_ataque, txt_pv],    spacing=8),
            ft.Row([txt_prob,   txt_dano],  spacing=8),
            ft.Row([txt_perfo,  txt_tasa],  spacing=8),
            ft.Divider(height=8, color=ft.Colors.with_opacity(0.15, ft.Colors.WHITE)),
            ft.Row([txt_recarga,txt_am],    spacing=8),
            ft.Row([txt_imp,    txt_def],   spacing=8),

            ft.Divider(height=6, color="outline"),
            ft.Row([txt_tipo, txt_elemento, txt_faccion], spacing=10, alignment=ft.MainAxisAlignment.END),
            ft.Row([img_set, dd_set4, dd_set_stacks], spacing=6, vertical_alignment=ft.CrossAxisAlignment.CENTER)
        ], spacing=10)

        # ── Tarjeta con hover elevación ───────────────────────────────
        tarjeta = ft.Container(
            padding=ft.padding.all(15),
            bgcolor="surface",
            border_radius=12,
            border=ft.border.all(1, ft.Colors.with_opacity(0.6, color_tema)),
            shadow=ft.BoxShadow(
                blur_radius=14, spread_radius=0,
                color=ft.Colors.with_opacity(0.18, color_tema),
                offset=ft.Offset(0, 3)
            ),
            animate_scale=ft.Animation(280, ft.AnimationCurve.EASE_OUT),
            content=ft.Stack([
                contenido_tarjeta,
                contenedor_lista_agente
            ], clip_behavior=ft.ClipBehavior.NONE)
        )

        def on_hover_tarjeta(e):
            tarjeta.scale = 1.012 if e.data == "true" else 1.0
            tarjeta.shadow = ft.BoxShadow(
                blur_radius=26 if e.data == "true" else 14,
                spread_radius=2 if e.data == "true" else 0,
                color=ft.Colors.with_opacity(
                    0.35 if e.data == "true" else 0.18,
                    color_tema
                ),
                offset=ft.Offset(0, 5 if e.data == "true" else 3)
            )
            tarjeta.update()

        tarjeta.on_hover = on_hover_tarjeta
        return tarjeta

    def create_buffs_tab(self):
        """Pestaña de Buffs — VISUAL REFACTOR"""
        lista_agentes  = []
        lista_wengines = []
        lista_sets     = []

        btn_info = ft.IconButton(
            icon=ft.Icons.INFO_OUTLINE,
            icon_color="primary",
            tooltip=self.i18n.t("ui.tab_equipo.tooltip_info")
        )

        header_row = ft.Row(
            controls=[
                ft.Text(
                    self.i18n.t("ui.tab_equipo.config_equipo"),
                    size=22, weight=ft.FontWeight.BOLD
                ),
                btn_info
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=6
        )

        panel_sup1 = self._crear_panel_soporte(
            self.i18n.t("ui.tab_equipo.agente_1"), "sup1",
            lista_agentes, lista_wengines, lista_sets,
            color_tema="primary"
        )
        panel_sup2 = self._crear_panel_soporte(
            self.i18n.t("ui.tab_equipo.agente_2"), "sup2",
            lista_agentes, lista_wengines, lista_sets,
            color_tema="secondary"
        )

        self.lbl_resumen_buffs = ft.Text(
            self.i18n.t("ui.tab_equipo.desc_resumen"),
            italic=True, color="outline"
        )
        self.team_controls["resumen_texto"] = self.lbl_resumen_buffs

        # ── Panel resumen con borde suave y sombra ────────────────────
        panel_resumen = ft.Container(
            margin=ft.margin.only(top=14),
            padding=ft.padding.all(20),
            bgcolor="background",
            border=ft.border.all(1, "outline"),
            border_radius=12,
            shadow=ft.BoxShadow(
                blur_radius=16, spread_radius=0,
                color=ft.Colors.BLACK26,
                offset=ft.Offset(0, 3)
            ),
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.AUTO_AWESOME, size=18, color="primary"),
                    ft.Text(
                        self.i18n.t("ui.tab_equipo.resumen_efectos"),
                        size=self.FS['lg'], weight="bold"
                    )
                ], spacing=8),
                ft.Divider(height=10),
                self.lbl_resumen_buffs,
            ], spacing=8)
        )

        columna_contenido = ft.Column([
            header_row,
            ft.Container(height=6),
            ft.ResponsiveRow([
                ft.Column([panel_sup1], col={"md": 6, "sm": 12}),
                ft.Column([panel_sup2], col={"md": 6, "sm": 12}),
            ], spacing=14, run_spacing=14),
            panel_resumen
        ], scroll=ft.ScrollMode.AUTO, expand=True)

        return ft.Container(
            content=columna_contenido,
            padding=ft.padding.all(14),
            expand=True
        )

    def create_da_buffs_tab(self):
        """Pestaña DA Buffs — VISUAL REFACTOR"""

        # ── Estado (intocable) ────────────────────────────────────────
        self.da_active_buffs  = {}
        self.da_custom_buffs  = {}
        self.da_enemy_buffs   = {}
        self.da_imagen_actual = ""
        self.da_lista_imagenes = []
        self.da_indice_imagen  = 0

        _t = self.i18n.t
        self.mapa_stats_da = {
            _t("ui.tab_da_buffs.stats_da.ataque_pct",        default="ATK %"):                    "Ataque_%",
            _t("ui.tab_da_buffs.stats_da.dano_critico_pct",  default="CRIT DMG %"):               "Daño_crítico",
            _t("ui.tab_da_buffs.stats_da.prob_critica_pct",  default="CRIT Rate %"):              "Probabilidad_crítico",
            _t("ui.tab_da_buffs.stats_da.dano_elemental_pct",default="Elemental DMG %"):          "Daño_elemental",
            _t("ui.tab_da_buffs.stats_da.dmg_pct",           default="DMG %"):                   "Daño_Adicional",
            _t("ui.tab_da_buffs.stats_da.maestria_anomalia",  default="Anomaly Mastery"):         "Tasa_de_Anomalía",
            _t("ui.tab_da_buffs.stats_da.anomaly_proficiency", default="Anomaly Proficiency"):     "Maestría_Anomalía",
            _t("ui.tab_da_buffs.stats_da.bono_acumulacion",   default="Anomaly Buildup Bonus %"): "Bono_Acumulación",
            _t("ui.tab_da_buffs.stats_da.bono_dano_anomalia", default="Anomaly DMG Bonus"):       "Bono_Daño_Anomalia",
            _t("ui.tab_da_buffs.stats_da.dano_sheer_pct",     default="Sheer Force %"):           "Sheer_force",
            _t("ui.tab_da_buffs.stats_da.dano_abloom",        default="Abloom DMG"):              "Abloom_dmg",
            _t("ui.tab_da_buffs.stats_da.red_ignorar_def",    default="DEF Reduction / Ignore %"):"Reduccion_DEF_enemigo",
            _t("ui.tab_da_buffs.stats_da.red_res_elemental",  default="Elemental RES Reduction"): "Red_Resistencia_Global",
            _t("ui.tab_da_buffs.stats_da.red_resistencia",    default="RES Reduction"):           "Pen_Res_Global",
            _t("ui.tab_da_buffs.stats_da.dano_infligido_pct", default="DMG Dealt %"):             "DMG_Taken",
            _t("ui.tab_da_buffs.stats_da.res_anomalia",       default="Anomaly RES"):             "Resistencia_Anomalía_Enemigo",
        }

        ruta_imgs = os.path.join(self.app.ruta_recursos, "images", "buffs")
        if os.path.exists(ruta_imgs):
            self.da_lista_imagenes = [
                f"/images/buffs/{f}" for f in os.listdir(ruta_imgs)
                if f.lower().endswith(('.png', '.jpg', '.jpeg'))
            ]
        if not self.da_lista_imagenes:
            self.da_lista_imagenes = ["/images/default.png"]

        self.da_imagen_actual = self.da_lista_imagenes[0]

        # ── Carrusel de imágenes ──────────────────────────────────────
        img_carousel = ft.Image(
            src=self.da_imagen_actual, width=128, height=128,
            fit=ft.ImageFit.CONTAIN, border_radius=12,
        )

        lbl_carrusel_pos = ft.Text(
            f"1 / {len(self.da_lista_imagenes)}",
            size=11, color="secondary", text_align=ft.TextAlign.CENTER
        )

        def cambiar_imagen(delta):
            self.da_indice_imagen = (self.da_indice_imagen + delta) % len(self.da_lista_imagenes)
            self.da_imagen_actual = self.da_lista_imagenes[self.da_indice_imagen]
            img_carousel.src = self.da_imagen_actual
            lbl_carrusel_pos.value = f"{self.da_indice_imagen + 1} / {len(self.da_lista_imagenes)}"
            img_carousel.update()
            lbl_carrusel_pos.update()

        btn_prev_img = ft.IconButton(
            ft.Icons.ARROW_BACK_IOS, icon_size=16, icon_color="white54",
            on_click=lambda e: cambiar_imagen(-1)
        )
        btn_next_img = ft.IconButton(
            ft.Icons.ARROW_FORWARD_IOS, icon_size=16, icon_color="white54",
            on_click=lambda e: cambiar_imagen(1)
        )
        carrusel_ui = ft.Column([
            ft.Row(
                [btn_prev_img, img_carousel, btn_next_img],
                alignment=ft.MainAxisAlignment.CENTER
            ),
            lbl_carrusel_pos
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4)

        # ── Controles de entrada (intocables) ────────────────────────
        dd_stat_selector = ft.Dropdown(
            label=self.i18n.t("ui.tab_da_buffs.selecciona_stat"),
            options=[ft.dropdown.Option(k) for k in self.mapa_stats_da.keys()],
            width=250, dense=True, text_size=13, bgcolor="background"
        )
        txt_stat_value = ft.TextField(
            label=self.i18n.t("ui.tab_da_buffs.valor"),
            width=80, dense=True, text_size=13, value="0", bgcolor="background"
        )

        contenedor_texto_tarjeta = ft.Column(spacing=6)
        contenedor_lista_activos = ft.Column(spacing=5)
        self.lbl_da_resumen = ft.Text(
            self.i18n.t("ui.tab_da_buffs.sin_buffs_activos"),
            color="secondary", size=14, weight=ft.FontWeight.BOLD
        )

        # ── refrescar_interfaz_da (lógica intocable, solo fila activa mejorada) ──
        def refrescar_interfaz_da():
            self.da_active_buffs.clear()
            for k, v in self.da_custom_buffs.items():
                self.da_active_buffs[k] = self.da_active_buffs.get(k, 0.0) + v
            for k, v in self.da_enemy_buffs.items():
                self.da_active_buffs[k] = self.da_active_buffs.get(k, 0.0) + v

            contenedor_texto_tarjeta.controls.clear()
            contenedor_lista_activos.controls.clear()

            if not self.da_custom_buffs:
                contenedor_texto_tarjeta.controls.append(
                    ft.Text(self.i18n.t("ui.tab_da_buffs.sin_modificadores"),
                            color="secondary", italic=True)
                )
            else:
                for stat_ui, valor in self.da_custom_buffs.items():
                    color_stat = "primary"
                    if "Daño" in stat_ui:                             color_stat = "secondary"
                    if "Defensa" in stat_ui or "Resistencia" in stat_ui: color_stat = "error"

                    span_texto = ft.Text(spans=[
                        ft.TextSpan(self.i18n.t("ui.tab_da_buffs.buff_de"),       style=ft.TextStyle(size=14)),
                        ft.TextSpan(stat_ui,                                        style=ft.TextStyle(size=14, color=color_stat, weight=ft.FontWeight.BOLD)),
                        ft.TextSpan(self.i18n.t("ui.tab_da_buffs.incrementa_en"), style=ft.TextStyle(size=14)),
                        ft.TextSpan(f"{valor}",                                     style=ft.TextStyle(size=14, color="primary", weight=ft.FontWeight.BOLD)),
                        ft.TextSpan(".",                                             style=ft.TextStyle(size=14)),
                    ])
                    contenedor_texto_tarjeta.controls.append(span_texto)

                    # ── Fila activa con pill visual ───────────────────
                    fila_activa = ft.Container(
                        content=ft.Row([
                            ft.Container(
                                width=6, height=22, bgcolor=color_stat,
                                border_radius=3
                            ),
                            ft.Text(f"{stat_ui}: +{valor}", expand=True, size=13),
                            ft.IconButton(
                                ft.Icons.DELETE_OUTLINE, icon_color="error",
                                icon_size=16,
                                tooltip=self.i18n.t("ui.tab_da_buffs.tooltip_eliminar"),
                                on_click=lambda e, k=stat_ui: eliminar_buff(k)
                            )
                        ], spacing=8),
                        bgcolor="background",
                        padding=ft.padding.symmetric(horizontal=12, vertical=4),
                        border_radius=8,
                        border=ft.border.all(1, ft.Colors.with_opacity(0.2, color_stat)),
                    )
                    contenedor_lista_activos.controls.append(fila_activa)

            if not self.da_active_buffs:
                self.lbl_da_resumen.value = self.i18n.t("ui.tab_da_buffs.sin_buffs_activos")
                self.lbl_da_resumen.color = "outline"
            else:
                # Mapeo de claves internas a claves de traducción
                _mapa_trad = {
                    "Bono_Daño_Anomalia": "stats.bono_dano_anomalia",
                    "DMG_Taken": "stats.dmg_recibido",
                    "Bono_Acumulación": "stats.tasa_anomalia",
                    "Daño_Adicional": "stats.bono_dmg",
                    "Daño_elemental": "stats.dano_elemental",
                    "Daño_crítico": "stats.dano_crit",
                    "Aumento_Daño_Critico": "stats.aumento_crit_dmg",
                    "ATQ %": "stats.atq_pct",
                    "Ataque_%": "stats.atq_pct",
                    "Aturdimiento": "stats.aturdimiento",
                    "Buff_Defensa": "stats.buff_defensa",
                    "Daño Crítico %": "stats.dano_crit",
                    "Daño_Cadena_Ulti": "stats.dano_cadena_ulti",
                    "Daño_Etereo": "stats.dano_etereo",
                    "Daño_Hielo": "stats.dano_hielo",
                    "Daño_elemental__hielo_etereo": "stats.dano_hielo_etereo",
                    "Daño_elemental__fisico_electrico": "stats.dano_fisico_electrico",
                    "Multiplicador Aturdimiento": "stats.mult_aturdimiento",
                    "Multiplicador_Aturdimiento": "stats.mult_aturdimiento",
                    "Resistencia Anomalía": "stats.res_anomalia_enemigo",
                    "Resistencia_Anomalía_Enemigo": "stats.res_anomalia_enemigo",
                    "Abloom_dmg": "stats.dano_floracion",
                }
                textos_resumen = []
                for stat_ui, valor in self.da_active_buffs.items():
                    signo = "+" if valor > 0 else ""
                    nombre = self.i18n.t(_mapa_trad[stat_ui], default=stat_ui) if stat_ui in _mapa_trad else stat_ui
                    textos_resumen.append(f"{signo}{valor} {nombre}")
                self.lbl_da_resumen.value = " | ".join(textos_resumen)
                self.lbl_da_resumen.color = "primary"

            if contenedor_texto_tarjeta.page:
                contenedor_texto_tarjeta.update()
                contenedor_lista_activos.update()
                self.lbl_da_resumen.update()
                self.app.recalcular_stats_finales()

        self.refrescar_interfaz_da_local = refrescar_interfaz_da

        def agregar_buff(e):
            stat = dd_stat_selector.value
            try:
                valor = float(txt_stat_value.value.replace(",", "."))
                if stat and valor != 0:
                    self.da_custom_buffs[stat] = valor
                    txt_stat_value.value = "0"
                    txt_stat_value.update()
                    refrescar_interfaz_da()
            except ValueError:
                pass

        def eliminar_buff(stat_ui):
            if stat_ui in self.da_custom_buffs:
                del self.da_custom_buffs[stat_ui]
                refrescar_interfaz_da()

        btn_add = ft.Container(
            content=ft.ElevatedButton(
                self.i18n.t("ui.tab_da_buffs.anadir_efecto"),
                icon=ft.Icons.ADD, on_click=agregar_buff, color="primary"
            ),
            animate_scale=ft.Animation(250, ft.AnimationCurve.EASE_OUT),
        )
        def on_hover_btn_add(e):
            btn_add.scale = 1.05 if e.data == "true" else 1.0
            btn_add.update()
        btn_add.on_hover = on_hover_btn_add
        btn_clear = ft.TextButton(
            self.i18n.t("ui.tab_da_buffs.limpiar_todo"),
            icon=ft.Icons.DELETE_SWEEP, icon_color="error",
            on_click=lambda e: [self.da_custom_buffs.clear(), refrescar_interfaz_da()]
        )

        txt_nombre_guardar = ft.TextField(
            label=self.i18n.t("ui.tab_da_buffs.nombre_buff"),
            dense=True, expand=True, text_size=12
        )
        lista_guardados_ui = ft.Column(spacing=4, scroll=ft.ScrollMode.AUTO, height=250)

        def refrescar_lista_guardados():
            lista_guardados_ui.controls.clear()
            archivos = self.app.obtener_buffs_da_guardados()
            if not archivos:
                lista_guardados_ui.controls.append(
                    ft.Text(self.i18n.t("ui.tab_da_buffs.sin_buffs_guardados"),
                            italic=True, color="grey", size=self.FS['xs'])
                )
            for arch in archivos:
                nombre_arch = arch.replace(".json", "")
                datos_buff  = self.app.cargar_buff_da(nombre_arch)
                ruta_imagen = "images/default.png"
                if datos_buff and "imagen" in datos_buff:
                    ruta_imagen = datos_buff["imagen"]

                fila = ft.Container(
                    content=ft.Row([
                        ft.Image(src=ruta_imagen, width=32, height=32,
                                fit=ft.ImageFit.CONTAIN, border_radius=6),
                        ft.Text(nombre_arch, expand=True, size=13),
                        ft.IconButton(
                            ft.Icons.DOWNLOAD, icon_size=16,
                            tooltip=self.i18n.t("ui.tab_da_buffs.tooltip_cargar"),
                            on_click=lambda e, n=nombre_arch: aplicar_buff_guardado(n)
                        ),
                        ft.IconButton(
                            ft.Icons.DELETE, icon_color="error", icon_size=16,
                            tooltip=self.i18n.t("ui.tab_da_buffs.tooltip_borrar"),
                            on_click=lambda e, n=nombre_arch: borrar_buff_guardado(n)
                        )
                    ], spacing=4),
                    bgcolor="surface",
                    padding=ft.padding.symmetric(horizontal=8, vertical=6),
                    border_radius=8,
                    border=ft.border.all(1, ft.Colors.with_opacity(0.15, ft.Colors.WHITE)),
                )
                lista_guardados_ui.controls.append(fila)
            if lista_guardados_ui.page:
                lista_guardados_ui.update()

        def guardar_buff_actual(e):
            nombre = txt_nombre_guardar.value.strip()
            if nombre and self.da_custom_buffs:
                self.app.guardar_buff_da(nombre, self.da_custom_buffs, self.da_imagen_actual)
                txt_nombre_guardar.value = ""
                txt_nombre_guardar.update()
                refrescar_lista_guardados()
                mensaje = self.i18n.t("ui.tab_da_buffs.msg_guardado").replace("{nombre}", nombre)
                self.app.mostrar_mensaje(mensaje)
            else:
                self.app.mostrar_mensaje(self.i18n.t("ui.tab_da_buffs.msg_error_guardar"))

        def aplicar_buff_guardado(nombre):
            datos = self.app.cargar_buff_da(nombre)
            if datos:
                self.da_custom_buffs = datos.get("buffs", {}).copy()
                img_guardada = datos.get("imagen", "")
                if img_guardada in self.da_lista_imagenes:
                    self.da_indice_imagen = self.da_lista_imagenes.index(img_guardada)
                    self.da_imagen_actual = img_guardada
                    img_carousel.src = self.da_imagen_actual
                    img_carousel.update()
                refrescar_interfaz_da()
                mensaje = self.i18n.t("ui.tab_da_buffs.msg_cargado").replace("{nombre}", nombre)
                self.app.mostrar_mensaje(mensaje)

        def borrar_buff_guardado(nombre):
            self.app.eliminar_buff_da(nombre)
            refrescar_lista_guardados()
            mensaje = self.i18n.t("ui.tab_da_buffs.msg_borrado").replace("{nombre}", nombre)
            self.app.mostrar_mensaje(mensaje)

        btn_guardar_ui = ft.Container(
            content=ft.ElevatedButton(
                self.i18n.t("ui.tab_da_buffs.guardar"),
                icon=ft.Icons.SAVE, on_click=guardar_buff_actual, color="primary"
            ),
            animate_scale=ft.Animation(250, ft.AnimationCurve.EASE_OUT),
        )
        def on_hover_btn_guardar(e):
            btn_guardar_ui.scale = 1.05 if e.data == "true" else 1.0
            btn_guardar_ui.update()
        btn_guardar_ui.on_hover = on_hover_btn_guardar
        refrescar_lista_guardados()

        # ── Tarjeta de preview del buff ───────────────────────────────
        tarjeta_buff = ft.Container(
            expand=True,
            bgcolor="background",
            border_radius=12,
            border=ft.border.all(1, ft.Colors.with_opacity(0.35, ft.Colors.WHITE)),
            shadow=ft.BoxShadow(
                blur_radius=18, spread_radius=0,
                color=ft.Colors.BLACK38, offset=ft.Offset(0, 4)
            ),
            content=ft.Column([
                ft.Container(
                    content=ft.Column([
                        ft.Text(
                            self.i18n.t("ui.tab_da_buffs.titulo_tarjeta"),
                            size=18, weight=ft.FontWeight.BOLD
                        ),
                        carrusel_ui
                    ], alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    alignment=ft.alignment.center,
                    padding=ft.padding.all(14),
                    bgcolor="surface",
                    border_radius=ft.border_radius.only(top_left=14, top_right=14)
                ),
                ft.Container(
                    content=contenedor_texto_tarjeta,
                    padding=ft.padding.all(16)
                )
            ], spacing=0)
        )

        # ── Panel de descripción / añadir efectos ─────────────────────
        panel_descripcion = ft.Container(
            expand=True,
            padding=ft.padding.all(20),
            bgcolor="surface",
            border=ft.border.all(1, "outline"),
            border_radius=12,
            shadow=ft.BoxShadow(
                blur_radius=14, spread_radius=0,
                color=ft.Colors.BLACK26, offset=ft.Offset(0, 3)
            ),
            content=ft.Column([
                ft.Text(
                    self.i18n.t("ui.tab_da_buffs.titulo_panel"),
                    size=20, weight=ft.FontWeight.BOLD, color="primary"
                ),
                ft.Text(
                    self.i18n.t("ui.tab_da_buffs.desc_panel"),
                    color="secondary", size=13
                ),
                ft.Divider(height=16, color="outline"),
                ft.Row(
                    [dd_stat_selector, txt_stat_value, btn_add],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=8
                ),
                ft.Container(height=12),
                ft.Row([
                    ft.Text(
                        self.i18n.t("ui.tab_da_buffs.efectos_agregados"),
                        weight=ft.FontWeight.BOLD, color="secondary"
                    ),
                    btn_clear
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                contenedor_lista_activos
            ], alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.START,
            spacing=8)
        )

        # ── Panel de guardados ────────────────────────────────────────
        panel_guardados = ft.Container(
            width=285,
            padding=ft.padding.all(16),
            bgcolor="background",
            border=ft.border.all(1, "outline"),
            border_radius=12,
            shadow=ft.BoxShadow(
                blur_radius=14, spread_radius=0,
                color=ft.Colors.BLACK26, offset=ft.Offset(0, 3)
            ),
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.BOOKMARK, size=16, color="primary"),
                    ft.Text(
                        self.i18n.t("ui.tab_da_buffs.mis_buffs"),
                        size=16, weight=ft.FontWeight.BOLD
                    )
                ], spacing=6),
                ft.Row([txt_nombre_guardar, btn_guardar_ui], spacing=6),
                ft.Divider(height=10, color="outline"),
                lista_guardados_ui
            ], spacing=10)
        )

        top_layout = ft.Row(
            controls=[tarjeta_buff, panel_descripcion, panel_guardados],
            expand=True,
            vertical_alignment=ft.CrossAxisAlignment.START,
            spacing=16
        )

        # ── Panel resumen activo ──────────────────────────────────────
        panel_resumen = ft.Container(
            padding=ft.padding.all(14),
            bgcolor="surface",
            border_radius=12,
            border=ft.border.all(2, "primary"),
            shadow=ft.BoxShadow(
                blur_radius=16, spread_radius=0,
                color=ft.Colors.with_opacity(0.3, ft.Colors.PRIMARY),
                offset=ft.Offset(0, 3)
            ),
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.BOLT, size=15, color="primary"),
                    ft.Text(
                        self.i18n.t("ui.tab_da_buffs.valores_calculo"),
                        size=12, weight=ft.FontWeight.BOLD, color="primary"
                    )
                ], spacing=6),
                self.lbl_da_resumen
            ], spacing=6)
        )

        # ── Panel enemigo ─────────────────────────────────────────────
        self.da_img_enemigo_detalle = ft.Image(
            src="images/enemigos/default_enemy.png",
            width=165, height=228,
            fit=ft.ImageFit.CONTAIN, border_radius=8
        )
        self.da_txt_detalle_enemigo = ft.Text(size=14)
        self.da_opciones_enemigo_ui = ft.Column(spacing=6)

        marco_img_enemigo = ft.Container(
            content=self.da_img_enemigo_detalle,
            padding=8,
            border_radius=12,
            bgcolor="surface",
            border=ft.border.all(1, "outline"),
            shadow=ft.BoxShadow(blur_radius=10, spread_radius=0, color=ft.Colors.BLACK26),
            alignment=ft.alignment.center,
            animate_scale=ft.Animation(260, ft.AnimationCurve.EASE_OUT),
        )
        def on_hover_enemy_img(e):
            marco_img_enemigo.scale = 1.04 if e.data == "true" else 1.0
            marco_img_enemigo.update()
        marco_img_enemigo.on_hover = on_hover_enemy_img

        panel_enemigo_da = ft.Container(
            padding=ft.padding.all(20),
            bgcolor="surface",
            border_radius=12,
            border=ft.border.all(1, "outline"),
            shadow=ft.BoxShadow(
                blur_radius=14, spread_radius=0,
                color=ft.Colors.BLACK26, offset=ft.Offset(0, 3)
            ),
            margin=ft.margin.only(top=16),
            content=ft.Column([
                ft.Row([
                    marco_img_enemigo,
                    ft.Column([
                        ft.Row([
                            ft.Icon(ft.Icons.RADAR, size=18, color="secondary"),
                            ft.Text(
                                self.i18n.t("ui.tab_da_buffs.detalles_enemigo"),
                                size=18, weight="bold", color="secondary"
                            )
                        ], spacing=8),
                    ], expand=True),
                ], vertical_alignment=ft.CrossAxisAlignment.CENTER, spacing=12),
                ft.Container(
                    padding=ft.padding.all(14),
                    bgcolor="background",
                    border_radius=12,
                    border=ft.border.all(1, "outline"),
                    content=self.da_txt_detalle_enemigo
                ),
                ft.Container(height=6),
                ft.Text(
                    self.i18n.t("ui.tab_da_buffs.efectos_enemigo"),
                    size=self.FS['md'], weight="bold", color="primary"
                ),
                self.da_opciones_enemigo_ui
            ], spacing=8)
        )

        refrescar_interfaz_da()

        return ft.Container(
            padding=ft.padding.all(20),
            expand=True,
            content=ft.Column(
                [
                    top_layout,
                    ft.Container(height=12),
                    panel_resumen,
                    panel_enemigo_da
                ],
                scroll=ft.ScrollMode.AUTO,
                spacing=0
            )
        )

    def actualizar_panel_enemigo_da(self, nombre_enemigo, ruta_imagen, spans_descripcion, opciones_buffs):
        """
        Actualiza la sección inferior de la pestaña DA Buffs con la info del enemigo.
        """
        if not self.da_img_enemigo_detalle: return
        
        if not hasattr(self, 'da_enemy_buffs'): self.da_enemy_buffs = {}
        if not hasattr(self, 'da_custom_buffs'): self.da_custom_buffs = {}
        
        self.da_img_enemigo_detalle.src = ruta_imagen
        self.da_img_enemigo_detalle.update()
        self.da_txt_detalle_enemigo.spans = spans_descripcion
        self.da_txt_detalle_enemigo.update()
        self.da_opciones_enemigo_ui.controls.clear()
        
        self.da_enemy_buffs.clear()

        if not opciones_buffs:
            self.da_opciones_enemigo_ui.controls.append(ft.Text(self.i18n.t("ui.tab_da_buffs.enemigo_sin_modificadores"), color="grey", italic=True))
            self.da_opciones_enemigo_ui.update()
            self.actualizar_interfaz_da_forzado()
            return

        for opcion in opciones_buffs:
            tipo = opcion.get("tipo", "checkbox")
            efectos = opcion.get("efectos", {})
            label = opcion["label"]

            if tipo == "checkbox":
                def toggle_checkbox(e, ef=efectos):
                    for stat, valor in ef.items():
                        if e.control.value: self.da_enemy_buffs[stat] = valor
                        else: self.da_enemy_buffs.pop(stat, None)
                    self.actualizar_interfaz_da_forzado()
                    
                chk = ft.Checkbox(label=label, value=False, on_change=toggle_checkbox)
                self.da_opciones_enemigo_ui.controls.append(chk)

            elif tipo == "dropdown":
                max_stacks = opcion.get("max_stacks", 1)
                
                def toggle_dropdown(e, ef=efectos):
                    cargas = int(e.control.value)
                    for stat, valor_por_carga in ef.items():
                        if cargas > 0:
                            self.da_enemy_buffs[stat] = valor_por_carga * cargas
                        else:
                            self.da_enemy_buffs.pop(stat, None)
                    self.actualizar_interfaz_da_forzado()

                texto_cargas = self.i18n.t("ui.tab_da_buffs.cargas")
                texto_desactivado = self.i18n.t("ui.tab_da_buffs.desactivado")
                
                dd = ft.Dropdown(
                    label=label, value="0", width=350, dense=True, text_size=13,
                    options=[ft.dropdown.Option(str(i), text=f"{i} {texto_cargas}" if i>0 else texto_desactivado) for i in range(max_stacks + 1)],
                    on_change=toggle_dropdown
                )
                self.da_opciones_enemigo_ui.controls.append(dd)

        self.da_opciones_enemigo_ui.update()
        self.actualizar_interfaz_da_forzado()
        
    def actualizar_interfaz_da_forzado(self):
        """Pequeño helper para refrescar el resumen de DA desde fuera de su scope local"""
        if hasattr(self, 'refrescar_interfaz_da_local'):
            self.refrescar_interfaz_da_local()

    def create_comparator_tab(self):
        """Pestaña Comparador — VISUAL REFACTOR"""

        self.config_name_field = ft.TextField(
            label=self.i18n.t("ui.tab_comparador.nombre_build"),
            width=140, text_size=12, height=40, content_padding=10
        )

        btn_add_main = ft.ElevatedButton(
            self.i18n.t("ui.tab_comparador.anadir"),
            on_click=self.app.agregar_al_ranking,
            icon=ft.Icons.ADD, height=40
        )

        self.dd_tipo_dano_ranking = ft.Dropdown(
            label=self.i18n.t("ui.tab_comparador.clasificar_por"),
            options=[
                ft.dropdown.Option("maximo",   text=self.i18n.t("ui.tab_comparador.suma_danos")),
                ft.dropdown.Option("normal",   text=self.i18n.t("ui.tab_comparador.dano_normal")),
                ft.dropdown.Option("anomalia", text=self.i18n.t("ui.tab_comparador.dano_anomalia")),
                ft.dropdown.Option("sheer",    text=self.i18n.t("ui.tab_comparador.dano_sheer")),
                ft.dropdown.Option("calidad",  text=self.i18n.t("ui.tab_comparador.calidad_substats"))
            ],
            value="maximo", width=160, dense=True, text_size=12, content_padding=10,
            bgcolor="background",
            border_radius=ft.border_radius.only(bottom_left=8, bottom_right=8),
            border_color=ft.Colors.with_opacity(0.25, ft.Colors.WHITE),
            focused_border_color="primary",
            on_change=lambda e: self.renderizar_ranking_ui()
        )

        self.chk_agrupar_m = ft.Switch(
            label=self.i18n.t("ui.tab_comparador.evaluar_dupes"),
            value=False, scale=0.9,
            tooltip=self.i18n.t("ui.tab_comparador.tooltip_agrupar_dupes"),
            on_change=lambda e: self.renderizar_ranking_ui()
        )

        self.dd_filtro_m = ft.Dropdown(
            label=self.i18n.t("ui.tab_comparador.filtrar_dupes"),
            options=[ft.dropdown.Option("Todos", text=self.i18n.t("ui.tab_comparador.todos"))]
                    + [ft.dropdown.Option(f"M{i}") for i in range(7)],
            value="Todos", width=110, dense=True, text_size=12, content_padding=10,
            bgcolor="background",
            border_radius=ft.border_radius.only(bottom_left=8, bottom_right=8),
            border_color=ft.Colors.with_opacity(0.25, ft.Colors.WHITE),
            focused_border_color="primary",
            on_change=lambda e: self.renderizar_ranking_ui()
        )

        btn_reset        = ft.IconButton(icon=ft.Icons.DELETE_SWEEP,    icon_color="error",   tooltip=self.i18n.t("ui.tab_comparador.borrar_ranking"),  on_click=self.app.reiniciar_ranking)
        btn_save         = ft.IconButton(icon=ft.Icons.SAVE,             icon_color="primary", tooltip=self.i18n.t("ui.tab_comparador.guardar_json"),    on_click=self.app.guardar_config)
        btn_generar_poster = ft.Container(
            content=ft.ElevatedButton(
                self.i18n.t("ui.tab_comparador.poster_top5"),
                icon=ft.Icons.IMAGE, color="primary",
                on_click=self.generar_poster_ranking
            ),
            animate_scale=ft.Animation(250, ft.AnimationCurve.EASE_OUT),
        )
        def on_hover_btn_poster(e):
            btn_generar_poster.scale = 1.05 if e.data == "true" else 1.0
            btn_generar_poster.update()
        btn_generar_poster.on_hover = on_hover_btn_poster

        self.lista_ranking_controls = ft.Column(spacing=3)

        # ── Contenedor ranking con sombra y radio mejorado ────────────
        self.contenedor_ranking = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.LEADERBOARD, size=16, color="primary"),
                    ft.Text(self.i18n.t("ui.tab_comparador.promedio_dano"),
                            weight="bold", color="primary")
                ], spacing=6),
                ft.Container(
                    content=ft.Column([self.lista_ranking_controls], scroll=ft.ScrollMode.AUTO),
                    height=260,
                    padding=ft.padding.all(8),
                    border=ft.border.all(1, "outline"),
                    border_radius=12,
                    bgcolor="surface",
                    shadow=ft.BoxShadow(blur_radius=10, spread_radius=0,
                                        color=ft.Colors.BLACK26, offset=ft.Offset(0, 2))
                )
            ], spacing=8),
            padding=ft.padding.all(14),
            visible=False,
            border_radius=12,
            bgcolor="background",
            border=ft.border.all(1, ft.Colors.with_opacity(0.2, ft.Colors.WHITE)),
            shadow=ft.BoxShadow(blur_radius=14, spread_radius=0,
                                color=ft.Colors.BLACK26, offset=ft.Offset(0, 3))
        )

        row_top = ft.ResponsiveRow(
            controls=[
                ft.Container(
                    content=ft.Row(
                        [self.config_name_field, btn_save, btn_add_main],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=6
                    ),
                    col={"sm": 12, "lg": 4},
                    alignment=ft.alignment.center_left,
                ),
                ft.Container(
                    content=ft.Row(
                        [self.dd_tipo_dano_ranking, self.chk_agrupar_m, self.dd_filtro_m],
                        alignment=ft.MainAxisAlignment.CENTER,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=15
                    ),
                    col={"sm": 12, "lg": 5},
                    alignment=ft.alignment.center,
                ),
                ft.Container(
                    content=ft.Row(
                        [btn_generar_poster, btn_reset],
                        alignment=ft.MainAxisAlignment.END,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=6
                    ),
                    col={"sm": 12, "lg": 3},
                    alignment=ft.alignment.center_right,
                ),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        opciones_archivos = []

        # ── Panel izquierdo ───────────────────────────────────────────
        self.dropdown_left = ft.Dropdown(
            label=self.i18n.t("ui.tab_comparador.build_a"),
            options=opciones_archivos, width=180,
            text_size=12, content_padding=10, dense=True,
            bgcolor="background",
            border_radius=ft.border_radius.only(bottom_left=8, bottom_right=8),
            border_color=ft.Colors.with_opacity(0.25, ft.Colors.WHITE),
            focused_border_color="primary"
        )
        self.container_left_content = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True, controls=[
            ft.Column([ft.Icon(ft.Icons.UPLOAD_FILE, size=48, color="outline"), ft.Text("Carga una build para comparar", size=13, color="outline")], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        ])
        frame_left = ft.Container(
            content=self.container_left_content,
            height=500, expand=True,
            border=ft.border.all(1, "outline"),
            border_radius=12,
            padding=ft.padding.all(12),
            shadow=ft.BoxShadow(blur_radius=12, spread_radius=0,
                                color=ft.Colors.BLACK26, offset=ft.Offset(0, 3))
        )

        btn_load_l     = ft.IconButton(ft.Icons.FILE_OPEN,       icon_color="#74DFF1", tooltip=self.i18n.t("ui.tab_comparador.cargar_local"),    on_click=lambda e: self.app.cargar_comparacion(e, "left"))
        btn_uid_l      = ft.IconButton(ft.Icons.CLOUD_DOWNLOAD,  icon_color="secondary", tooltip=self.i18n.t("ui.tab_comparador.importar_uid"),  on_click=lambda e: self.app.abrir_dialogo_uid(e, "left"))
        btn_rank_l     = ft.IconButton(ft.Icons.ADD_CHART,        icon_color="#FFE34D", tooltip=self.i18n.t("ui.tab_comparador.anadir_ranking"),  on_click=lambda e: self.app.agregar_desde_panel(e, "left"))
        btn_to_main_l  = ft.IconButton(ft.Icons.EDIT_DOCUMENT,   icon_color="#EB5E8D", tooltip=self.i18n.t("ui.tab_comparador.editar_principal"),on_click=lambda e: self.app.transferir_datos(e, "left_to_main"))
        btn_from_main_l= ft.IconButton(ft.Icons.OUTPUT_ROUNDED,  icon_color="primary", tooltip=self.i18n.t("ui.tab_comparador.traer_principal"), on_click=lambda e: self.app.transferir_datos(e, "main_to_left"))
        btn_refresh_l  = ft.IconButton(ft.Icons.REFRESH,         icon_color="outline", icon_size=18, tooltip="Actualizar lista de builds guardadas", on_click=self.app.actualizar_lista_archivos)

        row_l = ft.Row(
            [self.dropdown_left, btn_refresh_l, btn_load_l, btn_uid_l,
            btn_rank_l, ft.VerticalDivider(width=5), btn_to_main_l, btn_from_main_l],
            alignment=ft.MainAxisAlignment.CENTER, spacing=0
        )

        # ── Panel derecho ─────────────────────────────────────────────
        self.dropdown_right = ft.Dropdown(
            label=self.i18n.t("ui.tab_comparador.build_b"),
            options=opciones_archivos, width=180,
            text_size=12, content_padding=10, dense=True,
            bgcolor="background",
            border_radius=ft.border_radius.only(bottom_left=8, bottom_right=8),
            border_color=ft.Colors.with_opacity(0.25, ft.Colors.WHITE),
            focused_border_color="primary"
        )
        self.container_right_content = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True, controls=[
            ft.Column([ft.Icon(ft.Icons.UPLOAD_FILE, size=48, color="outline"), ft.Text("Carga una build para comparar", size=13, color="outline")], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        ])
        frame_right = ft.Container(
            content=self.container_right_content,
            height=500, expand=True,
            border=ft.border.all(1, "outline"),
            border_radius=12,
            padding=ft.padding.all(12),
            shadow=ft.BoxShadow(blur_radius=12, spread_radius=0,
                                color=ft.Colors.BLACK26, offset=ft.Offset(0, 3))
        )

        btn_load_r     = ft.IconButton(ft.Icons.FILE_OPEN,       icon_color="#74DFF1", tooltip=self.i18n.t("ui.tab_comparador.cargar_local"),    on_click=lambda e: self.app.cargar_comparacion(e, "right"))
        btn_uid_r      = ft.IconButton(ft.Icons.CLOUD_DOWNLOAD,  icon_color="secondary", tooltip=self.i18n.t("ui.tab_comparador.importar_uid"),  on_click=lambda e: self.app.abrir_dialogo_uid(e, "right"))
        btn_rank_r     = ft.IconButton(ft.Icons.ADD_CHART,        icon_color="#FFE34D", tooltip=self.i18n.t("ui.tab_comparador.anadir_ranking"),  on_click=lambda e: self.app.agregar_desde_panel(e, "right"))
        btn_to_main_r  = ft.IconButton(ft.Icons.EDIT_DOCUMENT,   icon_color="#EB5E8D", tooltip=self.i18n.t("ui.tab_comparador.editar_principal"),on_click=lambda e: self.app.transferir_datos(e, "right_to_main"))
        btn_from_main_r= ft.IconButton(ft.Icons.OUTPUT_ROUNDED,  icon_color="primary", tooltip=self.i18n.t("ui.tab_comparador.traer_principal"), on_click=lambda e: self.app.transferir_datos(e, "main_to_right"))
        btn_refresh_r  = ft.IconButton(ft.Icons.REFRESH,         icon_color="outline", icon_size=18, tooltip="Actualizar lista de builds guardadas", on_click=self.app.actualizar_lista_archivos)

        row_r = ft.Row(
            [self.dropdown_right, btn_refresh_r, btn_load_r, btn_uid_r,
            btn_rank_r, ft.VerticalDivider(width=5), btn_to_main_r, btn_from_main_r],
            alignment=ft.MainAxisAlignment.CENTER, spacing=0
        )

        # ── Contenedor análisis con sombra ────────────────────────────
        self.contenedor_analisis = ft.Container(
            content=ft.Column(),
            padding=ft.padding.all(14),
            border_radius=12,
            bgcolor="surface",
            border=ft.border.all(1, ft.Colors.with_opacity(0.15, ft.Colors.WHITE)),
            shadow=ft.BoxShadow(blur_radius=16, spread_radius=0,
                                color=ft.Colors.BLACK26, offset=ft.Offset(0, 4)),
            margin=ft.margin.only(top=14)
        )

        return ft.Column([
            ft.Container(height=12),
            ft.Text(self.i18n.t("ui.tab_comparador.titulo_tab"),
                    size=22, weight="bold"),
            ft.Container(height=4),
            row_top,
            ft.Container(height=8),
            self.contenedor_ranking,
            ft.Divider(height=16),
            ft.ResponsiveRow([
                ft.Column([row_l, frame_left],
                        col={"md": 6, "sm": 12},
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        expand=True),
                ft.Column([row_r, frame_right],
                        col={"md": 6, "sm": 12},
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        expand=True),
            ], vertical_alignment=ft.CrossAxisAlignment.START, spacing=14, run_spacing=14),
            self.contenedor_analisis
        ], scroll=ft.ScrollMode.AUTO, horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=0)

    def renderizar_panel_comparacion(self, lado, datos):
        contenedor = self.container_left_content if lado == "left" else self.container_right_content
        contenedor.controls.clear()

        if not datos:
            contenedor.controls.append(ft.Text(self.i18n.t("ui.tab_comparador.error_datos", default="Error: Datos vacíos.")))
            contenedor.update()
            return

        MAPA_STATS_JSON = {
            "ATK": "Ataque", "atk": "Ataque", "Attack": "Ataque", "Percent ATK": "Ataque",
            "HP": "Puntos_Vida", "hp": "Puntos_Vida", "Hp": "Puntos_Vida", "Percent HP": "Puntos_Vida",
            "DEF": "Defensa", "def": "Defensa", "Def": "Defensa", "Percent DEF": "Defensa",
            "CRIT Rate": "Probabilidad_crítico", "crit_rate": "Probabilidad_crítico", "Crit Rate": "Probabilidad_crítico",
            "CRIT DMG": "Daño_crítico", "crit_dmg": "Daño_crítico", "Crit DMG": "Daño_crítico",
            "PEN Ratio": "Tasa_de_Perforación", "pen_ratio": "Tasa_de_Perforación", "Pen Ratio": "Tasa_de_Perforación",
            "PEN": "Perforación_Plana", "pen": "Perforación_Plana",
            "Anomaly Proficiency": "Maestría_Anomalía", "anomaly_proficiency": "Maestría_Anomalía",
            "Impact": "Impacto", "impact": "Impacto",
            "Energy Regen": "Recuperación_energía", "energy_regen": "Recuperación_energía",
            "Physical DMG Bonus": "Daño_elemental", "physical_dmg": "Daño_elemental",
            "Fire DMG Bonus": "Daño_elemental", "fire_dmg": "Daño_elemental",
            "Ice DMG Bonus": "Daño_elemental", "ice_dmg": "Daño_elemental",
            "Electric DMG Bonus": "Daño_elemental", "electric_dmg": "Daño_elemental",
            "Ether DMG Bonus": "Daño_elemental", "ether_dmg": "Daño_elemental",
            "Wind DMG Bonus": "Daño_elemental", "wind_dmg": "Daño_elemental",
            "elemental_damage": "Daño_elemental"
        }

        ABREVIATURAS_SLOTS = {
            "Probabilidad_crítico": self.i18n.t("stats.prob_crit", default="Crit Rate"),
            "Daño_crítico": self.i18n.t("stats.dano_crit", default="Crit Dmg"),
            "Maestría_Anomalía": self.i18n.t("stats.maestria_anomalia", default="Maestría"),
            "Tasa_de_Anomalía": self.i18n.t("stats.tasa_anomalia", default="Tasa Anom."),
            "Recuperación_energía": self.i18n.t("stats.rec_energia", default="Rec. Energía"),
            "Tasa_de_Perforación": self.i18n.t("stats.perforacion", default="Pen Ratio"),
            "Puntos_Vida": self.i18n.t("stats.puntos_vida", default="HP %"),
            "Ataque": self.i18n.t("stats.ataque", default="ATK %"),
            "Defensa": self.i18n.t("stats.defensa", default="DEF %"),
            "Impacto": self.i18n.t("stats.impacto", default="Impacto"),
            "Daño_elemental": self.i18n.t("stats.dano_elemental", default="DMG %"),
            "Ninguno": "---"
        }

        MAPA_SETS_ID_LOCAL = {
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

        es_externo = "character" in datos or "name" in datos or "uid" in datos
        stats_main = {}
        sets_texto = self.i18n.t("ui.tab_comparador.sin_sets", default="Sin sets activos")
        titulo_identificador = self.i18n.t("ui.tab_comparador.build_desconocida", default="Build Desconocida")
        main_stats_slots = {4: "Ninguno", 5: "Ninguno", 6: "Ninguno"}
        
        txt_ninguno = self.i18n.t("ui.comun.ninguno", default="Ninguno")
        txt_desconocido = self.i18n.t("ui.comun.desconocido", default="Desconocido")

        if es_externo:
            nombre_agente = datos.get("name") or datos.get("character", {}).get("name", txt_desconocido)
            nombre_arma = datos.get("weapon", {}).get("name", "Ninguno")
            refinamiento = datos.get("weapon", {}).get("refinement", 1)
            mindscape = datos.get("mindscape", 0)
            
            nickname = datos.get("nickname", "")
            if nickname: titulo_identificador = f"{nickname} ({nombre_agente})"
            else: titulo_identificador = f"{nombre_agente} ({self.i18n.t('ui.tab_comparador.importado', default='Importado')})"

            raw_stats = datos.get("stats", datos)
            
            for key_json, key_app in MAPA_STATS_JSON.items():
                if key_json in raw_stats:
                    raw_val = raw_stats[key_json]
                    
                    if stats_main.get(key_app, 0) > 0: continue

                    valor_limpio = 0.0
                    if isinstance(raw_val, dict):
                        valor_limpio = float(raw_val.get('value', 0))
                    else:
                        try:
                            str_val = str(raw_val).replace("%", "").replace(",", ".").strip()
                            valor_limpio = float(str_val)
                        except: valor_limpio = 0.0

                    if key_app == "Probabilidad_crítico" and valor_limpio > 150: valor_limpio /= 100.0
                    elif key_app == "Daño_crítico" and valor_limpio > 1000: valor_limpio /= 100.0
                    elif key_app == "Tasa_de_Perforación" and valor_limpio > 200: valor_limpio /= 100.0
                    elif key_app == "Daño_elemental" and valor_limpio > 200: valor_limpio /= 100.0
                    
                    stats_main[key_app] = valor_limpio

            discos = datos.get("discs", [])
            conteo_sets = {}
            for d in discos:
                if "slot" in d and "main_stat" in d:
                    try:
                        slot_num = int(d["slot"])
                        if slot_num in [4, 5, 6]:
                            n_raw = d["main_stat"].get("name", "Ninguno")
                            main_stats_slots[slot_num] = MAPA_STATS_JSON.get(n_raw, n_raw)
                    except: pass
                s_id = int(d.get("set_id", 0))
                brand = d.get("brand", MAPA_SETS_ID_LOCAL.get(s_id, "Desconocido"))
                if brand != "Desconocido": conteo_sets[brand] = conteo_sets.get(brand, 0) + 1
            
            sets_res = []
            for nombre, cant in conteo_sets.items():
                nombre_trans = self.i18n.t(f"sets.{nombre}", default=nombre)
                if cant >= 4: sets_res.append(f"4pc {nombre_trans}")
                elif cant >= 2: sets_res.append(f"2pc {nombre_trans}")
            if sets_res: sets_texto = "\n".join(sets_res)

        else:
            nombre_agente = datos.get("agente", "Ninguno")
            nombre_arma = datos.get("wengine", "Ninguno")
            refinamiento = datos.get("refinamiento", 1)
            mindscape = datos.get("mindscape", 0)
            stats_main = datos.get("stats_manuales", {}).copy()
            
            if "_meta_nombre" in datos: titulo_identificador = datos["_meta_nombre"]
            else: titulo_identificador = f"{nombre_agente} ({self.i18n.t('ui.tab_comparador.local', default='Local')})"

            s1 = datos.get("sets", {}).get("set1", "Ninguno")
            s2 = datos.get("sets", {}).get("set2", "Ninguno")
            sets_res = []
            if s1 != "Ninguno" and s1: 
                sets_res.append(f"4pc: {self.i18n.t(f'sets.{s1}', default=s1)}")
            if s2 != "Ninguno" and s2: 
                sets_res.append(f"2pc: {self.i18n.t(f'sets.{s2}', default=s2)}")
            if sets_res: sets_texto = "\n".join(sets_res)
            
            discos_dict = datos.get("discos", {})
            for k, v in discos_dict.items():
                try: 
                    k_int = int(k)
                    if k_int in [4, 5, 6]: main_stats_slots[k_int] = v 
                except: pass

        try:
            stats_main["Nombre_Agente"] = nombre_agente
            elem_calc = "fisico"
            if hasattr(self.app, '_detectar_elemento'):
                elem_calc = self.app._detectar_elemento(nombre_agente, datos)

            stats_calc = stats_main.copy()
            keys_check = ["Probabilidad_crítico", "Daño_crítico", "Tasa_de_Perforación", "Daño_elemental"]
            
            for k in keys_check:
                val = stats_calc.get(k, 0.0)
                try:
                    val_f = float(val)
                except:
                    val_f = 0.0
                    
                if 0 < val_f < 3.0: 
                    stats_calc[k] = val_f * 100.0
                else:
                    stats_calc[k] = val_f

            d_norm, d_sheer, d_anom, _, _, _, _ = self.app.calcular_dano_simulado(stats_calc, elem_calc)
            
            stats_main["_dano_total"] = d_norm + d_sheer + d_anom
            stats_main["_dano_normal"] = d_norm
            stats_main["_dano_anomalia"] = d_anom
        except Exception as e:
            print(f"Error calculando: {e}")
            stats_main["_dano_total"] = 0

        img_src_agente = f"/images/{nombre_agente}.png"
        img_src_arma = f"/images/wengine/{nombre_arma}.png"
        
        if not os.path.exists(os.path.join(self.app.ruta_recursos, img_src_agente.lstrip('/'))):
             img_src_agente = "/images/default.png"
        if not os.path.exists(os.path.join(self.app.ruta_recursos, img_src_arma.lstrip('/'))):
             img_src_arma = "/images/wengine/default_wengine.png"

        txt_mindscape = self.i18n.t("ui.comun.mindscape", default="Mindscape")
        txt_refinamiento = self.i18n.t("ui.comun.refinamiento", default="Refinamiento")
        arma_vis = txt_ninguno if nombre_arma == "Ninguno" else self.i18n.t(f"wengines.{nombre_arma}", default=nombre_arma)
        agente_vis = txt_ninguno if nombre_agente == "Ninguno" else nombre_agente

        img_a = ft.Image(src=img_src_agente, width=70, height=76, fit=ft.ImageFit.CONTAIN, border_radius=8)
        col_info_a = ft.Column([ft.Text(agente_vis, weight="bold", size=self.FS['lg']), ft.Text(f"{txt_mindscape}: {mindscape}", size=12, color="primary")], spacing=2)

        img_w = ft.Image(src=img_src_arma, width=60, height=60, fit=ft.ImageFit.CONTAIN, border_radius=8)
        col_info_w = ft.Column([
            ft.Text(arma_vis, weight="bold", size=13), 
            ft.Text(f"{txt_refinamiento}: {refinamiento}", size=12, color="secondary")
        ], spacing=2)

        header = ft.Container(content=ft.Column([ft.Row([img_a, col_info_a]), ft.Divider(height=5, color="outline"), ft.Row([img_w, col_info_w])]), padding=10, bgcolor="surface", border_radius=12, border=ft.border.all(1, "outline"))

        col_slots_info = ft.Column(spacing=2)
        numeros_romanos = {4: "IV", 5: " V ", 6: "VI"}
        
        for slot_num in [4, 5, 6]:
            stat_completa = main_stats_slots.get(slot_num, "Ninguno")
            stat_corta = ABREVIATURAS_SLOTS.get(stat_completa, stat_completa.replace("_", " "))
            if stat_completa == "Ninguno": stat_corta = "---"
            color_texto = "on_surface_variant" if stat_completa != "Ninguno" else "outline"
            
            item_slot = ft.Row([
                ft.Container(
                    content=ft.Text(numeros_romanos[slot_num], size=10, weight="bold", color="background"),
                    bgcolor="primary",
                    padding=2, border_radius=8, width=25, alignment=ft.alignment.center
                ),
                ft.Text(stat_corta, size=11, color=color_texto)
            ], spacing=5)
            col_slots_info.controls.append(item_slot)

        content_sets = ft.Row([
            ft.Column([
                ft.Text(self.i18n.t("ui.tab_comparador.bonos_set", default="Bonos de Set"), size=12, weight="bold", color="secondary"),
                ft.Text(sets_texto, size=13)
            ], expand=True),
            ft.Container(
                content=col_slots_info,
                padding=ft.padding.only(left=10),
                border=ft.border.only(left=ft.BorderSide(1, "outline"))
            )
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        card_sets = ft.Container(content=content_sets, padding=10, bgcolor="surface", border_radius=12, margin=ft.margin.only(top=5))

        elem_str = str(elem_calc).capitalize()
        if elem_calc == "fisico": 
            key_res_elem = "Resistencia_Físico"
            key_pen_res = "Pen_Res_Fisico"
        elif elem_calc == "electrico":
            key_res_elem = "Resistencia_Electrico"
            key_pen_res = "Pen_Res_Electrico"
        elif elem_calc == "etereo":
            key_res_elem = "Resistencia_Etereo"
            key_pen_res = "Pen_Res_Etereo"
        else:
            key_res_elem = f"Resistencia_{elem_str}"
            key_pen_res = f"Pen_Res_{elem_str}"

        if "_stats_reales_calculo" in datos:
            stats_calc_reales = datos["_stats_reales_calculo"]
            for k_env in ["Reduccion_DEF_enemigo", "Resistencia_porcentual", key_res_elem, key_pen_res, "Perforación_Plana"]:
                if k_env in stats_calc_reales:
                    stats_main[k_env] = stats_calc_reales.get(k_env, 0.0)

        grid_stats = ft.Column(spacing=2)
        keys_mostrar = [
            (self.i18n.t("stats.ataque", default="Ataque"), "Ataque"), 
            (self.i18n.t("stats.puntos_vida", default="HP"), "Puntos_Vida"), 
            (self.i18n.t("stats.prob_crit", default="Crit Rate"), "Probabilidad_crítico"),
            (self.i18n.t("stats.dano_crit", default="Crit Dmg"), "Daño_crítico"), 
            (self.i18n.t("stats.dano_elemental", default="Daño Elem."), "Daño_elemental"), 
            (self.i18n.t("stats.perforacion", default="Pen Ratio"), "Tasa_de_Perforación"), 
            (self.i18n.t("stats.perf_plana", default="Perf. Plana"), "Perforación_Plana"),
            (self.i18n.t("stats.maestria_anomalia", default="Maestría"), "Maestría_Anomalía"), 
            (self.i18n.t("stats.impacto", default="Impacto"), "Impacto"), 
            (self.i18n.t("stats.fuerza_absoluta", default="Sheer"), "Sheer_force"),
            (self.i18n.t("ui.tab_comparador.red_def", default="Red. DEF %"), "Reduccion_DEF_enemigo"), 
            (self.i18n.t("ui.tab_comparador.res_global", default="Res. Global %"), "Resistencia_porcentual"),
            (f"{self.i18n.t('ui.tab_comparador.res_abrev', default='Res.')} {elem_str[:4]} %", key_res_elem), 
            (self.i18n.t("ui.tab_comparador.pen_res", default="PEN RES %"), key_pen_res)
        ]
        
        filas = []
        for label, key in keys_mostrar:
            val = stats_main.get(key, 0)
            v_str = "0"
            try:
                v_float = float(val)
                es_pct = key in ["Probabilidad_crítico", "Daño_crítico", "Tasa_de_Perforación"]
                if es_pct and 0 < v_float < 2.0: v_float *= 100
                v_str = f"{v_float:.1f}%" if es_pct else f"{int(v_float)}"
            except: v_str = str(val)
            filas.append(ft.Row([ft.Text(label, size=12, color="grey", expand=True), ft.Text(v_str, size=12, weight="bold")]))
        
        if not filas: filas.append(ft.Text(self.i18n.t("ui.tab_comparador.sin_datos", default="Sin datos"), size=12))
        grid_stats.controls = filas

        card_stats = ft.Container(content=ft.Column([ft.Text(self.i18n.t("ui.tab_comparador.resumen_stats", default="Resumen Stats"), size=13, weight="bold", color="primary"), ft.Divider(height=5, color="outline"), grid_stats]), padding=10, bgcolor="surface", border_radius=12, margin=ft.margin.only(top=5))

        if lado == "left":
            self.cache_datos_left = stats_main.copy()
            self.cache_datos_left["_meta_nombre"] = titulo_identificador
            if "_stats_reales_calculo" in datos: self.cache_datos_left["_stats_reales_calculo"] = datos["_stats_reales_calculo"]
        else:
            self.cache_datos_right = stats_main.copy()
            self.cache_datos_right["_meta_nombre"] = titulo_identificador
            if "_stats_reales_calculo" in datos: self.cache_datos_right["_stats_reales_calculo"] = datos["_stats_reales_calculo"]

        try:
            self.generar_analisis_final()
        except Exception as e:
            print(f"Error generando análisis comparativo: {e}")

        contenedor.controls.extend([header, card_sets, card_stats])
        contenedor.update()
    
    def generar_poster_ranking(self, e):
        criterio = self.dd_tipo_dano_ranking.value if hasattr(self, 'dd_tipo_dano_ranking') else "maximo"
        agente_filtro = self.dd_filtro_m.value if hasattr(self, 'dd_filtro_m') else "Todos"
        
        ranking_crudo = getattr(self.app, 'ranking_builds', [])
        if not ranking_crudo: 
            self.app.mostrar_mensaje(self.i18n.t("ui_dinamico.poster_sin_builds", default="No hay builds en el ranking para generar póster."))
            return
            
        ranking_filtrado = []
        for item in ranking_crudo:
            if agente_filtro == "Todos" or item.get('agente') == agente_filtro:
                ranking_filtrado.append(item)
                
        for item in ranking_filtrado:
            danos = item.get("danos", {})
            item["score_valor"] = danos.get(criterio, item.get("score", 0))
            
        ranking_filtrado.sort(key=lambda x: float(x.get("score_valor", 0)), reverse=True)
        top_5 = ranking_filtrado[:5] 
        
        if not top_5:
            self.app.mostrar_mensaje(self.i18n.t("ui_dinamico.poster_sin_datos", default="No hay suficientes datos para el filtro seleccionado."))
            return
        
        self.app.mostrar_mensaje(self.i18n.t("ui_dinamico.poster_generando", default="Generando póster del TOP 5... Por favor espera."))

        def thread_leaderboard():
            import os
            import base64
            import httpx
            from generador_imagenes import GeneradorTarjetas
            
            try:
                agente_bg = agente_filtro if agente_filtro != "Todos" else top_5[0].get('agente', 'Desconocido')
                
                if criterio == "calidad":
                    nombre_archivo = f"Leaderboard_TOP5_Calidad_{agente_bg.replace(' ', '_')}.png"
                else:
                    nombre_archivo = f"Leaderboard_TOP5_{agente_bg.replace(' ', '_')}.png"

                generador = GeneradorTarjetas(os.getcwd())
                
                buffer = generador.generar_ranking_card(top_5, agente_bg, ruta_salida=None, criterio=criterio)
                
                if buffer:
                    imagen_bytes = buffer.getvalue()
                    imagen_base64 = base64.b64encode(imagen_bytes).decode('utf-8')
                    
                    imagen_preview = ft.Image(
                        src_base64=imagen_base64,
                        fit=ft.ImageFit.CONTAIN,
                        height=450
                    )

                    def cerrar_dialogo(e):
                        self.app.page.close(dialogo)

                    def click_descargar(e, _nombre=nombre_archivo, _bytes=imagen_bytes):
                        try:
                            resp = httpx.post(f"{self.app.api_base_url}/download/prepare", files={"file": (_nombre, _bytes, "image/png")}, timeout=10)
                            if resp.status_code != 200:
                                self.app.mostrar_mensaje(f"❌ Error API: {resp.status_code}")
                                return
                            dl_id = resp.json()["id"]
                            self.app.page.launch_url(f"{self.app.api_base_url}/download/{dl_id}", web_window_name="_blank")
                        except Exception as ex:
                            self.app.mostrar_mensaje(f"❌ Error al preparar descarga: {ex}")

                    dialogo = ft.AlertDialog(
                        title=ft.Text(f"Leaderboard TOP 5 - {agente_bg}"),
                        content=imagen_preview,
                        actions=[
                            ft.ElevatedButton(
                                text="Descargar",
                                icon=ft.Icons.DOWNLOAD,
                                bgcolor=ft.Colors.BLUE_700,
                                color=ft.Colors.WHITE,
                                on_click=click_descargar
                            ),
                            ft.TextButton("Cerrar", on_click=cerrar_dialogo)
                        ],
                        actions_alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    )

                    self.app.page.open(dialogo)
                    self.app.mostrar_mensaje(self.i18n.t("ui_dinamico.poster_generado", default="¡Leaderboard generado!"))
                else:
                    self.app.mostrar_mensaje(self.i18n.t("ui_dinamico.poster_error_imagen", default="Error: La imagen no se pudo generar."))
                
            except Exception as ex:
                import traceback
                traceback.print_exc()
                self.app.mostrar_mensaje(f"Error crítico al generar: {ex}")

        import threading
        threading.Thread(target=thread_leaderboard).start()

    def renderizar_ranking_ui(self):
        """Renderiza la tabla del ranking — VISUAL REFACTOR (solo filas y cabecera)"""
        self.lista_ranking_controls.controls.clear()
        ranking_crudo = self.app.ranking_builds

        if not ranking_crudo:
            self.contenedor_ranking.visible = False
            self.contenedor_ranking.update()
            return

        self.contenedor_ranking.visible = True

        filtro       = getattr(self, 'dd_filtro_m', None)
        val_filtro   = filtro.value if filtro else "Todos"
        agrupar      = getattr(self, 'chk_agrupar_m', None)
        val_agrupar  = agrupar.value if agrupar else False
        tipo_dano_ctrl = getattr(self, 'dd_tipo_dano_ranking', None)
        criterio     = tipo_dano_ctrl.value if tipo_dano_ctrl else "maximo"

        ranking_filtrado = []
        for idx, item in enumerate(ranking_crudo):
            datos = item.get("datos", {})
            if "wengine" in datos:   m_level = int(datos.get("mindscape", 0))
            elif "weapon" in datos:  m_level = int(datos.get("mindscape", 0))
            else:                    m_level = 0
            item["_m_level"]      = m_level
            item["_original_idx"] = idx
            danos_dict = item.get("danos", {})
            if danos_dict:
                item["dano_raw"] = danos_dict.get(criterio, 0)
                item["score"]    = int(item["dano_raw"])
            if val_filtro == "Todos" or val_filtro == f"M{m_level}":
                ranking_filtrado.append(item)

        if not ranking_filtrado:
            self.lista_ranking_controls.controls.append(
                ft.Text(self.i18n.t("ui.tab_comparador.no_builds",
                                    default="No hay builds que cumplan el filtro."),
                        color="grey", italic=True)
            )
            self.lista_ranking_controls.update()
            self.contenedor_ranking.update()
            return

        grupos = {}
        if val_agrupar:
            for item in ranking_filtrado:
                m = item["_m_level"]
                if m not in grupos: grupos[m] = []
                grupos[m].append(item)
        else:
            grupos["Global"] = ranking_filtrado

        titulos_dano = {
            "maximo":   self.i18n.t("recom.score_potencial"),
            "normal":   self.i18n.t("recom.score_normal"),
            "anomalia": self.i18n.t("recom.score_anomalia"),
            "sheer":    self.i18n.t("recom.score_sheer"),
            "calidad":  self.i18n.t("ui.tab_recomendaciones_visual.evaluacion_substats")
        }
        titulo_columna = titulos_dano.get(criterio, "Score")

        # ── Cabecera mejorada ─────────────────────────────────────────
        self.lista_ranking_controls.controls.append(
            ft.Container(
                content=ft.Row([
                    ft.Text("RK",           width=35,  weight="bold", color="primary", size=11),
                    ft.Text(self.i18n.t("ui.tab_comparador.jugador_build", default="Jugador/Build (✎)"), width=110, weight="bold", color="primary", size=11),
                    ft.Text(self.i18n.t("ui.tab_comparador.agente",  default="Agente"),  width=110, weight="bold", color="primary", size=11),
                    ft.Text(self.i18n.t("ui.tab_comparador.team",    default="Team"),    width=110, weight="bold", color="primary", size=11),
                    ft.Text(self.i18n.t("ui.tab_comparador.enemigo", default="Enemigo"), width=90,  weight="bold", color="primary", size=11),
                    ft.Text(titulo_columna, expand=True, weight="bold", color="primary", size=11),
                    ft.Text(self.i18n.t("ui.tab_comparador.acciones", default="Acciones"), width=110, weight="bold", color="primary", text_align=ft.TextAlign.CENTER, size=11),
                ]),
                padding=ft.padding.symmetric(horizontal=6, vertical=4),
                bgcolor=ft.Colors.with_opacity(0.08, ft.Colors.PRIMARY),
                border_radius=ft.border_radius.only(top_left=8, top_right=8),
            )
        )
        self.lista_ranking_controls.controls.append(
            ft.Divider(height=1, color="outline")
        )

        llaves_ordenadas = sorted(grupos.keys()) if val_agrupar else ["Global"]
        txt_ninguno    = self.i18n.t("ui.comun.ninguno",    default="Ninguno")
        txt_desconocido = self.i18n.t("ui.comun.desconocido", default="Desconocido")
        def _tr_substat_ranking(clave):
            return self.i18n.t(
                f"substats.{clave}",
                default=str(clave).replace("_porcentual", " %").replace("_plano", "").replace("_", " "),
            )

        for llave in llaves_ordenadas:
            items_grupo = grupos[llave]
            items_grupo.sort(key=lambda x: x.get("dano_raw", 0), reverse=True)
            max_dano_grupo = items_grupo[0].get("dano_raw", 1) or 1

            if val_agrupar:
                color_cat = "primary"
                if llave >= 6:   color_cat = ft.Colors.AMBER_400
                elif llave >= 3: color_cat = ft.Colors.PURPLE_400
                self.lista_ranking_controls.controls.append(
                    ft.Container(
                        content=ft.Text(
                            self.i18n.t("ui.tab_comparador.agrupacion_dupes",
                                        default=f"Agrupación por dupes: M{llave}", llave=llave),
                            weight="bold", color=color_cat, size=12
                        ),
                        bgcolor=ft.Colors.with_opacity(0.12, color_cat),
                        padding=ft.padding.symmetric(horizontal=8, vertical=5),
                        border_radius=8,
                        margin=ft.margin.only(top=10, bottom=5)
                    )
                )

            for i, item in enumerate(items_grupo):
                idx_real           = item["_original_idx"]
                txt_nombre         = str(item.get("nombre_build", "---"))
                nombre_agente_real = str(item.get("agente", txt_desconocido))
                datos              = item.get("datos", {})
                arma, ref          = "Ninguno", 1
                mindscape          = item["_m_level"]

                if "wengine" in datos:
                    arma = datos.get("wengine", "Ninguno")
                    ref  = datos.get("refinamiento", 1)
                elif "weapon" in datos:
                    arma = datos.get("weapon", {}).get("name", "Ninguno")
                    ref  = datos.get("weapon", {}).get("refinement", 1)

                arma_vis   = txt_ninguno if arma == "Ninguno" else self.i18n.t(f"wengines.{arma}", default=arma)
                agente_vis = txt_ninguno if nombre_agente_real == "Ninguno" else nombre_agente_real
                score      = item.get("dano_raw", 0)

                # ── Colores por posición ──────────────────────────────
                color_barra = ft.Colors.BLUE_GREY_400
                if i == 0:   color_barra = ft.Colors.AMBER
                elif i == 1: color_barra = ft.Colors.CYAN_200
                elif i == 2: color_barra = ft.Colors.ORANGE_300
                if criterio == "calidad" and score >= 80:
                    color_barra = ft.Colors.GREEN_400

                if mindscape >= 6:   color_m = ft.Colors.AMBER_400
                elif mindscape >= 3: color_m = ft.Colors.PURPLE_400
                else:                color_m = "primary"

                if criterio == "calidad":
                    pct                  = score / 100.0
                    texto_score_principal = f"{score:.1f}%"
                    prioridad_dyn = (datos.get("_calidad_substats", {}) or {}).get("prioridad_dinamica", [])
                    texto_secundario     = ""
                    if prioridad_dyn:
                        texto_secundario = f"→ {_tr_substat_ranking(prioridad_dyn[0].get('substat', ''))}"
                else:
                    pct                  = score / max_dano_grupo if max_dano_grupo > 0 else 0
                    texto_score_principal = f"{score:,.0f}"
                    texto_secundario     = f"{int(pct*100)}%"

                btn_edit = ft.IconButton(
                    icon=ft.Icons.EDIT, icon_size=14, icon_color="outline",
                    tooltip=self.i18n.t("ui_dinamico.tooltip_renombrar", default="Renombrar"),
                    on_click=lambda e, r=idx_real, nom=txt_nombre: self.app.abrir_dialogo_renombrar(r, nom)
                )

                bloque_build = ft.Row([
                    ft.Text(txt_nombre, width=80, overflow=ft.TextOverflow.ELLIPSIS, weight="bold", size=12),
                    btn_edit
                ], spacing=0, width=110)

                bloque_agente = ft.Column([
                    ft.Text(agente_vis, width=110, overflow=ft.TextOverflow.ELLIPSIS, weight="bold", size=12, color=ft.Colors.WHITE),
                    ft.Text(f"M{mindscape}", size=11, color=color_m, weight="bold"),
                    ft.Text(f"R{ref} | {arma_vis}", width=110, overflow=ft.TextOverflow.ELLIPSIS, size=10, color="secondary")
                ], spacing=0, width=110)

                equipo_data   = datos.get("equipo", [])
                team_controls = []
                if equipo_data:
                    for sup in equipo_data:
                        ag_name = sup.get("agente", txt_desconocido[:4])
                        m_val   = sup.get("mindscape", "0")
                        r_val   = sup.get("refinamiento", "1")
                        w_val   = sup.get("wengine", "Ninguno")
                        w_val_vis = txt_ninguno if w_val == "Ninguno" else self.i18n.t(f"wengines.{w_val}", default=w_val)
                        team_controls.append(ft.Column([
                            ft.Text(f"{ag_name} M{m_val}R{r_val}", size=10, color="primary", weight="bold", overflow=ft.TextOverflow.ELLIPSIS, width=110),
                            ft.Text(f"└ {w_val_vis}", size=9, color="grey", overflow=ft.TextOverflow.ELLIPSIS, width=110)
                        ], spacing=0))
                else:
                    team_controls.append(
                        ft.Text(self.i18n.t("ui.tab_comparador.solo", default="Solo"), size=10, color="grey")
                    )

                bloque_team = ft.Column(team_controls, spacing=4, width=110, alignment=ft.MainAxisAlignment.CENTER)

                enemigo_nombre     = datos.get("_stats_reales_calculo", {}).get("Nombre_Enemigo", "Ninguno")
                enemigo_nombre_vis = txt_ninguno if enemigo_nombre == "Ninguno" else self.i18n.t(f"enemigos.{enemigo_nombre}", default=enemigo_nombre)
                defensa_enemigo    = int(datos.get("_stats_reales_calculo", {}).get("Defensa_Base", 950))

                bloque_enemigo = ft.Column([
                    ft.Text(enemigo_nombre_vis, width=90, overflow=ft.TextOverflow.ELLIPSIS, weight="bold", size=11, color="error"),
                    ft.Text(f"Def: {defensa_enemigo}", size=10, color="grey")
                ], spacing=0, width=90)

                columna_score = ft.Column([
                    ft.Row([
                        ft.Text(texto_score_principal, size=11, weight="bold", color="white"),
                        ft.Text(texto_secundario, size=11, color=color_barra)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.ProgressBar(value=pct, color=color_barra, bgcolor="black", height=5, border_radius=3)
                ], spacing=2, expand=True)

                btn_to_a = ft.IconButton(ft.Icons.ARROW_BACK,    tooltip=self.i18n.t("ui_dinamico.tooltip_cargar_a", default="Cargar en A"), icon_size=16, on_click=lambda e, x=idx_real: self.app.cargar_desde_ranking(x, "left"))
                btn_to_b = ft.IconButton(ft.Icons.ARROW_FORWARD, tooltip=self.i18n.t("ui_dinamico.tooltip_cargar_b", default="Cargar en B"), icon_size=16, on_click=lambda e, x=idx_real: self.app.cargar_desde_ranking(x, "right"))
                btn_del  = ft.IconButton(ft.Icons.DELETE_OUTLINE, tooltip=self.i18n.t("ui_dinamico.tooltip_eliminar_rank", default="Eliminar"), icon_size=16, icon_color="error", on_click=lambda e, x=idx_real: self.app.eliminar_del_ranking(x))

                # ── Fila con hover sutil ──────────────────────────────
                fila = ft.Container(
                    content=ft.Row([
                        ft.Text(f"#{i+1}", width=35, weight="bold", size=14, color=color_barra),
                        bloque_build,
                        bloque_agente,
                        bloque_team,
                        bloque_enemigo,
                        columna_score,
                        ft.Container(
                            content=ft.Row([btn_to_a, btn_to_b, btn_del],
                                        spacing=0, alignment=ft.MainAxisAlignment.END),
                            width=110, padding=ft.padding.only(right=5)
                        )
                    ]),
                    bgcolor=ft.Colors.with_opacity(0.07, color_barra) if i < 3 else "surface",
                    padding=ft.padding.symmetric(horizontal=6, vertical=6),
                    border_radius=8,
                    margin=ft.margin.only(bottom=3),
                    border=ft.border.all(1, ft.Colors.with_opacity(
                        0.18 if i < 3 else 0.06, color_barra
                    )),
                )
                self.lista_ranking_controls.controls.append(fila)

        self.lista_ranking_controls.update()
        self.contenedor_ranking.update()
        
    def generar_analisis_final(self):
        """Genera el bloque comparativo con Gráfico de Radar y polígonos interactivos"""
        try:
            self.contenedor_analisis.content.controls.clear()
            
            if not self.cache_datos_left or not self.cache_datos_right:
                self.contenedor_analisis.update()
                return

            stats_a = self.cache_datos_left
            stats_b = self.cache_datos_right
            
            nombre_a = stats_a.get("_meta_nombre", "Build A")
            nombre_b = stats_b.get("_meta_nombre", "Build B")

            agente_a = stats_a.get("Nombre_Agente", "Desconocido")
            agente_b = stats_b.get("Nombre_Agente", "Desconocido")

            rol_a = "Atacante"
            rol_b = "Atacante"
            
            if hasattr(self.app, 'agentes_data') and self.app.agentes_data:
                d_a = next((a for a in self.app.agentes_data if a['Nombre'] == agente_a), None)
                if d_a: rol_a = d_a.get("Tipo", "Atacante")
                d_b = next((a for a in self.app.agentes_data if a['Nombre'] == agente_b), None)
                if d_b: rol_b = d_b.get("Tipo", "Atacante")

            es_ruptura_a = (rol_a == "Ruptura")
            es_ruptura_b = (rol_b == "Ruptura")

            keys_comparar = [
                ("Ataque", self.i18n.t("stats.ataque", default="Ataque"), False),
                ("Puntos_Vida", self.i18n.t("stats.puntos_vida", default="HP"), False),
                ("Probabilidad_crítico", self.i18n.t("stats.prob_crit", default="Crit Rate"), True),
                ("Daño_crítico", self.i18n.t("stats.dano_crit", default="Crit Dmg"), True),
                ("Daño_elemental", self.i18n.t("stats.dano_elemental", default="Daño Elem."), True), 
            ]

            if es_ruptura_a and es_ruptura_b:
                keys_comparar.append(("Sheer_force", self.i18n.t("stats.fuerza_absoluta", default="Sheer Force"), False))
            elif es_ruptura_a or es_ruptura_b:
                keys_comparar.append(("Tasa_de_Perforación", self.i18n.t("stats.perforacion", default="Pen Ratio"), True))
                keys_comparar.append(("Sheer_force", self.i18n.t("stats.fuerza_absoluta", default="Sheer Force"), False))
            else:
                keys_comparar.append(("Tasa_de_Perforación", self.i18n.t("stats.perforacion", default="Pen Ratio"), True))

            keys_comparar.extend([
                ("Maestría_Anomalía", self.i18n.t("stats.maestria_anomalia", default="Maestría"), False),
                ("Impacto", self.i18n.t("stats.impacto", default="Impacto"), False)
            ])

            lista_ventajas_a = []
            lista_ventajas_b = []

            def limpiar_valor(v):
                if isinstance(v, (int, float)): return float(v)
                if isinstance(v, str):
                    v = v.replace("%", "").replace(",", "").strip()
                    try: return float(v)
                    except: return 0.0
                return 0.0

            puntos_a = 0
            puntos_b = 0
            
            valores_radar_a = []
            valores_radar_b = []
            tooltips_a = []
            tooltips_b = []

            for key, label, es_pct in keys_comparar:
                val_a = limpiar_valor(stats_a.get(key, 0))
                val_b = limpiar_valor(stats_b.get(key, 0))

                if es_pct:
                    if 0 < val_a < 2.0: val_a *= 100
                    if 0 < val_b < 2.0: val_b *= 100

                if val_b > 0: diff = ((val_a - val_b) / val_b) * 100
                else: diff = 100 if val_a > 0 else 0
                
                str_val_a = f"{val_a:.1f}%" if es_pct else f"{int(val_a)}"
                str_val_b = f"{val_b:.1f}%" if es_pct else f"{int(val_b)}"
                tooltips_a.append(f"{label}: {str_val_a}")
                tooltips_b.append(f"{label}: {str_val_b}")

                if diff > 1.0:
                    puntos_a += 1
                    texto = f"{label}: {str_val_a} vs {str_val_b}"
                    if diff > 10: texto += f" (+{diff:.0f}%)"
                    lista_ventajas_a.append(ft.Row([ft.Icon(ft.Icons.CHECK, color="primary", size=12), ft.Text(texto, size=12)]))
                elif diff < -1.0:
                    puntos_b += 1
                    texto = f"{label}: {str_val_b} vs {str_val_a}"
                    if abs(diff) > 10: texto += f" (+{abs(diff):.0f}%)"
                    lista_ventajas_b.append(ft.Row([ft.Icon(ft.Icons.CHECK, color="secondary", size=12), ft.Text(texto, size=12)]))

                if key in ["Probabilidad_crítico", "Tasa_de_Perforación"]:
                    max_val = 100.0 
                else:
                    max_val = max(val_a, val_b) * 1.10 
                    if max_val == 0: 
                        max_val = 1.0
                
                valores_radar_a.append(min(val_a / max_val, 1.0))
                valores_radar_b.append(min(val_b / max_val, 1.0))

            header_comparativa = ft.Container(
                content=ft.Column([
                    ft.Text(self.i18n.t("ui.tab_comparador.analisis_stats"), size=20, weight="bold"),
                    ft.Row([
                        ft.Text(nombre_a, size=14, color="primary", weight="bold"),
                        ft.Text(self.i18n.t("ui.tab_comparador.vs"), size=self.FS['xs'], italic=True, color="secondary"),
                        ft.Text(nombre_b, size=14, color="secondary", weight="bold"),
                    ], alignment=ft.MainAxisAlignment.CENTER)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=10
            )

            import flet.canvas as cv 
            
            canvas_size = 320
            center = canvas_size / 2
            radio_max = 110
            radio_min = 15
            radio_disp = radio_max - radio_min
            num_ejes = len(keys_comparar)
            
            shapes_radar = []
            
            for r_step in [0.25, 0.5, 0.75, 1.0]:
                r = radio_min + (radio_disp * r_step)
                path_anillo = cv.Path(paint=ft.Paint(style=ft.PaintingStyle.STROKE, color=ft.Colors.WHITE12))
                for i in range(num_ejes):
                    ang = (math.pi * 2 * i / num_ejes) - (math.pi / 2)
                    x = center + r * math.cos(ang)
                    y = center + r * math.sin(ang)
                    if i == 0: path_anillo.elements.append(cv.Path.MoveTo(x, y))
                    else: path_anillo.elements.append(cv.Path.LineTo(x, y))
                path_anillo.elements.append(cv.Path.Close())
                shapes_radar.append(path_anillo)
                
            for i in range(num_ejes):
                ang = (math.pi * 2 * i / num_ejes) - (math.pi / 2)
                x_edge = center + radio_max * math.cos(ang)
                y_edge = center + radio_max * math.sin(ang)
                
                x_start = center + radio_min * math.cos(ang)
                y_start = center + radio_min * math.sin(ang)
                
                shapes_radar.append(cv.Path(
                    elements=[cv.Path.MoveTo(x_start, y_start), cv.Path.LineTo(x_edge, y_edge)],
                    paint=ft.Paint(style=ft.PaintingStyle.STROKE, color="outline")
                ))
                x_text = center + (radio_max + 25) * math.cos(ang)
                y_text = center + (radio_max + 15) * math.sin(ang)
                shapes_radar.append(cv.Text(
                    x_text, y_text, text=keys_comparar[i][1], 
                    style=ft.TextStyle(size=10, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                    alignment=ft.alignment.center
                ))

            puntos_a_xy = []
            puntos_b_xy = []
            for i in range(num_ejes):
                ang = (math.pi * 2 * i / num_ejes) - (math.pi / 2)
                
                r_a = radio_min + (radio_disp * valores_radar_a[i])
                puntos_a_xy.append((center + r_a * math.cos(ang), center + r_a * math.sin(ang)))
                
                r_b = radio_min + (radio_disp * valores_radar_b[i])
                puntos_b_xy.append((center + r_b * math.cos(ang), center + r_b * math.sin(ang)))

            elementos_path_a = [cv.Path.MoveTo(puntos_a_xy[0][0], puntos_a_xy[0][1])] + [cv.Path.LineTo(x, y) for x, y in puntos_a_xy[1:]] + [cv.Path.Close()]
            path_a_fill = cv.Path(elements=elementos_path_a, paint=ft.Paint(color=ft.Colors.with_opacity(0.4, "primary"), style=ft.PaintingStyle.FILL))
            path_a_stroke = cv.Path(elements=elementos_path_a, paint=ft.Paint(color="primary", stroke_width=2, style=ft.PaintingStyle.STROKE))
            
            elementos_path_b = [cv.Path.MoveTo(puntos_b_xy[0][0], puntos_b_xy[0][1])] + [cv.Path.LineTo(x, y) for x, y in puntos_b_xy[1:]] + [cv.Path.Close()]
            path_b_fill = cv.Path(elements=elementos_path_b, paint=ft.Paint(color=ft.Colors.with_opacity(0.4, "secondary"), style=ft.PaintingStyle.FILL))
            path_b_stroke = cv.Path(elements=elementos_path_b, paint=ft.Paint(color="secondary", stroke_width=2, style=ft.PaintingStyle.STROKE))

            shapes_radar.extend([path_a_fill, path_b_fill, path_a_stroke, path_b_stroke])

            dots_a = [cv.Circle(x, y, 3, ft.Paint(color="primary")) for x, y in puntos_a_xy]
            dots_b = [cv.Circle(x, y, 3, ft.Paint(color="secondary")) for x, y in puntos_b_xy]
            shapes_radar.extend(dots_a + dots_b)

            canvas_radar = cv.Canvas(shapes=shapes_radar, width=canvas_size, height=canvas_size)
            zonas_interactivas = []
            for i in range(num_ejes):
                x_a, y_a = puntos_a_xy[i]
                x_b, y_b = puntos_b_xy[i]
                
                zonas_interactivas.append(
                    ft.Container(
                        width=20, height=20, left=x_a - 10, top=y_a - 10,
                        tooltip=ft.Tooltip(message=f"{nombre_a} | {tooltips_a[i]}", prefer_below=False),
                        bgcolor=ft.Colors.TRANSPARENT, shape=ft.BoxShape.CIRCLE
                    )
                )
                zonas_interactivas.append(
                    ft.Container(
                        width=20, height=20, left=x_b - 10, top=y_b - 10,
                        tooltip=ft.Tooltip(message=f"{nombre_b} | {tooltips_b[i]}", prefer_below=False),
                        bgcolor=ft.Colors.TRANSPARENT, shape=ft.BoxShape.CIRCLE
                    )
                )

            stack_radar = ft.Stack(
                controls=[canvas_radar] + zonas_interactivas,
                width=canvas_size, height=canvas_size
            )
            
            container_radar = ft.Container(
                content=stack_radar, padding=15, bgcolor="surface", 
                border_radius=12, alignment=ft.alignment.center
            )

            estado_highlight = {"activo": None}

            def actualizar_opacidades():
                if estado_highlight["activo"] == "A":
                    path_a_fill.paint.color = ft.Colors.with_opacity(0.8, "primary")
                    path_b_fill.paint.color = ft.Colors.with_opacity(0.05, "secondary")
                    path_b_stroke.paint.color = ft.Colors.with_opacity(0.2, "secondary")
                    for dot in dots_b: dot.paint.color = ft.Colors.with_opacity(0.2, "secondary")
                elif estado_highlight["activo"] == "B":
                    path_a_fill.paint.color = ft.Colors.with_opacity(0.05, "primary")
                    path_a_stroke.paint.color = ft.Colors.with_opacity(0.2, "primary")
                    for dot in dots_a: dot.paint.color = ft.Colors.with_opacity(0.2, "primary")
                    path_b_fill.paint.color = ft.Colors.with_opacity(0.8, "secondary")
                else:
                    path_a_fill.paint.color = ft.Colors.with_opacity(0.4, "primary")
                    path_a_stroke.paint.color = "primary"
                    path_b_fill.paint.color = ft.Colors.with_opacity(0.4, "secondary")
                    path_b_stroke.paint.color = "secondary"
                    for dot in dots_a: dot.paint.color = "primary"
                    for dot in dots_b: dot.paint.color = "secondary"
                canvas_radar.update()

            def click_card_a(e):
                estado_highlight["activo"] = "A" if estado_highlight["activo"] != "A" else None
                actualizar_opacidades()

            def click_card_b(e):
                estado_highlight["activo"] = "B" if estado_highlight["activo"] != "B" else None
                actualizar_opacidades()

            score_card = ft.Container(
                padding=10, bgcolor="surface", border_radius=12, border=ft.border.all(1, "outline"),
                content=ft.Row([
                    ft.Container(
                        content=ft.Column([
                            ft.Text(f"{puntos_a}", size=30, weight="bold", color="primary"), 
                            ft.Text(f"{self.i18n.t('ui.tab_comparador.puntos')} {nombre_a}", size=10, text_align=ft.TextAlign.CENTER)
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        expand=True, ink=True, on_click=click_card_a, border_radius=8, padding=5
                    ),
                    ft.VerticalDivider(width=10, color="white12"),
                    ft.Container(
                        content=ft.Column([
                            ft.Text(f"{puntos_b}", size=30, weight="bold", color="secondary"), 
                            ft.Text(f"{self.i18n.t('ui.tab_comparador.puntos')} {nombre_b}", size=10, text_align=ft.TextAlign.CENTER)
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        expand=True, ink=True, on_click=click_card_b, border_radius=8, padding=5
                    ),
                ], alignment=ft.MainAxisAlignment.CENTER)
            )

            col_checks = ft.Row([
                ft.Column([ft.Text(f"{self.i18n.t('ui.tab_comparador.mejores_stats')} {nombre_a}", color="primary", weight="bold"), *lista_ventajas_a], expand=True),
                ft.VerticalDivider(width=10),
                ft.Column([ft.Text(f"{self.i18n.t('ui.tab_comparador.mejores_stats')} {nombre_b}", color="secondary", weight="bold"), *lista_ventajas_b], expand=True)
            ], vertical_alignment=ft.CrossAxisAlignment.START)
            
            container_checks = ft.Container(content=col_checks, padding=10, bgcolor="surface", border_radius=12)

            stats_calc_a = self.app._normalizar_stats_para_calculo(stats_a)
            stats_calc_b = self.app._normalizar_stats_para_calculo(stats_b)

            agente_a = stats_calc_a.get("Nombre_Agente", "Desconocido")
            agente_b = stats_calc_b.get("Nombre_Agente", "Desconocido")
            
            elem_a = self.app._detectar_elemento(agente_a, stats_a)
            elem_b = self.app._detectar_elemento(agente_b, stats_b)

            dmg_a_norm, dmg_a_sheer, dmg_a_anom, dmg_a_dis, _, _, _ = self.app.calcular_dano_simulado(stats_calc_a, elem_a)
            dmg_b_norm, dmg_b_sheer, dmg_b_anom, dmg_b_dis, _, _, _ = self.app.calcular_dano_simulado(stats_calc_b, elem_b)

            enemigo_nombre = stats_calc_a.get("Nombre_Enemigo", "Ninguno")
            defensa_enemigo = int(stats_calc_a.get("Defensa_Base", 950))
            res_enemigo = int(stats_calc_a.get("Resistencia_porcentual", 0))

            def crear_barra_dmg(titulo, val_a, val_b, color_base):
                max_v = max(val_a, val_b)
                if max_v == 0: max_v = 1
                
                p_a = val_a / max_v
                p_b = val_b / max_v
                
                txt_a_style = ft.FontWeight.BOLD if val_a >= val_b else ft.FontWeight.NORMAL
                txt_b_style = ft.FontWeight.BOLD if val_b > val_a else ft.FontWeight.NORMAL

                diff_pct = 0
                if val_b > 0: diff_pct = ((val_a - val_b) / val_b) * 100
                
                txt_diff = ""
                if val_a > val_b: txt_diff = self.i18n.t("ui.tab_comparador.a_superior").replace("{pct}", f"{diff_pct:.1f}")
                elif val_b > val_a: 
                    if val_a > 0:
                        diff_inv = ((val_b - val_a) / val_a) * 100
                        txt_diff = self.i18n.t("ui.tab_comparador.b_superior").replace("{pct}", f"{diff_inv:.1f}")
                    else:
                        txt_diff = self.i18n.t("ui.tab_comparador.b_infinito")

                return ft.Column([
                    ft.Row([ft.Text(titulo, size=12, weight="bold"), ft.Text(txt_diff, size=10, color="grey")], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Row([
                        ft.Column([
                            ft.ProgressBar(value=p_a, color="primary", bgcolor="black", height=8),
                            ft.Text(f"{val_a:,.0f}", size=11, color="primary", weight=txt_a_style)
                        ], expand=True),
                        ft.Text(self.i18n.t("ui.tab_comparador.vs"), size=10, italic=True),
                        ft.Column([
                            ft.ProgressBar(value=p_b, color="secondary", bgcolor="black", height=8),
                            ft.Text(f"{val_b:,.0f}", size=11, color="secondary", weight=txt_b_style)
                        ], expand=True),
                    ])
                ], spacing=2)
            
            grid_dano_content = ft.ResponsiveRow(spacing=20, run_spacing=20)

            def agregar_al_grid(control):
                grid_dano_content.controls.append(
                    ft.Container(content=control, col={"md": 6, "sm": 12})
                )

            if dmg_a_norm > 0 or dmg_b_norm > 0:
                agregar_al_grid(crear_barra_dmg(self.i18n.t("ui.tab_comparador.dano_normal_crit"), dmg_a_norm, dmg_b_norm, "blue"))
            
            if dmg_a_sheer > 0 or dmg_b_sheer > 0:
                agregar_al_grid(crear_barra_dmg(self.i18n.t("ui.tab_comparador.dano_sheer_rup"), dmg_a_sheer, dmg_b_sheer, "teal"))

            if dmg_a_anom > 0 or dmg_b_anom > 0:
                agregar_al_grid(crear_barra_dmg(self.i18n.t("ui.tab_comparador.dano_anomalia_title"), dmg_a_anom, dmg_b_anom, "purple"))
                
            if dmg_a_dis > 0 or dmg_b_dis > 0:
                agregar_al_grid(crear_barra_dmg(self.i18n.t("ui.tab_comparador.dano_disorder_title"), dmg_a_dis, dmg_b_dis, "pink"))

            if not grid_dano_content.controls:
                grid_dano_content.controls.append(ft.Text(self.i18n.t("ui.tab_comparador.sin_datos_dano"), italic=True, color="grey"))

            card_dano = ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text(self.i18n.t("ui.tab_comparador.simulacion_dano"), weight=ft.FontWeight.BOLD, size=15)
                    ], alignment=ft.MainAxisAlignment.CENTER),
                    ft.Divider(height=5, color="outline"),
                    ft.Row([
                        ft.Text(f"{self.i18n.t('ui.tab_comparador.evaluado_contra')} {enemigo_nombre} (Def {defensa_enemigo} / Res {res_enemigo}%) | Skill MV (500%)", size=self.FS['xs'], italic=True, color="primary")
                    ], alignment=ft.MainAxisAlignment.CENTER),
                    ft.Container(height=10),
                    grid_dano_content
                ], spacing=5),
                padding=20,
                bgcolor="background",
                border=ft.border.all(1, "outline"),
                border_radius=12,
                margin=ft.margin.only(top=10)
            )
            
            self.contenedor_analisis.content.controls = [
                header_comparativa,
                ft.Divider(height=10),
                
                ft.ResponsiveRow([
                    ft.Column([score_card, container_checks], col={"md": 5}),
                    ft.Column([container_radar], col={"md": 7})
                ]),

                ft.ResponsiveRow([
                    ft.Column([card_dano], col={"md": 12})
                ])
            ]
            self.contenedor_analisis.update()

        except Exception as e:
            print(f"ERROR CRÍTICO EN GENERAR_ANALISIS: {e}")
            self.contenedor_analisis.content.controls = [ft.Text(f"Error en análisis: {e}", color="red")]
            self.contenedor_analisis.update()

    def mostrar_recomendaciones_ui(self, rol, consejos):
        """Muestra tarjetas de recomendaciones — VISUAL REFACTOR"""
        self.columna_recomendaciones.controls.clear()

        # ── Header con pill de rol ────────────────────────────────────
        self.columna_recomendaciones.controls.append(
            ft.Container(
                content=ft.Row([
                    ft.Container(
                        content=ft.Icon(ft.Icons.PERSON_SEARCH, color="background", size=20),
                        bgcolor="primary",
                        padding=ft.padding.all(8),
                        border_radius=20,
                        shadow=ft.BoxShadow(blur_radius=10, spread_radius=0,
                                            color=ft.Colors.with_opacity(0.4, ft.Colors.PRIMARY))
                    ),
                    ft.Text(
                        self.i18n.t("ui.tab_recomendaciones.arquetipo_detectado")
                            .replace("{rol}", rol),
                        size=22, weight="bold", color="primary"
                    )
                ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                padding=ft.padding.only(bottom=20)
            )
        )

        mitad = (len(consejos) + 1) // 2
        items_izq = consejos[:mitad]
        items_der = consejos[mitad:]

        def crear_tarjeta(item):
            icono, titulo, mensaje, color_tema = item

            tarjeta = ft.Container(
                padding=ft.padding.all(16),
                bgcolor="surface",
                border=ft.border.only(left=ft.BorderSide(4, color_tema)),
                border_radius=12,
                shadow=ft.BoxShadow(
                    blur_radius=10, spread_radius=0,
                    color=ft.Colors.with_opacity(0.15, color_tema),
                    offset=ft.Offset(0, 3)
                ),
                animate_scale=ft.Animation(260, ft.AnimationCurve.EASE_OUT),
                content=ft.Row([
                    ft.Container(
                        content=ft.Icon(icono, color="background", size=22),
                        bgcolor=color_tema,
                        padding=ft.padding.all(8),
                        border_radius=8,
                        shadow=ft.BoxShadow(
                            blur_radius=8, spread_radius=0,
                            color=ft.Colors.with_opacity(0.3, color_tema)
                        )
                    ),
                    ft.VerticalDivider(width=14, color="transparent"),
                    ft.Column([
                        ft.Text(titulo, weight=ft.FontWeight.BOLD, size=15,
                                color=ft.Colors.WHITE),
                        ft.Text(mensaje, size=12, color=ft.Colors.WHITE70,
                                selectable=True)
                    ], spacing=3, expand=True)
                ], vertical_alignment=ft.CrossAxisAlignment.CENTER)
            )

            def on_hover_tarjeta(e):
                tarjeta.scale = 1.015 if e.data == "true" else 1.0
                tarjeta.shadow = ft.BoxShadow(
                    blur_radius=18 if e.data == "true" else 10,
                    spread_radius=2 if e.data == "true" else 0,
                    color=ft.Colors.with_opacity(
                        0.3 if e.data == "true" else 0.15,
                        color_tema
                    ),
                    offset=ft.Offset(0, 5 if e.data == "true" else 3)
                )
                tarjeta.update()

            tarjeta.on_hover = on_hover_tarjeta
            return tarjeta

        col_izq = ft.Column(
            controls=[crear_tarjeta(i) for i in items_izq],
            spacing=12,
            expand=True
        )
        col_der = ft.Column(
            controls=[crear_tarjeta(i) for i in items_der],
            spacing=12,
            expand=True
        )

        self.columna_recomendaciones.controls.append(
            ft.Row(
                controls=[
                    col_izq,
                    ft.VerticalDivider(width=20, color="transparent"),
                    col_der
                ],
                vertical_alignment=ft.CrossAxisAlignment.START,
                expand=True
            )
        )

        self.columna_recomendaciones.update()
        self.app.tabs_control.selected_index = 3
        self.app.tabs_control.update()

    def renderizar_bloque_visual_equipamiento(
            self, nombre_agente, datos_discos_json, nombre_wengine, rol_agente="Atacante",
            contenedor_texto_recomm=None, resumen_rolls=None, ruta_wengine_custom=None,
            tarjeta_discos=None, eficiencia_wengine=100.0, top_wengines=None,
            proj_final=None
            ):

        def _tr_set(nombre):
            return self.i18n.t(f"sets.{nombre}", default=nombre)

        canvas_size = 620       
        center_xy = canvas_size / 2
        radio = 220             
        size_disco = 140        
        size_wengine = 200      

        config_rol = CONFIG_ROLES.get(rol_agente, CONFIG_ROLES["Atacante"])
        if nombre_agente in EXCEPCIONES_AGENTES:
            excep = EXCEPCIONES_AGENTES[nombre_agente]
            if "subs" in excep: config_rol["subs"] = excep["subs"]

        stats_ideales = [s.lower() for s in config_rol["subs"]["ideal"]]
        stats_decentes = [s.lower() for s in config_rol["subs"]["decente"]]

        def limpiar_nombre_stat(nombre_raw, valor_str):
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

        def calcular_rolls_real(nombre_stat, valor_texto):
            try:
                val_str = str(valor_texto).replace("%","").replace(",",".").strip()
                val_float = float(val_str)
                n_low = nombre_stat.lower()
                base = 3.0 
                
                if "crit" in n_low:
                    base = 4.8 if ("dmg" in n_low or "daño" in n_low) else 2.4
                elif "def" in n_low:
                    base = 4.8 if ("%" in str(valor_texto) or "percent" in n_low) else 15
                elif "pen" in n_low:
                    base = 2.4 if ("%" in str(valor_texto) or "ratio" in n_low) else 9
                elif "maestr" in n_low or "prof" in n_low: base = 9.0
                elif "impact" in n_low: base = 18.0
                
                if base == 3.0 and ("%" not in str(valor_texto) and "percent" not in n_low):
                    if "ataque" in n_low or "atk" in n_low: base = 19
                    elif "vida" in n_low or "hp" in n_low: base = 112
                
                rolls = int(round(val_float / base))
                return max(1, rolls)
            except: return 1

        def obtener_tier_disco(substats, nombre_main_stat, slot_num):
            score_total = 0
            clave_main = limpiar_nombre_stat(nombre_main_stat, "0%")
            
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
                clave_interna = limpiar_nombre_stat(raw_name, raw_val).lower()
                rolls = calcular_rolls_real(raw_name, raw_val)

                if clave_interna in stats_ideales:
                    score_total += (rolls * mult_ideal)
                elif clave_interna in stats_decentes:
                    score_total += (rolls * mult_decente)
            
            clave, color_hex = calificacion_a_tier(score_total * 10)
            sombra = construir_sombra_tier(clave, color_hex) if clave != "MID" else None

            return clave, clave, color_hex, sombra

        def mostrar_detalle_disco(e):
            datos = e.control.data
            slot_num = datos.get("slot_num")
            
            if not datos or not datos.get("tiene_datos"):
                dlg = ft.AlertDialog(
                    title=ft.Text(self.i18n.t("ui.tab_recomendaciones_visual.slot_num").replace("{slot}", str(slot_num))), 
                    content=ft.Text(self.i18n.t("ui.tab_recomendaciones_visual.vacio"))
                )
                self.app.page.open(dlg)
                return

            nombre_set = datos.get("nombre_set", "Desconocido")
            nombre_set_trad = _tr_set(nombre_set)
            main_stat = datos.get("main_stat", {})
            sub_stats = datos.get("sub_stats", [])
            
            def obtener_estilo_stat_visual(nombre_stat, valor_texto):
                clave = limpiar_nombre_stat(nombre_stat, valor_texto).lower()
                rolls_totales = calcular_rolls_real(nombre_stat, valor_texto)
                upgrades = rolls_totales - 1
                txt_roll = f"+{upgrades}" if upgrades > 0 else ""
                if clave in stats_ideales:
                    c_bg = "#ffb300" if upgrades > 0 else ft.Colors.TRANSPARENT
                    return "#ffc107", c_bg, "black", txt_roll, ft.Icons.AUTO_AWESOME
                elif clave in stats_decentes:
                    c_bg = "#0097a7" if upgrades > 0 else ft.Colors.TRANSPARENT
                    return "#00bcd4", c_bg, "white", txt_roll, ft.Icons.CHECK_CIRCLE_OUTLINE
                else:
                    c_bg = "#424242" if upgrades > 0 else ft.Colors.TRANSPARENT
                    return "#bdbdbd", c_bg, "white", txt_roll, ft.Icons.CIRCLE_OUTLINED
                
            filas_subs = []
            for sub in sub_stats:
                s_name = sub.get("name","")
                s_name_trad = self.i18n.t(f"api_stats.{s_name}", default=s_name)
                s_val = sub.get("value","0")
                c_txt, c_bg, c_pil, txt_roll, icon_data = obtener_estilo_stat_visual(s_name, s_val)
                
                filas_subs.append(ft.Container(
                    padding=ft.padding.symmetric(vertical=3),
                    content=ft.Row([
                        ft.Icon(icon_data, size=14, color=c_txt),
                        ft.Text(s_name_trad, size=13, color=c_txt, weight="bold", expand=True),
                        ft.Container(content=ft.Text(txt_roll, size=10, color=c_pil, weight="bold"), bgcolor=c_bg, border_radius=8, padding=ft.padding.symmetric(horizontal=5)),
                        ft.Text(s_val, size=13, weight="bold", color="white")
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER)
                ))

            ruta_icono = f"images/discos/{nombre_set}.png"
            if hasattr(self.app, 'ruta_recursos'): ruta_icono = os.path.join(self.app.ruta_recursos, ruta_icono)
            img_header = ft.Image(src=ruta_icono, width=50, height=50) if os.path.exists(ruta_icono) else ft.Icon(ft.Icons.DISC_FULL, size=40)
            
            panel_ideal = ft.Container(visible=False)
            tier_pct_act = _tier_activo[0]
            if tier_pct_act is not None and proj_final:
                tier_colors_dlg = {100: "primary", 90: "secondary", 80: "tertiary"}
                tier_names_dlg  = {
                    100: self.i18n.t("ui.tab_recomendaciones.tier_perfecto",  default="100% — Perfect"),
                    90:  self.i18n.t("ui.tab_recomendaciones.tier_excelente", default="90% — Excellent"),
                    80:  self.i18n.t("ui.tab_recomendaciones.tier_bueno",     default="80% — Good"),
                }
                cc_dlg = tier_colors_dlg.get(tier_pct_act, "primary")
                card = _mk_disco_card(slot_num, tier_pct_act, cc_dlg)
                lbl_disco_ideal = (
                    self.i18n.t("ui.tab_recomendaciones_visual.disco_ideal_titulo",
                                default=f"Disco ideal — {tier_names_dlg.get(tier_pct_act,'')}")
                    .replace("{tier}", tier_names_dlg.get(tier_pct_act,""))
                )
                panel_ideal = ft.Container(
                    width=260, padding=0,
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(ft.Icons.AUTO_FIX_HIGH, size=14, color=cc_dlg),
                            ft.Text(lbl_disco_ideal, size=12, weight="bold", color=cc_dlg),
                        ], spacing=4),
                        card,
                    ], spacing=6, tight=True),
                    visible=True,
                )

            dlg = ft.AlertDialog(
                content=ft.Container(
                    bgcolor="#1b1b1b", border=ft.border.all(1, "#333"),
                    border_radius=12, padding=15,
                    content=ft.Row([
                        ft.Container(
                            width=320,
                            content=ft.Column([
                                ft.Row([ft.Column([ft.Text(nombre_set_trad, weight="bold", size=14), ft.Text(self.i18n.t("ui.tab_recomendaciones_visual.slot_num", default="Slot {slot}").replace("{slot}", str(slot_num)), color="grey", size=12)]), img_header], alignment="spaceBetween"),
                                ft.Divider(color="#444"),
                                ft.Row([ft.Text(self.i18n.t(f"api_stats.{main_stat.get('name','')}", default=main_stat.get("name","")), size=15, weight="bold"), ft.Text(main_stat.get("value",""), size=24, weight="bold", color="primary")], alignment="spaceBetween"),
                                ft.Divider(color="#444"),
                                ft.Column(filas_subs, spacing=4)
                            ], tight=True, spacing=6)
                        ),
                        panel_ideal,
                    ], spacing=16, vertical_alignment=ft.CrossAxisAlignment.START, tight=True)
                ),
                bgcolor="transparent", content_padding=0
            )
            self.app.page.open(dlg)

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

        ruta_img_rel = f"images/builds/{nombre_agente}.png"
        src_agente = ruta_img_rel
        if hasattr(self.app, 'ruta_recursos'):
                full_path = os.path.join(self.app.ruta_recursos, ruta_img_rel)
                if not os.path.exists(full_path) and not os.path.exists(ruta_img_rel): src_agente = ""
        elif not os.path.exists(ruta_img_rel): src_agente = ""

        colores_agentes = {
            "Nicole": (255, 124, 164), "Anby": (220, 249, 33), "Billy": (198, 28, 28),
            "Nekomata": (246, 85, 59), "Koleda": (255, 90, 0), "Anton": (255, 90, 0),
            "Ben": (249, 149, 27), "Grace": (228, 97, 53), "Lycaon": (167, 193, 199),
            "Rina": (237, 60, 76), "Ellen": (252, 53, 118), "Corin": (182, 65, 255),
            "Zhu Yuan": (0, 76, 211), "Qingyi": (0, 245, 190), "Seth": (84, 139, 239),
            "Jane": (252, 53, 116), "Caesar": (210, 172, 71), "Lighter": (177, 31, 49),
            "Lucy": (245, 182, 53), "Burnice": (210, 172, 71), "Piper": (255, 188, 1),
            "Pulchra": (237, 140, 34), "Miyabi": (82, 171, 169), "Yanagi": (253, 115, 136),
            "Harumasa": (255, 204, 0), "Soukaku": (0, 228, 255), "Astra Yao": (182, 25, 39),
            "Evelyn": (182, 154, 228), "Soldier 0 - Anby": (254, 191, 37), "Hugo": (245, 11, 38),
            "Vivian": (132, 94, 230), "Orphie & Magus": (231, 45, 80), "Trigger": (253, 200, 33),
            "Soldier 11": (254, 209, 22), "Seed": (254, 183, 32), "Yixuan": (249, 196, 62),
            "Ye Shunguang": (212, 30, 16), "Ju Fufu": (255, 144, 0), "Pan Yinhu": (253, 203, 90),
            "Yuzuha": (226, 60, 60), "Alice": (253, 208, 124), "Manato": (198, 61, 32),
            "Lucia": (25, 203, 228), "Yidhari": (123, 107, 165), "Dialyn": (108, 252, 236),
            "Banyue": (217, 175, 103), "Zhao": (254, 95, 121), "Sunna": (214, 255, 100),
            "Aria": (132, 94, 230), "Nangong Yu": (168, 114, 235), "Cissia": (235, 52, 142),
            "Promeia": (132, 73, 239), "Starlight - Billy": (195, 68, 73),
        }
        
        rgb = (38, 50, 56)
        for k, v in colores_agentes.items():
            if k.lower() == nombre_agente.lower():
                rgb = v
                break
                
        bg_color_agente = f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"

        fondo_tarjeta = ft.Container(
            width=260, height=600,
            bgcolor=bg_color_agente,
            border=ft.border.all(2, ft.Colors.RED_900),
            border_radius=12,
            shadow=ft.BoxShadow(blur_radius=15, color=ft.Colors.BLACK),
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
            content=ft.Image(
                src="images/builds/fondo.png", 
                width=260, height=600, 
                fit=ft.ImageFit.COVER,
                opacity=0.9
            )
        )

        ajustes_agentes = {
        "Alice": (50, 35, 1.00),
        "Anby": (-25, 180, 1.15),
        "Anton": (10, 55, 1.10),
        "Aria": (30, 25, 0.95),
        "Astra Yao": (30, 75, 1.10),
        "Banyue": (50, 35, 1.00),
        "Ben": (65, 200, 1.15),
        "Billy": (30, 95, 1.10),
        "Burnice": (00, 125, 1.20),
        "Caesar": (-10, 175, 1.20),
        "Cissia": (0, 155, 1.20),
        "Corin": (-20, 175, 1.20),
        "Dialyn": (30, 35, 1.00),
        "Ellen": (-30, 220, 1.30),
        "Evelyn": (0, 130, 1.20),
        "Grace": (35, 0, 0.65),
        "Harumasa": (0, 135, 1.20),
        "Hugo": (-10, 55, 1.10),
        "Jane": (40, 15, 1.00),
        "Ju Fufu": (80, 135, 1.10),
        "Koleda": (40, 200, 1.20),
        "Lighter": (20, -10, 0.90),
        "Lucia": (80, 75, 1.00),
        "Lucy": (-20, 200, 1.20),
        "Lycaon": (0, 155, 1.25),
        "Manato": (40, 105, 1.15),
        "Miyabi": (20, 155, 1.25),
        "Nangong Yu": (0, 135, 1.10),
        "Nekomata": (0, 135, 1.00),
        "Nicole": (-10, 35, 1.00),
        "Orphie & Magus": (90, 125, 1.02),
        "Pan Yinhu": (50, 155, 1.10),
        "Piper": (70, 35, 0.8),
        "Pulchra": (50, 135, 1.10),
        "Promeia": (50, 100, 1.00),
        "Qingyi": (20, 65, 1.00),
        "Rina": (60, 185, 1.20),
        "Seed": (0, -35, 0.8),
        "Seth": (20, 125, 1.20),
        "Soldier 0 - Anby": (20, 35, 1.00),
        "Soldier 11": (0, -15, 0.80),
        "Soukaku": (0, 155, 1.20),
        "Sunna": (0, -15, 0.80),
        "Trigger": (40, 55, 1.10),
        "Vivian": (0, 55, 1.10),
        "Yanagi": (100, 155, 1.25),
        "Ye Shunguang": (40, 135, 1.25),
        "Yidhari": (50, 55, 1.00),
        "Yixuan": (-10, 135, 1.30),
        "Yuzuha": (-10, 95, 1.0),
        "Zhao": (45, 230, 1.25),
        "Zhu Yuan": (40, -25, 0.80),
        }

        offset_x, offset_y, escala = ajustes_agentes.get(nombre_agente, (0, 0, 1.0))

        imagen_agente_flotante = ft.Container(
            bottom=0,    
            left=-100 + offset_x, 
            width=420,   
            height=1200, 
            clip_behavior=ft.ClipBehavior.HARD_EDGE, 
            content=ft.Stack(
                controls=[
                    ft.Container(
                        left=0,
                        bottom=-175 + offset_y, 
                        width=420,
                        height=975,
                        alignment=ft.alignment.bottom_center, 
                        content=ft.Image(
                            src=src_agente, 
                            fit=ft.ImageFit.CONTAIN, 
                            scale=escala,
                            opacity=1.0 if src_agente else 0
                        )
                    )
                ]
            )
        )

        etiqueta_nombre = ft.Container(
            bottom=0, left=0, right=0,
            content=ft.Text(nombre_agente.upper(), size=26, weight="bold", color="white", text_align="center"),
            bgcolor=ft.Colors.BLACK87, 
            padding=15, 
            alignment=ft.alignment.center,
            border_radius=ft.border_radius.only(bottom_left=15, bottom_right=15)
        )

        columna_imagen_agente = ft.Container(
            width=260, height=600,
            margin=ft.margin.only(top=40), 
            content=ft.Stack(
                controls=[
                    fondo_tarjeta,
                    imagen_agente_flotante,
                    etiqueta_nombre
                ],
                clip_behavior=ft.ClipBehavior.NONE
            )
        )

        posiciones_disco = {
            1: (113,  65),
            2: ( 32, 240),
            3: (113, 415),
            4: (365, 415),
            5: (450, 240),
            6: (365,  65),
        }
        controles_stack = []

        src_wengine_final = ""
        if ruta_wengine_custom: src_wengine_final = ruta_wengine_custom
        else:
            nombre_clean = nombre_wengine.strip()
            src_wengine_final = f"/images/wengine/{nombre_clean}.png"
            path_check = f"images/wengine/{nombre_clean}.png"
            if hasattr(self.app, 'ruta_recursos'): path_check = os.path.join(self.app.ruta_recursos, path_check)
            if not os.path.exists(path_check) and not os.path.exists(f"images/wengine/{nombre_clean}.png"): src_wengine_final = ""
        
        def obtener_color_eficiencia_wengine(eficiencia):
            if eficiencia >= 100: return "#00ffff", ft.BoxShadow(blur_radius=25, spread_radius=3, color="#00ffff")
            elif eficiencia >= 90: return "#ffea00", ft.BoxShadow(blur_radius=25, spread_radius=2, color="#ffea00")
            elif eficiencia >= 80: return "#ff6d00", ft.BoxShadow(blur_radius=25, spread_radius=1, color="#ff6d00")
            elif eficiencia >= 70: return "#ff1744", ft.BoxShadow(blur_radius=25, spread_radius=1, color="#ff1744")
            elif eficiencia >= 60: return "#d500f9", ft.BoxShadow(blur_radius=20, color="#d500f9")
            elif eficiencia >= 50: return "#2979ff", ft.BoxShadow(blur_radius=15, color="#2979ff")
            else: return "secondary", ft.BoxShadow(blur_radius=10, color="background")

        color_wengine, sombra_wengine = obtener_color_eficiencia_wengine(eficiencia_wengine)
        contenido_wengine = ft.Image(src=src_wengine_final, fit=ft.ImageFit.CONTAIN, scale=0.8) if src_wengine_final else ft.Icon(ft.Icons.FLASH_ON, color="yellow", size=50)
        controles_stack.append(ft.Container(
            content=contenido_wengine, width=size_wengine, height=size_wengine, bgcolor=ft.Colors.BLACK87, 
            border_radius=size_wengine/2, border=ft.border.all(3, color_wengine), alignment=ft.alignment.center,
            left=center_xy - (size_wengine/2), top=center_xy - (size_wengine/2), 
            shadow=sombra_wengine,
        ))

        mapa_discos_importados = {}
        if datos_discos_json:
            print(f"DEBUG renderizar_bloque: Recibidos {len(datos_discos_json)} discos JSON")
            for d in datos_discos_json:
                try:
                    s = int(d.get("slot", 0))
                    if 1 <= s <= 6: 
                        mapa_discos_importados[s] = d
                except Exception as ex:
                    print(f"  - Error procesando disco: {ex}")
        else:
            print(f"DEBUG renderizar_bloque: NO se recibieron datos_discos_json")
        
        discos_manuales = self.app.estado_actual.discos
        
        for slot, (pos_x, pos_y) in posiciones_disco.items():

            ruta_disco = ""
            texto_tooltip = f"Slot {slot}" 
            datos_evento = {"slot_num": slot, "tiene_datos": False}
            tier_key = ""
            tier_texto = ""
            tier_color = ft.Colors.TRANSPARENT
            tier_shadow = None
            
            if slot in mapa_discos_importados:
                disco_data = mapa_discos_importados[slot]
                raw_set_id = disco_data.get("set_id", 0)
                try: set_id = int(raw_set_id)
                except: set_id = 0
                nombre_set = MAPA_SETS_ID.get(set_id, f"Set ID: {set_id}")
                ruta_disco = f"images/discos/{nombre_set}.png"
                texto_tooltip = f"{_tr_set(nombre_set)}"
                
                subs = disco_data.get("sub_stats", [])
                main_stat_name = disco_data.get("main_stat", {}).get("name", "")
                tier_key, tier_texto, tier_color, tier_shadow = obtener_tier_disco(subs, main_stat_name, slot)

                datos_evento = {
                    "slot_num": slot, "tiene_datos": True, "nombre_set": nombre_set,
                    "main_stat": disco_data.get("main_stat", {}), "sub_stats": subs
                }
            elif not ruta_disco:
                if slot in [1, 2, 3]:
                    fixed_stats = ["Vida", "Ataque", "Defensa"]
                    texto_tooltip = f"{fixed_stats[slot-1]} (Base)"
                else:
                    stat_manual = discos_manuales.get(slot, "Ninguno")
                    texto_tooltip = f"{stat_manual}" if stat_manual != "Ninguno" else self.i18n.t("ui.tab_recomendaciones_visual.slot_vacio").replace("{slot}", str(slot))

            contenido_disco = None
            
            if os.path.exists(ruta_disco):
                contenido_disco = ft.Image(src=ruta_disco, fit=ft.ImageFit.CONTAIN, scale=1.1)
            else:
                icono_stat = ft.Icons.CIRCLE
                if slot == 1: icono_stat = ft.Icons.FAVORITE
                elif slot == 2: icono_stat = ft.Icons.FLASH_ON 
                elif slot == 3: icono_stat = ft.Icons.SHIELD
                contenido_disco = ft.Column([ft.Icon(icono_stat, size=20, color="white24"),
                                            ft.Text(self.i18n.t("ui.tab_recomendaciones_visual.empty"), size=12, color="white24")],
                                            alignment=ft.MainAxisAlignment.CENTER, spacing=2)
            
            badge_tier_content = ft.Container()
            if tier_texto:
                if tier_key == "GODLIKE":
                    letras_dios = ft.Text(
                        spans=[
                            ft.TextSpan("G", style=ft.TextStyle(color="#FF85A2", weight="bold", font_family="Consolas")),
                            ft.TextSpan("O", style=ft.TextStyle(color="#FFEA75", weight="bold", font_family="Consolas")),
                            ft.TextSpan("D", style=ft.TextStyle(color="#85FF9E", weight="bold", font_family="Consolas")),
                        ],
                        size=14, text_align="center"
                    )

                    badge_tier_content = ft.Container(
                        padding=1, 
                        border_radius=8,
                        gradient=ft.LinearGradient(
                            colors=["#FF003C", "#FFD500", "#00FF2A", "#0066FF"],
                            begin=ft.alignment.center_left,
                            end=ft.alignment.center_right
                        ),
                        content=ft.Container(
                            bgcolor=ft.Colors.BLACK87,
                            padding=ft.padding.symmetric(horizontal=8, vertical=2),
                            border_radius=8,
                            alignment=ft.alignment.center,
                            content=letras_dios
                        )
                    )
                else:
                    badge_tier_content = ft.Container(
                        content=ft.Text(tier_texto, size=14, weight="bold", color=tier_color, font_family="Consolas"),
                        bgcolor=ft.Colors.BLACK87, padding=ft.padding.symmetric(horizontal=8, vertical=2),
                        border=ft.border.all(1, tier_color), border_radius=8, shadow=tier_shadow, alignment=ft.alignment.center
                    )

            borde_color = ft.Colors.GREY_800
            if tier_key == "GODLIKE": borde_color = ft.Colors.WHITE 
            elif tier_color and tier_color != ft.Colors.TRANSPARENT: borde_color = tier_color
            elif os.path.exists(ruta_disco): borde_color = ft.Colors.AMBER_600
            
            sombra_disco = ft.BoxShadow(blur_radius=12, color=ft.Colors.BLACK)
            if tier_shadow and tier_key != "GODLIKE": 
                sombra_disco = tier_shadow

            if tier_key == "GODLIKE":
                focos_rgb = [
                    ("#FF003C", -10, 0),
                    ("#FFD500", -5, 0),
                    ("#00FF2A", 5, 0),
                    ("#0066FF", 10, 0),
                ]
                
                for color_hex, ox, oy in focos_rgb:
                    controles_stack.append(
                        ft.Container(
                            width=size_disco, height=size_disco,
                            bgcolor="surface",
                            border_radius=size_disco / 2,
                            shadow=ft.BoxShadow(blur_radius=15, spread_radius=1, color=color_hex, offset=ft.Offset(ox, oy)),
                            left=pos_x, top=pos_y
                        )
                    )

            btn_disco = ft.Container(
                width=size_disco, height=size_disco, 
                content=ft.Stack([
                    ft.Container(
                        width=size_disco, height=size_disco, bgcolor=ft.Colors.BLACK87, 
                        border_radius=size_disco/2, border=ft.border.all(2, borde_color),
                        content=ft.Container(content=contenido_disco, alignment=ft.alignment.center, padding=8),
                        shadow=sombra_disco if tier_key != "GODLIKE" else None 
                    ),
                    ft.Container(content=ft.Text(str(slot), size=12, weight="bold", color="white"), 
                        bgcolor="surface", padding=ft.padding.symmetric(horizontal=8, vertical=4), 
                        border_radius=8, border=ft.border.all(1, "outline"), top=0, left=(size_disco/2)-12
                    ),
                    ft.Container(content=badge_tier_content, alignment=ft.alignment.bottom_center, width=size_disco, bottom=-10)
                ], clip_behavior=ft.ClipBehavior.NONE), 
                left=pos_x, top=pos_y, tooltip=texto_tooltip, data=datos_evento, on_click=mostrar_detalle_disco, ink=False 
            )
            controles_stack.append(btn_disco)

        _calidad_discos_actuales = {}
        for slot in range(1, 7):
            if slot in mapa_discos_importados:
                _d = mapa_discos_importados[slot]
                _subs = _d.get("sub_stats", [])
                _main = _d.get("main_stat", {}).get("name", "")
                _tt, _, _, _ = obtener_tier_disco(_subs, _main, slot)
                _calidad_discos_actuales[slot] = _tt
            else:
                _calidad_discos_actuales[slot] = ""

        ruta_disco_bg = "images/builds/disco.png"
        ruta_disco_full = ruta_disco_bg
        if hasattr(self.app, 'ruta_recursos'):
            ruta_disco_full = os.path.join(self.app.ruta_recursos, ruta_disco_bg)
        tiene_disco_bg = os.path.exists(ruta_disco_full) or os.path.exists(ruta_disco_bg)

        if tiene_disco_bg:
            _bg_w    = 674
            _bg_h    = 575
            _bg_left = -27
            _bg_top  =  22
            controles_stack.insert(0, ft.Container(
                width=_bg_w, height=_bg_h,
                left=_bg_left, top=_bg_top,
                content=ft.Image(
                    src=ruta_disco_bg,
                    width=_bg_w, height=_bg_h,
                    fit=ft.ImageFit.FILL,
                    opacity=0.50,
                )
            ))

        contenedor_hexagono = ft.Container(
            width=canvas_size, height=canvas_size,
            content=ft.Stack(controles_stack),
            alignment=ft.alignment.center,
            margin=ft.margin.only(left=0)
        )

        total_ideal = resumen_rolls.get("ideal", 0) if resumen_rolls else 0
        total_decente = resumen_rolls.get("decente", 0) if resumen_rolls else 0
        total_basura = resumen_rolls.get("basura", 0) if resumen_rolls else 0
        calidad_pct = resumen_rolls.get("calidad_pct", 0) if resumen_rolls else 0
        calidad_dinamica_pct = resumen_rolls.get("calidad_dinamica_pct", calidad_pct) if resumen_rolls else calidad_pct
        calidad_clasica_pct = resumen_rolls.get("calidad_clasica_pct", calidad_pct) if resumen_rolls else calidad_pct
        color_calidad = ft.Colors.RED_400
        if calidad_pct > 75: color_calidad = ft.Colors.GREEN_400
        elif calidad_pct > 50: color_calidad = "secondary"

        top_armas_ui = []
        if top_wengines:
            for nombre_w, pct in top_wengines:
                if pct >= 100: c_color = "#00ffff"
                elif pct >= 90: c_color = "#ffea00"
                elif pct >= 80: c_color = "#ff6d00"
                elif pct >= 70: c_color = "#ff1744"
                elif pct >= 60: c_color = "#d500f9"
                elif pct >= 50: c_color = "#2979ff"
                else: c_color = "secondary"

                nombre_clean_w = str(nombre_w).strip()
                ruta_img_w = f"/images/wengine/{nombre_clean_w}.png"
                
                path_check_w = f"images/wengine/{nombre_clean_w}.png"
                if hasattr(self.app, 'ruta_recursos'): 
                    path_check_w = os.path.join(self.app.ruta_recursos, path_check_w)
                    
                if not os.path.exists(path_check_w) and not os.path.exists(f"images/wengine/{nombre_clean_w}.png"): 
                    img_control = ft.Icon(ft.Icons.FLASH_ON, size=18, color=c_color)
                else:
                    img_control = ft.Image(src=ruta_img_w, width=20, height=20, fit=ft.ImageFit.CONTAIN)

                top_armas_ui.append(
                    ft.Column([
                        ft.Row([
                            img_control,
                            ft.Text(f"{nombre_w} ({pct:.1f}%)", size=11, color="on_surface_variant", weight="bold")
                        ], spacing=5, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                        ft.ProgressBar(value=pct/100, color=c_color, bgcolor="surface", height=6, border_radius=3)
                    ], spacing=2)
                )

        contenedor_top_armas = ft.Container(
            width=220, padding=15, bgcolor="surface", border_radius=12, border=ft.border.all(1, "outline"),
            content=ft.Column([
                ft.Text(self.i18n.t("ui.tab_recomendaciones_visual.top_wengines"), size=self.FS['md'], weight="bold", color="primary"),
                ft.Divider(height=5, color="outline"),
                *top_armas_ui
            ], spacing=8),
            visible=bool(top_armas_ui)
        )

        import flet.canvas as cv
        
        rolls_actuales = getattr(self.app.estado_actual, 'substats_counts', {}) if hasattr(self.app, 'estado_actual') else {}
        if not rolls_actuales: rolls_actuales = {}

        ejes_radar = self.app.substats_db if hasattr(self.app, 'substats_db') else []
        num_ejes = len(ejes_radar)
        contenedor_radar_subs = ft.Container(visible=False)
        
        if num_ejes > 0:
            canvas_size_radar = 200
            center_r = canvas_size_radar / 2
            radio_max_r = 65
            radio_min_r = 12 
            radio_disp_r = radio_max_r - radio_min_r
            
            max_rolls = 1
            for k, v in rolls_actuales.items():
                if v > max_rolls: max_rolls = v
            max_val_radar = max(max_rolls, 5) 
            
            shapes_r = []
            
            for r_step in [0.33, 0.66, 1.0]:
                r_cur = radio_min_r + (radio_disp_r * r_step)
                path_bg = cv.Path(paint=ft.Paint(style=ft.PaintingStyle.STROKE, color=ft.Colors.WHITE12))
                for i in range(num_ejes):
                    ang = (math.pi * 2 * i / num_ejes) - (math.pi / 2)
                    x = center_r + r_cur * math.cos(ang)
                    y = center_r + r_cur * math.sin(ang)
                    if i == 0: path_bg.elements.append(cv.Path.MoveTo(x, y))
                    else: path_bg.elements.append(cv.Path.LineTo(x, y))
                path_bg.elements.append(cv.Path.Close())
                shapes_r.append(path_bg)
                
            puntos_ideal = []
            puntos_decente = []
            puntos_basura = []
            puntos_zero = []
            zonas_hover = []
            
            label_map = {
                "Ataque_plano": "ATK", "Ataque_porcentual": "ATK%",
                "Puntos_Vida_plano": "HP", "Puntos_Vida_porcentual": "HP%",
                "Defensa_plano": "DEF", "Defensa_porcentual": "DEF%",
                "Perforación_Plana_plano": "PEN", "Maestría_Anomalía_plano": "AP",
                "Probabilidad_crítico_porcentual": "CR%", "Daño_crítico_porcentual": "CD%"
            }
            
            for i in range(num_ejes):
                item = ejes_radar[i]
                key_ui = item['unique_key']
                lbl = label_map.get(key_ui, item.get('key_interna', key_ui)[:4])
                
                val = rolls_actuales.get(key_ui, 0)
                simular_porcentaje = "0%" if "porcentual" in key_ui else "0"
                key_limpia = limpiar_nombre_stat(key_ui, simular_porcentaje).lower()
                
                is_ideal = key_limpia in stats_ideales
                is_decente = key_limpia in stats_decentes and not is_ideal
                is_basura = not is_ideal and not is_decente
                
                ang = (math.pi * 2 * i / num_ejes) - (math.pi / 2)
                
                x_edge = center_r + radio_max_r * math.cos(ang)
                y_edge = center_r + radio_max_r * math.sin(ang)
                shapes_r.append(cv.Path(elements=[cv.Path.MoveTo(center_r, center_r), cv.Path.LineTo(x_edge, y_edge)], paint=ft.Paint(style=ft.PaintingStyle.STROKE, color="outline")))
                
                x_text = center_r + (radio_max_r + 20) * math.cos(ang)
                y_text = center_r + (radio_max_r + 14) * math.sin(ang)
                
                color_label = ft.Colors.AMBER_400 if is_ideal else ("primary" if is_decente else ft.Colors.GREY_500)
                shapes_r.append(cv.Text(x_text, y_text, text=lbl, style=ft.TextStyle(size=10, color=color_label, weight=ft.FontWeight.BOLD), alignment=ft.alignment.center))
                
                pct = min(val / max_val_radar, 1.0)
                
                px_zero = center_r + radio_min_r * math.cos(ang)
                py_zero = center_r + radio_min_r * math.sin(ang)
                puntos_zero.append((px_zero, py_zero))
                
                px_val = center_r + (radio_min_r + radio_disp_r * pct) * math.cos(ang)
                py_val = center_r + (radio_min_r + radio_disp_r * pct) * math.sin(ang)
                
                puntos_ideal.append((px_val, py_val) if is_ideal else (px_zero, py_zero))
                puntos_decente.append((px_val, py_val) if is_decente else (px_zero, py_zero))
                puntos_basura.append((px_val, py_val) if is_basura else (px_zero, py_zero))
                
                if val > 0:
                    zonas_hover.append(
                        ft.Container(
                            width=24, height=24, left=px_val-12, top=py_val-12,
                            tooltip=ft.Tooltip(message=f"{item.get('label', lbl)}: {val} rolls", prefer_below=False),
                            bgcolor=ft.Colors.TRANSPARENT, shape=ft.BoxShape.CIRCLE
                        )
                    )

            def draw_poly(puntos, color):
                tiene_datos = False
                for idx, (px, py) in enumerate(puntos):
                    if abs(px - puntos_zero[idx][0]) > 0.5 or abs(py - puntos_zero[idx][1]) > 0.5:
                        tiene_datos = True
                        break
                        
                if tiene_datos:
                    el_path = [cv.Path.MoveTo(puntos[0][0], puntos[0][1])] + [cv.Path.LineTo(x, y) for x, y in puntos[1:]] + [cv.Path.Close()]
                    shapes_r.append(cv.Path(elements=el_path, paint=ft.Paint(color=ft.Colors.with_opacity(0.4, color), style=ft.PaintingStyle.FILL)))
                    shapes_r.append(cv.Path(elements=el_path, paint=ft.Paint(color=color, stroke_width=2, style=ft.PaintingStyle.STROKE)))
                    for idx, (px, py) in enumerate(puntos):
                        if abs(px - puntos_zero[idx][0]) > 0.5 or abs(py - puntos_zero[idx][1]) > 0.5:
                            shapes_r.append(cv.Circle(px, py, 3, ft.Paint(color=ft.Colors.WHITE)))

            draw_poly(puntos_basura, ft.Colors.GREY_500)
            draw_poly(puntos_decente, "primary")
            draw_poly(puntos_ideal, ft.Colors.AMBER_400)
            
            stack_radar_subs = ft.Stack(
                controls=[cv.Canvas(shapes=shapes_r, width=canvas_size_radar, height=canvas_size_radar)] + zonas_hover,
                width=canvas_size_radar, height=canvas_size_radar
            )
            
            contenedor_radar_subs = ft.Container(
                width=240, padding=15, bgcolor="surface", border_radius=12, border=ft.border.all(1, "outline"),
                content=ft.Column([
                    ft.Text(self.i18n.t("ui.tab_recomendaciones_visual.radar_rolls"), size=self.FS['md'], weight="bold", color="primary", text_align=ft.TextAlign.CENTER),
                    ft.Container(content=stack_radar_subs, alignment=ft.alignment.center)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            )

        columna_rolls_azules = ft.Column([
            ft.Container(
                width=220,
                padding=ft.padding.all(16),
                bgcolor="surface",
                border_radius=12,
                border=ft.border.all(1, "outline"),
                shadow=ft.BoxShadow(blur_radius=12, spread_radius=0,
                                    color=ft.Colors.BLACK26, offset=ft.Offset(0, 3)),
                content=ft.Column([
                    ft.Text(self.i18n.t("ui.tab_recomendaciones_visual.substats_totales"),
                            size=self.FS['md'], weight="bold", color="primary"),
                    ft.Divider(height=8, color="outline"),
                    ft.Row([
                        ft.Icon(ft.Icons.STAR, color=ft.Colors.AMBER_400, size=18),
                        ft.Text(f"{total_ideal} {self.i18n.t('ui.tab_recomendaciones_visual.ideal')}",
                                size=14)
                    ], spacing=8),
                    ft.Row([
                        ft.Icon(ft.Icons.CHECK_CIRCLE, color="primary", size=18),
                        ft.Text(f"{total_decente} {self.i18n.t('ui.tab_recomendaciones_visual.decente')}",
                                size=14)
                    ], spacing=8),
                    ft.Row([
                        ft.Icon(ft.Icons.DELETE, color="secondary", size=18),
                        ft.Text(f"{total_basura} {self.i18n.t('ui.tab_recomendaciones_visual.malos')}",
                                size=14)
                    ], spacing=8),
                ], spacing=8)
            ),
            ft.Container(
                width=220,
                padding=ft.padding.all(16),
                bgcolor="surface",
                border_radius=12,
                border=ft.border.all(1, "outline"),
                shadow=ft.BoxShadow(blur_radius=12, spread_radius=0,
                                    color=ft.Colors.BLACK26, offset=ft.Offset(0, 3)),
                content=ft.Column([
                    ft.Text(self.i18n.t("ui.tab_recomendaciones_visual.evaluacion_substats"),
                            size=self.FS['md'], weight="bold", color="primary"),
                    ft.Container(height=4),
                    ft.ProgressBar(value=calidad_pct / 100, color=color_calidad,
                                   bgcolor="surface", height=10, border_radius=5),
                    ft.Text(f"{calidad_dinamica_pct:.1f} / 100", size=22, weight="bold",
                            color=color_calidad, text_align="center"),
                    ft.Row([
                        ft.Text(
                            f"{self.i18n.t('ui.tab_recomendaciones_visual.calidad_dinamica', default='Dynamic')}: {calidad_dinamica_pct:.1f}",
                            size=11,
                            color=color_calidad,
                            weight="bold",
                        ),
                        ft.Text(
                            f"{self.i18n.t('ui.tab_recomendaciones_visual.calidad_clasica', default='Classic')}: {calidad_clasica_pct:.1f}",
                            size=11,
                            color="on_surface_variant",
                        ),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                ], spacing=8, alignment=ft.MainAxisAlignment.CENTER)
            ),
            ft.Container(
                content=contenedor_top_armas,
                shadow=ft.BoxShadow(blur_radius=10, spread_radius=0,
                                    color=ft.Colors.BLACK26, offset=ft.Offset(0, 2)),
                border_radius=12,
                visible=bool(top_armas_ui)
            ),
            contenedor_radar_subs
        ], spacing=14, alignment=ft.MainAxisAlignment.CENTER)

        columna_izquierda_perfil = ft.Column([
            columna_imagen_agente,
            ft.Container(height=12),
            columna_rolls_azules
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)

        _tier_activo = [None]

        def _construir_col_discos(slots, lado):
            if not proj_final or not proj_final.get("encabezado"):
                return ft.Container(visible=False)

            def _mk_mini_disco(slot_num):
                tier_pct = _tier_activo[0]
                if tier_pct is None:
                    return ft.Container(visible=False)
                tier_colors = {100: "primary", 90: "secondary", 80: "tertiary"}
                cc = tier_colors.get(tier_pct, "primary")
                return _mk_disco_card(slot_num, tier_pct, cc)

            controles = [_mk_mini_disco(s) for s in slots]
            return ft.Column(controles, spacing=6, expand=True)

        col_discos_izq = _construir_col_discos([1, 2, 3], "izq")
        col_discos_der = _construir_col_discos([6, 5, 4], "der")

        def _fmt_disco(s):
            return self.i18n.t(f"substats.{s}", default=s.replace("_porcentual"," %").replace("_plano","").replace("_"," ").strip())

        def _cargar_disco_en_principal(slot_num, disco_info, tier_pct):
            """Reemplaza el disco del slot con el recomendado — borra todo y pone el ideal."""
            if not disco_info:
                return

            MAX_ROLLS_POR_SUB = 5
            main_ideal   = disco_info.get("main", "Ninguno")
            subs_ideales = disco_info.get("subs", {})
            disco_actual = self.app.estado_actual.discos_detalles[slot_num]

            disco_actual["main"] = main_ideal
            main_ctrl = self.app.gui.team_controls.get(f"disco_{slot_num}_main")
            if main_ctrl:
                main_ctrl.value = main_ideal
                if main_ctrl.page: main_ctrl.update()

            MAX_MEJORAS_DISCO = 5

            candidatos = sorted(
                [(s, min(r, MAX_ROLLS_POR_SUB)) for s, r in subs_ideales.items() if r > 0],
                key=lambda x: -x[1]
            )[:4]

            mejoras_repartidas = 0
            for sub_idx in range(1, 5):
                if sub_idx - 1 < len(candidatos):
                    stat_key, rolls_total = candidatos[sub_idx - 1]
                    mejoras_deseadas = max(0, rolls_total - 1)
                    mejoras = min(mejoras_deseadas, MAX_MEJORAS_DISCO - mejoras_repartidas)
                    mejoras_repartidas += mejoras
                else:
                    stat_key, mejoras = "Ninguno", 0

                disco_actual["subs"][sub_idx]["stat"]  = stat_key
                disco_actual["subs"][sub_idx]["rolls"] = mejoras

                stat_ctrl  = self.app.gui.team_controls.get(f"disco_{slot_num}_sub_{sub_idx}_stat")
                rolls_ctrl = self.app.gui.team_controls.get(f"disco_{slot_num}_sub_{sub_idx}_rolls")
                if stat_ctrl:
                    stat_ctrl.value = stat_key if stat_key != "Ninguno" else None
                    if stat_ctrl.page: stat_ctrl.update()
                if rolls_ctrl:
                    rolls_ctrl.value = str(mejoras)
                    if rolls_ctrl.page: rolls_ctrl.update()

            if hasattr(self.app, 'tabs_control'):
                self.app.tabs_control.selected_index = 0
                self.app.tabs_control.update()
            self.app.recalcular_stats_finales()

        def _mk_disco_card(slot_num, tier_pct, cc):

            """Construye una tarjeta visual de disco ideal para slot_num al tier_pct dado."""
            if not proj_final: return ft.Container(visible=False)
            disco_info = proj_final.get(f"discos_ideales_{tier_pct}", {}).get(slot_num)
            if not disco_info: return ft.Container(visible=False)

            _TIER_RANK = {
                "GODLIKE": 7, "FLAWLESS": 6, "GREAT": 5, "SOLID": 4,
                "DECENT": 3, "AVERAGE": 2, "MID": 1, "": 0
            }
            _calidad_actual = _calidad_discos_actuales.get(slot_num, "")
            _rank_actual    = _TIER_RANK.get(_calidad_actual, 0)
            _umbral = {100: _TIER_RANK["GODLIKE"], 90: _TIER_RANK["FLAWLESS"], 80: _TIER_RANK["GREAT"]}
            if _rank_actual >= _umbral.get(tier_pct, 0):
                return ft.Container(
                    padding=12, border_radius=12,
                    bgcolor="surface",
                    border=ft.border.all(1, "outline"),
                    margin=ft.margin.only(bottom=8),
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(ft.Icons.CHECK_CIRCLE, size=16, color="primary"),
                            ft.Text(
                                self.i18n.t("ui.tab_recomendaciones_visual.slot_ideal",
                                            default="Slot {slot}").replace("{slot}", str(slot_num)),
                                size=13, weight="bold", color="primary"
                            ),
                            ft.Text(_calidad_actual, size=11,
                                    color="secondary", italic=True),
                        ], spacing=6),
                        ft.Text(
                            self.i18n.t("ui.tab_recomendaciones_visual.todos_slots_perfectos",
                                        default="✓  Ya es óptimo para este tier."),
                            size=self.FS['xs'], color="secondary", italic=True
                        ),
                    ], spacing=4)
                )

            li = proj_final.get("lista_ideal", [])
            ld = proj_final.get("lista_decente", [])

            main = disco_info.get("main", "?")
            subs = disco_info.get("subs", {})

            lbl_ideal    = self.i18n.t("ui.tab_recomendaciones_visual.ideal_label",    default="Ideal")
            lbl_decente  = self.i18n.t("ui.tab_recomendaciones_visual.decente_label",  default="Útil")
            lbl_inev     = self.i18n.t("ui.tab_recomendaciones_visual.inevitable_label", default="Relleno")
            lbl_main     = self.i18n.t("ui.tab_recomendaciones_visual.main_label",     default="Main:")
            lbl_slot     = (self.i18n.t("ui.tab_recomendaciones_visual.slot_ideal",    default="Slot {slot}")
                            .replace("{slot}", str(slot_num)))

            filas_subs = []
            for s, rolls in sorted(subs.items(), key=lambda x: (-x[1], x[0])):
                if rolls == 0: continue
                es_i  = s in li
                es_d  = s in ld
                color = "tertiary" if es_i else ("primary" if es_d else "secondary")
                icon  = ft.Icons.STAR if es_i else (ft.Icons.CHECK_CIRCLE_OUTLINE if es_d else ft.Icons.REMOVE_CIRCLE_OUTLINE)
                lbl_cat = lbl_ideal if es_i else (lbl_decente if es_d else lbl_inev)
                val_unit  = valor_substat(s)
                val_total = val_unit * rolls
                val_str   = (f"+{val_total:.1f}%" if "_porcentual" in s
                             else f"+{int(val_total)}" if val_unit > 0 else "")
                upgrades = rolls - 1
                upgrade_badge = (
                    ft.Container(
                        padding=ft.padding.symmetric(horizontal=5, vertical=2),
                        bgcolor=ft.Colors.with_opacity(0.3, color),
                        border_radius=8,
                        content=ft.Text(
                            f"+{upgrades}",
                            size=11, color=ft.Colors.WHITE, weight="bold"
                        ),
                    ) if upgrades > 0 else ft.Container(width=0)
                )

                filas_subs.append(
                    ft.Container(
                        padding=ft.padding.symmetric(horizontal=8, vertical=6),
                        bgcolor="background",
                        border_radius=8,
                        border=ft.border.only(left=ft.BorderSide(2, color)),
                        content=ft.Row([
                            ft.Icon(icon, size=15, color=color),
                            ft.Text(_fmt_disco(s), size=12, color=ft.Colors.WHITE,
                                    weight="bold", expand=True, no_wrap=False),
                            upgrade_badge,
                            ft.Text(val_str, size=11, color=color,
                                    weight="bold"),
                        ], spacing=6, vertical_alignment=ft.CrossAxisAlignment.CENTER)
                    )
                )

            has_ideals = any(s in li for s in subs if subs.get(s,0) > 0)
            card_bg = "primary" if has_ideals else "secondary"

            aumento_tier = proj_final.get("aumento_pct", 0)
            total_rolls_ideal = sum(
                sum(v for v in proj_final.get(f"discos_ideales_{tier_pct}", {}).get(s, {}).get("subs", {}).values())
                for s in range(1, 7)
            )
            rolls_este_slot = sum(subs.values())
            if total_rolls_ideal > 0 and rolls_este_slot > 0:
                aumento_slot = aumento_tier * rolls_este_slot / total_rolls_ideal
            else:
                aumento_slot = 0

            pct_badge = ft.Container(
                padding=ft.padding.symmetric(horizontal=6, vertical=2),
                bgcolor=ft.Colors.with_opacity(0.2, cc),
                border_radius=8,
                content=ft.Text(
                    f"+{aumento_slot:.1f}%",
                    size=11, color=cc, weight="bold"
                ),
                tooltip=self.i18n.t(
                    "ui.tab_recomendaciones_visual.ganancia_estimada",
                    default="Estimated gain equipping this disc (tier total: +{aumento}%)"
                ).replace("{aumento}", f"{aumento_tier:.1f}"),
                visible=aumento_slot > 0.05,
            )

            btn_cargar = ft.IconButton(
                icon=ft.Icons.UPLOAD_ROUNDED,
                icon_size=16,
                icon_color=cc,
                tooltip=self.i18n.t(
                    "ui.tab_recomendaciones_visual.cargar_en_slot",
                    default="Load into Slot {slot} of main DPS"
                ).replace("{slot}", str(slot_num)),
                padding=ft.padding.all(2),
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=6)),
                on_click=lambda e, sn=slot_num, di=disco_info, tp=tier_pct:
                    _cargar_disco_en_principal(sn, di, tp),
            )

            return ft.Container(
                padding=12, border_radius=12,
                bgcolor="surface",
                border=ft.border.all(1, cc),
                margin=ft.margin.only(bottom=8),
                shadow=ft.BoxShadow(blur_radius=14, spread_radius=0, color=ft.Colors.with_opacity(0.4, cc), offset=ft.Offset(0, 3)),
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.ALBUM, size=16, color=cc),
                        ft.Text(lbl_slot, size=13, weight="bold", color=cc),
                        ft.Text(f"{lbl_main} {_fmt_disco(main)}", size=11,
                                color=ft.Colors.WHITE70, italic=True, expand=True),
                        pct_badge,
                        btn_cargar,
                    ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    ft.Divider(height=5, color=ft.Colors.with_opacity(0.3, cc)),
                    *filas_subs,
                ], spacing=6)
            )

        def _actualizar_cols_tier(tier_pct):
            _tier_activo[0] = tier_pct
            if not proj_final: return
            tier_colors = {100: "primary", 90: "secondary", 80: "tertiary"}
            cc = tier_colors.get(tier_pct, "primary")
            for col, slots in ((col_discos_izq, [1, 2, 3]), (col_discos_der, [6, 5, 4])):
                col.controls = [_mk_disco_card(s, tier_pct, cc) for s in slots]
                col.visible  = True
                col.expand   = True
                if col.page: col.update()

        elementos_inferiores = []

        if tarjeta_discos:
            elementos_inferiores.append(
                ft.Container(content=tarjeta_discos, expand=3,
                             alignment=ft.alignment.top_left)
            )

        elementos_inferiores.append(ft.Container(
            content=ft.Row([
                ft.Container(
                    content=col_discos_izq,
                    expand=2,
                    alignment=ft.alignment.top_right,
                    visible=bool(proj_final),
                    padding=ft.padding.only(right=8),
                ),
                ft.Container(
                    content=contenedor_hexagono,
                    alignment=ft.alignment.center,
                ),
                ft.Container(
                    content=col_discos_der,
                    expand=2,
                    alignment=ft.alignment.top_left,
                    visible=bool(proj_final),
                    padding=ft.padding.only(left=8),
                ),
            ], spacing=0, vertical_alignment=ft.CrossAxisAlignment.START),
            expand=True if not tarjeta_discos else 5,
            alignment=ft.alignment.center_left,
        ))

        fila_inferior = ft.Row(
            controls=elementos_inferiores,
            expand=True,
            vertical_alignment=ft.CrossAxisAlignment.START
        )

        # ── Panel derecho: recomendaciones + discos ───────────────
        columna_derecha_completa = ft.Column([
            ft.Container(
                content=contenedor_texto_recomm,
                padding=ft.padding.all(20),
                bgcolor="surface",
                border_radius=12,
                border=ft.border.all(1, "outline"),
                shadow=ft.BoxShadow(
                    blur_radius=16, spread_radius=0,
                    color=ft.Colors.BLACK26, offset=ft.Offset(0, 4)
                ),
                expand=True
            ),
            ft.Container(height=16),
            ft.Container(content=fila_inferior, expand=True)
        ], expand=True, spacing=0)

        fila_final = ft.Row([
            columna_izquierda_perfil,
            ft.VerticalDivider(width=0, color="transparent"),
            columna_derecha_completa
        ], expand=True, vertical_alignment=ft.CrossAxisAlignment.START)
        fila_final.data = {"actualizar_tier": _actualizar_cols_tier}
        return fila_final

    def create_recommendations_tab(self):
        import flet as ft
        from logica_recomendaciones import generar_recomendaciones_texto, CONFIG_ROLES, AnalistaBuild, EXCEPCIONES_AGENTES
        
        self.contenedor_principal_recomm = ft.Container(padding=20, expand=True)

        def construir_interfaz():

            nombre_agente = self.app.estado_actual.nombre_agente
            
            if not nombre_agente or nombre_agente == "Ninguno":
                return ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.PERSON_SEARCH, size=80, color="outline"),
                        ft.Text(self.i18n.t("ui.tab_recomendaciones.selecciona_agente"), size=self.FS['xl'], weight="bold", color="secondary"),
                        ft.Text(self.i18n.t("ui.tab_recomendaciones.para_ver_analisis"), color="secondary")
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER),
                    alignment=ft.alignment.center,
                    expand=True
                )

            datos_agente_local = None
            if hasattr(self.app, 'agentes_data') and self.app.agentes_data:
                datos_agente_local = next((a for a in self.app.agentes_data if a['Nombre'] == nombre_agente), None)
            if not datos_agente_local and hasattr(self.app, 'cargador') and hasattr(self.app.cargador, 'datos_agentes'):
                datos_agente_local = next((a for a in self.app.cargador.datos_agentes if a['Nombre'] == nombre_agente), None)

            if datos_agente_local:
                rol_agente = datos_agente_local.get("Tipo", "Atacante")
                elemento_agente = datos_agente_local.get("elemento") or datos_agente_local.get("Elemento") or "Físico"
                faccion_agente = datos_agente_local.get("Faccion", "") or datos_agente_local.get("Facción", "")
            else:
                rol_agente = "Atacante"
                elemento_agente = "Físico"
                faccion_agente = ""

            nombre_wengine_actual = self.app.estado_actual.nombre_wengine
            
            ruta_wengine_gui = None
            if hasattr(self, 'img_wengine') and self.img_wengine and self.img_wengine.src:
                ruta_wengine_gui = self.img_wengine.src

            datos_json_discos = []
            
            if hasattr(self, '_cache_discos_json') and self._cache_discos_json:
                nombre_cache = self._cache_discos_json.get("agente", "").lower().strip()
                nombre_actual = str(nombre_agente).lower().strip()
                if nombre_cache == nombre_actual:
                    datos_json_discos = self._cache_discos_json.get("discos", [])
            
            if not datos_json_discos and hasattr(self.app, 'datos_importados_temp') and self.app.datos_importados_temp:
                nombre_api = str(self.app.datos_importados_temp.get("name", "")).lower().strip()
                nombre_actual = str(nombre_agente).lower().strip()
                
                coincide_nombre = False
                if nombre_api and nombre_actual:
                    nombre_api_norm = nombre_api.replace(" ", "").replace("-", "").replace("_", "")
                    nombre_actual_norm = nombre_actual.replace(" ", "").replace("-", "").replace("_", "")
                    
                    if (nombre_api_norm in nombre_actual_norm or 
                        nombre_actual_norm in nombre_api_norm or
                        nombre_api_norm == nombre_actual_norm):
                        coincide_nombre = True
                
                tiene_discos = "discs" in self.app.datos_importados_temp and len(self.app.datos_importados_temp.get("discs", [])) > 0
                
                if coincide_nombre or tiene_discos:
                    datos_json_discos = self.app.datos_importados_temp.get("discs", [])

                    self._cache_discos_json = {
                        "agente": nombre_agente,
                        "discos": datos_json_discos
                    }
                    print(f"DEBUG: Discos cargados para {nombre_agente}: {len(datos_json_discos)} discos (CACHEADOS)")

 

            from logica_recomendaciones import AnalistaBuild, EXCEPCIONES_AGENTES, generar_recomendaciones_texto, CONFIG_ROLES
            
            analista = AnalistaBuild(traductor=self.i18n)
            stats_actuales = {k: float(v.value) for k, v in self.entry_vars.items() if v.value}
            
            equipo_en_pantalla = []
            if "sup1_agente" in self.team_controls and self.team_controls["sup1_agente"].value:
                equipo_en_pantalla.append(self.team_controls["sup1_agente"].value)
            if "sup2_agente" in self.team_controls and self.team_controls["sup2_agente"].value:
                equipo_en_pantalla.append(self.team_controls["sup2_agente"].value)
                
            enemigo_seleccionado = self.enemy_dropdown.value if self.enemy_dropdown.value else "Ninguno"

            etiqueta_rol_calc, consejos_calc = analista.analizar_build(
                self.app.estado_actual, 
                self.app.agentes_data, 
                elemento_agente,
                stats_finales=stats_actuales,
                equipo_actual=equipo_en_pantalla,
                enemigo_actual=enemigo_seleccionado
            )

            etiqueta_actual = "elemental" 
            if self.app.estado_actual.nombre_habilidad in self.app.habilidades_agente:
                etiqueta_leida = self.app.habilidades_agente[self.app.estado_actual.nombre_habilidad].get('Etiqueta_Dano', 'elemental')
                etiqueta_actual = "elemental" if etiqueta_leida == "normal" else etiqueta_leida
                
            tipo_evaluacion = "normal" 

            if rol_agente in ["Anomalo", "Anomalía"]:
                tipo_evaluacion = "anomalia"
                etiqueta_actual = "anomalia"
            elif rol_agente == "Ruptura":
                tipo_evaluacion = "sheer"
                etiqueta_actual = "sheer"

            if nombre_agente in EXCEPCIONES_AGENTES:
                excep = EXCEPCIONES_AGENTES[nombre_agente]
                if "etiqueta_dano" in excep:
                    etiqueta_actual = excep["etiqueta_dano"]

                meta_cfg = excep.get("meta_dano", "general").lower()
                if meta_cfg in ["anomalia", "anomalía"]:
                    etiqueta_actual = "anomalia"
                    tipo_evaluacion = "anomalia"
                elif meta_cfg == "sheer":
                    etiqueta_actual = "sheer"
                    tipo_evaluacion = "sheer"
                elif meta_cfg in ["general", "normal"]:
                    tipo_evaluacion = "normal"
                    
            def formatear_stats_completas(s_dict):
                if not s_dict: return " (Sin datos)"
                _t = self.i18n.t
                atk = int(s_dict.get('Ataque', 0))
                cr = s_dict.get('Probabilidad_crítico', 0)
                cd = s_dict.get('Daño_crítico', 0)
                ap = s_dict.get('Maestría_Anomalía', 0) or s_dict.get('Maestria_Anomalia', 0)
                am = s_dict.get('Tasa_de_Anomalía', 0)
                pen_pct = s_dict.get('Tasa_de_Perforación', 0)
                pen_flat = s_dict.get('Perforación_Plana', 0)
                dmg = s_dict.get('Daño_elemental', 0)
                regen = s_dict.get('Recuperación_energía', 0)
                
                l1 = f"{_t('recom.stat_atk', default='ATK')}: {atk} | CR: {cr:.1f}% | CD: {cd:.1f}% | {_t('recom.stat_bono_dmg', default='DMG Bonus')}: {dmg:.1f}%"
                l2 = f"{_t('recom.stat_atk', default='ATK')}: {atk} | {_t('recom.stat_maestria', default='Anomaly Prof.')}: {int(ap)} | {_t('recom.stat_tasa_anom', default='Anomaly Mastery')}: {am:.1f}% | PEN: {pen_pct:.1f}% (+{int(pen_flat)}) | {_t('recom.stat_regen', default='Energy Regen')}: {regen:.1f}%"
                return f"\n  ↳ {l1}\n  ↳ {l2}"

            estado_enemigo = self.dd_estado_enemigo.value if hasattr(self, 'dd_estado_enemigo') and self.dd_estado_enemigo.value else "Normal"
            stacks_core = int(self.core_stacks_dropdown.value) if hasattr(self, 'core_stacks_dropdown') and self.core_stacks_dropdown.value else 0
            anomalia_aplicada = getattr(self, 'checkbox_anomalia', ft.Checkbox(value=False)).value

            kwargs_pasivas = {}
            if hasattr(self, 'controles_pasivas'):
                for key, control in self.controles_pasivas.items():
                    kwargs_pasivas[key] = control.value
            
            buffs_nodos_da = {}
            if hasattr(self, 'da_active_buffs') and hasattr(self, 'mapa_stats_da'):
                for stat_ui, valor in self.da_active_buffs.items():
                    clave_logica = self.mapa_stats_da.get(stat_ui, stat_ui)
                    buffs_nodos_da[clave_logica] = buffs_nodos_da.get(clave_logica, 0.0) + valor

            base_buffeada = getattr(self.app, 'stats_base_buffeadas', self.app.base_stats).copy()

            lista_sets_externos = []
            soportes_nombres = []
            wengines_soportes = []
            
            for prefijo in ["sup1", "sup2"]:
                if f"{prefijo}_agente" in self.team_controls:
                    n_agente_sup = self.team_controls[f"{prefijo}_agente"].value
                    n_arma_sup = self.team_controls.get(f"{prefijo}_wengine", ft.Dropdown()).value
                    
                    if n_agente_sup and n_agente_sup != "Ninguno":
                        soportes_nombres.append(n_agente_sup)
                        wengines_soportes.append(n_arma_sup)
                        
                        d_ag = next((a for a in self.app.agentes_data if a['Nombre'] == n_agente_sup), None)
                        
                        stats_soporte = {
                            "Ataque": self.app.gestor_stats._parse_valor(self.team_controls.get(f"{prefijo}_stat_atk").value),
                            "Puntos_de_Vida": self.app.gestor_stats._parse_valor(self.team_controls.get(f"{prefijo}_stat_hp").value),
                            "Probabilidad_de_crítico": self.app.gestor_stats._parse_valor(self.team_controls.get(f"{prefijo}_stat_crit_rate").value),
                            "Daño_crítico": self.app.gestor_stats._parse_valor(self.team_controls.get(f"{prefijo}_stat_crit_dmg").value),
                            "Tasa_de_Perforación": self.app.gestor_stats._parse_valor(self.team_controls.get(f"{prefijo}_stat_pen").value),
                            "Tasa_de_Anomalía": self.app.gestor_stats._parse_valor(self.team_controls.get(f"{prefijo}_stat_am").value),
                            "Recuperación_energía": self.app.gestor_stats._parse_valor(self.team_controls.get(f"{prefijo}_stat_er").value),
                            "Impacto": self.app.gestor_stats._parse_valor(self.team_controls.get(f"{prefijo}_stat_imp").value)
                        }
                        
                        try: ref_arma = int(self.team_controls.get(f"{prefijo}_wengine_ref", ft.Dropdown()).value)
                        except: ref_arma = 1
                        try: stacks_arma = int(self.team_controls.get(f"{prefijo}_wengine_stacks", ft.Dropdown()).value)
                        except: stacks_arma = 0
                        try: val_m = int(self.team_controls.get(f"{prefijo}_mindscape", ft.Dropdown()).value)
                        except: val_m = 0

                        lista_sets_externos.append({
                            "origen": prefijo,
                            "nombre_set": self.team_controls.get(f"{prefijo}_set4", ft.Dropdown()).value,
                            "nombre_agente": n_agente_sup,
                            "tipo_agente": d_ag.get("Tipo", "") if d_ag else "",
                            "elemento_agente": d_ag.get("Elemento", "") or d_ag.get("elemento", "") if d_ag else "",
                            "faccion_agente": d_ag.get("Faccion", "") or d_ag.get("Facción", "") if d_ag else "",
                            "nombre_arma": n_arma_sup,
                            "refinamiento_arma": ref_arma,
                            "stacks_arma": stacks_arma,
                            "stats": stats_soporte,
                            "mindscape": val_m
                        })

            mejor_build = self.app.optimizador.encontrar_mejor_build(
                estado_base=self.app.estado_actual,
                agente_data=datos_agente_local,
                stats_gui_reales=stats_actuales,
                elemento_input=elemento_agente,
                etiqueta_dano=etiqueta_actual,
                sets_externos=lista_sets_externos,
                estado_enemigo=estado_enemigo,
                stacks_core=stacks_core,
                faccion_agente=faccion_agente,
                anomalia_aplicada=anomalia_aplicada,
                base_stats=self.app.base_stats,
                soportes_nombres=soportes_nombres,
                wengines_soportes=wengines_soportes,
                buffs_nodos=buffs_nodos_da,
                wengine_db=self.app.wengine_data,
                sets_db=self.app.sets_data,
                discos_db=self.app.discos_data,
                substats_db=self.app.substats_db,
                **kwargs_pasivas
            )

            elementos_optimizacion = []
            eficiencia_wengine_actual = 100.0
            top_wengines_lista = []
            tarjeta_revision_discos = None

            MAPA_SETS_ID_LOCAL = {
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

            if mejor_build:
                s = mejor_build.get('stats', {})
                # Traducir nombres de sets
                def _tr_set(nombre):
                    return self.i18n.t(f"sets.{nombre}", default=nombre)
                _set4_raw = mejor_build.get('set4', '')
                _set2_raw = mejor_build.get('set2', '')
                texto_sets = f"{_tr_set(_set4_raw)} / {_tr_set(_set2_raw)}"
                # Traducir mains
                def _tr_stat(s):
                    return self.i18n.t(f"substats.{s}", default=s.replace("_porcentual", " %").replace("_plano", "").replace("_", " "))
                _m4 = _tr_stat(mejor_build.get('main_4', ''))
                _m5 = _tr_stat(mejor_build.get('main_5', ''))
                _m6 = _tr_stat(mejor_build.get('main_6', ''))
                texto_discos = f"IV: {_m4} | V: {_m5} | VI: {_m6}"
                
                stats_str = formatear_stats_completas(s)
                
                ranking_completo = mejor_build.get("ranking_completo", [])
                
                if ranking_completo:
                    top_1_score = ranking_completo[0]["score"]
                    armas_vistas = set()
                    
                    for res in ranking_completo:
                        arma_nombre = res["wengine"]
                        if arma_nombre not in armas_vistas:
                            armas_vistas.add(arma_nombre)
                            pct = (res["score"] / top_1_score) * 100 if top_1_score > 0 else 0
                            top_wengines_lista.append((arma_nombre, pct))
                            if len(top_wengines_lista) >= 4:
                                break
                    
                    self.app._ultimo_top_wengines = top_wengines_lista
                                
                    texto_wengine = " | ".join([f"{self.i18n.t(f'wengines.{w}', default=w)} ({pct:.0f}%)" for w, pct in top_wengines_lista])
                    
                    for res in ranking_completo:
                        if res["wengine"] == nombre_wengine_actual:
                            eficiencia_wengine_actual = (res["score"] / top_1_score) * 100 if top_1_score > 0 else 0
                            break
                else:
                    texto_wengine = mejor_build.get('wengine', 'Ninguno')
                    top_wengines_lista = [(texto_wengine, 100.0)]
                    self.app._ultimo_top_wengines = top_wengines_lista

                elementos_optimizacion.append(
                    ft.Container(
                        padding=10, bgcolor="background", border_radius=8,
                        border=ft.border.only(left=ft.BorderSide(4, "outline")),
                        content=ft.Column([
                            ft.Row([ft.Icon(ft.Icons.AUTO_AWESOME, color="secondary", size=18), ft.Text(self.i18n.t("ui.tab_recomendaciones.ranking_optimo"), weight="bold", color="secondary")]),
                            ft.Text(f"W-Engine: {texto_wengine}\nSets: {texto_sets}\n{self.i18n.t('ui.tab_recomendaciones.label_discos', default='Discs')}: {texto_discos}\n{self.i18n.t('ui.tab_recomendaciones.stats_finales')}:{stats_str}", size=13)
                        ], spacing=2),
                        margin=ft.margin.only(top=10)
                    )
                )

                try:
                    analisis_marginal = self.app.optimizador.analizar_valor_marginal_substats(
                        estado_base=self.app.estado_actual,
                        agente_data=datos_agente_local,
                        stats_gui_reales=stats_actuales,
                        elemento_input=elemento_agente,
                        sets_externos=lista_sets_externos,
                        estado_enemigo=estado_enemigo,
                        stacks_core=stacks_core,
                        faccion_agente=faccion_agente,
                        anomalia_aplicada=anomalia_aplicada,
                        base_stats=self.app.base_stats,
                        soportes_nombres=soportes_nombres,
                        wengines_soportes=wengines_soportes,
                        buffs_nodos=buffs_nodos_da,
                        wengine_db=self.app.wengine_data,
                        sets_db=self.app.sets_data,
                        discos_db=self.app.discos_data,
                        substats_db=self.app.substats_db,
                        **kwargs_pasivas
                    )
                except Exception as e:
                    print(f"Error en análisis marginal de substats: {e}")
                    analisis_marginal = None

                resultados_marginales = (analisis_marginal or {}).get("resultados", [])
                top_marginales = resultados_marginales[:4]
                filas_marginales = [
                    ft.Text(
                        self.i18n.t("ui.tab_recomendaciones.valor_marginal_desc"),
                        size=12,
                        color="on_surface_variant",
                    )
                ]

                if top_marginales:
                    for idx, res_marginal in enumerate(top_marginales, start=1):
                        stat_key = res_marginal.get("substat", "")
                        delta_pct = float(res_marginal.get("delta_pct", 0.0) or 0.0)
                        gain_txt = f"+{delta_pct:.2f}" if delta_pct >= 0 else f"{delta_pct:.2f}"
                        ubicaciones = res_marginal.get("ubicaciones", []) or []
                        slots_txt = ", ".join(str(u.get("slot")) for u in ubicaciones[:6] if u.get("slot"))
                        slots_txt = slots_txt or "-"
                        item_txt = (
                            self.i18n.t("ui.tab_recomendaciones.valor_marginal_item")
                            .replace("{stat}", _tr_stat(stat_key))
                            .replace("{gain}", gain_txt)
                        )
                        slots_label = (
                            self.i18n.t("ui.tab_recomendaciones.valor_marginal_slots")
                            .replace("{slots}", slots_txt)
                        )
                        filas_marginales.append(
                            ft.Container(
                                padding=8,
                                bgcolor="surface",
                                border_radius=6,
                                content=ft.Column([
                                    ft.Row([
                                        ft.Text(f"{idx}", size=12, weight="bold", color="primary"),
                                        ft.Text(item_txt, size=13, weight="bold", expand=True),
                                    ], spacing=8),
                                    ft.Text(slots_label, size=11, color="on_surface_variant"),
                                ], spacing=2),
                            )
                        )

                    top_delta = float(top_marginales[0].get("delta_pct", 0.0) or 0.0)
                    stat_top = _tr_stat(top_marginales[0].get("substat", ""))
                    atk_marginal = next(
                        (r for r in resultados_marginales if r.get("substat") == "Ataque_porcentual"),
                        None,
                    )
                    if (
                        atk_marginal
                        and top_marginales[0].get("substat") != "Ataque_porcentual"
                        and top_delta > 0
                        and float(atk_marginal.get("delta_pct", 0.0) or 0.0) <= top_delta * 0.7
                    ):
                        filas_marginales.append(
                            ft.Row([
                                ft.Icon(ft.Icons.INFO_OUTLINE, size=16, color="tertiary"),
                                ft.Text(
                                    self.i18n.t("ui.tab_recomendaciones.valor_marginal_atk_saturado")
                                    .replace("{stat}", stat_top),
                                    size=12,
                                    color="tertiary",
                                    expand=True,
                                ),
                            ], spacing=6)
                        )

                    rolls_actuales_marginal = getattr(self.app.estado_actual, "substats_counts", {}) or {}
                    mejor_substat = top_marginales[0].get("substat", "")
                    reemplazo_candidato = next(
                        (
                            r for r in resultados_marginales
                            if rolls_actuales_marginal.get(r.get("substat", ""), 0) > 0
                            and r.get("substat") != mejor_substat
                            and top_delta > 0
                            and float(r.get("delta_pct", 0.0) or 0.0) <= top_delta * 0.70
                        ),
                        None,
                    )
                    if reemplazo_candidato:
                        slots_mejor = ", ".join(
                            str(u.get("slot"))
                            for u in (top_marginales[0].get("ubicaciones", []) or [])[:6]
                            if u.get("slot")
                        ) or "-"
                        reemplazo_txt = (
                            self.i18n.t("ui.tab_recomendaciones.valor_marginal_reemplazo")
                            .replace("{from_stat}", _tr_stat(reemplazo_candidato.get("substat", "")))
                            .replace("{to_stat}", _tr_stat(mejor_substat))
                            .replace("{slots}", slots_mejor)
                        )
                        filas_marginales.append(
                            ft.Row([
                                ft.Icon(ft.Icons.SWAP_HORIZ, size=16, color="primary"),
                                ft.Text(reemplazo_txt, size=12, color="primary", expand=True),
                            ], spacing=6)
                        )

                    stat_cap = next(
                        (r for r in top_marginales if float(r.get("delta_pct", 0.0) or 0.0) <= 0.05),
                        None,
                    )
                    if stat_cap:
                        filas_marginales.append(
                            ft.Row([
                                ft.Icon(ft.Icons.WARNING_AMBER, size=16, color="outline"),
                                ft.Text(
                                    self.i18n.t("ui.tab_recomendaciones.valor_marginal_stat_cap")
                                    .replace("{stat}", _tr_stat(stat_cap.get("substat", ""))),
                                    size=12,
                                    color="outline",
                                    expand=True,
                                ),
                            ], spacing=6)
                        )
                else:
                    filas_marginales.append(
                        ft.Text(
                            self.i18n.t("ui.tab_recomendaciones.valor_marginal_sin_resultados"),
                            size=12,
                            color="on_surface_variant",
                        )
                    )

                elementos_optimizacion.append(
                    ft.Container(
                        padding=10,
                        bgcolor="background",
                        border_radius=8,
                        border=ft.border.only(left=ft.BorderSide(4, "primary")),
                        content=ft.Column([
                            ft.Row([
                                ft.Icon(ft.Icons.TRENDING_UP, color="primary", size=18),
                                ft.Text(
                                    self.i18n.t("ui.tab_recomendaciones.valor_marginal_titulo"),
                                    weight="bold",
                                    color="primary",
                                ),
                            ], spacing=6),
                            *filas_marginales,
                        ], spacing=6),
                        margin=ft.margin.only(top=10),
                    )
                )

                _exc_ag = EXCEPCIONES_AGENTES.get(nombre_agente, {})
                _sets_ag = _exc_ag.get("sets", {})
                _sets_ideales_ag    = _sets_ag.get("ideal", []) or _sets_ag.get("4pc", [])
                _sets_funcionales_ag = _sets_ag.get("funcional", []) or _sets_ag.get("2pc", [])
                if not _sets_ideales_ag:
                    from logica_recomendaciones import CONFIG_SETS_ROLES
                    _sr = CONFIG_SETS_ROLES.get(rol_agente, {})
                    _sets_ideales_ag    = _sr.get("ideal", [])
                    _sets_funcionales_ag = _sr.get("funcional", [])

                _todos_sets = list(dict.fromkeys(_sets_ideales_ag))
                _set4_activo = [mejor_build.get("set4", _todos_sets[0] if _todos_sets else "Ninguno")]
                _set2_activo = [mejor_build.get("set2", "Ninguno")]

                def _recalcular_con_set(set4_nombre):
                    try:
                        return self.app.optimizador.simular_proyeccion_realista(
                            mejor_config=mejor_build,
                            elemento=elemento_agente,
                            delta_stats=None,
                            rol_agente=rol_agente,
                            nombre_agente=nombre_agente,
                            estado_base=self.app.estado_actual,
                            min_basura=1,
                            etiqueta_dano=etiqueta_actual,
                            ranking_completo=mejor_build.get("ranking_completo", []),
                            base_stats=self.app.base_stats,
                            set4_override=set4_nombre,
                            set2_override=_set2_activo[0],
                        )
                    except Exception as e:
                        print(f"Error en proyección con set {set4_nombre}: {e}")
                        return {}

                try:
                    proj_final = self.app.optimizador.simular_proyeccion_realista(
                        mejor_config=mejor_build,
                        elemento=elemento_agente,
                        delta_stats=None,
                        rol_agente=rol_agente,
                        nombre_agente=nombre_agente,
                        estado_base=self.app.estado_actual,
                        min_basura=1,
                        etiqueta_dano=etiqueta_actual,
                        ranking_completo=mejor_build.get("ranking_completo", []),
                        base_stats=self.app.base_stats,
                    )
                except Exception as e:
                    print(f"Error en proyección: {e}")
                    proj_final = {}
                
                if proj_final and proj_final.get("encabezado"):
                    aumento = proj_final.get("aumento_pct", 0)
                    titulo_bloque = (
                        self.i18n.t("ui.tab_recomendaciones.stats_ideales_potencial",
                                    default=f"Ideal Stats (+{aumento:.1f}% DAMAGE POTENTIAL)"
                                    ).replace("{aumento}", f"{aumento:.1f}")
                        if aumento > 0
                        else self.i18n.t("ui.tab_recomendaciones.stats_ideales_build_optima",
                                         default="Theoretical Ideal Stats (Optimal Build)")
                    )

                    _tier_colors = {100: "primary", 90: "secondary", 80: "tertiary"}
                    _tier_icons  = {100: ft.Icons.DIAMOND, 90: ft.Icons.STAR, 80: ft.Icons.THUMB_UP}
                    _tier_nombres_loc = {
                        100: self.i18n.t("ui.tab_recomendaciones.tier_perfecto",  default="100% — Perfect"),
                        90:  self.i18n.t("ui.tab_recomendaciones.tier_excelente", default="90% — Excellent"),
                        80:  self.i18n.t("ui.tab_recomendaciones.tier_bueno",     default="80% — Good"),
                    }

                    li_e  = proj_final.get("lista_ideal", [])
                    ld_e  = proj_final.get("lista_decente", [])
                    lb_e  = proj_final.get("lista_basura", [])
                    mc_e  = proj_final.get("mains_config", {})
                    rj_e  = getattr(self.app.estado_actual, "substats_counts", {}) or {}

                    tier_data_e = [
                        (100, proj_final.get("texto_rolls_100",""), proj_final.get("stats_str_100",""),
                         proj_final.get("resumen_rolls_100",{})),
                        (90,  proj_final.get("texto_rolls_90",""),  proj_final.get("stats_str_90",""),
                         proj_final.get("resumen_rolls_90",{})),
                        (80,  proj_final.get("texto_rolls_80",""),  proj_final.get("stats_str_80",""),
                         proj_final.get("resumen_rolls_80",{})),
                    ]

                    def _mk_tier_card_elem(tc, tr, ts, rd):
                        cc      = _tier_colors[tc]
                        ti      = _tier_icons[tc]
                        nom     = _tier_nombres_loc[tc]
                        btn_lbl = self.i18n.t("ui.tab_recomendaciones.ver_ruta_tier",
                                              default=f"View path for {nom} →"
                                              ).replace("{tier}", nom)

                        def _on_btn(e, _tc=tc, _cc=cc):
                            if hasattr(panel_completo, "data") and panel_completo.data:
                                upd = panel_completo.data.get("actualizar_tier")
                                if upd: upd(_tc)
                            self.app.page.update()

                        _stats_raw = tr + "\n\n" + ts
                        stats_lines = [
                            ft.Text(line, size=12, color="on_surface_variant", selectable=True)
                            for line in _stats_raw.split("\n") if line.strip()
                        ]

                        return ft.Container(
                            expand=1, padding=12, border_radius=12, bgcolor="surface",
                            border=ft.border.all(2, cc),
                            content=ft.Column([
                                ft.Row([
                                    ft.Icon(ti, size=16, color=cc),
                                    ft.Text(nom, size=14, weight="bold", color=cc),
                                ], spacing=6),
                                ft.Divider(height=4, color=ft.Colors.with_opacity(0.3, cc)),
                                ft.Column(stats_lines, spacing=1, tight=True),
                                ft.ElevatedButton(
                                    text=btn_lbl, icon=ft.Icons.ROUTE, height=34,
                                    on_click=_on_btn,
                                    style=ft.ButtonStyle(
                                        color=ft.Colors.WHITE, bgcolor=cc,
                                        padding=ft.padding.symmetric(horizontal=10, vertical=6),
                                    ),
                                ),
                            ], spacing=8)
                        )

                    # ── Selector de set ──────────────────────────────────────────
                    _col_tier_cards = ft.Ref[ft.Row]()
                    _col_overcap    = ft.Ref[ft.Column]()
                    _col_encabezado = ft.Ref[ft.Text]()

                    def _mk_tier_row(pf):
                        td = [
                            (100, pf.get("texto_rolls_100",""), pf.get("stats_str_100",""), pf.get("resumen_rolls_100",{})),
                            (90,  pf.get("texto_rolls_90",""),  pf.get("stats_str_90",""),  pf.get("resumen_rolls_90",{})),
                            (80,  pf.get("texto_rolls_80",""),  pf.get("stats_str_80",""),  pf.get("resumen_rolls_80",{})),
                        ]
                        return ft.Row([
                            _mk_tier_card_elem(tc, tr, ts, rd) for tc, tr, ts, rd in td
                        ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.START,
                           ref=_col_tier_cards)

                    def _mk_overcap_row(pf):
                        warns = pf.get("overcap_warnings", {})
                        if not warns:
                            return ft.Column([], visible=False, ref=_col_overcap)
                        items = []
                        for stat, info in warns.items():
                            nom = stat.replace("_", " ")
                            items.append(ft.Row([
                                ft.Icon(ft.Icons.WARNING_AMBER, size=14, color=ft.Colors.AMBER_400),
                                ft.Text(
                                    f"⚠ Prob. Crítica en combate: {info['valor']:.1f}% > {info['cap']:.0f}% cap "
                                    f"— {info.get('rolls_desperdiciados', 0)} rolls de CRIT desperdiciados",
                                    size=11, color=ft.Colors.AMBER_300
                                ),
                            ], spacing=4))
                        return ft.Column(items, spacing=3, ref=_col_overcap)

                    _tier_row_ctrl  = _mk_tier_row(proj_final)
                    _overcap_ctrl   = _mk_overcap_row(proj_final)
                    _encabezado_txt = ft.Text(proj_final.get("encabezado",""), size=12,
                                             color="on_surface_variant")

                    _set_selector_ctrl = ft.Container(visible=False)
                    if len(_todos_sets) > 1:
                        set_opts = []
                        for s in _todos_sets:
                            s_clean = s[0] if isinstance(s, tuple) else s
                            s_trad = _tr_set(s_clean)
                            lbl = f"⭐ {s_trad}" if s_clean in [
                                x[0] if isinstance(x, tuple) else x for x in _sets_ideales_ag
                            ] else f"◎ {s_trad}"
                            set_opts.append(ft.dropdown.Option(key=s_clean, text=lbl))

                        def _on_set_change(e,
                                           _enc=_encabezado_txt,
                                           _tr=_tier_row_ctrl,
                                           _oc=_overcap_ctrl):
                            nuevo_set = e.control.value
                            _set4_activo[0] = nuevo_set
                            pf_nuevo = _recalcular_con_set(nuevo_set)
                            if not pf_nuevo: return
                            _enc.value = pf_nuevo.get("encabezado", "")
                            td_nuevo = [
                                (100, pf_nuevo.get("texto_rolls_100",""), pf_nuevo.get("stats_str_100",""), pf_nuevo.get("resumen_rolls_100",{})),
                                (90,  pf_nuevo.get("texto_rolls_90",""),  pf_nuevo.get("stats_str_90",""),  pf_nuevo.get("resumen_rolls_90",{})),
                                (80,  pf_nuevo.get("texto_rolls_80",""),  pf_nuevo.get("stats_str_80",""),  pf_nuevo.get("resumen_rolls_80",{})),
                            ]
                            _tr.controls = [_mk_tier_card_elem(tc, tr, ts, rd) for tc, tr, ts, rd in td_nuevo]
                            warns = pf_nuevo.get("overcap_warnings", {})
                            oc_items = []
                            for stat, info in warns.items():
                                nom = stat.replace("_", " ")
                                oc_items.append(ft.Row([
                                    ft.Icon(ft.Icons.WARNING_AMBER, size=14, color=ft.Colors.AMBER_400),
                                    ft.Text(
                                        f"Overcap {nom}: {info['valor']:.1f}% > {info['cap']:.0f}% "
                                        f"(+{info['exceso']:.1f}% desperdiciado)",
                                        size=11, color=ft.Colors.AMBER_300
                                    ),
                                ], spacing=4))
                            _oc.controls = oc_items
                            _oc.visible  = bool(oc_items)
                            self.app.page.update()

                        set_actual_clean = _set4_activo[0][0] if isinstance(_set4_activo[0], tuple) else _set4_activo[0]
                        _set_selector_ctrl = ft.Row([
                            ft.Icon(ft.Icons.STYLE, size=14, color="primary"),
                            ft.Text("Set 4pc:", size=12, color="secondary", weight="bold"),
                            ft.Dropdown(
                                options=set_opts,
                                value=set_actual_clean,
                                on_change=_on_set_change,
                                width=220,
                                dense=True,
                                text_size=12,
                                content_padding=ft.padding.symmetric(horizontal=10, vertical=4),
                            ),
                        ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER,
                           visible=True)

                    elementos_optimizacion.append(
                        ft.Container(
                            padding=14, bgcolor="background", border_radius=12,
                            border=ft.border.only(left=ft.BorderSide(5, "primary")),
                            content=ft.Column([
                                ft.Row([
                                    ft.Icon(ft.Icons.AUTO_FIX_HIGH, color="primary", size=20),
                                    ft.Text(titulo_bloque, weight="bold", color="primary", size=15),
                                ]),
                                _encabezado_txt,
                                _set_selector_ctrl,
                                _overcap_ctrl,
                                ft.Divider(height=6, color="outline"),
                                _tier_row_ctrl,
                            ], spacing=8),
                            margin=ft.margin.only(top=10)
                        )
                    )

                tarjeta_revision_discos = None


                if datos_json_discos:
                    config_rol_temp = CONFIG_ROLES.get(rol_agente, CONFIG_ROLES["Atacante"]).copy()
                    sets_ideales = []
                    sets_funcionales = []
                    
                    if nombre_agente in EXCEPCIONES_AGENTES:
                        excep = EXCEPCIONES_AGENTES[nombre_agente]
                        if "subs" in excep: config_rol_temp["subs"] = excep["subs"]
                        if "main_4" in excep: config_rol_temp["main_4"] = excep["main_4"]
                        if "main_5" in excep: config_rol_temp["main_5"] = excep["main_5"]
                        if "main_6" in excep: config_rol_temp["main_6"] = excep["main_6"]
                        if "sets" in excep:
                            sets_ideales = excep["sets"].get("ideal", [])
                            sets_funcionales = excep["sets"].get("funcional", [])
                            
                    MAPA_STATS_TRADUCCION = {
                        "HP": "Puntos de Vida", "ATK": "Ataque", "DEF": "Defensa", 
                        "Percent HP": "Puntos de Vida %", "Percent ATK": "Ataque %", "Percent DEF": "Defensa %",
                        "CRIT Rate": "Prob. Crítica", "CRIT DMG": "Daño Crítico", 
                        "PEN Ratio": "Perforación %", "Anomaly Proficiency": "Maestría Anom.",
                        "Anomaly Mastery": "Tasa Anom.", "Energy Regen": "Recup. Energía",
                        "Physical DMG Bonus": "Daño Físico", "Fire DMG Bonus": "Daño Fuego",
                        "Ice DMG Bonus": "Daño Hielo", "Electric DMG Bonus": "Daño Eléctrico",
                        "Ether DMG Bonus": "Daño Etéreo", "Impact": "Impacto", "PEN": "Perforación Plana"
                    }

                    def normalizar_para_analisis(key_sucia):
                        import unicodedata
                        k = str(key_sucia).lower().strip()
                        k = ''.join(c for c in unicodedata.normalize('NFD', k) if unicodedata.category(c) != 'Mn')
                        
                        es_pct = "%" in k or "porcentual" in k or "tasa" in k or "prob" in k or "dano" in k or "recup" in k or "ratio" in k or "percent" in k
                        sufijo = "_porcentual" if es_pct else "_plano"
                        
                        base = ''.join([i for i in k.replace("porcentual", "").replace("plano", "").replace("_", "").replace("%", "").replace("+", "") if not i.isdigit()]).strip()
                        
                        if "ataque" in base or "atk" in base or "attack" in base: return f"Ataque{sufijo}"
                        if "vida" in base or "hp" in base: return f"Puntos_Vida{sufijo}"
                        if "defensa" in base or "def" in base: return f"Defensa{sufijo}"
                        
                        if "anomal" in base or "maestria" in base or "prof" in base:
                            if "tasa" in base or "mastery" in base: return "Tasa_de_Anomalía"
                            return "Maestría_Anomalía"
                            
                        if "prob" in base or "rate" in base: return "Probabilidad_crítico"
                        
                        if "dano" in base and ("crit" in base or "dmg" in base): 
                            if not any(x in base for x in ["fisico", "fuego", "hielo", "electrico", "etereo", "elemental", "physical", "fire", "ice", "ether"]):
                                return "Daño_crítico"
                                
                        if "elemental" in base or "fisico" in base or "fuego" in base or "hielo" in base or "electrico" in base or "etereo" in base or "physical" in base or "fire" in base or "ice" in base or "ether" in base: 
                            return "Daño_elemental"
                            
                        if "pen" in base or "perf" in base:
                            if "ratio" in base or "tasa" in base or es_pct: return "Tasa_de_Perforación"
                            return "Perforación_Plana"
                            
                        if "recup" in base or "energy" in base or "regen" in base: return "Recuperación_energía"
                        if "impact" in base: return "Impacto"
                        
                        return "Desconocido"

                    base_combat_stats = self.app.gestor_stats.calcular_stats_finales(
                        base_stats=self.app.base_stats.copy(), estado_build=self.app.estado_actual,
                        wengine_db=self.app.wengine_data, sets_db=self.app.sets_data,
                        discos_db=self.app.discos_data, substats_db=self.app.substats_db,
                        elemento_agente=self.app.elemento, tipo_agente=self.app.tipo,
                        stacks_core=stacks_core, sets_externos=lista_sets_externos, 
                        estado_enemigo=estado_enemigo, buffs_nodos={}
                    )
                    base_combat_stats['Multiplicador_de_ataques'] = stats_actuales.get('Multiplicador_de_ataques', 100.0)
                    base_combat_stats['Aturdimiento'] = stats_actuales.get('Aturdimiento', 100.0)
                    base_combat_stats['Etiqueta_Dano'] = etiqueta_actual

                    def calc_dano_simulando_substat(stat_norm_key, rolls):
                        s_sim = base_combat_stats.copy()
                        
                        if rolls > 0 and stat_norm_key != "nada":
                            valor_por_roll = valor_substat(stat_norm_key)
                            mejora_total = valor_por_roll * rolls
                            
                            if "Probabilidad" in stat_norm_key: s_sim["Probabilidad_crítico"] = s_sim.get("Probabilidad_crítico", 0) + mejora_total
                            elif "Daño_crítico" in stat_norm_key: s_sim["Daño_crítico"] = s_sim.get("Daño_crítico", 0) + mejora_total
                            elif "Ataque_porcentual" in stat_norm_key:
                                atk_base = self.app.base_stats.get("Ataque", 800)
                                s_sim["Ataque"] = s_sim.get("Ataque", 0) + (atk_base * (mejora_total / 100.0))
                            elif "Ataque_plano" in stat_norm_key: s_sim["Ataque"] = s_sim.get("Ataque", 0) + mejora_total
                            elif "Maestría" in stat_norm_key: s_sim["Maestría_Anomalía"] = s_sim.get("Maestría_Anomalía", 0) + mejora_total
                            elif "Perforación_Plana" in stat_norm_key: s_sim["Perforación_Plana"] = s_sim.get("Perforación_Plana", 0) + mejora_total
                            elif "Tasa_de_Perforación" in stat_norm_key: s_sim["Tasa_de_Perforación"] = s_sim.get("Tasa_de_Perforación", 0) + mejora_total
                            elif "Recuperación_energía" in stat_norm_key: s_sim["Recuperación_energía"] = s_sim.get("Recuperación_energía", 0) + mejora_total
                            
                        d_norm, d_sheer, d_anom, _, _, _, _ = self.app.calcular_dano_simulado(s_sim, self.app.elemento)
                        if tipo_evaluacion == "anomalia": return d_anom
                        elif tipo_evaluacion == "sheer": return d_sheer
                        else: return d_norm

                    basura_norm = {normalizar_para_analisis(k) for k in config_rol_temp["subs"]["basura"]}
                    recomendaciones_organizadas = []

                    if mejor_build and nombre_wengine_actual != "Ninguno" and nombre_wengine_actual != mejor_build.get('wengine', ''):
                        arma_ideal = mejor_build.get('wengine', '')
                        diff_pct = 0
                        if top_wengines_lista:
                            for w, pct in top_wengines_lista:
                                if w == nombre_wengine_actual:
                                    diff_pct = 100 - pct
                                    break
                        txt_arma = self.i18n.t("ui.tab_recomendaciones.arma_suboptima").replace("{arma}", nombre_wengine_actual)
                        if diff_pct > 0: txt_arma += self.i18n.t("ui.tab_recomendaciones.perdiendo_eficiencia").replace("{pct}", f"{diff_pct:.1f}")
                        
                        tarjeta_arma = ft.Container(
                            padding=10, bgcolor="surface", border_radius=8, border=ft.border.only(left=ft.BorderSide(3, "tertiary")),
                            content=ft.Column([
                                ft.Row([ft.Icon(ft.Icons.FLASH_ON, color="amber", size=16), ft.Text(self.i18n.t("ui.tab_recomendaciones.cambio_wengine"), weight="bold", color="on_surface_variant", size=13)]),
                                ft.Text(txt_arma, color="tertiary", size=12),
                                ft.Text(self.i18n.t("ui.tab_recomendaciones.equipa_idealmente").replace("{arma}", arma_ideal), color="primary", size=self.FS['xs'], italic=True)
                            ], spacing=3)
                        )
                        recomendaciones_organizadas.append({"urgencia": 999, "ui": tarjeta_arma})

                    for d in sorted(datos_json_discos, key=lambda x: int(x.get("slot", 0))):
                        slot = int(d.get("slot", 0))
                        if slot < 1 or slot > 6: continue
                        
                        advertencias = []
                        urgencia_score = 0 

                        s_id = int(d.get("set_id", 0))
                        nombre_set_disco = MAPA_SETS_ID_LOCAL.get(s_id, d.get("brand", "Desconocido"))
                        
                        def norm_set(s): 
                            if isinstance(s, tuple): s = s[0]
                            return s.lower().replace(" ", "").replace("ó", "o").replace("é", "e").replace("á", "a").replace("í", "i")
                        
                        set_es_bueno = False
                        for s_ok in sets_ideales + sets_funcionales:
                            if norm_set(s_ok) in norm_set(nombre_set_disco) or norm_set(nombre_set_disco) in norm_set(s_ok):
                                set_es_bueno = True
                                break
                        if not set_es_bueno and nombre_set_disco != "Desconocido":
                            if sets_ideales:
                                s_pref = sets_ideales[0][0] if isinstance(sets_ideales[0], tuple) else sets_ideales[0]
                                advertencias.append(ft.Text(self.i18n.t("ui.tab_recomendaciones.set_incorrecto").replace("{set}", _tr_set(s_pref)), color="error", size=12))
                                urgencia_score += 40 

                        if slot == 1: main_stat_norm = "Puntos_Vida_plano"
                        elif slot == 2: main_stat_norm = "Ataque_plano"
                        elif slot == 3: main_stat_norm = "Defensa_plano"
                        else:
                            nombre_api_main = d.get("main_stat", {}).get("name", "")
                            main_stat_norm = normalizar_para_analisis(nombre_api_main)
                            
                            if main_stat_norm in ["Ataque_plano", "Defensa_plano", "Puntos_Vida_plano"]:
                                main_stat_norm = main_stat_norm.replace("_plano", "_porcentual")
                            
                            lista_mains_ok = config_rol_temp.get(f"main_{slot}", {}).get("general", [])
                            mains_aceptados = []
                            for s in lista_mains_ok + config_rol_temp.get(f"main_{slot}", {}).get("particular", []):
                                s_norm = normalizar_para_analisis(s)
                                if s_norm in ["Ataque_plano", "Defensa_plano", "Puntos_Vida_plano"]:
                                    s_norm = s_norm.replace("_plano", "_porcentual")
                                mains_aceptados.append(s_norm)

                            if main_stat_norm not in mains_aceptados and main_stat_norm != "Desconocido":
                                n_vis = MAPA_STATS_TRADUCCION.get(nombre_api_main, nombre_api_main)
                                sug = " o ".join([s.replace("_", " ") for s in lista_mains_ok])
                                advertencias.append(ft.Text(self.i18n.t("ui.tab_recomendaciones.atributo_base").replace("{actual}", n_vis).replace("{sugerencia}", sug), color="tertiary", size=12))
                                urgencia_score += 100 

                        ideal_norm = {normalizar_para_analisis(k) for k in config_rol_temp["subs"].get("ideal", [])}
                        decente_norm = {normalizar_para_analisis(k) for k in config_rol_temp["subs"].get("decente", [])}
                        basura_norm = {normalizar_para_analisis(k) for k in config_rol_temp["subs"].get("basura", [])}

                        subs = d.get("sub_stats", [])
                        subs_actuales_norm = []
                        rolls_basura_base = 0
                        rolls_basura_upgrades = 0
                        nombres_basura_base = []
                        nombres_basura_upgrades = []
                        
                        for sub in subs:
                            n_api = sub.get("name", "")
                            norm_key = normalizar_para_analisis(n_api)
                            subs_actuales_norm.append(norm_key)
                            
                            val_api = str(sub.get("value", "0")).replace("%", "").replace(",", ".")
                            try: val_float = float(val_api)
                            except: val_float = 0
                            
                            rolls_calc = calcular_rolls_substat(norm_key, val_float)
                            
                            if norm_key in basura_norm:
                                n_limpio = MAPA_STATS_TRADUCCION.get(n_api, n_api).replace(" porcentual", "%").replace(" plano", "")
                                if rolls_calc == 1:
                                    rolls_basura_base += 1
                                    nombres_basura_base.append(n_limpio)
                                else:
                                    rolls_basura_upgrades += (rolls_calc - 1)
                                    rolls_basura_base += 1
                                    nombres_basura_upgrades.append(f"{n_limpio} (+{rolls_calc-1})")
                                    nombres_basura_base.append(n_limpio)

                        ideales_posibles = [s for s in ideal_norm if s != main_stat_norm]
                        decentes_posibles = [s for s in decente_norm if s != main_stat_norm]
                        
                        slots_buenos_maximos = min(4, len(ideales_posibles) + len(decentes_posibles))
                        basura_inevitable_permitida = 4 - slots_buenos_maximos
                        
                        ideales_presentes = [s for s in subs_actuales_norm if s in ideales_posibles]
                        ideales_faltantes = [s for s in ideales_posibles if s not in subs_actuales_norm]
                        decentes_faltantes = [s for s in decentes_posibles if s not in subs_actuales_norm]

                        if rolls_basura_upgrades > 0:
                            str_upg = ", ".join(nombres_basura_upgrades)
                            advertencias.append(ft.Text(self.i18n.t("ui.tab_recomendaciones.mejoras_perdidas").replace("{rolls}", str(rolls_basura_upgrades)).replace("{stats}", str_upg), color="tertiary", size=12))
                            urgencia_score += (rolls_basura_upgrades * 15)
                            
                            if ideales_presentes:
                                n_ideal = ideales_presentes[0].replace('_porcentual', '%').replace('_plano', '').replace('_', ' ').title()
                                if "Probabilidad" in n_ideal: n_ideal = "Prob. Crítica %"
                                if "Crítico" in n_ideal and "Daño" in n_ideal: n_ideal = "Daño Crítico %"
                                advertencias.append(ft.Text(self.i18n.t("ui.tab_recomendaciones.subidas_debieron_irse").replace("{stat}", n_ideal), color="primary", size=self.FS['xs'], italic=True))
                        
                        if rolls_basura_base > 0:
                            nombres_unicos_base = list(dict.fromkeys(nombres_basura_base))
                            str_base = ", ".join(nombres_unicos_base)
                            
                            if rolls_basura_base > basura_inevitable_permitida:
                                exceso = rolls_basura_base - basura_inevitable_permitida
                                advertencias.append(ft.Text(self.i18n.t("ui.tab_recomendaciones.slot_ineficiente").replace("{stats}", str_base), color=ft.Colors.YELLOW_300, size=12))
                                urgencia_score += (exceso * 5)
                                
                                sugerencias = ideales_faltantes + decentes_faltantes
                                if sugerencias:
                                    i_str = " o ".join([s.replace("_porcentual", "%").replace("_plano", "").replace("_", " ") for s in sugerencias[:2]])
                                    advertencias.append(ft.Text(self.i18n.t("ui.tab_recomendaciones.busca_perfeccion").replace("{stats}", i_str), color="primary", size=self.FS['xs'], italic=True))
                            
                            else:
                                advertencias.append(ft.Text(self.i18n.t("ui.tab_recomendaciones.slot_inevitable").replace("{stats}", str_base), color=ft.Colors.WHITE70, size=11))
                                urgencia_score += 1

                        if advertencias:
                            recomendaciones_organizadas.append({
                                "urgencia": urgencia_score,
                                "ui": ft.Container(
                                    padding=10, bgcolor="surface", border_radius=8, border=ft.border.only(left=ft.BorderSide(3, "error")),
                                    content=ft.Column([
                                        ft.Row([ft.Text(self.i18n.t("ui.tab_recomendaciones.disco_prioridad").replace("{slot}", str(slot)).replace("{set}", _tr_set(nombre_set_disco)), weight="bold", size=13), ft.Text(self.i18n.t("ui.tab_recomendaciones.prioridad_alta") if urgencia_score > 80 else self.i18n.t("ui.tab_recomendaciones.prioridad_media"), size=10, color="secondary")]), 
                                        *advertencias
                                    ], spacing=3)
                                )
                            })
                            


            items_calculo = []
            if consejos_calc:
                for icono, titulo, detalle, color_i in consejos_calc:
                    items_calculo.append(
                        ft.Row([
                            ft.Icon(icono, color=color_i, size=20),
                            ft.Column([
                                ft.Text(titulo, weight="bold", size=14, color="white"),
                                ft.Text(detalle, size=12, color="grey")
                            ], spacing=0, expand=True)
                        ], vertical_alignment=ft.CrossAxisAlignment.START)
                    )
            else:
                items_calculo.append(ft.Text(self.i18n.t("ui.tab_recomendaciones.faltan_datos"), italic=True, color="grey"))

            seccion_calculo_build = ft.Container(
                padding=10, bgcolor="background", border_radius=8,
                border=ft.border.only(left=ft.BorderSide(4, "primary")),
                content=ft.Column([
                    ft.Text(self.i18n.t("ui.tab_recomendaciones.calculo_eficiencia"), weight="bold", color="primary"),
                    ft.Container(height=5),
                    *items_calculo
                ], spacing=10)
            )

            recomendaciones = generar_recomendaciones_texto(nombre_agente, rol_agente, elemento_agente, datos_agente_local, traductor=self.i18n)
            
            def crear_seccion_texto(titulo, items, icono):
                return ft.Column([
                    ft.Row([ft.Icon(icono, color="primary", size=18), ft.Text(titulo, weight="bold", size=14, color="primary")]),
                    ft.Container(
                        padding=ft.padding.only(left=10),
                        content=ft.Column([
                            ft.Row([
                                ft.Icon(ft.Icons.CIRCLE, size=8, color="white54"), 
                                ft.Text(item, size=13, expand=True)
                            ], alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.START)
                            for item in items
                        ], spacing=2)
                    )
                ], spacing=5)

            contenedor_texto_recomm = ft.Column([
                ft.Text(self.i18n.t("ui.tab_recomendaciones.analisis_de").replace("{agente}", nombre_agente.upper()), size=self.FS['xl'], weight="bold"),
                ft.Text(self.i18n.t("ui.tab_recomendaciones.rol_detectado").replace("{rol}", etiqueta_rol_calc).replace("{elemento}", elemento_agente), size=self.FS['xs'], italic=True, color="secondary"),
                ft.Divider(height=10, color="outline"),
                seccion_calculo_build, 
                *elementos_optimizacion,
                ft.Divider(height=20, color="outline"),
                ft.Text(self.i18n.t("ui.tab_recomendaciones.guia_referencia"), size=self.FS['lg'], weight="bold", color="secondary"),
                ft.Container(height=5),
                ft.ResponsiveRow([
                    ft.Column([crear_seccion_texto(self.i18n.t("ui.tab_recomendaciones.sets_recomendados"), recomendaciones["sets"], ft.Icons.DISC_FULL)], col={"md": 6}),
                    ft.Column([crear_seccion_texto(self.i18n.t("ui.tab_recomendaciones.wengines_sugeridos"), recomendaciones["wengines"], ft.Icons.FLASH_ON)], col={"md": 6}),
                ]),
                ft.Container(height=10),
                ft.ResponsiveRow([
                    ft.Column([crear_seccion_texto(self.i18n.t("ui.tab_recomendaciones.stats_principales"), recomendaciones["main_stats"], ft.Icons.STAR)], col={"md": 6}),
                    ft.Column([crear_seccion_texto(self.i18n.t("ui.tab_recomendaciones.substats_prioritarias"), recomendaciones["sub_stats"], ft.Icons.TRENDING_UP)], col={"md": 6}),
                ])
            ], scroll=ft.ScrollMode.AUTO, expand=True)

            resumen_rolls = evaluar_calidad_global(
                nombre_agente=nombre_agente,
                rol_agente=rol_agente,
                rolls_actuales=self.app.estado_actual.substats_counts,
                stats_finales=getattr(self.app, 'ultimos_stats_calculados', {}),
                eficiencia_wengine_actual=eficiencia_wengine_actual,
                excepciones=EXCEPCIONES_AGENTES,
                config_roles=CONFIG_ROLES,
                tiene_4pc=any(list(d.get("set_id") for d in datos_json_discos).count(sid) >= 4 for sid in set(d.get("set_id") for d in datos_json_discos)) if datos_json_discos else True
            )

            panel_completo = self.renderizar_bloque_visual_equipamiento(
                nombre_agente=nombre_agente,
                datos_discos_json=datos_json_discos,
                nombre_wengine=nombre_wengine_actual,
                rol_agente=rol_agente,
                contenedor_texto_recomm=contenedor_texto_recomm,
                resumen_rolls=resumen_rolls,
                ruta_wengine_custom=ruta_wengine_gui,
                tarjeta_discos=tarjeta_revision_discos,
                eficiencia_wengine=eficiencia_wengine_actual,
                top_wengines=top_wengines_lista,
                proj_final=proj_final,
            )

            # ── Auto-seleccionar tier según calidad actual ─────────────────────
            if proj_final and panel_completo.data and "actualizar_tier" in panel_completo.data:
                calidad_actual = resumen_rolls.get("calidad_pct", 0) if resumen_rolls else 0
                tier_auto = 80 if calidad_actual < 80 else (90 if calidad_actual < 90 else 100)
                try:
                    panel_completo.data["actualizar_tier"](tier_auto)
                except Exception:
                    pass

            return panel_completo

        def acción_generar(e):
            pantalla_carga = ft.Container(
                content=ft.Column([
                    ft.Image(src="images/bangboo_corriendo.gif", width=240, height=240, fit=ft.ImageFit.CONTAIN),
                    ft.Container(height=10),
                    ft.Text(self.i18n.t("ui.tab_recomendaciones.calculando_rutas", default="Calculando rutas óptimas..."), size=self.FS['xl'], weight="bold", color="secondary"),
                    ft.Text(self.i18n.t("ui.tab_recomendaciones.simulando_combinaciones", default="Simulando combinaciones..."), size=14, color="secondary")
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER),
                alignment=ft.alignment.center,
                height=300,
                expand=True
            )
            self.area_dinamica_recomm.content = pantalla_carga
            if self.area_dinamica_recomm.page:
                self.area_dinamica_recomm.update()

            try:
                nuevo_contenido = construir_interfaz()
                self.area_dinamica_recomm.content = nuevo_contenido
            except Exception as ex:
                self.area_dinamica_recomm.content = ft.Text(f"Error en la simulación: {ex}", color="red")

            if self.area_dinamica_recomm.page:
                self.area_dinamica_recomm.update()
                self.app.page.snack_bar = ft.SnackBar(content=ft.Text(self.i18n.t("ui.tab_recomendaciones.analisis_completado", default="Análisis completado.")))
                self.app.page.snack_bar.open = True
                self.app.page.update()

        # Exponer para auto-trigger desde cargar_agente
        self._accion_generar_recomm = acción_generar

        btn_generar_wrap = ft.Container(
            content=ft.ElevatedButton(
                self.i18n.t("ui.tab_recomendaciones.recalcular_build"),
                icon=ft.Icons.REFRESH,
                on_click=acción_generar,
                bgcolor="primary",
                color="background",
                height=42,
            ),
            animate_scale=ft.Animation(250, ft.AnimationCurve.EASE_OUT),
            # Eliminamos alignment=ft.alignment.center_right
            padding=ft.padding.only(bottom=14)
        )
        
        def on_hover_btn_generar(e):
            btn_generar_wrap.scale = 1.05 if e.data == "true" else 1.0
            btn_generar_wrap.update()
            
        btn_generar_wrap.on_hover = on_hover_btn_generar

        # 2. Usamos un Row para alinear el botón a la derecha de la pantalla de forma segura
        fila_boton = ft.Row(
            controls=[btn_generar_wrap],
            alignment=ft.MainAxisAlignment.END # Esto lo empuja a la derecha
        )

        try:
            contenido_inicial = construir_interfaz()
        except Exception as e:
            contenido_inicial = ft.Text(f"Error cargando interfaz: {e}", color="red")

        self.area_dinamica_recomm = ft.AnimatedSwitcher(
            content=contenido_inicial,
            transition=ft.AnimatedSwitcherTransition.FADE,
            duration=400,
            reverse_duration=400,
            switch_in_curve=ft.AnimationCurve.EASE_IN,
            switch_out_curve=ft.AnimationCurve.EASE_OUT
        )

        # 3. Agregas la 'fila_boton' a tu columna en lugar del contenedor directo
        self.contenedor_principal_recomm.content = ft.Column([
            fila_boton, 
            self.area_dinamica_recomm
        ], expand=True, scroll=ft.ScrollMode.AUTO)

        return self.contenedor_principal_recomm

    def create_improvement_guide_tab(self):
        """Pestaña Guía de Mejoras — VISUAL REFACTOR"""

        lista_sugerencias_uid = ft.Column(spacing=2, scroll=ft.ScrollMode.AUTO, height=260)

        contenedor_sugerencias_uid = ft.Container(
            content=lista_sugerencias_uid,
            bgcolor=ft.Colors.with_opacity(0.97, "surface"),
            border_radius=12,
            border=ft.border.all(1, "outline"),
            shadow=ft.BoxShadow(spread_radius=2, blur_radius=16, color=ft.Colors.BLACK87),
            visible=False,
            padding=ft.padding.symmetric(vertical=4),
        )

        self.txt_uid_mejoras = ft.TextField(
            label=self.i18n.t("ui.mejoras_discos.buscar_label"),
            hint_text=self.i18n.t("ui.mejoras_discos.buscar_hint"),
            dense=True,
            expand=True,
            prefix_icon=ft.Icons.SEARCH,
            on_submit=lambda e: self.app.cargar_personajes_para_mejoras_directo(e),
            border_radius=8,
        )

        def seleccionar_uid_mejoras(e):
            uid_seleccionado = e.control.data
            self.txt_uid_mejoras.value = uid_seleccionado
            contenedor_sugerencias_uid.visible = False
            self.txt_uid_mejoras.update()
            contenedor_sugerencias_uid.update()
            self.app.cargar_personajes_para_mejoras_directo(e)

        def crear_item_uid_mejoras(nombre, uid):
            # Obtener mejor agente del ranking para mostrar su imagen
            mejor_agente_img = None
            try:
                ranking = self.app.gestor_ranking.cargar_ranking_global()
                datos_jugador = ranking.get(nombre, {})
                personajes = datos_jugador.get('personajes', {})
                if personajes:
                    mejor = max(personajes.items(), key=lambda x: x[1].get('calificacion', 0))
                    import os as _os_uid
                    for ruta in [f"images/Iconos/{mejor[0]}.png", f"images/iconos/{mejor[0]}.png"]:
                        if _os_uid.path.exists(ruta):
                            mejor_agente_img = ruta
                            break
            except Exception:
                pass

            if mejor_agente_img:
                icono_jugador = ft.Container(
                    content=ft.Image(src=mejor_agente_img, width=32, height=32, fit=ft.ImageFit.COVER),
                    width=32, height=32, border_radius=16,
                    clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                    border=ft.border.all(1, "primary"),
                )
            else:
                icono_jugador = ft.Container(
                    content=ft.Icon(ft.Icons.PERSON, size=16, color="background"),
                    bgcolor="primary",
                    padding=ft.padding.all(6),
                    border_radius=16,
                    width=32, height=32,
                )

            return ft.Container(
                content=ft.Row([
                    icono_jugador,
                    ft.Column([
                        ft.Text(nombre, size=13, weight="bold",
                                overflow=ft.TextOverflow.ELLIPSIS, max_lines=1),
                        ft.Text(uid, size=11, color=ft.Colors.GREY_400,
                                overflow=ft.TextOverflow.ELLIPSIS, max_lines=1),
                    ], spacing=0, expand=True, tight=True),
                ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                padding=ft.padding.symmetric(horizontal=14, vertical=10),
                ink=True,
                on_click=seleccionar_uid_mejoras,
                data=uid,
                border_radius=8,
            )

        def actualizar_sugerencias_uid(e):
            texto_busqueda = self.txt_uid_mejoras.value.strip().lower()
            if not texto_busqueda:
                contenedor_sugerencias_uid.visible = False
                contenedor_sugerencias_uid.update()
                return
            uids_guardados = self.app.cargar_uids_guardados()
            if not uids_guardados:
                contenedor_sugerencias_uid.visible = False
                contenedor_sugerencias_uid.update()
                return
            sugerencias = {n: u for n, u in uids_guardados.items()
                        if texto_busqueda in n.lower() or texto_busqueda in u}
            if sugerencias:
                lista_sugerencias_uid.controls.clear()
                for nombre, uid in list(sugerencias.items())[:8]:
                    lista_sugerencias_uid.controls.append(crear_item_uid_mejoras(nombre, uid))
                contenedor_sugerencias_uid.visible = True
            else:
                contenedor_sugerencias_uid.visible = False
            contenedor_sugerencias_uid.update()

        self.txt_uid_mejoras.on_change = actualizar_sugerencias_uid

        def _on_click_cargar(e):
            self.contenedor_mejoras.controls.clear()
            self.contenedor_mejoras.controls.append(
                ft.Column([
                    ft.ProgressRing(),
                    ft.Text(self.i18n.t("ui.mejoras_discos.analizando", default="Analizando..."), size=14, color="secondary")
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER)
            )
            self.contenedor_mejoras.update()
            self.app.cargar_personajes_para_mejoras_directo(e)

        btn_cargar = ft.ElevatedButton(
            self.i18n.t("ui.mejoras_discos.analizar", default="Analizar"),
            icon=ft.Icons.ANALYTICS,
            on_click=_on_click_cargar,
            bgcolor="primary",
            color="background",
            height=42,
        )

        self.contenedor_mejoras = ft.Column(
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            spacing=14
        )

        instrucciones = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.TIPS_AND_UPDATES, size=22, color="primary"),
                    ft.Text(self.i18n.t("ui.mejoras_discos.titulo"),
                            size=20, weight="bold")
                ], spacing=10),
                ft.Container(height=4),
                ft.Text(
                    self.i18n.t("ui.mejoras_discos.descripcion"),
                    size=14,
                    color=ft.Colors.GREY_400
                ),
            ], spacing=4),
            padding=ft.padding.all(18),
            bgcolor=ft.Colors.with_opacity(0.07, ft.Colors.PRIMARY),
            border_radius=12,
            border=ft.border.all(1, ft.Colors.with_opacity(0.2, ft.Colors.PRIMARY)),
            shadow=ft.BoxShadow(blur_radius=10, spread_radius=0,
                                color=ft.Colors.BLACK26, offset=ft.Offset(0, 2))
        )

        return ft.Column([
            instrucciones,
            ft.Container(height=8),
            ft.Row([
                self.txt_uid_mejoras,
                btn_cargar,
            ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            contenedor_sugerencias_uid,
            ft.Divider(height=14),
            self.contenedor_mejoras
        ], scroll=ft.ScrollMode.AUTO, expand=True)

    def create_graph_tab(self):
        """Pestaña de Gráficas — VISUAL REFACTOR"""
        self.dd_tipo_dano_grafica = ft.Dropdown(
            label=self.i18n.t("ui.tab_graficas.tipo_dano"),
            options=[
                ft.dropdown.Option("General",  text=self.i18n.t("ui.tab_graficas.maximo_auto")),
                ft.dropdown.Option("Normal",   text=self.i18n.t("ui.tab_graficas.dano_normal")),
                ft.dropdown.Option("Anomalía", text=self.i18n.t("ui.tab_graficas.dano_anomalia")),
                ft.dropdown.Option("Sheer",    text=self.i18n.t("ui.tab_graficas.dano_sheer")),
            ],
            bgcolor="background",
            border_radius=ft.border_radius.only(bottom_left=8, bottom_right=8),
            border_color=ft.Colors.with_opacity(0.25, ft.Colors.WHITE),
            focused_border_color="primary",
            value="General", width=250
        )

        self.contenedor_grafica_dispersion = ft.Container(expand=True, height=550)

        btn_generar_wrap = ft.Container(
            content=ft.ElevatedButton(
                self.i18n.t("ui.tab_graficas.generar_analisis"),
                icon=ft.Icons.BAR_CHART,
                on_click=self.app.ejecutar_analisis_grafico,
                bgcolor="primary",
                color="background",
                height=42,
            ),
            animate_scale=ft.Animation(240, ft.AnimationCurve.EASE_OUT),
        )
        def on_hover_btn_grafica(e):
            btn_generar_wrap.scale = 1.05 if e.data == "true" else 1.0
            btn_generar_wrap.update()
            btn_generar_wrap.on_hover = on_hover_btn_grafica

        panel_grafica = ft.Container(
            padding=ft.padding.all(18),
            bgcolor="surface",
            border_radius=12,
            border=ft.border.all(1, "outline"),
            shadow=ft.BoxShadow(blur_radius=16, spread_radius=0,
                                color=ft.Colors.BLACK26, offset=ft.Offset(0, 4)),
            expand=True,
            content=ft.ResponsiveRow([
                ft.Column([
                    ft.Text(self.i18n.t("ui.tab_graficas.rendimiento_interactivo"),
                            weight="bold", size=self.FS['md']),
                    ft.Container(height=8),
                    self.contenedor_grafica_dispersion
                ], col={"md": 12}),
            ])
        )

        return ft.Column([
            ft.Row([
                ft.Text(self.i18n.t("ui.tab_graficas.analitica_rendimiento"),
                        size=24, weight="bold"),
            ]),
            ft.Container(height=8),
            ft.Row([self.dd_tipo_dano_grafica, btn_generar_wrap],
                spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            ft.Divider(height=14),
            panel_grafica,
        ], scroll=ft.ScrollMode.AUTO, expand=True, spacing=0)

    def actualizar_imagen_agente(self, nombre_agente):
        if nombre_agente == "Ninguno":
            self.img_agente.src = "/images/default.png" 
            self.img_agente.opacity = 0.2
        else:
            ruta_imagen = f"/images/{nombre_agente}.png"
            self.img_agente.src = ruta_imagen
            self.img_agente.opacity = 1.0
        if self.img_agente.page:
            self.img_agente.update()
        self.iluminar_stats_dps(nombre_agente)

    def iluminar_stats_soporte(self, prefijo, nombre_agente):
        """Ilumina los stats requeridos por el agente seleccionado en el panel de soportes."""
        n_norm = str(nombre_agente).lower().strip()
        
        campos = {
            "atk": self.team_controls.get(f"{prefijo}_stat_atk"),
            "hp": self.team_controls.get(f"{prefijo}_stat_hp"),
            "er": self.team_controls.get(f"{prefijo}_stat_er"),
            "imp": self.team_controls.get(f"{prefijo}_stat_imp"),
            "pen": self.team_controls.get(f"{prefijo}_stat_pen"),
            "tasa": self.team_controls.get(f"{prefijo}_stat_tasa"),
            "am": self.team_controls.get(f"{prefijo}_stat_am"),
            "ap": self.team_controls.get(f"{prefijo}_stat_ap"),
        }
        
        for field in campos.values():
            if field:
                field.border_color = None
                field.label_style = ft.TextStyle(color=None, weight=ft.FontWeight.NORMAL)
        
        color_hl = "primary"
        style_hl = ft.TextStyle(color=color_hl, weight=ft.FontWeight.BOLD)
        
        campos_a_iluminar = []
        
        if n_norm in ["astra yao", "lucy", "pan yinhu", "ju fufu", "soukaku", "yuzuha", "sunna"]:
            campos_a_iluminar.append(campos["atk"])
        elif n_norm in ["lucia", "zhao"]:
            campos_a_iluminar.append(campos["hp"])
        elif n_norm in ["orphie & magus", "orphie", "magus"]:
            campos_a_iluminar.append(campos["er"])
        elif n_norm in ["lighter"]:
            campos_a_iluminar.append(campos["imp"])
        elif n_norm in ["rina"]:
            campos_a_iluminar.append(campos["pen"])
        elif n_norm in ["vivian"]:
            campos_a_iluminar.append(campos["am"])
            
        for campo in campos_a_iluminar:
            if campo:
                campo.border_color = color_hl
                campo.label_style = style_hl
                
        for field in campos.values():
            if field and field.page:
                field.update()

    def iluminar_stats_dps(self, nombre_agente):
        """Ilumina las substats ideales en la pestaña principal del DPS basándose en los diccionarios."""
        from logica_recomendaciones import CONFIG_ROLES, EXCEPCIONES_AGENTES
        
        campos_dps = [
            "Ataque", "Puntos_Vida", "Defensa", "Probabilidad_crítico", 
            "Daño_crítico", "Daño_elemental", "Maestría_Anomalía", 
            "Tasa_de_Anomalía", "Impacto", "Tasa_de_Perforación", 
            "Perforación_Plana", "Recuperación_energía"
        ]
        
        for key in campos_dps:
            field = self.entry_vars.get(key)
            if field:
                field.border_color = None
                field.label_style = ft.TextStyle(color=None, weight=ft.FontWeight.NORMAL)
                
        if not nombre_agente or nombre_agente == "Ninguno":
            for key in campos_dps:
                if self.entry_vars.get(key) and self.entry_vars[key].page:
                    self.entry_vars[key].update()
            return

        rol_agente = "Atacante"
        if hasattr(self.app, 'agentes_data') and self.app.agentes_data:
            datos_agente = next((a for a in self.app.agentes_data if a['Nombre'] == nombre_agente), None)
            if datos_agente:
                rol_agente = datos_agente.get("Tipo", "Atacante")

        config_rol = CONFIG_ROLES.get(rol_agente, CONFIG_ROLES["Atacante"])
        ideales_raw = config_rol.get("subs", {}).get("ideal", [])
        
        if nombre_agente in EXCEPCIONES_AGENTES:
            excep = EXCEPCIONES_AGENTES[nombre_agente]
            if "subs" in excep and "ideal" in excep["subs"]:
                ideales_raw = excep["subs"]["ideal"]

        keys_a_iluminar = set()
        for stat in ideales_raw:
            stat_clean = stat.replace("_porcentual", "").replace("_plano", "")
            keys_a_iluminar.add(stat_clean)
            
        color_hl = "primary"
        style_hl = ft.TextStyle(color=color_hl, weight=ft.FontWeight.BOLD)
        
        for key in keys_a_iluminar:
            field = self.entry_vars.get(key)
            if field:
                field.border_color = color_hl
                field.label_style = style_hl

        for key in campos_dps:
            if self.entry_vars.get(key) and self.entry_vars[key].page:
                self.entry_vars[key].update()

    def actualizar_imagen_enemigo(self, nombre_enemigo):
        if not nombre_enemigo or nombre_enemigo == "Ninguno":
            self.img_enemigo.src = "/images/enemigos/default_enemy.png" 
            self.img_enemigo.opacity = 0.2
        else:
            ruta_imagen = f"/images/enemigos/{nombre_enemigo}.png"
            self.img_enemigo.src = ruta_imagen
            self.img_enemigo.opacity = 1.0
        if self.img_enemigo.page:
            self.img_enemigo.update()
        
    def actualizar_imagen_wengine(self, nombre_wengine):
        if not nombre_wengine or nombre_wengine == "Ninguno":
            self.img_wengine.src = "/images/wengine/default_wengine.png"
            self.img_wengine.opacity = 0.2
        else:
            ruta_imagen = f"/images/wengine/{nombre_wengine}.png"
            self.img_wengine.src = ruta_imagen
            self.img_wengine.opacity = 1.0
        if self.img_wengine.page:
            self.img_wengine.update()

    def actualizar_imagen_team(self, prefijo, tipo, nombre):
        """
        Actualiza la imagen de un agente específico.
        """
        clave_control = f"{prefijo}_img_{tipo}"

        img_control = self.team_controls.get(clave_control)
        
        if not img_control:
            print(f"Error: No se encontró el control de imagen para {clave_control}")
            return

        if tipo == "agente":
            ruta_default = "/images/default.png"
            ruta_carpeta = "/images/"
            
            self.iluminar_stats_soporte(prefijo, nombre)
            
        else:
            ruta_default = "/images/wengine/default_wengine.png"
            ruta_carpeta = "/images/wengine/"

        if not nombre or nombre == "Ninguno":
            img_control.src = ruta_default
            img_control.opacity = 0.3
        else:
            img_control.src = f"{ruta_carpeta}{nombre}.png"
            img_control.opacity = 1.0

        if img_control.page:
            img_control.update()

    def configurar_input_core(self, visible, usa_slider=False, label="Stacks", max_val=1, val_def=0):
            """
            Configura dinámicamente si se muestra el Dropdown (pocos stacks) 
            o el Slider (muchos stacks) y actualiza sus etiquetas.
            Sirve tanto para Core Skills como para Pasivas con recursos.
            """
            if not visible:
                self.core_stacks_dropdown.visible = False
                self.core_stacks_slider.visible = False
                self.core_stacks_dropdown.update()
                self.core_stacks_slider.update()
                return

            if usa_slider:
                self.core_stacks_dropdown.visible = False
                self.core_stacks_slider.visible = True
                
                self.core_stacks_slider.min = 0
                self.core_stacks_slider.max = float(max_val)
                self.core_stacks_slider.divisions = int(max_val) if max_val < 100 else 100
                self.core_stacks_slider.value = float(val_def)
                
            else:
                self.core_stacks_slider.visible = False
                self.core_stacks_dropdown.visible = True
                
                self.core_stacks_dropdown.label = label
                self.core_stacks_dropdown.value = str(val_def)

                step = 1
                if max_val > 20: step = 5
                self.core_stacks_dropdown.options = [ft.dropdown.Option(str(i)) for i in range(0, int(max_val) + 1, step)]

            self.core_stacks_dropdown.update()
            self.core_stacks_slider.update()
   
    def actualizar_campo_pen_res(self, elemento):
        """
        Cambia dinámicamente el campo PEN RES ubicado en la sección del Enemigo.
        """
        if not elemento: return
        
        elemento = elemento.lower().strip()

        mapa_keys = {
            "fuego": "Pen_Res_Fuego",
            "electrico": "Pen_Res_Electrico", 
            "eléctrico": "Pen_Res_Electrico",
            "hielo": "Pen_Res_Hielo",
            "fisico": "Pen_Res_Fisico", 
            "físico": "Pen_Res_Fisico",
            "etereo": "Pen_Res_Etereo", 
            "etéreo": "Pen_Res_Etereo",
            "viento": "Pen_Res_Viento"
        }

        nueva_clave = mapa_keys.get(elemento, "Pen_Res_Fisico")
        nuevo_label = f"PEN RES ({elemento.capitalize()})"

        self.campo_pen_res.label = nuevo_label
        self.campo_pen_res.data = nueva_clave
        self.campo_pen_res.update()

        keys_viejas = [k for k, v in self.entry_vars.items() if v == self.campo_pen_res]
        for k in keys_viejas:
            del self.entry_vars[k]

        self.entry_vars[nueva_clave] = self.campo_pen_res
    
    def _refrescar_lista_agentes_ranking(self, e=None):
        """Limpia y recarga la lista de agentes (útil tras actualizaciones)."""
        self._ranking_cache_gui = None
        self.ranking_lista_agentes.controls.clear()
        self._cargar_lista_agentes_ranking()
        self.ranking_lista_agentes.update()

    def create_ranking_tab(self):
        """Pestaña ranking global — VISUAL REFACTOR"""

        self.ranking_lista_agentes = ft.Column(
            scroll=ft.ScrollMode.AUTO,
            spacing=6,
        )

        # Lazy: no cargamos la lista aquí, se carga al seleccionar la pestaña
        self._ranking_tab_loaded = False

        contenedor_izquierdo = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.PEOPLE_ALT, size=18, color="primary"),
                    ft.Text(self.i18n.t("ui.ranking.selecciona_agente"), size=self.FS['lg'], weight="bold"),
                    ft.IconButton(
                        icon=ft.Icons.REFRESH,
                        tooltip="Actualizar lista",
                        on_click=self._refrescar_lista_agentes_ranking
                    ),
                ], spacing=8),
                ft.Divider(height=8, color="outline"),
                ft.Container(
                    content=self.ranking_lista_agentes,
                    expand=True,
                )
            ], spacing=8, expand=True),
            padding=ft.padding.all(16),
            bgcolor="surface",
            border_radius=12,
            border=ft.border.all(1, "outline"),
            shadow=ft.BoxShadow(blur_radius=14, spread_radius=0,
                                color=ft.Colors.BLACK26, offset=ft.Offset(0, 3)),
            width=280,
            alignment=ft.alignment.top_left
        )

        self.ranking_contenido_derecha = ft.Column(
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            spacing=10
        )

        contenedor_derecho = ft.Container(
            content=self.ranking_contenido_derecha,
            padding=ft.padding.all(16),
            bgcolor="surface",
            border_radius=12,
            border=ft.border.all(1, "outline"),
            shadow=ft.BoxShadow(blur_radius=14, spread_radius=0,
                                color=ft.Colors.BLACK26, offset=ft.Offset(0, 3)),
            expand=True,
            alignment=ft.alignment.top_left
        )

        return ft.Row([
            contenedor_izquierdo,
            contenedor_derecho
        ], spacing=14, expand=True,
        vertical_alignment=ft.CrossAxisAlignment.START)

    def _obtener_ranking_cached(self, force=False):
        """Devuelve ranking_global cacheado en memoria (TTL 60s)."""
        now = time.time()
        if force or self._ranking_cache_gui is None or (now - self._ranking_cache_ts) > 60:
            self._ranking_cache_gui = self.app.gestor_ranking.cargar_ranking_global()
            self._ranking_cache_ts = now
        return self._ranking_cache_gui

    def _cargar_lista_agentes_ranking(self):
        """Carga la lista de agentes disponibles en el ranking"""
        
        # Usamos agentes_data en vez de listar archivos de disco (incompatible en web)
        ranking_data = self._obtener_ranking_cached()
        import time
        if (time.time() - self._ranking_cache_ts) > 45:
            self.ranking_lista_agentes.controls.insert(0, ft.Container(
                bgcolor=ft.Colors.with_opacity(0.12, ft.Colors.AMBER),
                border_radius=8,
                content=ft.Row([
                    ft.Icon(ft.Icons.UPDATE, size=14, color=ft.Colors.AMBER_400),
                    ft.Text("Datos en caché — actualiza tu UID para ver cambios recientes", size=11, color=ft.Colors.AMBER_400)
                ])
            ))
        agentes_con_datos = set()

        for jugador_data in ranking_data.values():
            personajes = jugador_data.get('personajes', {})
            agentes_con_datos.update(personajes.keys())

        nombres_agentes = sorted(
            [a.get('Nombre', '') for a in self.app.agentes_data if a.get('Nombre')]
        ) if self.app.agentes_data else sorted(agentes_con_datos)

        agentes_con_ranking = []
        agentes_sin_ranking = []

        for nombre_agente in nombres_agentes:
            # Simulamos el mismo nombre de archivo que antes
            if nombre_agente in agentes_con_datos:
                agentes_con_ranking.append(nombre_agente)
            else:
                agentes_sin_ranking.append(nombre_agente)
        
        if agentes_con_ranking:
            self.ranking_lista_agentes.controls.append(
                ft.Text(self.i18n.t("ui.ranking.datos"), size=12, weight="bold", color="primary")
            )
            for nombre_agente in agentes_con_ranking:
                self.ranking_lista_agentes.controls.append(
                    self._crear_boton_agente_ranking(nombre_agente, archivo=f"{nombre_agente}.png")
                )
        
        if agentes_sin_ranking:
            self.ranking_lista_agentes.controls.append(
                ft.Divider(height=2, color="outline")
            )
            self.ranking_lista_agentes.controls.append(
                ft.Text(self.i18n.t("ui.ranking.nodatos"), size=12, weight="bold", color="primary")
            )
            for nombre_agente in agentes_sin_ranking:
                self.ranking_lista_agentes.controls.append(
                    self._crear_boton_agente_ranking(nombre_agente, archivo=f"{nombre_agente}.png", tiene_datos=False)
                )
    
    def _crear_boton_agente_ranking(self, nombre_agente, archivo, tiene_datos=True):
        """Botón agente en ranking — VISUAL REFACTOR"""

        ruta_imagen = f"images/{archivo}"

        def on_click(e):
            self.ranking_agente_seleccionado = nombre_agente
            self.ranking_pagina_actual = 0
            self._cargar_ranking_agente(nombre_agente)

        boton = ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Image(src=ruta_imagen, width=44, height=44,
                                    fit=ft.ImageFit.COVER, border_radius=22),
                    width=44, height=44, border_radius=22,
                    clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                    border=ft.border.all(2, "primary" if tiene_datos else "outline"),
                    shadow=ft.BoxShadow(blur_radius=8, spread_radius=0,
                                        color=ft.Colors.with_opacity(
                                            0.4 if tiene_datos else 0.1,
                                            ft.Colors.PRIMARY))
                ),
                ft.Text(nombre_agente, size=13, weight="bold", expand=True,
                        overflow=ft.TextOverflow.ELLIPSIS),
                ft.Icon(ft.Icons.CHEVRON_RIGHT, size=18, color="primary")
                if tiene_datos else
                ft.Icon(ft.Icons.RADIO_BUTTON_UNCHECKED, size=14, color="outline")
            ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.padding.symmetric(horizontal=10, vertical=8),
            bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.PRIMARY)
            if tiene_datos else ft.Colors.with_opacity(0.03, ft.Colors.WHITE),
            border_radius=12,
            border=ft.border.all(1, ft.Colors.with_opacity(
                0.3 if tiene_datos else 0.08, ft.Colors.PRIMARY)),
            on_click=on_click,
            ink=True,
            animate_scale=ft.Animation(220, ft.AnimationCurve.EASE_OUT),
        )

        def on_hover(e):
            boton.scale = 1.03 if e.data == "true" else 1.0
            boton.bgcolor = (
                ft.Colors.with_opacity(0.18 if e.data == "true" else
                                    (0.1 if tiene_datos else 0.03),
                                    ft.Colors.PRIMARY)
            )
            boton.update()

        boton.on_hover = on_hover
        return boton

    def _cargar_ranking_agente(self, nombre_agente):
        """Carga y muestra el ranking para un agente específico"""
        
        ranking_lista = self.app.gestor_ranking.generar_ranking_por_personaje(nombre_agente)
        
        if not ranking_lista:
            self.ranking_contenido_derecha.controls = [
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.INBOX, size=80, color="outline"),
                        ft.Text(
                            self.i18n.t("ui.ranking.no_datos_agente").format(nombre_agente=nombre_agente), 
                            size=16, 
                            color="outline"
                        ),
                        ft.Text(
                            self.i18n.t("ui.ranking.jugadores_apareceran"), 
                            size=12, 
                            color="outline"
                        )
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                    alignment=ft.alignment.center,
                    expand=True
                )
            ]
            self.page.update()
            return
        
        total_items = len(ranking_lista)
        inicio = self.ranking_pagina_actual * self.ranking_items_por_pagina
        fin = min(inicio + self.ranking_items_por_pagina, total_items)
        items_pagina = ranking_lista[inicio:fin]
        
        # --- LIMPIAR Y FORZAR ALINEACIÓN ARRIBA ---
        self.ranking_contenido_derecha.controls.clear()
        
        # Resetear el scroll al inicio cada vez que cambiamos de agente
        self.ranking_contenido_derecha.scroll_to(offset=0, duration=100)

        # Header del Agente
        self.ranking_contenido_derecha.controls.append(
            ft.Row([
                ft.Image(src=f"images/{nombre_agente}.png", width=60, height=60, fit=ft.ImageFit.COVER, border_radius=30),
                ft.Column([
                    ft.Text(f"Ranking de {nombre_agente}", size=20, weight="bold"),
                    ft.Text(f"Total: {total_items} jugadores", size=12, color="outline")
                ], spacing=2)
            ], spacing=15)
        )
        
        self.ranking_contenido_derecha.controls.append(ft.Divider(height=2))
        
        # Usamos una Row para las dos columnas de tarjetas
        # No le pongas expand=True a las columnas internas si quieres que el scroll 
        # lo maneje el contenedor padre (ranking_contenido_derecha)
        columna_izq = ft.Column(spacing=10, expand=True)
        columna_der = ft.Column(spacing=10, expand=True)
        
        ranking_data = self._obtener_ranking_cached()
        for idx, (apodo, calificacion, tier, uid) in enumerate(items_pagina):
            posicion = inicio + idx + 1
            tarjeta = self._crear_tarjeta_ranking(posicion, apodo, calificacion, tier, uid, nombre_agente, ranking_data)
            if idx % 2 == 0:
                columna_izq.controls.append(tarjeta)
            else:
                columna_der.controls.append(tarjeta)
        
        self.ranking_contenido_derecha.controls.append(
            ft.Row([columna_izq, columna_der], spacing=15, vertical_alignment=ft.CrossAxisAlignment.START)
        )
        
        # Paginación al final
        if total_items > self.ranking_items_por_pagina:
            self.ranking_contenido_derecha.controls.append(
                self._crear_controles_paginacion(total_items)
            )
            
        self.page.update()

    def _crear_tarjeta_ranking(self, posicion, apodo, calificacion, tier, uid, nombre_agente, ranking_data):
        """Tarjeta individual del ranking — VISUAL REFACTOR"""
        datos_jugador   = ranking_data.get(apodo, {})
        personajes      = datos_jugador.get('personajes', {})
        datos_personaje = personajes.get(nombre_agente, {})
        wengine_nombre  = datos_personaje.get('wengine', 'Ninguno')
        wengine_ref     = datos_personaje.get('wengine_refinamiento', 1)

        ruta_wengine = os.path.join("images", "wengine", f"{wengine_nombre}.png")
        if not os.path.exists(ruta_wengine):
            wengine_limpio = wengine_nombre.replace(":", "").replace("/", "_").strip()
            ruta_wengine   = os.path.join("images", "wengine", f"{wengine_limpio}.png")
            if not os.path.exists(ruta_wengine):
                ruta_wengine = None

        discos_sets = datos_personaje.get('discos_sets', {})

        MAPEO_STATS = {
            "Anomaly Proficiency": "AP", "Anomaly Mastery": "AM",
            "CRIT Rate": "CR",  "CRIT Dmg": "CD",  "CRIT DMG": "CD",
            "Percent ATK": "ATK%", "Percent DEF": "DEF%", "Percent HP": "HP%",
            "PEN Ratio": "PEN%", "Energy Regen": "ER"
        }
        discos = datos_personaje.get('discos', {})

        def simplificar_stat(stat_raw):
            if not isinstance(stat_raw, str): return stat_raw
            stat_limpio = stat_raw.strip().replace('\xa0', ' ')
            if "DMG Bonus" in stat_limpio: return "DMG%"
            return MAPEO_STATS.get(stat_limpio, stat_limpio)

        stats_principales = {
            4: simplificar_stat(discos.get('disco4', 'ATK%')),
            5: simplificar_stat(discos.get('disco5', 'PEN%')),
            6: simplificar_stat(discos.get('disco6', 'CR'))
        }
        if 'stats_principales' in datos_personaje:
            stats_principales = datos_personaje['stats_principales']

        MAPA_TRADUCCION = {
            "31800": "Jazz caótico",        "32600": "Metal colmilludo",
            "32400": "Metal eléctrico",     "32300": "Metal caótico",
            "32200": "Metal infernal",      "32500": "Metal Polar",
            "32700": "Balada de la rama y la espada", "33100": "Fábula Yunkui",
            "31400": "Punk Hormonal",       "31000": "Tecno Pícido",
            "32800": "Voz Astral",          "31600": "Jazz Oscilante",
            "32900": "Armonía Umbría",      "31100": "Tecno Tetraodóntido",
            "33300": "Floración del alba",  "33200": "Monarca del Pináculo",
            "33400": "Nana a la Luz Cenicienta", "33000": "Melodía de Phaeton",
            "31900": "Proto Punk",          "31200": "Disco sacudestrellas",
            "33600": "Aria Radiante",       "33500": "Balada de Aguas Blancas",
            "31300": "Blues Libre",         "31500": "Rock espiritual",
            "33700": "Conejo en el país de las maravillas",
            "33800": "Diario de una prisionera",
            "33900": "Metal colmilludo",
            "34000": "Metal infernal"
        }

        imagenes_discos = []
        for slot in range(1, 7):
            set_nombre = discos_sets.get(slot) or discos_sets.get(str(slot))
            if set_nombre:
                set_nombre = MAPA_TRADUCCION.get(str(set_nombre), set_nombre)
                set_limpio = set_nombre.replace(":", "").replace("/", "_").strip()
                ruta_sistema = os.path.join("images", "discos", f"{set_limpio}.png")
                ruta_flet    = f"images/discos/{set_limpio}.png"
                
                if os.path.exists(ruta_sistema):
                    imagenes_discos.append(ft.Container(
                        content=ft.Image(src=ruta_flet, width=64, height=64,
                                        fit=ft.ImageFit.CONTAIN, border_radius=32),
                        width=64, height=64, border_radius=32,
                        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                        border=ft.border.all(1, ft.Colors.with_opacity(0.3, ft.Colors.WHITE)),
                        shadow=ft.BoxShadow(blur_radius=8, spread_radius=0, color=ft.Colors.BLACK38)
                    ))
                else:
                    imagenes_discos.append(ft.Container(
                        content=ft.Icon(ft.Icons.ALBUM, size=32, color=ft.Colors.GREY_600),
                        width=64, height=64, border_radius=32,
                        bgcolor=ft.Colors.with_opacity(0.08, ft.Colors.WHITE),
                        alignment=ft.alignment.center,
                        border=ft.border.all(1, ft.Colors.GREY_800)
                    ))
            else:
                imagenes_discos.append(ft.Container(
                    content=ft.Icon(ft.Icons.ALBUM, size=32, color=ft.Colors.GREY_800),
                    width=64, height=64, border_radius=32,
                    bgcolor=ft.Colors.with_opacity(0.04, ft.Colors.WHITE),
                    alignment=ft.alignment.center
                ))

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

        color_agente = COLORES_AGENTES.get(nombre_agente, "#808080")

        if posicion <= 10:
            if posicion == 1:
                color_borde    = color_agente
                opacity_fondo  = 0.15
            else:
                factor = max(0.1, 1.0 - ((posicion - 1) / 9))
                def hex_to_rgb(h):
                    h = h.lstrip('#')
                    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
                def rgb_to_hex(rgb):
                    return '#{:02x}{:02x}{:02x}'.format(int(rgb[0]), int(rgb[1]), int(rgb[2]))
                rgb_a = hex_to_rgb(color_agente)
                rgb_g = (128, 128, 128)
                rgb_i = tuple(rgb_a[i]*factor + rgb_g[i]*(1-factor) for i in range(3))
                color_borde   = rgb_to_hex(rgb_i)
                opacity_fondo = 0.15 * factor
        else:
            color_borde   = "#808080"
            opacity_fondo = 0.04

        if posicion == 1:
            color_pos  = ft.Colors.AMBER_400
            glow_pos   = ft.BoxShadow(color=ft.Colors.AMBER_400, blur_radius=18, offset=ft.Offset(0,0))
            size_pos   = 32
            medalla    = ""
        elif posicion == 2:
            color_pos  = ft.Colors.GREY_300
            glow_pos   = ft.BoxShadow(color=ft.Colors.GREY_300, blur_radius=12, offset=ft.Offset(0,0))
            size_pos   = 28
            medalla    = ""
        elif posicion == 3:
            color_pos  = ft.Colors.ORANGE_400
            glow_pos   = ft.BoxShadow(color=ft.Colors.ORANGE_400, blur_radius=12, offset=ft.Offset(0,0))
            size_pos   = 24
            medalla    = ""
        else:
            color_pos  = ft.Colors.WHITE54
            glow_pos   = None
            size_pos   = 18
            medalla    = None

        bg_calif = calificacion_a_color_semaforo(calificacion)

        # ── Número de posición con glow ───────────────────────────────
        txt_pos = ft.Text(
            f"{medalla or ''} #{posicion}",
            size=size_pos, weight="bold", color=color_pos,
            style=ft.TextStyle(shadow=glow_pos) if glow_pos else None
        )

        # ── Icono del agente con glow de color ────────────────────────
        ruta_icono = f"images/Iconos/{nombre_agente}.png"
        icono_agente = ft.Container(
            content=ft.Stack([
                # 1. FONDO: El contenedor que genera el brillo (sombra)
                ft.Container(
                    width=80, height=80, border_radius=40,
                    shadow=ft.BoxShadow(
                        blur_radius=16, spread_radius=2,
                        color=ft.Colors.with_opacity(0.55, color_borde),
                    )
                ),
                # 2. FRENTE: La imagen del agente con su borde, dibujada por encima
                ft.Container(
                    content=ft.Image(src=ruta_icono, fit=ft.ImageFit.COVER,
                                    width=80, height=80),
                    width=80, height=80, border_radius=40,
                    clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                    border=ft.border.all(2, color_borde), # Movemos el borde aquí
                ),
            ], width=80, height=80),
        )

        # ── Pill de calificación (flotante, se coloca en Stack más abajo) ──
        pill_calif = ft.Container(
            content=ft.Text(f"{tier}  {calificacion:.1f}%",
                            size=13, weight="bold", color=ft.Colors.WHITE),
            bgcolor=bg_calif,
            padding=ft.padding.symmetric(horizontal=14, vertical=5),
            border_radius=20,
            shadow=construir_sombra_tier(tier, bg_calif)
        )

        # ── Bloque izquierdo: pos + apodo + icono + nombre agente ─────
        bloque_izquierdo = ft.Column([
            ft.Row([
                txt_pos,
                ft.Text(apodo, size=14, weight="bold", color=ft.Colors.WHITE70)
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
            icono_agente,
            ft.Text(nombre_agente, size=11, color=ft.Colors.WHITE54,
                    text_align=ft.TextAlign.CENTER),
            pill_calif,
        ], spacing=5, horizontal_alignment=ft.CrossAxisAlignment.CENTER,
           alignment=ft.MainAxisAlignment.CENTER)

        # ── Grid 3×2 de discos ────────────────────────────────────────
        fila_discos_top = ft.Row(imagenes_discos[:3], spacing=6,
                                 alignment=ft.MainAxisAlignment.CENTER)
        fila_discos_bot = ft.Row(imagenes_discos[3:], spacing=6,
                                 alignment=ft.MainAxisAlignment.CENTER)
        grid_discos = ft.Column([fila_discos_top, fila_discos_bot], spacing=6)

        # ── UID como chip visual ──────────────────────────────────────
        def copiar_uid(e):
            self.app.page.set_clipboard(str(uid))
            self.app.page.snack_bar = ft.SnackBar(
                content=ft.Text(self.i18n.t("ui_dinamico.uid_copiado", uid=uid, default=f"✓  UID {uid} copiado"), color=ft.Colors.WHITE),
                bgcolor=ft.Colors.GREEN_700,
                duration=1500,
            )
            self.app.page.snack_bar.open = True
            self.app.page.update()
            
        chip_uid = ft.GestureDetector(
            content=ft.Container(
                content=ft.Text(f"UID: {uid}", size=15, weight="w800",
                                color=ft.Colors.WHITE,
                                style=ft.TextStyle(letter_spacing=2, font_family='Consolas')),
                bgcolor=ft.Colors.with_opacity(0.08, ft.Colors.WHITE),
                border=ft.border.all(1, ft.Colors.with_opacity(0.12, ft.Colors.WHITE)),
                border_radius=6,
                padding=ft.padding.symmetric(horizontal=10, vertical=3),
                tooltip=self.i18n.t("ui_dinamico.tooltip_copiar_uid", default="Copiar UID"),
            ),
            on_tap=copiar_uid,
            mouse_cursor=ft.MouseCursor.CLICK,
        )

        bloque_central = ft.Column([
            chip_uid,
            grid_discos,
        ], spacing=10, expand=True,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER)

        # ── Bloque arma: badge de refinamiento superpuesto ────────────
        circulo_arma = ft.Stack([
            ft.Container(
                content=ft.Stack([
                    ft.Container(
                        content=ft.Image(src=ruta_wengine, fit=ft.ImageFit.CONTAIN,
                                        width=72, height=72)
                        if ruta_wengine else
                        ft.Icon(ft.Icons.QUESTION_MARK, color=ft.Colors.GREY, size=32),
                        width=72, height=72, border_radius=36,
                        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                    ),
                    ft.Container(
                        width=72, height=72, border_radius=36,
                        border=ft.border.all(1, ft.Colors.with_opacity(0.3, ft.Colors.WHITE)),
                    ),
                ], width=72, height=72),
            ),
            ft.Container(
                content=ft.Text(f"R{wengine_ref}", size=10, weight="bold",
                               color=ft.Colors.WHITE),
                bgcolor=ft.Colors.with_opacity(0.85, ft.Colors.BLACK),
                border=ft.border.all(1, ft.Colors.with_opacity(0.3, ft.Colors.WHITE)),
                border_radius=10,
                padding=ft.padding.symmetric(horizontal=5, vertical=1),
                bottom=0, right=0,
            ),
        ], width=72, height=72)

        def crear_pill_stat(texto):
            return ft.Container(
                content=ft.Text(texto, size=12, weight="bold",
                                text_align=ft.TextAlign.CENTER),
                width=46, height=46, border_radius=23,
                bgcolor=ft.Colors.with_opacity(0.22, ft.Colors.WHITE),
                border=ft.border.all(1, ft.Colors.with_opacity(0.45, ft.Colors.WHITE)),
                alignment=ft.alignment.center,
                shadow=ft.BoxShadow(blur_radius=6, spread_radius=0, color=ft.Colors.BLACK38)
            )

        bloque_derecho = ft.Column([
            ft.Container(
                content=ft.Text(wengine_nombre, size=12, color=ft.Colors.WHITE70,
                                overflow=ft.TextOverflow.ELLIPSIS,
                                text_align=ft.TextAlign.CENTER, max_lines=2,
                                weight="w500"),
                alignment=ft.alignment.center,
                expand=True,
            ),
            ft.Container(content=circulo_arma, alignment=ft.alignment.center, expand=True),
            ft.Container(
                content=ft.Row([
                    crear_pill_stat(str(stats_principales.get(4, '?'))),
                    crear_pill_stat(str(stats_principales.get(5, '?'))),
                    crear_pill_stat(str(stats_principales.get(6, '?'))),
                ], spacing=8, alignment=ft.MainAxisAlignment.CENTER),
                expand=True,
                alignment=ft.alignment.center,
            ),
        ], spacing=0,
           horizontal_alignment=ft.CrossAxisAlignment.CENTER,
           alignment=ft.MainAxisAlignment.CENTER,
           expand=True)

        # ── Separadores verticales (Bug 1: dos instancias separadas) ─────
        sep1 = ft.Container(width=1, height=200, bgcolor=ft.Colors.with_opacity(0.07, ft.Colors.WHITE))
        sep2 = ft.Container(width=1, height=200, bgcolor=ft.Colors.with_opacity(0.07, ft.Colors.WHITE))

        # ── Tarjeta final: franja lateral dentro del Stack + pill flotante ─
        contenido_tarjeta = ft.Container(
            content=ft.Stack([
                # Bug 2: franja lateral con posición absoluta dentro del Stack
                ft.Container(
                    width=10, height=260,
                    bgcolor=color_agente,
                    opacity=0.7,
                    border_radius=ft.border_radius.only(top_left=10, bottom_left=10),
                    left=0, top=0,
                ),
                ft.Container(
                    content=ft.ResponsiveRow([
                        ft.Container(content=bloque_izquierdo, col={'sm': 12, 'md': 3}),
                        ft.Container(content=sep1, col={'sm': 0, 'md': 0.2}),
                        ft.Container(content=bloque_central, col={'sm': 12, 'md': 5}),
                        ft.Container(content=sep2, col={'sm': 0, 'md': 0.2}),
                        ft.Container(content=bloque_derecho, col={'sm': 12, 'md': 3.6}),
                    ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=ft.padding.only(left=26, right=16, top=16, bottom=16),
                ),
                # Bug 3: pill con margen top/right
            ]),
            height=260,
            bgcolor=ft.Colors.with_opacity(opacity_fondo, color_borde),
            border=ft.border.all(2, color_borde),
            border_radius=12,
            shadow=ft.BoxShadow(blur_radius=12, spread_radius=0,
                                color=ft.Colors.with_opacity(0.3, color_borde),
                                offset=ft.Offset(0, 3)),
            animate_scale=ft.Animation(250, ft.AnimationCurve.EASE_OUT),
        )

        def on_hover_tarjeta(e):
            contenido_tarjeta.scale = 1.012 if e.data == "true" else 1.0
            contenido_tarjeta.shadow = ft.BoxShadow(
                blur_radius=22 if e.data == "true" else 12,
                spread_radius=3 if e.data == "true" else 0,
                color=ft.Colors.with_opacity(
                    0.5 if e.data == "true" else 0.3, color_borde),
                offset=ft.Offset(0, 5 if e.data == "true" else 3)
            )
            contenido_tarjeta.update()

        contenido_tarjeta.on_hover = on_hover_tarjeta
        return contenido_tarjeta

    def create_info_tab(self):
        """Pestaña de información del creador — crash fix definitivo"""

        # ── Sin base64, sin open() — igual que el resto de la app ────
        import base64
        import flet as ft

        ruta_imagen = "images/rorin.png"

        try:
            with open(ruta_imagen, "rb") as image_file:
                imagen_b64 = base64.b64encode(image_file.read()).decode('utf-8')
                # LA MAGIA: Le damos formato de URL de datos (Data URI)
                uri_imagen = f"data:image/png;base64,{imagen_b64}"
        except FileNotFoundError:
            uri_imagen = None

        foto = ft.Container(
            content=ft.CircleAvatar(
                # Usamos el parámetro normal, pero le pasamos el texto con la imagen
                foreground_image_src=uri_imagen,
                radius=100,
            ) if uri_imagen else ft.CircleAvatar(radius=100, bgcolor="red"),
            shape=ft.BoxShape.CIRCLE,
            border=ft.border.all(3, "primary"),
        )

        nombre = ft.Text(
            "Rorin",
            size=28, weight=ft.FontWeight.BOLD, color="primary",
        )

        descripcion = ft.Text(
            self.i18n.t("ui.tab_info.descripcion",
                        default="Creador de esta calculadora\nFanático de ZZZ"),
            size=14, color=ft.Colors.WHITE70,
            text_align=ft.TextAlign.CENTER,
        )

        def boton_link(icono, etiqueta, url, color_icono=ft.Colors.WHITE):
            btn = ft.Container(
                content=ft.ElevatedButton(
                    content=ft.Row([
                        ft.Icon(icono, color=color_icono, size=20),
                        ft.Text(etiqueta, size=13, weight=ft.FontWeight.W_500),
                    ], spacing=10, alignment=ft.MainAxisAlignment.CENTER),
                    on_click=lambda e: self.app.page.launch_url(url),
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=10),
                        padding=ft.padding.symmetric(horizontal=24, vertical=14),
                    ),
                    width=280,
                ),
                animate_scale=ft.Animation(240, ft.AnimationCurve.EASE_OUT),
            )
            def on_hover(e):
                btn.scale = 1.04 if e.data == "true" else 1.0
                btn.update()
            btn.on_hover = on_hover
            return btn

        def fila_discord():
            import httpx as _httpx

            campo_nombre = ft.TextField(
                hint_text=self.i18n.t("ui.tab_info.hint_nombre",
                                      default="Tu nombre (opcional)"),
                border_radius=10,
                filled=True,
                width=280,
                text_size=13,
                prefix_icon=ft.Icons.PERSON_OUTLINE,
            )
            campo_mensaje = ft.TextField(
                hint_text=self.i18n.t("ui.tab_info.hint_feedback",
                                      default="Escribe tu reporte de bug o sugerencia..."),
                multiline=True,
                min_lines=3,
                max_lines=5,
                max_length=1000,
                border_radius=10,
                filled=True,
                width=280,
                text_size=13,
            )
            estado_txt = ft.Text("", size=12)

            def enviar_feedback(e):
                texto = campo_mensaje.value.strip() if campo_mensaje.value else ""
                if not texto:
                    estado_txt.value = self.i18n.t("ui.tab_info.feedback_vacio",
                                                   default="⚠️ Escribe algo primero")
                    estado_txt.color = ft.Colors.ORANGE_400
                    estado_txt.update()
                    return
                nombre = campo_nombre.value.strip() if campo_nombre.value else "Anónimo"
                try:
                    _httpx.post(
                        "https://discord.com/api/webhooks/1507856434203721749/bWuYuRYJ4fTjeH7mrbAsz8jrbFgBB1l-G0txwZunwv-R4EgRjPoL0K3UJqIJB32Vtp_f",
                        json={"content": f"<@787000259284566056> 📩 **Feedback/Bug Report**\n👤 **De:** {nombre}\n```\n{texto}\n```"},
                        timeout=10,
                    )
                    campo_mensaje.value = ""
                    campo_nombre.value = ""
                    estado_txt.value = self.i18n.t("ui.tab_info.feedback_enviado",
                                                   default="✅ ¡Enviado! Gracias por tu feedback")
                    estado_txt.color = ft.Colors.GREEN_400
                except Exception:
                    estado_txt.value = self.i18n.t("ui.tab_info.feedback_error",
                                                   default="❌ Error al enviar, intenta de nuevo")
                    estado_txt.color = ft.Colors.RED_400
                campo_mensaje.update()
                campo_nombre.update()
                estado_txt.update()

            btn_enviar = ft.ElevatedButton(
                text=self.i18n.t("ui.tab_info.enviar_feedback", default="Enviar"),
                icon=ft.Icons.SEND,
                on_click=enviar_feedback,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=10),
                    padding=ft.padding.symmetric(horizontal=20, vertical=12),
                ),
                width=280,
            )

            return ft.Column([
                ft.Text(self.i18n.t("ui.tab_info.titulo_feedback",
                                    default="💬 Reportar bug o sugerencia"),
                        size=13, weight=ft.FontWeight.W_500, color=ft.Colors.WHITE70),
                campo_nombre,
                campo_mensaje,
                btn_enviar,
                estado_txt,
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8)

        separador = ft.Divider(color=ft.Colors.WHITE12, thickness=1, height=30)

        seccion_links = ft.Column([
            ft.Text(self.i18n.t("ui.tab_info.encontrame_en",
                                default="Encuéntrame en:"),
                    size=15, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE60),
            boton_link(ft.Icons.PLAY_CIRCLE_FILLED,
                    self.i18n.t("ui.tab_info.youtube", default="Canal de YouTube"),
                    "https://www.youtube.com/channel/UCFjgrdEbDO6NRKhhsPfW6BQ",
                    color_icono=ft.Colors.RED_400),
            boton_link(ft.Icons.COFFEE,
                    self.i18n.t("ui.tab_info.kofi", default="Apóyame en Ko-fi"),
                    "https://ko-fi.com/rorin",
                    color_icono=ft.Colors.ORANGE_300),
            fila_discord(),
        ], spacing=12, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

        tarjeta = ft.Container(
            content=ft.Column([
                foto, nombre, descripcion,
                separador,
                seccion_links,
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=14, scroll=ft.ScrollMode.AUTO),
            padding=ft.padding.symmetric(horizontal=44, vertical=34),
            border_radius=20,
            bgcolor=ft.Colors.with_opacity(0.08, ft.Colors.WHITE),
            border=ft.border.all(1, ft.Colors.WHITE12),
            shadow=ft.BoxShadow(
                blur_radius=6,
                spread_radius=0,
                color=ft.Colors.with_opacity(0.15, ft.Colors.PRIMARY),
                offset=ft.Offset(0, 2)
            ),
            width=420,
            expand=True,
            animate_scale=ft.Animation(300, ft.AnimationCurve.EASE_OUT),
        )

        def on_hover_tarjeta(e):
            tarjeta.scale = 1.015 if e.data == "true" else 1.0
            tarjeta.shadow = ft.BoxShadow(
                blur_radius=10 if e.data == "true" else 6, # Máximo 10
                spread_radius=1 if e.data == "true" else 0, # Apenas se expande 1px
                color=ft.Colors.with_opacity(
                    0.25 if e.data == "true" else 0.15, # Opacidad máxima de 0.25
                    ft.Colors.PRIMARY
                ),
                offset=ft.Offset(0, 4 if e.data == "true" else 2) # Se levanta un poquito
            )
            tarjeta.update()

        tarjeta.on_hover = on_hover_tarjeta

        # ── Changelog ──────────────────────────────────────────────────────────
        import json as _json, os as _osc
        _ruta_cl = "changelog.json"
        _entradas = []
        if _osc.path.exists(_ruta_cl):
            try:
                with open(_ruta_cl, encoding="utf-8") as _f:
                    _entradas = _json.load(_f)
            except Exception:
                _entradas = []

        _COLOR_BADGE = {0: ft.Colors.PRIMARY, 1: ft.Colors.ORANGE_400, 2: ft.Colors.GREY_500}

        def _entrada_changelog(i, entrada):
            items = ft.Column([
                ft.Row([
                    ft.Container(width=6, height=6, border_radius=3, bgcolor=ft.Colors.GREY_500),
                    ft.Text(entrada_item, size=12, color=ft.Colors.WHITE70, expand=True),
                ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER)
                for entrada_item in entrada.get("cambios", [])
            ], spacing=4, tight=True)
            return ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Container(
                            content=ft.Text(f"v{entrada['version']}", size=13,
                                           weight="bold", color=ft.Colors.BLACK),
                            bgcolor=_COLOR_BADGE.get(i, ft.Colors.GREY_600),
                            border_radius=8,
                            padding=ft.padding.symmetric(horizontal=10, vertical=3),
                        ),
                        ft.Text(entrada.get("fecha", ""), size=11,
                                color=ft.Colors.GREY_500, italic=True),
                    ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    items,
                ], spacing=8, tight=True),
                padding=ft.padding.symmetric(horizontal=16, vertical=12),
                bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE),
                border=ft.border.only(left=ft.BorderSide(3, _COLOR_BADGE.get(i, ft.Colors.GREY_600))),
                border_radius=8,
            )

        panel_changelog = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.HISTORY, size=18, color="primary"),
                    ft.Text("Changelog", size=18, weight="bold", color="primary"),
                ], spacing=8),
                ft.Divider(color=ft.Colors.WHITE12, height=16),
                ft.Column(
                    [_entrada_changelog(i, e) for i, e in enumerate(_entradas)],
                    spacing=10, scroll=ft.ScrollMode.AUTO, expand=True,
                ),
            ], spacing=8, expand=True),
            padding=ft.padding.symmetric(horizontal=28, vertical=28),
            border_radius=20,
            bgcolor=ft.Colors.with_opacity(0.08, ft.Colors.WHITE),
            border=ft.border.all(1, ft.Colors.WHITE12),
            expand=True,
        )

        return ft.Container(
            content=ft.Row([
                ft.Container(content=tarjeta, alignment=ft.alignment.top_center),
                ft.Container(content=panel_changelog, expand=True),
            ], spacing=24, vertical_alignment=ft.CrossAxisAlignment.START, expand=True),
            expand=True,
            padding=ft.padding.symmetric(horizontal=32, vertical=24),
        )

    def _crear_controles_paginacion(self, total_items):
        """Crea los controles de paginación"""
        
        total_paginas = (total_items + self.ranking_items_por_pagina - 1) // self.ranking_items_por_pagina
        
        def ir_pagina_anterior(e):
            if self.ranking_pagina_actual > 0:
                self.ranking_pagina_actual -= 1
                self._cargar_ranking_agente(self.ranking_agente_seleccionado)
        
        def ir_pagina_siguiente(e):
            if self.ranking_pagina_actual < total_paginas - 1:
                self.ranking_pagina_actual += 1
                self._cargar_ranking_agente(self.ranking_agente_seleccionado)
        
        return ft.Container(
            content=ft.Row([
                ft.IconButton(
                    icon=ft.Icons.CHEVRON_LEFT,
                    on_click=ir_pagina_anterior,
                    disabled=self.ranking_pagina_actual == 0
                ),
                ft.Text(
                    f"Página {self.ranking_pagina_actual + 1} de {total_paginas}",
                    size=14,
                    weight="bold"
                ),
                ft.IconButton(
                    icon=ft.Icons.CHEVRON_RIGHT,
                    on_click=ir_pagina_siguiente,
                    disabled=self.ranking_pagina_actual >= total_paginas - 1
                ),
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=20),
            padding=15,
            margin=ft.margin.only(top=20)
        )
