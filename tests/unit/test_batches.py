from datetime import date

from allocation.models import OrderLine, Batch


def make_batch_and_line(sku, batch_qty, line_qty):
    batch = Batch(
        reference='batch-001',
        sku=sku,
        quantity=batch_qty,
        eta=date.today()
    )
    order_line = OrderLine(
        orderid='order-001',
        sku=sku,
        quantity=line_qty
    )
    return batch, order_line


def test_allocating_to_batch_reduce_available_quantity():
    batch, order_line = make_batch_and_line(sku='Table', batch_qty=12, line_qty=2)
    batch.allocate(order_line)
    assert batch.available_quantity == 10


def test_can_allocate_if_available_gt_required():
    batch, order_line = make_batch_and_line(sku='Table', batch_qty=12, line_qty=2)
    assert batch.can_allocate(order_line)


def test_can_allocate_if_available_lt_required():
    batch, order_line = make_batch_and_line(sku='Table', batch_qty=2, line_qty=10)
    assert batch.can_allocate(order_line) is False


def test_can_allocate_if_available_eq_required():
    batch, order_line = make_batch_and_line(sku='Table', batch_qty=10, line_qty=10)
    assert batch.can_allocate(order_line)


def test_can_allocate_if_sku_does_not_match():
    batch = Batch(
        reference='batch-001',
        sku='sku-001',
        quantity=2,
        eta=date.today()
    )
    order_line = OrderLine(
        orderid='order-001',
        sku='sku-002',
        quantity=2
    )
    assert batch.can_allocate(order_line) is False


def test_can_only_deallocate_allocated_lines():
    batch, order_line = make_batch_and_line(sku='Table', batch_qty=10, line_qty=2)
    batch.deallocate(order_line)
    assert batch.available_quantity == 10


def test_allocation_is_idempotent():
    batch, order_line = make_batch_and_line(sku='Table', batch_qty=10, line_qty=2)
    batch.allocate(order_line)
    batch.allocate(order_line)
    assert batch.available_quantity == 8


