from sqlalchemy import text

from app.core.database import engine

#prueba de conexion a base de datos.
def database_connection():

    try:

        with engine.connect() as conexion:

            resultado = conexion.execute(text("SELECT DATABASE();")).fetchone()

        return {
            "conexion": "exitosa",
            "baseDeDatos": resultado[0]
        }

    except Exception as error:

        return {
            "error": str(error)
        }
