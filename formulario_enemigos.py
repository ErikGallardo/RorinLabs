"""
formulario_enemigos.py — editor de enemigos del Deadly Assault sin tocar código.

Sustituye la necesidad de escribir ft.TextSpan a mano en datos_enemigos_da.py.
Lee/escribe datos/enemigos_da.json (generado una vez por migrar_enemigos.py)
y expone obtener_mapa_enemigos_da(), que devuelve EXACTAMENTE lo mismo que
la función vieja (mismas claves de traducción, mismo formato), para que el
resto de tu app no tenga que cambiar nada.
"""

import json
import os
import re
import flet as ft

# ---------------------------------------------------------------------------
# CONFIGURACIÓN
# ---------------------------------------------------------------------------
RUTA_JSON = "datos/enemigos_da.json"

# nombre semántico (lo que ves en el dropdown del formulario) -> estilo real de Flet
ESTILOS = {
    "normal": ft.TextStyle(color=ft.Colors.WHITE),
    "resaltado": ft.TextStyle(weight=ft.FontWeight.BOLD, color=ft.Colors.CYAN_300),
    "buff": ft.TextStyle(weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_400),
    "debuff": ft.TextStyle(weight=ft.FontWeight.BOLD, color=ft.Colors.RED_400),
    "especial": ft.TextStyle(weight=ft.FontWeight.BOLD, color=ft.Colors.PURPLE_300),
    "advertencia": ft.TextStyle(weight=ft.FontWeight.BOLD, color=ft.Colors.ORANGE_400),
    "cargas": ft.TextStyle(weight=ft.FontWeight.BOLD, color=ft.Colors.AMBER_400),
}
NOMBRES_ESTILO = list(ESTILOS.keys())


def generar_slug(nombre):
    slug = re.sub(r"[^a-z0-9]+", "_", nombre.lower()).strip("_")
    return slug or "enemigo"


# ---------------------------------------------------------------------------
# LECTURA / ESCRITURA DEL JSON
# ---------------------------------------------------------------------------
def leer_enemigos():
    if not os.path.exists(RUTA_JSON):
        return {}
    with open(RUTA_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


def escribir_enemigos(datos):
    carpeta = os.path.dirname(RUTA_JSON)
    if carpeta:
        os.makedirs(carpeta, exist_ok=True)
    with open(RUTA_JSON, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# RENDER: el JSON -> lo que tu app real necesita (reemplaza obtener_mapa_enemigos_da de siempre)
# ---------------------------------------------------------------------------
def obtener_mapa_enemigos_da():
    from traductor import traductor_global as i18n

    datos = leer_enemigos()
    mapa = {}
    for nombre, e in datos.items():
        slug = e.get("_slug") or generar_slug(nombre)
        spans = []
        for i, seg in enumerate(e.get("spans", []), start=1):
            estilo = ESTILOS.get(seg.get("estilo", "normal"), ESTILOS["normal"])
            clave = f"enemigo.{slug}.s{i}"
            spans.append(ft.TextSpan(i18n.t(clave, default=seg.get("texto", "")), style=estilo))

        opciones = []
        for i, opt in enumerate(e.get("opciones", []), start=1):
            clave = f"enemigo.{slug}.opt{i}"
            nueva = {k: v for k, v in opt.items()}
            nueva["label"] = i18n.t(clave, default=opt.get("label", ""))
            opciones.append(nueva)

        mapa[nombre] = {"imagen": e.get("imagen", ""), "spans": spans, "opciones": opciones}
    return mapa


# ---------------------------------------------------------------------------
# WIDGET: editor de un enemigo
# ---------------------------------------------------------------------------
class EditorEnemigo(ft.Column):
    def __init__(self, nombre_original, datos_enemigo, on_volver):
        super().__init__(expand=True, spacing=14)
        self.on_volver = on_volver
        self.nombre_original = nombre_original  # None si es nuevo
        self.datos = datos_enemigo  # dict de trabajo: imagen, spans, opciones, _slug

        # convertir efectos (dict) a lista [nombre, valor] editable por fila
        for opt in self.datos.get("opciones", []):
            opt["_efectos_lista"] = list(opt.get("efectos", {}).items())

        self._confirmar_eliminar = False

        self.campo_nombre = ft.TextField(
            label="Nombre del enemigo", value=nombre_original or "", width=420
        )
        self.campo_imagen = ft.TextField(
            label="Ruta de imagen", value=self.datos.get("imagen", ""), width=420
        )
        self.mensaje = ft.Text("", color=ft.Colors.GREEN_400)
        self.boton_eliminar = ft.OutlinedButton(
            "Eliminar enemigo", icon=ft.Icons.DELETE_OUTLINE, on_click=self._eliminar
        )

        self.col_spans = ft.Column(spacing=8)
        self.col_opciones = ft.Column(spacing=12)
        self._refrescar_spans()
        self._refrescar_opciones()

        self.controls = [
            ft.Row(
                [
                    ft.IconButton(ft.Icons.ARROW_BACK, tooltip="Volver", on_click=lambda e: self.on_volver()),
                    ft.Text("Editor de enemigo", size=20, weight=ft.FontWeight.BOLD),
                    ft.Container(expand=True),
                    self.boton_eliminar,
                    ft.ElevatedButton("Guardar", icon=ft.Icons.SAVE, on_click=self._guardar),
                ]
            ),
            self.mensaje,
            ft.Row([self.campo_nombre, self.campo_imagen]),
            ft.Divider(),
            ft.Text("Texto (orden en el que se muestra)", weight=ft.FontWeight.BOLD),
            self.col_spans,
            ft.TextButton("+ Agregar segmento al final", on_click=lambda e: self._agregar_segmento()),
            ft.Divider(),
            ft.Text("Opciones (checkboxes / cargas)", weight=ft.FontWeight.BOLD),
            self.col_opciones,
            ft.TextButton("+ Agregar opción", on_click=lambda e: self._agregar_opcion()),
        ]

    # ----- SPANS -------------------------------------------------------
    def _refrescar_spans(self):
        filas = []
        spans = self.datos.setdefault("spans", [])
        for idx, seg in enumerate(spans):
            campo_texto = ft.TextField(
                value=seg.get("texto", ""),
                multiline=True,
                min_lines=1,
                max_lines=3,
                expand=True,
                dense=True,
                on_change=lambda e, i=idx: self._editar_segmento_texto(i, e.control.value),
            )
            campo_estilo = ft.Dropdown(
                value=seg.get("estilo", "normal"),
                options=[ft.dropdown.Option(n) for n in NOMBRES_ESTILO],
                width=150,
                dense=True,
                on_change=lambda e, i=idx: self._editar_segmento_estilo(i, e.control.value),
            )
            filas.append(
                ft.Row(
                    [
                        campo_texto,
                        campo_estilo,
                        ft.IconButton(ft.Icons.ADD, tooltip="Insertar después",
                                      on_click=lambda e, i=idx: self._insertar_segmento(i)),
                        ft.IconButton(ft.Icons.DELETE_OUTLINE, icon_color=ft.Colors.RED_300,
                                      tooltip="Eliminar",
                                      on_click=lambda e, i=idx: self._eliminar_segmento(i)),
                    ]
                )
            )
        self.col_spans.controls = filas

    def _editar_segmento_texto(self, idx, valor):
        self.datos["spans"][idx]["texto"] = valor

    def _editar_segmento_estilo(self, idx, valor):
        self.datos["spans"][idx]["estilo"] = valor

    def _agregar_segmento(self):
        self.datos["spans"].append({"texto": "", "estilo": "normal"})
        self._refrescar_spans()
        self.update()

    def _insertar_segmento(self, idx):
        self.datos["spans"].insert(idx + 1, {"texto": "", "estilo": "normal"})
        self._refrescar_spans()
        self.update()

    def _eliminar_segmento(self, idx):
        self.datos["spans"].pop(idx)
        self._refrescar_spans()
        self.update()

    # ----- OPCIONES ------------------------------------------------------
    def _refrescar_opciones(self):
        tarjetas = []
        opciones = self.datos.setdefault("opciones", [])
        for idx, opt in enumerate(opciones):
            tarjetas.append(self._tarjeta_opcion(idx, opt))
        self.col_opciones.controls = tarjetas

    def _tarjeta_opcion(self, idx, opt):
        campo_tipo = ft.Dropdown(
            value=opt.get("tipo", "checkbox"),
            options=[ft.dropdown.Option("checkbox"), ft.dropdown.Option("dropdown")],
            width=140,
            dense=True,
            on_change=lambda e, i=idx: self._editar_opcion_campo(i, "tipo", e.control.value, refrescar=True),
        )
        campo_label = ft.TextField(
            label="Etiqueta", value=opt.get("label", ""), expand=True, dense=True,
            on_change=lambda e, i=idx: self._editar_opcion_campo(i, "label", e.control.value),
        )
        controles_fila1 = [campo_tipo, campo_label]
        if opt.get("tipo") == "dropdown":
            campo_stacks = ft.TextField(
                label="Máx. cargas", value=str(opt.get("max_stacks", 1)), width=110, dense=True,
                on_change=lambda e, i=idx: self._editar_opcion_campo(i, "max_stacks", e.control.value, numerico=True),
            )
            controles_fila1.append(campo_stacks)

        filas_efectos = []
        for j, (nombre_efecto, valor_efecto) in enumerate(opt.get("_efectos_lista", [])):
            filas_efectos.append(
                ft.Row(
                    [
                        ft.TextField(
                            label="Stat", value=nombre_efecto, width=220, dense=True,
                            on_change=lambda e, i=idx, jj=j: self._editar_efecto(i, jj, e.control.value, None),
                        ),
                        ft.TextField(
                            label="Valor", value=str(valor_efecto), width=110, dense=True,
                            on_change=lambda e, i=idx, jj=j: self._editar_efecto(i, jj, None, e.control.value),
                        ),
                        ft.IconButton(ft.Icons.DELETE_OUTLINE, icon_color=ft.Colors.RED_300,
                                      on_click=lambda e, i=idx, jj=j: self._eliminar_efecto(i, jj)),
                    ]
                )
            )

        return ft.Container(
            padding=12,
            border=ft.border.all(1, ft.Colors.WHITE24),
            border_radius=8,
            content=ft.Column(
                [
                    ft.Row(controles_fila1),
                    ft.Text("Efectos:", size=12, color=ft.Colors.WHITE54),
                    ft.Column(filas_efectos, spacing=4),
                    ft.Row(
                        [
                            ft.TextButton("+ Efecto", on_click=lambda e, i=idx: self._agregar_efecto(i)),
                            ft.Container(expand=True),
                            ft.IconButton(ft.Icons.DELETE_OUTLINE, icon_color=ft.Colors.RED_300,
                                          tooltip="Eliminar esta opción",
                                          on_click=lambda e, i=idx: self._eliminar_opcion(i)),
                        ]
                    ),
                ]
            ),
        )

    def _editar_opcion_campo(self, idx, campo, valor, refrescar=False, numerico=False):
        if numerico:
            try:
                valor = int(valor)
            except ValueError:
                valor = self.datos["opciones"][idx].get("max_stacks", 1)
        self.datos["opciones"][idx][campo] = valor
        if refrescar:
            self._refrescar_opciones()
            self.update()

    def _editar_efecto(self, idx, j, nombre, valor):
        actual = self.datos["opciones"][idx]["_efectos_lista"][j]
        nuevo_nombre = nombre if nombre is not None else actual[0]
        nuevo_valor = valor if valor is not None else actual[1]
        self.datos["opciones"][idx]["_efectos_lista"][j] = (nuevo_nombre, nuevo_valor)

    def _agregar_efecto(self, idx):
        self.datos["opciones"][idx]["_efectos_lista"].append(("", 0.0))
        self._refrescar_opciones()
        self.update()

    def _eliminar_efecto(self, idx, j):
        self.datos["opciones"][idx]["_efectos_lista"].pop(j)
        self._refrescar_opciones()
        self.update()

    def _agregar_opcion(self):
        self.datos["opciones"].append({"tipo": "checkbox", "label": "", "_efectos_lista": []})
        self._refrescar_opciones()
        self.update()

    def _eliminar_opcion(self, idx):
        self.datos["opciones"].pop(idx)
        self._refrescar_opciones()
        self.update()

    # ----- GUARDAR / ELIMINAR enemigo completo -------------------------
    def _guardar(self, e):
        nombre_nuevo = self.campo_nombre.value.strip()
        if not nombre_nuevo:
            self.mensaje.value = "Ponle un nombre al enemigo antes de guardar."
            self.mensaje.color = ft.Colors.RED_400
            self.update()
            return

        # pasar _efectos_lista de vuelta a dict y limpiar campos internos
        opciones_finales = []
        for opt in self.datos.get("opciones", []):
            limpio = {k: v for k, v in opt.items() if k != "_efectos_lista"}
            valores_efectos = {}
            for nombre_ef, valor_ef in opt.get("_efectos_lista", []):
                if nombre_ef.strip():
                    try:
                        valores_efectos[nombre_ef.strip()] = float(str(valor_ef).replace(",", "."))
                    except ValueError:
                        valores_efectos[nombre_ef.strip()] = valor_ef
            limpio["efectos"] = valores_efectos
            opciones_finales.append(limpio)

        slug = self.datos.get("_slug") or generar_slug(nombre_nuevo)
        registro = {
            "imagen": self.campo_imagen.value.strip(),
            "spans": self.datos.get("spans", []),
            "opciones": opciones_finales,
            "_slug": slug,
        }

        todos = leer_enemigos()
        if self.nombre_original and self.nombre_original != nombre_nuevo:
            todos.pop(self.nombre_original, None)
        todos[nombre_nuevo] = registro
        escribir_enemigos(todos)

        self.nombre_original = nombre_nuevo
        self.mensaje.value = "Guardado."
        self.mensaje.color = ft.Colors.GREEN_400
        self.update()

    def _eliminar(self, e):
        if not self._confirmar_eliminar:
            self._confirmar_eliminar = True
            self.boton_eliminar.text = "¿Seguro? clic de nuevo"
            self.boton_eliminar.icon_color = ft.Colors.RED_400
            self.update()
            return
        if self.nombre_original:
            todos = leer_enemigos()
            todos.pop(self.nombre_original, None)
            escribir_enemigos(todos)
        self.on_volver()


# ---------------------------------------------------------------------------
# PÁGINA: lista de enemigos
# ---------------------------------------------------------------------------
class PaginaFormularioEnemigos(ft.Column):
    def __init__(self):
        super().__init__(expand=True, spacing=16)
        self.contenido = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO)
        self.controls = [
            ft.Text("Enemigos del Deadly Assault", size=24, weight=ft.FontWeight.BOLD),
            self.contenido,
        ]
        self._mostrar_lista(actualizar=False)

    def _mostrar_lista(self, actualizar=True):
        todos = leer_enemigos()
        items = [
            ft.ListTile(
                title=ft.Text(nombre),
                leading=ft.Icon(ft.Icons.SHIELD_MOON_OUTLINED),
                on_click=lambda e, n=nombre: self._abrir(n),
            )
            for nombre in sorted(todos.keys())
        ]
        self.contenido.controls = [
            *items,
            ft.Divider(),
            ft.ElevatedButton("+ Nuevo enemigo", icon=ft.Icons.ADD, on_click=lambda e: self._abrir(None)),
        ]
        if actualizar:
            self.update()

    def _abrir(self, nombre):
        todos = leer_enemigos()
        if nombre and nombre in todos:
            datos_enemigo = todos[nombre]
        else:
            datos_enemigo = {"imagen": "", "spans": [], "opciones": []}
        self.contenido.controls = [EditorEnemigo(nombre, datos_enemigo, on_volver=self._mostrar_lista)]
        self.update()


# ---------------------------------------------------------------------------
# Modo standalone — para probarlo solo
# ---------------------------------------------------------------------------
def main(page: ft.Page):
    page.title = "Formulario de enemigos DA"
    page.scroll = ft.ScrollMode.AUTO
    page.add(PaginaFormularioEnemigos())


if __name__ == "__main__":
    PUERTO = 8551
    print(f"Iniciando servidor... abre http://localhost:{PUERTO} en tu navegador")
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=PUERTO, host="0.0.0.0")
