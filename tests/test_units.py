import unittest
from flask_bcrypt import generate_password_hash
from flask import url_for
from flask_testing import TestCase

from unittest.mock import ANY
import requests
import models
import db_utils
import app
import base64


class BaseTest(TestCase):
    def setUp(self):
        super().setUp()
        self.create_tables()

        self.user_1_data = {
            "username": "testuser",
            "firstname": "andrian",
            "lastname": "vozniy",
            "email": "test@gmail.com",
            "password": "123",
            "phone": "380990124517812"
        }

        self.user_2_data = {
            "username": "test2user",
            "firstname": "adrian",
            "lastname": "vniy",
            "email": "test2@gmail.com",
            "password": generate_password_hash("123"),
            "phone": "380990124517812"
        }

        self.user_1_wrong_data = {
            "username": "testuser",
            "firstname": "andrian",
            "lastname": "vozniy",
            "email": "tescom1312",
            "password": "123",
            "phone": "380990124517812"
        }

        self.user_1_data_get = {
            "username": "testuser",
            "firstname": "andrian",
            "lastname": "vozniy",
            "email": "test@gmail.com",
            "password": generate_password_hash("123"),
            "phone": "380990124517812"
        }

        self.user_1_data_upd = {
            "email": "test1@gmail.com",
            "password": "123",
        }

        self.admin_1_data = {
            "username": "user1",
            "firstname": "admin",
            "lastname": "aaa",
            "email": "admin@gmail.com",
            "password": generate_password_hash("admin"),
            "phone": "380990123517812",
            "isAdmin": 1
        }

        self.user_1_cred = {
            "email": self.user_1_data["email"],
            "password": self.user_1_data["password"]
        }

        self.admin_cred = {
            "email": self.admin_1_data["email"],
            "password": self.admin_1_data["password"]
        }

        self.user1_hash_cred = {
            **self.user_1_data,
            "password": generate_password_hash(self.user_1_data["password"])
        }

        self.admin1_hash_cred = {
            **self.admin_1_data,
            "password": generate_password_hash(self.admin_1_data["password"])
        }

        self.pay_method_data = {
            "cardNumber": "412341561245",
            "balance": 100,
        }

        self.pay_method_data_create = {
            "cardNumber": "412341561245",
            "balance": 100,
            "user_id": 1
        }

        self.pay_method_data2_create = {
            "cardNumber": "4124457192045",
            "balance": 100,
            "user_id": 2
        }

        self.pay_method_data_upd = {
            "cardNumber": "412341561245",
            "balance": 150,
            "user_id": 1
        }

        self.pay_method_wr_data1 = {
            "cardNumber": "asbas",
            "balance": 100
        }

        self.pay_method_wr_data2 = {
            "cardNumber": "1231244",
            "balance": -100
        }

        self.transfer_add = {
            "transferValue": 100,
            "source_paymethod_id": 1,
            "destination_paymethod_id": 2
        }
        self.transfer_add_wr1 = {
            "transferValue": 1000,
            "source_paymethod_id": 1,
            "destination_paymethod_id": 2
        }
        self.transfer_wr2 = {
            "transferValue": 100,
            "source_paymethod_id": 1,
            "destination_paymethod_id": 1
        }




    def create_tables(self):
        models.Base.metadata.drop_all(models.engine)
        models.Base.metadata.create_all(models.engine)

    def tearDown(self):
        self.close_session()

    def close_session(self):
        models.session().close()

    def create_app(self):
        return app.app


class TestAuthUser(BaseTest):

    def test_auth_admin(self):
        db_utils.create_entry(models.User, **self.admin1_hash_cred)

        self.assertEqual(app.verify_password(self.admin_cred["email"], self.admin_cred["password"]),
                         self.admin_cred["email"])
        self.assertEqual(app.get_user_roles(self.admin_cred["email"]), 'admin')

    def test_auth_admin_failed(self):
        db_utils.create_entry(models.User, **self.admin1_hash_cred)

        self.assertEqual(app.verify_password(self.admin_cred["email"],
                                             "Thereisnowayitwouldbethecorrectpassword"), False)
        self.assertEqual(app.get_user_roles(self.user_1_cred["email"]), '')

    def test_auth_user(self):
        db_utils.create_entry(models.User, **self.user1_hash_cred)

        self.assertEqual(app.verify_password(self.user_1_cred["email"], self.user_1_cred["password"]),
                         self.user_1_cred["email"])
        self.assertEqual(app.get_user_roles(self.user_1_cred["email"]), '')

    def test_auth_user_failed(self):
        db_utils.create_entry(models.User, **self.user1_hash_cred)

        self.assertEqual(app.verify_password(self.user_1_cred["email"],
                                             "Thereisnowayitwouldbethecorrectpassword"), False)


class TestGetUser(BaseTest):
    def test_get_by_id(self):
        db_utils.create_entry(models.User, **self.user1_hash_cred)
        db_utils.create_entry(models.User, **self.admin_1_data)

        valid_credentials = base64.b64encode(b"admin@gmail.com:admin").decode("utf-8")

        resp = self.client.get(
            url_for("get_user", user_id=1),
            headers={"Authorization": "Basic " + valid_credentials}
        )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json,
                         {
                             'username': self.user_1_data['username'],
                             'firstname': self.user_1_data['firstname'],
                             'lastname': self.user_1_data['lastname'],
                             'phone': self.user_1_data['phone'],
                         })

    def test_get_user_by_id_auth_error(self):
        db_utils.create_entry(models.User, **self.user_1_data_get)
        valid_credentials = base64.b64encode(b"test@gmail.com:123").decode("utf-8")

        resp = self.client.get(
            url_for("get_user", user_id=1),
            headers={"Authorization": "Basic " + valid_credentials}
        )

        self.assertEqual(resp.status_code, 403)

    def test_get_user_by_id_not_found(self):
        db_utils.create_entry(models.User, **self.user_1_data_get)
        db_utils.create_entry(models.User, **self.admin_1_data)

        valid_credentials = base64.b64encode(b"admin@gmail.com:admin").decode("utf-8")

        resp = self.client.get(
            url_for("get_user", user_id=5),
            headers={"Authorization": "Basic " + valid_credentials}
        )

        self.assertEqual(resp.status_code, 404)
        self.assertEqual(resp.json, {"Error": "User not found"})


class TestPostUser(BaseTest):

    def test_post_user(self):
        resp = self.client.post(url_for("create_user"),
                                json=self.user_1_data)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json, {
            "username": self.user_1_data["username"],
            "firstname": self.user_1_data["firstname"],
            "lastname": self.user_1_data["lastname"],
            "phone": self.user_1_data["phone"]
        })

        self.assertTrue(
            models.session().query(models.User).filter_by(email=self.user_1_data["email"]).one()
        )

    def test_post_user_failed(self):
        resp = self.client.post(url_for("create_user"),
                                json=self.user_1_wrong_data)

        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json, {"Error": "Validation error"})


class TestUpdateUser(BaseTest):

    def test_update_user(self):
        db_utils.create_entry(models.User, **self.user_1_data_get)

        valid_credentials = base64.b64encode(b"test@gmail.com:123").decode("utf-8")

        resp = self.client.put(
            url_for("update_user", user_id=1),
            json=self.user_1_data_upd,
            headers={"Authorization": "Basic " + valid_credentials}
        )
        self.assertEqual(resp.status_code, 200)

    def test_update_user_auth_error(self):
        db_utils.create_entry(models.User, **self.user_1_data_get)
        db_utils.create_entry(models.User, **self.admin_1_data)

        valid_credentials = base64.b64encode(b"test@gmail.com:123").decode("utf-8")

        resp = self.client.put(
            url_for("update_user", user_id=2),
            json=self.user_1_data_upd,
            headers={"Authorization": "Basic " + valid_credentials}
        )

        self.assertEqual(resp.status_code, 401)
        self.assertEqual(resp.json, {"Error": "Not enough rights"})

    def test_update_user_valid_failed(self):
        db_utils.create_entry(models.User, **self.user_1_data_get)

        valid_credentials = base64.b64encode(b"test@gmail.com:123").decode("utf-8")

        resp = self.client.put(
            url_for("update_user", user_id=1),
            json=self.user_1_wrong_data,
            headers={"Authorization": "Basic " + valid_credentials}
        )
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json, {"Error": "Validation error"})


class TestUserDelete(BaseTest):

    def test_delete_user(self):
        db_utils.create_entry(models.User, **self.user_1_data_get)

        valid_credentials = base64.b64encode(b"test@gmail.com:123").decode("utf-8")

        resp = self.client.delete(
            url_for("delete_user", user_id=1),
            headers={"Authorization": "Basic " + valid_credentials}
        )
        self.assertEqual(resp.status_code, 200)

    def test_delete_user_auth_error(self):
        db_utils.create_entry(models.User, **self.user_1_data_get)
        db_utils.create_entry(models.User, **self.user_2_data)

        valid_credentials = base64.b64encode(b"test@gmail.com:123").decode("utf-8")

        resp = self.client.delete(
            url_for("delete_user", user_id=2),
            headers={"Authorization": "Basic " + valid_credentials}
        )
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(resp.json, {"Error": "Not enough rights"})


class TestPostPayMethod(BaseTest):
    def test_add_method(self):
        db_utils.create_entry(models.User, **self.user_1_data_get)
        db_utils.create_entry(models.User, **self.admin_1_data)

        valid_credentials = base64.b64encode(b"admin@gmail.com:admin").decode("utf-8")

        resp = self.client.post(url_for("user_paymethods", user_id=1),
                                json=self.pay_method_data,
                                headers={"Authorization": "Basic " + valid_credentials})
        self.assertEqual(resp.status_code, 200)

        resp = self.client.post(url_for("user_paymethods", user_id=1),
                                json=self.pay_method_data,
                                headers={"Authorization": "Basic " + valid_credentials})
        self.assertEqual(resp.status_code, 409)
        self.assertEqual(resp.json, {"Error": "Paymethod with this cardnumber currently exists"})

    def test_add_wrong_method(self):
        db_utils.create_entry(models.User, **self.user_1_data_get)
        db_utils.create_entry(models.User, **self.admin_1_data)
        valid_credentials = base64.b64encode(b"admin@gmail.com:admin").decode("utf-8")

        resp = self.client.post(url_for("user_paymethods", user_id=1),
                                json=self.pay_method_wr_data1,
                                headers={"Authorization": "Basic " + valid_credentials})
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json, {"Error": "Wrong card number"})

        resp = self.client.post(url_for("user_paymethods", user_id=1),
                                json=self.pay_method_wr_data2,
                                headers={"Authorization": "Basic " + valid_credentials})
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json, {"Error": "Wrong balance"})

        resp = self.client.post(url_for("user_paymethods", user_id=10),
                                json=self.pay_method_data,
                                headers={"Authorization": "Basic " + valid_credentials})
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(resp.json, {"Error": "User not found"})


class TestGetPayMethod(BaseTest):

    def test_get_method(self):
        db_utils.create_entry(models.User, **self.user_1_data_get)
        db_utils.create_entry(models.User, **self.admin_1_data)
        db_utils.create_entry(models.Paymethod, **self.pay_method_data_create)

        valid_credentials = base64.b64encode(b"admin@gmail.com:admin").decode("utf-8")

        resp = self.client.get(url_for("user_paymethods", user_id=1, paymethod_id=1),
                               headers={"Authorization": "Basic " + valid_credentials})
        self.assertEqual(resp.status_code, 200)

        valid_credentials = base64.b64encode(b"test@gmail.com:123").decode("utf-8")

        resp = self.client.get(url_for("user_paymethods_edit", user_id=1, paymethod_id=20),
                               headers={"Authorization": "Basic " + valid_credentials})
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(resp.json, {"Error": "Paymethod not found"})

    def test_get_method_auth_failed(self):
        db_utils.create_entry(models.User, **self.user_1_data_get)
        db_utils.create_entry(models.User, **self.admin_1_data)
        db_utils.create_entry(models.Paymethod, **self.pay_method_data_create)

        valid_credentials = base64.b64encode(b"t@gmail.com:1").decode("utf-8")

        resp = self.client.get(url_for("user_paymethods", user_id=1),
                               headers={"Authorization": "Basic " + valid_credentials})
        self.assertEqual(resp.status_code, 401)


class TestUpdatePayMethod(BaseTest):
    def test_update_method(self):
        db_utils.create_entry(models.User, **self.user_1_data_get)
        db_utils.create_entry(models.Paymethod, **self.pay_method_data_create)

        valid_credentials = base64.b64encode(b"test@gmail.com:123").decode("utf-8")

        resp = self.client.put(
            url_for("user_paymethods_edit", user_id=1, paymethod_id=1),
            json=self.pay_method_data_upd,
            headers={"Authorization": "Basic " + valid_credentials}
        )
        self.assertEqual(resp.status_code, 200)

        resp = self.client.put(
            url_for("user_paymethods_edit", user_id=1, paymethod_id=1),
            json=self.pay_method_wr_data1,
            headers={"Authorization": "Basic " + valid_credentials}
        )
        self.assertEqual(resp.status_code, 409)
        self.assertEqual(resp.json, {"Error": "Conflict"})


class TestDeletePayMethod(BaseTest):
    def test_delete(self):
        db_utils.create_entry(models.User, **self.user_1_data_get)
        db_utils.create_entry(models.Paymethod, **self.pay_method_data_create)

        valid_credentials = base64.b64encode(b"test@gmail.com:123").decode("utf-8")

        resp = self.client.delete(
            url_for("user_paymethods_edit", user_id=1, paymethod_id=1),
            headers={"Authorization": "Basic " + valid_credentials}
        )
        self.assertEqual(resp.status_code, 200)

    def test_delete_failed(self):
        db_utils.create_entry(models.User, **self.user_1_data_get)
        db_utils.create_entry(models.Paymethod, **self.pay_method_data_create)

        valid_credentials = base64.b64encode(b"test@gmail.com:123").decode("utf-8")

        resp = self.client.delete(
            url_for("user_paymethods_edit", user_id=1, paymethod_id=2),
            headers={"Authorization": "Basic " + valid_credentials}
        )
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(resp.json, {"Error": "Paymethod not found"})


class TestTransfer(BaseTest):
    def test_create_transfer(self):
        db_utils.create_entry(models.User, **self.user_1_data_get)
        db_utils.create_entry(models.User, **self.user_2_data)
        db_utils.create_entry(models.Paymethod, **self.pay_method_data_create)
        db_utils.create_entry(models.Paymethod, **self.pay_method_data2_create)

        valid_credentials = base64.b64encode(b"test@gmail.com:123").decode("utf-8")

        resp = self.client.post(url_for("create_money_transfer", user_id=1),
                                json=self.transfer_add,
                                headers={"Authorization": "Basic " + valid_credentials})
        self.assertEqual(resp.status_code, 200)

    def test_create_transfer_failed(self):
        db_utils.create_entry(models.User, **self.user_1_data_get)
        db_utils.create_entry(models.User, **self.user_2_data)
        db_utils.create_entry(models.Paymethod, **self.pay_method_data_create)
        db_utils.create_entry(models.Paymethod, **self.pay_method_data2_create)

        valid_credentials = base64.b64encode(b"test@gmail.com:123").decode("utf-8")

        resp = self.client.post(url_for("create_money_transfer", user_id=1),
                                json=self.transfer_add_wr1,
                                headers={"Authorization": "Basic " + valid_credentials})
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(resp.json, {"Error": "Source paymethod don't have enough balance"})

        resp = self.client.post(url_for("create_money_transfer", user_id=1),
                                json=self.transfer_wr2,
                                headers={"Authorization": "Basic " + valid_credentials})
        self.assertEqual(resp.status_code, 405)
        self.assertEqual(resp.json, {"Error": "Paymethods are identical"})
