import uuid

import pytest as pytest
import requests as requests

from allocation import config


def random_suffix():
    return uuid.uuid4().hex[:6]


def random_sku(name=""):
    return f"sku-{name}-{random_suffix()}"


def random_batch_ref(name=""):
    return f"batch-{name}-{random_suffix()}"


def random_order_id(name=""):
    return f"order-{name}-{random_suffix()}"


def post_to_add_batch(
        reference,
        sku,
        quantity,
        eta
):
    uri = config.get_api_url()
    r = requests.post(
        f'{uri}/add_batch',
        json=dict(
            reference=reference,
            sku=sku,
            quantity=quantity,
            eta=eta
        )
    )
    assert r.status_code == 201


@pytest.mark.usefixtures("sqlite_db")
@pytest.mark.usefixtures("restart_api")
def test_api_returns_201_and_allocate_batch():
    sku, other_sku = random_sku(), random_sku('other')
    early_batch_ref = random_batch_ref('1')
    later_batch_ref = random_batch_ref('2')
    other_batch_ref = random_batch_ref('3')
    post_to_add_batch(later_batch_ref, sku, 100, '2023-01-02'),
    post_to_add_batch(early_batch_ref, sku, 100, '2023-01-01'),
    post_to_add_batch(other_batch_ref, sku, 100, None),
    data = dict(orderid=random_order_id(), sku=sku, quantity=2)
    url = config.get_api_url()
    r = requests.post(f'{url}/allocate', json=data)
    assert r.status_code == 201
    assert r.json()['batch_ref'] == other_batch_ref


@pytest.mark.usefixtures("sqlite_db")
@pytest.mark.usefixtures('restart_api')
def test_api_returns_400_and_error_message():
    unknown_sku = random_sku()
    order_id = random_order_id()
    data = dict(orderid=order_id, sku=unknown_sku, quantity=2)
    url = config.get_api_url()
    r = requests.post(f'{url}/allocate', json=data)
    assert r.status_code == 400
    assert r.json()['message'] == f'Недопустимый артикул {unknown_sku}'
