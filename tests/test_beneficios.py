from tests.conftest import _crear_beneficio_en_bd

BENEFICIO_PAYLOAD = {
    "nombre": "Descuento Farmacia",
    "descripcion": "20% de descuento",
    "tipo_descuento": "monto_fijo",
    "valor_descuento": 2000,
    "stock": 100,
    "fecha_inicio": "2026-01-01",
    "fecha_vencimiento": "2026-12-31",
    "comercio": "Farmacia Municipal",
}


class TestListarBeneficios:

    def test_listar_vacio(self, client):
        respuesta = client.get("/beneficios/")
        assert respuesta.status_code == 200
        assert respuesta.json() == []

    def test_listar_solo_activos(self, client, admin_headers):
        id_beneficio = _crear_beneficio_en_bd()
        client.delete(f"/beneficios/eliminar/{id_beneficio}", headers=admin_headers)

        respuesta = client.get("/beneficios/")
        assert respuesta.status_code == 200
        assert respuesta.json() == []


class TestCrearBeneficio:

    def test_crear_ok(self, client, admin_headers):
        respuesta = client.post(
            "/beneficios/crear", json=BENEFICIO_PAYLOAD, headers=admin_headers
        )
        assert respuesta.status_code == 200
        assert respuesta.json()["id_beneficio"]
        assert respuesta.json()["mensaje"] == "Beneficio creado correctamente"

        listado = client.get("/beneficios/").json()
        assert len(listado) == 1
        assert listado[0]["nombre"] == "Descuento Farmacia"

    def test_crear_sin_token(self, client):
        respuesta = client.post("/beneficios/crear", json=BENEFICIO_PAYLOAD)
        assert respuesta.status_code == 401

    def test_crear_rol_insuficiente(self, client, funcionario_headers):
        respuesta = client.post(
            "/beneficios/crear", json=BENEFICIO_PAYLOAD, headers=funcionario_headers
        )
        assert respuesta.status_code == 403

    def test_crear_fecha_vencimiento_anterior(self, client, admin_headers):
        payload = {
            **BENEFICIO_PAYLOAD,
            "fecha_inicio": "2026-12-31",
            "fecha_vencimiento": "2026-01-01",
        }
        respuesta = client.post(
            "/beneficios/crear", json=payload, headers=admin_headers
        )
        assert respuesta.status_code == 422

    def test_crear_stock_negativo(self, client, admin_headers):
        payload = {**BENEFICIO_PAYLOAD, "stock": -1}
        respuesta = client.post(
            "/beneficios/crear", json=payload, headers=admin_headers
        )
        assert respuesta.status_code == 422


class TestActualizarBeneficio:

    def test_actualizar_ok(self, client, admin_headers):
        id_beneficio = _crear_beneficio_en_bd()
        payload = {**BENEFICIO_PAYLOAD, "nombre": "Descuento Renovado"}

        respuesta = client.put(
            f"/beneficios/actualizar/{id_beneficio}",
            json=payload,
            headers=admin_headers,
        )
        assert respuesta.status_code == 200
        assert respuesta.json()["mensaje"] == "Beneficio actualizado correctamente"

        listado = client.get("/beneficios/").json()
        assert listado[0]["nombre"] == "Descuento Renovado"

    def test_actualizar_no_existe(self, client, admin_headers):
        respuesta = client.put(
            "/beneficios/actualizar/9999",
            json=BENEFICIO_PAYLOAD,
            headers=admin_headers,
        )
        assert respuesta.status_code == 404
        assert respuesta.json()["detail"] == "Beneficio no encontrado"


class TestEliminarBeneficio:

    def test_eliminar_ok(self, client, admin_headers):
        id_beneficio = _crear_beneficio_en_bd()
        respuesta = client.delete(
            f"/beneficios/eliminar/{id_beneficio}", headers=admin_headers
        )
        assert respuesta.status_code == 200
        assert respuesta.json()["mensaje"] == "Beneficio eliminado correctamente"
        assert client.get("/beneficios/").json() == []

    def test_eliminar_no_existe(self, client, admin_headers):
        respuesta = client.delete(
            "/beneficios/eliminar/9999", headers=admin_headers
        )
        assert respuesta.status_code == 404
