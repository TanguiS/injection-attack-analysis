from pydantic import BaseSettings


# !!! Should not set values in this file, use the .env file instead
class Settings(BaseSettings):
    app_name: str = "Report service"
    version: str = '1.0.0'

    # Database
    no_postgres: bool = True
    postgres_user: str = "mobai"
    postgres_password: str = 'change-in-env'
    postgres_db: str = "report-service"
    postgres_server: str = "db"
    postgres_port: int = 5432

    # Redis
    redis_name: str = 'redis'
    redis_pass: str = 'change-in-env'
    redis_port: int = 6379
    redis_consent_exp_sec: int = 86400

    redis_test_name: str = 'redis'
    redis_test_port: int = 6380

    # Authentication
    auth_audience: str = 'change-in-env'
    auth_issuer: str = 'change-in-env'

    def get_redis_url(self):
        return f"redis://:{self.redis_pass}@{self.redis_name}:{self.redis_port}/0"

    def get_test_redis_url(self):
        return f"redis://{self.redis_test_name}:{self.redis_test_port}"

    def get_db_url(self):
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_server}:{self.postgres_port}/{self.postgres_db}"
    
    def get_test_db_url(self):
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@172.23.112.1:{self.postgres_port}/{self.postgres_db}-test"

    class Config:
        env_file = ".env"


settings = Settings()