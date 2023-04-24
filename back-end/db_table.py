from sqlalchemy import Integer, Integer, Column, ForeignKey, TEXT, TIMESTAMP
from sqlalchemy.orm import declarative_base, joinedload, relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# engine = create_engine(
#     'postgresql://postgres:postgres@postgres_db_container:5432/postgres')
engine = create_engine(
    'postgresql://postgres:passw0rd@localhost:5432/amazon_568')
Session = sessionmaker(bind=engine)
Base = declarative_base()

class Warehouse(Base):
    __tablename__ = 'warehouse'
    id = Column(Integer, primary_key=True, autoincrement=False)
    world_id = Column(Integer, autoincrement=False)
    x = Column(Integer)
    y = Column(Integer)


class Product(Base):
    __tablename__ = 'product'
    id = Column(Integer, primary_key=True, autoincrement=False)
    description = Column(TEXT)


class Inventory(Base):
    __tablename__ = 'inventory'
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('product.id'))
    remain_count = Column(Integer)
    warehouse_id = Column(Integer, ForeignKey('warehouse.id'))


class Order(Base):
    __tablename__ = 'order'
    package_id = Column(Integer, primary_key=True, autoincrement=False)
    count = Column(Integer, nullable=False)
    status = Column(TEXT) #Delivered, OutForDelivery, Packed, Processing
    truck_id = Column(Integer, nullable=True)
    warehouse_id = Column(Integer, ForeignKey('warehouse.id'), nullable=True)
    addr_x = Column(Integer)
    addr_y = Column(Integer)
    product_id = Column(Integer, ForeignKey('product.id'))
    #time = Column(TIMESTAMP, default=None, nullable=True)
    product = relationship("Product")


