from sqlalchemy import create_engine, Column, Enum, Integer, String, ForeignKey, DATETIME, DECIMAL, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker, scoped_session

engine = create_engine('mysql://root:ab?sad132FF..@localhost:3306/mydb')
SessionFactory = sessionmaker(bind=engine)
session = scoped_session(SessionFactory)
Base = declarative_base()


class User(Base):
    __tablename__ = "User"

    id = Column('id', Integer, primary_key=True)
    username = Column('username', String(45))
    firstname = Column('firstname', String(45))
    lastname = Column('lastname', String(45))
    email = Column('email', String(45))
    password = Column('password', String(500))
    phone = Column('phone', String(45))
    isAdmin = Column('isAdmin', Boolean)


class Paymethod(Base):
    __tablename__ = "Paymethod"

    id = Column('id', Integer, primary_key=True)
    cardNumber = Column('cardNumber', String(45))
    balance = Column('balance', Integer)
    user_id = Column('user_id', ForeignKey(User.id))


class Transfer(Base):
    __tablename__ = "Transfer"

    transferValue = Column('transferValue', DECIMAL(10, 2))
    datetime = Column('datetime', DATETIME)
    status = Column('status', Enum('failed', 'approved', 'denied'))
    source_paymethod_id = Column("source_paymethod_id", Integer, ForeignKey(Paymethod.id))
    destination_paymethod_id = Column("destination_paymethod_id", Integer, ForeignKey(Paymethod.id))
    id = Column('id', Integer, primary_key=True)

