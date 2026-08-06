import flet as ft
from traductor import traductor_global as i18n


def obtener_mapa_enemigos_da():
    """Genera el mapa con traducciones evaluadas en tiempo de llamada (no de import)."""
    return {
        "Notorious - Dead End Butcher": {
            "imagen": "/images/enemigos/Notorious - Dead End Butcher.png",
            "spans": [
                ft.TextSpan(i18n.t("enemigo.butcher.s1", default="• El daño que inflige la "), style=ft.TextStyle(color=ft.Colors.WHITE)),
                ft.TextSpan(i18n.t("enemigo.butcher.s2", default="Anomalía de Atributo"), style=ft.TextStyle(weight=ft.FontWeight.BOLD, color=ft.Colors.CYAN_300)),
                ft.TextSpan(i18n.t("enemigo.butcher.s3", default=" contra los jefes aumenta en un "), style=ft.TextStyle(color=ft.Colors.WHITE)),
                ft.TextSpan(i18n.t("enemigo.butcher.s4", default="50 %"), style=ft.TextStyle(weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_400)),
                ft.TextSpan(i18n.t("enemigo.butcher.s5", default=".\nCuando el Carnicero del Callejón Infame está en el estado de "), style=ft.TextStyle(color=ft.Colors.WHITE)),
                ft.TextSpan(i18n.t("enemigo.butcher.s6", default="potenciación etérea"), style=ft.TextStyle(weight=ft.FontWeight.BOLD, color=ft.Colors.PURPLE_300)),
                ft.TextSpan(i18n.t("enemigo.butcher.s7", default=", el daño que recibe se reduce en un "), style=ft.TextStyle(color=ft.Colors.WHITE)),
                ft.TextSpan(i18n.t("enemigo.butcher.s8", default="15 %"), style=ft.TextStyle(weight=ft.FontWeight.BOLD, color=ft.Colors.RED_400)),
                ft.TextSpan(i18n.t("enemigo.butcher.s9", default=" y el Aturdimiento que inflige el agente se reduce en un "), style=ft.TextStyle(color=ft.Colors.WHITE)),
                ft.TextSpan(i18n.t("enemigo.butcher.s10", default="30 %"), style=ft.TextStyle(weight=ft.FontWeight.BOLD, color=ft.Colors.RED_400)),
                ft.TextSpan(i18n.t("enemigo.butcher.s11", default="."), style=ft.TextStyle(color=ft.Colors.WHITE)),
            ],
            "opciones": [
                {"tipo": "checkbox", "label": i18n.t("enemigo.butcher.opt1", default="Estado: Potenciación Etérea"), "efectos": {"DMG_Taken": -15.0, "Aturdimiento": -30.0}},
                {"tipo": "checkbox", "label": i18n.t("enemigo.butcher.opt2", default="Buff de Escenario: Daño Anomalía +50%"), "efectos": {"Bono_Daño_Anomalia": 50.0}},
            ]
        },
        "Miasma Priest": {
            "imagen": "/images/enemigos/Miasma Priest.png",
            "spans": [
                ft.TextSpan(i18n.t("enemigo.priest.s1", default="• Cada vez que el sacerdote miasmático cambia de fase, su "), style=ft.TextStyle(color=ft.Colors.WHITE)),
                ft.TextSpan(i18n.t("enemigo.priest.s2", default="resistencia a la acumulación de Anomalía"), style=ft.TextStyle(weight=ft.FontWeight.BOLD, color=ft.Colors.CYAN_300)),
                ft.TextSpan(i18n.t("enemigo.priest.s3", default=" aumenta en un "), style=ft.TextStyle(color=ft.Colors.WHITE)),
                ft.TextSpan(i18n.t("enemigo.priest.s4", default="10 %"), style=ft.TextStyle(weight=ft.FontWeight.BOLD, color=ft.Colors.RED_400)),
                ft.TextSpan(i18n.t("enemigo.priest.s5", default=". Además, el "), style=ft.TextStyle(color=ft.Colors.WHITE)),
                ft.TextSpan(i18n.t("enemigo.priest.s6", default="Daño Crítico"), style=ft.TextStyle(weight=ft.FontWeight.BOLD, color=ft.Colors.CYAN_300)),
                ft.TextSpan(i18n.t("enemigo.priest.s7", default=" recibido aumenta en un "), style=ft.TextStyle(color=ft.Colors.WHITE)),
                ft.TextSpan(i18n.t("enemigo.priest.s8", default="30 %"), style=ft.TextStyle(weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_400)),
                ft.TextSpan(i18n.t("enemigo.priest.s9", default=". Pueden acumularse hasta "), style=ft.TextStyle(color=ft.Colors.WHITE)),
                ft.TextSpan(i18n.t("enemigo.priest.s10", default="2 cargas"), style=ft.TextStyle(weight=ft.FontWeight.BOLD, color=ft.Colors.AMBER_400)),
                ft.TextSpan(i18n.t("enemigo.priest.s11", default=" de este efecto. Cuando el escudo miasmático se rompe, se eliminan todas las cargas."), style=ft.TextStyle(color=ft.Colors.WHITE)),
            ],
            "opciones": [
                {"tipo": "dropdown", "label": i18n.t("enemigo.priest.opt1", default="Cambios de fase (Daño Crit Recibido +30% | Res Anomalía +10%)"), "max_stacks": 2, "efectos": {"Daño_crítico": 30.0, "Resistencia_Anomalía_Enemigo": 10.0}},
            ]
        },
        "Primordial Nightmare - The Creator": {
            "imagen": "/images/enemigos/Primordial Nightmare - The Creator.png",
            "spans": [
                ft.TextSpan(i18n.t("enemigo.creator.s1", default="• El daño de anomalía recibido por el jefe "), style=ft.TextStyle(color=ft.Colors.WHITE)),
                ft.TextSpan(i18n.t("enemigo.creator.s2", default="se reduce en un 30 %"), style=ft.TextStyle(weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_400)),
                ft.TextSpan(i18n.t("enemigo.creator.s3", default=". Cuando cambia del estado "), style=ft.TextStyle(color=ft.Colors.WHITE)),
                ft.TextSpan(i18n.t("enemigo.creator.s4", default="escudo miasmático"), style=ft.TextStyle(weight=ft.FontWeight.BOLD, color=ft.Colors.ORANGE_400)),
                ft.TextSpan(i18n.t("enemigo.creator.s5", default=" al estado normal, o del estado normal al estado "), style=ft.TextStyle(color=ft.Colors.WHITE)),
                ft.TextSpan(i18n.t("enemigo.creator.s6", default="escudo miasmático"), style=ft.TextStyle(weight=ft.FontWeight.BOLD, color=ft.Colors.ORANGE_400)),
                ft.TextSpan(i18n.t("enemigo.creator.s7", default=", el Daño Crítico que le infligen los agentes "), style=ft.TextStyle(color=ft.Colors.WHITE)),
                ft.TextSpan(i18n.t("enemigo.creator.s8", default="aumenta en un 20 %"), style=ft.TextStyle(weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_400)),
                ft.TextSpan(i18n.t("enemigo.creator.s9", default=". Pueden acumularse hasta 3 cargas. Al recuperarse del Aturdimiento, el número de cargas se restablece."), style=ft.TextStyle(color=ft.Colors.WHITE)),
            ],
            "opciones": [
                {"tipo": "checkbox", "label": i18n.t("enemigo.creator.opt1", default="Pasiva: Daño de Anomalía recibido -30%"), "efectos": {"Bono_Daño_Anomalia": -30.0}},
                {"tipo": "dropdown", "label": i18n.t("enemigo.creator.opt2", default="Cambios de fase (Daño Crítico Recibido +20%)"), "max_stacks": 3, "efectos": {"Daño_crítico": 20.0}},
            ]
        },
        "Discordant Solo - Vesper": {
            "imagen": "/images/enemigos/Discordant Solo - Vesper.png",
            "spans": [
                ft.TextSpan(i18n.t("enemigo.vesper.s1", default="• Cuando la solista disonante recibe un ataque, el Daño Crítico de este ataque "), style=ft.TextStyle(color=ft.Colors.WHITE)),
                ft.TextSpan(i18n.t("enemigo.vesper.s2", default="disminuye en un 40 %"), style=ft.TextStyle(weight=ft.FontWeight.BOLD, color=ft.Colors.ORANGE_400)),
                ft.TextSpan(i18n.t("enemigo.vesper.s3", default=". Cuando un agente activa o prolonga la duración de velo etéreo durante el combate, todo el equipo obtiene "), style=ft.TextStyle(color=ft.Colors.WHITE)),
                ft.TextSpan(i18n.t("enemigo.vesper.s4", default="1 carga"), style=ft.TextStyle(weight=ft.FontWeight.BOLD, color=ft.Colors.CYAN_300)),
                ft.TextSpan(i18n.t("enemigo.vesper.s5", default=" de resonancia sónica. Pueden acumularse hasta "), style=ft.TextStyle(color=ft.Colors.WHITE)),
                ft.TextSpan(i18n.t("enemigo.vesper.s6", default="3 cargas"), style=ft.TextStyle(weight=ft.FontWeight.BOLD, color=ft.Colors.AMBER_400)),
                ft.TextSpan(i18n.t("enemigo.vesper.s7", default=" de resonancia sónica. Por cada carga de resonancia sónica, la tasa de acumulación de anomalía "), style=ft.TextStyle(color=ft.Colors.WHITE)),
                ft.TextSpan(i18n.t("enemigo.vesper.s8", default="aumenta en un 8 %"), style=ft.TextStyle(weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_400)),
                ft.TextSpan(i18n.t("enemigo.vesper.s9", default=" y el daño de anomalía "), style=ft.TextStyle(color=ft.Colors.WHITE)),
                ft.TextSpan(i18n.t("enemigo.vesper.s10", default="aumenta en un 15 %"), style=ft.TextStyle(weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_400)),
                ft.TextSpan(i18n.t("enemigo.vesper.s11", default="."), style=ft.TextStyle(color=ft.Colors.WHITE)),
            ],
            "opciones": [
                {"tipo": "checkbox", "label": i18n.t("enemigo.vesper.opt1", default="Pasiva: Daño Crítico disminuye un 40%"), "efectos": {"Daño_crítico": -40.0}},
                {"tipo": "dropdown", "label": i18n.t("enemigo.vesper.opt2", default="Cargas de resonancia sónica (Acumulación +8% | Daño Anom. +15%)"), "max_stacks": 3, "efectos": {"Bono_Acumulación": 8.0, "Bono_Daño_Anomalia": 15.0}},
            ]
        },
        "The Defiler": {
            "imagen": "/images/enemigos/The Defiler.png",
            "spans": [
                ft.TextSpan(i18n.t("enemigo.defiler.s1", default="• Cuando un agente golpea a Profanadora con el apoyo defensivo, todo el equipo obtiene "), style=ft.TextStyle(color=ft.Colors.WHITE)),
                ft.TextSpan(i18n.t("enemigo.defiler.s2", default="1 carga"), style=ft.TextStyle(weight=ft.FontWeight.BOLD, color=ft.Colors.CYAN_300)),
                ft.TextSpan(i18n.t("enemigo.defiler.s3", default=" de dictamen. Cuando un agente derriba a Profanadora mientras ataca desde el aire, todo el equipo obtiene "), style=ft.TextStyle(color=ft.Colors.WHITE)),
                ft.TextSpan(i18n.t("enemigo.defiler.s4", default="4 cargas"), style=ft.TextStyle(weight=ft.FontWeight.BOLD, color=ft.Colors.CYAN_300)),
                ft.TextSpan(i18n.t("enemigo.defiler.s5", default=" de dictamen. Pueden acumularse hasta "), style=ft.TextStyle(color=ft.Colors.WHITE)),
                ft.TextSpan(i18n.t("enemigo.defiler.s6", default="6 cargas"), style=ft.TextStyle(weight=ft.FontWeight.BOLD, color=ft.Colors.AMBER_400)),
                ft.TextSpan(i18n.t("enemigo.defiler.s7", default=" de dictamen. Cada carga dura 30 s. La duración se reinicia con cada activación.\nPor cada dictamen el Daño Crítico de los agentes "), style=ft.TextStyle(color=ft.Colors.WHITE)),
                ft.TextSpan(i18n.t("enemigo.defiler.s8", default="aumenta en un 5 %"), style=ft.TextStyle(weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_400)),
                ft.TextSpan(i18n.t("enemigo.defiler.s9", default=", el Daño Físico "), style=ft.TextStyle(color=ft.Colors.WHITE)),
                ft.TextSpan(i18n.t("enemigo.defiler.s10", default="aumenta en un 5 %"), style=ft.TextStyle(weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_400)),
                ft.TextSpan(i18n.t("enemigo.defiler.s11", default=" y el Daño Eléctrico "), style=ft.TextStyle(color=ft.Colors.WHITE)),
                ft.TextSpan(i18n.t("enemigo.defiler.s12", default="aumenta en un 5 %"), style=ft.TextStyle(weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_400)),
                ft.TextSpan(i18n.t("enemigo.defiler.s13", default=".\nEl daño infligido a Profanadora por medio de Anomalía de Atributo "), style=ft.TextStyle(color=ft.Colors.WHITE)),
                ft.TextSpan(i18n.t("enemigo.defiler.s14", default="se reduce en un 25 %"), style=ft.TextStyle(weight=ft.FontWeight.BOLD, color=ft.Colors.RED_400)),
                ft.TextSpan(i18n.t("enemigo.defiler.s15", default="."), style=ft.TextStyle(color=ft.Colors.WHITE)),
            ],
            "opciones": [
                {"tipo": "checkbox", "label": i18n.t("enemigo.defiler.opt1", default="Pasiva: Daño de Anomalía recibido -25%"), "efectos": {"Bono_Daño_Anomalia": -25.0}},
                {"tipo": "dropdown", "label": i18n.t("enemigo.defiler.opt2", default="Cargas de dictamen (Daño Crít. +5% | Daño Fís/Eléc +5%)"), "max_stacks": 6, "efectos": {"Daño_crítico": 5.0, "Daño_elemental__fisico_electrico": 5.0}},
            ]
        },
        "Wandering Hunter": {
            "imagen": "/images/enemigos/Wandering Hunter.png",
            "spans": [
                ft.TextSpan(i18n.t("enemigo.hunter.s1", default="• La Defensa Base del cazador errante "), style=ft.TextStyle(color=ft.Colors.WHITE)),
                ft.TextSpan(i18n.t("enemigo.hunter.s2", default="aumenta en un 40 %"), style=ft.TextStyle(weight=ft.FontWeight.BOLD, color=ft.Colors.RED_400)),
                ft.TextSpan(i18n.t("enemigo.hunter.s3", default=" al encontrarse en el dominio miasmático. Cuando un agente golpea al cazador errante con un "), style=ft.TextStyle(color=ft.Colors.WHITE)),
                ft.TextSpan(i18n.t("enemigo.hunter.s4", default="ataque sucesivo o un contraataque"), style=ft.TextStyle(weight=ft.FontWeight.BOLD, color=ft.Colors.ORANGE_400)),
                ft.TextSpan(i18n.t("enemigo.hunter.s5", default=", le aplica "), style=ft.TextStyle(color=ft.Colors.WHITE)),
                ft.TextSpan(i18n.t("enemigo.hunter.s6", default="1 carga"), style=ft.TextStyle(weight=ft.FontWeight.BOLD, color=ft.Colors.CYAN_300)),
                ft.TextSpan(i18n.t("enemigo.hunter.s7", default=" de inestabilidad. Pueden acumularse hasta "), style=ft.TextStyle(color=ft.Colors.WHITE)),
                ft.TextSpan(i18n.t("enemigo.hunter.s8", default="5 cargas"), style=ft.TextStyle(weight=ft.FontWeight.BOLD, color=ft.Colors.AMBER_400)),
                ft.TextSpan(i18n.t("enemigo.hunter.s9", default=" de inestabilidad durante 15 s. La duración se reinicia con cada activación.\nCuando el agente golpea al cazador errante, el daño bruto del agente "), style=ft.TextStyle(color=ft.Colors.WHITE)),
                ft.TextSpan(i18n.t("enemigo.hunter.s10", default="aumenta en un 7 %"), style=ft.TextStyle(weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_400)),
                ft.TextSpan(i18n.t("enemigo.hunter.s11", default=" por cada carga de inestabilidad que tenga el objetivo."), style=ft.TextStyle(color=ft.Colors.WHITE)),
            ],
            "opciones": [
                {"tipo": "checkbox", "label": i18n.t("enemigo.hunter.opt1", default="Dominio miasmático (Defensa Base +40%)"), "efectos": {"Buff_Defensa": 0.40}},
                {"tipo": "dropdown", "label": i18n.t("enemigo.hunter.opt2", default="Cargas de inestabilidad (Daño Bruto +7%)"), "max_stacks": 5, "efectos": {"Daño_Adicional": 7.0}},
            ]
        },
        "Miasmic Fiend - Unfathomable": {
            "imagen": "/images/enemigos/Miasmic Fiend - Unfathomable.png",
            "spans": [
                ft.TextSpan(i18n.t("enemigo.fiend.s1", default="• Cuando el demonio miasmático sufre una Anomalía de Atributo, recibe un "), style=ft.TextStyle(color=ft.Colors.WHITE)),
                ft.TextSpan(i18n.t("enemigo.fiend.s2", default="8 % de Daño de Anomalía"), style=ft.TextStyle(weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_400)),
                ft.TextSpan(i18n.t("enemigo.fiend.s3", default=" adicional de los agentes. Puede acumularse hasta "), style=ft.TextStyle(color=ft.Colors.WHITE)),
                ft.TextSpan(i18n.t("enemigo.fiend.s4", default="6 veces"), style=ft.TextStyle(weight=ft.FontWeight.BOLD, color=ft.Colors.AMBER_400)),
                ft.TextSpan(i18n.t("enemigo.fiend.s5", default=". Activar el escudo miasmático elimina todas las cargas, y cada carga aumenta la eficiencia de reducción del escudo en un 2.5 %."), style=ft.TextStyle(color=ft.Colors.WHITE)),
            ],
            "opciones": [
                {"tipo": "dropdown", "label": i18n.t("enemigo.fiend.opt1", default="Cargas de Anomalía (Daño de Anomalía +8%)"), "max_stacks": 6, "efectos": {"Bono_Daño_Anomalia": 8.0}},
            ]
        },
        "Notorious - Pompey": {
            "imagen": "/images/enemigos/Notorious - Pompey.png",
            "spans": [
                ft.TextSpan(i18n.t("enemigo.pompey.s1", default="• Cuando el agente golpea al jefe con una "), style=ft.TextStyle(color=ft.Colors.WHITE)),
                ft.TextSpan(i18n.t("enemigo.pompey.s2", default="Asistencia Defensiva o Ataque en Cadena"), style=ft.TextStyle(weight=ft.FontWeight.BOLD, color=ft.Colors.CYAN_300)),
                ft.TextSpan(i18n.t("enemigo.pompey.s3", default=", le aplica 1 carga de Debilitamiento, que dura 20 s. La duración de cada carga se calcula de forma independiente. Por cada carga de Debilitamiento, el "), style=ft.TextStyle(color=ft.Colors.WHITE)),
                ft.TextSpan(i18n.t("enemigo.pompey.s4", default="Daño Crítico"), style=ft.TextStyle(weight=ft.FontWeight.BOLD, color=ft.Colors.ORANGE_400)),
                ft.TextSpan(i18n.t("enemigo.pompey.s5", default=" del agente aumenta en un "), style=ft.TextStyle(color=ft.Colors.WHITE)),
                ft.TextSpan(i18n.t("enemigo.pompey.s6", default="15 %"), style=ft.TextStyle(weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_400)),
                ft.TextSpan(i18n.t("enemigo.pompey.s7", default="."), style=ft.TextStyle(color=ft.Colors.WHITE)),
            ],
            "opciones": [
                {"tipo": "dropdown", "label": i18n.t("enemigo.pompey.opt1", default="Cargas de Debilitamiento (Daño Crítico +15%)"), "max_stacks": 10, "efectos": {"Daño_crítico": 15.0}},
            ]
        },
        "Ye Shiyuan the Thrall": {
            "imagen": "/images/enemigos/Ye Shiyuan the Thrall.png",
            "spans": [
                ft.TextSpan(i18n.t("enemigo.yeshiyuan.s1", default="• Cuando Sobek y la Sierva alternan turnos, la Sierva obtiene "), style=ft.TextStyle(color=ft.Colors.WHITE)),
                ft.TextSpan(i18n.t("enemigo.yeshiyuan.s2", default="1 carga"), style=ft.TextStyle(weight=ft.FontWeight.BOLD, color=ft.Colors.CYAN_300)),
                ft.TextSpan(i18n.t("enemigo.yeshiyuan.s3", default=" de Contrato y Autosacrificio. Pueden acumularse hasta "), style=ft.TextStyle(color=ft.Colors.WHITE)),
                ft.TextSpan(i18n.t("enemigo.yeshiyuan.s4", default="3 veces"), style=ft.TextStyle(weight=ft.FontWeight.BOLD, color=ft.Colors.AMBER_400)),
                ft.TextSpan(i18n.t("enemigo.yeshiyuan.s5", default=". Cada carga de Contrato aumenta la "), style=ft.TextStyle(color=ft.Colors.WHITE)),
                ft.TextSpan(i18n.t("enemigo.yeshiyuan.s6", default="Resistencia a la acumulación de Anomalía"), style=ft.TextStyle(weight=ft.FontWeight.BOLD, color=ft.Colors.RED_400)),
                ft.TextSpan(i18n.t("enemigo.yeshiyuan.s7", default=" de todos los atributos en un "), style=ft.TextStyle(color=ft.Colors.WHITE)),
                ft.TextSpan(i18n.t("enemigo.yeshiyuan.s8", default="15 %"), style=ft.TextStyle(weight=ft.FontWeight.BOLD, color=ft.Colors.RED_400)),
                ft.TextSpan(i18n.t("enemigo.yeshiyuan.s9", default=", y cada carga de Autosacrificio aumenta el multiplicador de daño por Aturdimiento de la Sierva en un "), style=ft.TextStyle(color=ft.Colors.WHITE)),
                ft.TextSpan(i18n.t("enemigo.yeshiyuan.s10", default="10 %"), style=ft.TextStyle(weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_400)),
                ft.TextSpan(i18n.t("enemigo.yeshiyuan.s11", default=".\nCuando la Sierva está aturdida, el Daño Crítico recibido "), style=ft.TextStyle(color=ft.Colors.WHITE)),
                ft.TextSpan(i18n.t("enemigo.yeshiyuan.s12", default="aumenta en un 50 %"), style=ft.TextStyle(weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_400)),
                ft.TextSpan(i18n.t("enemigo.yeshiyuan.s13", default="."), style=ft.TextStyle(color=ft.Colors.WHITE)),
            ],
            "opciones": [
                {"tipo": "dropdown", "label": i18n.t("enemigo.yeshiyuan.opt1", default="Cargas de turno (Res. Anomalía +15% | Mult. Aturdimiento +10%)"), "max_stacks": 3, "efectos": {"Resistencia_Anomalía_Enemigo": 15.0, "Multiplicador_Aturdimiento": 10.0}},
                {"tipo": "checkbox", "label": i18n.t("enemigo.yeshiyuan.opt2", default="Sierva Aturdida (Daño Crítico Recibido +50%)"), "efectos": {"Daño_crítico": 50.0}},
            ]
        },
        "Notorious - Marionette": {
            "imagen": "/images/enemigos/Notorious - Marionette.png",
            "spans": [
                ft.TextSpan(i18n.t("enemigo.marionette.s1", default="• El daño infligido por el jefe "), style=ft.TextStyle(color=ft.Colors.WHITE)),
                ft.TextSpan(i18n.t("enemigo.marionette.s2", default="aumenta en un 25 %"), style=ft.TextStyle(weight=ft.FontWeight.BOLD, color=ft.Colors.RED_400)),
                ft.TextSpan(i18n.t("enemigo.marionette.s3", default=".\nCuando se destruye un clon o cuando el cuerpo principal es aturdido, se le aplican "), style=ft.TextStyle(color=ft.Colors.WHITE)),
                ft.TextSpan(i18n.t("enemigo.marionette.s4", default="1 o 5 cargas"), style=ft.TextStyle(weight=ft.FontWeight.BOLD, color=ft.Colors.CYAN_300)),
                ft.TextSpan(i18n.t("enemigo.marionette.s5", default=" de Sobre hielo fino, respectivamente. Cada carga disminuye el daño que inflige el jefe en un "), style=ft.TextStyle(color=ft.Colors.WHITE)),
                ft.TextSpan(i18n.t("enemigo.marionette.s6", default="5 %"), style=ft.TextStyle(weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_400)),
                ft.TextSpan(i18n.t("enemigo.marionette.s7", default=" y aumenta el Daño de Hielo y el Daño Etéreo que recibe de los agentes en un "), style=ft.TextStyle(color=ft.Colors.WHITE)),
                ft.TextSpan(i18n.t("enemigo.marionette.s8", default="10 %"), style=ft.TextStyle(weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_400)),
                ft.TextSpan(i18n.t("enemigo.marionette.s9", default=". Las cargas se restablecen cuando el jefe se recupera del Aturdimiento."), style=ft.TextStyle(color=ft.Colors.WHITE)),
            ],
            "opciones": [
                {"tipo": "dropdown", "label": i18n.t("enemigo.marionette.opt1", default="Cargas de Sobre hielo fino (Daño Hielo/Etéreo +10%)"), "max_stacks": 5, "efectos": {"Daño_elemental__hielo_etereo": 10.0}},
            ]
        },
        "Unknown Corruption Complex": {
            "imagen": "/images/enemigos/Unknown Corruption Complex.png",
            "spans": [
                ft.TextSpan(i18n.t("enemigo.unknown.s1", default="• Al infligir suficiente daño a las piernas del jefe, se activará el Deterioro. Tras romperle las piernas con éxito, el agente recupera 1000 Decibelios y el jefe obtiene "), style=ft.TextStyle(color=ft.Colors.WHITE)),
                ft.TextSpan(i18n.t("enemigo.unknown.s2", default="1 carga"), style=ft.TextStyle(weight=ft.FontWeight.BOLD, color=ft.Colors.CYAN_300)),
                ft.TextSpan(i18n.t("enemigo.unknown.s3", default=" de Desintegración durante 20 s, hasta un máximo de "), style=ft.TextStyle(color=ft.Colors.WHITE)),
                ft.TextSpan(i18n.t("enemigo.unknown.s4", default="4 cargas"), style=ft.TextStyle(weight=ft.FontWeight.BOLD, color=ft.Colors.AMBER_400)),
                ft.TextSpan(i18n.t("enemigo.unknown.s5", default=".\nCuando los ataques del agente golpean al enemigo, por cada carga de Desintegración que tenga el objetivo, el Daño Crítico "), style=ft.TextStyle(color=ft.Colors.WHITE)),
                ft.TextSpan(i18n.t("enemigo.unknown.s6", default="aumenta en un 25 %"), style=ft.TextStyle(weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_400)),
                ft.TextSpan(i18n.t("enemigo.unknown.s7", default="."), style=ft.TextStyle(color=ft.Colors.WHITE)),
            ],
            "opciones": [
                {"tipo": "dropdown", "label": i18n.t("enemigo.unknown.opt1", default="Cargas de Desintegración (Daño Crítico +25%)"), "max_stacks": 4, "efectos": {"Daño_crítico": 25.0}},
            ]
        },
        "Sacrifice - Bringer": {
            "imagen": "/images/enemigos/Sacrifice - Bringer.png",
            "spans": [
                ft.TextSpan(i18n.t("enemigo.bringer.s1", default="• Al infligir Anomalía de Atributo o Desorden en un jefe, todos los miembros del escuadrón obtienen "), style=ft.TextStyle(color=ft.Colors.WHITE)),
                ft.TextSpan(i18n.t("enemigo.bringer.s2", default="1 carga"), style=ft.TextStyle(weight=ft.FontWeight.BOLD, color=ft.Colors.CYAN_300)),
                ft.TextSpan(i18n.t("enemigo.bringer.s3", default=" de Concentración Láser, acumulable hasta "), style=ft.TextStyle(color=ft.Colors.WHITE)),
                ft.TextSpan(i18n.t("enemigo.bringer.s4", default="6 veces"), style=ft.TextStyle(weight=ft.FontWeight.BOLD, color=ft.Colors.AMBER_400)),
                ft.TextSpan(i18n.t("enemigo.bringer.s5", default=". Cada carga de Concentración Láser aumenta el ATQ del agente en un "), style=ft.TextStyle(color=ft.Colors.WHITE)),
                ft.TextSpan(i18n.t("enemigo.bringer.s6", default="8 %"), style=ft.TextStyle(weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_400)),
                ft.TextSpan(i18n.t("enemigo.bringer.s7", default=".\nCon al menos 3 cargas, infligir una Anomalía de Atributo aumentará su duración en 5 s. Cuando Sacrifice - Bringer ataca con su Cuchillo Sacrificial, todas las cargas del escuadrón se reinician."), style=ft.TextStyle(color=ft.Colors.WHITE)),
            ],
            "opciones": [
                {"tipo": "dropdown", "label": i18n.t("enemigo.bringer.opt1", default="Cargas de Concentración Láser (ATQ +8%)"), "max_stacks": 6, "efectos": {"Ataque_%": 8.0}},
            ]
        },
        "Dead End Butcher": {
            "imagen": "/images/enemigos/Dead End Butcher.png",
            "spans": [
                ft.TextSpan(i18n.t("enemigo.normal_butcher.s1", default="• Cuando no está en estado Aturdido, el jefe obtiene "), style=ft.TextStyle(color=ft.Colors.WHITE)),
                ft.TextSpan(i18n.t("enemigo.normal_butcher.s2", default="1 carga"), style=ft.TextStyle(weight=ft.FontWeight.BOLD, color=ft.Colors.CYAN_300)),
                ft.TextSpan(i18n.t("enemigo.normal_butcher.s3", default=" de Todo o Nada cada 6 s, acumulándose hasta "), style=ft.TextStyle(color=ft.Colors.WHITE)),
                ft.TextSpan(i18n.t("enemigo.normal_butcher.s4", default="3 cargas"), style=ft.TextStyle(weight=ft.FontWeight.BOLD, color=ft.Colors.AMBER_400)),
                ft.TextSpan(i18n.t("enemigo.normal_butcher.s5", default=". Cada carga aumenta el daño que inflige el jefe en un "), style=ft.TextStyle(color=ft.Colors.WHITE)),
                ft.TextSpan(i18n.t("enemigo.normal_butcher.s6", default="10 %"), style=ft.TextStyle(weight=ft.FontWeight.BOLD, color=ft.Colors.RED_400)),
                ft.TextSpan(i18n.t("enemigo.normal_butcher.s7", default=".\nCuando el ataque de un agente golpea al enemigo, el Daño Crítico del agente "), style=ft.TextStyle(color=ft.Colors.WHITE)),
                ft.TextSpan(i18n.t("enemigo.normal_butcher.s8", default="aumenta en un 25 %"), style=ft.TextStyle(weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_400)),
                ft.TextSpan(i18n.t("enemigo.normal_butcher.s9", default=" por cada carga de Todo o Nada que tenga el objetivo. Las cargas se reinician al recuperarse del Aturdimiento."), style=ft.TextStyle(color=ft.Colors.WHITE)),
            ],
            "opciones": [
                {"tipo": "dropdown", "label": i18n.t("enemigo.normal_butcher.opt1", default="Cargas de Todo o Nada (Daño Crítico +25%)"), "max_stacks": 3, "efectos": {"Daño_crítico": 25.0}},
            ]
        },
        "Corrupted Overlord - Pompey": {
            "imagen": "/images/enemigos/Corrupted Overlord - Pompey.png",
            "spans": [
                ft.TextSpan(i18n.t("enemigo.normal_pompey.s1", default="• El jefe obtiene "), style=ft.TextStyle(color=ft.Colors.WHITE)),
                ft.TextSpan(i18n.t("enemigo.normal_pompey.s2", default="1 carga"), style=ft.TextStyle(weight=ft.FontWeight.BOLD, color=ft.Colors.CYAN_300)),
                ft.TextSpan(i18n.t("enemigo.normal_pompey.s3", default=" de Curtido en Batalla cada 10 s, lo que aumenta el daño que inflige en un "), style=ft.TextStyle(color=ft.Colors.WHITE)),
                ft.TextSpan(i18n.t("enemigo.normal_pompey.s4", default="20 %"), style=ft.TextStyle(weight=ft.FontWeight.BOLD, color=ft.Colors.RED_400)),
                ft.TextSpan(i18n.t("enemigo.normal_pompey.s5", default=" y se acumula hasta "), style=ft.TextStyle(color=ft.Colors.WHITE)),
                ft.TextSpan(i18n.t("enemigo.normal_pompey.s6", default="3 veces"), style=ft.TextStyle(weight=ft.FontWeight.BOLD, color=ft.Colors.AMBER_400)),
                ft.TextSpan(i18n.t("enemigo.normal_pompey.s7", default=".\nAl infligirle una Anomalía de Atributo, pierde 1 carga de Curtido en Batalla y el daño que recibe "), style=ft.TextStyle(color=ft.Colors.WHITE)),
                ft.TextSpan(i18n.t("enemigo.normal_pompey.s8", default="aumenta en un 15 %"), style=ft.TextStyle(weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_400)),
                ft.TextSpan(i18n.t("enemigo.normal_pompey.s9", default=" durante 20 s."), style=ft.TextStyle(color=ft.Colors.WHITE)),
            ],
            "opciones": [
                {"tipo": "checkbox", "label": i18n.t("enemigo.normal_pompey.opt1", default="Debuff de Anomalía (Daño Recibido +15%)"), "efectos": {"DMG_Taken": 15.0}},
            ]
        },
        "Autonomous Assault Unit - Typhon Destroyer": {
            "imagen": "/images/enemigos/Autonomous Assault Unit - Typhon Destroyer.png",
            "spans": [
                ft.TextSpan(i18n.t("enemigo.typhon.s1", default="• Los agentes aplican Abrumado al asestar una Asistencia Defensiva contra el jefe, y "), style=ft.TextStyle(color=ft.Colors.WHITE)),
                ft.TextSpan(i18n.t("enemigo.typhon.s2", default="3 cargas"), style=ft.TextStyle(weight=ft.FontWeight.BOLD, color=ft.Colors.CYAN_300)),
                ft.TextSpan(i18n.t("enemigo.typhon.s3", default=" de Abrumado al acumular 3 Asistencias Defensivas y activar el Deterioro. Cada carga aumenta el Aturdimiento en un "), style=ft.TextStyle(color=ft.Colors.WHITE)),
                ft.TextSpan(i18n.t("enemigo.typhon.s4", default="15 %"), style=ft.TextStyle(weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_400)),
                ft.TextSpan(i18n.t("enemigo.typhon.s5", default=", y el daño recibido de Ataques en Cadena y Definitivas (estando aturdido) en un "), style=ft.TextStyle(color=ft.Colors.WHITE)),
                ft.TextSpan(i18n.t("enemigo.typhon.s6", default="10 %"), style=ft.TextStyle(weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_400)),
                ft.TextSpan(i18n.t("enemigo.typhon.s7", default=".\nEl enemigo repara las partes deterioradas al cargar, y reiniciará sus cargas de Abrumado tras recuperarse del Aturdimiento."), style=ft.TextStyle(color=ft.Colors.WHITE)),
            ],
            "opciones": [
                {"tipo": "dropdown", "label": i18n.t("enemigo.typhon.opt1", default="Cargas de Abrumado (Aturdimiento +15% | Daño Cadena/Ulti +10%)"), "max_stacks": 3, "efectos": {"Aturdimiento": 15.0, "Daño_Cadena_Ulti": 10.0}},
            ]
        },
        "Phaethon of the Scorched Horizon": {
            "imagen": "/images/enemigos/Phaethon of the Scorched Horizon.png",
            "spans": [
                ft.TextSpan(i18n.t("enemigo.phaethon.s1", default="• Después de activar Calcinador de vendavales, obtiene "), style=ft.TextStyle(color=ft.Colors.WHITE)),
                ft.TextSpan(i18n.t("enemigo.phaethon.s2", default="5 cargas"), style=ft.TextStyle(weight=ft.FontWeight.BOLD, color=ft.Colors.CYAN_300)),
                ft.TextSpan(i18n.t("enemigo.phaethon.s3", default=" de En llamas. Cada carga aumenta el daño infligido en un "), style=ft.TextStyle(color=ft.Colors.WHITE)),
                ft.TextSpan(i18n.t("enemigo.phaethon.s4", default="10 %"), style=ft.TextStyle(weight=ft.FontWeight.BOLD, color=ft.Colors.RED_400)),
                ft.TextSpan(i18n.t("enemigo.phaethon.s5", default=" y reduce el Daño Crítico recibido en un "), style=ft.TextStyle(color=ft.Colors.WHITE)),
                ft.TextSpan(i18n.t("enemigo.phaethon.s6", default="25 %"), style=ft.TextStyle(weight=ft.FontWeight.BOLD, color=ft.Colors.RED_400)),
                ft.TextSpan(i18n.t("enemigo.phaethon.s7", default=".\nCon cargas de En llamas, cada vez que sufra una Anomalía perderá una carga, y el Daño de Floración recibido posteriormente aumentará en un "), style=ft.TextStyle(color=ft.Colors.WHITE)),
                ft.TextSpan(i18n.t("enemigo.phaethon.s8", default="10 %"), style=ft.TextStyle(weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_400)),
                ft.TextSpan(i18n.t("enemigo.phaethon.s9", default=" durante 15 s (hasta un máximo de "), style=ft.TextStyle(color=ft.Colors.WHITE)),
                ft.TextSpan(i18n.t("enemigo.phaethon.s10", default="3 cargas"), style=ft.TextStyle(weight=ft.FontWeight.BOLD, color=ft.Colors.AMBER_400)),
                ft.TextSpan(i18n.t("enemigo.phaethon.s11", default="). Al activarse de nuevo, se reinicia la duración."), style=ft.TextStyle(color=ft.Colors.WHITE)),
            ],
            "opciones": [
                {"tipo": "dropdown", "label": i18n.t("enemigo.phaethon.opt1", default="Cargas de En llamas (Daño Crítico Recibido -25%)"), "max_stacks": 5, "efectos": {"Daño_crítico": -25.0}},
                {"tipo": "dropdown", "label": i18n.t("enemigo.phaethon.opt2", default="Debuff por Anomalía (Daño de Floración +10%)"), "max_stacks": 3, "efectos": {"Abloom_dmg": 10.0}},
            ]
        },
        "Sanguine Sweeper": {
            "imagen": "/images/enemigos/Sanguine Sweeper.png",
            "spans": [
                ft.TextSpan(i18n.t("enemigo.sanguine.s1", default="• Mientras la Barrera Corruptiva está activa, el Daño de Anomalía infligido por los agentes "), style=ft.TextStyle(color=ft.Colors.WHITE)),
                ft.TextSpan(i18n.t("enemigo.sanguine.s2", default="aumenta en un 50 %"), style=ft.TextStyle(weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_400)),
                ft.TextSpan(i18n.t("enemigo.sanguine.s3", default=" y la acumulación de Anomalía "), style=ft.TextStyle(color=ft.Colors.WHITE)),
                ft.TextSpan(i18n.t("enemigo.sanguine.s4", default="aumenta en un 30 %"), style=ft.TextStyle(weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_400)),
                ft.TextSpan(i18n.t("enemigo.sanguine.s5", default=".\nCuando el jefe está "), style=ft.TextStyle(color=ft.Colors.WHITE)),
                ft.TextSpan(i18n.t("enemigo.sanguine.s6", default="Aturdido"), style=ft.TextStyle(weight=ft.FontWeight.BOLD, color=ft.Colors.ORANGE_400)),
                ft.TextSpan(i18n.t("enemigo.sanguine.s7", default=", el Daño de Anomalía recibido aumenta en un "), style=ft.TextStyle(color=ft.Colors.WHITE)),
                ft.TextSpan(i18n.t("enemigo.sanguine.s8", default="15 %"), style=ft.TextStyle(weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_400)),
                ft.TextSpan(i18n.t("enemigo.sanguine.s9", default=" y la acumulación de Anomalía aumenta en un "), style=ft.TextStyle(color=ft.Colors.WHITE)),
                ft.TextSpan(i18n.t("enemigo.sanguine.s10", default="15 %"), style=ft.TextStyle(weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_400)),
                ft.TextSpan(i18n.t("enemigo.sanguine.s11", default=".\nCuando el jefe "), style=ft.TextStyle(color=ft.Colors.WHITE)),
                ft.TextSpan(i18n.t("enemigo.sanguine.s12", default="no está Aturdido"), style=ft.TextStyle(weight=ft.FontWeight.BOLD, color=ft.Colors.RED_400)),
                ft.TextSpan(i18n.t("enemigo.sanguine.s13", default=", el daño que recibe se reduce en un "), style=ft.TextStyle(color=ft.Colors.WHITE)),
                ft.TextSpan(i18n.t("enemigo.sanguine.s14", default="15 %"), style=ft.TextStyle(weight=ft.FontWeight.BOLD, color=ft.Colors.RED_400)),
                ft.TextSpan(i18n.t("enemigo.sanguine.s15", default="."), style=ft.TextStyle(color=ft.Colors.WHITE)),
            ],
            "opciones": [
                {"tipo": "checkbox", "label": i18n.t("enemigo.sanguine.opt1", default="Barrera Corruptiva activa (Daño Anom +50% | Acum. +30%)"), "efectos": {"Bono_Daño_Anomalia": 50.0, "Bono_Acumulación": 30.0}},
                {"tipo": "checkbox", "label": i18n.t("enemigo.sanguine.opt2", default="Jefe Aturdido (Daño Anom. Recibido +15% | Acum. +15%)"), "efectos": {"Bono_Daño_Anomalia": 15.0, "Bono_Acumulación": 15.0}},
                {"tipo": "checkbox", "label": i18n.t("enemigo.sanguine.opt3", default="Jefe No Aturdido (Daño Recibido -15%)"), "efectos": {"DMG_Taken": -15.0}},
            ]
        },
    }


MAPA_ENEMIGOS_DA = None
