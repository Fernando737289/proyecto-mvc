from app.core.database import get_connection


def obtener_conexion():

    conexion = get_connection()
    cursor = conexion.cursor(dictionary=True)

    return conexion, cursor


def obtener_persona(cursor, id_persona: int):

    cursor.execute(
        """
        SELECT id_persona
        FROM persona
        WHERE id_persona = %s
        """,
        (id_persona,)
    )

    return cursor.fetchone()


def obtener_beneficio(cursor, id_beneficio: int):

    cursor.execute(
        """
        SELECT *
        FROM beneficios
        WHERE id_beneficio = %s
        """,
        (id_beneficio,)
    )

    return cursor.fetchone()


def obtener_canje_existente(
    cursor,
    id_persona: int,
    id_beneficio: int
):

    cursor.execute(
        """
        SELECT id_historial
        FROM historial_beneficios
        WHERE id_persona = %s
        AND id_beneficio = %s
        """,
        (
            id_persona,
            id_beneficio
        )
    )

    return cursor.fetchone()


def descontar_stock(cursor, id_beneficio: int):

    cursor.execute(
        """
        UPDATE beneficios
        SET stock = stock - 1
        WHERE id_beneficio = %s
        """,
        (id_beneficio,)
    )


def registrar_canje(
    cursor,
    id_persona: int,
    id_beneficio: int,
    codigo_canje: str
):

    cursor.execute(
        """
        INSERT INTO historial_beneficios(
            id_persona,
            id_beneficio,
            codigo_canje
        )
        VALUES(%s,%s,%s)
        """,
        (
            id_persona,
            id_beneficio,
            codigo_canje
        )
    )