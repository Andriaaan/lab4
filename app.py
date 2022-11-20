from flask import Flask, request, jsonify, json, make_response
from flask_bcrypt import check_password_hash
from sqlalchemy import exc
from marshmallow import validate, ValidationError
import db_utils
from db_utils import *
from models import *
from db_utils import *
from schemas import *
from datetime import datetime
from flask_httpauth import HTTPBasicAuth

app = Flask(__name__)
auth = HTTPBasicAuth()

# basic authorization ------------------------------------------------------------------------------------------------------------------------------------------------------

@auth.verify_password
def verify_password(username, password):
    try:
        user = session.query(User).filter_by(email=username).one()
        if check_password_hash(user.password, password):
            return username
    except exc.NoResultFound:
        return False


@auth.get_user_roles
def get_user_roles(user):
    try:
        user_db = session.query(User).filter_by(email=user).one()
        if user_db.isAdmin:
            return 'admin'
        else:
            return ''
    except exc.NoResultFound:
        return ''


# USER ------------------------------------------------------------------------------------------------------------------------------------------------------


@app.route("/user", methods=['POST'])
def create_user():
    try:
        user_data = UserRegister().load(request.json)
        user = db_utils.create_entry(User, **user_data)
        return jsonify(UserInfo().dump(user))
    except ValidationError as err:
        return str(err), 400


@app.route("/user/<user_id>/", methods=['GET'])
@auth.login_required(role='admin')
def get_user(user_id):
    try:
        user = db_utils.get_entry_byid(User, user_id)
        return jsonify(UserInfo().dump(user)), 200
    except exc.NoResultFound:
        return "User not found", 404


@app.route("/user/<user_id>", methods=['PUT'])
@auth.login_required()
def update_user(user_id):
    try:
        if not session.query(User).filter(User.id == user_id, User.email == auth.current_user()).count() == 0:
            user_data = UserToUpdate().load(request.json)
            user = db_utils.get_entry_byid(User, user_id)
            db_utils.update_entry(user, **user_data)
            return "User updated", 200
        return "Not enough rights", 404
    except exc.NoResultFound:
        return "User not found", 404
    except ValidationError as err:
        return str(err), 400


@app.route("/user/<user_id>", methods=['DELETE'])
@auth.login_required
def delete_user(user_id):
    try:
        if not session.query(User).filter(User.id == user_id, User.email == auth.current_user()).count() == 0:
            session.query(Paymethod).filter(Paymethod.user_id == user_id).delete()
            session.query(User).filter(User.id == user_id).delete()
            session.commit()
            return "User deleted", 200
        return "Not enough rights", 404
    except exc.NoResultFound:
        return "User not found", 404


# HISTORY ------------------------------------------------------------------------------------------------------------------------------------------------------


@app.route("/user/<user_id>/history", methods=['GET'])
@auth.login_required
def get_user_history(user_id):
    if not is_user_exist(user_id):
        return "User not found", 404

    if session.query(User).filter(User.id == user_id, User.email == auth.current_user()).count() == 0:
        return "Not enough rights", 404

    history = session.query(Transfer).join(Paymethod, Paymethod.id == Transfer.source_paymethod_id).filter(
        Paymethod.user_id == user_id).all()

    if session.query(Transfer).join(Paymethod, Paymethod.id == Transfer.source_paymethod_id).filter(
            Paymethod.user_id == user_id).count() > 0:
        return jsonify(TransferSchema().dump(history, many=True)), 200
    else:
        return "No content", 204


# PAYMETHOD Admin ------------------------------------------------------------------------------------------------------------------------------------------------------


@app.route("/user/<user_id>/paymethods", methods=['GET', 'POST'])
@auth.login_required(role='admin')
def user_paymethods(user_id):
    if session.query(User).filter(User.id == user_id, User.email == auth.current_user()).count() == 0:
        return "Not enough rights", 404
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
            if balance is None or balance < 0:
                return "Wrong balance", 400
            paymetod = Paymethod(balance=balance, cardNumber=cardnumber, user_id=user_id)
            session.add(paymetod)
            session.commit()
            return jsonify(PaymethodReturnSchema().dump(paymetod)), 200
        except ValidationError as err:
            return str(err), 400
        return 'POST'


# PAYMETHOD User ------------------------------------------------------------------------------------------------------------------------------------------------------


@app.route("/user/<user_id>/paymethods/<paymethod_id>", methods=['PUT', 'DELETE', 'GET'])
@auth.login_required
def user_paymethods_edit(user_id, paymethod_id):
    if session.query(User).filter(User.id == user_id, User.email == auth.current_user()).count() == 0:
        return "Not enough rights", 404
    if not is_user_exist(user_id):
        return "User not found", 404

    if not is_user_paymethod_exist(paymethod_id, user_id):
        return "Paymethod not found", 404

    if request.method == 'GET':
        paymethod = db_utils.get_entry_byid(Paymethod, paymethod_id)
        return jsonify(PaymethodReturnSchema().dump(paymethod)), 200

    if request.method == 'PUT':
        try:
            paymethod_data = PaymethodEditSchema().load(request.json)
            if not validate_paymethod(paymethod_data.get('cardNumber'), paymethod_data.get('balance'),
                                      paymethod_data.get('user_id')):
                return "Conflict", 409
            paymethod = db_utils.get_entry_byid(Paymethod, paymethod_id)
            db_utils.update_entry(paymethod, **paymethod_data)
            return "Successfuly added", 200
        except ValidationError as err:
            return str(err), 400

    if request.method == 'DELETE':
        session.query(Paymethod).filter_by(id=paymethod_id).delete()
        session.commit()
        return "Successfuly deleted", 200


# TRANSFER ------------------------------------------------------------------------------------------------------------------------------------------------------


@app.route("/user/<user_id>/money-transfer", methods=['POST'])
@auth.login_required
def create_money_transfer(user_id):
    if session.query(User).filter(User.id == user_id, User.email == auth.current_user()).count() == 0:
        return "Not enough rights", 404

    transfer_s = TransferAddSchema().dump(request.json)
    transfer_value = transfer_s.get('transferValue')
    source_id = transfer_s.get('source_paymethod_id')
    dest_id = transfer_s.get('destination_paymethod_id')

    if session.query(Paymethod).filter(Paymethod.id == source_id, Paymethod.user_id == user_id).count() == 0:
        return "paymethod not found for this user", 404

    if source_id is None or dest_id is None or transfer_value is None or transfer_value <= 0:
        return "Wrong inputs", 405

    if not is_paymethod_exist(source_id) or not is_paymethod_exist(dest_id):
        return "Paymethod not found", 404

    if source_id == dest_id:
        return "Paymethods are identical", 405

    source_payment = session.query(Paymethod).filter_by(id=source_id).one()
    dest_payment = session.query(Paymethod).filter_by(id=dest_id).one()

    if source_payment.balance < transfer_value:
        return "Source paymethod don't have enough balance", 403

    source_payment.balance -= transfer_value
    dest_payment.balance += transfer_value

    transfer = Transfer(transferValue=transfer_value, datetime=datetime.today(), status='approved',
                        source_paymethod_id=source_id, destination_paymethod_id=dest_id)
    session.add(transfer)
    session.commit()

    return "Scuccessful operation", 200


# verification functions ------------------------------------------------------------------------------------------------------------------------------------------------------


def is_user_exist(user_id):
    try:
        db_utils.get_entry_byid(User, user_id)
        return True
    except exc.NoResultFound:
        return False


def is_user_paymethod_exist(paymethod_id, user_id):
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
    return (user_id is None or is_user_exist(user_id)) and (
            cardnumber is None or not is_cardnumber_exist(cardnumber)) and (balance is None or balance >= 0)


if __name__ == "__main__":
    app.run()
