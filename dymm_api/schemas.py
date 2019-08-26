from jsonschema import validate
from jsonschema.exceptions import ValidationError, SchemaError


def validate_schema(data, schema):
    try:
        validate(data, schema)
    except ValidationError as error:
        return dict(ok=False, message=error)
    except SchemaError as error:
        return dict(ok=False, message=error)
    return dict(ok=True, data=data)


class Schema:
    auth_avatar = {
        "type": "object",
        "properties": {
            "email": {
                "type": "string",
                "format": "email"
            },
            "password": {
                "type": "string",
                "minLength": 8,
                "maxLength": 40
            },
            "id": {
                "type": "integer"
            }
        },
        "required": ["email", "password"],
        "additionalProperties": False
    }
    create_avatar = {
        "type": "object",
        "properties": {
            "email": {
                "type": "string",
                "format": "email"
            },
            "password": {
                "type": "string",
                "minLength": 8,
                "maxLength": 40
            },
            "first_name": {
                "type": "string",
                "minLength": 1,
                "maxLength": 60
            },
            "last_name": {
                "type": "string",
                "minLength": 1,
                "maxLength": 60
            },
            "language_id": {
                "type": "integer"
            }
        },
        "required": ["email", "password", "first_name", "last_name",
                     "language_id"],
        "additionalProperties": False
    }
    update_avatar = {
        "type": "object",
        "properties": {
            "avatar_id": {
                "type": "integer"
            },
            "target": {
                "type": "integer"
            },
            "new_info": {
                "type": "string"
            }
        },
        "required": ["avatar_id", "target", "new_info"],
        "additionalProperties": False
    }
    create_log = {
        "type": "object",
        "properties": {
            "avatar_id": {
                "type": "integer"
            },
            "tag_id": {
                "type": "integer"
            },
            "year_number": {
                "type": "integer",
                "pattern": "[1-2][0-9][0-9][0-9]"
            },
            "month_number": {
                "type": "integer",
                "pattern": "[1-12]"
            },
            "week_of_year": {
                "type": "integer",
                "pattern": "[1-54]"
            },
            "day_of_year": {
                "type": "integer",
                "pattern": "[1-365]"
            },
            "group_type": {
                "type": "integer",
                "pattern": "[1-4]"
            },
            "x_val": {
                "type": "integer"
            },
            "y_val": {
                "type": "integer"
            },
            "log_group_id": {
                "type": "integer"
            },
            "log_date": {
                "type": "string",
                "minLength": 8,
                "maxLength": 10,
                "pattern": "^\d{4}\-\d{1,2}\-\d{1,2}$"
            }
        },
        "required": ["avatar_id", "tag_id", "year_number", "month_number",
                     "week_of_year", "day_of_year", "group_type", "x_val",
                     "y_val", "log_date"],
        "additionalProperties": False
    }
    create_avatar_cond = {
        "type": "object",
        "properties": {
            "avatar_id": {
                "type": "integer"
            },
            "tag_id": {
                "type": "integer"
            },
            "cond_log_type": {
                "type": "integer"
            },
            "log_date": {
                "type": "string",
                "minLength": 8,
                "maxLength": 10,
                "pattern": "^\d{4}\-\d{1,2}\-\d{1,2}$"
            }
        },
        "required": ["avatar_id", "tag_id", "cond_log_type", "log_date"],
        "additionalProperties": False
    }
    update_cond_score = {
        "type": "object",
        "properties": {
            "cond_score": {
                "type": "integer"
            }
        },
        "required": ["cond_score"],
        "additionalProperties": False
    }
    search_key_word = {
        "type": "object",
        "properties": {
            "key_word": {
                "type": "string"
            }
        },
        "required": ["key_word"],
        "additionalProperties": False
    }
