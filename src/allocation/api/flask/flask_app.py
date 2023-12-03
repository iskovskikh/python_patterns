from datetime import datetime

from flask import Flask, jsonify, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from allocation import config, services
from allocation.adapters.orm import start_mappers
from allocation.models import OutOfStockException
from allocation.repository import SqlAlchemyBatchRepository
from allocation.service_layer.unit_of_work import SqlAlchemyBatchUnitOfWork
from allocation.services import InvalidSkuException

app = Flask(__name__)


@app.route('/', methods=['get'])
def index():
    return jsonify({'app': 'flask'}), 200


start_mappers()
engine = create_engine(config.get_sqlite_uri(), echo=True)
get_session = sessionmaker(bind=engine)


# metadata.create_all(bind=engine)


@app.route('/allocate', methods=['get', 'post'])
def allocate():
    uow = SqlAlchemyBatchUnitOfWork()
    try:
        batch_ref = services.allocate(
            orderid=request.json['orderid'],
            sku=request.json['sku'],
            quantity=request.json['quantity'],
            uow=uow
        )
    except (OutOfStockException, InvalidSkuException) as e:
        return jsonify(dict(message=str(e))), 400
    return jsonify({'batch_ref': batch_ref}), 201


@app.route('/add_batch', methods=['post', ])
def add_batch():
    uow = SqlAlchemyBatchUnitOfWork()
    eta = request.json['eta']
    if eta is not None:
        eta = datetime.fromisoformat(eta).date()

    services.add_batch(
        reference=request.json['reference'],
        sku=request.json['sku'],
        quantity=request.json['quantity'],
        eta=eta,
        uow=uow
    )

    return 'OK', 201
