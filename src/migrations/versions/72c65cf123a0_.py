"""empty message

Revision ID: 72c65cf123a0
Revises: 955ad3e96429
Create Date: 2024-05-01 08:03:44.796346

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '72c65cf123a0'
down_revision: Union[str, None] = '955ad3e96429'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('association_group_purchase_category')
    op.drop_table('association_group_tag')
    op.drop_table('association_transaction_tag')
    op.drop_table('association_transaction_item_tag')
    op.drop_table('association_transaction_receipt')
    op.drop_table('association_user_purchase_category')
    op.drop_table('association_user_tag')
    op.drop_table('association_transaction_item_transaction')
    op.add_column('purchase_category', sa.Column('category_description', sa.String(), nullable=True))
    op.drop_column('purchase_category', 'description')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('purchase_category', sa.Column('description', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.drop_column('purchase_category', 'category_description')
    op.create_table('association_transaction_item_transaction',
    sa.Column('transaction_item_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('transaction_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['transaction_id'], ['transaction.id'], name='association_transaction_item_transaction_transaction_id_fkey'),
    sa.ForeignKeyConstraint(['transaction_item_id'], ['transaction_item.id'], name='association_transaction_item_transacti_transaction_item_id_fkey'),
    sa.PrimaryKeyConstraint('transaction_item_id', 'transaction_id', name='association_transaction_item_transaction_pkey')
    )
    op.create_table('association_user_tag',
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('tag_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['tag_id'], ['tag.id'], name='association_user_tag_tag_id_fkey'),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], name='association_user_tag_user_id_fkey'),
    sa.PrimaryKeyConstraint('user_id', 'tag_id', name='association_user_tag_pkey')
    )
    op.create_table('association_user_purchase_category',
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('purchase_category_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['purchase_category_id'], ['purchase_category.id'], name='association_user_purchase_category_purchase_category_id_fkey'),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], name='association_user_purchase_category_user_id_fkey'),
    sa.PrimaryKeyConstraint('user_id', 'purchase_category_id', name='association_user_purchase_category_pkey')
    )
    op.create_table('association_transaction_receipt',
    sa.Column('transaction_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('receipt_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['receipt_id'], ['receipt.id'], name='association_transaction_receipt_receipt_id_fkey'),
    sa.ForeignKeyConstraint(['transaction_id'], ['transaction.id'], name='association_transaction_receipt_transaction_id_fkey'),
    sa.PrimaryKeyConstraint('transaction_id', 'receipt_id', name='association_transaction_receipt_pkey')
    )
    op.create_table('association_transaction_item_tag',
    sa.Column('transaction_item_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('tag_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['tag_id'], ['tag.id'], name='association_transaction_item_tag_tag_id_fkey'),
    sa.ForeignKeyConstraint(['transaction_item_id'], ['transaction_item.id'], name='association_transaction_item_tag_transaction_item_id_fkey'),
    sa.PrimaryKeyConstraint('transaction_item_id', 'tag_id', name='association_transaction_item_tag_pkey')
    )
    op.create_table('association_transaction_tag',
    sa.Column('transaction_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('tag_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['tag_id'], ['tag.id'], name='association_transaction_tag_tag_id_fkey'),
    sa.ForeignKeyConstraint(['transaction_id'], ['transaction.id'], name='association_transaction_tag_transaction_id_fkey'),
    sa.PrimaryKeyConstraint('transaction_id', 'tag_id', name='association_transaction_tag_pkey')
    )
    op.create_table('association_group_tag',
    sa.Column('group_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('tag_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['group_id'], ['group.id'], name='association_group_tag_group_id_fkey'),
    sa.ForeignKeyConstraint(['tag_id'], ['tag.id'], name='association_group_tag_tag_id_fkey'),
    sa.PrimaryKeyConstraint('group_id', 'tag_id', name='association_group_tag_pkey')
    )
    op.create_table('association_group_purchase_category',
    sa.Column('group_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('purchase_category_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['group_id'], ['group.id'], name='association_group_purchase_category_group_id_fkey'),
    sa.ForeignKeyConstraint(['purchase_category_id'], ['purchase_category.id'], name='association_group_purchase_category_purchase_category_id_fkey'),
    sa.PrimaryKeyConstraint('group_id', 'purchase_category_id', name='association_group_purchase_category_pkey')
    )
    # ### end Alembic commands ###