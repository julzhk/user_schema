from flask import Flask

from config import Config
from models import db, Der
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
    """
    Called once to initialize the database with a schema.
    This schema checks if there's a 'Person' record with various mandatory characteristics
    and an age greater than 18.

    See the AVRO documentation for more.
    """
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
    """
    initialize the database
    :return:
    """
    with app.app_context():
        db.create_all()


def generate_der():
    """ we're making a fake person here.
    The person is valid against the schema;
    alter this to see how to handle invalid data.
    The data may have an age field < 18 so may not pass the validation """
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
def init_tables():
    # make sure we're ready;
    # create the tables and add a schema
    db.create_all()
    try:
        get_current_schema_record()
    except ValueError:
        schema = generate_schema()
        db.session.add(schema)

@app.route('/')
def hello_world():
    """ This is a simple route that generates a fake person """
    der = fake_some_data()
    return f'{der.name}, {der.data}'


def fake_some_data():
    """ generate a person, validate it, and save it"""
    der = generate_der()
    validated_against_version: int = validate_der(der.data)
    der.validation_schema = validated_against_version
    db.session.add(der)
    db.session.commit()
    return der


def load_current_schema():
    # Load the schema from the database and return it
    schema_record = get_current_schema_record()
    schema_json = json.dumps(schema_record.data)
    return schema_json


def get_current_schema_record():
    # get the latest schema
    schema_record = SchemaModel.query.order_by(SchemaModel.version.desc()).first()
    if not schema_record:
        raise ValueError("No schema found in the database")
    return schema_record


def validate_der(der_data: dict[str, any]):
    """validate the data against the schema
    and against the rules"""
    validate_against_schema(der_data)
    validate_der_against_rules(der_data)
    return get_current_schema_record().version


def validate_against_schema(der_data):
    """ validates or raises an error """
    schema = load_current_schema()
    schema = Schema(schema)
    parsed_schema = schema.parse()
    validated = parsed_schema.validate(der_data)
    print(validated)


def validate_der_against_rules(der_data: dict[str, any]):
    schema_record: SchemaModel = get_current_schema_record()
    rule = rule_engine.Rule(schema_record.rules)
    if not (rule.matches(der_data)):
        raise ValueError("Data does not meet the rules", der_data)


if __name__ == '__main__':
    init_tables()  # Create tables

    app.run(debug=True)
