"""add service status table

Revision ID: 002_add_service_status
Revises: 001_initial_schema
Create Date: 2024-11-08 10:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "002_add_service_status"
down_revision = "001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Crear tabla service_status
    op.create_table(
        "service_status",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("service_name", sa.String(), nullable=False),
        sa.Column("status", sa.Boolean(), nullable=False),
        sa.Column("last_check", sa.DateTime(), nullable=False),
        sa.Column("error_message", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    # Crear índice único en service_name
    op.create_index(
        op.f("ix_service_status_service_name"),
        "service_status",
        ["service_name"],
        unique=True,
    )

    # Insertar servicios iniciales
    op.execute(
        """
        INSERT INTO service_status (service_name, status, last_check)
        VALUES 
        ('claude', true, CURRENT_TIMESTAMP),
        ('meta', true, CURRENT_TIMESTAMP)
    """
    )


def downgrade() -> None:
    # Eliminar índice
    op.drop_index(op.f("ix_service_status_service_name"), table_name="service_status")

    # Eliminar tabla
    op.drop_table("service_status")
