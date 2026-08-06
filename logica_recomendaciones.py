import flet as ft
from collections import Counter
from simulador_equipos import SimuladorEquipos

CONFIG_ROLES = {
    "Atacante": {
        "main_4": {"general": ["Probabilidad_crítico", "Daño_crítico"],"particular": ["Ataque"]},
        "main_5": {"general": ["Daño_elemental", "Ataque"],"particular": ["Tasa_de_Perforación"]},
        "main_6": {"general": ["Ataque"],"particular": []},
        "subs": {
            "ideal":   ["Probabilidad_crítico_porcentual", "Daño_crítico_porcentual", "Ataque_porcentual"],
            "decente": ["Ataque_plano", "Perforación_Plana_plano"],
            "basura":  ["Defensa_plano", "Defensa_porcentual", "Puntos_Vida_plano", "Puntos_Vida_porcentual", "Maestría_Anomalía_plano"]
        }
    },
    "Aturdidor": {
        "main_4": {"general": ["Probabilidad_crítico", "Daño_crítico"],"particular": ["Maestría_Anomalía", "Ataque"]},
        "main_5": {"general": ["Daño_elemental", "Ataque"],"particular": ["Tasa_de_Perforación"]},
        "main_6": {"general": ["Impacto", "Ataque"],"particular": ["Recuperación_energía", "Tasa_de_Anomalía"]},
        "subs": {
            "ideal":   ["Ataque_porcentual", "Maestría_Anomalía_plano"],
            "decente": ["Probabilidad_crítico_porcentual", "Daño_crítico_porcentual", "Ataque_plano"],
            "basura":  ["Defensa_plano", "Defensa_porcentual", "Puntos_Vida_plano", "Puntos_Vida_porcentual"]
        }
    },
    "Anomalo": {
        "main_4": {"general": ["Maestría_Anomalía"],"particular": ["Ataque"]},
        "main_5": {"general": ["Daño_elemental", "Ataque"],"particular": ["Tasa_de_Perforación"]},
        "main_6": {"general": ["Tasa_de_Anomalía"],"particular": ["Recuperación_energía", "Ataque"]},
        "subs": {
            "ideal":   ["Maestría_Anomalía_plano", "Ataque_porcentual"],
            "decente": ["Ataque_plano", "Perforación_Plana_plano"],
            "basura":  ["Probabilidad_crítico_porcentual", "Daño_crítico_porcentual", "Defensa_plano", "Defensa_porcentual", "Puntos_Vida_plano", "Puntos_Vida_porcentual"]
        }
    },
    "Soporte": {
        "main_4": {"general": ["Probabilidad_crítico", "Ataque", "Daño_crítico"],"particular": ["Maestría_Anomalía"]},
        "main_5": {"general": ["Daño_elemental", "Ataque"],"particular": ["Tasa_de_Perforación"]},
        "main_6": {"general": ["Recuperación_energía"],"particular": ["Ataque"]},
        "subs": {
            "ideal":   ["Recuperación_energía_porcentual", "Ataque_porcentual"],
            "decente": ["Puntos_Vida_porcentual", "Defensa_porcentual", "Probabilidad_crítico_porcentual"],
            "basura":  ["Defensa_plano", "Puntos_Vida_plano", "Maestría_Anomalía_plano", "Daño_crítico_porcentual"]
        }
    },
    "Ruptura": {
        "main_4": {"general": ["Probabilidad_crítico", "Daño_crítico"],"particular": ["Puntos_Vida"]},
        "main_5": {"general": ["Daño_elemental", "Puntos_Vida"],"particular": ["Tasa_de_Perforación"]},
        "main_6": {"general": ["Puntos_Vida"],"particular": []},
        "subs": {
            "ideal":   ["Probabilidad_crítico_porcentual", "Daño_crítico_porcentual", "Puntos_Vida_porcentual"],
            "decente": ["Puntos_Vida_plano"],
            "basura":  ["Defensa_plano", "Defensa_porcentual", "Ataque_plano", "Ataque_porcentual", "Maestría_Anomalía_plano"]
        }
    },
}

CONFIG_ROLES["Anomalía"] = CONFIG_ROLES["Anomalo"]
CONFIG_ROLES["Auxiliar"] = CONFIG_ROLES["Soporte"]

MAPA_SETS_ELEMENTALES = {
    "Etereo":    ["Metal caótico", "Aria Radiante"],
    "Físico":    ["Metal colmilludo", "Balada de Aguas Blancas"],
    "Eléctrico": ["Metal eléctrico"],
    "Fuego":     ["Metal infernal"],
    "Hielo":     ["Metal Polar"]
}

CONFIG_SETS_ROLES = {
    "Atacante": {
        "ideal": ["Tecno Pícido", "Punk Hormonal", "Balada de la rama y la espada"], 
        "funcional": ["Voz Astral", "Tecno Tetraodóntido", "Punk Hormonal"] 
    },
    "Aturdidor": {
        "ideal": ["Monarca del Pináculo", "Proto Punk", "Voz Astral"], 
        "funcional": ["Disco sacudestrellas", "Blues Libre", "Balada de la rama y la espada", "Tecno Pícido"] 
    },
    "Anomalo": {
        "ideal": ["Blues Libre", "Jazz caótico", "Melodía de Phaeton"], 
        "funcional": ["Punk Hormonal", "Tecno Tetraodóntido", "Voz Astral"] 
    },
    "Soporte": {
        "ideal": ["Voz Astral","Jazz Oscilante", "Proto Punk", "Nana a la Luz Cenicienta"], 
        "funcional": ["Blues Libre"]
    },
    "Ruptura": {
        "ideal": ["Fábula Yunkui"],
        "funcional": ["Tecno Pícido", "Balada de la rama y la espada"]
    },
}
CONFIG_SETS_ROLES["Anomalía"] = CONFIG_SETS_ROLES["Anomalo"]
CONFIG_SETS_ROLES["Auxiliar"] = CONFIG_SETS_ROLES["Soporte"]

EXCEPCIONES_AGENTES = {
    "Alice": {
        "meta_dano": "anomalia",
        "main_4": {"general": ["Maestría_Anomalía", "Ataque"], "particular": []},
        "main_5": {"general": ["Tasa_de_Perforación", "Daño_elemental"], "particular": ["Ataque"]},
        "main_6": {"general": ["Tasa_de_Anomalía"], "particular": []},
        "subs": {
            "ideal":   ["Maestría_Anomalía_plano", "Ataque_porcentual"],
            "decente": ["Ataque_plano", "Perforación_Plana_plano"],
            "basura":  ["Probabilidad_crítico_porcentual", "Daño_crítico_porcentual"]
        },
        "sets": {
            "ideal": ["Metal colmilludo","Punk Hormonal"], 
            "funcional": ["Blues Libre", "Tecno Tetraodóntido", "Melodía de Phaeton", "Voz Astral", "Jazz caótico"]
        },
         "wengines": {
            "ideal": [("Practiced Perfection", "max")],
            "funcional": [("Sharpened Stinger", 1), ("Weeping Gemini", "max"), ("Fusion Compiler", 1), "Electro-Lip Gloss"]
        }
    },
    "Anby": {
        "meta_dano": "general",
        "main_4": {"general": ["Ataque", "Daño_crítico", "Probabilidad_crítico"], "particular": []},
        "main_5": {"general": ["Ataque", "Daño_elemental"], "particular": ["Tasa_de_Perforación"]},
        "main_6": {"general": ["Impacto"], "particular": []},
        "subs": {
            "ideal":   ["Daño_crítico_porcentual", "Ataque_porcentual", "Probabilidad_crítico_porcentual"],
            "decente": ["Ataque_plano", "Perforación_Plana_plano"],
            "basura":  ["Defensa_plano", "Defensa_porcentual", "Puntos_Vida_plano", "Puntos_Vida_porcentual"]
        },
        "sets": {
            "4pc": [("Monarca del Pináculo", "max"), "Voz Astral", "Proto Punk", "Disco sacudestrellas"], 
            "2pc": ["Nana a la Luz Cenicienta", "Jazz Oscilante","Disco sacudestrellas", "Monarca del Pináculo"]
        },
        "wengines": {"ideal": ["Hellfire Gears", "Demara Battery Mark II"], "funcional": ["Steam Oven", "Precious Fossilized Core", "The Restrained"]}
    },
    "Soldier 0 - Anby": {
        "meta_dano": "general",
        "etiqueta_dano": "aftershock",
        "main_4": {"general": ["Probabilidad_crítico", "Ataque"], "particular": ["Daño_crítico"]},
        "main_5": {"general": ["Ataque", "Daño_elemental"], "particular": ["Tasa_de_Perforación",]},
        "main_6": {"general": ["Ataque"], "particular": []},
        "subs": {
            "ideal":   ["Daño_crítico_porcentual", "Ataque_porcentual", "Probabilidad_crítico_porcentual"],
            "decente": ["Ataque_plano", "Perforación_Plana_plano"],
            "basura":  ["Defensa_plano", "Defensa_porcentual", "Puntos_Vida_plano", "Puntos_Vida_porcentual", "Maestría_Anomalía_plano"]
        },
        "sets": {
            "ideal": ["Armonía Umbría"], 
            "funcional": ["Voz Astral", "Tecno Tetraodóntido", "Punk Hormonal", "Tecno Pícido", "Balada de la rama y la espada", "Metal eléctrico"] 
        },
        "wengines": {
            "ideal": [("Severed Innocence", "max")], 
            "funcional": ["Heartstring Nocturne", "Marcato Desire", ("Cordis Germina", "max"), "Starlight Engine"] 
        }
    },
    "Anton": {
        "meta_dano": "general",
        "main_4": {"general": ["Probabilidad_crítico", "Daño_crítico"], "particular": ["Ataque"]},
        "main_5": {"general": ["Ataque", "Daño_elemental"], "particular": ["Tasa_de_Perforación",]},
        "main_6": {"general": ["Ataque"], "particular": []},
        "subs": {
            "ideal":   ["Daño_crítico_porcentual", "Ataque_porcentual", "Probabilidad_crítico_porcentual"],
            "decente": ["Ataque_plano", "Perforación_Plana_plano"],
            "basura":  ["Defensa_plano", "Defensa_porcentual", "Puntos_Vida_plano", "Puntos_Vida_porcentual"]
        },
        "sets": {
            "ideal": ["Metal eléctrico", "Tecno Tetraodóntido", "Tecno Pícido"], 
            "funcional": ["Voz Astral", "Tecno Tetraodóntido", "Punk Hormonal", "Tecno Pícido", "Balada de la rama y la espada", "Metal eléctrico"] 
        },
        "wengines": {
            "ideal": [("Heartstring Nocturne", "max"), "Zanshin Herb Case", ("The Brimstone", 5)], 
            "funcional": [ "Street Superstar", "Starlight Engine", "Marcato Desire", "Cannon Rotor", "Gilded Blossom", "Drill Rig - Red Axis"] 
        }
    },
    "Aria": {
        "meta_dano": "anomalia",
        "main_4": {"general": ["Maestría_Anomalía"], "particular": []},
        "main_5": {"general": ["Tasa_de_Perforación", "Daño_elemental"], "particular": ["Ataque"]},
        "main_6": {"general": ["Tasa_de_Anomalía"], "particular": []},
        "subs": {
            "ideal":   ["Maestría_Anomalía_plano", "Ataque_porcentual"],
            "decente": ["Ataque_plano", "Perforación_Plana_plano"],
            "basura":  ["Probabilidad_crítico_porcentual", "Daño_crítico_porcentual"]
        },
        "sets": {
            "ideal": ["Melodía de Phaeton", "Aria Radiante"], 
            "funcional": ["Blues Libre", "Tecno Tetraodóntido", "Metal caótico", "Voz Astral", "Punk Hormonal"]
        },
         "wengines": {
            "ideal": [ ("Angel in the Shell", "max")],
            "funcional": [("Flight of Fancy", 0), "Fusion Compiler", "Electro-Lip Gloss", ("Weeping Gemini", "max")]
        }
    },
    "Astra Yao": {
        "meta_dano": "general",
        "main_4": {"general": ["Ataque"],"particular": ["Probabilidad_crítico", "Daño_crítico"]},
        "main_5": {"general": ["Ataque"],"particular": ["Daño_elemental"]},
        "main_6": {"general": ["Recuperación_energía"],"particular": ["Ataque"]},
        "subs": {
            "ideal":   ["Probabilidad_crítico_porcentual", "Ataque_porcentual", "Daño_crítico_porcentual"],
            "decente": ["Ataque_plano"],
            "basura":  ["Defensa_plano", "Defensa_porcentual", "Puntos_Vida_plano", "Puntos_Vida_porcentual"]
        },
        "sets": {
            "ideal": ["Voz Astral", "Nana a la Luz Cenicienta"], 
            "funcional": ["Jazz Oscilante", "Punk Hormonal"]
        },
        "wengines": {"ideal": [("Elegant Vanity", "max")], "funcional": ["Bashful Demon", "Kaboom the Cannon"]}
    },
    "Banyue": {
        "meta_dano": "sheer",
        "main_4": {"general": ["Probabilidad_crítico", "Daño_crítico"], "particular": ["Puntos_Vida"]},
        "main_5": {"general": ["Daño_elemental"], "particular": ["Puntos_Vida"]},
        "main_6": {"general": ["Puntos_Vida"], "particular": []},
        "subs": {
            "ideal":   ["Puntos_Vida_porcentual", "Probabilidad_crítico_porcentual", "Daño_crítico_porcentual"],
            "decente": ["Puntos_Vida_plano", "Ataque_porcentual"],
            "basura":  ["Defensa_plano", "Defensa_porcentual"]
        },
        "sets": {
            "ideal": ["Fábula Yunkui"], 
            "funcional": ["Balada de la rama y la espada", "Tecno Pícido"]
        },
        "wengines": {"ideal": [("Wrathful Vajra", "max")], "funcional": [("Qingming Birdcage", 0), ("Cauldron of Clarity", 2), "Grill O'Wisp", "Puzzle Sphere", "Radiowave Journey"]}
    },
    "Ben": {
        "meta_dano": "general",
        "main_4": {"general": ["Probabilidad_crítico", "Daño_crítico"],"particular": ["Ataque"]},
        "main_5": {"general": ["Daño_elemental", "Ataque"],"particular": ["Tasa_de_Perforación"]},
        "main_6": {"general": ["Ataque"],"particular": []},
        "subs": {
            "ideal":   ["Probabilidad_crítico_porcentual", "Daño_crítico_porcentual", "Ataque_porcentual"],
            "decente": ["Ataque_plano", "Perforación_Plana_plano"],
            "basura":  ["Defensa_plano", "Defensa_porcentual", "Puntos_Vida_plano", "Puntos_Vida_porcentual"]
        },
        "sets": {
            "ideal": ["Tecno Pícido", "Punk Hormonal", "Balada de la rama y la espada"], 
            "funcional": ["Voz Astral", "Punk Hormonal", "Tecno Tetraodóntido"] 
        },
         "wengines": {
            "ideal": ["Hailstorm Shrine", "Cloudcleave Radiance"],
            "funcional": [""]
        }
    },
    "Billy": {
        "meta_dano": "general",
        "main_4": {"general": ["Probabilidad_crítico", "Daño_crítico"], "particular": ["Ataque"]},
        "main_5": {"general": ["Daño_elemental","Ataque"], "particular": ["Tasa_de_Perforación"]},
        "main_6": {"general": ["Ataque"], "particular": []},
        "subs": {
            "ideal":   ["Daño_crítico_porcentual", "Ataque_porcentual", "Probabilidad_crítico_porcentual"],
            "decente": ["Ataque_plano", "Perforación_Plana_plano"],
            "basura":  ["Defensa_plano", "Defensa_porcentual", "Puntos_Vida_plano", "Puntos_Vida_porcentual"]
        },
        "sets": {
            "4pc": ["Tecno Pícido", "Tecno Tetraodóntido", "Metal colmilludo"], 
            "2pc": ["Punk Hormonal", "Balada de la rama y la espada", "Tecno Tetraodóntido", "Tecno Pícido", "Metal colmilludo", "Voz Astral"]
        },
        "wengines": {"ideal": ["Steel Cushion", "Starlight Engine Replica"], "funcional": [("Heartstring Nocturne", 1), "Zanshin Herb Case", ("The Brimstone", "max"), "Marcato Desire", "Starlight Engine", "Street Superstar", "Cannon Rotor", "Gilded Blossom"]}
    },
    "Burnice": {
        "meta_dano": "anomalia",
        "main_4": {"general": ["Maestría_Anomalía"], "particular": ["Ataque"]},
        "main_5": {"general": ["Daño_elemental", "Ataque"], "particular": ["Tasa_de_Perforación"]},
        "main_6": {"general": ["Recuperación_energía"], "particular": ["Tasa_de_Anomalía"]},
        "subs": {
            "ideal":   ["Maestría_Anomalía_plano", "Ataque_porcentual"],
            "decente": ["Ataque_plano", "Perforación_Plana_plano"],
            "basura":  ["Probabilidad_crítico_porcentual", "Daño_crítico_porcentual"]
        },
        "sets": {
            "ideal": ["Jazz caótico"], 
            "funcional": ["Nana a la Luz Cenicienta", "Jazz Oscilante", "Blues Libre", "Tecno Tetraodóntido", "Melodía de Phaeton", "Voz Astral", "Punk Hormonal", "Metal infernal"]
        },
         "wengines": {
            "ideal": [("Flamemaker Shaker", "max")],
            "funcional": ["Practiced Perfection", "Electro-Lip Gloss", ("Weeping Gemini", "max")]
        }
    },
    "Caesar": {
        "meta_dano": "general",
        "main_4": {"general": ["Maestría_Anomalía", "Probabilidad_crítico"], "particular": []},
        "main_5": {"general": ["Ataque", "Daño_elemental"], "particular": []},
        "main_6": {"general": ["Impacto"], "particular": []},
        "subs": {
            "ideal":   ["Ataque_porcentual", "Maestría_Anomalía_plano", "Probabilidad_crítico_porcentual", "Daño_crítico_porcentual"],
            "decente": ["Puntos_Vida_porcentual", "Defensa_porcentual"],
            "basura":  ["Defensa_plano", "Defensa_porcentual", "Puntos_Vida_plano", "Puntos_Vida_porcentual"]
        },
        "sets": {
            "ideal": ["Voz Astral","Punk Hormonal", "Jazz Oscilante", "Proto Punk"], 
            "funcional": ["Blues Libre"]
        },
         "wengines": {
            "ideal": ["Tusks of Fury", "Original Transmorpher"],
            "funcional": ["The Restrained", "Hellfire Gears", "Precious Fossilized Core"]
        }
    },
    "Corin": {
        "meta_dano": "general",
        "main_4": {"general": ["Probabilidad_crítico", "Daño_crítico"], "particular": ["Ataque"]},
        "main_5": {"general": ["Ataque", "Tasa_de_Perforación"], "particular": ["Daño_elemental"]},
        "main_6": {"general": ["Ataque"], "particular": []},
        "subs": {
            "ideal":   ["Daño_crítico_porcentual", "Ataque_porcentual", "Probabilidad_crítico_porcentual"],
            "decente": ["Ataque_plano", "Perforación_Plana_plano"],
            "basura":  ["Defensa_plano", "Defensa_porcentual", "Puntos_Vida_plano", "Puntos_Vida_porcentual"]
        },
        "sets": {
            "4pc": ["Tecno Tetraodóntido", "Punk Hormonal"], 
            "2pc": ["Punk Hormonal", "Balada de la rama y la espada", "Tecno Pícido", "Metal colmilludo", "Voz Astral"]
        },
        "wengines": {"ideal": ["Cordis Germina", "Steel Cushion", ("Heartstring Nocturne", 1)], "funcional": ["Myriad Eclipse", ("Housekeeper", "max"), "Starlight Engine"]}
    },
    "Dialyn": {
        "meta_dano": "general",
        "main_4": {"general": ["Probabilidad_crítico"],"particular": []},
        "main_5": {"general": ["Daño_elemental", "Ataque"],"particular": ["Tasa_de_Perforación"]},
        "main_6": {"general": ["Impacto", "Recuperación_energía"],"particular": ["Recuperación_energía", "Ataque"]},
        "subs": {
            "ideal":   ["Probabilidad_crítico_porcentual", "Ataque_porcentual"],
            "decente": ["Daño_crítico_porcentual", "Ataque_plano", "Perforación_Plana_plano"],
            "basura":  ["Defensa_plano", "Defensa_porcentual", "Puntos_Vida_plano", "Puntos_Vida_porcentual"]
        },
        "sets": {
            "ideal": ["Monarca del Pináculo", "Voz Astral"], 
            "funcional": ["Disco sacudestrellas", "Tecno Pícido"] 
        },
        "wengines": {"ideal": ["Yesterday Calls"], "funcional": ["Hellfire Gears", "Steam Oven"]}
    },
    "Ellen": {
        "meta_dano": "general",
        "main_4": {"general": ["Probabilidad_crítico", "Daño_crítico"], "particular": ["Ataque"]},
        "main_5": {"general": ["Ataque", "Tasa_de_Perforación"], "particular": ["Daño_elemental"]},
        "main_6": {"general": ["Ataque"], "particular": []},
        "subs": {
            "ideal":   ["Daño_crítico_porcentual", "Ataque_porcentual", "Probabilidad_crítico_porcentual"],
            "decente": ["Ataque_plano", "Perforación_Plana_plano"],
            "basura":  ["Defensa_plano", "Defensa_porcentual", "Puntos_Vida_plano", "Puntos_Vida_porcentual"]
        },
        "sets": {
            "4pc": ["Tecno Tetraodóntido", "Tecno Pícido", "Armonía Umbría"], 
            "2pc": ["Punk Hormonal", "Balada de la rama y la espada", "Tecno Pícido", "Metal Polar", "Voz Astral"]
        },
        "wengines": {"ideal": ["Deep Sea Visitor"], "funcional": ["Myriad Eclipse", "Cordis Germina", ("Heartstring Nocturne", 1), "Steel Cushion", "Starlight Engine"]}
    },
    "Evelyn": {
        "meta_dano": "general",
        "main_4": {"general": ["Probabilidad_crítico", "Daño_crítico"], "particular": ["Ataque"]},
        "main_5": {"general": ["Ataque", "Tasa_de_Perforación"], "particular": ["Daño_elemental"]},
        "main_6": {"general": ["Ataque"], "particular": []},
        "subs": {
            "ideal":   ["Daño_crítico_porcentual", "Ataque_porcentual", "Probabilidad_crítico_porcentual"],
            "decente": ["Ataque_plano", "Perforación_Plana_plano"],
            "basura":  ["Defensa_plano", "Defensa_porcentual", "Puntos_Vida_plano", "Puntos_Vida_porcentual"]
        },
        "sets": {
            "4pc": ["Tecno Tetraodóntido", "Tecno Pícido", "Punk Hormonal"], 
            "2pc": ["Punk Hormonal", "Balada de la rama y la espada", "Tecno Pícido", "Voz Astral"]
        },
        "wengines": {"ideal": [("Heartstring Nocturne", "max")], "funcional": [("Myriad Eclipse", 0), ("Severed Innocence", 1), ("Steel Cushion", 0), "Starlight Engine"]}
    },
    "Grace": {
        "meta_dano": "anomalia",
        "main_4": {"general": ["Maestría_Anomalía"], "particular": ["Ataque"]},
        "main_5": {"general": ["Tasa_de_Perforación", "Daño_elemental"], "particular": ["Ataque"]},
        "main_6": {"general": ["Tasa_de_Anomalía"], "particular": ["Recuperación_energía"]},
        "subs": {
            "ideal":   ["Maestría_Anomalía_plano", "Ataque_porcentual"],
            "decente": ["Ataque_plano", "Perforación_Plana_plano"],
            "basura":  ["Probabilidad_crítico_porcentual", "Daño_crítico_porcentual"]
        },
        "sets": {
            "ideal": ["Metal eléctrico","Jazz caótico"], 
            "funcional": ["Blues Libre", "Tecno Tetraodóntido", "Melodía de Phaeton", "Voz Astral", "Punk Hormonal"]
        },
         "wengines": {
            "ideal": ["Timeweaver", ("Practiced Perfection", 0), ("Fusion Compiler", "max")],
            "funcional": ["Electro-Lip Gloss", ("Weeping Gemini", "max")]
        }
    },
    "Harumasa": {
        "meta_dano": "general",
        "main_4": {"general": ["Probabilidad_crítico", "Daño_crítico", "Ataque"], "particular": []},
        "main_5": {"general": ["Ataque", "Daño_elemental"], "particular": ["Tasa_de_Perforación"]},
        "main_6": {"general": ["Ataque"], "particular": []},
        "subs": {
            "ideal":   ["Daño_crítico_porcentual", "Ataque_porcentual", "Probabilidad_crítico_porcentual"],
            "decente": ["Ataque_plano", "Perforación_Plana_plano"],
            "basura":  ["Defensa_plano", "Defensa_porcentual", "Puntos_Vida_plano", "Puntos_Vida_porcentual"]
        },
        "sets": {
            "4pc": ["Armonía Umbría", "Metal eléctrico"], 
            "2pc": ["Punk Hormonal", "Balada de la rama y la espada", "Tecno Pícido", "Voz Astral", "Armonía Umbría"]
        },
        "wengines": {"ideal": [("Cordis Germina", "max"), ("Zanshin Herb Case", "max")], "funcional": [("The Brimstone", 4), ("Severed Innocence", 1), ("Heartstring Nocturne", 0), "Starlight Engine"]}
    },
    "Hugo": {
        "meta_dano": "general",
        "main_4": {"general": ["Probabilidad_crítico", "Daño_crítico"], "particular": ["Ataque"]},
        "main_5": {"general": ["Daño_elemental"], "particular": ["Ataque", "Tasa_de_Perforación"]},
        "main_6": {"general": ["Ataque"], "particular": []},
        "subs": {
            "ideal":   ["Daño_crítico_porcentual", "Ataque_porcentual", "Probabilidad_crítico_porcentual"],
            "decente": ["Ataque_plano", "Perforación_Plana_plano"],
            "basura":  ["Defensa_plano", "Defensa_porcentual", "Puntos_Vida_plano", "Puntos_Vida_porcentual"]
        },
        "sets": {
            "4pc": ["Tecno Tetraodóntido", "Punk Hormonal"], 
            "2pc": ["Punk Hormonal", "Balada de la rama y la espada", "Tecno Tetraodóntido" ,"Tecno Pícido", "Metal Polar", "Voz Astral"]
        },
        "wengines": {"ideal": ["Myriad Eclipse"], "funcional": [("Cordis Germina", 0), ("Heartstring Nocturne", 0), "Steel Cushion", "Marcato Desire"]}
    },
    "Jane": {
        "meta_dano": "anomalia",
        "main_4": {"general": ["Maestría_Anomalía"], "particular": []},
        "main_5": {"general": ["Tasa_de_Perforación", "Daño_elemental"], "particular": ["Ataque"]},
        "main_6": {"general": ["Tasa_de_Anomalía"], "particular": []},
        "subs": {
            "ideal":   ["Maestría_Anomalía_plano", "Ataque_porcentual"],
            "decente": ["Ataque_plano", "Perforación_Plana_plano"],
            "basura":  ["Probabilidad_crítico_porcentual", "Daño_crítico_porcentual"]
        },
        "sets": {
            "ideal": ["Metal colmilludo"], 
            "funcional": ["Blues Libre", "Tecno Tetraodóntido", "Melodía de Phaeton", "Voz Astral", "Jazz caótico","Punk Hormonal"]
        },
         "wengines": {
            "ideal": [("Sharpened Stinger", "max")],
            "funcional": [("Practiced Perfection", 1), ("Weeping Gemini", "max"), ("Fusion Compiler", 1), "Electro-Lip Gloss"]
        }
    },
    "Ju Fufu": {
        "meta_dano": "general",
        "main_4": {"general": ["Probabilidad_crítico_porcentual", "Ataque"],"particular": []},
        "main_5": {"general": ["Ataque"],"particular": []},
        "main_6": {"general": ["Impacto", "Ataque"],"particular": []},
        "subs": {
            "ideal":   ["Probabilidad_crítico_porcentual", "Ataque_porcentual", "Daño_crítico_porcentual"],
            "decente": ["Ataque_porcentual", "Ataque_plano"],
            "basura":  ["Defensa_plano", "Defensa_porcentual", "Puntos_Vida_plano", "Puntos_Vida_porcentual"]
        },
        "sets": {
            "ideal": ["Monarca del Pináculo","Punk Hormonal", "Tecno Pícido"], 
            "funcional": ["Disco sacudestrellas", "Voz Astral"] 
        },
        "wengines": {"ideal": ["Roaring Fur-nace", "max"], "funcional": ["Hellfire Gears", "Blazing Laurel"]}
    },
    "Koleda": {
        "meta_dano": "general",
        "main_4": {"general": ["Ataque", "Daño_crítico", "Probabilidad_crítico"], "particular": []},
        "main_5": {"general": ["Ataque", "Daño_elemental"], "particular": ["Tasa_de_Perforación"]},
        "main_6": {"general": ["Impacto"], "particular": []},
        "subs": {
            "ideal":   ["Daño_crítico_porcentual", "Ataque_porcentual", "Probabilidad_crítico_porcentual"],
            "decente": ["Ataque_plano", "Perforación_Plana_plano"],
            "basura":  ["Defensa_plano", "Defensa_porcentual", "Puntos_Vida_plano", "Puntos_Vida_porcentual"]
        },
        "sets": {
            "4pc": [("Monarca del Pináculo", "max"), "Voz Astral", "Proto Punk", "Disco sacudestrellas"], 
            "2pc": ["Nana a la Luz Cenicienta", "Jazz Oscilante","Disco sacudestrellas", "Monarca del Pináculo"]
        },
        "wengines": {"ideal": ["Hellfire Gears"], "funcional": ["Steam Oven", "Precious Fossilized Core", "The Restrained"]}
    },
    "Lighter": {
        "meta_dano": "general",
        "main_4": {"general": ["Ataque", "Daño_crítico", "Probabilidad_crítico"], "particular": []},
        "main_5": {"general": ["Ataque", "Daño_elemental", "Tasa_de_Perforación"], "particular": []},
        "main_6": {"general": ["Impacto"], "particular": []},
        "subs": {
            "ideal":   ["Daño_crítico_porcentual", "Ataque_porcentual", "Probabilidad_crítico_porcentual"],
            "decente": ["Ataque_plano", "Perforación_Plana_plano"],
            "basura":  ["Defensa_plano", "Defensa_porcentual", "Puntos_Vida_plano", "Puntos_Vida_porcentual"]
        },
        "sets": {
            "4pc": [("Monarca del Pináculo", "max"), "Voz Astral", "Proto Punk", "Disco sacudestrellas"], 
            "2pc": ["Nana a la Luz Cenicienta", "Jazz Oscilante","Disco sacudestrellas", "Monarca del Pináculo"]
        },
        "wengines": {"ideal": ["Blazing Laurel"], "funcional": ["Ice-Jade Teapot", "Hellfire Gears", "The Restrained", "Precious Fossilized Core"]}
    },
    "Lucia": {
        "meta_dano": "general",
        "main_4": {"general": ["Puntos_Vida"], "particular": []},
        "main_5": {"general": ["Puntos_Vida"], "particular": []},
        "main_6": {"general": ["Recuperación_energía"], "particular": ["Puntos_Vida"]},
        "subs": {
            "ideal":   ["Puntos_Vida_porcentual", "Probabilidad_crítico_porcentual", "Daño_crítico_porcentual"],
            "decente": ["Puntos_Vida_plano",],
            "basura":  ["Defensa_plano", "Defensa_porcentual"]
        },
        "sets": {
            "ideal": ["Nana a la Luz Cenicienta"],
            "funcional": ["Voz Astral","Jazz Oscilante", "Fábula Yunkui"]
        },
        "wengines": {"ideal": ["Dreamlit Hearth"], "funcional": ["Weeping Cradle", "Unfettered Game Ball", "Kaboom the Cannon"]}
    },
    "Lucy": {
        "meta_dano": "general",
        "main_4": {"general": ["Ataque", "Probabilidad_crítico"],"particular": []},
        "main_5": {"general": ["Ataque"],"particular": []},
        "main_6": {"general": ["Recuperación_energía"],"particular": ["Ataque"]},
        "subs": {
            "ideal":   ["Probabilidad_crítico_porcentual", "Ataque_porcentual", "Daño_crítico_porcentual"],
            "decente": ["Ataque_plano"],
            "basura":  ["Defensa_plano", "Defensa_porcentual", "Puntos_Vida_plano", "Puntos_Vida_porcentual"]
        },
        "sets": {
            "ideal": ["Voz Astral", "Nana a la Luz Cenicienta", "Jazz Oscilante"], 
            "funcional": ["Jazz Oscilante", "Punk Hormonal", "Tecno Tetraodóntido", "Voz Astral", "Blues Libre", "Jazz caótico", "Metal colmilludo"]
        },
        "wengines": {"ideal": ["Kaboom the Cannon"], "funcional": ["Bashful Demon", "Slice of Time", "(Reverb) Mark II"]}
    },
    "Lycaon": {
        "meta_dano": "general",
        "main_4": {"general": ["Ataque", "Daño_crítico", "Probabilidad_crítico"], "particular": []},
        "main_5": {"general": ["Ataque", "Daño_elemental", "Tasa_de_Perforación"], "particular": []},
        "main_6": {"general": ["Impacto"], "particular": []},
        "subs": {
            "ideal":   ["Daño_crítico_porcentual", "Ataque_porcentual", "Probabilidad_crítico_porcentual"],
            "decente": ["Ataque_plano", "Perforación_Plana_plano"],
            "basura":  ["Defensa_plano", "Defensa_porcentual", "Puntos_Vida_plano", "Puntos_Vida_porcentual"]
        },
        "sets": {
            "4pc": [("Monarca del Pináculo", "max"), "Voz Astral", "Proto Punk", "Disco sacudestrellas"], 
            "2pc": ["Nana a la Luz Cenicienta", "Jazz Oscilante","Disco sacudestrellas", "Monarca del Pináculo"]
        },
        "wengines": {"ideal": ["Blazing Laurel", "Hellfire Gears", "The Restrained", "Precious Fossilized Core"], "funcional": []}
    },
    "Manato": {
        "meta_dano": "sheer",
        "main_4": {"general": ["Probabilidad_crítico", "Daño_crítico"], "particular": ["Puntos_Vida"]},
        "main_5": {"general": ["Daño_elemental"], "particular": ["Puntos_Vida"]},
        "main_6": {"general": ["Puntos_Vida"], "particular": []},
        "subs": {
            "ideal":   ["Puntos_Vida_porcentual", "Probabilidad_crítico_porcentual", "Daño_crítico_porcentual"],
            "decente": ["Puntos_Vida_plano", "Ataque_porcentual"],
            "basura":  ["Defensa_plano", "Defensa_porcentual"]
        },
        "sets": {
            "ideal": ["Fábula Yunkui"], 
            "funcional": ["Balada de la rama y la espada", "Tecno Pícido"]
        },
        "wengines": {"ideal": ["Grill O'Wisp"], "funcional": [("Wrathful Vajra", 1), ("Qingming Birdcage", 0),"Puzzle Sphere", "Radiowave Journey"]}
    },
    "Miyabi": {
        "meta_dano": "normal",
        "main_4": {"general": ["Probabilidad_crítico", "Daño_crítico", "Maestría_Anomalía"], "particular": ["Ataque"]},
        "main_5": {"general": ["Tasa_de_Perforación","Ataque"], "particular": [ "Daño_elemental"]},
        "main_6": {"general": ["Ataque"], "particular": ["Tasa_de_Anomalía"]},
        "subs": {
            "ideal":   ["Probabilidad_crítico_porcentual", "Daño_crítico_porcentual", "Ataque_porcentual"],
            "decente": ["Ataque_plano", "Maestría_Anomalía_plano", "Perforación_Plana_plano"],
            "basura":  ["Defensa_plano", "Defensa_porcentual", "Puntos_Vida_plano", "Puntos_Vida_porcentual"]
        },
        "sets": {
            "ideal": ["Balada de la rama y la espada"], 
            "funcional": ["Punk Hormonal", "Tecno Tetraodóntido", "Tecno Pícido", "Blues Libre"]
        },
        "wengines": {"ideal": [("Hailstorm Shrine", "max")], "funcional": [("Fusion Compiler", 1), "Electro-Lip Gloss"]}
    },
    "Nekomata": {
        "meta_dano": "general",
        "main_4": {"general": ["Probabilidad_crítico", "Daño_crítico"], "particular": ["Ataque"]},
        "main_5": {"general": ["Ataque", "Tasa_de_Perforación", "Daño_elemental"], "particular": []},
        "main_6": {"general": ["Ataque"], "particular": []},
        "subs": {
            "ideal":   ["Daño_crítico_porcentual", "Ataque_porcentual", "Probabilidad_crítico_porcentual"],
            "decente": ["Ataque_plano", "Perforación_Plana_plano"],
            "basura":  ["Defensa_plano", "Defensa_porcentual", "Puntos_Vida_plano", "Puntos_Vida_porcentual"]
        },
        "sets": {
            "4pc": ["Tecno Tetraodóntido", "Tecno Pícido"], 
            "2pc": ["Punk Hormonal", "Balada de la rama y la espada", "Tecno Pícido", "Metal colmilludo", "Voz Astral"]
        },
        "wengines": {"ideal": [("Cordis Germina", 0), ("Steel Cushion", "max"), ("Heartstring Nocturne", 1)], "funcional": [("The Brimstone", 5), "Starlight Engine"]}
    },
    "Nicole": {
        "meta_dano": "general",
        "main_4": {"general": ["Probabilidad_crítico", "Ataque", "Daño_crítico"],"particular": ["Maestría_Anomalía"]},
        "main_5": {"general": ["Daño_elemental", "Ataque"],"particular": ["Tasa_de_Perforación"]},
        "main_6": {"general": ["Recuperación_energía"],"particular": ["Ataque"]},
        "subs": {
            "ideal":   ["Recuperación_energía_porcentual", "Ataque_porcentual"],
            "decente": ["Puntos_Vida_porcentual", "Defensa_porcentual", "Probabilidad_crítico_porcentual"],
            "basura":  ["Defensa_plano", "Puntos_Vida_plano", "Maestría_Anomalía_plano", "Daño_crítico_porcentual"]
        },
        "sets": {
            "ideal": ["Voz Astral", "Nana a la Luz Cenicienta", "Jazz Oscilante"], 
            "funcional": ["Jazz Oscilante", "Punk Hormonal", "Tecno Tetraodóntido", "Voz Astral", "Blues Libre", "Jazz caótico", "Metal colmilludo"]
        },
        "wengines": {"ideal": ["The Vault"], "funcional": ["Weeping Cradle", "Kaboom the Cannon", "Unfettered Game Ball"]}
    },
    "Orphie & Magus": { 
        "meta_dano": "general",
        "etiqueta_dano": "aftershock",
        "main_4": {"general": ["Probabilidad_crítico", "Daño_crítico"],"particular": ["Ataque"]},
        "main_5": {"general": ["Ataque"],"particular": ["Tasa_de_Perforación", "Daño_elemental"]},
        "main_6": {"general": ["Ataque", "Recuperación_energía"],"particular": []},
        "subs": {
            "ideal":   ["Probabilidad_crítico_porcentual", "Daño_crítico_porcentual", "Ataque_porcentual"],
            "decente": ["Ataque_plano", "Perforación_Plana_plano"],
            "basura":  ["Defensa_plano", "Defensa_porcentual", "Puntos_Vida_plano", "Puntos_Vida_porcentual"]
        },
        "sets": {
            "ideal": ["Voz Astral", "Armonía Umbría"],
            "funcional": ["Punk Hormonal","Jazz Oscilante", "Nana a la Luz Cenicienta"]
        },
        "wengines": {"ideal": [("Bellicose Blaze", "max")], "funcional": [("Heartstring Nocturne", "max"), ("Severed Innocence", 2),
                                                                ("Myriad Eclipse", 0), ("Cordis Germina", 0), "Gilded Blossom", "Marcato Desire"]}
    },
    "Pan Yinhu": {
        "meta_dano": "general",
        "main_4": {"general": [ "Ataque"], "particular": ["Probabilidad_crítico"]},
        "main_5": {"general": ["Ataque", "Daño_elemental"], "particular": []},
        "main_6": {"general": ["Recuperación_energía"], "particular": ["Impacto"]},
        "subs": {
            "ideal":   ["Ataque_porcentual", "Probabilidad_crítico_porcentual", "Daño_crítico_porcentual"],
            "decente": ["Ataque_plano"],
            "basura":  []
        },
        "sets": {
            "ideal": ["Voz Astral", "Jazz Oscilante", "Proto Punk"], 
            "funcional": ["Punk Hormonal"]
        },
         "wengines": {
            "ideal": ["Tusks of Fury", "Tremor Trigram Vessel"],
            "funcional": ["Peacekeeper - Specialized", "Spring Embrace"]
        }
    },
    "Piper": {
        "meta_dano": "anomalia",
        "main_4": {"general": ["Maestría_Anomalía"], "particular": []},
        "main_5": {"general": ["Tasa_de_Perforación", "Daño_elemental", "Ataque"], "particular": []},
        "main_6": {"general": ["Tasa_de_Anomalía"], "particular": []},
        "subs": {
            "ideal":   ["Maestría_Anomalía_plano", "Ataque_porcentual"],
            "decente": ["Ataque_plano", "Perforación_Plana_plano"],
            "basura":  ["Probabilidad_crítico_porcentual", "Daño_crítico_porcentual"]
        },
        "sets": {
            "ideal": ["Metal colmilludo"], 
            "funcional": ["Blues Libre", "Tecno Tetraodóntido", "Melodía de Phaeton", "Voz Astral", "Jazz caótico"]
        },
         "wengines": {
            "ideal": [("Practiced Perfection", "max"), ("Weeping Gemini", "max"), "Sharpened Stinger", ("Roaring Ride", "max")],
            "funcional": ["Electro-Lip Gloss"]
        }
    },
    "Pulchra": {
        "meta_dano": "general",
        "main_4": {"general": ["Daño_crítico", "Probabilidad_crítico"], "particular": ["Ataque"]},
        "main_5": {"general": ["Ataque", "Daño_elemental"], "particular": []},
        "main_6": {"general": ["Impacto"], "particular": []},
        "subs": {
            "ideal":   ["Daño_crítico_porcentual", "Ataque_porcentual", "Probabilidad_crítico_porcentual"],
            "decente": ["Ataque_plano", "Perforación_Plana_plano"],
            "basura":  ["Defensa_plano", "Defensa_porcentual", "Puntos_Vida_plano", "Puntos_Vida_porcentual"]
        },
        "sets": {
            "4pc": [("Monarca del Pináculo", "max"), "Voz Astral", "Proto Punk", "Disco sacudestrellas"], 
            "2pc": ["Nana a la Luz Cenicienta", "Jazz Oscilante","Disco sacudestrellas", "Monarca del Pináculo"]
        },
        "wengines": {"ideal": ["Blazing Laurel", "Box Cutter"], "funcional": ["Hellfire Gears", "Steam Oven", "The Restrained", "Precious Fossilized Core"]}
    },
    "Promeia": {
        "meta_dano": "anomalia",
        "main_4": {"general": ["Maestría_Anomalía"], "particular": []},
        "main_5": {"general": [ "Daño_elemental", "Ataque"], "particular": ["Tasa_de_Perforación"]},
        "main_6": {"general": ["Tasa_de_Anomalía"], "particular": []},
        "subs": {
            "ideal":   ["Maestría_Anomalía_plano", "Ataque_porcentual"],
            "decente": ["Ataque_plano", "Perforación_Plana_plano"],
            "basura":  ["Probabilidad_crítico_porcentual", "Daño_crítico_porcentual"]
        },
        "sets": {
            "ideal": ["Diario de una prisionera"], 
            "funcional": ["Melodía de Phaeton", "Blues Libre", "Jazz caótico", "Voz Astral", "Punk Hormonal"]
        },
         "wengines": {
            "ideal": [ ("Frostfall Sickle", "max")],
            "funcional": [("Angel in the Shell", 0), "Fusion Compiler", "Electro-Lip Gloss", ("Weeping Gemini", "max")]
        }
    },
    "Qingyi": {
        "meta_dano": "general",
        "main_4": {"general": ["Ataque", "Daño_crítico", "Probabilidad_crítico"], "particular": []},
        "main_5": {"general": ["Ataque", "Daño_elemental"], "particular": ["Tasa_de_Perforación"]},
        "main_6": {"general": ["Impacto"], "particular": []},
        "subs": {
            "ideal":   ["Daño_crítico_porcentual", "Ataque_porcentual", "Probabilidad_crítico_porcentual"],
            "decente": ["Ataque_plano", "Perforación_Plana_plano"],
            "basura":  ["Defensa_plano", "Defensa_porcentual", "Puntos_Vida_plano", "Puntos_Vida_porcentual"]
        },
        "sets": {
            "4pc": [("Monarca del Pináculo", "max"), "Voz Astral", "Proto Punk", "Disco sacudestrellas"], 
            "2pc": ["Nana a la Luz Cenicienta", "Jazz Oscilante","Disco sacudestrellas", "Monarca del Pináculo"]
        },
        "wengines": {"ideal": [("Ice-Jade Teapot", "max")], "funcional": ["Steam Oven", "Precious Fossilized Core", "The Restrained"]}
    },
    "Rina": {
        "meta_dano": "general",
        "main_4": {"general": ["Ataque", "Maestría_Anomalía"],"particular": ["Probabilidad_crítico"]},
        "main_5": {"general": ["Tasa_de_Perforación"],"particular": []},
        "main_6": {"general": ["Recuperación_energía"],"particular": ["Ataque"]},
        "subs": {
            "ideal":   ["Maestría_Anomalía_plano", "Ataque_porcentual"],
            "decente": ["Probabilidad_crítico_porcentual", "Daño_crítico_porcentual", "Ataque_plano", "Perforación_Plana_plano"],
            "basura":  ["Defensa_plano", "Puntos_Vida_plano"]
        },
        "sets": {
            "ideal": ["Voz Astral", "Nana a la Luz Cenicienta"], 
            "funcional": ["Blues Libre", "Tecno Tetraodóntido", "Jazz Oscilante"]
        },
         "wengines": {
            "ideal": ["Weeping Cradle"],
            "funcional": ["Kaboom the Cannon", "Slice of Time"]
        }
    },
    "Seed": {
        "meta_dano": "general",
        "main_4": {"general": ["Probabilidad_crítico"], "particular": ["Daño_crítico", "Ataque"]},
        "main_5": {"general": ["Ataque", "Daño_elemental"], "particular": ["Tasa_de_Perforación",]},
        "main_6": {"general": ["Ataque"], "particular": []},
        "subs": {
            "ideal":   ["Daño_crítico_porcentual", "Ataque_porcentual", "Probabilidad_crítico_porcentual"],
            "decente": ["Ataque_plano", "Perforación_Plana_plano"],
            "basura":  ["Defensa_plano", "Defensa_porcentual", "Puntos_Vida_plano", "Puntos_Vida_porcentual"]
        },
        "sets": {
            "ideal": [("Tecno Pícido", "max"), "Floración del alba", "Punk Hormonal"], 
            "funcional": ["Voz Astral", "Tecno Tetraodóntido", "Punk Hormonal", "Tecno Pícido", "Balada de la rama y la espada", "Metal eléctrico"] 
        },
        "wengines": {
            "ideal": [("Cordis Germina", "max")], 
            "funcional": ["Heartstring Nocturne", "Marcato Desire", ("The Brimstone", 6), "Myriad Eclipse", "Zanshin Herb Case", "Riot Suppressor Mark VI"] 
        }
    },
    "Seth": {
        "meta_dano": "anomalia",
        "main_4": {"general": ["Maestría_Anomalía", "Ataque"], "particular": []},
        "main_5": {"general": ["Ataque", "Daño_elemental"], "particular": []},
        "main_6": {"general": ["Tasa_de_Anomalía", "Recuperación_energía"], "particular": ["Impacto"]},
        "subs": {
            "ideal":   ["Ataque_porcentual", "Maestría_Anomalía_plano"],
            "decente": ["Ataque_plano"],
            "basura":  ["Probabilidad_crítico_porcentual", "Daño_crítico_porcentual"]
        },
        "sets": {
            "ideal": ["Voz Astral","Punk Hormonal", "Jazz Oscilante", "Proto Punk"], 
            "funcional": ["Blues Libre"]
        },
         "wengines": {
            "ideal": ["Peacekeeper - Specialized", "Tremor Trigram Vessel", "Spring Embrace"],
            "funcional": ["Bunny Band"]
        }
    },
    "Soldier 11": {
        "meta_dano": "general",
        "main_4": {"general": ["Probabilidad_crítico", "Ataque"], "particular": ["Daño_crítico"]},
        "main_5": {"general": ["Ataque","Tasa_de_Perforación"], "particular": ["Daño_elemental"]},
        "main_6": {"general": ["Ataque"], "particular": []},
        "subs": {
            "ideal":   ["Daño_crítico_porcentual", "Ataque_porcentual", "Probabilidad_crítico_porcentual"],
            "decente": ["Ataque_plano", "Perforación_Plana_plano"],
            "basura":  ["Defensa_plano", "Defensa_porcentual", "Puntos_Vida_plano", "Puntos_Vida_porcentual"]
        },
        "sets": {
            "ideal": ["Tecno Tetraodóntido", "Floración del alba", "Tecno Pícido", "Metal infernal"], 
            "funcional": ["Voz Astral", "Tecno Tetraodóntido", "Punk Hormonal", "Tecno Pícido", "Balada de la rama y la espada", "Metal infernal"] 
        },
        "wengines": {
            "ideal": [("Heartstring Nocturne", "max"),  ], 
            "funcional": [("The Brimstone", "max"), "Cordis Germina", "Starlight Engine", "Myriad Eclipse", ("Severed Innocence", 1)] 
        }
    },
    "Soukaku": {
        "main_4": {"general": ["Ataque"], "particular": ["Maestría_Anomalía"]},
        "main_5": {"general": ["Ataque"], "particular": ["Tasa_de_Perforación"]},
        "main_6": {"general": ["Recuperación_energía", "Ataque"], "particular": ["Tasa_de_Anomalía"]},
        "subs": {
            "ideal":   ["Ataque_porcentual", "Ataque_plano", "Recuperación_energía_porcentual"],
            "decente": ["Puntos_Vida_porcentual", "Defensa_porcentual"],
            "basura":  ["Maestría_Anomalía_plano", "Probabilidad_crítico_porcentual"]
        },
        "sets": {
            "ideal": ["Blues Libre", "Nana a la Luz Cenicienta"], 
            "funcional": ["Blues Libre","Punk Hormonal", "Proto Punk", "Voz Astral"]
        },
         "wengines": {
            "ideal": ["Kaboom the Cannon", "Bashful Demon"],
            "funcional": ["Weeping Cradle"]
        }
    },
    "Sunna": {
        "meta_dano": "general",
        "main_4": {"general": ["Ataque"],"particular": []},
        "main_5": {"general": ["Ataque"],"particular": []},
        "main_6": {"general": ["Recuperación_energía"],"particular": ["Ataque"]},
        "subs": {
            "ideal":   ["Probabilidad_crítico_porcentual", "Ataque_porcentual", "Daño_crítico_porcentual"],
            "decente": ["Ataque_plano"],
            "basura":  ["Defensa_plano", "Defensa_porcentual", "Puntos_Vida_plano", "Puntos_Vida_porcentual"]
        },
        "sets": {
            "ideal": ["Nana a la Luz Cenicienta"], 
            "funcional": ["Voz Astral", "Jazz Oscilante", "Punk Hormonal"]
        },
        "wengines": {"ideal": [("Thoughtbop", "max")], "funcional": ["Weeping Cradle", "Kaboom the Cannon", "Unfettered Game Ball"]}
    },
    "Trigger": {
        "meta_dano": "general",
        "main_4": {"general": ["Probabilidad_crítico"],"particular": []},
        "main_5": {"general": ["Daño_elemental", "Ataque"],"particular": ["Tasa_de_Perforación"]},
        "main_6": {"general": ["Impacto", "Recuperación_energía"],"particular": ["Recuperación_energía", "Ataque"]},
        "subs": {
            "ideal":   ["Probabilidad_crítico_porcentual", "Ataque_porcentual"],
            "decente": ["Daño_crítico_porcentual", "Ataque_plano"],
            "basura":  ["Defensa_plano", "Defensa_porcentual", "Puntos_Vida_plano", "Puntos_Vida_porcentual"]
        },
        "sets": {
            "ideal": ["Monarca del Pináculo", "Voz Astral"], 
            "funcional": ["Disco sacudestrellas", "Tecno Pícido"] 
        },
        "wengines": {"ideal": ["Spectral Gaze"], "funcional": ["Blazing Laurel", "Ice-Jade Teapot", "The Restrained", "Precious Fossilized Core"]}
    },
    "Vivian": {
        "meta_dano": "anomalia",
        "main_4": {"general": ["Maestría_Anomalía"], "particular": []},
        "main_5": {"general": ["Tasa_de_Perforación", "Daño_elemental"], "particular": ["Ataque"]},
        "main_6": {"general": ["Tasa_de_Anomalía"], "particular": []},
        "subs": {
            "ideal":   ["Maestría_Anomalía_plano"],
            "decente": ["Ataque_plano", "Ataque_porcentual", "Perforación_Plana_plano"],
            "basura":  ["Probabilidad_crítico_porcentual", "Daño_crítico_porcentual"]
        },
        "sets": {
            "ideal": ["Melodía de Phaeton"], 
            "funcional": ["Blues Libre", "Tecno Tetraodóntido", "Metal caótico", "Voz Astral", "Punk Hormonal"]
        },
         "wengines": {
            "ideal": [("Flight of Fancy", "max")],
            "funcional": [("Weeping Gemini", "max")]
        }
    },
    "Yanagi": {
        "meta_dano": "anomalia",
        "main_4": {"general": ["Maestría_Anomalía"], "particular": ["Ataque"]},
        "main_5": {"general": ["Tasa_de_Perforación", "Daño_elemental"], "particular": ["Ataque"]},
        "main_6": {"general": ["Tasa_de_Anomalía"], "particular": ["Recuperación_energía"]},
        "subs": {
            "ideal":   ["Maestría_Anomalía_plano", "Ataque_porcentual"],
            "decente": ["Ataque_plano", "Perforación_Plana_plano"],
            "basura":  ["Probabilidad_crítico_porcentual", "Daño_crítico_porcentual"]
        },
        "sets": {
            "ideal": ["Metal eléctrico","Jazz caótico"], 
            "funcional": ["Blues Libre", "Tecno Tetraodóntido", "Melodía de Phaeton", "Voz Astral", "Punk Hormonal"]
        },
         "wengines": {
            "ideal": ["Timeweaver"],
            "funcional": ["Electro-Lip Gloss", "Weeping Gemini", "Fusion Compiler"]
        }
    },
    "Ye Shunguang": {
        "meta_dano": "general",
        "main_4": {"general": ["Ataque", "Daño_crítico"], "particular": []},
        "main_5": {"general": ["Tasa_de_Perforación","Ataque"], "particular": [ "Daño_elemental"]},
        "main_6": {"general": ["Ataque"], "particular": []},
        "subs": {
            "ideal":   ["Daño_crítico_porcentual", "Ataque_porcentual", "Probabilidad_crítico_porcentual"],
            "decente": ["Ataque_plano", "Perforación_Plana_plano"],
            "basura":  ["Defensa_plano", "Defensa_porcentual", "Puntos_Vida_plano", "Puntos_Vida_porcentual"]
        },
        "sets": {
            "4pc": ["Balada de Aguas Blancas"], 
            "2pc": ["Punk Hormonal", "Balada de la rama y la espada", "Tecno Tetraodóntido", "Tecno Pícido", "Metal colmilludo", "Voz Astral"]
        },
        "wengines": {"ideal": [("Cloudcleave Radiance", "max")], "funcional": [("The Brimstone", 5), ("Severed Innocence", 1), "Starlight Engine"]}
    },
    "Yidhari": {
        "meta_dano": "sheer",
        "main_4": {"general": ["Probabilidad_crítico", "Daño_crítico"], "particular": ["Puntos_Vida"]},
        "main_5": {"general": ["Daño_elemental"], "particular": ["Puntos_Vida"]},
        "main_6": {"general": ["Puntos_Vida"], "particular": []},
        "subs": {
            "ideal":   ["Puntos_Vida_porcentual", "Probabilidad_crítico_porcentual", "Daño_crítico_porcentual"],
            "decente": ["Puntos_Vida_plano", "Ataque_porcentual"],
            "basura":  ["Defensa_plano", "Defensa_porcentual"]
        },
        "sets": {
            "ideal": ["Fábula Yunkui"], 
            "funcional": ["Balada de la rama y la espada", "Tecno Pícido"]
        },
        "wengines": {"ideal": [("Kraken's Cradle", "max")], "funcional": [("Cauldron of Clarity", 1),"Puzzle Sphere", "Radiowave Journey", ("Qingming Birdcage", 0) , ("Grill O'Wisp", "max")]}
    },
    "Yixuan": {
        "meta_dano": "sheer",
        "main_4": {"general": ["Probabilidad_crítico", "Daño_crítico"], "particular": ["Puntos_Vida"]},
        "main_5": {"general": ["Daño_elemental"], "particular": ["Puntos_Vida"]},
        "main_6": {"general": ["Puntos_Vida"], "particular": []},
        "subs": {
            "ideal":   ["Puntos_Vida_porcentual", "Probabilidad_crítico_porcentual", "Daño_crítico_porcentual"],
            "decente": ["Puntos_Vida_plano", "Ataque_porcentual"],
            "basura":  ["Defensa_plano", "Defensa_porcentual"]
        },
        "sets": {
            "ideal": ["Fábula Yunkui"], 
            "funcional": ["Balada de la rama y la espada", "Tecno Pícido"]
        },
        "wengines": {"ideal": [("Qingming Birdcage", "max")], "funcional": [("Cauldron of Clarity", 1),"Puzzle Sphere", "Radiowave Journey", ("Kraken's Cradle", 0), ("Grill O'Wisp", "max")]}
    },
    "Yuzuha": {
        "meta_dano": "general",
        "main_4": {"general": ["Ataque", "Maestría_Anomalía"],"particular": []},
        "main_5": {"general": ["Ataque"],"particular": []},
        "main_6": {"general": ["Tasa_de_Anomalía"],"particular": ["Ataque"]},
        "subs": {
            "ideal":   ["Maestría_Anomalía_plano", "Ataque_porcentual"],
            "decente": ["Perforación_Plana_plano", "Ataque_plano"],
            "basura":  ["Defensa_plano", "Defensa_porcentual", "Puntos_Vida_plano", "Puntos_Vida_porcentual"]
        },
        "sets": {
            "ideal": ["Voz Astral", "Nana a la Luz Cenicienta"], 
            "funcional": ["Blues Libre", "Punk Hormonal","Jazz Oscilante", "Proto Punk"]
        },
        "wengines": {
            "ideal": ["Metanukimorphosis"],
            "funcional": ["Kaboom the Cannon", "Weeping Cradle"]
        }
    },
    "Zhao": {
        "meta_dano": "general",
        "main_4": {"general": ["Puntos_Vida"], "particular": []},
        "main_5": {"general": ["Puntos_Vida"], "particular": []},
        "main_6": {"general": ["Recuperación_energía"], "particular": ["Puntos_Vida"]},
        "subs": {
            "ideal":   ["Puntos_Vida_porcentual", "Probabilidad_crítico_porcentual", "Daño_crítico_porcentual"],
            "decente": ["Puntos_Vida_plano"],
            "basura":  ["Defensa_plano", "Defensa_porcentual"]
        },
        "sets": {
            "ideal": ["Voz Astral","Jazz Oscilante"], 
            "funcional": ["Fábula Yunkui"]
        },
        "wengines": {"ideal": ["Half-Sugar Bunny"], "funcional": ["Tusks of Fury", "Original Transmorpher"]}
    },
    "Zhu Yuan": {
        "meta_dano": "general",
        "main_4": {"general": ["Daño_crítico", "Probabilidad_crítico"], "particular": ["Ataque"]},
        "main_5": {"general": ["Ataque"], "particular": ["Tasa_de_Perforación", "Daño_elemental"]},
        "main_6": {"general": ["Ataque"], "particular": []},
        "subs": {
            "ideal":   ["Daño_crítico_porcentual", "Ataque_porcentual", "Probabilidad_crítico_porcentual"],
            "decente": ["Ataque_plano", "Perforación_Plana_plano"],
            "basura":  ["Defensa_plano", "Defensa_porcentual", "Puntos_Vida_plano", "Puntos_Vida_porcentual"]
        },
        "sets": {
            "ideal": [("Tecno Pícido", "max"), "Tecno Tetraodóntido", "Metal caótico"], 
            "funcional": ["Voz Astral", "Tecno Tetraodóntido", "Punk Hormonal", "Floración del alba", "Tecno Pícido", "Balada de la rama y la espada", "Metal caótico"] 
        },
        "wengines": {
            "ideal": [("The Brimstone", 6), ("Cordis Germina", "max")], 
            "funcional": ["Marcato Desire", ("Riot Suppressor Mark VI", "max"), "Starlight Engine"] 
        }
    },
    "Nangong Yu": {
        "meta_dano": "anomalia",
        "main_4": {"general": ["Maestría_Anomalía"], "particular": []},
        "main_5": {"general": ["Daño_elemental"], "particular": ["Tasa_de_Perforación","Ataque"]},
        "main_6": {"general": ["Tasa_de_Anomalía"], "particular": []},
        "subs": {
            "ideal":   ["Maestría_Anomalía_plano", "Ataque_porcentual"],
            "decente": ["Ataque_plano", "Perforación_Plana_plano"],
            "basura":  ["Probabilidad_crítico_porcentual", "Daño_crítico_porcentual"]
        },
        "sets": {
            "ideal": ["Melodía de Phaeton", "Blues Libre"], 
            "funcional": ["Blues Libre", "Tecno Tetraodóntido", "Metal caótico", "Voz Astral", "Punk Hormonal", "Aria Radiante"]
        },
         "wengines": {
            "ideal": [ ("Neon Fantasies", "max")],
            "funcional": [("Hellfire Gears", 2), "The Simmering Pot", ("The Restrained", 3), "Precious Fossilized Core", ("Roaring Fur-nace", 0)]
        }
    },
    "Cissia": {
        "meta_dano": "general",
        "main_4": {"general": ["Daño_crítico", "Probabilidad_crítico"], "particular": [ "Ataque"]},
        "main_5": {"general": ["Daño_elemental"], "particular": ["Ataque"]},
        "main_6": {"general": ["Recuperación_energía"], "particular": []},
        "subs": {
            "ideal":   ["Daño_crítico_porcentual", "Ataque_porcentual", "Probabilidad_crítico_porcentual"],
            "decente": ["Ataque_plano", "Perforación_Plana_plano"],
            "basura":  ["Defensa_plano", "Defensa_porcentual", "Puntos_Vida_plano", "Puntos_Vida_porcentual"]
        },
        "sets": {
            "ideal": ["Voz Astral", "Floración del alba", "Metal eléctrico"], 
            "funcional": ["Voz Astral", "Tecno Tetraodóntido", "Punk Hormonal", "Tecno Pícido", "Balada de la rama y la espada", "Metal eléctrico"] 
        },
        "wengines": {
            "ideal": [("Serpentine Seeker", "max")], 
            "funcional": ["Bellicose Blaze", "Drill Rig - Red Axis", ("Cordis Germina", 0), ("Severed Innocence", 1)] 
        }
    },
    "Starlight - Billy": {
        "meta_dano": "sheer",
        "main_4": {"general": ["Probabilidad_crítico", "Daño_crítico"], "particular": ["Puntos_Vida"]},
        "main_5": {"general": ["Daño_elemental", "Puntos_Vida"], "particular": []},
        "main_6": {"general": ["Puntos_Vida"], "particular": []},
        "subs": {
            "ideal":   ["Puntos_Vida_porcentual", "Probabilidad_crítico_porcentual", "Daño_crítico_porcentual"],
            "decente": ["Puntos_Vida_plano", "Ataque_porcentual"],
            "basura":  ["Defensa_plano", "Defensa_porcentual"]
        },
        "sets": {
            "ideal": ["Fábula Yunkui"], 
            "funcional": ["Balada de la rama y la espada", "Tecno Pícido"]
        },
        "wengines": {"ideal": [("Starlight Rider Faceplate", "max")], "funcional": [("Wrathful Vajra", 0),("Qingming Birdcage", 0), ("Cauldron of Clarity", "max"), "Grill O'Wisp", "Puzzle Sphere", "Radiowave Journey"]}
    },
}

UMBRALES_UTILIDAD = {
    "Caesar":     {"Impacto": 145, "Ataque": 1500},
    "Lucy":       {"Ataque": 2653, "Recuperación_energía": 1.5},
    "Astra Yao":  {"Ataque": 2963, "Recuperación_energía": 1.5},
    "Soukaku":    {"Ataque": 2500, "Recuperación_energía": 1.5},
    "Lighter":    {"Impacto": 195},
    "Pan Yinhu":  {"Ataque": 2500},
    "Rina":       {"Tasa_de_Perforación": 70.4, "Recuperación_energía": 1.3},
    "Orphie & Magus": {"Recuperación_energía": 2.8},
    "Qingyi":     {"Impacto": 180},
    "Koleda":     {"Impacto": 180},
    "Lycaon":     {"Impacto": 180},
    "Dialyn":     {"Probabilidad_crítico": 100},
    "Trigger":     {"Probabilidad_crítico": 90},
    "Ju Fufu":  {"Ataque": 3400},
    "Lucia":    {"Puntos_Vida": 24000},
    "Nangong Yu":    {"Tasa_de_Anomalía": 173},
    "Sunna":  {"Ataque": 3500, "Recuperación_energía": 1.5},
    "Yuzuha":  {"Ataque": 3000, "Tasa_de_Anomalía": 173},
    "Zhao":    {"Puntos_Vida": 27000},
}

NOMBRES_STATS_AMIGABLES = {
    "Impacto":                          "Impacto",
    "Recuperación_energía":             "Rec. Energía",
    "Recuperación_energía_porcentual":  "Rec. Energía %",
    "Ataque":                           "ATK",
    "Ataque_porcentual":                "ATK %",
    "Ataque_plano":                     "ATK flat",
    "Puntos_Vida":                      "HP",
    "Puntos_Vida_porcentual":           "HP %",
    "Puntos_Vida_plano":                "HP flat",
    "Defensa_porcentual":               "DEF %",
    "Defensa_plano":                    "DEF flat",
    "Tasa_de_Perforación":              "PEN Ratio %",
    "Tasa_de_Perforación_porcentual":   "PEN Ratio %",
    "Perforación_Plana_plano":          "Flat PEN",
    "Probabilidad_crítico_porcentual":  "Crit Rate %",
    "Daño_crítico_porcentual":          "Crit DMG %",
    "Maestría_Anomalía_plano":          "Anomaly Mastery",
    "Tasa_de_Anomalía":                 "Anomaly Rate",
    "Daño_elemental":                   "Elemental DMG",
}


def _nombre_stat(clave: str) -> str:
    return NOMBRES_STATS_AMIGABLES.get(clave, clave.replace("_porcentual", "%").replace("_plano", "").replace("_", " "))


class AnalistaBuild:
    def __init__(self, traductor=None):
        self.simulador = SimuladorEquipos()
        self.i18n = traductor

    def _t(self, key, default="", **kwargs):
        if self.i18n:
            return self.i18n.t(key, default=default, **kwargs)
        if kwargs:
            try:
                return default.format(**kwargs)
            except KeyError:
                return default
        return default

    def analizar_build(self, estado_build, agentes_data, elemento_actual, stats_finales=None, equipo_actual=None, enemigo_actual=None):
        nombre_agente = estado_build.nombre_agente
        
        if not nombre_agente or nombre_agente == "Ninguno":
            return None, []

        datos_agente = next((a for a in agentes_data if a['Nombre'] == nombre_agente), None)
        rol = datos_agente.get("Tipo", "Atacante") if datos_agente else "Atacante"
        elemento_agente = datos_agente.get("Elemento", "Físico")

        config = CONFIG_ROLES.get(rol, CONFIG_ROLES["Atacante"]).copy()
        
        etiqueta_rol = rol
        rol_analisis = rol 

        if nombre_agente in EXCEPCIONES_AGENTES:
            excepcion = EXCEPCIONES_AGENTES[nombre_agente]
            etiqueta_rol = f"{rol} (Especial)"
            for key in ["main_4", "main_5", "main_6", "subs"]:
                if key in excepcion: config[key] = excepcion[key]

        consejos = []

        if stats_finales:
            ranking_equipos = self.simulador.simular_mejor_soporte(
                stats_finales, nombre_agente, rol_analisis, elemento_agente
            )
            
            if ranking_equipos:
                top1 = ranking_equipos[0]
                consejos.append((
                    ft.Icons.GROUP_ADD, 
                    self._t("recom.mejor_companero", "Mejor Compañero: {soporte}", soporte=top1['soporte']), 
                    self._t("recom.mejora_pct", "Mejora tu potencial un {pct}%. ({detalle})", pct=f"{top1['mejoria']:.1f}", detalle=top1['detalle']), 
                    ft.Colors.PURPLE_ACCENT
                ))
                
                if len(ranking_equipos) > 1:
                    top2 = ranking_equipos[1]
                    if top2['mejoria'] > 5.0:
                        consejos.append((
                            ft.Icons.GROUP, 
                            self._t("recom.alternativa", "Alternativa: {soporte}", soporte=top2['soporte']), 
                            self._t("recom.mejora_simple", "Mejora: {pct}%.", pct=f"{top2['mejoria']:.1f}"), 
                            ft.Colors.DEEP_PURPLE_200
                        ))

        c_subs = config.get("subs", {})
        l_ideal = c_subs.get("ideal", [])
        l_decente = c_subs.get("decente", [])
        l_basura = c_subs.get("basura", [])

        consejos.extend(self._generar_consejos_subs(
            estado_build.substats_counts, l_ideal, l_decente, l_basura,
            nombre_agente, rol, stats_finales=stats_finales
        ))

        umbrales_agente = {}
        umbrales_agente.update(UMBRALES_UTILIDAD.get(rol, {}))
        umbrales_agente.update(UMBRALES_UTILIDAD.get(nombre_agente, {}))

        if umbrales_agente and stats_finales:
            for stat_key, umbral in umbrales_agente.items():
                val_actual = stats_finales.get(stat_key, 0.0)
                try:
                    val_actual = float(val_actual)
                except Exception:
                    continue
                if val_actual < umbral:
                    nombre_stat = _nombre_stat(stat_key)
                    consejos.append((
                        ft.Icons.PRIORITY_HIGH,
                        f"Umbral: {nombre_stat} insuficiente",
                        f"{val_actual:.0f} / {umbral:.0f} recomendado. "
                        f"Prioriza esta stat para que el efecto del agente funcione al máximo.",
                        ft.Colors.DEEP_ORANGE_300
                    ))

        return etiqueta_rol, consejos

    def _analizar_wengine(self, wengine_actual, wengines_config):
        consejos = []
        l_ideal = wengines_config.get("ideal", [])
        l_funcional = wengines_config.get("funcional", [])
        
        def extr(item): return item[0] if isinstance(item, tuple) else item
        
        if not wengine_actual or wengine_actual == "Ninguno":
            return [(ft.Icons.WARNING_AMBER, "Sin W-Engine", "No tienes un arma equipada.", ft.Colors.RED)]
            
        es_ideal = any(extr(i).lower() in wengine_actual.lower() for i in l_ideal)
        es_funcional = any(extr(f).lower() in wengine_actual.lower() for f in l_funcional)
        
        if es_ideal:
            consejos.append((ft.Icons.VERIFIED, f"W-Engine: {wengine_actual}", "¡Arma Ideal!", ft.Colors.GREEN))
        elif es_funcional:
            consejos.append((ft.Icons.CHECK, f"W-Engine: {wengine_actual}", "Arma Funcional.", ft.Colors.CYAN))
        else:
            sugerencia = ", ".join([extr(w) for w in l_ideal[:2]]) if l_ideal else "Consultar lista"
            consejos.append((ft.Icons.FLASH_OFF, f"W-Engine: {wengine_actual}", f"Ineficiente. Busca: {sugerencia}", ft.Colors.RED_ACCENT))
        return consejos
    
    def _analizar_sets(self, sets_activos, sets_config):
        consejos = []
        
        recom_4pc = sets_config.get("4pc", [])
        recom_2pc = sets_config.get("2pc", [])
        
        def extr(item): return item[0] if isinstance(item, tuple) else item
        
        sets_procesados = {}
        if isinstance(sets_activos, dict):
            if any(k.startswith('set') for k in sets_activos.keys()):
                for slot, nombre_set in sets_activos.items():
                    if not nombre_set or nombre_set == "Ninguno": continue
                    cantidad = 4 if slot == 'set1' else 2
                    sets_procesados[nombre_set] = sets_procesados.get(nombre_set, 0) + cantidad
            else:
                for k, v in sets_activos.items():
                    try: sets_procesados[k] = int(v)
                    except: pass
        
        sets_encontrados = 0
        
        for nombre_set, cantidad in sets_procesados.items():
            if cantidad >= 2:
                sets_encontrados += 1
                
                if cantidad >= 4:
                    es_ideal_4pc = any(extr(i).lower() in nombre_set.lower() for i in recom_4pc)
                    
                    if es_ideal_4pc:
                        consejos.append((ft.Icons.VERIFIED_USER, f"Set 4pz: {nombre_set}", "¡Efecto 4pc Ideal!", ft.Colors.GREEN))
                    else:
                        es_bueno_2pc = any(extr(i).lower() in nombre_set.lower() for i in recom_2pc)
                        if es_bueno_2pc:
                            consejos.append((ft.Icons.INFO, f"Set 4pz: {nombre_set}", "El bono 4pc no es meta, pero el 2pc sirve.", ft.Colors.ORANGE))
                        else:
                            consejos.append((ft.Icons.HIGHLIGHT_OFF, f"Set 4pz: {nombre_set}", "Ineficiente para este agente.", ft.Colors.RED))
                
                else:
                    es_ideal_2pc = any(extr(i).lower() in nombre_set.lower() for i in recom_2pc)
                    es_ideal_4pc = any(extr(i).lower() in nombre_set.lower() for i in recom_4pc) 
                    
                    if es_ideal_2pc or es_ideal_4pc:
                        consejos.append((ft.Icons.CHECK, f"Set 2pz: {nombre_set}", "Buen complemento de stats.", ft.Colors.CYAN))
                    else:
                        consejos.append((ft.Icons.HIGHLIGHT_OFF, f"Set 2pz: {nombre_set}", "Aporta poco valor.", ft.Colors.BLUE_GREY_200))

        if sets_encontrados == 0:
             consejos.append((ft.Icons.BROKEN_IMAGE, "Sin Sets", "Equipa discos para obtener bonos.", ft.Colors.RED))
             
        return consejos

    def _generar_consejos_subs(self, rolls, l_ideal, l_decente, l_basura,
                                nombre_agente, rol, stats_finales=None):
        """
        Analiza la distribución de rolls y genera consejos concretos.
        Considera:
        - Crit cap (100%) y PEN cap (100%) para detectar excesos
        - Proporción ideal/decente/basura relativa al total
        - Aviso si stats relevantes están muy bajas
        """
        consejos = []
        total_rolls = sum(rolls.values()) if rolls else 0

        if total_rolls < 45:
            faltantes = 54 - total_rolls
            consejos.append((
                ft.Icons.AUTO_GRAPH, "Substats",
                f"Progreso: {int((total_rolls / 54) * 100)}% — faltan ~{faltantes} tiradas.",
                ft.Colors.BLUE_GREY
            ))
        else:
            consejos.append((
                ft.Icons.VERIFIED, "Substats",
                f"Maxeadas ({total_rolls}/54).",
                ft.Colors.TEAL
            ))

        if not rolls:
            return consejos

        c_ideal  = sum(rolls.get(s, 0) for s in l_ideal)
        c_decente = sum(rolls.get(s, 0) for s in l_decente)
        c_basura  = sum(rolls.get(s, 0) for s in l_basura)

        cr_key  = "Probabilidad_crítico_porcentual"
        cr_val  = (stats_finales or {}).get("Probabilidad_crítico", 0.0)
        cr_rolls = rolls.get(cr_key, 0)
        if cr_val > 100.0 and cr_rolls > 0:
            exceso_cr = min(cr_rolls, int((cr_val - 100.0) / 2.4) + 1)
            consejos.append((
                ft.Icons.WARNING_AMBER, "Crit Rate excedido",
                f"{cr_val:.1f}% — {exceso_cr} roll(s) desperdiciados sobre el cap. "
                f"Redirige a Crit DMG o ATK%.",
                ft.Colors.ORANGE
            ))

        pen_key  = "Tasa_de_Perforación_porcentual"
        pen_val  = (stats_finales or {}).get("Tasa_de_Perforación", 0.0)
        pen_rolls = rolls.get(pen_key, 0)
        if pen_val > 100.0 and pen_rolls > 0:
            exceso_pen = min(pen_rolls, int((pen_val - 100.0) / 2.4) + 1)
            consejos.append((
                ft.Icons.WARNING_AMBER, "PEN Ratio excedido",
                f"{pen_val:.1f}% — {exceso_pen} roll(s) sobre el cap (100%). "
                f"Prioriza otras stats.",
                ft.Colors.ORANGE
            ))

        if stats_finales:
            dinamico = calcular_pesos_dinamicos_substats(
                nombre_agente, rol, stats_finales, EXCEPCIONES_AGENTES, CONFIG_ROLES
            )
            prioridad = dinamico.get("prioridad", [])
            if prioridad:
                top = prioridad[0]
                consejos.append((
                    ft.Icons.TRENDING_UP,
                    self._t("recom.prioridad_dinamica", "Prioridad dinámica: {stat}", stat=_nombre_stat(top["substat"])),
                    self._t(
                        "recom.prioridad_dinamica_detalle",
                        "Por tus stats actuales, cada roll nuevo debería favorecer {stat}.",
                        stat=_nombre_stat(top["substat"]),
                    ),
                    ft.Colors.CYAN
                ))

            rolls_norm = {normalizar_clave_substat(k): v for k, v in rolls.items()}
            ajuste_saturado = next(
                (
                    a for a in dinamico.get("ajustes", [])
                    if rolls_norm.get(a.get("substat"), 0) > 0 and a.get("factor", 1.0) <= 0.70
                ),
                None,
            )
            if ajuste_saturado:
                stat_saturada = _nombre_stat(ajuste_saturado.get("substat"))
                mejor_stat = _nombre_stat(prioridad[0]["substat"]) if prioridad else stat_saturada
                motivos = ajuste_saturado.get("motivos", [])
                motivos_txt = ", ".join(
                    self._t(f"recom.motivo_{m}", m.replace("_", " "))
                    for m in motivos[:2]
                )
                consejos.append((
                    ft.Icons.SPEED,
                    self._t("recom.stat_saturada", "{stat} con bajo rendimiento", stat=stat_saturada),
                    self._t(
                        "recom.stat_saturada_detalle",
                        "{stat} ya rinde menos en esta build ({motivo}); busca más {mejor_stat}.",
                        stat=stat_saturada,
                        motivo=motivos_txt or self._t("recom.motivo_rendimiento_bajo", "rendimiento bajo"),
                        mejor_stat=mejor_stat,
                    ),
                    ft.Colors.ORANGE
                ))

        LIMITE_BASURA_ACEPTABLE = 6
        if c_basura > LIMITE_BASURA_ACEPTABLE:
            nombres_b = [_nombre_stat(s) for s in l_basura if rolls.get(s, 0) > 0]
            consejos.append((
                ft.Icons.DELETE_SWEEP, self._t("recom.exceso_basura", "Exceso de rolls basura"),
                self._t("recom.exceso_basura_detalle", "{n} tiradas en stats inútiles ({stats}). Ideal ≤6.", n=c_basura, stats=', '.join(nombres_b[:3])),
                ft.Colors.RED
            ))
        elif c_basura > 0:
            consejos.append((
                ft.Icons.INFO_OUTLINE, self._t("recom.rolls_inevitables", "Rolls inevitables"),
                self._t("recom.rolls_inevitables_detalle", "{n} tiradas en basura (aceptable, mínimo por mecánica).", n=c_basura),
                ft.Colors.BLUE_GREY_200
            ))

        nombres_i = [_nombre_stat(s) for s in l_ideal[:3]]
        pct_ideal = (c_ideal / max(total_rolls, 1)) * 100

        if c_ideal >= 40:
            consejos.append((ft.Icons.DIAMOND, self._t("recom.calidad_perfecta", "Calidad: PERFECTA"),
                             self._t("recom.rolls_ideales_dios", "{n} rolls ideales — build de Dios.", n=c_ideal), ft.Colors.AMBER))
        elif c_ideal >= 30:
            consejos.append((ft.Icons.DIAMOND, self._t("recom.calidad_excelente", "Calidad: Excelente"),
                             self._t("recom.rolls_ideales_pct", "{n} rolls ideales ({pct}%).", n=c_ideal, pct=f"{pct_ideal:.0f}"), ft.Colors.AMBER))
        elif c_ideal >= 20:
            consejos.append((ft.Icons.THUMB_UP, self._t("recom.calidad_buena", "Calidad: Buena"),
                             self._t("recom.rolls_ideales_pct", "{n} rolls ideales ({pct}%).", n=c_ideal, pct=f"{pct_ideal:.0f}"), ft.Colors.CYAN))
        elif total_rolls > 30:
            consejos.append((ft.Icons.SEARCH_OFF, self._t("recom.calidad_baja", "Calidad baja"),
                             self._t("recom.sigue_farmeando", "Solo {n} rolls en {stats}. Sigue farmando.", n=c_ideal, stats=', '.join(nombres_i)),
                             ft.Colors.ORANGE))

        for k, v in rolls.items():
            if v >= 15:
                nombre_k = _nombre_stat(k)
                if k in l_ideal:
                    consejos.append((ft.Icons.VERTICAL_ALIGN_TOP, self._t("recom.supertirada", "Supertirada: {stat}", stat=nombre_k),
                                     self._t("recom.supertirada_detalle", "¡{n} rolls! Un fijo de tu cuenta.", n=v), ft.Colors.AMBER))
                elif k in l_basura:
                    consejos.append((ft.Icons.WARNING, self._t("recom.tiradas_perdidas", "Tiradas perdidas: {stat}", stat=nombre_k),
                                     self._t("recom.tiradas_perdidas_detalle", "{n} rolls en stat no deseada.", n=v), ft.Colors.RED))

        return consejos

def normalizar_clave_substat(nombre: str, valor: str = "") -> str:
    """Normaliza cualquier nombre de substat de disco a su clave canónica interna."""
    n = str(nombre).lower().strip()
    import unicodedata
    n = ''.join(c for c in unicodedata.normalize('NFD', n) if unicodedata.category(c) != 'Mn')
    v = str(valor).strip()
    es_pct = "%" in v or "%" in n or "porcentual" in n or "ratio" in n

    # PEN Ratio / Tasa de Perforación (porcentual) — ANTES de "pen" genérico
    if "pen ratio" in n or "tasa_de_perforación" in n or "tasa de perforación" in n or "tasa_de_perforacion" in n:
        return "Tasa_de_Perforación_porcentual"

    # Impacto y PEN flat NO son substats de disco → descartar
    if "impact" in n or "impacto" in n:
        return ""
    if "pen" in n:
        return ""

    if "crit" in n and ("rate" in n or "prob" in n): return "Probabilidad_crítico_porcentual"
    if "crit" in n and ("dmg" in n or "daño" in n or "dano" in n): return "Daño_crítico_porcentual"
    if "prob" in n and "crit" not in n and "crít" not in n: return "Probabilidad_crítico_porcentual"
    if ("daño" in n or "dano" in n) and ("crit" in n or "crít" in n): return "Daño_crítico_porcentual"

    if "atk" in n or "ataque" in n:
        return "Ataque_porcentual" if es_pct else "Ataque_plano"
    if "hp" in n or "vida" in n:
        return "Puntos_Vida_porcentual" if es_pct else "Puntos_Vida_plano"
    if "def" in n or "defensa" in n:
        return "Defensa_porcentual" if es_pct else "Defensa_plano"
    if ("perfor" in n or "perf" in n) and "tasa" not in n and "porcentual" not in n:
        return "Perforación_Plana_plano"
    if "maestr" in n or "mastery" in n or "proficiency" in n or "prof" in n or "anomal" in n:
        return "Maestría_Anomalía_plano"
    if "energy" in n or "regen" in n or "recup" in n:
        return "Recuperación_energía_porcentual"

    return ""


def _float_stat(stats, *claves, default=0.0):
    for clave in claves:
        if clave in (stats or {}):
            try:
                return float(str(stats.get(clave, default)).replace("%", "").replace(",", "."))
            except Exception:
                return default
    return default


def _factor_rendimiento_substat(substat_key, stats_finales):
    """
    Factor de rendimiento decreciente para la calificacion de substats.
    No agrega stats nuevas: solo ajusta el valor de las que ya vienen del diccionario.
    """
    if not stats_finales:
        return 1.0, []

    notas = []
    factor = 1.0

    crit = _float_stat(stats_finales, "Probabilidad_crítico", "Probabilidad_critico")
    pen = _float_stat(stats_finales, "Tasa_de_Perforación", "Tasa_de_Perforacion")
    atk = _float_stat(stats_finales, "Ataque")
    atk_base = _float_stat(stats_finales, "Ataque_Base", "Ataque_base", "Base_ATK", default=0.0)
    dmg_elem = _float_stat(stats_finales, "Daño_elemental", "Dano_elemental")
    rec_energia = _float_stat(stats_finales, "Recuperación_energía", "Recuperacion_energia")

    if substat_key == "Probabilidad_crítico_porcentual":
        if crit >= 100.0:
            return 0.0, ["crit_cap"]
        if crit >= 95.0:
            factor *= 0.25
            notas.append("crit_casi_cap")
        elif crit >= 90.0:
            factor *= 0.55
            notas.append("crit_alto")
        elif crit >= 80.0:
            factor *= 0.85
            notas.append("crit_estable")

    elif substat_key == "Daño_crítico_porcentual":
        if 0 < crit < 35.0:
            factor *= 0.70
            notas.append("crit_rate_bajo")
        elif 35.0 <= crit < 50.0:
            factor *= 0.85
            notas.append("crit_rate_medio")
        elif crit >= 80.0:
            factor *= 1.05
            notas.append("crit_rate_solido")

    elif substat_key == "Tasa_de_Perforación_porcentual":
        if pen >= 100.0:
            return 0.0, ["pen_cap"]
        if pen >= 90.0:
            factor *= 0.35
            notas.append("pen_alto")
        elif pen >= 75.0:
            factor *= 0.70
            notas.append("pen_estable")

    elif substat_key in ("Ataque_porcentual", "Ataque_plano"):
        if atk_base > 0 and atk > 0:
            ratio = atk / max(atk_base, 1.0)
            if ratio >= 4.2:
                factor *= 0.50
                notas.append("atk_saturado")
            elif ratio >= 3.6:
                factor *= 0.70
                notas.append("atk_alto")
            elif ratio >= 3.0:
                factor *= 0.85
                notas.append("atk_estable")
        elif atk >= 3600:
            factor *= 0.55
            notas.append("atk_saturado")
        elif atk >= 3200:
            factor *= 0.70
            notas.append("atk_alto")
        elif atk >= 2800:
            factor *= 0.85
            notas.append("atk_estable")

        if substat_key == "Ataque_plano":
            factor *= 0.85

    elif substat_key == "Recuperación_energía_porcentual":
        if rec_energia >= 160:
            factor *= 0.50
            notas.append("energia_alta")
        elif rec_energia >= 140:
            factor *= 0.75
            notas.append("energia_estable")

    elif substat_key == "Daño_elemental" and dmg_elem > 75.0:
        factor *= max(0.45, 1.0 - ((dmg_elem - 75.0) / 100.0))
        notas.append("dano_elemental_alto")

    return max(0.0, min(factor, 1.20)), notas


def calcular_pesos_dinamicos_substats(nombre_agente, rol_agente, stats_finales, excepciones, config_roles):
    config_rol = config_roles.get(rol_agente, config_roles.get("Atacante", {}))
    excep = excepciones.get(nombre_agente)
    if not excep:
        def _norm(s): return s.lower().replace("-", "").replace("  ", " ").strip()
        nombre_norm = _norm(nombre_agente)
        mejor_match = None
        mejor_len = 0
        for clave in excepciones:
            clave_norm = _norm(clave)
            if clave_norm == nombre_norm:
                mejor_match = clave
                break
            if clave_norm in nombre_norm or nombre_norm in clave_norm:
                if len(clave_norm) > mejor_len:
                    mejor_len = len(clave_norm)
                    mejor_match = clave
        if mejor_match:
            excep = excepciones[mejor_match]
    if excep and "subs" in excep:
        config_rol = dict(config_rol)
        config_rol["subs"] = excep["subs"]

    subs_cfg = config_rol.get("subs", {})
    pesos_base = {}
    for stat in subs_cfg.get("ideal", []):
        clave = normalizar_clave_substat(stat)
        if clave:
            pesos_base[clave] = max(pesos_base.get(clave, 0.0), 1.5)
    for stat in subs_cfg.get("decente", []):
        clave = normalizar_clave_substat(stat)
        if clave and clave not in pesos_base:
            pesos_base[clave] = 1.0

    pesos = {}
    ajustes = []
    for clave, peso_base in pesos_base.items():
        factor, notas = _factor_rendimiento_substat(clave, stats_finales)
        peso_final = round(peso_base * factor, 4)
        pesos[clave] = peso_final
        if notas or abs(factor - 1.0) > 0.001:
            ajustes.append({
                "substat": clave,
                "peso_base": round(peso_base, 4),
                "peso_final": peso_final,
                "factor": round(factor, 4),
                "motivos": notas,
            })

    prioridad = [
        {
            "substat": clave,
            "peso": peso,
            "peso_base": pesos_base.get(clave, 0.0),
            "factor": round(peso / pesos_base.get(clave, 1.0), 4) if pesos_base.get(clave) else 0.0,
        }
        for clave, peso in pesos.items()
        if peso > 0
    ]
    prioridad.sort(key=lambda x: x["peso"], reverse=True)

    return {"pesos": pesos, "prioridad": prioridad, "ajustes": ajustes}


def evaluar_calidad_global(nombre_agente, rol_agente, rolls_actuales, stats_finales, eficiencia_wengine_actual, excepciones, config_roles, tiene_4pc: bool = True, num_discos: int = 6):
    """
    Evalúa la calidad de la build unificando lógica de GUI y Calculadora:
    Incluye hard caps (Prob, Perforación) y soft caps (Daño Elemental).
    """
    resumen_rolls = {
        "ideal": 0, "decente": 0, "basura": 0, "total_rolls": 0,
        "puntaje_total": 0, "puntaje_total_clasico": 0,
        "calidad_pct": 0, "calidad_clasica_pct": 0,
        "calidad_dinamica_pct": 0, "calidad_dinamica_raw_pct": 0,
        "penalizacion_dinamica_pct": 0,
        "pesos_dinamicos": {}, "prioridad_dinamica": [], "ajustes_dinamicos": []
    }
    config_rol = config_roles.get(rol_agente, config_roles.get("Atacante", {}))
    
    # Match fuzzy del nombre del agente en excepciones
    excep = excepciones.get(nombre_agente)
    if not excep:
        def _norm(s): return s.lower().replace("-", "").replace("  ", " ").strip()
        nombre_norm = _norm(nombre_agente)
        mejor_match = None
        mejor_len = 0
        for clave in excepciones:
            clave_norm = _norm(clave)
            if clave_norm == nombre_norm:
                mejor_match = clave
                break
            if clave_norm in nombre_norm or nombre_norm in clave_norm:
                if len(clave_norm) > mejor_len:
                    mejor_len = len(clave_norm)
                    mejor_match = clave
        if mejor_match:
            excep = excepciones[mejor_match]
    if excep and "subs" in excep:
        config_rol = dict(config_rol) 
        config_rol["subs"] = excep["subs"]
    
    ideales_norm = {normalizar_clave_substat(k) for k in config_rol.get("subs", {}).get("ideal", [])} - {""}
    decentes_norm = {normalizar_clave_substat(k) for k in config_rol.get("subs", {}).get("decente", [])} - {""}
    analisis_dinamico = calcular_pesos_dinamicos_substats(
        nombre_agente, rol_agente, stats_finales, excepciones, config_roles
    ) if stats_finales else {"pesos": {}, "prioridad": [], "ajustes": []}
    pesos_dinamicos = analisis_dinamico.get("pesos", {})
    resumen_rolls["pesos_dinamicos"] = pesos_dinamicos
    resumen_rolls["prioridad_dinamica"] = analisis_dinamico.get("prioridad", [])
    resumen_rolls["ajustes_dinamicos"] = analisis_dinamico.get("ajustes", [])

    exceso_crit_rolls = 0
    exceso_pen_rolls = 0
    penalizacion_dmg_elem = 0
    
    if stats_finales:
        crit = stats_finales.get("Probabilidad_crítico", 0)
        if crit > 100.0: exceso_crit_rolls = int((crit - 100.0) // 2.4)
        
        pen = stats_finales.get("Tasa_de_Perforación", 0)
        if pen > 100.0: exceso_pen_rolls = int((pen - 100.0) // 2.4)
            
        dmg_elem = stats_finales.get("Daño_elemental", 0)
        if dmg_elem > 75.0:
            exceso = dmg_elem - 75.0
            penalizacion_dmg_elem = exceso * 0.5 

    if rolls_actuales:
        for key_ui, cantidad in rolls_actuales.items():
            if cantidad > 0:
                key_limpia = normalizar_clave_substat(key_ui)
                resumen_rolls["total_rolls"] += cantidad
                cantidad_efectiva = cantidad
                
                if key_limpia == "Probabilidad_crítico_porcentual" and exceso_crit_rolls > 0:
                    desp = min(cantidad_efectiva, exceso_crit_rolls)
                    exceso_crit_rolls -= desp
                    cantidad_efectiva -= desp
                    resumen_rolls["basura"] += desp
                    
                if key_limpia == "Tasa_de_Perforación_porcentual" and exceso_pen_rolls > 0:
                    desp = min(cantidad_efectiva, exceso_pen_rolls)
                    exceso_pen_rolls -= desp
                    cantidad_efectiva -= desp
                    resumen_rolls["basura"] += desp 
                
                if key_limpia in ideales_norm:
                    resumen_rolls["ideal"] += cantidad_efectiva
                    resumen_rolls["puntaje_total_clasico"] += cantidad_efectiva * 1.5
                    resumen_rolls["puntaje_total"] += cantidad_efectiva * pesos_dinamicos.get(key_limpia, 1.5)
                elif key_limpia in decentes_norm:
                    resumen_rolls["decente"] += cantidad_efectiva
                    resumen_rolls["puntaje_total_clasico"] += cantidad_efectiva * 1.0
                    resumen_rolls["puntaje_total"] += cantidad_efectiva * pesos_dinamicos.get(key_limpia, 1.0)
                else:
                    resumen_rolls["basura"] += cantidad_efectiva
                    
        resumen_rolls["puntaje_total"] = max(0, resumen_rolls["puntaje_total"] - penalizacion_dmg_elem)
        resumen_rolls["puntaje_total_clasico"] = max(0, resumen_rolls["puntaje_total_clasico"] - penalizacion_dmg_elem)

    cantidad_ideales = len(ideales_norm)
    factor_indulgencia = 1.0
    if cantidad_ideales == 1: factor_indulgencia = 0.65
    elif cantidad_ideales == 2: factor_indulgencia = 0.78 
    elif cantidad_ideales >= 3: factor_indulgencia = 0.95 
        
    if nombre_agente in ["Miyabi"]: 
        factor_indulgencia = 0.95

    TOTAL_ROLLS_MAXIMOS = 54
    max_pts_substats = TOTAL_ROLLS_MAXIMOS * 1.5 * factor_indulgencia
    calidad_substats = min((resumen_rolls["puntaje_total"] / max_pts_substats) * 100, 100)
    calidad_substats_clasica = min((resumen_rolls["puntaje_total_clasico"] / max_pts_substats) * 100, 100)
    
    peso_arma = 0.10
    peso_substats = 0.90
    factor_arma = eficiencia_wengine_actual / 100.0

    def _calidad_final(calidad_base_substats):
        calidad = min((calidad_base_substats * peso_substats) + (factor_arma * 100 * peso_arma), 100)
        if not tiene_4pc:
            calidad *= 0.70
        if num_discos < 6:
            calidad *= 0.70
        if eficiencia_wengine_actual == 0:
            calidad = max(0, calidad * 0.50)
        return calidad
    
    calidad_clasica_final = _calidad_final(calidad_substats_clasica)
    calidad_dinamica_raw = _calidad_final(calidad_substats)

    if stats_finales and resumen_rolls["ajustes_dinamicos"]:
        if calidad_dinamica_raw < calidad_clasica_final:
            distancia = calidad_clasica_final - calidad_dinamica_raw
            penalizacion = min(distancia * 0.25, 10.0)
            calidad_dinamica_final = calidad_clasica_final - penalizacion
        else:
            penalizacion = 0.0
            calidad_dinamica_final = min(calidad_dinamica_raw, calidad_clasica_final + 4.0)
    else:
        penalizacion = 0.0
        calidad_dinamica_final = calidad_clasica_final

    resumen_rolls["calidad_clasica_pct"] = calidad_clasica_final
    resumen_rolls["calidad_dinamica_raw_pct"] = calidad_dinamica_raw
    resumen_rolls["calidad_dinamica_pct"] = calidad_dinamica_final
    resumen_rolls["penalizacion_dinamica_pct"] = max(0.0, calidad_clasica_final - calidad_dinamica_final)
    resumen_rolls["calidad_pct"] = resumen_rolls["calidad_dinamica_pct"]

    return resumen_rolls

def generar_recomendaciones_texto(nombre_agente, rol_agente, elemento_agente, datos_agente_api=None, traductor=None):
    """
    Genera un diccionario con listas de texto formateado para la UI de recomendaciones.
    """
    _MAPA_STATS = {
        "Probabilidad_crítico": "prob_crit", "Daño_crítico": "dano_crit",
        "Ataque": "ataque", "Daño_elemental": "dano_elemental",
        "Tasa_de_Perforación": "perforacion", "Maestría_Anomalía": "maestria_anomalia",
        "Impacto": "impacto", "Recuperación_energía": "rec_energia",
        "Puntos_Vida": "puntos_vida", "Tasa_de_Anomalía": "tasa_anomalia",
        "Defensa": "defensa", "Perforación_Plana": "perf_plana",
    }

    def _t(clave, default=None, **kw):
        if traductor: return traductor.t(clave, default=default, **kw)
        return default if default else f"[{clave}]"

    def trad_stat(nombre_raw):
        """Traduce un nombre interno de stat (con o sin sufijo _porcentual/_plano)."""
        if not traductor:
            return nombre_raw.replace("_", " ").replace("porcentual", "%").replace("plano", "")
        base = nombre_raw.replace("_porcentual", "").replace("_plano", "")
        clave = _MAPA_STATS.get(base)
        if not clave:
            return traductor.t(f"stats.{base.lower().replace(' ', '_')}", default=nombre_raw.replace("_", " "))
        texto = traductor.t(f"stats.{clave}", default=base.replace("_", " "))
        if "_porcentual" in nombre_raw and "%" not in texto:
            texto += " %"
        elif "_plano" in nombre_raw:
            flat_key = {"Ataque": "ataque_plano", "Defensa": "defensa_plana",
                        "Puntos_Vida": "vida_plana", "Perforación_Plana": "perf_plana",
                        "Maestría_Anomalía": "maestria_anomalia"}.get(base)
            if flat_key:
                texto = traductor.t(f"stats.{flat_key}", default=texto)
        return texto

    def trad_set(nombre_set):
        if not traductor: return nombre_set
        return traductor.t(f"sets.{nombre_set}", default=nombre_set)

    config = CONFIG_ROLES.get(rol_agente, CONFIG_ROLES["Atacante"]).copy()
    sets_rol = CONFIG_SETS_ROLES.get(rol_agente, {"ideal": [], "funcional": []}).copy()
    sets_elementales = MAPA_SETS_ELEMENTALES.get(elemento_agente, [])
    wengines_config = {"ideal": [], "funcional": []}
    
    if nombre_agente in EXCEPCIONES_AGENTES:
        excepcion = EXCEPCIONES_AGENTES[nombre_agente]
        
        for key in ["main_4", "main_5", "main_6", "subs"]:
            if key in excepcion: config[key] = excepcion[key]
            
        if "sets" in excepcion:
            custom_sets = excepcion["sets"]
            if "ideal" in custom_sets:
                sets_rol["ideal"] = custom_sets["ideal"]
                sets_rol["funcional"] = custom_sets.get("funcional", [])
            elif "4pc" in custom_sets:
                sets_rol["ideal"] = custom_sets["4pc"]
                sets_rol["funcional"] = custom_sets.get("2pc", [])

        if "wengines" in excepcion:
            wengines_config = excepcion["wengines"]

    def extr(item): return item[0] if isinstance(item, tuple) else item

    sets_out = []
    if sets_rol.get("ideal"):
        nombres = ', '.join([trad_set(extr(s)) for s in sets_rol['ideal']])
        sets_out.append(_t("ui.tab_recomendaciones.recom_meta", default=f"Meta: {nombres}").replace("{sets}", nombres))

    extras_raw = sets_rol.get("funcional", []) + [s for s in sets_elementales if s not in sets_rol.get("ideal", [])]
    extras = list(dict.fromkeys([extr(s) for s in extras_raw])) 
    
    if extras:
        nombres = ', '.join([trad_set(s) for s in extras[:3]])
        sets_out.append(_t("ui.tab_recomendaciones.recom_opciones", default=f"Opciones: {nombres}").replace("{sets}", nombres))
        
    w_out = []
    w_ideales = [extr(w) for w in wengines_config.get("ideal", [])]
    if w_ideales:
        nombres = ', '.join(w_ideales)
        w_out.append(_t("ui.tab_recomendaciones.recom_bis", default=f"S-Rank / BiS: {nombres}").replace("{wengines}", nombres))
        
    w_funcionales = [extr(w) for w in wengines_config.get("funcional", [])]
    if w_funcionales:
        nombres = ', '.join(w_funcionales)
        w_out.append(_t("ui.tab_recomendaciones.recom_alternativas", default=f"Alternativas: {nombres}").replace("{wengines}", nombres))
        
    if not w_out:
        w_out.append(_t("ui.tab_recomendaciones.recom_wengine_generico", default="Cualquiera que aporte ATK o stats ofensivas."))
        
    m_out = []
    def fmt_stats(lista):
        return " / ".join([trad_stat(s) for s in lista])
        
    m_out.append(_t("ui.tab_recomendaciones.recom_disco_iv", default=f"Disco IV: {fmt_stats(config['main_4']['general'])}").replace("{stats}", fmt_stats(config['main_4']['general'])))
    m_out.append(_t("ui.tab_recomendaciones.recom_disco_v", default=f"Disco V: {fmt_stats(config['main_5']['general'])}").replace("{stats}", fmt_stats(config['main_5']['general'])))
    m_out.append(_t("ui.tab_recomendaciones.recom_disco_vi", default=f"Disco VI: {fmt_stats(config['main_6']['general'])}").replace("{stats}", fmt_stats(config['main_6']['general'])))

    s_out = []
    if config["subs"].get("ideal"):
        stats_txt = fmt_stats(config['subs']['ideal'])
        s_out.append(_t("ui.tab_recomendaciones.recom_prioridad", default=f"Prioridad: {stats_txt}").replace("{stats}", stats_txt))
    if config["subs"].get("decente"):
        stats_txt = fmt_stats(config['subs']['decente'])
        s_out.append(_t("ui.tab_recomendaciones.recom_utiles", default=f"Útiles: {stats_txt}").replace("{stats}", stats_txt))
    
    return {
        "sets": sets_out,
        "wengines": w_out,
        "main_stats": m_out,
        "sub_stats": s_out
    }


def calificacion_a_tier(calificacion_pct: float) -> tuple:
    if calificacion_pct >= 95: return ('GODLIKE', '#ffffff')
    if calificacion_pct >= 85: return ('FLAWLESS', '#00ffff')
    if calificacion_pct >= 75: return ('GREAT', '#ffea00')
    if calificacion_pct >= 60: return ('SOLID', '#ff6d00')
    if calificacion_pct >= 50: return ('DECENT', '#e78f4b')
    if calificacion_pct >= 40: return ('AVERAGE', '#2979ff')
    return ('MID', '#9e9e9e')

def calificacion_a_color_semaforo(calificacion_pct: float) -> str:
    if calificacion_pct >= 80: return '#388e3c'
    if calificacion_pct >= 70: return '#f57c00'
    if calificacion_pct >= 40: return '#c62828'
    return '#616161'

_PALETA_ARCOIRIS = [
    '#ff0000', '#00ff00', '#0000ff', '#ff00ff', '#00ffff', '#ffff00',
    '#ff0a54', '#9d4edd', '#390099', '#ff5400', '#00bbf9', '#00f5d4'
]

def construir_sombra_tier(tier_clave, color_hex):
    import random
    if tier_clave == 'GODLIKE':
        luz = random.sample(_PALETA_ARCOIRIS, 4)
        return [
            ft.BoxShadow(blur_radius=22, spread_radius=4, color=luz[0], offset=ft.Offset(-4, -4)),
            ft.BoxShadow(blur_radius=22, spread_radius=4, color=luz[1], offset=ft.Offset(4, -4)),
            ft.BoxShadow(blur_radius=22, spread_radius=4, color=luz[2], offset=ft.Offset(4, 4)),
            ft.BoxShadow(blur_radius=22, spread_radius=4, color=luz[3], offset=ft.Offset(-4, 4)),
        ]
    return ft.BoxShadow(blur_radius=20, spread_radius=3, color=color_hex)
