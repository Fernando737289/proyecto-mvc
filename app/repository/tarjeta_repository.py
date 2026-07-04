from app.core.database import get_connection


def verificar_tarjeta_existente(id_persona: int):

    conexion = get_connection()
    cursor = conexion.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT id_tarjeta
        FROM tarjeta
        WHERE id_persona = %s
        """,
        (id_persona,)
    )

    tarjeta = cursor.fetchone()

    cursor.close()
    conexion.close()

    return tarjeta


def crear_tarjeta(
    id_persona: int,
    numero_tarjeta: str,
    codigo_qr: str,
    fecha_emision,
    fecha_vencimiento,
    estado: str
):

    conexion = get_connection()
    cursor = conexion.cursor(dictionary=True)

    cursor.execute(
        """
        INSERT INTO tarjeta(
            id_persona,
            numero_tarjeta,
            codigo_qr,
            fecha_emision,
            fecha_vencimiento,
            estado
        )
        VALUES(%s,%s,%s,%s,%s,%s)
        """,
        (
            id_persona,
            numero_tarjeta,
            codigo_qr,
            fecha_emision,
            fecha_vencimiento,
            estado
        )
    )

    conexion.commit()

    id_tarjeta = cursor.lastrowid

    cursor.close()
    conexion.close()

    return id_tarjeta

def get_tarjeta(rut=None, numero_tarjeta=None):

    conexion = get_connection()
    cursor = conexion.cursor(dictionary=True)

    query = """
        SELECT
            t.id_tarjeta,
            t.numero_tarjeta,
            t.codigo_qr,
            t.fecha_emision,
            t.fecha_vencimiento,
            t.estado,
            t.id_persona,
            p.rut,
            p.nombres,
            p.apellidos,
            p.telefono
        FROM tarjeta t
        INNER JOIN persona p
            ON t.id_persona = p.id_persona
        WHERE 1 = 1
    """

    params = []

    if rut:
        query += " AND p.rut = %s"
        params.append(rut)

    if numero_tarjeta:
        query += " AND t.numero_tarjeta = %s"
        params.append(numero_tarjeta)

    cursor.execute(query, tuple(params))

    tarjeta = cursor.fetchone()

    cursor.close()
    conexion.close()

    return tarjeta


def get_tarjeta_by_id(id_tarjeta):

    conexion = get_connection()
    cursor = conexion.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT id_tarjeta
        FROM tarjeta
        WHERE id_tarjeta = %s
        """,
        (id_tarjeta,)
    )

    tarjeta = cursor.fetchone()

    cursor.close()
    conexion.close()

    return tarjeta


def update_tarjeta(
    id_tarjeta,
    estado,
    fecha_vencimiento
):

    conexion = get_connection()
    cursor = conexion.cursor()

    cursor.execute(
        """
        UPDATE tarjeta
        SET
            estado = %s,
            fecha_vencimiento = %s
        WHERE id_tarjeta = %s
        """,
        (
            estado,
            fecha_vencimiento,
            id_tarjeta
        )
    )

    conexion.commit()

    cursor.close()
    conexion.close()
    
def obtener_tarjeta_por_id(id_tarjeta: int):

    conexion = get_connection()
    cursor = conexion.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT id_tarjeta
        FROM tarjeta
        WHERE id_tarjeta = %s
        """,
        (id_tarjeta,)
    )

    tarjeta = cursor.fetchone()

    cursor.close()
    conexion.close()

    return tarjeta

def eliminar_tarjeta(id_tarjeta: int):

    conexion = get_connection()
    cursor = conexion.cursor()

    cursor.execute(
        """
        DELETE FROM tarjeta
        WHERE id_tarjeta = %s
        """,
        (id_tarjeta,)
    )

    conexion.commit()

    filas_afectadas = cursor.rowcount

    cursor.close()
    conexion.close()

    return filas_afectadas
