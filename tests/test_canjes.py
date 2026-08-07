from tests.conftest import _crear_beneficio_en_bd, _crear_persona_en_bd


def _stock_beneficio(id_beneficio):
    from app.core.database import SessionLocal
    from app.models.orm import Beneficio

    with SessionLocal() as db:
        return db.get(Beneficio, id_beneficio).stock


def _cantidad_historial():
    from app.core.database import SessionLocal
    from app.models.orm import HistorialBeneficio

    with SessionLocal() as db:
        return db.query(HistorialBeneficio).count()


class TestCanjear:

    def test_canjear_ok(self, client):
        id_persona = _crear_persona_en_bd()
        id_beneficio = _crear_beneficio_en_bd(stock=5)

        respuesta = client.post(
            "/beneficios/canjear",
            params={"id_persona": id_persona, "id_beneficio": id_beneficio},
        )
        assert respuesta.status_code == 200
        assert respuesta.json()["mensaje"] == "Beneficio canjeado correctamente"

        assert _stock_beneficio(id_beneficio) == 4
        assert _cantidad_historial() == 1

    def test_canjear_persona_no_existe(self, client):
        id_beneficio = _crear_beneficio_en_bd()
        respuesta = client.post(
            "/beneficios/canjear",
            params={"id_persona": 9999, "id_beneficio": id_beneficio},
        )
        assert respuesta.status_code == 404
        assert respuesta.json()["detail"] == "Persona no encontrada"

    def test_canjear_beneficio_no_existe(self, client):
        id_persona = _crear_persona_en_bd()
        respuesta = client.post(
            "/beneficios/canjear",
            params={"id_persona": id_persona, "id_beneficio": 9999},
        )
        assert respuesta.status_code == 404
        assert respuesta.json()["detail"] == "Beneficio no encontrado"

    def test_canjear_sin_stock(self, client):
        id_persona = _crear_persona_en_bd()
        id_beneficio = _crear_beneficio_en_bd(stock=0)
        respuesta = client.post(
            "/beneficios/canjear",
            params={"id_persona": id_persona, "id_beneficio": id_beneficio},
        )
        assert respuesta.status_code == 400
        assert respuesta.json()["detail"] == "Beneficio sin stock"

    def test_canjear_repetido(self, client):
        id_persona = _crear_persona_en_bd()
        id_beneficio = _crear_beneficio_en_bd(stock=5)

        primero = client.post(
            "/beneficios/canjear",
            params={"id_persona": id_persona, "id_beneficio": id_beneficio},
        )
        assert primero.status_code == 200

        repetido = client.post(
            "/beneficios/canjear",
            params={"id_persona": id_persona, "id_beneficio": id_beneficio},
        )
        assert repetido.status_code == 400
        assert repetido.json()["detail"] == "Este beneficio ya fue canjeado por esta persona"

    def test_canjear_registra_auditoria(self, client, admin_headers):
        id_persona = _crear_persona_en_bd()
        id_beneficio = _crear_beneficio_en_bd()
        client.post(
            "/beneficios/canjear",
            params={"id_persona": id_persona, "id_beneficio": id_beneficio},
        )

        auditoria = client.get("/auditoria/", headers=admin_headers)
        assert auditoria.status_code == 200
        registros = auditoria.json()
        assert len(registros) == 1
        assert registros[0]["tabla_afectada"] == "historial_beneficios"
        assert registros[0]["usuario_accion"] == "publico"


class TestHistorial:

    def test_historial_persona_no_existe(self, client):
        respuesta = client.get("/beneficios/historial/9999")
        assert respuesta.status_code == 404
        assert respuesta.json()["detail"] == "Persona no encontrada"

    def test_historial_sin_canjes(self, client):
        id_persona = _crear_persona_en_bd()
        respuesta = client.get(f"/beneficios/historial/{id_persona}")
        assert respuesta.status_code == 200
        assert respuesta.json() == []

    def test_historial_con_canjes(self, client):
        id_persona = _crear_persona_en_bd()
        id_beneficio = _crear_beneficio_en_bd(nombre="Farmacia Municipal", stock=5)
        client.post(
            "/beneficios/canjear",
            params={"id_persona": id_persona, "id_beneficio": id_beneficio},
        )

        respuesta = client.get(f"/beneficios/historial/{id_persona}")
        assert respuesta.status_code == 200
        registro = respuesta.json()[0]
        assert registro["beneficio"] == "Farmacia Municipal"
        assert registro["codigo_canje"]
        assert registro["descuento"] == 1000
