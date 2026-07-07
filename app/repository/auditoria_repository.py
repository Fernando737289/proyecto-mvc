from app.core.database import get_connection


def registrar_auditoria(
    tabla_afectada: str,
    accion_realizada: str,
    descripcion: str,
    usuario_accion: str
):

    conexion = get_connection()
    cursor = conexion.cursor()

    cursor.execute(
        """
        INSERT INTO auditoria(
            tabla_afectada,
            accion_realizada,
            descripcion,
            usuario_accion
        )
        VALUES(%s,%s,%s,%s)
        """,
        (
            tabla_afectada,
            accion_realizada,
            descripcion,
            usuario_accion
        )
    )

    conexion.commit()

    cursor.close()
    conexion.close()


def obtener_auditoria():

    conexion = get_connection()
    cursor = conexion.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            tabla_afectada,
            accion_realizada,
            descripcion,
            usuario_accion,
            fecha_accion
        FROM auditoria
        ORDER BY fecha_accion DESC
        """
    )

    resultado = cursor.fetchall()

    cursor.close()
    conexion.close()

    return resultado