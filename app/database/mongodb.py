import motor.motor_asyncio
from bson import ObjectId
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Obtener configuración de MongoDB desde variables de entorno
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "kanban_db")

# Crear cliente de MongoDB
client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
db = client[DB_NAME]

# Colecciones
board_collection = db.boards
task_collection = db.tasks

# Helper para convertir ObjectId a string en documentos
def fix_object_id(document):
    if document is None:
        return None
    
    if isinstance(document, list):
        return [fix_object_id(item) for item in document]
    
    if not isinstance(document, dict):
        return document
    
    for k, v in document.items():
        if isinstance(v, ObjectId):
            document[k] = str(v)
        elif isinstance(v, dict) or isinstance(v, list):
            document[k] = fix_object_id(v)
    
    return document