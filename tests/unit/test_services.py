import pytest

from allocation import services
from allocation.models import Batch
from allocation.repository import AbstractBatchRepository
from allocation.service_layer.unit_of_work import AbstractProductUnitOfWork
from allocation.services import InvalidSkuException


class FakeSession:
    committed = False

    def commit(self):
        self.committed = True


class FakeBatchRepository(AbstractBatchRepository):

    def __init__(self, batches):
        self._batches = set(batches)

    def add(self, batch: Batch):
        self._batches.add(batch)

    def get(self, reference):
        return next(b for b in self._batches if b.reference == reference)

    def list(self) -> list[Batch]:
        return list(self._batches)


class FakeProductUnitOfWork(AbstractProductUnitOfWork):
    def __init__(self):
        self.batches = FakeBatchRepository([])
        self.committed = False

    def commit(self):
        self.committed = True

    def rollback(self):
        pass


def test_add_batch():
    # repo, session = FakeBatchRepository([]), FakeSession()
    uow = FakeProductUnitOfWork()
    services.add_batch(
        reference='b1',
        sku='table',
        quantity=2,
        eta=None,
        uow=uow
    )

    assert uow.batches.get('b1') is not None
    assert uow.committed


def test_allocate_returns_allocation():
    uow = FakeProductUnitOfWork()
    services.add_batch(
        reference='b1',
        sku='Table',
        quantity=2,
        eta=None,
        uow=uow
    )
    result = services.allocate(
        orderid='o1',
        sku='Table',
        quantity=1,
        uow=uow
    )
    assert result == "b1"


def test_allocate_error_for_invalid_sku():
    uow = FakeProductUnitOfWork()
    services.add_batch(
        reference='batch-001',
        sku='Table',
        quantity=100,
        eta=None,
        uow=uow
    )
    with pytest.raises(InvalidSkuException, match='Недопустимый артикул NotExistingTable'):
        services.allocate(
            orderid='order-001',
            sku='NotExistingTable',
            quantity=10,
            uow=uow
        )


def test_allocate_commits():
    uow = FakeProductUnitOfWork()
    services.add_batch(
        reference='batch-001',
        sku='Table',
        quantity=100,
        eta=None,
        uow=uow
    )
    services.allocate(
        orderid='order-001',
        sku='Table',
        quantity=10,
        uow=uow
    )
    assert uow.committed
