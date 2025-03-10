from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import board, task

# Crear aplicación FastAPI
app = FastAPI(
    title="Kanban API",
    description="API REST para gestionar tableros y tareas Kanban",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(board.router)
app.include_router(task.router)

@app.get("/", tags=["Root"])
async def read_root():
    return {
        "message": "Bienvenido a la API de Kanban",
        "docs": "/docs",
        "endpoints": {
            "boards": "/boards",
            "tasks": "/tasks"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)