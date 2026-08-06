from traductor import traductor_global as i18n

CONFIG_SETS = {
    "Tecno Pícido": {"max_stacks": 3, "nombre_stack": i18n.t("ui.sets_cond.cargas", default="Cargas"), "usa_condicion": False},
    "Voz Astral": {"max_stacks": 3, "nombre_stack": i18n.t("ui.sets_cond.cargas", default="Cargas"), "usa_condicion": False},
    "Armonía Umbría": {"max_stacks": 3, "nombre_stack": i18n.t("ui.sets_cond.cargas", default="Cargas"), "usa_condicion": False},
    "Fábula Yunkui": {"max_stacks": 3, "nombre_stack": i18n.t("ui.sets_cond.cargas", default="Cargas"), "usa_condicion": False},
    "Metal colmilludo": {"max_stacks": 0, "usa_condicion": True, "texto_condicion": i18n.t("ui.sets_cond.assault", default="¿Aplicaste Assault?")},
    "Metal caótico": {"max_stacks": 6, "nombre_stack": i18n.t("ui.sets_cond.triggers", default="Triggers"), "usa_condicion": True, "texto_condicion": i18n.t("ui.sets_cond.corrupcion", default="¿Aplicaste Corrupción?")},
    "Metal eléctrico": {"max_stacks": 0, "usa_condicion": True, "texto_condicion": i18n.t("ui.sets_cond.shock", default="¿Aplicaste Shock?")},
    "Metal infernal": {"max_stacks": 0, "usa_condicion": True, "texto_condicion": i18n.t("ui.sets_cond.burn", default="¿Aplicaste Burn?")},
    "Metal Polar": {"max_stacks": 0, "usa_condicion": True, "texto_condicion": i18n.t("ui.sets_cond.freeze_shatter", default="¿Aplicaste Freeze o Shatter?")},
    "Balada de la rama y la espada": {"max_stacks": 0, "usa_condicion": True, "texto_condicion": i18n.t("ui.sets_cond.freeze_shatter", default="¿Aplicaste Freeze o Shatter?")},
    "Punk Hormonal": {"max_stacks": 0, "usa_condicion": True, "texto_condicion": i18n.t("ui.sets_cond.switcheo_campo", default="¿Switcheaste al campo?")},
    "Tecno Tetraodóntido": {"max_stacks": 0, "usa_condicion": True, "texto_condicion": i18n.t("ui.sets_cond.lanzaste_ultimate", default="¿Lanzaste Ultimate?")},
    "Disco sacudestrellas": {"max_stacks": 0, "usa_condicion": False},
    "Jazz Oscilante": {"max_stacks": 0, "usa_condicion": True, "texto_condicion": i18n.t("ui.sets_cond.ataque_cadena", default="¿Usaste Cadena/Ultimate?")},
    "Rock espiritual": {"max_stacks": 0, "usa_condicion": False},
    "Floración del alba": {"max_stacks": 0, "usa_condicion": True, "texto_condicion": i18n.t("ui.sets_cond.ex_o_ultimate", default="¿Usaste EX o Ultimate?")},
    "Blues Libre": {"max_stacks": 0, "usa_condicion": True, "texto_condicion": i18n.t("ui.sets_cond.habilidad_ex", default="¿Usaste Habilidad EX?")},
    "Nana a la Luz Cenicienta": {"max_stacks": 0, "usa_condicion": True, "texto_condicion": i18n.t("ui.sets_cond.ex_o_ultimate", default="¿Usaste EX o Ultimate?")},
    "Balada de Aguas Blancas": {"max_stacks": 0, "usa_condicion": True, "texto_condicion": i18n.t("ui.sets_cond.ether_veil", default="¿Dentro de Ether Veil? (Atacante)")},
    "Aria Radiante": {"max_stacks": 0, "usa_condicion": True, "texto_condicion": i18n.t("ui.sets_cond.enemigo_stunneado", default="¿Enemigo Stunneado?")},
    "Conejo en el país de las maravillas": {"max_stacks": 3, "nombre_stack": i18n.t("ui.sets_cond.cargas", default="Cargas"), "usa_condicion": False},
    "Diario de una prisionera": {"max_stacks": 0, "usa_condicion": True, "texto_condicion": i18n.t("ui.sets_cond.abloom_o_freeze", default="¿Activaste Abloom/Freeze?")},
    "Monarca del Pináculo": {"max_stacks": 0, "usa_condicion": True, "texto_condicion": i18n.t("ui.sets_cond.ex_o_ultimate", default="¿Usaste EX o Ultimate?")},
    "Melodía de Phaeton": {"max_stacks": 0, "usa_condicion": True, "texto_condicion": i18n.t("ui.sets_cond.habilidad_ex", default="¿Usaste Habilidad EX?")}
}

def efecto_chaos_jazz(stats_actuales, elemento=None, stacks=0, condicion_activa=False, tipo_agente=None, **kwargs):
    """
    Jazz caótico (Chaos Jazz):
    - +15% Daño Fuego y Eléctrico.
    - +20% Daño de Ex/Assist.
    """
    bonos = {}
    if elemento and elemento.lower() in ["fuego", "electrico"]:
        bonos["Daño_elemental"] = 15.0
        bonos["Bono_Dano_Ex"] = 20.0
        bonos["Bono_Dano_Assist"] = 20.0
        bonos["Bono_Dano_Ex"] = 20.0
    return bonos

def efecto_fanged_metal(stats_actuales, elemento=None, stacks=0, condicion_activa=False, tipo_agente=None, **kwargs):
    """
    Metal colmilludo (Fanged Metal):
    - (Mejor Caso) Enemigo bajo Assault -> +35% Daño.
    """
    bonos = {}

    fisico = elemento and "físico" in elemento.lower()

    if fisico and condicion_activa:
        bonos["Daño_Adicional"] = 35.0
        
    return bonos

def efecto_thunder_metal(stats_actuales, elemento=None, stacks=0, condicion_activa=False, tipo_agente=None, **kwargs):
    """
    Metal eléctrico (Thunder Metal):
    - (Mejor Caso) Enemigo bajo Shock -> +28% Atk.
    """
    bonos = {}
    electro = elemento and "electrico" in elemento.lower()
    
    if electro and condicion_activa:
        bonos["Ataque"] = 28.0
    return bonos

def efecto_chaotic_metal(stats_actuales, elemento=None, stacks=0, condicion_activa=False, tipo_agente=None, **kwargs):
    """
    Metal caótico (Chaotic Metal):
    - +20% Daño Crítico.
    - (Mejor Caso) Corruption stack max -> +33% Crit DMG extra.
    Total: 53% Daño Crítico.
    """
    bonos = {}
    
    bonos["Daño_crítico"] = 20.0 

    if condicion_activa:
        stacks_reales = int(stacks) if stacks else 0
        extra_cd = 5.5 * stacks_reales
        

        bonos["Daño_crítico"] += extra_cd

    return bonos

def efecto_Inferno_Metal(stats_actuales, elemento=None, stacks=0, condicion_activa=False, tipo_agente=None, **kwargs):
    """
    Metal infernal (Inferno Metal):
    - (Mejor Caso) Enemigo bajo Burn -> +28% crit rate.
    """
    bonos = {}
    
    fuego = elemento and "fuego" in elemento.lower()

    if fuego and condicion_activa:
        bonos["Probabilidad_crítico"] = 28.0

    return bonos

def efecto_polar_metal(stats_actuales, elemento=None, stacks=0, condicion_activa=False, tipo_agente=None, **kwargs):
    """
    Metal Polar (Polar Metal):
    - Aumenta el daño de Ataque Básico y Dash en 20%.
    - Si cualquier miembro congela (Freeze) o rompe hielo (Shatter) -> +20% extra.
    Total máximo: 40.0%
    """
    bonos = {}

    efecto = 20.0

    if condicion_activa:
        efecto += 20
    
    bonos["Bono_Dano_Basico"] = efecto
    bonos["Bono_Dash"] = efecto

    return bonos

def efecto_branch_blade_song(stats_actuales, elemento=None, stacks=0, condicion_activa=False, tipo_agente=None, **kwargs):
    """
    Balada de la rama y la espada (Branch & Blade Song):
    - Si Maestría >= 115 -> +30% Daño Crítico.
    - (Mejor Caso) Trigger activo -> +12% Prob Crítica.
    """
    bonos = {}
    
    maestria = stats_actuales.get("Tasa_de_Anomalía", 0)
    
    if maestria >= 115:
        bonos["Daño_crítico"] = 30.0 
    
    if condicion_activa:
        bonos["Probabilidad_crítico"] = 12.0
    
    return bonos

def efecto_Yunkui_Tales(stats_actuales, elemento=None, stacks=0, condicion_activa=False, tipo_agente=None, **kwargs):
    """
    Fábula Yunkui(Yunkui Tales):
    - (Mejor Caso) acumulas las 3 cargas -> +12% crit rate.
    - Sheer -> +10% DMG  
    """
    bonos = {}

    stacks_reales = int(stacks) if stacks else 0
    bonos["Probabilidad_crítico"] = 4.0 * stacks_reales

    if stacks_reales >= 3:
        bonos["Daño_Adicional"] = 10.0


    return bonos

def efecto_hormone_punk(stats_actuales, elemento=None, stacks=0, condicion_activa=False, tipo_agente=None, **kwargs):
    """
    Punk Hormonal (Hormone Punk):
    - Efecto deseado: Multiplicar el Ataque Final acumulado por 1.25 (+25% Final).
    """
    bonos = {}
    if condicion_activa:
        bonos["Ataque"] = 25.0
    return bonos

def efecto_woodpecker_electro(stats_actuales, elemento=None, stacks=0, condicion_activa=False, tipo_agente=None, **kwargs):
    """
    Tecno Pícido (Woodpecker Electro):
    - 9% ATK por stack (Max 3 stacks = 27%).
    """
    bonos = {}
    stacks_reales = int(stacks) if stacks else 0
    
    if stacks_reales > 0:
        bonos["Ataque"] = 9.0 * stacks_reales
    return bonos

def efecto_Astral_Voice(stats_actuales, elemento=None, stacks=0, condicion_activa=False, tipo_agente=None, **kwargs):
    """
    Voz Astral (Astral Voice):
    - Aumenta el dmg 8% por stack (Max 3 stacks = 24%)
    """
    bonos = {}

    stacks_reales = int(stacks) if stacks else 0

    bonos["Daño_Adicional"] = stacks_reales * 8

    return bonos

def efecto_Swing_Jazz(stats_actuales, elemento=None, stacks=0, condicion_activa=False, tipo_agente=None, **kwargs):
    """
    Jazz Oscilante (Swing jazz):
    - Aumenta el dmg en un 15%
    """
    bonos = {}

    if condicion_activa:
        bonos["Daño_Adicional"] = 15.0

    return bonos

def efecto_Shadow_Harmony(stats_actuales, elemento=None, stacks=0, condicion_activa=False, tipo_agente=None, **kwargs):
    """
    Armonía Umbría (Shadow Harmony):
    - (Mejor Caso) acumulas las 3 cargas -> +12% crit rate + +12% atk.
    """

    bonos = {}
    stacks_reales = int(stacks) if stacks else 0

    if stacks_reales > 0:
        bonos["Ataque"] = 4.0 * stacks_reales
        bonos["Probabilidad_crítico"] = 4.0 * stacks_reales
    return bonos

def efecto_Puffer_Electro(stats_actuales, elemento=None, stacks=0, condicion_activa=False, tipo_agente=None, **kwargs):
    """
    Tecno Tetraodóntido (Puffer Electro):
    - Aumenta el daño de la ultimate en 20%.
    - Luego de lanzar la ultimate aumenta el atk en 15%
    """
    bonos = {}
    bonos["Bono_Dano_Ulti"] = 20.0

    if condicion_activa:
        bonos["Ataque"] = 15.0
    return bonos

def efecto_Dawns_Bloom(stats_actuales, elemento=None, stacks=0, condicion_activa=False, tipo_agente=None, **kwargs):
    """
    Floración del alba (Daw's Bloom)
    - basic dmg +20
    - cuando usa ex o ultimate +20 extras 
    """
    bonos = {}
    basica = 20.0

    if condicion_activa:
        basica += 20.0
    
    bonos['Bono_Dano_Basico'] = basica

    return bonos

def efecto_king_of_summit(stats_actuales, elemento=None, stacks=0, condicion_activa=False, tipo_agente=None, **kwargs):
    """
    Monarca del Pináculo (King of summit):
    - crit = +15
    - Si Prob >= 50 -> +15% crit.
    """

    bonos = {}
    proba = 0.0

    stunner = tipo_agente and "aturdidor" in tipo_agente.lower()
    prob = stats_actuales.get("Probabilidad_crítico", 0)


    if stunner:
        if condicion_activa:
            proba += 15.0 

        if prob >= 50:
            proba += 15.0
    bonos["Daño_crítico"] = proba

    return bonos

def efecto_Moonlight_Lullaby(stats_actuales, elemento=None, stacks=0, condicion_activa=False, tipo_agente=None, **kwargs):
    """
    Nana a la Luz Cenicienta (Moonlight Lullaby):
    - Aumenta el dmg en un 18%
    """
    bonos = {}

    soporte = tipo_agente and "soporte" in tipo_agente.lower()

    if condicion_activa and soporte:
        bonos["Daño_Adicional"] = 18.0

    return bonos

def efecto_Phaethons_Melody(stats_actuales, elemento=None, stacks=0, condicion_activa=False, tipo_agente=None, **kwargs):
    """
    Melodía de Phaeton (Phaethon's Melody):
    - Aumenta la tasa de anomalía en 45 puntos
    - Si el agente tira ex aumenta el daño elemental en 25%
    """
    bonos = {}
    ether = elemento and "etereo" in elemento.lower()

    if condicion_activa and ether:
        bonos['Tasa_de_Anomalía'] = 45.0
        bonos['Daño_elemental'] = 25.0

    return bonos

def efecto_Proto_Punk(stats_actuales, elemento=None, stacks=0, condicion_activa=False, tipo_agente=None, **kwargs):
    """
    Proto Punk (Proto Punk):
    - Aumenta el dmg en un 15%
    """
    bonos = {}

    if condicion_activa:
        bonos['Daño_Adicional'] = 15.0
    
    return bonos

def efecto_Shockstar_Disco(stats_actuales, elemento=None, stacks=0, condicion_activa=False, tipo_agente=None, **kwargs):
    """
    Disco sacudestrellas (Shockstar Disco):
    - Aumenta el dmg en un 15%
    """
    bonos = {}

    bonos['Bono_Stun_Basico'] = 20.0
    bonos['Bono_Stun_Assist'] = 20.0
    bonos['Bono_Stun_Dash'] = 20.0

    return bonos

def efecto_Shining_Aria(stats_actuales, elemento=None, stacks=0, condicion_activa=False, tipo_agente=None, **kwargs):
    """
    Aria Radiante (Shining Aria):
    - Aumenta la tasa de anomalía en 36 puntos
    - Si el enemigo está stunneado aumenta el dmg en 25%
    """
    bonos = {}

    bonos['Tasa_de_Anomalía'] = 36.0

    if condicion_activa:
        bonos['Daño_Adicional'] = 25.0

    return bonos

def efecto_White_Water_Ballad(stats_actuales, elemento=None, stacks=0, condicion_activa=False, tipo_agente=None, **kwargs):
    """
    Balada de Aguas Blancas (White Water Ballad):
    - Cuando hay ether viel aumenta la prob en 10%
    - Si es atacante +10% de prob y el atk aumenta un 10%
    """
    bonos = {}
    proba = 0.0 
    atacante = tipo_agente and "atacante" in tipo_agente.lower()

    if condicion_activa:
        proba += 10.0
        if atacante:
            proba += 10.0
            bonos["Ataque"] = 10.0
            
    if proba > 0:
        bonos["Probabilidad_crítico"] = proba
    return bonos

def efecto_Freedom_Blues(stats_actuales, elemento=None, stacks=0, condicion_activa=False, tipo_agente=None, **kwargs):
    """
    Blues Libre (Freedom Blues):
    - Cuando golpeas con una EX, reduce la Resistencia a la Anomalía del objetivo
      (correspondiente a tu elemento) en un 20%.
    """
    bonos = {}

    if condicion_activa:
        bonos['Reducción_Resistencia_Anomalía'] = 20.0

    return bonos

def efecto_Prisoners_Diary(stats_actuales, elemento=None, stacks=0, condicion_activa=False, tipo_agente=None, **kwargs):
    """
    Diario de una prisionera (Prisoner's Diary):
    - (Mejor Caso) Si activa Abloom -> +48 Tasa de Anomalía.
    - (Mejor Caso) Si aplica Congelación (Freeze) -> +16% Daño de Anomalía de Atributo y Daño de Desorden (Disorder).
    """
    bonos = {}
    
    if condicion_activa:
        bonos["Tasa_de_Anomalía"] = 48.0
        bonos["Bono_Daño_Anomalia"] = 16.0 
        bonos["Disorder_Extra_Mult"] = 16.0

    return bonos

def efecto_Wonderland_Rabbit(stats_actuales, elemento=None, stacks=0, condicion_activa=False, tipo_agente=None, **kwargs):
    """
    Conejo en el país de las maravillas (Wonderland Rabbit):
    - [Defensa] Aumenta el daño de todo el equipo en 6% por carga (Max 3 cargas = 18%).
    - Se activa con EX Special Attack o Assists.
    """
    bonos = {}
    
    defensa = tipo_agente and ("defensor" in tipo_agente.lower())
    
    if defensa:
        stacks_reales = int(stacks) if stacks else 0
        if stacks_reales > 0:
            bonos["Daño_Adicional"] = 6.0 * stacks_reales
            
    return bonos

MAPA_EFECTOS_SETS = {
    "Balada de la rama y la espada": efecto_branch_blade_song,
    "Jazz caótico": efecto_chaos_jazz,
    "Metal colmilludo": efecto_fanged_metal,
    "Metal caótico": efecto_chaotic_metal,
    "Punk Hormonal": efecto_hormone_punk,
    "Metal eléctrico": efecto_thunder_metal,
    "Metal infernal": efecto_Inferno_Metal,
    "Fábula Yunkui": efecto_Yunkui_Tales,
    "Metal Polar": efecto_polar_metal,
    "Tecno Tetraodóntido": efecto_Puffer_Electro,
    "Jazz Oscilante": efecto_Swing_Jazz,
    "Voz Astral": efecto_Astral_Voice,
    "Monarca del Pináculo": efecto_king_of_summit,
    "Tecno Pícido": efecto_woodpecker_electro,
    "Armonía Umbría": efecto_Shadow_Harmony,
    "Floración del alba": efecto_Dawns_Bloom,
    "Nana a la Luz Cenicienta": efecto_Moonlight_Lullaby,
    "Melodía de Phaeton": efecto_Phaethons_Melody,
    "Proto Punk": efecto_Proto_Punk,
    "Disco sacudestrellas": efecto_Shockstar_Disco,
    "Aria Radiante": efecto_Shining_Aria,
    "Balada de Aguas Blancas": efecto_White_Water_Ballad,
    "Blues Libre": efecto_Freedom_Blues,
    "Diario de una prisionera": efecto_Prisoners_Diary,
    "Conejo en el país de las maravillas": efecto_Wonderland_Rabbit,
}