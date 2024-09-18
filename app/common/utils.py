import psycopg2
from sdk.dto.credentials import BasicCredential
from sqlalchemy.ext.asyncio import create_async_engine as sqlalchemy_create_async_engine
from urllib.parse import quote_plus


def connect_to_db(db_params: BasicCredential):
    return psycopg2.connect(**db_params.model_dump())


def create_async_engine(db_params: BasicCredential):
    # Construct your connection string using the credentials
    encoded_password = quote_plus(db_params.password)
    connection_string = f"postgresql+asyncpg://{db_params.user}:{encoded_password}@{db_params.host}:{db_params.port}/{db_params.database}"
    return sqlalchemy_create_async_engine(connection_string)
