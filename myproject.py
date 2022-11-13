from flask import Flask, request, jsonify, json
from sqlalchemy import exc
from marshmallow import validate, ValidationError
import db_utils
from db_utils import *
from models import *
from db_utils import *
from schemas import *

app = Flask(__name__)

@app.route("/api/v1/user", methods=['POST'])
def create_user():
    try:
        user_data = UserSchema().load(request.json)
        user = db_utils.create_entry(User, **user_data)
        return jsonify(UserSchema().dump(user))
    except ValidationError as err:
        return str(err), 400

@app.route("/api/v1/user/<user_id>", methods=['PUT'])
def update_user(user_id):
    try:
        user_data = UserSchema().load(request.json)
        user = db_utils.get_entry_byid(User, user_id)
        db_utils.update_entry(user, **user_data)
        return "User updated", 200
    except exc.NoResultFound:
        return "User not found", 404
    except ValidationError as err:
        return str(err), 400


@app.route("/api/v1/user/<user_id>", methods=['DELETE'])
def delete_user(user_id):
    if session.query(Users).filter_by(user_id=user_id).count() == 0:
        return  "User not found", 404
    session.query(User).filter_by(id=user_id).delete()
    session.query(Paymethod).filter_by(user_id=user_id).delete()
    session.commit()
    return "User deleted", 200

@app.route("/api/v1/user/<user_id>/", methods=['GET'])
def user(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return jsonify(UserSchema().dump(user)), 200
    
@app.route("/api/v1/user/login")
def user_login():
    return "<h1 style='color:red'>login!</h1>"

@app.route("/api/v1/user/logout")
def user_logout():
    return "<h1 style='color:red'>logout!</h1>"

@app.route("/api/v1/user/<user_id>/history", methods=['GET'])
def get_user_history(user_id):
    if not is_user_exist(user_id):
        return "User not found", 404

    if session.query(Transfer).filter_by(source_paymethod_id=user_id).count() > 0:
        history = session.query(Transfer).filter_by(source_paymethod_id=user_id).all()
        return jsonify(TransferSchema().dump(history, many=True)), 200
    else:
        return "No content", 204


@app.route("/api/v1/user/<user_id>/paymethods", methods=['GET', 'POST'])
def user_paymethods(user_id):
    if not is_user_exist(user_id):
        return "User not found", 404

    if request.method == 'GET':
        if session.query(Paymethod).filter_by(user_id=user_id).count() > 0:
            paymethods = session.query(Paymethod).filter_by(user_id=user_id).all()
            return jsonify(PaymethodReturnSchema().dump(paymethods, many=True)), 200
        else:
            return "No content", 204

    elif request.method == 'POST':
        cardnumber = request.json.get('cardNumber')
        balance = request.json.get('balance')
        if is_cardnumber_exist(cardnumber):
            return "Paymethod with this cardnumber currently exists", 409
        try:
            if cardnumber is None or not cardnumber.isdigit():
                return "Wrong cardnumber", 400
            if balance is None or balance <0:
                return "Wrong balance", 400
            paymetod = Paymethod(balance=balance, cardNumber=cardnumber, user_id=user_id)
            session.add(paymetod)
            session.commit()
            return jsonify(PaymethodReturnSchema().dump(paymetod)),200
        except ValidationError as err:
            return str(err), 400
        return 'POST'

@app.route("/api/v1/user/<user_id>/paymethods/<paymethod_id>", methods=['PUT', 'DELETE', 'GET'])
def user_paymethods_edit(user_id,paymethod_id):
    if not is_user_exist(user_id):
        return "User not found", 404

    if not is_user_paymethod_exist(paymethod_id,user_id):
        return "Paymethod not found", 404

    if request.method == 'GET':
        paymethod = db_utils.get_entry_byid(Paymethod, paymethod_id)
        return jsonify(PaymethodReturnSchema().dump(paymethod)),200

    if  request.method == 'PUT':
        try:
            paymethod_data = PaymethodEditSchema().load(request.json)
            if not validate_paymethod(paymethod_data.get('cardNumber'), paymethod_data.get('balance'), paymethod_data.get('user_id')):
                return "Conflict", 409
            paymethod = db_utils.get_entry_byid(Paymethod, paymethod_id)
            db_utils.update_entry(paymethod, **paymethod_data)
            return "Successfuly added", 200
        except ValidationError as err:
            return str(err), 400

    if  request.method == 'DELETE':
        session.query(Paymethod).filter_by(id=paymethod_id).delete()
        session.commit()
        return "Successfuly deleted", 200

@app.route("/api/v1/money-transfer", methods=['POST'])
def create_money_transfer():
    transfer = TransferAddSchema().dump(request.json)
    transfer_value = transfer.get('transferValue')
    source_id = transfer.get('source_paymethod_id')
    dest_id = transfer.get('destination_paymethod_id')
    if source_id is None or dest_id is None or transfer_value is None or transfer_value <= 0:
        return "Wrong inputs", 405

    if not is_paymethod_exist(source_id) or not is_paymethod_exist(dest_id):
        return "Paymethod not found", 404

    if source_id==dest_id:
        return "Paymethods are identical", 405

    source_payment = session.query(Paymethod).filter_by(id=source_id).one()
    dest_payment = session.query(Paymethod).filter_by(id=dest_id).one()

    if source_payment.balance < transfer_value:
        return "Source paymethod don't have enough balance", 403

    source_payment.balance -= transfer_value
    dest_payment.balance += transfer_value

    session.commit()

    return "Scuccessful operation", 200

def is_user_exist(user_id):
    try:
        user = db_utils.get_entry_byid(User, user_id)
        return True
    except exc.NoResultFound:
        return False

def is_user_paymethod_exist(paymethod_id,user_id):
    try:
        if session.query(Paymethod).filter_by(user_id=user_id).filter_by(id=paymethod_id).count() > 0:
            return True
        else:
            return False
    except exc.NoResultFound:
        return False

def is_paymethod_exist(paymethod_id):
    try:
        if session.query(Paymethod).filter_by(id=paymethod_id).count() > 0:
            return True
        else:
            return False
    except exc.NoResultFound:
        return False

def is_cardnumber_exist(cardNumber):
    try:
        paymethods = session.query(Paymethod).filter_by(cardNumber=cardNumber).count()
        if paymethods > 0:
            return True
        else:
            return False
    except exc.NoResultFound:
        return False

def validate_paymethod(cardnumber, balance, user_id):
    print(cardnumber)
    print(balance)
    print(user_id)
    print(is_user_exist(user_id) and not is_cardnumber_exist(cardnumber) and balance >= 0)
    return (user_id is None or is_user_exist(user_id)) and (cardnumber is None or not is_cardnumber_exist(cardnumber)) and (balance is None or balance >= 0)


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)



