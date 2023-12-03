import pytest

from allocation import services
from allocation.models import Batch
from allocation.repository import AbstractBatchRepository
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


def test_add_batch():
    repo, session = FakeBatchRepository([]), FakeSession()
    services.add_batch(
        reference='b1',
        sku='table',
        quantity=2,
        eta=None,
        repo=repo,
        session=session
    )
    assert repo.get('b1') is not None
    assert session.committed


def test_allocate_returns_allocation():
    repo, session = FakeBatchRepository([]), FakeSession()
    services.add_batch(
        reference='b1',
        sku='Table',
        quantity=2,
        eta=None,
        repo=repo,
        session=session
    )
    result = services.allocate(
        orderid='o1',
        sku='Table',
        quantity=1,
        repo=repo,
        session=session
    )
    assert result == "b1"


def test_error_for_invalid_sku():
    repo, session = FakeBatchRepository([]), FakeSession()
    services.add_batch(
        reference='batch-001',
        sku='Table',
        quantity=100,
        eta=None,
        repo=repo,
        session=session
    )
    with pytest.raises(InvalidSkuException, match='Недопустимый артикул NotExistingTable'):
        services.allocate(
            orderid='order-001',
            sku='NotExistingTable',
            quantity=10,
            repo=repo,
            session=FakeSession()
        )


def test_commits():
    repo, session = FakeBatchRepository([]), FakeSession()
    services.add_batch(
        reference='batch-001',
        sku='Table',
        quantity=100,
        eta=None,
        repo=repo,
        session=session
    )
    services.allocate(
        orderid='order-001',
        sku='Table',
        quantity=10,
        repo=repo,
        session=FakeSession()
    )
    assert session.committed is True
