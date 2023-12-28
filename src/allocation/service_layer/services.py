from datetime import date
from typing import Optional

from allocation.models import Batch, OrderLine, Product
from allocation.service_layer.unit_of_work import AbstractProductUnitOfWork


class InvalidSkuException(Exception):
    pass


def is_valid_sku(sku, batches):
    return sku in {b.sku for b in batches}


def allocate(
        orderid: str,
        sku: str,
        quantity: int,
        uow: AbstractProductUnitOfWork
) -> str:
    line = OrderLine(
        orderid=orderid,
        sku=sku,
        quantity=quantity
    )
    with uow:
        product = uow.products.get(line.sku)
        if product is None:
            raise InvalidSkuException(f'Недопустимый артикул {sku}')
        batch_ref = product.allocate(line)
        uow.commit()
    return batch_ref


def add_batch(
        reference: str,
        sku: str,
        quantity: int,
        eta: Optional[date],
        uow: AbstractProductUnitOfWork
):
    with uow:
        product = uow.products.get(sku=sku)
        if product is None:
            product = Product(sku=sku, batches=[])
            uow.products.add(product)
        product.batches.append(Batch(reference=reference, sku=sku, quantity=quantity, eta=eta))
        uow.commit()
