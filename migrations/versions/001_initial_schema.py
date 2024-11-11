"""initial schema

Revision ID: 001_initial_schema
Revises:
Create Date: 2024-11-08 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Crear tabla users
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("hashed_password", sa.String(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, default=True),
        sa.Column("is_superuser", sa.Boolean(), nullable=False, default=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("username"),
        sa.UniqueConstraint("email"),
    )

    # Crear tabla interactions
    op.create_table(
        "interactions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.Column("student_name", sa.String(), nullable=False),
        sa.Column("tutor_phone", sa.String(), nullable=False),
        sa.Column("tutor_name", sa.String(), nullable=True),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("claude_response", postgresql.JSONB(), nullable=True),
        sa.Column("sensitivity_score", sa.Integer(), nullable=True),
        sa.Column("follow_up_required", sa.Boolean(), nullable=False, default=False),
        sa.Column("follow_up_date", sa.DateTime(), nullable=True),
        sa.Column("created_by_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["created_by_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Crear tabla interaction_messages
    op.create_table(
        "interaction_messages",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("interaction_id", sa.Integer(), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.Column("sender_type", sa.String(), nullable=False),
        sa.Column("content", sa.String(), nullable=False),
        sa.Column("metadata", postgresql.JSONB(), nullable=True),
        sa.ForeignKeyConstraint(
            ["interaction_id"],
            ["interactions.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Crear índices
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=True)
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(
        op.f("ix_interactions_student_name"),
        "interactions",
        ["student_name"],
        unique=False,
    )
    op.create_index(
        op.f("ix_interactions_timestamp"), "interactions", ["timestamp"], unique=False
    )


def downgrade() -> None:
    # Eliminar índices
    op.drop_index(op.f("ix_interactions_timestamp"), table_name="interactions")
    op.drop_index(op.f("ix_interactions_student_name"), table_name="interactions")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_index(op.f("ix_users_username"), table_name="users")

    # Eliminar tablas
    op.drop_table("interaction_messages")
    op.drop_table("interactions")
    op.drop_table("users")
