from dataclasses import dataclass
from datetime import date
from typing import Optional, Set, List


class OutOfStockException(Exception):
    pass


@dataclass(unsafe_hash=True)
class OrderLine:
    orderid: str
    sku: str
    quantity: int


class Batch:
    def __init__(
            self,
            reference: str,
            sku: str,
            quantity: int,
            eta: Optional[date]
    ):
        self.reference = reference
        self.sku = sku
        self.eta = eta
        self._purchased_quantity: int = quantity
        self._allocations: Set[OrderLine] = set()

    def __repr__(self):
        return f"<Batch {self.reference}>"

    def __hash__(self):
        return hash(self.reference)

    def __gt__(self, other):
        if self.eta is None:
            return False
        if other.eta is None:
            return True
        return self.eta > other.eta

    def __eq__(self, other):
        if not isinstance(other, Batch):
            return False
        return self.reference == other.reference

    def allocate(self, line: OrderLine):
        if self.can_allocate(line):
            return self._allocations.add(line)

    def deallocate(self, line: OrderLine):
        if line in self._allocations:
            self._allocations.remove(line)

    @property
    def allocated_quantity(self) -> int:
        return sum(line.quantity for line in self._allocations)

    @property
    def available_quantity(self) -> int:
        return self._purchased_quantity - self.allocated_quantity

    def can_allocate(self, line: OrderLine) -> bool:
        return self.sku == line.sku and self.available_quantity >= line.quantity


class Product:

    def __init__(self, sku: str, batches: list[Batch], version_number: int = 0):
        self.sku = sku
        self.batches = batches
        self.version_number = version_number

    def allocate(self, line: OrderLine) -> str:
        try:
            batch = next(b for b in sorted(self.batches) if b.can_allocate(line))
            batch.allocate(line)
            self.version_number += 1
            return batch.reference
        except StopIteration:
            raise OutOfStockException(f'Артикула {line.sku} нет в наличии')
