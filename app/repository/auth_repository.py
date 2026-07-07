from app.core.database import get_connection


def obtener_usuario_por_email(email: str):

    conexion = get_connection()
    cursor = conexion.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            id_usuario,
            username,
            password_hash,
            rol,
            estado,
            email
        FROM usuario
        WHERE email = %s
        """,
        (email,)
    )
    
    usuario = cursor.fetchone()

    cursor.close()
    conexion.close()


    return usuario