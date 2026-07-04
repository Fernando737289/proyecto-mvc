from app.core.database import get_connection


def get_persona_by_rut(rut: str):

    conexion = get_connection()
    cursor = conexion.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            id_persona,
            rut,
            nombres,
            apellidos,
            telefono
        FROM persona
        WHERE rut = %s
        """,
        (rut,)
    )

    persona = cursor.fetchone()

    cursor.close()
    conexion.close()

    return persona