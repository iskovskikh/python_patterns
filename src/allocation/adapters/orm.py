from sqlalchemy import (
    Table, MetaData, Column, Integer, String, Date, ForeignKey,
    event,
)
from sqlalchemy.orm import registry
from sqlalchemy.orm import relationship

from allocation.models import OrderLine, Batch, Product

metadata = MetaData()

mapper_registry = registry()

order_lines = Table(
    'order_lines', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('sku', String(255)),
    Column('quantity', Integer, nullable=False),
    Column('orderid', String(255)),
)

# products = Table(
#     'products', metadata,
#     Column('sku', String(255), primary_key=True),
#     Column('version_number', Integer, nullable=False, server_default='0'),
# )

batches = Table(
    'batches', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('reference', String(255)),
    # Column('sku', ForeignKey('products.sku')),
    Column('sku', String(255)),
    Column('_purchased_quantity', Integer, nullable=False),
    Column('eta', Date, nullable=True),
)

allocations = Table(
    'allocations', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('order_line_id', ForeignKey('order_lines.id')),
    Column('batch_id', ForeignKey('batches.id')),
)


# def start_mappers():
#     lines_mapper = mapper_registry.map_imperatively(OrderLine, order_lines)
#     mapper_registry.map_imperatively(Batch, batches, properties={
#         '_allocations': relationship(
#             lines_mapper,
#             secondary=allocations,
#             collection_class=set,
#         )
#     })

def start_mappers():
    lines_mapper = mapper_registry.map_imperatively(OrderLine, order_lines)
    mapper_registry.map_imperatively(
        Batch,
        batches,
        properties={
            "_allocations": relationship(
                lines_mapper, secondary=allocations, collection_class=set,
            )
        },
    )
