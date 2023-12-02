import pytest

from allocation.models import OrderLine, Batch
from allocation.repository import InMemoryBatchRepository
from allocation.services import allocate, InvalidSkuException


class FakeSession():
    committed = False

    def commit(self):
        self.committed = True


def test_return_allocations():
    line = OrderLine(orderid='order-001', sku='Table', quantity=10)
    batch = Batch(reference='batch-001', sku='Table', quantity=100, eta=None)
    repo = InMemoryBatchRepository([batch])
    result = allocate(line, repo, FakeSession())
    assert result == 'batch-001'

def test_commits():
    line = OrderLine(orderid='order-001', sku='Table', quantity=10)
    batch = Batch(reference='batch-001', sku='Table', quantity=100, eta=None)
    repo = InMemoryBatchRepository([batch])
    session = FakeSession()
    allocate(line, repo, session)
    assert session.committed is True

def test_error_for_invalid_sku():
    line = OrderLine(orderid='order-001', sku='NotExistingTable', quantity=10)
    batch = Batch(reference='batch-001', sku='Table', quantity=100, eta=None)
    repo = InMemoryBatchRepository([batch])
    with pytest.raises(InvalidSkuException, match='Недопустимый артикул NotExistingTable'):
        allocate(line, repo, FakeSession())
