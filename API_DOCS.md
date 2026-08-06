# Calculadora ZZZ - API

Base URL: `http://140.84.187.50:8000`

Documentación interactiva: [http://140.84.187.50:8000/docs](http://140.84.187.50:8000/docs)

---

## Endpoints

### `GET /agentes`
Lista todos los agentes disponibles.

**Respuesta:**
```json
[
  {"nombre": "Miyabi", "tipo": "Anomalo", "elemento": "Hielo", "rango": "S"},
  {"nombre": "Ellen", "tipo": "Atacante", "elemento": "Hielo", "rango": "S"},
  ...
]
```

---

### `GET /uid/{uid}`
Consulta un UID en Enka Network. Devuelve los agentes del showcase con stats, discos y weapon.

**Ejemplo:** `GET /uid/1300000001`

**Respuesta:**
```json
{
  "uid": 1300000001,
  "nick": "NombreJugador",
  "agentes": [
    {
      "name": "Miyabi",
      "level": 60,
      "element": "Ice",
      "specialty": "Anomaly",
      "stats": {"CRIT Rate": {"value": 0.55, "formatted": "55.0%"}, ...},
      "weapon": {"name": "Hailstorm Shrine", "rarity": 5, "level": 60, "refinement": 1},
      "discs": [...],
      "mindscape": 0
    }
  ]
}
```

---

### `GET /uid/{uid}/evaluar`
Evalúa la calidad de build de **todos** los agentes de un UID.

**Ejemplo:** `GET /uid/1300000001/evaluar`

**Respuesta:**
```json
{
  "uid": 1300000001,
  "nick": "NombreJugador",
  "evaluaciones": [
    {
      "nombre": "Miyabi",
      "level": 60,
      "element": "Ice",
      "weapon": "Hailstorm Shrine",
      "evaluacion": {
        "calidad_pct": 78.5,
        "rolls_ideal": 24,
        "rolls_decente": 8,
        "rolls_basura": 12,
        "total_rolls": 44
      }
    }
  ]
}
```

---

### `GET /uid/{uid}/agente/{nombre}`
Evalúa un agente específico. El nombre no distingue mayúsculas/minúsculas.

**Ejemplo:** `GET /uid/1300000001/agente/miyabi`

**Respuesta:**
```json
{
  "uid": 1300000001,
  "nick": "NombreJugador",
  "agente": { ... },
  "evaluacion": {
    "calidad_pct": 78.5,
    "rolls_ideal": 24,
    "rolls_decente": 8,
    "rolls_basura": 12,
    "total_rolls": 44
  }
}
```

Si el agente no está en el showcase, devuelve 404 con la lista de agentes disponibles.

---

### `GET /ranking`
Devuelve el ranking global de jugadores registrados.

---

## Ejemplos de uso

### Python (para bots de Discord)
```python
import requests

API = "http://140.84.187.50:8000"

# Evaluar un UID completo
r = requests.get(f"{API}/uid/1300000001/evaluar")
data = r.json()

for agente in data["evaluaciones"]:
    print(f"{agente['nombre']}: {agente['evaluacion']['calidad_pct']}%")
```

### JavaScript (Node.js)
```javascript
const res = await fetch("http://140.84.187.50:8000/uid/1300000001/evaluar");
const data = await res.json();

data.evaluaciones.forEach(a => {
  console.log(`${a.nombre}: ${a.evaluacion.calidad_pct}%`);
});
```

### cURL
```bash
curl http://140.84.187.50:8000/uid/1300000001/evaluar
```

---

### `GET /assets/list`
Lista todos los archivos disponibles en `/assets`.

**Parámetros opcionales:**
- `categoria` — Subcarpeta a filtrar (ej: `images`, `images/Iconos`, `images/wengine`)

**Ejemplo:** `GET /assets/list?categoria=images/Iconos`

**Respuesta:**
```json
{
  "total": 52,
  "archivos": ["images/Iconos/Alice.png", "images/Iconos/Anby.png", ...]
}
```

Para descargar un archivo directamente: `GET /assets/images/Iconos/Alice.png`

---

### `GET /images/list`
Lista todos los archivos disponibles en `/images`.

**Parámetros opcionales:**
- `categoria` — Subcarpeta a filtrar (ej: `Iconos`, `wengine`, `discos`, `elementos`, `enemigos`, `faccion`, `ranking`, `builds`, `buffs`)

**Ejemplo:** `GET /images/list?categoria=wengine`

**Respuesta:**
```json
{
  "total": 85,
  "archivos": ["wengine/Deep Sea Visitor.png", "wengine/Hailstorm Shrine.png", ...]
}
```

Para descargar un archivo directamente: `GET /images/wengine/Deep%20Sea%20Visitor.png`

---

### Archivos estáticos (assets e imágenes)

Todos los assets e imágenes están disponibles directamente por URL:

| Ruta | Contenido |
|------|-----------|
| `/images/Iconos/{nombre}.png` | Iconos de agentes |
| `/images/wengine/{nombre}.png` | Imágenes de W-Engines |
| `/images/discos/{nombre}.png` | Imágenes de sets de discos |
| `/images/elementos/{nombre}.png` | Iconos de elementos y roles |
| `/images/enemigos/{nombre}.png` | Imágenes de enemigos |
| `/images/faccion/{nombre}.png` | Logos de facciones |
| `/images/builds/{nombre}.png` | Splash arts para builds |
| `/assets/` | Assets generales (favicon, build cards generadas, etc.) |

**Nota:** Los nombres con espacios deben ir URL-encoded (`%20`).

---

## Errores

| Código | Significado |
|--------|-------------|
| 404 | UID no encontrado o agente no está en el showcase |
| 503 | Enka Network en mantenimiento |
| 500 | Error interno |

---

## Notas
- La API consulta Enka Network en tiempo real, puede tardar 2-5 segundos por request.
- El showcase del jugador debe estar público en el juego para que funcione.
- No hay límite de requests por ahora, pero no abusen 🙏
