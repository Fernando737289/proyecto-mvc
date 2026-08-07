from tests.conftest import _crear_persona_en_bd


def _id_tarjeta():
    from app.core.database import SessionLocal
    from app.models.orm import Tarjeta

    with SessionLocal() as db:
        return db.query(Tarjeta).first().id_tarjeta

PERSONA = {
    "rut": "14187947-2",
    "nombres": "Francisco",
    "apellidos": "Baez",
    "telefono": "912345678",
}


class TestCrearTarjeta:

    def test_crear_ok(self, client, admin_headers):
        _crear_persona_en_bd(telefono="912345678")

        respuesta = client.post(
            "/tarjeta/crear", json=PERSONA, headers=admin_headers
        )
        assert respuesta.status_code == 200
        body = respuesta.json()
        assert body["mensaje"] == "Tarjeta creada correctamente"
        assert body["numero_tarjeta"]

        numero = body["numero_tarjeta"]
        tarjeta = client.get(
            f"/tarjeta/buscar?numero_tarjeta={numero}"
        ).json()
        assert tarjeta["estado"] == "activa"
        assert tarjeta["codigo_qr"]

    def test_crear_sin_token(self, client):
        _crear_persona_en_bd()
        respuesta = client.post("/tarjeta/crear", json=PERSONA)
        assert respuesta.status_code == 401

    def test_crear_rol_insuficiente(self, client, funcionario_headers):
        _crear_persona_en_bd()
        respuesta = client.post(
            "/tarjeta/crear", json=PERSONA, headers=funcionario_headers
        )
        assert respuesta.status_code == 403

    def test_crear_persona_no_existe(self, client, admin_headers):
        payload = {**PERSONA, "rut": "11111111-1"}
        respuesta = client.post(
            "/tarjeta/crear", json=payload, headers=admin_headers
        )
        assert respuesta.status_code == 404
        assert respuesta.json()["detail"] == "Persona no encontrada"

    def test_crear_nombres_no_coinciden(self, client, admin_headers):
        _crear_persona_en_bd()
        payload = {**PERSONA, "nombres": "Otro Nombre"}
        respuesta = client.post(
            "/tarjeta/crear", json=payload, headers=admin_headers
        )
        assert respuesta.status_code == 400
        assert respuesta.json()["detail"] == "Los nombres no coinciden con los registros"

    def test_crear_apellidos_no_coinciden(self, client, admin_headers):
        _crear_persona_en_bd()
        payload = {**PERSONA, "apellidos": "Otro Apellido"}
        respuesta = client.post(
            "/tarjeta/crear", json=payload, headers=admin_headers
        )
        assert respuesta.status_code == 400

    def test_crear_telefono_no_coincide(self, client, admin_headers):
        _crear_persona_en_bd(telefono="912345678")
        payload = {**PERSONA, "telefono": "999999999"}
        respuesta = client.post(
            "/tarjeta/crear", json=payload, headers=admin_headers
        )
        assert respuesta.status_code == 400
        assert respuesta.json()["detail"] == "El teléfono no coincide con los registros"

    def test_crear_tarjeta_duplicada(self, client, admin_headers):
        _crear_persona_en_bd(telefono="912345678")
        primera = client.post(
            "/tarjeta/crear", json=PERSONA, headers=admin_headers
        )
        assert primera.status_code == 200

        respuesta = client.post(
            "/tarjeta/crear", json=PERSONA, headers=admin_headers
        )
        assert respuesta.status_code == 400
        assert respuesta.json()["detail"] == "La persona ya posee una tarjeta"

    def test_crear_rut_dv_invalido(self, client, admin_headers):
        payload = {**PERSONA, "rut": "12345678-9"}
        respuesta = client.post(
            "/tarjeta/crear", json=payload, headers=admin_headers
        )
        assert respuesta.status_code == 422


class TestBuscarTarjeta:

    def test_buscar_sin_parametros(self, client):
        respuesta = client.get("/tarjeta/buscar")
        assert respuesta.status_code == 400

    def test_buscar_no_encontrada(self, client):
        respuesta = client.get("/tarjeta/buscar?numero_tarjeta=000000")
        assert respuesta.status_code == 404
        assert respuesta.json()["detail"] == "Tarjeta no encontrada"

    def test_buscar_por_rut(self, client, admin_headers):
        _crear_persona_en_bd(telefono="912345678")
        numero = client.post(
            "/tarjeta/crear", json=PERSONA, headers=admin_headers
        ).json()["numero_tarjeta"]

        respuesta = client.get("/tarjeta/buscar?rut=14187947-2")
        assert respuesta.status_code == 200
        assert respuesta.json()["numero_tarjeta"] == numero
        assert respuesta.json()["nombres"] == "Francisco"


class TestActualizarTarjeta:

    def test_actualizar_ok(self, client, admin_headers):
        _crear_persona_en_bd(telefono="912345678")
        numero = client.post(
            "/tarjeta/crear", json=PERSONA, headers=admin_headers
        ).json()["numero_tarjeta"]
        id_tarjeta = _id_tarjeta()

        respuesta = client.put(
            f"/tarjeta/{id_tarjeta}",
            json={"estado": "bloqueada", "fecha_vencimiento": "2027-12-31"},
            headers=admin_headers,
        )
        assert respuesta.status_code == 200
        assert respuesta.json()["mensaje"] == "Tarjeta actualizada correctamente"

        actualizada = client.get(f"/tarjeta/buscar?numero_tarjeta={numero}").json()
        assert actualizada["estado"] == "bloqueada"

    def test_actualizar_no_existe(self, client, admin_headers):
        respuesta = client.put(
            "/tarjeta/9999",
            json={"estado": "bloqueada", "fecha_vencimiento": "2027-12-31"},
            headers=admin_headers,
        )
        assert respuesta.status_code == 404


class TestEliminarTarjeta:

    def test_eliminar_ok(self, client, admin_headers):
        _crear_persona_en_bd(telefono="912345678")
        client.post("/tarjeta/crear", json=PERSONA, headers=admin_headers).json()[
            "numero_tarjeta"
        ]
        id_tarjeta = _id_tarjeta()

        respuesta = client.delete(f"/tarjeta/{id_tarjeta}", headers=admin_headers)
        assert respuesta.status_code == 200
        assert respuesta.json()["mensaje"] == "Tarjeta eliminada correctamente"

    def test_eliminar_no_existe(self, client, admin_headers):
        respuesta = client.delete("/tarjeta/9999", headers=admin_headers)
        assert respuesta.status_code == 404
