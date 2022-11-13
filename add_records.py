from models import *

user1 = User(username='user1', firstname='Qwer', lastname='asd',
             email='qwer@gmail.com', password='123', phone='380964515657', userStatus=1)
user2 = User(username='user1', firstname='Qwer', lastname='asd',
             email='qwer@gmail.com', password='123', phone='380964515657', userStatus=1)
session.add(user1)
session.add(user2)
session.commit()

paymethod1 = Paymethod(cardNumber="123456789", balance=1111111111, user_id=1)
paymethod2 = Paymethod(cardNumber="223456789", balance=1011111111, user_id=2)
session.add(paymethod1)
session.add(paymethod2)
session.commit()

transfer1 = Transfer(transferValue=420.69, datetime="2022-01-02", status='approved', source_paymethod_id=1, destination_paymethod_id=2)
transfer2 = Transfer(transferValue=420.69, datetime="2022-01-03", status='approved', source_paymethod_id=1, destination_paymethod_id=2)
session.add(transfer1)
session.add(transfer2)
session.commit()

session.close()