from urllib.parse import quote_plus
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "StockMaster"
    API_V1_STR: str = "/api/v1"

    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = "Database@123"
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_DB: str = "stockmaster_simple"

    SECRET_KEY: str = "fe158c41-c70a-4662-938a-92da5de47055"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        password = quote_plus(self.MYSQL_PASSWORD)  # safely encode special chars
        return (
            f"mysql+pymysql://{self.MYSQL_USER}:{password}"
            f"@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DB}"
        )

    class Config:
        env_file = ".env"

settings = Settings()