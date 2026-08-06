CONFIG_CORE_UI = {
    "Harumasa": {"usa_stacks": True, "max_stacks": 6,
        "default": 6, "label": "Stacks", "label_key": "core_ui.harumasa.label"},
    "Hugo": {"usa_stacks": True, "max_stacks": 15,
        "default": 15, "label": "Segundos", "label_key": "core_ui.hugo.label"},
    "Piper": {"usa_stacks": True, "max_stacks": 20,
        "default": 20, "label": "Stacks", "label_key": "core_ui.piper.label"},
    "ZhuYuan": {"usa_stacks": True, "max_stacks": 2,
        "default": 2, "label": "Modo", "label_key": "core_ui.zhuyuan.label"},
    "Astra Yao": {"usa_stacks": True, "max_stacks": 1, 
        "default": 1, "label": "\u00bfActivo?", "label_key": "core_ui.astra_yao.label"},
    "Lighter": {"usa_stacks": True, "max_stacks": 10,
        "default": 10, "label": "Moral (x10)", "label_key": "core_ui.lighter.label"},
    "Qingyi": {"usa_stacks": True, "max_stacks": 20,
        "default": 20, "label": "Cargas Subyugaci\u00f3n", "label_key": "core_ui.qingyi.label"},
    "Soukaku": {"usa_stacks": True, "max_stacks": 3, 
        "default": 3, "label": "1=Normal, 2=Vortex", "label_key": "core_ui.soukaku.label"},
    "Yuzuha": {"usa_stacks": True, "max_stacks": 6, 
        "default": 3, "label": "Sugar Points", "label_key": "core_ui.yuzuha.label"},
    "Aria": {"usa_stacks": True, "max_stacks": 2,
        "default": 1, "label": "1=Normal, 2=Aturdido", "label_key": "core_ui.aria.label"},
    "Nangong Yu": {"usa_stacks": True, "max_stacks": 4, 
        "default": 4, "label": "Vibrato", "label_key": "core_ui.nangong_yu.label"},
        "Cissia": {"usa_stacks": True, "max_stacks": 2, 
        "default": 2, "label": "Personajes Eléctricos", "label_key": "core_ui.cissia.label"},
    "Promeia": {"usa_stacks": True, "max_stacks": 2, 
        "default": 2, "label": "Trial by Cold", "label_key": "core_ui.promeia.label"},
    "Starlight - Billy": {"usa_stacks": True, "max_stacks": 120,
        "default": 100, "label": "Determinación", "label_key": "core_ui.starlight_billy.label"},
}


KEYS = {
    "ATK_PCT": "Ataque",
    "DMG_BONUS": "Daño_Adicional",
    "CRIT_DMG": "Daño_crítico",
    "ENERGY_REGEN": "Recuperación_energía",
    "CRIT_RATE": "Probabilidad_crítico",
    "DAZE": "Aturdimiento",
    "PEN_RATIO": "Tasa_de_Perforación",
    "ANOMALY_BUILDUP": "Bono_Acumulación",
    "ANOMALY_MASTERY": "Tasa_de_Anomalía",
    "ANOMALY_PROF": "Maestría_Anomalía",
    "DEF_FLAT": "Defensa",
}

def core_anby(condicion_activa=False, nombre_habilidad="", **kwargs):
    """
    Core: Launch Basic Attack: Thunderbolt... for an extra 64% Daze.
    Aplicamos esto si la casilla 'Core Activo' está marcada.
    """
    bonos = {}
    if condicion_activa:
        bonos[KEYS["DAZE"]] = 64.0
    return bonos

def core_ellen(condicion_activa=False, nombre_habilidad="", **kwargs):
    """
    Core: ...skill's CRIT DMG increases by 100%.
    Aplica a: Chain, Ultimate, y Básicos específicos.
    """
    bonos = {}

    hab = nombre_habilidad.lower()
    keywords = ["basico", "cadena", "definitiva"]
    
    es_habilidad_valida = any(k in hab for k in keywords)

    if condicion_activa and es_habilidad_valida:
        bonos[KEYS["CRIT_DMG"]] = 100.0
        
    return bonos

def core_evelyn(condicion_activa=False, nombre_habilidad="", **kwargs):
    """
    Core: Upon entering Binding Seal, CRIT Rate increases by 25%.
    """
    bonos = {}
    if condicion_activa:
        bonos[KEYS["CRIT_RATE"]] = 25.0
    return bonos

def core_alice(condicion_activa=False, nombre_habilidad="", **kwargs):
    """
    Core: 
    1. (Activo) +25% Physical Anomaly Buildup Rate (durante 30s tras Assault).
    2. (Opcional) Max Disorder Multiplier +180% (Depende de la duración).
    """
    bonos = {}
    
    if condicion_activa:
        bonos[KEYS["ANOMALY_BUILDUP"]] = 25.0
        bonos["Bono_Disorder_Seg"] = 18.0

    return bonos

def core_soldier_0(condicion_activa=False, nombre_habilidad="", stats_actuales=None, **kwargs):
    """
    Core: 
    1. +25% DMG a enemigos marcados (Silver Star).
    2. Las Réplicas (Aftershocks) ganan Crit DMG igual al 35% (30+5) del Crit DMG de Anby.
    """
    bonos = {}
    
    if condicion_activa:
        bonos[KEYS["DMG_BONUS"]] = 25.0

        if stats_actuales:

            crit_dmg_actual = stats_actuales.get(KEYS["CRIT_DMG"], 50.0)
            bono_critico = crit_dmg_actual * 0.35
            
            bonos[KEYS["CRIT_DMG"]] = bono_critico

    return bonos

def core_anton(condicion_activa=False, nombre_habilidad="", **kwargs):
    """
    Core Passive Anton:
    - Drill Attack (Taladro) -> +40% DMG
    - Pile Driver (Piloteadora) -> +24% DMG
    """
    bonos = {}
    if not condicion_activa:
        return bonos

    hab = nombre_habilidad.lower()

    keywords_drill = ["taladro"]
    if any(k in hab for k in keywords_drill):
        bonos[KEYS["DMG_BONUS"]] = 40.0

    elif any(k in hab for k in ["martillo"]):
        bonos[KEYS["DMG_BONUS"]] = 24.0

    return bonos

def core_ben(condicion_activa=False, stats_actuales=None, **kwargs):
    """
    Core Ben:
    1. Gana 80% de su Defensa como ATAQUE (Plano).
    2. (Shield) 30% DEF + 550. (Calculamos el valor por si lo quieres mostrar).
    """
    bonos = {}
    
    if stats_actuales:
        defensa = stats_actuales.get(KEYS["DEF_FLAT"], 0.0)
        if defensa == 0:
             defensa = stats_actuales.get("Defensa", 0.0)

        atk_extra = defensa * 0.80

        bonos["Ataque_Ben_Conversion"] = atk_extra

    return bonos

def core_banyue(condicion_activa=False, **kwargs):
    """
    Core Passive Banyue:
    - Activa (EX/Assist): +300 Sheer Force, +36% Fire DMG, +36% Crit DMG.
    """
    bonos = {}

    if condicion_activa:
        bonos["Sheer_force"] = 300.0
        bonos["Daño_elemental"] = 36.0
        bonos[KEYS["CRIT_DMG"]] = 36.0

    return bonos

def core_billy(condicion_activa=False, **kwargs):
    """
    Core Billy:
    - Crouching Shot (Disparo Agachado) -> +50% DMG
    """
    bonos = {}
    
    if condicion_activa:
        bonos[KEYS["DMG_BONUS"]] = 50.0

    return bonos

def core_burnice(condicion_activa=False, stats_actuales=None, nombre_habilidad="", **kwargs):
    bonos = {}
    if not stats_actuales:
        return bonos
        
    maestria = stats_actuales.get("Maestría_Anomalía", 0.0)
    bono_afterburn = maestria / 10.0
    if bono_afterburn > 30.0:
        bono_afterburn = 30.0
    bonos["Bono_Afterburn"] = bono_afterburn

    ratio_am = stats_actuales.get("Ratio_Maestría_por_ER", 0.0)
    ratio_dmg = stats_actuales.get("Ratio_DMG_por_ER", 0.0)
    tope_am = stats_actuales.get("Tope_Maestría", 0.0)
    tope_dmg = stats_actuales.get("Tope_DMG", 0.0)
    
    er = stats_actuales.get("Recuperación_energía", 0.0)
    
    if er >= 1.8 and ratio_am > 0:
        exceso = er - 1.8
        puntos = exceso * 10.0
        
        bono_am = min(tope_am, puntos * ratio_am)
        bono_dmg = min(tope_dmg, puntos * ratio_dmg)
        
        if bono_am > 0:
            bonos["Maestría_Anomalía"] = bono_am
        if bono_dmg > 0:
            bonos["Daño_Adicional"] = bono_dmg

    if condicion_activa:
        potencial = int(kwargs.get('potencial', 0))
        hab_norm = nombre_habilidad.lower()
        
        if potencial >= 1 and ("intense heat tossing method" in hab_norm or "burnice_lanza" in hab_norm):
            bonos["Abloom_Ether_Add"] = 480.0
            bonos["Abloom_Elec_Add"]  = 240.0
            bonos["Abloom_Fire_Add"]  = 600.0
            bonos["Abloom_Phys_Add"]  = 40.0
            bonos["Abloom_Ice_Add"]   = 60.0
            bonos["Abloom_Wind_Add"]  = 24.0
            
    return bonos

def core_corin(condicion_activa=False, **kwargs):
    """
    Core Corin:
    - Extended Slash (Motosierra continua) -> +37.5% DMG
    """
    bonos = {}
    
    if condicion_activa:
        bonos[KEYS["DMG_BONUS"]] = 37.5

    return bonos

def core_grace(condicion_activa=False, nombre_habilidad="", **kwargs):
    """
    Core Grace:
    - Consumir 8 stacks de Zap -> +130% Electric Anomaly Buildup.
    - (NUEVO) Potencial 1: Pulse Grenade aplica multiplicadores masivos de Abloom
      (solo si se usa la habilidad Supercharged Obstruction Removal).
    """
    bonos = {}
    
    if condicion_activa:
        bonos[KEYS["ANOMALY_BUILDUP"]] = 130.0
        potencial = int(kwargs.get('potencial', 0))
        hab_norm = nombre_habilidad.lower()
        
        if potencial >= 1 and ("supercharged obstruction removal" in hab_norm or "grace_abloom" in hab_norm):
            bonos["Abloom_Ether_Add"] = 560.0
            bonos["Abloom_Elec_Add"]  = 280.0
            bonos["Abloom_Fire_Add"]  = 700.0
            bonos["Abloom_Phys_Add"]  = 50.0
            bonos["Abloom_Ice_Add"]   = 70.0
            bonos["Abloom_Wind_Add"]  = 28.0

    return bonos

def core_harumasa(condicion_activa=False, **kwargs):
    """
    Core Harumasa (Dinámico):
    - Dash Attack: +25% Crit Rate (Fijo si activo).
    - Gleaming Edge: +12% Crit DMG por Stack (Max 6).
    """
    bonos = {}
    
    if condicion_activa:
        bonos[KEYS["CRIT_RATE"]] = 25.0

        stacks_input = kwargs.get('stacks', 0)
        if not stacks_input:
            stacks_input = 6

        stacks_reales = min(int(stacks_input), 6)

        bonos[KEYS["CRIT_DMG"]] = 12.0 * stacks_reales

    return bonos

def core_hugo(condicion_activa=False, nombre_habilidad="", stacks=0, tipos_soportes=None, **kwargs):
    """
    Core Hugo:
    - Dark Abyss Reverb (Activo): +12% Crit Rate, +25% Crit DMG.
    - Sinergia Stun: +300 ATK (1 Stunner), +900 ATK (2 Stunners).
    - Totalize (Stacks = Segundos Restantes de Stun):
      Aumenta masivamente el Multiplicador de la Habilidad (Ex/Ulti).
      Base +1000%. 
      <= 5s: +280% por seg.
      > 5s: +100% por seg extra.
      Max +3400%.
    """
    bonos = {}
    

    if condicion_activa:
        bonos["Probabilidad_crítico"] = 12.0
        bonos["Daño_crítico"] = 25.0

    if tipos_soportes:
        num_stunners = sum(1 for t in tipos_soportes if "aturdidor" in t)
        
        if num_stunners == 1:
            bonos["Ataque"] = 300.0
        elif num_stunners >= 2:
            bonos["Ataque"] = 900.0

    hab_norm = nombre_habilidad.lower()
    es_nuke = "ex" in hab_norm or "special" in hab_norm or "definitiva" in hab_norm or "ultimate" in hab_norm or "soul" in hab_norm or "hugo_c1" in hab_norm or "hugo_c3" in hab_norm
    
    if es_nuke and stacks > 0:
        tiempo_restante = float(stacks)
        
        bono_mv = 1000.0
        
        segundos_fase1 = min(tiempo_restante, 5.0)
        bono_mv += segundos_fase1 * 280.0
        
        if tiempo_restante > 5.0:
            segundos_fase2 = min(tiempo_restante - 5.0, 10.0)
            bono_mv += segundos_fase2 * 100.0

        if bono_mv > 3400.0:
            bono_mv = 3400.0
            
        bonos["Multiplicador_de_ataques"] = bono_mv

    if "ex" in hab_norm and stacks == 0:
        bonos["Bono_Stun_Ex"] = 20.0

    return bonos

def core_jane(condicion_activa=False, stats_actuales=None, **kwargs):
    """
    Core Jane:
    - Estado 'Gnawed': Permite que el ASSAULT (Asalto) haga Crítico.
    - Base: 40% Rate, 50% DMG.
    - Scaling: +0.16% Rate por cada punto de Maestría de Anomalía.
    """
    bonos = {}

    if condicion_activa:
        maestria = 0.0
        if stats_actuales:
            maestria = stats_actuales.get("Maestría_Anomalía", 0.0)

        extra_rate = maestria * 0.16
        total_assault_rate = 40.0 + extra_rate

        bonos["Assault_Crit_Rate"] = total_assault_rate
        bonos["Assault_Crit_DMG"] = 50.0

    return bonos

def core_manato(condicion_activa=False, **kwargs):
    """
    Core Manato:
    - Molten Edge (Activo):
        * +10% Crit Rate
        * +20% Fire DMG
        * +50% Crit DMG (Asumiendo ataque con consumo de HP)
    """
    bonos = {}

    if condicion_activa:
        bonos["Probabilidad_crítico"] = 10.0
        bonos["Daño_elemental"] = 20.0
        
        bonos[KEYS["CRIT_DMG"]] = 50.0

    return bonos

def core_miyabi(condicion_activa=False, stats_actuales=None, **kwargs):
    """
    Core Miyabi:
    - Pasiva: Convierte Crit Rate en Anomaly Buildup (1:1).
      * Tope: 80% extra.
    - Activa (Frostburn - Break):
      * Simula el golpe de 1500% ATK (Se suma al Multiplicador).
      * Aplica el bono de equipo de +20% Buildup.
    """
    bonos = {}

    if stats_actuales:
        crit_rate = stats_actuales.get("Probabilidad_crítico", 0.0)
        
        extra_buildup = crit_rate
        
        if extra_buildup > 80.0:
            extra_buildup = 80.0

        bonos[KEYS["ANOMALY_BUILDUP"]] = extra_buildup

    if condicion_activa:
        atk_actual = 0.0
        if stats_actuales:
            atk_actual = stats_actuales.get("Ataque", 0.0)

        daño_proc = atk_actual * 15.0

        bonos["Flat_MV"] = daño_proc

        bonos[KEYS["ANOMALY_BUILDUP"]] = bonos.get(KEYS["ANOMALY_BUILDUP"], 0.0) + 20.0

    return bonos

def core_nekomata(condicion_activa=False, **kwargs):
    """
    Core Nekomata:
    - Al acertar Dodge Counter o Quick Assist: +60% DMG por 6s.
    """
    bonos = {}

    if condicion_activa:
        bonos[KEYS["DMG_BONUS"]] = 60.0

    return bonos

def core_piper(condicion_activa=False, **kwargs):
    """
    Core Piper:
    - Acumula stacks de 'Power' (Max 20).
    - Efecto: +4% Physical Anomaly Buildup por stack.
    - Max: +80% Buildup.
    """
    bonos = {}

    if condicion_activa:
        stacks_input = kwargs.get('stacks', 20)

        stacks_reales = min(int(stacks_input), 20)

        bono_buildup = stacks_reales * 4.0

        bonos[KEYS["ANOMALY_BUILDUP"]] = bono_buildup

    return bonos

def core_soldier11(condicion_activa=False, **kwargs):
    """
    Core Soldier 11:
    - Fire Suppression: Requiere timing preciso en los ataques.
    - Efecto: +70% DMG al acertar el timing (Basic Attack).
    """
    bonos = {}

    if condicion_activa:
        bonos[KEYS["DMG_BONUS"]] = 70.0

    return bonos

def core_yanagi(condicion_activa=False, **kwargs):
    """
    Core Yanagi:
    - Buff Elemental: +20% Daño Eléctrico (por 15s).
    - Buff Disorder: Aumenta el multiplicador base de Disorder en +250%.
      (Ej: De 450% pasa a 700%).
    """
    bonos = {}

    if condicion_activa:
        bonos["Daño_elemental"] = 20.0
        bonos["Disorder_Extra_Mult"] = 250.0

    return bonos

def core_yidhari(condicion_activa=False, **kwargs):
    """
    Core Yidhari:
    - Low HP Buff (<50% HP):
      * Si activas el Core, asumimos que estás por debajo del 50% de vida.
      * Otorga el bono máximo: +100% DMG.
    """
    bonos = {}

    if condicion_activa:
        bonos[KEYS["DMG_BONUS"]] = 100.0

    return bonos

def core_yixuan(condicion_activa=False, **kwargs):
    """
    Core Yixuan:
    - Buff de Habilidad: +60% DMG a Básicos, EX, Assist, Chain y Ult.
      (Al cubrir casi todo el kit, lo aplicamos como DMG Bonus general).
    """
    bonos = {}

    if condicion_activa:
        bonos[KEYS["DMG_BONUS"]] = 60.0

    return bonos

def core_zhuyuan(condicion_activa=False, **kwargs):
    """
    Core Zhu Yuan:
    - Modo Supresivo (Uso de Cartuchos): +36.6% DMG base.
    - Bonus Stun: +36.6% adicional si el enemigo está aturdido.
    Control por Stacks:
    - 1: Solo Modo Supresivo (+36.6%).
    - 2: Modo Supresivo + Enemigo Aturdido (+73.2%).
    """
    bonos = {}

    if condicion_activa:
        bono_dmg = 36.6
        modo_stun = int(kwargs.get('stacks', 1)) >= 2
        
        if modo_stun:
            bono_dmg += 36.6
            
        bonos[KEYS["DMG_BONUS"]] = bono_dmg

    return bonos

def core_lucy(condicion_activa=False, stats_actuales=None, **kwargs):
    """
    Core Lucy:
    - Los Jabalíes heredan el ATK y el Impacto de Lucy.
    - El bufo 'Cheer On!' para los jabalíes es del 200% de su efecto original.
    """
    bonos = {}

    if condicion_activa and stats_actuales:
        atk_lucy = stats_actuales.get(KEYS["ATK_PCT"], 0.0)
        if atk_lucy == 0: 
            atk_lucy = stats_actuales.get("Ataque", 0.0)
            
        impact_lucy = stats_actuales.get("Impacto", 0.0)

        buff_base = (atk_lucy * 0.138) + 44.0

        buff_jabalies = buff_base * 2.0

        atk_jabali_total = atk_lucy + buff_jabalies

        bonos["Jabalí_Impacto"] = impact_lucy
        bonos["Jabalí_ATK_Total"] = atk_jabali_total

    return bonos

def core_astra_yao(condicion_activa=False, stats_actuales=None, **kwargs):
    """
    Core Astra Yao:
    - Estado 'Idyllic Cadenza': Aumenta el ATK en 35% del ATK Inicial de Astra.
    - Máximo: 1,200 ATK.
    """
    bonos = {}

    if condicion_activa and stats_actuales:
        atk_inicial = stats_actuales.get("Ataque", 0.0)
        
        buff_atk = atk_inicial * 0.35

        if buff_atk > 1200.0:
            buff_atk = 1200.0
            
        bonos["Ataque_Plano"] = buff_atk

    return bonos

def core_dialyn(condicion_activa=False, stats_actuales=None, **kwargs):
    """
    Core Dialyn:
    1. Conversión de Stats: Si Prob. Crit > 50%, gana 2 Impacto por cada 1% extra.
       (Máximo +100 Impacto).
    2. Queja Maliciosa (Condición Activa): +30% Multiplicador de Daño de Aturdimiento.
    """
    bonos = {}

    if stats_actuales:
        crit_rate = stats_actuales.get("Probabilidad_crítico", 0.0)
        
        if crit_rate > 50.0:
            exceso = crit_rate - 50.0
            bono_impacto = exceso * 2.0
            
            if bono_impacto > 100.0:
                bono_impacto = 100.0
                
            bonos["Impacto"] = bono_impacto

    if condicion_activa:
        bonos["Stun_DMG_Multiplier"] = 30.0

    return bonos

def core_ju_fufu(condicion_activa=False, stats_actuales=None, **kwargs):
    """
    Core Ju Fufu (Tiger's Roar):
    - Base: +20% Crit DMG para el equipo.
    - Escalado: Si ATK Inicial > 2800 -> +5% Crit DMG por cada 100 ATK extra.
    - Máximo extra: +30% (Tope total: 50% Crit DMG).
    - Efectos adicionales: Chain DMG +20%, Ult DMG +40%.
    - Self-Buff (Solo ella): +50 Impacto.
    """
    bonos = {}

    if condicion_activa and stats_actuales:
        atk_actual = stats_actuales.get("Ataque", 0.0)
        
        crit_dmg_bonus = 20.0

        if atk_actual >= 2800.0:
            exceso = atk_actual - 2800.0
            pasos = int(exceso // 100)
            extra = pasos * 5.0
            
            if extra > 30.0:
                extra = 30.0
            
            crit_dmg_bonus += extra

        bonos["Daño_crítico"] = crit_dmg_bonus

        bonos["Bono_Daño_Ulti"] = 40.0
        bonos["Bono_Daño_Cadena"] = 20.0
        bonos["Impacto"] = 50.0

    return bonos

def core_koleda(condicion_activa=False, **kwargs):
    """
    Core Koleda:
    - Al usar EX Special Attack o Basic Attack potenciado (Furnace Fire): El Daze (Aturdimiento) aumenta un 60%.
    """
    bonos = {}
    
    if condicion_activa:
        bonos[KEYS["DAZE"]] = 60.0

    return bonos

def core_caesar(condicion_activa=False, **kwargs):
    """
    Core Caesar (Radiant Aegis):

    - Buff: ATK +1000 (Plano).
    - Escudo: 1400% del Impacto + 1400 que no nos importa
    """
    bonos = {}
    
    if condicion_activa:
        bonos["Ataque_Plano"] = 1000.0
        
    return bonos

def core_lighter(condicion_activa=False, stacks=0, **kwargs):
    """
    Core Lighter (Morale Burst):
    - Impacto: Aumenta 2% por cada 10 Moral consumida (Stacks 0-10). Máx 20%.
    - Debuff (Activo): Reduce RES Hielo y Fuego del enemigo en 15%.
    """
    bonos = {}
    
    if stacks > 0:
        buff_impacto = stacks * 2.0
        if buff_impacto > 20.0: buff_impacto = 20.0
        bonos["Impacto"] = buff_impacto

    if condicion_activa:
        bonos["Red_Resistencia_Fuego"] = 15.0
        bonos["Red_Resistencia_Hielo"] = 15.0

    return bonos

def core_lucia(condicion_activa=False, **kwargs):
    """
    Core Lucia (Dream State):
    - Ether Veil: Aumenta HP Max en 5%.
    - Dreamer's Nursery Rhyme: Aumenta Daño en 20%.
    """
    bonos = {}
    
    if condicion_activa:
        bonos["Puntos_Vida"] = 5.0 
        bonos["Daño_Adicional"] = 20.0

    return bonos

def core_lycaon(condicion_activa=False, nombre_habilidad="", stats_actuales=None, **kwargs):
    bonos = {}
    
    habilidad_norm = nombre_habilidad.lower() if nombre_habilidad else ""
    if "basic" in habilidad_norm or "básico" in habilidad_norm or "basico" in habilidad_norm:
        bonos["Bono_Stun_Basico"] = 80.0

    if condicion_activa:
        bonos["Pen_Res_Hielo"] = 25.0

    if stats_actuales:
        impacto_base = stats_actuales.get("Impacto", 0.0)
        if impacto_base > 0:
            bonos["Impacto"] = 15.0
            
    return bonos

def core_nicole(condicion_activa=False, **kwargs):
    """
    Core Nicole:
    - Al golpear con balas mejoradas o Campo de Energía:
      Reduce la DEF del enemigo en 40% durante 3.5s.
    """
    bonos = {}
    
    if condicion_activa:
        bonos["Reduccion_DEF_enemigo"] = 40.0

    return bonos

def core_orphie_magus(condicion_activa=False, stats_actuales=None, **kwargs):
    """
    Core Orphie & Magus:
    - Pasiva: Crit Rate +25%, Aftershock DMG +85%.
    - Zeroed In (Activo): ATK Base +280.
    - Escalado: Si ER >= 1.6, +20 ATK por cada 0.1 ER extra.
    - Tope total ATK: 700.
    """
    bonos = {}
    
    bonos["Probabilidad_crítico"] = 25.0
    bonos["Daño_Aftershock"] = 85.0

    if condicion_activa and stats_actuales:
        er_actual = stats_actuales.get("Recuperación_energía", 1.56)
        
        buff_atk = 280.0

        if er_actual >= 1.6:
            exceso = er_actual - 1.6
            pasos = int(exceso / 0.1)
            extra = pasos * 20.0
            buff_atk += extra
            
        if buff_atk > 700.0:
            buff_atk = 700.0
            
        bonos["Ataque"] = buff_atk

    return bonos

def core_pan_yinhu(condicion_activa=False, stats_actuales=None, **kwargs):
    """
    Core Pan Yinhu (Meridian Flow):
    - Activo: Otorga Sheer Force igual al 18% del ATK.
    - Max: 540 puntos.
    """
    bonos = {}
    
    if condicion_activa and stats_actuales:
        atk_actual = stats_actuales.get("Ataque", 0.0)
        
        buff_sheer = atk_actual * 0.18
        
        if buff_sheer > 540.0:
            buff_sheer = 540.0

        bonos["Sheer_force"] = buff_sheer

    return bonos

def core_pulchra(condicion_activa=False, **kwargs):
    """
    Core Pulchra (Hunter's Gait):
    - Activo: Aumenta el Aturdimiento (Daze) que ella inflige en un 30%.
    """
    bonos = {}
    
    if condicion_activa:
        bonos["Aturdimiento"] = 30.0

    return bonos

def core_qingyi(stacks=0, **kwargs):
    """
    Core Qingyi (Subjugation):
    - Aplica cargas al enemigo (Max 20).
    - Cada carga aumenta el Multiplicador de Daño de Aturdimiento en 4%.
    """
    bonos = {}
    
    if stacks > 0:
        buff_stun_mult = stacks * 4.0

        if buff_stun_mult > 80.0:
            buff_stun_mult = 80.0

        bonos["Stun_DMG_Multiplier"] = buff_stun_mult

    return bonos

def core_rina(condicion_activa=False, stats_actuales=None, **kwargs):
    """
    Core Rina (Mini Destruction Partner):
    - Activo: Aumenta PEN Ratio del equipo (y ella misma).
    - Fórmula: (PEN_Actual * 0.25) + 12%.
    - Máximo: 30%.
    """
    bonos = {}
    
    if condicion_activa and stats_actuales:
        pen_actual = stats_actuales.get("Tasa_de_Perforación", 0.0)

        bono_pen = (pen_actual * 0.25) + 12.0

        if bono_pen > 30.0:
            bono_pen = 30.0
            
        bonos["Tasa_de_Perforación"] = bono_pen

    return bonos

def core_seed(condicion_activa=False, **kwargs):
    """
    Core Seed:
    - Onslaught: ATK +1000, Crit DMG +30%.
    - Besiege: Daño +25%.
    (Se asume que hay un Vanguardia en el equipo para activar Besiege).
    """
    bonos = {}
    
    if condicion_activa:
        bonos["Ataque_Plano"] = 1000.0
        bonos["Daño_crítico"] = 30.0

        bonos["Daño_Adicional"] = 25.0

    return bonos

def core_seth(condicion_activa=False, stats_actuales=None, **kwargs):
    """
    Core Seth:
    - Escudo: 80% del ATK Inicial (Máx 3000).
    - Buff: +100 Maestría de Anomalía (AP) mientras el escudo dura.
    """
    bonos = {}
    
    if condicion_activa:
        bonos["Maestría_Anomalía"] = 100.0
        
        if stats_actuales:
            atk_actual = stats_actuales.get("Ataque", 0.0)
            valor_escudo = atk_actual * 0.80
            
            if valor_escudo > 3000.0:
                valor_escudo = 3000.0
                
            bonos["Escudo_Seth"] = valor_escudo

    return bonos

def core_soukaku(stacks=0, stats_actuales=None, **kwargs):
    """
    Core Soukaku (Fly the Flag):
    - Stack 1 (Normal): ATK +20% (Max 500).
    - Stack 3 (Vortex): ATK +40% (Max 1000).
    - El bono es ATK Plano añadido a sí misma (y transferible).
    """
    bonos = {}
    
    if stacks > 0 and stats_actuales:
        atk_actual = stats_actuales.get("Ataque", 0.0)
        
        if stacks <= 2:
            buff = atk_actual * 0.20
            if buff > 500.0: buff = 500.0
        else:
            buff = atk_actual * 0.40
            if buff > 1000.0: buff = 1000.0
            
        bonos["Ataque_Plano"] = buff

    return bonos

def core_trigger(condicion_activa=False, **kwargs):
    """
    Core Trigger:
    - Debuff: Aumenta el Multiplicador de Daño de Stun del enemigo en 35%.
    - Aplica incluso si no está aturdido (afecta cálculo de daño final).
    """
    bonos = {}
    
    if condicion_activa:
        bonos["Unstun_DMG_Multiplier"] = 35.0

    return bonos

def core_vivian(condicion_activa=False, stats_actuales=None, nombre_habilidad="", **kwargs):
    bonos = {}

    if condicion_activa and stats_actuales:
        atk_actual = stats_actuales.get("Ataque", 0.0)
        ap_actual = stats_actuales.get("Maestría_Anomalía", 0.0)        
        dano_profecia = atk_actual * 0.55
        bonos["Vivian_Prophecy_Tick"] = dano_profecia
        
        hab_norm = nombre_habilidad.lower()
        
        if "featherbloom" in hab_norm or "frock" in hab_norm or "vivian_abloom" in hab_norm or "vivian_c3" in hab_norm:
            bloques_ap = ap_actual / 10.0
            bonos["Abloom_Ether_Add"] = bloques_ap * 6.15
            bonos["Abloom_Fire_Add"] = bloques_ap * 8.00
            bonos["Abloom_Elec_Add"] = bloques_ap * 3.20
            bonos["Abloom_Ice_Add"] = bloques_ap * 1.08
            bonos["Abloom_Phys_Add"] = bloques_ap * 0.75
            bonos["Abloom_Wind_Add"]  = bloques_ap * 0.32
        
    return bonos

def core_yuzuha(condicion_activa=False, stats_actuales=None, **kwargs):
    """
    Core Yuzuha (Tanuki Wish):
    - Mecánica: Puntos de Azúcar (Sugar Points) 0-6 (No afectan el buff en este texto).
    - Buff Activo: 
      1. ATK +40% del ATK Inicial (Max 1200).
      2. Daño +15%.
    """
    bonos = {}
    
    if condicion_activa and stats_actuales:
        atk_actual = stats_actuales.get("Ataque", 0.0)

        buff_atk = atk_actual * 0.40

        if buff_atk > 1200.0:
            buff_atk = 1200.0
            
        bonos["Ataque_Plano"] = buff_atk
        
        bonos["Daño_Adicional"] = 15.0

    return bonos

def core_zhao(condicion_activa=False, stats_actuales=None, **kwargs):
    """
    Core Zhao:
    - Pasiva: Gana 1.4% Crit Rate por cada 1,000 de HP Máximo.
    - Activa (Ether Veil): +1000 ATK y +5% HP Máximo.
    """
    bonos = {}
    
    if stats_actuales:
        hp_actual = stats_actuales.get("Puntos_Vida", 0.0)
        
        crit_extra = (hp_actual / 1000.0) * 1.4
        bonos["Probabilidad_crítico"] = crit_extra

        if condicion_activa:
            bonos["Ataque_Plano"] = 1000.0
            bonos["Puntos_Vida_%"] = 5.0 

    return bonos

def core_ye_shunguang(condicion_activa=False, **kwargs):
    """
    Core Ye Shunguang:
    - Unity (Siempre): +30% Crit Rate, +25% DMG.
    - Enlightened Mind (Activo):
      Reemplaza el Multiplicador de Stun con Vulnerabilidad (Max 110%).
      Simulamos esto sumando 110% al bono de stun.
      Esto hace que golpear a un enemigo no aturdido sea devastador (210% total).
    """
    bonos = {}
    
    bonos["Probabilidad_crítico"] = 30.0
    bonos["Daño_Adicional"] = 25.0
    
    if condicion_activa:
        bonos["Stun_DMG_Multiplier"] = 110.0

    return bonos

def core_sunna(condicion_activa=False, **kwargs):
    """
    Core Sunna (Habilidad Adicional):
    - Condición: Aliado 'Atacante' o Facción 'Ángeles de la Delusión'.
    - Efecto 1: Si el enemigo es atacado dentro del Ether Veil, su Stun DMG Multiplier aumenta en 30%.
    - Efecto 2: Sunna recupera 15 de Energía al entrar al combate.
    """
    bonos = {}
    
    if condicion_activa:
        bonos["Stun_DMG_Multiplier"] = 30.0
        bonos["Energia_Inicial_Plana"] = 15.0
        bonos["Info_Core_Sunna"] = "Ether Veil Activo: +30% Stun DMG Mult. / +15 Energía al entrar"

    return bonos

def core_aria(condicion_activa=False, stats_actuales=None, nombre_habilidad="", **kwargs):
    bonos = {}

    if condicion_activa and stats_actuales:
        bonos[KEYS["ANOMALY_PROF"]] = 90.0
        hab_norm = nombre_habilidad.lower()
        es_perfect_pitch = ("perfect pitch" in hab_norm or "3 cargas" in hab_norm
                           or "basico cargado" in hab_norm
                           or any(f"aria_c{i}" in hab_norm for i in range(4, 10)))
        if es_perfect_pitch:
            stat_anomalia = stats_actuales.get(KEYS["ANOMALY_MASTERY"], 0.0)
            bloques = stat_anomalia / 10.0
            es_aturdido = int(kwargs.get('stacks', 1)) >= 2
            multiplicador_stun = 1.5 if es_aturdido else 1.0
            
            bonos["Abloom_Ether_Add"] = bloques * 27.5 * multiplicador_stun
            bonos["Abloom_Fire_Add"]  = bloques * 35.7 * multiplicador_stun
            bonos["Abloom_Elec_Add"]  = bloques * 14.3 * multiplicador_stun
            bonos["Abloom_Ice_Add"]   = bloques * 3.6 * multiplicador_stun
            bonos["Abloom_Phys_Add"]  = bloques * 2.5 * multiplicador_stun
            bonos["Abloom_Wind_Add"]  = bloques * 1.4 * multiplicador_stun

    return bonos

def core_nangong_yu(condicion_activa=False, stats_actuales=None, **kwargs):
    """
    Core Nangong Yu:
    - Pasiva: +120 Anomaly Proficiency (Maestría de Anomalía).
    - Escalado: Impacto +1 por cada punto de Anomaly Mastery (Tasa de Anomalía) sobre 110.
    - Activa (Buff de 30s al golpear con Básico o EX): 
      * +35% Anomaly Buildup Rate
      * +20% Daze 
      * +25% DMG para todo el equipo
    - Efecto Abloom (Vibrato Stacks): 
      Al limpiar Vibrato, detona Anomaly DMG adicional.
      Bases: 720% (Ether), 360% (Elec), 900% (Fire), 63% (Phys), 90% (Ice).
      Cada stack de Vibrato suma un 25% extra a este ratio.
    """
    bonos = {}
    
    bonos[KEYS["ANOMALY_PROF"]] = 120.0
    
    if stats_actuales:
        mastery = stats_actuales.get(KEYS["ANOMALY_MASTERY"], 0.0)
        if mastery > 110.0:
            bonos["Impacto"] = mastery - 110.0
            
    if condicion_activa:
        bonos[KEYS["ANOMALY_BUILDUP"]] = 35.0
        bonos[KEYS["DAZE"]] = 20.0
        bonos[KEYS["DMG_BONUS"]] = 25.0

        stacks = int(kwargs.get('stacks', 4))
        bono_ratio = 25.0 * stacks
        
        bonos["Abloom_Ether_Add"] = 720.0 + bono_ratio
        bonos["Abloom_Elec_Add"]  = 360.0 + bono_ratio
        bonos["Abloom_Fire_Add"]  = 900.0 + bono_ratio
        bonos["Abloom_Phys_Add"]  = 63.0 + bono_ratio
        bonos["Abloom_Ice_Add"]   = 90.0 + bono_ratio
        bonos["Abloom_Wind_Add"]  = 36.0 + bono_ratio
        
    return bonos

def core_cissia(condicion_activa=False, stats_actuales=None, **kwargs):
    """
    Core Cissia:
    - Activa (Venom): Ignora 6% de la DEF enemiga para daño Eléctrico.
    - Escalado (Venom): +1% DEF ignorada por cada 0.12 de ER sobre 1.4. Máx total 25%.
    - Corrode Bone: Inflige 335% del ATK como daño.
    - Stacks (Personajes Eléctricos): 1 -> +40% Daze (Corrode Bone), 2 -> +60% Daze.
    """
    bonos = {}
    
    bonos["Corrode_Bone_MV"] = 335.0
    
    if condicion_activa:
        def_ignore = 6.0
        
        if stats_actuales:
            er_actual = stats_actuales.get(KEYS["ENERGY_REGEN"], 1.2)
            
            if er_actual > 1.4:
                exceso = er_actual - 1.4
                pasos = int(exceso / 0.12)
                extra_ignore = pasos * 1.0
                def_ignore += extra_ignore
                
        if def_ignore > 25.0:
            def_ignore = 25.0
            
        bonos["Reduccion_DEF_enemigo"] = def_ignore

    stacks_elec = int(kwargs.get('stacks', 2))
    if stacks_elec == 1:
        bonos["Corrode_Bone_Daze_Bonus"] = 40.0
    elif stacks_elec >= 2:
        bonos["Corrode_Bone_Daze_Bonus"] = 60.0

    return bonos

def core_promeia(condicion_activa=False, stats_actuales=None, **kwargs):
    """
    Core Promeia:
    - Pasiva: Si Anomaly Mastery (Tasa de Anomalía) > 150, cada punto extra otorga:
      * +1.5 Anomaly Proficiency (Maestría de Anomalía).
      * +0.35% Bono de Daño Abloom para el equipo.
    - Trial by Cold: Permite detonar Abloom con un ataque EX infligiendo 635% del Daño 
      de Anomalía correspondiente (si hay al menos 1 carga).
    Nota: Las mecánicas dinámicas de Corrosive Chill, Decibelios y Frost Oath 
    se manejan asumiendo que tienes las cargas de Trial by Cold disponibles.
    """
    bonos = {}
    
    if stats_actuales:
        mastery = stats_actuales.get(KEYS["ANOMALY_MASTERY"], 0.0)
        
        if mastery > 150.0:
            exceso = mastery - 150.0
            bonos[KEYS["ANOMALY_PROF"]] = exceso * 1.5
            bonos["Bono_Abloom_DMG"] = exceso * 0.35

    stacks = int(kwargs.get('stacks', 2))
    
    if condicion_activa and stacks >= 1:
        bonos["Abloom_Ether_Add"] = 635.0
        bonos["Abloom_Elec_Add"]  = 635.0
        bonos["Abloom_Fire_Add"]  = 635.0
        bonos["Abloom_Phys_Add"]  = 635.0
        bonos["Abloom_Ice_Add"]   = 635.0
        bonos["Abloom_Wind_Add"]  = 635.0

    return bonos

def core_starlight_billy(condicion_activa=False, stats_actuales=None, nombre_habilidad="", **kwargs):
    """
    Core Starlight - Billy:

    1. PASIVA — Sheer Force escalada por HP Máximo:
       Gana Sheer Force adicional igual a (HP Máximo × 0.1).
       Todo el daño Físico de Starlight - Billy es Daño Sheer:
         - Ignora la DEF enemiga.
         - Usa Sheer Force como multiplicador de daño (en lugar de ATK).

    2. PASIVA — Adrenalina al entrar en combate:
       Restaura 60 de Adrenalina al entrar al campo.
       En Modo Zona de Investigación, este efecto solo puede activarse cada 180s.
       (Informativo; no afecta bonos de daño directamente.)

    3. ACTIVA — Special Attack: Drive Suppression (condicion_activa):
       Se activa al consumir HP (solo si HP > 25%).
       Cada uso aumenta el CRIT DMG en 90% durante 45s (renovable).
       Cuando HP ≤ 25%, reduce el daño recibido en 50% (defensivo, informativo).

    4. PASIVA — Sistema de Determinación (stacks = Determinación actual, máx 120):
       Determinación se gana golpeando enemigos y se regenera lentamente en combate.
       Eventos que restauran Determinación extra:
         - Golpear con EX Special Attack: Cool Wheelie.
         - Activar Chain Attack: Knight's Swagger.
         - Activar un bloqueo.
         - Perfect Dodge (cualquier método): +3 Determinación (1 vez cada 0.5s).
       Con ≥ 100 de Determinación: puede consumir 100 para activar
         Basic Attack: Full-Throttle Starlight (manteniendo el botón de ataque básico).

    5. PASIVA — Restauración de HP:
       - Basic Attack: Knight's Technique: restaura una pequeña cantidad de HP al golpear.
       - Dodge Counter: Duel King (activado por Perfect Dodge): restaura HP al golpear.
       - EX Special Attack: High-Traction Wheels o EX Special Attack: Rocking Footwork: restaura HP.
       (Efectos de curación; informativos en el contexto de cálculo de daño.)
    """
    bonos = {}

    # --- 1. Sheer Force escalada por HP Máximo ---
    if stats_actuales:
        hp_max = stats_actuales.get("Puntos_Vida", 0.0)
        sheer_force_extra = hp_max * 0.1
        bonos["Sheer_Force_Extra"] = sheer_force_extra
        bonos["Tipo_DMG_Fisico"] = "Sheer"  # Indica que el daño ignora DEF

    # --- 3. CRIT DMG de Drive Suppression (condicion_activa = HP consumido / buff activo) ---
    if condicion_activa:
        bonos[KEYS["CRIT_DMG"]] = 90.0
        bonos["Info_Drive_Suppression"] = "HP consumido: +90% CRIT DMG (45s, renovable)"

    # --- 4. Estado de Determinación ---
    determinacion = int(kwargs.get('stacks', 0))
    bonos["Determinacion_Actual"] = determinacion

    if determinacion >= 100:
        bonos["Full_Throttle_Disponible"] = True
        bonos["Info_Full_Throttle"] = "≥100 Determinación: Full-Throttle Starlight disponible"

    return bonos


MAPA_CORE = {
    "Anby": core_anby,
    "Ellen": core_ellen,
    "Evelyn": core_evelyn,
    "Alice": core_alice,
    "Soldier 0 - Anby": core_soldier_0,
    "Anton": core_anton,
    "Ben": core_ben,
    "Banyue": core_banyue,
    "Billy": core_billy,
    "Burnice": core_burnice,
    "Corin": core_corin,
    "Grace": core_grace,
    "Harumasa": core_harumasa,
    "Hugo": core_hugo,
    "Jane": core_jane,
    "Manato": core_manato,
    "Miyabi": core_miyabi,
    "Nekomata": core_nekomata,
    "Piper": core_piper,
    "Soldier 11": core_soldier11,
    "Yanagi": core_yanagi,
    "Yidhari": core_yidhari,
    "Yixuan": core_yixuan,
    "Zhu Yuan": core_zhuyuan,
    "Lucy": core_lucy,
    "Astra Yao": core_astra_yao,
    "Dialyn": core_dialyn,
    "Ju Fufu": core_ju_fufu,
    "Koleda": core_koleda,
    "Caesar": core_caesar,
    "Lighter": core_lighter,
    "Lucia": core_lucia,
    "Lycaon": core_lycaon,
    "Nicole": core_nicole,
    "Orphie & Magus": core_orphie_magus,
    "Pan Yinhu": core_pan_yinhu,
    "Pulchra": core_pulchra,
    "Qingyi": core_qingyi,
    "Rina": core_rina,
    "Seed": core_seed,
    "Seth": core_seth,
    "Soukaku": core_soukaku,
    "Trigger": core_trigger,
    "Vivian": core_vivian,
    "Yuzuha": core_yuzuha,
    "Zhao": core_zhao,
    "Ye Shunguang": core_ye_shunguang,
    "Sunna": core_sunna,
    "Aria": core_aria,
    "Nangong Yu": core_nangong_yu,
    "Cissia": core_cissia,
    "Promeia": core_promeia,
    "Starlight - Billy": core_starlight_billy,
}