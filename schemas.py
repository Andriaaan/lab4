from marshmallow import validate, Schema, fields
from flask_bcrypt import generate_password_hash

class UserSchema(Schema):
    id = fields.Integer()
    username = fields.String()
    firstname = fields.String()
    lastname = fields.String()
    email = fields.String(validate=validate.Email())
    password = fields.Function(
        deserialize=lambda obj: generate_password_hash(obj), load_only=True
    )
    phone = fields.Integer()

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