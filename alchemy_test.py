from sqlalchemy import create_engine
from sqlalchemy import text
print('alchemy_test')

engine = create_engine('sqlite:///*memory*', echo=True)

