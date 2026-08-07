from tests.conftest import _crear_persona_en_bd, _crear_tarjeta_en_bd


def _auditoria(client, admin_headers):
    respuesta = client.get("/auditoria/", headers=admin_headers)
    assert respuesta.status_code == 200
    return respuesta.json()


def _un_solo_registro(client, admin_headers):
    registros = _auditoria(client, admin_headers)
    assert len(registros) == 1
    return registros[0]


class TestAuditoriaPersonas:

    def test_registro_persona(self, client, admin_headers, dec_valida):
        respuesta = client.post(
            "/users/usuarios",
            json={
                "rut": "14187947-2",
                "serial_number": "SN123456",
                "nombres": "Francisco",
                "apellidos": "Baez",
                "telefono": "912345678",
                "email": "francisco@example.cl",
            },
            headers=admin_headers,
        )
        assert respuesta.status_code == 200

        registro = _un_solo_registro(client, admin_headers)
        assert registro["tabla_afectada"] == "persona"
        assert registro["accion_realizada"] == "INSERT"
        assert registro["usuario_accion"] == "admin_test"

    def test_actualizar_persona(self, client, admin_headers):
        id_persona = _crear_persona_en_bd()
        respuesta = client.put(
            f"/users/{id_persona}",
            json={
                "rut": "14187947-2",
                "serial_number": "SN123456",
                "nombres": "Francisco",
                "apellidos": "Baez",
                "telefono": "912345678",
                "email": "francisco@example.cl",
            },
            headers=admin_headers,
        )
        assert respuesta.status_code == 200

        registro = _un_solo_registro(client, admin_headers)
        assert registro["tabla_afectada"] == "persona"
        assert registro["accion_realizada"] == "UPDATE"
        assert registro["usuario_accion"] == "admin_test"

    def test_eliminar_persona(self, client, admin_headers):
        id_persona = _crear_persona_en_bd()
        respuesta = client.delete(f"/users/{id_persona}", headers=admin_headers)
        assert respuesta.status_code == 200

        registro = _un_solo_registro(client, admin_headers)
        assert registro["tabla_afectada"] == "persona"
        assert registro["accion_realizada"] == "DELETE"

    def test_cambiar_estado_persona(self, client, admin_headers):
        id_persona = _crear_persona_en_bd()
        respuesta = client.patch(
            f"/users/{id_persona}/estado",
            json={"estado": "inactivo"},
            headers=admin_headers,
        )
        assert respuesta.status_code == 200

        registro = _un_solo_registro(client, admin_headers)
        assert registro["tabla_afectada"] == "persona"
        assert registro["accion_realizada"] == "UPDATE"


class TestAuditoriaTarjetas:

    def test_registro_tarjeta(self, client, admin_headers):
        _crear_persona_en_bd()
        respuesta = client.post(
            "/tarjeta/crear",
            json={
                "rut": "14187947-2",
                "nombres": "Francisco",
                "apellidos": "Baez",
            },
            headers=admin_headers,
        )
        assert respuesta.status_code == 200

        registro = _un_solo_registro(client, admin_headers)
        assert registro["tabla_afectada"] == "tarjeta"
        assert registro["accion_realizada"] == "INSERT"

    def test_regenerar_qr(self, client, admin_headers):
        id_persona = _crear_persona_en_bd()
        _crear_tarjeta_en_bd(id_persona)
        respuesta = client.post(
            "/qr/generar", json={"rut": "14187947-2"}, headers=admin_headers
        )
        assert respuesta.status_code == 200

        registro = _un_solo_registro(client, admin_headers)
        assert registro["tabla_afectada"] == "tarjeta"
        assert registro["accion_realizada"] == "UPDATE"


class TestAuditoriaBeneficios:

    def test_ciclo_completo(self, client, admin_headers):
        payload = {
            "nombre": "Farmacia Municipal",
            "tipo_descuento": "monto_fijo",
            "valor_descuento": 500,
            "stock": 10,
            "fecha_inicio": "2026-01-01",
            "fecha_vencimiento": "2026-12-31",
            "comercio": "Farmacia",
        }

        crear = client.post("/beneficios/crear", json=payload, headers=admin_headers)
        assert crear.status_code == 200
        id_beneficio = crear.json()["id_beneficio"]

        actualizar = client.put(
            f"/beneficios/actualizar/{id_beneficio}",
            json=payload,
            headers=admin_headers,
        )
        assert actualizar.status_code == 200

        eliminar = client.delete(
            f"/beneficios/eliminar/{id_beneficio}", headers=admin_headers
        )
        assert eliminar.status_code == 200

        registros = _auditoria(client, admin_headers)
        assert [r["accion_realizada"] for r in registros] == [
            "INSERT",
            "UPDATE",
            "DELETE",
        ]
        assert all(r["tabla_afectada"] == "beneficio" for r in registros)


class TestAuditoriaUsuarios:

    def test_registro_usuario_sistema(self, client, admin_headers):
        respuesta = client.post(
            "/auth/registro",
            json={
                "username": "nuevo_operador",
                "email": "nuevo_operador@example.cl",
                "password": "ClaveSegura123",
            },
            headers=admin_headers,
        )
        assert respuesta.status_code == 200

        registro = _un_solo_registro(client, admin_headers)
        assert registro["tabla_afectada"] == "usuario"
        assert registro["accion_realizada"] == "INSERT"
        assert registro["usuario_accion"] == "admin_test"
