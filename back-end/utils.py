from datetime import datetime
from db_table import *


'''
@init_engin: Drop all the tables and restart
'''

def init_engine():
    # engine = create_engine(
    #     'postgresql://postgres:passw0rd@localhost:5432/hw4_568')
    # engine = create_engine(
    #     'postgresql://postgres:postgres@postgres_db_container:5432/postgres')
    # print('Opened database successfully')
    Base.metadata.drop_all(engine)
    print('Drop tables successfully')
    Base.metadata.create_all(engine)
    