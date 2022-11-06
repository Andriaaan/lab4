from sqlalchemy import create_engine, Column, Enum, Integer, String, ForeignKey, DATE, DECIMAL
from sqlalchemy.orm import declarative_base, sessionmaker, scoped_session

engine = create_engine('mysql://root:123456@localhost:3306/ppdb')
SessionFactory = sessionmaker(bind=engine)
Session = scoped_session(SessionFactory)
Base = declarative_base()


class User(Base):
    __tablename__ = "User"

    id = Column('id', Integer, primary_key=True)
    username = Column('username', String(45))
    firstname = Column('firstname', String(45))
    lastname = Column('lastname', String(45))
    email = Column('email', String(45))
    password = Column('password', String(45))
    phone = Column('phone', String(45))
    userStatus = Column('userStatus', Integer)


class Paymethod(Base):
    __tablename__ = "Paymethod"

    id = Column('id', Integer, primary_key=True)
    cardNumber = Column('cardNumber', String(45))
    balance = Column('balance', Integer)
    User_id = Column('User_id', ForeignKey(User.id))


class Transfer(Base):
    __tablename__ = "Transfer"

    TransferValue = Column('TransferValue', DECIMAL(10, 2))
    datetime = Column('datetime', DATE)
    Status = Column('Status', Enum('not enough founds', 'approved', 'denied'))
    id = Column('id', Integer, primary_key=True)


class User_has_Transfer(Base):
    __tablename__ = "User_has_Transfer"

    Who_User_id = Column('Who_User_id', ForeignKey(User.id))
    Transfer_id = Column('id', Integer, ForeignKey(Transfer.id), primary_key=True)
    Whom_User_id = Column('Whom_User_id', ForeignKey(User.id))
