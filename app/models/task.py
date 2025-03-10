from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime

class TaskModel(BaseModel):
    board_id: str = Field(...)
    title: str = Field(...)
    description: Optional[str] = None
    status: str = Field(...)  # Corresponde a una columna del tablero
    priority: str = Field(default="Medium", description="Priority level: Low, Medium, or High")
    assignee: Optional[str] = None
    tags: List[str] = Field(default=[])
    due_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "board_id": "507f1f77bcf86cd799439011",
                "title": "Implementar API REST",
                "description": "Crear endpoints para gestión de usuarios",
                "status": "Por hacer",
                "priority": "High",
                "assignee": "Juan Pérez",
                "tags": ["backend", "api"],
                "due_date": "2023-12-15T00:00:00"
            }
        }
    )

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    assignee: Optional[str] = None
    tags: Optional[List[str]] = None
    due_date: Optional[datetime] = None
    updated_at: datetime = Field(default_factory=datetime.now)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Implementar API REST v2",
                "status": "En progreso",
                "priority": "Medium"
            }
        }
    )

class TaskResponse(TaskModel):
    id: str = Field(default=None, alias="_id")
    
    model_config = ConfigDict(
        populate_by_name=True,
    )