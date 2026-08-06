"""
Editor de tablas CSV — agentes, habilidades por personaje y discos.

Funciona para cualquiera de tus CSV (agentes.csv, Aria.csv, Anby.csv, discos.csv, etc.)
porque no le importa el significado de las columnas: lee el encabezado y las filas,
las muestra como tabla editable, y guarda de vuelta con el mismo delimitador ';'.

AJUSTA estas tres rutas a donde vivan tus archivos reales en el proyecto:
"""

import csv
import json
import os
import re
import secrets
import shutil
import uuid
from dataclasses import dataclass
import flet as ft
from formulas_dano import cargar_formulas_dano, guardar_formulas_dano
from mapeos_enka import cargar_mappings_enka, guardar_mappings_enka

# ---------------------------------------------------------------------------
# CONFIGURACIÓN — cambia esto a tus rutas reales
# ---------------------------------------------------------------------------
RUTA_AGENTES = "datos/agentes.csv"
RUTA_DISCOS = "datos/discos.csv"
CARPETA_PERSONAJES = "datos/agentes"
PLANTILLA_PERSONAJE = "Anby" 
RUTA_SETS = "datos/sets.csv"
RUTA_ENEMIGOS = "datos/enemigos.csv"
RUTA_WENGINE = "datos/wengine.csv"
RUTA_SUBSTATS = "datos/substat.csv"
CARPETA_LOCALES = "locales"
CARPETA_UPLOADS = "storage/editor_uploads"
os.makedirs(CARPETA_UPLOADS, exist_ok=True)


def asegurar_secret_key_uploads():
    ruta_secret = os.path.join(CARPETA_UPLOADS, ".secret_key")
    if not os.environ.get("FLET_SECRET_KEY"):
        if os.path.exists(ruta_secret):
            with open(ruta_secret, "r", encoding="utf-8") as f:
                secret_key = f.read().strip()
        else:
            secret_key = secrets.token_urlsafe(32)
            with open(ruta_secret, "w", encoding="utf-8") as f:
                f.write(secret_key)
            try:
                os.chmod(ruta_secret, 0o600)
            except OSError:
                pass
        os.environ["FLET_SECRET_KEY"] = secret_key


asegurar_secret_key_uploads()

DELIMITADOR = ";"
ENCODING = "utf-8-sig"  # utf-8-sig: respeta el BOM que ya tienen agentes.csv y discos.csv

# Coincide solo si la celda es ÍNTEGRAMENTE numérica (no toca "Soldier 0 - Anby" ni "1er Basico")
PATRON_NUMERICO = re.compile(r"^-?\d+([.,]\d+)?$")

# Ajusta estos valores si quieres tablas mas compactas o mas amplias.
ANCHO_MIN_COLUMNA = 160
ANCHO_MAX_COLUMNA = 680
ANCHO_MAX_TEXTO_LARGO = 980
COLUMNAS_TEXTO_LARGO = (
    "pasiva",
    "descripcion",
    "descripción",
    "detalle",
    "efecto",
    "texto",
    "recomendacion",
    "recomendación",
)
COLOR_CELDA_EDITADA = ft.Colors.with_opacity(0.14, "secondary")
COLOR_BORDE_EDITADO = "secondary"
COLOR_FILA_PAR = "surface"
COLOR_FILA_IMPAR = ft.Colors.with_opacity(0.04, "primary")
COLOR_CABECERA_TABLA = ft.Colors.with_opacity(0.12, "primary")
COLOR_PANEL_EDITOR = "surface"
COLOR_BORDE_EDITOR = "outline"
COLOR_TEXTO_SUAVE = "on_surface_variant"


# ---------------------------------------------------------------------------
# LECTURA / ESCRITURA DE CSV
# ---------------------------------------------------------------------------
def leer_csv(ruta):
    """Lee un CSV con el delimitador del proyecto. Devuelve (encabezados, filas_como_dicts)."""
    if not os.path.exists(ruta):
        return [], []
    with open(ruta, "r", encoding=ENCODING, newline="") as f:
        lector = csv.reader(f, delimiter=DELIMITADOR)
        filas_crudas = [fila for fila in lector if fila]
    if not filas_crudas:
        return [], []
    encabezados = filas_crudas[0]
    filas = [dict(zip(encabezados, fila)) for fila in filas_crudas[1:]]
    return encabezados, filas


def normalizar_celda(valor):
    """Si la celda es puramente numérica, estandariza el separador decimal a coma.

    Esto arregla de paso la inconsistencia que tenías en agentes.csv (78.8 vs 19,04):
    cada vez que guardes, todo numérico queda con coma.
    """
    valor = (valor or "").strip()
    if PATRON_NUMERICO.fullmatch(valor):
        return valor.replace(".", ",")
    return valor


def escribir_csv(ruta, encabezados, filas):
    """Escribe de vuelta el CSV, normalizando decimales y preservando el orden de columnas."""
    carpeta = os.path.dirname(ruta)
    if carpeta:
        os.makedirs(carpeta, exist_ok=True)
    with open(ruta, "w", encoding=ENCODING, newline="") as f:
        escritor = csv.writer(f, delimiter=DELIMITADOR)
        escritor.writerow(encabezados)
        for fila in filas:
            escritor.writerow([normalizar_celda(fila.get(h, "")) for h in encabezados])


def listar_personajes():
    """Nombres (sin .csv) de todos los archivos de habilidades en CARPETA_PERSONAJES."""
    if not os.path.exists(CARPETA_PERSONAJES):
        return []
    nombres = [f[:-4] for f in os.listdir(CARPETA_PERSONAJES) if f.lower().endswith(".csv")]
    return sorted(nombres)


def crear_csv_personaje(nombre):
    """Crea un CSV nuevo copiando como base PLANTILLA_PERSONAJE, listo para editar."""
    ruta_plantilla = os.path.join(CARPETA_PERSONAJES, f"{PLANTILLA_PERSONAJE}.csv")
    encabezados, filas = leer_csv(ruta_plantilla)
    if not encabezados:
        encabezados = ["Habilidad", "Multiplicador", "Aturdimiento", "Etiqueta_Dano"]
        filas = []
    ruta = os.path.join(CARPETA_PERSONAJES, f"{nombre}.csv")
    escribir_csv(ruta, encabezados, filas)
    return ruta


def nombre_archivo_seguro(nombre):
    """Evita separadores de ruta al crear CSV nuevos desde la interfaz."""
    return re.sub(r'[\\/:*?"<>|]+', "", nombre).strip()


def aplanar_json(valor, prefijo=""):
    """Convierte un JSON anidado en pares clave.valor -> texto."""
    resultado = {}
    if isinstance(valor, dict):
        for clave, subvalor in valor.items():
            nueva_clave = f"{prefijo}.{clave}" if prefijo else clave
            resultado.update(aplanar_json(subvalor, nueva_clave))
    else:
        resultado[prefijo] = "" if valor is None else str(valor)
    return resultado


def expandir_json(plano):
    """Reconstruye un JSON anidado desde claves tipo ui.tab_dps.buscar_agente."""
    raiz = {}
    for clave, valor in plano.items():
        partes = [p.strip() for p in clave.split(".") if p.strip()]
        if not partes:
            continue
        cursor = raiz
        for parte in partes[:-1]:
            cursor = cursor.setdefault(parte, {})
        cursor[partes[-1]] = valor
    return raiz


def leer_json(ruta):
    if not os.path.exists(ruta):
        return {}
    with open(ruta, "r", encoding="utf-8") as f:
        return json.load(f)


def escribir_json(ruta, datos):
    carpeta = os.path.dirname(ruta)
    if carpeta:
        os.makedirs(carpeta, exist_ok=True)
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)
        f.write("\n")


def leer_texto(ruta):
    if not os.path.exists(ruta):
        return ""
    with open(ruta, "r", encoding="utf-8") as f:
        return f.read()


def escribir_texto(ruta, texto):
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(texto)


@dataclass
class ProblemaValidacion:
    severidad: str
    categoria: str
    titulo: str
    detalle: str
    ruta: str = ""
    destino_imagen: str = ""


def _normalizar_nombre(valor):
    return (valor or "").strip().lower()


def _archivo_existe(*partes):
    return os.path.exists(os.path.join(*partes))


def _agregar_problema(problemas, severidad, categoria, titulo, detalle, ruta="", destino_imagen=""):
    problemas.append(ProblemaValidacion(severidad, categoria, titulo, detalle, ruta, destino_imagen))


def _detectar_duplicados(filas, columna):
    vistos = {}
    duplicados = []
    for idx, fila in enumerate(filas, start=2):
        clave = _normalizar_nombre(fila.get(columna, ""))
        if not clave:
            continue
        if clave in vistos:
            duplicados.append((fila.get(columna, ""), vistos[clave], idx))
        else:
            vistos[clave] = idx
    return duplicados


def _leer_mappings_sets_codigo():
    patron = re.compile(r"(\d{4,6})\s*:\s*[\"']([^\"']+)[\"']")
    rutas = [
        "api.py",
        "gestor_ranking.py",
        "Crear_Gui.py",
        "Calculadora_ZZZ.py",
        "analizador_prioridades.py",
    ]
    encontrados = {}
    conflictos = {}
    for ruta in rutas:
        if not os.path.exists(ruta):
            continue
        with open(ruta, "r", encoding="utf-8", errors="ignore") as f:
            texto = f.read()
        for id_set, nombre in patron.findall(texto):
            if int(id_set) < 30000:
                continue
            actual = encontrados.setdefault(id_set, {})
            actual.setdefault(nombre, set()).add(ruta)
    for id_set, nombres in encontrados.items():
        if len(nombres) > 1:
            conflictos[id_set] = nombres
    return encontrados, conflictos


def validar_assets_y_datos():
    problemas = []

    rutas_requeridas = [
        RUTA_AGENTES,
        RUTA_DISCOS,
        RUTA_SETS,
        RUTA_ENEMIGOS,
        RUTA_WENGINE,
        RUTA_SUBSTATS,
        os.path.join(CARPETA_LOCALES, "es.json"),
        os.path.join(CARPETA_LOCALES, "en.json"),
    ]
    for ruta in rutas_requeridas:
        if not os.path.exists(ruta):
            _agregar_problema(problemas, "error", "Archivos base", "Archivo requerido no encontrado", ruta, ruta)

    encabezados_agentes, agentes = leer_csv(RUTA_AGENTES)
    encabezados_sets, sets = leer_csv(RUTA_SETS)
    encabezados_wengines, wengines = leer_csv(RUTA_WENGINE)
    encabezados_enemigos, enemigos = leer_csv(RUTA_ENEMIGOS)

    columnas_agentes = {"Nombre", "elemento", "Tipo", "Rango"}
    faltantes_agentes = columnas_agentes - set(encabezados_agentes)
    if faltantes_agentes:
        _agregar_problema(
            problemas,
            "error",
            "Agentes",
            "Columnas requeridas faltantes",
            ", ".join(sorted(faltantes_agentes)),
            RUTA_AGENTES,
        )

    for nombre, fila_1, fila_2 in _detectar_duplicados(agentes, "Nombre"):
        _agregar_problema(
            problemas,
            "error",
            "Agentes",
            f"Agente duplicado: {nombre}",
            f"Aparece en las filas {fila_1} y {fila_2}.",
            RUTA_AGENTES,
        )

    elementos_validos = {"fisico", "físico", "fuego", "hielo", "electrico", "eléctrico", "etereo", "etéreo", "viento", "frost"}
    tipos_validos = {"atacante", "aturdidor", "anomalo", "anomalía", "soporte", "auxiliar", "defensor", "ruptura"}
    for agente in agentes:
        nombre = (agente.get("Nombre") or "").strip()
        if not nombre:
            _agregar_problema(problemas, "error", "Agentes", "Fila de agente sin nombre", "Hay una fila vacía o incompleta.", RUTA_AGENTES)
            continue
        elemento = _normalizar_nombre(agente.get("elemento") or agente.get("Elemento"))
        tipo = _normalizar_nombre(agente.get("Tipo"))
        if elemento and elemento not in elementos_validos:
            _agregar_problema(problemas, "warning", "Agentes", f"Elemento no reconocido: {nombre}", agente.get("elemento", ""), RUTA_AGENTES)
        if tipo and tipo not in tipos_validos:
            _agregar_problema(problemas, "warning", "Agentes", f"Tipo no reconocido: {nombre}", agente.get("Tipo", ""), RUTA_AGENTES)
        ruta_habilidades = os.path.join(CARPETA_PERSONAJES, f"{nombre}.csv")
        if not os.path.exists(ruta_habilidades):
            _agregar_problema(problemas, "error", "Habilidades", f"Falta CSV de habilidades: {nombre}", ruta_habilidades, ruta_habilidades)
        else:
            encabezados_hab, _ = leer_csv(ruta_habilidades)
            requeridas_hab = {"Habilidad", "Multiplicador", "Aturdimiento", "Etiqueta_Dano"}
            faltantes_hab = requeridas_hab - set(encabezados_hab)
            if faltantes_hab:
                _agregar_problema(
                    problemas,
                    "error",
                    "Habilidades",
                    f"Columnas faltantes en {nombre}.csv",
                    ", ".join(sorted(faltantes_hab)),
                    ruta_habilidades,
                )
        for carpeta, severidad in (("images", "error"), ("images/Iconos", "warning"), ("images/builds", "warning"), ("images/ranking", "info")):
            ruta_img = os.path.join(carpeta, f"{nombre}.png")
            if not os.path.exists(ruta_img):
                _agregar_problema(problemas, severidad, "Imagenes", f"Falta imagen de {nombre}", ruta_img, carpeta, ruta_img)

    personajes_csv = set(listar_personajes())
    agentes_csv = {(a.get("Nombre") or "").strip() for a in agentes if (a.get("Nombre") or "").strip()}
    for nombre in sorted(personajes_csv - agentes_csv):
        _agregar_problema(
            problemas,
            "warning",
            "Habilidades",
            f"CSV de habilidades sin agente maestro: {nombre}",
            "Existe el archivo, pero no aparece en datos/agentes.csv.",
            os.path.join(CARPETA_PERSONAJES, f"{nombre}.csv"),
        )

    for nombre, fila_1, fila_2 in _detectar_duplicados(sets, "Nombre"):
        _agregar_problema(problemas, "error", "Sets", f"Set duplicado: {nombre}", f"Filas {fila_1} y {fila_2}.", RUTA_SETS)

    nombres_sets = {(s.get("Nombre") or "").strip() for s in sets if (s.get("Nombre") or "").strip()}
    for nombre in sorted(nombres_sets):
        ruta_img = os.path.join("images", "discos", f"{nombre}.png")
        ruta_asset = os.path.join("assets", "images", "discos", f"{nombre}.png")
        if not os.path.exists(ruta_img):
            _agregar_problema(problemas, "error", "Discos", f"Falta imagen de disco: {nombre}", ruta_img, "images/discos", ruta_img)
        if not os.path.exists(ruta_asset):
            _agregar_problema(problemas, "warning", "Discos", f"Falta asset web de disco: {nombre}", ruta_asset, "assets/images/discos", ruta_asset)

    mappings_sets, conflictos_sets = _leer_mappings_sets_codigo()
    sets_en_codigo = set()
    for nombres in mappings_sets.values():
        sets_en_codigo.update(nombres.keys())
    for nombre in sorted(nombres_sets - sets_en_codigo):
        _agregar_problema(
            problemas,
            "warning",
            "Mappings Enka",
            f"Set sin ID hardcodeado: {nombre}",
            "Si llega desde Enka, puede aparecer como Desconocido.",
            RUTA_SETS,
        )
    for id_set, nombres in conflictos_sets.items():
        detalle = " | ".join(f"{nombre}: {', '.join(sorted(rutas))}" for nombre, rutas in nombres.items())
        _agregar_problema(problemas, "error", "Mappings Enka", f"ID de set conflictivo: {id_set}", detalle)
    for id_set, nombres in mappings_sets.items():
        for nombre, rutas in nombres.items():
            if nombre not in nombres_sets:
                _agregar_problema(
                    problemas,
                    "warning",
                    "Mappings Enka",
                    f"Set mapeado no existe en CSV: {nombre}",
                    f"ID {id_set} en {', '.join(sorted(rutas))}.",
                    RUTA_SETS,
                )

    for nombre, fila_1, fila_2 in _detectar_duplicados(wengines, "Nombre W-Engine"):
        _agregar_problema(problemas, "error", "W-Engines", f"W-Engine duplicado: {nombre}", f"Filas {fila_1} y {fila_2}.", RUTA_WENGINE)
    for wengine in wengines:
        nombre = (wengine.get("Nombre W-Engine") or "").strip()
        ruta_img = os.path.join("images", "wengine", f"{nombre}.png")
        if nombre and not os.path.exists(ruta_img):
            _agregar_problema(problemas, "warning", "W-Engines", f"Falta imagen de W-Engine: {nombre}", ruta_img, "images/wengine", ruta_img)

    for nombre, fila_1, fila_2 in _detectar_duplicados(enemigos, "nombre"):
        _agregar_problema(problemas, "warning", "Enemigos", f"Enemigo duplicado: {nombre}", f"Filas {fila_1} y {fila_2}.", RUTA_ENEMIGOS)
    for enemigo in enemigos:
        nombre = (enemigo.get("nombre") or enemigo.get("Nombre") or "").strip()
        ruta_img = os.path.join("images", "enemigos", f"{nombre}.png")
        if nombre and not os.path.exists(ruta_img):
            _agregar_problema(problemas, "warning", "Enemigos", f"Falta imagen de enemigo: {nombre}", ruta_img, "images/enemigos", ruta_img)

    try:
        claves_es = set(aplanar_json(leer_json(os.path.join(CARPETA_LOCALES, "es.json"))))
        claves_en = set(aplanar_json(leer_json(os.path.join(CARPETA_LOCALES, "en.json"))))
        for clave in sorted(claves_es - claves_en):
            _agregar_problema(problemas, "warning", "Traducciones", f"Falta clave en EN: {clave}", "Existe en es.json, pero no en en.json.", os.path.join(CARPETA_LOCALES, "en.json"))
        for clave in sorted(claves_en - claves_es):
            _agregar_problema(problemas, "warning", "Traducciones", f"Falta clave en ES: {clave}", "Existe en en.json, pero no en es.json.", os.path.join(CARPETA_LOCALES, "es.json"))
    except Exception as ex:
        _agregar_problema(problemas, "error", "Traducciones", "No se pudieron validar traducciones", str(ex), CARPETA_LOCALES)

    orden = {"error": 0, "warning": 1, "info": 2}
    return sorted(problemas, key=lambda p: (orden.get(p.severidad, 9), p.categoria, p.titulo))


# ---------------------------------------------------------------------------
# WIDGET: tabla editable genérica
# ---------------------------------------------------------------------------
class TablaEditable(ft.Column):
    def __init__(self, ruta, on_volver):
        super().__init__(expand=True, spacing=12)
        self.ruta = ruta
        self.on_volver = on_volver
        self.encabezados, self.filas = leer_csv(ruta)
        if not self.encabezados:
            self.encabezados = ["Columna_1"]
        self.filas_originales = [dict(fila) for fila in self.filas]
        self.cambios = set()

        self.filtro = ft.TextField(
            label="Buscar en esta tabla",
            prefix_icon=ft.Icons.SEARCH,
            dense=True,
            expand=True,
            on_change=lambda e: self._refrescar_tabla(),
        )
        self.estado_cambios = ft.Text("", color=COLOR_TEXTO_SUAVE)
        self.mensaje = ft.Text("", color="primary")
        self.contenedor_tabla = ft.Row(
            [self._construir_tabla()],
            scroll=ft.ScrollMode.ALWAYS,
            vertical_alignment=ft.CrossAxisAlignment.START,
        )
        self._actualizar_estado_cambios()

        self.controls = [
            ft.Row(
                [
                    ft.IconButton(ft.Icons.ARROW_BACK, tooltip="Volver", on_click=lambda e: self.on_volver()),
                    ft.Text(os.path.basename(ruta), size=20, weight=ft.FontWeight.BOLD),
                    ft.Container(expand=True),
                    ft.ElevatedButton("Agregar plantilla", icon=ft.Icons.CONTENT_COPY, on_click=self._agregar_desde_plantilla),
                    ft.ElevatedButton("Agregar vacía", icon=ft.Icons.ADD, on_click=self._agregar_fila),
                    ft.ElevatedButton("Guardar", icon=ft.Icons.SAVE, on_click=self._guardar),
                ]
            ),
            ft.Container(
                padding=12,
                bgcolor=COLOR_PANEL_EDITOR,
                border_radius=8,
                border=ft.border.all(1, COLOR_BORDE_EDITOR),
                content=ft.Row([self.filtro, self.estado_cambios], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            ),
            self.mensaje,
            ft.Container(
                content=self.contenedor_tabla,
                expand=True,
                padding=8,
                bgcolor=COLOR_PANEL_EDITOR,
                border=ft.border.all(1, COLOR_BORDE_EDITOR),
                border_radius=8,
            ),
        ]

    def _filas_visibles(self):
        texto = (self.filtro.value or "").strip().lower() if hasattr(self, "filtro") else ""
        if not texto:
            return list(enumerate(self.filas))
        return [
            (idx, fila)
            for idx, fila in enumerate(self.filas)
            if texto in " ".join(str(fila.get(h, "")) for h in self.encabezados).lower()
        ]

    def _anchos_columnas(self):
        """Ancho por columna según el contenido más largo que tenga (encabezado o celdas)."""
        anchos = {}
        for h in self.encabezados:
            largo = len(h)
            for fila in self.filas:
                largo = max(largo, len(fila.get(h, "") or ""))
            maximo = ANCHO_MAX_TEXTO_LARGO if self._es_columna_texto_largo(h) else ANCHO_MAX_COLUMNA
            anchos[h] = min(maximo, max(ANCHO_MIN_COLUMNA, largo * 10 + 48))
        return anchos

    def _es_columna_texto_largo(self, encabezado):
        nombre = encabezado.lower()
        return any(palabra in nombre for palabra in COLUMNAS_TEXTO_LARGO)

    def _celda_modificada(self, idx, encabezado):
        if idx >= len(self.filas_originales):
            return True
        return self.filas[idx].get(encabezado, "") != self.filas_originales[idx].get(encabezado, "")

    def _registrar_cambio(self, idx, encabezado):
        clave = (idx, encabezado)
        if self._celda_modificada(idx, encabezado):
            self.cambios.add(clave)
        else:
            self.cambios.discard(clave)

    def _actualizar_estado_cambios(self):
        visibles = len(self._filas_visibles())
        total = len(self.filas)
        pendientes = len(self.cambios)
        if pendientes:
            self.estado_cambios.value = f"{visibles}/{total} filas visibles · {pendientes} celdas modificadas sin guardar"
            self.estado_cambios.color = "secondary"
        else:
            self.estado_cambios.value = f"{visibles}/{total} filas visibles · sin cambios pendientes"
            self.estado_cambios.color = COLOR_TEXTO_SUAVE

    def _construir_tabla(self):
        anchos = self._anchos_columnas()
        columnas = [
            ft.DataColumn(
                ft.Container(
                    width=anchos[h],
                    padding=ft.padding.symmetric(vertical=4),
                    content=ft.Text(h, weight=ft.FontWeight.BOLD, color="primary"),
                )
            )
            for h in self.encabezados
        ]
        columnas.append(ft.DataColumn(ft.Text("")))

        filas_ui = []
        for posicion, (idx, fila) in enumerate(self._filas_visibles()):
            celdas = []
            for h in self.encabezados:
                es_texto_largo = self._es_columna_texto_largo(h)
                modificada = self._celda_modificada(idx, h)
                campo = ft.TextField(
                    value=fila.get(h, ""),
                    dense=False,
                    width=anchos[h],
                    multiline=es_texto_largo,
                    min_lines=2 if es_texto_largo else 1,
                    max_lines=6 if es_texto_largo else 1,
                    text_size=13,
                    border=ft.InputBorder.OUTLINE,
                    border_radius=6,
                    border_width=1,
                    border_color=COLOR_BORDE_EDITADO if modificada else COLOR_BORDE_EDITOR,
                    focused_border_color="primary",
                    focused_border_width=2,
                    filled=True,
                    fill_color=COLOR_CELDA_EDITADA if modificada else "surface",
                    suffix_icon=ft.Icons.EDIT if modificada else None,
                    content_padding=ft.padding.symmetric(horizontal=10, vertical=8),
                    on_change=lambda e, i=idx, hh=h: self._editar_celda(i, hh, e.control),
                )
                celdas.append(ft.DataCell(campo))
            celdas.append(
                ft.DataCell(
                    ft.Row(
                        [
                            ft.IconButton(
                                ft.Icons.CONTENT_COPY,
                                tooltip="Duplicar fila",
                                on_click=lambda e, i=idx: self._duplicar_fila(i),
                            ),
                            ft.IconButton(
                                ft.Icons.DELETE_OUTLINE,
                                icon_color="error",
                                tooltip="Eliminar fila",
                                on_click=lambda e, i=idx: self._eliminar_fila(i),
                            ),
                        ],
                        spacing=0,
                    )
                )
            )
            filas_ui.append(
                ft.DataRow(
                    cells=celdas,
                    color=COLOR_FILA_PAR if posicion % 2 == 0 else COLOR_FILA_IMPAR,
                )
            )

        if not filas_ui:
            return ft.Container(
                width=600,
                padding=24,
                alignment=ft.alignment.center,
                content=ft.Text("No hay filas con esos filtros.", color=COLOR_TEXTO_SUAVE),
            )

        return ft.DataTable(
            columns=columnas,
            rows=filas_ui,
            heading_row_color=COLOR_CABECERA_TABLA,
            heading_row_height=48,
            data_row_min_height=58,
            data_row_max_height=170,
            column_spacing=14,
            horizontal_margin=12,
            divider_thickness=0.5,
            show_bottom_border=True,
            bgcolor="surface",
            border=ft.border.all(1, COLOR_BORDE_EDITOR),
            border_radius=8,
            vertical_lines=ft.BorderSide(1, COLOR_BORDE_EDITOR),
            horizontal_lines=ft.BorderSide(1, COLOR_BORDE_EDITOR),
        )

    def _editar_celda(self, idx, encabezado, control):
        valor = control.value
        self.filas[idx][encabezado] = valor
        self._registrar_cambio(idx, encabezado)
        modificada = self._celda_modificada(idx, encabezado)
        control.border_color = COLOR_BORDE_EDITADO if modificada else COLOR_BORDE_EDITOR
        control.fill_color = COLOR_CELDA_EDITADA if modificada else "surface"
        control.suffix_icon = ft.Icons.EDIT if modificada else None
        control.update()
        self._actualizar_estado_cambios()
        self.estado_cambios.update()

    def _refrescar_tabla(self):
        self._actualizar_estado_cambios()
        self.contenedor_tabla.controls = [self._construir_tabla()]
        self.update()

    def _agregar_fila(self, e):
        self.filas.append({h: "" for h in self.encabezados})
        nuevo_idx = len(self.filas) - 1
        for h in self.encabezados:
            self.cambios.add((nuevo_idx, h))
        self._refrescar_tabla()

    def _agregar_desde_plantilla(self, e):
        if self.filas:
            self.filas.append(dict(self.filas[-1]))
        else:
            self.filas.append({h: "" for h in self.encabezados})
        nuevo_idx = len(self.filas) - 1
        for h in self.encabezados:
            self.cambios.add((nuevo_idx, h))
        self._refrescar_tabla()

    def _duplicar_fila(self, idx):
        self.filas.insert(idx + 1, dict(self.filas[idx]))
        self.cambios = set()
        for i, fila in enumerate(self.filas):
            for h in self.encabezados:
                if i >= len(self.filas_originales) or fila.get(h, "") != self.filas_originales[i].get(h, ""):
                    self.cambios.add((i, h))
        self._refrescar_tabla()

    def _eliminar_fila(self, idx):
        self.filas.pop(idx)
        self.cambios = set()
        for i, fila in enumerate(self.filas):
            for h in self.encabezados:
                if i >= len(self.filas_originales) or fila.get(h, "") != self.filas_originales[i].get(h, ""):
                    self.cambios.add((i, h))
        self._refrescar_tabla()

    def _guardar(self, e):
        try:
            escribir_csv(self.ruta, self.encabezados, self.filas)
            self.filas_originales = [dict(fila) for fila in self.filas]
            self.cambios.clear()
            self.mensaje.value = f"Guardado: {len(self.filas)} filas."
            self.mensaje.color = "primary"
        except Exception as ex:
            self.mensaje.value = f"Error al guardar: {ex}"
            self.mensaje.color = "error"
        self._refrescar_tabla()


class EditorTraducciones(ft.Column):
    def __init__(self, on_volver):
        super().__init__(expand=True, spacing=12)
        self.on_volver = on_volver
        self.ruta_es = os.path.join(CARPETA_LOCALES, "es.json")
        self.ruta_en = os.path.join(CARPETA_LOCALES, "en.json")
        self.es = aplanar_json(leer_json(self.ruta_es))
        self.en = aplanar_json(leer_json(self.ruta_en))
        self.claves = sorted(set(self.es) | set(self.en))
        self.grupos = self._calcular_grupos()
        grupo_inicial = "ui.tab_dps" if "ui.tab_dps" in self.grupos else (self.grupos[0] if self.grupos else "__all__")
        self.filtro = ft.TextField(
            label="Buscar dentro de traducciones",
            prefix_icon=ft.Icons.SEARCH,
            dense=True,
            expand=True,
            on_change=lambda e: self._refrescar_tabla(),
        )
        self.selector_grupo = ft.Dropdown(
            label="Seccion",
            value=grupo_inicial,
            width=300,
            dense=True,
            options=[
                ft.dropdown.Option(key="__all__", text=f"Todas ({len(self.claves)})"),
                *[
                    ft.dropdown.Option(key=grupo, text=f"{grupo.replace('.', ' > ')} ({self._contar_grupo(grupo)})")
                    for grupo in self.grupos
                ],
            ],
            on_change=lambda e: self._refrescar_tabla(),
        )
        self.solo_pendientes = ft.Checkbox(
            label="Solo pendientes",
            value=False,
            on_change=lambda e: self._refrescar_tabla(),
        )
        self.nueva_clave = ft.TextField(
            label="Nuevo campo en la seccion seleccionada",
            dense=True,
            expand=True,
        )
        self.resumen = ft.Text("")
        self.mensaje = ft.Text("")
        self.contenedor_tabla = ft.Column([self._construir_lista()], expand=True, scroll=ft.ScrollMode.ALWAYS)
        self._actualizar_resumen()
        self.controls = [
            ft.Row(
                [
                    ft.IconButton(ft.Icons.ARROW_BACK, tooltip="Volver", on_click=lambda e: self.on_volver()),
                    ft.Text("Traducciones", size=20, weight=ft.FontWeight.BOLD),
                    ft.Container(expand=True),
                    ft.ElevatedButton("Guardar", icon=ft.Icons.SAVE, on_click=self._guardar),
                ]
            ),
            ft.Text("Trabaja por secciones para mantener contexto. Las claves nuevas se crean en español e ingles."),
            ft.Row([self.selector_grupo, self.filtro, self.solo_pendientes], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            self.resumen,
            ft.Row([self.nueva_clave, ft.ElevatedButton("Agregar en esta seccion", icon=ft.Icons.ADD, on_click=self._agregar_clave)]),
            self.mensaje,
            ft.Container(content=self.contenedor_tabla, expand=True),
        ]

    def _calcular_grupos(self):
        grupos = sorted({".".join(clave.split(".")[:-1]) for clave in self.claves if "." in clave})
        return [g for g in grupos if g]

    def _contar_grupo(self, grupo):
        prefijo = f"{grupo}."
        return sum(1 for clave in self.claves if clave.startswith(prefijo))

    def _grupo_actual(self):
        return self.selector_grupo.value or "__all__"

    def _campo_corto(self, clave):
        return clave.split(".")[-1]

    def _grupo_de_clave(self, clave):
        partes = clave.split(".")
        return ".".join(partes[:-1]) if len(partes) > 1 else ""

    def _esta_pendiente(self, clave):
        return not (self.es.get(clave, "").strip() and self.en.get(clave, "").strip())

    def _claves_visibles(self):
        texto = (self.filtro.value or "").strip().lower()
        grupo = self._grupo_actual()
        claves = self.claves
        if grupo != "__all__":
            prefijo = f"{grupo}."
            claves = [clave for clave in claves if clave.startswith(prefijo)]
        if self.solo_pendientes.value:
            claves = [clave for clave in claves if self._esta_pendiente(clave)]
        if texto:
            claves = [
                clave for clave in claves
                if texto in clave.lower()
                or texto in self.es.get(clave, "").lower()
                or texto in self.en.get(clave, "").lower()
            ]
        return claves

    def _construir_lista(self):
        tarjetas = []
        for clave in self._claves_visibles():
            pendiente = self._esta_pendiente(clave)
            tarjetas.append(
                ft.Container(
                    padding=12,
                    border=ft.border.all(1, ft.Colors.RED_200 if pendiente else ft.Colors.GREY_300),
                    border_radius=8,
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Column(
                                        [
                                            ft.Text(self._campo_corto(clave), size=16, weight=ft.FontWeight.BOLD),
                                            ft.Text(self._grupo_de_clave(clave), size=12, color=ft.Colors.GREY_600),
                                        ],
                                        spacing=2,
                                        expand=True,
                                    ),
                                    ft.Text("Pendiente" if pendiente else "Completa", color=ft.Colors.RED_400 if pendiente else ft.Colors.GREEN_500),
                                    ft.IconButton(ft.Icons.CONTENT_COPY, tooltip="Copiar ES a EN", on_click=lambda e, k=clave: self._copiar_es_a_en(k)),
                                    ft.IconButton(ft.Icons.DELETE_OUTLINE, icon_color=ft.Colors.RED_300, tooltip="Eliminar clave", on_click=lambda e, k=clave: self._eliminar_clave(k)),
                                ],
                                vertical_alignment=ft.CrossAxisAlignment.START,
                            ),
                            ft.Row(
                                [
                                    ft.TextField(
                                        label="Español",
                                        value=self.es.get(clave, ""),
                                        dense=True,
                                        expand=True,
                                        multiline=True,
                                        min_lines=1,
                                        max_lines=5,
                                        on_change=lambda e, k=clave: self._editar("es", k, e.control.value),
                                    ),
                                    ft.TextField(
                                        label="English",
                                        value=self.en.get(clave, ""),
                                        dense=True,
                                        expand=True,
                                        multiline=True,
                                        min_lines=1,
                                        max_lines=5,
                                        on_change=lambda e, k=clave: self._editar("en", k, e.control.value),
                                    ),
                                ]
                            ),
                        ],
                        spacing=8,
                    ),
                )
            )
        if not tarjetas:
            return ft.Container(
                padding=24,
                alignment=ft.alignment.center,
                content=ft.Text("No hay claves con esos filtros.", color=ft.Colors.GREY_600),
            )
        return ft.Column(tarjetas, spacing=10)

    def _editar(self, idioma, clave, valor):
        destino = self.es if idioma == "es" else self.en
        destino[clave] = valor

    def _actualizar_resumen(self):
        visibles = self._claves_visibles()
        pendientes = sum(1 for clave in visibles if self._esta_pendiente(clave))
        grupo = self._grupo_actual()
        nombre_grupo = "todas las secciones" if grupo == "__all__" else grupo.replace(".", " > ")
        self.resumen.value = f"{len(visibles)} claves en {nombre_grupo}. Pendientes: {pendientes}."

    def _refrescar_tabla(self):
        self._actualizar_resumen()
        self.contenedor_tabla.controls = [self._construir_lista()]
        self.update()

    def _normalizar_nueva_clave(self, texto):
        texto = (texto or "").strip().replace(" ", "_")
        texto = re.sub(r"[^A-Za-z0-9_.-]+", "_", texto)
        texto = texto.strip("._")
        if not texto:
            return ""
        if "." in texto:
            return texto
        grupo = self._grupo_actual()
        if grupo == "__all__":
            grupo = self.grupos[0] if self.grupos else "ui"
        return f"{grupo}.{texto}"

    def _agregar_clave(self, e):
        clave = self._normalizar_nueva_clave(self.nueva_clave.value)
        if not clave or "." not in clave:
            self.mensaje.value = "Escribe un nombre de campo o una clave completa."
            self.mensaje.color = ft.Colors.RED_400
            self.update()
            return
        if clave not in self.claves:
            self.claves.append(clave)
            self.claves.sort()
            grupo = self._grupo_de_clave(clave)
            if grupo and grupo not in self.grupos:
                self.grupos = self._calcular_grupos()
                self.selector_grupo.options = [
                    ft.dropdown.Option(key="__all__", text=f"Todas ({len(self.claves)})"),
                    *[
                        ft.dropdown.Option(key=g, text=f"{g.replace('.', ' > ')} ({self._contar_grupo(g)})")
                        for g in self.grupos
                    ],
                ]
        self.es.setdefault(clave, "")
        self.en.setdefault(clave, "")
        self.selector_grupo.value = self._grupo_de_clave(clave)
        self.nueva_clave.value = ""
        self.mensaje.value = f"Clave agregada: {clave}"
        self.mensaje.color = ft.Colors.GREEN_400
        self._refrescar_tabla()

    def _copiar_es_a_en(self, clave):
        self.en[clave] = self.es.get(clave, "")
        self.mensaje.value = f"Copiado ES -> EN: {clave}"
        self.mensaje.color = ft.Colors.GREEN_400
        self._refrescar_tabla()

    def _eliminar_clave(self, clave):
        if clave in self.claves:
            self.claves.remove(clave)
        self.es.pop(clave, None)
        self.en.pop(clave, None)
        self.grupos = self._calcular_grupos()
        self._refrescar_tabla()

    def _guardar(self, e):
        try:
            escribir_json(self.ruta_es, expandir_json(self.es))
            escribir_json(self.ruta_en, expandir_json(self.en))
            self.mensaje.value = "Traducciones guardadas."
            self.mensaje.color = ft.Colors.GREEN_400
        except Exception as ex:
            self.mensaje.value = f"Error al guardar traducciones: {ex}"
            self.mensaje.color = ft.Colors.RED_400
        self.update()


class EditorMappingsEnka(ft.Column):
    def __init__(self, on_volver):
        super().__init__(expand=True, spacing=12)
        self.on_volver = on_volver
        avatares, sets = cargar_mappings_enka()
        self.mappings = {
            "avatares": [{"id": str(k), "nombre": v} for k, v in sorted(avatares.items())],
            "sets": [{"id": str(k), "nombre": v} for k, v in sorted(sets.items())],
        }
        self.tipo = ft.SegmentedButton(
            selected={"avatares"},
            segments=[
                ft.Segment(value="avatares", label=ft.Text("Agentes"), icon=ft.Icon(ft.Icons.PERSON)),
                ft.Segment(value="sets", label=ft.Text("Sets"), icon=ft.Icon(ft.Icons.ALBUM)),
            ],
            on_change=lambda e: self._refrescar(),
        )
        self.filtro = ft.TextField(
            label="Buscar ID o nombre",
            prefix_icon=ft.Icons.SEARCH,
            dense=True,
            expand=True,
            on_change=lambda e: self._refrescar(),
        )
        self.nuevo_id = ft.TextField(label="ID Enka", dense=True, width=150)
        self.nuevo_nombre = ft.TextField(label="Nombre local", dense=True, expand=True)
        self.mensaje = ft.Text("")
        self.resumen = ft.Text("")
        self.lista = ft.Column(expand=True, scroll=ft.ScrollMode.ALWAYS)
        self._refrescar(actualizar=False)
        self.controls = [
            ft.Row(
                [
                    ft.IconButton(ft.Icons.ARROW_BACK, tooltip="Volver", on_click=lambda e: self.on_volver()),
                    ft.Text("Mappings Enka", size=20, weight=ft.FontWeight.BOLD),
                    ft.Container(expand=True),
                    ft.ElevatedButton("Guardar", icon=ft.Icons.SAVE, on_click=self._guardar),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            ft.Container(
                padding=12,
                bgcolor=COLOR_PANEL_EDITOR,
                border=ft.border.all(1, COLOR_BORDE_EDITOR),
                border_radius=8,
                content=ft.Column(
                    [
                        ft.Row([self.tipo, self.filtro], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                        self.resumen,
                        ft.Row(
                            [
                                self.nuevo_id,
                                self.nuevo_nombre,
                                ft.IconButton(ft.Icons.ADD, tooltip="Agregar mapping", on_click=self._agregar),
                            ],
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                    ],
                    spacing=10,
                ),
            ),
            self.mensaje,
            ft.Container(content=self.lista, expand=True),
        ]

    def _tipo_actual(self):
        return next(iter(self.tipo.selected or {"avatares"}))

    def _filas_actuales(self):
        return self.mappings[self._tipo_actual()]

    def _filas_visibles(self):
        texto = (self.filtro.value or "").strip().lower()
        filas = self._filas_actuales()
        if not texto:
            return list(enumerate(filas))
        return [
            (idx, fila)
            for idx, fila in enumerate(filas)
            if texto in fila["id"].lower() or texto in fila["nombre"].lower()
        ]

    def _validar_filas(self):
        errores = []
        for tipo, filas in self.mappings.items():
            ids = {}
            nombres = {}
            for idx, fila in enumerate(filas):
                id_txt = fila["id"].strip()
                nombre = fila["nombre"].strip()
                if not id_txt or not id_txt.isdigit():
                    errores.append(f"{tipo}: ID inválido en fila {idx + 1}.")
                    continue
                if not nombre:
                    errores.append(f"{tipo}: nombre vacío para ID {id_txt}.")
                if id_txt in ids:
                    errores.append(f"{tipo}: ID duplicado {id_txt}.")
                ids[id_txt] = idx
                clave_nombre = nombre.lower()
                if clave_nombre and clave_nombre in nombres:
                    errores.append(f"{tipo}: nombre duplicado {nombre}.")
                nombres[clave_nombre] = idx
        return errores

    def _actualizar_resumen(self):
        visibles = len(self._filas_visibles())
        total = len(self._filas_actuales())
        errores = len(self._validar_filas())
        self.resumen.value = f"{visibles}/{total} mappings visibles · {errores} problemas"
        self.resumen.color = "error" if errores else COLOR_TEXTO_SUAVE

    def _editar(self, idx, campo, valor):
        self._filas_actuales()[idx][campo] = valor
        self._actualizar_resumen()
        self.resumen.update()

    def _eliminar(self, idx):
        self._filas_actuales().pop(idx)
        self._refrescar()

    def _agregar(self, e):
        id_txt = (self.nuevo_id.value or "").strip()
        nombre = (self.nuevo_nombre.value or "").strip()
        if not id_txt or not nombre:
            self.mensaje.value = "Escribe ID y nombre local."
            self.mensaje.color = "error"
            self.update()
            return
        self._filas_actuales().append({"id": id_txt, "nombre": nombre})
        self._filas_actuales().sort(key=lambda f: int(f["id"]) if f["id"].isdigit() else 10**9)
        self.nuevo_id.value = ""
        self.nuevo_nombre.value = ""
        self.mensaje.value = f"Mapping agregado: {id_txt} -> {nombre}"
        self.mensaje.color = "primary"
        self._refrescar()

    def _construir_lista(self):
        controles = []
        for idx, fila in self._filas_visibles():
            controles.append(
                ft.Container(
                    padding=10,
                    bgcolor=COLOR_PANEL_EDITOR,
                    border=ft.border.all(1, COLOR_BORDE_EDITOR),
                    border_radius=8,
                    content=ft.Row(
                        [
                            ft.TextField(
                                value=fila["id"],
                                label="ID",
                                dense=True,
                                width=150,
                                keyboard_type=ft.KeyboardType.NUMBER,
                                on_change=lambda e, i=idx: self._editar(i, "id", e.control.value),
                            ),
                            ft.TextField(
                                value=fila["nombre"],
                                label="Nombre local",
                                dense=True,
                                expand=True,
                                on_change=lambda e, i=idx: self._editar(i, "nombre", e.control.value),
                            ),
                            ft.IconButton(
                                ft.Icons.DELETE_OUTLINE,
                                icon_color="error",
                                tooltip="Eliminar mapping",
                                on_click=lambda e, i=idx: self._eliminar(i),
                            ),
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                )
            )
        if not controles:
            return ft.Container(
                padding=24,
                alignment=ft.alignment.center,
                bgcolor=COLOR_PANEL_EDITOR,
                border=ft.border.all(1, COLOR_BORDE_EDITOR),
                border_radius=8,
                content=ft.Text("No hay mappings con ese filtro.", color=COLOR_TEXTO_SUAVE),
            )
        return ft.Column(controles, spacing=8)

    def _refrescar(self, actualizar=True):
        self._actualizar_resumen()
        self.lista.controls = [self._construir_lista()]
        if actualizar:
            self.update()

    def _guardar(self, e):
        errores = self._validar_filas()
        if errores:
            self.mensaje.value = errores[0]
            self.mensaje.color = "error"
            self.update()
            return
        avatares = {int(f["id"]): f["nombre"].strip() for f in self.mappings["avatares"]}
        sets = {int(f["id"]): f["nombre"].strip() for f in self.mappings["sets"]}
        try:
            guardar_mappings_enka(avatares, sets)
            self.mensaje.value = "Mappings Enka guardados en datos/enka_mappings.json."
            self.mensaje.color = "primary"
        except Exception as ex:
            self.mensaje.value = f"Error al guardar mappings: {ex}"
            self.mensaje.color = "error"
        self.update()


class EditorFormulasDano(ft.Column):
    def __init__(self, on_volver):
        super().__init__(expand=True, spacing=12)
        self.on_volver = on_volver
        self.formulas = cargar_formulas_dano()
        self.mensaje = ft.Text("")
        self.lista = ft.Column(expand=True, scroll=ft.ScrollMode.ALWAYS)
        self.resumen = ft.Text("")
        self._refrescar(actualizar=False)
        self.controls = [
            ft.Row(
                [
                    ft.IconButton(ft.Icons.ARROW_BACK, tooltip="Volver", on_click=lambda e: self.on_volver()),
                    ft.Text("Formulas de daño", size=20, weight=ft.FontWeight.BOLD),
                    ft.Container(expand=True),
                    ft.ElevatedButton("Guardar", icon=ft.Icons.SAVE, on_click=self._guardar),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            ft.Container(
                padding=12,
                bgcolor=COLOR_PANEL_EDITOR,
                border=ft.border.all(1, COLOR_BORDE_EDITOR),
                border_radius=8,
                content=ft.Row(
                    [
                        ft.Icon(ft.Icons.CALCULATE, color="primary"),
                        ft.Column(
                            [
                                ft.Text("Vortex", weight=ft.FontWeight.BOLD),
                                self.resumen,
                            ],
                            spacing=2,
                            expand=True,
                        ),
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
            ),
            self.mensaje,
            ft.Container(content=self.lista, expand=True),
        ]

    def _vortex(self):
        return self.formulas.setdefault("vortex", {})

    def _actualizar_resumen(self):
        self.resumen.value = f"{len(self._vortex())} elementos configurados · base%, tick%, segundos por tick e intervalos"
        self.resumen.color = COLOR_TEXTO_SUAVE

    def _parse_numero(self, valor, default=0.0):
        try:
            return float(str(valor).replace(",", "."))
        except (TypeError, ValueError):
            return default

    def _editar(self, elemento, campo, valor):
        formula = self._vortex().setdefault(elemento, {})
        if campo == "usar_intervalos":
            formula[campo] = bool(valor)
        else:
            formula[campo] = self._parse_numero(valor, formula.get(campo, 0.0))

    def _construir_lista(self):
        controles = []
        for elemento, formula in sorted(self._vortex().items()):
            controles.append(
                ft.Container(
                    padding=12,
                    bgcolor=COLOR_PANEL_EDITOR,
                    border=ft.border.all(1, COLOR_BORDE_EDITOR),
                    border_radius=8,
                    content=ft.Row(
                        [
                            ft.Text(elemento.title(), width=110, weight=ft.FontWeight.BOLD, color="primary"),
                            ft.TextField(
                                label="Base %",
                                value=str(formula.get("base_pct", 0)),
                                dense=True,
                                width=120,
                                keyboard_type=ft.KeyboardType.NUMBER,
                                on_change=lambda e, el=elemento: self._editar(el, "base_pct", e.control.value),
                            ),
                            ft.TextField(
                                label="Tick %",
                                value=str(formula.get("tick_pct", 0)),
                                dense=True,
                                width=120,
                                keyboard_type=ft.KeyboardType.NUMBER,
                                on_change=lambda e, el=elemento: self._editar(el, "tick_pct", e.control.value),
                            ),
                            ft.TextField(
                                label="Seg/tick",
                                value=str(formula.get("tick_seg", 1)),
                                dense=True,
                                width=120,
                                keyboard_type=ft.KeyboardType.NUMBER,
                                on_change=lambda e, el=elemento: self._editar(el, "tick_seg", e.control.value),
                            ),
                            ft.Checkbox(
                                label="Por intervalos",
                                value=bool(formula.get("usar_intervalos", False)),
                                on_change=lambda e, el=elemento: self._editar(el, "usar_intervalos", e.control.value),
                            ),
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                )
            )
        return ft.Column(controles, spacing=8)

    def _refrescar(self, actualizar=True):
        self._actualizar_resumen()
        self.lista.controls = [self._construir_lista()]
        if actualizar:
            self.update()

    def _guardar(self, e):
        try:
            guardar_formulas_dano(self.formulas)
            self.mensaje.value = "Formulas guardadas en datos/formulas_dano.json."
            self.mensaje.color = "primary"
        except Exception as ex:
            self.mensaje.value = f"Error al guardar formulas: {ex}"
            self.mensaje.color = "error"
        self.update()


class GeneradorAgenteNuevo(ft.Column):
    def __init__(self, on_volver, abrir_ruta):
        super().__init__(expand=True, spacing=12)
        self.on_volver = on_volver
        self.abrir_ruta = abrir_ruta
        self.nombre = ft.TextField(label="Nombre", dense=True, expand=True)
        self.elemento = ft.Dropdown(
            label="Elemento",
            value="Físico",
            dense=True,
            width=180,
            options=[ft.dropdown.Option(v) for v in ["Físico", "Fuego", "Hielo", "Electrico", "Etereo", "Frost", "Viento"]],
        )
        self.tipo = ft.Dropdown(
            label="Tipo",
            value="Atacante",
            dense=True,
            width=180,
            options=[ft.dropdown.Option(v) for v in ["Atacante", "Aturdidor", "Anomalo", "Soporte", "Defensor", "Ruptura"]],
        )
        self.rango = ft.Dropdown(
            label="Rango",
            value="S",
            dense=True,
            width=120,
            options=[ft.dropdown.Option("S"), ft.dropdown.Option("A")],
        )
        self.mensaje = ft.Text("")
        self.controls = [
            ft.Row(
                [
                    ft.IconButton(ft.Icons.ARROW_BACK, tooltip="Volver", on_click=lambda e: self.on_volver()),
                    ft.Text("Nuevo agente", size=20, weight=ft.FontWeight.BOLD),
                    ft.Container(expand=True),
                    ft.ElevatedButton("Crear", icon=ft.Icons.ADD, on_click=self._crear),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            ft.Container(
                padding=12,
                bgcolor=COLOR_PANEL_EDITOR,
                border=ft.border.all(1, COLOR_BORDE_EDITOR),
                border_radius=8,
                content=ft.Column(
                    [
                        ft.Row([self.nombre, self.elemento, self.tipo, self.rango], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                        ft.Text("Usa valores base editables; despues abre Agentes para ajustar stats finos.", color=COLOR_TEXTO_SUAVE),
                    ],
                    spacing=10,
                ),
            ),
            self.mensaje,
        ]

    def _fila_base(self, nombre):
        encabezados, filas = leer_csv(RUTA_AGENTES)
        plantilla = filas[0] if filas else {}
        fila = {h: plantilla.get(h, "") for h in encabezados}
        defaults = {
            "Nombre": nombre,
            "probabilidad": "5",
            "daño crítico": "50",
            "Tasa de perforación": "0",
            "Maestría de anomalía": "93",
            "Perforación plana": "0",
            "elemento": self.elemento.value,
            "daño elemental": "0",
            "Tipo": self.tipo.value,
            "ataque": "700",
            "puntos de vida": "7500",
            "defensa": "600",
            "tasa de anomalía": "90",
            "Impacto": "90",
            "Recuperación de energía": "1,2",
            "nivel": "60",
            "Aturdimiento": "0",
            "Facción": "",
            "Rango": self.rango.value,
        }
        for clave, valor in defaults.items():
            if clave in fila:
                fila[clave] = valor
        return encabezados, filas, fila

    def _crear(self, e):
        nombre = nombre_archivo_seguro(self.nombre.value or "")
        if not nombre:
            self.mensaje.value = "Escribe el nombre del agente."
            self.mensaje.color = "error"
            self.update()
            return
        encabezados, filas, fila_nueva = self._fila_base(nombre)
        if not encabezados:
            self.mensaje.value = "No pude leer datos/agentes.csv."
            self.mensaje.color = "error"
            self.update()
            return
        if any(_normalizar_nombre(f.get("Nombre")) == _normalizar_nombre(nombre) for f in filas):
            self.mensaje.value = f"{nombre} ya existe en agentes.csv."
            self.mensaje.color = "error"
            self.update()
            return
        filas.append(fila_nueva)
        escribir_csv(RUTA_AGENTES, encabezados, filas)
        ruta_habilidades = os.path.join(CARPETA_PERSONAJES, f"{nombre}.csv")
        if not os.path.exists(ruta_habilidades):
            crear_csv_personaje(nombre)
        self.mensaje.value = f"Agente creado: {nombre}. Abriendo agentes.csv para ajustar stats."
        self.mensaje.color = "primary"
        self.update()
        self.abrir_ruta(RUTA_AGENTES)


class EditorTextoSimple(ft.Column):
    def __init__(self, ruta, on_volver):
        super().__init__(expand=True, spacing=12)
        self.ruta = ruta
        self.on_volver = on_volver
        self.editor = ft.TextField(
            value=leer_texto(ruta),
            multiline=True,
            min_lines=30,
            max_lines=30,
            text_size=13,
            expand=True,
            border=ft.InputBorder.OUTLINE,
        )
        self.mensaje = ft.Text("")
        self.controls = [
            ft.Row(
                [
                    ft.IconButton(ft.Icons.ARROW_BACK, tooltip="Volver", on_click=lambda e: self.on_volver()),
                    ft.Text(os.path.basename(ruta), size=20, weight=ft.FontWeight.BOLD),
                    ft.Container(expand=True),
                    ft.ElevatedButton("Guardar", icon=ft.Icons.SAVE, on_click=self._guardar),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            self.mensaje,
            ft.Container(
                content=self.editor,
                expand=True,
                padding=8,
                bgcolor=COLOR_PANEL_EDITOR,
                border=ft.border.all(1, COLOR_BORDE_EDITOR),
                border_radius=8,
            ),
        ]

    def _guardar(self, e):
        try:
            escribir_texto(self.ruta, self.editor.value or "")
            self.mensaje.value = f"Guardado: {self.ruta}"
            self.mensaje.color = "primary"
        except Exception as ex:
            self.mensaje.value = f"Error al guardar: {ex}"
            self.mensaje.color = "error"
        self.update()


class PanelEfectos(ft.Column):
    def __init__(self, on_volver, abrir_codigo):
        super().__init__(expand=True, spacing=12)
        self.on_volver = on_volver
        self.abrir_codigo = abrir_codigo
        self.resumen = ft.Text("")
        self.lista = ft.Column(expand=True, scroll=ft.ScrollMode.ALWAYS)
        self._refrescar(actualizar=False)
        self.controls = [
            ft.Row(
                [
                    ft.IconButton(ft.Icons.ARROW_BACK, tooltip="Volver", on_click=lambda e: self.on_volver()),
                    ft.Text("Efectos", size=20, weight=ft.FontWeight.BOLD),
                    ft.Container(expand=True),
                    ft.ElevatedButton("Refrescar", icon=ft.Icons.REFRESH, on_click=self._refrescar),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            ft.Container(
                padding=12,
                bgcolor=COLOR_PANEL_EDITOR,
                border=ft.border.all(1, COLOR_BORDE_EDITOR),
                border_radius=8,
                content=self.resumen,
            ),
            ft.Container(content=self.lista, expand=True),
        ]

    def _coverage(self):
        _, sets = leer_csv(RUTA_SETS)
        _, wengines = leer_csv(RUTA_WENGINE)
        nombres_sets = {(s.get("Nombre") or "").strip() for s in sets if (s.get("Nombre") or "").strip()}
        nombres_wengines = {(w.get("Nombre W-Engine") or "").strip() for w in wengines if (w.get("Nombre W-Engine") or "").strip()}
        try:
            from efectos_sets import CONFIG_SETS, MAPA_EFECTOS_SETS
        except Exception:
            CONFIG_SETS, MAPA_EFECTOS_SETS = {}, {}
        try:
            from efectos_wengines import CONFIG_WENGINES, MAPA_WENGINES
        except Exception:
            CONFIG_WENGINES, MAPA_WENGINES = {}, {}
        return {
            "sets_config": sorted(nombres_sets - set(CONFIG_SETS)),
            "sets_func": sorted(nombres_sets - set(MAPA_EFECTOS_SETS)),
            "wengines_config": sorted(nombres_wengines - set(CONFIG_WENGINES)),
            "wengines_func": sorted(nombres_wengines - set(MAPA_WENGINES)),
        }

    def _tarjeta_modulo(self, titulo, ruta, detalle):
        return ft.Container(
            padding=12,
            bgcolor=COLOR_PANEL_EDITOR,
            border=ft.border.all(1, COLOR_BORDE_EDITOR),
            border_radius=8,
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.CODE, color="primary"),
                    ft.Column(
                        [
                            ft.Text(titulo, weight=ft.FontWeight.BOLD),
                            ft.Text(detalle, color=COLOR_TEXTO_SUAVE),
                            ft.Text(ruta, color=COLOR_TEXTO_SUAVE, size=12),
                        ],
                        spacing=3,
                        expand=True,
                    ),
                    ft.IconButton(ft.Icons.OPEN_IN_NEW, tooltip="Abrir modulo", on_click=lambda e, r=ruta: self.abrir_codigo(r)),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )

    def _refrescar(self, e=None, actualizar=True):
        coverage = self._coverage()
        total_pendientes = sum(len(v) for v in coverage.values())
        self.resumen.value = f"{total_pendientes} pendientes detectados entre CSV y módulos de efectos"
        self.resumen.color = "secondary" if total_pendientes else "primary"
        self.lista.controls = [
            self._tarjeta_modulo(
                "Sets",
                "efectos_sets.py",
                f"Sin CONFIG: {len(coverage['sets_config'])} · sin función 4pc: {len(coverage['sets_func'])}",
            ),
            self._tarjeta_modulo(
                "W-Engines",
                "efectos_wengines.py",
                f"Sin CONFIG: {len(coverage['wengines_config'])} · sin función pasiva: {len(coverage['wengines_func'])}",
            ),
            self._tarjeta_modulo("Pasivas", "efectos_pasivas.py", "Pasivas por agente."),
            self._tarjeta_modulo("Mindscapes", "efectos_mindscapes.py", "Mindscapes por agente."),
            self._tarjeta_modulo("Core", "efectos_core.py", "Core skills por agente."),
            self._tarjeta_modulo("Potencial", "efectos_potencial.py", "Efectos de potencial."),
            self._tarjeta_modulo("Soportes", "efectos_soportes.py", "Agentes, sets y W-Engines de soporte."),
        ]
        if actualizar:
            self.update()


class ValidadorAssets(ft.Column):
    def __init__(self, on_volver, abrir_ruta):
        super().__init__(expand=True, spacing=12)
        self.on_volver = on_volver
        self.abrir_ruta = abrir_ruta
        self.problemas = []
        self.destino_imagen_pendiente = ""
        self.uploads_pendientes = {}
        self.file_picker = ft.FilePicker(
            on_result=self._copiar_imagen_seleccionada,
            on_upload=self._finalizar_upload_imagen,
        )
        self.mensaje = ft.Text("")
        self.filtro = ft.TextField(
            label="Buscar problema",
            prefix_icon=ft.Icons.SEARCH,
            dense=True,
            expand=True,
            on_change=lambda e: self._refrescar_lista(),
        )
        self.selector_severidad = ft.Dropdown(
            label="Severidad",
            value="todos",
            width=180,
            dense=True,
            options=[
                ft.dropdown.Option("todos", "Todas"),
                ft.dropdown.Option("error", "Errores"),
                ft.dropdown.Option("warning", "Avisos"),
                ft.dropdown.Option("info", "Info"),
            ],
            on_change=lambda e: self._refrescar_lista(),
        )
        self.selector_categoria = ft.Dropdown(
            label="Categoria",
            value="todos",
            width=240,
            dense=True,
            options=[ft.dropdown.Option("todos", "Todas")],
            on_change=lambda e: self._refrescar_lista(),
        )
        self.resumen = ft.Text("")
        self.lista = ft.Column(expand=True, scroll=ft.ScrollMode.ALWAYS)
        self._ejecutar_validacion(actualizar=False)
        self.controls = [
            ft.Row(
                [
                    ft.IconButton(ft.Icons.ARROW_BACK, tooltip="Volver", on_click=lambda e: self.on_volver()),
                    ft.Text("Validador de assets", size=20, weight=ft.FontWeight.BOLD),
                    ft.Container(expand=True),
                    ft.ElevatedButton("Refrescar", icon=ft.Icons.REFRESH, on_click=self._ejecutar_validacion),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            ft.Container(
                padding=12,
                bgcolor=COLOR_PANEL_EDITOR,
                border=ft.border.all(1, COLOR_BORDE_EDITOR),
                border_radius=8,
                content=ft.Column(
                    [
                        ft.Row([self.selector_severidad, self.selector_categoria, self.filtro]),
                        self.resumen,
                    ],
                    spacing=10,
                ),
            ),
            self.mensaje,
            ft.Container(content=self.lista, expand=True),
        ]

    def did_mount(self):
        if self.page and self.file_picker not in self.page.overlay:
            self.page.overlay.append(self.file_picker)
            self.page.update()

    def _ejecutar_validacion(self, e=None, actualizar=True):
        self.problemas = validar_assets_y_datos()
        categorias = sorted({p.categoria for p in self.problemas})
        categoria_actual = self.selector_categoria.value if hasattr(self, "selector_categoria") else "todos"
        self.selector_categoria.options = [
            ft.dropdown.Option("todos", "Todas"),
            *[ft.dropdown.Option(cat, cat) for cat in categorias],
        ]
        self.selector_categoria.value = categoria_actual if categoria_actual in {"todos", *categorias} else "todos"
        self._refrescar_lista(actualizar=False)
        if actualizar:
            self.update()

    def _problemas_visibles(self):
        texto = (self.filtro.value or "").strip().lower()
        severidad = self.selector_severidad.value or "todos"
        categoria = self.selector_categoria.value or "todos"
        problemas = self.problemas
        if severidad != "todos":
            problemas = [p for p in problemas if p.severidad == severidad]
        if categoria != "todos":
            problemas = [p for p in problemas if p.categoria == categoria]
        if texto:
            problemas = [
                p for p in problemas
                if texto in " ".join([p.severidad, p.categoria, p.titulo, p.detalle, p.ruta]).lower()
            ]
        return problemas

    def _actualizar_resumen(self, visibles):
        errores = sum(1 for p in self.problemas if p.severidad == "error")
        avisos = sum(1 for p in self.problemas if p.severidad == "warning")
        info = sum(1 for p in self.problemas if p.severidad == "info")
        color = "error" if errores else ("secondary" if avisos else "primary")
        self.resumen.value = f"{len(visibles)}/{len(self.problemas)} visibles · {errores} errores · {avisos} avisos · {info} info"
        self.resumen.color = color

    def _color_severidad(self, severidad):
        return {
            "error": "error",
            "warning": "secondary",
            "info": "primary",
        }.get(severidad, COLOR_TEXTO_SUAVE)

    def _icono_severidad(self, severidad):
        return {
            "error": ft.Icons.ERROR_OUTLINE,
            "warning": ft.Icons.WARNING_AMBER_ROUNDED,
            "info": ft.Icons.INFO_OUTLINE,
        }.get(severidad, ft.Icons.INFO_OUTLINE)

    def _abrir_destino(self, ruta):
        if ruta.endswith(".csv"):
            self.abrir_ruta(ruta)

    def _seleccionar_imagen(self, destino):
        self.destino_imagen_pendiente = destino
        self.file_picker.pick_files(
            allow_multiple=False,
            file_type=ft.FilePickerFileType.IMAGE,
            allowed_extensions=["png", "jpg", "jpeg", "webp"],
            dialog_title=f"Selecciona imagen para {destino}",
        )

    def _copiar_imagen_seleccionada(self, e):
        if not e.files or not self.destino_imagen_pendiente:
            return
        origen = getattr(e.files[0], "path", None)
        destino = self.destino_imagen_pendiente
        if not origen:
            self._subir_imagen_web(e.files[0], destino)
            return
        try:
            os.makedirs(os.path.dirname(destino), exist_ok=True)
            shutil.copyfile(origen, destino)
            self.mensaje.value = f"Imagen agregada: {destino}"
            self.mensaje.color = "primary"
            self.destino_imagen_pendiente = ""
            self._ejecutar_validacion(actualizar=False)
            self.update()
        except Exception as ex:
            self.mensaje.value = f"Error al copiar imagen: {ex}"
            self.mensaje.color = "error"
            self.update()

    def _subir_imagen_web(self, archivo, destino):
        if not self.page:
            self.mensaje.value = "No pude iniciar la subida desde el navegador."
            self.mensaje.color = "error"
            self.update()
            return
        extension = os.path.splitext(archivo.name or "")[1].lower() or ".png"
        nombre_temporal = f"{uuid.uuid4().hex}{extension}"
        self.uploads_pendientes[nombre_temporal] = destino
        try:
            upload_url = self.page.get_upload_url(nombre_temporal, 600)
            self.file_picker.upload([ft.FilePickerUploadFile(archivo.name, upload_url)])
            self.mensaje.value = f"Subiendo imagen para {destino}..."
            self.mensaje.color = "secondary"
        except Exception as ex:
            self.uploads_pendientes.pop(nombre_temporal, None)
            self.mensaje.value = f"Error al preparar subida: {ex}"
            self.mensaje.color = "error"
        self.update()

    def _finalizar_upload_imagen(self, e):
        if e.error:
            self.mensaje.value = f"Error al subir imagen: {e.error}"
            self.mensaje.color = "error"
            self.update()
            return
        if e.progress is not None and e.progress < 1:
            return

        destino = None
        origen = None
        for nombre_temporal, destino_posible in list(self.uploads_pendientes.items()):
            ruta_posible = os.path.join(CARPETA_UPLOADS, nombre_temporal)
            if os.path.exists(ruta_posible):
                origen = ruta_posible
                destino = destino_posible
                self.uploads_pendientes.pop(nombre_temporal, None)
                break

        if not origen or not destino:
            return

        try:
            os.makedirs(os.path.dirname(destino), exist_ok=True)
            shutil.copyfile(origen, destino)
            self.mensaje.value = f"Imagen agregada: {destino}"
            self.mensaje.color = "primary"
            self.destino_imagen_pendiente = ""
            self._ejecutar_validacion(actualizar=False)
        except Exception as ex:
            self.mensaje.value = f"Error al guardar imagen subida: {ex}"
            self.mensaje.color = "error"
        self.update()

    def _construir_tarjeta(self, problema):
        acciones = []
        if problema.ruta.endswith(".csv") and os.path.exists(problema.ruta):
            acciones.append(
                ft.IconButton(
                    ft.Icons.OPEN_IN_NEW,
                    tooltip="Abrir CSV relacionado",
                    on_click=lambda e, r=problema.ruta: self._abrir_destino(r),
                )
            )
        if problema.destino_imagen:
            acciones.append(
                ft.IconButton(
                    ft.Icons.ADD_PHOTO_ALTERNATE,
                    tooltip="Agregar imagen",
                    on_click=lambda e, d=problema.destino_imagen: self._seleccionar_imagen(d),
                )
            )
        return ft.Container(
            padding=12,
            bgcolor=COLOR_PANEL_EDITOR,
            border=ft.border.all(1, self._color_severidad(problema.severidad)),
            border_radius=8,
            content=ft.Row(
                [
                    ft.Icon(self._icono_severidad(problema.severidad), color=self._color_severidad(problema.severidad)),
                    ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Text(problema.categoria, color="primary", weight=ft.FontWeight.BOLD),
                                    ft.Text(problema.severidad.upper(), color=self._color_severidad(problema.severidad), size=12),
                                ],
                                spacing=10,
                            ),
                            ft.Text(problema.titulo, weight=ft.FontWeight.BOLD),
                            ft.Text(problema.detalle, color=COLOR_TEXTO_SUAVE, selectable=True),
                            ft.Text(problema.ruta, color=COLOR_TEXTO_SUAVE, size=12, selectable=True) if problema.ruta else ft.Container(),
                        ],
                        spacing=3,
                        expand=True,
                    ),
                    ft.Row(acciones, spacing=0),
                ],
                vertical_alignment=ft.CrossAxisAlignment.START,
            ),
        )

    def _refrescar_lista(self, actualizar=True):
        visibles = self._problemas_visibles()
        self._actualizar_resumen(visibles)
        if visibles:
            self.lista.controls = [self._construir_tarjeta(p) for p in visibles]
        else:
            self.lista.controls = [
                ft.Container(
                    padding=24,
                    alignment=ft.alignment.center,
                    bgcolor=COLOR_PANEL_EDITOR,
                    border=ft.border.all(1, COLOR_BORDE_EDITOR),
                    border_radius=8,
                    content=ft.Text("No hay problemas con esos filtros.", color=COLOR_TEXTO_SUAVE),
                )
            ]
        if actualizar:
            self.update()


# ---------------------------------------------------------------------------
# PÁGINA: selector de archivos (agentes, discos, personajes)
# ---------------------------------------------------------------------------
class PaginaEditorCSV(ft.Column):
    """Punto de entrada. Insértalo como una página/ruta más de tu app existente,
    o úsalo standalone con el bloque main() de abajo."""

    def __init__(self):
        super().__init__(expand=True, spacing=16)
        self.contenido = ft.Column(expand=True)
        self.controls = [
            ft.Text("Editor de tablas", size=24, weight=ft.FontWeight.BOLD),
            self.contenido,
        ]
        self._mostrar_lista(actualizar=False)

    def _mostrar_lista(self, actualizar=True):
        nombre_nuevo = ft.TextField(label="Nombre del nuevo personaje", width=260)

        def crear_nuevo(e):
            nombre = nombre_archivo_seguro(nombre_nuevo.value or "")
            if nombre:
                ruta = crear_csv_personaje(nombre)
                self._abrir(ruta)

        items_personajes = [
            ft.ListTile(
                title=ft.Text(nombre),
                leading=ft.Icon(ft.Icons.PERSON),
                on_click=lambda e, n=nombre: self._abrir(os.path.join(CARPETA_PERSONAJES, f"{n}.csv")),
            )
            for nombre in listar_personajes()
        ]

        self.contenido.controls = [
            ft.ListTile(
                title=ft.Text("Agentes (stats base)"),
                subtitle=ft.Text(RUTA_AGENTES),
                leading=ft.Icon(ft.Icons.TABLE_CHART),
                on_click=lambda e: self._abrir(RUTA_AGENTES),
            ),
            ft.ListTile(
                title=ft.Text("Discos (sets)"),
                subtitle=ft.Text(RUTA_DISCOS),
                leading=ft.Icon(ft.Icons.TABLE_CHART),
                on_click=lambda e: self._abrir(RUTA_DISCOS),
            ),
            ft.ListTile(
                title=ft.Text("Sets de discos"),
                subtitle=ft.Text(RUTA_SETS),
                leading=ft.Icon(ft.Icons.TABLE_CHART),
                on_click=lambda e: self._abrir(RUTA_SETS),
            ),
            ft.ListTile(
                title=ft.Text("Enemigos (stats base)"),
                subtitle=ft.Text(RUTA_ENEMIGOS),
                leading=ft.Icon(ft.Icons.TABLE_CHART),
                on_click=lambda e: self._abrir(RUTA_ENEMIGOS),
            ),
            ft.ListTile(
                title=ft.Text("W-Engines"),
                subtitle=ft.Text(RUTA_WENGINE),
                leading=ft.Icon(ft.Icons.TABLE_CHART),
                on_click=lambda e: self._abrir(RUTA_WENGINE),
            ),
            ft.ListTile(
                title=ft.Text("Substats"),
                subtitle=ft.Text(RUTA_SUBSTATS),
                leading=ft.Icon(ft.Icons.TABLE_CHART),
                on_click=lambda e: self._abrir(RUTA_SUBSTATS),
            ),
            ft.ListTile(
                title=ft.Text("Traducciones"),
                subtitle=ft.Text(CARPETA_LOCALES),
                leading=ft.Icon(ft.Icons.TRANSLATE),
                on_click=lambda e: self._abrir_traducciones(),
            ),
            ft.ListTile(
                title=ft.Text("Validador de assets"),
                subtitle=ft.Text("Agentes, sets, imagenes, traducciones y mappings Enka"),
                leading=ft.Icon(ft.Icons.FACT_CHECK),
                on_click=lambda e: self._abrir_validador(),
            ),
            ft.ListTile(
                title=ft.Text("Mappings Enka"),
                subtitle=ft.Text("IDs de agentes y sets usados al importar builds"),
                leading=ft.Icon(ft.Icons.HUB),
                on_click=lambda e: self._abrir_mappings_enka(),
            ),
            ft.ListTile(
                title=ft.Text("Formulas de daño"),
                subtitle=ft.Text("Configuracion editable de Vortex y futuros tipos de daño"),
                leading=ft.Icon(ft.Icons.CALCULATE),
                on_click=lambda e: self._abrir_formulas_dano(),
            ),
            ft.ListTile(
                title=ft.Text("Generador de agente"),
                subtitle=ft.Text("Crea fila base, CSV de habilidades y deja pendientes visibles en el validador"),
                leading=ft.Icon(ft.Icons.PERSON_ADD),
                on_click=lambda e: self._abrir_generador_agente(),
            ),
            ft.ListTile(
                title=ft.Text("Efectos"),
                subtitle=ft.Text("Sets, W-Engines, pasivas, mindscapes, core y soportes"),
                leading=ft.Icon(ft.Icons.TUNE),
                on_click=lambda e: self._abrir_panel_efectos(),
            ),
            ft.Divider(),
            ft.Text("Habilidades por personaje", weight=ft.FontWeight.BOLD),
            *items_personajes,
            ft.Row([nombre_nuevo, ft.ElevatedButton("+ Nuevo personaje", on_click=crear_nuevo)]),
        ]
        if actualizar: self.update()

    def _abrir(self, ruta):
        self.contenido.controls = [TablaEditable(ruta, on_volver=self._mostrar_lista)]
        self.update()

    def _abrir_traducciones(self):
        self.contenido.controls = [EditorTraducciones(on_volver=self._mostrar_lista)]
        self.update()

    def _abrir_validador(self):
        self.contenido.controls = [ValidadorAssets(on_volver=self._mostrar_lista, abrir_ruta=self._abrir)]
        self.update()

    def _abrir_mappings_enka(self):
        self.contenido.controls = [EditorMappingsEnka(on_volver=self._mostrar_lista)]
        self.update()

    def _abrir_formulas_dano(self):
        self.contenido.controls = [EditorFormulasDano(on_volver=self._mostrar_lista)]
        self.update()

    def _abrir_generador_agente(self):
        self.contenido.controls = [GeneradorAgenteNuevo(on_volver=self._mostrar_lista, abrir_ruta=self._abrir)]
        self.update()

    def _abrir_panel_efectos(self):
        self.contenido.controls = [PanelEfectos(on_volver=self._mostrar_lista, abrir_codigo=self._abrir_codigo)]
        self.update()

    def _abrir_codigo(self, ruta):
        self.contenido.controls = [EditorTextoSimple(ruta, on_volver=self._abrir_panel_efectos)]
        self.update()


# ---------------------------------------------------------------------------
# Modo standalone — para probarlo solo, sin integrarlo todavía a tu app
# ---------------------------------------------------------------------------
def main(page: ft.Page):
    page.title = "Editor de tablas CSV"
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
            elevation=5,
        ),
    )
    page.scroll = ft.ScrollMode.AUTO
    page.add(PaginaEditorCSV())


asgi_app = ft.app(target=main, export_asgi_app=True, upload_dir=CARPETA_UPLOADS)


if __name__ == "__main__":
    import uvicorn

    PUERTO = 8550
    print(f"Iniciando servidor... abre http://localhost:{PUERTO} en tu navegador")
    print("(o busca el puerto {} en la pestaña PORTS de VS Code).".format(PUERTO))
    uvicorn.run(asgi_app, host="0.0.0.0", port=PUERTO)
