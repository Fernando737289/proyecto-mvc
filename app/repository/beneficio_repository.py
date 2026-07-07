from app.core.database import get_connection


def crear_beneficio(data):

    conexion = get_connection()
    cursor = conexion.cursor(dictionary=True)

    cursor.execute(
        """
        INSERT INTO beneficios(
            nombre,
            descripcion,
            tipo_descuento,
            valor_descuento,
            stock,
            fecha_inicio,
            fecha_vencimiento,
            comercio
        )
        VALUES(%s,%s,%s,%s,%s,%s,%s,%s)
        """,
        (
            data.nombre,
            data.descripcion,
            data.tipo_descuento,
            data.valor_descuento,
            data.stock,
            data.fecha_inicio,
            data.fecha_vencimiento,
            data.comercio
        )
    )

    conexion.commit()

    id_beneficio = cursor.lastrowid

    cursor.close()
    conexion.close()

    return id_beneficio


def obtener_beneficios():

    conexion = get_connection()
    cursor = conexion.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT *
        FROM beneficios
        WHERE estado = 'activo'
        """
    )

    beneficios = cursor.fetchall()

    cursor.close()
    conexion.close()

    return beneficios


def eliminar_beneficio(id_beneficio: int):

    conexion = get_connection()
    cursor = conexion.cursor()

    cursor.execute(
        """
            DELETE beneficios
            SET estado = 'inactivo'
            WHERE id = %s
        """,
        (id_beneficio,)
    )

    conexion.commit()

    filas_afectadas = cursor.rowcount

    cursor.close()
    conexion.close()

    return filas_afectadas


def actualizar_beneficio(
    id_beneficio: int,
    data
):

    conexion = get_connection()
    cursor = conexion.cursor()

    cursor.execute(
        """
        UPDATE beneficios
        SET
            nombre = %s,
            descripcion = %s
        WHERE id = %s
        """,
        (
            data.nombre,
            data.descripcion,
            id_beneficio
        )
    )

    conexion.commit()

    filas_afectadas = cursor.rowcount

    cursor.close()
    conexion.close()

    return filas_afectadas