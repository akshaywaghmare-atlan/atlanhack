from application_sdk.clients.sql import BaseSQLClient


class SQLClient(BaseSQLClient):
    """
    This client handles connection string generation based on authentication
    type and manages database connectivity using SQLAlchemy with Trino.
    """

    DB_CONFIG = {
        "template": "trino://{username}:{password}@{host}:{port}/{catalog}/{schema}?protocol={protocol}&verify={verify}&source={source}&isolation_level={isolation_level}",
        "required": ["username", "password", "host", "port", "catalog", "schema"],
        "defaults": {
            "source": "atlan",
            "isolation_level": "AUTOCOMMIT",
            "protocol": "http",
            "verify": "true",
            "host": "localhost",
            "port": "8081",
            "username": "admin",
            "catalog": "system",
            "schema": "information_schema"
        },
    }

    def get_sqlalchemy_connection_string(self) -> str:
        """
        Generate SQLAlchemy connection string for Trino.
        """
        if not self.credentials:
            raise KeyError("Credentials not set")

        # Get required fields
        username = self.credentials.get("username")
        password = self.credentials.get("password", "")
        host = self.credentials.get("host")
        port = self.credentials.get("port")
        extra = self.credentials.get("extra", {})
        
        # Get catalog and schema from extra
        catalog = extra.get("catalog", self.DB_CONFIG["defaults"]["catalog"])
        schema = extra.get("schema", self.DB_CONFIG["defaults"]["schema"])
        
        # Get connection parameters
        protocol = extra.get("protocol", self.DB_CONFIG["defaults"]["protocol"])
        verify = extra.get("verify", self.DB_CONFIG["defaults"]["verify"])
        source = extra.get("source", self.DB_CONFIG["defaults"]["source"])
        isolation_level = extra.get("isolation_level", self.DB_CONFIG["defaults"]["isolation_level"])

        # Validate required fields
        required_fields = ["username", "host", "port", "catalog", "schema"]
        for field in required_fields:
            if not locals().get(field):
                raise KeyError(f"Required field {field} not found in credentials")

        # Build connection string
        return self.DB_CONFIG["template"].format(
            username=username,
            password=password,
            host=host,
            port=port,
            catalog=catalog,
            schema=schema,
            protocol=protocol,
            verify=verify,
            source=source,
            isolation_level=isolation_level
        )
