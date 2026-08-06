import json
from gestor_ranking import GestorRanking

gestor = GestorRanking("guardados")

with open(gestor.ruta_ranking, "r", encoding="utf-8") as f:
    ranking = json.load(f)

total = 0
for apodo, jugador in ranking.items():
    for nombre, datos_pj in jugador.get("personajes", {}).items():
        resultado = gestor.calcular_calificacion_personaje(datos_pj)
        datos_pj["calificacion"] = resultado["calificacion"]
        datos_pj["tier"] = resultado["tier"]
        datos_pj["breakdown"] = resultado["breakdown"]
        datos_pj["consejos"] = resultado["consejos"]
        total += 1

with open(gestor.ruta_ranking, "w", encoding="utf-8") as f:
    json.dump(ranking, f, ensure_ascii=False, indent=2)

print(f"Recalculados {total} personajes.")
