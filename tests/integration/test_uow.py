import threading
import time

from sqlalchemy import text

from allocation.models import OrderLine
from allocation.service_layer.unit_of_work import SqlAlchemyProductUnitOfWork
from tests.e2e.test_api import random_batch_ref, random_sku, random_order_id


def insert_batch(session, reference, sku, qty, eta, version_number):
    session.execute(
        text('INSERT INTO batches (reference, sku, _purchased_quantity, eta, version_number)'
             ' VALUES (:reference, :sku, :qty, :eta, :version_number)'),
        dict(reference=reference, sku=sku, qty=qty, eta=eta, version_number=version_number)
    )


def get_allocated_batch_ref(session, orderid, sku):
    [[order_line_id]] = session.execute(
        text('SELECT id FROM order_lines WHERE orderid = :orderid AND sku=:sku'),
        dict(orderid=orderid, sku=sku)
    )
    [[batch_ref]] = session.execute(
        text('SELECT b.reference FROM allocations JOIN batches AS b ON batch_id = b.id'
             ' WHERE order_line_id=:order_line_id'),
        dict(order_line_id=order_line_id)
    )
    return batch_ref


def test_uow_can_retrieve_a_batch_and_allocate_to_it(session_factory):
    session = session_factory()
    insert_batch(session, 'batch-007', 'Table', 30, None)
    session.commit()

    uow = SqlAlchemyProductUnitOfWork(session_factory)
    with uow:
        batch = uow.products.get(reference='batch-007')
        line = OrderLine(orderid='order-001', sku='Table', quantity=10)
        batch.allocate(line)
        uow.commit()

    batch_ref = get_allocated_batch_ref(session, orderid='order-001', sku='Table')
    assert batch_ref == 'batch-007'


def try_to_allocate(order_id, sku, exceptions):
    line = OrderLine(orderid=order_id, sku=sku, quantity=10)
    try:
        with SqlAlchemyProductUnitOfWork() as uow:
            product = uow.products.get(sku)
            product.allocate(line)
            time.sleep(0.2)
            uow.commit()
    except Exception as e:
        exceptions.append(e)


def test_concurrent_updates_to_version_are_not_allowed(postgres_session_factory):
    sku = random_sku()
    batch = random_batch_ref()
    session = postgres_session_factory()
    insert_batch(session, batch, sku, 30, eta=None, version=0)
    session.commit()

    order1 = random_order_id(1)
    order2 = random_order_id(2)

    exceptions = []

    try_to_allocate_order1 = lambda: try_to_allocate(order1, sku, exceptions)
    try_to_allocate_order2 = lambda: try_to_allocate(order2, sku, exceptions)

    tread1 = threading.Thread(target=try_to_allocate_order1)
    tread2 = threading.Thread(target=try_to_allocate_order2)

    tread1.start()
    tread2.start()
    tread1.join()
    tread2.join()

    [[version]] = session.execute(
        text('SELECT version_number FROM products WHERE sku=:sku'),
        dict(sku=sku)
    )
    assert version == 2
    [exception] = exceptions
    assert 'не получилось сериализовать доступ из-за параллельного обновления' in str(exception)

    orders = list(session.execute(
        text(
            'SELECT orderid FROM allocations'
            ' JOIN batches ON allocations.batch_id = batches.id'
            ' JOIN order_lines ON allocations.order_line_id = order_lines.id'
            ' WHERE order_lines.sku = :sku'
        ),
        dict(sku=sku),
    ))

    assert len(orders) == 1

    with SqlAlchemyProductUnitOfWork() as uow:
        uow.session.execute(
            text('SELECT 1')
        )