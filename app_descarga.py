from flask import Flask, send_file, request, jsonify
from generador_imagenes import GeneradorTarjetas
import json

app = Flask(__name__)

# Inicializa el generador
generador = GeneradorTarjetas(ruta_recursos="./recursos")

@app.route('/descargar_build_card', methods=['POST'])
def descargar_build_card():
    """
    Endpoint para descargar una build card
    Recibe los datos del build en el body del POST
    """
    try:
        datos = request.json
        
        # Genera la imagen en memoria (sin guardar en disco)
        buffer = generador.generar_build_card(datos, ruta_salida=None)
        
        # Envía el archivo para descarga
        return send_file(
            buffer,
            mimetype='image/png',
            as_attachment=True,
            download_name='build_card.png'  # Nombre del archivo a descargar
        )
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/descargar_ranking_card', methods=['POST'])
def descargar_ranking_card():
    """
    Endpoint para descargar una ranking card
    """
    try:
        datos = request.json
        nombre_agente = datos.get('nombre_agente')
        top_data = datos.get('top_data')
        criterio = datos.get('criterio', 'calidad')
        
        # Genera la imagen en memoria
        buffer = generador.generar_ranking_card(
            nombre_agente, 
            top_data, 
            criterio, 
            ruta_salida=None
        )
        
        # Nombre del archivo dinámico
        nombre_archivo = f"{nombre_agente}_ranking.png"
        
        return send_file(
            buffer,
            mimetype='image/png',
            as_attachment=True,
            download_name=nombre_archivo
        )
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Opcional: Endpoint que solo guarda en servidor (modo anterior)
@app.route('/guardar_build_card', methods=['POST'])
def guardar_build_card():
    """
    Endpoint que guarda el archivo en el servidor (comportamiento original)
    """
    try:
        datos = request.json
        ruta = datos.get('ruta_salida', './outputs/build_card.png')
        
        # Guarda en disco
        generador.generar_build_card(datos, ruta_salida=ruta)
        
        return jsonify({"success": True, "path": ruta})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
