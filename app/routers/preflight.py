from fastapi import APIRouter, HTTPException
from app.common.utils import connect_to_db
from app.const import TEST_AUTHENTICATION_SQL, FILTER_METADATA_SQL
from app.models.credentials import CredentialPayload
import psycopg2

router = APIRouter(
    prefix="/preflight",
    tags=["preflight"],
    responses={404: {"description": "Not found"}},
)

@router.post("/test-authentication")
async def test_authentication(payload: CredentialPayload):
    conn = None
    try:
        credentials = payload.get_credential_config()
        conn = connect_to_db(credentials)
        cursor = conn.cursor()
        cursor.execute(TEST_AUTHENTICATION_SQL)
        row = cursor.fetchone()

        return {
            "success": True,
            "results": row[0] if row else None
        }
    except psycopg2.Error as e:
        raise HTTPException(status_code=400, detail={
            "success": False,
            "error": "Unable to connect to the database. Please check your credentials and try again.",
            "message": str(e),
            "errorCode": "DATABASE_CONNECTION_ERROR"
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail={
            "success": False,
            "error": "An unexpected error occurred during authentication test.",
            "message": str(e),
            "errorCode": "INTERNAL_SERVER_ERROR"
        })
    finally:
        if conn:
            conn.close()


@router.post("/filter-metadata")
async def filter_metadata(payload: CredentialPayload):
    conn = None
    try:
        credentials = payload.get_credential_config()
        conn = connect_to_db(credentials)
        cursor = conn.cursor()
        cursor.execute(FILTER_METADATA_SQL)

        result = {}
        while True:
            rows = cursor.fetchmany(1000)  # Fetch 1000 rows at a time
            if not rows:
                break
            for schema_name, catalog_name in rows:
                if catalog_name not in result:
                    result[catalog_name] = []
                result[catalog_name].append(schema_name)

        return {
            "success": True,
            "results": result
        }
    except psycopg2.Error as e:
        raise HTTPException(status_code=400, detail={
            "success": False,
            "error": "Unable to execute the query. Please check your database connection.",
            "message": str(e),
            "errorCode": "DATABASE_QUERY_ERROR"
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail={
            "success": False,
            "error": "An unexpected error occurred while filtering metadata.",
            "message": str(e),
            "errorCode": "INTERNAL_SERVER_ERROR"
        })
    finally:
        if conn:
            conn.close()
