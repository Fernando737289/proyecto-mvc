from tests.conftest import ADMIN_PASSWORD, FUNCIONARIO_PASSWORD, _crear_usuario_en_bd


class TestLogin:

    def test_login_ok(self, client):
        _crear_usuario_en_bd(
            "vecino", "vecino@example.cl", "funcionario", FUNCIONARIO_PASSWORD
        )
        respuesta = client.post(
            "/auth/login",
            json={"email": "vecino@example.cl", "password": FUNCIONARIO_PASSWORD},
        )
        assert respuesta.status_code == 200
        assert respuesta.json()["token_type"] == "bearer"
        assert respuesta.json()["access_token"]

    def test_login_credenciales_invalidas(self, client):
        _crear_usuario_en_bd(
            "vecino", "vecino@example.cl", "funcionario", FUNCIONARIO_PASSWORD
        )
        respuesta = client.post(
            "/auth/login",
            json={"email": "vecino@example.cl", "password": "incorrecta"},
        )
        assert respuesta.status_code == 401
        assert respuesta.json()["detail"] == "Credenciales inválidas"

    def test_login_usuario_inexistente(self, client):
        respuesta = client.post(
            "/auth/login",
            json={"email": "nadie@example.cl", "password": "cualquiera"},
        )
        assert respuesta.status_code == 401

    def test_login_usuario_inactivo(self, client):
        _crear_usuario_en_bd(
            "inactivo", "inactivo@example.cl", "funcionario", FUNCIONARIO_PASSWORD
        )
        from app.core.database import SessionLocal
        from app.models.orm import Usuario

        with SessionLocal() as db:
            usuario = (
                db.query(Usuario).filter(Usuario.email == "inactivo@example.cl").first()
            )
            usuario.estado = "inactivo"
            db.commit()

        respuesta = client.post(
            "/auth/login",
            json={"email": "inactivo@example.cl", "password": FUNCIONARIO_PASSWORD},
        )
        assert respuesta.status_code == 401
        assert respuesta.json()["detail"] == "Usuario inactivo"

    def test_login_email_invalido(self, client):
        respuesta = client.post(
            "/auth/login",
            json={"email": "no-es-email", "password": "x"},
        )
        assert respuesta.status_code == 422


class TestRegistro:

    def test_registro_ok(self, client, admin_headers):
        respuesta = client.post(
            "/auth/registro",
            json={
                "username": "nuevo_admin",
                "email": "nuevo@example.cl",
                "password": "ClaveSegura1",
            },
            headers=admin_headers,
        )
        assert respuesta.status_code == 200
        assert respuesta.json()["mensaje"] == "Usuario creado correctamente"

    def test_registro_sin_token(self, client):
        respuesta = client.post(
            "/auth/registro",
            json={
                "username": "nuevo",
                "email": "nuevo@example.cl",
                "password": "ClaveSegura1",
            },
        )
        assert respuesta.status_code == 401

    def test_registro_rol_insuficiente(self, client, funcionario_headers):
        respuesta = client.post(
            "/auth/registro",
            json={
                "username": "nuevo",
                "email": "nuevo@example.cl",
                "password": "ClaveSegura1",
            },
            headers=funcionario_headers,
        )
        assert respuesta.status_code == 403

    def test_registro_usuario_duplicado(self, client, admin_headers):
        _crear_usuario_en_bd(
            "duplicado", "duplicado@example.cl", "funcionario", FUNCIONARIO_PASSWORD
        )
        respuesta = client.post(
            "/auth/registro",
            json={
                "username": "duplicado",
                "email": "otro@example.cl",
                "password": "ClaveSegura1",
            },
            headers=admin_headers,
        )
        assert respuesta.status_code == 400
        assert respuesta.json()["detail"] == "Usuario o correo ya registrado"

    def test_registro_password_corta(self, client, admin_headers):
        respuesta = client.post(
            "/auth/registro",
            json={
                "username": "corta",
                "email": "corta@example.cl",
                "password": "corta",
            },
            headers=admin_headers,
        )
        assert respuesta.status_code == 422


class TestTokenInvalido:

    def test_endpoint_protegido_con_token_invalido(self, client):
        respuesta = client.get(
            "/auditoria/",
            headers={"Authorization": "Bearer token.invalido.xyz"},
        )
        assert respuesta.status_code == 401
        assert respuesta.json()["detail"] == "Token inválido o expirado"
