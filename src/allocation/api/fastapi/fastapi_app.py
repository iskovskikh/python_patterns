from datetime import date
from typing import Optional

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from allocation import services
from allocation.api.flask.flask_app import get_session
from allocation.models import OrderLine, OutOfStockException
from allocation.repository import SqlAlchemyBatchRepository
from allocation.services import InvalidSkuException

app = FastAPI()


# def get_session():
#     pass


class LineInput(BaseModel):
    orderid: str
    sku: str
    quantity: int


@app.post('/allocate', status_code=201)
def allocate(line: LineInput):
    session = get_session()
    repo = SqlAlchemyBatchRepository(session)
    try:
        batch_ref = services.allocate(
            orderid=line.orderid,
            sku=line.sku,
            quantity=line.quantity,
            repo=repo,
            session=session
        )
    except (OutOfStockException, InvalidSkuException) as e:
        return JSONResponse(
            status_code=400,
            content={"message": str(e)}
        )
    return {'batch_ref': batch_ref}


class BatchInput(BaseModel):
    reference: str
    sku: str
    quantity: int
    eta: Optional[date]


@app.post('/add_batch', status_code=201)
def add_batch(batch: BatchInput):
    session = get_session()
    repo = SqlAlchemyBatchRepository(session)

    # eta = batch.eta
    # if eta is not None:
    #     eta = datetime.fromisoformat(eta).date()

    services.add_batch(
        reference=batch.reference,
        sku=batch.sku,
        quantity=batch.quantity,
        eta=batch.eta,
        repo=repo,
        session=session
    )

    return 'OK'
