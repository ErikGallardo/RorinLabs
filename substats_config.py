import csv
import os

DELIMITADOR = ";"
ENCODING = "utf-8-sig"
NOMBRE_ARCHIVO_SUBSTATS = "substat.csv"


def _parse_float(valor, default=0.0):
    try:
        texto = str(valor).replace("%", "").replace(",", ".").strip()
        return float(texto) if texto else default
    except (TypeError, ValueError):
        return default


def construir_unique_key(nombre_substat, tipo):
    nombre = str(nombre_substat or "").strip()
    tipo_norm = str(tipo or "").strip().lower()
    if not nombre or not tipo_norm:
        return ""
    return f"{nombre}_{tipo_norm}"


def cargar_valores_substats(ruta_base=None):
    """Lee datos/substat.csv y devuelve {unique_key: valor_por_roll}."""
    if ruta_base is None:
        ruta_base = os.path.join(os.path.dirname(__file__), "datos")
    ruta = ruta_base if str(ruta_base).lower().endswith(".csv") else os.path.join(ruta_base, NOMBRE_ARCHIVO_SUBSTATS)
    valores = {}
    if not os.path.exists(ruta):
        return valores

    with open(ruta, "r", encoding=ENCODING, newline="") as f:
        lector = csv.DictReader(f, delimiter=DELIMITADOR)
        for fila in lector:
            fila = {str(k).replace("\ufeff", "").strip(): v for k, v in fila.items()}
            key = construir_unique_key(fila.get("substat"), fila.get("tipo"))
            if key:
                valores[key] = _parse_float(fila.get("valor"))
    return valores


VALORES_SUBSTATS = cargar_valores_substats()


def valor_substat(unique_key, default=0.0):
    return VALORES_SUBSTATS.get(str(unique_key or "").strip(), default)


def calcular_rolls_substat(unique_key, valor_texto, default=1):
    valor_roll = valor_substat(unique_key)
    if valor_roll <= 0:
        return default
    valor = _parse_float(valor_texto)
    return max(1, int(round(valor / valor_roll)))
