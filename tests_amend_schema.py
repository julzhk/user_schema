import unittest
from flask import Flask
from config import Config
from models import db, Der, Schema as SchemaModel
from app import get_current_schema_record, save_and_validate_der_data, generate_schema


class TestSaveAndValidateDerDataWithNewSchema(unittest.TestCase):

    def setUp(self):
        self.app = Flask(__name__)
        self.app.config.from_object(Config)
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        db.init_app(self.app)
        with self.app.app_context():
            db.create_all()
            schema0 = generate_schema()
            db.session.add(schema0)
            db.session.commit()
            print(f"Schema0 added: {schema0}")
            schema = self.generate_new_schema()
            db.session.add(schema)
            db.session.commit()
            print(f"New schema added: {schema}")


    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def generate_new_schema(self):
        schema = SchemaModel(
            name="PersonSchema",
            data={
                "type": "record",
                "name": "Person",
                "fields": [
                    {"name": "name", "type": "string"},
                    {"name": "superpower", "type": "string"},
                    {"name": "quirk", "type": "string"},
                    {"name": "age", "type": "int"},
                    {"name": "hobbies", "type": {"type": "array", "items": "string"}},
                    {"name": "email", "type": "string"}  # New field added
                ]
            },
            rules="age > 18"
        )
        return schema

    def test_get_current_schema_record(self):
        with self.app.app_context():
            schema = get_current_schema_record()
        assert schema.id == 2

    def test_save_and_validate_der_data_pass(self):
        with self.app.app_context():
            der_data = {
                "name": "John Doe",
                "superpower": "Flying",
                "quirk": "Always happy",
                "age": 25,
                "hobbies": ["Reading", "Swimming", "Running"],
                "email": "john.doe@example.com"  # New field
            }
            der = Der(name="John Doe", data=der_data)
            result = save_and_validate_der_data(der)
            self.assertIsNotNone(result.id)
            self.assertEqual(result.data, der_data)
            self.assertEqual(result.validation_schema, 2)

    def test_save_and_validate_der_data_fail_age(self):
        with self.app.app_context():
            der_data = {
                "name": "Jane Doe",
                "superpower": "Invisibility",
                "quirk": "Always curious",
                "age": 15,  # Age less than 18 should fail
                "hobbies": ["Reading", "Swimming", "Running"],
                "email": "jane.doe@example.com"  # New field
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
                "hobbies": ["Reading", "Swimming", "Running"]
                # Missing email field should fail
            }
            der = Der(name="Jane Doe", data=der_data)
            with self.assertRaises(ValueError):
                save_and_validate_der_data(der)


if __name__ == '__main__':
    unittest.main()