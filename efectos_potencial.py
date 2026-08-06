KEYS = {
    "DMG_BONUS": "Daño_Adicional",
    "CRIT_DMG": "Daño_crítico",
    "CRIT_RATE": "Probabilidad_crítico",
    "ATK_PCT": "Ataque",
    "AFTERSHOCK_DMG": "Daño_Aftershock",
    "Reshielo": "Pen_Res_Hielo",
    "Reselectro": "Pen_Res_Electrico",
    "Impacto": "Impacto",
    "Elemental_Dmg": "Daño_elemental"
}

def potencial_soldier_0_anby(nivel):
    bonos = {}
    if nivel == 2:
        bonos[KEYS["AFTERSHOCK_DMG"]] = 34.0
    if nivel == 3:
        bonos[KEYS["AFTERSHOCK_DMG"]] = 38.0
    if nivel == 4:
        bonos[KEYS["AFTERSHOCK_DMG"]] = 42.0
    if nivel == 5:
        bonos[KEYS["AFTERSHOCK_DMG"]] = 46.0
    if nivel >= 6:
        bonos[KEYS["AFTERSHOCK_DMG"]] = 50.0 
    return bonos

def potencial_ellen(nivel):
    bonos = {}
    if nivel == 2:
        bonos[KEYS["CRIT_DMG"]] = 16.0
        bonos[KEYS["Reshielo"]] = 3.3
    if nivel == 3:
        bonos[KEYS["CRIT_DMG"]] = 24.0
        bonos[KEYS["Reshielo"]] = 5.0
    if nivel == 4:
        bonos[KEYS["CRIT_DMG"]] = 32.0
        bonos[KEYS["Reshielo"]] = 6.7
    if nivel == 5:
        bonos[KEYS["CRIT_DMG"]] = 40.0
        bonos[KEYS["Reshielo"]] = 8.3
    if nivel >= 6:
        bonos[KEYS["CRIT_DMG"]] = 48.0
        bonos[KEYS["Reshielo"]] = 10.0
    return bonos

def potencial_lycaon(nivel):
    bonos = {}
    if nivel == 2:
        bonos["Aumento_Impacto_%"] = 5.0
    if nivel == 3:
        bonos["Aumento_Impacto_%"] = 7.5
    if nivel == 4:
        bonos["Aumento_Impacto_%"] = 10.0
    if nivel == 5:
        bonos["Aumento_Impacto_%"] = 12.5
    if nivel >= 6:
        bonos["Aumento_Impacto_%"] = 15.0 
    return bonos

def potencial_grace(nivel):
    bonos = {}
    if nivel == 2:
        bonos[KEYS["Elemental_Dmg"]] = 10.0
    if nivel == 3:
        bonos[KEYS["Elemental_Dmg"]] = 15.0
    if nivel == 4:
        bonos[KEYS["Elemental_Dmg"]] = 20.0
    if nivel == 5:
        bonos[KEYS["Elemental_Dmg"]] = 25.0
    if nivel >= 6:
        bonos[KEYS["Elemental_Dmg"]] = 30.0 
    return bonos

def potencial_harumasa(nivel):
    bonos = {}
    if nivel == 2:
        bonos[KEYS["ATK_PCT"]] = 4.0
        bonos[KEYS["Reselectro"]] = 5.0
    if nivel == 3:
        bonos[KEYS["ATK_PCT"]] = 6.0
        bonos[KEYS["Reselectro"]] = 7.5
    if nivel == 4:
        bonos[KEYS["ATK_PCT"]] = 8.0
        bonos[KEYS["Reselectro"]] = 10.0
    if nivel == 5:
        bonos[KEYS["ATK_PCT"]] = 10.0
        bonos[KEYS["Reselectro"]] = 12.5
    if nivel >= 6:
        bonos[KEYS["ATK_PCT"]] = 12.0
        bonos[KEYS["Reselectro"]] = 15.0
    return bonos

def potencial_burnice(nivel):
    bonos = {}
    
    if nivel == 2:
        bonos["Ratio_Maestría_por_ER"] = 1.0
        bonos["Ratio_DMG_por_ER"] = 1.0
    elif nivel == 3:
        bonos["Ratio_Maestría_por_ER"] = 1.3
        bonos["Ratio_DMG_por_ER"] = 1.25
    elif nivel == 4:
        bonos["Ratio_Maestría_por_ER"] = 1.6
        bonos["Ratio_DMG_por_ER"] = 1.5
    elif nivel == 5:
        bonos["Ratio_Maestría_por_ER"] = 2.0
        bonos["Ratio_DMG_por_ER"] = 1.75
    elif nivel >= 6:
        bonos["Ratio_Maestría_por_ER"] = 2.5
        bonos["Ratio_DMG_por_ER"] = 2.0
        
    if nivel >= 2:
        bonos["Tope_Maestría"] = 25.0
        bonos["Tope_DMG"] = 20.0
        
    return bonos

def potencial_soldier_11(nivel):
    bonos = {}
    if nivel == 2:
        bonos[KEYS["CRIT_DMG"]] = 16.0
    if nivel == 3:
        bonos[KEYS["CRIT_DMG"]] = 24.0
    if nivel == 4:
        bonos[KEYS["CRIT_DMG"]] = 32.0
    if nivel == 5:
        bonos[KEYS["CRIT_DMG"]] = 40.0
    if nivel >= 6:
        bonos[KEYS["CRIT_DMG"]] = 48.0 
    return bonos

MAPA_POTENCIAL = {
    "Soldier 0 - Anby": potencial_soldier_0_anby,
    "Ellen": potencial_ellen,
    "Lycaon": potencial_lycaon,
    "Grace": potencial_grace,
    "Harumasa": potencial_harumasa,
    "Burnice": potencial_burnice,
    "Soldier 11": potencial_soldier_11,
}

CONFIG_POTENCIAL = {
    "Soldier 0 - Anby": True,
    "Ellen": True,
    "Lycaon": True,
    "Grace": True,
    "Harumasa": True,
    "Burnice": True,
    "Soldier 11": True,
}