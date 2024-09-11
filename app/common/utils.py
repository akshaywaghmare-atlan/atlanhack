import psycopg2
from sdk.dto.credentials import BasicCredential


def connect_to_db(db_params: BasicCredential):
    return psycopg2.connect(**db_params.model_dump())
