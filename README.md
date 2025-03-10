# Kanban API

Una API REST para gestionar tableros y tareas en un sistema Kanban, desarrollada con FastAPI y MongoDB.

## Requisitos

- Python 3.8+
- MongoDB

## Instalación

1. Clona este repositorio:
   ```bash
   git clone https://github.com/XLUER5/kanban-api.git
   cd kanban-api
   ```

2. Crea un entorno virtual e instala las dependencias:
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Configura las variables de entorno en el archivo `.env`:
   ```
   MONGODB_URL=mongodb://localhost:27017
   DB_NAME=kanban_db
   ```

## Ejecución

Inicia la aplicación con Uvicorn:

```bash
uvicorn app.main:app --reload
```

La API estará disponible en http://localhost:8000 y la documentación interactiva en http://localhost:8000/docs.


## Colección Postman

Se incluye un archivo `Kanban_API.postman_collection.json` con ejemplos de todos los endpoints para facilitar las pruebas.