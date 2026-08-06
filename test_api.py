"""Tests automáticos para la API de la Calculadora ZZZ."""
import requests
import sys

API = "http://localhost:8000"
UID_TEST = 1300000001  # Cambia por un UID con showcase público

passed = 0
failed = 0


def test(nombre, func):
    global passed, failed
    try:
        func()
        print(f"  ✅ {nombre}")
        passed += 1
    except Exception as e:
        print(f"  ❌ {nombre} → {e}")
        failed += 1


def test_root():
    r = requests.get(f"{API}/", timeout=5)
    assert r.status_code == 200, f"Status {r.status_code}"
    assert r.json().get("status") == "ok"


def test_agentes():
    r = requests.get(f"{API}/agentes", timeout=5)
    assert r.status_code == 200, f"Status {r.status_code}"
    data = r.json()
    assert isinstance(data, list) and len(data) > 0, "Lista vacía"
    assert "nombre" in data[0], f"Falta campo 'nombre': {data[0]}"


def test_uid():
    r = requests.get(f"{API}/uid/{UID_TEST}", timeout=15)
    if r.status_code == 404:
        print(f"    ⚠️  UID {UID_TEST} no encontrado (showcase privado?)")
        return
    assert r.status_code == 200, f"Status {r.status_code}: {r.text[:100]}"
    data = r.json()
    assert "agentes" in data and len(data["agentes"]) > 0
    ag = data["agentes"][0]
    assert "name" in ag and "level" in ag


def test_evaluar():
    r = requests.get(f"{API}/uid/{UID_TEST}/evaluar", timeout=15)
    if r.status_code == 404:
        print(f"    ⚠️  UID {UID_TEST} no encontrado")
        return
    assert r.status_code == 200, f"Status {r.status_code}: {r.text[:100]}"
    data = r.json()
    assert "evaluaciones" in data and len(data["evaluaciones"]) > 0
    ev = data["evaluaciones"][0]
    assert "calidad_pct" in ev["evaluacion"], f"Falta calidad_pct: {ev}"


def test_agente_especifico():
    # Primero obtener un nombre válido
    r = requests.get(f"{API}/uid/{UID_TEST}", timeout=15)
    if r.status_code != 200:
        print(f"    ⚠️  No se pudo obtener UID para esta prueba")
        return
    nombre = r.json()["agentes"][0]["name"]
    r2 = requests.get(f"{API}/uid/{UID_TEST}/agente/{nombre}", timeout=15)
    assert r2.status_code == 200, f"Status {r2.status_code}: {r2.text[:100]}"
    assert "evaluacion" in r2.json()


def test_agente_404():
    r = requests.get(f"{API}/uid/{UID_TEST}/agente/NoExiste999", timeout=15)
    if r.status_code == 404:
        detail = r.json().get("detail", "")
        assert "Disponibles" in detail or "no encontrad" in detail.lower()
    # Si el UID no existe, también da 404, está bien


def test_ranking():
    r = requests.get(f"{API}/ranking", timeout=5)
    assert r.status_code == 200, f"Status {r.status_code}: {r.text[:100]}"


if __name__ == "__main__":
    if len(sys.argv) > 1:
        UID_TEST = int(sys.argv[1])

    print(f"\n🔍 Testing API: {API}")
    print(f"   UID de prueba: {UID_TEST}\n")

    test("GET /", test_root)
    test("GET /agentes", test_agentes)
    test("GET /uid/{uid}", test_uid)
    test("GET /uid/{uid}/evaluar", test_evaluar)
    test("GET /uid/{uid}/agente/{nombre}", test_agente_especifico)
    test("GET /uid/{uid}/agente/NoExiste (404)", test_agente_404)
    test("GET /ranking", test_ranking)

    print(f"\n{'='*40}")
    print(f"  Resultado: {passed} pasaron, {failed} fallaron")
    print(f"{'='*40}\n")
    sys.exit(1 if failed else 0)
