from sqlalchemy import text

from allocation.models import Batch, OrderLine
from allocation.repository import SqlAlchemyBatchRepository


def test_repository_can_save_batch(session):
    batch = Batch(
        reference='batch-001',
        sku='Table',
        quantity=10,
        eta=None
    )

    repo = SqlAlchemyBatchRepository(session)
    repo.add(batch)
    session.commit()

    rows = list(session.execute(
        text('SELECT reference, sku, _purchased_quantity, eta FROM batches')
    ))
    assert rows == [('batch-001', 'Table', 10, None)]


def insert_order_line(session) -> str:
    session.execute(
        text('INSERT INTO order_lines (orderId, sku, quantity) VALUES ("order-001", "Table", 10)')
    )

    [[order_line_id]] = session.execute(
        text('SELECT id FROM order_lines WHERE orderId=:orderId AND sku=:sku'), dict(orderId='order-001', sku='Table')
    )

    return order_line_id


def insert_batch(session, batch_id):
    session.execute(
        text('INSERT INTO batches (reference, sku, _purchased_quantity, eta) VALUES (:batch_id, "Table", 10, null)'),
        dict(batch_id=batch_id)
    )
    [[batch_id]] = session.execute(
        text('SELECT id FROM batches WHERE reference=:batch_id AND sku="Table"'), dict(batch_id=batch_id)
    )
    return batch_id


def insert_allocation(session, order_line_id, batch_id):
    session.execute(
        text('INSERT INTO allocations (order_line_id, batch_id) VALUES (:order_line_id, :batch_id)'),
        dict(order_line_id=order_line_id, batch_id=batch_id)
    )


def test_repository_can_retrieve_batch_with_allocations(session):
    order_line_id = insert_order_line(session)
    batch1_id = insert_batch(session, 'batch1')
    insert_batch(session, 'batch2')
    insert_allocation(session, order_line_id, batch1_id)
    repo = SqlAlchemyBatchRepository(session)
    retrieved = repo.get('batch1')

    expected = Batch(
        reference='batch1',
        sku='Table',
        quantity=10,
        eta=None
    )

    assert retrieved == expected

    assert retrieved.sku == expected.sku
    assert retrieved._purchased_quantity == expected._purchased_quantity
    assert retrieved._allocations == {OrderLine('order-001', 'Table', 10)}
