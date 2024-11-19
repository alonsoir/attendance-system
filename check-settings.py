from backend.core.config import Settings

try:
    settings = Settings()
    print(f"BACKEND_CORS_ORIGINS: {settings.BACKEND_CORS_ORIGINS}")
except Exception as e:
    print(f"Error initializing Settings: {e}")
