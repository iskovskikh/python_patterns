from dataclasses import dataclass
from datetime import date
from typing import Optional, Set


class OutOfStock(Exception):
    pass


class Product:
    sku: str
    version_number: int


# @dataclass(frozen=True)
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


def allocate(line: OrderLine, batches: list[Batch]) -> str:
    try:
        batch = next(
            b for b in sorted(batches) if b.can_allocate(line)
        )
    except StopIteration:
        raise OutOfStock(f'Артикула {line.sku} нет в наличии')
    batch.allocate(line)
    return batch.reference
