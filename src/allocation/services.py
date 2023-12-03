from datetime import date
from typing import Optional

from allocation import models
from allocation.models import Batch, OrderLine
from allocation.repository import AbstractBatchRepository


class InvalidSkuException(Exception):
    pass


def is_valid_sku(sku, batches):
    return sku in {b.sku for b in batches}


def allocate(
        orderid: str,
        sku: str,
        quantity: int,
        repo: AbstractBatchRepository,
        session
) -> str:
    line = OrderLine(
        orderid=orderid,
        sku=sku,
        quantity=quantity
    )
    batches = repo.list()
    if not is_valid_sku(line.sku, batches):
        raise InvalidSkuException(f'Недопустимый артикул {sku}')
    batch_ref = models.allocate(line, batches)
    session.commit()
    return batch_ref


def add_batch(
        reference: str,
        sku: str,
        quantity: int,
        eta: Optional[date],
        repo: AbstractBatchRepository,
        session
):
    repo.add(Batch(reference=reference, sku=sku, quantity=quantity, eta=eta))
    session.commit()
