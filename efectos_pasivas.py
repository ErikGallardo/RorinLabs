from traductor import traductor_global as i18n

def pasiva_alice(roles_equipo=None, stats_actuales=None, **kwargs):
    """
    Pasiva Alice:
    - Condición: Aliado 'Anomalía' o 'Soporte'.
    - Efecto: Si Tasa de Anomalía > 140, el exceso se convierte en Maestría.
    - Ratio: 1.6 AP por cada 1 AM.
    """
    bonos = {}
    roles_validos = ["anomalo", "soporte"]
    
    activado = False
    if roles_equipo:
        for rol in roles_equipo:
            r_norm = str(rol).lower().strip()
            if any(valido in r_norm for valido in roles_validos):
                activado = True
                break
    
    if activado and stats_actuales:
        am_actual = stats_actuales.get("Tasa_de_Anomalía", 0.0)
        
        if am_actual > 140:
            exceso = am_actual - 140
            ap_extra = exceso * 1.6
            bonos["Maestría_Anomalía"] = ap_extra

    return bonos

def pasiva_anby(datos_equipo=None, **kwargs):
    """
    Pasiva Anby (Parallel Connection):
    - Condición: Aliado del mismo Atributo (Eléctrico) o Facción (Cunning Hares).
    - Efecto: Dodge Counter recupera 7.2 Energía extra.
    """
    bonos = {}
    
    req_elemento = ["electrico"]
    req_faccion = ["liebres astutas"]
    
    activado = False
    if datos_equipo:
        elementos = datos_equipo.get("elementos", [])
        facciones = datos_equipo.get("facciones", [])
        
        for e in elementos:
            if any(r in e for r in req_elemento):
                activado = True
                break

        if not activado:
            for f in facciones:
                if any(r in f for r in req_faccion):
                    activado = True
                    break
    
    if activado:
        bonos["Info_Pasiva_Anby"] = "7.2 Energía (Dodge Counter)"

    return bonos

def pasiva_soldier_0_anby(roles_equipo=None, **kwargs):
    """
    Pasiva Soldier 0 - Anby:
    - Condición: Un aliado es 'Aturdidor' (Stun) o 'Auxiliar' (Support).
    - Efecto 1: Crit Rate +10%.
    - Efecto 2: Aftershock DMG +25% (Asumimos activo).
    - Nota: Chain y Ulti cuentan como Aftershock (esto se maneja sumando al bono Aftershock).
    """
    bonos = {}
    roles_validos = ["aturdidor", "soporte"]
    
    activado = False
    if roles_equipo:
        for rol in roles_equipo:
            r_norm = str(rol).lower().strip()
            if any(valido in r_norm for valido in roles_validos):
                activado = True
                break
    
    if activado:
        bonos["Probabilidad_crítico"] = 10.0
        bonos["Daño_Aftershock"] = 25.0 

    return bonos

def pasiva_anton(datos_equipo=None, **kwargs):
    """
    Pasiva Anton (Arm-Drilling Technique):
    - Condición: Aliado del mismo Atributo (Eléctrico) o Facción (Belobog).
    - Efecto: En Modo Explosivo (Burst), cada 4 críticos detona un Shock adicional.
    - Valor: 45% del daño original del golpe.
    """
    bonos = {}
    
    req_elemento = ["electrico"]
    req_faccion = ["construcciones belobog"]
    
    activado = False
    if datos_equipo:
        elementos = datos_equipo.get("elementos", [])
        facciones = datos_equipo.get("facciones", [])

        for e in elementos:
            if any(r in e for r in req_elemento):
                activado = True
                break

        if not activado:
            for f in facciones:
                if any(r in f for r in req_faccion):
                    activado = True
                    break
    
    if activado:
        bonos["Info_Pasiva_Anton"] = "Burst: Proc Shock 45% DMG (cada 4 Crits)"

    return bonos

def pasiva_astra_yao(roles_equipo=None, **kwargs):
    """
    Pasiva Astra Yao:
    - Condición: Aliado 'Atacante', 'Anomalía' o 'Ruptura'.
    - Efecto: Al gastar energía en Assist o Finale, lanza golpes extra (1 Tremolo + 3 Tone Clusters).
    """
    bonos = {}
    
    roles_validos = ["atacante","anomalia", "ruptura"]
    
    activado = False
    if roles_equipo:
        for rol in roles_equipo:
            r_norm = str(rol).lower().strip()
            if any(valido in r_norm for valido in roles_validos):
                activado = True
                break
    
    if activado:
        bonos["Info_Pasiva_Astra"] = "Activo: Extra Tremolo + 3 Clusters (Assist/Finale)"

    return bonos

def pasiva_banyue(roles_equipo=None, **kwargs):
    """
    Pasiva Banyue:
    - Condición: Aliado 'Aturdidor' o 'Soporte'.
    - Efecto: Gana stacks 'Vidyaraja' al usar EX Special en estado Wrath.
    - Max Stacks: 3. Cada uno da 5% Fire DMG.
    - Asumimos 3 stacks activos = +15% Fire DMG.
    """
    bonos = {}
    roles_validos = ["aturdidor", "soporte"]
    
    activado = False
    if roles_equipo:
        for rol in roles_equipo:
            r_norm = str(rol).lower().strip()
            if any(valido in r_norm for valido in roles_validos):
                activado = True
                break
    
    if activado:
        bonos["Daño_elemental"] = 15.0

    return bonos

def pasiva_ben(datos_equipo=None, **kwargs):
    """
    Pasiva Ben (React):
    - Condición: Aliado del mismo Atributo (Fuego) o Facción (Belobog).
    - Efecto: Si tiene Escudo (Core Passive), gana +16% Crit Rate.
    - Asumimos escudo activo para el cálculo.
    """
    bonos = {}
    
    req_elemento = ["fuego"]
    req_faccion = ["construcciones belobog"]
    
    activado = False
    if datos_equipo:
        elementos = datos_equipo.get("elementos", [])
        facciones = datos_equipo.get("facciones", [])

        for e in elementos:
            if any(r in e for r in req_elemento):
                activado = True
                break

        if not activado:
            for f in facciones:
                if any(r in f for r in req_faccion):
                    activado = True
                    break
    
    if activado:
        bonos["Probabilidad_crítico"] = 16.0

    return bonos

def pasiva_billy(datos_equipo=None, **kwargs):
    """
    Pasiva Billy (Roulette):
    - Condición: Aliado Físico o Cunning Hares (Liebres Astutas).
    - Efecto: Tras Chain Attack, la siguiente Ulti gana +50% DMG.
    - Max Stacks: 2 (+100%).
    - Asumimos 1 Stack (+50%) que es el combo estándar (Chain -> Ulti).
    """
    bonos = {}

    req_elemento = ["fisico"]
    req_faccion = ["liebres astutas"]
    
    activado = False
    if datos_equipo:
        elementos = datos_equipo.get("elementos", [])
        facciones = datos_equipo.get("facciones", [])
        
        for e in elementos:
            if any(r in e for r in req_elemento):
                activado = True
                break
        
        if not activado:
            for f in facciones:
                if any(r in f for r in req_faccion):
                    activado = True
                    break
    
    if activado:
        bonos["Bono_Dano_Ulti"] = 50.0

    return bonos

def pasiva_burnice(datos_equipo=None, **kwargs):
    """
    Pasiva Burnice (Fuel to the Fire):
    - Condición: Aliado 'Anomalía' o 'Hijos de Calidón'.
    - Efecto 1: +65% Anomaly Buildup (Acumulación de Anomalía).
    - Efecto 2: Burn Duration +3s (Info).
    """
    bonos = {}
    req_rol = ["anomalia"]
    req_faccion = ["hijos de calidon"]
    
    activado = False
    if datos_equipo:
        roles = datos_equipo.get("roles", [])
        facciones = datos_equipo.get("facciones", [])

        for r in roles:
            if any(valido in r for valido in req_rol):
                activado = True
                break
        
        if not activado:
            for f in facciones:
                if any(valido in f for valido in req_faccion):
                    activado = True
                    break
    
    if activado:
        bonos["Bono_Acumulación"] = 65.0
        bonos["Info_Pasiva_Burnice"] = "Burn Duration +3s"

    return bonos

def pasiva_caesar(datos_equipo=None, **kwargs):
    """
    Pasiva Caesar (Barrier of Resilience):
    - Condición: 
        1. Aliado de 'Hijos de Calidón'.
        2. O Aliado que pueda activar 'Defensive Assist'.
    - Lógica de Defensive Assist:
        La mayoría puede. Solo NO pueden los que usan 'Evasive Assist'.
        Excepciones (Evasive): Astra Yao, Zhu Yuan, Grace, Rina, Pulchra.
        Si el aliado NO está en esa lista, asumimos que hace Parry y activa la pasiva.
    """
    bonos = {}
    excepciones_evasivas = ["astra yao", "zhu yuan", "grace", "rina", "pulchra", "billy"]    
    req_faccion = ["hijos de calidón"]
    
    activado = False
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
        bonos["Daño_Adicional"] = 25.0

    return bonos

def pasiva_corin(datos_equipo=None, **kwargs):
    """
    Pasiva Corin (I-I'm Just Helping!):
    - Condición: Aliado Físico o Victoria Housekeeping (Servicios Domésticos Victoria).
    - Efecto: +35% DMG a enemigos aturdidos.
    """
    bonos = {}
    
    req_elemento = ["fisico"]
    req_faccion = ["servicios domésticos victoria"]
    
    activado = False
    if datos_equipo:
        elementos = datos_equipo.get("elementos", [])
        facciones = datos_equipo.get("facciones", [])

        for e in elementos:
            if any(r in e for r in req_elemento):
                activado = True
                break

        if not activado:
            for f in facciones:
                if any(r in f for r in req_faccion):
                    activado = True
                    break
    
    if activado:
        bonos["Daño_Adicional"] = 35.0

    return bonos

def pasiva_dialyn(datos_equipo=None, **kwargs):
    """
    Pasiva Dialyn (Winning Streak):
    - Condición: Aliado 'Atacante', 'Ruptura' o Misma Facción.
    - Efecto 1: EX Special Crit DMG +50%.
    - Efecto 2: Overwhelmingly Positive (+40% DMG Global). Asumimos activo.
    - Efecto 3: Bonus DMG basado en el rol del aliado (Atacante/Ruptura).
    """
    bonos = {}
    
    req_rol = ["atacante", "ruptura"]
    req_faccion = ["auditoría krampus"] 
    
    activado = False
    tipo_aliado_detectado = []

    if datos_equipo:
        roles = datos_equipo.get("roles", [])
        facciones = datos_equipo.get("facciones", [])

        for r in roles:
            if any(valido in r for valido in req_rol):
                activado = True
                if "atacante" in r or "attack" in r:
                    tipo_aliado_detectado.append("Atacante")
                if "ruptura" in r or "rupture" in r:
                    tipo_aliado_detectado.append("Ruptura")

        if not activado:
            for f in facciones:
                if any(valido in f for valido in req_faccion):
                    activado = True
                    break
    
    if activado:
        bonos["Bono_Crit_DMG_Ex"] = 50.0
        bonos["Daño_Adicional"] = 40.0
        
        info_extra = []
        if "Atacante" in tipo_aliado_detectado:
            info_extra.append("Heavy Atk: +320% ATK (Aliado Atacante)")
        if "Ruptura" in tipo_aliado_detectado:
            info_extra.append("Heavy Atk: +400% Sheer Force (Aliado Ruptura)")
            
        if info_extra:
            bonos["Info_Pasiva_Dialyn"] = " / ".join(info_extra)

    return bonos

def pasiva_ellen(datos_equipo=None, **kwargs):
    """
    Pasiva Ellen (Sharkami):
    - Condición: Aliado 'Aturdidor' (Stun), 'Hielo' (Ice) o 'Victoria Housekeeping'.
    - Efecto: +3% Ice DMG por stack al hacer daño de hielo (Max 10 stacks).
    - Asumimos: 10 Stacks siempre activos (+30% Ice DMG).
    """
    bonos = {}
    
    req_rol = ["aturdidor"]
    req_elemento = ["hielo"]
    req_faccion = ["servicios domésticos victoria"]
    
    activado = False
    
    if datos_equipo:
        roles = datos_equipo.get("roles", [])
        elementos = datos_equipo.get("elementos", [])
        facciones = datos_equipo.get("facciones", [])
        
        for r in roles:
            if any(valido in r for valido in req_rol):
                activado = True
                break

        if not activado:
            for e in elementos:
                if any(valido in e for valido in req_elemento):
                    activado = True
                    break

        if not activado:
            for f in facciones:
                if any(valido in f for valido in req_faccion):
                    activado = True
                    break
    
    if activado:
        bonos["Daño_elemental"] = 30.0

    return bonos

def pasiva_evelyn(datos_equipo=None, stats_actuales=None, **kwargs):
    """
    Pasiva Evelyn (Phantom):
    - Condición: Aliado 'Stun' o 'Support'.
    - Efecto 1: Ulti/Chain DMG +30%.
    - Efecto 2: Si Crit Rate >= 80%, el Multiplicador (MV) de Ulti/Chain aumenta al 125%.
      (Es decir, se multiplica por 1.25).
    """
    bonos = {}
    

    nombre_habilidad = str(kwargs.get("nombre_habilidad", "")).lower()
    es_ulti_chain = any(k in nombre_habilidad for k in ["ultimate", "definitiva", "chain", "cadena"])

    req_rol = ["aturdidor", "soporte"]
    
    activado = False
    if datos_equipo:
        roles = datos_equipo.get("roles", [])
        for r in roles:
            if any(valido in r for valido in req_rol):
                activado = True
                break
    
    if activado:
        bonos["Bono_Dano_Ulti"] = 30.0
        
        if stats_actuales and es_ulti_chain:
            crit_rate = stats_actuales.get("Probabilidad_crítico", 0.0)
            
            if crit_rate >= 80.0:
                mv_actual = stats_actuales.get("Multiplicador_de_ataques", 0.0)
                extra_mv = mv_actual * 0.25
                
                bonos["Multiplicador_de_ataques"] = extra_mv
                bonos["Info_Pasiva_Evelyn"] = "MV x1.25 (Crit >= 80%)"

    return bonos

def pasiva_grace(datos_equipo=None, **kwargs):
    """
    Pasiva Grace (Pre-Driven Needle):
    - Condición: Aliado 'Eléctrico' o 'Belobog'.
    - Efecto: EX Special aumenta el daño del próximo Shock en 18% (Max 2 stacks).
    - Asumimos: 2 Stacks siempre activos (+36% Shock DMG).
    - Implementación: Sumamos a 'Bono_Daño_Anomalia'.
    """
    bonos = {}
    
    req_elemento = ["electrico"]
    req_faccion = ["construcciones belobog"]
    
    activado = False
    
    if datos_equipo:
        elementos = datos_equipo.get("elementos", [])
        facciones = datos_equipo.get("facciones", [])
        
        for e in elementos:
            if any(r in e for r in req_elemento):
                activado = True
                break

        if not activado:
            for f in facciones:
                if any(r in f for r in req_faccion):
                    activado = True
                    break
    
    if activado:
        bonos["Bono_Daño_Anomalia"] = 36.0
        bonos["Info_Pasiva_Grace"] = "Shock DMG +36% (2 Stacks)"

    return bonos

def pasiva_harumasa(datos_equipo=None, **kwargs):
    """
    Pasiva Harumasa:
    - Condición 1 (Equipo): Aliado 'Aturdidor' o 'Anomalía'.
    - Condición 2 (Enemigo): Enemigo Aturdido (Stun_Boss) o bajo Anomalía.
      (En la calculadora, usamos el trigger 'Stun_Boss' para activar esto).
    - Efecto 1: DMG +40%.
    - Efecto 2: Falling Feather aplica 2 stacks de Electro Prison (Info).
    """
    bonos = {}

    estado_enemigo = kwargs.get("estado_enemigo", "Normal")

    req_rol = ["aturdidor", "anomalia"]
    
    equipo_valido = False
    if datos_equipo:
        roles = datos_equipo.get("roles", [])
        for r in roles:
            if any(valido in r for valido in req_rol):
                equipo_valido = True
                break

    if equipo_valido and estado_enemigo == "Stun_Boss":
        bonos["Daño_Adicional"] = 40.0
        bonos["Info_Pasiva_Harumasa"] = "Falling Feather: +2 Stacks Electro Prison"

    return bonos

def pasiva_hugo(datos_equipo=None, **kwargs):
    """
    Pasiva Hugo (Nombre provisional):
    - Condición: Aliado 'Aturdidor' (Stun) o mismo Elemento (Hielo).
    - Efecto 1 (Chain Attack): +15% DMG Base.
    - Efecto 2 (Chain Attack): +40% DMG si activa 'Totalize'. (Asumimos SI).
    - Efecto 3 (Chain Attack): +35% DMG vs Enemigos Normales. (IGNORADO para cálculo de Boss).
    - Total Aplicado a Chain/Ulti: +55% DMG.
    """
    bonos = {}

    nombre_habilidad = str(kwargs.get("nombre_habilidad", "")).lower()
    
    es_chain = any(k in nombre_habilidad for k in ["chain", "cadena", "ultimate", "definitiva"])
    
    req_rol = ["aturdidor"]
    req_elemento = ["hielo"]
    
    activado = False
    
    if datos_equipo:
        roles = datos_equipo.get("roles", [])
        elementos = datos_equipo.get("elementos", [])
        
        for r in roles:
            if any(valido in r for valido in req_rol):
                activado = True
                break

        if not activado:
            for e in elementos:
                if any(valido in e for valido in req_elemento):
                    activado = True
                    break
    
    if activado:
        if es_chain:
            bonos["Bono_Dano_Ulti"] = 55.0
            bonos["Info_Pasiva_Hugo"] = "Totalize Activo (+40%). (Bono vs Mobs excluido)"
        else:
            bonos["Info_Pasiva_Hugo"] = "Pasiva Activa (Aplica a Chain Attack)"

    return bonos

def pasiva_jane(datos_equipo=None, **kwargs):
    """
    Pasiva Jane (Passion Stream):
    - Condición Equipo: Aliado 'Anomalía' o misma Facción (N.E.P.S. / Criminal Investigation).
    - Efecto 1: +15% Anomaly Buildup Rate (Base).
    - Efecto 2: +15% Adicional si el enemigo sufre Anomalía.
    - Implementación: 
        - Siempre damos el +15% si hay equipo.
        - Si 'estado_enemigo' es 'Stun_Boss', sumamos el otro +15% (Total 30%).
    """
    bonos = {}
    
    estado_enemigo = kwargs.get("estado_enemigo", "Normal")
    req_rol = ["anomalia"]
    req_faccion = ["n.e.p.s.", "m_o_d_"]
    
    activado = False
    if datos_equipo:
        roles = datos_equipo.get("roles", [])
        facciones = datos_equipo.get("facciones", [])
        
        for r in roles:
            if any(valido in r for valido in req_rol):
                activado = True
                break
        
        if not activado:
            for f in facciones:
                if any(valido in f for valido in req_faccion):
                    activado = True
                    break
    
    if activado:
        buildup_total = 15.0
        
        if estado_enemigo == "Stun_Boss":
            buildup_total += 15.0
            bonos["Info_Pasiva_Jane"] = "+30% Buildup (Enemy Debuffed)"
        else:
            bonos["Info_Pasiva_Jane"] = "+15% Buildup (Base)"
            
        bonos["Bono_Acumulación"] = buildup_total

    return bonos

def pasiva_Jufufu(datos_equipo=None, **kwargs):
    """
    Pasiva Jufufu:
    - Condición: Aliado 'Atacante' (Attack) o 'Ruptura' (Rupture).
    - Efecto 1: Max Decibeles +1000 (Capacidad de Ulti aumentada).
    - Efecto 2: Recupera 300 Decibeles al usar Ulti (Refund).
    - Implementación: Texto informativo (No afecta el daño por screenshot).
    """
    bonos = {}
    
    req_rol = ["atacante", "ruptura"]
    
    activado = False
    if datos_equipo:
        roles = datos_equipo.get("roles", [])
        for r in roles:
            if any(valido in r for valido in req_rol):
                activado = True
                break
    
    if activado:
        bonos["Info_Pasiva_Kouk"] = "Max Decibeles +1000 / Refund Ulti 300"

    return bonos

def pasiva_koleda(datos_equipo=None, **kwargs):
    """
    Pasiva Koleda (Fuel-Consuming Swing):
    - Condición 1 (Equipo): Aliado 'Fuego', 'Belobog' o 'Ruptura'.
    - Condición 2 (Estado): El enemigo DEBE estar Aturdido (Stun_Boss).
    - Condición 3 (Habilidad): Solo aplica a 'Chain Attack' (Ataque en Cadena).
    - Efecto: Chain Attacks deal +35% DMG (Max 2 stacks = +70%).
    """
    bonos = {}
    
    estado_enemigo = kwargs.get("estado_enemigo", "Normal")
    nombre_habilidad = str(kwargs.get("nombre_habilidad", "")).lower()
    es_chain = any(k in nombre_habilidad for k in ["chain", "cadena", "ultimate", "definitiva"])
    
    req_elemento = ["fuego"]
    req_faccion = ["construcciones belobog"]
    req_rol = ["ruptura"]
    
    equipo_valido = False
    
    if datos_equipo:
        elementos = datos_equipo.get("elementos", [])
        facciones = datos_equipo.get("facciones", [])
        roles = datos_equipo.get("roles", [])
        
        for e in elementos:
            if any(valido in e for valido in req_elemento):
                equipo_valido = True
                break

        if not equipo_valido:
            for f in facciones:
                if any(valido in f for valido in req_faccion):
                    equipo_valido = True
                    break

        if not equipo_valido:
            for r in roles:
                if any(valido in r for valido in req_rol):
                    equipo_valido = True
                    break
    
    if equipo_valido and estado_enemigo == "Stun_Boss":
        if es_chain:
            bonos["Bono_Dano_Ulti"] = 70.0
            bonos["Info_Pasiva_Koleda"] = "Chain DMG +70% (Stunned + 2 Stacks)"
        else:
            bonos["Info_Pasiva_Koleda"] = "Pasiva Lista (Usa Chain Attack)"

    return bonos

def pasiva_lighter(datos_equipo=None, stats_actuales=None, elemento=None, **kwargs):
    """
    Pasiva Lighter:
    - Condición Equipo: Aliado 'Atacante' o 'Hijos de Calidón'.
    - Condición Elemento: El personaje debe ser FUEGO o HIELO.
    - Efecto: +1.25% Ice/Fire DMG por stack (Max 20).
    - Escalado: Si Impacto > 170, +0.25% por stack cada 10 Impacto.
    - Cap Máximo: 75% Total.
    """
    bonos = {}
    
    req_rol = ["atacante"]
    req_faccion = ["hijos de calidón"]
    
    activado = False
    if datos_equipo:
        roles = datos_equipo.get("roles", [])
        facciones = datos_equipo.get("facciones", [])
        
        for r in roles:
            if any(valido in r for valido in req_rol):
                activado = True
                break
        
        if not activado:
            for f in facciones:
                if any(valido in f for valido in req_faccion):
                    activado = True
                    break
    
    if activado and stats_actuales:
        impacto = stats_actuales.get("Impacto", 0.0)
        base_stack = 1.25
        extra_stack = 0.0
        
        if impacto > 170:
            exceso = impacto - 170
            incrementos = int(exceso / 10)
            extra_stack = incrementos * 0.25
            
        valor_por_stack = base_stack + extra_stack
        total_buff = valor_por_stack * 20.0
        
        if total_buff > 75.0: total_buff = 75.0

        elem_norm = str(elemento).lower().strip()
        elementos_validos = ["fuego", "hielo"]
        
        if elem_norm in elementos_validos:
            bonos["Daño_elemental"] = total_buff
            bonos["Info_Pasiva_Lighter"] = f"Buff Activo (Impacto: {impacto:.0f})"
        else:
            bonos["Info_Pasiva_Lighter"] = "Buff Inactivo (Requiere Fuego/Hielo)"

    return bonos

def pasiva_lucia(datos_equipo=None, **kwargs):
    """
    Pasiva (Lucia):
    - Condición: Aliado 'Ruptura' (Rupture) o 'Aturdidor' (Stun).
    - Efecto: Al aplicar Darkbreaker, otorga +30% CRIT DMG.
    - Asumimos: Darkbreaker activo para el cálculo.
    """
    bonos = {}
    
    req_rol = ["ruptura", "aturdidor"]
    
    activado = False
    if datos_equipo:
        roles = datos_equipo.get("roles", [])
        for r in roles:
            if any(valido in r for valido in req_rol):
                activado = True
                break
    
    if activado:
        bonos["Daño_crítico"] = 30.0
        bonos["Info_Pasiva"] = "Darkbreaker Activo (+30% CDMG)"

    return bonos

def pasiva_lucy(datos_equipo=None, **kwargs):
    """
    Pasiva Lucy (Cheering Squad):
    - Condición: Aliado 'Fuego', 'Hijos de Calidón' o 'Ruptura'.
    - Efecto: Los jabalíes heredan el Crit Rate/Crit DMG de Lucy.
    - Implementación: Solo informativo (confirma que la pasiva está activa).
    """
    bonos = {}
    
    req_elemento = ["fuego"]
    req_faccion = ["hijos de calidón"]
    req_rol = ["ruptura"]
    
    activado = False
    if datos_equipo:
        elementos = datos_equipo.get("elementos", [])
        facciones = datos_equipo.get("facciones", [])
        roles = datos_equipo.get("roles", [])

        for e in elementos:
            if any(valido in e for valido in req_elemento):
                activado = True
                break

        if not activado:
            for f in facciones:
                if any(valido in f for valido in req_faccion):
                    activado = True
                    break

        if not activado:
            for r in roles:
                if any(valido in r for valido in req_rol):
                    activado = True
                    break
    
    if activado:
        bonos["Info_Pasiva_Lucy"] = "Boars inherit CRIT Stats (Active)"

    return bonos

def pasiva_lycaon(datos_equipo=None, **kwargs):
    """
    Pasiva Lycaon (Elegant Predator):
    - Condición 1: Aliado 'Hielo' o 'Victoria Housekeeping'.
    - Condición 2: Enemigo Aturdido (Stun_Boss).
    - Efecto: +35% Stun DMG Multiplier.
    - Implementación: Se suma a 'Stun_DMG_Multiplier' solo si el enemigo está marcado como Stun_Boss.
    """
    bonos = {}
    
    estado_enemigo = kwargs.get("estado_enemigo", "Normal")
    req_elemento = ["hielo"]
    req_faccion = ["servicios domésticos victoria"]
    
    equipo_valido = False
    
    if datos_equipo:
        elementos = datos_equipo.get("elementos", [])
        facciones = datos_equipo.get("facciones", [])
        
        for e in elementos:
            if any(valido in e for valido in req_elemento):
                equipo_valido = True
                break

        if not equipo_valido:
            for f in facciones:
                if any(valido in f for valido in req_faccion):
                    equipo_valido = True
                    break

    if equipo_valido and estado_enemigo == "Stun_Boss":
        bonos["Stun_DMG_Multiplier"] = 35.0
        bonos["Info_Pasiva_Lycaon"] = "+35% Stun Multiplier (Active)"

    return bonos

def pasiva_manato(datos_equipo=None, **kwargs):
    """
    Pasiva Manato (Remnant Flame):
    - Condición: Aliado 'Aturdidor' (Stun) o 'Soporte' (Support).
    - Efecto (Generación): Ulti (+8 Stacks), Chain (+4 Stacks). Max 20.
    - Efecto (Consumo): Basic/Assist consume 1 stack para curar 2% HP.
    - Implementación: Texto informativo (Mecánica de curación activa).
    """
    bonos = {}
    
    req_rol = ["aturdidor", "soporte"]
    
    activado = False
    if datos_equipo:
        roles = datos_equipo.get("roles", [])
        for r in roles:
            if any(valido in r for valido in req_rol):
                activado = True
                break
    
    if activado:
        bonos["Info_Pasiva_Manato"] = "Healing Active (Ulti +8 Stacks / Chain +4 Stacks)"

    return bonos

def pasiva_miyabi(datos_equipo=None, **kwargs):
    """
    Pasiva Miyabi:
    - Condición: Aliado 'Soporte' o 'Sección 6'.
    - Trigger: Habilidad debe ser 'Ataque Básico' (Shimotsuki).
    - Efecto 1: +60% DMG al Básico.
    - Efecto 2: Ignora 30% Ice RES.
      (Implementación: Sumamos 30.0 a 'Red_Resistencia_Hielo').
    """
    bonos = {}

    nombre_habilidad = str(kwargs.get("nombre_habilidad", "")).lower()

    es_basico = any(k in nombre_habilidad for k in ["básico", "shimotsuki"])
    
    req_rol = ["soporte"]
    req_faccion = ["sección 6"]
    
    activado = False
    if datos_equipo:
        roles = datos_equipo.get("roles", [])
        facciones = datos_equipo.get("facciones", [])
        
        for r in roles:
            if any(valido in r for valido in req_rol):
                activado = True
                break
        
        if not activado:
            for f in facciones:
                if any(valido in f for valido in req_faccion):
                    activado = True
                    break
    
    if activado and es_basico:
        bonos["Bono_Dano_Basico"] = 60.0
        bonos["Red_Resistencia_Hielo"] = 30.0 
        bonos["Info_Pasiva_Miyabi"] = "Shimotsuki: +60% DMG / -30% Enemy RES"
        
    elif activado:
        bonos["Info_Pasiva_Miyabi"] = "Pasiva Activa (Aplica a Shimotsuki/Básico)"

    return bonos

def pasiva_nekomata(datos_equipo=None, **kwargs):
    """
    Pasiva Nekomata (Habilidad Adicional):
    - Condición: Aliado 'Físico' o 'Liebres Astutas' (Cunning Hares).
    - Trigger: Habilidad debe ser 'Ataque Especial EX' (EX Special).
    - Variable: Requiere cargas de 'Asalto' (0, 1 o 2).
    - Efecto: +35% DMG al EX Special por carga (Max 70%).
    """
    bonos = {}

    nombre_habilidad = str(kwargs.get("nombre_habilidad", "")).lower()
    
    es_ex_special = any(k in nombre_habilidad for k in ["ex", "especial"])
    
    cargas = kwargs.get("cargas_nekomata", 0)
    if cargas > 2: cargas = 2

    req_atributo = ["físico"]
    req_faccion = ["liebres astutas"] 
    
    activado = False
    if datos_equipo:
        elementos = datos_equipo.get("elementos", [])
        facciones = datos_equipo.get("facciones", [])

        for e in elementos:
            if any(valido in e for valido in req_atributo):
                activado = True
                break
        
        if not activado:
            for f in facciones:
                if any(valido in f for valido in req_faccion):
                    activado = True
                    break

    if activado and es_ex_special and cargas > 0:
        valor_bono = 35.0 * cargas
        bonos["Bono_Dano_Ex"] = valor_bono
        bonos["Info_Pasiva_Nekomata"] = f"Pasiva Activa: +{valor_bono}% DMG EX ({cargas} stacks)"
        
    elif activado:
        bonos["Info_Pasiva_Nekomata"] = "Pasiva Activa (Esperando EX Special o Cargas)"

    return bonos

def pasiva_nicole(datos_equipo=None, elemento=None, **kwargs):
    """
    Pasiva Nicole (Habilidad Adicional):
    - Condición: Aliado 'Etereo' o 'Liebres Astutas'.
    - Requisito del Personaje: Ser de Elemento Etereo (para recibir el bono).
    - Trigger: Enemigo bajo debuff (pasiva central activada).
    """
    bonos = {}
    elem_norm = str(elemento).lower().strip() if elemento else ""
    
    req_atributo = ["etereo"]
    req_faccion = ["liebres astutas"]
    
    activado = False
    
    if datos_equipo:
        elementos = datos_equipo.get("elementos", [])
        facciones = datos_equipo.get("facciones", [])

        for e in elementos:
            if any(valido in e for valido in req_atributo):
                activado = True
                break

        if not activado:
            for f in facciones:
                if any(valido in f for valido in req_faccion):
                    activado = True
                    break
    
    es_etereo = elem_norm == "etereo"

    if activado and es_etereo:
        bonos["Bono_Dano_Ether"] = 25.0
        bonos["Info_Pasiva_Nicole"] = "Pasiva Activa: +25% Ether DMG (Debuff presente)"

    return bonos

def pasiva_Orpheus(datos_equipo=None, **kwargs):
    """
    Pasiva Orpheus (Field Promotion):
    - Condición: Aliado 'Aturdidor' (Stun) o 'Soporte' (Support).
    - Trigger: Ataques con 'Zeroed In' (Supresión/Timing correcto).
    - Efecto: Esos ataques (Aftershock) ignoran 25% DEF.
    """
    bonos = {}
    
    req_rol = ["aturdidor", "soporte"]
    
    activado = False
    if datos_equipo:
        roles = datos_equipo.get("roles", [])
        
        for r in roles:
            if any(valido in r for valido in req_rol):
                activado = True
                break
    
    if activado:
        bonos["Ignorar_Defensa_Aftershock"] = 25.0
        bonos["Info_Pasiva_Orpheus"] = "Zeroed In: Ignora 25% DEF"

    return bonos

def pasiva_pan_yinhu(datos_equipo=None, **kwargs):
    """
    Pasiva Pan Yinhu (Touch of Death):
    - Condición: Aliado 'Ruptura' o misma Facción.
    - Trigger: Golpe con 'Special Attack: Touch of Death'.
    - Efecto: Aplica 'Depleted Qi' al enemigo.
    - Valor: +20% a TODO el daño contra el objetivo (All DMG).
    """
    bonos = {}
    
    debuff_activo = kwargs.get("debuff_qi_activo", False)

    req_rol = ["ruptura"]
    req_faccion = ["pináculo yunkui"] 
    
    activado = False
    if datos_equipo:
        roles = datos_equipo.get("roles", [])
        facciones = datos_equipo.get("facciones", [])
        
        for r in roles:
            if any(valido in r for valido in req_rol):
                activado = True
                break

        if not activado:
            for f in facciones:
                if any(valido in f for valido in req_faccion):
                    activado = True
                    break
    
    if activado and debuff_activo:
        bonos["Daño_Adicional"] = 20.0
        bonos["Info_Pasiva_PanYinhu"] = "Depleted Qi Activo (+20% All DMG)"

    return bonos

def pasiva_piper(datos_equipo=None, **kwargs):
    """
    Pasiva Piper (Start Your Engines!):
    - Condición: Aliado 'Físico' o 'Hijos de Calidón'.
    - Trigger: Piper tiene 20 o más cargas de 'Power'.
    - Efecto: +18% DMG para todo el equipo.
    """
    bonos = {}
    stacks = kwargs.get("stacks_piper", 0)

    req_atributo = ["fisico", "físico"]
    req_faccion = ["hijos de calidon", "hijos de calidón"]
    
    activado = False
    if datos_equipo:
        elementos = datos_equipo.get("elementos", [])
        facciones = datos_equipo.get("facciones", [])

        for e in elementos:
            if any(valido in e for valido in req_atributo):
                activado = True
                break

        if not activado:
            for f in facciones:
                if any(valido in f for valido in req_faccion):
                    activado = True
                    break

    if activado and stacks >= 20:
        bonos["Daño_Adicional"] = 18.0
        bonos["Info_Pasiva_Piper"] = "Power >= 20 (+18% Squad DMG)"
        
    elif activado:
        bonos["Info_Pasiva_Piper"] = f"Pasiva Inactiva (Cargas actuales: {stacks})"

    return bonos

def pasiva_pulchra(datos_equipo=None, **kwargs):
    """
    Pasiva Pulchra (Nightmare Shadow):
    - Condición: Aliado 'Atacante', 'Ruptura' o Facción (Hijos de Calidón).
    - Trigger: Aplicar 'Binding Trap' (Trampa Vinculante) con ataques especiales/ulti.
    - Efecto: +30% Aftershock DMG contra el objetivo (para todos).
    """
    bonos = {}

    debuff_activo = kwargs.get("debuff_binding_trap_activo", False)

    req_rol = ["atacante", "ruptura"]
    req_faccion = ["hijos de calidón"] 
    
    activado = False
    if datos_equipo:
        roles = datos_equipo.get("roles", [])
        facciones = datos_equipo.get("facciones", [])
        
        for r in roles:
            if any(valido in r for valido in req_rol):
                activado = True
                break
        
        if not activado:
            for f in facciones:
                if any(valido in f for valido in req_faccion):
                    activado = True
                    break
    
    if activado and debuff_activo:
        bonos["Daño_Aftershock"] = 30.0
        bonos["Info_Pasiva_Pulchra"] = "Binding Trap Activa (+30% Aftershock DMG)"

    return bonos

def pasiva_qingyi(datos_equipo=None, stats_actuales=None, **kwargs):
    """
    Pasiva Qingyi (Dazzling Transformation):
    - Condición: Aliado 'Atacante' o misma Facción (N.E.P.S. / Seguridad Pública).
    - Efecto 1: Ataques Básicos infligen +20% Aturdimiento (Daze).
    - Efecto 2: Si Impacto > 120, gana +6 ATK por punto extra (Max 600).
    """
    bonos = {}
    
    nombre_habilidad = str(kwargs.get("nombre_habilidad", "")).lower()
    es_basico = any(k in nombre_habilidad for k in ["básico", "basic", "ataque normal"])

    req_rol = ["atacante"]
    req_faccion = ["n.e.p.s.", "r.o.v.e.r.", "m_o_d_"]
    
    activado = False
    if datos_equipo:
        roles = datos_equipo.get("roles", [])
        facciones = datos_equipo.get("facciones", [])
        
        for r in roles:
            if any(valido in r for valido in req_rol):
                activado = True
                break
        
        if not activado:
            for f in facciones:
                if any(valido in f for valido in req_faccion):
                    activado = True
                    break
    
    if activado:
        if es_basico:
            bonos["Bono_Stun_Basico"] = 20.0
        
        if stats_actuales:
            impacto = stats_actuales.get("Impacto", 0.0)
            
            if impacto > 120:
                exceso = impacto - 120
                atk_extra = exceso * 6.0
                
                if atk_extra > 600.0: 
                    atk_extra = 600.0
                
                bonos["Ataque_Plano"] = atk_extra
                bonos["Info_Pasiva_Qingyi"] = f"Buff Activo: +{atk_extra:.0f} ATK (Impacto: {impacto:.0f})"

    return bonos

def pasiva_rina(datos_equipo=None, elemento=None, **kwargs):
    """
    Pasiva Rina (Banquet of Error):
    - Condición: Aliado 'Eléctrico' o 'Victoria Housekeeping'.
    - Trigger: Enemigo afectado por Shock (Electrificado).
    - Efecto 1: +10% Electric DMG para todo el squad.
    - Efecto 2: +3s Duración de Shock (Informativo).
    """
    bonos = {}

    enemigo_shocked = kwargs.get("enemigo_shocked", False)

    req_atributo = ["electrico"]
    req_faccion = ["servicios domésticos victoria"]
    
    activado = False
    if datos_equipo:
        elementos = datos_equipo.get("elementos", [])
        facciones = datos_equipo.get("facciones", [])
        
        for e in elementos:
            if any(valido in e for valido in req_atributo):
                activado = True
                break
        
        if not activado:
            for f in facciones:
                if any(valido in f for valido in req_faccion):
                    activado = True
                    break

    elem_norm = str(elemento).lower().strip()
    elementos_validos = ["electrico"]

    if elem_norm in elementos_validos and activado and enemigo_shocked:

        bonos["Daño_elemental"] = 10.0
        bonos["Info_Pasiva_Rina"] = "Enemigo en Shock (+10% Electric DMG)"

    return bonos

def pasiva_seed(datos_equipo=None, **kwargs):
    """
    Pasiva Seed (Nombre provisional):
    - Condición: Otro personaje 'Atacante' en el equipo.
    - Efecto 1 (Resource): Restaura 2 Energía al Vanguardia (Info).
    - Efecto 2 (DMG): +30% DMG y Ignora 25% Electric RES.
    - Moves afectados: Básicos específicos (Slaughter/Downfall) y Ultimate (Bloom).
    """
    bonos = {}
    
    nombre_habilidad = str(kwargs.get("nombre_habilidad", "")).lower()
    
    es_basico = any(k in nombre_habilidad for k in ["básico", "petals", "slaughter", "downfall"])
    es_ulti = any(k in nombre_habilidad for k in ["ultimate", "definitiva"])
    
    es_habilidad_afectada = es_basico or es_ulti

    req_rol = ["atacante"]
    
    activado = False
    if datos_equipo:
        roles = datos_equipo.get("roles", [])
        
        for r in roles:
            if any(valido in r for valido in req_rol):
                activado = True
                break
    
    if activado:
        bonos["Info_Pasiva_Seed"] = "Active: Restore 2 Energy (on Hit)"
        
        if es_habilidad_afectada:
            bonos["Daño_Adicional"] = 30.0
            bonos["Pen_Res_Electrico"] = 25.0
            bonos["Info_Pasiva_Seed"] += " / Buff Applied (DMG + RES Ign)"

    return bonos

def pasiva_seth(datos_equipo=None, **kwargs):
    """
    Pasiva Seth (High-Spirited Shield):
    - Condición: Aliado 'Eléctrico' o 'N.E.P.S.'.
    - Trigger: Golpe Final de Básico o Chain Attack aplica el debuff.
    - Efecto: Reduce la Resistencia a Anomalía (Buildup RES) del enemigo en 20% (20s).
    - Nota: Aplica a TODOS los atributos.
    """
    bonos = {}

    debuff_activo = kwargs.get("debuff_seth_activo", False)

    req_atributo = ["electrico"]
    req_faccion = ["n.e.p.s.", "r.o.v.e.r.", "m_o_d_"]
    
    activado = False
    if datos_equipo:
        elementos = datos_equipo.get("elementos", [])
        facciones = datos_equipo.get("facciones", [])
        
        for e in elementos:
            if any(valido in e for valido in req_atributo):
                activado = True
                break
        
        if not activado:
            for f in facciones:
                if any(valido in f for valido in req_faccion):
                    activado = True
                    break
    
    if activado and debuff_activo:
        bonos["Red_Res_Buildup"] = 20.0
        bonos["Info_Pasiva_Seth"] = "Debuff Activo: -20% Enemy Buildup RES"

    return bonos

def pasiva_soldier_11(datos_equipo=None, elemento=None, **kwargs):
    """
    Pasiva Soldier 11 (Versión DMG):
    - Condición: Aliado 'Fuego' o 'Escuadrón Óbolo' (Obol Squad).
    - Efecto Base: +10% Fire DMG.
    - Efecto Extra: +22.5% Fire DMG adicional si el enemigo está Aturdido.
    - Total en Stun: +32.5% Fire DMG.
    """
    bonos = {}
    
    elem_norm = str(elemento).lower().strip() if elemento else ""
    es_fuego = elem_norm == "fuego"
    estado_enemigo = kwargs.get("estado_enemigo", "Normal")
    esta_aturdido = (estado_enemigo == "Stun_Boss")

    req_atributo = ["fuego"]
    req_faccion = ["batallón óbolos", "batallón argente del ministerio de defensa"]
    
    activado = False
    if datos_equipo:
        elementos = datos_equipo.get("elementos", [])
        facciones = datos_equipo.get("facciones", [])
        
        for e in elementos:
            if any(valido in e for valido in req_atributo):
                activado = True
                break
        
        if not activado:
            for f in facciones:
                if any(valido in f for valido in req_faccion):
                    activado = True
                    break
    
    if activado and es_fuego:
        bono_total = 10.0
        
        if esta_aturdido:
            bono_total += 22.5
            bonos["Info_Pasiva_Soldier11"] = "Pasiva Activa: +32.5% Fire DMG (Enemigo Aturdido)"
        else:
            bonos["Info_Pasiva_Soldier11"] = "Pasiva Activa: +10% Fire DMG (Base)"
            
        bonos["Daño_elemental"] = bono_total

    return bonos

def pasiva_soukaku(datos_equipo=None, elemento=None, **kwargs):
    """
    Pasiva Soukaku (Blade Banner):
    - Condición: Aliado 'Hielo' o 'Sección 6' (Section 6).
    - Trigger: Consumir 'Vortex' para activar 'Fly the Flag'.
    - Efecto: +20% Ice DMG para el equipo (22s).
    """
    bonos = {}
    buff_activo = kwargs.get("buff_soukaku_activo", False)

    req_atributo = ["hielo"]
    req_faccion = ["sección 6"]
    
    activado = False
    if datos_equipo:
        elementos = datos_equipo.get("elementos", [])
        facciones = datos_equipo.get("facciones", [])
        
        for e in elementos:
            if any(valido in e for valido in req_atributo):
                activado = True
                break
        
        if not activado:
            for f in facciones:
                if any(valido in f for valido in req_faccion):
                    activado = True
                    break
    
    elem_norm = str(elemento).lower().strip() if elemento else ""
    es_hielo = elem_norm == "hielo"

    if activado and buff_activo and es_hielo:
        bonos["Daño_elemental"] = 20.0
        bonos["Info_Pasiva_Soukaku"] = "Fly the Flag Activo (+20% Ice DMG)"
        
    elif activado:
        bonos["Info_Pasiva_Soukaku"] = "Pasiva Lista (Requiere activar Fly the Flag)"

    return bonos

def pasiva_trigger(datos_equipo=None, stats_actuales=None, elemento=None, **kwargs):
    """
    Pasiva Trigger (Precision Protocol):
    - Condición: Aliado 'Atacante' o del Mismo Atributo (Elemento).
    - Efecto: Si Prob. Crítico > 40%, el exceso aumenta el Aturdimiento (Daze) de los Aftershocks.
    - Ratio: 1.5% Daze por cada 1% CRIT Rate extra.
    - Cap Máximo: +75% Daze.
    """
    bonos = {}
    
    req_rol = ["atacante"]
    
    mi_elemento = str(elemento).lower().strip() if elemento else ""
    
    activado = False
    if datos_equipo:
        roles = datos_equipo.get("roles", [])
        elementos = datos_equipo.get("elementos", [])
        
        for r in roles:
            if any(valido in r for valido in req_rol):
                activado = True
                break
        
        if not activado and mi_elemento:
            for e in elementos:
                if mi_elemento in str(e).lower():
                    activado = True
                    break
    
    if activado and stats_actuales:
        crit_rate = stats_actuales.get("Probabilidad_crítico", 0.0)
        
        if crit_rate > 40.0:
            exceso = crit_rate - 40.0
            bono_daze = exceso * 1.5
            
            if bono_daze > 75.0:
                bono_daze = 75.0
            
            bonos["ono_Stun_Basico"] = bono_daze
            bonos["Info_Pasiva_Trigger"] = f"Buff Activo: +{bono_daze:.1f}% Aftershock Daze (CR: {crit_rate:.1f}%)"

    return bonos

def pasiva_vivian(datos_equipo=None, elemento=None, **kwargs):
    """
    Pasiva Vivian (Nombre provisional):
    - Condición: Otro aliado 'Anomalía' o del mismo Atributo (Asumimos Etéreo).
    - Efecto Mecánico: Consume 'Guard Feather' para atacar (Info).
    - Efecto Estadístico: +12% Corruption DMG (Anomalía Etérea) y Disorder DMG.
    - Implementación: Se suma al 'Bono_Daño_Anomalia' solo si el elemento es Etereo.
    """
    bonos = {}

    elem_norm = str(elemento).lower().strip() if elemento else ""
    es_corrupcion = elem_norm in ["etereo"]

    req_rol = ["anomalia"]
    req_atributo = ["etereo"]
    
    activado = False
    if datos_equipo:
        roles = datos_equipo.get("roles", [])
        elementos = datos_equipo.get("elementos", [])
        
        for r in roles:
            if any(valido in r for valido in req_rol):
                activado = True
                break
        
        if not activado:
            for e in elementos:
                if any(valido in e for valido in req_atributo):
                    activado = True
                    break
    
    if activado:
        info_text = i18n.t("pasivas.vivian.info_activa", default="Active: Feather Consume -> Extra Attack")
        
        if es_corrupcion:
            bonos["Bono_Daño_Anomalia"] = 12.0
            info_text += " / +12% Corruption DMG"
            
        bonos["Info_Pasiva_Vivian"] = info_text

    return bonos

def pasiva_yanagi(datos_equipo=None, **kwargs):
    """
    Pasiva Yanagi (Moonflower):
    - Condición: Aliado 'Anomalía' o mismo Atributo (Eléctrico).
    - Trigger: Cambio de Postura + Golpe Básico (Tsukuyomi Kagura).
    - Efecto: +45% Anomaly Buildup durante 8s.
    """
    bonos = {}

    buff_activo = kwargs.get("buff_yanagi_activo", False)

    req_rol = ["anomalia"]
    req_atributo = ["electrico"] 
    
    activado = False
    if datos_equipo:
        roles = datos_equipo.get("roles", [])
        elementos = datos_equipo.get("elementos", [])
        
        for r in roles:
            if any(valido in r for valido in req_rol):
                activado = True
                break
        
        if not activado:
            for e in elementos:
                if any(valido in e for valido in req_atributo):
                    activado = True
                    break
    
    if activado and buff_activo:
        bonos["Bono_Acumulación"] = 45.0
        bonos["Info_Pasiva_Yanagi"] = "Buff Activo: +45% Anomaly Buildup (8s)"
        
    elif activado:
        bonos["Info_Pasiva_Yanagi"] = "Pasiva Lista (Requiere Cambio de Postura)"

    return bonos

def pasiva_Ye_Shunguang(datos_equipo=None, **kwargs):
    """
    Pasiva Ye shunguang:
    - Condición: Aliado 'Soporte' (Support) o 'Defensa' (Defense).
    - Trigger: Aliado activa 'Ether Veil'.
    - Efecto: Genera 3 puntos de 'Qingming Sword Force'.
    - Alternativa: Si está en estado 'Enlightened Mind', genera 3 stacks de 'Bearer'.
    - Implementación: Texto informativo sobre la generación de recursos activa.
    """
    bonos = {}
    
    req_rol = ["soporte", "defensor"]
    
    activado = False
    if datos_equipo:
        roles = datos_equipo.get("roles", [])
        
        for r in roles:
            if any(valido in r for valido in req_rol):
                activado = True
                break
    
    if activado:
        bonos["Info_Pasiva_Qingming"] = "Recarga Activa: +3 Qingming/Bearer (on Ether Veil)"

    return bonos

def pasiva_yidhari(datos_equipo=None, **kwargs):
    """
    Pasiva Yidhari (Chilling Depths):
    - Condición Squad: Aliado 'Aturdidor' (Stun) o 'Soporte' (Support).
    
    - Efecto 1 (Supervivencia): Si HP < 50%:
        * +30% CRIT DMG.
        * -25% Daño Recibido (Reducción).
        
    - Efecto 2 (Velo): Si está en 'Ether Veil: Wellspring':
        * Ataques Cargados (Lv3) y EX Special invocan un 'Icy Tentacle'.
        * Este tentáculo se considera daño de 'EX Special Attack'.
    """
    bonos = {}

    hp_bajo = kwargs.get("hp_bajo_50", False)
    velo_activo = kwargs.get("velo_yidhari_activo", False)

    req_rol = ["aturdidor", "soporte"]
    
    activado = False
    if datos_equipo:
        roles = datos_equipo.get("roles", [])
        
        for r in roles:
            if any(valido in r for valido in req_rol):
                activado = True
                break
    
    if activado:
        info_parts = []
        
        if hp_bajo:
            bonos["Daño_crítico"] = 30.0
            bonos["Reduccion_Daño"] = 25.0
            info_parts.append("HP < 50% (+30% CDMG)")
            
        if velo_activo:
            info_parts.append("Velo Activo (Tentáculo Habilitado -> Tratar como EX DMG)")
            
        if info_parts:
            bonos["Info_Pasiva_Yidhari"] = " / ".join(info_parts)
        else:
            bonos["Info_Pasiva_Yidhari"] = "Pasiva Lista (Sin condiciones activas)"

    return bonos

def pasiva_yixuan(datos_equipo=None, **kwargs):
    """
    Pasiva Yixuan (Ink & Thunder):
    - Condición: Aliado 'Aturdidor', 'Soporte' o 'Defensa'.
    
    - Efecto 1 (Mecánica): Recupera Adrenalina tras Ulti aliada o Perfect Assist.
    - Efecto 2 (EX): +30% DMG en ataques EX si el enemigo está Aturdido (Stun).
    - Efecto 3 (Buff): Tras usar Ulti, entra en 'Meditation' (+40% CRIT DMG por 15s).
    """
    bonos = {}

    estado_enemigo = kwargs.get("estado_enemigo", "Normal")
    nombre_habilidad = str(kwargs.get("nombre_habilidad", "")).lower()
    meditacion_activa = kwargs.get("meditacion_yixuan_activa", False)

    es_ex = any(k in nombre_habilidad for k in ["ex", "especial"])

    req_rol = ["aturdidor", "soporte", "defensa"]
    
    activado = False
    if datos_equipo:
        roles = datos_equipo.get("roles", [])
        for r in roles:
            if any(valido in r for valido in req_rol):
                activado = True
                break
    
    if activado:
        info_parts = []

        if es_ex and estado_enemigo == "Stun_Boss":
            bonos["Bono_Dano_Ex"] = 30.0
            info_parts.append("+30% EX DMG (Enemy Stunned)")
        
        if meditacion_activa:
            bonos["Daño_crítico"] = 40.0
            info_parts.append("Meditation (+40% CDMG)")
            
        if not info_parts:
            bonos["Info_Pasiva_Yixuan"] = "Pasiva Lista (Adrenaline Regen / Assist Lightning)"
        else:
            bonos["Info_Pasiva_Yixuan"] = " / ".join(info_parts)

    return bonos

def pasiva_yuzuha(datos_equipo=None, stats_actuales=None, **kwargs):
    """
    Pasiva Yuzuha (Tanuki Wish):
    - Condición: Aliado 'Anomalía' o misma Facción.
    - Mecánica: Convierte exceso de Tasa de Anomalía (>100) en Buffs.
    - Ratio: 0.2% por cada punto extra. Max 20% (al llegar a 200 Tasa).
    - Efectos: 
        1. +% Anomaly Buildup Rate (Acumulación).
        2. +% Attribute Anomaly DMG (Daño Anomalía).
        3. +% Disorder DMG (Desorden).
    """
    bonos = {}
    
    req_rol = ["anomalia"]
    req_faccion = ["cabaña del terror"] 
    
    activado = False
    if datos_equipo:
        roles = datos_equipo.get("roles", [])
        facciones = datos_equipo.get("facciones", [])
        
        for r in roles:
            if any(valido in r for valido in req_rol):
                activado = True
                break

        if not activado:
            for f in facciones:
                if any(valido in f for valido in req_faccion):
                    activado = True
                    break

    if activado and stats_actuales:
        tasa = stats_actuales.get("Tasa_de_Anomalía", 0.0)
        
        if tasa > 100.0:
            exceso = tasa - 100.0
            bono_pct = exceso * 0.2
            
            if bono_pct > 20.0: 
                bono_pct = 20.0
            
            bonos["Bono_Acumulación"] = bono_pct
            bonos["Bono_Daño_Anomalia"] = bono_pct
            bonos["Bono_Daño_Desorden"] = bono_pct
            
            bonos["Info_Pasiva_Yuzuha"] = f"Tanuki Wish: +{bono_pct:.1f}% Buildup/DMG (AM: {tasa:.0f})"

    return bonos

def pasiva_zhao(datos_equipo=None, stats_actuales=None, **kwargs):
    """
    Pasiva Zhao (Nombre provisional):
    - Condición Squad: Aliado 'Atacante', 'Anomalía' o 'Soporte'.
    - Trigger: Zhao está dentro de un 'Ether Veil' (Velo Etéreo).
    - Efecto Base: +10% DMG para todo el squad.
    - Escalado: +1% DMG extra por cada 400 HP por encima de 15,000.
    - Cap Máximo: 40% Total (a los 27,000 HP).
    """
    bonos = {}

    velo_activo = kwargs.get("velo_activo", False)
    req_rol = ["atacante", "anomalia", "soporte"]
    
    activado = False
    if datos_equipo:
        roles = datos_equipo.get("roles", [])
        
        for r in roles:
            if any(valido in r for valido in req_rol):
                activado = True
                break
    
    if activado and velo_activo:
        hp_max = stats_actuales.get("HP_Max", 0.0) if stats_actuales else 0.0
        
        base_bonus = 10.0
        extra_bonus = 0.0
        
        if hp_max > 15000:
            exceso = hp_max - 15000
            stacks = int(exceso / 400)
            extra_bonus = stacks * 1.0
            
        total_bonus = base_bonus + extra_bonus
        
        if total_bonus > 40.0:
            total_bonus = 40.0
            
        bonos["Daño_Adicional"] = total_bonus
        bonos["Info_Pasiva_Zhao"] = f"Velo Activo: +{total_bonus:.1f}% Squad DMG (HP: {hp_max:.0f})"
        
    elif activado:
        bonos["Info_Pasiva_Zhao"] = "Pasiva Lista (Requiere activar Velo)"

    return bonos

def pasiva_zhu_yuan(datos_equipo=None, **kwargs):
    """
    Pasiva Zhu Yuan (Tactical Coordination):
    - Condición: Aliado 'Soporte' o misma Facción (N.E.P.S.).
    - Trigger: Tras usar EX Special, Chain Attack o Ulti.
    - Efecto: +30% Crit Rate durante 10s.
    """
    bonos = {}

    buff_activo = kwargs.get("buff_zhuyuan_activo", False)

    req_rol = ["soporte"]
    req_faccion = ["n.e.p.s.", "r.o.v.e.r.", "m_o_d_"]
    
    activado = False
    if datos_equipo:
        roles = datos_equipo.get("roles", [])
        facciones = datos_equipo.get("facciones", [])
        
        for r in roles:
            if any(valido in r for valido in req_rol):
                activado = True
                break
        
        if not activado:
            for f in facciones:
                if any(valido in f for valido in req_faccion):
                    activado = True
                    break
    
    if activado and buff_activo:
        bonos["Probabilidad_crítico"] = 30.0
        bonos["Info_Pasiva_ZhuYuan"] = "Buff Activo: +30% Crit Rate (10s)"
        
    elif activado:
        bonos["Info_Pasiva_ZhuYuan"] = "Pasiva Lista (Esperando activación)"

    return bonos

def pasiva_sunna(datos_equipo=None, **kwargs):
    """
    Pasiva Sunna:
    - Condición: Aliado 'Atacante' (Attack) o 'Anomalía' (Anomaly).
    - Efecto: Permite aplicar [Cat's Gaze] para que los aliados lo detonen.
    - Implementación: Como el daño lo detonan los aliados, para la simulación 
      personal de Sunna esto es informativo. Los multiplicadores de 300%/480% 
      se aplican cuando ella está en el slot de Soporte.
    """
    bonos = {}
    
    req_rol = ["atacante", "anomalia"]
    
    activado = False
    if datos_equipo:
        roles = datos_equipo.get("roles", [])
        for r in roles:
            r_norm = str(r).lower().strip()
            if any(valido in r_norm for valido in req_rol):
                activado = True
                break
    
    if activado:
        bonos["Info_Pasiva_Sunna"] = "Cat's Gaze habilitado (Detonable por Atacante/Anomalía)"
    else:
        bonos["Info_Pasiva_Sunna"] = "Pasiva Inactiva (Requiere Atacante o Anomalía)"

    return bonos

def pasiva_aria(datos_equipo=None, **kwargs):
    """
    Pasiva Aria:
    - Condición: Aliado 'Aturdidor' (Stun), 'Soporte' (Support) o misma Facción ('Ángeles de la Delusión').
    - Efecto 1: Al activar Ether Veil, genera 4 Fandom Power en el campo (CD: 1s).
    - Efecto 2: Extiende la duración de Corruption (Corrupción) aplicada por el equipo en 3s.
    - Implementación: Texto informativo sobre la generación de recursos y extensión de debuff.
    """
    bonos = {}
    
    req_rol = ["aturdidor", "soporte"]

    
    activado = False
    if datos_equipo:
        roles = datos_equipo.get("roles", [])
        facciones = datos_equipo.get("facciones", [])
        
        for r in roles:
            r_norm = str(r).lower().strip()
            if any(valido in r_norm for valido in req_rol):
                activado = True
                break
    
    if activado:
        bonos["Info_Pasiva_Aria"] = "Pasiva Activa: Velo genera 4 Fandom Power / Corrupción +3s"
    else:
        bonos["Info_Pasiva_Aria"] = "Pasiva Inactiva (Falta Aturdidor o Soporte)"

    return bonos

def pasiva_nangong_yu(datos_equipo=None, nombre_habilidad="", **kwargs):
    """
    Pasiva Nangong Yu:
    - Condición: Aliado 'Anomalía' o misma Facción ('Ángeles de la Delusión').
    - Efecto Base (Si Enemigo Stunned): 
        * +30% Anomaly Buildup Rate general.
        * +30% extra a Chain Attacks (+60% Total).
    - Mecánica Dance Prowess (Activable UI): 
        * Permite detonar Polarity Disorder (25% DMG del Disorder original).
        * EX no cuesta energía si el enemigo fue aturdido recientemente.
    - Mecánica Misstep (Activable UI):
        * +30% Stun DMG Multiplier.
        * +3s de duración de Stun.
    """
    bonos = {}
    
    estado_enemigo = kwargs.get("estado_enemigo", "Normal")
    esta_aturdido = (estado_enemigo == "Stun_Boss")
    
    dance_prowess_activo = kwargs.get("nangong_dance_prowess", False)
    misstep_activo = kwargs.get("nangong_misstep", False)
    
    hab_norm = str(nombre_habilidad).lower()
    es_chain = any(k in hab_norm for k in ["chain", "cadena"])

    req_rol = ["anomalia"]
    req_faccion = ["ángeles de la delusión"]
    
    activado = False
    if datos_equipo:
        roles = datos_equipo.get("roles", [])
        facciones = datos_equipo.get("facciones", [])
        
        for r in roles:
            r_norm = str(r).lower().strip()
            if any(valido in r_norm for valido in req_rol):
                activado = True
                break
        
        if not activado:
            for f in facciones:
                f_norm = str(f).lower().strip()
                if any(valido in f_norm for valido in req_faccion):
                    activado = True
                    break
    
    if activado:
        info_parts = []
        
        if esta_aturdido:
            buildup = 30.0
            if es_chain:
                buildup += 30.0
                info_parts.append(f"+{buildup}% Buildup (Stunned + Chain)")
            else:
                info_parts.append(f"+{buildup}% Buildup (Stunned)")
                
            bonos["Bono_Acumulación"] = buildup
            
        if misstep_activo:
            bonos["Stun_DMG_Multiplier"] = 30.0
            info_parts.append("Misstep (+30% Stun DMG Mult. / +3s Stun)")
            
        if dance_prowess_activo:
            info_parts.append("Dance Prowess (Polarity Disorder Activo / EX Cost=0)")
            
        if not info_parts:
            bonos["Info_Pasiva_Nangong"] = "Pasiva Lista (Requiere Enemigo Aturdido o Buffs Activos)"
        else:
            bonos["Info_Pasiva_Nangong"] = " / ".join(info_parts)

    return bonos

def pasiva_cissia(datos_equipo=None, elemento=None, **kwargs):
    """
    Pasiva Cissia:
    - Condición: Aliado 'Aturdidor' (Stun) o del mismo Atributo (Eléctrico).
    - Efecto: Mientras tenga Venom, otorga +40% CRIT DMG al equipo. Cissia gana +10% adicional.
    - Implementación: Para los cálculos del daño personal de Cissia, sumamos directamente el 50% (40 + 10).
      Asumimos que el estado Venom está activo durante el combate debido a su larga duración (30s tras agotarse).
    """
    bonos = {}
    
    req_rol = ["aturdidor"]
    req_atributo = ["electrico", "eléctrico"]
    
    activado = False
    if datos_equipo:
        roles = datos_equipo.get("roles", [])
        elementos = datos_equipo.get("elementos", [])
        
        for r in roles:
            r_norm = str(r).lower().strip()
            if any(valido in r_norm for valido in req_rol):
                activado = True
                break
        
        if not activado:
            for e in elementos:
                e_norm = str(e).lower().strip()
                if any(valido in e_norm for valido in req_atributo):
                    activado = True
                    break
    
    if activado:
        bonos["Daño_crítico"] = 50.0
        bonos["Info_Pasiva_Cissia"] = "Pasiva Activa: Venom (+50% CRIT DMG)"
    else:
        bonos["Info_Pasiva_Cissia"] = "Pasiva Inactiva (Falta Aturdidor o Eléctrico)"

    return bonos

def pasiva_promeia(datos_equipo=None, **kwargs):
    """
    Pasiva Promeia:
    - Condición: Aliado 'Anomalía' (Anomaly) o 'Soporte' (Support).
    - Efecto 1: Tras usar EX Special, +30% Ice Anomaly Buildup Rate por 30s.
    - Efecto 2: +3s a la duración del efecto Frostbite aplicado por el equipo.
    - Efecto 3: EX Special aplica 'Presumption of Guilt'. Abloom ignora 40% de DEF contra objetivos con esta marca.
    """
    bonos = {}
    
    ex_buff_activo = kwargs.get("promeia_ex_buff", True)
    
    req_rol = ["anomalia", "soporte"]
    
    activado = False
    if datos_equipo:
        roles = datos_equipo.get("roles", [])
        for r in roles:
            r_norm = str(r).lower().strip()
            if any(valido in r_norm for valido in req_rol):
                activado = True
                break
    
    if activado:
        info_parts = ["Duración Frostbite +3s"]
        
        if ex_buff_activo:
            bonos["Bono_Acumulación"] = 30.0
            bonos["Ignorar_Defensa_Abloom"] = 40.0
            info_parts.append("EX Buff (+30% Ice Buildup / Abloom Ignora 40% DEF)")
        else:
            info_parts.append("Esperando activación de EX Special")
            
        bonos["Info_Pasiva_Promeia"] = " / ".join(info_parts)
    else:
        bonos["Info_Pasiva_Promeia"] = "Pasiva Inactiva (Falta aliado Anomalía o Soporte)"

    return bonos

def pasiva_starlight_billy(roles_equipo=None, nombre_habilidad="", **kwargs):
    """
    Pasiva Starlight - Billy (Starlight):
    - Condición: Un aliado es 'Aturdidor' (Stun), 'Defensor' (Defense) o 'Soporte' (Support).
    - Efecto: Ciertos ataques otorgan 1 stack de Starlight (máx 2, duración 45s).
      Habilidades que otorgan stack (1 por uso):
        * EX Special Attack: Cool Wheelie
        * 4to golpe de Basic Attack: Knight's Technique
        * Chain Attack
        * Ultimate
    - Por stack: +20% DMG en Chain, Ultimate, EX Special y Basic Attack: Full-Throttle Starlight.
    """
    bonos = {}
    roles_validos = ["aturdidor", "defensor", "soporte"]

    activado = False
    if roles_equipo:
        for rol in roles_equipo:
            r_norm = str(rol).lower().strip()
            if any(valido in r_norm for valido in roles_validos):
                activado = True
                break

    if activado:
        stacks = int(kwargs.get('stacks', 2))
        stacks = max(0, min(stacks, 2))

        if stacks > 0:
            hab_norm = nombre_habilidad.lower()
            keywords_buff = ["cadena", "chain", "definitiva", "ultimate", "ex special", "ex ", "full-throttle", "full throttle"]
            es_habilidad_buffada = any(k in hab_norm for k in keywords_buff)

            if es_habilidad_buffada:
                bonos["Daño_Adicional"] = 20.0 * stacks

            bonos["Info_Pasiva_Starlight_Billy"] = f"Starlight Activo: {stacks}/2 stacks (+{20 * stacks}% DMG en Chain/Ulti/EX/Full-Throttle)"
        else:
            bonos["Info_Pasiva_Starlight_Billy"] = "Pasiva Activa (0 stacks de Starlight acumulados)"
    else:
        bonos["Info_Pasiva_Starlight_Billy"] = "Pasiva Inactiva (Falta Aturdidor, Defensor o Soporte)"

    return bonos

MAPA_PASIVAS = {
    "Soldier 0 - Anby": pasiva_soldier_0_anby,
    "Alice": pasiva_alice,
    "Anby": pasiva_anby,
    "Anton": pasiva_anton,
    "Astra Yao": pasiva_astra_yao,
    "Banyue": pasiva_banyue,
    "Ben": pasiva_ben,
    "Billy": pasiva_billy,
    "Burnice": pasiva_burnice,
    "Caesar": pasiva_caesar,
    "Corin": pasiva_corin,
    "Dialyn": pasiva_dialyn,
    "Ellen": pasiva_ellen,
    "Evelyn": pasiva_evelyn,
    "Grace": pasiva_grace,
    "Harumasa": pasiva_harumasa,
    "Hugo": pasiva_hugo,
    "Jane": pasiva_jane,
    "Ju Fufu": pasiva_Jufufu,
    "Koleda": pasiva_koleda,
    "Lighter": pasiva_lighter,
    "Lucia": pasiva_lucia,
    "Lucy": pasiva_lucy,
    "Lycaon": pasiva_lycaon,
    "Manato": pasiva_manato,
    "Miyabi": pasiva_miyabi,
    "Nekomata": pasiva_nekomata,
    "Nicole": pasiva_nicole,
    "Orphie & Magus": pasiva_Orpheus,
    "Pan Yinhu": pasiva_pan_yinhu,
    "Piper": pasiva_piper,
    "Pulchra": pasiva_pulchra,
    "Qingyi": pasiva_qingyi,
    "Rina": pasiva_rina,
    "Seed": pasiva_seed,
    "Seth": pasiva_seth,
    "Soldier 11": pasiva_soldier_11,
    "Soukaku": pasiva_soukaku,
    "Trigger": pasiva_trigger,
    "Vivian": pasiva_vivian,
    "Yanagi": pasiva_yanagi,
    "Ye Shunguang": pasiva_Ye_Shunguang,
    "Yidhari": pasiva_yidhari,
    "Yixuan": pasiva_yixuan,
    "Yuzuha": pasiva_yuzuha,
    "Zhao": pasiva_zhao,
    "Zhu Yuan": pasiva_zhu_yuan,
    "Sunna": pasiva_sunna,
    "Aria": pasiva_aria,
    "Nangong Yu": pasiva_nangong_yu,
    "Cissia": pasiva_cissia,
    "Promeia": pasiva_promeia,
    "Starlight - Billy": pasiva_starlight_billy,
}

CONFIG_CORE_UI = {
    "Alice": {"usa_stacks": True, "max_stacks": 300,
        "default": 300, "label": "Blade Etiquette", "label_key": "core_ui.alice.label"},
    "Piper": {"usa_stacks": True, "max_stacks": 30,
        "default": 20, "label": "Power Stacks", "label_key": "core_ui.piper_pasiva.label"},
}

CONFIG_PASIVAS_UI = {
    "Nicole": [
        {"key": "debuff_nicole_activo", "label": "¿Debuff Caja Mecánica? (-DEF)", "label_key": "pasivas.nicole.debuff", "tipo": "checkbox", "default": True}
    ],
    "Pan Yinhu": [
        {"key": "debuff_qi_activo", "label": "¿Depleted Qi Activo? (+20% DMG)", "label_key": "pasivas.pan_yinhu.depleted_qi", "tipo": "checkbox", "default": True}
    ],
    "Pulchra": [
        {"key": "debuff_binding_trap_activo", "label": "¿Trampa Vinculante Activa?", "label_key": "pasivas.pulchra.trampa", "tipo": "checkbox", "default": True}
    ],
    "Rina": [
        {"key": "enemigo_shocked", "label": "¿Enemigo bajo efecto Shock?", "label_key": "pasivas.rina.shock", "tipo": "checkbox", "default": True}
    ],
    "Seth": [
        {"key": "debuff_seth_activo", "label": "¿Debuff Res. Anomalía (20s)?", "label_key": "pasivas.seth.debuff_res", "tipo": "checkbox", "default": True}
    ],
    "Soukaku": [
        {"key": "buff_soukaku_activo", "label": "¿Fly the Flag (Vortex)? (+Ice DMG)", "label_key": "pasivas.soukaku.fly_flag", "tipo": "checkbox", "default": True}
    ],
    "Yanagi": [
        {"key": "buff_yanagi_activo", "label": "¿Cambio Postura + Básico? (+Buildup)", "label_key": "pasivas.yanagi.cambio_postura", "tipo": "checkbox", "default": True}
    ],
    "Yidhari": [
        {"key": "hp_bajo_50", "label": "¿HP < 50%?", "label_key": "pasivas.yidhari.hp_bajo", "tipo": "checkbox", "default": False},
        {"key": "velo_yidhari_activo", "label": "¿Velo Wellspring Activo?", "label_key": "pasivas.yidhari.wellspring", "tipo": "checkbox", "default": True}
    ],
    "Yixuan": [
        {"key": "meditacion_yixuan_activa", "label": "¿Estado Meditación (Ulti)?", "label_key": "pasivas.yixuan.meditacion", "tipo": "checkbox", "default": True}
    ],
    "Zhao": [
        {"key": "velo_activo", "label": "¿Está dentro del Velo Etéreo?", "label_key": "pasivas.zhao.velo_etereo", "tipo": "checkbox", "default": True}
    ],
    "Zhu Yuan": [
        {"key": "buff_zhuyuan_activo", "label": "¿Buff tras EX/Chain/Ulti?", "label_key": "pasivas.zhuyuan.buff_ex", "tipo": "checkbox", "default": True}
    ],
    "Nangong Yu": [
        {"key": "nangong_dance_prowess", "label": "¿Dance Prowess Activo? (Polarity Disorder)", "label_key": "pasivas.nangong_yu.dance_prowess", "tipo": "checkbox", "default": True},
        {"key": "nangong_misstep", "label": "¿Misstep Activo? (+30% Stun Mult)", "label_key": "pasivas.nangong_yu.misstep", "tipo": "checkbox", "default": True}
    ],
    "Promeia": [
        {"key": "promeia_ex_buff", "label": "¿Buff EX Activo? (Presumption of Guilt)", "label_key": "pasivas.promeia.ex_buff", "tipo": "checkbox", "default": True}
    ],
    "Starlight - Billy": [
    {"key": "stacks", "label": "Stacks Starlight (0-2)", "label_key": "pasivas.starlight_billy.stacks", "tipo": "numero", "default": 2, "min": 0, "max": 2}
    ],
}