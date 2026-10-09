"""add organizations and scope users/aws_accounts

Revision ID: ee29caab13cb
Revises: 09b6f52e288d
Create Date: 2026-10-09 00:33:04.454935

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ee29caab13cb'
down_revision: Union[str, None] = '09b6f52e288d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'organizations',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )

    # Added nullable first: a database created before multi-tenancy may
    # already have a user and a connected AWS account, and they need an
    # organization backfilled before the NOT NULL constraint below applies.
    op.add_column('aws_accounts', sa.Column('organization_id', sa.String(), nullable=True))
    op.add_column('users', sa.Column('organization_id', sa.String(), nullable=True))

    # Every user predating this migration was the single MVP admin. Give
    # each one its own organization (named after its email) and move its
    # connected AWS account, if any, into that same organization.
    connection = op.get_bind()
    users = connection.execute(sa.text("SELECT id, email FROM users")).fetchall()
    for user_id, email in users:
        org_id = connection.execute(
            sa.text(
                "INSERT INTO organizations (id, name, created_at) "
                "VALUES (gen_random_uuid()::text, :name, now()) RETURNING id"
            ),
            {"name": email},
        ).scalar_one()
        connection.execute(
            sa.text("UPDATE users SET organization_id = :org_id WHERE id = :user_id"),
            {"org_id": org_id, "user_id": user_id},
        )
        connection.execute(
            sa.text("UPDATE aws_accounts SET organization_id = :org_id WHERE organization_id IS NULL"),
            {"org_id": org_id},
        )

    op.alter_column('users', 'organization_id', nullable=False)
    op.alter_column('aws_accounts', 'organization_id', nullable=False)

    op.create_index(op.f('ix_users_organization_id'), 'users', ['organization_id'], unique=False)
    op.create_index(op.f('ix_aws_accounts_organization_id'), 'aws_accounts', ['organization_id'], unique=False)
    op.create_foreign_key(
        'fk_users_organization_id', 'users', 'organizations', ['organization_id'], ['id']
    )
    op.create_foreign_key(
        'fk_aws_accounts_organization_id', 'aws_accounts', 'organizations', ['organization_id'], ['id']
    )


def downgrade() -> None:
    op.drop_constraint('fk_aws_accounts_organization_id', 'aws_accounts', type_='foreignkey')
    op.drop_index(op.f('ix_aws_accounts_organization_id'), table_name='aws_accounts')
    op.drop_column('aws_accounts', 'organization_id')

    op.drop_constraint('fk_users_organization_id', 'users', type_='foreignkey')
    op.drop_index(op.f('ix_users_organization_id'), table_name='users')
    op.drop_column('users', 'organization_id')

    op.drop_table('organizations')
