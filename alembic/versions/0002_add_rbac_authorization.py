"""Add database-backed RBAC.

Revision ID: 0002_add_rbac
Revises: 0001_create_users
Create Date: 2026-09-18
"""

from alembic import op
import sqlalchemy as sa


revision = "0002_add_rbac"
down_revision = "0001_create_users"
branch_labels = None
depends_on = None


ADMIN_ROLE_ID = "e1649b05-857f-4a75-9a17-64a4e4f6b1f1"
MEMBER_ROLE_ID = "69040c83-548a-4d14-9fb8-d0ec562ff049"

PERMISSIONS = (
    ("434a3b7d-6bdd-4d70-bd9e-2e85d2f541ce", "task", "read_assigned"),
    ("0f9bfe95-bdc9-4822-bc0d-5c271d3d91f1", "task", "create"),
    ("4db65b76-39a2-485d-ab95-8976dc6f7cf8", "task", "update_assigned"),
    ("f2b69e87-3ee2-416e-bc9d-5545d218e7cf", "task", "delete"),
    ("2690da70-94e9-46b2-a7ce-95e05d6a7dc8", "project", "read_all"),
    ("abfcfe7b-992e-4ef3-8967-1d5033348008", "user", "manage"),
)


def upgrade() -> None:
    op.create_table(
        "roles",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index("ix_roles_name", "roles", ["name"], unique=False)

    op.create_table(
        "permissions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("resource", sa.String(length=50), nullable=False),
        sa.Column("action", sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("resource", "action", name="uq_permissions_resource_action"),
    )
    op.create_table(
        "role_permissions",
        sa.Column("role_id", sa.String(length=36), nullable=False),
        sa.Column("permission_id", sa.String(length=36), nullable=False),
        sa.ForeignKeyConstraint(["permission_id"], ["permissions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("role_id", "permission_id"),
    )

    roles = sa.table("roles", sa.column("id", sa.String), sa.column("name", sa.String))
    permissions = sa.table(
        "permissions",
        sa.column("id", sa.String),
        sa.column("resource", sa.String),
        sa.column("action", sa.String),
    )
    role_permissions = sa.table(
        "role_permissions",
        sa.column("role_id", sa.String),
        sa.column("permission_id", sa.String),
    )
    op.bulk_insert(
        roles,
        [
            {"id": ADMIN_ROLE_ID, "name": "ADMIN"},
            {"id": MEMBER_ROLE_ID, "name": "MEMBER"},
        ],
    )
    op.bulk_insert(
        permissions,
        [
            {"id": permission_id, "resource": resource, "action": action}
            for permission_id, resource, action in PERMISSIONS
        ],
    )
    member_permission_names = {
        ("task", "read_assigned"),
        ("task", "create"),
        ("task", "update_assigned"),
    }
    op.bulk_insert(
        role_permissions,
        [
            {"role_id": role_id, "permission_id": permission_id}
            for role_id in (ADMIN_ROLE_ID, MEMBER_ROLE_ID)
            for permission_id, resource, action in PERMISSIONS
            if role_id == ADMIN_ROLE_ID or (resource, action) in member_permission_names
        ],
    )

    op.add_column("users", sa.Column("role_id", sa.String(length=36), nullable=True))
    op.execute(
        "UPDATE users SET role_id = CASE "
        f"WHEN UPPER(role) = 'ADMIN' THEN '{ADMIN_ROLE_ID}' "
        f"ELSE '{MEMBER_ROLE_ID}' END"
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
    op.drop_column("users", "role")


def downgrade() -> None:
    op.add_column(
        "users",
        sa.Column("role", sa.String(length=50), nullable=False, server_default="MEMBER"),
    )
    op.execute(
        "UPDATE users SET role = CASE "
        f"WHEN role_id = '{ADMIN_ROLE_ID}' THEN 'ADMIN' ELSE 'MEMBER' END"
    )
    op.drop_index("ix_users_role_id", table_name="users")
    op.drop_constraint("fk_users_role_id_roles", "users", type_="foreignkey")
    op.drop_column("users", "role_id")

    op.drop_table("role_permissions")
    op.drop_table("permissions")
    op.drop_index("ix_roles_name", table_name="roles")
    op.drop_table("roles")
