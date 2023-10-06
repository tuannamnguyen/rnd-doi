from src.databases.get_db_instance import get_db_instance
from src.settings.app_settings import app_settings

db_instance = get_db_instance(app_settings.MONGODB_URL, app_settings.DB_NAME)
