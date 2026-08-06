"""
Actualizador de UIDs
Ejecuta en loop para actualizar constantemente los datos de los UIDs guardados.
Se ejecuta cada 5 minutos y actualiza el ranking global.
"""

import time
import logging
import sys
import os
from datetime import datetime, timedelta
from gestor_ranking import GestorRanking
from gestor_api import GestorApi
from cargar_datos import CargadorDatos

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

import logging.handlers

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

_console_handler = logging.StreamHandler(sys.stdout)
_console_handler.setStream(open(sys.stdout.fileno(), mode='w', encoding='utf-8', closefd=False))

import pathlib
_LOG_PATH = pathlib.Path(__file__).parent / 'actualizador_uids.log'

_file_handler = logging.handlers.RotatingFileHandler(
    str(_LOG_PATH),   # <-- ruta absoluta junto al .py
    maxBytes=5 * 1024 * 1024,
    backupCount=3,
    encoding='utf-8'
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[_file_handler, _console_handler]
)
logger = logging.getLogger(__name__)

class ActualizadorUIDs:
    """
    Actualiza periódicamente los datos de todos los UIDs guardados.
    """
    
    def __init__(self, ruta_guardados: str, datos_dir: str, intervalo_minutos: int = 5):
        """
        Args:
            ruta_guardados: Ruta donde se guardan los datos
            datos_dir: Ruta al directorio de datos de agentes
            intervalo_minutos: Intervalo entre actualizaciones (default: 5)
        """
        self.gestor_ranking = GestorRanking(ruta_guardados)
        self.gestor_api = GestorApi()
        self.intervalo = intervalo_minutos * 60
        self.ultima_actualizacion = {}
        logger.info(f"Cargando datos de agentes desde: {datos_dir}")
        import os
        try:
            self.cargador = CargadorDatos(datos_dir)
            
            nombre_archivo_personajes = "agentes.csv"
            self.agentes_data = self.cargador.cargar_csv(nombre_archivo_personajes)
            self.agentes_dict = {}
            
            if not self.agentes_data:
                logger.error(f"¡El CSV '{nombre_archivo_personajes}' devolvió 0 datos!")
            else:
                columnas = list(self.agentes_data[0].keys())                
                col_nombre = 'Nombre' if 'Nombre' in columnas else (columnas[0] if columnas else '')
                
                for agente in self.agentes_data:
                    nombre = agente.get(col_nombre, '')
                    if nombre:
                        self.agentes_dict[nombre] = agente
                        
                logger.info(f"Cargados {len(self.agentes_dict)} agentes en el diccionario")
                
                if self.agentes_dict:
                    nombres_guardados = list(self.agentes_dict.keys())
                
        except Exception as e:
            logger.error(f"Error cargando datos de agentes: {e}")
            self.agentes_data = []
            self.agentes_dict = {}
    
    def necesita_actualizacion(self, apodo: str) -> bool:
        """
        Verifica si un UID necesita ser actualizado basándose en:
        1. Si nunca ha sido actualizado
        2. Si han pasado más de 5 minutos desde la última actualización
        3. Si hay cambios detectados (implementación futura)
        """
        if apodo not in self.ultima_actualizacion:
            return True
        
        tiempo_desde_ultima = datetime.now() - self.ultima_actualizacion[apodo]
        return tiempo_desde_ultima.total_seconds() >= self.intervalo
    
    def actualizar_uid(self, apodo: str, uid: str) -> bool:
        """
        Actualiza los datos de un UID específico.
        
        Returns:
            True si la actualización fue exitosa, False en caso contrario
        """
        try:
            logger.info(f"Actualizando UID: {apodo} ({uid})")

            datos_completos = self.gestor_ranking.obtener_datos_completos_uid(
                uid, 
                self.gestor_api,
                self.agentes_dict
            )
            
            if not datos_completos:
                logger.error(f"No se pudieron obtener datos para {apodo} ({uid})")
                return False
            
            datos_completos['apodo'] = apodo
            self.gestor_ranking.actualizar_jugador_en_ranking(apodo, datos_completos)
            self.ultima_actualizacion[apodo] = datetime.now()
            personajes = datos_completos.get('personajes', {})
            num_personajes = len(personajes)
            
            if personajes:
                calificaciones = [p.get('calificacion', 0) for p in personajes.values()]
                promedio = sum(calificaciones) / len(calificaciones)
                logger.info(f"✓ {apodo}: {num_personajes} personajes | Calificación promedio: {promedio:.1f}")
            else:
                logger.info(f"✓ {apodo}: {num_personajes} personajes")
            
            return True
            
        except Exception as e:
            logger.error(f"✗ Error actualizando {apodo} ({uid}): {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def actualizar_todos(self):
        """Actualiza todos los UIDs que necesiten actualización."""
        uids = self.gestor_ranking.cargar_uids_guardados()
        
        if not uids:
            logger.info("No hay UIDs guardados para actualizar")
            return
        
        logger.info(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        logger.info(f"Iniciando actualización de {len(uids)} UIDs...")
        logger.info(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        exitosos = 0
        fallidos = 0
        saltados = 0
        
        for apodo, uid in uids.items():
            if self.necesita_actualizacion(apodo):
                if self.actualizar_uid(apodo, uid):
                    exitosos += 1
                else:
                    fallidos += 1
                time.sleep(2)
            else:
                logger.info(f"⊙ {apodo} (actualizado recientemente)")
                saltados += 1
        
        logger.info(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        logger.info(f"Actualización completada:")
        logger.info(f"  ✓ Exitosos: {exitosos}")
        logger.info(f"  ✗ Fallidos: {fallidos}")
        logger.info(f"  ⊙ Saltados: {saltados}")
        logger.info(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    def ejecutar_loop(self):
        """
        Ejecuta el loop principal de actualización.
        Se ejecuta indefinidamente actualizando cada X minutos.
        """
        logger.info(f"╔════════════════════════════════════════════════╗")
        logger.info(f"║  ACTUALIZADOR DE UIDs - RANKING GLOBAL         ║")
        logger.info(f"║  Intervalo: {self.intervalo/60:.0f} minutos                       ║")
        logger.info(f"╚════════════════════════════════════════════════╝")
        logger.info("")
        logger.info("Presiona Ctrl+C para detener")
        logger.info("")
        
        try:
            while True:
                inicio = time.time()
                
                self.actualizar_todos()
                
                tiempo_transcurrido = time.time() - inicio
                tiempo_espera = max(0, self.intervalo - tiempo_transcurrido)
                
                if tiempo_espera > 0:
                    proximo = datetime.now() + timedelta(seconds=tiempo_espera)
                    logger.info("")
                    logger.info(f"⏰ Próxima actualización: {proximo.strftime('%H:%M:%S')}")
                    logger.info(f"   Esperando {tiempo_espera/60:.1f} minutos...")
                    logger.info("")
                    time.sleep(tiempo_espera)
                
        except KeyboardInterrupt:
            logger.info("")
            logger.info("╔════════════════════════════════════════════════╗")
            logger.info("║  Actualizador detenido por el usuario          ║")
            logger.info("╚════════════════════════════════════════════════╝")
        except Exception as e:
            logger.error(f"Error en el loop principal: {e}")
            import traceback
            traceback.print_exc()
    
    def ejecutar_una_vez(self):
        """Ejecuta una única actualización de todos los UIDs."""
        logger.info("╔════════════════════════════════════════════════╗")
        logger.info("║  ACTUALIZACIÓN ÚNICA                            ║")
        logger.info("╚════════════════════════════════════════════════╝")
        logger.info("")
        self.actualizar_todos()
        logger.info("")
        logger.info("✓ Actualización única completada")
    
    def mostrar_estadisticas(self):
        """Muestra estadísticas del ranking actual."""
        ranking = self.gestor_ranking.cargar_ranking_global()
        
        if not ranking:
            logger.info("No hay datos en el ranking global")
            return
        
        logger.info("")
        logger.info("╔════════════════════════════════════════════════════════╗")
        logger.info("║       ESTADÍSTICAS DEL RANKING GLOBAL                  ║")
        logger.info("╚════════════════════════════════════════════════════════╝")
        logger.info("")
        logger.info(f"👥 Total de jugadores: {len(ranking)}")
        
        personajes_unicos = set()
        total_personajes = 0
        todas_calificaciones = []
        distribucion_tiers = {}
        
        for apodo, datos in ranking.items():
            personajes = datos.get('personajes', {})
            total_personajes += len(personajes)
            personajes_unicos.update(personajes.keys())
            
            for personaje_data in personajes.values():
                calificacion = personaje_data.get('calificacion', 0)
                tier = personaje_data.get('tier', 'MID')
                todas_calificaciones.append(calificacion)
                distribucion_tiers[tier] = distribucion_tiers.get(tier, 0) + 1
        
        logger.info(f"🎮 Total de personajes: {total_personajes}")
        logger.info(f"⭐ Personajes únicos: {len(personajes_unicos)}")
        
        if todas_calificaciones:
            promedio_global = sum(todas_calificaciones) / len(todas_calificaciones)
            max_calif = max(todas_calificaciones)
            min_calif = min(todas_calificaciones)
            
            logger.info("")
            logger.info("📊 Calificaciones:")
            logger.info(f"   Promedio global: {promedio_global:.1f}")
            logger.info(f"   Máxima: {max_calif}")
            logger.info(f"   Mínima: {min_calif}")
        
        if distribucion_tiers:
            logger.info("")
            logger.info("🏆 Distribución de Tiers:")
            orden_tiers = ['SSS', 'SS', 'S', 'A', 'B', 'C', 'MID']
            for tier in orden_tiers:
                if tier in distribucion_tiers:
                    cantidad = distribucion_tiers[tier]
                    porcentaje = (cantidad / len(todas_calificaciones)) * 100
                    barra = "█" * int(porcentaje / 2)
                    logger.info(f"   {tier:>4}: {barra} {cantidad} ({porcentaje:.1f}%)")
        
        contador_personajes = {}
        for datos in ranking.values():
            for nombre_personaje in datos.get('personajes', {}).keys():
                contador_personajes[nombre_personaje] = contador_personajes.get(nombre_personaje, 0) + 1
        
        if contador_personajes:
            top_personajes = sorted(contador_personajes.items(), key=lambda x: x[1], reverse=True)[:5]
            logger.info("")
            logger.info("🌟 Top 5 personajes más populares:")
            for i, (nombre, cantidad) in enumerate(top_personajes, 1):
                logger.info(f"   {i}. {nombre}: {cantidad} jugadores")
        
        logger.info("")
        logger.info("Top 5 jugadores por calificación promedio:")
        promedios_jugadores = []
        for apodo, datos in ranking.items():
            personajes = datos.get('personajes', {})
            if personajes:
                calificaciones = [p.get('calificacion', 0) for p in personajes.values()]
                promedio = sum(calificaciones) / len(calificaciones)
                promedios_jugadores.append((apodo, promedio, len(personajes)))
        
        promedios_jugadores.sort(key=lambda x: x[1], reverse=True)
        for i, (apodo, promedio, num_pers) in enumerate(promedios_jugadores[:5], 1):
            logger.info(f"   {i}. {apodo}: {promedio:.1f} ({num_pers} personajes)")
        
        logger.info("")
        logger.info("╚════════════════════════════════════════════════════════╝")
        logger.info("")


def main():
    """Punto de entrada principal."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Actualizador de UIDs para ranking global')
    parser.add_argument('--guardados', type=str, required=True, 
                       help='Ruta al directorio de guardados')
    parser.add_argument('--datos', type=str, required=True,
                       help='Ruta al directorio de datos de agentes')
    parser.add_argument('--intervalo', type=int, default=5,
                       help='Intervalo entre actualizaciones en minutos (default: 5)')
    parser.add_argument('--una-vez', action='store_true',
                       help='Ejecutar una sola vez y salir')
    parser.add_argument('--stats', action='store_true',
                       help='Mostrar estadísticas del ranking')
    parser.add_argument('--limpiar-cache', action='store_true',
                       help='Elimina el ranking_global.json y recalcula todo desde la API')

    args = parser.parse_args()

    actualizador = ActualizadorUIDs(
        ruta_guardados=args.guardados,
        datos_dir=args.datos,
        intervalo_minutos=args.intervalo
    )

    if args.stats:
        actualizador.mostrar_estadisticas()
    elif args.limpiar_cache:
        logger.info("Limpiando cache del ranking...")
        actualizador.gestor_ranking.limpiar_cache_ranking()
        logger.info("Cache limpiado. Ejecutando actualización completa...")
        actualizador.ejecutar_una_vez()
    elif args.una_vez:
        actualizador.ejecutar_una_vez()
    else:
        actualizador.ejecutar_loop()


if __name__ == '__main__':
    main()