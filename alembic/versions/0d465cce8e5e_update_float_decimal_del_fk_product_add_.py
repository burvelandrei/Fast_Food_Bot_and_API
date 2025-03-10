"""update_float-->decimal_del_fk_product_add_c_name

Revision ID: 0d465cce8e5e
Revises: 7ef13faa1d14
Create Date: 2025-02-28 13:01:25.833642

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0d465cce8e5e'
down_revision: Union[str, None] = '7ef13faa1d14'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('order', sa.Column('total_amount', sa.DECIMAL(precision=10, scale=2), nullable=False))
    op.drop_column('order', 'total_price')
    op.add_column('order_item', sa.Column('name', sa.String(), nullable=False))
    op.add_column('order_item', sa.Column('total_price', sa.DECIMAL(precision=10, scale=2), nullable=False))
    op.drop_constraint('order_item_product_id_fkey', 'order_item', type_='foreignkey')
    op.alter_column('product', 'price',
               existing_type=sa.DOUBLE_PRECISION(precision=53),
               type_=sa.DECIMAL(precision=10, scale=2),
               existing_nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('product', 'price',
               existing_type=sa.DECIMAL(precision=10, scale=2),
               type_=sa.DOUBLE_PRECISION(precision=53),
               existing_nullable=False)
    op.create_foreign_key('order_item_product_id_fkey', 'order_item', 'product', ['product_id'], ['id'], ondelete='CASCADE')
    op.drop_column('order_item', 'total_price')
    op.drop_column('order_item', 'name')
    op.add_column('order', sa.Column('total_price', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=False))
    op.drop_column('order', 'total_amount')
    # ### end Alembic commands ###
