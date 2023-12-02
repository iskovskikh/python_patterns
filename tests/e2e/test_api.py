import uuid

import pytest as pytest
import requests as requests

from allocation import config


def random_suffix():
    return uuid.uuid4().hex[:6]


def random_sku(name=""):
    return f"sku-{name}-{random_suffix()}"


def random_batchref(name=""):
    return f"batch-{name}-{random_suffix()}"


def random_orderid(name=""):
    return f"order-{name}-{random_suffix()}"


@pytest.mark.usefixtures("restart_api")
def test_api_returns_201_and_allocate_batch(add_stock):
    sku, other_sku = random_sku(), random_sku('other')
    early_batch_ref = random_batchref('1')
    later_batch_ref = random_batchref('2')
    other_batch_ref = random_batchref('3')
    add_stock([
        (later_batch_ref, sku, 100, '2023-01-02'),
        (early_batch_ref, sku, 100, '2023-01-01'),
        (other_batch_ref, sku, 100, None),
    ])

    data = dict(orderid=random_orderid(), sku=sku, quantity=2)
    url = config.get_api_url()
    r = requests.post(f'{url}/allocate', json=data)
    assert r.status_code == 201
    assert r.json()['batch_ref'] == other_batch_ref


@pytest.mark.usefixtures('restart_api')
def test_api_returns_400_and_error_message():
    unknown_sku = random_sku()
    order_id = random_orderid()
    data = dict(orderid=order_id, sku=unknown_sku, quantity=2)
    url = config.get_api_url()
    r = requests.post(f'{url}/allocate', json=data)
    assert r.status_code == 400
    assert r.json()['message'] == f'Недопустимый артикул {unknown_sku}'