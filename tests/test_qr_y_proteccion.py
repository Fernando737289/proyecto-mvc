from tests.conftest import _crear_persona_en_bd, _crear_tarjeta_en_bd


def _qr_guardado(id_tarjeta):
    from app.core.database import SessionLocal
    from app.models.orm import Tarjeta

    with SessionLocal() as db:
        return db.get(Tarjeta, id_tarjeta).codigo_qr


class TestGenerarQR:

    def test_generar_ok(self, client, admin_headers):
        id_persona = _crear_persona_en_bd()
        id_tarjeta = _crear_tarjeta_en_bd(id_persona)

        respuesta = client.post(
            "/qr/generar", json={"rut": "14187947-2"}, headers=admin_headers
        )
        assert respuesta.status_code == 200
        assert respuesta.json()["codigo_qr"]

        assert _qr_guardado(id_tarjeta) == respuesta.json()["codigo_qr"]
        assert _qr_guardado(id_tarjeta) != "qr-anterior"

    def test_generar_persona_sin_tarjeta(self, client, admin_headers):
        _crear_persona_en_bd()
        respuesta = client.post(
            "/qr/generar", json={"rut": "14187947-2"}, headers=admin_headers
        )
        assert respuesta.status_code == 404
        assert respuesta.json()["detail"] == "La persona no posee una tarjeta"

    def test_generar_persona_no_existe(self, client, admin_headers):
        respuesta = client.post(
            "/qr/generar", json={"rut": "11111111-1"}, headers=admin_headers
        )
        assert respuesta.status_code == 404
        assert respuesta.json()["detail"] == "Persona no encontrada"

    def test_generar_rut_dv_invalido(self, client, admin_headers):
        respuesta = client.post(
            "/qr/generar", json={"rut": "12345678-9"}, headers=admin_headers
        )
        assert respuesta.status_code == 422

    def test_generar_sin_rut(self, client, admin_headers):
        respuesta = client.post("/qr/generar", json={}, headers=admin_headers)
        assert respuesta.status_code == 422

    def test_generar_sin_token(self, client):
        respuesta = client.post("/qr/generar", json={"rut": "14187947-2"})
        assert respuesta.status_code == 401

    def test_generar_rol_insuficiente(self, client, funcionario_headers):
        respuesta = client.post(
            "/qr/generar",
            json={"rut": "14187947-2"},
            headers=funcionario_headers,
        )
        assert respuesta.status_code == 403


class TestEndpointsProtegidos:

    def test_auditoria_sin_token(self, client):
        respuesta = client.get("/auditoria/")
        assert respuesta.status_code == 401

    def test_auditoria_rol_insuficiente(self, client, funcionario_headers):
        respuesta = client.get("/auditoria/", headers=funcionario_headers)
        assert respuesta.status_code == 403

    def test_auditoria_ok(self, client, admin_headers):
        respuesta = client.get("/auditoria/", headers=admin_headers)
        assert respuesta.status_code == 200
        assert respuesta.json() == []

    def test_health_db(self, client):
        respuesta = client.get("/health/test-db")
        assert respuesta.status_code == 200
