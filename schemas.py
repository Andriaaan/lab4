from marshmallow import validate, Schema, fields, ValidationError
from flask_bcrypt import generate_password_hash

from models import *


def validate_email(emeil1):
    if not (session.query(User).filter(User.email == emeil1).count() == 0):
        raise ValidationError("Email exists")


def validate_username(username):
    if not (session.query(User).filter(User.username == username).count() == 0):
        raise ValidationError("Username exists")


class UserInfo(Schema):
    username = fields.String()
    firstname = fields.String()
    lastname = fields.String()
    phone = fields.Integer()


class UserRegister(Schema):
    username = fields.String()
    firstname = fields.String()
    lastname = fields.String()
    email = fields.Email(validate=validate_email)
    password = fields.Function(
        deserialize=lambda obj: generate_password_hash(obj), load_only=True
    )
    phone = fields.Integer()


class UserToUpdate(Schema):
    email = fields.Email(validate=validate_email)
    password = fields.Function(
        deserialize=lambda obj: generate_password_hash(obj), load_only=True
    )


class PaymethodSchema(Schema):
    cardNumber = fields.String()
    balance = fields.Integer()
    user_id = fields.Integer()


class PaymethodReturnSchema(Schema):
    id = fields.Integer()
    cardNumber = fields.String()
    balance = fields.Integer()
    user_id = fields.Integer()


class PaymethodAddSchema(Schema):
    cardNumber = fields.String()
    balance = fields.Integer()


class PaymethodEditSchema(Schema):
    cardNumber = fields.String()
    balance = fields.Integer()
    user_id = fields.Integer()


class TransferSchema(Schema):
    transferValue = fields.Integer()
    datetime = fields.String()
    status = fields.String()
    source_paymethod_id = fields.Integer()
    destination_paymethod_id = fields.Integer()


class TransferAddSchema(Schema):
    transferValue = fields.Integer()
    source_paymethod_id = fields.Integer()
    destination_paymethod_id = fields.Integer()
