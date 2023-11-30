
from fastapi import FastAPI

app = FastAPI()

# def get_session():
#     pass


@app.get('/')
def index():
    return {'app': 'fastapi'}

@app.post('/allocate')
def allocate_endpoint():
    return {}