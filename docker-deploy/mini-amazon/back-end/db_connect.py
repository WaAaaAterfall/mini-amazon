from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import Session, sessionmaker, declarative_base
import psycopg2
from db_table import *

def connectDB():
    return create_engine('postgresql://postgres:passw0rd@localhost:5432/amazon_568')
def createAllTable(engine):
    Base.metadata.create_all(engine)

def dropAllTable(engine):
    Base.metadata.drop_all(engine)

def getSession(engine):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    engine.dispose()
    return session

def dbInit():
    engine = connectDB()
    return getSession(engine)

def initDB():
    engine = connectDB()
    dropAllTable(engine)
    insp = inspect(engine)
    if not (insp.has_table("warehouse") and insp.has_table("product") and insp.has_table("inventory") and insp.has_table("order")):
        dropAllTable(engine)
        createAllTable(engine)
    return engine