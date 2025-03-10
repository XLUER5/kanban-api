from fastapi import APIRouter, HTTPException, status, Body, Query
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from typing import List, Optional
from bson import ObjectId

from app.models.task import TaskModel, TaskUpdate, TaskResponse
from app.database.mongodb import task_collection, board_collection, fix_object_id

router = APIRouter(tags=["Tasks"], prefix="/tasks")

@router.post("/", response_description="Crear una nueva tarea", response_model=TaskResponse)
async def create_task(task: TaskModel = Body(...)):
    # Verificar que el tablero existe
    if not ObjectId.is_valid(task.board_id):
        raise HTTPException(status_code=400, detail=f"ID de tablero inválido: {task.board_id}")
    
    board = await board_collection.find_one({"_id": ObjectId(task.board_id)})
    if board is None:
        raise HTTPException(
            status_code=404, 
            detail=f"Tablero con ID {task.board_id} no encontrado"
        )
    
    # Verificar que el estado es válido (corresponde a una columna del tablero)
    if task.status not in board["columns"]:
        raise HTTPException(
            status_code=400, 
            detail=f"Estado '{task.status}' no válido. Estados permitidos: {board['columns']}"
        )
    
    task_dict = jsonable_encoder(task)
    # Convertir board_id a ObjectId para almacenarlo en MongoDB
    task_dict["board_id"] = ObjectId(task_dict["board_id"])
    
    new_task = await task_collection.insert_one(task_dict)
    created_task = await task_collection.find_one({"_id": new_task.inserted_id})
    
    return fix_object_id(created_task)

@router.get("/", response_description="Listar todas las tareas", response_model=List[TaskResponse])
async def list_tasks(
    board_id: Optional[str] = Query(None, description="Filtrar por ID del tablero"),
    status: Optional[str] = Query(None, description="Filtrar por estado"),
    priority: Optional[str] = Query(None, description="Filtrar por prioridad"),
    assignee: Optional[str] = Query(None, description="Filtrar por asignado"),
    tag: Optional[str] = Query(None, description="Filtrar por etiqueta")
):
    # Construir filtro
    query = {}
    
    if board_id:
        if not ObjectId.is_valid(board_id):
            raise HTTPException(status_code=400, detail=f"ID de tablero inválido: {board_id}")
        query["board_id"] = ObjectId(board_id)
    
    if status:
        query["status"] = status
    
    if priority:
        query["priority"] = priority
    
    if assignee:
        query["assignee"] = assignee
    
    if tag:
        query["tags"] = tag
    
    tasks = await task_collection.find(query).to_list(1000)
    return fix_object_id(tasks)

@router.get("/{id}", response_description="Obtener una tarea por ID", response_model=TaskResponse)
async def get_task(id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail=f"ID inválido: {id}")
    
    task = await task_collection.find_one({"_id": ObjectId(id)})
    if task is None:
        raise HTTPException(status_code=404, detail=f"Tarea con ID {id} no encontrada")
    
    return fix_object_id(task)

@router.put("/{id}", response_description="Actualizar una tarea", response_model=TaskResponse)
async def update_task(id: str, task: TaskUpdate = Body(...)):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail=f"ID inválido: {id}")
    
    # Excluir campos None/null
    task_data = {k: v for k, v in task.model_dump(exclude_unset=True).items() if v is not None}
    
    if not task_data:
        raise HTTPException(status_code=400, detail="Se debe proporcionar al menos un campo para actualizar")
    
    # Si se actualiza el estado, verificar que sea válido
    if "status" in task_data:
        # Obtener la tarea actual para conocer su tablero
        current_task = await task_collection.find_one({"_id": ObjectId(id)})
        if current_task is None:
            raise HTTPException(status_code=404, detail=f"Tarea con ID {id} no encontrada")
        
        # Verificar que el nuevo estado es válido para el tablero
        board = await board_collection.find_one({"_id": current_task["board_id"]})
        if board and task_data["status"] not in board["columns"]:
            raise HTTPException(
                status_code=400, 
                detail=f"Estado '{task_data['status']}' no válido. Estados permitidos: {board['columns']}"
            )

    result = await task_collection.update_one(
        {"_id": ObjectId(id)}, {"$set": task_data}
    )

    if result.modified_count == 0:
        # Verificar si el documento existe
        if (await task_collection.find_one({"_id": ObjectId(id)})) is None:
            raise HTTPException(status_code=404, detail=f"Tarea con ID {id} no encontrada")
    
    updated_task = await task_collection.find_one({"_id": ObjectId(id)})
    return fix_object_id(updated_task)

@router.delete("/{id}", response_description="Eliminar una tarea")
async def delete_task(id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail=f"ID inválido: {id}")
    
    delete_result = await task_collection.delete_one({"_id": ObjectId(id)})
    
    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail=f"Tarea con ID {id} no encontrada")
    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"detail": f"Tarea con ID {id} eliminada correctamente"}
    )

@router.get("/board/{board_id}", response_description="Listar todas las tareas de un tablero", response_model=List[TaskResponse])
async def list_board_tasks(board_id: str):
    if not ObjectId.is_valid(board_id):
        raise HTTPException(status_code=400, detail=f"ID de tablero inválido: {board_id}")
    
    # Verificar que el tablero existe
    board = await board_collection.find_one({"_id": ObjectId(board_id)})
    if board is None:
        raise HTTPException(status_code=404, detail=f"Tablero con ID {board_id} no encontrado")
    
    tasks = await task_collection.find({"board_id": ObjectId(board_id)}).to_list(1000)
    return fix_object_id(tasks)