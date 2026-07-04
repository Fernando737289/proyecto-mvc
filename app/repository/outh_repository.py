import bcrypt
from app.core.database import get_connection


def buscar_usuario_por_username_email(
    username: str,
    email: str
):

    conexion = get_connection()
    cursor = conexion.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT id_usuario
        FROM usuario
        WHERE username = %s
           OR email = %s
        """,
        (
            username,
            email
        )
    )

    usuario = cursor.fetchone()

    cursor.close()
    conexion.close()

    return usuario


def crear_usuario(
    username: str,
    email: str,
    password: str
):

    conexion = get_connection()
    cursor = conexion.cursor(dictionary=True)

    password_hash = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt(rounds=14)
    ).decode("utf-8")

    cursor.execute(
        """
        INSERT INTO usuario(
            username,
            email,
            password_hash
        )
        VALUES(%s,%s,%s)
        """,
        (
            username,
            email,
            password_hash
        )
    )

    conexion.commit()

    id_usuario = cursor.lastrowid

    cursor.close()
    conexion.close()

    return id_usuario