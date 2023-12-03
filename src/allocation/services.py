from datetime import date
from typing import Optional

from allocation import models
from allocation.models import Batch, OrderLine
from allocation.repository import AbstractBatchRepository
from allocation.service_layer.unit_of_work import AbstractBatchUnitOfWork


class InvalidSkuException(Exception):
    pass


def is_valid_sku(sku, batches):
    return sku in {b.sku for b in batches}


def allocate(
        orderid: str,
        sku: str,
        quantity: int,
        uow:AbstractBatchUnitOfWork
) -> str:
    line = OrderLine(
        orderid=orderid,
        sku=sku,
        quantity=quantity
    )
    with uow:
        batches = uow.batches.list()
        if not is_valid_sku(line.sku, batches):
            raise InvalidSkuException(f'Недопустимый артикул {sku}')
        batch_ref = models.allocate(line, batches)
        uow.commit()
    return batch_ref


def add_batch(
        reference: str,
        sku: str,
        quantity: int,
        eta: Optional[date],
        uow: AbstractBatchUnitOfWork
):
    with uow:
        uow.batches.add(Batch(reference=reference, sku=sku, quantity=quantity, eta=eta))
        uow.commit()
