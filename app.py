from flask import Flask

from avro_schema import schema
from config import Config
from models import db, Der, Schema
from models import Schema as SchemaModel
from faker import Faker
import json
from avro_validator.schema import Schema
import rule_engine

faker = Faker()

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)


def generate_schema():
    schema = SchemaModel(
        name="Person",
        rules="age > 18",
        version=1,
        data={
            "type": "record",
            "name": "Person",
            "fields": [
                {"name": "name", "type": "string"},
                {"name": "superpower", "type": "string"},
                {"name": "quirk", "type": "string"},
                {"name": "age", "type": "int"},
                {"name": "hobbies", "type": {"type": "array", "items": "string"}}
            ]
        }
    )
    return schema


def create_tables():
    with app.app_context():
        db.create_all()


def generate_der():
    der = Der(
        is_deleted=False,
        name=faker.name(),
        data={
            "name": faker.name(),
            "superpower": faker.word(),
            "quirk": faker.word(),
            "age": faker.random_int(min=0, max=100),
            "hobbies": [faker.word() for _ in range(3)]
        })
    return der


@app.before_request
def create_tables():
    db.create_all()


@app.route('/')
def hello_world():
    der = fake_some_data()
    return f'{der.name}, {der.data}'


@app.route('/add_der/')
def fake_some_data():
    # schema = generate_schema()
    # db.session.add(schema)
    der = generate_der()
    validated_against_version: int = validate_der_against_schema(der.data)
    der.validation_schema = validated_against_version
    db.session.add(der)
    db.session.commit()
    return der


def load_current_schema():
    schema_record = get_current_schema_record()
    # Load the schema from the database and return it
    schema_json = json.dumps(schema_record.data)
    return schema_json, schema_record.version


def get_current_schema_record():
    schema_record = SchemaModel.query.order_by(SchemaModel.version.desc()).first()
    if not schema_record:
        raise ValueError("No schema found in the database")
    return schema_record


def validate_der_against_schema(der_data: dict[str, any]):
    schema, schema_version = load_current_schema()
    schema = Schema(schema)
    parsed_schema = schema.parse()
    validated = parsed_schema.validate(der_data)
    print(validated)
    validate_der_against_rules(der_data)
    return schema_version


def validate_der_against_rules(der_data: dict[str, any]):
    schema_record: SchemaModel = get_current_schema_record()
    rule = rule_engine.Rule(schema_record.rules)
    if not (rule.matches(der_data)):
        raise ValueError("Data does not meet the rules", der_data)


if __name__ == '__main__':
    create_tables()  # Create tables

    app.run(debug=True)
