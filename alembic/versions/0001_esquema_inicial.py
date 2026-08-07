"""esquema inicial

Baseline del esquema de la Tarjeta Vecino. Es idempotente sobre la base
existente (la que crea backTarjetaVecino.sql): cada CREATE TABLE se omite
si la tabla ya existe. Sirve tambien para aprovisionar una base vacia.

Revision ID: 0001
Revises:
Create Date: 2026-08-06
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def _table_exists(name: str) -> bool:
    return sa.inspect(op.get_bind()).has_table(name)


def upgrade() -> None:
    if not _table_exists("auditoria"):
        op.create_table(
            "auditoria",
            sa.Column("id_auditoria", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("tabla_afectada", sa.String(length=100), nullable=True),
            sa.Column("accion_realizada", sa.String(length=50), nullable=True),
            sa.Column("descripcion", sa.Text(), nullable=True),
            sa.Column("usuario_accion", sa.String(length=100), nullable=True),
            sa.Column(
                "fecha_accion",
                sa.DateTime(),
                server_default=sa.text("CURRENT_TIMESTAMP"),
                nullable=True,
            ),
            sa.PrimaryKeyConstraint("id_auditoria"),
            mysql_charset="utf8mb4",
        )

    if not _table_exists("beneficios"):
        op.create_table(
            "beneficios",
            sa.Column("id_beneficio", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("nombre", sa.String(length=150), nullable=False),
            sa.Column("descripcion", sa.Text(), nullable=True),
            sa.Column(
                "tipo_descuento",
                sa.Enum("porcentaje", "monto_fijo", "2x1"),
                nullable=True,
            ),
            sa.Column("valor_descuento", sa.DECIMAL(10, 2), nullable=True),
            sa.Column(
                "stock",
                sa.Integer(),
                server_default=sa.text("'0'"),
                nullable=False,
            ),
            sa.Column("fecha_inicio", sa.Date(), nullable=True),
            sa.Column("fecha_vencimiento", sa.Date(), nullable=True),
            sa.Column("comercio", sa.String(length=150), nullable=True),
            sa.Column(
                "estado",
                sa.Enum("activo", "inactivo"),
                server_default=sa.text("'activo'"),
                nullable=False,
            ),
            sa.PrimaryKeyConstraint("id_beneficio"),
            mysql_charset="utf8mb4",
        )

    if not _table_exists("persona"):
        op.create_table(
            "persona",
            sa.Column("id_persona", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("rut", sa.String(length=12), nullable=False),
            sa.Column("serial_number", sa.String(length=500), nullable=False),
            sa.Column("nombres", sa.String(length=100), nullable=False),
            sa.Column("apellidos", sa.String(length=100), nullable=False),
            sa.Column("direccion", sa.String(length=200), nullable=True),
            sa.Column("numero_direccion", sa.String(length=10), nullable=True),
            sa.Column("telefono", sa.String(length=20), nullable=True),
            sa.Column("email", sa.String(length=100), nullable=True),
            sa.Column("fecha_nacimiento", sa.Date(), nullable=True),
            sa.Column(
                "estado",
                sa.Enum("activo", "inactivo"),
                server_default=sa.text("'activo'"),
                nullable=False,
            ),
            sa.Column(
                "fecha_creacion",
                sa.DateTime(),
                server_default=sa.text("CURRENT_TIMESTAMP"),
                nullable=True,
            ),
            sa.PrimaryKeyConstraint("id_persona"),
            sa.UniqueConstraint("rut", name="uk_persona_rut"),
            mysql_charset="utf8mb4",
        )

    if not _table_exists("tarjeta"):
        op.create_table(
            "tarjeta",
            sa.Column("id_tarjeta", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("id_persona", sa.Integer(), nullable=False),
            sa.Column("numero_tarjeta", sa.String(length=50), nullable=False),
            sa.Column("codigo_qr", mysql.LONGTEXT(), nullable=False),
            sa.Column("fecha_emision", sa.Date(), nullable=False),
            sa.Column("fecha_vencimiento", sa.Date(), nullable=False),
            sa.Column(
                "estado",
                sa.Enum("activa", "bloqueada", "vencida"),
                server_default=sa.text("'activa'"),
                nullable=False,
            ),
            sa.ForeignKeyConstraint(
                ["id_persona"],
                ["persona.id_persona"],
                name="fk_tarjeta_persona",
                ondelete="RESTRICT",
                onupdate="CASCADE",
            ),
            sa.PrimaryKeyConstraint("id_tarjeta"),
            sa.UniqueConstraint("id_persona", name="uk_tarjeta_persona"),
            sa.UniqueConstraint("numero_tarjeta", name="uk_tarjeta_numero"),
            mysql_charset="utf8mb4",
        )

    if not _table_exists("historial_beneficios"):
        op.create_table(
            "historial_beneficios",
            sa.Column("id_historial", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("id_persona", sa.Integer(), nullable=False),
            sa.Column("id_beneficio", sa.Integer(), nullable=False),
            sa.Column("codigo_canje", sa.String(length=50), nullable=False),
            sa.Column(
                "fecha_uso",
                sa.DateTime(),
                server_default=sa.text("CURRENT_TIMESTAMP"),
                nullable=True,
            ),
            sa.ForeignKeyConstraint(
                ["id_beneficio"],
                ["beneficios.id_beneficio"],
                name="fk_historial_beneficio",
            ),
            sa.ForeignKeyConstraint(
                ["id_persona"],
                ["persona.id_persona"],
                name="fk_historial_persona",
            ),
            sa.PrimaryKeyConstraint("id_historial"),
            mysql_charset="utf8mb4",
        )

    if not _table_exists("usuario"):
        op.create_table(
            "usuario",
            sa.Column("id_usuario", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("username", sa.String(length=50), nullable=False),
            sa.Column("password_hash", sa.String(length=255), nullable=False),
            sa.Column(
                "rol",
                sa.Enum("admin", "funcionario"),
                server_default=sa.text("'funcionario'"),
                nullable=False,
            ),
            sa.Column(
                "estado",
                sa.Enum("activo", "inactivo"),
                server_default=sa.text("'activo'"),
                nullable=False,
            ),
            sa.Column(
                "fecha_creacion",
                sa.DateTime(),
                server_default=sa.text("CURRENT_TIMESTAMP"),
                nullable=True,
            ),
            sa.Column("email", sa.String(length=255), nullable=False),
            sa.PrimaryKeyConstraint("id_usuario"),
            sa.UniqueConstraint("username", name="uk_usuario_username"),
            sa.UniqueConstraint("email", name="uk_usuario_email"),
            mysql_charset="utf8mb4",
        )


def downgrade() -> None:
    op.drop_table("historial_beneficios")
    op.drop_table("usuario")
    op.drop_table("tarjeta")
    op.drop_table("persona")
    op.drop_table("beneficios")
    op.drop_table("auditoria")
