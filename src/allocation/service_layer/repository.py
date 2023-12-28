from abc import ABC, abstractmethod

from allocation.models import Batch, Product


class AbstractBatchRepository(ABC):

    @abstractmethod
    def add(self, batch: Batch):
        raise NotImplementedError

    @abstractmethod
    def get(self, reference) -> Batch:
        raise NotImplementedError

    @abstractmethod
    def list(self) -> list[Batch]:
        raise NotImplementedError


class AbstractProductRepository(ABC):
    @abstractmethod
    def add(self, product: Product) -> None:
        raise NotImplementedError

    @abstractmethod
    def get(self, sku) -> Product:
        raise NotImplementedError


class SqlAlchemyProductRepository(AbstractBatchRepository):

    def __init__(self, session):
        self.session = session

    def add(self, batch):
        self.session.add(batch)

    def get(self, reference):
        return self.session.query(Batch).filter_by(reference=reference).one()

    def list(self):
        return self.session.query(Batch).all()
