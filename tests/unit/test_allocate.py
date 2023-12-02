from datetime import date, timedelta

import pytest

from allocation.models import Batch, OrderLine, OutOfStockException, allocate


def test_prefer_current_stock_batches():
    in_stock_batch = Batch(
        reference='batch-001',
        sku='Table',
        quantity=10,
        eta=None
    )
    shipment_batch = Batch(
        reference='batch-001',
        sku='Table',
        quantity=10,
        eta=date.today() + timedelta(days=1)
    )

    order_line = OrderLine(
        orderid='order-001',
        sku='Table',
        quantity=2
    )

    allocate(order_line, [in_stock_batch, shipment_batch])

    assert in_stock_batch.available_quantity == 8
    assert shipment_batch.available_quantity == 10


def test_prefer_earlier_batches():
    earlier_batch = Batch(
        reference='batch-001',
        sku='Table',
        quantity=10,
        eta=date.today()
    )
    medium_batch = Batch(
        reference='batch-001',
        sku='Table',
        quantity=10,
        eta=date.today() + timedelta(days=1)
    )
    latest_batch = Batch(
        reference='batch-001',
        sku='Table',
        quantity=10,
        eta=date.today() + timedelta(days=2)
    )

    order_line = OrderLine(
        orderid='order-001',
        sku='Table',
        quantity=2
    )

    allocate(order_line, [earlier_batch, medium_batch, latest_batch])

    assert earlier_batch.available_quantity == 8
    assert medium_batch.available_quantity == 10
    assert latest_batch.available_quantity == 10


def test_return_allocated_batch_ref():
    in_stock_batch = Batch(
        reference='batch-001',
        sku='Table',
        quantity=10,
        eta=None
    )
    shipment_batch = Batch(
        reference='batch-001',
        sku='Table',
        quantity=10,
        eta=date.today() + timedelta(days=1)
    )

    order_line = OrderLine(
        orderid='order-001',
        sku='Table',
        quantity=2
    )

    allocation = allocate(order_line, [in_stock_batch, shipment_batch])

    assert allocation == in_stock_batch.reference


def test_raise_out_of_stock_exception_if_cannot_allocate():
    in_stock_batch = Batch(
        reference='batch-001',
        sku='Table',
        quantity=10,
        eta=None
    )
    order_1 = OrderLine(
        orderid='order-001',
        sku='Table',
        quantity=10
    )
    allocate(order_1, [in_stock_batch, ])
    order_2 = OrderLine(
        orderid='order-002',
        sku='Table',
        quantity=10
    )
    with pytest.raises(OutOfStockException, match='Table'):
        allocate(order_2, [in_stock_batch, ])
