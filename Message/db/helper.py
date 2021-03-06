from sqlalchemy import Column
from sqlalchemy import create_engine
from sqlalchemy.sql import expression
from sqlalchemy import desc
from sqlalchemy.types import CHAR
from sqlalchemy.types import Integer
from sqlalchemy.types import Float
from sqlalchemy.types import String
from sqlalchemy.types import VARCHAR
from sqlalchemy.types import TIMESTAMP
from sqlalchemy.types import Text
from sqlalchemy.types import Date
from sqlalchemy.orm.exc import MultipleResultsFound
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.dialects.postgresql import VARCHAR
from sqlalchemy.dialects.postgresql import SMALLINT
from sqlalchemy.dialects.postgresql import INTEGER
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func
from sqlalchemy import or_
from sqlalchemy import not_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql.expression import func
from sqlalchemy.schema import UniqueConstraint
from datetime import datetime
import logging
import traceback
from uuid import uuid4
import random
import string
import hashlib
import uuid
import os
import time

from Message.config import database_config
user = database_config.get('user', 'postgres')
password = database_config.get('password')
port = database_config.get('port', 5432)
host = database_config.get('host', '127.0.0.1')
db_name = database_config.get('db_name')

engine = create_engine('postgresql://{user}:{password}@{host}:{port}/{db_name}'.format(user=user, password=password,
                                                                                       host=host, port=port,
                                                                                       db_name=db_name))

base = declarative_base()
session = sessionmaker(bind=engine)


class Task(base):

    __tablename__ = 'task'

    id = Column(INTEGER, primary_key=True)
    type = Column(VARCHAR)
    status = Column(SMALLINT)
    failed_reason = Column(VARCHAR)
    create_time = Column(TIMESTAMP, server_default=expression.text('CURRENT_TIMESTAMP(3)'))
    update_time = Column(TIMESTAMP, server_default=expression.text('CURRENT_TIMESTAMP(3)'))


if __name__ == '__main__':
    base.metadata.create_all(engine)