'''
What do we do here??
- this file manages the application's configuration settings using the
Pydantic Settings
- we automatically read environment variables

'''


from pydantic_settings import BaseSettings
from functools import lru_cache #last recently used cache - for optimizing
# used in a I/O function that is periodically called with the same arguments



class Settings(BaseSettings):
    GEMINI_API_KEY: str
    GEMINI_MODEL: str = "gemini-1.5-flash"
    MAX_IMAGE_SIZE_MB: int = 10
    ALLOWED_IMAGE_FORMATS: list = ["jpg", "jpeg", "png", "bmp"]

    class Config:
        env_file = ".env"

    '''
    .env (environment) files are increasingly popular as a way to configure an
    application by securely storing configuration settings, environment 
    variables, and sensitive information.
    '''

# This decorator caches the Settings object so it's only created once
@lru_cache()
def get_settings():
    return Settings()