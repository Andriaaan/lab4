from models import *

session = Session

user1 = User(id=1, username='user1', firstname='Qwer', lastname='asd',
             email='qwer@gmail.com', password='123', phone='380964515657', userStatus=1)
user2 = User(id=2, username='user1', firstname='Qwer', lastname='asd',
             email='qwer@gmail.com', password='123', phone='380964515657', userStatus=1)
session.add(user1)
session.add(user2)
session.commit()

paymethod1 = Paymethod(id=1, cardNumber="123456789", balance=1111111111, User_id=1)
paymethod2 = Paymethod(id=2, cardNumber="223456789", balance=1011111111, User_id=2)
session.add(paymethod1)
session.add(paymethod2)
session.commit()

transfer1 = Transfer(TransferValue=420.69, datetime="2022-01-02", Status='approved', id=1)
transfer2 = Transfer(TransferValue=420.69, datetime="2022-01-03", Status='approved', id=2)
session.add(transfer1)
session.add(transfer2)
session.commit()

User_has_Transfer1 = User_has_Transfer(Who_User_id=1, Transfer_id=1, Whom_User_id=2)
User_has_Transfer2 = User_has_Transfer(Who_User_id=2, Transfer_id=2, Whom_User_id=1)
session.add(transfer1)
session.add(transfer2)
session.commit()

session.close()