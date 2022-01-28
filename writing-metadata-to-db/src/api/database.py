import os
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, String, MetaData


# SQLALCHEMY_DATABASE_URL = os.getenv('DATABASE_URL')
SQLALCHEMY_DATABASE_URL = 'postgresql://root:12345678@127.0.0.1:5432/test_db'

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)


metadata = MetaData()

def get_table_obj(table, columns):
    return Table(
        table, metadata, *columns
    )

    


