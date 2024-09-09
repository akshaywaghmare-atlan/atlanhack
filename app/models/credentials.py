from pydantic import BaseModel, Field

class CredentialConfig(BaseModel):
    host: str
    port: int
    user: str
    password: str
    database: str

class CredentialPayload(BaseModel):
    url: str
    port: int
    user_name: str = Field(..., alias="userName")
    password: str
    database: str

    class Config:
        populate_by_name = True
    
    def get_credential_config(self) -> CredentialConfig:
        return CredentialConfig(
            host=self.url,
            port=self.port,
            database=self.database,
            user=self.user_name,
            password=self.password
        )

