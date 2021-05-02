import datetime

import click
import pymongo
from PyInquirer import style_from_dict, Token, prompt
from PyInquirer import Validator, ValidationError
from passlib import hash
from pprint import pprint
from slugify import slugify
import logging

logger = logging.getLogger("ErtisAuth CLI")

membership_doc = {
    "name": "",
    "token_ttl": 0,
    "refresh_token_ttl": 0,
    "max_token_count": 0,
    "sys": {
        "created_at": datetime.datetime.utcnow(),
        "created_by": "ertis_cli"
    }
}

role_doc = {
    "name": "",
    "permissions": [
        "*"
    ],
    "slug": "",
    "membership_id": "",
    "sys": {
        "created_at": datetime.datetime.utcnow(),
        "created_by": "ertis_cli"
    },
    "membership_owner": True
}

user_doc = {
    "status": "active",
    "username": "",
    "password": "",
    "email": "",
    "membership_id": "",
    "sys": {
        "created_at": datetime.datetime.utcnow(),
        "created_by": "ertis_cli"
    },
    "firstname": "",
    "lastname": "",
    "email_verified": False,
    "providers": [],
    "role": "",
    "token": {}
}

style = style_from_dict({
    Token.QuestionMark: '#E91E63 bold',
    Token.Selected: '#673AB7 bold',
    Token.Instruction: '',  # default
    Token.Answer: '#2196f3 bold',
    Token.Question: '',
})

print('Initialize you ertis auth service.')


class ValidateName(Validator):
    def validate(self, document):
        try:
            if document.text != slugify(document.text):
                logger.warning(document.text)
                logger.warning(slugify(document.text))

                raise ValidationError(message=f"value is not valid a slugified name. {document.text}")
        except Exception as e:
            logger.error(f"invalid value. {str(e)}")

            raise ValidationError(
                message="value is not valid a slugified name",
                cursor_position=len(document.text)
            )


class ValidateTtl(Validator):
    def validate(self, document):
        try:
            int(document.text)
        except ValueError:
            raise ValidationError(message='Please enter a number', cursor_position=len(document.text))


questions = [
    {
        'type': 'input',
        'name': 'membership_name',
        'message': 'Enter a membership name:',
        'default': "ertis",
        'filter': lambda val: val.lower(),
        'validate': ValidateName
    },
    {
        'type': 'input',
        'name': 'role_name',
        'default': "admin",
        'message': 'Enter a role name:',
        'filter': lambda val: val.lower(),
        'validate': ValidateName
    },
    {
        'type': 'input',
        'name': 'username',
        'default': "admin",
        'message': 'Enter a username:',
        'filter': lambda val: val.lower(),
        'validate': ValidateName
    },
    {
        'type': 'input',
        'name': 'password',
        'default': "mySecretP@assWord!",
        'message': 'Enter a password:'
    },
    {
        'type': 'input',
        'name': 'token_ttl',
        'default': "60",
        'message': 'Enter token ttl value as a minutes:',
        'validate': ValidateTtl
    },
    {
        'type': 'input',
        'name': 'refresh_token_ttl',
        'default': "120",
        'message': 'Enter refresh token ttl value as a minutes:',
        'validate': ValidateTtl
    },
    {
        'type': 'input',
        'name': 'max_token_count_by_user',
        'default': "120",
        'message': 'Enter max active token count by user:',
        'validate': ValidateTtl
    },
    {
        'type': 'expand',
        'name': 'indexes',
        'message': 'Do you want create indexes on mongodb for ertis auth? [y|N]',
        'choices': [
            {
                'key': 'y',
                'name': 'Create indexes',
                'value': "True"
            },
            {
                'key': 'N',
                'name': 'Cont create indexes',
                'value': "False"
            }
        ]
    }
]


def connect_to_db(conn_str, db):
    client = pymongo.MongoClient(host=conn_str)
    if db:
        return client.get_database(db)

    else:
        return client.get_default_database()


def insert_membership(db, membership_name, token_ttl, refresh_token_ttl, max_token_count):
    membership = membership_doc
    membership["name"] = membership_name
    membership["token_ttl"] = int(token_ttl)
    membership["refresh_token_ttl"] = int(refresh_token_ttl)
    membership["max_token_count"] = int(max_token_count)

    return db.memberships.insert_one(membership)


def insert_role(db, role_name, inserted_id):
    role = role_doc
    role["name"] = role_name
    role["slug"] = role_name
    role["membership_id"] = str(inserted_id)
    db.roles.insert_one(role)


def insert_user(db, username, password, membership_id, role_name):
    user = user_doc
    hashed_password = hash.bcrypt.hash(password)
    email = f"{username}@email.com"

    user["username"] = username
    user["firstname"] = username
    user["lastname"] = username
    user["password"] = hashed_password
    user["email"] = email
    user["membership_id"] = str(membership_id)
    user["role"] = role_name

    db.users.insert_one(user)


def create_indexes(db):
    db.roles.create_index([("slug", 1)])
    db.users.create_index([("username", 1), ("membership_id", 1), ("status", 1)])
    db.active_tokens.create_index([("expire_date", 1)], expireAfterSeconds=0)
    db.revoked_tokens.create_index([("expire_date", 1)], expireAfterSeconds=0)
    db.events.create_index([
        ("document._id", 1),
        ("prior._id", 1),
        ("sys.created_at", 1),
        ("sys.modified_at", 1),
        ("sys.created_by", 1),
        ("sys.modified_by", 1)
    ])


def initialize_db(db, answers):
    membership = insert_membership(
        db, answers["membership_name"], answers["token_ttl"],
        answers["refresh_token_ttl"], answers["max_token_count_by_user"]
    )

    insert_role(db, answers["role_name"], membership.inserted_id)

    insert_user(db, answers["username"], answers["password"], membership.inserted_id, answers["role_name"])

    if answers["indexes"] == "True":
        create_indexes(db)


def rollback_db(db):
    db.memberships.drop()
    db.users.drop()
    db.roles.drop()
    db.active_tokens.drop()
    db.revoked_tokens.drop()
    db.events.drop()


@click.command()
@click.option('--conn_str', '-c')
@click.option('--db', '-d')
def main(conn_str, db):
    db = connect_to_db(conn_str, db)

    answers = prompt(questions, style=style)

    try:
        initialize_db(db, answers)
    except Exception as e:
        logger.error(f"Error occurred. Db rollback... Detail: {str(e)}")
        rollback_db(db)

    pprint(answers)


if __name__ == '__main__':
    main()
