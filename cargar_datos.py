import pandas as pd
import os
import logging

class CargadorDatos:
    
    def __init__(self, base_path):
        self.base_path = base_path
        self.wengines_data = {}
        self.sets_data = []
        self.discos_data = {}
        self.substats_data = []

    def cargar_todo(self):
        self.wengines_data = self.cargar_wengine("wengine.csv", campos_numericos=["Ataque wengine"])
        self.sets_data = self.cargar_csv("sets.csv", campos_numericos=["valor"])
        self.substats_data = self.cargar_csv("substat.csv", campos_numericos=["valor"])
        
        discos_planos = self.cargar_csv("discos.csv", campos_numericos=["valor"])
        self.discos_data = {4: [], 5: [], 6: []}
        for d in discos_planos:
            try:
                slot = int(d.get('slot', d.get('Slot', 0)))
                if slot in self.discos_data:
                    self.discos_data[slot].append(d)
            except: continue

    def cargar_agentes(self):
        """
        Carga los datos de los agentes/personajes desde el CSV.
        Asegúrate de que el nombre del archivo ('agentes.csv') coincida con el tuyo.
        """
        return self.cargar_csv("agentes.csv")

    def cargar_csv(self, nombre_archivo, campos_numericos=None):
        """
        Carga un archivo CSV y lo convierte en una lista de diccionarios.
        CORRECCIÓN: Limpia los espacios de las cabeceras para evitar errores.
        """
        ruta_archivo = os.path.join(self.base_path, nombre_archivo)
        if not os.path.exists(ruta_archivo):
            return []
        try:
            df = pd.read_csv(ruta_archivo, delimiter=';', encoding='utf-8-sig', dtype=str)
            df = df.fillna('')
            
            df = df.rename(columns=lambda x: x.strip())
            
            if campos_numericos:
                for campo in campos_numericos:
                    if campo in df.columns:
                        df[campo] = pd.to_numeric(
                            df[campo].astype(str).str.replace(',', '.'), 
                            errors='coerce'
                        ).fillna(0)
            
            return df.to_dict('records')
        except Exception as e:
            return []

    def cargar_wengine(self, nombre_archivo, campos_numericos=None):
        """
        Carga los datos de W-Engine, usando el nombre como clave del diccionario.
        """
        ruta_archivo = os.path.join(self.base_path, nombre_archivo)
        if not os.path.exists(ruta_archivo):
            return {}
        try:
            df = pd.read_csv(ruta_archivo, delimiter=';', encoding='utf-8-sig', dtype=str)
            df = df.fillna('')
            df = df.rename(columns=lambda x: x.strip()) 
            
            if 'Nombre W-Engine' not in df.columns:
                return {}

            df.set_index('Nombre W-Engine', inplace=True)
            
            if campos_numericos:
                for campo in campos_numericos:
                    if campo in df.columns:
                        df[campo] = pd.to_numeric(
                            df[campo].astype(str).str.replace(',', '.'), 
                            errors='coerce'
                        ).fillna(0)

            return df.to_dict('index')
        except Exception as e:
            return {}
    
