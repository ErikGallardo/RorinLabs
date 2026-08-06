import json
import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RUTA_MAPPINGS = os.path.join(BASE_DIR, "datos", "enka_mappings.json")


AVATAR_ID_MAP_DEFAULT = {
    1011: "Anby", 1021: "Nekomata", 1031: "Nicole", 1041: "Soldier 11",
    1051: "Yidhari", 1061: "Corin", 1071: "Caesar", 1081: "Billy",
    1091: "Miyabi", 1101: "Koleda", 1111: "Anton", 1121: "Ben", 1131: "Soukaku",
    1141: "Lycaon", 1151: "Lucy", 1161: "Lighter", 1171: "Burnice", 1181: "Grace",
    1191: "Ellen", 1201: "Harumasa", 1211: "Rina", 1221: "Yanagi", 1241: "Zhu Yuan",
    1251: "Qingyi", 1271: "Seth", 1281: "Piper", 1291: "Hugo", 1301: "Orphie & Magus",
    1311: "Astra Yao", 1321: "Evelyn", 1331: "Vivian", 1341: "Zhao", 1351: "Pulchra",
    1361: "Trigger", 1371: "Yixuan", 1381: "Soldier 0 - Anby", 1391: "Ju Fufu", 1401: "Alice",
    1411: "Yuzuha", 1421: "Pan Yinhu", 1431: "Ye Shunguang", 1441: "Manato", 1451: "Lucia",
    1461: "Seed", 1471: "Banyue", 1481: "Dialyn", 1491: "Sunna", 1501: "Aria", 1511: "Nangong Yu",
    1521: "Cissia", 1531: "Starlight - Billy", 1541: "Promeia", 1551: "Pyrois", 1561: "Velina",
    1571: "Norma",
}


MAPA_SETS_ID_DEFAULT = {
    31800: "Jazz caótico", 32600: "Metal colmilludo", 32400: "Metal eléctrico",
    32300: "Metal caótico", 32200: "Metal infernal", 32500: "Metal Polar",
    32700: "Balada de la rama y la espada", 33100: "Fábula Yunkui",
    31400: "Punk Hormonal", 31000: "Tecno Pícido", 32800: "Voz Astral",
    31600: "Jazz Oscilante", 32900: "Armonía Umbría", 31100: "Tecno Tetraodóntido",
    33300: "Floración del alba", 33200: "Monarca del Pináculo",
    33400: "Nana a la Luz Cenicienta", 33000: "Melodía de Phaeton",
    31900: "Proto Punk", 31200: "Disco sacudestrellas",
    33600: "Aria Radiante", 33500: "Balada de Aguas Blancas",
    31300: "Blues Libre", 31500: "Rock espiritual",
    33700: "Conejo en el país de las maravillas", 33800: "Diario de una prisionera",
    33900: "Metal colmilludo", 34000: "Metal infernal",
}


def _cargar_json_usuario():
    if not os.path.exists(RUTA_MAPPINGS):
        return {}
    try:
        with open(RUTA_MAPPINGS, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def cargar_mappings_enka():
    datos = _cargar_json_usuario()
    avatares = dict(AVATAR_ID_MAP_DEFAULT)
    sets = dict(MAPA_SETS_ID_DEFAULT)
    avatares.update({int(k): str(v) for k, v in datos.get("avatares", {}).items() if str(k).isdigit()})
    sets.update({int(k): str(v) for k, v in datos.get("sets", {}).items() if str(k).isdigit()})
    return avatares, sets


def guardar_mappings_enka(avatares, sets):
    os.makedirs(os.path.dirname(RUTA_MAPPINGS), exist_ok=True)
    datos = {
        "avatares": {str(k): avatares[k] for k in sorted(avatares)},
        "sets": {str(k): sets[k] for k in sorted(sets)},
    }
    with open(RUTA_MAPPINGS, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)
        f.write("\n")


AVATAR_ID_MAP, MAPA_SETS_ID = cargar_mappings_enka()
