from flask import Flask, jsonify, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from allocation import config, services
from allocation.adapters.orm import start_mappers, metadata
from allocation.models import Batch, OrderLine, allocate, OutOfStockException
from allocation.repository import SqlAlchemyBatchRepository
from allocation.services import InvalidSkuException

app = Flask(__name__)


@app.route('/', methods=['get'])
def index():
    return jsonify({'app': 'flask'}), 200


start_mappers()
engine = create_engine(config.get_sqlite_uri(),echo=True)
get_session = sessionmaker(bind=engine)
# metadata.create_all(bind=engine)


@app.route('/allocate', methods=['get', 'post'])
def allocate_endpoint():
    session = get_session()
    repo = SqlAlchemyBatchRepository(session)
    line = OrderLine(
        orderid=request.json['orderid'],
        sku=request.json['sku'],
        quantity=request.json['quantity']
    )
    try:
        batch_ref = services.allocate(line, repo, session)
    except (OutOfStockException, InvalidSkuException) as e:
        return jsonify(dict(message=str(e))), 400
    return jsonify({'batch_ref': batch_ref}), 201
