from allocation import models
from allocation.models import OrderLine
from allocation.repository import AbstractBatchRepository


class InvalidSkuException(Exception):
    pass


def is_valid_sku(sku, batches):
    return sku in {b.sku for b in batches}


def allocate(line: OrderLine, repo: AbstractBatchRepository, sesson) -> str:
    batches = repo.list()
    if not is_valid_sku(line.sku, batches):
        raise InvalidSkuException(f'Недопустимый артикул {line.sku}')
    batch_ref = models.allocate(line, batches)
    sesson.commit()
    return batch_ref
