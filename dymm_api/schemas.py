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
    fb_login = {
        "type": "object",
        "properties": {
            "fb_id": {
                "type": "string"
            },
            "email": {
                "type": "string",
                "format": "email"
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
        "required": ["fb_id", "first_name", "last_name", "language_id"],
        "additionalProperties": False
    }
    g_login = {
        "type": "object",
        "properties": {
            "email": {
                "type": "string",
                "format": "email"
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
        "required": ["email", "first_name", "last_name", "language_id"],
        "additionalProperties": False
    }
    avatar_email = {
        "type": "object",
        "properties": {
            "email": {
                "type": "string",
                "format": "email"
            },
            "code": {
                "type": "string",
                "minLength": 6,
                "maxLength": 6
            }
        },
        "required": ["email"],
        "additionalProperties": False
    }
    new_avatar_email = {
        "type": "object",
        "properties": {
            "email": {
                "type": "string",
                "format": "email"
            },
            "code": {
                "type": "string",
                "minLength": 6,
                "maxLength": 6
            },
            "language_id": {
                "type": "integer"
            }
        },
        "required": ["email"],
        "additionalProperties": False
    }
    update_avatar = {
        "type": "object",
        "properties": {
            "avatar_id": {
                "type": "integer"
            },
            "email": {
                "type": "string",
                "format": "email"
            },
            "target": {
                "type": "integer"
            },
            "new_info": {
                "type": "string"
            },
            "old_password": {
                "type": "string"
            }
        },
        "required": ["target", "new_info"],
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
    new_create_log = {
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
            "year_forweekofyear": {
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
    create_bookmark = {
        "type": "object",
        "properties": {
            "avatar_id": {
                "type": "integer"
            },
            "tag_id": {
                "type": "integer"
            },
            "tag_type": {
                "type": "integer"
            }
        },
        "required": ["avatar_id", "tag_id", "tag_type"],
        "additionalProperties": False
    }
    update_log_group = {
        "type": "object",
        "properties": {
            "cond_score": {
                "type": "integer"
            },
            "note_txt": {
                "type": "string"
            }
        },
        "required": [],
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
    mail_conf_link = {
        "type": "object",
        "properties": {
            "avatar_id": {
                "type": "integer"
            }
        },
        "required": ["avatar_id"],
        "additionalProperties": False
    }
    mail_user_opinion = {
        "type": "object",
        "properties": {
            "avatar_id": {
                "type": "integer"
            },
            "tag_id": {
                "type": "integer"
            },
            "opinion": {
                "type": "string"
            },
        },
        "required": ["avatar_id", "tag_id", "opinion"],
        "additionalProperties": False
    }
    receipt_data = {
        "type": "object",
        "properties": {
            "receipt_data": {
                "type": "string"
            }
        },
        "required": ["receipt_data"],
        "additionalProperties": False
    }
