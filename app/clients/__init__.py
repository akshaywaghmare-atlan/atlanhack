from application_sdk.clients.sql import BaseSQLClient

class SQLClient(BaseSQLClient):
    """
    This client handles connection string generation based on authentication
    type and manages database connectivity using SQLAlchemy with Presto.
    """

    DB_CONFIG = {
        "template": "presto://{username}@{host}:{port}/{catalog}/{schema}",
        "required": ["username", "host", "port", "catalog", "schema"],
        "defaults": {
            "host": "13.127.207.43",  # Default Presto server
            "port": "8080",           # Default Presto port
            "username": "admin",      # Default Presto username
            "catalog": "system",
            "schema": "information_schema"
        },  
        "autofill": {
            "name": "Default Presto Server",
            "description": "Connect to the default Presto server at 13.127.207.43:8080",
            "values": {
                "host": "13.127.207.43",
                "port": "8080",
                "username": "admin",
                "catalog": "system",
                "schema": "information_schema"
            }
        }
    }

    def get_sqlalchemy_connection_string(self) -> str:
        """
        Generate SQLAlchemy connection string for Presto.
        """
        if not self.credentials:
            raise KeyError("Credentials not set")

        username = self.credentials.get("username")
        host = self.credentials.get("host")
        port = self.credentials.get("port")
        extra = self.credentials.get("extra", {})
        
        catalog = extra.get("catalog", self.DB_CONFIG["defaults"]["catalog"])
        schema = extra.get("schema", self.DB_CONFIG["defaults"]["schema"])

        required_fields = ["username", "host", "port", "catalog", "schema"]
        for field in required_fields:
            if not locals().get(field):
                raise KeyError(f"Required field {field} not found in credentials")

        return self.DB_CONFIG["template"].format(
            username=username,
            host=host,
            port=port,
            catalog=catalog,
            schema=schema
        )

    @classmethod
    def get_autofill_options(cls):
        """
        Return autofill options for the connection form.
        """
        return [cls.DB_CONFIG["autofill"]]
