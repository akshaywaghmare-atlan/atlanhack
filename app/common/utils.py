

import psycopg2
from app.models.credentials import CredentialConfig


def connect_to_db(db_params: CredentialConfig):
    return psycopg2.connect(**db_params.model_dump())