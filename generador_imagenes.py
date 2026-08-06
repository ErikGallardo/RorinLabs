import os
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageFilter

class GeneradorTarjetas:
    def __init__(self, ruta_recursos):
        self.ruta_recursos = ruta_recursos
        try:
            self.f_titulo = ImageFont.truetype("arialbd.ttf", 40)
            self.f_rank = ImageFont.truetype("BebasNeue-Regular.ttf", 140)
            self.f_agente = ImageFont.truetype("arialbd.ttf", 30)
            self.f_wengine = ImageFont.truetype("arialbd.ttf", 16)
            self.f_stats = ImageFont.truetype("arialbd.ttf", 24)
            self.f_chica = ImageFont.truetype("arial.ttf", 16)
            self.f_subs = ImageFont.truetype("arialbd.ttf", 16)
        except:
            self.f_titulo = ImageFont.load_default()
            self.f_stats = ImageFont.load_default()
            self.f_chica = ImageFont.load_default()

    def generar_build_card(self, datos, ruta_salida=None):
        """
        Genera una build card.
        Args:
            datos: Diccionario con los datos de la build
            ruta_salida: Si es None, retorna (True, BytesIO) para descarga web.
                        Si es un string, guarda el archivo normalmente.
        """
        from logica_recomendaciones import EXCEPCIONES_AGENTES, CONFIG_ROLES

        def dibujar_parrafo_justificado(texto, fuente, x_caja, y_caja, ancho_caja, alto_caja, draw_obj, color_base="white", max_lineas=5):
            import re
            if not texto: return
            
            stats_keywords = [
                "DMG", "ATK", "HP", "DEF", "CRIT", "Anomaly", "Impact", 
                "Energy", "PEN", "Proficiency", "Mastery", "RES", "Rate",
                "increases", "increase", "reducing", "reduces", "bonus", "Daze",
                "Buildup", "Stun", "Shield", "Physical", "Electric", "Fire", 
                "Ice", "Ether", "Sheer", "Disorder", "Ultimate", "Special",
                "Chain", "Basic", "Dash", "Freeze", "Shatter", "Assault",
                "Shocked", "Burning", "Corruption"
            ]
            
            # 1. Separar el texto en palabras y crear líneas basadas en el tamaño real en píxeles
            palabras = texto.split()
            lineas = []
            linea_actual = []
            ancho_actual = 0
            espacio_normal = draw_obj.textlength(" ", font=fuente)
            
            for palabra in palabras:
                ancho_palabra = draw_obj.textlength(palabra, font=fuente)
                if not linea_actual:
                    linea_actual.append(palabra)
                    ancho_actual = ancho_palabra
                else:
                    if ancho_actual + espacio_normal + ancho_palabra <= ancho_caja:
                        linea_actual.append(palabra)
                        ancho_actual += espacio_normal + ancho_palabra
                    else:
                        lineas.append(linea_actual)
                        linea_actual = [palabra]
                        ancho_actual = ancho_palabra
            if linea_actual:
                lineas.append(linea_actual)
                
            lineas = lineas[:max_lineas] # Respetar el límite de líneas
            
            # 2. Calcular centrado vertical de todo el bloque
            alto_linea = fuente.size + 4 
            alto_total = len(lineas) * alto_linea
            y_actual = y_caja + (alto_caja - alto_total) // 2 
            
            # 3. Dibujar calculando el justificado
            for i, linea in enumerate(lineas):
                es_ultima_linea = (i == len(lineas) - 1)
                
                # Si es una sola palabra o la última línea, se centra normalmente
                if len(linea) == 1 or es_ultima_linea:
                    ancho_linea = sum(draw_obj.textlength(p, font=fuente) for p in linea) + espacio_normal * (len(linea) - 1)
                    x_actual = x_caja + (ancho_caja - ancho_linea) / 2
                    espacio_extra = espacio_normal
                else:
                    # Magia del justificado: estirar los espacios
                    ancho_palabras = sum(draw_obj.textlength(p, font=fuente) for p in linea)
                    espacios_libres = ancho_caja - ancho_palabras
                    espacio_extra = espacios_libres / (len(linea) - 1)
                    x_actual = x_caja
                    
                for p in linea:
                    es_stat = any(k.lower() in p.lower() for k in stats_keywords)
                    tiene_numero_pct = bool(re.search(r'\d+%', p))
                    color = "#FFD700" if (es_stat or tiene_numero_pct) else color_base
                    
                    draw_obj.text((x_actual, y_actual), p, fill=color, font=fuente, anchor="lt")
                    x_actual += draw_obj.textlength(p, font=fuente) + espacio_extra
                    
                y_actual += alto_linea

        def ajustar_imagen(img, ancho_max, alto_max):
            img.thumbnail((ancho_max, alto_max), Image.Resampling.LANCZOS)
            fondo = Image.new("RGBA", (ancho_max, alto_max), (0, 0, 0, 0))
            x = (ancho_max - img.width) // 2
            y = (alto_max - img.height) // 2
            fondo.paste(img, (x, y), img)
            return fondo

        def normalizar_stat(k):
            import unicodedata
            
            k = str(k).lower().strip()
            k = ''.join(c for c in unicodedata.normalize('NFD', k) if unicodedata.category(c) != 'Mn')
            
            es_pct = "%" in k or "porcentual" in k or "tasa" in k or "prob" in k or "dano" in k or "recup" in k
            sfx = "_porcentual" if es_pct else "_plano"
            b = k.replace("porcentual","").replace("plano","").replace("_","").replace("%","").replace("+","")
            b = "".join(c for c in b if not c.isdigit()).strip()
            
            if "ataque" in b or "atk" in b:        return "Ataque" + sfx
            if "vida"  in b or "hp" in b:          return "Puntos_Vida" + sfx
            if "defensa" in b or "def" in b:       return "Defensa" + sfx
            if "maestria" in b or "anomalia" in b: return "Maestria_Anomalia_plano"
            if "prob" in b:                        return "Probabilidad_critico_porcentual"
            if ("dano" in b or "dao" in b) and "crit" in b: return "Dano_critico_porcentual"
            
            # 👇 AQUÍ ESTÁ EL FIX 👇
            if "pen" in b or "perf" in b:          return "Tasa_de_Perforacion_porcentual" if ("ratio" in b or es_pct) else "Perforacion_Plana_plano"
            
            if "recup" in b or "energy" in b:      return "Recuperacion_energia_porcentual"
            
            return "Desconocido"
            
        def formatear_stat(texto):
            # Quitamos los guiones bajos y ponemos formato Título (Primera Letra Mayúscula)
            import unicodedata
            
            # Limpiamos tildes por si acaso llega algo como "Daño" o "Crítico"
            t = str(texto).strip()
            t = ''.join(c for c in unicodedata.normalize('NFD', t) if unicodedata.category(c) != 'Mn')
            t = t.replace("_", " ").title()
            
            # Diccionario Mágico: Traduce del español/interno al Inglés de ZZZ
            remplazos = {
                "Porcentual": "%", 
                "Plano": "", 
                "Plana": "",
                "Dano Critico": "CRIT DMG",
                "Dao Critico": "CRIT DMG",
                "Probabilidad Critico": "CRIT RATE",
                "Prob. Critica": "CRIT RATE",
                "Prob. Critico": "CRIT RATE",
                "Probabilidad Crítico": "CRIT RATE",
                "Probabilidad": "CRIT RATE",
                "Maestria Anomalia": "Anomaly Prof.",
                "Maestria": "Anomaly Prof.",
                "Recuperacion Energia": "Energy Regen",
                "Puntos Vida": "HP",
                "Vida": "HP",
                "Perforacion": "PEN",
                "Ataque": "ATK",
                "Defensa": "DEF",
                "Impacto": "Impact"
            }
            
            # Aplicamos las traducciones
            for k, v in remplazos.items():
                t = t.replace(k, v)
                
            # Limpieza final: Quita espacios dobles y pega el "%" a la letra
            t = t.replace("  ", " ").replace(" %", "%").strip()
            
            return t

        def calcular_rolls_sub(nombre_sub, valor_sub):
            try:
                val = float(str(valor_sub).replace("%","").replace(",",".").strip())
                n = nombre_sub.lower()
                base = 3.0
                if "crit" in n:
                    base = 4.8 if ("dmg" in n or "dano" in n) else 2.4
                elif "def" in n:  base = 4.8 if "%" in str(valor_sub) else 15
                elif "pen" in n or "perf" in n:  base = 2.4 if "%" in str(valor_sub) else 9 # <-- AQUÍ ESTÁ EL FIX
                elif "maestr" in n or "prof" in n: base = 9.0
                elif "impact" in n: base = 18.0
                
                if base == 3.0 and "%" not in str(valor_sub):
                    if "ataque" in n or "atk" in n: base = 19
                    elif "vida" in n or "hp" in n:  base = 112
                return max(1, int(round(val / base)))
            except Exception:
                return 1

        def score_disco_fn(subs_lista, ideales_n, decentes_n):
            n_id   = max(1, len(ideales_n))
            mult_i = 1.20 if n_id == 1 else (1.02 if n_id == 2 else 1.0)
            mult_d = 0.95 if n_id == 1 else (0.80 if n_id == 2 else 0.75)
            sc = 1.0
            for sub in subs_lista:
                nm = sub.get("nombre", "")
                vl = sub.get("valor", "0")
                cl = normalizar_stat(nm)
                r  = calcular_rolls_sub(nm, vl)
                if cl in ideales_n:    sc += r * mult_i
                elif cl in decentes_n: sc += r * mult_d
            return sc

        def tier_from_score(sc):
            if sc >= 8.5: return "GOD",      "#ff003c"
            if sc >= 8.0: return "PERFECT",  "#00ffff"
            if sc >= 7.0: return "SSS",      "#ffea00"
            if sc >= 6.0: return "SS",       "#00ff2a"
            if sc >= 5.0: return "S",        "#ff6d00"
            if sc >= 4.0: return "A",        "#d500f9"
            if sc >= 3.0: return "B",        "#2979ff"
            if sc >= 2.0: return "C",        "#00e676"
            return "MID", "#888888"

        nivel_mindscape = int(datos.get("mindscapes", datos.get("mindscape", 0)))

        IMG_ANCHO, IMG_ALTO   = 1600, 1500
        ARMA_ANCHO,   ARMA_ALTO   = 120, 120
        ICONO_ELEM_TAM = 36

        _fp = lambda name: os.path.join(self.ruta_recursos, name)

        try:
            f_agente     = ImageFont.truetype(_fp("BarlowCondensed-Bold.ttf"), 65)
            f_wengine    = ImageFont.truetype(_fp("BarlowCondensed-Bold.ttf"), 45)
            f_arma_nom   = ImageFont.truetype(_fp("BebasNeue-Regular.ttf"), 45)
            f_nickname   = ImageFont.truetype(_fp("BebasNeue-Regular.ttf"), 45)
            f_uid        = ImageFont.truetype(_fp("BebasNeue-Regular.ttf"), 24)
            f_stats      = ImageFont.truetype(_fp("DMSans-Regular.ttf"), 28)
            f_subs       = ImageFont.truetype(_fp("DMSans-Regular.ttf"), 19)
            f_tier       = ImageFont.truetype(_fp("ShadowsIntoLight-Regular.ttf"), 30)
            f_eval       = ImageFont.truetype(_fp("ShadowsIntoLight-Regular.ttf"), 52)
            
            f_slot_num   = ImageFont.truetype(_fp("BebasNeue-Regular.ttf"), 50)
            f_set_name   = ImageFont.truetype(_fp("BarlowCondensed-Bold.ttf"), 18)
            f_main_stat  = ImageFont.truetype(_fp("DMSans-Regular.ttf"), 18)
        except Exception as e:
            f_agente = f_wengine = f_arma_nom = f_nickname = f_uid = f_stats = f_subs = ImageFont.load_default()
            f_tier = f_eval = f_slot_num = f_set_name = f_main_stat = ImageFont.load_default()

        try:
            nombre_agente   = datos.get("agente", "default")
            elemento_bruto  = str(datos.get("elemento", "fisico")).lower()
            elemento_limpio = elemento_bruto
            for orig, rep in [("e\u0301","e"),("i\u0301","i"),("\xe9","e"),("\xed","i")]:
                elemento_limpio = elemento_limpio.replace(orig, rep)

            colores_elem = {
                "electrico":(6,131,255),"etereo":(211,52,120),
                "fisico":(250,156,0),"fuego":(242,31,4),"hielo":(1,189,252),
            }
            if   nombre_agente == "Yixuan":       r_f,g_f,b_f = 204,147,57
            elif nombre_agente == "Ye Shunguang": r_f,g_f,b_f = 136,138,254
            elif nombre_agente == "Miyabi":        r_f,g_f,b_f = 1,187,253
            else:                                  r_f,g_f,b_f = colores_elem.get(elemento_limpio,(18,19,23))

            lienzo = Image.new("RGBA", (IMG_ANCHO, IMG_ALTO), (r_f,g_f,b_f,255))
            draw   = ImageDraw.Draw(lienzo)

            # Capas base
            ruta_p = os.path.join(self.ruta_recursos,"images","builds","plantilla_base.png")
            if os.path.exists(ruta_p):
                pl = Image.open(ruta_p).convert("RGBA").resize((IMG_ANCHO,IMG_ALTO))
                lienzo.paste(pl,(0,0),pl)

            COLORES_AGENTES = {"Nicole":"#FF7CA4","Anby":"#DCF921","Billy":"#FF3B3B","Nekomata":"#F6553B","Koleda":"#FF7A1A",
                               "Anton":"#FF7A1A","Ben":"#F9951B","Grace":"#FF7B4A","Lycaon":"#C6E0E5","Rina":"#E83445",
                               "Ellen":"#FC3576","Corin":"#C86BFF","Zhu Yuan":"#33B5FF","Qingyi":"#00F5BE","Seth":"#6FA8FF",
                               "Jane":"#FD3476","Caesar":"#E6C76B","Lighter":"#FF5A4F","Lucy":"#F5B635","Burnice":"#E6C76B",
                               "Piper":"#FFBC01","Pulchra":"#FFA94D","Miyabi":"#1DC0C5","Yanagi":"#FD7388","Harumasa":"#FFCC00",
                               "Soukaku":"#00E4FF","Astra Yao":"#FF3A5A","Evelyn":"#B69AE4","Soldier 0 - Anby":"#FEBF25",
                               "Hugo":"#FF3D57","Vivian":"#9A7BFF","Orphie & Magus":"#E72D50","Trigger":"#FDC821","Soldier 11":"#FFE34D",
                               "Seed":"#FFD24D","Yixuan":"#FFD966","Ye Shunguang":"#FF6A3D","Ju Fufu":"#FF9000","Pan Yinhu":"#FDCB7A",
                               "Yuzuha":"#F43638","Alice":"#FDD07C","Manato":"#FF4A3A","Lucia":"#19CBE4","Yidhari":"#B266FF",
                               "Dialyn":"#6EFCEB","Banyue":"#E8C98A","Zhao":"#FF6993","Sunna":"#D5FF63","Aria":"#FE678A",
                               "Nangong Yu":"#A872EB", "Cissia": "#EB348E", "Promeia": "#8449EF", "Starlight - Billy": "#C5454A"}
            hex_c = COLORES_AGENTES.get(nombre_agente,"#505050").lstrip("#")
            r_ag,g_ag,b_ag = tuple(int(hex_c[i:i+2],16) for i in (0,2,4))
            draw.rectangle([22,120,339,750], fill=(r_ag,g_ag,b_ag,250))

            ruta_g = os.path.join(self.ruta_recursos,"images","builds","Gradiante.png")
            if os.path.exists(ruta_g):
                gr = Image.open(ruta_g).convert("RGBA").resize((IMG_ANCHO,IMG_ALTO))
                lienzo.paste(gr,(0,0),gr)

            # =========================================================================
            # NUEVO SISTEMA DE RENDERIZADO DEL AGENTE - POSICIÓN DESDE ESQUINA INFERIOR DERECHA
            # =========================================================================
            ajustes_agentes = {
                "Alice": (50, 35, 1.00), "Anby": (-35, 130, 1.15), "Anton": (10, 25, 1.10),
                "Aria": (30, 25, 0.95), "Astra Yao": (30, 45, 1.10), "Banyue": (50, 35, 1.00),
                "Ben": (65, 200, 1.15), "Billy": (10, 65, 1.10), "Burnice": (00, 75, 1.20),
                "Caesar": (-10, 135, 1.20), "Cissia": (0, 105, 1.20), "Corin": (-20, 135, 1.20),
                "Dialyn": (30, 35, 1.00), "Ellen": (-30, 130, 1.30), "Evelyn": (0, 70, 1.20),
                "Grace": (35, 70, 0.75), "Harumasa": (0, 65, 1.20), "Hugo": (-30, 5, 1.10),
                "Jane": (40,-5, 1.00), "Ju Fufu": (80, 95, 1.10), "Koleda": (20, 180, 1.20),
                "Lighter": (20, -10, 0.90), "Lucia": (80, 55, 1.00), "Lucy": (-20, 170, 1.20),
                "Lycaon": (0, 85, 1.25), "Manato": (40, 35, 1.15), "Miyabi": (20, 75, 1.25),
                "Nangong Yu": (0, 135, 1.10), "Nekomata": (0, 135, 1.00), "Nicole": (-10, 45, 1.00),
                "Orphie & Magus": (60, 105, 1.02), "Pan Yinhu": (50, 125, 1.10), "Piper": (70, 125, 0.8),
                "Pulchra": (30, 85, 1.10), "Promeia": (30, 35, 1.10),  "Qingyi": (20, 65, 1.00), 
                "Rina": (40, 125, 1.20),
                "Seed": (0, 0, 0.85), "Seth": (20, 45, 1.20), "Soldier 0 - Anby": (20, 35, 1.00),
                "Soldier 11": (0, 20, 0.85), "Soukaku": (-20, 135, 1.20), "Sunna": (0, 35, 0.80),
                "Trigger": (40, 55, 1.00), "Vivian": (0, 25, 1.10), "Yanagi": (100, 125, 1.15),
                "Ye Shunguang": (40, 105, 1.15), "Yidhari": (50, 25, 1.00), "Yixuan": (-10, 105, 1.20),
                "Yuzuha": (-10, 65, 1.0), "Zhao": (35, 180, 1.25), "Zhu Yuan": (10, 35, 0.80), 
            }
            ruta_ag = os.path.join(self.ruta_recursos,"images","builds",f"{nombre_agente}.png")
            if os.path.exists(ruta_ag):
                ag_img = Image.open(ruta_ag).convert("RGBA")
                offset_x, offset_y, escala = ajustes_agentes.get(nombre_agente, (0, 0, 1.0))
                
                # Dimensiones de la caja contenedora
                box_w, box_h = 420, 975
                ratio = min(box_w / ag_img.width, box_h / ag_img.height)
                
                # Aplicar escala
                w_escalado = int(ag_img.width * ratio * escala)
                h_escalado = int(ag_img.height * ratio * escala)
                ag_img = ag_img.resize((w_escalado, h_escalado), Image.Resampling.LANCZOS)
                
                # Sistema de posicionamiento desde esquina INFERIOR IZQUIERDA de la caja del agente
                # Caja del agente: X desde 20 hasta 440 (ancho 420px)
                base_x_izq = 20          # Borde izquierdo de la caja del agente
                base_y_piso = 850        # Piso del agente (Y desde arriba)
                
                # offset_x positivo = mueve a la DERECHA, negativo = a la IZQUIERDA
                # offset_y positivo = mueve ARRIBA desde el piso
                # Centramos la imagen horizontalmente en la caja y aplicamos offset
                final_x = base_x_izq + (box_w - w_escalado) // 2 + offset_x - 60
                final_y = base_y_piso - h_escalado - offset_y + 60
                
                lienzo.paste(ag_img, (final_x, final_y), ag_img)
            # =========================================================================

            for png in ["Texto_Build.png","Texto_Build.PNG","Capa superior.png"]:
                ruta_lay = os.path.join(self.ruta_recursos,"images","builds",png)
                if os.path.exists(ruta_lay):
                    lay = Image.open(ruta_lay).convert("RGBA").resize((IMG_ANCHO,IMG_ALTO))
                    lienzo.paste(lay,(0,0),lay)

            # =========================================================================
            # W-ENGINE: Icono + Nombre + Descripción de Pasiva
            # =========================================================================
            nombre_arma = datos.get("wengine","default")
            
            # 1. IMAGEN W-ENGINE
            # Caja: X de 1036 a 1185 (ancho 149) | Y de 166 a 315 (alto 149)
            ARMA_ANCHO, ARMA_ALTO = 149, 149
            cx_arma = 1036 + (1185 - 1036) // 2
            cy_arma = 166 + (315 - 166) // 2
            
            ruta_arma = os.path.join(self.ruta_recursos,"images","wengine",f"{nombre_arma}.png")
            if os.path.exists(ruta_arma):
                arm = ajustar_imagen(Image.open(ruta_arma).convert("RGBA"), ARMA_ANCHO, ARMA_ALTO)
                lienzo.paste(arm, (cx_arma - ARMA_ANCHO//2, cy_arma - ARMA_ALTO//2), arm)
            
            # 2. NOMBRE W-ENGINE (Centrado completamente)
            # Caja: X de 484 a 947 | Y de 160 a 218
            cx_arma_nom = 484 + (947 - 484) // 2  # Centro X exacto (715)
            cy_arma_nom = 160 + (218 - 160) // 2  # Centro Y exacto (189)
            
            nombre_arma_txt = str(nombre_arma).replace("_", " ").title()
            draw.text((cx_arma_nom, cy_arma_nom), nombre_arma_txt, fill="white", font=f_arma_nom, anchor="mm")
            
            # 3. REFINAMIENTO (RX)
            # Caja: X de 959 a 1021 | Y de 267 a 299
            cx_ref = 959 + (1021 - 959) // 2
            cy_ref = 268 + (299 - 267) // 2
            
            raw_ref = str(datos.get("refinamiento",datos.get("refinement",datos.get("rank","1")))).upper().replace("R","")
            
            try:
                # Usamos la fuente Bebas ajustada
                f_ref = ImageFont.truetype(_fp("BebasNeue-Regular.ttf"), 28)
            except Exception:
                f_ref = ImageFont.load_default()
                
            draw.text((cx_ref, cy_ref), f"R{raw_ref}", fill="white", font=f_wengine , anchor="mm")
            
            # 4. DESCRIPCIÓN PASIVA DESDE CSV
            descripcion_pasiva = ""
            print(f"🔎 DEBUG: Python está buscando: '{nombre_arma}'")
            
            try:
                ruta_csv_pasivas = os.path.join(self.ruta_recursos, "wengine_passives.csv")
                if os.path.exists(ruta_csv_pasivas):
                    import csv
                    import re
                    # IMPORTANTE: Cambiamos 'utf-8' por 'utf-8-sig' para ignorar caracteres invisibles de Excel
                    with open(ruta_csv_pasivas, 'r', encoding='utf-8-sig') as f:
                        reader = csv.DictReader(f)
                        
                        for row in reader:
                            # Extraemos de forma segura
                            arma_csv = row.get('nombre_arma', '')
                            if arma_csv:
                                arma_csv = arma_csv.strip()
                            
                            if arma_csv == nombre_arma:
                                descripcion_pasiva = row.get('descripcion_pasiva', '').strip()
                                break
            except Exception as e:
                print(f"Error cargando pasivas de armas: {e}")
            
            # Caja: X de 486 a 944 (ancho 458) | Y de 231 a 317 (alto 86)
            if descripcion_pasiva:
                try:
                    f_pasiva = ImageFont.truetype(_fp("DMSans-Regular.ttf"), 14)
                except Exception:
                    f_pasiva = ImageFont.load_default()
                
                # ¡Una sola línea hace todo el trabajo de justificado y color!
                dibujar_parrafo_justificado(
                    texto=descripcion_pasiva, 
                    fuente=f_pasiva, 
                    x_caja=486, y_caja=233, 
                    ancho_caja=458, alto_caja=86, 
                    draw_obj=draw, color_base="white", max_lineas=5
                )
                
                # Función para colorear stats importantes
                
            nombre_base = str(nombre_agente).upper()
            
            nombres_completos = {
                "ALICE": "ALICE THYMEFIELD","ANBY": "ANBY DEMARA", "NICOLE": "NICOLE DEMARA", "BILLY": "BILLY KID",
                "ANTON": "ANTON IVANOV", "BEN": "BEN BIGGER", "GRACE": "GRACE HOWARD",
                "KOLEDA": "KOLEDA BELOBOG", "CORIN": "CORIN WICKES", "LYCAON": "VON LYCAON",
                "ELLEN": "ELLEN JOE", "SETH": "SETH LOWELL", "JANE": "JANE DOE",
                "CAESAR": "CAESAR KING", "BURNICE": "BURNICE WHITE", "PIPER": "PIPER WHEEL",
                "MIYABI": "HOSHIMI MIYABI", "YANAGI": "TSUKISHIRO YANAGI", 
                "HARUMASA": "ASABA HARUMASA", "LUCY": "LUCIANA DE MONTEFIO", "RINA": "ALEXANDRINA",
                "NEKOMATA": "NEKOMIYA MATA", "PULCHRA": "PULCHRA FELLINI", "EVELYN": "EVELYN CHEVALIER",
                "MANATO": "KOMANO MANATO", "YUZUHA": "UKINAMI YUZUHA", "LUCIA": "LUCIA ELOWEN", "HUGO": "HUGO VLAD",
                "ORPHIE & MAGUS": "ORPHIE MAGNUSSON & MAGUS"
            }
            nombre_full = nombres_completos.get(nombre_base, nombre_base)
            
            # 👇 LISTA VIP: Agentes que NUNCA deben separarse en dos líneas
            excepciones_una_linea = [
                "JU FUFU", "ASTRA YAO", "ZHU YUAN", "YE SHUNGUANG", "PAN YINHU", "NANGONG YU", "SOLDIER 11"
            ]
            
            linea1, linea2 = nombre_full, ""
            
            # Lógica de corte inteligente (ahora con el filtro VIP primero)
            if nombre_full in excepciones_una_linea:
                linea1 = nombre_full
                linea2 = ""
            elif " - " in nombre_full:
                partes = nombre_full.split(" - ")
                linea1 = partes[0].strip()
                linea2 = partes[1].strip()
            elif "&" in nombre_full:
                partes = nombre_full.split("&")
                linea1 = partes[0].strip()
                linea2 = "& " + partes[1].strip()
            elif " " in nombre_full:
                palabras = nombre_full.split()
                mitad = (len(palabras) + 1) // 2 
                linea1 = " ".join(palabras[:mitad])
                linea2 = " ".join(palabras[mitad:])
                
            # Variables de tu caja
            caja_w = 231  
            caja_h = 86   
            centro_y = 789 + (caja_h // 2)
            
            try:
                if not linea2:
                    tam = 65
                    f_nom = ImageFont.truetype(_fp("BarlowCondensed-Bold.ttf"), tam)
                    while draw.textlength(linea1, font=f_nom) > caja_w and tam > 15:
                        tam -= 2
                        f_nom = ImageFont.truetype(_fp("BarlowCondensed-Bold.ttf"), tam)
                    draw.text((66, centro_y), linea1, fill="white", font=f_nom, anchor="lm")
                
                else:
                    tam1 = 60 
                    tam2 = 40 
                    
                    f_nom1 = ImageFont.truetype(_fp("BarlowCondensed-Bold.ttf"), tam1)
                    f_nom2 = ImageFont.truetype(_fp("BarlowCondensed-Bold.ttf"), tam2)
                    
                    while draw.textlength(linea1, font=f_nom1) > caja_w and tam1 > 15:
                        tam1 -= 2
                        f_nom1 = ImageFont.truetype(_fp("BarlowCondensed-Bold.ttf"), tam1)
                        
                    while draw.textlength(linea2, font=f_nom2) > caja_w and tam2 > 10:
                        tam2 -= 2
                        f_nom2 = ImageFont.truetype(_fp("BarlowCondensed-Bold.ttf"), tam2)
                        
                    espaciado = 2
                    alto_total = tam1 + tam2 + espaciado
                    
                    while alto_total > caja_h and tam1 > 15 and tam2 > 10:
                        tam1 -= 2
                        tam2 -= 2
                        f_nom1 = ImageFont.truetype(_fp("BarlowCondensed-Bold.ttf"), tam1)
                        f_nom2 = ImageFont.truetype(_fp("BarlowCondensed-Bold.ttf"), tam2)
                        alto_total = tam1 + tam2 + espaciado
                    
                    y_inicio = 789 + (caja_h - alto_total) // 2
                    
                    draw.text((66, y_inicio), linea1, fill="white", font=f_nom1, anchor="lt")
                    draw.text((66, y_inicio + tam1 + espaciado), linea2, fill="#e0e0e0", font=f_nom2, anchor="lt")
                    
            except Exception:
                f_nom_def = ImageFont.load_default()
                texto_final = f"{linea1}\n{linea2}" if linea2 else linea1
                draw.text((66, centro_y), texto_final, fill="white", font=f_nom_def, anchor="lm")

            nickname = str(datos.get("nickname",""))
            if nickname and nickname != "Jugador":
                draw.text((IMG_ANCHO//2,56), nickname, fill="black", font=f_nickname, anchor="ma")

            uid_j = str(datos.get("uid",""))
            if uid_j and uid_j.strip() and uid_j != "Sin UID":
                draw.text((1268,68), uid_j, fill="black", font=f_uid, anchor="la")

            nivel_str = str(datos.get("nivel_agente", "1"))
            
            cx_nivel = 97
            cy_nivel = 903
            
            try:
                f_nivel = ImageFont.truetype(_fp("BebasNeue-Regular.ttf"), 20)
            except Exception:
                f_nivel = ImageFont.load_default()
                
            draw.text((cx_nivel, cy_nivel), f"Lvl. {nivel_str}", fill="white", font=f_nivel, anchor="mm")

            draw.text((49,177), f"M{nivel_mindscape}", fill="white", font=f_wengine, anchor="mm")
            y_stat = 172
            for _, valor in datos.get("stats_principales",{}).items():
                draw.text((1560, y_stat), f"{valor}", fill="white", font=f_stats, anchor="rm")
                y_stat += 52  
            
            # 1. Definimos la lista exacta de stats que pediste
            nombres_stats = [
                "HP", "ATK", "DEF", "IMPACT", "CRIT RATE", "CRIT DMG", 
                "AM", "AP", "PEN RATIO", "ENERGY REGEN", "PEN", 
                "ELEMENTAL DMG", "SHEER FORCE"
            ]
            
            # 2. Cargamos la fuente Bebas Neue para las etiquetas (tamaño 28, ajustalo si lo ves muy grande/chico)
            try:
                f_stat_labels = ImageFont.truetype(_fp("BebasNeue-Regular.ttf"), 28)
            except Exception:
                f_stat_labels = ImageFont.load_default()

            y_stat = 172
            # 3. Extraemos solo los valores del diccionario para emparejarlos en orden
            valores_stats = list(datos.get("stats_principales", {}).values())
            
            for i, nombre_stat in enumerate(nombres_stats):
                # Dibujamos el NOMBRE del stat (alineado a la izquierda en X=1350)
                # Cambia el "#cccccc" por "white" si quieres que brille igual que los números
                draw.text((1320, y_stat), nombre_stat, fill="#cccccc", font=f_stat_labels, anchor="lm")
                
                # Dibujamos el VALOR numérico (alineado a la derecha en X=1560)
                if i < len(valores_stats):
                    valor = valores_stats[i]
                    draw.text((1560, y_stat), f"{valor}", fill="white", font=f_stats, anchor="rm")
                
                y_stat += 52

            rol_agente = datos.get("tipo","Atacante")
            config_rol = CONFIG_ROLES.get(rol_agente, CONFIG_ROLES["Atacante"]).copy()
            if nombre_agente in EXCEPCIONES_AGENTES:
                exc = EXCEPCIONES_AGENTES[nombre_agente]
                if "subs" in exc: config_rol["subs"] = exc["subs"]
            ideales_n  = {normalizar_stat(k) for k in config_rol.get("subs",{}).get("ideal",  [])}
            decentes_n = {normalizar_stat(k) for k in config_rol.get("subs",{}).get("decente",[])}

            # =========================================================================
            # DISCOS
            # =========================================================================
            DISCO_INICIO_X = 416 
            DISCO_INICIO_Y = 355  
            
            DELTA_X_DISCO  = 282  
            DELTA_Y_DISCO  = 336  

            # Reconvertir el color del agente a HEX para usarlo en el texto
            color_agente_hex = f"#{r_ag:02x}{g_ag:02x}{b_ag:02x}"

            discos = datos.get("discos",[])
            for i, disco in enumerate(discos):
                columna, fila = i % 3, i // 3
                box_x = DISCO_INICIO_X + columna * DELTA_X_DISCO
                box_y = DISCO_INICIO_Y + fila    * DELTA_Y_DISCO

                # 1. NÚMERO DEL SLOT
                slot_num = str(i + 1)
                try:
                    f_slot_num = ImageFont.truetype(_fp("BebasNeue-Regular.ttf"), 30)
                except Exception:
                    f_slot_num = ImageFont.load_default()
                    
                draw.text((box_x, box_y + 3), slot_num, fill="#FFD700", font=f_slot_num, anchor="lt")
                
                # 2. STAT PRINCIPAL (Ahora con el color del Agente)
                st_p = disco.get("stat_principal", disco.get("main_stat", {}))
                if isinstance(st_p, dict):
                    m_nm = formatear_stat(st_p.get("nombre", ""))
                    m_vl = str(st_p.get("valor", ""))
                    ms_text = f"{m_nm} {m_vl}".strip()
                else:
                    ms_text = formatear_stat(str(st_p))
                
                if not ms_text or ms_text == "{}":
                    ms_text = "N/A" 
                
                try:
                    f_main_stat = ImageFont.truetype(_fp("BebasNeue-Regular.ttf"), 26)
                except Exception:
                    f_main_stat = ImageFont.load_default()
                    
                # Anclado en 'lm' al lado del número, usando color_agente_hex
                draw.text((box_x + 26, box_y + 16), ms_text, fill=color_agente_hex, font=f_main_stat, anchor="lm")

                # 3. NOMBRE DEL SET (Auto-ajustable)
                set_name = str(disco.get("set", disco.get("set_original", "N/A"))).replace("_", " ").title()
                
                # La caja del texto va desde 416 hasta 540 (Ancho máximo: 124px)
                caja_set_w = 124
                tam_set = 22 # Tamaño inicial ideal
                
                try:
                    f_set_name = ImageFont.truetype(_fp("BarlowCondensed-Bold.ttf"), tam_set)
                    # Bucle mágico: Si el texto es más ancho que la caja, reduce la fuente
                    while draw.textlength(set_name, font=f_set_name) > caja_set_w and tam_set > 10:
                        tam_set -= 1
                        f_set_name = ImageFont.truetype(_fp("BarlowCondensed-Bold.ttf"), tam_set)
                except Exception:
                    f_set_name = ImageFont.load_default()
                
                # Anclado en 'lt' debajo de ambos
                draw.text((box_x, box_y + 45), set_name, fill="white", font=f_set_name, anchor="lt")

                # 4. IMAGEN DEL DISCO
                set_orig  = str(disco.get("set_original", disco.get("set","")))
                set_clean = set_orig.replace(":","").replace("/","_").strip()
                ruta_d    = os.path.join(self.ruta_recursos,"images","discos",f"{set_clean}.png")
                
                if os.path.exists(ruta_d):
                    tam_d = 79 
                    img_d = ajustar_imagen(Image.open(ruta_d).convert("RGBA"), tam_d, tam_d)
                    cx_d = box_x + 168
                    cy_d = box_y + 39
                    lienzo.paste(img_d, (cx_d - (tam_d//2), cy_d - (tam_d//2)), img_d)

                # 5. SUBSTATS
                sub_y = box_y + 112
                SUB_PASO = 44

                for sub in disco.get("subs",[]):
                    c_s  = sub.get("color","white")
                    nm_s = formatear_stat(str(sub.get("nombre","")))
                    vl_s = str(sub.get("valor",""))
                    rl_s = str(sub.get("rolls",""))
                    
                    try:
                        f_subs = ImageFont.truetype(_fp("Exo2-Bold.ttf"), 16)
                        f_rolls = ImageFont.truetype(_fp("BarlowCondensed-Bold.ttf"), 20)
                    except Exception:
                        f_subs = ImageFont.load_default()
                        f_rolls = ImageFont.load_default()
                    
                    draw.text((box_x + 1, sub_y), nm_s, fill=c_s, font=f_subs, anchor="lt")
                    draw.text((box_x + 165, sub_y), vl_s, fill=c_s, font=f_subs, anchor="rt")
                    
                    # Rolls (+X) sin el rectángulo de fondo
                    if rl_s:
                        draw.text((box_x + 191, sub_y + 10), rl_s, fill=c_s, font=f_rolls, anchor="mm")
                        
                    sub_y += SUB_PASO

                # 6. TIER SCORE
                sc_val           = score_disco_fn(disco.get("subs",[]), ideales_n, decentes_n)
                tier_txt, tier_c = tier_from_score(sc_val)
                
                # Ancho máximo permitido para que no se salga del recuadro
                ancho_max_tier = 110 # Lo dejamos en 110px para que tenga un pequeñísimo margen
                tam_tier = 40 # Tamaño inicial ideal
                
                try:
                    f_tier = ImageFont.truetype(_fp("ShadowsIntoLight-Regular.ttf"), tam_tier)
                    
                    # Bucle mágico: reduce el tamaño de la fuente si el texto es muy largo
                    while draw.textlength(tier_txt, font=f_tier) > ancho_max_tier and tam_tier > 14:
                        tam_tier -= 2
                        f_tier = ImageFont.truetype(_fp("ShadowsIntoLight-Regular.ttf"), tam_tier)
                except Exception:
                    f_tier = ImageFont.load_default()
                    
                draw.text((box_x + 115, box_y + 283), tier_txt, fill=tier_c, font=f_tier, anchor="mm", 
                          stroke_width=2, stroke_fill=(0, 0, 0, 200))
            
            from logica_recomendaciones import evaluar_calidad_global
            import math
            
            rol_agente = datos.get("rol", "DPS")
            eficiencia_arma = datos.get("eficiencia_arma", 0)
            
            try:
                resumen_rolls = evaluar_calidad_global(
                    nombre_agente=nombre_agente,
                    rol_agente=rol_agente,
                    rolls_actuales=datos.get("substats_counts", {}),
                    stats_finales=datos.get("_stats_reales_calculo", {}),
                    eficiencia_wengine_actual=eficiencia_arma,
                    excepciones=EXCEPCIONES_AGENTES,
                    config_roles=CONFIG_ROLES
                )
            except Exception:
                resumen_rolls = {"ideal": 0, "decente": 0, "basura": 0, "total_rolls": 0, "puntaje_total": 0, "calidad_pct": 0}

            eval_level = str(datos.get("evaluacion_build", "B")).upper()
            
            circle_colors = {
                "SSS": "#ff003c", "SS": "#ff6600", "S": "#ffea00",
                "A+": "#d500f9", "A": "#2979ff", "B": "#00e676", "C": "#888888"
            }
            circle_color = circle_colors.get(eval_level, "#888888")
            
            # Obtenemos el mismo porcentaje que usamos en "Quality"
            calidad_pct = resumen_rolls.get('calidad_pct', 0)
            
            # Determinamos la palabra épica y el color basándonos en el porcentaje
            if calidad_pct >= 90:
                texto_eval = "GODLIKE"
                circle_color = "#ff003c"  # Rojo intenso
            elif calidad_pct >= 80:
                texto_eval = "FLAWLESS"
                circle_color = "#ff6600"  # Naranja
            elif calidad_pct >= 75:
                texto_eval = "GREAT"
                circle_color = "#ffea00"  # Amarillo
            elif calidad_pct >= 60:
                texto_eval = "SOLID"
                circle_color = "#d500f9"  # Morado
            elif calidad_pct >= 50:
                texto_eval = "DECENT"
                circle_color = "#2979ff"  # Azul
            else:
                texto_eval = "AVERAGE"
                circle_color = "#888888"  # Gris
            
            # Coordenadas exactas del recuadro
            C_X1, C_Y1 = 1347 + 8, 842 + 8 - 7
            C_X2, C_Y2 = 1506 - 8, 1002 - 8 - 7
            EVAL_CX = C_X1 + (C_X2 - C_X1) // 2  
            EVAL_CY = C_Y1 + (C_Y2 - C_Y1) // 2  
            
            # 1. Dibujamos un anillo de fondo oscuro para que se vea por dónde va a "cargar" el porcentaje
            draw.ellipse([C_X1, C_Y1, C_X2, C_Y2], fill=None, outline=(50, 50, 50, 150), width=4)
            
            # 2. Lógica del arco de progreso
            # En Pillow, 0° es la derecha (las 3 en el reloj). Para empezar a llenar desde arriba (las 12), usamos 270°.
            start_angle = 270
            
            # Regla de 3: 100% es a 360 grados, entonces multiplicamos el % por 3.6
            end_angle = start_angle + (calidad_pct * 3.6)
            
            # Dibujamos el arco de color por encima del fondo gris (si el puntaje es mayor a 0)
            if calidad_pct > 0:
                draw.arc([C_X1, C_Y1, C_X2, C_Y2], start=start_angle, end=end_angle, fill=circle_color, width=4)
            
            # --- MAGIA DE AUTO-ESCALADO CON BEBASNEUE ---
            tamaño_fuente = 45  
            
            try:
                # Cambiamos a la fuente BebasNeue como solicitaste
                fuente_eval = ImageFont.truetype(_fp("BebasNeue-Regular.ttf"), tamaño_fuente)
                
                while draw.textlength(texto_eval, font=fuente_eval) > 120 and tamaño_fuente > 15:
                    tamaño_fuente -= 2
                    fuente_eval = ImageFont.truetype(_fp("BebasNeue-Regular.ttf"), tamaño_fuente)
            except Exception:
                fuente_eval = ImageFont.load_default()
            
            # Dibujamos la palabra épica centrada. 
            # OJO: Quité el "+ 5" que tenías en EVAL_CY porque BebasNeue tiene otra caja de texto 
            # y suele centrarse mejor matemáticamente. Si la ves muy arriba, le pones el +5 de vuelta.
            draw.text((EVAL_CX, EVAL_CY + 8), texto_eval, fill=circle_color, 
                     font=fuente_eval, anchor="mm", stroke_width=2, stroke_fill=(0, 0, 0, 220))

            agentes_esp = {"Miyabi":"frost","Yixuan":"tinta aurica","Ye Shunguang":"cortante"}
            ruta_ico_sup = os.path.join(self.ruta_recursos, "images", "elementos", f"{elemento_limpio}.png")
            if os.path.exists(ruta_ico_sup):
                ico_sup = ajustar_imagen(Image.open(ruta_ico_sup).convert("RGBA"), ICONO_ELEM_TAM, ICONO_ELEM_TAM)
                cx_elem_sup, cy_elem_sup = 1297, 746
                lienzo.paste(ico_sup, (cx_elem_sup - (ICONO_ELEM_TAM // 2), cy_elem_sup - (ICONO_ELEM_TAM // 2)), ico_sup)


            # 2. CAJA DE TIPO Y ELEMENTO ESPECIAL (Fondo #36363B)
            # Caja: X de 180 a 270 (ancho 90) | Y de 885 a 923 (alto 38)
            # ═══════════════════════════════════════════════════════════════════════
            # BLOQUE CENTRAL DE ICONOS (Tipo, Elemento, Rango, Facción, VIP)
            # ═══════════════════════════════════════════════════════════════════════
            
            # 1. CAJA DE TIPO Y ELEMENTO ESPECIAL (Recuadro: 175,856 a 301,922)
            # Centro Y = 856 + (66 // 2) = 889. Centro X = 175 + (126 // 2) = 238
            CY_INF = 894
            TAM_INF = 46 # Íconos más grandes para llenar mejor los 66px de alto
            # Distanciamos los centros simétricamente desde el eje X (238)
            CX_TIPO = 208
            CX_ELEM2 = 268
            color_fondo = "#36363B"
            
            # A) TIPO (Rol)
            tipo_l = str(datos.get("tipo","")).lower()
            for ch,rep in [("\xe9","e"),("\xed","i"),("\xf3","o")]:
                tipo_l = tipo_l.replace(ch,rep)
            ruta_tipo = os.path.join(self.ruta_recursos,"images","elementos",f"{tipo_l}.png")
            if os.path.exists(ruta_tipo):
                r_bg = TAM_INF // 2
                draw.ellipse([CX_TIPO - r_bg, CY_INF - r_bg, CX_TIPO + r_bg, CY_INF + r_bg], fill=color_fondo)
                tip_img = ajustar_imagen(Image.open(ruta_tipo).convert("RGBA"), TAM_INF, TAM_INF)
                lienzo.paste(tip_img, (CX_TIPO - r_bg, CY_INF - r_bg), tip_img)

            # B) ELEMENTO
            agentes_esp = {"Miyabi":"frost","Yixuan":"tinta aurica","Ye Shunguang":"cortante"}
            elem_icon_inf = agentes_esp.get(nombre_agente, elemento_limpio)
            ruta_ico_inf = os.path.join(self.ruta_recursos, "images", "elementos", f"{elem_icon_inf}.png")
            if os.path.exists(ruta_ico_inf):
                r_bg = TAM_INF // 2
                draw.ellipse([CX_ELEM2 - r_bg, CY_INF - r_bg, CX_ELEM2 + r_bg, CY_INF + r_bg], fill=color_fondo)
                ico_inf = ajustar_imagen(Image.open(ruta_ico_inf).convert("RGBA"), TAM_INF, TAM_INF)
                lienzo.paste(ico_inf, (CX_ELEM2 - r_bg, CY_INF - r_bg), ico_inf)

            # 2. IMAGEN DEL RANGO
            rango_s = str(datos.get("rango_agente","S")).upper()
            ruta_rang = os.path.join(self.ruta_recursos,"images","rangos",f"{rango_s}.png")
            if os.path.exists(ruta_rang):
                tam_rango_nuevo = 84
                rng = ajustar_imagen(Image.open(ruta_rang).convert("RGBA"), tam_rango_nuevo, tam_rango_nuevo)
                cx_rng = 301 + (355 - 301) // 2
                cy_rng = 722 + (766 - 722) // 2
                lienzo.paste(rng, (cx_rng - (tam_rango_nuevo // 2), cy_rng - (tam_rango_nuevo // 2)), rng)
            i
            agentes_slash = {"Anby", "Nekomata", "Soldier 11", "Corin", "Caesar", "Miyabi", "Soukaku", "Ellen",
                             "Yanagi", "Jane", "Seth", "Piper", "Hugo", "Evelyn", "Vivian", "Zhao", "Pulchra",
                             "Soldier 0 - Anby", "Alice", "Ye Shunguang", "Manato", "Seed", "Dialyn", "Cissia",
                             "Starlight - Billy", "Promeia",} 
            agentes_strike = {"Nicole", "Yidhari", "Koleda", "Ben", "Lycaon", "Lucy", "Lighter", "Rina", "Qingyi",
                              "Astra Yao", "Yixuan", "Ju Fufu", "Yuzuha", "Pan Yinhu", "Lucia", "Banyue", "Sunna",
                              "Aria", "Nangong Yu",}
            agentes_pierce = {"Billy", "Anton", "Burnice", "Grace", "Harumasa", "Zhu Yuan", "Orphie & Magus", "Trigger",
                              }
            
            tipo_ataque = None
            if nombre_agente in agentes_slash:
                tipo_ataque = "slash"
            elif nombre_agente in agentes_strike:
                tipo_ataque = "strike"
            elif nombre_agente in agentes_pierce:
                tipo_ataque = "pierce"
                
            if tipo_ataque:
                ruta_ataque = os.path.join(self.ruta_recursos, "images", "elementos", f"{tipo_ataque}.png")
                
                if os.path.exists(ruta_ataque):
                    cx_ataque = 132 + (39 // 2) 
                    cy_ataque = 873 + (39 // 2)  
                    tam_ataque = 38 
                    
                    img_ataque = ajustar_imagen(Image.open(ruta_ataque).convert("RGBA"), tam_ataque, tam_ataque)
                    lienzo.paste(img_ataque, (cx_ataque - (tam_ataque // 2), cy_ataque - (tam_ataque // 2)), img_ataque)

            # 3. FACCIÓN (Recuadro exacto: 90,933 a 147,991)
            cx_facc = 90 + (147 - 90) // 2   # Centro X: 118
            cy_facc = 933 + (991 - 933) // 2 # Centro Y: 962
            tam_facc = 56 # Cubre perfecto los 58px de altura del recuadro
            
            facc = str(datos.get("faccion_agente","liebres astutas")).lower()
            for ch,rep in [("\xe1","a"),("\xe9","e"),("\xed","i"),("\xf3","o"),("\xfa","u"),("\xf1","n")]:
                facc = facc.replace(ch,rep)
            ruta_facc = os.path.join(self.ruta_recursos,"images","faccion",f"{facc}.png")
            
            if os.path.exists(ruta_facc):
                fac_img = ajustar_imagen(Image.open(ruta_facc).convert("RGBA"), tam_facc, tam_facc)
                lienzo.paste(fac_img, (cx_facc - (tam_facc // 2), cy_facc - (tam_facc // 2)), fac_img)

            # 4. TÍTULOS VIP (Void Hunter / Grandmaster) en (159,933 a 301,990)
            if nombre_agente in ["Miyabi", "Ye Shunguang", "Yixuan"]:
                if nombre_agente == "Yixuan":
                    img_name = "Grandmaster.png"
                    txt_titulo = "GRANDMASTER"
                else:
                    img_name = "Voidhunter.png"
                    txt_titulo = "VOID HUNTER"
                    
                ruta_titulo = os.path.join(self.ruta_recursos, "images", "elementos", img_name)
                
                if os.path.exists(ruta_titulo):
                    # Altura de la caja = 57px. Hacemos el ícono de 54px para que respire por 1 pixel.
                    tam_titulo = 54
                    # Pegamos el ícono anclado al límite izquierdo (X = 159)
                    x_icono_vip = 159
                    y_icono_vip = 933 + (57 - tam_titulo) // 2 # Centrado vertical (934)
                    
                    tit_img = ajustar_imagen(Image.open(ruta_titulo).convert("RGBA"), tam_titulo, tam_titulo)
                    lienzo.paste(tit_img, (x_icono_vip, y_icono_vip), tit_img)
                    
                    # El texto empieza justo después del ícono, más 5px de margen (159 + 54 + 5 = 218)
                    x_texto_vip = 218
                    cy_texto_vip = 933 + 57 // 2 # Centro Y (961)
                    ancho_disp_texto = 301 - x_texto_vip # Espacio restante antes del límite derecho
                    
                    try:
                        tam_fuente_vip = 18
                        f_titulo = ImageFont.truetype(_fp("BarlowCondensed-Bold.ttf"), tam_fuente_vip)
                        
                        # Autoescalado para no salirnos nunca del recuadro por la derecha (límite 301)
                        while draw.textlength(txt_titulo, font=f_titulo) > ancho_disp_texto and tam_fuente_vip > 10:
                            tam_fuente_vip -= 1
                            f_titulo = ImageFont.truetype(_fp("BarlowCondensed-Bold.ttf"), tam_fuente_vip)
                    except Exception:
                        f_titulo = ImageFont.load_default()
                        
                    # CLAVE: Anclamos en "lm" (Left-Middle). 
                    # Crece hacia la derecha desde X=218. JAMÁS se encimará con el ícono.
                    draw.text((x_texto_vip, cy_texto_vip), txt_titulo, fill="white", font=f_titulo, anchor="lm")

            # B) Tipo (Rol)
            tipo_l = str(datos.get("tipo","")).lower()
            for ch,rep in [("\xe9","e"),("\xed","i"),("\xf3","o")]:
                tipo_l = tipo_l.replace(ch,rep)
            ruta_tipo = os.path.join(self.ruta_recursos,"images","elementos",f"{tipo_l}.png")
            if os.path.exists(ruta_tipo):
                tip_img = ajustar_imagen(Image.open(ruta_tipo).convert("RGBA"), TAM_INF, TAM_INF)
                lienzo.paste(tip_img, (CX_TIPO - (TAM_INF // 2), CY_INF - (TAM_INF // 2)), tip_img)

            # C) Elemento 2 (CON excepciones, muestra "frost", "tinta aurica", etc.)
            agentes_esp = {"Miyabi":"frost","Yixuan":"tinta aurica","Ye Shunguang":"cortante"}
            elem_icon_inf = agentes_esp.get(nombre_agente, elemento_limpio)
            ruta_ico_inf = os.path.join(self.ruta_recursos, "images", "elementos", f"{elem_icon_inf}.png")
            
            if os.path.exists(ruta_ico_inf):
                ico_inf = ajustar_imagen(Image.open(ruta_ico_inf).convert("RGBA"), TAM_INF, TAM_INF)
                lienzo.paste(ico_inf, (CX_ELEM2 - (TAM_INF // 2), CY_INF - (TAM_INF // 2)), ico_inf)

            # =========================================================================
            # PANEL INFERIOR: ANÁLISIS DE SUBSTATS + DISC RATINGS + GRÁFICO RADIAL
            # Posición: Espacio azul de abajo (después de iconos de facción/elemento/rol)
            # =========================================================================
            
            # Preparar fuentes para el panel inferior
            try:
                f_panel_titulo = ImageFont.truetype(_fp("BarlowCondensed-Bold.ttf"), 24)
                f_panel_numero = ImageFont.truetype(_fp("BebasNeue-Regular.ttf"), 28)
                f_panel_small = ImageFont.truetype(_fp("DMSans-Regular.ttf"), 14)
            except:
                f_panel_titulo = f_panel_texto = f_panel_numero = f_panel_small = ImageFont.load_default()
            
            # ══════════════════════════════════════════════════════════════════════
            # LAYOUT DEL PANEL INFERIOR (3 columnas)
            # ══════════════════════════════════════════════════════════════════════
            PANEL_Y_INICIO = 970   # Debajo de los iconos
            PANEL_HEIGHT = 500     # Altura del panel
            
            # Columna 2: DISC RATINGS (centro)
            COL2_X = 580
            COL2_Y = PANEL_Y_INICIO
            
            
            # ═══════════════════════════════════════════════════════════════════════
            # COLUMNA 1: SUBSTAT ANALYSIS
            # ═══════════════════════════════════════════════════════════════════════
            cx_col1 = 198
            
            # Como el bloque completo es más alto por las fuentes grandes, 
            # empezamos un poco más arriba (1130) para que siga abrazando el centro
            y_actual = 1130  
            
            draw.text((cx_col1, y_actual), "SUBSTAT ANALYSIS", 
                     fill="#FFD700", font=f_panel_titulo, anchor="mm")
            
            y_actual += 60  # Salto después del título
            
            x_izq = cx_col1 - 120   
            x_der = cx_col1 + 120   
            
            # Rolls ideales (Amber 400) - Fuente Bebas (f_panel_numero)
            draw.text((x_izq, y_actual), "Ideal:", fill="#fbbf24", font=f_panel_numero, anchor="lm")
            draw.text((x_der, y_actual), str(resumen_rolls["ideal"]), fill="#fbbf24", font=f_panel_numero, anchor="rm")
            y_actual += 45 
            
            # Rolls decentes (Cyan 400) - Fuente Bebas
            draw.text((x_izq, y_actual), "Decent:", fill="#22d3ee", font=f_panel_numero, anchor="lm")
            draw.text((x_der, y_actual), str(resumen_rolls["decente"]), fill="#22d3ee", font=f_panel_numero, anchor="rm")
            y_actual += 45
            
            # Rolls basura (Gray 400) - Fuente Bebas
            draw.text((x_izq, y_actual), "Waste:", fill="#9ca3af", font=f_panel_numero, anchor="lm")
            draw.text((x_der, y_actual), str(resumen_rolls["basura"]), fill="#9ca3af", font=f_panel_numero, anchor="rm")
            y_actual += 45
            
            # Total de rolls (Amarillo del título) - Fuente Bebas
            draw.text((x_izq, y_actual), "Total:", fill="#FFD700", font=f_panel_numero, anchor="lm")
            draw.text((x_der, y_actual), str(resumen_rolls["total_rolls"]), fill="#FFD700", font=f_panel_numero, anchor="rm")
            y_actual += 35
            
            # Línea separadora
            draw.line([(x_izq, y_actual), (x_der, y_actual)], fill="#888888", width=2)
            y_actual += 35
            
            # Calidad porcentual (Mismo color de la evaluación principal: circle_color) - Fuente Bebas
            draw.text((x_izq, y_actual), "Quality:", fill=circle_color, font=f_panel_numero, anchor="lm")
            draw.text((x_der, y_actual), f"{resumen_rolls['calidad_pct']:.1f}%", fill=circle_color, font=f_panel_numero, anchor="rm")
            
            # ═══════════════════════════════════════════════════════════════════════
            # COLUMNA 2: DISCO 4 INFO + DESCRIPCIÓN DE EFECTO DE SET + DISCO 2
            # ═══════════════════════════════════════════════════════════════════════
            
            # Obtener el disco en posición 4 (índice 3)
            discos_temp = datos.get("discos", [])
            
            # 1. Contar frecuencias de los sets reales equipados en todos los slots
            conteo_sets = {}
            for d in discos_temp:
                n_set = str(d.get("set_original", d.get("set", "")))
                if n_set and n_set != "N/A" and n_set != "Desconocido":
                    conteo_sets[n_set] = conteo_sets.get(n_set, 0) + 1
                    
            # 2. Determinar cuáles son los sets dominantes (Ordenamos de mayor a menor)
            set_x4_nombre = None
            set_x2_nombre = None
            
            sets_ordenados = sorted(conteo_sets.items(), key=lambda x: x[1], reverse=True)
            
            if sets_ordenados:
                # El set con más piezas (idealmente 4) va al recuadro principal
                if sets_ordenados[0][1] >= 4:
                    set_x4_nombre = sets_ordenados[0][0]
                elif sets_ordenados[0][1] >= 2:
                    # Fallback por si llevan build rara de 2+2+2
                    set_x4_nombre = sets_ordenados[0][0] 
                
                # El segundo set con más piezas (idealmente 2) va al recuadro secundario
                if len(sets_ordenados) > 1 and sets_ordenados[1][1] >= 2:
                    set_x2_nombre = sets_ordenados[1][0]

            # 3. Asignar disco_4 y disco_2 capturando el primer disco que pertenezca a esos sets
            disco_4 = next((d for d in discos_temp if str(d.get("set_original", d.get("set", ""))) == set_x4_nombre), None)
            disco_2 = next((d for d in discos_temp if str(d.get("set_original", d.get("set", ""))) == set_x2_nombre), None)
            
            if disco_4:
                # 1. IMAGEN DEL DISCO 4
                set_orig_4 = str(disco_4.get("set_original", disco_4.get("set", "")))
                set_clean_4 = set_orig_4.replace(":", "").replace("/", "_").strip()
                ruta_disco_4 = os.path.join(self.ruta_recursos, "images", "discos", f"{set_clean_4}.png")
                
                if os.path.exists(ruta_disco_4):
                    img_disco_4 = Image.open(ruta_disco_4).convert("RGBA")
                    disco_size = 144  
                    img_disco_4 = img_disco_4.resize((disco_size, disco_size), Image.Resampling.LANCZOS)
                    lienzo.paste(img_disco_4, (445, 1117), img_disco_4)
                
                # 2. TEXTO "DRIVE DISC 4" 
                draw.text((624, 1107), "DRIVE DISC X4", 
                          fill="#FFD700", font=f_panel_titulo, anchor="lm")
                
                # 3. NOMBRE DEL SET
                set_name_4 = str(disco_4.get("set", "N/A")).replace("_", " ").title()
                try:
                    f_set_bebas = ImageFont.truetype(_fp("BebasNeue-Regular.ttf"), 22)
                except Exception:
                    f_set_bebas = ImageFont.load_default()
                    
                draw.text((624, 1137), set_name_4, fill="white", font=f_set_bebas, anchor="lm")
                
                # 4. DESCRIPCIÓN DEL EFECTO X4
                descripcion_efecto = ""
                try:
                    ruta_csv_efectos = os.path.join(self.ruta_recursos, "disc_set_effects.csv")
                    if os.path.exists(ruta_csv_efectos):
                        import csv
                        with open(ruta_csv_efectos, 'r', encoding='utf-8-sig') as f:
                            reader = csv.DictReader(f)
                            set_objetivo = set_orig_4.strip().lower()
                            
                            for row in reader:
                                set_csv = row.get('nombre_set', '')
                                if set_csv:
                                    set_csv = set_csv.strip().lower()
                                    
                                if set_csv == set_objetivo:
                                    descripcion_efecto = row.get('descripcion_efecto', '').strip()
                                    break
                except Exception as e:
                    print(f"Error cargando efectos de sets: {e}")
                
                if descripcion_efecto:
                    dibujar_parrafo_justificado(
                        texto=descripcion_efecto, 
                        fuente=f_panel_small, 
                        x_caja=624, y_caja=1141, 
                        ancho_caja=511, alto_caja=118, 
                        draw_obj=draw, color_base="#aaaaaa", max_lineas=6
                    )
            
            # ═══════════════════════════════════════════════════════════════════════
            # AGREGAR DISCO X2 DEBAJO DEL DISCO 4
            # ═══════════════════════════════════════════════════════════════════════
            
            # (YA BORRAMOS LA LÍNEA QUE SOBREESCRIBÍA A DISCO_2 AQUÍ)
            
            if disco_2:
                # 1. IMAGEN DEL DISCO X2
                set_orig_2 = str(disco_2.get("set_original", disco_2.get("set", "")))
                set_clean_2 = set_orig_2.replace(":", "").replace("/", "_").strip()
                ruta_disco_2 = os.path.join(self.ruta_recursos, "images", "discos", f"{set_clean_2}.png")
                
                if os.path.exists(ruta_disco_2):
                    img_disco_2 = Image.open(ruta_disco_2).convert("RGBA")
                    disco_size_2 = 104 
                    img_disco_2 = img_disco_2.resize((disco_size_2, disco_size_2), Image.Resampling.LANCZOS)
                    lienzo.paste(img_disco_2, (465, 1304), img_disco_2)
                
                # 2. TEXTO "DRIVE DISC X2" 
                draw.text((625, 1291), "DRIVE DISC X2", 
                          fill="#00d4ff", font=f_panel_titulo, anchor="lm")
                
                # 3. NOMBRE DEL SET X2 
                set_name_2 = str(disco_2.get("set", "N/A")).replace("_", " ").title()
                try:
                    f_set_x2 = ImageFont.truetype(_fp("BebasNeue-Regular.ttf"), 22)
                except Exception:
                    f_set_x2 = ImageFont.load_default()
                    
                draw.text((625, 1321), set_name_2, fill="white", font=f_set_x2, anchor="lm")
                
                # 4. DESCRIPCIÓN DEL EFECTO X2
                efecto_x2 = ""
                try:
                    ruta_csv_efectos = os.path.join(self.ruta_recursos, "disc_set_effects.csv")
                    if os.path.exists(ruta_csv_efectos):
                        import csv
                        with open(ruta_csv_efectos, 'r', encoding='utf-8-sig') as f:
                            reader = csv.DictReader(f)
                            set_objetivo_2 = set_orig_2.strip().lower()
                            
                            for row in reader:
                                set_csv = row.get('nombre_set', '')
                                if set_csv:
                                    set_csv = set_csv.strip().lower()
                                    
                                if set_csv == set_objetivo_2:
                                    efecto_x2 = row.get('efectox2', '').strip()
                                    break
                except Exception as e:
                    print(f"Error cargando efecto x2: {e}")
                
                if efecto_x2:
                    try:
                        f_efecto_x2 = ImageFont.truetype(_fp("DMSans-Regular.ttf"), 15)
                    except Exception:
                        f_efecto_x2 = ImageFont.load_default()
                    
                    # Función de coloreo para efecto x2
                    import re
                    def colorear_x2(texto, fuente, x_pos, y_pos, draw_obj):
                        stats_keywords = [
                            "DMG", "ATK", "HP", "DEF", "CRIT", "Anomaly", "Impact", 
                            "Energy", "PEN", "Proficiency", "Mastery"
                        ]
                        
                        palabras = texto.split()
                        x_actual = x_pos
                        
                        for palabra in palabras:
                            es_stat = any(keyword.lower() in palabra.lower() for keyword in stats_keywords)
                            tiene_numero_pct = bool(re.search(r'[+\-]?\d+%', palabra))
                            
                            color = "#FFD700" if (es_stat or tiene_numero_pct) else "#999999"
                            
                            ancho_palabra = draw_obj.textlength(palabra + " ", font=fuente)
                            draw_obj.text((x_actual, y_pos), palabra + " ", fill=color, font=fuente, anchor="lt")
                            x_actual += ancho_palabra
                    
                    colorear_x2(efecto_x2, f_efecto_x2, 625, 1345, draw)
            

            
            # ═══════════════════════════════════════════════════════════════════════
            # COLUMNA 3: GRÁFICO RADIAL DE STATS (10 stats como en crear_gui)
            # ═══════════════════════════════════════════════════════════════════════
            
            # Obtener stats desde _stats_reales_calculo (datos procesados del cálculo)
            rolls_calculo = datos.get("substats_counts", {})
            
            MAX_ROLLS = 15.0 
            
            # Estas son las llaves originales que vienen de tu primera función (con tildes)
            config_ejes = [
                ("ATK", "Ataque_plano"),
                ("ATK%", "Ataque_porcentual"),
                ("HP", "Puntos_Vida_plano"),
                ("HP%", "Puntos_Vida_porcentual"),
                ("DEF", "Defensa_plano"),
                ("DEF%", "Defensa_porcentual"),
                ("PEN", "Perforación_Plana_plano"), 
                ("AP", "Maestría_Anomalía_plano"),
                ("CR%", "Probabilidad_crítico_porcentual"),
                ("CD%", "Daño_crítico_porcentual")
            ]
            
            radar_stats = []
            
            for short_name, norm_key in config_ejes:
                # 1. Buscar los rolls (intentamos con y sin tilde para evitar que devuelva 0)
                norm_key_sin_tilde = norm_key.replace("í", "i").replace("ó", "o").replace("ñ", "n").replace("á", "a")
                rolls = float(rolls_calculo.get(norm_key, rolls_calculo.get(norm_key_sin_tilde, 0)))
                
                # 2. Pasar la llave por la función local para que coincida 100% con las listas de ideales (que no usan tildes)
                clave_local = normalizar_stat(norm_key)
                
                # 3. Caso especial PEN (Junta perforación plana y porcentual)
                if short_name == "PEN":
                    rolls += float(rolls_calculo.get("Perforación_Plana_plano", rolls_calculo.get("Perforacion_Plana_plano", 0)))
                    clave_plana_local = normalizar_stat("Perforación_Plana_plano")
                    
                    es_ideal = clave_local in ideales_n or clave_plana_local in ideales_n
                    es_decente = clave_local in decentes_n or clave_plana_local in decentes_n
                else:
                    es_ideal = clave_local in ideales_n
                    es_decente = clave_local in decentes_n
                
                # 4. Asignar color según utilidad
                if es_ideal:
                    color_txt = "#fbbf24"  # Amber 400 (Ideal)
                elif es_decente:
                    color_txt = "#22d3ee"  # Cyan 400 (Decente)
                else:
                    color_txt = "#888888"  # Gris (Basura/No sirve)
                
                stat_value = (rolls / MAX_ROLLS) * 100
                radar_stats.append((short_name, stat_value, rolls, color_txt))

            radar_cx = 1404
            radar_cy = 1280
            radar_radius = 90  
            
            draw.text((radar_cx, radar_cy - 161), "STATS DISTRIBUTION", 
                     fill="#FFD700", font=f_panel_titulo, anchor="mm")

            # Dibujar círculos de guía
            for pct in [25, 50, 75, 100]:
                r = int(radar_radius * pct / 100)
                draw.ellipse([
                    (radar_cx - r, radar_cy - r),
                    (radar_cx + r, radar_cy + r)
                ], outline=(80, 80, 80, 128), width=1)
            
            num_stats = len(radar_stats)
            angle_step = 360 / num_stats
            polygon_points = []
            
            BASE_PCT = 15  
            
            for i, (stat_name, stat_value, rolls, label_color) in enumerate(radar_stats):
                angle_deg = 90 - (i * angle_step)  
                angle_rad = math.radians(angle_deg)
                
                # Línea del eje
                end_x = radar_cx + radar_radius * math.cos(angle_rad)
                end_y = radar_cy - radar_radius * math.sin(angle_rad)
                draw.line([(radar_cx, radar_cy), (end_x, end_y)], fill=(100, 100, 100, 180), width=1)
                
                # Cálculo de los puntos del polígono
                value_normalized = min(max(stat_value, 0), 100)  
                visual_pct = BASE_PCT + ((100 - BASE_PCT) * (value_normalized / 100))
                
                point_x = radar_cx + (radar_radius * visual_pct / 100) * math.cos(angle_rad)
                point_y = radar_cy - (radar_radius * visual_pct / 100) * math.sin(angle_rad)
                polygon_points.append((point_x, point_y))
                
                # Texto dinámico (Solo muestra el número si sacaste rolls ahí)
                display_text = f"{stat_name} ({int(rolls)})" if rolls > 0 else stat_name
                
                # Etiquetas
                label_distance = radar_radius + 35
                label_x = radar_cx + label_distance * math.cos(angle_rad)
                label_y = radar_cy - label_distance * math.sin(angle_rad)
                
                draw.text((label_x, label_y), display_text, 
                         fill=label_color, font=f_panel_small, anchor="mm",
                         stroke_width=1, stroke_fill=(0, 0, 0, 200))
            
            # Dibujar el polígono semitransparente
            if len(polygon_points) >= 3:
                draw.polygon(polygon_points, fill=(r_ag, g_ag, b_ag, 80), 
                             outline=(255, 255, 255, 200), width=2)

            from PIL import ImageFilter
            import colorsys  # <-- Necesario para la magia del arcoíris

            posicion_ranking = datos.get("posicion_ranking")
            total_jugadores = datos.get("total_jugadores")

            if posicion_ranking and total_jugadores and total_jugadores > 0:
                RANK_X = EVAL_CX
                RANK_Y = EVAL_CY + 107  # Posicionado justo debajo del círculo radial

                def dibujar_texto_glow(pos, texto, font, anchor, glow_col, text_col, glow_radius=4, glow_layers=3, is_rainbow=False):
                    """Texto con halo sutil o gradiente arcoíris."""
                    bb = draw.textbbox(pos, texto, font=font, anchor=anchor)
                    tx, ty, tx2, ty2 = bb
                    pad = int(glow_radius) + 5
                    w = max(tx2 - tx + pad*2, 1)
                    h = max(ty2 - ty + pad*2, 1)
                    
                    glow_layer = Image.new("RGBA", (w, h), (0,0,0,0))
                    
                    # Color base para dibujar las capas del halo (Blanco puro si es arcoíris)
                    base_color = (255, 255, 255) if is_rainbow else glow_col

                    # Generamos las capas del halo
                    for layer in range(glow_layers, 0, -1):
                        radius = glow_radius * layer / glow_layers
                        # Si es arcoíris, subimos un poco la opacidad para que brille más fuerte
                        mult_alpha = 130 if is_rainbow else 90
                        alpha  = int(mult_alpha * (layer / glow_layers) ** 2)
                        if alpha <= 0: continue
                        
                        colored = Image.new("RGBA", (w, h), (0,0,0,0))
                        cd = ImageDraw.Draw(colored)
                        cd.text((pad, pad), texto, fill=(*base_color, alpha), font=font,
                                anchor="lt", stroke_width=max(1, int(radius)),
                                stroke_fill=(*base_color, alpha))
                        
                        blurred = colored.filter(ImageFilter.GaussianBlur(radius=radius))
                        glow_layer = Image.alpha_composite(glow_layer, blurred)
                        
                    # --- MAGIA ARCOÍRIS ---
                    if is_rainbow:
                        # Extraemos la capa de transparencia (Alpha) del halo blanco
                        alpha_channel = glow_layer.split()[3]
                        
                        # Creamos un lienzo nuevo para el arcoíris
                        rainbow_layer = Image.new("RGBA", (w, h), (0,0,0,0))
                        rd = ImageDraw.Draw(rainbow_layer)
                        
                        # Dibujamos líneas verticales de colores
                        for x in range(w):
                            hue = x / w  # Va de 0.0 (Rojo) a 1.0 (Rojo), pasando por todos los colores
                            r, g, b = colorsys.hsv_to_rgb(hue, 0.85, 1.0)
                            color_linea = (int(r*255), int(g*255), int(b*255), 255)
                            rd.line([(x, 0), (x, h)], fill=color_linea)
                            
                        # Recortamos el arcoíris usando el halo blanco original
                        rainbow_layer.putalpha(alpha_channel)
                        glow_layer = rainbow_layer  # Reemplazamos el halo normal por el arcoíris

                    # Texto principal encima
                    final_txt = Image.new("RGBA", (w, h), (0,0,0,0))
                    fd = ImageDraw.Draw(final_txt)
                    fd.text((pad, pad), texto, fill=(*text_col, 255), font=font, anchor="lt")
                    
                    result = Image.alpha_composite(glow_layer, final_txt)
                    lienzo.paste(result, (tx - pad, ty - pad), result)

                # Matemática real del porcentaje
                porcentaje = (posicion_ranking / total_jugadores) * 100
                
                # La Regla de Oro del Rey
                if posicion_ranking == 1:
                    porcentaje = 1.0
                
                porcentaje_int = max(1, int(porcentaje))
                texto_rango = f"{porcentaje_int}%"

                # ═════════════════════════════════════════════════════════════════
                # TIERS DE COLOR Y GLOW (Ahora con Arcoíris)
                # ═════════════════════════════════════════════════════════════════
                usa_arcoiris = False
                
                if porcentaje <= 1:
                    usa_arcoiris = True      # Activamos el RGB
                    g_col = (0, 0, 0)        # Se ignora, lo sobreescribe el arcoíris
                    t_col = (255, 255, 255)  # Texto blanco puro destaca hermoso en arcoíris
                    r_glow = 6               # Glow exagerado
                elif porcentaje <= 3:
                    g_col = (160, 210, 255)  # <= 3%: Azul plateado
                    t_col = (215, 235, 255)
                    r_glow = 4
                elif porcentaje <= 5:
                    g_col = (210, 120, 50)   # <= 5%: Bronce anaranjado
                    t_col = (255, 215, 160)
                    r_glow = 4
                elif porcentaje <= 10:
                    g_col = (213, 0, 249)    # <= 10%: Morado épico vibrante
                    t_col = (245, 215, 255)
                    r_glow = 3
                elif porcentaje <= 30:
                    g_col = (41, 121, 255)   # <= 30%: Azul eléctrico
                    t_col = (215, 235, 255)
                    r_glow = 2
                elif porcentaje <= 50:
                    g_col = (0, 230, 118)    # <= 50%: Verde sólido
                    t_col = (210, 255, 220)
                    r_glow = 2
                else:
                    g_col = (50, 50, 50)     # > 50%: Gris aburrido
                    t_col = (136, 136, 136)  # Texto oscuro
                    r_glow = 0               # Sin glow

                try:
                    f_porcentaje = ImageFont.truetype(_fp("BebasNeue-Regular.ttf"), 55)
                    f_lugar = ImageFont.truetype(_fp("BebasNeue-Regular.ttf"), 26)
                except Exception:
                    f_porcentaje = f_lugar = ImageFont.load_default()

                # 1. Dibujar el % gigante
                if r_glow > 0 or usa_arcoiris:
                    dibujar_texto_glow(
                        pos=(RANK_X, RANK_Y),
                        texto=texto_rango,
                        font=f_porcentaje,
                        anchor="mm",
                        glow_col=g_col,
                        text_col=t_col,
                        glow_radius=r_glow,
                        is_rainbow=usa_arcoiris
                    )
                else:
                    # Texto triste para > 50%
                    draw.text((RANK_X, RANK_Y), texto_rango, fill=t_col, font=f_porcentaje, anchor="mm")

                # 2. Dibujar #Posicion / Total debajo
                color_lugar = "#FFFFFF" if porcentaje <= 50 else "#888888"
                draw.text(
                    (RANK_X, RANK_Y + 45),
                    f"#{posicion_ranking} / {total_jugadores}",
                    fill=color_lugar,
                    font=f_lugar,
                    anchor="mm"
                )
            # =========================================================================
            
            if ruta_salida is None:
                # Modo web: devolver BytesIO para descarga directa
                buffer = BytesIO()
                lienzo.save(buffer, format='PNG')
                buffer.seek(0)
                return True, buffer
            else:
                # Modo normal: guardar en archivo
                lienzo.save(ruta_salida)
                return True, ruta_salida

        except Exception as e:
            return False, f"Error en Pillow: {str(e)}"

    def generar_ranking_card(self, top_data, nombre_agente, ruta_salida=None, criterio="maximo"):
        # ── Coordenadas medidas (540×960) ─────────────────────────────────────
        # Los 5 recuadros grises tienen x_contenido=136 (borde real del gris)
        # Box 1: y=150..214  Box 2: y=235..299  Box 3: y=328..392
        # Box 4: y=421..485  Box 5: y=513..577
        # Recuadro negro mindscape: y=137..194  x=0..157
        # Recuadro gris nombre:     y=601..777  x=16..539
        # Texto_Ranking banner:     y=33..117
        IMG_ANCHO, IMG_ALTO = 1080, 1920

        RANK_BOXES = [
            (300, 428),
            (470, 598),
            (656, 784),
            (842, 970),
            (1026, 1154),
        ]
        # X desde donde arranca el contenido en todos los recuadros
        CONTENT_X0   = 272
        CONTENT_X1   = 1078

        MIND_Y0, MIND_Y1 = 274, 388
        MIND_X0, MIND_X1 =   0, 314
        NAME_Y0, NAME_Y1 = 1202, 1554
        NAME_X0, NAME_X1 =  32, 1078
        TEXTO_Y_TOP, TEXTO_Y_BOT = 66, 300

        COLORES_HEX = {
            "Nicole": "#FF7CA4", "Anby": "#DCF921", "Billy": "#FF3B3B",
            "Nekomata": "#F6553B", "Koleda": "#FF7A1A", "Anton": "#FF7A1A",
            "Ben": "#F9951B", "Grace": "#FF7B4A", "Lycaon": "#C6E0E5",
            "Rina": "#E83445", "Ellen": "#FC3576", "Corin": "#C86BFF",
            "Zhu Yuan": "#33B5FF", "Qingyi": "#00F5BE", "Seth": "#6FA8FF",
            "Jane": "#FD3476", "Caesar": "#E6C76B", "Lighter": "#FF5A4F",
            "Lucy": "#F5B635", "Burnice": "#E6C76B", "Piper": "#FFBC01",
            "Pulchra": "#FFA94D", "Miyabi": "#1DC0C5", "Yanagi": "#FD7388",
            "Harumasa": "#FFCC00", "Soukaku": "#00E4FF", "Astra Yao": "#FF3A5A",
            "Evelyn": "#B69AE4", "Soldier 0 - Anby": "#FEBF25", "Hugo": "#FF3D57",
            "Vivian": "#9A7BFF", "Orphie & Magus": "#E72D50", "Trigger": "#FDC821",
            "Soldier 11": "#FFE34D", "Seed": "#FFD24D", "Yixuan": "#FFD966",
            "Ye Shunguang": "#FF6A3D", "Ju Fufu": "#FF9000", "Pan Yinhu": "#FDCB7A",
            "Yuzuha": "#F43638", "Alice": "#FDD07C", "Manato": "#FF4A3A",
            "Lucia": "#19CBE4", "Yidhari": "#B266FF", "Dialyn": "#6EFCEB",
            "Banyue": "#E8C98A", "Zhao": "#FF6993", "Sunna": "#D5FF63",
            "Aria": "#FE678A", "Nangong Yu": "#A872EB", "Cissia": "#EB348E", "Promeia": "#8449EF",
            "Starlight - Billy": "#C5454A"
        }

        facciones = {
            "Nicole": "liebres astutas", "Anby": "liebres astutas",
            "Billy": "liebres astutas", "Nekomata": "liebres astutas",
            "Koleda": "construcciones belobog", "Anton": "construcciones belobog",
            "Ben": "construcciones belobog", "Grace": "construcciones belobog",
            "Lycaon": "servicios domesticos victoria", "Rina": "servicios domesticos victoria",
            "Ellen": "servicios domesticos victoria", "Corin": "servicios domesticos victoria",
            "Zhu Yuan": "n.e.p.s.", "Qingyi": "n.e.p.s.", "Seth": "n.e.p.s.", "Cissia": "m_o_d_",
            "Jane": "r.o.v.e.r.",
            "Caesar": "hijos de calidon", "Lighter": "hijos de calidon",
            "Lucy": "hijos de calidon", "Burnice": "hijos de calidon",
            "Piper": "hijos de calidon", "Pulchra": "hijos de calidon",
            "Miyabi": "seccion 6", "Yanagi": "seccion 6",
            "Harumasa": "seccion 6", "Soukaku": "seccion 6",
            "Astra Yao": "estrellas de lyra", "Evelyn": "estrellas de lyra",
            "Soldier 0 - Anby": "batallon argente del ministerio de defensa",
            "Hugo": "ruisenor", "Vivian": "ruisenor",
            "Orphie & Magus": "batallon obolos", "Trigger": "batallon obolos",
            "Soldier 11": "batallon obolos", "Seed": "batallon obolos",
            "Yixuan": "pinaculo yunkui", "Ye Shunguang": "pinaculo yunkui",
            "Ju Fufu": "pinaculo yunkui", "Pan Yinhu": "pinaculo yunkui",
            "Yuzuha": "cabana del terror", "Alice": "cabana del terror",
            "Manato": "cabana del terror", "Lucia": "cabana del terror",
            "Yidhari": "cabana del terror",
            "Dialyn": "auditoria krampus", "Banyue": "auditoria krampus",
            "Zhao": "auditoria krampus", "Promeia": "auditoria krampus",
            "Sunna": "angeles de la delusion", "Aria": "angeles de la delusion", "Nangong Yu": "angeles de la delusion"
        }

        def hex_a_rgb(h):
            h = h.lstrip("#")
            return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

        def fuente_ajustada(texto, fp, tam_max, tam_min, ancho_max, dr):
            tam = tam_max
            while tam >= tam_min:
                try:    f = ImageFont.truetype(fp, tam)
                except: f = ImageFont.load_default()
                bb = dr.textbbox((0, 0), texto, font=f)
                if (bb[2] - bb[0]) <= ancho_max:
                    return f
                tam -= 2
            return f

        color_hex = COLORES_HEX.get(nombre_agente, "#323240")
        color_rgb = hex_a_rgb(color_hex)
        BB = "BebasNeue-Regular.ttf"
        # Top 4 y 5 oscuros; top 1-3 con efecto glow (luz irradiada)
        colores_puesto = ["#FFD700", "#C0C0C0", "#CD7F32", "#888888", "#888888"]
        COLOR_OSCURO   = (120, 120, 120, 255)   # nick y número puestos 4-5

        # Color del halo y del texto para cada puesto
        GLOW_COLORS = [
            (255, 200,  30),   # #1 — dorado cálido
            (160, 210, 255),   # #2 — azul plateado
            (210, 120,  50),   # #3 — bronce anaranjado
        ]
        TEXT_GLOW_COLORS = [
            (255, 255, 210),   # #1 — blanco cálido
            (215, 235, 255),   # #2 — blanco frío
            (255, 215, 160),   # #3 — blanco bronceado
        ]

        def texto_glow(pos, texto, font, anchor, glow_col, text_col,
                       glow_radius=3, glow_layers=3):
            """Texto con halo sutil — brillo tenue alrededor del texto."""
            bb = draw.textbbox(pos, texto, font=font, anchor=anchor)
            tx, ty, tx2, ty2 = bb
            pad = glow_radius + 3
            w = max(tx2 - tx + pad*2, 1)
            h = max(ty2 - ty + pad*2, 1)
            # Una sola pasada de glow suave
            glow_layer = Image.new("RGBA", (w, h), (0,0,0,0))
            for layer in range(glow_layers, 0, -1):
                radius = glow_radius * layer / glow_layers
                alpha  = int(90 * (layer / glow_layers) ** 2)
                colored = Image.new("RGBA", (w, h), (0,0,0,0))
                cd = ImageDraw.Draw(colored)
                cd.text((pad, pad), texto, fill=(*glow_col, alpha), font=font,
                        anchor="lt", stroke_width=max(1, int(radius)),
                        stroke_fill=(*glow_col, alpha))
                blurred = colored.filter(ImageFilter.GaussianBlur(radius=radius))
                glow_layer = Image.alpha_composite(glow_layer, blurred)
            # Texto limpio encima en color claro
            final_txt = Image.new("RGBA", (w, h), (0,0,0,0))
            fd = ImageDraw.Draw(final_txt)
            fd.text((pad, pad), texto, fill=(*text_col, 255), font=font, anchor="lt")
            result = Image.alpha_composite(glow_layer, final_txt)
            lienzo.paste(result, (tx - pad, ty - pad), result)

        def texto_metalico(draw, pos, texto, font, anchor, gradiente):
            """
            Dibuja texto con gradiente vertical metálico.
            Técnica: renderiza el texto en blanco sobre fondo negro,
            usa esa imagen como máscara de alpha, y aplica el gradiente
            de color píxel a píxel solo donde hay texto.
            """
            import numpy as np

            # 1. Bounding box con anchor para saber dónde cae el texto
            bb = draw.textbbox(pos, texto, font=font, anchor=anchor)
            tx, ty, tx2, ty2 = bb
            pad = 4
            w = max(tx2 - tx + pad * 2, 1)
            h = max(ty2 - ty + pad * 2, 1)

            # 2. Renderizar texto en blanco sobre negro → máscara de alpha
            mask_img = Image.new("L", (w, h), 0)
            mask_draw = ImageDraw.Draw(mask_img)
            mask_draw.text((pad - (tx - tx), pad),  # offset al origen
                           texto, fill=255, font=font, anchor="lt",
                           stroke_width=1)
            # Re-renderizar con anchor correcto referenciado al origen del bbox
            mask_img2 = Image.new("L", (w, h), 0)
            mask_draw2 = ImageDraw.Draw(mask_img2)
            # anchor "lt" desde esquina superior izquierda del bbox
            mask_draw2.text((pad, pad), texto, fill=255, font=font, anchor="lt",
                            stroke_width=1)
            alpha = np.array(mask_img2, dtype=np.float32) / 255.0  # 0.0-1.0

            # 3. Construir imagen de gradiente vertical del mismo tamaño
            n = len(gradiente)
            grad_arr = np.zeros((h, w, 4), dtype=np.uint8)
            for dy in range(h):
                t = dy / max(h - 1, 1)
                t_s = t * (n - 1)
                idx = int(t_s)
                frac = t_s - idx
                c0 = gradiente[min(idx,     n - 1)]
                c1 = gradiente[min(idx + 1, n - 1)]
                r  = int(c0[0] + (c1[0] - c0[0]) * frac)
                gr = int(c0[1] + (c1[1] - c0[1]) * frac)
                b  = int(c0[2] + (c1[2] - c0[2]) * frac)
                grad_arr[dy, :, 0] = r
                grad_arr[dy, :, 1] = gr
                grad_arr[dy, :, 2] = b
                grad_arr[dy, :, 3] = (alpha[dy] * 255).astype(np.uint8)

            text_img = Image.fromarray(grad_arr, "RGBA")

            # 4. Stroke negro debajo para legibilidad
            draw.text(pos, texto, fill=(0, 0, 0, 200), font=font, anchor=anchor,
                      stroke_width=2, stroke_fill=(0, 0, 0, 220))

            # 5. Pegar texto metálico encima
            lienzo.paste(text_img, (tx - pad, ty - pad), text_img)

        # ══════════════════════════════════════════════════════════════════════
        # CAPA 1 — Fondo sólido del agente
        # ══════════════════════════════════════════════════════════════════════
        lienzo = Image.new("RGBA", (IMG_ANCHO, IMG_ALTO), (*color_rgb, 255))

        # ══════════════════════════════════════════════════════════════════════
        # CAPA 2 — Imagen "fondo" (\images\builds\fondo.png)
        # ══════════════════════════════════════════════════════════════════════
        ruta_fondo = os.path.join(self.ruta_recursos, "images", "builds", "fondo.png")
        if os.path.exists(ruta_fondo):
            try:
                img_fondo = Image.open(ruta_fondo).convert("RGBA")
                img_fondo = img_fondo.resize((IMG_ANCHO, IMG_ALTO), Image.LANCZOS)
                lienzo.paste(img_fondo, (0, 0), img_fondo)
            except Exception as e:
                print(f"[ranking_card] fondo: {e}")

        # ══════════════════════════════════════════════════════════════════════
        # CAPA 3 — Imagen del agente
        # ══════════════════════════════════════════════════════════════════════
        IMG_AG_START_Y = 1440
        ruta_ag = os.path.join(self.ruta_recursos, "images", "ranking",
                               f"{nombre_agente}.png")
        if not os.path.exists(ruta_ag):
            ruta_ag = os.path.join(self.ruta_recursos, "images", "ranking",
                                   f"{nombre_agente.replace(' ', '_')}.png")
        if os.path.exists(ruta_ag):
            try:
                img_ag = Image.open(ruta_ag).convert("RGBA")
                zona_h = IMG_ALTO - IMG_AG_START_Y
                ratio  = max(IMG_ANCHO / img_ag.width, zona_h / img_ag.height)
                nw = int(img_ag.width  * ratio)
                nh = int(img_ag.height * ratio)
                img_ag = img_ag.resize((nw, nh), Image.LANCZOS)
                x_ag = (IMG_ANCHO - nw) // 2
                lienzo.paste(img_ag, (x_ag, IMG_AG_START_Y), img_ag)
            except Exception as e:
                print(f"[ranking_card] imagen agente: {e}")

        # ══════════════════════════════════════════════════════════════════════
        # CAPA 4 — Plantilla
        # ══════════════════════════════════════════════════════════════════════
        ruta_plantilla = os.path.join(self.ruta_recursos, "images", "builds",
                                      "Plantilla_Ranking_Vertical.png")
        if os.path.exists(ruta_plantilla):
            try:
                plantilla = Image.open(ruta_plantilla).convert("RGBA")
                plantilla = plantilla.resize((IMG_ANCHO, IMG_ALTO), Image.LANCZOS)
                lienzo.paste(plantilla, (0, 0), plantilla)
            except Exception as e:
                print(f"[ranking_card] plantilla: {e}")

        draw = ImageDraw.Draw(lienzo)

        # ══════════════════════════════════════════════════════════════════════
        # CAPA 3 — Contenido tarjetas ranking (todos desde x=136)
        # ══════════════════════════════════════════════════════════════════════
        try:
            f_puesto = ImageFont.truetype(BB, 72)
            f_score  = ImageFont.truetype(BB, 60)
        except:
            f_puesto = f_score = ImageFont.load_default()

        es_mix = False
        texto_mindscape = "M0"
        if top_data:
            niveles_mindscape = set()
            for item in top_data:
                if "_m_level" in item:
                    niveles_mindscape.add(int(item["_m_level"]))
                else:
                    niveles_mindscape.add(int(item.get("datos", {}).get("mindscape", 0)))
            
            if len(niveles_mindscape) > 1:
                es_mix = True
                texto_mindscape = "MIX"
            elif len(niveles_mindscape) == 1:
                texto_mindscape = f"M{niveles_mindscape.pop()}"

        ACENTO_W   = 10
        PUESTO_X   = CONTENT_X0 + 28
        NICK_X     = CONTENT_X0 + 120
        SCORE_X    = CONTENT_X1 - 24
        # NICK_MAX_W: espacio total entre NICK_X y SCORE_X menos margen para el score
        SCORE_RESERVA = 300   # px reservados para el score a la derecha
        NICK_MAX_W = SCORE_X - NICK_X - SCORE_RESERVA

        for i, (y0, y1) in enumerate(RANK_BOXES):
            item  = top_data[i] if (top_data and i < len(top_data)) else {}
            y_mid = (y0 + y1) // 2
            col_p = colores_puesto[i]

            # Acento color del agente — franja izquierda
            draw.rectangle([(CONTENT_X0, y0 + 4), (CONTENT_X0 + ACENTO_W, y1 - 4)],
                           fill=(*color_rgb, 255))

            # Puesto — glow para top 3, oscuro para el resto
            if i < 3:
                texto_glow((PUESTO_X, y_mid), f"#{i+1}",
                           f_puesto, "lm", GLOW_COLORS[i], TEXT_GLOW_COLORS[i])
            else:
                draw.text((PUESTO_X, y_mid), f"#{i+1}",
                          fill=COLOR_OSCURO, font=f_puesto, anchor="lm")

            # Nickname — usa f_puesto directamente, solo reduce si es muy largo
            nick_base = item.get("nombre_build", "---") if item else "---"
            if es_mix and item and nick_base != "---":
                m_lvl = int(item.get("_m_level", item.get("datos", {}).get("mindscape", 0)))
                nick = f"{nick_base} (M{m_lvl})"
            else:
                nick = nick_base
            try:
                f_nick = fuente_ajustada(nick, BB, 72, 48, NICK_MAX_W, draw)
            except:
                f_nick = f_puesto
            if i < 3:
                texto_glow((NICK_X, y_mid), nick,
                           f_nick, "lm", GLOW_COLORS[i], TEXT_GLOW_COLORS[i])
            else:
                draw.text((NICK_X, y_mid), nick,
                          fill=COLOR_OSCURO, font=f_nick, anchor="lm")

            # Score — metálico para top 3, plano para el resto
            valor     = item.get("score_valor", 0) if item else 0
            score_txt = f"{valor:.1f}%" if criterio == "calidad" else f"{valor:,.0f}"
            if i < 3:
                texto_glow((SCORE_X, y_mid), score_txt,
                           f_score, "rm", GLOW_COLORS[i], TEXT_GLOW_COLORS[i])
            else:
                draw.text((SCORE_X, y_mid), score_txt,
                          fill=COLOR_OSCURO, font=f_score, anchor="rm")

        # ══════════════════════════════════════════════════════════════════════
        # CAPA 4 — Mindscape: M# centrado en el recuadro negro
        # ══════════════════════════════════════════════════════════════════════
        texto_mindscape = "M0"
        
        if top_data:
            niveles_mindscape = set()
            for item in top_data:
                if "_m_level" in item:
                    niveles_mindscape.add(int(item["_m_level"]))
                else:
                    niveles_mindscape.add(int(item.get("datos", {}).get("mindscape", 0)))
            
            # Si hay más de un nivel distinto, es un MIX. Si no, ponemos el nivel único.
            if len(niveles_mindscape) > 1:
                texto_mindscape = "MIX"
            elif len(niveles_mindscape) == 1:
                texto_mindscape = f"M{niveles_mindscape.pop()}"

        try:
            tam_fuente = 90 if texto_mindscape == "MIX" else 112
            f_mind_num = ImageFont.truetype(BB, tam_fuente)
        except:
            f_mind_num = ImageFont.load_default()

        mind_cx = (MIND_X0 + MIND_X1) // 2
        mind_cy = (MIND_Y0 + MIND_Y1) // 2
        draw.text((mind_cx, mind_cy), texto_mindscape,
                  fill=color_rgb, font=f_mind_num, anchor="mm",
                  stroke_width=2, stroke_fill=(0, 0, 0, 220))

        # ══════════════════════════════════════════════════════════════════════
        # CAPA 5 — Recuadro gris nombre: nombre centrado + facción+elemento debajo
        # Offset: +20 en x, +5 en y respecto al centro del recuadro
        # ══════════════════════════════════════════════════════════════════════
        OFFSET_X = 10
        OFFSET_Y = 5
        name_box_cx = (NAME_X0 + NAME_X1) // 2 + OFFSET_X
        name_box_h  = NAME_Y1 - NAME_Y0    # 176 px

        # ── Detectar elemento ────────────────────────────────────────────────
        # datos["elemento"] ahora se guarda desde Calculadora_ZZZ.obtener_estado_actual_dict
        # Agentes especiales usan iconos propios en lugar del elemento
        agentes_especiales_elem = {
            "Miyabi":       "frost",
            "Yixuan":       "tinta aurica",
            "Ye Shunguang": "cortante",
        }
        elemento_str = "fisico"
        if nombre_agente in agentes_especiales_elem:
            elemento_str = agentes_especiales_elem[nombre_agente]
        else:
            datos0 = top_data[0].get("datos", {}) if top_data else {}
            # 1. Campo directo (ahora siempre debería estar)
            elem_raw = str(datos0.get("elemento", "") or "").strip()
            # 2. Fallback: bonus de daño en stats_reales
            if not elem_raw:
                stats_r = datos0.get("_stats_reales_calculo", datos0)
                if   float(stats_r.get("Electric DMG Bonus", stats_r.get("Bono_Electrico", 0))) > 0:
                    elem_raw = "electrico"
                elif float(stats_r.get("Fire DMG Bonus",     stats_r.get("Bono_Fuego",     0))) > 0:
                    elem_raw = "fuego"
                elif float(stats_r.get("Ice DMG Bonus",      stats_r.get("Bono_Hielo",     0))) > 0:
                    elem_raw = "hielo"
                elif float(stats_r.get("Ether DMG Bonus",    stats_r.get("Bono_Etereo",    0))) > 0:
                    elem_raw = "etereo"
            if elem_raw:
                e = (elem_raw.lower()
                     .replace("é","e").replace("í","i")
                     .replace("ó","o").replace("ú","u"))
                mapa = {"electric":"electrico","electricity":"electrico",
                        "ether":"etereo","fire":"fuego","ice":"hielo",
                        "physical":"fisico","eléctrico":"electrico",
                        "etéreo":"etereo","físico":"fisico"}
                elemento_str = mapa.get(e, e)

        # Tamaño de los iconos
        ICON_SIZE = 120
        icon_row_w = ICON_SIZE * 2 + 20  # facción + elemento + gap

        # Nombre: centrado en x con offset, posicionado al 40% + offset_y
        nombre_upper = nombre_agente.upper()
        nombre_max_w = NAME_X1 - NAME_X0 - 24
        nombre_y = NAME_Y0 + int(name_box_h * 0.40) + OFFSET_Y - 5
        try:
            f_nombre = fuente_ajustada(nombre_upper, BB, 160, 44, nombre_max_w, draw)
        except:
            f_nombre = ImageFont.load_default()
        draw.text((name_box_cx, nombre_y), nombre_upper,
                  fill=(255, 255, 255, 255), font=f_nombre, anchor="mm",
                  stroke_width=2, stroke_fill=(0, 0, 0, 180))

        # Fila de iconos: misma x con offset, 72% + offset_y
        icons_y = NAME_Y0 + int(name_box_h * 0.72) + OFFSET_Y + 5
        icon_start_x = name_box_cx - icon_row_w // 2

        # Icono facción — busca el archivo con múltiples variantes del nombre
        faccion_raw  = facciones.get(nombre_agente, "liebres astutas")
        faccion_norm = (faccion_raw
                        .replace("á","a").replace("é","e").replace("í","i")
                        .replace("ó","o").replace("ú","u").replace("ñ","n"))
        ruta_fac = None
        for cand in [
            faccion_norm,                          # ej: "n.e.p.s."
            faccion_norm.lower(),                  # lowercase
            faccion_norm.replace(".","_"),          # "n_e_p_s_"
            faccion_norm.lower().replace(".","_"),  # lowercase + guiones bajos
            faccion_norm.replace(" ","_"),          # espacios → guiones bajos
            faccion_norm.lower().replace(" ","_"),
        ]:
            c = os.path.join(self.ruta_recursos, "images", "faccion", f"{cand}.png")
            if os.path.exists(c):
                ruta_fac = c
                break
        if ruta_fac:
            try:
                img_fac = Image.open(ruta_fac).convert("RGBA")
                img_fac = img_fac.resize((ICON_SIZE, ICON_SIZE), Image.LANCZOS)
                lienzo.paste(img_fac, (icon_start_x, icons_y - ICON_SIZE // 2), img_fac)
            except Exception as e:
                print(f"[ranking_card] facción: {e}")
        else:
            print(f"[ranking_card] facción no encontrada: {faccion_norm}")

        # Icono elemento — prueba varias extensiones y capitalizaciones
        ruta_elem = None
        for nombre_elem in [elemento_str, elemento_str.capitalize()]:
            for ext in [".png", ".PNG"]:
                candidato = os.path.join(self.ruta_recursos, "images", "elementos",
                                         f"{nombre_elem}{ext}")
                if os.path.exists(candidato):
                    ruta_elem = candidato
                    break
            if ruta_elem:
                break
        if ruta_elem:
            try:
                img_el = Image.open(ruta_elem).convert("RGBA")
                img_el = img_el.resize((ICON_SIZE, ICON_SIZE), Image.LANCZOS)
                lienzo.paste(img_el, (icon_start_x + ICON_SIZE + 20, icons_y - ICON_SIZE // 2), img_el)
            except Exception as e:
                print(f"[ranking_card] elemento: {e}")
        else:
            print(f"[ranking_card] elemento no encontrado: {elemento_str}")

        # ══════════════════════════════════════════════════════════════════════
        # CAPA 7 — Texto_Ranking.png + texto TOP 5 DAÑO / TOP 5 BUILDS
        # ══════════════════════════════════════════════════════════════════════
        ruta_texto = os.path.join(self.ruta_recursos, "images", "builds",
                                  "Texto_Ranking.png")
        if os.path.exists(ruta_texto):
            try:
                texto_img = Image.open(ruta_texto).convert("RGBA")
                texto_img = texto_img.resize((IMG_ANCHO, IMG_ALTO), Image.LANCZOS)
                lienzo.paste(texto_img, (0, 0), texto_img)
            except Exception as e:
                print(f"[ranking_card] Texto_Ranking: {e}")

        draw = ImageDraw.Draw(lienzo)
        texto_banner = "TOP 5 BUILDS" if criterio == "calidad" else "TOP 5 DAMAGE"
        rect_cx = IMG_ANCHO // 2
        rect_cy = (TEXTO_Y_TOP + TEXTO_Y_BOT) // 2
        try:
            f_banner = fuente_ajustada(texto_banner, BB, 160, 60, 1020, draw)
        except:
            f_banner = ImageFont.load_default()
        draw.text((rect_cx, rect_cy), texto_banner,
                  fill=(0, 0, 0, 255), font=f_banner, anchor="mm")

        if ruta_salida is None:
            # Modo web: devolver BytesIO para descarga directa
            buffer = BytesIO()
            lienzo.save(buffer, format='PNG')
            buffer.seek(0)
            return buffer
        else:
            # Modo normal: guardar en archivo
            lienzo.save(ruta_salida)
            return None