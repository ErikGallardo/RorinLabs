import json
import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RUTA_FORMULAS = os.path.join(BASE_DIR, "datos", "formulas_dano.json")


FORMULAS_DEFAULT = {
    "vortex": {
        "fuego": {"base_pct": 900, "tick_pct": 50, "tick_seg": 0.5, "usar_intervalos": True},
        "electrico": {"base_pct": 650, "tick_pct": 125, "tick_seg": 1.0, "usar_intervalos": False},
        "hielo": {"base_pct": 1300, "tick_pct": 7.5, "tick_seg": 1.0, "usar_intervalos": False},
        "frost": {"base_pct": 0, "tick_pct": 7.5, "tick_seg": 1.0, "usar_intervalos": False},
        "físico": {"base_pct": 800, "tick_pct": 7.5, "tick_seg": 1.0, "usar_intervalos": False},
        "etereo": {"base_pct": 650, "tick_pct": 62.5, "tick_seg": 0.5, "usar_intervalos": True},
    }
}


def cargar_formulas_dano():
    formulas = json.loads(json.dumps(FORMULAS_DEFAULT))
    if not os.path.exists(RUTA_FORMULAS):
        return formulas
    try:
        with open(RUTA_FORMULAS, "r", encoding="utf-8") as f:
            datos = json.load(f)
        for grupo, valores in datos.items():
            if isinstance(valores, dict):
                formulas.setdefault(grupo, {}).update(valores)
    except Exception:
        pass
    return formulas


def guardar_formulas_dano(formulas):
    os.makedirs(os.path.dirname(RUTA_FORMULAS), exist_ok=True)
    with open(RUTA_FORMULAS, "w", encoding="utf-8") as f:
        json.dump(formulas, f, ensure_ascii=False, indent=2)
        f.write("\n")
