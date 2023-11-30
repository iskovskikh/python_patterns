from flask import Flask, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from allocation import config
from allocation.adapters import orm
from allocation.repository import SqlAlchemyBatchRepository

app = Flask(__name__)


@app.route('/', methods=['get'])
def index():
    return jsonify({'app': 'flask'}), 200


orm.start_mappers()
get_session = sessionmaker(bind=create_engine(config.get_sqlite_uri(), echo=True))


@app.route('/allocate', methods=['post'])
def allocate_endpoint():
    session = get_session()
    repo = SqlAlchemyBatchRepository(session)

    return jsonify({'batch_ref': 'batch_00x'}), 201
