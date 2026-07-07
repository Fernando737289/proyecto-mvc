from app.core.database import get_connection


def obtener_historial_persona(id_persona: int):

    conexion = get_connection()
    cursor = conexion.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            h.id_historial,
            h.codigo_canje,
            h.fecha_uso,

            b.id_beneficio,
            b.nombre,
            b.descripcion,
            b.comercio,
            b.tipo_descuento,
            b.valor_descuento

        FROM historial_beneficios h

        INNER JOIN beneficios b
            ON h.id_beneficio = b.id_beneficio

        WHERE h.id_persona = %s

        ORDER BY h.fecha_uso DESC
        """,
        (id_persona,)
    )

    historial = cursor.fetchall()

    cursor.close()
    conexion.close()

    return historial