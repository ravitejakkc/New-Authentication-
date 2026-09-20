"""Add user-role mapping table.

Revision ID: 0004_add_role_users
Revises: 0003_add_tasks_projects
Create Date: 2026-09-20
"""

from alembic import op
import sqlalchemy as sa


revision = "0004_add_role_users"
down_revision = "0003_add_tasks_projects"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "role_users",
        sa.Column("role_id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("role_id", "user_id"),
    )

    op.execute(
        "INSERT INTO role_users (role_id, user_id) "
        "SELECT role_id, id FROM users WHERE role_id IS NOT NULL"
    )

    op.drop_index("ix_users_role_id", table_name="users")
    op.drop_constraint("fk_users_role_id_roles", "users", type_="foreignkey")
    op.drop_column("users", "role_id")


def downgrade() -> None:
    op.add_column("users", sa.Column("role_id", sa.String(length=36), nullable=True))
    op.execute(
        "UPDATE users "
        "SET role_id = ("
        "    SELECT role_users.role_id "
        "    FROM role_users "
        "    WHERE role_users.user_id = users.id "
        "    ORDER BY role_users.role_id "
        "    LIMIT 1"
        ")"
    )
    op.alter_column("users", "role_id", nullable=False)
    op.create_foreign_key(
        "fk_users_role_id_roles",
        "users",
        "roles",
        ["role_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_index("ix_users_role_id", "users", ["role_id"], unique=False)
    op.drop_table("role_users")
