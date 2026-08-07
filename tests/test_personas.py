from tests.conftest import FUNCIONARIO_PASSWORD, _crear_persona_en_bd

PERSONA_PAYLOAD = {
    "rut": "14187947-2",
    "serial_number": "ABC-123",
    "nombres": "Francisco",
    "apellidos": "Baez",
    "direccion": "Av. Central 123",
    "numero_direccion": "123",
    "telefono": "912345678",
    "email": "francisco@example.cl",
    "fecha_nacimiento": "1990-05-10",
}


class TestListarPersonas:

    def test_listar_sin_datos(self, client):
        respuesta = client.get("/users/")
        assert respuesta.status_code == 200
        assert respuesta.json() == []

    def test_listar_con_personas(self, client):
        _crear_persona_en_bd()
        respuesta = client.get("/users/")
        assert respuesta.status_code == 200
        assert len(respuesta.json()) == 1
        assert respuesta.json()[0]["rut"] == "14187947-2"


class TestCrearPersona:

    def test_crear_ok(self, client, dec_valida, admin_headers):
        respuesta = client.post(
            "/users/usuarios", json=PERSONA_PAYLOAD, headers=admin_headers
        )
        assert respuesta.status_code == 200
        assert respuesta.json()["status"] == "success"

        listado = client.get("/users/").json()
        assert len(listado) == 1
        assert listado[0]["nombres"] == "Francisco"

    def test_crear_sin_token(self, client, dec_valida):
        respuesta = client.post("/users/usuarios", json=PERSONA_PAYLOAD)
        assert respuesta.status_code == 401

    def test_crear_rol_insuficiente(self, client, dec_valida, funcionario_headers):
        respuesta = client.post(
            "/users/usuarios", json=PERSONA_PAYLOAD, headers=funcionario_headers
        )
        assert respuesta.status_code == 403

    def test_crear_cedula_no_vigente(self, client, dec_no_vigente, admin_headers):
        respuesta = client.post(
            "/users/usuarios", json=PERSONA_PAYLOAD, headers=admin_headers
        )
        assert respuesta.status_code == 400
        assert "vigente" in respuesta.json()["detail"]

    def test_crear_cedula_sin_verificar(self, client, monkeypatch, admin_headers):
        async def fake_validar(user_rut, serial_number, api_key=None):
            return {"status": 500, "result": {}}

        monkeypatch.setattr(
            "app.services.user_service.validar_vigencia_rut", fake_validar
        )
        respuesta = client.post(
            "/users/usuarios", json=PERSONA_PAYLOAD, headers=admin_headers
        )
        assert respuesta.status_code == 400
        assert respuesta.json()["detail"] == "No se pudo verificar la cédula con el servicio externo."

    def test_crear_rut_duplicado(self, client, dec_valida, admin_headers):
        _crear_persona_en_bd(rut="14187947-2")
        respuesta = client.post(
            "/users/usuarios", json=PERSONA_PAYLOAD, headers=admin_headers
        )
        assert respuesta.status_code == 400
        assert respuesta.json()["detail"] == "Ya existe una persona registrada con ese RUT"

    def test_crear_rut_dv_invalido(self, client, dec_valida, admin_headers):
        payload = {**PERSONA_PAYLOAD, "rut": "12345678-9"}
        respuesta = client.post(
            "/users/usuarios", json=payload, headers=admin_headers
        )
        assert respuesta.status_code == 422

    def test_crear_serial_vacio(self, client, dec_valida, admin_headers):
        payload = {**PERSONA_PAYLOAD, "serial_number": "   "}
        respuesta = client.post(
            "/users/usuarios", json=payload, headers=admin_headers
        )
        assert respuesta.status_code == 422


class TestActualizarPersona:

    def test_actualizar_ok(self, client, admin_headers):
        id_persona = _crear_persona_en_bd()
        payload = {
            **PERSONA_PAYLOAD,
            "nombres": "Francisco Manuel",
            "serial_number": "ABC-456",
        }
        respuesta = client.put(
            f"/users/{id_persona}", json=payload, headers=admin_headers
        )
        assert respuesta.status_code == 200
        assert respuesta.json()["mensaje"] == "Usuario actualizado correctamente"

        persona = client.get("/users/").json()[0]
        assert persona["nombres"] == "Francisco Manuel"

    def test_actualizar_no_existe(self, client, admin_headers):
        respuesta = client.put(
            "/users/9999", json=PERSONA_PAYLOAD, headers=admin_headers
        )
        assert respuesta.status_code == 404
        assert respuesta.json()["detail"] == "Usuario no encontrado"


class TestEstadoPersona:

    def test_cambiar_estado(self, client, admin_headers):
        id_persona = _crear_persona_en_bd()
        respuesta = client.patch(
            f"/users/{id_persona}/estado",
            json={"estado": "inactivo"},
            headers=admin_headers,
        )
        assert respuesta.status_code == 200
        assert respuesta.json()["mensaje"] == "Persona inactivo correctamente"

        persona = client.get("/users/").json()[0]
        assert persona["estado"] == "inactivo"

    def test_estado_invalido(self, client, admin_headers):
        id_persona = _crear_persona_en_bd()
        respuesta = client.patch(
            f"/users/{id_persona}/estado",
            json={"estado": "inexistente"},
            headers=admin_headers,
        )
        assert respuesta.status_code == 422

    def test_estado_persona_no_existe(self, client, admin_headers):
        respuesta = client.patch(
            "/users/9999/estado",
            json={"estado": "inactivo"},
            headers=admin_headers,
        )
        assert respuesta.status_code == 404


class TestEliminarPersona:

    def test_eliminar_ok(self, client, admin_headers):
        id_persona = _crear_persona_en_bd()
        respuesta = client.delete(f"/users/{id_persona}", headers=admin_headers)
        assert respuesta.status_code == 200
        assert client.get("/users/").json() == []

    def test_eliminar_no_existe(self, client, admin_headers):
        respuesta = client.delete("/users/9999", headers=admin_headers)
        assert respuesta.status_code == 404
        assert respuesta.json()["detail"] == "Usuario no encontrado"
