import json
import os

IDIOMAS_DISPONIBLES = {
    "es": "Español",
    "en": "English",
    "ja": "日本語",
    "zh": "中文",
}

class Traductor:
    def __init__(self, idioma_por_defecto="en"):
        self.idioma_actual = idioma_por_defecto
        self.textos = {}
        self._callbacks_cambio = []
        self.cargar_idioma(self.idioma_actual)

    def cargar_idioma(self, idioma):
        ruta = os.path.join(os.path.dirname(__file__), "locales", f"{idioma}.json")
        try:
            with open(ruta, 'r', encoding='utf-8') as f:
                self.textos = json.load(f)
            self.idioma_actual = idioma
        except FileNotFoundError:
            print(f"Idioma '{idioma}' no encontrado. Manteniendo idioma anterior.")

    def cambiar_idioma(self, nuevo_idioma):
        """Cambia el idioma activo y notifica a todos los suscriptores."""
        if nuevo_idioma == self.idioma_actual:
            return
        self.cargar_idioma(nuevo_idioma)
        for cb in self._callbacks_cambio:
            try:
                cb()
            except Exception as ex:
                print(f"Error en callback de cambio de idioma: {ex}")

    def on_cambio(self, callback):
        """Registra una función que se ejecutará al cambiar de idioma."""
        if callback not in self._callbacks_cambio:
            self._callbacks_cambio.append(callback)

    def idiomas_disponibles(self):
        """Retorna los idiomas que tienen archivo .json en locales/."""
        carpeta = os.path.join(os.path.dirname(__file__), "locales")
        disponibles = {}
        for codigo, nombre in IDIOMAS_DISPONIBLES.items():
            if os.path.exists(os.path.join(carpeta, f"{codigo}.json")):
                disponibles[codigo] = nombre
        return disponibles

    def t(self, clave_jerarquica, default=None, **kwargs):
        """
        Busca la traducción por clave jerárquica (ej: 'ui.tabs.dps').
        Si no existe, devuelve 'default' o '[clave]'.
        Formatea variables automáticamente con kwargs.
        """
        claves = clave_jerarquica.split('.')
        valor = self.textos
        for c in claves:
            if isinstance(valor, dict) and c in valor:
                valor = valor[c]
            else:
                valor = default if default is not None else f"[{clave_jerarquica}]"
                break

        if kwargs and isinstance(valor, str):
            try:
                return valor.format(**kwargs)
            except KeyError:
                return valor
        return valor

traductor_global = Traductor("en")