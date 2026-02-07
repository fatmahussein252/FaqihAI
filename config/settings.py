from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    MODEL_NAME: str
    MASTER_API_KEY: str
    RAG_FORMATTER_API_KEY: str
    RAG_AGENT_API_KEY: str
    FILTER_API_KEY: str
    FIQH_API_KEY: str
    MAZHAB_API_KEY: str
    FATWA_API_KEY: str
    THREAD_CLASSIFIER_API_KEY: str
    COMMAND_PREPROCESSOR_API_KEY: str
    
    model_config = SettingsConfigDict(env_file=".env")



def get_settings():
    return Settings()