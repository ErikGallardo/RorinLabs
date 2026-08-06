from traductor import traductor_global as i18n

def _verificar_activacion(datos_equipo, req_rol=None, req_elemento=None, req_faccion=None):
    if not datos_equipo:
        return False
        
    roles = datos_equipo.get("roles", [])
    elementos = datos_equipo.get("elementos", [])
    facciones = datos_equipo.get("facciones", [])

    if req_rol:
        for r in roles:
            for valido in req_rol:
                if valido in r.lower():
                    return True
                    
    if req_elemento:
        for e in elementos:
            for valido in req_elemento:
                if valido in e.lower():
                    return True
                    
    if req_faccion:
        for f in facciones:
            for valido in req_faccion:
                if valido in f.lower():
                    return True
                
    return False

def soporte_astra_yao(resultados, **kwargs):
    stats = kwargs.get('stats', {})
    atk_soporte = stats.get("Ataque", 0.0)
    mindscape = kwargs.get('mindscape', 0)
    crit_dmg_total = 25.0
    dmg = 20.0
    ratio = 0.35
    tope = 1200.0
    msg_m2 = ""

    if mindscape >= 2:
        ratio += 0.19
        tope += 400.0
        crit_dmg_total += 3.0
        dmg += 2.0
        msg_m2 = " (M2)"
    
    if mindscape >= 5:
        crit_dmg_total += 3.0
        dmg += 2.0

    buff_calculado = atk_soporte * ratio
    if buff_calculado > tope:
        buff_calculado = tope
        
    resultados["Ataque"] = resultados.get("Ataque", 0.0) + buff_calculado
    resultados["Daño_crítico"] = resultados.get("Daño_crítico", 0.0) + crit_dmg_total
    resultados["Daño_Adicional"] = resultados.get("Daño_Adicional", 0.0) + dmg

    atk_requerido = tope / ratio

    return i18n.t("soportes.astra_yao", 
        default="Astra Yao{m2}: Buff de ATK +{atk:.0f} ({pct:.0f}% de {atk_sop:.0f}, Max {tope:.0f}), Crit Dmg +{cd}% y Buff de DMG +{dmg}% (se requiere {req:.0f} de atk para el buff completo)",
        m2=msg_m2, atk=buff_calculado, pct=ratio*100, atk_sop=atk_soporte, tope=tope, cd=crit_dmg_total, dmg=dmg, req=atk_requerido)

def soporte_burnice(resultados, **kwargs):
    datos_equipo = kwargs.get('datos_equipo')
    activado = _verificar_activacion(datos_equipo, req_rol=["anomalia"], req_faccion=["hijos de calidón"])
    
    if activado:
        resultados["Bono_Acumulación"] = resultados.get("Bono_Acumulación", 0.0) + 65.0
        return i18n.t("soportes.burnice_activo", default="+65% Buildup & +3s Burn")
        
    return i18n.t("soportes.burnice_inactivo", default="Burnice: Aumento de la acumulación de anomalía.")

def soporte_caesar(resultados, **kwargs):
    resultados["Ataque"] = resultados.get("Ataque", 0.0) + 1000.0
    excepciones_evasivas = ["astra yao", "zhu yuan", "grace", "rina", "pulchra", "billy"]
    datos_equipo = kwargs.get('datos_equipo')
    req_faccion = ["hijos de calidón"]
    activado = True 

    if datos_equipo:
        facciones = datos_equipo.get("facciones", [])
        nombres = datos_equipo.get("nombres", [])
        
        for f in facciones:
            if any(valido in f for valido in req_faccion):
                activado = True
                break

        if not activado:
            for nombre in nombres:
                n_norm = str(nombre).lower().strip()
                es_evasivo = any(exc in n_norm for exc in excepciones_evasivas)             
                if not es_evasivo:
                    activado = True
                    break

    if activado:
        resultados["Daño_Adicional"] = resultados.get("Daño_Adicional", 0.0) + 25.0
        return i18n.t("soportes.caesar_activo", default="Caesar: Buff de ATK +1000, y un incremento de DMG +25% luego de un apoyo defensivo.")
    
    return i18n.t("soportes.caesar_inactivo", default="ATK +1000")

def soporte_dialyn(resultados, **kwargs):
    resultados["Stun_DMG_Multiplier"] = resultados.get("Stun_DMG_Multiplier", 0.0) + 30.0
    return i18n.t("soportes.dialyn", default="Dialyn: El bono de Stun aumenta en un 30%.")

def soporte_ju_fufu(resultados, **kwargs):
    stats = kwargs.get('stats', {})
    atk_soporte = stats.get("Ataque", 0.0)
    
    crit_dmg_total = 20.0
    if atk_soporte >= 2800.0:
        exceso = atk_soporte - 2800.0
        pasos = int(exceso // 100)
        extra = pasos * 5.0
        if extra > 30.0: extra = 30.0
        crit_dmg_total += extra

    resultados["Daño_crítico"] = resultados.get("Daño_crítico", 0.0) + crit_dmg_total
    resultados["Daño_Adicional"] = resultados.get("Daño_Adicional", 0.0) + 40.0
    
    return i18n.t("soportes.ju_fufu", default="Ju Fufu: Buff de Crit DMG +{cd:.1f}% (se requiere 3400 de atk para el buff completo), DMG +40%", cd=crit_dmg_total)

def soporte_lighter(resultados, **kwargs):
    stats = kwargs.get('stats', {})
    datos_equipo = kwargs.get('datos_equipo')
    elemento_dps = str(kwargs.get('elemento_dps', '')).lower()

    resultados["Resistencia_Hielo"] = resultados.get("Resistencia_Hielo", 0.0) - 15.0
    resultados["Resistencia_Fuego"] = resultados.get("Resistencia_Fuego", 0.0) - 15.0

    msg = i18n.t("soportes.lighter_base", default="RES Hielo/Fuego -15%")
    activado = _verificar_activacion(datos_equipo, req_rol=["atacante"], req_faccion=["hijos de calidon"])
    es_fuego_hielo = elemento_dps in ["fuego", "hielo"]
   
    if activado and es_fuego_hielo:
        impacto = stats.get("Impacto", 0.0)
        base_stack = 1.25
        extra_stack = 0.0

        if impacto > 170:
            exceso = impacto - 170
            pasos = int(exceso / 10)
            extra_stack = pasos * 0.25
           
        valor_por_stack = base_stack + extra_stack
        total_buff = valor_por_stack * 20.0

        if total_buff > 75.0:
            total_buff = 75.0

        resultados["Daño_elemental"] = resultados.get("Daño_elemental", 0.0) + total_buff
        msg += i18n.t("soportes.lighter_extra", default=", Lighter: Buff de +{tb:.1f}% DMG de Hielo y Fuego (Imp: {imp:.0f} se requieren 270 de impacto para el buff completo)", tb=total_buff, imp=impacto)

    return msg

def soporte_lucia(resultados, **kwargs):
    resultados["Puntos_Vida_%"] = resultados.get("Puntos_Vida_%", 0.0) + 5.0
    resultados["Daño_Adicional"] = resultados.get("Daño_Adicional", 0.0) + 20.0
    
    stats = kwargs.get('stats', {})
    hp_soporte = stats.get("Puntos_de_Vida", stats.get("Puntos_Vida", 0.0))
    datos_equipo = kwargs.get('datos_equipo')
    
    hp_calculo = 24000.0 if hp_soporte > 24000.0 else hp_soporte
    base_sheer = 12.0
    bloques = int(hp_calculo / 200)
    extra_sheer = bloques * 7.4
    
    val_sheer_potencial = base_sheer + extra_sheer
    if val_sheer_potencial > 900.0: val_sheer_potencial = 900.0
    
    req_rol = ["ruptura", "aturdidor"]
    activado = False

    if datos_equipo:
        roles = datos_equipo.get("roles", [])
        for r in roles:
            if any(valido in str(r).lower() for valido in req_rol):
                activado = True
                break
    
    valor_a_aplicar = 0.0
    if activado:
        valor_a_aplicar = val_sheer_potencial
        msg_estado = i18n.t("soportes.estado_activo", default="(Activo)")
    else:
        msg_estado = i18n.t("soportes.estado_inactivo", default="(INACTIVO: Potencial {val:.0f})", val=val_sheer_potencial)
    
    resultados["Sheer_force"] = resultados.get("Sheer_force", 0.0) + valor_a_aplicar
    
    return i18n.t("soportes.lucia", default="Lucía: Buff de HP +5%, DMG +20% y un aumento del Sheer Force en +{va:.0f} {est} (HP: {hp:.0f} se requiere 24,000 de hp para el buff completo)", va=valor_a_aplicar, est=msg_estado, hp=hp_soporte)

def soporte_lucy(resultados, **kwargs):
    stats = kwargs.get('stats', {})
    atk_soporte = stats.get("Ataque", 0.0)
    buff_atk = atk_soporte * 0.226
    if buff_atk > 600: buff_atk = 600
    
    resultados["Ataque"] = resultados.get("Ataque", 0.0) + buff_atk
    return i18n.t("soportes.lucy", default="Lucy: Buff de ATK +{atk:.0f} (Considerando ex al nivel 12, se requiere 2653 de atk para el buff completo)", atk=buff_atk)

def soporte_lycaon(resultados, **kwargs):
    datos_equipo = kwargs.get('datos_equipo')
    activado = _verificar_activacion(datos_equipo, req_elemento=["hielo"], req_faccion=["servicios domésticos victoria"])
    
    resultados["Resistencia_Hielo"] = resultados.get("Resistencia_Hielo", 0.0) - 25.0
    msg = i18n.t("soportes.lycaon_base", default="RES Hielo -25%")
    
    if activado:
        resultados["Stun_DMG_Multiplier"] = resultados.get("Stun_DMG_Multiplier", 0.0) + 35.0
        msg += i18n.t("soportes.lycaon_extra", default=", Lycaon: Aumenta el Bono de stun en +35%")

    return msg

def soporte_nicole(resultados, **kwargs):
    datos_equipo = kwargs.get('datos_equipo')
    elemento_dps = str(kwargs.get('elemento_dps', '')).lower()
    
    resultados["Reduccion_DEF_enemigo"] = resultados.get("Reduccion_DEF_enemigo", 0.0) + 40.0
    msg = i18n.t("soportes.nicole_base", default="Nicole: Reducción de DEF en 40%")
    
    activado = _verificar_activacion(datos_equipo, req_elemento=["etereo"], req_faccion=["liebres astutas"])
    
    if activado and ("etereo" in elemento_dps or "ether" in elemento_dps):
        resultados["Daño_elemental"] = resultados.get("Daño_elemental", 0.0) + 25.0
        msg += i18n.t("soportes.nicole_extra", default=" y aumento de +25% DMG en daño etereo.")
        
    return msg

def soporte_orphie_magus(resultados, **kwargs):
    stats = kwargs.get('stats', {})
    er_soporte = stats.get("Recuperación_energía", 1.56)
    buff_atk = 280.0
    shred_total = 25.0
    if er_soporte >= 1.6:
        exceso = er_soporte - 1.6
        pasos = int((exceso + 0.0001) / 0.1) 
        extra = pasos * 20.0
        buff_atk += extra

    if buff_atk > 700.0:
        buff_atk = 700.0
        
    resultados["Ataque"] = resultados.get("Ataque", 0.0) + buff_atk
    resultados["Reduccion_DEF_enemigo"] = resultados.get("Reduccion_DEF_enemigo", 0.0) + shred_total
    return i18n.t("soportes.orphie", default="Orpheus: Buff de ATK +{atk:.0f} (depende de la ER: {er:.2f}), se requieren 3.7% de recuperación de energía para el buff completo", atk=buff_atk, er=er_soporte)

def soporte_pan_yinhu(resultados, **kwargs):
    stats = kwargs.get('stats', {})
    atk_soporte = stats.get("Ataque", 0.0)
    mindscape = kwargs.get('mindscape', 0)
    datos_equipo = kwargs.get('datos_equipo')
    
    ratio = 0.18
    tope = 540.0
    msg_m6 = ""

    if mindscape >= 6:
        ratio = 0.24
        tope = 720.0
        msg_m6 = " (M6)"
        
    buff_calculado = atk_soporte * ratio
    if buff_calculado > tope:
        buff_calculado = tope
        
    resultados["Sheer_force"] = resultados.get("Sheer_force", 0.0) + buff_calculado
    
    activado = _verificar_activacion(datos_equipo, req_rol=["ruptura"], req_faccion=["yunkui"])
    atk_requerido = tope / ratio
    
    extra_dmg = ""
    if activado:
        if kwargs.get("debuff_qi_activo", True): 
            resultados["Daño_Adicional"] = resultados.get("Daño_Adicional", 0.0) + 20.0
            extra_dmg = ", +20% DMG"

    return i18n.t("soportes.pan", default="Pan Yinhu{m6}: Buff de Sheer Force +{buff:.0f} (Max {tope:.0f}), se requiere {req:.0f} de atk para el buff completo{ext}", m6=msg_m6, buff=buff_calculado, tope=tope, req=atk_requerido, ext=extra_dmg)

def soporte_piper(resultados, **kwargs):
    datos_equipo = kwargs.get('datos_equipo')
    activado = _verificar_activacion(datos_equipo, req_elemento=["fisico"], req_faccion=["hijos de calidón"])
    
    if activado:
        resultados["Daño_Adicional"] = resultados.get("Daño_Adicional", 0.0) + 18.0
    return i18n.t("soportes.piper", default="Piper: Aumenta el DMG en un 18%.")

def soporte_qingyi(resultados, **kwargs):
    resultados["Stun_DMG_Multiplier"] = resultados.get("Stun_DMG_Multiplier", 0.0) + 80.0
    return i18n.t("soportes.qingyi", default="Qingyi: Aumenta el multiplicador de Stun en +80% (20 Stacks)")

def soporte_rina(resultados, **kwargs):
    stats = kwargs.get('stats', {})
    datos_equipo = kwargs.get('datos_equipo')
    elemento_dps = str(kwargs.get('elemento_dps', '')).lower()
    
    mindscape_raw = kwargs.get('mindscape', 0)
    mindscape = 0
    if isinstance(mindscape_raw, (int, float)):
        mindscape = int(mindscape_raw)
    else:
        digitos = ''.join(filter(str.isdigit, str(mindscape_raw)))
        if digitos: mindscape = int(digitos)
            
    pen_soporte = stats.get("Tasa_de_Perforación", 0.0)
    bono_base = (pen_soporte * 0.25) + 12.0
    if bono_base > 30.0: bono_base = 30.0
        
    msg_m1 = ""
    bono_final = bono_base
    
    if mindscape >= 1:
        bono_final = bono_base * 1.30
        msg_m1 = " (M1)"
        
    resultados["Tasa_de_Perforación"] = resultados.get("Tasa_de_Perforación", 0.0) + bono_final
    
    activado = _verificar_activacion(datos_equipo, req_elemento=["electrico"], req_faccion=["servicios domésticos victoria"])
    en_shock = kwargs.get("enemigo_shocked", True)
    
    extra = ""
    if activado and en_shock and ("electrico" in elemento_dps or "eléctrico" in elemento_dps):
        resultados["Daño_elemental"] = resultados.get("Daño_elemental", 0.0) + 10.0
        extra = i18n.t("soportes.rina_extra", default=", aumento del daño eléctrico en +10%")
        
    return i18n.t("soportes.rina", default="Rina{m1}: Aumento de la perforación +{bono:.1f}%, se requieren 72% de perforación para el buff completo{ext}", m1=msg_m1, bono=bono_final, ext=extra)

def soporte_seed(resultados, **kwargs):
    resultados["Ataque"] = resultados.get("Ataque", 0.0) + 1000.0
    resultados["Daño_crítico"] = resultados.get("Daño_crítico", 0.0) + 30.0
    resultados["Daño_Adicional"] = resultados.get("Daño_Adicional", 0.0) + 25.0
    return i18n.t("soportes.seed", default="Seed: Cuando Seed es subdps otorga un buff de ATK +1000, Crit dmg +30% y buff de DMG +25%")

def soporte_seth(resultados, **kwargs):
    datos_equipo = kwargs.get('datos_equipo')
    resultados["Maestría_Anomalía"] = resultados.get("Maestría_Anomalía", 0.0) + 100.0
    msg = i18n.t("soportes.seth_base", default="Seth: Buff de Maestría de anomalía +100")
    
    activado = _verificar_activacion(datos_equipo, req_elemento=["electrico"], req_faccion=["n.e.p.s.", "r.o.v.e.r."])
    
    if activado and kwargs.get("debuff_seth_activo", True):
        resultados["Red_Res_Buildup"] = 20.0
        msg += i18n.t("soportes.seth_extra", default=", -20% Reducción de resistencia de anomalía")
        
    return msg

def soporte_soukaku(resultados, **kwargs):
    stats = kwargs.get('stats', {})
    datos_equipo = kwargs.get('datos_equipo')
    elemento_dps = str(kwargs.get('elemento_dps', '')).lower()
    
    atk_soporte = stats.get("Ataque", 0.0)
    buff = atk_soporte * 0.40
    if buff > 1000.0: buff = 1000.0
    resultados["Ataque"] = resultados.get("Ataque", 0.0) + buff
    
    msg = i18n.t("soportes.soukaku_base", default="Soukaku: Buff de ATK +{buff:.0f}, se requiere 2500 de atk para el buff completo", buff=buff)
    
    activado = _verificar_activacion(datos_equipo, req_elemento=["hielo"], req_faccion=["sección 6"])
    
    if activado and ("hielo" in elemento_dps):
        if kwargs.get("buff_soukaku_activo", True):
            resultados["Daño_elemental"] = resultados.get("Daño_elemental", 0.0) + 20.0
            msg += i18n.t("soportes.soukaku_extra", default=", aumento de +20% en daño elemental de hielo")
            
    return msg

def soporte_trigger(resultados, **kwargs):
    resultados["Unstun_DMG_Multiplier"] = resultados.get("Unstun_DMG_Multiplier", 0.0) + 35.0
    return i18n.t("soportes.trigger", default="Trigger: Aplica un debuff de 35% de stun aunque el enemigo no esté aturdido")

def soporte_vivian(resultados, **kwargs):
    stats = kwargs.get('stats', {})
    datos_equipo = kwargs.get('datos_equipo')
    elemento_dps = str(kwargs.get('elemento_dps', '')).lower()
    
    atk_soporte = stats.get("Ataque", 0.0)
    ap_soporte = stats.get("Maestría_Anomalía", 0.0) + stats.get("Tasa_de_Anomalía", 0.0)
    
    dano_dot = atk_soporte * 0.55
    resultados["Vivian_Prophecy_Tick"] = resultados.get("Vivian_Prophecy_Tick", 0.0) + dano_dot
    
    ratios = {
        "eter": 6.15,   "etereo": 6.15, "ether": 6.15,
        "fuego": 8.00,  "fire": 8.00,
        "electrico": 3.20, "eléctrico": 3.20, "electric": 3.20,
        "hielo": 1.08,  "ice": 1.08,
        "fisico": 0.75, "físico": 0.75, "physical": 0.75
    }
    
    ratio_seleccionado = 0.0
    nombre_elemento = "Desconocido"
    
    for clave, valor in ratios.items():
        if clave in elemento_dps:
            ratio_seleccionado = valor
            nombre_elemento = clave.capitalize()
            break
            
    texto_abloom = ""
    if ratio_seleccionado > 0:
        bloques_ap = ap_soporte / 10.0
        bono_final = bloques_ap * ratio_seleccionado
        resultados["Bono_Abloom_Final"] = resultados.get("Bono_Abloom_Final", 0.0) + bono_final
        texto_abloom = i18n.t("soportes.vivian_abloom", default=", Abloom ({elem}) +{bono:.2f}%", elem=nombre_elemento, bono=bono_final)
    else:
        texto_abloom = i18n.t("soportes.vivian_no_elem", default=", Abloom (Sin Elemento)")

    activado = _verificar_activacion(datos_equipo, req_rol=["anomalia"])
    if activado and "etereo" in elemento_dps:
        resultados["Bono_Daño_Anomalia"] = resultados.get("Bono_Daño_Anomalia", 0.0) + 12.0
        texto_abloom += i18n.t("soportes.vivian_corr", default=", +12% Corruption")

    return i18n.t("soportes.vivian_base", default="Prophecy {dot:.0f}{txt}", dot=dano_dot, txt=texto_abloom)

def soporte_yuzuha(resultados, **kwargs):
    stats = kwargs.get('stats', {})
    atk_soporte = stats.get("Ataque", 0.0)
    buff_atk = atk_soporte * 0.40
    if buff_atk > 1200.0: buff_atk = 1200.0
        
    resultados["Ataque"] = resultados.get("Ataque", 0.0) + buff_atk
    resultados["Daño_Adicional"] = resultados.get("Daño_Adicional", 0.0) + 15.0
    
    return i18n.t("soportes.yuzuha", default="Yuzuha: aumento del ATK +{atk:.0f}, se requiere 3000 de atk para el buff completo, aumento del DMG +15%", atk=buff_atk)

def soporte_zhao(resultados, **kwargs):
    resultados["Ataque"] = resultados.get("Ataque", 0.0) + 1000.0
    resultados["Puntos_Vida_%"] = resultados.get("Puntos_Vida_%", 0.0) + 5.0

    stats = kwargs.get('stats', {})
    hp_max = stats.get("Puntos_de_Vida", 0.0)
    
    base_bonus = 10.0
    extra_bonus = 0.0
    if hp_max > 15000:
        exceso = hp_max - 15000
        stacks = int(exceso / 400)
        extra_bonus = stacks * 1.0
        
    total_bonus = base_bonus + extra_bonus
    if total_bonus > 40.0: total_bonus = 40.0
    
    resultados["Daño_Adicional"] = resultados.get("Daño_Adicional", 0.0) + total_bonus
    
    return i18n.t("soportes.zhao", default="Zhao: Cuando se aplica velo etereo se aumenta el ATK +1000, los HP +5% y el DMG +{tot:.1f}%, se requieren 27,000 de h para el buff completo", tot=total_bonus)

def soporte_sunna(resultados, **kwargs):
    stats = kwargs.get('stats', {})
    atk_soporte = stats.get("Ataque", 0.0)
    ratio = 0.30 
    buff_atk = atk_soporte * ratio
    
    if buff_atk > 1050.0: buff_atk = 1050.0
    resultados["Ataque"] = resultados.get("Ataque", 0.0) + buff_atk

    tipo_dps = str(kwargs.get('tipo_agente', '')).lower()
    msg_extra = ""
    
    if "atacante" in tipo_dps or "attack" in tipo_dps:
        resultados["Sunna_Cats_Gaze_Atacante"] = 300.0
        msg_extra = i18n.t("soportes.sunna_ata", default=", Cat's Gaze (Atacante): +300% ATK DMG.")
        
    elif "anomalia" in tipo_dps or "anomalía" in tipo_dps or "anomaly" in tipo_dps:
        resultados["Sunna_Cats_Gaze_Anomalia"] = 480.0
        resultados["Sunna_Cats_Gaze_CDMG_Extra"] = 150.0 
        msg_extra = i18n.t("soportes.sunna_anom", default=", Cat's Gaze (Anomalía): +480% ATK DMG (Crit 100%, +150% CDMG).")
        
    return i18n.t("soportes.sunna_base", default="Sunna: Buff de ATK +{atk:.0f}{ext} (se requiere 3500 de atk para el buff completo)", atk=buff_atk, ext=msg_extra)

def soporte_nangong_yu(resultados, **kwargs):
    resultados["Daño_Adicional"] = resultados.get("Daño_Adicional", 0.0) + 25.0
    
    resultados["Stun_DMG_Multiplier"] = resultados.get("Stun_DMG_Multiplier", 0.0) + 30.0
    
    datos_equipo = kwargs.get('datos_equipo')
    activado = _verificar_activacion(datos_equipo, req_rol=["anomalia"], req_faccion=["ángeles de la delusión", "angeles de la delusion"])
    
    msg_extra = ""
    if activado:
        resultados["Bono_Acumulación"] = resultados.get("Bono_Acumulación", 0.0) + 30.0
        msg_extra = i18n.t("soportes.nangong_extra", default=", +30% Anomaly Buildup (vs Stunned)")

    return i18n.t("soportes.nangong_base", default="Nangong Yu: DMG +25%, Stun DMG Mult. +30%{ext}", ext=msg_extra)

MAPA_SOPORTES_AGENTES = {
    "astra yao": soporte_astra_yao, "burnice": soporte_burnice, "caesar": soporte_caesar,
    "dialyn": soporte_dialyn, "ju fufu": soporte_ju_fufu, "lighter": soporte_lighter,
    "lucia": soporte_lucia, "lucy": soporte_lucy, "lycaon": soporte_lycaon,
    "nicole": soporte_nicole, "orphie & magus": soporte_orphie_magus, "pan yinhu": soporte_pan_yinhu,
    "piper": soporte_piper, "qingyi": soporte_qingyi, "rina": soporte_rina,
    "seed": soporte_seed, "seth": soporte_seth, "soukaku": soporte_soukaku,
    "trigger": soporte_trigger, "vivian": soporte_vivian, "yuzuha": soporte_yuzuha,
    "zhao": soporte_zhao, "sunna": soporte_sunna, "nangong yu": soporte_nangong_yu,
}

###======================
# --- SETS DE SOPORTE ---
###======================

def set_swing_jazz(resultados, **kwargs):
    resultados["Daño_Adicional"] = resultados.get("Daño_Adicional", 0.0) + 15.0
    return i18n.t("sets_sup.jazz", default="Set 4pc: Jazz oscilante = Daño +15%")

def set_proto_punk(resultados, **kwargs):
    resultados["Daño_Adicional"] = resultados.get("Daño_Adicional", 0.0) + 15.0
    return i18n.t("sets_sup.punk", default="Set 4pc: Proto Punk activo = Daño +15%")

def set_astral_voice(resultados, **kwargs):
    stacks = int(kwargs.get("stacks_set", 3))
    if stacks >= 6:
        bono = 24.0
    elif stacks >= 3:
        bono = 16.0
    elif stacks >= 1:
        bono = 8.0
    else:
        bono = 0.0
    if bono > 0:
        resultados["Daño_Adicional"] = resultados.get("Daño_Adicional", 0.0) + bono
    return i18n.t("sets_sup.astral", default=f"Set 4pc: Voz Astral ({stacks} Cargas) = Daño +{bono:.0f}%")

def set_king_of_summit(resultados, **kwargs):
    tipo = kwargs.get("tipo_agente", "").lower()
    if "aturdidor" in tipo:
        stacks = int(kwargs.get("stacks_set", 2))
        stacks = max(0, min(stacks, 15))
        bono = (stacks / 15) * 30.0
        if bono > 0:
            resultados["Daño_crítico"] = resultados.get("Daño_crítico", 0.0) + bono
        return i18n.t("sets_sup.summit", default=f"Set 4pc: Monarca del Pináculo ({stacks} Cargas) = Crit DMG +{bono:.1f}%")
    return None

def set_moonlight_lullaby(resultados, **kwargs):
    tipo = kwargs.get("tipo_agente", "").lower()
    if "soporte" in tipo:
        resultados["Daño_Adicional"] = resultados.get("Daño_Adicional", 0.0) + 18.0
        return i18n.t("sets_sup.moonlight", default="Set 4pc: Nana a la luz Cenicienta = Daño +18%")
    return None

def efecto_Wonderland_Rabbit(resultados, **kwargs):
    tipo = kwargs.get("tipo_agente", "").lower()
    if "defensor" in tipo:
        stacks = int(kwargs.get("stacks_set", 3))
        stacks = max(0, min(stacks, 6))
        bono = stacks * 3.0
        if bono > 0:
            resultados["Daño_Adicional"] = resultados.get("Daño_Adicional", 0.0) + bono
        return i18n.t("sets_sup.rabbit", default=f"Set 4pc: Conejo en el país de las maravillas ({stacks} Cargas) = Daño +{bono:.0f}%")

MAPA_SOPORTES_SETS = {
    "jazz oscilante": set_swing_jazz, "proto punk": set_proto_punk, "voz astral": set_astral_voice,
    "monarca del pinaculo": set_king_of_summit, "nana a la luz cenicienta": set_moonlight_lullaby,
    "conejo en el pais de las maravillas": efecto_Wonderland_Rabbit,
}

###=========================
# --- W-Engines Soporte ---
###=========================

def wengine_Kaboom_the_Cannon(resultados, **kwargs):
    try: ref = int(kwargs.get('refinamiento', 1))
    except: ref = 1
    try: stacks = int(kwargs.get('stacks', 0))
    except: stacks = 0
    
    valores_base = [2.5, 2.8, 3.2, 3.6, 4.0]
    idx = max(0, min(ref - 1, 4))
    buff_total = valores_base[idx] * 4 if stacks > 0 else 0
    resultados["Ataque_%"] = resultados.get("Ataque_%", 0.0) + buff_total
    return i18n.t("wengines_sup.kaboom", default="Kaboom the Cannon: Buff de ATK +{b:.1f}% (4 Stacks)", b=buff_total)

def wengine_unfettered_game_ball(resultados, **kwargs):
    try: ref = int(kwargs.get('refinamiento', 1))
    except: ref = 1
    valores = [12.0, 13.5, 15.5, 17.5, 20.0]
    idx = max(0, min(ref - 1, 4))
    buff_aplicado = valores[idx]
    resultados["Probabilidad_crítico"] = resultados.get("Probabilidad_crítico", 0.0) + buff_aplicado
    return i18n.t("wengines_sup.unfettered", default="Unfettered Game Ball: Crit Rate +{b:.1f}%", b=buff_aplicado)

def wengine_the_vault(resultados, **kwargs):
    try: ref = int(kwargs.get('refinamiento', 1))
    except: ref = 1
    valores = [15.0, 17.5, 20.0, 22.0, 24.0]
    idx = max(0, min(ref - 1, 4))
    buff_aplicado = valores[idx]
    resultados["Daño_Adicional"] = resultados.get("Daño_Adicional", 0.0) + buff_aplicado
    return i18n.t("wengines_sup.vault", default="The Vault: DMG +{b:.1f}%", b=buff_aplicado)

def wengine_bashful_demon(resultados, **kwargs):
    try: ref = int(kwargs.get('refinamiento', 1))
    except: ref = 1
    try: stacks = int(kwargs.get('stacks', 0))
    except: stacks = 0
    
    valores = [2.0, 2.3, 2.6, 2.9, 3.2]
    idx = max(0, min(ref - 1, 4))
    buff_total = valores[idx] * 4 if min(stacks, 4) > 0 else 0
    
    if buff_total > 0: resultados["Ataque_%"] = resultados.get("Ataque_%", 0.0) + buff_total
    return i18n.t("wengines_sup.bashful", default="Bashful Demon: Buff de ATK +{b:.1f}% (4 Stacks)", b=buff_total)

def wengine_slice_of_time(resultados, **kwargs):
    try: ref = int(kwargs.get('refinamiento', 1))
    except: ref = 1
    idx = max(0, min(ref - 1, 4))
    db_dodge   = [20.0, 23.0, 26.0, 29.0, 32.0]
    db_chain   = [35.0, 40.0, 45.0, 50.0, 55.0]
    energy_gen = [0.7,  0.8,  0.9,  1.0,  1.1]
    return i18n.t("wengines_sup.slice_act", default="Slice of Time: Decibeles +{mn:g}-{mx:g} / Energía +{en:g}", mn=db_dodge[idx], mx=db_chain[idx], en=energy_gen[idx])

def wengine_weeping_cradle(resultados, **kwargs):
    try: ref = int(kwargs.get('refinamiento', 1))
    except: ref = 1
    base_dmg    = [10.0, 12.5, 15.0, 17.5, 20.0]
    max_add_dmg = [10.2, 12.0, 15.0, 18.0, 19.8]
    idx = max(0, min(ref - 1, 4))
    total_buff = base_dmg[idx] + max_add_dmg[idx]
    resultados["Daño_Adicional"] = resultados.get("Daño_Adicional", 0.0) + total_buff
    return i18n.t("wengines_sup.cradle", default="Weeping Cradle: DMG +{b:.1f}% (caso ideal)", b=total_buff)

def wengine_metanukimorphosis(resultados, **kwargs):
    try: ref = int(kwargs.get('refinamiento', 1))
    except: ref = 1
    try: stacks = int(kwargs.get('stacks', 0))
    except: stacks = 0
    
    valores = [60.0, 69.0, 78.0, 87.0, 98.0]
    idx = max(0, min(ref - 1, 4))
    buff_aplicado = valores[idx] if stacks > 0 else 0.0
    
    if stacks > 0: resultados["Maestría_Anomalía"] = resultados.get("Maestría_Anomalía", 0.0) + buff_aplicado
    return i18n.t("wengines_sup.meta", default="Metanukimorphosis: Aumento en la maestría de anomalía en +{b:.0f}", b=buff_aplicado)

def wengine_elegant_vanity(resultados, **kwargs):
    try: ref = int(kwargs.get('refinamiento', 1))
    except: ref = 1
    try: stacks = int(kwargs.get('stacks', 0))
    except: stacks = 0
    valores = [10.0, 11.5, 13.0, 14.5, 16.0]
    idx = max(0, min(ref - 1, 4))
    cargas = min(max(stacks, 0), 2)
    buff_total = valores[idx] * cargas
    if buff_total > 0:
        resultados["Daño_Adicional"] = resultados.get("Daño_Adicional", 0.0) + buff_total
    label = f"{cargas}/2"
    return i18n.t("wengines_sup.elegant", default="Elegant Vanity: DMG +{b:.1f}% ({l} cargas)", b=buff_total, l=label)

def wengine_dreamlit_hearth(resultados, **kwargs):
    try: ref = int(kwargs.get('refinamiento', 1))
    except: ref = 1
    vals_dmg = [25.0, 28.8, 32.5, 36.3, 40.0]
    vals_hp  = [15.0, 17.3, 19.5, 21.8, 24.0]
    idx = max(0, min(ref - 1, 4))
    resultados["Daño_Adicional"] = resultados.get("Daño_Adicional", 0.0) + vals_dmg[idx]
    resultados["Puntos_Vida_%"]  = resultados.get("Puntos_Vida_%",  0.0) + vals_hp[idx]
    return i18n.t("wengines_sup.dreamlit", default="Dreamlit Hearth: DMG +{d:.1f}% / HP +{h:.1f}%", d=vals_dmg[idx], h=vals_hp[idx])

def wengine_reverb_mark_i(resultados, **kwargs):
    try: ref = int(kwargs.get('refinamiento', 1))
    except: ref = 1
    valores = [8.0, 9.0, 10.0, 11.0, 12.0]
    idx = max(0, min(ref - 1, 4))
    buff_aplicado = valores[idx]
    resultados["Impacto"] = resultados.get("Impacto", 0.0) + buff_aplicado
    return i18n.t("wengines_sup.reverb1", default="(Reverb) Mark I: Impacto +{b:.1f}%", b=buff_aplicado)

def wengine_reverb_mark_ii(resultados, **kwargs):
    try: ref = int(kwargs.get('refinamiento', 1))
    except: ref = 1
    valores = [10.0, 12.0, 13.0, 15.0, 16.0]
    idx = max(0, min(ref - 1, 4))
    buff_aplicado = valores[idx]
    resultados["Maestría_Anomalía"] = resultados.get("Maestría_Anomalía", 0.0) + buff_aplicado
    resultados["Tasa_de_Anomalía"]  = resultados.get("Tasa_de_Anomalía",  0.0) + buff_aplicado
    return i18n.t("wengines_sup.reverb2", default="(Reverb) Mark II: Maestría y Tasa Anomalía +{b:.0f}", b=buff_aplicado)

def wengine_reverb_mark_iii(resultados, **kwargs):
    try: ref = int(kwargs.get('refinamiento', 1))
    except: ref = 1
    valores = [8.0, 9.0, 10.0, 11.0, 12.0]
    idx = max(0, min(ref - 1, 4))
    buff_aplicado = valores[idx]
    resultados["Ataque_%"] = resultados.get("Ataque_%", 0.0) + buff_aplicado
    return i18n.t("wengines_sup.reverb3", default="(Reverb) Mark III: ATK +{b:.1f}%", b=buff_aplicado)

def wengine_tusks_of_fury(resultados, **kwargs):
    try: ref = int(kwargs.get('refinamiento', 1))
    except: ref = 1
    try: stacks = int(kwargs.get('stacks', 0))
    except: stacks = 0
    
    vals_dmg = [18.0, 22.5, 27.0, 31.5, 36.0]
    vals_daze = [12.0, 15.0, 18.0, 21.0, 24.0]
    idx = max(0, min(ref - 1, 4))
    
    if stacks > 0:
        resultados["Daño_Adicional"] = resultados.get("Daño_Adicional", 0.0) + vals_dmg[idx]
        resultados["Aturdimiento"] = resultados.get("Aturdimiento", 0.0) + vals_daze[idx]
        return i18n.t("wengines_sup.tusks", default="Tusks of Fury: Buff de DMG +{d:.1f}% / Aumento de Aturdimiento +{a:.1f}%", d=vals_dmg[idx], a=vals_daze[idx])

def wengine_half_sugar_bunny(resultados, **kwargs):
    try: ref = int(kwargs.get('refinamiento', 1))
    except: ref = 1
    try: stacks = int(kwargs.get('stacks', 0))
    except: stacks = 0
    
    vals_stat = [10.0, 11.5, 13.0, 14.5, 16.0]
    vals_cd = [30.0, 34.5, 39.0, 43.5, 48.0]
    idx = max(0, min(ref - 1, 4))
    
    if stacks > 0:
        resultados["Ataque_%"] = resultados.get("Ataque_%", 0.0) + vals_stat[idx]
        resultados["Puntos_Vida_%"] = resultados.get("Puntos_Vida_%", 0.0) + vals_stat[idx]
        resultados["Daño_crítico"] = resultados.get("Daño_crítico", 0.0) + vals_cd[idx]
        return i18n.t("wengines_sup.bunny", default="Half-Sugar Bunny: Aumento del ATK y HP +{s:.1f}% / Aumento de Daño Crítico +{c:.1f}%", s=vals_stat[idx], c=vals_cd[idx])

def wengine_blazing_laurel(resultados, **kwargs):
    try: ref = int(kwargs.get('refinamiento', 1))
    except: ref = 1
    try: stacks_ui = int(kwargs.get('stacks', 0))
    except: stacks_ui = 0

    val_stack = [1.5, 1.72, 1.95, 2.17, 2.4]
    idx = max(0, min(ref - 1, 4))
    buff_total = val_stack[idx] * 20.0
    
    elemento_dps = str(kwargs.get('elemento_dps', '')).lower()
    es_fuego_hielo = elemento_dps in ["fuego", "hielo"]

    if stacks_ui > 0 and es_fuego_hielo:
        resultados["Daño_crítico"] = resultados.get("Daño_crítico", 0.0) + buff_total
        estado = i18n.t("wengines_sup.laurel_act", default="(Activo: 20 Stacks - {el})", el=elemento_dps)
        return i18n.t("wengines_sup.laurel_base", default="Blazing Laurel: Aumento de Crit DMG +{b:.1f}% {est}", b=buff_total, est=estado)
    elif stacks_ui > 0 and not es_fuego_hielo:
        estado = i18n.t("wengines_sup.laurel_inact", default="(Inactivo: DPS es {el}, requiere DPS fuego o hielo)", el=elemento_dps)
        return i18n.t("wengines_sup.laurel_base", default="Blazing Laurel: Aumento de Crit DMG +{b:.1f}% {est}", b=0.0, est=estado)
    
    return i18n.t("wengines_sup.laurel_base", default="Blazing Laurel: Aumento de Crit DMG +{b:.1f}% {est}", b=0.0, est="(Inactivo)")

def wengine_ice_jade_teapot(resultados, **kwargs):
    try: ref = int(kwargs.get('refinamiento', 1))
    except: ref = 1
    try: stacks = int(kwargs.get('stacks', 0))
    except: stacks = 0
    
    vals_imp_stack = [0.7, 0.88, 1.05, 1.22, 1.4]
    vals_team_dmg = [20.0, 23.0, 26.0, 29.0, 32.0]
    idx = max(0, min(ref - 1, 4))
    
    stacks_reales = min(stacks, 30)
    resultados["Impacto"] = resultados.get("Impacto", 0.0) + (vals_imp_stack[idx] * stacks_reales)
    
    if stacks_reales > 0:
        resultados["Daño_Adicional"] = resultados.get("Daño_Adicional", 0.0) + vals_team_dmg[idx]
        return i18n.t("wengines_sup.teapot", default="Ice-Jade Teapot: Aumento del DMG +{b:.1f}% (Full Stacks)", b=vals_team_dmg[idx])

def wengine_roaring_furnace(resultados, **kwargs):
    try: ref = int(kwargs.get('refinamiento', 1))
    except: ref = 1
    try: stacks = int(kwargs.get('stacks', 0))
    except: stacks = 0
    
    vals_dmg = [10.0, 11.5, 13.0, 14.5, 16.0]
    idx = max(0, min(ref - 1, 4))
    buff_total = vals_dmg[idx] * 2 if min(stacks, 2) > 0 else 0
    
    if buff_total > 0:
        resultados["Daño_Adicional"] = resultados.get("Daño_Adicional", 0.0) + buff_total
    return i18n.t("wengines_sup.furnace", default="Roaring Furnace: Buff de DMG +{b:.1f}% (2 Stacks)", b=buff_total)

def wengine_spectral_gaze(resultados, **kwargs):
    try: ref = int(kwargs.get('refinamiento', 1))
    except: ref = 1
    try: stacks = int(kwargs.get('stacks', 0))
    except: stacks = 0
    
    vals_shred = [25.0, 28.75, 32.5, 36.25, 40.0]
    vals_imp_stack = [4.0, 4.6, 5.2, 5.8, 6.4]
    vals_imp_bonus = [8.0, 9.2, 10.4, 11.6, 12.8]
    idx = max(0, min(ref - 1, 4))
    stacks_reales = min(stacks, 3)
    
    if stacks_reales == 0:
        return i18n.t("wengines_sup.spectral_inact", default="Spectral Gaze: (Inactivo)")

    shred_total = vals_shred[idx]
    resultados["Reduccion_DEF_enemigo"] = resultados.get("Reduccion_DEF_enemigo", 0.0) + shred_total
    imp_total = vals_imp_stack[idx] * stacks_reales
    if stacks_reales > 0: imp_total += vals_imp_bonus[idx]
        
    resultados["Impacto"] = resultados.get("Impacto", 0.0) + imp_total
    return i18n.t("wengines_sup.spectral_act", default="Spectral Gaze: Reducción de defensa -{s:.2f}%", s=shred_total)

def wengine_yesterday_calls(resultados, **kwargs):
    try: ref = int(kwargs.get('refinamiento', 1))
    except: ref = 1
    try: stacks = int(kwargs.get('stacks', 0))
    except: stacks = 0
    
    vals_cd = [30.0, 34.5, 39.0, 43.5, 48.0]
    idx = max(0, min(ref - 1, 4))
    buff_total = vals_cd[idx] if min(stacks, 3) > 0 else 0.0
    
    if buff_total > 0: resultados["Daño_crítico"] = resultados.get("Daño_crítico", 0.0) + buff_total
    return i18n.t("wengines_sup.yesterday", default="Yesterday Calls: Daño Crítico aumenta en +{b:.1f}%", b=buff_total)

def wengine_thoughtbop(resultados, **kwargs):
    try: ref = int(kwargs.get('refinamiento', 1))
    except: ref = 1
    try: stacks = int(kwargs.get('stacks', 0))
    except: stacks = 0
    
    vals_dmg = [12.5, 14.3, 16.1, 17.9, 20.0]
    vals_atk = [10.0, 11.5, 13.0, 14.5, 16.0]
    idx = max(0, min(ref - 1, 4))
    
    if stacks > 0:
        buff_dmg = vals_dmg[idx] * 2.0
        buff_atk = vals_atk[idx]
        resultados["Daño_Adicional"] = resultados.get("Daño_Adicional", 0.0) + buff_dmg
        resultados["Ataque_%"] = resultados.get("Ataque_%", 0.0) + buff_atk
        return i18n.t("wengines_sup.thoughtbop_act", default="Thoughtbop: Buff de DMG +{d:.1f}% (Max) / Buff de ATK +{a:.1f}%", d=buff_dmg, a=buff_atk)

    return i18n.t("wengines_sup.thoughtbop_inact", default="Thoughtbop: (Inactivo)")

def wengine_neon_fantasies(resultados, **kwargs):
    try: ref = int(kwargs.get('refinamiento', 1))
    except: ref = 1
    try: stacks = int(kwargs.get('stacks', 0))
    except: stacks = 0
    
    vals_dmg = [15.0, 17.0, 19.5, 21.0, 24.0]
    idx = max(0, min(ref - 1, 4))
    
    stacks_reales = min(max(stacks, 0), 2)
    buff_total = vals_dmg[idx] * stacks_reales
    
    if buff_total > 0:
        resultados["Daño_Adicional"] = resultados.get("Daño_Adicional", 0.0) + buff_total
        return i18n.t("wengines_sup.neon", default="Neon Fantasies: DMG de todo el equipo +{b:.1f}% ({s} Stacks)", b=buff_total, s=stacks_reales)
        
    return i18n.t("wengines_sup.neon_inact", default="Neon Fantasies: (Inactivo)")

def wengine_the_simmering_pot(resultados, **kwargs):
    try: ref = int(kwargs.get('refinamiento', 1))
    except: ref = 1
    try: stacks = int(kwargs.get('stacks', 0))
    except: stacks = 0

    vals_buff = [7.2, 8.2, 9.2, 10.2, 11.5]
    idx = max(0, min(ref - 1, 4))
    
    if stacks > 0:
        buff_aplicado = vals_buff[idx]
        resultados["Aturdimiento"] = resultados.get("Aturdimiento", 0.0) + buff_aplicado
        resultados["Daño_Adicional"] = resultados.get("Daño_Adicional", 0.0) + buff_aplicado
        
        return i18n.t("wengines_sup.simmering_act", default="The Simmering Pot: Aturdimiento +{b:.1f}% / DMG +{b:.1f}%", b=buff_aplicado)

    return i18n.t("wengines_sup.simmering_inact", default="The Simmering Pot: (Inactivo)")

MAPA_SOPORTES_WENGINES = {
    "kaboom the cannon": wengine_Kaboom_the_Cannon, "unfettered game ball": wengine_unfettered_game_ball,
    "the vault": wengine_the_vault, "bashful demon": wengine_bashful_demon,
    "slice of time": wengine_slice_of_time, "weeping cradle": wengine_weeping_cradle,
    "metanukimorphosis": wengine_metanukimorphosis, "elegant vanity": wengine_elegant_vanity,
    "dreamlit hearth": wengine_dreamlit_hearth, "(reverb) mark i": wengine_reverb_mark_i,
    "(reverb) mark ii": wengine_reverb_mark_ii, "(reverb) mark iii": wengine_reverb_mark_iii,
    "tusks of fury": wengine_tusks_of_fury, "half-sugar bunny": wengine_half_sugar_bunny,
    "blazing laurel": wengine_blazing_laurel, "ice-jade teapot": wengine_ice_jade_teapot,
    "roaring fur-nace": wengine_roaring_furnace, "spectral gaze": wengine_spectral_gaze,
    "yesterday calls": wengine_yesterday_calls, "thoughtbop": wengine_thoughtbop,"neon fantasies": wengine_neon_fantasies,
    "the simmering pot": wengine_the_simmering_pot,
}