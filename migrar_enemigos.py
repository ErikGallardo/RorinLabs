"""
migrar_enemigos.py — corre esto UNA SOLA VEZ.

Lee datos_enemigos_da.py (el archivo viejo con ft.TextSpan a mano) usando el
módulo `ast` (analiza el código como árbol de sintaxis, sin ejecutarlo —
por eso no necesita tener flet ni traductor instalados para correr esto)
y vuelca todo a un JSON plano que el formulario web puede leer y escribir.

Uso:
    python3 migrar_enemigos.py datos_enemigos_da.py datos/enemigos_da.json
"""

import ast
import json
import os
import sys

# (color, weight) -> nombre semántico que usará el formulario
ESTILO_DESDE_COLOR = {
    ("WHITE", None): "normal",
    ("CYAN_300", "BOLD"): "resaltado",
    ("GREEN_400", "BOLD"): "buff",
    ("RED_400", "BOLD"): "debuff",
    ("PURPLE_300", "BOLD"): "especial",
    ("ORANGE_400", "BOLD"): "advertencia",
    ("AMBER_400", "BOLD"): "cargas",
}


def _ultimo_atributo(nodo):
    """De un nodo tipo ft.Colors.CYAN_300 saca solo 'CYAN_300'."""
    return ast.unparse(nodo).split(".")[-1]


def _extraer_default(llamada_i18n):
    """De i18n.t('clave', default='texto') saca 'texto'."""
    for kw in llamada_i18n.keywords:
        if kw.arg == "default":
            return ast.literal_eval(kw.value)
    return ""


def _extraer_clave_i18n(llamada_i18n):
    """De i18n.t('enemigo.butcher.s1', default=...) saca 'enemigo.butcher.s1'."""
    return ast.literal_eval(llamada_i18n.args[0])


def _extraer_estilo(llamada_style):
    color, weight = None, None
    for kw in llamada_style.keywords:
        if kw.arg == "color":
            color = _ultimo_atributo(kw.value)
        elif kw.arg == "weight":
            weight = _ultimo_atributo(kw.value)
    return ESTILO_DESDE_COLOR.get((color, weight), "normal")


def _extraer_span(llamada_span):
    i18n_call = llamada_span.args[0]
    texto = _extraer_default(i18n_call)
    estilo_kw = next(kw for kw in llamada_span.keywords if kw.arg == "style")
    estilo = _extraer_estilo(estilo_kw.value)
    return {"texto": texto, "estilo": estilo}


def _extraer_opcion(nodo_dict):
    opcion = {}
    for k, v in zip(nodo_dict.keys, nodo_dict.values):
        clave = ast.literal_eval(k)
        if clave == "label":
            opcion["label"] = _extraer_default(v)
        elif clave == "efectos":
            opcion["efectos"] = {
                ast.literal_eval(kk): ast.literal_eval(vv)
                for kk, vv in zip(v.keys, v.values)
            }
        else:
            opcion[clave] = ast.literal_eval(v)
    return opcion


def _extraer_enemigo(nodo_dict):
    enemigo = {}
    slug = None
    for k, v in zip(nodo_dict.keys, nodo_dict.values):
        clave = ast.literal_eval(k)
        if clave == "imagen":
            enemigo["imagen"] = ast.literal_eval(v)
        elif clave == "spans":
            enemigo["spans"] = [_extraer_span(c) for c in v.elts]
            primera_clave = _extraer_clave_i18n(v.elts[0].args[0])
            partes = primera_clave.split(".")
            slug = partes[1] if len(partes) >= 2 else None
        elif clave == "opciones":
            enemigo["opciones"] = [_extraer_opcion(c) for c in v.elts]
    enemigo["_slug"] = slug
    return enemigo


def migrar(ruta_entrada, ruta_salida):
    with open(ruta_entrada, "r", encoding="utf-8") as f:
        arbol = ast.parse(f.read())

    dict_node = None
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.FunctionDef) and nodo.name == "obtener_mapa_enemigos_da":
            for stmt in ast.walk(nodo):
                if isinstance(stmt, ast.Return):
                    dict_node = stmt.value
                    break

    if dict_node is None:
        raise RuntimeError(
            "No encontré 'return {...}' dentro de obtener_mapa_enemigos_da(). "
            "¿Cambiaste el nombre de la función?"
        )

    resultado = {}
    for k, v in zip(dict_node.keys, dict_node.values):
        nombre = ast.literal_eval(k)
        resultado[nombre] = _extraer_enemigo(v)

    carpeta = os.path.dirname(ruta_salida)
    if carpeta:
        os.makedirs(carpeta, exist_ok=True)
    with open(ruta_salida, "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)

    print(f"Migrados {len(resultado)} enemigos -> {ruta_salida}")
    return resultado


if __name__ == "__main__":
    entrada = sys.argv[1] if len(sys.argv) > 1 else "datos_enemigos_da.py"
    salida = sys.argv[2] if len(sys.argv) > 2 else "datos/enemigos_da.json"
    migrar(entrada, salida)
