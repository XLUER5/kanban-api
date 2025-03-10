from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime

class BoardModel(BaseModel):
    name: str = Field(...)
    description: Optional[str] = None
    columns: List[str] = Field(default=["Por hacer", "En progreso", "Finalizado"])
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "name": "Proyecto Web",
                "description": "Desarrollo de aplicación web",
                "columns": ["Por hacer", "En progreso", "En revisión", "Finalizado"]
            }
        }
    )

class BoardUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    columns: Optional[List[str]] = None
    updated_at: datetime = Field(default_factory=datetime.now)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Proyecto Web Actualizado",
                "description": "Desarrollo de aplicación web moderna",
                "columns": ["Por hacer", "En progreso", "QA", "Finalizado"]
            }
        }
    )

class BoardResponse(BoardModel):
    id: str = Field(default=None, alias="_id")
    
    model_config = ConfigDict(
        populate_by_name=True,
    )