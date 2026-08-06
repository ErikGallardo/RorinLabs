import flet as ft


class GeneradorGraficas:
    def __init__(self, logica_dmg, translator=None):
        self.logica_dmg = logica_dmg
        self._t = translator if translator else (lambda k, default=k, **kw: default)

    def generar_analisis_buffs_interactivo(self, stats_base, elemento, tipo_dano="General"):
        # ── Lógica intocable ──────────────────────────────────────
        if stats_base.get("Defensa_Base", 0) <= 0:
            stats_base["Defensa_Base"] = 950.0

        def extraer_dano(stats):
            d_n, d_s, d_a, d_d, d_ab, d_v, _ = self.logica_dmg.calcular_todos_danos(stats, elemento)
            if tipo_dano == "Normal":    return d_n
            elif tipo_dano == "Anomalía": return d_a + d_ab
            elif tipo_dano == "Sheer":   return d_s
            elif tipo_dano == "Vortex":  return d_v
            else:                        return max(d_n, d_a + d_ab, d_s, d_v)

        dano_baseline = extraer_dano(stats_base)
        if dano_baseline <= 0:
            dano_baseline = 1

        _t = self._t
        buffs_a_evaluar = {
            "Ataque":                {"step": 500, "label": _t("ui.graficas.atk_plano",    default="ATK Plano"),     "unidad": " pts"},
            "Ataque_porcentual":     {"step": 10,  "label": _t("ui.graficas.atk_pct",      default="ATK %"),         "unidad": "%"},
            "Reduccion_DEF_enemigo": {"step": 10,  "label": _t("ui.graficas.red_def",      default="Red. Defensa"),  "unidad": "%"},
            "Tasa_de_Perforación":   {"step": 10,  "label": _t("ui.graficas.pen_pct",      default="Perforación %"), "unidad": "%"},
            "Perforación_Plana":     {"step": 20,  "label": _t("ui.graficas.pen_plana",    default="Perf. Plana"),   "unidad": " pts"},
            "Daño_elemental":        {"step": 10,  "label": _t("ui.graficas.dano_elem",    default="Daño Elem."),    "unidad": "%"},
            "Probabilidad_crítico":  {"step": 10,  "label": _t("ui.graficas.prob_critica", default="Prob. Crítica"), "unidad": "%"},
            "Daño_crítico":          {"step": 20,  "label": _t("ui.graficas.dano_critico", default="Daño Crítico"),  "unidad": "%"},
            "Maestría_Anomalía":     {"step": 25,  "label": _t("ui.graficas.maestria_anom",default="Maestría Anom."),"unidad": " pts"},
        }

        datos_precalculados = {}
        for nombre_buff, config in buffs_a_evaluar.items():
            puntos = []
            for tramo_mitad in range(21):
                x_val      = tramo_mitad / 2.0
                val_actual = x_val * config["step"]
                stats_simuladas = stats_base.copy()

                cap_buffs = ("Reduccion_DEF_enemigo", "Tasa_de_Perforación", "Probabilidad_crítico")
                if nombre_buff in cap_buffs and (stats_simuladas.get(nombre_buff, 0) + val_actual) >= 100:
                    puntos.append(puntos[-1]) if puntos else puntos.append((x_val, val_actual, 0))
                    continue

                if nombre_buff == "Ataque_porcentual":
                    stats_simuladas["Ataque"] = stats_simuladas.get("Ataque", 0) + (1000 * (val_actual / 100.0))
                else:
                    stats_simuladas[nombre_buff] = stats_simuladas.get(nombre_buff, 0) + val_actual

                dano_final  = extraer_dano(stats_simuladas)
                aumento_pct = ((dano_final / dano_baseline) - 1) * 100
                puntos.append((x_val, val_actual, max(0, aumento_pct)))

            datos_precalculados[nombre_buff] = puntos

        estado = {"izq": "Ataque", "der": "Daño_crítico"}
        contenedor_principal = ft.Container(expand=True)

        def renderizar_grafica():
            lineas_grafica = []
            max_y_val = 0

            COLOR_IZQ   = ft.Colors.TERTIARY
            COLOR_DER   = ft.Colors.PRIMARY
            COLOR_TEXTO = ft.Colors.ON_SURFACE_VARIANT
            COLOR_BORDE = ft.Colors.OUTLINE

            # ── Línea izquierda ───────────────────────────────────
            sel_izq  = estado["izq"]
            cfg_izq  = buffs_a_evaluar[sel_izq]
            puntos_izq = []
            for x_val, val_real, y_val in datos_precalculados[sel_izq]:
                if y_val > max_y_val: max_y_val = y_val
                val_fmt = int(val_real) if val_real.is_integer() else f"{val_real:.1f}"
                _lbl    = _t("ui.graficas.dano_tooltip", default="Daño")
                txt     = f"{cfg_izq['label']}\n+{val_fmt}{cfg_izq['unidad']}\n{_lbl}: +{y_val:.1f}%"
                puntos_izq.append(ft.LineChartDataPoint(x=x_val, y=y_val, tooltip=txt))

            lineas_grafica.append(ft.LineChartData(
                data_points=puntos_izq, stroke_width=4, color=COLOR_IZQ,
                curved=True, stroke_cap_round=True,
                below_line_gradient=ft.LinearGradient(
                    begin=ft.alignment.top_center, end=ft.alignment.bottom_center,
                    colors=[ft.Colors.with_opacity(0.35, COLOR_IZQ),
                            ft.Colors.with_opacity(0.0,  COLOR_IZQ)]
                )
            ))

            # ── Línea derecha ─────────────────────────────────────
            sel_der  = estado["der"]
            cfg_der  = buffs_a_evaluar[sel_der]
            puntos_der = []
            for x_val, val_real, y_val in datos_precalculados[sel_der]:
                if y_val > max_y_val: max_y_val = y_val
                val_fmt = int(val_real) if val_real.is_integer() else f"{val_real:.1f}"
                _lbl    = _t("ui.graficas.dano_tooltip", default="Daño")
                txt     = f"{cfg_der['label']}\n+{val_fmt}{cfg_der['unidad']}\n{_lbl}: +{y_val:.1f}%"
                puntos_der.append(ft.LineChartDataPoint(x=x_val, y=y_val, tooltip=txt))

            lineas_grafica.append(ft.LineChartData(
                data_points=puntos_der, stroke_width=4, color=COLOR_DER,
                curved=True, stroke_cap_round=True,
                below_line_gradient=ft.LinearGradient(
                    begin=ft.alignment.top_center, end=ft.alignment.bottom_center,
                    colors=[ft.Colors.with_opacity(0.35, COLOR_DER),
                            ft.Colors.with_opacity(0.0,  COLOR_DER)]
                )
            ))

            tope_y          = max_y_val * 1.15 if max_y_val > 0 else 10
            intervalo_y_grid = max(1, tope_y / 15)

            # ── LineChart ─────────────────────────────────────────
            chart = ft.LineChart(
                data_series=lineas_grafica,
                border=ft.border.all(1, COLOR_BORDE),
                horizontal_grid_lines=ft.ChartGridLines(
                    interval=intervalo_y_grid, color=COLOR_BORDE, width=1),
                vertical_grid_lines=ft.ChartGridLines(
                    interval=0.5, color=COLOR_BORDE, width=1),
                left_axis=ft.ChartAxis(
                    labels_size=40,
                    title=ft.Text(_t("ui.graficas.eje_y", default="Mejora de Daño estimada"),
                                  size=11, color=COLOR_TEXTO)
                ),
                bottom_axis=ft.ChartAxis(
                    labels_size=30, labels_interval=1,
                    title=ft.Text(_t("ui.graficas.eje_x", default="Tramos de Mejora (Ver Menús)"),
                                  size=11, color=COLOR_TEXTO)
                ),
                tooltip_bgcolor=ft.Colors.with_opacity(0.92, ft.Colors.SURFACE),
                expand=True, interactive=True,
                min_y=0, max_y=tope_y,
                min_x=0, max_x=10,
            )

            # ── Contenedor central de la gráfica con sombra ───────
            caja_grafica = ft.Container(
                content=chart,
                expand=True,
                height=500,
                padding=ft.padding.only(top=12, bottom=12, left=18, right=18),
                bgcolor="surface",
                border_radius=14,
                border=ft.border.all(1, COLOR_BORDE),
                shadow=ft.BoxShadow(
                    blur_radius=20, spread_radius=0,
                    color=ft.Colors.BLACK38, offset=ft.Offset(0, 4)
                ),
            )

            # ── Selector items con hover ──────────────────────────
            def _mk_selector_item(nombre_buff, cfg, color, es_seleccionado, on_click_fn):
                bg    = ft.Colors.with_opacity(0.18, color) if es_seleccionado else ft.Colors.TRANSPARENT
                borde = ft.border.all(1, color) if es_seleccionado else ft.border.all(1, COLOR_BORDE)

                item = ft.Container(
                    content=ft.Row([
                        ft.Container(
                            width=10, height=10,
                            bgcolor=color if es_seleccionado else ft.Colors.TRANSPARENT,
                            border_radius=5,
                            border=ft.border.all(1, color)
                        ),
                        ft.Text(
                            f"{cfg['label']} (+{cfg['step']})",
                            size=11,
                            color=color if es_seleccionado else COLOR_TEXTO,
                            weight=ft.FontWeight.BOLD if es_seleccionado else ft.FontWeight.NORMAL
                        )
                    ], spacing=8),
                    padding=ft.padding.symmetric(horizontal=10, vertical=7),
                    border_radius=8,
                    bgcolor=bg,
                    border=borde,
                    ink=True,
                    on_click=on_click_fn,
                    width=178,
                    animate_scale=ft.Animation(220, ft.AnimationCurve.EASE_OUT),
                )

                def on_hover_item(e):
                    if not es_seleccionado:
                        item.scale = 1.04 if e.data == "true" else 1.0
                        item.bgcolor = (ft.Colors.with_opacity(0.08, color)
                                        if e.data == "true" else ft.Colors.TRANSPARENT)
                        item.update()

                item.on_hover = on_hover_item
                return item

            # ── Columna izquierda ─────────────────────────────────
            controles_izq = []
            for nombre_buff, cfg in buffs_a_evaluar.items():
                es_sel = (nombre_buff == estado["izq"])

                def hacer_click_izq(e, nb=nombre_buff):
                    estado["izq"] = nb
                    contenedor_principal.content = renderizar_grafica()
                    contenedor_principal.update()

                controles_izq.append(
                    _mk_selector_item(nombre_buff, cfg, COLOR_IZQ, es_sel, hacer_click_izq)
                )

            header_izq = ft.Container(
                content=ft.Text(
                    _t("ui.graficas.variable_1", default="VARIABLE 1"),
                    color=COLOR_IZQ, weight="bold", size=13
                ),
                padding=ft.padding.only(bottom=4),
                border=ft.border.only(bottom=ft.BorderSide(2, ft.Colors.with_opacity(0.4, COLOR_IZQ)))
            )

            panel_izq = ft.Container(
                content=ft.Column(
                    [header_izq] + controles_izq,
                    spacing=6,
                    alignment=ft.MainAxisAlignment.START,
                    scroll=ft.ScrollMode.AUTO,
                ),
                padding=ft.padding.all(12),
                bgcolor="surface",
                border_radius=12,
                border=ft.border.all(1, ft.Colors.with_opacity(0.3, COLOR_IZQ)),
                shadow=ft.BoxShadow(
                    blur_radius=12, spread_radius=0,
                    color=ft.Colors.with_opacity(0.2, COLOR_IZQ),
                    offset=ft.Offset(0, 3)
                ),
                width=202,
            )

            # ── Columna derecha ───────────────────────────────────
            controles_der = []
            for nombre_buff, cfg in buffs_a_evaluar.items():
                es_sel = (nombre_buff == estado["der"])

                def hacer_click_der(e, nb=nombre_buff):
                    estado["der"] = nb
                    contenedor_principal.content = renderizar_grafica()
                    contenedor_principal.update()

                controles_der.append(
                    _mk_selector_item(nombre_buff, cfg, COLOR_DER, es_sel, hacer_click_der)
                )

            header_der = ft.Container(
                content=ft.Text(
                    _t("ui.graficas.variable_2", default="VARIABLE 2"),
                    color=COLOR_DER, weight="bold", size=13
                ),
                padding=ft.padding.only(bottom=4),
                border=ft.border.only(bottom=ft.BorderSide(2, ft.Colors.with_opacity(0.4, COLOR_DER)))
            )

            panel_der = ft.Container(
                content=ft.Column(
                    [header_der] + controles_der,
                    spacing=6,
                    alignment=ft.MainAxisAlignment.START,
                    scroll=ft.ScrollMode.AUTO,
                ),
                padding=ft.padding.all(12),
                bgcolor="surface",
                border_radius=12,
                border=ft.border.all(1, ft.Colors.with_opacity(0.3, COLOR_DER)),
                shadow=ft.BoxShadow(
                    blur_radius=12, spread_radius=0,
                    color=ft.Colors.with_opacity(0.2, COLOR_DER),
                    offset=ft.Offset(0, 3)
                ),
                width=202,
            )

            # ── Layout principal ──────────────────────────────────
            enemigo = stats_base.get('Nombre_Enemigo', 'Enemigo')
            if enemigo == "Ninguno":
                enemigo = "Enemigo Estándar"

            titulo = ft.Text(
                _t("ui.graficas.titulo_comparativa",
                   default=f"Comparativa de bonos contra {enemigo} ({tipo_dano})"
                   ).replace("{enemigo}", enemigo).replace("{tipo}", tipo_dano),
                weight="bold", size=18, color=COLOR_TEXTO,
                text_align=ft.TextAlign.CENTER
            )

            subtitulo = ft.Text(
                _t("ui.graficas.subtitulo",
                   default="Selecciona una variable de la izquierda y una de la derecha para cruzarlas en la gráfica."),
                size=13, color=COLOR_BORDE, italic=True,
                text_align=ft.TextAlign.CENTER
            )

            # ── Leyenda de colores ────────────────────────────────
            leyenda = ft.Row([
                ft.Container(
                    content=ft.Row([
                        ft.Container(width=14, height=4, bgcolor=COLOR_IZQ, border_radius=2),
                        ft.Text(buffs_a_evaluar[estado["izq"]]["label"],
                                size=12, color=COLOR_IZQ, weight="bold")
                    ], spacing=6),
                    padding=ft.padding.symmetric(horizontal=10, vertical=5),
                    bgcolor=ft.Colors.with_opacity(0.1, COLOR_IZQ),
                    border_radius=8,
                    border=ft.border.all(1, ft.Colors.with_opacity(0.3, COLOR_IZQ)),
                ),
                ft.Container(
                    content=ft.Row([
                        ft.Container(width=14, height=4, bgcolor=COLOR_DER, border_radius=2),
                        ft.Text(buffs_a_evaluar[estado["der"]]["label"],
                                size=12, color=COLOR_DER, weight="bold")
                    ], spacing=6),
                    padding=ft.padding.symmetric(horizontal=10, vertical=5),
                    bgcolor=ft.Colors.with_opacity(0.1, COLOR_DER),
                    border_radius=8,
                    border=ft.border.all(1, ft.Colors.with_opacity(0.3, COLOR_DER)),
                ),
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=16)

            layout_row = ft.Row(
                controls=[
                    panel_izq,
                    caja_grafica,
                    panel_der,
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.START,
                spacing=14,
            )

            return ft.Column([
                titulo,
                ft.Container(height=4),
                subtitulo,
                ft.Container(height=10),
                leyenda,
                ft.Container(height=14),
                layout_row,
            ],
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            scroll=ft.ScrollMode.AUTO,
            spacing=0)

        contenedor_principal.content = renderizar_grafica()
        return contenedor_principal
