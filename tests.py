import unittest
from flask import Flask
from config import Config
from models import db, Der, Schema as SchemaModel
from app import save_and_validate_der_data, generate_schema


class TestSaveAndValidateDerData(unittest.TestCase):

    def setUp(self):
        self.app = Flask(__name__)
        self.app.config.from_object(Config)
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        db.init_app(self.app)
        with self.app.app_context():
            db.create_all()
            schema = generate_schema()
            db.session.add(schema)
            db.session.commit()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_save_and_validate_der_data_pass(self):
        with self.app.app_context():
            der_data = {
                "name": "John Doe",
                "superpower": "Flying",
                "quirk": "Always happy",
                "age": 25,
                "hobbies": ["Reading", "Swimming", "Running"]
            }
            der = Der(name="John Doe", data=der_data)
            result = save_and_validate_der_data(der)
            self.assertIsNotNone(result.id)
            self.assertEqual(result.data, der_data)

    def test_save_and_validate_der_data_fail_age(self):
        with self.app.app_context():
            der_data = {
                "name": "Jane Doe",
                "superpower": "Invisibility",
                "quirk": "Always curious",
                "age": 15,  # Age less than 18 should fail
                "hobbies": ["Reading", "Swimming", "Running"]
            }
            der = Der(name="Jane Doe", data=der_data)
            with self.assertRaises(ValueError):
                save_and_validate_der_data(der)

    def test_save_and_validate_der_data_fail_missing_field(self):
        with self.app.app_context():
            der_data = {
                "name": "Jane Doe",
                "superpower": "Invisibility",
                "quirk": "Always curious",
                "age": 20,
                # Missing hobbies field should fail
            }
            der = Der(name="Jane Doe", data=der_data)
            with self.assertRaises(ValueError):
                save_and_validate_der_data(der)


if __name__ == '__main__':
    unittest.main()
