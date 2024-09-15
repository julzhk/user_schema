import avro.schema
import json

# Define the Avro schema
schema_json = {
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

# Parse the schema
schema = avro.schema.parse(json.dumps(schema_json))

# Print the schema
print(schema)