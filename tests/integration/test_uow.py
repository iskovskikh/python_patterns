from allocation.service_layer.unit_of_work import SqlAlchemyBatchUnitOfWork
from allocation.models import OrderLine
from sqlalchemy import text


def insert_batch(session, reference, sku, qty, eta):
    session.execute(
        text('INSERT INTO batches (reference, sku, _purchased_quantity, eta)'
        ' VALUES (:reference, :sku, :qty, :eta)'),
        dict(reference=reference, sku=sku, qty=qty, eta=eta)
    )


def get_allocated_batch_ref(session, orderid, sku):
    [[order_line_id]] = session.execute(
        text('SELECT id FROM order_lines WHERE orderid = :orderid AND sku=:sku'),
        dict(orderid=orderid, sku=sku)
    )
    [[batch_ref]]= session.execute(
        text('SELECT b.reference FROM allocations JOIN batches AS b ON batch_id = b.id'
             ' WHERE order_line_id=:order_line_id'),
        dict(order_line_id=order_line_id)
    )
    return batch_ref


def test_uow_can_retrieve_a_batch_and_allocate_to_it(session_factory):
    session = session_factory()
    insert_batch(session, 'batch-007', 'Table', 30, None)
    session.commit()

    uow = SqlAlchemyBatchUnitOfWork(session_factory)
    with uow:
        batch = uow.batches.get(reference='batch-007')
        line = OrderLine(orderid='order-001', sku='Table', quantity=10)
        batch.allocate(line)
        uow.commit()

    batch_ref = get_allocated_batch_ref(session, orderid='order-001', sku='Table')
    assert batch_ref == 'batch-007'
