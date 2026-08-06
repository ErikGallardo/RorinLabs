KEYS = {
    "ATK_PCT": "Ataque",
    "DMG_BONUS": "Daño_Adicional",
    "CRIT_DMG": "Daño_crítico",
    "ENERGY_REGEN": "Recuperación_energía",
    "CRIT_RATE": "Probabilidad_crítico",
    "DAZE": "Aturdimiento",
    "DEF_SHRED": "Reduccion_DEF_enemigo",
    "DISORDER_MULT": "Disorder_Extra_Mult",
    "PEN_RATIO": "Tasa_de_Perforación",
    "ANOMALY_MASTERY": "Tasa_de_Anomalía",
    "ANOMALY_PROF": "Maestría_Anomalía",   
    "PEN_RES_FISICO": "Pen_Res_Fisico",   
    "PEN_RES_ELECTRICO": "Pen_Res_Electrico",
    "PEN_RES_FUEGO": "Pen_Res_Fuego",
    "PEN_RES_HIELO": "Pen_Res_Hielo",
    "PEN_RES_ETEREO": "Pen_Res_Etereo",
    "PEN_RES_VIENTO": "Pen_Res_Viento",
    "MV_ADD": "Multiplicador_de_ataques",
    "ANOM_RES_RED": "Reducción_Resistencia_Anomalía",
    "Ignorar_Defensa": "Ignorar_Defensa",
}

def efecto_alice(mindscape, stacks=0, condicion_activa=False, **kwargs):
    """
    Alice:
    M1: Reduce DEF objetivo 20% (30s).
    M2: +15% Assault DMG (Sumado a DMG Global) y +15% Disorder DMG.
    M4: Ignora 10% Physical RES.
    M6: (Nota: Es un ataque extra de 3300% AP. No es un stat pasivo, no se suma aquí).
    """
    bonos = {}

    if mindscape >= 1:
        bonos[KEYS["DEF_SHRED"]] = 20.0
    if mindscape >= 2:
        bonos[KEYS["DMG_BONUS"]] = 15.0 
        bonos[KEYS["DISORDER_MULT"]] = 15.0
    if mindscape >= 4:
        bonos[KEYS["PEN_RES_FISICO"]] = 10.0

    return bonos

def efecto_anby(mindscape, stacks=0, condicion_activa=False, **kwargs):
    """
    M1: +12% Energy Regen.
    M2: +30% DMG contra aturdidos (Condicional).
    M6: +45% DMG al consumir carga (Stacks > 0).
    """
    bonos = {}
    
    if mindscape >= 1:
        bonos[KEYS["ENERGY_REGEN"]] = 12.0
    if mindscape >= 2:
        bonos[KEYS["DMG_BONUS"]] = 30.0
    if mindscape >= 6 and stacks > 0:
        bonos[KEYS["DMG_BONUS"]] = bonos.get(KEYS["DMG_BONUS"], 0) + 45.0

    return bonos

def efecto_anton(mindscape, stacks=0, condicion_activa=False, **kwargs):
    """
    M4: +10% Crit Rate (Condicional: Postura Defensiva).
    M6: +4% DMG por stack (Max 6) con Martillo.
    """
    bonos = {}

    if mindscape >= 4:
        bonos[KEYS["CRIT_RATE"]] = 10.0
    if mindscape >= 6 and stacks > 0:
        bonos[KEYS["DMG_BONUS"]] = stacks * 4.0

    return bonos

def efecto_astra_yao(mindscape, stacks=0, condicion_activa=False, **kwargs):
    """
    Astra Yao:
    M1: Reduce All-Type RES del enemigo 6% por stack (Max 3 -> 18%).
        - Afecta al DPS porque aplicamos PEN_RES a todos los elementos.
    M4: Buff al Quick Assist según el Rol del personaje que entra (DPS).
        - Ataque: +300% ATK (MV Add).
        - Anomalía: +50% Buildup.
        - Aturdimiento: +50% Daze.
        (Si la condición está activa, aplicamos los buffs ofensivos relevantes para el cálculo).
    M6: Buffs propios de Astra (Self-DMG).
    """
    bonos = {}

    if mindscape >= 1 and stacks > 0:
        stacks_reales = min(stacks, 3)
        valor_res_down = stacks_reales * 6.0
        
        bonos[KEYS["PEN_RES_FISICO"]] = valor_res_down
        bonos[KEYS["PEN_RES_ELECTRICO"]] = valor_res_down
        bonos[KEYS["PEN_RES_FUEGO"]] = valor_res_down
        bonos[KEYS["PEN_RES_HIELO"]] = valor_res_down
        bonos[KEYS["PEN_RES_ETEREO"]] = valor_res_down

    if mindscape >= 4 and condicion_activa:
        bonos[KEYS["MV_ADD"]] = 300.0 
        bonos[KEYS["ANOMALY_MASTERY"]] = 50.0 
        bonos[KEYS["DAZE"]] = 50.0

    if mindscape >= 6 and condicion_activa:
        bonos[KEYS["CRIT_RATE"]] = 80.0

    return bonos

def efecto_soldier_0_anby(mindscape, stacks=0, condicion_activa=False, **kwargs):
    """
    Soldier 0 - Anby:
    M1: (Mecánica) Gatilla 3 veces White Thunder en EX. (No es stat).
    M2: +12% Crit Rate (Permanente).
    M4: Ignora 12% Resistencia Eléctrica (Condición: Silver Star).
    M6: (Nuke) Vortex de 1000% ATK..
    """
    bonos = {}
    
    if mindscape >= 2:
        bonos[KEYS["CRIT_RATE"]] = 12.0
    if mindscape >= 4:
        bonos[KEYS["PEN_RES_ELECTRICO"]] = 12.0
    if mindscape >= 6:
        bonos[KEYS["MV_ADD"]] = 1000.0

    return bonos

def efecto_banyue(mindscape, stacks=0, condicion_activa=False, **kwargs):
    """
    Banyue:
    M1: -10% Fire RES (Debuff Tremor) y +10% DMG vs Tremor.
    M2: +15% Crit DMG y +15% Fire DMG (Pasivos permanentes).
    M4: +30% DMG a ataques principales (Skill/Basic fuertes).
    M6: +8% Fire DMG extra (Vidyaraja) y Nuke de 600% MV en Crushing Peaks.
    """
    bonos = {}
    
    if mindscape >= 2:
        bonos[KEYS["CRIT_DMG"]] = 15.0
        bonos[KEYS["DMG_BONUS"]] = 15.0


    if mindscape >= 1:
            bonos[KEYS["PEN_RES_FUEGO"]] = 10.0
            bonos[KEYS["DMG_BONUS"]] = bonos.get(KEYS["DMG_BONUS"], 0) + 10.0
        
    if mindscape >= 4:
            bonos[KEYS["DMG_BONUS"]] = bonos.get(KEYS["DMG_BONUS"], 0) + 30.0

    if mindscape >= 6:
            bonos[KEYS["DMG_BONUS"]] = bonos.get(KEYS["DMG_BONUS"], 0) + 8.0
            bonos[KEYS["MV_ADD"]] = 600.0

    return bonos

def efecto_ben(mindscape, stacks=0, condicion_activa=False, **kwargs):
    """
    Ben:
    M1: Reducción de daño recibido (Ignorado, defensivo).
    M2: Counter inflige 300% de la DEF extra. 
        (Sumamos 300 al MV. Asume que el usuario calcula daño basado en DEF).
    M4: +30% DMG en el counter tras bloquear.
    M6: +20% Daze (Aturdimiento) tras usar EX.
    """
    bonos = {}
    

    if mindscape >= 2:
            bonos[KEYS["MV_ADD"]] = 300.0
            
    if mindscape >= 4:
            bonos[KEYS["DMG_BONUS"]] = 30.0

    if mindscape >= 6:
            bonos[KEYS["DAZE"]] = 20.0

    return bonos

def efecto_billy(mindscape, stacks=0, condicion_activa=False, **kwargs):
    """
    Billy:
    M1: Energía plana (Ignorado).
    M2: +25% DMG en Dodge Counter.
    M4: +32% Crit Rate en EX Special (Distancia corta).
    M6: +6% DMG por stack (Max 5) al acumular hits/esquivas.
    """
    bonos = {}


    if mindscape >= 2:
            bonos[KEYS["DMG_BONUS"]] = 25.0
    
    if mindscape >= 4:
            bonos[KEYS["CRIT_RATE"]] = 32.0

    if mindscape >= 6 and stacks > 0:
        bonos[KEYS["DMG_BONUS"]] = bonos.get(KEYS["DMG_BONUS"], 0) + (stacks * 6.0)

    return bonos

def efecto_burnice(mindscape, stacks=0, condicion_activa=False, **kwargs):
    """
    Burnice:
    M1: +100% MV (Motion Value) al Afterburn y +25% Buildup. (Condicional: Calculando Afterburn).
    M2: +4% PEN Ratio por stack (Thermal Penetration). Max 5 stacks -> 20%.
    M4: +30% Crit Rate en EX Special o Assist. (Condicional).
    M6: Ignora 25% Fire RES y añade 60% MV (Special Afterburn) durante EX. (Condicional).
    """
    bonos = {}
    cond = str(condicion_activa).lower() if condicion_activa else ""
    todo = cond in ("true", "todo activo")
    afterburn = todo or "afterburn" in cond
    ex_assist = todo or "ex" in cond

    if mindscape >= 2 and stacks > 0:
        stacks_reales = min(stacks, 5)
        bonos[KEYS["PEN_RATIO"]] = stacks_reales * 4.0

    if mindscape >= 1 and afterburn:
        bonos[KEYS["MV_ADD"]] = 100.0
        bonos[KEYS["ANOMALY_MASTERY"]] = 25.0

    if mindscape >= 4 and ex_assist:
        bonos[KEYS["CRIT_RATE"]] = 30.0

    if mindscape >= 6 and ex_assist:
        bonos[KEYS["PEN_RES_FUEGO"]] = 25.0
        bonos[KEYS["MV_ADD"]] = bonos.get(KEYS["MV_ADD"], 0) + 60.0

    return bonos

def efecto_caesar(mindscape, stacks=0, condicion_activa=False, **kwargs):
    """
    Caesar:
    M1: Enemies near shield get -15% Attribute DMG RES (All types).
        - Afecta al DPS reduciendo resistencias elementales.
    M2: +10% Energy Regen (Self).
        - (El bono de ATK de M2 depende del Impacto, no se calcula aquí para evitar errores).
    M4: Mecánica de Assist Points (Ignorado).
    M6: Tras usar EX/Assist -> +30% Crit Rate y +60% Crit DMG (15s).
        - También +50% DMG a la skill específica (se puede sumar a DMG Bonus si se asume burst).
    """
    bonos = {}

    if mindscape >= 1 and condicion_activa:
        val_res = 15.0
        bonos[KEYS["PEN_RES_FISICO"]] = val_res
        bonos[KEYS["PEN_RES_FUEGO"]] = val_res
        bonos[KEYS["PEN_RES_ELECTRICO"]] = val_res
        bonos[KEYS["PEN_RES_HIELO"]] = val_res
        bonos[KEYS["PEN_RES_ETEREO"]] = val_res

    if mindscape >= 2 and condicion_activa:
        bonos[KEYS["ENERGY_REGEN"]] = 10.0

    if mindscape >= 6 and condicion_activa:
        bonos[KEYS["CRIT_RATE"]] = 30.0
        bonos[KEYS["CRIT_DMG"]] = 60.0

    return bonos

def efecto_corin(mindscape, stacks=0, condicion_activa=False, **kwargs):
    """
    Corin:
    M1: +12% DMG contra el objetivo tras Chain/Ulti.
    M2: Reduce Physical RES 0.5% por stack (Max 20 stacks -> 10%).
    M4: Energía (Ignorado).
    M6: Consumir cargas añade 3% ATK como daño por carga (Max 40 stacks -> 120% MV).
    """
    bonos = {}

    if mindscape >= 1:
        bonos[KEYS["DMG_BONUS"]] = 12.0
    if mindscape >= 2 and stacks > 0:
        stacks_res = min(stacks, 20)
        bonos[KEYS["PEN_RES_FISICO"]] = stacks_res * 0.5
    if mindscape >= 6 and stacks > 0:
        bonos[KEYS["MV_ADD"]] = stacks * 3.0

    return bonos

def efecto_dialyn(mindscape, stacks=0, condicion_activa=False, **kwargs):
    """
    Dialyn:
    M1: Ignore 15% All-Attribute RES (Condición: Overwhelmingly Positive).
    M2: +15% DMG a enemigos afectados (Condición: Malicious Complaint).
        (Nota: El bono de Stun DMG Multiplier de M2 se omite por no tener key directa expuesta, 
         pero el DMG Bonus aplica globalmente).
    M4: +500 ATK (Plano) (Condición: Overwhelmingly Positive).
    M6: Aftertone proc -> 480% ATK como Daño Físico adicional (Motion Value Add).
    """
    bonos = {}

    if condicion_activa:
        if mindscape >= 1:
            val_res = 15.0
            bonos[KEYS["PEN_RES_FISICO"]] = val_res
            bonos[KEYS["PEN_RES_FUEGO"]] = val_res
            bonos[KEYS["PEN_RES_ELECTRICO"]] = val_res
            bonos[KEYS["PEN_RES_HIELO"]] = val_res
            bonos[KEYS["PEN_RES_ETEREO"]] = val_res

        if mindscape >= 2:
            bonos[KEYS["DMG_BONUS"]] = bonos.get(KEYS["DMG_BONUS"], 0) + 15.0
        if mindscape >= 4:
            bonos[KEYS["ATK_PCT"]] = bonos.get(KEYS["ATK_PCT"], 0) + 500.0
        if mindscape >= 6:
            bonos[KEYS["MV_ADD"]] = 480.0

    return bonos

def efecto_ellen(mindscape, stacks=0, condicion_activa=False, **kwargs):
    """
    Ellen:
    M1: +2% Crit Rate por carga Flash Freeze (Max 6 stacks -> 12%).
    M2: Al usar EX, +20% Crit DMG por carga (Max 3 stacks -> 60%). (Requiere Condición).
    M6: +20% PEN Ratio y +250% DMG en el ataque cargado. (Requiere Condición).
    """
    bonos = {}

    if mindscape >= 1 and stacks > 0:
        stacks_reales = min(stacks, 6)
        bonos[KEYS["CRIT_RATE"]] = stacks_reales * 2.0


    if mindscape >= 2 and stacks > 0:
            stacks_ex = min(stacks, 3)
            bonos[KEYS["CRIT_DMG"]] = stacks_ex * 20.0

    if mindscape >= 6:
            bonos[KEYS["PEN_RATIO"]] = 20.0
            bonos[KEYS["DMG_BONUS"]] = bonos.get(KEYS["DMG_BONUS"], 0) + 250.0

    return bonos

def efecto_evelyn(mindscape, stacks=0, condicion_activa=False, **kwargs):
    """
    Evelyn:
    M1: Ignora 12% DEF (PEN Ratio) vs enemigos Bound. (Condicional).
    M2: +15% ATK (Pasivo permanente).
    M4: +40% Crit DMG mientras tenga Escudo. (Condicional).
    M6: Follow-up attack de 375% ATK (MV Add). (Condicional).
    """
    bonos = {}

    if mindscape >= 2:
        bonos[KEYS["ATK_PCT"]] = 15.0

    if mindscape >= 1:
            bonos[KEYS["PEN_RATIO"]] = 12.0
    if mindscape >= 4:
            bonos[KEYS["CRIT_DMG"]] = 40.0
    if mindscape >= 6:
            bonos[KEYS["MV_ADD"]] = 375.0

    return bonos

def efecto_grace(mindscape, stacks=0, condicion_activa=False, **kwargs):
    """
    Grace:
    M1: Energía para el equipo (Utilidad, ignorado en daño directo).
    M2: -8.5% Electric RES y -8.5% Anomaly Buildup RES. (Debuff).
    M4: +20% Energy Gen al consumir carga. (Self Buff).
    M6: Extra grenade y daño aumentado a 200%. 
        - Simulamos la granada extra sumando 200% al Motion Value (MV_ADD).
    """
    bonos = {}

    if mindscape >= 2:
        bonos[KEYS["PEN_RES_ELECTRICO"]] = 8.5
        bonos[KEYS["ANOM_RES_RED"]] = 8.5
    if mindscape >= 4:
        bonos[KEYS["ENERGY_REGEN"]] = 20.0
    if mindscape >= 6:
        bonos[KEYS["MV_ADD"]] = 200.0

    return bonos

def efecto_harumasa(mindscape, stacks=0, condicion_activa=False, **kwargs):
    """
    Harumasa:
    M1: Mecánica de doble flecha (No es stat, es hit count. Se ignora aquí).
    M2: +50% DMG al Dash Attack (Mientras tenga stacks de Electro Blitz).
    M4: Utilidad (Duración/Decibelios).
    M6:
       - Ignora 15% Electric RES (Si enemigo Stunned/Anomaly).
       - Nuke de 1500% ATK (Explosión electromagnética).
    """
    bonos = {}


    if mindscape >= 2:
            bonos[KEYS["DMG_BONUS"]] = 50.0
    if mindscape >= 6:
            bonos[KEYS["PEN_RES_ELECTRICO"]] = 15.0
            bonos[KEYS["MV_ADD"]] = 1500.0

    return bonos

def efecto_hugo(mindscape, stacks=0, condicion_activa=False, **kwargs):
    """
    Hugo:
    M1: +12% CR y +30% CD durante efecto 'Totalize'.
    M2: Ignora 15% DEF (PEN Ratio) durante 'Totalize'.
    M4: Ignora 12% Ice RES tras Charged Shot.
    M6: +60% DMG a 'Totalize' y +1000% MV en EX Finisher.
    """
    bonos = {}


    if mindscape >= 1:
            bonos[KEYS["CRIT_RATE"]] = 12.0
            bonos[KEYS["CRIT_DMG"]] = 30.0
    if mindscape >= 2:
            bonos[KEYS["PEN_RATIO"]] = 15.0
    if mindscape >= 4:
            bonos[KEYS["PEN_RES_HIELO"]] = 12.0
    if mindscape >= 6:
            bonos[KEYS["DMG_BONUS"]] = bonos.get(KEYS["DMG_BONUS"], 0) + 60.0
            bonos[KEYS["MV_ADD"]] = 1000.0

    return bonos

def efecto_jane(mindscape, stacks=0, condicion_activa=False, **kwargs):
    """
    Jane:
    M1: +15% Phys Anomaly Buildup y +30% DMG (Max @ 300 AP).
        (Asumimos que la Jane del usuario tiene >300 AP para el bono de daño).
    M2: Ignora 15% DEF y +50% Crit DMG (Para Assault).
    M4: +18% Anomaly DMG (Team Buff).
    M6: +20% Crit Rate y +40% Crit DMG (State: Passion).
    """
    bonos = {}

    if mindscape >= 4:
        bonos[KEYS["DMG_BONUS"]] = 18.0


    if mindscape >= 1:
            bonos[KEYS["ANOMALY_MASTERY"]] = 15.0
            bonos[KEYS["DMG_BONUS"]] = bonos.get(KEYS["DMG_BONUS"], 0) + 30.0
    if mindscape >= 2:
            bonos[KEYS["Ignorar_Defensa"]] = 15.0
            bonos[KEYS["CRIT_DMG"]] = bonos.get(KEYS["CRIT_DMG"], 0) + 50.0
    if mindscape >= 6:
            bonos[KEYS["CRIT_RATE"]] = 20.0
            bonos[KEYS["CRIT_DMG"]] = bonos.get(KEYS["CRIT_DMG"], 0) + 40.0

    return bonos

def efecto_ju_fufu(mindscape, stacks=0, condicion_activa=False, **kwargs):
    """
    Ju Fufu:
    M1: +12% Crit Rate (Al entrar en combate).
        (Nota: El Stun DMG Multiplier +35% se omite por falta de key específica).
    M2: +22% Crit DMG en estado 'Tiger's Roar'.
    M4: +35% Crit DMG en estado 'Tiger's Roar'.
    M6: +30% Chain DMG (Se suma a DMG Bonus si cond_activa) y Nuke de 480% (160%*3).
    """
    bonos = {}

    if mindscape >= 1:
        bonos[KEYS["CRIT_RATE"]] = 12.0
        bonos["Stun_DMG_Multiplier"] = 35.0

    if condicion_activa:
        crit_dmg_extra = 0.0
        if mindscape >= 2: crit_dmg_extra += 22.0
        if mindscape >= 4: crit_dmg_extra += 35.0
        
        if crit_dmg_extra > 0:
            bonos[KEYS["CRIT_DMG"]] = crit_dmg_extra
        if mindscape >= 6:
            bonos[KEYS["MV_ADD"]] = 480.0
            bonos[KEYS["DMG_BONUS"]] = 30.0

    return bonos

def efecto_koleda(mindscape, stacks=0, condicion_activa=False, **kwargs):
    """
    Koleda:
    M1: +15% Daze (Aturdimiento) en EX/Special tras combo. (Condicional).
    M2: Energía plana (Ignorado).
    M4: +18% DMG por carga en Chain/Ulti (Max 2 stacks -> 36%).
    M6: Explosión adicional de 360% ATK en EX/Chain/Ulti.
    """
    bonos = {}

    if condicion_activa:
        if mindscape >= 1:
            bonos[KEYS["DAZE"]] = 15.0
        if mindscape >= 4 and stacks > 0:
            stacks_reales = min(stacks, 2)
            bonos[KEYS["DMG_BONUS"]] = stacks_reales * 18.0
        if mindscape >= 6:
            bonos[KEYS["MV_ADD"]] = 360.0

    return bonos

def efecto_lighter(mindscape, stacks=0, condicion_activa=False, **kwargs):
    """
    Lighter:
    M1: -10% Fire/Ice RES (Debuff Collapse) y +30% DMG al Finishing Move.
    M2: +25% Stun DMG Multiplier (Debuff Collapse).
    M4: +10% Energy Regen (Team Buff/Passive).
    M6: Nuke 'Blazing Impact' de 250% ATK (MV Add).
    """
    bonos = {}
    cond = str(condicion_activa).lower() if condicion_activa else ""
    todo = cond in ("true", "todo activo")
    collapse = todo or "collapse" in cond
    finishing = todo or "finishing" in cond
    nuke = todo or "nuke" in cond

    if mindscape >= 4:
        bonos[KEYS["ENERGY_REGEN"]] = 10.0

    if mindscape >= 1 and collapse:
        bonos[KEYS["PEN_RES_FUEGO"]] = 10.0
        bonos[KEYS["PEN_RES_HIELO"]] = 10.0
    if mindscape >= 1 and finishing:
        bonos[KEYS["DMG_BONUS"]] = 30.0
    if mindscape >= 2 and collapse:
        bonos["Stun_DMG_Multiplier"] = 25.0
    if mindscape >= 6 and nuke:
        bonos[KEYS["MV_ADD"]] = 250.0

    return bonos

def efecto_lucia(mindscape, stacks=0, condicion_activa=False, **kwargs):
    """
    Lucia:
    M1: Ignora 18% All-Attribute RES (Team Buff).
    M2: +15% Sheer DMG para aliados en estado Darkbreaker (Team Buff).
    M4: 100 Decibels (Ignorado, utilidad).
    M6: ATK + 2% HP (No calculado dinámicamente aquí).
        Harmony Skill: Always Crit (+100% CR) y +30% Crit DMG.
    """
    bonos = {}

    if condicion_activa:
        if mindscape >= 1:
            val_res = 18.0
            bonos[KEYS["PEN_RES_FISICO"]] = val_res
            bonos[KEYS["PEN_RES_FUEGO"]] = val_res
            bonos[KEYS["PEN_RES_ELECTRICO"]] = val_res
            bonos[KEYS["PEN_RES_HIELO"]] = val_res
            bonos[KEYS["PEN_RES_ETEREO"]] = val_res
        if mindscape >= 2:
            bonos[KEYS["DMG_BONUS"]] = bonos.get(KEYS["DMG_BONUS"], 0) + 15.0
        if mindscape >= 6:
            bonos[KEYS["CRIT_DMG"]] = 30.0
            bonos[KEYS["CRIT_RATE"]] = 100.0

    return bonos

def efecto_lucy(mindscape, stacks=0, condicion_activa=False, **kwargs):
    """
    Lucy:
    M1: Energía (Utilidad, ignorado).
    M2: Activa el estado 'Cheer On!' (La base del buff de ATK suele ir en efectos_soportes, 
        aquí manejamos los extras de los Mindscapes).
    M4: +10% Crit DMG para aliados bajo 'Cheer On!'.
    M6: Nuke del Jabalí (300% ATK) al golpear con EX.
    """
    bonos = {}

    if condicion_activa:
        if mindscape >= 4:
            bonos[KEYS["CRIT_DMG"]] = 10.0
        if mindscape >= 6:
            bonos[KEYS["MV_ADD"]] = 300.0

    return bonos

def efecto_lycaon(mindscape, stacks=0, condicion_activa=False, **kwargs):
    """
    Lycaon:
    M1: +12% Daze en EX. Si es cargado, +10% extra (Total 22%). (Condicional).
    M2: Energía plana (Ignorado).
    M4: Escudo (Defensivo, ignorado).
    M6: Enemigo recibe +10% DMG por stack (Max 5 -> 50%). (Condicional).
    """
    bonos = {}

    if mindscape >= 6 and stacks > 0:
        stacks_reales = min(stacks, 5)
        bonos[KEYS["DMG_BONUS"]] = stacks_reales * 10.0

    if condicion_activa:
        if mindscape >= 1:
            bonos[KEYS["DAZE"]] = 22.0

    return bonos

def efecto_manato(mindscape, stacks=0, condicion_activa=False, **kwargs):
    """
    Manato:
    M1: +20% Fire DMG (Basic/Assist) basado en HP perdido. 
        (Asumimos acumulación máxima si la condición está activa).
    M2: Ignora 8% Fire RES (Estado Molten Edge).
    M4: +8% Max HP (Pasivo defensivo, ignorado en DPS).
    M6: +3% Fire DMG por stack de Remnant Flame (Max 5 -> 15%).
    """
    bonos = {}


    if mindscape >= 1:
            bonos[KEYS["DMG_BONUS"]] = 20.0
    if mindscape >= 2:
            bonos[KEYS["PEN_RES_FUEGO"]] = 8.0
    if mindscape >= 6 and stacks > 0:
        stacks_reales = min(stacks, 5)
        bonos[KEYS["DMG_BONUS"]] = bonos.get(KEYS["DMG_BONUS"], 0) + (stacks_reales * 3.0)

    return bonos

def efecto_miyabi(mindscape, stacks=0, condicion_activa=False, **kwargs):
    """
    Miyabi:
    M1: Ignora 6% DEF por punto de Fallen Frost (Max 6 -> 36%).
        +20% Anomaly Buildup (Team Buff al romper Frostburn).
    M2: +15% Crit Rate (Pasivo). 
        +30% DMG a Kazahana/Dodge (Condicional).
    M4: +30% Frostburn Break DMG (Condicional).
    M6: +30% Shimotsuki DMG (Condicional).
    """
    bonos = {}
    cond = str(condicion_activa).lower() if condicion_activa else ""
    todo = cond in ("true", "todo activo")
    kazahana = todo or "kazahana" in cond
    frostburn = todo or "frostburn" in cond
    shimotsuki = todo or "shimotsuki" in cond

    if mindscape >= 2:
        bonos[KEYS["CRIT_RATE"]] = 15.0

    if mindscape >= 1 and stacks > 0:
        stacks_reales = min(stacks, 6)
        bonos[KEYS["Ignorar_Defensa"]] = stacks_reales * 6.0

    if mindscape >= 1:
        bonos[KEYS["ANOMALY_MASTERY"]] = 20.0

    dmg_extra = 0.0
    if mindscape >= 2 and kazahana: dmg_extra += 30.0
    if mindscape >= 4 and frostburn: dmg_extra += 30.0
    if mindscape >= 6 and shimotsuki: dmg_extra += 30.0
    if dmg_extra > 0:
        bonos[KEYS["DMG_BONUS"]] = bonos.get(KEYS["DMG_BONUS"], 0) + dmg_extra

    return bonos

def efecto_nekomata(mindscape, stacks=0, condicion_activa=False, **kwargs):
    """
    Nekomata:
    M1: Ignora 16% Phys RES (Condición: Back Attack / Stunned).
    M2: +25% Energy Regen (Condición: Single Target).
    M4: +7% Crit Rate por stack tras EX (Max 2 -> 14%). (Condición).
    M6: +18% Crit DMG tras Chain/Ult (Max 3 -> 54%). (Usa Slider Stacks).
    """
    bonos = {}

    if mindscape >= 6 and stacks > 0:
        stacks_reales = min(stacks, 3)
        bonos[KEYS["CRIT_DMG"]] = stacks_reales * 18.0


    if mindscape >= 1:
            bonos[KEYS["PEN_RES_FISICO"]] = 16.0

    if mindscape >= 2:
            bonos[KEYS["ENERGY_REGEN"]] = 25.0

    if mindscape >= 4:
            bonos[KEYS["CRIT_RATE"]] = 14.0

    return bonos

def efecto_nicole(mindscape, stacks=0, condicion_activa=False, **kwargs):
    """
    Nicole:
    M1: +16% DMG y +16% Anomaly Buildup rate en EX Special. (Condicional).
    M2: Energía (Ignorado).
    M4: Radio del campo (Ignorado).
    M6: +1.5% Crit Rate por golpe del campo (Team Buff). (Max 10 stacks -> 15%).
    """
    bonos = {}

    if mindscape >= 6 and stacks > 0:
        stacks_reales = min(stacks, 10)
        bonos[KEYS["CRIT_RATE"]] = stacks_reales * 1.5

    if condicion_activa:
        if mindscape >= 1:
            bonos[KEYS["DMG_BONUS"]] = 16.0
            bonos[KEYS["ANOMALY_MASTERY"]] = 16.0

    return bonos

def efecto_orphie_magus(mindscape, stacks=0, condicion_activa=False, **kwargs):
    """
    Orphie & Magus:
    M1: Ignora 15% Fire RES (Skills) y +20% DMG (Estado Zeroed In).
    M2: +20% ATK tras usar Ultimate (Buff 45s).
    M4: +40% DMG a EX Special y Ultimate.
    M6: Nuke de 250% ATK (Fire DMG) al golpear con láser EX/Ult.
    """
    bonos = {}


    if mindscape >= 1:
            bonos[KEYS["PEN_RES_FUEGO"]] = 15.0
            bonos[KEYS["DMG_BONUS"]] = 20.0
    if mindscape >= 2:
            bonos[KEYS["ATK_PCT"]] = 20.0
    if mindscape >= 4:
            bonos[KEYS["DMG_BONUS"]] = bonos.get(KEYS["DMG_BONUS"], 0) + 40.0
    if mindscape >= 6:
            bonos[KEYS["MV_ADD"]] = 250.0

    return bonos

def efecto_pan_yinhu(mindscape, stacks=0, condicion_activa=False, **kwargs):
    """
    Pan Yinhu:
    M1: +10% DMG recibido por enemigos con 'Depleted Qi'. (Team Buff).
    M6: Aumenta la Sheer Force en 180 planos (Adicional a la pasiva base).
    """
    bonos = {}

    if condicion_activa:
        if mindscape >= 1:
            bonos[KEYS["DMG_BONUS"]] = 10.0

    return bonos

def efecto_piper(mindscape, stacks=0, condicion_activa=False, **kwargs):
    """
    Piper:
    M1: Aumenta el límite de stacks de Power a 30 (vs 20 base).
    M2: Al hacer el remate (Downward Smash):
        +10% DMG Base.
        +1% DMG por stack de Power.
    M4: Energía (Ignorado).
    M6: Duración de buffs (Ignorado).
    """
    bonos = {}
    if mindscape >= 2:
        limite_stacks = 30 if mindscape >= 1 else 20
        stacks_reales = min(stacks, limite_stacks)
        bonos[KEYS["DMG_BONUS"]] = 10.0 + (stacks_reales * 1.0)

    return bonos

def efecto_pulchra(mindscape, stacks=0, condicion_activa=False, **kwargs):
    """
    Pulchra:
    M1: +10% Crit Rate vs Binding Trap (Condicional).
    M2: +10% ATK en Hunter's Gait (Condicional).
    M4: Energy Cost reduction (Ignorado).
    M6: +15% DMG a Rending Claw (Skill principal).
    """
    bonos = {}

    if condicion_activa:
        if mindscape >= 1:
            bonos[KEYS["CRIT_RATE"]] = 10.0
        if mindscape >= 2:
            bonos[KEYS["ATK_PCT"]] = 10.0
        if mindscape >= 6:
            bonos[KEYS["DMG_BONUS"]] = bonos.get(KEYS["DMG_BONUS"], 0) + 15.0

    return bonos

def efecto_qingyi(mindscape, stacks=0, condicion_activa=False, **kwargs):
    """
    Qingyi:
    M1: Reduce DEF 15% y +20% Crit Rate (Condición: Max Voltage Attack).
    M2: +15% Daze (Condición: Max Subjugation Stacks).
        (Nota: El aumento al Stun DMG Multiplier del Core se omite aquí 
         porque depende de la lógica interna de stacks del Core).
    M6: +100% Crit DMG (Basic Atk) y Ignora 20% All-Res (Debuff Universal).
    """
    bonos = {}

    if condicion_activa:
        if mindscape >= 1:
            bonos[KEYS["DEF_SHRED"]] = 15.0
            bonos[KEYS["CRIT_RATE"]] = 20.0
        if mindscape >= 2:
            bonos[KEYS["DAZE"]] = 15.0
        if mindscape >= 6:
            bonos[KEYS["CRIT_DMG"]] = bonos.get(KEYS["CRIT_DMG"], 0) + 100.0
            val_res = 20.0
            bonos[KEYS["PEN_RES_FISICO"]] = val_res
            bonos[KEYS["PEN_RES_FUEGO"]] = val_res
            bonos[KEYS["PEN_RES_ELECTRICO"]] = val_res
            bonos[KEYS["PEN_RES_HIELO"]] = val_res
            bonos[KEYS["PEN_RES_ETEREO"]] = val_res

    return bonos

def efecto_rina(mindscape, stacks=0, condicion_activa=False, **kwargs):
    """
    Rina:
    M1: Core Passive effect -> 130%. (Modificador de Core, no stat directo aquí).
    M2: +15% DMG al entrar en combate. (Condicional).
    M4: +0.5/s Energy Regen (Plano, ignorado).
    M6: +15% Electric DMG a todo el equipo. (Condicional).
    """
    bonos = {}

    if condicion_activa:
        if mindscape >= 2:
            bonos[KEYS["DMG_BONUS"]] = 15.0
        if mindscape >= 6:
            bonos[KEYS["DMG_BONUS"]] = bonos.get(KEYS["DMG_BONUS"], 0) + 15.0

    return bonos

def efecto_seed(mindscape, stacks=0, condicion_activa=False, **kwargs):
    """
    Seed:
    M1: +30% Crit DMG (Ataque Downfall).
    M2: Ignora 20% DEF (Estado Besiege).
        +5% DMG a 'Slaughter' por cada 5 de Energía consumida.
        (Max 120 Energía = 24 Stacks -> +120% DMG).
    M4: +20% Ult DMG (Estado Besiege).
    M6: +50% Crit DMG (Global).
        Nuke de 495% (165% * 3) en 'Slaughter'.
    """
    bonos = {}
    if mindscape >= 6:
        bonos[KEYS["CRIT_DMG"]] = 50.0

    if mindscape >= 1:
            bonos[KEYS["CRIT_DMG"]] = bonos.get(KEYS["CRIT_DMG"], 0) + 30.0
    if mindscape >= 2:
            bonos[KEYS["Ignorar_Defensa"]] = 20.0
            if stacks > 0:
                stacks_reales = min(stacks, 24)
                bonos[KEYS["DMG_BONUS"]] = stacks_reales * 5.0
    if mindscape >= 4:
            bonos[KEYS["DMG_BONUS"]] = bonos.get(KEYS["DMG_BONUS"], 0) + 20.0
    if mindscape >= 6:
            bonos[KEYS["MV_ADD"]] = 495.0

    return bonos

def efecto_seth(mindscape, stacks=0, condicion_activa=False, **kwargs):
    """
    Seth:
    M1: Mejoras de Escudo (Defensivo, ignorado).
    M2: +35% Anomaly Buildup en 'Lightning Strike - Electrified'. (Condicional).
    M4: +25% Daze en Defensive Assist. (Condicional).
    M6: Finisher 'Lightning Strike - Electrified':
        +500% MV (Nuke).
        Guaranteed Crit (Forzamos +100% CR).
        +60% Crit DMG.
    """
    bonos = {}

    if condicion_activa:
        if mindscape >= 2:
            bonos[KEYS["ANOMALY_MASTERY"]] = 35.0
        if mindscape >= 4:
            bonos[KEYS["DAZE"]] = 25.0
        if mindscape >= 6:
            bonos[KEYS["MV_ADD"]] = 500.0
            bonos[KEYS["CRIT_RATE"]] = 100.0
            bonos[KEYS["CRIT_DMG"]] = 60.0

    return bonos

def efecto_soldier_11(mindscape, stacks=0, condicion_activa=False, **kwargs):
    """
    Soldier 11:
    M1: Recuperación de energía (Ignorado).
    M2: +3% DMG por stack al activar Fire Suppression (Max 12 -> 36%).
    M4: Defensa/Anti-Interrupt (Ignorado).
    M6: Ignora 25% Fire RES si consume una carga de 'Charge' (Condicional).
    """
    bonos = {}

    if mindscape >= 2 and stacks > 0:
        stacks_reales = min(stacks, 12)
        bonos[KEYS["DMG_BONUS"]] = stacks_reales * 3.0

    if mindscape >= 6:
        bonos[KEYS["PEN_RES_FUEGO"]] = 25.0

    return bonos

def efecto_soukaku(mindscape, stacks=0, condicion_activa=False, **kwargs):
    """
    Soukaku:
    M1: Duración de buff (Ignorado).
    M2: Generación de Vortex/Energía (Ignorado).
    M4: -10% Ice RES al enemigo golpeado por Fly the Flag (Condicional).
    M6: +45% DMG a ataques reforzados en estado Frosted Banner (Condicional).
    """
    bonos = {}

    if condicion_activa:
        if mindscape >= 4:
            bonos[KEYS["PEN_RES_HIELO"]] = 10.0
        if mindscape >= 6:
            bonos[KEYS["DMG_BONUS"]] = 45.0

    return bonos

def efecto_trigger(mindscape, stacks=0, condicion_activa=False, **kwargs):
    """
    Trigger:
    M1: +20% Stun DMG Multiplier (Pasivo).
    M2: +6% Crit DMG por stack 'Hunter's Gaze' (Team Buff, Max 4 -> 24%).
    M4: Golpe extra de 200% ATK ('Disconnect'). (Condicional).
    M6: Nuke 'Armor Break Round':
        +1200% MV (Motion Value Add).
        +50% DMG Bonus para este golpe.
    """
    bonos = {}

    if mindscape >= 1:
        bonos["Stun_DMG_Multiplier"] = 20.0
    if mindscape >= 2 and stacks > 0:
        stacks_reales = min(stacks, 4)
        bonos[KEYS["CRIT_DMG"]] = stacks_reales * 6.0
    if condicion_activa:
        if mindscape >= 4:
            bonos[KEYS["MV_ADD"]] = bonos.get(KEYS["MV_ADD"], 0) + 200.0
        if mindscape >= 6:
            bonos[KEYS["MV_ADD"]] = bonos.get(KEYS["MV_ADD"], 0) + 1200.0
            bonos[KEYS["DMG_BONUS"]] = 50.0

    return bonos

def efecto_vivian(mindscape, stacks=0, condicion_activa=False, **kwargs):
    """
    Vivian:
    M1: +16% DMG recibido (Anomaly/Disorder) en enemigos bajo Prophecy.
    M2: +25% Anomaly Buildup y 15% Ignore All-RES.
        (Nota: El cambio de escalado de Proficiency al 130% altera la fórmula base,
         aquí aplicamos los stats directos).
    M4: +12% ATK y ataques específicos siempre son Críticos (+100% CR).
    M6: +40% Ether DMG (Pasivo).
        Consumo de Plumas (Guard Feathers) para multiplicar el daño de Abloom.
        Max 5 stacks = 5x Daño. Simulamos esto agregando +80% DMG por stack (Max +400%).
    """
    bonos = {}

    if mindscape >= 6:
        bonos[KEYS["DMG_BONUS"]] = 40.0

    if condicion_activa:
        if mindscape >= 1:
            bonos[KEYS["DMG_BONUS"]] = bonos.get(KEYS["DMG_BONUS"], 0) + 16.0
        if mindscape >= 2:
            bonos[KEYS["ANOMALY_MASTERY"]] = 25.0
            val_res = 15.0
            bonos[KEYS["PEN_RES_ETEREO"]] = val_res
            bonos[KEYS["PEN_RES_FISICO"]] = val_res
            bonos[KEYS["PEN_RES_FUEGO"]] = val_res
            bonos[KEYS["PEN_RES_ELECTRICO"]] = val_res
            bonos[KEYS["PEN_RES_HIELO"]] = val_res
        if mindscape >= 4:
            bonos[KEYS["ATK_PCT"]] = 12.0
            bonos[KEYS["CRIT_RATE"]] = 100.0

        if mindscape >= 6 and stacks > 0:
            stacks_reales = min(stacks, 5)
            bonos[KEYS["DMG_BONUS"]] = bonos.get(KEYS["DMG_BONUS"], 0) + (stacks_reales * 80.0)

    return bonos

def efecto_yanagi(mindscape, stacks=0, condicion_activa=False, **kwargs):
    """
    Yanagi:
    M1: +80 Anomaly Proficiency (Si tiene stacks de Clarity).
    M2: +20% Electric Anomaly Buildup (EX Thrust).
        (Nota: El aumento al multiplicador de Disorder se omite por ser lógica de reacción).
    M4: Ignora 16% DEF (PEN Ratio) en enemigos con 'Exposed'.
    M6: +20% EX Special DMG.
    """
    bonos = {}


    if mindscape >= 1:
            bonos["ANOMALY_PROF"] = 80.0
    if mindscape >= 2:
            bonos[KEYS["ANOMALY_MASTERY"]] = 20.0
    if mindscape >= 4:
            bonos[KEYS["PEN_RATIO"]] = 16.0
    if mindscape >= 6:
            bonos[KEYS["DMG_BONUS"]] = bonos.get(KEYS["DMG_BONUS"], 0) + 20.0

    return bonos

def efecto_ye_shunguang(mindscape, stacks=0, condicion_activa=False, **kwargs):
    """
    Ye Shunguang:
    M1: +10% DMG y Ignora 20% DEF (Bajo efecto Unity).
    M2: EX Special y Ultimate ignoran 40% DEF adicional.
        (En Burst, se suma a la M1 para un total de 60% PEN Ratio).
    M4: Aumenta topes de Vulnerabilidad (Mecánica compleja, ignorada en stats planos).
    M6: Nuke de 1500% ATK (Physical DMG) en EX/Ult.
    """
    bonos = {}


    if mindscape >= 1:
            bonos[KEYS["DMG_BONUS"]] = 10.0
            bonos[KEYS["Ignorar_Defensa"]] = 20.0
    if mindscape >= 2:
            bonos[KEYS["Ignorar_Defensa"]] = bonos.get(KEYS["Ignorar_Defensa"], 0) + 40.0
    if mindscape >= 6:
            bonos[KEYS["MV_ADD"]] = 1500.0

    return bonos

def efecto_yidhari(mindscape, stacks=0, condicion_activa=False, **kwargs):
    """
    Yidhari:
    M1: Basic/EX Attacks ignoran 20% Ice RES. (Condicional).
    M2: +40% Crit DMG (Permanente/Pasivo).
    M4: HP/Decibels (Ignorado).
    M6: +25% Sheer DMG (DMG Bonus) bajo estado Erudition. (Condicional).
    """
    bonos = {}

    if mindscape >= 2:
        bonos[KEYS["CRIT_DMG"]] = 40.0


    if mindscape >= 1:
            bonos[KEYS["PEN_RES_HIELO"]] = 20.0
    if mindscape >= 6:
            bonos[KEYS["DMG_BONUS"]] = bonos.get(KEYS["DMG_BONUS"], 0) + 25.0

    return bonos

def efecto_yixuan(mindscape, stacks=0, condicion_activa=False, **kwargs):
    """
    Yixuan:
    M1: +10% Crit Rate (Pasivo en combate).
    M2: Ignora 15% Ether RES (EX/Ult).
        Nuke de 1200% Sheer Force (Simulado como MV Add).
    M4: +30% EX DMG por stack de Tranquillity (Max 2 -> 60%).
    M6: +20% Sheer DMG en estado Meditation.
    """
    bonos = {}

    if mindscape >= 1:
        bonos[KEYS["CRIT_RATE"]] = 10.0


    if mindscape >= 2:
            bonos[KEYS["PEN_RES_ETEREO"]] = 15.0
            bonos[KEYS["MV_ADD"]] = 1200.0
    if mindscape >= 4 and stacks > 0:
            stacks_reales = min(stacks, 2)
            bonos[KEYS["DMG_BONUS"]] = stacks_reales * 30.0
    if mindscape >= 6:
            bonos[KEYS["DMG_BONUS"]] = bonos.get(KEYS["DMG_BONUS"], 0) + 20.0

    return bonos

def efecto_yuzuha(mindscape, stacks=0, condicion_activa=False, **kwargs):
    """
    Yuzuha:
    M1: -10% All-Attribute RES (Enemigos en Sweet Scare).
    M2: +15% Team DMG y +15% Anomaly Buildup (Buff 40s).
    M4: +30% DMG y +20% Anomaly Buildup (Assist Follow-Up).
    M6: Nuke de 300% ATK (Por shell consumido).
        +105% Disorder Multiplier por stack (Max 3 -> +315%).
    """
    bonos = {}

    if mindscape >= 6 and stacks > 0:
        stacks_reales = min(stacks, 3)
        bonos["DISORDER_MULT"] = stacks_reales * 105.0

    if condicion_activa:
        if mindscape >= 1:
            val_res = 10.0
            bonos[KEYS["PEN_RES_FISICO"]] = val_res
            bonos[KEYS["PEN_RES_FUEGO"]] = val_res
            bonos[KEYS["PEN_RES_ELECTRICO"]] = val_res
            bonos[KEYS["PEN_RES_HIELO"]] = val_res
            bonos[KEYS["PEN_RES_ETEREO"]] = val_res
            bonos[KEYS["ANOM_RES_RED"]] = 10.0
        if mindscape >= 2:
            bonos[KEYS["DMG_BONUS"]] = bonos.get(KEYS["DMG_BONUS"], 0) + 15.0
            bonos[KEYS["ANOMALY_MASTERY"]] = bonos.get(KEYS["ANOMALY_MASTERY"], 0) + 15.0
        if mindscape >= 4:
            bonos[KEYS["DMG_BONUS"]] = bonos.get(KEYS["DMG_BONUS"], 0) + 30.0
            bonos[KEYS["ANOMALY_MASTERY"]] = bonos.get(KEYS["ANOMALY_MASTERY"], 0) + 20.0
        if mindscape >= 6:
            bonos[KEYS["MV_ADD"]] = 300.0

    return bonos

def efecto_zhao(mindscape, stacks=0, condicion_activa=False, **kwargs):
    """
    Zhao:
    M1: Ignora 15% All-Attribute RES (Team Buff tras Switch out).
    M2: +20% ATK (Self) tras curarse. (El equipo recibe 15%).
    M4: +40% Crit DMG (Ultimate / Final Verdict).
    M6: Core Passive Crit Rate * 1.25 (Ignorado, base variable).
        Final Verdict Charge DMG -> 140% (Simulamos como +40% DMG Bonus extra).
    """
    bonos = {}

    if condicion_activa:
        if mindscape >= 1:
            val_res = 15.0
            bonos[KEYS["PEN_RES_FISICO"]] = val_res
            bonos[KEYS["PEN_RES_FUEGO"]] = val_res
            bonos[KEYS["PEN_RES_ELECTRICO"]] = val_res
            bonos[KEYS["PEN_RES_HIELO"]] = val_res
            bonos[KEYS["PEN_RES_ETEREO"]] = val_res

        if mindscape >= 2:
            bonos[KEYS["ATK_PCT"]] = 20.0
        if mindscape >= 4:
            bonos[KEYS["CRIT_DMG"]] = 40.0
        if mindscape >= 6:
            bonos[KEYS["DMG_BONUS"]] = bonos.get(KEYS["DMG_BONUS"], 0) + 40.0

    return bonos

def efecto_zhu_yuan(mindscape, stacks=0, condicion_activa=False, **kwargs):
    """
    Zhu Yuan:
    M1: Recarga de munición (Mecánica, ignorada en stats).
    M2: +10% Ether DMG recibido por el enemigo por stack (Max 5 -> 50%).
        (Aplica a Basic/Dash, lo sumamos como DMG Bonus).
    M4: Ignora 25% Ether RES (Basic/Dash).
    M6: Nuke adicional en EX Special (Ether Buckshot):
        4 balas * 220% ATK = 880% MV Add.
    """
    bonos = {}


    if mindscape >= 2 and stacks > 0:
            stacks_reales = min(stacks, 5)
            bonos[KEYS["DMG_BONUS"]] = stacks_reales * 10.0
    if mindscape >= 4:
            bonos[KEYS["PEN_RES_ETEREO"]] = 25.0
    if mindscape >= 6:
            bonos[KEYS["MV_ADD"]] = 880.0

    return bonos

def efecto_sunna(mindscape, stacks=0, condicion_activa=False, stats_actuales=None, **kwargs):
    """
    Sunna:
    M1: Reduce la DEF del enemigo en 7% por stack (Max 3 -> 21%).
    M2: +10% ATK (Ether Veil). Aumenta multiplicadores de Cat's Gaze (+200% Atacante / +300% Anomalía).
    M4: +18% DMG para el equipo tras usar Ultimate (60s).
    M6: En estado Focused Creation! (Usar EX):
        +100% Crit Rate (Crítico garantizado).
        +Crit DMG igual al 0.03% del ATK inicial (ATK * 0.03), máximo 105%.
        +50% DMG extra a las detonaciones de Cat's Gaze.
    """
    bonos = {}

    if mindscape >= 1 and stacks > 0:
        stacks_reales = min(stacks, 3)
        bonos[KEYS["DEF_SHRED"]] = stacks_reales * 7.0

    if condicion_activa:
        if mindscape >= 2:
            bonos[KEYS["ATK_PCT"]] = 10.0
            bonos["Sunna_Cat_Gaze_Extra_Atacante"] = 200.0
            bonos["Sunna_Cat_Gaze_Extra_Anomalia"] = 300.0

        if mindscape >= 4:
            bonos[KEYS["DMG_BONUS"]] = bonos.get(KEYS["DMG_BONUS"], 0) + 18.0

        if mindscape >= 6:
            bonos[KEYS["CRIT_RATE"]] = 100.0
            
            atk_actual = stats_actuales.get("Ataque", 0.0) if stats_actuales else 0.0
            crit_dmg_bonus = atk_actual * 0.03
            
            if crit_dmg_bonus > 105.0:
                crit_dmg_bonus = 105.0
                
            bonos[KEYS["CRIT_DMG"]] = bonos.get(KEYS["CRIT_DMG"], 0) + crit_dmg_bonus
            bonos["Sunna_Cat_Gaze_DMG_Bonus_M6"] = 50.0

    return bonos

def efecto_aria(mindscape, stacks=0, condicion_activa=False, stats_actuales=None, **kwargs):
    """
    Aria:
    M1: Ignora 10% Anomaly Buildup RES. 
        Abloom puede hacer crítico (Base: 25% CR / 25% CD).
        Si Anomaly Mastery (Proficiency) > 100, gana +0.5% CR por punto extra.
    M2: Ignora 16% DEF. En 'Moment of Delusion', ignora 8% adicional (24% total).
    M4: Utilidad de Energía y Decibelios (Ignorado).
    M6: +40% Ether DMG a Básicos mejorados y Ultimate (Moment of Delusion).
    """
    bonos = {}

    if mindscape >= 1:
        bonos[KEYS["ANOM_RES_RED"]] = 10.0
        
        if condicion_activa:
            crit_rate_abloom = 25.0
            
            if stats_actuales:
                anom_mastery = stats_actuales.get("ANOMALY_PROF", 0.0)
                if anom_mastery > 100.0:
                    exceso = anom_mastery - 100.0
                    crit_rate_abloom += exceso * 0.5
            
            bonos[KEYS["CRIT_RATE"]] = crit_rate_abloom
            bonos[KEYS["CRIT_DMG"]] = 25.0

    if mindscape >= 2:
        bonos[KEYS["Ignorar_Defensa"]] = 24.0 if condicion_activa else 16.0

    if mindscape >= 6 and condicion_activa:
        bonos[KEYS["DMG_BONUS"]] = bonos.get(KEYS["DMG_BONUS"], 0) + 40.0

    return bonos

def efecto_nangong_yu(mindscape, stacks=0, condicion_activa=False, stats_actuales=None, **kwargs):
    """
    Nangong Yu:
    M1: Reduce All-Attribute RES un 18% al golpear con EX o Básico (40s).
    M2: +10% al ratio de Abloom por cada stack de Vibrato. +30% Stun DMG Multiplier (Angel Captain).
    M4: +40 Anomaly Proficiency (Siempre). +35% Anomaly Buildup en Ataque Básico.
    M6: +50% Daze global. Modifica las bases de Abloom y la mecánica a 'Vibrato: Modified'.
    """
    bonos = {}

    if mindscape >= 4:
        bonos[KEYS["ANOMALY_PROF"]] = 40.0

    if mindscape >= 6:
        bonos[KEYS["DAZE"]] = 50.0
        bonos["Info_Nangong_M6"] = "Vibrato: Modified Activo (Bases de Abloom masivas)"

    if condicion_activa:
        if mindscape >= 1:
            val_res = 18.0
            bonos[KEYS["PEN_RES_FISICO"]] = val_res
            bonos[KEYS["PEN_RES_FUEGO"]] = val_res
            bonos[KEYS["PEN_RES_ELECTRICO"]] = val_res
            bonos[KEYS["PEN_RES_HIELO"]] = val_res
            bonos[KEYS["PEN_RES_ETEREO"]] = val_res
        
        if mindscape >= 2:
            bonos["Stun_DMG_Multiplier"] = 30.0
            if stacks > 0:
                stacks_reales = min(stacks, 4)
                bonos["Abloom_Ratio_Extra_M2"] = stacks_reales * 10.0

        if mindscape >= 4:
            bonos[KEYS["ANOMALY_BUILDUP"]] = bonos.get(KEYS["ANOMALY_BUILDUP"], 0) + 35.0

    return bonos

def efecto_cissia(mindscape, stacks=0, condicion_activa=False, stats_actuales=None, **kwargs):
    """
    Cissia:
    M1: Todo el equipo ignora 5% Electric RES.
    M2: +35% DMG al Ataque Básico (Serpent's Kiss).
    M4: Consume stacks de 'Decidedness' (Max 3) al usar el Básico. Cada stack detona 1 Corrode Bone extra (335% MV).
    M6: Los aliados pueden detonar Corrode Bone (informativo).
    """
    bonos = {}

    if mindscape >= 1:
        bonos[KEYS["PEN_RES_ELECTRICO"]] = 5.0

    if condicion_activa:
        if mindscape >= 2:
            bonos["Bono_Dano_Basico"] = 35.0

        if mindscape >= 4 and stacks > 0:
            stacks_reales = min(stacks, 3)
            bonos[KEYS["MV_ADD"]] = stacks_reales * 335.0

    return bonos

def efecto_promeia(mindscape, stacks=0, condicion_activa=False, stats_actuales=None, **kwargs):
    """
    Promeia:
    M1: Ignora 20% de DEF si se detona Abloom en un enemigo con 'Presumption of Guilt'. (Condicional).
        (Nota: La regeneración de 1 punto de Trial by Cold es utilidad y no se calcula aquí).
    M2: +40 Anomaly Proficiency (Maestría de Anomalía) permanente.
        El Abloom detonado por Trial by Cold gana +120% de multiplicador. (Condicional).
    M4: Regeneración de Corrosive Chill (Ignorado, utilidad).
    M6: Detona un Abloom adicional fijo de 200% (Simulado como +200% extra a los ratios).
        Además, el daño de Anomalía y Disorder ignora 15% All-Attribute RES. (Condicional).
    """
    bonos = {}

    if mindscape >= 2:
        bonos[KEYS["ANOMALY_PROF"]] = 40.0

    if condicion_activa:
        if mindscape >= 1:
            bonos[KEYS["Ignorar_Defensa"]] = 20.0
            
        if mindscape >= 2:
            bonos["Abloom_Ratio_Extra_M2"] = 120.0

        if mindscape >= 6:
            bonos["Abloom_Ratio_Extra_M6"] = 200.0
            
            val_res = 15.0
            bonos[KEYS["PEN_RES_FISICO"]] = val_res
            bonos[KEYS["PEN_RES_FUEGO"]] = val_res
            bonos[KEYS["PEN_RES_ELECTRICO"]] = val_res
            bonos[KEYS["PEN_RES_HIELO"]] = val_res
            bonos[KEYS["PEN_RES_ETEREO"]] = val_res

    return bonos

def efecto_starlight_billy(mindscape, stacks=0, condicion_activa=False, nombre_habilidad="", stats_actuales=None, **kwargs):
    """
    Starlight - Billy Mindscapes (solo los que afectan daño):

    M1 — Heroic Entrance:
      - Core Passive: +60 Adrenalina al entrar (informativo).
      - Golpear con EX Special: ignora 18% Physical RES por 45s.

    M2 — Wasteland Automaton:
      - Full-Throttle Starlight, EX Cool Wheelie, Ultimate: +50% DMG.
      - Turbocharged (condicion_activa): Drive Suppression → sigue con EX Cool Wheelie
        y ese hit gana +50% CRIT DMG.

    M4 — Flames of Justice:
      - Cada uso de Drive Suppression: +8% CRIT DMG (máx 2 stacks, 45s).
        → Usamos stacks (0-2) para representar las cargas activas.

    M6 — Starlight Knight:
      - Ultimate y Full-Throttle Starlight: +18% Sheer DMG (se suma como DMG_BONUS).
      - Brilliant Starlight (stacks, máx 6): al usar Ulti o Full-Throttle,
        consume hasta 2 stacks → cada stack añade 100% Sheer Force como daño físico adicional.
        Representamos esto sumando el valor de Sheer Force × stacks_consumidos.
    """
    bonos = {}

    hab_norm = nombre_habilidad.lower() if nombre_habilidad else ""
    es_ex       = "ex" in hab_norm or "cool wheelie" in hab_norm or "high-traction" in hab_norm or "rocking" in hab_norm
    es_ulti     = "ultimate" in hab_norm or "definitiva" in hab_norm or "flying kick" in hab_norm
    es_fullthro = "full-throttle" in hab_norm or "full throttle" in hab_norm

    if mindscape >= 1 and condicion_activa and es_ex:
        bonos[KEYS["PEN_RES_FISICO"]] = bonos.get(KEYS["PEN_RES_FISICO"], 0.0) + 18.0

    if mindscape >= 2:
        if es_fullthro or es_ex or es_ulti:
            bonos[KEYS["DMG_BONUS"]] = bonos.get(KEYS["DMG_BONUS"], 0.0) + 50.0
        if condicion_activa and es_ex:
            bonos[KEYS["CRIT_DMG"]] = bonos.get(KEYS["CRIT_DMG"], 0.0) + 50.0

    if mindscape >= 4:
        cargas_m4 = max(0, min(int(stacks), 2))
        bonos[KEYS["CRIT_DMG"]] = bonos.get(KEYS["CRIT_DMG"], 0.0) + 8.0 * cargas_m4

    if mindscape >= 6:
        if es_ulti or es_fullthro:
            bonos[KEYS["DMG_BONUS"]] = bonos.get(KEYS["DMG_BONUS"], 0.0) + 18.0

            brilliant_stacks = max(0, min(int(stacks), 6))
            stacks_consumidos = min(brilliant_stacks, 2)
            if stacks_consumidos > 0 and stats_actuales:
                sheer_force = stats_actuales.get("Sheer_Force_Total", 0.0)
                bonos["DMG_Extra_Plano_Fisico"] = sheer_force * stacks_consumidos * 1.0

    return bonos

MAPA_MINDSCAPES = {
    "Anby": efecto_anby,
    "Anton": efecto_anton,
    "Astra Yao": efecto_astra_yao,
    "Alice": efecto_alice,
    "Soldier 0 - Anby": efecto_soldier_0_anby,
    "Banyue": efecto_banyue,
    "Ben": efecto_ben,
    "Burnice": efecto_burnice,
    "Caesar": efecto_caesar,
    "Corin": efecto_corin,
    "Dialyn": efecto_dialyn,
    "Ellen": efecto_ellen,
    "Evelyn": efecto_evelyn,
    "Grace": efecto_grace,
    "Harumasa": efecto_harumasa,
    "Hugo": efecto_hugo,
    "Jane": efecto_jane,
    "Ju Fufu": efecto_ju_fufu,
    "Koleda": efecto_koleda,
    "Lighter": efecto_lighter,
    "Lucia": efecto_lucia,
    "Lucy": efecto_lucy,
    "Lycaon": efecto_lycaon,
    "Manato": efecto_manato,
    "Miyabi": efecto_miyabi,
    "Nekomata": efecto_nekomata,
    "Nicole": efecto_nicole,
    "Orphie & Magus": efecto_orphie_magus,
    "Pan Yinhu": efecto_pan_yinhu,
    "Piper": efecto_piper,
    "Pulchra": efecto_pulchra,
    "Qingyi": efecto_qingyi,
    "Rina": efecto_rina,
    "Seed": efecto_seed,
    "Seth": efecto_seth,
    "Soldier 11": efecto_soldier_11,
    "Soukaku": efecto_soukaku,
    "Trigger": efecto_trigger,
    "Vivian": efecto_vivian,
    "Yanagi": efecto_yanagi,
    "Ye Shunguang": efecto_ye_shunguang,
    "Yidhari": efecto_yidhari,
    "Yixuan": efecto_yixuan,
    "Yuzuha": efecto_yuzuha,
    "Zhao": efecto_zhao,
    "Zhu Yuan": efecto_zhu_yuan,
    "Sunna": efecto_sunna,
    "Aria": efecto_aria,
    "Nangong Yu": efecto_nangong_yu,
    "Cissia": efecto_cissia,
    "Promeia": efecto_promeia,
    "Starlight - Billy": efecto_starlight_billy,
}

CONFIG_MINDSCAPES = {

    "Anby": {"min_mindscape": [2, 6],"usa_condicion": True, 
        "texto_condicion": "Enemigo Aturdido (M2)",
        "max_stacks": 8, "nombre_stack": "Carga M6"},
    
    "Anton": {"min_mindscape": 4, "usa_condicion": True, 
        "texto_condicion": "Postura Defensiva (M4)",
        "max_stacks": 6, "nombre_stack": "Piloteadora (M6)"},

    "Astra Yao": {"min_mindscape": 1,"usa_condicion": True,
        "texto_condicion": "Buff Quick Assist (M4) / Self-Buff (M6)",
        "max_stacks": 3,"nombre_stack": "Res Down (M1)"},

    "Alice": {"min_mindscape": 1, "usa_condicion": True, 
        "texto_condicion": "Buffs Activos (M1 Def / M2 Dmg)"},

    "Soldier 0 - Anby": {"min_mindscape": 4, 
        "usa_condicion": True,"texto_condicion": "Silver Star (M4) / Vortex (M6)"},

    "Banyue": {"min_mindscape": 1, 
        "usa_condicion": True,"texto_condicion": "Tremor / Skills Potenciadas (M1/M4/M6)"},

    "Ben": {
        "min_mindscape": 2,"usa_condicion": True,
        "texto_condicion": "Tras Bloqueo / Counter / EX (M2/M4/M6)"},

    "Billy": {"min_mindscape": 2, "usa_condicion": True,
        "texto_condicion": "Dodge Counter (M2) / EX Cerca (M4)",
        "max_stacks": 5,"nombre_stack": "Hits M6"},

    "Burnice": {"min_mindscape": 1,"usa_condicion": True,
        "texto_condicion": "Skills Activas (EX / Afterburn / Assist)",
        "opciones_condicion": ["Ninguno", "Afterburn (M1)", "EX/Assist (M4+M6)", "Todo activo"],
        "max_stacks": 5,"nombre_stack": "Thermal Pen. (M2)"},

    "Caesar": {"min_mindscape": 1,"usa_condicion": True,
        "texto_condicion": "Escudo Activo (M1) / Buff M6",},

    "Corin": {"min_mindscape": 1,"usa_condicion": True,
        "texto_condicion": "Buff Post-Ulti (M1)","max_stacks": 40,
        "nombre_stack": "Cargas (M2/M6)"},    

    "Dialyn": {"min_mindscape": 1,"usa_condicion": True,
        "texto_condicion": "Buffs Activos (Reviews / Complaint)",},

    "Ellen": {"min_mindscape": 1,"usa_condicion": True,
        "texto_condicion": "Burst/EX Activo (M2/M6)","max_stacks": 6,
        "nombre_stack": "Flash Freeze"},    

    "Evelyn": {"min_mindscape": 1,"usa_condicion": True,
        "texto_condicion": "Combate Activo (Bound/Shield/M6)",},

    "Grace": {"min_mindscape": 2,"usa_condicion": True,
        "texto_condicion": "Debuff Aplicado / M6 Active",},

    "Harumasa": {"min_mindscape": 2,"usa_condicion": True,
        "texto_condicion": "Dash Atk (M2) / Stunned+Nuke (M6)",},

    "Hugo": {"min_mindscape": 1,"usa_condicion": True,
        "texto_condicion": "Modo Totalize / Burst",},

    "Jane": {"min_mindscape": 1,"usa_condicion": True,
        "texto_condicion": "Estado Passion / Gnawed",},

    "Ju Fufu": {"min_mindscape": 1,"usa_condicion": True,
        "texto_condicion": "Tiger's Roar / Chain Attack",},

    "Koleda": {"min_mindscape": 1,"usa_condicion": True,
        "texto_condicion": "Combo / Burst Activo","max_stacks": 2,
        "nombre_stack": "Cargas Furnace (M4)"},

    "Lighter": {"min_mindscape": 1,"usa_condicion": True,
        "texto_condicion": "Collapse (Res/Stun) / M6 Nuke",
        "opciones_condicion": ["Ninguno", "Collapse (M1 Res)", "Finishing Move (M1 DMG)", "Nuke M6", "Todo activo"],},

    "Lucia": {"min_mindscape": 1,"usa_condicion": True,
        "texto_condicion": "Buff Activo / Skill Harmony",},

    "Lucy": {"min_mindscape": 1,"usa_condicion": True,
        "texto_condicion": "Buff Cheer On! / M6 Activo",},

    "Lycaon": {"min_mindscape": 1,"usa_condicion": True,
        "texto_condicion": "EX Charged (M1)","max_stacks": 5,
        "nombre_stack": "Hunter Stacks (M6)"},

    "Manato": {"min_mindscape": 1,"usa_condicion": True,
        "texto_condicion": "Molten Edge / Max HP Loss","max_stacks": 5,
        "nombre_stack": "Remnant Flame (M6)"},

    "Miyabi": {"min_mindscape": 1,"usa_condicion": True,
        "texto_condicion": "Buffs Activos / Stance",
        "opciones_condicion": ["Ninguno", "Kazahana/Dodge (M2)", "Frostburn Break (M4)", "Shimotsuki (M6)", "Todo activo"],
        "max_stacks": 6,"nombre_stack": "Fallen Frost (M1)"},

    "Nekomata": {"min_mindscape": 1,"usa_condicion": True,
        "texto_condicion": "Back Atk / EX Buff Active","max_stacks": 3,
        "nombre_stack": "Predator Stacks (M6)"},

    "Nicole": {"min_mindscape": 1,"usa_condicion": True,
        "texto_condicion": "Usando EX Special (M1)","max_stacks": 10,
        "nombre_stack": "Hits de Campo (M6)"},

    "Orphie & Magus": {"min_mindscape": 1,"usa_condicion": True,
        "texto_condicion": "Zeroed In / Post-Ult / Burst",},

    "Pan Yinhu": {"min_mindscape": 1,"usa_condicion": True,
        "texto_condicion": "Depleted Qi / M6 Activo",},

    "Piper": {"min_mindscape": 1,"usa_condicion": True,
        "texto_condicion": "Remate / Smash (M2)","max_stacks": 30,
        "nombre_stack": "Cargas Power"},

    "Pulchra": {"min_mindscape": 1,"usa_condicion": True,
        "texto_condicion": "Hunter's Gait / Binding Trap",},

    "Qingyi": {"min_mindscape": 1,"usa_condicion": True,
        "texto_condicion": "Max Voltage / Stacks",},

    "Rina": {"min_mindscape": 2,"usa_condicion": True,
        "texto_condicion": "Buffs Activos (M2/M6)",},

    "Seed": {"min_mindscape": 1,"usa_condicion": True,
        "texto_condicion": "Besiege / Max Energy","max_stacks": 24,
        "nombre_stack": "Energía (x5)"},

    "Seth": {"min_mindscape": 2,"usa_condicion": True,
        "texto_condicion": "Electrified Strike / Finisher",},

    "Soldier 11": {"min_mindscape": 2,"usa_condicion": True,
        "texto_condicion": "Usa Carga M6 (Fire Pen)","max_stacks": 12,
        "nombre_stack": "Stacks M2 (+3%)"},

    "Soukaku": {"min_mindscape": 4,"usa_condicion": True,
        "texto_condicion": "Frosted Banner / Flag Hit",},

    "Trigger": {"min_mindscape": 1,"usa_condicion": True,
        "texto_condicion": "Nuke M6 / Extra Hit M4","max_stacks": 4,
        "nombre_stack": "Hunter's Gaze (M2)"},

    "Vivian": {"min_mindscape": 1,"usa_condicion": True,
        "texto_condicion": "Prophecy / Special Atk","max_stacks": 5,
        "nombre_stack": "Plumas (M6 x5 DMG)"},

    "Yanagi": {"min_mindscape": 1,"usa_condicion": True,
        "texto_condicion": "Clarity / Exposed / EX",},

    "Ye Shunguang": {"min_mindscape": 1,"usa_condicion": True,
        "texto_condicion": "Unity / EX / Ultimate",},

    "Yidhari": {"min_mindscape": 1,"usa_condicion": True,
        "texto_condicion": "Basic/EX / Erudition",},

    "Yixuan": {"min_mindscape": 1,"usa_condicion": True,
        "texto_condicion": "Meditation / EX / Ult","max_stacks": 2,
        "nombre_stack": "Tranquillity (M4)"},

    "Yuzuha": {"min_mindscape": 1,"usa_condicion": True,
        "texto_condicion": "Sweet Scare / Buffs Activos",
        "max_stacks": 3,"nombre_stack": "Disorder Stacks (+105%)"},

    "Zhao": {"min_mindscape": 1,"usa_condicion": True,
        "texto_condicion": "Buffs Activos / Final Verdict",},

    "Zhu Yuan": {"min_mindscape": 2,"usa_condicion": True,
        "texto_condicion": "Suppressive Mode / EX",
        "max_stacks": 5,"nombre_stack": "Ether Ember (M2)"},
    
    "Sunna": {"min_mindscape": 1, "usa_condicion": True,
        "texto_condicion": "Ether Veil (M2) / Ultimate (M4) / EX (M6)",

        "max_stacks": 3, "nombre_stack": "DEF Shred (M1)"},
    "Aria": {"min_mindscape": 1, "usa_condicion": True,
        "texto_condicion": "Abloom / Moment of Delusion (M1/M2/M6)"},
        
    "Nangong Yu": {"min_mindscape": 1, "usa_condicion": True,
        "texto_condicion": "Hits de EX/Básico (M1/M4) / Enemigo Aturdido (M2)",
        "max_stacks": 4, "nombre_stack": "Vibrato (M2)"},

    "Cissia": {"min_mindscape": 1, "usa_condicion": True,
        "texto_condicion": "Usar Ataque Básico (M2/M4)","max_stacks": 3, 
        "nombre_stack": "Decidedness (M4)"},
    
    "Promeia": {"min_mindscape": 1, "usa_condicion": True,
        "texto_condicion": "Detonar Abloom / Enemigo con Presumption of Guilt"},

    "Starlight - Billy": {"min_mindscape": 1,"usa_condicion": True,
        "texto_condicion": "EX golpea (M1 Res) / Turbocharged (M2) / Buff Activo",
        "max_stacks": 6,"nombre_stack": "Drive Supp. (M4, 0-2) / Brilliant Starlight (M6, 0-6)",},
}