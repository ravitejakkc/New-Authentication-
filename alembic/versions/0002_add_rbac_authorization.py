"""Add database-backed RBAC.

Revision ID: 0002_add_rbac
Revises: 0001_create_users
Create Date: 2026-09-18
"""

from alembic import op
import sqlalchemy as sa
import uuid


revision = "0002_add_rbac"
down_revision = "0001_create_users"
branch_labels = None
depends_on = None


PERMISSIONS = (
    ("task", "read_assigned"),
    ("task", "create"),
    ("task", "update_assigned"),
    ("task", "delete"),
    ("project", "read_all"),
    ("user", "manage"),
)


def upgrade() -> None:
    role_ids = {
        "ADMIN": str(uuid.uuid4()),
        "MEMBER": str(uuid.uuid4()),
    }
    permission_ids = {
        (resource, action): str(uuid.uuid4())
        for resource, action in PERMISSIONS
    }

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
            {"id": role_ids["ADMIN"], "name": "ADMIN"},
            {"id": role_ids["MEMBER"], "name": "MEMBER"},
        ],
    )
    op.bulk_insert(
        permissions,
        [
            {
                "id": permission_ids[(resource, action)],
                "resource": resource,
                "action": action,
            }
            for resource, action in PERMISSIONS
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
            {
                "role_id": role_id,
                "permission_id": permission_ids[(resource, action)],
            }
            for role_name, role_id in role_ids.items()
            for resource, action in PERMISSIONS
            if role_name == "ADMIN" or (resource, action) in member_permission_names
        ],
    )

    op.add_column("users", sa.Column("role_id", sa.String(length=36), nullable=True))
    op.execute(
        "UPDATE users SET role_id = CASE "
        f"WHEN UPPER(role) = 'ADMIN' THEN '{role_ids['ADMIN']}' "
        f"ELSE '{role_ids['MEMBER']}' END"
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
        "UPDATE users "
        "SET role = COALESCE((SELECT name FROM roles WHERE roles.id = users.role_id), 'MEMBER')"
    )
    op.drop_index("ix_users_role_id", table_name="users")
    op.drop_constraint("fk_users_role_id_roles", "users", type_="foreignkey")
    op.drop_column("users", "role_id")

    op.drop_table("role_permissions")
    op.drop_table("permissions")
    op.drop_index("ix_roles_name", table_name="roles")
    op.drop_table("roles")
