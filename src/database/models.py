import os
import json
from datetime import datetime
from peewee import (
    MySQLDatabase, Model, CharField, DateTimeField,
    ForeignKeyField, TextField, BooleanField, IntegerField
)
from src.config.config import DB_ADDR, DB_NAME, DB_PASS, DB_USER
from src.utils.random_string import generate_random_string

DB_MARKER_FILE = os.path.join("src", "config", ".db")

database = MySQLDatabase(
    host=DB_ADDR,
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASS,
    charset='utf8mb4'
)


class BaseModel(Model):
    class Meta:
        database = database
        table_settings = [
            "DEFAULT CHARSET=utf8mb4",
            "COLLATE utf8mb4_general_ci"
        ]


class Members(BaseModel):
    id = CharField(max_length=32, primary_key=True)
    chat_id = CharField(max_length=32, unique=True, null=False)
    username = CharField(max_length=32, default='')
    first_name = CharField(max_length=32, default='')
    last_name = CharField(max_length=32, default='')
    is_here = CharField(max_length=255, default='')
    join_time = DateTimeField(default=datetime.now)
    accessibility = CharField(max_length=32, default='USER')

    @classmethod
    def insert_new_member(cls, chat_id):
        new_id = generate_random_string(
            length=6,
            include_lower=True,
            include_upper=True,
            include_digits=True,
            include_special=False,
            prefix='ME'
        )
        member = cls.create(
            id=new_id,
            chat_id=chat_id,
            join_time=datetime.now()
        )
        return member

    @classmethod
    def check_member_exists(cls, chat_id):
        member = cls.get_or_none(cls.chat_id == chat_id)
        if member:
            return member
        return cls.insert_new_member(chat_id)

    def update_member_info(self, username=None, first_name=None, last_name=None, is_here=None, accessibility=None):
        if username is not None:
            self.username = username
        if first_name is not None:
            self.first_name = first_name
        if last_name is not None:
            self.last_name = last_name
        if is_here is not None:
            self.is_here = is_here
        if accessibility is not None:
            self.accessibility = accessibility

        self.save()
        return self


class Files(BaseModel):
    id = CharField(max_length=32, primary_key=True)
    creator_member_id = ForeignKeyField(Members, backref='files')
    file_ids = TextField(default="[]")
    is_vip = BooleanField(default=False)
    download_count = IntegerField(default=0)
    created_time = DateTimeField(default=datetime.now)
    status = CharField(max_length=32, default='103')

    def set_file_ids(self, ids: list):
        self.file_ids = json.dumps(ids)

    def get_file_ids(self) -> list:
        try:
            return json.loads(self.file_ids)
        except:
            return []


def init_database():
    if not os.path.exists(DB_MARKER_FILE):
        with database:
            database.create_tables([Members, Files], safe=True)
        open(DB_MARKER_FILE, "w").close()
    else:
        with database:
            database.create_tables([Members, Files], safe=True)
