"""empty message

Revision ID: 92639a1e1ecc
Revises: 72c65cf123a0
Create Date: 2024-05-02 17:10:18.774059

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '92639a1e1ecc'
down_revision: Union[str, None] = '72c65cf123a0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_user_group_link_group_id', table_name='user_group_link')
    op.drop_index('ix_user_group_link_group_uuid', table_name='user_group_link')
    op.drop_index('ix_user_group_link_id', table_name='user_group_link')
    op.drop_index('ix_user_group_link_user_id', table_name='user_group_link')
    op.drop_index('ix_user_group_link_user_role', table_name='user_group_link')
    op.drop_index('ix_user_group_link_user_uuid', table_name='user_group_link')
    op.drop_index('ix_user_group_link_uuid', table_name='user_group_link')
    op.drop_table('user_group_link')
    op.drop_index('ix_transaction_group_link_created_by_user_id', table_name='transaction_group_link')
    op.drop_index('ix_transaction_group_link_created_by_user_uuid', table_name='transaction_group_link')
    op.drop_index('ix_transaction_group_link_group_id', table_name='transaction_group_link')
    op.drop_index('ix_transaction_group_link_group_uuid', table_name='transaction_group_link')
    op.drop_index('ix_transaction_group_link_id', table_name='transaction_group_link')
    op.drop_index('ix_transaction_group_link_is_deleted', table_name='transaction_group_link')
    op.drop_index('ix_transaction_group_link_transaction_id', table_name='transaction_group_link')
    op.drop_index('ix_transaction_group_link_transaction_uuid', table_name='transaction_group_link')
    op.drop_index('ix_transaction_group_link_uuid', table_name='transaction_group_link')
    op.drop_table('transaction_group_link')
    op.drop_index('ix_user_transaction_transaction_id', table_name='user_transaction')
    op.create_index(op.f('ix_user_transaction_transaction_id'), 'user_transaction', ['transaction_id'], unique=True)
    op.drop_index('ix_user_transaction_transaction_uuid', table_name='user_transaction')
    op.create_index(op.f('ix_user_transaction_transaction_uuid'), 'user_transaction', ['transaction_uuid'], unique=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_user_transaction_transaction_uuid'), table_name='user_transaction')
    op.create_index('ix_user_transaction_transaction_uuid', 'user_transaction', ['transaction_uuid'], unique=False)
    op.drop_index(op.f('ix_user_transaction_transaction_id'), table_name='user_transaction')
    op.create_index('ix_user_transaction_transaction_id', 'user_transaction', ['transaction_id'], unique=False)
    op.create_table('transaction_group_link',
    sa.Column('transaction_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('transaction_uuid', sa.UUID(), autoincrement=False, nullable=False),
    sa.Column('group_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('group_uuid', sa.UUID(), autoincrement=False, nullable=False),
    sa.Column('created_by_user_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('created_by_user_uuid', sa.UUID(), autoincrement=False, nullable=False),
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('uuid', sa.UUID(), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
    sa.Column('deleted_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
    sa.Column('is_deleted', sa.BOOLEAN(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['created_by_user_id'], ['user.id'], name='transaction_group_link_created_by_user_id_fkey'),
    sa.ForeignKeyConstraint(['group_id'], ['group.id'], name='transaction_group_link_group_id_fkey'),
    sa.ForeignKeyConstraint(['transaction_id'], ['transaction.id'], name='transaction_group_link_transaction_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='transaction_group_link_pkey')
    )
    op.create_index('ix_transaction_group_link_uuid', 'transaction_group_link', ['uuid'], unique=True)
    op.create_index('ix_transaction_group_link_transaction_uuid', 'transaction_group_link', ['transaction_uuid'], unique=True)
    op.create_index('ix_transaction_group_link_transaction_id', 'transaction_group_link', ['transaction_id'], unique=True)
    op.create_index('ix_transaction_group_link_is_deleted', 'transaction_group_link', ['is_deleted'], unique=False)
    op.create_index('ix_transaction_group_link_id', 'transaction_group_link', ['id'], unique=True)
    op.create_index('ix_transaction_group_link_group_uuid', 'transaction_group_link', ['group_uuid'], unique=False)
    op.create_index('ix_transaction_group_link_group_id', 'transaction_group_link', ['group_id'], unique=False)
    op.create_index('ix_transaction_group_link_created_by_user_uuid', 'transaction_group_link', ['created_by_user_uuid'], unique=False)
    op.create_index('ix_transaction_group_link_created_by_user_id', 'transaction_group_link', ['created_by_user_id'], unique=False)
    op.create_table('user_group_link',
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('user_uuid', sa.UUID(), autoincrement=False, nullable=False),
    sa.Column('group_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('group_uuid', sa.UUID(), autoincrement=False, nullable=False),
    sa.Column('user_role', postgresql.ENUM('ADMIN', 'MEMBER', name='userrole'), autoincrement=False, nullable=False),
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('uuid', sa.UUID(), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['group_id'], ['group.id'], name='user_group_link_group_id_fkey'),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], name='user_group_link_user_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='user_group_link_pkey')
    )
    op.create_index('ix_user_group_link_uuid', 'user_group_link', ['uuid'], unique=True)
    op.create_index('ix_user_group_link_user_uuid', 'user_group_link', ['user_uuid'], unique=False)
    op.create_index('ix_user_group_link_user_role', 'user_group_link', ['user_role'], unique=False)
    op.create_index('ix_user_group_link_user_id', 'user_group_link', ['user_id'], unique=False)
    op.create_index('ix_user_group_link_id', 'user_group_link', ['id'], unique=True)
    op.create_index('ix_user_group_link_group_uuid', 'user_group_link', ['group_uuid'], unique=False)
    op.create_index('ix_user_group_link_group_id', 'user_group_link', ['group_id'], unique=False)
    # ### end Alembic commands ###
