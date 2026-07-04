from app.core.database import get_connection


def existe_usuario_por_rut(rut: str):

    conexion = get_connection()
    cursor = conexion.cursor(dictionary=True)

    try:

        cursor.execute(
            """
            SELECT id_persona
            FROM persona
            WHERE rut = %s
            """,
            (rut,)
        )

        return cursor.fetchone()

    finally:

        cursor.close()
        conexion.close()


def insertar_usuario(values):

    conexion = get_connection()
    cursor = conexion.cursor()

    try:

        query = """
            INSERT INTO persona (
                rut,
                serial_number,
                nombres,
                apellidos,
                direccion,
                numero_direccion,
                telefono,
                email,
                fecha_nacimiento
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """

        cursor.execute(query, values)

        conexion.commit()

    finally:

        cursor.close()
        conexion.close()


def obtener_personas():

    conexion = get_connection()
    cursor = conexion.cursor(dictionary=True)

    try:

        cursor.execute(
            """
            SELECT
                id_persona,
                rut,
                nombres,
                apellidos,
                direccion,
                numero_direccion,
                telefono,
                email,
                fecha_nacimiento,
                estado,
                fecha_creacion
            FROM persona
            """
        )

        return cursor.fetchall()

    finally:

        cursor.close()
        conexion.close()
        
def update_user_repository(id_persona, user):

    conexion = get_connection()
    cursor = conexion.cursor(dictionary=True)

    query = """
        UPDATE persona
        SET
            rut = %s,
            nombres = %s,
            apellidos = %s,
            direccion = %s,
            numero_direccion = %s,
            telefono = %s,
            email = %s,
            fecha_nacimiento = %s
        WHERE id_persona = %s
    """

    values = (
        user.rut,
        user.nombres,
        user.apellidos,
        user.direccion,
        user.numero_direccion,
        user.telefono,
        user.email,
        user.fecha_nacimiento,
        id_persona
    )

    cursor.execute(query, values)
    conexion.commit()

    filas = cursor.rowcount

    cursor.close()
    conexion.close()

    return filas


def delete_user_repository(id_persona):

    conexion = get_connection()
    cursor = conexion.cursor()

    cursor.execute(
        """
        DELETE FROM persona
        WHERE id_persona = %s
        """,
        (id_persona,)
    )

    conexion.commit()

    filas = cursor.rowcount

    cursor.close()
    conexion.close()

    return filas


def update_estado_persona_repository(
    id_persona,
    estado
):

    conexion = get_connection()
    cursor = conexion.cursor()

    cursor.execute(
        """
        UPDATE persona
        SET estado = %s
        WHERE id_persona = %s
        """,
        (
            estado,
            id_persona
        )
    )

    conexion.commit()

    filas = cursor.rowcount

    cursor.close()
    conexion.close()

    return filas